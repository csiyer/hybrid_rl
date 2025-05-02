#!/bin/bash

# code used to carry out cluster correction on the negative cluster in CSI model 3 revT x ep_lik_enc interaction

cd /Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses/Group_Level_MixEff/csi_model3/revtxep_lik_enc.gfeat/cope1.feat
mkdir -p svc
fslmaths stats/zstat1 -mul -1 -mas mask svc/zstat1_negative # svc/hipp_mask svc/hipp_zstat1_negative
# calculated with smoothest -z stats/res4d -m svc/hipp_mask
volume=185254
dlh=0.0293215 # whole brain: 0.0233783
cluster -i svc/zstat1_negative -t 2.3 --mm \
    --othresh=svc/thresh_zstat1_negative -o svc/cluster_mask_zstat1_negative \
    --connectivity=26 --mm --olmax=svc/lmax_zstat1_negative_std.txt \
    --scalarname=Z -p 1.0 -d $dlh --volume=$volume -c \
    stats/cope1 > svc/cluster_zstat1_negative_std.txt
