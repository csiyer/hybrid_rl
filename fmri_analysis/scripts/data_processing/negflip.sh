#!/bin/bash

input=$1
dir=$(dirname $input)
dir_out=$(dirname $dir)
fname=$(basename $input .nii.gz)
neg="$dir"/"$fname"_neg.nii.gz
thresh="$dir_out"/thresh_"$fname"_neg.nii.gz

fslmaths $input -mul -1 $neg

smooth_output=$(smoothest -z $neg -m "$dir_out"/mask.nii.gz)
dlh=$(echo "$smooth_output" | awk '/DLH/ {print $2}')
volume=$(echo "$smooth_output" | awk '/VOLUME/ {print $2}')

cluster -i $neg -t 2.3 -o $thresh --dlh="$dlh" --volume="$volume" --pthresh=0.05 