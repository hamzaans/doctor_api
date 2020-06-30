# medicare_scrape.py
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

# URL = "https://www.medicare.gov/physiciancompare/#results&loc=WALDORF%2C%20MD&lat=38.6265124&lng=-76.9105483&flow=interim&type=specialty&paging=1&keyword=Cardiology&previouspage=IS&dist=15&name=Cardiovascular%20disease%20(Cardiology)&id=06&loctype=c"
# URL = "https://www.medicare.gov/physiciancompare/#results&loc=ALEXANDRIA%2C%20VA&lat=38.8048355&lng=-77.0469214&flow=default&type=specialty&paging=1&keyword=internal%20medicine&previouspage=IS&dist=15&name=Cardiovascular%20disease%20(Cardiology)&id=06&loctype=c&index=4&total=104&curPage=1"
URL = "https://www.medicare.gov/physiciancompare/#results&loc=SAN%20FRANCISCO%2C%20CA&lat=37.7749295&lng=-122.4194155&flow=interim&type=specialty&paging=1&keyword=plastic%20surgery&previouspage=IS&dist=15&name=Plastic%20and%20Reconstructive%20Surgery&id=24&loctype=c&index=4&total=104&curPage=1"
TITLE = 'Medicare.gov'
XPATH = '//*[@id="results-section"]/results-list/div[1]/div[2]/div[1]'
FILENAME = 'waldorf-cardiologists.json'

driver = webdriver.Firefox()
driver.get(URL)

time.sleep(3)

# developer helper function to print inner html 
def _print_innerhtml(element):
    print(element.get_attribute("innerHTML"))

# scrapes the provider card and tells you whether the doctor is a solo clinican or belongs to a group
def _get_is_solo_clinician(card=None):
    info_type = card.find_element_by_class_name("provider-info-type").get_attribute("innerHTML")

    if 'Solo Clinician' in info_type:
        return True
    
    if 'Group' in info_type:
        return False
    
    raise Exception("Doctor is neither Solo Clinician nor Group")

def _get_primary_specialty(card=None):
    # get the tag based on class name primary specialty
    primary_specialty = card.find_element_by_class_name('primary-specialty')
    
    # if it is within a strong tag get the value within strong tag
    if '<strong>' in primary_specialty.get_attribute('innerHTML'):
        return primary_specialty.find_element_by_tag_name('strong').get_attribute('innerHTML').strip()

    # otherwise you already have the value you want in the span tag
    return primary_specialty.find_element_by_tag_name('span').get_attribute('innerHTML').strip()

def _get_additional_specialty(card=None, name=None):
    # since additional specialty may not exist try to get it
    try:
        additional_specialty = card.find_element_by_class_name('additional-specialty')
    except Exception as e:
        print("Exception: ", str(e))
        print("No additional specialty found for ", name)
        return None
    
    # if it is within a strong tag get the value within strong tag
    if '<strong>' in additional_specialty.get_attribute('innerHTML'):
        return additional_specialty.find_element_by_tag_name('strong').get_attribute('innerHTML').strip()

    # otherwise you already have the value you want in the span tag
    return additional_specialty.find_element_by_tag_name('span').get_attribute('innerHTML').strip()


# get name, primary specialty, Additional speciality, address, phone number
def _get_solo_clinician_info(card=None):
    name = card.find_element_by_class_name('provider-name').find_element_by_tag_name('a').get_attribute("innerHTML").strip()
    primary_specialty = _get_primary_specialty(card=card)
    additional_specialty = _get_additional_specialty(card=card, name=name)

    address_parts = card.find_element_by_class_name('address-info').get_attribute('innerHTML').split("<br>")
    address = address_parts[0].strip() + " " + address_parts[1].strip()
    
    phone_number = card.find_element_by_class_name('phone').get_attribute('innerHTML').strip()
    
    # after you get all varaibles, return doctor info
    return {
        "name": name,
        "primary_specialty": primary_specialty,
        "additional_specialty": additional_specialty,
        "address": address,
        "phone_number": phone_number
    }

# takes in a group doctor card and returns the doctors name, primary specialty and additional specialty as a dictionary
def _get_group_doctor_info(card=None):
    name = card.find_element_by_tag_name('a').get_attribute("innerHTML").strip()
    primary_specialty = _get_primary_specialty(card=card)
    additional_specialty = _get_additional_specialty(card=card, name=name)

    return {
        "name": name,
        "primary_specialty": primary_specialty,
        "additional_specialty": additional_specialty
    }

def _write_json_to_file(doctors=None):
    # if file doesnt exist create it
    path = FILENAME

    # convert doctor list of arrays to json string
    doctors_json = json.dumps(doctors, indent=4)

    # create file if doesnt exist
    if not os.path.exists(path):
        with open(path, 'w'): pass

    # write to file - overwrites if exists
    file1 = open(path,"w+") # write mode 
    file1.write(doctors_json) 
    file1.close() 


# initialize doctors list
doctors = []

# get all provider cards
provider_cards = driver.find_elements_by_class_name('provider-card')

# for each card, 
for card in provider_cards:
    # figure out if provider card is solo clinician or a group
    is_solo_clinican = _get_is_solo_clinician(card=card)

    # if solo clinican get name, primary specialty, Additional speciality, address, phone number
    if is_solo_clinican:
        doctor_info = _get_solo_clinician_info(card=card)
        doctors.append(doctor_info)

    # if group
    else:
        # get the groups name, phone number and address
        group_name = card.find_element_by_class_name('provider-name').find_element_by_tag_name('a').get_attribute("innerHTML").strip()
        phone_number = card.find_element_by_class_name('phone').get_attribute('innerHTML').strip()

        address_parts = card.find_element_by_class_name('address-info').get_attribute('innerHTML').split("<br>")
        address = address_parts[0].strip() + " " + address_parts[1].strip()

        # get list of doctors in group 
        doctor_cards = card.find_elements_by_class_name("group-member")

        # for each doctor
        for doctor_card in doctor_cards:
            # get name, primary specialty, Additional speciality
            doctor_info = _get_group_doctor_info(card=doctor_card)
            doctor_info["group"] = group_name
            doctor_info["address"] = address
            doctor_info["phone_number"] = phone_number

            # add to doctors list 
            doctors.append(doctor_info)

print("printing doctors list")
print(doctors)

_write_json_to_file(doctors)

driver.close()