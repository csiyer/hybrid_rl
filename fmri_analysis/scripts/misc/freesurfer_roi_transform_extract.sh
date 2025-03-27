#!/bin/bash

# this script does several things:
# 1. for some reason fmriprep did not output the aseg files that i wanted, 
#   so we had to take the raw freesurfer outputs and transform to MNI\
# 2. Extract L, R, and bilateral hippocampal ROIs (one per run)

ROOT=/burg/dslab/users/csi2108/hybrid_mri_bids/derivatives/fmriprep_anat
ALT_ROOT=/burg/dslab/users/csi2108/hybrid_mri_bids/derivatives/fmriprep

for subfolder in "$ROOT"/sub-hybrid??; do 
    sub_id=$(basename $subfolder)

    echo "Processing $sub_id"

    # Convert aseg.mgz to NIfTI
    aseg_nii="$ROOT/sourcedata/freesurfer/$sub_id/mri/aseg.nii.gz"
    if [ ! -f "$aseg_nii" ]; then
        echo "Converting aseg.mgz to NIfTI for $sub_id..."
        mri_convert "$ROOT"/sourcedata/freesurfer/"$sub_id"/mri/aseg.{mgz,nii.gz}
    else
        echo "aseg.nii.gz already exists for $sub_id, skipping conversion."
    fi

    # For each run, use that run's transformation to MNI space to resample the aseg file to MNI
    # fsnative -> T1w -> MNI

    for run_num in {1..5}; do  

        run_boldref="$ROOT"/"$sub_id"/func/"$sub_id"_task-main_run-"$run_num"_space-MNI152NLin2009cAsym_boldref.nii.gz

        if [ -f "$run_boldref" ]; then
        
            echo "Processing $sub_id, run $run_num"
            seg_file="$ROOT"/"$sub_id"/func/"$sub_id"_task-main_run-"$run_num"_space-MNI152NLin2009cAsym_seg-aseg_dseg.nii.gz

            # ---- Transform segementation to MNI ---- #
            antsApplyTransforms \
            -i "$aseg_nii" \
            -r "$run_boldref" \
            -o "$seg_file" \
            -n GenericLabel \
            -t "$ROOT"/"$sub_id"/anat/"$sub_id"_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5 \
            -t "$ROOT"/"$sub_id"/anat/"$sub_id"_from-fsnative_to-T1w_mode-image_xfm.txt

            # ---- Extract Hippocampal ROIs ---- #
            roi_dir="$ROOT/$sub_id/func/rois"
            mkdir -p "$roi_dir"

            l_file="$roi_dir"/"$sub_id"_run-"$run_num"_hippocampus_L.nii.gz
            r_file="$roi_dir"/"$sub_id"_run-"$run_num"_hippocampus_R.nii.gz
            bl_file="$roi_dir"/"$sub_id"_run-"$run_num"_hippocampus_BL.nii.gz

            # Left Hippocampus (Label 17)
            fslmaths "$seg_file" -thr 17 -uthr 17 "$l_file"
            # Right Hippocampus (Label 53)
            fslmaths "$seg_file" -thr 53 -uthr 53 "$r_file"
            # Bilateral Hippocampus (Left + Right)
            fslmaths "$seg_file" -thr 17 -uthr 17 -add "$seg_file" -thr 53 -uthr 53 "$bl_file"


            # ---- Copy into initial fmriprep directory too ---- #
            cp $seg_file "$ALT_ROOT"/"$sub_id"/func/"$sub_id"_task-main_run-"$run_num"_space-MNI152NLin2009cAsym_seg-aseg_dseg.nii.gz
            alt_roi_dir="$ALT_ROOT/$sub_id/func/rois"
            mkdir -p "$alt_roi_dir"
            cp $l_file "$alt_roi_dir"/"$sub_id"_run-"$run_num"_hippocampus_L.nii.gz
            cp $r_file "$alt_roi_dir"/"$sub_id"_run-"$run_num"_hippocampus_R.nii.gz
            cp $bl_file "$alt_roi_dir"/"$sub_id"_run-"$run_num"_hippocampus_BL.nii.gz

        else
            echo "No bold files found for $sub_id, run $run_num"
        fi
    done
done
