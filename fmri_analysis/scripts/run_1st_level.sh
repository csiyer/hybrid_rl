#!/bin/bash

input=$(realpath $1)
fsf=$(realpath $2)
sub=$3
run=$4

if [ ! -e $input ];
	then
	echo $input does not exist for sub $sub, run $run !
elif [ -z $run ];
	then
	echo Usage\:
	echo run_1st_level.sh \<input nifti\> \<template fsf\> \<subject number\> \<run number\>
else
	output=$(dirname $1)/../$(basename $2 .fsf).feat

		if [ -e $output/stats/res4d.nii.gz ];
			then 
			echo $output completed already for sub $sub, run $run, model $(basename $fsf)
		else
			nvols=$(fslinfo $input | grep dim4 | grep -v pix | awk '{ print $2 }');
			TMP_FSF=$(dirname $1)/../tmp.fsf
			sed -e 's:XXSUBXX:'$sub':g' -e 's:XXRUNXX:'$run':g' -e 's:XXVOLSXX:'$nvols':g' -e 's:XXINXX:'$input':g'<$fsf>$TMP_FSF;
			feat $TMP_FSF;
			rm -f $TMP_FSF;
		fi
fi