#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmriprep
#SBATCH --output=log.out
#SBATCH --error=log.err
#SBATCH --time=2:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8

module load singularity 

SUBJECT_ID="hybrid01"

echo "Processing subject: $SUBJECT_ID"

singularity run --home $HOME --cleanenv \
    /burg/dslab/users/csi2108/fmriprep-24.1.1.simg \
    /burg/dslab/users/csi2108/hybrid_mri_bids /burg/dslab/users/csi2108/hybrid_mri_fmriprep \
    participant -w /burg/home/csi2108/work/ --participant-label $SUBJECT_ID \
    --nthreads 8  --fs-license-file /burg/dslab/users/csi2108/freesurfer_license.txt --fs-no-reconall