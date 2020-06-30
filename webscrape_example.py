# anime_scrape.py
import time
import traceback
import re
import os
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from datetime import date


URL = "https://twist.moe/a/kaguya-sama-wa-kokurasetai-tensai-tachi-no-renai-zunousen-2/1"
TITLE = 'kaguya-sama'
XPATH = '//*[@id="__layout"]/div/div[1]/section/main/div[2]/div[3]/ul'
FILENAME = 'kaguya-sama.txt'

def _parse_episode_from_a_tag(a):
    # get string when we split by spaces
    string = a.split('episode-number">')
    if len(string) < 2:
        return

    val = string[1].replace('</span></a>', '')
    return val

def _get_latest_episode(episodes):
    episode = episodes[len(episodes) - 1]
    a = episode.get_attribute("innerHTML")
    ep = _parse_episode_from_a_tag(a)
    return ep

def _get_stored_episode():
    path = 'latest/' + FILENAME
    if not os.path.exists(path):
        return
    
    # read the file
    file1 = open(path, "r+")
    latest = file1.readline()
    stored = re.findall('\d+', latest )[0]
    return stored

def _retry_assert_title(title):
    count = 0
    max_retries = 3

    print('title, driver_title')
    print(title.lower(), driver.title.lower())

    while count < max_retries:
        try:
            assert title.lower() in driver.title.lower()
            return
        except:
            count += 1
    
    assert title in driver.title
            
def _store_latest(latest):
    path = 'latest/' + FILENAME
    # if file doesnt exist create it and return empty list
    if not os.path.exists(path):
        open(path, 'w')
    file1 = open(path, "r+")
    file1.write('latest:{latest}\nnew_flag:1'.format(latest=latest)) # write the new line before

try:
    today = date.today()
    print("Today's date:", today)
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(URL)
    time.sleep(1)

    # assert title in driver.title
    _retry_assert_title(TITLE)
    print('\n\n\ndriver.title')
    print(driver.title)

    ul = driver.find_element_by_xpath(XPATH)
    episodes = ul.find_elements_by_tag_name("li")
    print("number of episodes: {length}".format(length=len(episodes)))
    
    latest = _get_latest_episode(episodes)
    print('The latest episode is Episode {latest}'.format(latest=latest))
    
    stored = _get_stored_episode()
    
    if stored == latest:
        print("No new episode")
        driver.close()
        sys.exit()

    # store latest episode in file with new_flag set to 1
    _store_latest(latest)
    print("Set flag to 1, to download episode {latest}".format(latest=latest))

    driver.close()

except Exception as e:
    traceback.print_exc()
    driver.close()
    