# Process Syracuse scraped data
# THIS FUNCTION ENSURE DOES FOLLOWING
# 1. creates a new version of event_master data everytime it runs
# 2. Ensures the time frame for event_master is 7 days rolling
# 3. Combines all scrapped data from establishments in Syracuse, NY into one event_master
# 4. Creates a new variable for each row ( i.e. each event instance) called event_date

import json
import boto3
from datetime import date, datetime, timedelta
from dateutil.parser import parse
import pandas as pd
from io import StringIO
import csv

rawzone_bucket = 'peeeq-datalake-raw-zone'
orgdomain_bucket = 'peeeq-datalake-organized-zone'
prefix = 'syracuse/' 

clients3 = boto3.client('s3')

resources3 = boto3.resource('s3')
rawzone = resources3.Bucket(rawzone_bucket)

## column 'event_date' is added to this list
columns_currently_used = ['event_url','ea_name','loc_name', 'loc_address', 'img_url', 'img_key', 'lat', 'lng', 'day_of_event', 'time_of_event', 'frequency', 'start_date', 'end_date', 'category', 'description', 'contact_phone', 'price']
    
def calc_event_date(startdate, enddate, day_of_event):
    today_date = date.today()
    sevent_date = today_date + timedelta(days = 6)
    st_dt = parse(startdate).date()
    ed_dt = parse(enddate).date()
    dy_of_event = parse(day_of_event).strftime("%w") # given int value of day
    if st_dt == ed_dt:
        return st_dt
    else:
        startdate_of_interest = st_dt if st_dt > today_date else today_date
        enddate_of_interest = ed_dt if ed_dt > sevent_date else sevent_date
        start_day = startdate_of_interest.strftime("%w")   # int value of st_dt
        day_diff = int(start_day) - int(dy_of_event)
        final_day_diff = int(dy_of_event) - int(start_day) if int(start_day) <= int(dy_of_event) else (int(dy_of_event) + 7) - int(start_day)
        event_date = startdate_of_interest + timedelta(days = final_day_diff)
        if event_date <= enddate_of_interest: 
            return event_date
        else:
            return(parse("1970-01-01"))  # event will not be shown if the event date ends up being after event end date
            
def is_event_date_in_range(event_date):
    today_date = date.today()
    sevent_date = today_date + timedelta(days = 6)
    if today_date <= event_date and event_date <= sevent_date:
        return True
    else:
        return False


def lambda_handler(event, context):
    # list of syracuse establishments
    syracuse_targets = [] # targets are establishments
    result = clients3.list_objects(Bucket=rawzone_bucket, Prefix=prefix, Delimiter='/')
    for o in result.get('CommonPrefixes'):
        syracuse_targets.append(o.get('Prefix'))
    
    cum_rows_added_df = pd.DataFrame()
    cum_rows_removed_df = pd.DataFrame()
    today_date = date.today()
    seventh_date = today_date + timedelta(days = 6)
    
    for locs in syracuse_targets:
        # 1. calculate new updates recieved today - new events, updates to existing events
        dates_list = []
        for object_summary in rawzone.objects.filter(Prefix=locs):
            dates_list.append(datetime.strptime(object_summary.key.split('/')[-2], "%Y-%m-%d").date())
        dates_list = sorted(dates_list) # ascending sort
        todays_prefix = locs + str(dates_list[-1]) +'/df.csv'
        todays_obj = clients3.get_object(Bucket= rawzone_bucket, Key= todays_prefix) 
        todays_df = pd.read_csv(todays_obj['Body'])
        todays_df = todays_df[columns_currently_used]
        cum_rows_added_df = pd.concat([cum_rows_added_df, todays_df], ignore_index = True)

    ## filling in end_date = start_date for adhoc events
    cum_rows_added_df.end_date.fillna(cum_rows_added_df.start_date, inplace=True) 
    
    event_master_df = cum_rows_added_df
    
    # remove duplicate
    # Add sanity check to remove any duplicate event_urls... there should never be two rows with same event_urls
    event_master_df = event_master_df.drop_duplicates(subset=['event_url','lat','lng','start_date','end_date','day_of_event'], ignore_index= True) #subset=['event_url'],
    event_master_df['event_date'] = event_master_df.apply(lambda row: calc_event_date(row['start_date'], row['end_date'], row['day_of_event']), axis = 1)
    event_master_df['is_event_in_range'] = event_master_df.apply(lambda row: is_event_date_in_range(row['event_date']), axis = 1)
    event_master_df = event_master_df[event_master_df['is_event_in_range']]

    ## write back event master
    csv_buffer = StringIO()
    event_master_df.to_csv(csv_buffer, index= False)
    object_key = 'event_master_devtest.csv'  
    resources3.Object(orgdomain_bucket, object_key).put(Body=csv_buffer.getvalue())
    #print("object written!")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }