from keras.models import Model
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization
from keras.callbacks import ModelCheckpoint, EarlyStopping, TensorBoard
from PIL import Image
import numpy as np
import csv
import os
import pandas as pd

LETTERSTR = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def toonehot(text):
    labellist = []
    for letter in text:
        onehot = [0 for _ in range(36)]
        num = LETTERSTR.find(letter)
        onehot[num] = 1
        labellist.append(onehot)
    return labellist


# Create CNN Model
print("Creating CNN model...")
inputs = Input((20, 60, 3))
out = inputs
out = Conv2D(filters=32, kernel_size=(3, 3), padding='same', activation='relu')(out)
out = Conv2D(filters=32, kernel_size=(3, 3), activation='relu')(out)
out = BatchNormalization()(out)
out = MaxPooling2D(pool_size=(2, 2))(out)
out = Dropout(0.5)(out)
out = Conv2D(filters=64, kernel_size=(3, 3), padding='same', activation='relu')(out)
out = Conv2D(filters=64, kernel_size=(3, 3), activation='relu')(out)
out = BatchNormalization()(out)
out = MaxPooling2D(pool_size=(2, 2))(out)
out = Dropout(0.5)(out)
out = Conv2D(filters=128, kernel_size=(3, 3), padding='same', activation='relu')(out)
out = Conv2D(filters=128, kernel_size=(3, 3), activation='relu')(out)
out = BatchNormalization()(out)
out = Flatten()(out)
out = Dropout(0.5)(out)
# out = Conv2D(filters=256, kernel_size=(3, 3), activation='relu')(out)
# out = BatchNormalization()(out)
# out = Flatten()(out)
# out = Dropout(0.5)(out)
out = [Dense(36, name='digit1', activation='softmax')(out),\
    Dense(36, name='digit2', activation='softmax')(out),\
    Dense(36, name='digit3', activation='softmax')(out),\
    Dense(36, name='digit4', activation='softmax')(out)]
model = Model(inputs=inputs, outputs=out)
model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
model.summary()

print("Reading training data...")
training_df=pd.read_csv('training_data.csv')
training_label_list=list(training_df['label'])
training_data = np.stack([np.array(Image.open('captcha_imgs/'+label+'.png'))/80.0 for label in training_label_list])
read_label = [toonehot(label) for label in training_label_list]
training_label = [[] for _ in range(4)]
for arr in read_label:
    for index in range(4):
        training_label[index].append(arr[index])
training_label = [arr for arr in np.asarray(training_label)]
print("Shape of training data:", training_data.shape)

print("Reading validation data...")
validation_df=pd.read_csv('validation_data.csv')
validation_label_list=list(validation_df['label'])
validation_data = np.stack([np.array(Image.open('captcha_imgs/'+label+'.png'))/80.0 for label in validation_label_list])
read_label = [toonehot(label) for label in validation_label_list]
validation_label = [[] for _ in range(4)]
for arr in read_label:
    for index in range(4):
        validation_label[index].append(arr[index])
validation_label = [arr for arr in np.asarray(validation_label)]
print("Shape of validation data:", validation_data.shape)

earlystop = EarlyStopping(monitor='val_digit4_acc', patience=5, verbose=1, mode='auto')
#callbacks_list = [earlystop]
model.fit(training_data, training_label, batch_size=1000, epochs=20, verbose=2, validation_data=(validation_data, validation_label))
model.save("model.h5")
