"""Python version of the matlab script (last script) in rgerraty's readme"""

import os, glob
import numpy as np

# with open('/Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses/n31_subs.txt', 'r') as file:
#     s = file.read()
# subs_runs_in_order = [sub[45:62] for sub in s.split('\n')]

subs = sorted(glob.glob('/Volumes/shohamy-locker/chris/hybrid_mri_CSI/TCST*'))
subs2 = []
design_mat = []
feat = 'csi_model1.feat'
j = 0  # Column index

for sub in subs:
    runs = sorted(glob.glob(f'{sub}/hybrid_r?/{feat}'))
    design_mat.extend([[1 if i == j else 0 for i in range(len(subs))] for _ in runs])
    subs2.extend(runs)
    j+=1

design_mat = np.array(design_mat, dtype=int)
con_mat = np.eye(design_mat.shape[1], dtype=int)

np.savetxt('/Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses/n31_fe_design.mat', design_mat, fmt='%d')
np.savetxt('/Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses/n31_fe_con.mat', con_mat, fmt='%d')
with open('/Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses/n31_subs.txt', 'w') as f:
    f.write("\n".join(subs2) + "\n")