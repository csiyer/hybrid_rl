"""Prepare filenames, events files, and confound files for beta series modeling with NiBetaSeries"""

import os, glob
import numpy as np
import pandas as pd

def get_orig_sub_num(bids_sub_num):
    """Get subject ID in original dataset from subject ID in BIDS dataset"""
    conversion = pd.read_csv('/Volumes/shohamy-locker/chris/hybrid_mri_bids/n31_subject_list.txt')
    return conversion[conversion.bids==f'sub-hybrid{bids_sub_num}'].original.iloc[0][-2:]

def create_events_file(sub,run,beh_path='/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/behavior'):
    """Create events file with choice and feedback trials for beta series modeling"""
    orig_sub = get_orig_sub_num(sub) # from bids number to original

    choice_onsets = np.loadtxt(os.path.join(beh_path, f'{orig_sub}_output/EV_files/choice_run{run}.txt'))[:,0]
    fb_onsets = np.loadtxt(os.path.join(beh_path, f'{orig_sub}_output/EV_files/FB_run{run}.txt'))[:,0]
    inval_ev = np.atleast_2d( np.loadtxt(os.path.join(beh_path, f'{orig_sub}_output/EV_files/inval_run{run}.txt')) )

    if np.all(inval_ev == 0): 
        inval_ev = np.array([ [], [] ]).T  # ignore it

    all_onsets = np.concatenate([choice_onsets, fb_onsets, inval_ev[:, 0]])
    all_durations = np.concatenate([np.full_like(choice_onsets, 1.5), np.full_like(fb_onsets, 1.5), inval_ev[:, 1]])
    all_trial_types = np.concatenate([np.repeat('choice', len(choice_onsets)), np.repeat('fb', len(fb_onsets)), np.repeat('inval', len(inval_ev))])

    events = pd.DataFrame({'onset': all_onsets, 'duration': all_durations, 'trial_type': all_trial_types})
    return events.sort_values(by='onset')



base = '/Volumes/shohamy-locker/chris/hybrid_mri_bids'
paths_to_server =[]
for subdir in glob.glob(base+'/sub-hybrid??'): 
    sub = subdir[-2:]
    print('Beginning subject ' + sub)
    paths_to_server.extend([subdir, subdir+'/func']) # add folder names

    available_runs = [1,2,3,5] if sub == '12' else [1,2,3,4,5]
    for run in available_runs:

        # create events file
        events = create_events_file(sub,run)
        events_file = os.path.join(subdir, 'func', f'sub-hybrid{sub}_task-main_run-{run}_events.tsv')
        # if os.path.isfile(events_file):
        #     os.rename(events_file, events_file.replace('events','events-OLD'))
        events.to_csv(events_file, index=False, sep='\t')

        # add path to bold and brain mask files
        fmriprep_funcdir = os.path.join(base, 'derivatives', 'fmriprep', f'sub-hybrid{sub}', 'func')
        bold_file = os.path.join(fmriprep_funcdir, f'sub-hybrid{sub}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
        mask_file = os.path.join(fmriprep_funcdir, f'sub-hybrid{sub}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz')
        
        # rename confounds file timeseries->regressors
        confounds_file = os.path.join(fmriprep_funcdir, f'sub-hybrid{sub}_task-main_run-{run}_desc-confounds_timeseries.tsv')
        confounds_columns =  [
            'trans_x','trans_y','trans_z','rot_x','rot_y','rot_z',
            'trans_x_derivative1','trans_y_derivative1','trans_z_derivative1','rot_x_derivative1','rot_y_derivative1','rot_z_derivative1',
            'trans_x_power2','trans_y_power2','trans_z_power2','rot_x_power2','rot_y_power2','rot_z_power2',
            'trans_x_derivative1_power2','trans_y_derivative1_power2','trans_z_derivative1_power2','rot_x_derivative1_power2','rot_y_derivative1_power2','rot_z_derivative1_power2',
        ]
        confounds = pd.read_csv(confounds_file, usecols=confounds_columns, sep='\t')
        confounds_file = confounds_file.replace('timeseries', 'regressors') # nibs wants it named this instead
        confounds.to_csv(confounds_file, index=False, sep='\t')
        
        paths_to_server.extend([events_file, bold_file, mask_file, confounds_file])


# write files to copy them to server
with open('../files_to_ginsburg.txt', 'w') as f:
    for path in paths_to_server:
        f.write(path + '\n')