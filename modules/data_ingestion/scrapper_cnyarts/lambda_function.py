
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

# Some activities don't have data-lat and data-lng. That's why we use google geocode on CNYarts.org 
# Should not use on any other site.
# class Hasher:
#     def __init__(self, key):
#         self.key = key 
#         regex = r"maps-api-v3\/api\/js.*?\[(\d+)\]"
#         try:
#             req = requests.get("https://maps.google.com/maps/api/js?key={}&channel=SOLNET&sensor=false".format(self.key))
#             self.code = int(re.search(regex, req.text).group(1))
#         except:
#             print("Can't access hash code")
#             self.code = 4001957292

#     def hash_arr(self, char_arr):
#         d = 0
#         for char in char_arr:
#             d *= 1729
#             d += char
#             d %= 131071
#         return d

#     def qda(self, text):
#         char_arr = [ord(i) for i in text]
#         char_arr.insert(0, self.code)
#         return self.hash_arr(char_arr)
    

#     def hash(self, url):
#         m = url.replace("'", "%27") + "&key={}&channel=SOLNET".format(self.key)
#         p = m + "&token="
#         m = re.match(r"(?:https?://[^/]+)?(.*)", m).groups()[0]
#         return p + str(self.qda(m))

# class CnyArts():
#    def __init__(self):
def CnyArts():
    # We add the event informations in the dictionary structure to this list.
    RESULT = []
    # We add scraped events url to this list. 
    savedEventUrls = []
    
    # Hasher Object
    """self.hasherObj = Hasher("AIzaSyC00L0023LPBhzj12uTCL-4EwJ_6zgwcTU")"""
    
    # Start from page 1
    page_number = 1
    while True:
        # We will request to get event list page. It return json data. Headers is must
        req = requests.get("https://cnyarts.org/events/events?page={}".format(page_number), headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://cnyarts.org/events/events",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43",
            "X-Requested-With": "XMLHttpRequest"
        })
        
        eventListData = json.loads(req.text)
        
        # eventListData["Content"] is event list page's html (page source)
        soup = BeautifulSoup(eventListData["Content"], "lxml")
        
        # we extract events url to list
        event_urls = [i.find("a").get("href") for i in soup.findAll("h3", "event-title")]
        if event_urls:
            for event_url in event_urls:
                # If we haven't scraped the event previously, we'll scrape. 
                if event_url not in savedEventUrls:
                    print(event_url)
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
                        lat = None
                        
                    try:
                        lng = map_obj.get("data-lng")
                    except:
                        lng = None
                        
                    # if lat and lng is empty. use the google geocode with Hasher
                    if lat == None and lng == None:
                        # Google Geocode Part
                        """safe_string = urllib.parse.quote("4s{}".format(address))
                
                        url = self.hasherObj.hash("https://maps.googleapis.com/maps/api/js/GeocodeService.Search?{}&7sUS&9sen-US&callback=_".format(safe_string))
                        g_req = requests.get(url )
                        alternative_coords = json.loads(g_req.text.replace("/**/_ && _( ","")[0:-3])
                        for result in alternative_coords["results"]:
                            lat = result["geometry"]["location"]["lat"]
                            lng = result["geometry"]["location"]["lng"]"""
                            
                        # Static Coords
                        lat = lng = 0.0000
        
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
                        
                    # Main Event Informations
                    event_info = {
                        "event_url":event_url,
                        "ea_name":event_name,
                        "loc_name":location_name,
                        "loc_address":address,
                        "img_key":event_image,
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
                    
                    #print(event_info)
                    RESULT.append(event_info)
                    savedEventUrls.append(event_url)
                    
                    ## I can write code to put data in Database here, right? -- Yes! You can write code here
                else:
                    # If we have scraped the event previously, we'll pass.  
                    continue  
        else:
            # If event_urls is empty so that means we scraped all the events
            # We will break loop
            break
        #We increase the page number by one
        page_number+=1
    print(page_number)        
    
    # with open('/tmp/cnyresults.csv', 'w', newline='') as f:
    #     w = csv.writer(f)
    #     w.writerows(self.RESULT)
    
    print(RESULT)
    bucket = 'peeeq-datalake-raw-zone' # 'eventactivityscrapperdata'
    df = pd.DataFrame(RESULT)
    
    df.end_date.fillna(df.start_date, inplace=True)
    df['start_date'] = df['start_date'].apply(lambda x: datetime.strptime(str(x + ' 2022'), "%b %d %Y").date())
    df['end_date'] = df['end_date'].apply(lambda x: datetime.strptime(str(x + ' 2022'), "%b %d %Y").date())
    csv_buffer = StringIO() 
    df.to_csv(csv_buffer)
    s3_resource = boto3.resource('s3')
    today = date.today()
    object_key = 'syracuse/cnyarts/'+ str(today) + '/df.csv'
    s3_resource.Object(bucket, object_key).put(Body=csv_buffer.getvalue())
    print("object written!")

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

# ###############################
# Main Lambda handler function
# ##########
def lambda_handler(event, context):
    
    print("start scrapping...")
    CnyArts() 
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
