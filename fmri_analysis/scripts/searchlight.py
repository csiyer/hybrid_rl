"""
Searchlight for clusters of voxels whose patterns at retrieval trials correlate to patterns at encoding trials.
When encoding_trial_type=='choice', this is unsurprising in visual areas but more surprising in other areas
When encoding_trial_type=='fb', this would resemble reinstatement of some value representation.
"""
import os, argparse
import numpy as np
import nibabel as nib
import pandas as pd
from joblib import Parallel, delayed

N_JOBS = -1

bids_dir = '/burg/dslab/users/csi2108/hybrid_mri_bids'
nibs_dir = f'{bids_dir}/derivatives/nibetaseries'

sub_conversion = pd.read_csv(f'{bids_dir}/n31_subject_list.txt')
beh = pd.read_csv(f'{bids_dir}/hybrid_data.csv')


############ Loading data ################

def get_beh_data(sub_num):
    """behavioral data of one subject, including only valid trials"""
    bids_sub_num = f'sub-hybrid{sub_num:02d}'
    orig_sub_id = sub_conversion.original[sub_conversion.bids == bids_sub_num].iloc[0]
    orig_sub_num = int(orig_sub_id[-2:])
    return beh[(beh.Sub==orig_sub_num) & (~pd.isna(beh.RT))].reset_index()


def get_encoding_retrieval_pairs(beh_data):
    """Get indices of matching encoding and retrieval pairs"""
    retrieval_indices = beh_data.index[beh_data.OldT == 1].to_numpy()
    optimal_mask = beh_data.OptObj[beh_data.OldT==1] == 1 # mask for optimal trials

    # find encoding indices of those retrieval trials
    encoding_indices = []
    retrieval_indices_to_remove = []
    for i,retrieval_idx in enumerate(retrieval_indices):
        encoding_trials_idx_match = beh_data.index[beh_data.Trial == beh_data.encTrialNum.iloc[retrieval_idx]]
        if len(encoding_trials_idx_match) == 0:
            # encoding trial was an invalid trial, excluded from neuroimaging analyses
            retrieval_indices_to_remove.append(i)
        else:
            encoding_indices.append(encoding_trials_idx_match[0]) # append matching index
    encoding_indices = np.array(encoding_indices)

    # remove the retrieval trials whose encoding trials were invalid
    retrieval_indices = np.delete(retrieval_indices, retrieval_indices_to_remove)
    optimal_mask = np.delete(optimal_mask, retrieval_indices_to_remove)
    return encoding_indices, retrieval_indices, optimal_mask


def get_nibs_files(sub_num, trial_type):
    """Retrieve filenames of beta series images for a given trial type (choice or fb)"""
    sub_id = f'sub-hybrid{sub_num:02d}'
    sub_files = [
        nibs_dir + f'/{sub_id}/func/{sub_id}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-{trial_type}_betaseries.nii.gz'
        for run in range(1,6) if not (sub_num ==12 and run ==4)
    ]
    return sub_files


def get_encoding_retrieval_data(sub_num, encoding_trial_type, encoding_indices, retrieval_indices):
    """Get encoding patterns and retrieval patterns, index matched"""

    choice_data = np.concatenate([
        nib.load(im).get_fdata(dtype=np.float32) for im in get_nibs_files(sub_num,'choice')
    ], axis=3)

    retrieval_data = choice_data[:,:,:,retrieval_indices]

    if encoding_trial_type=='fb':
        fb_data = np.concatenate([
            nib.load(im).get_fdata(dtype=np.float32) for im in get_nibs_files(sub_num,'fb')
        ], axis=3)
        encoding_data = fb_data[:,:,:,encoding_indices]
    else:
        encoding_data = choice_data[:,:,:,encoding_indices]

    return encoding_data, retrieval_data


