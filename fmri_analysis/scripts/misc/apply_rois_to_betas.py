"""Take the subject-specific hippocampal ROIs (from freesurfer) and mask the trial-level betas"""
import os, glob
import numpy as np
import nibabel as nib
from joblib import Parallel, delayed

BIDSDIR='/Volumes/shohamy-locker/chris/hybrid_mri_bids'
nibs_base= BIDSDIR + '/derivatives/nibetaseries'
fmriprep_base= BIDSDIR + '/derivatives/fmriprep' # for brainmass
fmriprep_anat_base=BIDSDIR + '/derivatives/fmriprep_anat' #ROIs stored with the other run of fmriprep
rois = {
    'hippocampusBL': 'hipp', 
    'vmpfc': 'vmpfc',
    'caudate+putamen': 'striatum',
    'loc': 'loc',
    'v12L': 'v12L',
    'v12R': 'v12R',
    'locL': 'locL',
    'locR': 'locR',
    'v1L': 'v1L',
    'v1R': 'v1R'
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
        if roi_in == 'v1L' or roi_in == 'v1R':

            # combine this subject's brain mask with a mask of what's included in the ROI
            # (rarely there is ~1 voxel that is counted in ROI but not in brain mask)
            roi_mask_file = os.path.join(fmriprep_anat_base, sub, 'anat', 'rois', f'{sub}_space-MNI152NLin2009cAsym_desc-{roi_in}.nii.gz')
            roi_mask_bool = nib.load(roi_mask_file).get_fdata().astype(bool)
            sub_mask_indices = np.where( sub_brainmask_bool & roi_mask_bool )

            for beta_file in [f for f in os.listdir(subdir) if 'betaseries.nii.gz' in f and 'inval' not in f]: # only choice and feedback
                
                beta_path = os.path.join(subdir, beta_file)
                outpath = os.path.join(subdir, 'rois', beta_file).replace('.nii.gz', f'_{roi_out}_norm.npy')

                if not os.path.isfile(outpath):
                    
                    beta_data = nib.load(beta_path).get_fdata()
                    beta_masked = beta_data[sub_mask_indices]

                    allzero_voxels = np.all(beta_masked == 0, axis=1).nonzero()[0]
                    if len(allzero_voxels > 0):
                        print(sub, roi_out, beta_file)
                        continue

                    # normalize within-pattern
                    beta_normalized = (beta_masked - np.mean(beta_masked, axis=1, keepdims=True)) / np.std(beta_masked, axis=1, keepdims=True)
                    # save
                    np.save(outpath, beta_normalized)

Parallel(n_jobs=4)( delayed(process_one_sub)(sub) for sub in subs )

# if sub == 'sub-hybrid13' and roi_out=='hipp':
#     # there is one voxel in subject 13 that is on the edge of the brain and counted as 0 by nibetaseries
#     # this only occurs in run 3, but we'll exclude the voxel from all runs for consistency
#     run3path = subdir + '/sub-hybrid13_task-main_run-3_space-MNI152NLin2009cAsym_desc-choice_betaseries.nii.gz'
#     run3beta = nib.load(run3path).get_fdata()
#     run3masked = run3beta[sub_mask_indices]
#     sub13zerovoxel = np.all(run3masked == 0, axis=1).nonzero()[0][0] # there is only one, it's voxel 126 in the flattened array
#                   if sub == 'sub-hybrid13' and roi_out=='hipp':
#                   beta_masked = np.delete(beta_masked, sub13zerovoxel, axis = 0) 