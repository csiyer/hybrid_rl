### before running the FSL pipeline on fMRIPrep outputs, we need to sort out a couple things

import os, glob
import numpy as np
import pandas as pd
import nibabel as nib
from joblib import Parallel, delayed

FMRIPREP_DIR = '/Volumes/shohamy-locker/chris/hybrid_mri_fmriprep/'
OUTPUT_DIR = '/Volumes/shohamy-locker/chris/hybrid_mri_CSI/'
subs = pd.read_csv(FMRIPREP_DIR + 'n31_subject_list.txt')
BOLD_PROCESSING_SCRIPT = '/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/scripts/data_processing/prepare_fmriprep_bold.sh'

### 1. Functional image processing (apply smoothing, mask with brain mask)

def process_bold_data_one_run(orig, bids, run_num):
    relative_outpath = f'{orig}/hybrid_r{run_num}/fmriprep_bold_smoothed_masked.nii.gz'
    if not os.path.isfile(OUTPUT_DIR + relative_outpath):
        bold_file = FMRIPREP_DIR + f'{bids}/func/{bids}_task-main_run-{run_num}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
        mask_file = FMRIPREP_DIR + f'{bids}/func/{bids}_task-main_run-{run_num}_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'
        if os.path.isfile(bold_file):
            # run masking, smoothing (including the annoying intensity estimation)
            command = f'bash {BOLD_PROCESSING_SCRIPT} {bold_file} {mask_file} {OUTPUT_DIR+os.path.dirname(relative_outpath)}'
            os.system(command)
    else:
        print(f'Bold data already processed for subject {orig}, run {run_num}. Skipping...')
    return relative_outpath

# orig, bids, run_num tuples to pass to function above
sub_run_ids = [(subs.original.iloc[i], subs.bids.iloc[i], run_num) for i in range(len(subs)) for run_num in range(1,6)] 

print('Beginning bold files...')
# store paths for later copying to server
output_fpaths = Parallel(n_jobs=4)(delayed(process_bold_data_one_run)(*vals) for vals in sub_run_ids)
print('Finished bold files')


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

    for run_num in range(1,6):

        relative_outpath = f'{orig}/hybrid_r{run_num}/fmriprep_confounds_24par.txt'

        if not os.path.isfile(OUTPUT_DIR+relative_outpath):
            confounds_file = FMRIPREP_DIR + f'{bids}/func/{bids}_task-main_run-{run_num}_desc-confounds_timeseries.tsv'
            
            if os.path.isfile(confounds_file):
                # read in confounds, filter for just the ones we want
                confounds_trim = pd.read_csv(confounds_file, sep='\t', usecols=columns_to_keep).fillna(0)
                # write to FSL-compatible txt file
                outpath = OUTPUT_DIR + f'{orig}/hybrid_r{run_num}/fmriprep_confounds_24par.txt'
                confounds_trim.to_csv(os.path.join(OUTPUT_DIR, relative_outpath), sep=' ', index=False, header=False)
                output_fpaths.append(relative_outpath)
        else:
            pass
            print(f'Confounds file already created for subject {sub}, run {run}')
        output_fpaths.append(relative_outpath)


### write down paths for later copying to server
file_list_txt = "/Users/chrisiyer/_Current/lab/code/hybrid_rl/files_to_ginsburg.txt"
with open(file_list_txt, "w") as f:
    for path in output_fpaths:
        f.write(path + "\n")

