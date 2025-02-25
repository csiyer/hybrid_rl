# fsf=/Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/glms/csi_model1.fsf # CHANGE THIS!

for fsf in /burg/dslab/users/csi2108/scripts/glms/*: # /Users/chrisiyer/_Current/lab/code/hybrid_rl/fmri_analysis/glms/*;
	do
	echo Beginning $fsf
	for i in /burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz; # /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri
		do 
		s=$(echo $i | cut -c72-73); 
		r=$(echo $i | cut -c 83);
		if [ -e /burg/dslab/users/csi2108/hybrid_mri_CSI/behavior/"$s"_output/EV_files/FB_pe_run"$r".txt ];
			then 
			if [ -e /burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0"$s"/hybrid_r"$r"/csi_model1.feat/thresh_zstat1.nii.gz ];
				then
				echo Already completed subject "$s", run "$r" - skipping...
			else
				echo Running for subject "$s", run "$r"
				bash /burg/dslab/users/csi2108/scripts/run_1st_level.sh $i $fsf $s $r;
			fi;
		else 
			echo no RL behavioral files for subject $s, run $r - skipping... ;
		fi;
	done
done