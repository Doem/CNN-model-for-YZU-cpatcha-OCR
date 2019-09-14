import cv2
import time
import errno
import socket
import datetime
import requests
import pytesseract
import numpy as np
import configparser
from bs4 import BeautifulSoup

class Captcha():
    def __init__(self, account, password):
        self.pass_count = 0
        self.total_count = 0
        self.account = account
        self.password = password
        self.login_url = 'https://isdna1.yzu.edu.tw/CnStdSel/Index.aspx'
        self.captcha_url = 'https://isdna1.yzu.edu.tw/CnStdSel/SelRandomImage.aspx'
        self.tesseract_config = '-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 7'

    def processImg(self, img):
        # kernel = np.ones((2, 2), np.uint8)
        img[ 0, :, :].fill(255)
        img[19, :, :].fill(255)
        img[:,  0, :].fill(255)
        img[:, 59, :].fill(255)

        img = cv2.resize(img, (300, 100))
        img = cv2.fastNlMeansDenoisingColored(img, None, 40, 40, 7, 21)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        # img = cv2.dilate(img, kernel, iterations = 2)
        img = cv2.erode(img, np.ones((3, 3), np.uint8), iterations = 1)
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        return img

    def login(self):

        # create Session object and get session
        session = requests.Session()
        session.headers['Connection'] = 'close'
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

        with session.get(self.captcha_url, stream= True) as captcha_html: 
            # write data to img file
            with open('test.png', 'wb') as file:
                file.write(captcha_html.raw.read())

        # read temp img and do some processes
        org_img = cv2.imread('test.png')
        new_img = self.processImg(org_img.copy())

        # use pytesseract to recognize captcha 
        captcha = pytesseract.image_to_string(new_img, config= self.tesseract_config).replace(' ', '').upper()

        # get login data
        login_html = session.get(self.login_url)

        # use BeautifulSoup to parse html
        parser = BeautifulSoup(login_html.text, 'lxml')

        # login data
        payload = {
            '__VIEWSTATE': parser.select("#__VIEWSTATE")[0]['value'],
            '__VIEWSTATEGENERATOR': parser.select("#__VIEWSTATEGENERATOR")[0]['value'],
            '__EVENTVALIDATION': parser.select("#__EVENTVALIDATION")[0]['value'],
            'DPL_SelCosType': '108-1-2',  #need to check
            'Txt_User': self.account,
            'Txt_Password': self.password,
            'Txt_CheckCode': captcha,
            'btnOK': '確定'
        }

        # do login and check if successful
        result = session.post(self.login_url, data= payload)
        if '1.嚴禁使用外掛程式干擾選課系統' in result.text:
            print('captcha: {} successful'.format(captcha))
            self.pass_count += 1

            # store original img if successful
            cv2.imwrite('./captcha_imgs/{}.png'.format(captcha), org_img)
        else:
            print('captcha: {} fail'.format(captcha))
        self.total_count += 1
        session.close()
       
    def run(self):
        start_time = datetime.datetime.now()
        while True:
            try:
                self.login()
                print('[{}] {:.3f}%\n'.format(datetime.datetime.now() - start_time, self.pass_count / self.total_count * 100))
                # time.sleep(1)
            except requests.exceptions.RequestException as error:
                with open('logs.txt', 'a+') as file:
                    print(error)
                    file.write(error.response)
                continue

if __name__ == "__main__":

    # get account info from ini config file
    config = configparser.ConfigParser()
    config.read('accounts.ini')
    Account = config['Default']['Account']
    Password = config['Default']['Password']
    
    # do loop to download captchas
    myCaptcha = Captcha(Account, Password)
    myCaptcha.run()