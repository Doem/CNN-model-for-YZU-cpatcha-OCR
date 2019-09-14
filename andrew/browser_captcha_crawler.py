import cv2
import time
import configparser
from selenium import webdriver
import pytesseract
from PIL import Image, ImageEnhance


class webDriver():
    def __init__(self, account, password):
        self.pass_Count = 0
        self.fail_Count = 0
        self.Account = account
        self.Password = password
        self.browser = webdriver.Chrome('./chromedriver')

    def login(self):
        browser = self.browser

        # open url
        browser.get('https://isdna1.yzu.edu.tw/CnStdSel/Index.aspx')

        # find all elements we need
        SelCosType_ele = browser.find_element_by_id('DPL_SelCosType')
        Account_ele = browser.find_element_by_id('Txt_User')
        Password_ele = browser.find_element_by_id('Txt_Password')
        Captcha_ele = browser.find_element_by_id('Txt_CheckCode')
        Button_ele = browser.find_element_by_id('btnOK')

        # find and save captcha img
        Captcha_img = browser.find_element_by_xpath('//*[@id="Panel2"]/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[2]/td[2]/img')
        browser.save_screenshot('img.png')
        left = Captcha_img.location['x']+16
        right = left+75
        top = Captcha_img.location['y']+60
        bottom = top+25
        print(left, right, top,bottom)
        img = Image.open('img.png')
        img = img.crop((left, top, right, bottom))
        img=img.resize((60, 20))
        img=img.convert("RGB")

        enhancer = ImageEnhance.Contrast(img)
        pImg = enhancer.enhance(2.0)
        pImg=pImg.crop((1, 1, 59, 19))
        answer=pytesseract.image_to_string(pImg, config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 7v').replace(' ', '').upper()
        answer=answer[:4]
        # fill value to each element
        SelCosType_ele.send_keys('108-1-2')
        Account_ele.send_keys(self.Account)
        Password_ele.send_keys(self.Password)
        Captcha_ele.send_keys(answer) # Captcha

        # click login button
        Button_ele.click()

        # get alert information to check if login successful
        alert = browser.switch_to_alert()
        if '驗證碼錯誤' not in alert.text and len(answer)>0:
            img.save('browser_captcha_imgs/'+answer+'.png')
        # sleep to watch result and accept the alert
        time.sleep(1)
        alert.accept()

    def run(self, times):
        while True:
            self.login()
            time.sleep(1)

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
    # myModel = myWebDriver.CNN_Model()
    myWebDriver.run(5)

    # myWebDriver.run(5)
