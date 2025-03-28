#!/bin/bash

# Set the directory containing the masks
MASK_DIR="/Users/chrisiyer/Downloads/masks/sub_masks"
OUTPUT_MASK="/Users/chrisiyer/Downloads/masks/sub_masks/mask_group80.nii.gz"

# Count the number of masks (subjects)
NUM_SUBJECTS=$(ls ${MASK_DIR}/*.nii* | wc -l)
echo "Found $NUM_SUBJECTS subject masks."

# Create a temporary file to accumulate the sum of masks
TEMP_SUM="temp_mask_sum.nii.gz"
FIRST_MASK=true

# Loop over each mask and add to the sum
for MASK in ${MASK_DIR}/*.nii*; do
    if $FIRST_MASK; then
        cp "$MASK" "$TEMP_SUM"
        FIRST_MASK=false
    else
        fslmaths "$TEMP_SUM" -add "$MASK" "$TEMP_SUM"
    fi
done

# Compute threshold value (80% of subjects)
THRESH=$(echo "$NUM_SUBJECTS * 0.8" | bc -l)
echo "Applying threshold of $THRESH (80% of $NUM_SUBJECTS)"

# Apply threshold and binarize to get the final group mask
fslmaths "$TEMP_SUM" -thr "$THRESH" -bin "$OUTPUT_MASK"

# Clean up
rm "$TEMP_SUM"

echo "Group mask saved as $OUTPUT_MASK"
