import requests, json
from bs4 import BeautifulSoup

def syracusetrivianight():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in days:
        # Getting event list on days
        req_listing = requests.get("https://syracusetrivianight.com/scripts/venues2.php?day={}".format(day), 
                                        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.60"})
        jsonData = json.loads(req_listing.text)
        
        for venueItem in jsonData:
            
            # Merge event sub_url and main parent url
            event_url = "https://syracusetrivianight.com/venue/{}".format(venueItem["slug"])
            req = requests.get("https://syracusetrivianight.com/venue/{}".format(venueItem["slug"]),
                                    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.60"})
            soup = BeautifulSoup(req.text, "lxml")
            
            # Finding data contanier
            contanier = soup.find("div", "container")
            name = contanier.h1.text.strip()
            
            # Getting events informations dynamically
            subData = {}
            for contentItem in soup.find("div", "venue_content").find("h3").text.split("\n"):
                contentItemElements = contentItem.strip().split(": ")
                if len(contentItemElements) >= 2:
                    subData[contentItemElements[0].lower()] = contentItemElements[1]
                    
            # Combine parent url and img uri
            event_image = "https://syracusetrivianight.com" + soup.find("div", "venue_image").find("img").get("src")
            
            # We use BeautifulSoup to get 'ea_name' again because it comes in an html tag from the listing
            ea_name = BeautifulSoup(venueItem["html"], "lxml").h2.text.strip()
            
            # Splitted ea_name for time_of_event. Example :" Trivia at 'HOUR' "
            time_of_event = ea_name.split(" at ")[-1]
            
            # Collection 'p' elements from 'venue_content' element. 
            description = soup.find("div", "venue_content").findAll("p")[1].text.strip()
            
            # Main Event Informations
            event_info = {
                "event_url":event_url,
                "ea_name":ea_name,
                "loc_name":name,
                "loc_address":subData["address"],
                "img_key":event_image,
                "lat":venueItem["lat"],
                "lng":venueItem["lon"],
                "day_of_event":day,
                "time_of_event":time_of_event,
                "frequency":"Recurrent",
                "start_date":"na",
                "end_date":"na",
                "event_info_source":"https://syracusetrivianight.com",
                "category":"Trivia",
                "description": description,
                "state":"na",
                "email":"na",
                "contact_name":"na",
                "contact_phone":subData["phone"],
                "price":"na",
                "except_for":"na",
                "tags":"na"
            }
            
            print(event_info)
            


def lambda_handler(event, context):
    # TODO implement
    syracusetrivianight()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }