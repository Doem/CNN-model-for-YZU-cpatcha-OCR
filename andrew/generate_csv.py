import pandas as pd
import os

total_size=60000

testing_set_size=int(total_size*0.1)
validation_set_size=int((total_size-testing_set_size)*0.1)
training_set_size=int(total_size-testing_set_size-validation_set_size)

training_label_list=[]
validation_label_list=[]
testing_label_list=[]

label_list=[]
for i, file_name in enumerate(os.listdir('captcha_imgs/')):
    if(file_name.endswith(".png")) and i<total_size:
        label_list.append(file_name[:-4])

training_label_list=label_list[:training_set_size]
validation_label_list=label_list[training_set_size:training_set_size+validation_set_size]
testing_label_list=label_list[training_set_size+validation_set_size:total_size]


training_df=pd.DataFrame()
training_df['label']=training_label_list
validation_df=pd.DataFrame()
validation_df['label']=validation_label_list
testing_df=pd.DataFrame()
testing_df['label']=testing_label_list

training_df.to_csv('training_data.csv', index=False)
validation_df.to_csv('validation_data.csv', index=False)
testing_df.to_csv('testing_data.csv', index=False)

print(len(training_df))
print(len(validation_df))
print(len(testing_df))