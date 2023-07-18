
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


# def CnyArts():
#     # We add the event informations in the dictionary structure to this list.
#     RESULT = []
#     # We add scraped events url to this list. 
#     savedEventUrls = []
    
#     # Hasher Object
#     """self.hasherObj = Hasher("AIzaSyC00L0023LPBhzj12uTCL-4EwJ_6zgwcTU")"""
    
#     # Start from page 1
#     page_number = 1
#     while True:
#         # We will request to get event list page. It return json data. Headers is must
#         req = requests.get("https://cnyarts.org/events/events?page={}".format(page_number), headers={
#             "Accept": "application/json, text/javascript, */*; q=0.01",
#             "Referer": "https://cnyarts.org/events/events",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43",
#             "X-Requested-With": "XMLHttpRequest"
#         })
        
#         eventListData = json.loads(req.text)
        
#         # eventListData["Content"] is event list page's html (page source)
#         soup = BeautifulSoup(eventListData["Content"], "lxml")
        
#         # we extract events url to list
#         event_urls = [i.find("a").get("href") for i in soup.findAll("h3", "event-title")]
#         if event_urls:
#             for event_url in event_urls:
#                 # If we haven't scraped the event previously, we'll scrape. 
#                 if event_url not in savedEventUrls:
#                     print(event_url)
#                     req = requests.get(event_url)
#                     soup = BeautifulSoup(req.text, "lxml")
                    
#                     # generraly data
#                     event_name = soup.find("h1", "event-title element__title").text.strip()
#                     description = soup.find("div", "event-content article-body typography").text.strip()
#                     event_image = soup.find("div", "event-image maintain-aspect-ratio").find("img").get("data-lazy-src")
#                     try:
#                         ticket_price = soup.find("div", "cost").text.strip()
#                     except AttributeError:
#                         ticket_price = None
#                     category = soup.find("ol", "breadcrumb").findAll("li")[1].text.strip()
#                     state = soup.find("span", "pretitle d-block").text.strip()
                    
#                     frequency = leaveOne(soup.find("div", "repeat small").text.replace("REPEATS:", ""), "\t").replace("                                                                ", " ")
                    
#                     start_day = leaveOne(soup.find("div", "event-date-start").find("small", "day").text.strip(), "\t") 
#                     start_date = leaveOne(soup.find("div", "event-date-start").find("div", "date").text.strip(), "\t")
#                     full_start_date = start_date    
#                     # full_start_date = datetime.strptime(str(start_date + ' 2022'), "%b %d %Y").date()
#                     try:
#                         event_time = leaveOne(soup.find("div", "single-time").text.strip(), "\t").replace("                                   ","")
#                     except AttributeError:
#                         event_time = None
                        
#                     tags = [i.text.strip() for i in soup.findAll("a", "event-tag")]
                    
#                     try:
#                         end_day = leaveOne(soup.find("div", "event-date-end").find("small", "day").text.strip(), "\t")
#                     except AttributeError :
#                         end_day = None
                        
#                     try:
#                         end_date = leaveOne(soup.find("div", "event-date-end").find("div", "date").text.strip(), "\t").replace("                             ", " ")
#                     except AttributeError:
#                         end_date = None
                    
#                     full_end_date = end_date
#                     # if end_day and end_date:
#                     #     full_end_date =   "{} - {}".format(end_date, end_day)
#                     # else:
#                     #     full_end_date = None
                    
#                     try:
#                         except_for = soup.find("div", "event-exception-dates small").text.strip().replace("EXCEPT FOR:", "")
#                     except AttributeError:
#                         except_for = None
                        
                        
#                     # geography data
#                     address_container = soup.find("div", "venue venue-short")
#                     venue_address = address_container.find("address", "addr")
#                     address = leaveOne(venue_address.text.strip(), "\t").replace(" ● ",",").replace("VENUE WEBSITE", "").replace("         ,        ","")
#                     location_name = address_container.find("div", "title").text.strip()
                    
                    
#                     map_obj = soup.find("div", "mapAPI-map-container")
                    
