from selenium import webdriver

import time 
browser = webdriver.Chrome()
browser.get('http://naver.com/')
time.sleep(10)
browser.get('https://google.com/')
time.sleep(10)
# browser.implicitly_wait(10);