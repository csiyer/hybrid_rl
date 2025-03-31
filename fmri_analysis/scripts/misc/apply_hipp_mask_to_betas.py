"""Take the subject-specific hippocampal ROIs (from freesurfer) and mask the trial-level betas"""
import os, glob
import numpy as np
import nibabel as nib
from joblib import Parallel, delayed

base = '/Volumes/shohamy-locker/chris/hybrid_mri_bids/derivatives'
nibs_base= base + '/nibetaseries'
fmriprep_base= base + '/fmriprep'

subs = [i for i in os.listdir(nibs_base) if 'sub-hybrid' in i]

def process_one_sub(sub):
    print('Processing sub ', sub)
    subdir = os.path.join(nibs_base, sub, 'func')

    # get this subject's hippocampal mask
    sub_mask_file = os.path.join(fmriprep_base, sub, 'anat', f'{sub}_space-MNI152NLin2009cAsym_desc-hippocampusBL.nii.gz')
    sub_mask = nib.load(sub_mask_file)
    sub_mask_indices = np.where( sub_mask.get_fdata().astype(bool) )

    if sub == 'sub-hybrid13':
        # there is one voxel in subject 13 that is on the edge of the brain and counted as 0 by nibetaseries
        # this only occurs in runs 2 and 3, but we'll exclude the voxel from all runs for consistency
        run3path = subdir + '/sub-hybrid13_task-main_run-3_space-MNI152NLin2009cAsym_desc-choice_betaseries.nii.gz'
        run3beta = nib.load(run3path).get_fdata()
        run3masked = run3beta[sub_mask_indices]
        allzero_voxel = np.all(run3masked == 0, axis=1).nonzero()[0][0] # there is only one, it's voxel 126 in the flattened array

    for beta_file in [f for f in glob.glob(subdir + '/*betaseries.nii.gz') if 'inval' not in f]: # only choice and fb trials
        beta_data = nib.load(beta_file).get_fdata()
        beta_masked = beta_data[sub_mask_indices]

        if sub == 'sub-hybrid13':
            beta_masked = np.delete(beta_masked, allzero_voxel, axis = 0) 

        # normalize within-pattern
        beta_normalized = (beta_masked - np.mean(beta_masked, axis=1, keepdims=True)) / np.std(beta_masked, axis=1, keepdims=True)
        np.save(beta_file.replace('.nii.gz', '_hipp_norm.npy'), beta_normalized)

Parallel(n_jobs=4)( delayed(process_one_sub)(sub) for sub in subs )