#                     try:
#                         lat = map_obj.get("data-lat")
#                     except:
#                         lat = None
                        
#                     try:
#                         lng = map_obj.get("data-lng")
#                     except:
#                         lng = None
                        
#                     # if lat and lng is empty. use the google geocode with Hasher
#                     if lat == None and lng == None:
#                         # Google Geocode Part
#                         """safe_string = urllib.parse.quote("4s{}".format(address))
                
#                         url = self.hasherObj.hash("https://maps.googleapis.com/maps/api/js/GeocodeService.Search?{}&7sUS&9sen-US&callback=_".format(safe_string))
#                         g_req = requests.get(url )
#                         alternative_coords = json.loads(g_req.text.replace("/**/_ && _( ","")[0:-3])
#                         for result in alternative_coords["results"]:
#                             lat = result["geometry"]["location"]["lat"]
#                             lng = result["geometry"]["location"]["lng"]"""
                            
#                         # Static Coords
#                         lat = lng = 0.0000
        
#                     try:
#                         venue_website = venue_address.find("a", attrs={"target":"_blank"}).get("href")
#                     except:
#                         try:
#                             venue_website = soup.find("a", "www").get("href")
#                         except AttributeError:
#                             venue_website = None
                        
                    
#                     # contact 
#                     sidebar_content = soup.find("div", "sidebar page-content")
#                     contact_container = sidebar_content.findAll("div", "row")[-1]
                    
#                     try:
#                         contact_name = contact_container.find("div", "fn").text.strip()
#                     except AttributeError:
#                         contact_name = None
                        
#                     try:
#                         contact_phone = contact_container.find("div", "contact-phone").text.strip()
#                     except AttributeError:
#                         contact_phone = None
                    
#                     try:
#                         email = contact_container.find("a", "mail").get("href").replace("mailto:", "")
#                     except AttributeError:
#                         email = None
                        
#                     # Main Event Informations
#                     event_info = {
#                         "event_url":event_url,
#                         "ea_name":event_name,
#                         "loc_name":location_name,
#                         "loc_address":address,
#                         "img_key":event_image,
#                         "lat":lat,
#                         "lng":lng,
#                         "day_of_event":start_day,
#                         "time_of_event":event_time,
#                         "frequency":frequency,
#                         "start_date":full_start_date,
#                         "end_date":full_end_date,
#                         "event_info_source":venue_website,
#                         "category":category,
#                         "description":description,
#                         "state":state,
#                         "email":email,
#                         "contact_name":contact_name,
#                         "contact_phone":contact_phone,
#                         "price":ticket_price,
#                         "except_for":except_for,
#                         "tags": ", ".join(tags)
                        
#                     }
                    
#                     #print(event_info)
#                     RESULT.append(event_info)
#                     savedEventUrls.append(event_url)
                    
#                     ## I can write code to put data in Database here, right? -- Yes! You can write code here
#                 else:
#                     # If we have scraped the event previously, we'll pass.  
#                     continue  
#         else:
#             # If event_urls is empty so that means we scraped all the events
#             # We will break loop
#             break
#         #We increase the page number by one
#         page_number+=1
#     print(page_number)        
    
#     # with open('/tmp/cnyresults.csv', 'w', newline='') as f:
#     #     w = csv.writer(f)
#     #     w.writerows(self.RESULT)
    
#     print(RESULT)
#     bucket = 'peeeq-datalake-raw-zone' # 'eventactivityscrapperdata'
#     df = pd.DataFrame(RESULT)
    
#     df.end_date.fillna(df.start_date, inplace=True)
#     df['start_date'] = df['start_date'].apply(lambda x: datetime.strptime(str(x + ' 2022'), "%b %d %Y").date())
#     df['end_date'] = df['end_date'].apply(lambda x: datetime.strptime(str(x + ' 2022'), "%b %d %Y").date())
#     csv_buffer = StringIO() 
#     df.to_csv(csv_buffer)
#     s3_resource = boto3.resource('s3')
#     today = date.today()
#     object_key = 'syracuse/cnyarts/'+ str(today) + '/df.csv'
#     s3_resource.Object(bucket, object_key).put(Body=csv_buffer.getvalue())
#     print("object written!")

