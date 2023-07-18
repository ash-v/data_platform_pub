import requests, urllib
from bs4 import BeautifulSoup
import json, re #, sqlite3
import boto3
import csv
import pandas as pd
from io import StringIO
from datetime import date, datetime

def Alltrails_syr():
    EVENTS = []
    api_endpoint = "https://9ioacg5nhe-dsn.algolia.net/1/indexes/alltrails_index3/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.8.6)%3B%20Browser"
    cities = {
        # 74:"Albany"
        8042: "Syracuse"
    }
    
    session = requests.session()
    session.headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPR/90.0.4480.84",
        "x-algolia-api-key": "63a3cf94e0042b9c67abf0892fc1d223",
        "x-algolia-application-id": "9IOACG5NHE"
    }
    

    for city_id, city_name in cities.items():
        payload = {"query":"","hitsPerPage":1000,"attributesToRetrieve":["description","ID","_cluster_geoloc","_geoloc","activities","area_id","area_name","area_slug","avg_rating","city_id","city_name","country_id","country_name","created_at","difficulty_rating","duration_minutes","duration_minutes_cycling","duration_minutes_hiking","duration_minutes_mountain_biking","duration_minutes_trail_running","elevation_gain","filters","has_profile_photo","is_closed","is_private_property","length","name","num_photos","num_reviews","photo_count","popularity","profile_photo_data","route_type","slug","state_id","state_name","type","units","user","verified_map_id","visitor_usage","area_name_en-US","area_name_en","city_name_en-US","city_name_en","country_name_en-US","country_name_en","state_name_en-US","state_name_en","name_en-US","name_en","description_en-US","description_en"],"filters":"(city_id={}) AND ((length>=0)) AND ((elevation_gain>=0)) AND type:trail".format(city_id),"attributesToHighlight":[],"responseFields":["hits","hitsPerPage","nbHits"]}
        req = session.post(api_endpoint, json=payload)
        jsonData = json.loads(req.text)
        
        for event in jsonData["hits"]:
            print(event) # Informations of event

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
            
            EVENTS.append(event)
            
    
    return EVENTS

# ###############################
# Main Lambda handler function
# ##########
# def lambda_handler(event, context):
    
#     print("start scrapping...")
#     Alltrails_syr()
#     print("Done scrapping.")
#     return {
#       'statusCode': 200,
#       'headers': {
#           'Access-Control-Allow-Headers': '*',
#           'Access-Control-Allow-Origin': '*',
#           'Access-Control-Allow-Methods': 'POST'
#       },
#       'body': json.dumps('Hello from your new Amplify Python lambda!')
#   }
if __name__ == "__main__":
    Alltrails_syr()