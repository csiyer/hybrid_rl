Modifications of https://github.com/rgerraty/hybrid_reinforcement_learning/tree/master?tab=readme-ov-file

Chris Iyer
Updated 2/3/25


### Run 1st-Level GLM 
```.bash
fsf=csi_inc_ep_lik_encfb.fsf
for i in /Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/TCST0*/hybrid_r?/preproc_6mm_6del_100s_mc.feat/filtered_func_data.nii.gz; 
	do 
	s=$(echo $i | cut -c39-40); 
	r=$(echo $i | cut -c 50);
	bash /Users/chrisiyer/_Current/lab/code/hybrid_rl/run_1st_level.sh $i /Users/chrisiyer/_Current/lab/code/hybrid_rl/$fsf $s $r;
done
```

