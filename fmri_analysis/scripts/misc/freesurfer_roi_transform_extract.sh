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
    aparcaseg_nii="$ROOT/sourcedata/freesurfer/$sub_id/mri/aparcaseg.nii.gz"
    if [ ! -f "$aparcaseg_nii" ]; then
        echo "Converting aparcaseg.mgz to NIfTI for $sub_id..."
        mri_convert "$ROOT"/sourcedata/freesurfer/"$sub_id"/mri/aparc+aseg.mgz "$ROOT"/sourcedata/freesurfer/"$sub_id"/mri/aparcaseg.nii.gz
    else
        echo "aparcaseg.nii.gz already exists for $sub_id, skipping conversion."
    fi

    # ---- Transform segmentation to MNI space ---- #
    aparcaseg_mni="$anat_dir/${sub_id}_space-MNI152NLin2009cAsym_seg-aparcaseg_dseg.nii.gz"

    # Check if the MNI-transformed aparcaseg already exists
    if [ ! -f "$aparcaseg_mni" ]; then
        echo "Transforming aparcaseg.mgz to MNI space for $sub_id..."
        antsApplyTransforms \
            -i "$aparcaseg_nii" \
            -r "$ROOT/$sub_id/func/${sub_id}_task-main_run-1_space-MNI152NLin2009cAsym_boldref.nii.gz" \
            -o "$aparcaseg_mni" \
            -n GenericLabel \
            -t "$anat_dir/${sub_id}_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5" \
            -t "$anat_dir/${sub_id}_from-fsnative_to-T1w_mode-image_xfm.txt"
    else
        echo "aparcaseg MNI already exists, skipping transformation."
    fi

    # ---- Extract ROIs for this subject ---- #
    # hippocampus
    hipp_path="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-hippocampusBL.nii.gz 
    mri_binarize --i $aparcaseg_mni --match 17 53 --o $hipp_path
    # combined caudate + putamen
    striatum_path="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-caudate+putamen.nii.gz
    mri_binarize --i $aparcaseg_mni --match 11 12 50 51 --o $striatum_path
    # lateral occipital
    loc_path="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-loc.nii.gz
    mri_binarize --i $aparcaseg_mni --match 1011 2011 --o $loc_path
    # vmPFC
    vmpfc_path="$anat_dir"/"$sub_id"_space-MNI152NLin2009cAsym_desc-vmpfc.nii.gz
    mri_binarize --i $aparcaseg_mni --match 1014 2014 1026 2026 --o $vmpfc_path

    # ---- Copy ROIs into initial fmriprep directory too ---- #
    alt_anat_dir="$ALT_ROOT/$sub_id/anat"
    cp $aparcaseg_mni $hipp_path $striatum_path $vmpfc_path "$alt_anat_dir/" 
done