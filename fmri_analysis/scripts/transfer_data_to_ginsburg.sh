rsync -zhave --progress \
    --exclude='TCST001' --exclude='TCST003' --exclude='TCST011' --exclude='TCST035' --exclude='TCST035_2nd' \
    --exclude='behavior/01_output/*' --exclude='behavior/03_output/*' \
    --exclude='behavior/11_output/*' --exclude='behavior/35_output/*' --exclude='behavior/35_2nd_output/*' \
    /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/ \
    csi2108@ginsburg.rcs.columbia.edu:/burg/dslab/users/csi2108/hybrid_mri_CSI \
    --include='behavior/*_output/EV_files/***' \
    --include='TCST*/structural/***' \
    --include='TCST*/fsl_reg/***' \
    --include='TCST*/BO_map/***' \
    --include='TCST*/hybrid_r?/EPI*.nii.gz' \
    --include='TCST*/hybrid_r?/example_func.nii.gz' \
    --include='TCST*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz' \
    --include='TCST*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/reg/***' \
    --include='TCST*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/mc/extended_confs_24par.txt' \
    --exclude='*'

rsync -zhave -- progress \
    /Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/scripts \
    csi2108@ginsburg.rcs.columbia.edu:/burg/dslab/users/csi2108/scripts

