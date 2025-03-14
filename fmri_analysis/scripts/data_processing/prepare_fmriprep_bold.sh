#!/bin/bash

#### masking, smoothing
# because SUSAN is extremely lame and needs a manually calculated threshold to do smoothing, most of the work is that
# 1. Get intensity threshold for smoothing
#       - apply the brain mask to unsmoothed data 
#       - get the 98th percentile of image intensity of this masked data
#       - divide by 10 (this is the background threshold)
#       - make a mask that thresholds the data at this value 
#       - get the median intensity
#       - multiply by 0.75 -> this is the smoothing threshold SUSAN wants
# 2. Smooth with SUSAN
# 3. Apply brain mask to smoothed data


# Ensure we have the correct number of arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <BOLD_image> <brain_mask> <output_path>"
    exit 1
fi
BOLD_DATA=$1
BRAIN_MASK=$2
OUTPUT_PATH=$3

################# CALCULATING INTENSITY THRESHOLD

# Step 1: Apply the brain mask
MASKED_DATA="${OUTPUT_PATH}/bold_masked.nii.gz"
fslmaths $BOLD_DATA -mas $BRAIN_MASK $MASKED_DATA

# Step 2: Get the 98th percentile from the masked data
P98=$(fslstats $MASKED_DATA -p 98)

# Step 3: Divide this value by 10
THR_VALUE=$(echo "$P98 / 10" | bc -l)

# Step 4: Create a minimum-threshold binary mask
TEMP_MASK="${OUTPUT_PATH}/temp_mask.nii.gz"
fslmaths $MASKED_DATA -thr $THR_VALUE -Tmin -bin $TEMP_MASK -odt char

# Step 5: Get the median (50th percentile) value from the original data, using the temp mask
P50=$(fslstats $BOLD_DATA -k $TEMP_MASK -p 50)

# Step 6: Multiply the median by 0.75 to get the final threshold
FINAL_THRESHOLD=$(echo "$P50 * 0.75" | bc -l)

# Step 7: Run SUSAN smoothing
SMOOTHED_DATA="${OUTPUT_PATH}/bold_susan.nii.gz"
SMOOTHING_KERNEL_FWHM=6
SMOOTHING_SIGMA=$(echo "$SMOOTHING_KERNEL_FWHM/2.355" | bc -l)
susan $BOLD_DATA $FINAL_THRESHOLD $SMOOTHING_SIGMA 3 1 1 $BRAIN_MASK $FINAL_THRESHOLD $SMOOTHED_DATA

# Step 8: Apply the brain mask to the smoothed data
FINAL_OUTPUT="${OUTPUT_PATH}/fmriprep_bold_smoothed_masked.nii.gz"
fslmaths $SMOOTHED_DATA -mas $BRAIN_MASK $FINAL_OUTPUT

# Cleanup intermediate files
rm -f $MASKED_DATA $TEMP_MASK $SMOOTHED_DATA "$SMOOTHED_DATA"_usan_size.nii.gz

echo "Smoothing complete, output saved to: $FINAL_OUTPUT"
