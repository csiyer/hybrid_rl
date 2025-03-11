#!/bin/bash

# input=$(realpath $1)
fsf=$(realpath $1)
sub=$2
run=$3

# if [ ! -e $input ];
# 	then
# 	echo $input does not exist for sub $sub, run $run !

runpath=/burg/dslab/users/csi2108/hybrid_mri_CSI/TCST0$sub/hybrid_r$run

if [ -z $run ];
	then
	echo Usage\:
	echo run_1st_level.sh \<template fsf\> \<subject number\> \<run number\>
else
	output=$runpath/$(basename $fsf .fsf).feat
		if [ -e $output/stats/res4d.nii.gz ];
			then 
			echo $(basename $fsf) completed already for sub $sub, run $run
		else
			# nvols=$(fslinfo $input | grep dim4 | grep -v pix | awk '{ print $2 }');
			TMP_FSF="$runpath"/tmp.fsf
			sed -e 's:XXSUBXX:'$sub':g' -e 's:XXRUNXX:'$run':g'<$fsf>$TMP_FSF;
			feat $TMP_FSF;
			rm -f $TMP_FSF;
		fi
fi