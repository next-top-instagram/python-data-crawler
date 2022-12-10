import os
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from IPython import display
from IPython.display import Image
from base64 import b64decode, urlsafe_b64decode, decodebytes

from retry import retry
from loguru import logger
from timeit import default_timer as timer
from datetime import timedelta

def saveBase64Image(img_data, filename):
    with open(f"src/{filename}", "wb") as fh:
        fh.write(b64decode(img_data))

def getSlideItems(slideItemList):
    logger.debug("Slider item list len {}", len(slideItemList))
    try:
        return [(slideItem.find_element(By.TAG_NAME, 'img').get_attribute('alt'), # tour content name
            slideItem.find_element(By.TAG_NAME, 'img').get_attribute('src'), # tour content img
            slideItem.find_element(By.TAG_NAME, 'a').get_attribute('href') # tour content detail link
            ) for slideItem in slideItemList]
    except Exception as e:
        logger.error("Slider item error {}", e)

@retry(Exception, tries=3, delay=2)
def getSlideList(browser):
    sliderCrawlResult = []
    try:
        logger.info("Remove banner to load slider list")
        browser.execute_script("document.querySelector('div.section_banner_top').remove();document.querySelector('div.left_block').remove();jQuery(window).scroll();")
        logger.info("Banner removed")
    except Exception as e:
        logger.error("Remove banner has an error {}", e)
    logger.info("Crawl slider items")
    sliderCrawlResult = [(
        slider.find_element(By.CSS_SELECTOR, 'div.slider_ttl > h2').text, #title
        getSlideItems([item for item in slider.find_elements(By.CSS_SELECTOR, 'div.slick_slide_item')]) #slider's items
        ) for slider in browser.find_elements(By.CSS_SELECTOR, 'div.section_slider_body')]
    logger.debug("Crawl slider items result {}", sliderCrawlResult)
    if sum([len(sliderItemList[1]) for sliderItemList in sliderCrawlResult]) <= 0:
        logger.info("Slider is empty, raise error");
        raise Exception('Data not found')
    return sliderCrawlResult
    
@retry(Exception, tries=3, delay=2)
def initHeadlessBrowser():
    logger.info("Setup headless browser options")
    chrome_options = Options()
    options = [
        "--headless",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--ignore-certificate-errors",
        "--disable-extensions",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "start-maximized",
        "disable-infobars"
    ]
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    
    chrome_options.add_argument('user-agent={0}'.format(user_agent))
    for option in options:
        chrome_options.add_argument(option)
    browser = webdriver.Chrome(options=chrome_options)
    browser.set_window_size(1920, 1080)
    return browser

def resizeBrowserHeightAsContentFullHeight(browser):
    logger.info("Update browser's height same as content height")
    requireHeight = browser.execute_script('return document.body.parentNode.scrollHeight')
    logger.debug("Current content height {}", requireHeight)
    browser.set_window_size(1920, requireHeight)
    browser.execute_script("document.querySelector('div.section_banner_top.setheight').style.height = '464px';")
    logger.info("Manually set banner's height")
    time.sleep(2) # Because of pictures load time

def getAreaInfoProcess(areaName, url):
    logger.debug("Area crawling process start, areaName: {}, url: {}", areaName, url)
    slidItemList = []
    try:
        browser = initHeadlessBrowser()
        logger.debug("Browser move to url: {}", url)
        browser.get(url)
        resizeBrowserHeightAsContentFullHeight(browser)
        saveBase64Image(browser.find_element(By.CSS_SELECTOR, "div.left_block").screenshot_as_base64, f'{areaName}.png')
        slidItemList = getSlideList(browser)
        logger.info("Get slider item done len {}", len(slidItemList))
    except Exception as e:
        logger.error('Cannot get area info data {}', e)
    finally:
        browser.close()
    logger.info("Area crawling browser closed")
    return 0

def getAreaInfoProcessSingleLine(areaName, url):
    logger.debug("Area crawling process start, areaName: {}, url: {}", areaName, url)
    slidItemList = []
    try:
        # browser = initHeadlessBrowser()
        logger.info("Setup headless browser options")
        chrome_options = Options()
        options = [
            "--headless",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "start-maximized",
            "disable-infobars"
        ]
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'    
        chrome_options.add_argument('user-agent={0}'.format(user_agent))
        for option in options:
            chrome_options.add_argument(option)
        browser = webdriver.Chrome(options=chrome_options)
        browser.set_window_size(1920, 1080)

        logger.debug("Browser move to url: {}", url)
        browser.get(url)

        # resizeBrowserHeightAsContentFullHeight(browser)
        logger.info("Update browser's height same as content height")
        requireHeight = browser.execute_script('return document.body.parentNode.scrollHeight')
        logger.debug("Current content height {}", requireHeight)
        browser.set_window_size(1920, requireHeight)
        browser.execute_script("document.querySelector('div.section_banner_top.setheight').style.height = '464px';")
        logger.info("Manually set banner's height")
        time.sleep(2) # Because of pictures load time

        saveBase64Image(browser.find_element(By.CSS_SELECTOR, "div.left_block").screenshot_as_base64, f'{areaName}.png')

        # slidItemList = getSlideList(browser)

        sliderCrawlResult = []
        try:
            logger.info("Remove banner to load slider list")
            browser.execute_script("document.querySelector('div.section_banner_top').remove();document.querySelector('div.left_block').remove();jQuery(window).scroll();")
            time.sleep(10)
            logger.info("Banner removed")
        except Exception as e:
            logger.error("Remove banner has an error {}", e)
        logger.info("Crawl slider items")
        sliderCrawlResult = [(
            slider.find_element(By.CSS_SELECTOR, 'div.slider_ttl > h2').text, #title
            getSlideItems([item for item in slider.find_elements(By.CSS_SELECTOR, 'div.slick_slide_item')]) #slider's items
            ) for slider in browser.find_elements(By.CSS_SELECTOR, 'div.section_slider_body')]
        logger.debug("Crawl slider items result {}", sliderCrawlResult)
        if sum([len(sliderItemList[1]) for sliderItemList in sliderCrawlResult]) <= 0:
            logger.info("Slider is empty!");

        logger.info("Get slider item done len {}", len(sliderCrawlResult))
    except Exception as e:
        logger.error('Cannot get area info data {}', e)
    finally:
        if browser is not None:
            browser.close()
            logger.info("Area crawling browser closed")
    logger.info("Process done!")
    return 0

def testing(areaName, url):
    logger.debug("Area crawling process start, areaName: {}, url: {}", areaName, url)
    time.sleep(10)
    logger.info("Test process done")
    return 0
    # exit(0)