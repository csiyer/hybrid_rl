#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_bids
#SBATCH --output=logs/bids_%a.out
#SBATCH --error=logs/bids_%a.err
#SBATCH --time=01:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
#SBATCH --array=1-32

module load FSL/6.0.5.2
set -euo pipefail

src_root="/burg/dslab/users/csi2108/hybrid_mri_CSI"
dst_root="/burg/dslab/users/csi2108/hybrid_mri_bids/derivatives/fmriprep"
map_file="$src_root/n31_subject_list.txt"
mkdir -p "$dst_root"
target_space_label="MNI152NLin2009cAsym"

conf_headers="trans_x	trans_y	trans_z	rot_x	rot_y	rot_z	\
trans_x_derivative1	trans_y_derivative1	trans_z_derivative1	rot_x_derivative1	rot_y_derivative1	rot_z_derivative1	\
trans_x_power2	trans_y_power2	trans_z_power2	rot_x_power2	rot_y_power2	rot_z_power2	\
trans_x_derivative1_power2	trans_y_derivative1_power2	trans_z_derivative1_power2	rot_x_derivative1_power2	rot_y_derivative1_power2	rot_z_derivative1_power2"

# Read subject mapping into arrays
orig_list=()
bids_list=()
while IFS=, read -r orig bids; do
    [[ "$orig" == "original" ]] && continue
    orig_list+=("$orig")
    bids_list+=("$bids")
done < "$map_file"

# Determine subject index from SLURM_ARRAY_TASK_ID (1-based)
IDX=$((SLURM_ARRAY_TASK_ID - 1))
orig=${orig_list[$IDX]}
bids=${bids_list[$IDX]}
echo "Processing subject: $orig → $bids"

for run in {1..5}; do
    echo "Beginning run $run"
    src_dir="$src_root/${orig}/hybrid_r${run}/preproc_6mm_6del_100s_mc.feat"
    nifti_src="$src_dir/filtered_func_data.nii.gz"
    mask_src="$src_dir/mask.nii.gz"
    conf_src="$src_dir/mc/extended_confs_24par.txt"

    if [ -e "$nifti_src" ]; then
        func_dir="$dst_root/${bids}/func"
        mkdir -p "$func_dir"

        # Predefine transforms + reference
        FUNC2HIGHRES="$src_dir/reg/example_func2highres.mat"
        HIGHRES2STANDARD_WARP="$src_dir/reg/highres2standard_warp.nii.gz"
        MNI_REF="$FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz"

        # BOLD
        nifti_dst="${func_dir}/${bids}_task-main_run-${run}_space-${target_space_label}_bold.nii.gz"
        if [ ! -e "$nifti_dst" ]; then
            applywarp --ref="$MNI_REF" \
                      --in="$nifti_src" \
                      --warp="$HIGHRES2STANDARD_WARP" \
                      --premat="$FUNC2HIGHRES" \
                      --out="$nifti_dst"
        fi

        # Brain mask
        mask_dst="${func_dir}/${bids}_task-main_run-${run}_space-${target_space_label}_desc-brain_mask.nii.gz"
        if [ ! -e "$mask_dst" ]; then
            applywarp --ref="$MNI_REF" \
                      --in="$mask_src" \
                      --warp="$HIGHRES2STANDARD_WARP" \
                      --premat="$FUNC2HIGHRES" \
                      --interp=nn \
                      --out="$mask_dst"
            # rm -f "$mask_src"
        fi

        # Confounds
        conf_dst="${func_dir}/${bids}_task-main_run-${run}_space-${target_space_label}_desc-confounds_regressors.tsv"
        {
            echo -e "$conf_headers"
            cat "$conf_src"
        } | tr -s ' ' '\t' > "$conf_dst"
    fi
done

echo "finished! outputs at $dst_root"
