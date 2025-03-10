#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmri
#SBATCH --output=logs/group_%a.out
#SBATCH --error=logs/group_%a.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --array=0-4  # 5 different GLMs

module load FSL/6.0.5.2

BASEDIR=/burg/dslab/users/csi2108/hybrid_mri_CSI
fsf=$(realpath "$BASEDIR/../scripts/glms/group_mixed_effects.fsf")
example_first_level_dir="$BASEDIR/TCST002/hybrid_r1"


models_to_run=($BASEDIR/../scripts/glms/csi_model*) # all active moddels

if (( SLURM_ARRAY_TASK_ID < ${#models_to_run[@]} )); then

    model=$(basename "${models_to_run[$SLURM_ARRAY_TASK_ID]}" .fsf)
    echo "Processing model $model"

    # make output dir if necessary
    model_out="$BASEDIR/group_analyses/Group_Level_MixEff/$model"
    if [ ! -d $model_out ]; then
        mkdir "$model_out"
    fi

    # get the contrast names associated with this model
    contrast_names=($(awk -F' ' '/ContrastName/ {print $2}' "$example_first_level_dir/$model.feat/design.con"));

    # for each contrast
    for  i in ${!contrast_names[@]}; do 
        contrast=${contrast_names[$i]};
        cope_num=$(($i + 1)); # which number is the contrast in the lower level dirs (e.g. cope1.nii.gz)

        ## make template FSF file
        TMP_FSF="$BASEDIR/group_analyses/Group_Level_MixEff/${model}_${contrast}_tmp.fsf"
        sed -e "s:XXMODELXX:${model}:g" \
            -e "s:XXCONTRASTXX:${contrast}:g" \
            -e "s:XXCOPENUMXX:${cope_num}:g" \
            $fsf > "$TMP_FSF"

        ## run the analysis
        feat $TMP_FSF;
        rm -f $TMP_FSF;
    done

else
    echo "No model to run, exiting script."
fi


