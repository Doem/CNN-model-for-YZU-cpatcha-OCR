from PIL import Image
import numpy as np
import pandas as pd
from keras.models import load_model, Model
import statistics

LETTERSTR = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

testing_df=pd.read_csv('testing_data.csv')
label_list=testing_df['label']

model = load_model("model.h5")
dict={}
percentage_list=[]
for label in label_list:
    prediction = model.predict(np.stack([np.array(Image.open('captcha_imgs/'+label+'.png'))/80.0]))
    answer = ""
    for predict in prediction:
        answer += LETTERSTR[np.argmax(predict[0])]

    count=0
    for i in range(4):
        if answer[i] == label[i]:
            count+=1
    if str(count) not in dict:
        dict[str(count)]=0
    dict[str(count)] +=1
    percentage_list.append(count/4)
    print('original: '+label+', predicted: '+answer)
print(dict)
print(statistics.mean(percentage_list))