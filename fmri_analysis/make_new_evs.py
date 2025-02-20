"""
for my analysis, i wanted to make the following new EV files:
- choice_oldt_opt (optimal choice on old trial)
- choice_oldt_nonopt
- choice_oldt_prev_oldt_opt (previous trial was optimal old)
- choice_oldt_prev_oldt_nonopt
- choice_oldt_prev_newt (previous trial was new/new)
"""

import numpy as np
import pandas as pd
import os

def ev_equals(ev_1, ev_2):
	if len(ev_1) != len(ev_2): 
		return False
	return np.all(ev_1[0].to_numpy() == ev_2[0].to_numpy()) & \
		np.all(ev_1[1].to_numpy() == ev_2[1].to_numpy()) & \
		np.all(ev_1[2].to_numpy() == ev_2[2].to_numpy())

ev_path = '/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/behavior'
data_path = '/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/behavior/hybrid_data.csv'
data = pd.read_csv(data_path)

for sub in [i for i in os.listdir(ev_path) if 'output' in i]:
	subdir = os.path.join(ev_path,sub)
	subnum = int(sub[:2])
	for run in range(1,6):
		old_ev_path = subdir+f'/EV_files/choice_oldt_run{run}.txt'
		if os.path.isfile(old_ev_path): # exclude subjects like 1 and 35
			old_ev = pd.read_csv(old_ev_path, sep=' ', header=None)
			old_data = data[(data.Sub==subnum) & (data.Run==run) & (data.OldT==1) & (~pd.isna(data.Resp))]

			if len(old_data) == len(old_ev) + 1:
				# this means the first old trial fell within the first 12s (6 TRs) which were discarded, ignore first
				old_data = old_data.iloc[1:]
			elif len(old_data) != len(old_ev):
				print('other unknown length mismatch ', subnum, run)
				break
			
			# first, replicate choice_oldc to make sure it matches
			# replicate choice_oldc 
			oldc = old_ev[(old_data.OldObjC==1).to_numpy()] # old choices on old trials
			oldc_true = pd.read_csv(subdir+f'/EV_files/choice_oldc_run{run}.txt', sep=' ', header=None)
			if not ev_equals(oldc, oldc_true):
				print("ERROR - OLDC DID NOT MATCH: ", subnum, run)
				break

			# if we look good, then let's continue on to making the new EVs!

			# optimal and non-optimal choices
			choice_oldt_opt = old_ev[(old_data.OptObj == 1).to_numpy()]
			choice_oldt_nonopt = old_ev[(old_data.OptObj == 0).to_numpy()]

			# previous trial outcomes
			prev_oldt_opt_mask = []
			prev_oldt_nonopt_mask = []
			prev_newt_mask = []
			for trial_num in old_data.Trial: # for each trial
				# find the previous trial in the whole data set
				prev_trial = data[(data.Sub==subnum) & (data.Run==run) & (data.Trial==trial_num-1)]
				if len(prev_trial) > 1:
					print("ERROR: MULTIPLE TRIALS FOUND", subnum, run, trial_num)
				else:
					prev_oldt = prev_trial.OldT.iloc[0]
					if prev_trial.OldT.iloc[0] == 1:
						prev_newt_mask.append(False) # old/new, not a new/new trial
						if prev_trial.OptObj.iloc[0] == 1:
							prev_oldt_opt_mask.append(True)
							prev_oldt_nonopt_mask.append(False)
						else:
							prev_oldt_nonopt_mask.append(True)
							prev_oldt_opt_mask.append(False)
					else: 
						prev_newt_mask.append(True)
						prev_oldt_opt_mask.append(False)
						prev_oldt_nonopt_mask.append(False)
					
			choice_oldt_prev_oldt_opt = old_ev[np.array(prev_oldt_opt_mask)]
			choice_oldt_prev_oldt_nonopt = old_ev[np.array(prev_oldt_nonopt_mask)]
			choice_oldt_prev_newt = old_ev[np.array(prev_newt_mask)]

			# write outputs
			choice_oldt_opt.to_csv(subdir+f'/EV_files/choice_oldt_opt_run{run}.txt', sep = ' ', header=False, index=False)
			choice_oldt_nonopt.to_csv(subdir+f'/EV_files/choice_oldt_nonopt_run{run}.txt', sep = ' ', header=False, index=False)
			choice_oldt_prev_oldt_opt.to_csv(subdir+f'/EV_files/choice_oldt_prev_oldt_opt_run{run}.txt', sep = ' ', header=False, index=False)
			choice_oldt_prev_oldt_nonopt.to_csv(subdir+f'/EV_files/choice_oldt_prev_oldt_nonopt_run{run}.txt', sep = ' ', header=False, index=False)
			choice_oldt_prev_newt.to_csv(subdir+f'/EV_files/choice_oldt_prev_newt_run{run}.txt', sep = ' ', header=False, index=False)
			