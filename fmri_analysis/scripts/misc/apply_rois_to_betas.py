"""Take the subject-specific ROIs (from freesurfer) and mask the trial-level betas"""
import os, glob, pickle
import numpy as np
import nibabel as nib
from joblib import Parallel, delayed

BIDSDIR='/Volumes/shohamy-locker/chris/hybrid_mri_bids'
nibs_base= BIDSDIR + '/derivatives/nibetaseries'
fmriprep_base= BIDSDIR + '/derivatives/fmriprep' # for brainmasks and rois
rois = {
    'hippocampusBL': 'hipp', 
    'vmpfc': 'vmpfc',
    # 'caudate+putamen': 'striatum',
    'loc': 'loc',
    # 'v12L': 'v12L',
    # 'v12R': 'v12R',
    # 'locL': 'locL',
    # 'locR': 'locR',
    # 'v1L': 'v1L',
    # 'v1R': 'v1R'
}
subs = sorted([i for i in os.listdir(nibs_base) if 'sub-hybrid' in i])

def process_one_sub(sub):
    print('Processing sub ', sub)
    subdir = os.path.join(nibs_base, sub, 'func')

    # make subject brain mask (combine across runs)
    # this is because there are often a couple voxels on the edge of the brain in the mask but not functional data
    run_brainmasks = [nib.load(f).get_fdata() > 0 for f in glob.glob(fmriprep_base + f'/{sub}/func/*MNI*mask.nii.gz')]  # load binary masks
    sub_brainmask_bool = np.logical_and.reduce(run_brainmasks) # combine

    os.makedirs(subdir + '/rois', exist_ok=True)
    for roi_in,roi_out in rois.items():

        outpath = os.path.join(subdir, 'rois', f"{roi_out}_patterns_{sub}.pkl")
        if os.path.exists(outpath):
            continue

        # combine this subject's brain mask with a mask of what's included in the ROI
        # (rarely there is ~1 voxel that is counted in ROI but not in brain mask)
        roi_mask_file = os.path.join(fmriprep_base, sub, 'anat', 'rois', f'{sub}_space-MNI152NLin2009cAsym_desc-{roi_in}.nii.gz')
        roi_mask_bool = nib.load(roi_mask_file).get_fdata().astype(bool)
        sub_mask_indices = np.where( sub_brainmask_bool & roi_mask_bool )

        roi_patterns_allruns = {'choice': [], 'fb':[]} # list of arrays, n_voxels x n_trials
        for run in range(1,6):
            for trial_type in ['choice','fb']:
                beta_file = os.path.join(subdir, f'{sub}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-{trial_type}_betaseries.nii.gz')
                
                if not os.path.exists(beta_file):
                    continue

                beta_data = nib.load(beta_file).get_fdata() # shape: X×Y×Z×trials
                beta_masked = beta_data[sub_mask_indices] # shape: n_voxels × n_trials

                allzero_voxels = np.all(beta_masked == 0, axis=1).nonzero()[0]
                if len(allzero_voxels > 0):
                    print('ALL-ZERO VOXELS FOUND: ', sub, roi_out, beta_file)
                    beta_masked = np.delete(beta_masked, allzero_voxels, axis=0)

                ### normalize voxels through time
                beta_normalized = (beta_masked - np.mean(beta_masked, axis=1, keepdims=True)) / np.std(beta_masked, axis=1, keepdims=True)
                # save
                roi_patterns_allruns[trial_type].append(beta_normalized)

        # concatenate across runs
        for k, v in roi_patterns_allruns.items():
            roi_patterns_allruns[k] = np.hstack(v).T # choice: big np array of shape n_trials, n_voxels

        # save
        with open(outpath, 'wb') as f:
            pickle.dump(roi_patterns_allruns, f)
        print(f"Saved {roi_out} patterns for {sub} → {outpath}")

Parallel(n_jobs=4)( delayed(process_one_sub)(sub) for sub in subs )

# combine into one big pickle
for roi in rois.values():
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