import requests, re
from bs4 import BeautifulSoup


def Everson():
    savedEventUrls = []

    # Start from page 0 (first page)
    page = 1
    while True:
        # We will request to get event list page. It return json data. Headers is must
        req = requests.get("https://everson.org/events-list/events-category-events/page/{}/".format(page), headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43"
        })

        soup = BeautifulSoup(req.text, "lxml")

        # We extract events url to list
        event_urls = [event_box.find("a", attrs={"itemprop":"url"}).get("href") for event_box in soup.findAll("div", "list-blog post_content_holder")]
        if event_urls:
            for event_url in event_urls:
                # If we haven't scraped the event previously, we'll scrape.
                if event_url not in savedEventUrls:
                    req = requests.get(event_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43"
                    })

                    soup = BeautifulSoup(req.text, "lxml")

                    wpb_wrapper = soup.find("div", "wpb_wrapper")
                    elements =  wpb_wrapper.find("p").text.strip().split("\n")

                    if len(elements) == 3:
                        full_start_date = elements[0]
                        event_time = elements[1]

                        if "$" in elements[2] or "free" in elements[2].lower():
                            ticket_price = elements[2]
                            location_name = None
                        else:
                            ticket_price = None
                            location_name = elements[2]

                    elif len(elements) == 4:
                        full_start_date = elements[0]
                        event_time = elements[1]
                        location_name = elements[2]
                        ticket_price = elements[3]

                    day_of_event = None

                    date_items = full_start_date.split(", ")
                    if len(date_items) == 3 or len(date_items) == 1:
                        day_of_event = date_items[0]

                    event_name = soup.find("h1", attrs={"itemprop":"name"}).text.strip()
                    event_image_element = soup.find("div", "expo_feat_img").get("style")
                    event_image = re.findall(r'url\((https:.*)\)', event_image_element)[0]
                    description = wpb_wrapper.findAll("p")[1].text.strip()
                    categories = [i.get("class")[1] for i in soup.find("div", "iconsbox").findAll("a", attrs={"rel":"tag"})]

                    # Main Event Informations
                    event_info = {
                        "event_url":event_url,
                        "ea_name":event_name,
                        "loc_name":location_name,
                        "loc_address":None,
                        "img_url":event_image,
                        "img_key":event_image.split('/')[-1],
                        "lat":None,
                        "lng":None,
                        "day_of_event":day_of_event,
                        "time_of_event":event_time,
                        "frequency":None,
                        "start_date":full_start_date,
                        "end_date":None,
                        "event_info_source":None,
                        "category":categories,
                        "description":description,
                        "state":None,
                        "email":None,
                        "contact_name":None,
                        "contact_phone":None,
                        "price":ticket_price,
                        "except_for":None,
                        "tags":None
                    }

                    #------- You can write code here ---------#

                    savedEventUrls.append(event_url)
                else:
                    # If we have scraped the event previously, we'll pass.
                    continue
        else:
            # If event_urls is empty so that means we scraped all the events
            # We will break loop
            break

        page+=1

def lambda_handler(event, context):
    
    print("start scrapping...")
    Everson()
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
