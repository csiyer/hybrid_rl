import nibabel as nib
import glob

# change TR in nifti headers which for some reason is 1.0 instead of 2.0
root = '/Volumes/shohamy-locker/chris/hybrid_mri_JN/rawdata/'

def set_tr(img, tr):
    header = img.header.copy()
    zooms = header.get_zooms()[:3] + (tr,)
    header.set_zooms(zooms)
    return img.__class__(img.get_fdata().copy(), img.affine, header)

niifiles = glob.glob(root + 'sub-*/func/*.nii')
for niifile in niifiles:
    img = nib.load(niifile)
    fixed_img = set_tr(img, 2.0)
    fixed_img.to_filename(niifile)


# also, add taskname to functional json sidecars
import json
root = '/Volumes/shohamy-locker/chris/hybrid_mri_JN/rawdata/'
json_files = glob.glob(root + "sub-*/func/*.json")  # Adjust path if needed

for json_file in json_files:
    with open(json_file, "r") as f:
        metadata = json.load(f)

    if "TaskName" not in metadata:
        metadata["TaskName"] = "main"
        with open(json_file, "w") as f:
            json.dump(metadata, f, indent=4)

print("Done updating JSON files.")
