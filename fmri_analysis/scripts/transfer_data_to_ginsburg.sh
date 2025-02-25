rsync -zhav --files-from='fmri_analysis/scripts/files_to_ginsburg.txt' \
    /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/ \
    csi2108@ginsburg.rcs.columbia.edu:/burg/home/csi2108/hybrid_mri_CSI

# rsync -zhav --progress --ignore-existing \
#     /Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/scripts/ \
#     csi2108@ginsburg.rcs.columbia.edu:/burg/dslab/users/csi2108/scripts


## how the file list was constructed (python)
# import os, re
# base = '/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/'

# files = np.concatenate([
#     glob.glob(base+'TCST*/structural/bravo.anat/*'),
#     # glob.glob(base+'TCST*/fsl_reg/*'),
#     # glob.glob(base+'TCST*/B0_map/*'),
#     # glob.glob(base+'TCST*/hybrid_r?/EPI*.nii.gz'),
#     glob.glob(base+'TCST*/hybrid_r?/example_func.nii.gz'),
#     glob.glob(base+'TCST*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz'),
#     glob.glob(base+'TCST*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/reg/*'),
#     glob.glob(base+'TCST*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/mc/extended_confs_24par.txt'),
#     glob.glob(base+'TCST*/hybrid_r?/')
# ])
# files = [f[f.find('TCST'):] for f in files if np.all([sub not in f for sub in ['TCST001','TCST003','TCST011','TCST035']])]
# print(len(files))

# with open('scripts/files_to_ginsburg.txt', 'w') as f:
#     f.write('\n'.join(files))
