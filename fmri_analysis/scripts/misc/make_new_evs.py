"""
This script performs two tasks.
(1) Due to an error with the timing information in the MATLAB performance outputs, the timing of the choice trials was initially messed up.
    The EV files were iniitally made by this script: https://github.com/rgerraty/hybrid_reinforcement_learning/blob/master/make_EV.m
    The choice times corresponded to the onset of a jittered ITI, and the choice duration (supposed to be RT) was actually up until the stimulus onset, rather than the respones.
    This was looking for neural effects at the wrong timepoint!
    Because of this, we had to recreate all the choice EV files (and we did the FB too just as a sanity check). 
(2) There were also some new EV files that we wanted to add, not present in the initial make_EV.m script:
    for my analysis, i wanted to make the following new EV files:
    - choice_oldt_opt (optimal choice on old trial)
    - choice_oldt_nonopt
    - choice_oldt_prev_oldt_opt (previous trial was optimal old)
    - choice_oldt_prev_oldt_nonopt
    - choice_oldt_prev_newt (previous trial was new/new)

Because of these reasons, this script makes all the necessary EVs over again :) 
"""
import os, scipy.io
import numpy as np
import pandas as pd

# helper functions 
def add_prev_trial_outcomes(data):
    # add these three columns to the data
    data['choice_oldt_prev_newt'] = np.zeros(len(data),dtype=int)
    data['choice_oldt_prev_oldt_nonopt'] = np.zeros(len(data),dtype=int)
    data['choice_oldt_prev_oldt_opt'] = np.zeros(len(data),dtype=int)
    old_t = data['OldT'] == 1
    prev_old_t = data['OldT'].shift(1) == 1
    prev_opt = data['OptObj'].shift(1) == 1
    data.loc[old_t & ~prev_old_t, 'choice_oldt_prev_newt'] = 1
    data.loc[old_t & prev_old_t & prev_opt, 'choice_oldt_prev_oldt_opt'] = 1
    data.loc[old_t & prev_old_t & ~prev_opt, 'choice_oldt_prev_oldt_nonopt'] = 1

    ### add choice_prev3_uncertainy and choice_prev3_old ## looking at previous 3 trials
    # add a point for each old trial, and a point for each optobj trial
    # Compute rolling sums (shifted so we don't include the current trial)
    data['OptObj_helper'] = (data['OptObj'] == 1).astype(int)
    data['prev3_old'] = data.groupby('Sub')['OldT'].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).sum())
    data['prev3_optobj'] = data.groupby('Sub')['OptObj_helper'].transform(lambda x: x.shift(1).rolling(window=3, min_periods=1).sum())
    data['prev3_certainty'] = data['prev3_old'] + data['prev3_optobj']
    data = data.drop(columns='prev3_optobj')  # also fixed minor drop() syntax
    data['prev3_old'] /= 6 # normalize to 1
    data['prev3_certainty'] /= 6

    return data

def round_to_num(val, num=5):
    if isinstance(val, int):
        return val
    str_val = f"{val:.10f}".rstrip('0')  # Convert to string, strip trailing zeros
    decimals = str_val[::-1].find('.')  # Count decimals
    if decimals > num:
        return np.round(val, num)
    return val

def write_df_to_ev(df, path, overwrite=False):
    if len(df.columns) != 3:
        print('ERROR - more or less than 3 columns')

    if os.path.isfile(path) and not overwrite:
        print('Error--file already exists. Pass overwrite=true to ignore.')
        return 
    
    elif len(df) == 0 or np.all(pd.isna(df.iloc[:,2])):
        # no trials or all NA, empty regressor
        pd.DataFrame([[0, 0, 0]]).to_csv(path, sep=' ', header=False, index=False)

    else: # length >3 and it has values
        if df.columns[2] == 'submem': # this one is different, we want to include both 0 and 1
            df[df.iloc[:, 2].isin([0,1])].to_csv(path, sep = ' ', header=False, index=False)
        else:
            df.iloc[:,2] = df.iloc[:,2].apply(round_to_num)
            if len(df.iloc[:,2].unique()) <= 3:
                # this is a binary regressor, just get the "1" values
                filt = df[df.iloc[:, 2] == 1]
                if len(filt) == 0:
                    pd.DataFrame([[0, 0, 0]]).to_csv(path, sep=' ', header=False, index=False)
                else:
                    filt.to_csv(path, sep = ' ', header=False, index=False)
            else:
                # this is a parametric regressor, get all non-nan values
                df[~pd.isna(df.iloc[:,2])].to_csv(path, sep= ' ', header=False, index=False)
             
			    
# main script

