#!/bin/bash

# This script does several things:
# 1. Converts aseg.mgz to NIfTI if missing.
# 2. Transforms aseg to MNI space per run. (both of these should've been done by fmriprep but weren't)
# 3. Extracts L, R, and bilateral hippocampal ROIs.

# Ensure FSL is installed
# module load FSL/6.0.5.2
command -v fslmaths >/dev/null || { echo "FSL not found. Exiting."; exit 1; }

ROOT=/burg/dslab/users/csi2108/hybrid_mri_bids/derivatives/fmriprep_anat
ALT_ROOT=/burg/dslab/users/csi2108/hybrid_mri_bids/derivatives/fmriprep # copying outputs here

for subfolder in "$ROOT"/sub-hybrid??; do 
   
    sub_id=$(basename $subfolder)
    echo "Processing $sub_id"
    anat_dir="$ROOT/$sub_id/anat"

    # ---- Convert aseg.mgz to NIfTI ---- #
    aseg_nii="$ROOT/sourcedata/freesurfer/$sub_id/mri/aseg.nii.gz"
    if [ ! -f "$aseg_nii" ]; then
        echo "Converting aseg.mgz to NIfTI for $sub_id..."
        mri_convert "$ROOT"/sourcedata/freesurfer/"$sub_id"/mri/aseg.{mgz,nii.gz}
    else
        echo "aseg.nii.gz already exists for $sub_id, skipping conversion."
    fi

    # ---- Transform segmentation to MNI space ---- #
    aseg_mni="$anat_dir/${sub_id}_space-MNI152NLin2009cAsym_seg-aseg_dseg.nii.gz"

    # Check if the MNI-transformed aseg already exists
    if [ ! -f "$aseg_mni" ]; then
        echo "Transforming aseg.mgz to MNI space for $sub_id..."
        antsApplyTransforms \
            -i "$aseg_nii" \
            -r "$ROOT/$sub_id/func/${sub_id}_task-main_run-1_space-MNI152NLin2009cAsym_boldref.nii.gz" \
            -o "$aseg_mni" \
            -n GenericLabel \
            -t "$anat_dir/${sub_id}_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5" \
            -t "$anat_dir/${sub_id}_from-fsnative_to-T1w_mode-image_xfm.txt"
    else
        echo "Aseg MNI already exists, skipping transformation."
    fi

    # ---- Extract Hippocampal ROIs for this subject ---- #
    l_file="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-hippocampusL.nii.gz
    r_file="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-hippocampusR.nii.gz
    bl_file="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-hippocampusBL.nii.gz

    # Left Hippocampus (Label 17)
    fslmaths "$aseg_mni" -thr 17 -uthr 17 -div 17 "$l_file"
    # Right Hippocampus (Label 53)
    fslmaths "$aseg_mni" -thr 53 -uthr 53 -div 53 "$r_file"
    # Bilateral Hippocampus (Left + Right)
    fslmaths "$l_file" -add "$r_file" "$bl_file"

    # ---- Copy ROIs into initial fmriprep directory too ---- #
    alt_anat_dir="$ALT_ROOT/$sub_id/anat"
    cp $aseg_mni $l_file $r_file $bl_file "$alt_anat_dir/" 
done