#!/bin/bash

module load FSL/6.0.5.2

# get each subject's mean hippocampal z-statistic
HOME=/burg/dslab/users/csi2108/hybrid_mri_CSI
ROI=$HOME/bl_hipp_prob.nii.gz
OUTFILE=$HOME/roi_values.txt
> $OUTFILE  # Clear output file

for sub_z in $HOME/group_analyses/Subject_Level_FixEff/csi_model3_??.gfeat/cope5.feat/stats/zstat1.nii.gz; do
    mean=$(fslstats $sub_z -k $ROI -M)
    echo $mean >> $OUTFILE
done

# run t-test
python3 - <<END
import numpy as np
from scipy.stats import ttest_1samp
data = np.loadtxt("$OUTFILE")
tval, pval = ttest_1samp(data, 0, alternative='less')
print(f"Mean ROI value: {np.mean(data):.3f} ± {np.std(data, ddof=1):.3f}")
print(f"T = {tval:.3f}, p = {pval:.5f}")
END


##########
########## OUTPUT:
########## Mean ROI value: -0.275 ± 0.753
########## T = -2.037, p = 0.05059
##########