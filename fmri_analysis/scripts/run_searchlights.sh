#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_searchlight
#SBATCH --output=logs/searchlight_%A_%a.out
#SBATCH --error=logs/searchlight_%A_%a.err
#SBATCH --time=1:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=8
#SBATCH --array=1-31  # Submitting 31 jobs, one per subject

module load anaconda/3-2022.05
source /burg/opt/anaconda3-2022.05/bin/activate /burg/opt/anaconda3-2022.05/envs/brainiak
module load FSL/6.0.5.2

echo "Beginning subject $SLURM_ARRAY_TASK_ID"

echo "Encoding choice, opt-nonopt"
python /burg/dslab/users/csi2108/hybrid_mri_CSI/scripts/searchlight.py \
    --sub_num=$SLURM_ARRAY_TASK_ID \
    --enc_trial_type='choice' \
    --contrast='opt-nonopt'

echo "Encoding feedback, match-mismatch"
python /burg/dslab/users/csi2108/hybrid_mri_CSI/scripts/searchlight.py \
    --sub_num=$SLURM_ARRAY_TASK_ID \
    --enc_trial_type='fb' \
    --contrast='opt-nonopt'

echo "Encoding choice, match-mismatch"
python /burg/dslab/users/csi2108/hybrid_mri_CSI/scripts/searchlight.py \
    --sub_num=$SLURM_ARRAY_TASK_ID \
    --enc_trial_type='choice' \
    --contrast='match-mismatch'

echo "Encoding feedback, match-mismatch"
python /burg/dslab/users/csi2108/hybrid_mri_CSI/scripts/searchlight.py \
    --sub_num=$SLURM_ARRAY_TASK_ID \
    --enc_trial_type='fb' \
    --contrast='match-mismatch'
