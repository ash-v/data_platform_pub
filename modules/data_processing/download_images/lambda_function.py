import json
import urllib.request
import cv2  
import numpy as np
import boto3 
import logging 
import sys 
import pymysql
import os


### Get Data from 
s3_client = boto3.client('s3') 
FROM_BUCKET = 'peeeq-datalake-organized-zone' 
FROM_BUCKET_PREFIX = 'event_master.csv'
TO_BUCKET = 'peak8e68841e495b4152a8f0e6935754143a222640-dev' # image bucket

# file_name = '/tmp/img_wip.png' # lambda local file system
width, height = 512, 512 # target dimension



def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
	resp = urllib.request.urlopen(url)  ## 1. download the image using urllib
	image = np.asarray(bytearray(resp.read()), dtype="uint8")  ## 2. convert it into np array
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)  ## 3. read it into opencv format
	# return the image
	return image

def lambda_handler(event, context):
    # 1. Read in data from organizeddomains s3
    obj = s3_client.get_object(Bucket= S3_BUCKET_NAME, Key= S3_BUCKET_PREFIX) 
    event_master_df = pd.read_csv(obj['Body'])
   

    for index, row in event_master_df.iterrows():
        url = row[7] # get the url
        img = url_to_image(url)  # download image from url in cv2 format
        imgResize = cv2.resize(img,(width, height)) # resize img to 512 X 512
        file_name = "/tmp/"+ url.split('/')[-1]
        status = cv2.imwrite(file_name, imgResize) 
        #print("Image written to local file-system : ",status)
        key_name = 'public/'+ url.split('/')[-1]  # going directly to public folder
        s3.upload_file(file_name, bucket, key_name)
        os.remove(file_name)  # cleaing /tmp/ location
        
    return {
        'statusCode': 200,
        'body': json.dumps('Images downloaded  and save to s3 yo!')
    }
