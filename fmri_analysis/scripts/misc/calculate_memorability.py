# docker run --platform linux/amd64 -it --rm -v /Users/chrisiyer:/home bvlc/caffe:cpu /bin/bash
# python /home/_Current/lab/code/hybrid_rl/fmri_analysis/scripts/misc/calculate_memorability.py

import caffe
import numpy as np
import os
import pandas as pd

netdir = '/home/Downloads/memnet'
model_def = netdir+'/deploy.prototxt'
model_weights = netdir+'/MemNet.caffemodel'
mean_file = netdir+'/mean.binaryproto'
image_dir = netdir+'/images'

# Load mean
blob = caffe.proto.caffe_pb2.BlobProto()
data = open(mean_file, 'rb').read()
blob.ParseFromString(data)
mean_array = np.array(caffe.io.blobproto_to_array(blob))[0]

# Load model
net = caffe.Net(model_def, model_weights, caffe.TEST)
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_mean('data', mean_array.mean(1).mean(1))  # Use average mean
transformer.set_transpose('data', (2,0,1))
transformer.set_raw_scale('data', 255)

# Set input size
net.blobs['data'].reshape(1, 3, 227, 227)

# Run on images and store results in dataframe
out = pd.DataFrame(columns=['dataset','obj_id','memscore'])

katherine_image_dir = '/home/_Current/lab/code/hybrid_reinforcement_learning/Hybrid_MRI/Experiment_Katherine/Stimuli/objects' 
# format: 45.jpg
print('Beginning katherine dataset')
for obj_id in range(1,655): #loop through katherine's stimuli
    if obj_id % 50 == 0:
        print('Object ' + str(obj_id) + '/654')
    img_path = os.path.join(katherine_image_dir, str(obj_id)+".jpg")
    image = caffe.io.load_image(img_path)
    net.blobs['data'].data[...] = transformer.preprocess('data', image)
    output = net.forward()
    memscore = output['fc8-euclidean'][0][0]
    out.loc[len(out),:] = ['katherine',obj_id,memscore]

jonathan_image_dir = '/home/_Current/lab/code/hybrid_rl/task/stimuli/no_deck' 
# format: object45.jpg
print('Beginning jonathan dataset')
for obj_id in range(1,666): #loop through katherine's stimuli
    if obj_id % 50 == 0:
        print('Object ' + str(obj_id) + '/665')
    img_path = os.path.join(jonathan_image_dir, 'object'+str(obj_id)+".jpg")
    image = caffe.io.load_image(img_path)
    net.blobs['data'].data[...] = transformer.preprocess('data', image)
    output = net.forward()
    memscore = output['fc8-euclidean'][0][0]
    out.loc[len(out),:] = ['jonathan',obj_id,memscore]

out.to_csv('/home/_Current/lab/code/hybrid_rl/fmri_analysis/data/objects.csv',index=False)
