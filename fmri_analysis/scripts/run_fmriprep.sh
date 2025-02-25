#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmriprep
#SBATCH --output=hybrid_mri_fmriprep/logs/fmriprep_%A_%a.out
#SBATCH --error=hybrid_mri_fmriprep/logs/fmriprep_%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --array=1-31  # Submitting 31 jobs, one per subject

module load singularity 

SUBJECT_ID=$(printf "hybrid%02d" ${SLURM_ARRAY_TASK_ID})

echo "Processing subject: $SUBJECT_ID"

singularity run --home $HOME --cleanenv \
    /burg/dslab/users/csi2108/fmriprep-24.1.1.simg \
    /burg/dslab/users/csi2108/hybrid_mri_bids /burg/dslab/users/csi2108/hybrid_mri_fmriprep \
    participant -w /burg/dslab/users/csi2108/work/ --participant-label $SUBJECT_ID \
    --nthreads 8  --fs-license-file /burg/dslab/users/csi2108/freesurfer_license.txt --fs-no-reconall