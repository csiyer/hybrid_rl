### before running the FSL pipeline on fMRIPrep outputs, we need to sort out a couple things

import os, glob
import numpy as np
import pandas as pd
import nibabel as nib

output_fpaths = [] # write down paths for later copying to server
FMRIPREP_DIR = '/Volumes/shohamy-locker/chris/hybrid_mri_fmriprep/'
OUTPUT_DIR = '/Volumes/shohamy-locker/chris/hybrid_mri_CSI/'
subs = pd.read_csv(FMRIPREP_DIR + 'n31_subject_list.txt')


### 1. Mask functional file with brain mask

output_fpaths = [] # write down paths for later copying to server
FMRIPREP_DIR = '/Volumes/shohamy-locker/chris/hybrid_mri_fmriprep/'
OUTPUT_DIR = '/Volumes/shohamy-locker/chris/hybrid_mri_CSI/'
subs = pd.read_csv(FMRIPREP_DIR + 'n31_subject_list.txt')

print('Beginning bold files...')
for i in range(len(subs)):
    orig = subs.original.iloc[i] # original subject ID
    bids = subs.bids.iloc[i] # subject ID in bids dataset
    print('Subject ' + orig)

    for run_num in range(1,6):

        outpath = OUTPUT_DIR + f'{orig}/hybrid_r{run_num}/fmriprep_bold_masked.nii.gz'

        if not os.path.isfile(outpath):
            bold_file = FMRIPREP_DIR + f'{bids}/func/{bids}_task-main_run-{run_num}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
            mask_file = FMRIPREP_DIR + f'{bids}/func/{bids}_task-main_run-{run_num}_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'

            if os.path.isfile(bold_file):
                bold_img = nib.load(bold_file)
                bold_data = bold_img.get_fdata()
                mask_data = nib.load(mask_file).get_fdata()
                masked_bold_data = bold_data * mask_data[..., np.newaxis]  # Preserve time dimension
                masked_img = nib.Nifti1Image(masked_bold_data, affine=bold_img.affine, header=bold_img.header)
                nib.save(masked_img, outpath)
                output_fpaths.append(outpath)


### 2. Write filtered confounds file

columns_to_keep = [
    'trans_x','trans_y','trans_z','rot_x','rot_y','rot_z',
    'trans_x_derivative1','trans_y_derivative1','trans_z_derivative1','rot_x_derivative1','rot_y_derivative1','rot_z_derivative1',
    'trans_x_power2','trans_y_power2','trans_z_power2','rot_x_power2','rot_y_power2','rot_z_power2',
    'trans_x_derivative1_power2','trans_y_derivative1_power2','trans_z_derivative1_power2','rot_x_derivative1_power2','rot_y_derivative1_power2','rot_z_derivative1_power2',
]

print('Beginning confounds files...')
for i in range(len(subs)):
    orig = subs.original.iloc[i] # original subject ID
    bids = subs.bids.iloc[i] # subject ID in bids dataset
    print('Subject ' + orig)

    for run_num in range(1,6):
        
        outpath = OUTPUT_DIR + f'{orig}/hybrid_r{run_num}/fmriprep_confounds_24par.txt'

        if not os.path.isfile(outpath):
            confounds_file = FMRIPREP_DIR + f'{bids}/func/{bids}_task-main_run-{run_num}_desc-confounds_timeseries.tsv'
            
            if os.path.isfile(confounds_file):
                # read in confounds, filter for just the ones we want
                confounds_trim = pd.read_csv(confounds_file, sep='\t', usecols=columns_to_keep).fillna(0)
                # write to FSL-compatible txt file
                outpath = OUTPUT_DIR + f'{orig}/hybrid_r{run_num}/fmriprep_confounds_24par.txt'
                confounds_trim.to_csv(outpath, sep=' ', index=False, header=False)
                output_fpaths.append(outpath)


### write down paths for later copying to server
file_list_txt = "/Users/chrisiyer/_Current/lab/code/hybrid_rl/files_to_ginsburg.txt"
with open(file_list_txt, "w") as f:
    for path in output_fpaths:
        f.write(path + "\n")

