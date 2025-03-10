#!/bin/bash

# input=$(realpath $1)
fsf=$(realpath $1)
sub=$3
run=$4

# if [ ! -e $input ];
# 	then
# 	echo $input does not exist for sub $sub, run $run !

runpath=/burg/dslab/users/csi2108/hybrid_mri_CSI/$sub/hybrid_r$run

if [ -z $run ];
	then
	echo Usage\:
	echo run_1st_level.sh \<template fsf\> \<subject number\> \<run number\>
else
	output=$runpath/$(basename $1 .fsf).feat

		if [ -e $output/stats/res4d.nii.gz ];
			then 
			echo $output completed already for sub $sub, run $run, model $(basename $fsf)
		else
			# nvols=$(fslinfo $input | grep dim4 | grep -v pix | awk '{ print $2 }');
			TMP_FSF=$runpath/tmp.fsf
			sed -e 's:XXSUBXX:'$sub':g' -e 's:XXRUNXX:'$run':g'<$fsf>$TMP_FSF;
			feat $TMP_FSF;
			rm -f $TMP_FSF;
		fi
fi