#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmri
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --array=0-30  # 31 valid subjects (index-based)

module load FSL/6.0.5.2

# get subject number for this job 
SUBJECTS=(2 4 5 6 7 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34)
SUBJ_ID=$(printf "%02d" ${SUBJECTS[$SLURM_ARRAY_TASK_ID]})
SUBJ_DIR="/burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0$SUBJ_ID"

echo "Processing subject: $SUBJ_ID"

# Loop through all 5 GLMs for this subject
for FSF in /burg/dslab/users/csi2108/scripts/glms/*; # run each GLM
do
	model=$(echo $FSF | cut -c40-49)
    for i in "$SUBJ_DIR"/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz;
    do
        r=$(echo $i | cut -c58)  # Extract run number

        if [ -e /burg/dslab/users/csi2108/hybrid_mri_CSI/behavior/"$SUBJ_ID"_output/EV_files/FB_pe_run"$r".txt ]; then
            if [ -e "$SUBJ_DIR/hybrid_r$r/$model.feat/thresh_zstat1.nii.gz" ]; then
                echo "Already completed subject $SUBJ_ID, run $r - skipping..."
            else
                echo "Running GLM: $FSF for subject $SUBJ_ID, run $r"
                bash /burg/dslab/users/csi2108/scripts/run_1st_level.sh $i $FSF $SUBJ_ID $r
            fi
        else 
            echo "No RL behavioral files for subject $SUBJ_ID, run $r - skipping..."
        fi
    done
done

################ local, serial version
# for fsf in /burg/dslab/users/csi2108/scripts/glms/*: # /Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/glms/*;
# 	do
# 	echo Beginning $fsf
# 	for i in /burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz; # /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri
# 		do 
# 		s=$(echo $i | cut -c72-73); 
# 		r=$(echo $i | cut -c 83);
# 		if [ -e /burg/dslab/users/csi2108/hybrid_mri_CSI/behavior/"$s"_output/EV_files/FB_pe_run"$r".txt ];
# 			then 
# 			if [ -e /burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0"$s"/hybrid_r"$r"/csi_model1.feat/thresh_zstat1.nii.gz ];
# 				then
# 				echo Already completed subject "$s", run "$r" - skipping...
# 			else
# 				echo Running for subject "$s", run "$r"
# 				bash /burg/dslab/users/csi2108/scripts/run_1st_level.sh $i $fsf $s $r;
# 			fi;
# 		else 
# 			echo no RL behavioral files for subject $s, run $r - skipping... ;
# 		fi;
# 	done
# done