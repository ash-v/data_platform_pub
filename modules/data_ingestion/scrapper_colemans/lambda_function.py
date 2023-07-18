import requests, json
from datetime import datetime

class ColemansIrishPub():
    def __init__(self):
        self.savedEventNames = []
        
        # We will request to get event list page. It return json data. Headers is must
        req = requests.get("https://inffuse.eventscalendar.co/js/v0.1/calendar/data?pageId=yu24x&compId=comp-irz4egnw&viewerCompId=comp-irz4egnw&siteRevision=1240&viewMode=site&deviceType=desktop&locale=en&regionalLanguage=en&width=473&height=1297&instance=tRI1qxZay-KPk5aYwEdjzhyGudjUBxK24Ky1QFLiBF8.eyJpbnN0YW5jZUlkIjoiMTU1OWYwMTQtMTdlYS00MWQxLWE2NWItYmJmMGY2NDI2Yzk3IiwiYXBwRGVmSWQiOiIxMzNiYjExZS1iM2RiLTdlM2ItNDliYy04YWExNmFmNzJjYWMiLCJzaWduRGF0ZSI6IjIwMjItMDEtMjZUMTc6NDE6MDkuMTk0WiIsInZlbmRvclByb2R1Y3RJZCI6InByZW1pdW0iLCJkZW1vTW9kZSI6ZmFsc2UsImFpZCI6IjIyMmI2YzAxLTRhYmItNDljOC04OTQ3LTUwNmY4YjRlZjJkMyIsInNpdGVPd25lcklkIjoiNmM1YjZhN2QtMzIzZi00Y2Y5LTk4ODYtNGQ5YTgyMGRiNzU4In0&commonConfig=%7B%22brand%22%3A%22wix%22%2C%22bsi%22%3A%22192305f5-0d0a-4f96-9d0e-2e76ccbde0ca%7C2%22%2C%22BSI%22%3A%22192305f5-0d0a-4f96-9d0e-2e76ccbde0ca%7C2%22%7D&vsi=7146a3af-89f7-4eb3-b119-d75c107acf61", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.43"
        })

        jsonData = json.loads(req.text)
        
        
        for event in jsonData["project"]["data"]["events"]:
            #Some events can have same name but different dates, so we create unique ID with the name and start date. 
            event_unique_id = "-".join([event["title"], event["start"]])
            
            # Event start and end date is unix date number. I'll divide by 1000 because it have extra zeros for convert.
            event["start"] = int(event["start"])/1000
            event["end"] = int(event["end"])/1000
            
            if  event_unique_id not in self.savedEventNames:
                now_unix_time = int(datetime.utcnow().timestamp())
                if event["start"] >= now_unix_time:
                
                    start_date = datetime.fromtimestamp(int(event["start"]))
                    end_date = datetime.fromtimestamp(int(event["end"]))
                    
                    start_time = datetime.strptime("{}:{}".format(event["startHour"], event["startMinutes"]), "%H:%M").strftime("%I:%M %p")
                    end_time = datetime.strptime("{}:{}".format(event["endHour"], event["endMinutes"]), "%H:%M").strftime("%I:%M %p")
                    
                    event_info = {
                                "event_url":"https://www.colemansirishpub.com/music-events",
                                "ea_name":event["title"],
                                "loc_name":"Coleman's Authentic Irish Pub",
                                "loc_address":"100 S Lowell Ave, Syracuse, NY 13204",
                                "img_key":None,
                                "lat":43.048056,
                                "lng":-76.181823,
                                "day_of_event":start_date.strftime('%A'), # 
                                "time_of_event":"{} - {}".format(start_time, end_time),
                                "frequency":"All Day" if event["allday"] else None,
                                "start_date":start_date.strftime("%Y-%m-%d"),
                                "end_date":end_date.strftime("%Y-%m-%d"),
                                "event_info_source":None,
                                "category":"Live Music",
                                "description":event["description"] if "description" in list(event.keys()) else None,
                                "state":None,
                                "email":None,
                                "contact_name":None,
                                "contact_phone":None,
                                "price":None,
                                "except_for":None,
                                "tags":None
                            }

                    #------- You can write code here ---------#

                    self.savedEventNames.append(event_unique_id)

def lambda_handler(event, context):
    # TODO implement
    ColemansIrishPub()
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }