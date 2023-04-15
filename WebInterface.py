

from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import objc
import Vision
import CoreML
import Quartz
from time import sleep
import cv2
import numpy as np
import base64


# Press the green button in the gutter to run the script.
def link_web():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=/Users/xuzhilei/Library/Application Support/Google/Chrome")
    chrome_options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=chrome_options)
    browser.get('https://universe.flyff.com/play')
    sleep(5)
    soup4 = BeautifulSoup(browser.page_source, "html.parser")
    # canvas = soup4.find("canvas")
    # print(canvas)
    for i in range(20000):
        screenshot = browser.get_screenshot_as_base64()
        canvas_png = base64.b64decode(screenshot)
        img = cv2.imdecode(np.frombuffer(canvas_png, np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow("Screenshot", img)
        cv2.imwrite("/Users/xuzhilei/Desktop/flyff_pic/screenshot_" + str(i) + ".jpg", img)
    #
    #
    browser.quit()
