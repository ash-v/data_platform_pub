import requests
from bs4 import BeautifulSoup
import boto3
import json 
import csv
import pandas as pd
from io import StringIO
from datetime import date

# class FunknWaffles():
#     def __init__(self):
def FunknWaffles():
    RESULT = []
    savedEventUrls = []
    
    # Start from page 0 (first page)
    page = 0
    while True:
        # We will request to get event list page. It return json data. Headers is must
        req = requests.get("https://www.funknwaffles.com/syracuse/?twpage={}".format(page), headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43"
        })
        
        soup = BeautifulSoup(req.text, "lxml")
        
        # We extract events url to list
        event_urls = [i.find("div","tw-name").find("a").get("href") for i in soup.findAll("div", "tw-section")]
        if event_urls:
            for event_url in event_urls:
                # If we haven't scraped the event previously, we'll scrape. 
                if event_url not in savedEventUrls:
                    # print(event_url)
                    req = requests.get(event_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43"
                    })
                        
                    soup = BeautifulSoup(req.text, "lxml")
                    
                    # generraly data
                    event_name = soup.find("div", "tw-name").text.strip()
                    sub_name = soup.find("div", "tw-opening-act").text.strip()
                    event_image = soup.find("div", "tw-image").find("img").get("src")
                    ticket_price = soup.find("div", "tw-price").text.strip()
                    except_for = soup.find("div", "tw-age-restriction").text.strip()
                    description = soup.find("div", "tw-description").text.strip().replace("\n","").replace("\xa0"," ").replace("\t", "") if soup.find("div", "tw-description") else None
                    start_day = soup.find("span", "tw-day-of-week").text.strip()
                    event_time = soup.find("span", "tw-event-time").text.strip()
                    full_start_date = soup.find("span", "tw-event-date").text.strip()
                    artists = [i.text.strip() for i in soup.findAll("div", "tw-name")]
                    
                    # if description != None:
                    #     print(description)
                    
                    # Main Event Informations
                    event_info = {
                        "event_url":event_url,
                        "ea_name":"{} {}".format(event_name, sub_name),
                        "loc_name":"Funk 'n Waffles",
                        "loc_address":"307-13 S Clinton St, Syracuse, NY 13202",
                        "img_key":event_image,
                        "lat":43.050545,     ## "Funk 'n Waffles" coordinates hard coded
                        "lng":-76.153641,
                        "day_of_event":start_day,
                        "time_of_event":event_time,
                        "frequency":"Adhoc",
                        "start_date":full_start_date,
                        "end_date":full_start_date,
                        "event_info_source":event_url,
                        "category":"Live Music",
                        "description": description if description != None else ", ".join(artists) ,
                        "state":"Active",
                        "email":None,
                        "contact_name":None,
                        "contact_phone":None,
                        "price":ticket_price,
                        "except_for":except_for,
                        "tags":", ".join(artists)
                    }
                    
                   # print(event_info)                        
                    RESULT.append(event_info)
                   
                else:
                    # If we have scraped the event previously, we'll pass.  
                    continue
        else:
            # If event_urls is empty so that means we scraped all the events
            # We will break loop
            break

        page+=1
    
    
    # print(self.RESULT)
    
    bucket = 'eventactivityscrapperdata'   ## TODO: UPDTATE Bucket
    df = pd.DataFrame(RESULT)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    today = date.today()
    object_key = 'syracuse/funknwaffles/'+ str(today) + '/df.csv'
    s3_resource.Object(bucket, object_key).put(Body=csv_buffer.getvalue()) ## TODO: UPDTATE PATH
    
    
def lambda_handler(event, context):
    # TODO implement
    FunknWaffles()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
