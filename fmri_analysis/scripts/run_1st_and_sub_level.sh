#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmri
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=2:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --array=0-30  # 31 valid subjects (index-based)

module load FSL/6.0.5.2

BASEDIR=/burg/dslab/users/csi2108/hybrid_mri_CSI
# get subject number for this job 
SUBJECTS=(2 4 5 6 7 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34)
SUBJ_ID=$(printf "%02d" ${SUBJECTS[$SLURM_ARRAY_TASK_ID]})
SUBJ_DIR="$BASEDIR/TCST0$SUBJ_ID"

echo "Processing subject: $SUBJ_ID"
# Loop through all 5 GLMs for this subject
for FSF in /burg/dslab/users/csi2108/scripts/glms/*rtdur*; do # run each GLM

    model=$(basename $FSF | cut -c1-16) ## CAREFUL!

    ### FIRST LEVEL - for each run
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

    ### SUBJECT LEVEL
    fsf=$(realpath "$BASEDIR/../scripts/glms/subject_fixed_effects.fsf")
    sub=$SUBJ_ID

    output="$BASEDIR/group_analyses/Subject_Level_FixEff/${model}_${SUBJ_ID}.gfeat"
    if [ -e $output/cope1.feat/stats/zstat1.nii.gz ]; then
        echo Fixed effects model already run for sub $sub, located at $output
    
    else
        ### copy reg files from preprocessing directory to the first level dirs
        for r in "$BASEDIR"/TCST0"$sub"/hybrid_r?/preproc_6mm_6del_100s_mc.feat/reg/; do
            run_id=$(basename "$(dirname "$(dirname "$r")")") # "hybrid_r1" e.g.
            if [ ! -e "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/example_func2standard.mat" ]; then
                # files haven't already been copied
                cp -R "$r" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg" # copy reg files
                # replace a few with the bravo outputs
                cp "$BASEDIR/TCST0$sub/structural/bravo.anat/T1_to_MNI_lin.mat" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/highres2standard.mat"
                cp "$BASEDIR/TCST0$sub/structural/bravo.anat/T1_to_MNI_nonlin_field.nii.gz" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/highres2standard_warp.nii.gz"
                cp "$BASEDIR/MNI152_T1_2mm_brain.nii.gz" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/standard.nii.gz"
                updatefeatreg "$BASEDIR/TCST0$sub/$run_id/$model.feat/" # update other files in the reg folder
            fi
        done

        ## calculate how many run inputs (sub TCST017 only has 4 runs)
        run_count=$(find "$BASEDIR"/TCST0"$sub"/hybrid_r?/"$model".feat -maxdepth 0 -type d 2>/dev/null | wc -l)
        ## calculate how many contrast inputs
        cope_count=$(ls $BASEDIR/TCST0$sub/$run_id/$model.feat/stats/cope?.nii.gz 2>/dev/null | wc -l)

        ## make template FSF file
        TMP_FSF="$BASEDIR/group_analyses/Subject_Level_FixEff/${sub}_${model}_tmp.fsf"
        sed -e "s:XXSUBXX:${sub}:g" \
            -e "s:XXMODELXX:${model}:g" \
            -e "s:XXVOLSXX:${run_count}:g" \
            -e "s:XXCONTRASTSXX:${cope_count}:g" \
            $fsf > "$TMP_FSF"

        # replace stuff for the subject with only 4 runs
        if [ $run_count -eq 4 ]; then
            echo changing run count to $run_count for sub $sub
            # change "hybrid_r4" to "hybrid_r5" in the input -- LINUX SPECIFIC SYNTAX
            sed -i 's|hybrid_r4|hybrid_r5|g' "$TMP_FSF"
            # comment out these lines
            sed -i 's|^set feat_files(5)|# &|' \
                -e 's|^set fmri(evg5.1)|# &|' \
                -e 's|^set fmri(groupmem.5)|# &|' "$TMP_FSF"
        fi

        ## run the analysis
        feat $TMP_FSF;

        ## remove template fsf and reg files
        rm -f $TMP_FSF;
        rm -rf "$BASEDIR/TCST0$sub/hybrid_r?/$model.feat/reg/"
    fi
done



