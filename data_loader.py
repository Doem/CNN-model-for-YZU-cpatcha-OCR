import cv2
import glob
import random
import os.path
import numpy as np
from sklearn.model_selection import train_test_split

class DataLoader():
    def __init__(self):
        self.img_shape = (20, 60, 3)
        self.data_path = r'captcha_imgs'
        self.n_classes = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.num_classes = len(self.n_classes)
        
        self.load_from_folder(self.data_path)

    def load_from_folder(self, path):
        # get all imgs path from folder 
        files_path = glob.glob(os.path.join(path, '*.png'))

        # shuffle dataset
        random.shuffle(files_path)
        # files_path = files_path[0:20480]

        # read imgs and labels
        train_data = []
        train_labels = []
        for file in files_path:
            train_data.append(cv2.imread(file))
            train_labels.append(file[-8 : -4].upper())
            
        # split data to train and validation set
        self.X_train, self.X_test, y_train, y_test = train_test_split(train_data, train_labels, test_size= 0.25)

        self.y_test = [[] for _ in range(4)]
        self.y_train = [[] for _ in range(4)]

        # process label of y_train
        for label in y_train:
            for index, ndarr in enumerate(self.onehot_encoding(label)):
                self.y_train[index].append(ndarr)

        # process label of y_val
        for label in y_test:
            for index, ndarr in enumerate(self.onehot_encoding(label)):
                self.y_test[index].append(ndarr)

        # convert to adarray and normalize
        self.X_test = np.array(self.X_test) / 255.0
        self.X_train = np.array(self.X_train) / 255.0

    def onehot_encoding(self, label_str):
        label = []
        for index, ch in enumerate(label_str):
            label.append(np.zeros(self.num_classes, dtype= 'int32'))
            label[index][self.n_classes.find(ch)] = 1
        return np.array(label)