def get_combined_brainmask(sub_num):
    """get intersection of a subject's 5 run-specific brain masks to use for all runs"""
    sub_id = f'sub-hybrid{sub_num:02d}'
    brainmask_files = [
        bids_dir + f'/derivatives/fmriprep/{sub_id}/func/{sub_id}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'
        for run in range(1,6) if not (sub_num ==12 and run == 4)
    ]
    run_brainmasks = [nib.load(f).get_fdata() > 0 for f in brainmask_files]
    # compute the intersection to use for this subject
    sub_brainmask_bool = np.logical_and.reduce(run_brainmasks) # combine
    combined_mask_img = nib.Nifti1Image(sub_brainmask_bool.astype(np.uint8), affine=nib.load(brainmask_files[0]).affine)
    return combined_mask_img


############ Searchlight sphere helpers ################

def generate_sphere_offsets(radius):
    """Offsets relative to center (0,0,0) for a sphere of given radius."""
    x, y, z = np.mgrid[-radius:radius+1, -radius:radius+1, -radius:radius+1]
    sphere = (x**2 + y**2 + z**2) <= radius**2
    offsets = np.vstack(np.where(sphere)).T - radius
    return offsets

sphere_offsets = generate_sphere_offsets(radius=5) # helps below


def get_sphere_indices(center, mask):
    """Return valid voxel indices in sphere around center using fast vectorized offsets."""
    img_shape = mask.shape
    offsets = sphere_offsets
    center = np.array(center)
    coords = center + offsets  # shape: (N_offsets, 3)
    # Bounds check
    in_bounds = np.all((coords >= 0) & (coords < img_shape), axis=1)
    coords = coords[in_bounds]
    # Mask check
    mask_values = mask[tuple(coords.T)]  # Convert to (3, N) tuple for indexing
    valid_coords = coords[mask_values > 0]
    return [tuple(c) for c in valid_coords]


def extract_sphere_data(X, sphere_coords):
    """X is a data image (x,y,z,n_trials) and sphere_coords is a list of 3D coordinates from above"""
    x, y, z = zip(*sphere_coords)
    # Index the 4D array using numpy advanced indexing
    return X[x, y, z, :].T  # shape: (n_trials, n_voxels_in_sphere)


############ Computing correlations ################

def encoding_retrieval_correlation(X_enc, X_ret):
    """
    Helper for below. Computes mean encoding-retrieval correlation.
    Both inputs should be (n_trials, n_voxels_in_sphere) and index-matched for encoding-retrieval pairs.
    """
    # Normalize patterns, dot product = correlation when normalized, average and z-transform 
    X_enc = (X_enc - X_enc.mean(axis=1, keepdims=True)) 
    X_ret = (X_ret - X_ret.mean(axis=1, keepdims=True)) 
    X_enc /= np.linalg.norm(X_enc, axis=1, keepdims=True)
    X_ret /= np.linalg.norm(X_ret, axis=1, keepdims=True)
    correlations = np.sum(X_enc * X_ret, axis=1)  # Dot product for each trial (N_trials,)
    return np.arctanh(np.nanmean(correlations) ) # average across encoding-retrieval pairs and z-transform


def encoding_retrieval_match_mismatch(X_enc, X_ret):
    """Variation of above, but compute the whole correlation matrix to subtract match-mismatch."""
    # Normalize rows to zero-mean, unit-norm
    X_enc = (X_enc - X_enc.mean(axis=1, keepdims=True))
    X_ret = (X_ret - X_ret.mean(axis=1, keepdims=True))
    X_enc /= np.linalg.norm(X_enc, axis=1, keepdims=True)
    X_ret /= np.linalg.norm(X_ret, axis=1, keepdims=True)
    corr_matrix = X_enc @ X_ret.T # Compute full correlation matrix (n_trials x n_trials)
    # Extract match and mismatch
    match_corrs = np.diag(corr_matrix)
    mismatch_corrs = corr_matrix[np.tril_indices_from(corr_matrix, k=-1) ] # k=-1 excludes diagonal
    # Fisher z-transform and return difference
    return np.arctanh(np.nanmean(match_corrs)) - np.arctanh(np.nanmean(mismatch_corrs))


