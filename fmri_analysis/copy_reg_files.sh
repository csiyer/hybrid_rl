feat=csi_model1.feat
FSL_DIR="/Users/chrisiyer/fsl"
source_base="/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri"
target_base="/Volumes/shohamy-locker/chris/hybrid_mri_CSI"

for s in ${source_base}/TCST0*/; do
	subj_id=$(basename "$s")
	t="${target_base}/${subj_id}"

	if [[ -d "$t" ]]; then
        for r in $s/hybrid_r?/preproc_6mm_6del_100s_mc.feat/reg/; do
            run_id=$(basename "$(dirname "$(dirname "$r")")")
            if [[ ! -e "$t/$run_id/$feat/reg/example_func2standard.mat" ]]; then
                echo Subject $subj_id, run $run_id
                cp -R "$r" "$t/$run_id/$feat/reg"
                cp "$s/structural/bravo.anat/T1_to_MNI_lin.mat" "$t/$run_id/$feat/reg/highres2standard.mat"
                cp "$s/structural/bravo.anat/T1_to_MNI_nonlin_field.nii.gz" "$t/$run_id/$feat/reg/highres2standard_warp.nii.gz"
                cp "$FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz" "$t/$run_id/$feat/reg/standard.nii.gz"
                updatefeatreg "$t/$run_id/$feat/"
            fi
        done
    else
        echo "Warning: Target folder $t does not exist."
    fi
done