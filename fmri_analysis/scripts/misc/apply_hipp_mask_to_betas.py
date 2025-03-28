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

    for beta_file in [f for f in glob.glob(subdir + '/*betaseries.nii.gz') if 'inval' not in f]: # only choice and fb trials
        beta_data = nib.load(beta_file).get_fdata()
        beta_masked = beta_data[sub_mask_indices]

        # there is one voxel in subject that is on the edge of the brain and counted as 0 by nibetaseries
        allzero_voxels = np.all(beta_masked == 0, axis=1).nonzero()[0]
        if len(allzero_voxels) > 1:
            print("ERROR: unexpectedly more than 1 voxel with no signal")
        beta_masked = np.delete(beta_masked, allzero_voxels[0], axis = 0) 

        # normalize within-pattern
        beta_normalized = (beta_masked - np.mean(beta_masked, axis=1, keepdims=True)) / np.std(beta_masked, axis=1, keepdims=True)
        np.save(beta_file.replace('.nii.gz', '_hipp_norm.npy'), beta_normalized)

Parallel(n_jobs=4)( delayed(process_one_sub)(sub) for sub in subs )