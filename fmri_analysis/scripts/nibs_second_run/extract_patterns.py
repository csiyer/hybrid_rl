import os, glob, argparse, pickle
import numpy as np
import nibabel as nib
from joblib import Parallel, delayed

BIDSDIR='/burg/dslab/users/csi2108/hybrid_mri_bids'
nibs_base= os.path.join(BIDSDIR, 'derivatives', 'nibetaseries')
# GOAL: vmpfc_patterns = {subnum: {'choice': n_trials x n_voxels array, 'fb': n_trials x n_voxels array}, ...}

def process_one_sub(sub_num):
    sub_id = f'sub-hybrid{sub_num:02d}'
    subdir = os.path.join(nibs_base, sub_id, 'func')

    # make subject brain mask using functional data(combine across runs)
    # this is because there are often a couple voxels on the edge of the brain in the mask but not functional data
    run_brainmasks = [nib.load(f).get_fdata() > 0 for f in glob.glob(f'/{subdir}/*MNI*mask.nii.gz')]  # load brain masks
    sub_brainmask_bool = np.logical_and.reduce(run_brainmasks) # combine

    for roi in ['hipp','vmpfc']:
        if roi == 'hipp':
            roi_mask_file = '/burg/dslab/users/csi2108/hybrid_mri_CSI/masks/bl_hipp_binary.nii.gz'
        elif roi == 'vmpfc':
            roi_mask_file = '/burg/dslab/users/csi2108/hybrid_mri_CSI/masks/vmpfc_neurovault.nii'

        # combine brain mask with roi mask (sometimes they are not totally overlapping)
        roi_mask_bool = nib.load(roi_mask_file).get_fdata().astype(bool)
        sub_mask_indices = np.where( sub_brainmask_bool & roi_mask_bool )

        roi_patterns_allruns = {'choice': [], 'fb':[]} # list of arrays, n_voxels x n_trials
        for run in range(1,6):
            for trial_type in ['choice','fb']:
                beta_file = os.path.join(subdir, f'{sub_id}_task-main_run-{run:02d}_space-MNI152NLin2009cAsym_desc-{trial_type}_betaseries.nii.gz')
                
                if not os.path.exists(beta_file):
                    continue

                beta_data = nib.load(beta_file).get_fdata() # shape: X×Y×Z×trials
                beta_masked = beta_data[sub_mask_indices] # shape: n_voxels × n_trials

                allzero_voxels = np.all(beta_masked == 0, axis=1).nonzero()[0]
                if len(allzero_voxels > 0):
                    print('ALL-ZERO VOXELS FOUND: ', sub_id, roi, beta_file)
                    beta_masked = np.delete(beta_masked, allzero_voxels, axis=0)

                # normalize voxels through time
                beta_normalized = (beta_masked - np.mean(beta_masked, axis=1, keepdims=True)) / np.std(beta_masked, axis=1, keepdims=True)
                # save
                roi_patterns_allruns[trial_type].append(beta_normalized)

        # concatenate across runs
        for k, v in roi_patterns_allruns.items():
            roi_patterns_allruns[k] = np.hstack(v).T  # shape: n_trials x n_voxels

        # save
        outpath = os.path.join(subdir, f"{roi}_patterns_{sub_id}.pkl")
        with open(outpath, 'wb') as f:
            pickle.dump(roi_patterns_allruns, f)
        print(f"Saved {roi} patterns for {sub_id} → {outpath}")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='asdf')
    # parser.add_argument('--sub_num', type=int, help='sub-hybrid??')
    # args = parser.parse_args()
    # process_one_sub(args.sub_num)

    subs = sorted([i for i in os.listdir(nibs_base) if 'sub-hybrid' in i])
    Parallel(n_jobs=8)( delayed(process_one_sub)(sub) for sub in subs )

    # combine into one big pickle
    for roi in ['hipp','vmpfc']:
        all_patterns={}
        for sub_num in range(1,32):
            sub = f'sub-hybrid{sub_num:02d}'
            subdir = os.path.join(nibs_base, sub, 'func')
            sub_patterns_dict_path = os.path.join(subdir, 'rois', f"{roi}_patterns_{sub}.pkl")
            with open(sub_patterns_dict_path, 'rb') as f:
                sub_patterns = pickle.load(f)
            all_patterns[sub_num] = {
                'choice': sub_patterns['choice'],
                'fb': sub_patterns['fb']
            }
            os.remove(sub_patterns_dict_path)

        outpath = os.path.join(nibs_base, f'{roi}_patterns.pkl')
        with open(outpath, 'wb') as f:
            pickle.dump(all_patterns, f)