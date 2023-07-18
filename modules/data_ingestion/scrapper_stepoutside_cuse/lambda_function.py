import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
import pandas as pd

def stepoutside():
    headers = {
            "Accept":"*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Cookie": "ct=syracuse-ny; cs=step; _ga=GA1.2.544426653.1649881928; __gpi=UID=000004ed532d83a0:T=1650196138:RT=1650196138:S=ALNI_MbFf8chE9nsqHaJAGC8gVbUASjB4w; __gads=ID=bb042e188a0dc05b-2200a6167acd0001:T=1649881927:RT=1650196154:S=ALNI_MZnHqMsMJkiNz9Xq30H2t16gSLlVg; bt=syracuse-ny; _gid=GA1.2.246882328.1650299278; SLG_G_WPT_TO=tr; SLG_GWPT_Show_Hide_tmp=1; SLG_wptGlobTipTmp=1; _gat=1",
            "Host": "stepoutside.org",
            "Referer": "https://stepoutside.org/syracuse-ny/events/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.60",
            "X-Requested-With": "XMLHttpRequest"
        }
    
    pageNumber = 1
    while True:
        listingUrl = "https://stepoutside.org/ajax/events/next_page/?options%5Btitle%5D=Events%20Near%20Syracuse%20NY&options%5Bkeyword%5D=&options%5Bradius%5D=45&options%5Blimit%5D=15&options%5Bpage%5D=1&options%5Bsef%5D=&options%5Btags%5D=&options%5Btags_logical%5D=&options%5Bterms%5D=&options%5Bshow%5D=15&options%5Bshow_limit%5D=3&options%5Bsort%5D=&options%5Bdays%5D=365&options%5Bimages%5D=yes&options%5Bmax-days%5D=365&options%5Bmax-miles%5D=45&options%5Bmessage%5D=&options%5Bmin%5D=20&options%5Bprompt%5D=&options%5Bheight%5D=&options%5Bwidth%5D=&options%5Bmore%5D=yes&options%5Bautoshowmore%5D=no&options%5Blink%5D=&options%5Bshowdesc%5D=yes&options%5Brankby%5D=distance&options%5Btype%5D=&options%5Bad_slots%5D=&options%5Bsee-more-title%5D=&options%5Bsearchdate%5D=&options%5Blat%5D=43.05080032348633&options%5Blng%5D=-76.14739990234375&options%5Blatlng%5D=43.050800323486%2C-76.147399902344&options%5Bcount%5D=34&page={}".format(pageNumber)
        req = requests.get(listingUrl, headers=headers)
        
        listingSoup = BeautifulSoup(req.text, "lxml")
        eventItems = listingSoup.findAll("div", class_="media")
        
        if eventItems:
            for item in eventItems:
                eventUrl = "https://stepoutside.org{}".format(item.find("a").get("href"))
                print(eventUrl)
                
                eventReq = requests.get(eventUrl, headers=headers)
                soup = BeautifulSoup(eventReq.content, "lxml")
                
                #Getting common of event from listing page.
                location = item.find("div", "location").text.strip()
                eventName = item.find("h3", class_="media-heading").text.strip()
                
                startDate = item.find("div", class_="time").text.strip()
                
                eventDateObj = parse(startDate, fuzzy=True)
                eventDayName = eventDateObj.strftime("%A")
                
                eventFullDate = soup.find("p", "detail-event-date").text.strip()
                end_date_items = eventFullDate.split("to")
                if len(end_date_items) >= 2:
                    end_date = end_date_items[1]
                else:
                    end_date = end_date_items[0]
                
                # Getting description from event page
                try:
                    description = soup.find("div", "detail-description").text.strip().replace("\xa0", "")
                except:
                    try:
                        description = soup.find("h2").text.strip().replace("\xa0", "")
                    except:
                        description = None
                     
                # Getting phone number   
                phoneElement = soup.find("div", "detail-phone")
                if phoneElement:
                    phone = phoneElement.text.strip()
                else:
                    phone = None
                    
                # Getting coordinates
                mapElement = soup.find("div", attrs={"id":"detail-map"})
                if mapElement:
                    lat = mapElement.get("data-lat")
                    lng = mapElement.get("data-lng")
                else:
                    lat = lng = None
                    
                # Geting Image
                imgs = soup.find("div", "module").findAll("img")
                if len(imgs) >= 2:
                    event_image = imgs[1].get("src")
                    img_key = event_image.split('/')[-1].split('?')[0] 
                else:
                    event_image = None
                    img_key = None

                event_info = {
                                "event_url":eventUrl,
                                "ea_name":eventName,
                                "loc_name":location,
                                "loc_address":None,
                                "img_url":event_image,
                                "img_key":img_key,
                                "lat":lat,
                                "lng":lng,
                                "day_of_event":eventDayName,
                                "time_of_event":eventDateObj.strftime("%H:%M:%S"),
                                "frequency":None,
                                "start_date":eventDateObj.strftime("%Y-%m-%d %H:%M:%S"),
                                "end_date":end_date,
                                "event_info_source":None,
                                "category":None,
                                "description":description,
                                "state":None,
                                "email":None,
                                "contact_name":None,
                                "contact_phone":phone,
                                "price":None,
                                "except_for":None,
                                "tags":None,
                                "full_desc":None
                            }
                
                print(event_info)

            pageNumber+=1
        else:
            break
            



def lambda_handler(event, context):
    # TODO implement
    stepoutside()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }