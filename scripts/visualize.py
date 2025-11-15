import os
import cv2
import numpy as np
import pickle as pkl
import matplotlib.pyplot as plt

out_dir = '../out/'

file_names = list(set([val.split('.')[0] for val in os.listdir(out_dir)]))

for file_name in file_names:
    img = cv2.cvtColor(cv2.imread(out_dir + file_name + f'.png'), cv2.COLOR_BGR2RGB)

    plt.imshow(img)
    
    keypoints = np.array(pkl.load(open(out_dir + file_name + f'.pkl', 'rb')))
    if len(keypoints) > 0:
        keypoints = keypoints.transpose(2, 0, 1).reshape(2, -1).transpose(1, 0)
        keypoints = (keypoints * 640).astype(np.int32)
        
        plt.scatter(keypoints[:, 1], keypoints[:, 0], c = 'red', s = 0.5)
        
    plt.savefig(out_dir + file_name + f'_.png')
    plt.close()