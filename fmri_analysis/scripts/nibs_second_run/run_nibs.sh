#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_nibs
#SBATCH --output=logs/nibs.out
#SBATCH --error=logs/nibs.err
#SBATCH --time=08:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=8

module load anaconda
source activate /burg/dslab/users/csi2108/envs/nibsenv

work_dir=/burg/dslab/users/csi2108/work
mkdir -p $work_dir

for subnum in {1..31}; do
    SUBJECT_ID=$(printf "hybrid%02d" ${subnum})
    echo "Processing subject: $SUBJECT_ID"

    nibs \
        --work-dir $work_dir \
        --estimator lss \
        --high-pass 0.008 \
        --hrf-model glover \
        --confounds trans_x trans_y trans_z rot_x rot_y rot_z \
                    trans_x_derivative1 trans_y_derivative1 trans_z_derivative1 rot_x_derivative1 rot_y_derivative1 rot_z_derivative1 \
                    trans_x_power2 trans_y_power2 trans_z_power2 rot_x_power2 rot_y_power2 rot_z_power2 \
                    trans_x_derivative1_power2 trans_y_derivative1_power2 trans_z_derivative1_power2 rot_x_derivative1_power2 rot_y_derivative1_power2 rot_z_derivative1_power2 \
        --participant-label $SUBJECT_ID \
        --space-label MNI152NLin2009cAsym \
        --nthreads 8 \
        /burg/dslab/users/csi2108/hybrid_mri_bids \
        fmriprep \
        /burg/dslab/users/csi2108/hybrid_mri_bids/derivatives \
        participant

    # --database-path /burg/dslab/users/csi2108/hybrid_mri_bids/bids_db \
done

rm -rf $work_dir
echo "finished NIBS, beginning ROI extraction"
# now, we will apply the vmPFC mask and store the patterns specifically
/burg/opt/anaconda3-2022.05/envs/brainiak/bin/python \
    /burg/dslab/users/csi2108/extract_patterns.py