fsf=csi_model1.fsf
for i in /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/TCST0*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz; 
	do 
	s=$(echo $i | cut -c72-73); 
	r=$(echo $i | cut -c 83);
	if [ -e /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/behavior/"$s"_output/EV_files/FB_pe_run"$r".txt ];
		then 
		if [ -e /Volumes/shohamy-locker/chris/hybrid_mri_CSI/TCST0"$s"/hybrid_r"$r"/csi_model1.feat/thresh_zstat1.nii.gz ];
			then
			echo Already completed subject "$s", run "$r" -- skipping...
		else
			echo Running for subject "$s", run "$r"
			bash /Users/chrisiyer/_Current/lab/code/hybrid_rl/run_1st_level.sh $i /Users/chrisiyer/_Current/lab/code/hybrid_rl/$fsf $s $r;
		fi;
	else 
		echo no RL behavioral files for $i ;
	fi;
done
