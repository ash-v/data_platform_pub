import requests
import pandas as pd
from bs4 import BeautifulSoup
import re, json
from slugify import slugify
from datetime import datetime

def NYSFairgrounds():
    # get datetime of Today
    TODAY = datetime.now()
    
    req = requests.get("https://nysfairgrounds.ny.gov/events")       
    
    # I found regular json in HTML. Use regex to get data.
    data = re.findall(r'all\-events="(.*?)"', req.text)[0].replace("&quot;",'"')
    jsonData = json.loads(data)
    
    for event_item in jsonData:
        event_datetime = datetime.strptime(event_item["machineReadableStartDate"], '%Y-%m-%d %I:%M %p')
        
        # Number of days between two given dates (event time and today)
        days_between  = (event_datetime - TODAY).days
        if days_between <= 30:
            # request to event url
            req = requests.get(event_item["url"])
            soup = BeautifulSoup(req.text, "lxml")

            name = soup.find("h1", "c_headline").text.strip()
            description = soup.find("div", "event__content__main").text.strip()
            event_image = soup.find("img", "c_image").get("src")
            end_date = event_item["machineReadableStartDate"].replace(event_item["startTime"], event_item["endTime"]).replace(event_item["startTimeAmPm"], event_item["endTimeAmPm"])
            
            # Getting specifications from page dynamically
            specifications = soup.find("ul", "specifications").findAll("li")
            specification_data = {
                "venue":None,
                "website":None,
                "contact-email":None,
                "admission":None,
                "contact-phone":None
            }
            for specification in specifications:
                label = specification.find("div", "specifications__label").text.strip()
                value = specification.find("div", "specifications__value").text.strip()
                
                # Using slugify for standardization 
                specification_data[slugify(label)] = value

            # Main Event Informations
            event_info = {
                "event_url":event_item["url"],
                "ea_name":name,
                "loc_name":specification_data["venue"],
                "loc_address":specification_data["venue"],
                "img_key":event_image,
                "lat":0.0,
                "lng":0.0,
                "day_of_event":event_datetime.strftime("%A"),
                "time_of_event":event_datetime.strftime("%I:%M %p"),
                "frequency":None,
                "start_date":event_item["machineReadableStartDate"],
                "end_date":end_date,
                "event_info_source":specification_data["website"],
                "category":None,
                "description":description,
                "state":None,
                "email":specification_data["contact-email"],
                "contact_name":None,
                "contact_phone":specification_data["contact-phone"],
                "price":specification_data["admission"],
                "except_for":None,
                "tags":None
            }

            #------- You can write code here ---------#
            print(event_info)

                
NYSFairgrounds()