def eventbrite_scraper(place_id):
    events = []
    
    # Creating the new session
    session = requests.Session()
    session.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 OPR/89.0.4447.71",
                    "referrer-policy": "strict-origin-when-cross-origin",
                    "Referer": "https://www.eventbrite.com/d/ny--syracuse/all-events/?page=2"}

    # visit the first homepage and adding the cookie and X-CSRFToken to headers
    initial_req = session.get("https://www.eventbrite.com")
    crsf_token = re.findall(r'csrftoken=(.*?)\;', initial_req.headers["set-cookie"])[0]
    session.headers["cookie"] = "csrftoken={};".format(crsf_token)
    session.headers["X-CSRFToken"] = crsf_token
    
    current_page = 1
    while True:
        req = session.post("https://www.eventbrite.com/api/v3/destination/search/",
                            json={"event_search":{"dates":"this_week","dedup":True,"places":[str(place_id)],"page":current_page,"page_size":50,"online_events_only":False,"client_timezone":"America/New_York","include_promoted_events":True},"expand.destination_event":["primary_venue","image","ticket_availability","saves","event_sales_status","primary_organizer","public_collections"]})
        
        jsonData = json.loads(req.text)
        results = jsonData["events"]["results"]
                
        if len(results) >= 1:
            for result in results:  
                keywords_from_json = list(result.keys())
                
                # Preparing the required fields
                event_info = {
                            "event_url":result["url"],
                            "ea_name":result["name"],
                            "loc_name":result["primary_venue"]["name"],
                            "loc_address":result["primary_venue"]["address"]["localized_address_display"],
                            "img_url":result["image"]["url"] if "image" in keywords_from_json else None,
                            "img_key": None, # they create image dynamicly so no exist image name or image file type
                            "lat":result["primary_venue"]["address"]["latitude"],
                            "lng":result["primary_venue"]["address"]["longitude"],
                            "day_of_event":datetime.strptime(result["start_date"], '%Y-%m-%d').strftime("%A"),
                            "time_of_event":result["start_time"],
                            "frequency":None,
                            "start_date":result["start_date"],
                            "end_date":result["end_date"],
                            "event_info_source":result["url"],
                            "category":None,
                            "description":result["summary"],
                            "state":result["primary_venue"]["address"]["region"],
                            "email":None,
                            "contact_name":result["primary_organizer"]["name"],
                            "contact_phone":None,
                            "price":" - ".join([result["ticket_availability"]["minimum_ticket_price"]["display"] if result["ticket_availability"]["minimum_ticket_price"] else "Free", result["ticket_availability"]["maximum_ticket_price"]["display"] if result["ticket_availability"]["maximum_ticket_price"] else "Free"]),
                            "except_for":None,
                            "tags": ", ".join([tag["display_name"] for tag in result["tags"]])
                        }
                
                events.append(event_info)
                print(event_info)
            current_page+=1
        else:
            break
    
    return events


# ###############################
# Main Lambda handler function
# ##########
def lambda_handler(event, context):
    
    print("start scrapping...")
    CnyArts() 
    scrapped_events = eventbrite_scraper(85941375)
    bucket = 'peeeq-datalake-raw-zone' # 'eventactivityscrapperdata'
    df = pd.DataFrame(scrapped_events)
    df.end_date.fillna(df.start_date, inplace=True)
    df['start_date'] = df['start_date'].apply(lambda x: datetime.strptime(str(x + ' 2022'), "%b %d %Y").date())
    df['end_date'] = df['end_date'].apply(lambda x: datetime.strptime(str(x + ' 2022'), "%b %d %Y").date())
    csv_buffer = StringIO() 
    df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    today = date.today() 
    object_key = 'west_lafayette/eventbrite/'+ str(today) + '/df.csv' ## <- important
    s3_resource.Object(bucket, object_key).put(Body=csv_buffer.getvalue())
    print("object written!")
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