ROOTPATH = '/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/behavior'
data = pd.read_csv(os.path.join(ROOTPATH,'hybrid_data.csv'))
data = add_prev_trial_outcomes(data)
exclusions = ['01_output', '03_output', '11_output', '35_2nd_output', '35_output'] # missing data or otherwise excluded

for subdir in [i for i in os.listdir(ROOTPATH) if '_output' in i]:
    subdirpath = os.path.join(ROOTPATH, subdir)
    sub = int(subdir[0:2])

    if not os.path.exists(subdirpath+'/EV_files_OLD'):
        # rename the EV files folder
        os.rename(subdirpath+'/EV_files', subdirpath+'/EV_files_OLD')
        os.makedirs(subdirpath+'/EV_files')
        os.makedirs(subdirpath+'/EV_files/RTDur')

    if subdir in exclusions:
        continue # skip this subject for making the new EV files

    # load behavioral data from mat file
    matfile = scipy.io.loadmat(subdirpath + f'/Performance_5.mat') # this contains all data from all the runs we'll just use this

    for run in sorted(data[data.Sub==sub].Run.unique()):
    
        # find the data in the matlab file
        # we will mask for the current run, and subtract 12 seconds to account for the 6 dropped TRs (2s each) at the start of the run
        run_mask = matfile['Performance']['cond'][0,0]['Run'][0,0][0] == run # current run
        choice_start_times = matfile['Performance']['time'][0,0]['startChoice'][0,0][0][run_mask] - 12 
        time_of_response = matfile['Performance']['time'][0,0]['startDelay'][0,0][0][run_mask] - 12 # the difference between this and startChoice should = RT (it is within a fraction of a second)
        fb_start_times = matfile['Performance']['time'][0,0]['startFB'][0,0][0][run_mask] - 12 
        fb_end_times = matfile['Performance']['time'][0,0]['startISI'][0,0][0][run_mask]  - 12 # end of FB
        rt = matfile['Performance']['choose'][0,0]['RT'][0,0][0][run_mask] / 1000 # ms to s
        valid_mask = ~np.isnan(rt) # non-nan responses

        # create regressors, these will eventually be saved as FSL-style 3-column EV files
        # create the invalid regressor
        inval_ev = pd.DataFrame({
            'onset': np.round(choice_start_times[~valid_mask], 4),
            'duration': np.round(fb_end_times[~valid_mask] - choice_start_times[~valid_mask], 4),
            'value': np.ones(sum(~valid_mask), dtype=int)
        })
        # write the RT-duration regressor (all valid trials, duration of the RT -- for "ConsDurRTDur" modeling)
        rt_ev = pd.DataFrame({
            'onset': np.round(choice_start_times[valid_mask], 4),
            'duration': np.round(rt[valid_mask], 4),
            'value': np.ones(sum(valid_mask), dtype=int)
        })
        # now, create all the choice and FB EVs
        choice_evs = pd.DataFrame({
            'onset': np.round(choice_start_times[valid_mask], 4),
            'duration_const': np.ones(sum(valid_mask)) * 1.5, # 1.5s constant duration
            'duration_rt': np.round(rt[valid_mask], 4),
            'choice': np.ones(sum(valid_mask), dtype=int)
        })
        fb_evs = pd.DataFrame({
            'onset': np.round(fb_start_times[valid_mask], 4),
            'duration': np.round(fb_end_times[valid_mask] - fb_start_times[valid_mask], 4), # should be almost exactly 1.5
            'FB': np.ones(sum(valid_mask), dtype=int)
        })

        # Response (left/right) regressors
        # we will code resp == 1 as Left and resp == 2 as Right, but it doesn't matter in the GLM
        # this doesn't need the valid mask because that's coded in response_LR
        response_LR = matfile['Performance']['choose'][0,0]['resp'][0,0][0][run_mask]
        response_onsets_L = time_of_response[response_LR == 1]
        response_onsets_R = time_of_response[response_LR == 2]
        left_ev = pd.DataFrame({
            'onset': np.round(response_onsets_L, 4),
            'duration': np.zeros(len(response_onsets_L)), # stick regressors with 0 duration
            'value': np.ones(len(response_onsets_L), dtype=int)
        })
        right_ev = pd.DataFrame({
            'onset': np.round(response_onsets_R, 4),
            'duration': np.zeros(len(response_onsets_R)), # stick regressors with 0 duration
            'value': np.ones(len(response_onsets_R), dtype=int)
        })

        # now, create all the special choice EV files
        # for parametric regressors, values with be either the proper value or nan
        # for binary/boxcar regressors, values will be 1 when they should be included (0 or nan otherwise)
        rundata = data[(data.Sub==sub) & (data.Run==run) & (~pd.isna(data.RT))].reset_index()

        choice_evs['choice_enct'] = rundata['encT']
        choice_evs['choice_eplik_enc'] = rundata['Ep_lik_enc']
        choice_evs['choice_eplik'] = rundata['Ep_lik']
        choice_evs['choice_ierat'] = rundata['Lik_rat']
        choice_evs['choice_inclik'] = rundata['Inc_lik']
        choice_evs['choice_newc'] = (rundata['OldObjC'] == 0).astype(int)
        choice_evs['choice_noc'] = (rundata['OldT'] == 0).astype(int)
        choice_evs['choice_oldc'] = (rundata['OldObjC'] == 1).astype(int)
        choice_evs['choice_oldt_nonopt'] = ((rundata['OldT'] == 1) & (rundata['OptObj'] == 0)).astype(int)
        choice_evs['choice_oldt_opt'] = ((rundata['OldT'] == 1) & (rundata['OptObj'] == 1)).astype(int)
        choice_evs['choice_oldt_prev_newt'] = rundata['choice_oldt_prev_newt'] # added by the function above
        choice_evs['choice_oldt_prev_oldt_nonopt'] = rundata['choice_oldt_prev_oldt_nonopt'] # added by the function above
        choice_evs['choice_oldt_prev_oldt_opt'] = rundata['choice_oldt_prev_oldt_opt'] # added by the function above
        choice_evs['choice_prev3_old'] = rundata['prev3_old']
        choice_evs['choice_prev3_certainty'] = rundata['prev3_certainty']
        choice_evs['choice_oldt'] = rundata['OldT']
        choice_evs['choice_Qchose_newc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==0), rundata['Q_chosen'], np.nan)
        choice_evs['choice_Qchose_noc'] = np.where(rundata['OldT'] == 0, rundata['Q_chosen'], np.nan)
        choice_evs['choice_Qchose_oldc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==1), rundata['Q_chosen'], np.nan)
        choice_evs['choice_Qchose'] = rundata['Q_chosen']
        choice_evs['choice_Qdiff_newc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==0), rundata['Q_diff'], np.nan)
        choice_evs['choice_Qdiff_noc'] = np.where(rundata['OldT'] == 0, rundata['Q_diff'], np.nan)
        choice_evs['choice_Qdiff_noptdeck'] = np.where(rundata['LuckyDeckC'] == 0, rundata['Q_diff'], np.nan)
        choice_evs['choice_Qdiff_oldc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==1), rundata['Q_diff'], np.nan)
        choice_evs['choice_Qdiff_optdeck'] = np.where(rundata['LuckyDeckC'] == 1, rundata['Q_diff'], np.nan)
        choice_evs['choice_Qdiff'] = rundata['Q_diff']
        choice_evs['choice_Qunchose_newc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==0), rundata['Q_unchosen'], np.nan)
        choice_evs['choice_Qunchose_noc'] = np.where(rundata['OldT'] == 0, rundata['Q_unchosen'], np.nan)
        choice_evs['choice_Qunchose_oldc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==1), rundata['Q_unchosen'], np.nan)
        choice_evs['choice_Qunchose'] = rundata['Q_unchosen']
        choice_evs['choice_revT'] = rundata['RevT']
        choice_evs['oldval_newc'] = (np.where(rundata['OldObjC']==0, rundata['ObjPP'], np.nan) - 0.5).round(1) # idk its weird
        choice_evs['oldval_oldc'] = (np.where(rundata['OldObjC']==1, rundata['ObjPP'], np.nan) - 0.5).round(1)
        choice_evs['oldval'] = (rundata['ObjPP'] - 0.5).round(1)
        # choice_evs['oldvaldiff'] = rundata[''] #  not sure what this is, not in make_EV.m
        
        # constrast coded-versions of memory-optimal and q-optimal decisions
        choice_evs['choice_oldt_opt-nonopt'] = choice_evs['choice_oldt_opt'] - choice_evs['choice_oldt_nonopt']
        choice_evs['oldt_qdiff-bin'] = np.sign(rundata['Q_diff'][rundata['OldT'] == 1])
        # add encoding-shifted optimal-nonoptimal
        for i,row in rundata.iterrows():
            if row.OldT==1:
                enc_index = rundata.index[rundata.Trial == (row.Trial-row.Delay)]
                rundata.loc[enc_index,'Enc_opt-nonopt'] = np.sign(row.OptObj-0.5) # convert {0,1} to {-1,1}
        fb_evs['FB_enc_opt-nonopt'] = rundata['Enc_opt-nonopt']

        fb_evs['FB_eplik_enc'] = rundata['Ep_lik_enc']
        fb_evs['FB_eplik'] = rundata['Ep_lik']
        fb_evs['FB_inclik'] = rundata['Inc_lik']
        fb_evs['FB_newc'] = (rundata['OldObjC'] == 0).astype(int)
        fb_evs['FB_noc'] = (rundata['OldT'] == 0).astype(int)
        fb_evs['FB_oldc'] = (rundata['OldObjC'] == 1).astype(int)
        fb_evs['FB_pe_newc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==0), rundata['PE'], np.nan)
        fb_evs['FB_pe_noc'] = np.where(rundata['OldT'] == 0, rundata['PE'], np.nan)
        fb_evs['FB_pe_noptdeck'] = np.where(rundata['LuckyDeckC'] == 0, rundata['PE'], np.nan)
        fb_evs['FB_pe_oldc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==1), rundata['PE'], np.nan)
        fb_evs['FB_pe_optdeck'] = np.where(rundata['LuckyDeckC'] == 1, rundata['PE'], np.nan)
        fb_evs['FB_pe'] = rundata['PE']
        fb_evs['fb_revT'] = rundata['RevT']
        fb_evs['FBpay_newc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==0), rundata['Outcome'], np.nan)
        fb_evs['FBpay_noc'] = np.where(rundata['OldT'] == 0, rundata['Outcome'], np.nan)
        fb_evs['FBpay_oldc'] = np.where((rundata['OldT'] == 1)&(rundata['OldObjC']==1), rundata['Outcome'], np.nan)
        fb_evs['FBpay'] = rundata['Outcome']
        # leaving these out: ['FB_pay_run?_00','FB_pay_run?_02','FB_pay_run?_06','FB_pay_run?_08','FB_pay_run?_10']  

        choice_evs['submem'] = np.nan
        memory_data_path = os.path.join(subdirpath, 'Performance_Memory.mat')
        if os.path.isfile(memory_data_path):
            # get memory test data
            mdata = scipy.io.loadmat(memory_data_path)
            enc_trial_num = mdata['PerformanceMem']['Cond'][0,0]['EncTrial'][0,0][0]
            obj_rec_resp = mdata['PerformanceMem']['Resp'][0,0]['ObjRec'][0,0][0]
            old_or_new = mdata['PerformanceMem']['Cond'][0,0]['OldNew'][0,0][0]

            # some objects come up multiple times, filter based on first occurrence (we count only the first occurrence in subsequent memory)
            unique_trials, first_indices = np.unique(enc_trial_num, return_index=True)
            first_obj_rec_resp = obj_rec_resp[first_indices]
            first_old_or_new = old_or_new[first_indices]

            hit_trials = unique_trials[(first_obj_rec_resp < 3) & (first_old_or_new == 1)]
            miss_trials = unique_trials[(first_obj_rec_resp > 3) & (first_old_or_new == 1)]
            
            choice_evs.loc[rundata['Trial'].isin(hit_trials).to_numpy(), 'submem'] = 1  # match this to trials in the run data
            choice_evs.loc[rundata['Trial'].isin(miss_trials).to_numpy(), 'submem'] = 0 # match to trials in run data
        
        # cut off events from the first 12s (negative onset time) these are from the 6 removed TRs
        inval_ev = inval_ev[inval_ev['onset'] >= 0].reset_index(drop=True)
        rt_ev = rt_ev[rt_ev['onset'] >= 0].reset_index(drop=True)
        right_ev = right_ev[right_ev['onset'] >= 0].reset_index(drop=True)
        left_ev = left_ev[left_ev['onset'] >= 0].reset_index(drop=True)
        choice_evs = choice_evs[choice_evs['onset'] >= 0].reset_index(drop=True)
        fb_evs = fb_evs[fb_evs['onset'] >= 0].reset_index(drop=True)

        # save as 3-column FSL txt files
        write_df_to_ev(inval_ev, path = subdirpath+f'/EV_files/inval_run{run}.txt')
        write_df_to_ev(rt_ev, path = subdirpath+f'/EV_files/rt_run{run}.txt')
        write_df_to_ev(right_ev, path = subdirpath+f'/EV_files/respR_run{run}.txt')
        write_df_to_ev(left_ev, path = subdirpath+f'/EV_files/respL_run{run}.txt')
        for col in fb_evs.columns:
            if col not in ['onset','duration']:
                write_df_to_ev(fb_evs[['onset','duration',col]], path = subdirpath+f'/EV_files/{col}_run{run}.txt')
        for col in choice_evs.columns:
            if col not in ['onset','duration_const', 'duration_rt']:
                # write constant duration version
                write_df_to_ev(choice_evs[['onset','duration_const',col]], path = subdirpath+f'/EV_files/{col}_run{run}.txt')
                # rt duration version
                write_df_to_ev(choice_evs[['onset','duration_rt',col]], path = subdirpath+f'/EV_files/RTDur/{col}_run{run}.txt')
