#!/bin/bash

TRIALTYPE_KEY=$1 # 'encfb', 'encchoice', 'choice_opt-nonopt', 'fb_opt-nonopt', 'choice_match-mismatch', 'fb_match-mismatch'

# --- Configuration ---
BASE_DIR=/Volumes/shohamy-locker/chris/hybrid_mri_bids/derivatives/nibetaseries
OUTPUT_DIR="$BASE_DIR/group_searchlight"
FILE_PATTERN="sub-hybrid??/func/sub-hybrid??_task-main_space-MNI152NLin2009cAsym_desc-${TRIALTYPE_KEY}_searchlight.nii.gz"
N_SUBJECTS=31
N_PERMUTATIONS=1000

# Create output directory
if [ ! -e $OUTPUT_DIR ]; then mkdir -p $OUTPUT_DIR; fi
cd $OUTPUT_DIR

# --- Collect subject (z-transformed) searchlight files ---
echo "Reading inputs for $TRIALTYPE_KEY..."
FILE_LIST=()
for file in $BASE_DIR/$FILE_PATTERN; do
    FILE_LIST+=("$file")
done
echo ${#FILE_LIST[@]} files found
concat_map=all_searchlights_${TRIALTYPE_KEY}.nii.gz
fslmerge -t $concat_map "${FILE_LIST[@]}"

# --- Create design.mat and design.con for one-sample t-test ---

# Create design matrix (1s for one-sample t-test)
# cat <<EOF > design.mat
# /NumWaves 1
# /NumPoints $N_SUBJECTS
# /PPheights 1.0
# /Matrix
# $(for i in $(seq 1 $N_SUBJECTS); do echo "1"; done)
# EOF

# cat <<EOF > design.con
# /NumWaves 1
# /NumContrasts 1
# /Matrix
# 1
# EOF

# --- Run randomise with cluster correction ---
echo "Merged inputs, beginning randomise"
randomise \
  -i $concat_map \
  -o randomise_$TRIALTYPE_KEY \
  -d design.mat \
  -t design.con \
  -n $N_PERMUTATIONS \
  -c 3.1
rm $concat_map
echo "Done. Outputs in $OUTPUT_DIR/randomise_$TRIALTYPE_KEY_*"
