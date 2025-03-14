#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmri
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err
#SBATCH --time=3:00:00
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

### FIRST LEVEL
# Loop through all GLMs for this subject
for FSF in $BASEDIR/scripts/glms/csi_model*.fsf; do # run each GLM actively in this folder
    model=$(basename "$FSF" .fsf)
    for rundir in "$SUBJ_DIR"/hybrid_r?; do
        r=$(echo "$rundir" | grep -oP 'hybrid_r[1-5]' | cut -c9) # Extract run number
        if [ -e "$BASEDIR"/behavior/"$SUBJ_ID"_output/EV_files/FB_pe_run"$r".txt ]; then
            if [ -e "$SUBJ_DIR/hybrid_r$r/$model.feat/thresh_zstat1.nii.gz" ]; then
                echo "Already completed subject $SUBJ_ID, run $r - skipping..."
            else
                echo "Running GLM $model for subject $SUBJ_ID, run $r"
                bash $BASEDIR/scripts/run_1st_level.sh $FSF $SUBJ_ID $r
            fi
        else 
            echo "No behavioral files for subject $SUBJ_ID, run $r - skipping..."
        fi
    done

    ### SUBJECT LEVEL
    fsf=$(realpath "$BASEDIR/scripts/glms/subject_fixed_effects.fsf")
    sub=$SUBJ_ID

    output="$BASEDIR/group_analyses/Subject_Level_FixEff/${model}_${SUBJ_ID}.gfeat"
    if [ -e $output/cope1.feat/stats/zstat1.nii.gz ]; then
        echo Fixed effects model already run for sub $sub, located at $output

    else

        ### copy reg files from preprocessing output to lower level dirs
        for r in "$BASEDIR"/TCST0"$sub"/hybrid_r?/preproc_6mm_6del_100s_mc.feat/reg/; do
            run_id=$(basename "$(dirname "$(dirname "$r")")") # "hybrid_r1" e.g.

            rm -rf "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/"
            #### if we're working with (already MNI) fmriprep data, we need to do some hack-y stuff to stop FSL from re-registering
            if [[ "$model" == *fmriprep ]]; then
                mkdir "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/"
                # 1. replace mat transforms with identity matrix
                yes | cp /burg/dslab/users/csi2108/mri_utils/ident.mat "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/example_func2highres.mat"
                yes | cp /burg/dslab/users/csi2108/mri_utils/ident.mat "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/highres2standard.mat"
                # 2. replace standard image with mean functional image
                yes | cp $BASEDIR/TCST0$sub/$run_id/$model.feat/mean_func.nii.gz $BASEDIR/TCST0$sub/$run_id/$model.feat/reg/standard.nii.gz
                yes | cp $BASEDIR/TCST0$sub/$run_id/$model.feat/mean_func.nii.gz $BASEDIR/TCST0$sub/$run_id/$model.feat/reg/highres.nii.gz
                updatefeatreg $BASEDIR/TCST0$sub/$run_id/$model.feat/
            else 
                # copy the reg directory from preprocessing
                cp -R "$r" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg" # copy reg files
                # replace a few with the bravo outputs
                yes | cp "$BASEDIR/TCST0$sub/structural/bravo.anat/T1_to_MNI_lin.mat" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/highres2standard.mat"
                yes | cp "$BASEDIR/TCST0$sub/structural/bravo.anat/T1_to_MNI_nonlin_field.nii.gz" "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/highres2standard_warp.nii.gz"
                yes | cp $(realpath "$BASEDIR/../mri_utils/MNI152_T1_2mm_brain.nii.gz") "$BASEDIR/TCST0$sub/$run_id/$model.feat/reg/standard.nii.gz"
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

        # replace stuff for the subject (17) with only 4 runs
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