def sphere_correlation(X_enc, X_ret, contrast, optimal_mask):
    """
    Main function called in the searchlight, on encoding and retrieval data within the sphere.
    X_enc and X_ret should be data from extract_sphere_data() 
    Contrast specifies opt-nonopt or match-mismatch
    kwargs contains other stuff
    """
    if contrast == 'opt-nonopt':
        opt = encoding_retrieval_correlation(X_enc[optimal_mask,:], X_ret[optimal_mask])
        nonopt = encoding_retrieval_correlation(X_enc[~optimal_mask,:], X_ret[~optimal_mask])
        return opt-nonopt # difference of z-transformed correlations
    elif contrast == 'match-mismatch':
        return encoding_retrieval_match_mismatch(X_enc, X_ret)


############ Main ################

def run_searchlight(sub_num, encoding_trial_type='fb', contrast='opt-nonopt'):

    sub_id = f'sub-hybrid{sub_num:02d}'
    save_path = nibs_dir + f'/{sub_id}/func/{sub_id}_task-main_space-MNI152NLin2009cAsym_desc-{encoding_trial_type}_{contrast}_searchlight.nii.gz'
    if os.path.isfile(save_path):
        print(f'Already completed searchlight for sub {sub_num}, {encoding_trial_type}')
        return

    # get behavioral data for this subject, identify encoding-retrieval pairs (indices in the beh_data + nibs images)
    beh_data = get_beh_data(sub_num)
    encoding_indices, retrieval_indices, optimal_mask = get_encoding_retrieval_pairs(beh_data) # mask for optimal retrieval trials

    # get subject beta series data 
    # this handles the encoding_trial_type, and uses choice or fb data depending on that argument
    encoding_data, retrieval_data = get_encoding_retrieval_data(sub_num, encoding_trial_type, encoding_indices, retrieval_indices)

    # based on subject's brain mask, get the indices within each sphere (centered at each voxel in brain mask)
    sub_brainmask = get_combined_brainmask(sub_num)
    sub_brainmask_data = sub_brainmask.get_fdata()
    voxel_center_coords = list(zip(*np.where(sub_brainmask.get_fdata()))) # a sphere centered at each voxel in the brain mask
    sphere_indices_list = [get_sphere_indices(voxel, mask=sub_brainmask_data) for voxel in voxel_center_coords]

    # Run searchlight (parallel)
    searchlight_results = Parallel(n_jobs=N_JOBS)(
        delayed(sphere_correlation)(
            extract_sphere_data(encoding_data, sphere_idxs),
            extract_sphere_data(retrieval_data, sphere_idxs),
            contrast, optimal_mask
        ) for sphere_idxs in sphere_indices_list
    )

    # Create result image (1D → 3D)
    results_3d = np.full(sub_brainmask.shape, np.nan)
    for val, coord in zip(searchlight_results, voxel_center_coords):
        results_3d[coord] = val

    # save to nifti
    nib.save(nib.Nifti1Image(results_3d, sub_brainmask.affine), save_path)

    print(f"Searchlight map for sub {sub_num} saved to: {save_path}")



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Run searchlight analysis for a given subject, encoding type, and contrast.')
    parser.add_argument('--sub_num', type=int, help='Subject number (1 to 31)')
    parser.add_argument('--enc_trial_type', type=str, choices=['fb', 'choice'], help='Encoding data from "choice" or "fb" period.')
    parser.add_argument('--contrast', type=str, choices=['opt-nonopt', 'match-mismatch'], help='Contrast optimal choices - nonoptimal or matching trials - mismatching.')
    args = parser.parse_args()

    if args.sub_num and args.enc_trial_type and args.contrast:
        print(f'Running subject {args.sub_num}, encoding type {args.enc_trial_type}, contrast {args.contrast}')
        run_searchlight(args.sub_num, args.enc_trial_type, args.contrast)
