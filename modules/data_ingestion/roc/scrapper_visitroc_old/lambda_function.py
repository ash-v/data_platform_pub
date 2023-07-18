
## Scrape VisitSyracuse

# TODO
# 1. Need to refreshthe year for start and end date
# 2. rerun with hasher

import requests, urllib
from bs4 import BeautifulSoup
import json, re
import boto3
import csv
import pandas as pd
from io import StringIO
from datetime import date, datetime

weekday_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def VisitSyracuse():
    # We add the event informations in the dictionary structure to this list.
    RESULT = []
    # We add scraped events url to this list. 
    savedEventUrls = []

    # Start from page 1
    skip_count = 0 
    while True:
        # We will request to get event list page. It return json data. Headers is must
        # https://www.visitrochester.com/events/?view=list&sort=date&skip=12&bounds=false
        req = requests.get("https://www.visitrochester.com/events/?view=list&sort=date&skip=12&bounds=false", headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://www.visitrochester.com/events",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43",
            "X-Requested-With": "XMLHttpRequest"
        })
        
        eventListData = json.loads(req.text)
        
        # eventListData["Content"] is event list page's html (page source)
        soup = BeautifulSoup(eventListData["Content"], "lxml")
        
        # we extract events url to list
        event_urls = [i.find("a").get("href") for i in soup.findAll("h3", "event-title")]
        print(len(event_urls))


        if event_urls:
            for event_url in event_urls:
                # If we haven't scraped the event previously, we'll scrape. 
                if event_url not in savedEventUrls:
                    #print(event_url)
                    req = requests.get(event_url)
                    soup = BeautifulSoup(req.text, "lxml")
                    
                    # generraly data
                    event_name = soup.find("h1", "event-title element__title").text.strip()
                    description = soup.find("div", "event-content article-body typography").text.strip()
                    event_image = soup.find("div", "event-image maintain-aspect-ratio").find("img").get("data-lazy-src")
                    try:
                        ticket_price = soup.find("div", "cost").text.strip()
                    except AttributeError:
                        ticket_price = None
                    category = soup.find("ol", "breadcrumb").findAll("li")[1].text.strip()
                    
                    state = soup.find("span", "pretitle d-block").text.strip()
                    
                    frequency = leaveOne(soup.find("div", "repeat small").text.replace("REPEATS:", ""), "\t").replace("                                                                ", " ")
                    
                    start_day = leaveOne(soup.find("div", "event-date-start").find("small", "day").text.strip(), "\t") 
                    start_date = leaveOne(soup.find("div", "event-date-start").find("div", "date").text.strip(), "\t")
                    full_start_date = start_date    
                    # full_start_date = datetime.strptime(str(start_date + ' 2022'), "%b %d %Y").date()
                    try:
                        event_time = leaveOne(soup.find("div", "single-time").text.strip(), "\t").replace("                                   ","")
                    except AttributeError:
                        event_time = None
                        
                    tags = [i.text.strip() for i in soup.findAll("a", "event-tag")]
                    
                    try:
                        end_day = leaveOne(soup.find("div", "event-date-end").find("small", "day").text.strip(), "\t")
                    except AttributeError :
                        end_day = None
                        
                    try:
                        end_date = leaveOne(soup.find("div", "event-date-end").find("div", "date").text.strip(), "\t").replace("                             ", " ")
                    except AttributeError:
                        end_date = None
                    
                    full_end_date = end_date
                    # if end_day and end_date:
                    #     full_end_date =   "{} - {}".format(end_date, end_day)
                    # else:
                    #     full_end_date = None
                    
                    try:
                        except_for = soup.find("div", "event-exception-dates small").text.strip().replace("EXCEPT FOR:", "")
                    except AttributeError:
                        except_for = None
                        
                        
                    # geography data
                    address_container = soup.find("div", "venue venue-short")
                    venue_address = address_container.find("address", "addr")
                    address = leaveOne(venue_address.text.strip(), "\t").replace(" ● ",",").replace("VENUE WEBSITE", "").replace("         ,        ","")
                    location_name = address_container.find("div", "title").text.strip()
                    
                    
                    map_obj = soup.find("div", "mapAPI-map-container")
                    
                    try:
                        lat = map_obj.get("data-lat")
                    except:
                        lat = 0
                        
                    try:
                        lng = map_obj.get("data-lng")
                    except:
                        lng = 0
                        
        
                    try:
                        venue_website = venue_address.find("a", attrs={"target":"_blank"}).get("href")
                    except:
                        try:
                            venue_website = soup.find("a", "www").get("href")
                        except AttributeError:
                            venue_website = None
                        
                    
                    # contact 
                    sidebar_content = soup.find("div", "sidebar page-content")
                    contact_container = sidebar_content.findAll("div", "row")[-1]
                    
                    try:
                        contact_name = contact_container.find("div", "fn").text.strip()
                    except AttributeError:
                        contact_name = None
                        
                    try:
                        contact_phone = contact_container.find("div", "contact-phone").text.strip()
                    except AttributeError:
                        contact_phone = None
                    
                    try:
                        email = contact_container.find("a", "mail").get("href").replace("mailto:", "")
                    except AttributeError:
                        email = None
                        
                    # print(full_start_date)
                    # print(full_end_date)
                    if "CANCELLED" in event_name:
                        print("cancelled event",event_name)
                    else:
                        #print(frequency)
                        if frequency:  # recurrent events
                            # print("event is adhoc")
                            # print(event_url)
                            freq_tokens = frequency.split(' ')
                            # print(freq_tokens)
                            for tok in freq_tokens:
                                week_day = tok.split(',')[0]
                                # print(tok)
                                if week_day in weekday_short:
                                    # print(weekday_full[weekday_short.index(week_day)])
                                    event_info = {
                                    "event_url":event_url,
                                    "ea_name":event_name,
                                    "loc_name":location_name,
                                    "loc_address":address,
                                    "img_url":event_image,
                                    "img_key":event_image.split('/')[-1],
                                    "lat":lat,
                                    "lng":lng,
                                    "day_of_event":weekday_full[weekday_short.index(week_day)],
                                    "time_of_event":event_time,
                                    "frequency":frequency,
                                    "start_date":full_start_date,
                                    "end_date":full_end_date,
                                    "event_info_source":venue_website,
                                    "category":category,
                                    "description":description,
                                    "state":state,
                                    "email":email,
                                    "contact_name":contact_name,
                                    "contact_phone":contact_phone,
                                    "price":ticket_price,
                                    "except_for":except_for,
                                    "tags": ", ".join(tags)
                                    }

                                    RESULT.append(event_info)
                            
                        else: # adhoc events
                            # Main Event Informations
                            # print("Adhoc event")
                            event_info = {
                                "event_url":event_url,
                                "ea_name":event_name,
                                "loc_name":location_name,
                                "loc_address":address,
                                "img_url":event_image,
                                "img_key":event_image.split('/')[-1],
                                "lat":lat,
                                "lng":lng,
                                "day_of_event":start_day,
                                "time_of_event":event_time,
                                "frequency":frequency,
                                "start_date":full_start_date,
                                "end_date":full_end_date,
                                "event_info_source":venue_website,
                                "category":category,
                                "description":description,
                                "state":state,
                                "email":email,
                                "contact_name":contact_name,
                                "contact_phone":contact_phone,
                                "price":ticket_price,
                                "except_for":except_for,
                                "tags": ", ".join(tags)
                                
                            }

                            RESULT.append(event_info)
                    savedEventUrls.append(event_url)
                    
                    
                else:
                    # If we have scraped the event previously, we'll pass.  
                    continue  
        else:
            # If event_urls is empty so that means we scraped all the events
            # We will break loop
            break
        #We increase the page number by one
        page_number+=1
        print(event_info)


# This function is like a beautifier.
# Input --> "\t\t\n\rSample\t Data\n"
# Output --> "Sample Data"
##########
# why i named it "leaveOne"?
# - Because If we replace all tags there will be no spaces, so we don't touch the last character then we change it to space. That's it :)

def leaveOne(s, char): 
    s = re.sub(r'[\n\r]', '',s).strip()
    output = re.sub(r'(%s)\s?(?=.*?\1)' % char, '' , s)
    output = output.replace("\t", " ")
    
    return output

print("start scrapping...")
VisitSyracuse() 
print("Done scrapping.")