
## Scrape CNYARTS

# TODO
# 1. Need to refresh the year for start and end date
# 2. rerun with hasher

import requests, urllib
from bs4 import BeautifulSoup
import json, re #, sqlite3
import boto3
import csv
import pandas as pd
from io import StringIO
from datetime import date, datetime

def VisitRochester():
    today = datetime.datetime.today()
    today_str = today.strftime('%Y-%m-%d')
    
    week_ahead = today + datetime.timedelta(days=7)
    week_ahead_str = week_ahead.strftime('%Y-%m-%d')
    
    # We add the event informations in the dictionary structure to this list.
    EVENTS = []
    
    session = requests.session()
    session.headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.84"
    }
    
    # Generate new token for each session
    token_req = session.get("https://www.visitrochester.com/plugins/core/get_simple_token/")
    token = token_req.text
    
    base_url = "https://www.visitrochester.com/includes/rest_v2/plugins_events_events_by_date/find/?json=%7B%22filter%22%3A%7B%22active%22%3Atrue%2C%22%24and%22%3A%5B%7B%22categories.catId%22%3A%7B%22%24in%22%3A%5B%2239%22%2C%2233%22%2C%2210%22%2C%2217%22%2C%2215%22%2C%2235%22%2C%2236%22%2C%2230%22%2C%2212%22%2C%2211%22%2C%2213%22%2C%2232%22%5D%7D%7D%5D%2C%22date_range%22%3A%7B%22start%22%3A%7B%22%24date%22%3A%22{start_date}T04%3A00%3A00.000Z%22%7D%2C%22end%22%3A%7B%22%24date%22%3A%22{end_date}T04%3A00%3A00.000Z%22%7D%7D%7D%2C%22options%22%3A%7B%22limit%22%3A24%2C%22skip%22%3A{skip_offset}%2C%22count%22%3Atrue%2C%22castDocs%22%3Afalse%2C%22fields%22%3A%7B%22_id%22%3A1%2C%22location%22%3A1%2C%22date%22%3A1%2C%22startDate%22%3A1%2C%22endDate%22%3A1%2C%22recurrence%22%3A1%2C%22recurType%22%3A1%2C%22latitude%22%3A1%2C%22longitude%22%3A1%2C%22media_raw%22%3A1%2C%22recid%22%3A1%2C%22title%22%3A1%2C%22url%22%3A1%2C%22listing.title%22%3A1%2C%22listing.url%22%3A1%7D%2C%22hooks%22%3A%5B%5D%2C%22sort%22%3A%7B%22date%22%3A1%2C%22rank%22%3A1%2C%22title_sort%22%3A1%7D%7D%7D&token={token}"

    offset = 0
    while True:
        listing_url = base_url.format(
            start_date=today_str,
            end_date=week_ahead_str,
            skip_offset=offset,
            token=token
        )

        req = session.get(listing_url)
        jsonData = json.loads(req.text)
        
        if len(jsonData["docs"]["docs"]) == 0:
            break
        
        for event_document in jsonData["docs"]["docs"]:
            # print(event_document)
            
            start_date_obj = datetime.datetime.strptime(event_document["startDate"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            if "endDate" in list(event_document.keys()):
                end_date_obj = datetime.datetime.strptime(event_document["endDate"].split(".")[0],  "%Y-%m-%dT%H:%M:%S")
            else:
                end_date_obj = None
                
            event_page_req = session.get("https://www.visitrochester.com{}".format(event_document["url"]))
            soup = BeautifulSoup(event_page_req.text, "lxml")
            
            # Scraping Extra Data from Event page
            for script in soup.findAll("script"):
                data_from_page = re.findall(r'var.*?data.*?=.*?(\{.*?\})\;', str(script))
                if data_from_page:
                    jsonData_from_page = json.loads(data_from_page[0])
                    street_address = re.findall(r'var.*?cityStateZip.*?=.*?"(.*?)";', str(script))[0]
                    city_state_zip = re.findall(r'var.*?streetAddress.*?=.*?"(.*?)";', str(script))[0]
                    try:
                        _, stateCode, zipCode = re.findall(r'(([A-Za-z]{2}) (\d+))', street_address)[0]
                    except:
                        _ = stateCode = zipCode = None
                        
                    address = " - ".join([street_address, city_state_zip])
                    time_of_event = re.findall(r'var.*?time.*?=.*?"(.*?)";', str(script))[0]            
            
            event_info = {
                            "event_url":"https://www.visitrochester.com{}".format(event_document["url"]),
                            "ea_name":event_document["title"],
                            "loc_name":event_document["location"] if "location" in list(event_document.keys()) else None,
                            "loc_address":address,
                            "img_url":event_document["media_raw"][0]["mediaurl"],
                            "img_key":event_document["media_raw"][0]["mediaurl"].split("/")[-1],
                            "lat":event_document["latitude"] if "latitude" in list(event_document.keys()) else None,
                            "lng":event_document["longitude"] if "longitude" in list(event_document.keys()) else None,
                            "day_of_event":start_date_obj.strftime('%A'),
                            "time_of_event":time_of_event,
                            "frequency":jsonData_from_page["recurrence"] if "recurrence" in list(jsonData_from_page.keys()) else None,
                            "start_date":start_date_obj.strftime("%Y-%m-%d"),
                            "end_date":end_date_obj.strftime("%Y-%m-%d") if end_date_obj else None,
                            "event_info_source":jsonData_from_page["linkUrl"] if "linkUrl" in list(jsonData_from_page.keys()) else None,
                            "category":None,
                            "description": BeautifulSoup(jsonData_from_page["description"], "html5lib").text.strip() if "description" in list(jsonData_from_page.keys()) else None,
                            "state":stateCode,
                            "email":jsonData_from_page["email"] if "email" in list(jsonData_from_page.keys()) else None,
                            "contact_name":jsonData_from_page["hostname"] if "hostname" in list(jsonData_from_page.keys()) else None,
                            "contact_phone":jsonData_from_page["phone"] if "phone" in list(jsonData_from_page.keys()) else None,
                            "price":jsonData_from_page["admission"] if "admission" in list(jsonData_from_page.keys()) else None, 
                            "except_for":None,
                            "tags":None
                        }
            
            EVENTS.append(event_info)
            
            print(event_info)

        
        offset+=24

    return EVENTS


# ###############################
# Main Lambda handler function
# ##########
def lambda_handler(event, context):
    
    print("start scrapping...")
    events = VisitRochester()
    print("Done scrapping.")
    return {
      'statusCode': 200,
      'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST'
      },
      'body': json.dumps('Hello from your new Amplify Python lambda!')
  }
