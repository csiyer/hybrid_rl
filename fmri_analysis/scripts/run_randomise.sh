#!/bin/bash

module load FSL/6.0.5.2

# --- Configuration ---
BASEDIR=/burg/dslab/users/csi2108/hybrid_mri_CSI/group_analyses/ep_lik_randomise
COPE_DIR="$(dirname $BASEDIR)/Subject_Level_FixEff"
OUTPUT_DIR="$BASEDIR" 
# OUTPUT_DIR="$BASEDIR/randomise" 
COPE_PATTERN="csi_model1_v2_*.gfeat/cope2.feat/stats/cope1.nii.gz"
GROUP_MASK=/burg/dslab/users/csi2108/hybrid_mri_CSI/mask_group_thresh80.nii.gz
N_SUBJECTS=31
N_PERMUTATIONS=1000 

# Create output directory
mkdir -p $OUTPUT_DIR
cd $OUTPUT_DIR

# --- Collect cope and  varcopefiles ---
COPE_LIST=()
for file in $COPE_DIR/$COPE_PATTERN; do
    COPE_LIST+=("$file")
done
fslmerge -t all_copes.nii.gz "${COPE_LIST[@]}"

# --- Step 3: Create design.mat and design.con for one-sample t-test ---

# Create design matrix (1s for one-sample t-test)
cat <<EOF > design.mat
/NumWaves 1
/NumPoints $N_SUBJECTS
/PPheights 1.0
/Matrix
$(for i in $(seq 1 $N_SUBJECTS); do echo "1"; done)
EOF

# Create t contrast file
cat <<EOF > design.con
/NumWaves 1
/NumContrasts 2
/Matrix
1
-1
EOF

# --- Step 4: Run randomise with cluster correction ---
randomise \
  -i all_copes.nii.gz \
  -o randomise \
  -d design.mat \
  -t design.con \
  -m $GROUP_MASK \
  -n $N_PERMUTATIONS \
  -c 2.3

echo "Done. Outputs in $OUTPUT_DIR/randomise_*"
