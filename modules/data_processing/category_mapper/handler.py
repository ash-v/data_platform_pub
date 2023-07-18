import json
import pandas as pd
import boto3 
from io import StringIO
import csv

resources3 = boto3.resource('s3')
s3_client = boto3.client('s3') 
S3_BUCKET_NAME = 'peeeq-datalake-organized-zone' 
S3_BUCKET_PREFIX = 'event_master_devtest.csv'  ### change this

def normalize_category(curr_category):

    print(curr_category)
    assigned_cat = ""
    if "Art" in curr_category:
        assigned_cat = 'Art Show'
    elif "Music" in curr_category:
        assigned_cat = 'Live Music'
    elif "Trivia" in curr_category:
        assigned_cat = 'Trivia'
    elif "Outdoor" in curr_category or "walk" in curr_category or "run" in curr_category:
        assigned_cat = 'Outdoors'
    else:
        assigned_cat = 'Others'
    
    return assigned_cat


def hello(event, context):

    obj1 = s3_client.get_object(Bucket= S3_BUCKET_NAME, Key= S3_BUCKET_PREFIX) 
    event_master_df = pd.read_csv(obj1['Body'])

    event_master_df["norm_cat"] = event_master_df.apply(lambda x: normalize_category(curr_category=x["category"])  , axis=1)

    print(event_master_df)
    
    csv_buffer = StringIO()
    event_master_df.to_csv(csv_buffer, index= False)
    object_key = 'event_master_devtest.csv'
    resources3.Object(S3_BUCKET_NAME, object_key).put(Body=csv_buffer.getvalue())

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
