#!/bin/bash

### TO RUN:
# get on ginsburg, navigate to /burg/dslab/users/csi2108/hybrid_mri_CSI/scripts
# type: run_roi_analysis.sh MODELNAME CONTRASTNUMBER ROI
# modelname should be csi_model1_v3_noold, csi_model2, csi_model3
# CONTRASTNUMBER should be the number of the contrast we're looking at (see slack message)
# ROI should be either anterior or posterior

module load FSL/6.0.5.2

modelname=$1
copenum=$2
roiname=$3

HOME=/burg/dslab/users/csi2108/hybrid_mri_CSI
cope_pattern=$HOME/group_analyses/Subject_Level_FixEff/"$modelname"_??.gfeat/cope$copenum.feat/stats/cope1.nii.gz
ROI=$HOME/masks/bl_"$roiname"_hipp_prob.nii.gz
OUTFILE=$HOME/roi_analysis/"$modelname"_cope"$copenum"_$roi.txt
> $OUTFILE  # Clear output file

for sub_z in $cope_pattern; do
    mean=$(fslstats $sub_z -k $ROI -M)
    echo $mean >> $OUTFILE
done

# run t-test
python3 - <<END
import numpy as np
from scipy.stats import ttest_1samp
from scipy.stats import sem
data = np.loadtxt("$OUTFILE")
print('T-test for model "$modelname", contrast "$copenum", "$roiname" hippocampus: ')
tval, pval = ttest_1samp(data, 0)
print(f"Mean ROI value: {np.mean(data):.3f} ± {sem(data):.3f}")
print(f"T = {tval:.3f}, p = {pval:.5f}")
END