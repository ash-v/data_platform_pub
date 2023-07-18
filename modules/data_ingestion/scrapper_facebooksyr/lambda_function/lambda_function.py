import selenium
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import re, json
from dateutil.parser import parse

class FacebookEvent:
    def __init__(self):
        # url is listing page url / Please set filters (time range and location)
        url = "https://www.facebook.com/events/search?q=rochester&filters=eyJycF9ldmVudHNfbG9jYXRpb246MCI6IntcIm5hbWVcIjpcImZpbHRlcl9ldmVudHNfbG9jYXRpb25cIixcImFyZ3NcIjpcIjEwNzYxMTI3OTI2MTc1NFwifSIsImZpbHRlcl9ldmVudHNfZGF0ZV9yYW5nZTowIjoie1wibmFtZVwiOlwiZmlsdGVyX2V2ZW50c19kYXRlXCIsXCJhcmdzXCI6XCIyMDIyLTA2LTAzXCJ9IiwiZmlsdGVyX2V2ZW50c19kYXRlX3JhbmdlOjEiOiJ7XCJuYW1lXCI6XCJmaWx0ZXJfZXZlbnRzX2RhdGVcIixcImFyZ3NcIjpcIjIwMjItMDYtMDRcIn0iLCJmaWx0ZXJfZXZlbnRzX2RhdGVfcmFuZ2U6MiI6IntcIm5hbWVcIjpcImZpbHRlcl9ldmVudHNfZGF0ZVwiLFwiYXJnc1wiOlwiMjAyMi0wNS0zMH4yMDIyLTA2LTA1XCJ9IiwiZmlsdGVyX2V2ZW50c19kYXRlX3JhbmdlOjMiOiJ7XCJuYW1lXCI6XCJmaWx0ZXJfZXZlbnRzX2RhdGVcIixcImFyZ3NcIjpcIjIwMjItMDYtMDR%2BMjAyMi0wNi0wNVwifSIsImZpbHRlcl9ldmVudHNfY2F0ZWdvcnk6MCI6IntcIm5hbWVcIjpcImZpbHRlcl9ldmVudHNfY2F0ZWdvcnlcIixcImFyZ3NcIjpcIjY2MDAzMjYxNzUzNjM3M1wifSIsImZpbHRlcl9ldmVudHNfY2F0ZWdvcnk6MSI6IntcIm5hbWVcIjpcImZpbHRlcl9ldmVudHNfY2F0ZWdvcnlcIixcImFyZ3NcIjpcIjExMTYxMTE2NDg1MTU3MjFcIn0ifQ%3D%3D"
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.driver = webdriver.Chrome(executable_path="lambda_function/chromedriver.exe", chrome_options=options)
        self.driver.get(url)
        time.sleep(2)
        
        SCROLL_PAUSE_TIME = 3

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
                            
        # All events data
        EVENT_DATAS = []

        event_urls = self.getEventUrls()
        print(len(event_urls), event_urls)
        for event_url in event_urls:
            print(event_url)
            
            # We enter the event's page
            self.driver.get(event_url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, "lxml")
            scripts = soup.findAll("script")
            
            # Getting scripts from html page source code
            for script in scripts:
                if "event_privacy_info" in str(script):
                    data = re.findall(r'adp_PublicEventCometAboutRootQueryRelayPreloader_.*?",(.*\})]\]', str(script),)[0]
                    jsonData = json.loads(data)
                                        
                    date = soup.find("h2").text.strip()
                    eventDateObj = parse(date.split(" – ")[0], fuzzy=True)
                    eventDayName = eventDateObj.strftime("%A")
                    
                    try:
                        event_image = self.driver.find_element_by_xpath("//img[@data-imgperflogname='profileCoverPhoto']").get_attribute("src")
                    except:
                        event_image = None
                    
                    try:
                        location_name = jsonData["__bbox"]["result"]["data"]["event"]["event_place"]["name"]
                    except:
                        location_name = None 
                        
                    try:
                        location_address = jsonData["__bbox"]["result"]["data"]["event"]["event_place"]["contextual_name"]
                    except:
                        location_address = None 
                        
                    try:
                        lat = jsonData["__bbox"]["result"]["data"]["event"]["event_place"]["location"]["longitude"]
                    except:
                        lat = None    
                        
                    try:
                        lng = jsonData["__bbox"]["result"]["data"]["event"]["event_place"]["location"]["latitude"]
                    except:
                        lng = None  
                        
                    try:
                        description = jsonData["__bbox"]["result"]["data"]["event"]["event_description"]["text"]
                    except:
                        description = None   
                        
                    try:
                        price = re.findall(r'\$(.*?) ',str(description))[0]
                    except:
                        price = None   
                        
                    try:
                        categories = [category["label"] for category in jsonData["__bbox"]["result"]["data"]["event"]["discovery_categories"]]
                    except:
                        categories = None          
                    
                    event_info = {
                        "event_url":event_url,
                        "ea_name":soup.findAll("h2")[1].text.strip(),
                        "loc_name":location_name,
                        "loc_address":location_address,
                        "img_url":event_image,
                        "img_key":event_image.split('/')[-1] if event_image else None,
                        "lat":lat,  
                        "lng":lng,
                        "day_of_event":eventDayName,
                        "time_of_event":eventDateObj.strftime("%H:%M:%S"),
                        "frequency":None,
                        "start_date":eventDateObj.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_date":None,
                        "event_info_source":None,
                        "category":categories,
                        "description":description,
                        "state":None,
                        "email":None,
                        "contact_name":None,
                        "contact_phone":None,
                        "price":price,
                        "except_for":None,
                        "tags": re.findall(r'#([^ #]+)(?=[ #]|$)', description) # getting hastags from description
                    }
                    
                    print(event_info)

                    EVENT_DATAS.append(event_info)

        print(EVENT_DATAS)
        
        # with open('data.json', 'w', encoding='utf-8') as f:
        #     json.dump(EVENT_DATAS, f, ensure_ascii=False, indent=4)

    def getEventUrls(self):
        # Getting event's url from listing page
        urls = []
        item_index = 1
        while True:
            try:
                urls.append(
                    self.driver.find_element_by_xpath(
                        "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div/div[{}]/a/div[1]/div/div/div/div/div[2]/div[1]/div/div/div/div[2]/span/span/object/a".format(item_index)
                    ).get_attribute("href")
                )
                item_index+=1
            except:
                break
                        
                   
        return urls



def lambda_handler(event, context):
    
    print("start scrapping...")
    FacebookEvent()
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
