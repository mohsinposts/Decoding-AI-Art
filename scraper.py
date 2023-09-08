from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
import csv
import pandas as pd
import math
import time
import glob
import os

# Opening Safari browser
browser = webdriver.Safari()

# Going to webiste
browser.get('https://app.leonardo.ai/auth/login')

# Login info on website
WebDriverWait(browser, 10).until(EC.presence_of_element_located(("xpath",'//*[@id="email"]')))

browser.find_element("xpath",'//*[@id="email"]').send_keys('XXXXXXXXgmail.com')
browser.find_element("xpath",'//*[@id="password"]').send_keys('xxxxxxxxx')

time.sleep(2)

browser.find_element("xpath", '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div[2]/div[1]/form/div/button').submit()

browser.maximize_window()

WebDriverWait(browser, 10).until(EC.presence_of_element_located(("xpath", '//*[@id="chakra-modal-:r17:"]/footer/div/button[2]')))

for x in range(0,5):
    browser.find_element("xpath", '//*[@id="chakra-modal-:r17:"]/footer/div/button[2]').click()

browser.find_element("xpath", '//*[@id="chakra-modal--body-:r18:"]/div/div[2]/div/div/div/div[3]/button').click()


time.sleep(5)

# Scrolling the page for specific amount of time to load a large amount of images to download
screen_height = browser.execute_script("return window.screen.height;")

i = 1
t_end = time.time() + 600
# time.time() < t_end:
while time.time() < t_end:
    # scroll one screen height each time
    browser.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(3)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = browser.execute_script("return document.body.scrollHeight;")  
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        break 

time.sleep(2)

browser.execute_script("window.scrollTo(0,220);")

time.sleep(8)

# Go to first photo on the page
browser.find_element("xpath", '//*[@id="__next"]/div/div[2]/div/div[3]/div[2]/div/div/div[1]/div[1]/div/div/div[2]').click()
count = 1 # keep count to track number of images downloading

# opening a csv file to write images names and corresponding prompts
with open('dataset copy.csv','a') as file:
    while True:
        time.sleep(2)

        # Error handling if element on page does not load properly
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located(("xpath", "//*[starts-with(@id, 'chakra-modal--body-:')]/div/div[1]/div[1]/div[5]/div/button[2]")))
            browser.find_element("xpath", "//*[starts-with(@id, 'chakra-modal--body-:')]/div/div[1]/div[1]/div[5]/div/button[2]").click()
        except:
            try:
                WebDriverWait(browser, 10).until(EC.presence_of_element_located(("xpath", '/html/body/div[4]/div[2]/div/div[2]/button')))
                browser.find_element("xpath", '/html/body/div[4]/div[2]/div/div[2]/button').click()
                continue
            except:
                print("elements on page did not load properly")
                break
                
        time.sleep(8) # give time for image to download

        # Error handling if image does not downlad properly
        try: 
            # Putting current downloaded image in specific folder on computer
            filesList = glob.glob('/Users/poojasmac/Downloads/*.jpg')  # * means all if need specific format then *.csv
            recentFile = max(filesList, key=os.path.getctime)
        except:
            # print("file was not downloaded properly")
            WebDriverWait(browser, 10).until(EC.presence_of_element_located(("xpath", '/html/body/div[4]/div[2]/div/div[2]/button')))
            browser.find_element("xpath", '/html/body/div[4]/div[2]/div/div[2]/button').click()
            continue

        imageName = "img" + str(count) + ".jpg"

        newFile = os.path.join('/Users/poojasmac/Downloads/', imageName)

        os.rename(recentFile, newFile)

        filesList = glob.glob('/Users/poojasmac/Downloads/*.jpg') 
        recentFile = max(filesList, key=os.path.getctime)
   
        # Changing image size using ratio so image is not distorted
        image = Image.open(recentFile)
        imageSize = image.size
        print(f"Original image size: {imageSize}")

        width = imageSize[0]
        height = imageSize[1]

        if width <= height:
            ratio = width / 400
            width /= ratio
            height /= ratio

        else:
            ratio = height / 400
            height /= ratio
            width /= ratio

        imageResized = image.resize((math.ceil(width), math.ceil(height)))
        imageResized.save(recentFile)
        os.rename(recentFile, "/Users/poojasmac/Downloads/ImageDataset/" + imageName)

        prompt = browser.find_element("xpath", "//*[starts-with(@id, 'chakra-modal--body-:')]/div/div[1]/div[2]/div[2]/div[1]/div/div/p").text

        # Writing image name and corresponding prompt to the csv file
        writer = csv.writer(file, delimiter="~")
        writer.writerow([imageName, prompt])

        if count == 1:
            browser.find_element("xpath", '/html/body/div[4]/div[2]/div/div/button').click()
            count+=1
        else:
            browser.find_element("xpath", '/html/body/div[4]/div[2]/div/div[2]/button').click()
            count+=1
# Closing file and browser
file.close()
browser.close()