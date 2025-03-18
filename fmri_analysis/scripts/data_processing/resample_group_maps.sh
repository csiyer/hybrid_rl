#!/bin/bash

# fmriprep results are in 3mm resolution, resample to 2mm for comparison

# Define input and output directories
INPUT_DIR="/Volumes/shohamy-locker/chris/hybrid_mri_CSI/group_analyses/Group_Level_MixEff"
TEMPLATE="$FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz"

# Loop through all NIfTI files in the input directory
for cope_folder in "$INPUT_DIR"/csi_model?_fmriprep/*.gfeat/cope?.feat/; do

    thresh_zstat_file="$cope_folder"/thresh_zstat1.nii.gz
    thresh_zstat_out="$cope_folder"/thresh_zstat1_2mm.nii.gz
    zstat_file="$cope_folder"/stats/zstat1.nii.gz
    zstat_out="$cope_folder"/stats/zstat1_2mm.nii.gz

    # Run FLIRT to resample to 2mm
    flirt -in "$thresh_zstat_file" -ref "$TEMPLATE" -out "$thresh_zstat_out" -applyisoxfm 2
    flirt -in "$zstat_file" -ref "$TEMPLATE" -out "$zstat_out" -applyisoxfm 2

    if [ $? -eq 0 ]; then
        echo "✅ Resampled: $cope_folder"
    else
        echo "❌ Error resampling: $cope_folder"
    fi
done

echo "🎉 All group maps resampled!"
