import cv2
import time
import numpy as np
import configparser
from seleniumwire import webdriver
from keras.models import load_model

class webDriver():
    def __init__(self, account, password):
        self.pass_Count = 0
        self.fail_Count = 0
        self.Account = account
        self.Password = password
        self.model = load_model('model.h5')
        self.n_classes = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        # need to download the chrome webdriver
        # https://sites.google.com/a/chromium.org/chromedriver/downloads
        self.browser = webdriver.Chrome('chromedriver')

    def predict(self, img):
        prediction = self.model.predict(np.array([img]))

        predict_str = ""
        for pred in prediction:
            predict_str += self.n_classes[np.argmax(pred[0])]
        return predict_str

    def login(self):
        browser = self.browser
        del browser.requests

        # open url
        browser.get('https://isdna1.yzu.edu.tw/CnStdSel/Index.aspx')

        # find all elements we need
        SelCosType_ele = browser.find_element_by_id('DPL_SelCosType')
        Account_ele = browser.find_element_by_id('Txt_User')
        Password_ele = browser.find_element_by_id('Txt_Password')
        Captcha_ele = browser.find_element_by_id('Txt_CheckCode')
        Button_ele = browser.find_element_by_id('btnOK')

        # find captcha bytes data
        img_data = b''
        for request in browser.requests:
            if request.path == 'https://isdna1.yzu.edu.tw/CnStdSel/SelRandomImage.aspx':
                img_data = request.response.body

        # save captcha img
        with open('Captcha.png', 'wb') as file:
            file.write(img_data)

        # read img and use CNN to recognize captcha
        img = cv2.imread('Captcha.png') / 255.0
        captcha = self.predict(img)

        # fill value to each element
        SelCosType_ele.send_keys('108-1-2')
        Account_ele.send_keys(self.Account)
        Password_ele.send_keys(self.Password)
        Captcha_ele.send_keys(captcha)  # Captcha

        # click login button
        time.sleep(1)
        Button_ele.click()

        # get alert information to check if login successful
        alert = browser.switch_to.alert
        if '驗證碼錯誤' in alert.text:
            # store the fail captcah imgs that we can re-train model
            # cv2.imwrite('./fail_imgs/{}.png'.format(captcha), cv2.imread('Captcha.png'))
            self.fail_Count += 1
        elif '帳號或密碼錯誤' in alert.text:
            print('帳號或密碼錯誤，請重新確認！')
            exit()
        else:
            self.pass_Count += 1

        # output information
        print('{} Correct: {:04}, Wrong: {:04}, Accuracy: {:.3f}%'.format( \
            captcha, \
            self.pass_Count, \
            self.fail_Count, \
            self.pass_Count / (self.pass_Count + self.fail_Count) * 100) \
            )

        # sleep to watch result and accept the alert
        # time.sleep(1)
        alert.accept()

    def run(self, times):
        # do i times to test our model's accuracy
        for i in range(times):
            self.login()

        # close browser
        self.browser.close()


if __name__ == "__main__":
    # get account info from ini config file
    config = configparser.ConfigParser()
    config.read('accounts.ini')
    Account = config['Default']['Account']
    Password = config['Default']['Password']

    # test our CNN model online
    myWebDriver = webDriver(Account, Password)
    myWebDriver.run(1000)
