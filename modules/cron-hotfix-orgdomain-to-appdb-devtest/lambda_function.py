import json
import boto3
import os
import logging
import sys
import dynamodbgeo 
import datetime 
from dateutil.parser import parse
import time
from uuid import uuid4
import pandas as pd

### Get Data from 
s3_client = boto3.client('s3') 
S3_BUCKET_NAME = 'peeeq-datalake-organized-zone' 
S3_BUCKET_PREFIX = 'event_master.csv'

### put data to 
dynamodb = boto3.client('dynamodb', region_name='us-east-1')
config = dynamodbgeo.GeoDataManagerConfiguration(dynamodb, 'peeeqPosts-dev')
config.hashKeyLength = 3
geoDataManager = dynamodbgeo.GeoDataManager(config)
  


def lambda_handler(event, context):
  
# 1. Read in data from organizeddomains s3
  obj = s3_client.get_object(Bucket= S3_BUCKET_NAME, Key= S3_BUCKET_PREFIX) 
  event_master_df = pd.read_csv(obj['Body'])

# 2. Writting data to DynamoDB

  today_day = datetime.datetime.today().strftime('%A')
  today_date = datetime.date.today()
  for index, row in event_master_df.iterrows():
    startdate = parse(row['start_date']).date()
    enddate = parse(row['end_date']).date()
    # print(today_day)
    pk = "na"
    if startdate == enddate:  ## checking if the event is adhoc
      # print("Adhoc")
      ## For adhoc event, show event if start date is same as today's date
      if startdate == today_date:   ## ensuring only adhoc events happening today are included
        pk = str(uuid4())[:8] # id
        sk = "peeeq bot" # point of contact
        eventName = row['ea_name']
        imageKey = row['img_key'].split('/')[-1] # image key
        author = "peeeq bot"
        category = row['category'] # Category
        comment = row['description'] # Description
        locationName = row['loc_name'] # location name
        lat = row['lat'] # Lat
        long = row['lng'] # long
        timeOfEvent = str(row['time_of_event'] if row['time_of_event']==row['time_of_event'] else "Not Available")
        price = str(row['price'] if row['price']==row['price'] else "Not Available")
        createdAt = str(today_date) 
        #print(pk)
    elif startdate < enddate:  ## ensuring the event is recurrent
      #print("recurrent")
      ## For recurrent, show event if 'day_of_event' is same as today
      if row['day_of_event'] == today_day:  ## ensuring event is happening today
        pk = str(uuid4())[:8] # id
        sk = "peeeq bot" # point of contact
        eventName = row['ea_name']
        imageKey = row['img_key'].split('/')[-1] # image key
        author = "peeeq bot"
        category = row['category'] # Category
        comment = row['description'] # Description
        locationName = row['loc_name'] # location name
        lat = row['lat'] # Lat
        long = row['lng'] # long
        timeOfEvent = str(row['time_of_event'] if row['time_of_event']==row['time_of_event'] else "Not Available")
        price = str(row['price'] if row['price']==row['price'] else "Not Available")
        createdAt = str(today_date)
        #print(pk)
    else:
      print("some issue with start and end dates.")
      print(startdate,'-', enddate)
    

    if pk != "na":
      PutItemInput = {
        'Item': {
          'pk': {'S': str(pk) },
          'sk': {'S': str(sk) },
          'imageKey': {'S': imageKey},
          'author': {'S': author},
          'category': {'S': category },
          'comment': {'S': comment },
          'locationName': {'S': locationName },
          'createdAt': {'S': createdAt}, ## serves as event date.. i.e. date of occurance of the event
          'lat': {'S': str(lat) },  
          'long': {'S': str(long) },
          'eventName': {'S': eventName },
          'timeOfEvent': {'S': timeOfEvent},
          'price': {'S': price},
          'ttl': {'N':str(int(time.time()) + 24*3600)}, # 24 hours of tt
          } ,
      }
      
      geoDataManager.put_Point(dynamodbgeo.PutPointInput(
        dynamodbgeo.GeoPoint(float(lat),float(long)), # latitude then latitude longitude
        str(uuid4()), # Use this to ensure uniqueness of the hash/range pairs.
        PutItemInput # pass the dict here
      ))

  
  return {
      'statusCode': 200,
      'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps('Hello from your new Amplify Python lambda!')
  }