#!/bin/bash
#SBATCH --account=dslab
#SBATCH --job-name=csi_fmri
#SBATCH --output=logs/group.out
#SBATCH --error=logs/group.err
#SBATCH --time=08:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=4

module load FSL/6.0.5.2
BASEDIR=/burg/dslab/users/csi2108/hybrid_mri_CSI/group_analyses/Group_Level_MixEff
INPUT_DIR=/burg/dslab/users/csi2108/hybrid_mri_CSI/group_analyses/Subject_Level_FixEff
GROUP_MASK=/burg/dslab/users/csi2108/hybrid_mri_CSI/mask_group_thresh80.nii.gz
N_SUBJECTS=31
N_PERMUTATIONS=1000
cd $BASEDIR

# make design matrix
cat <<EOF > design.mat
/NumWaves 1
/NumPoints $N_SUBJECTS
/PPheights 1.0
/Matrix
$(for i in $(seq 1 $N_SUBJECTS); do echo "1"; done)
EOF

# Create one sided t contrast file
cat <<EOF > design.con
/NumWaves 1
/NumContrasts 1
/Matrix
1
EOF


# these are the models/contrasts i want to test at different thresholds:
# model 1: ep_lik (2), pe (6)
# model 2: Qchose (1), oldval (2)
# model 4: mem (1)

### model 1, ep_lik (2)
echo Beginning model1, eplik
model=csi_model1_v3_noold
output_dir=$BASEDIR/$model
mkdir -p $output_dir
cd $output_dir
cope_pattern=${model}_??.gfeat/cope2.feat/stats/cope1.nii.gz

# concatenate inputs
COPE_LIST=()
for file in $INPUT_DIR/$cope_pattern; do
    COPE_LIST+=("$file")
done
fslmerge -t all_copes.nii.gz "${COPE_LIST[@]}"

# run randomise
randomise \
  -i all_copes.nii.gz \
  -o eplik \
  -d $BASEDIR/design.mat \
  -t $BASEDIR/design.con \
  -m $GROUP_MASK \
  -n $N_PERMUTATIONS \
  -T # TFCE
rm -f all_copes.nii.gz


### model 1, pe (6)
echo Beginning model1, pe
cope_pattern=${model}_??.gfeat/cope6.feat/stats/cope1.nii.gz
COPE_LIST=()
for file in $INPUT_DIR/$cope_pattern; do
    COPE_LIST+=("$file")
done
fslmerge -t all_copes.nii.gz "${COPE_LIST[@]}"
randomise \
  -i all_copes.nii.gz \
  -o pe \
  -d $BASEDIR/design.mat \
  -t $BASEDIR/design.con \
  -m $GROUP_MASK \
  -n $N_PERMUTATIONS \
  -T # TFCE
rm -f all_copes.nii.gz


### model 2, qchose (1)
echo Beginning model2, qchose
model=csi_model2
output_dir=$BASEDIR/$model
mkdir -p $output_dir
cd $output_dir
cope_pattern=${model}_??.gfeat/cope1.feat/stats/cope1.nii.gz
COPE_LIST=()
for file in $INPUT_DIR/$cope_pattern; do
    COPE_LIST+=("$file")
done
fslmerge -t all_copes.nii.gz "${COPE_LIST[@]}"
randomise \
  -i all_copes.nii.gz \
  -o qchose \
  -d $BASEDIR/design.mat \
  -t $BASEDIR/design.con \
  -m $GROUP_MASK \
  -n $N_PERMUTATIONS \
  -T # TFCE
rm -f all_copes.nii.gz


### model 2, oldval (2)
echo Beginning model2, oldval
cope_pattern=${model}_??.gfeat/cope2.feat/stats/cope1.nii.gz
COPE_LIST=()
for file in $INPUT_DIR/$cope_pattern; do
    COPE_LIST+=("$file")
done
fslmerge -t all_copes.nii.gz "${COPE_LIST[@]}"
randomise \
  -i all_copes.nii.gz \
  -o oldval \
  -d $BASEDIR/design.mat \
  -t $BASEDIR/design.con \
  -m $GROUP_MASK \
  -n $N_PERMUTATIONS \
  -T # TFCE
rm -f all_copes.nii.gz


### model 4, mem (1)
echo Beginning model4, mem
model=csi_model4_cc
output_dir=$BASEDIR/$model
mkdir -p $output_dir
cd $output_dir
cope_pattern=${model}_??.gfeat/cope1.feat/stats/cope1.nii.gz
COPE_LIST=()
for file in $INPUT_DIR/$cope_pattern; do
    COPE_LIST+=("$file")
done
fslmerge -t all_copes.nii.gz "${COPE_LIST[@]}"
randomise \
  -i all_copes.nii.gz \
  -o mem \
  -d $BASEDIR/design.mat \
  -t $BASEDIR/design.con \
  -m $GROUP_MASK \
  -n $N_PERMUTATIONS \
  -T # TFCE
rm -f all_copes.nii.gz


rm -f $BASEDIR/design.*