#import required modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
import time
from selenium.webdriver.common.keys import Keys
import re
from english_words import english_words_lower_set
import pandas as pd
import string
import sys
from datetime import datetime
from collections import Counter
import os,sys

for i in range(0,len(sys.argv))[1:]:
    if i ==1:
        att1=str(sys.argv[i])

tracker=[]
def Clean(lis):
    letters=[]
    pres=[]
    for i in lis:
        l = re.search('letter=(.+?) ', i)
        ev= re.search('evaluation=(.+?)"', i)
        l=l.group(1)
        l=l.replace('"',"")
        ev=ev.group(1)
        ev=ev.replace('"',"")
        letters.append(l)
        pres.append(ev)
    df=pd.DataFrame({"Letters":letters,"Present":pres})
    return df


def Words(lis2):
    global wordsdf
#seperate into present/absent/correct
    absent=lis2.loc[lis2['Present'] == "absent"]
    correct=lis2.loc[lis2['Present'] == "correct"]
    present=lis2.loc[lis2['Present'] == "present"]
#deals with letters present more than once in word
    absent=absent.loc[~absent['Letters'].isin(correct["Letters"])]
    absent=absent.loc[~absent['Letters'].isin(present["Letters"])]
#removes words containing any absent letters
    wordsdf=wordsdf[~wordsdf["0"].str.contains('|'.join(list(absent["Letters"])))]
#removes words that don't contain present letters
    for i in present["Letters"]:
        wordsdf=wordsdf[wordsdf["0"].str.contains(i)]
#removes words that contain present letter in current position
    for i,a in zip(present["Letters"],present.index):
         wordsdf=wordsdf[wordsdf["0"].str[a] != i]
#removes words that don't contain correct letter in current position
    for i,a in zip(correct["Letters"],correct.index):
         wordsdf=wordsdf[wordsdf["0"].str[a] == i]
#if not solved return next guess, if solved return solved
    try:
        first= wordsdf["0"].values[0]
        return first,tracker
    except:
        print("Solution Found in",len(tracker),tracker)

def WordleE(guess):
    startTime = datetime.now()
    tracker.append(guess)
    chrome_options = Options()
    driver = webdriver.Chrome(executable_path=r"chromedriver", options=chrome_options)
    driver.get("https://www.powerlanguage.co.uk/wordle/")
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pz-gdpr-btn-accept"]'))).click()
    time.sleep(1)
    sends=driver.find_element_by_xpath("/html/body")
    sends.click()
    time.sleep(2)
    sends.send_keys(guess)
    sends.send_keys(Keys.ENTER)
    try:
        for i in range(1,6):
            x1="""return document.querySelector('game-app').shadowRoot.querySelector('#board > game-row:nth-child({})').shadowRoot.querySelectorAll('game-tile[letter]')""".format(i)
            inner_texts = [my_elem.get_attribute("outerHTML") for my_elem in driver.execute_script(x1)]
            cleaned=Clean(inner_texts)
            worded=Words(cleaned)
            tracker.append(worded[0])
            time.sleep(2)
            sends.send_keys(worded[0])
            sends.send_keys(Keys.ENTER)
    except:
        print(datetime.now() - startTime)
        #tracker=[]
wordsdf=pd.read_csv('words_final2.csv')
tracker=[]
WordleE(att1)
time.sleep(20)
