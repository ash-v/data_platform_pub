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
  api_key = "AIzaSyAJGypyvT3CDq1ChkwgH93k3pnLL0uqTiU"
  req = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key={}".format(api_key))
  print(req.json()["results"][0]["geometry"]["location"])
  
  return {
      'statusCode': 200,
      'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps('Hello from your new Amplify Python lambda!')
  }