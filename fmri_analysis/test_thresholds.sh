#!/bin/bash

# Set input paths
            
COPE_FILE="/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/group_analyses/Group_Level_MixEff/inc_ep_lik_encfb_badB0/ep_lik.gfeat/cope1.feat/stats/zstat1.nii.gz"
MASK_FILE="/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/group_analyses/Group_Level_MixEff/inc_ep_lik_encfb_badB0/ep_lik.gfeat/cope1.feat/mask.nii.gz"
DESIGN_MAT="/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/group_analyses/Group_Level_MixEff/inc_ep_lik_encfb_badB0/ep_lik.gfeat/design.mat"
DESIGN_CON="/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/group_analyses/Group_Level_MixEff/inc_ep_lik_encfb_badB0/ep_lik.gfeat/design.con"
OUT_DIR="/Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses_z3"

DLH=0.0234446
VOLUME=191458

mkdir -p "$OUT_DIR"

### --- 1. Cluster-Based Threshold: p < 0.05 ---
cluster --in=$COPE_FILE --thresh=3.0 --pthresh=0.05 --oindex=$OUT_DIR/cluster_p05.nii.gz --olmax=$OUT_DIR/lmax_p05.txt --osize=$OUT_DIR/cluster_size_p05.nii.gz --dlh=$DLH --volume=$VOLUME 
fslmaths $COPE_FILE -mas $OUT_DIR/cluster_p05.nii.gz $OUT_DIR/thresh_zstat1_p05.nii.gz

### --- 2. Cluster-Based Threshold: p < 0.01 ---
cluster --in=$COPE_FILE --thresh=3.0 --pthresh=0.01 --oindex=$OUT_DIR/cluster_p01.nii.gz --olmax=$OUT_DIR/lmax_p01.txt --osize=$OUT_DIR/cluster_size_p01.nii.gz --dlh=$DLH --volume=$VOLUME
fslmaths $COPE_FILE -mas $OUT_DIR/cluster_p01.nii.gz $OUT_DIR/thresh_zstat1_p01.nii.gz

### --- 3. Cluster-Based Threshold: p < 0.001 ---
cluster --in=$COPE_FILE --thresh=3.0 --pthresh=0.001 --oindex=$OUT_DIR/cluster_p001.nii.gz --olmax=$OUT_DIR/lmax_p001.txt --osize=$OUT_DIR/cluster_size_p001.nii.gz --dlh=$DLH --volume=$VOLUME
fslmaths $COPE_FILE -mas $OUT_DIR/cluster_p001.nii.gz $OUT_DIR/thresh_zstat1_p001.nii.gz

