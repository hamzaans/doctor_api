#Pokemon Home Webscrape
import time
import traceback
import re
import os
import sys
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from datetime import date

options = Options()
options.headless = False
pokemon_home_jsons = []
i = 0
while i < 36:
    driver = webdriver.Firefox(options=options)
    pokemon_list = ['Bulbasaur', 'Ivysaur', 'Venusaur', 'Squirtle', 'Wartortle', 'Blastoise', 'Mewtwo', 'Mew', 'Celebi', 'Jirachi', 'Cobalion', 'Terrakion', 'Virizion', 'Reshiram', 'Zekrom', 'Kyurem', 'Keldeo', 'Rowlet', 'Dartrix', 'Decidueye', 'Litten', 'Torracat', 'Incineroar', 'Popplio', 'Brionne', 'Primarina', 'Cosmog', 'Cosmoem', 'Solgaleo', 'Lunala', 'Necrozma', 'Marshadow', 'Zeraora', 'Meltan', 'Melmetal']

    driver.get('https://serebii.net')
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys(pokemon_list[i])
    elem.send_keys(Keys.RETURN)
    time.sleep(3)

    driver.find_element_by_xpath('//*[@id="___gcse_0"]/div/div/div/div[5]/div[2]/div/div/div[1]/div[1]/div[1]/div[1]/div/a').click()
    time.sleep(2)
    driver.close()

    window_after = driver.window_handles[0]
    driver.switch_to.window(window_after)
    time.sleep(5)

    #Want names, image, and abilities
    name = driver.find_element_by_xpath('/html/body/div[1]/div[2]/main/div/div/table[5]/tbody/tr[2]/td[1]').get_attribute('innerHTML')
    image = 'https://www.serebii.net/' +  (driver.find_element_by_xpath('//*[@id="content"]/main/div/div/table[4]/tbody/tr[2]/td/table/tbody/tr/td[1]/img').get_attribute('outerHTML').split('src="')[1].split('">')[0])
    abilities = driver.find_element_by_xpath('//*[@id="content"]/main/div/div/table[6]/tbody/tr[2]/td').find_elements_by_tag_name('a')
    
    abilities_list = []
    for ability in abilities:
        abilities_list.append((ability.get_attribute('innerHTML')).split('<b>')[1].split('</b>')[0])
        # print((ability.get_attribute('innerHTML')).split('<b>')[1].split('</b>')[0])
    pokemon_home_json = {"name": name, "image": image, "abilities": abilities_list}
    # print(pokemon_json)
    pokemon_home_jsons.append(pokemon_home_json)
    i = i + 1
    driver.close()

output = json.dumps(pokemon_home_jsons, indent=4)
print(output)

f = open("pokemon_home.json", "w")
f.write(output)