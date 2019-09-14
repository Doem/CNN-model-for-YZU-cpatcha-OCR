from keras.models import Model, load_model
from data_loader import DataLoader
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization

class CNN_Model():
    def __init__(self, input_shape, is_pretained= False, model_path= ""):
        if (is_pretained == True):
            self.myModel = load_model(model_path)
        else:
            self.myModel = self.build_CNN(input_shape)
            self.myModel.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
            self.myModel.summary()

    def build_CNN(self, input_shape):

        def conv2d(layer_input, filters, is_last= False):
            d = Conv2D(filters, kernel_size=(3, 3), padding='same', activation='relu')(layer_input)
            d = Conv2D(filters, kernel_size=(3, 3), activation='relu')(d)
            d = BatchNormalization()(d)
            if is_last == False:
                d = MaxPooling2D(pool_size=(2, 2))(d)
            d = Dropout(0.5)(d)
            return d

        l0 = Input(input_shape)
        l1 = conv2d(l0, 32)
        l2 = conv2d(l1, 64)
        l3 = conv2d(l2, 128, is_last= True)
        
        l4 = Flatten()(l3)
        out = [Dense(36, name='digit1', activation='softmax')(l4),\
            Dense(36, name='digit2', activation='softmax')(l4),\
            Dense(36, name='digit3', activation='softmax')(l4),\
            Dense(36, name='digit4', activation='softmax')(l4)]

        return Model(inputs= l0, outputs= out)

if __name__ == "__main__":
    dataloader = DataLoader()

    myCNN_model = CNN_Model(dataloader.img_shape)
    # myCNN_model = CNN_Model(dataloader.img_shape, True, "model_.h5")
    
    # train model with train_data (split 25% from train_data to be validation_data)
    myCNN_model.myModel.fit(dataloader.X_train, dataloader.y_train, batch_size= 512, epochs= 100, validation_split= 0.25)

    # test model with test_data
    print(myCNN_model.myModel.evaluate(dataloader.X_test, dataloader.y_test))

    # save model
    myCNN_model.myModel.save("model.h5")
