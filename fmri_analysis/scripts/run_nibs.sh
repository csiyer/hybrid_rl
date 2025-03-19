#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_nibs
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --array=1-31  # Submitting 31 jobs, one per subject

module load singularity 

SUBJECT_ID=$(printf "hybrid%02d" ${SLURM_ARRAY_TASK_ID})

echo "Processing subject: $SUBJECT_ID"

singularity run --cleanenv \
  -B /burg/dslab/users/csi2108/hybrid_mri_bids:/bids_dir \
  -B /burg/dslab/users/csi2108/hybrid_mri_bids/derivatives/nibs:/out_dir \
  -B /burg/dslab/users/csi2108/work:/work_dir \
  /burg/dslab/users/csi2108/mri_utils/nibetaseries-v0.6.0.simg \
    -w /work_dir \
    --estimator lss \
    --high-pass 0.0078125 \
    --hrf-model glover \
    --confounds trans_x trans_y trans_z rot_x rot_z rot_z \
        trans_x_derivative1 trans_y_derivative1 trans_z_derivative1 rot_x_derivative1 rot_y_derivative1 rot_z_derivative1 \
        trans_x_power2 trans_y_power2 trans_z_power2 rot_x_power2 rot_y_power2 rot_z_power2 \
        trans_x_derivative1_power2 trans_y_derivative1_power2 trans_z_derivative1_power2 rot_x_derivative1_power2 rot_y_derivative1_power2 rot_z_derivative1_power2 \
    --participant-label $SUBJECT_ID \
    --description-label preproc_bold \
    --sp MNI152NLin2009cAsym \
    --nthreads 8 \
    /bids_dir \
    fmriprep \
    /out_dir \
    participant