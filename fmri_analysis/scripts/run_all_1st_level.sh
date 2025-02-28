#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmri
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=10:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --array=0-30  # 31 valid subjects (index-based)

module load FSL/6.0.5.2

# get subject number for this job 
SUBJECTS=(2 4 5 6 7 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34)
SUBJ_ID=$(printf "%02d" ${SUBJECTS[$SLURM_ARRAY_TASK_ID]})
SUBJ_DIR="/burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0$SUBJ_ID"

echo "Processing subject: $SUBJ_ID"
FSF=/burg/dslab/users/csi2108/scripts/glms/csi_model5.fsf
# Loop through all 5 GLMs for this subject
for FSF in /burg/dslab/users/csi2108/scripts/glms/*; # run each GLM
do
    model=$(basename $FSF | cut -c1-10)
    for i in "$SUBJ_DIR"/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz;
    do
        r=$(echo $i | cut -c58)  # Extract run number

        if [ -e /burg/dslab/users/csi2108/hybrid_mri_CSI/behavior/"$SUBJ_ID"_output/EV_files/FB_pe_run"$r".txt ]; then
            if [ -e "$SUBJ_DIR/hybrid_r$r/$model.feat/thresh_zstat1.nii.gz" ]; then
                echo "Already completed subject $SUBJ_ID, run $r - skipping..."
            else
                echo "Running GLM $model for subject $SUBJ_ID, run $r"
                bash /burg/dslab/users/csi2108/scripts/run_1st_level.sh $i $FSF $SUBJ_ID $r
            fi
        else 
            echo "No behavioral files for subject $SUBJ_ID, run $r - skipping..."
        fi
    done
done

