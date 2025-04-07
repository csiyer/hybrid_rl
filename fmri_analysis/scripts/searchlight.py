"""
Searchlight for clusters of voxels whose patterns at retrieval trials correlate to patterns at encoding trials.
When encoding_trial_type=='choice', this is unsurprising in visual areas but more surprising in other areas
When encoding_trial_type=='fb', this would resemble reinstatement of some value representation.
"""
import os
import numpy as np
import nibabel as nib
import pandas as pd
from joblib import Parallel, delayed

N_JOBS = -1

bids_dir = '/Volumes/shohamy-locker/chris/hybrid_mri_bids'
nibs_dir = f'{bids_dir}/derivatives/nibetaseries'

sub_conversion = pd.read_csv(f'{bids_dir}/n31_subject_list.txt')
beh = pd.read_csv('/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/data/hybrid_data.csv')


def get_beh_data(sub_num):
    """behavioral data of one subject, including only valid trials"""
    bids_sub_num = f'sub-hybrid{sub_num:02d}'
    orig_sub_id = sub_conversion.original[sub_conversion.bids == bids_sub_num].iloc[0]
    orig_sub_num = int(orig_sub_id[-2:])
    return beh[(beh.Sub==orig_sub_num) & (~pd.isna(beh.RT))].reset_index()


def get_nibs_files(sub_num, trial_type):
    """Retrieve filenames of beta series images for a given trial type (choice or fb)"""
    sub_id = f'sub-hybrid{sub_num:02d}'
    sub_files = [
        nibs_dir + f'/{sub_id}/func/{sub_id}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-{trial_type}_betaseries.nii.gz'
        for run in range(1,6) if not (sub_num ==12 and run ==4)
    ]
    return sub_files


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


def encoding_retrieval_correlation_sphere(X_enc, X_ret):
    """
    Compute mean correlation of encoding trial patterns and retrieval trial patterns.
    Both inputs should be (n_trials, n_voxels_in_sphere) and index-matched for encoding-retrieval pairs.
    """
    # Normalize patterns
    X_enc = (X_enc - X_enc.mean(axis=1, keepdims=True)) 
    X_ret = (X_ret - X_ret.mean(axis=1, keepdims=True)) 

    X_enc /= np.linalg.norm(X_enc, axis=1, keepdims=True)
    X_ret /= np.linalg.norm(X_ret, axis=1, keepdims=True)
    
    # cosine distance = r when normalized
    correlations = np.sum(X_enc * X_ret, axis=1)  # Dot product for each trial (N_trials,)

    # average across encoding-retrieval pairs
    return np.nanmean(correlations) 


def run_searchlight(sub_num, encoding_trial_type='fb'):

    sub_id = f'sub-hybrid{sub_num:02d}'
    save_path = nibs_dir + f'/{sub_id}/func/{sub_id}_task-main_space-MNI152NLin2009cAsym_desc-enc{encoding_trial_type}_searchlight.nii.gz'
    if os.path.isfile(save_path):
        print(f'Already completed searchlight for sub {sub_num}, {encoding_trial_type}')
        return

    # get behavioral data for this subject, identify encoding-retrieval pairs (indices in the beh_data + nibs images)
    beh_data = get_beh_data(sub_num)
    retrieval_indices = beh_data.index[beh_data.OldT == 1].to_numpy()
    encoding_indices = np.array([ beh_data.index[beh_data.Trial == row.encTrialNum][0].astype(int) for _,row in beh_data[beh_data.OldT==1].iterrows()])

    # get subject beta series data 
    choice_data = np.concatenate([
        nib.load(im).get_fdata(dtype=np.float32) for im in get_nibs_files(sub_num,'choice')
    ], axis=3)

    retrieval_data = choice_data[:,:,:,retrieval_indices]

    if encoding_trial_type=='fb':
        fb_data = np.concatenate([
            nib.load(im).get_fdata(dtype=np.float32) for im in get_nibs_files(sub_num,'fb')
        ], axis=3)
        encoding_data = fb_data[:,:,:,encoding_indices]
        del fb_data
    else:
        encoding_data = choice_data[:,:,:,encoding_indices]
    del choice_data

    # based on subject's brain mask, get the indices within each sphere (centered at each voxel in brain mask)
    sub_brainmask = get_combined_brainmask(sub_num)
    sub_brainmask_data = sub_brainmask.get_fdata()
    voxel_center_coords = list(zip(*np.where(sub_brainmask.get_fdata()))) # a sphere centered at each voxel in the brain mask
    sphere_indices_list = [get_sphere_indices(voxel, mask=sub_brainmask_data) for voxel in voxel_center_coords]

    # Run searchlight (parallel)
    searchlight_results = Parallel(n_jobs=N_JOBS)(
        delayed(encoding_retrieval_correlation_sphere)(
            extract_sphere_data(encoding_data, sphere_idxs),
            extract_sphere_data(retrieval_data, sphere_idxs)
        ) for sphere_idxs in sphere_indices_list
    )

    # Create result image (1D → 3D)
    results_3d = np.full(sub_brainmask.shape, np.nan)
    for val, coord in zip(searchlight_results, voxel_center_coords):
        results_3d[coord] = val

    # Save to NIfTI
    nib.save(nib.Nifti1Image(results_3d, sub_brainmask.affine), save_path)
    print(f"Searchlight map for sub {sub_num} saved to: {save_path}")



if __name__ == '__main__':
    for sub_num in range(1,32):
        print('Beginning subject ', sub_num)
        run_searchlight(sub_num, 'fb')
        run_searchlight(sub_num, 'choice')