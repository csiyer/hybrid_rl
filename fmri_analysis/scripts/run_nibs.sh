#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_nibs
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=04:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8
#SBATCH --array=1-31  # Submitting 31 jobs, one per subject

SUBJECT_ID=$(printf "hybrid%02d" ${SLURM_ARRAY_TASK_ID})
echo "Processing subject: $SUBJECT_ID"

module load anaconda
source activate /burg/dslab/users/jdn2133/my-envs/nibsenv

nibs \
  --work-dir /burg/dslab/users/csi2108/work \
  --estimator lss \
  --high-pass 0.008 \
  --hrf-model glover \
  --confounds trans_x trans_y trans_z rot_x rot_z rot_z \
      trans_x_derivative1 trans_y_derivative1 trans_z_derivative1 rot_x_derivative1 rot_y_derivative1 rot_z_derivative1 \
      trans_x_power2 trans_y_power2 trans_z_power2 rot_x_power2 rot_y_power2 rot_z_power2 \
      trans_x_derivative1_power2 trans_y_derivative1_power2 trans_z_derivative1_power2 rot_x_derivative1_power2 rot_y_derivative1_power2 rot_z_derivative1_power2 \
  --participant-label $SUBJECT_ID \
  --description-label preproc \
  --space-label MNI152NLin2009cAsym \
  --nthreads 8 \
  /burg/dslab/users/csi2108/hybrid_mri_bids \
  fmriprep \
  /burg/dslab/users/csi2108/hybrid_mri_bids/derivatives \
  participant