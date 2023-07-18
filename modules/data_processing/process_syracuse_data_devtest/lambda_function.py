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
#Make sure you provide / in the end
prefix = 'syracuse/' 

clients3 = boto3.client('s3')

resources3 = boto3.resource('s3')
rawzone = resources3.Bucket(rawzone_bucket)
#orgdomainzone = resources3.Bucket(orgdomain_bucket)

## column 'event_date' is added to this list
columns_currently_used = ['event_url','ea_name','loc_name', 'loc_address', 'img_url', 'img_key', 'lat', 'lng', 'day_of_event', 'time_of_event', 'frequency', 'start_date', 'end_date', 'category', 'description', 'contact_phone', 'price']


# def get_removed_rows_df(todays_df, yesterdays_df):
#     #print(todays_df.equals(yesterdays_df))
#     #merged_df = todays_df.merge(yesterdays_df, on=columns_currently_used, how = 'outer' ,indicator=True)
#     #rows_added = todays_df.merge(yesterdays_df, on=columns_currently_used, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
#     rows_removed = todays_df.merge(yesterdays_df, on=columns_currently_used, how = 'outer' ,indicator=True).loc[lambda x : x['_merge']=='right_only']
#     return rows_removed
    
def calc_event_date(startdate, enddate, day_of_event):

    today_date = date.today()
    #print(today_date)
    sevent_date = today_date + timedelta(days = 6)
    #print(sevent_date)
    st_dt = parse(startdate).date()
    #print(st_dt)
    ed_dt = parse(enddate).date()
    dy_of_event = parse(day_of_event).strftime("%w") # given int value of day
    if st_dt == ed_dt:
        return st_dt
    else:
        # print(startdate)
        # print(enddate)
        # print(day_of_event)
        # print("--------")
        # print(dy_of_event)
        # print(st_dy)
        startdate_of_interest = st_dt if st_dt > today_date else today_date
        enddate_of_interest = ed_dt if ed_dt < sevent_date else sevent_date
        start_day = startdate_of_interest.strftime("%w")   # int value of st_dt
        day_diff = int(start_day) - int(dy_of_event)
     #   final_day_diff = day_diff if day_diff >= 0 else 7 + day_diff
        final_day_diff = int(dy_of_event) - int(start_day) if int(start_day) <= int(dy_of_event) else (int(dy_of_event) + 7) - int(start_day)
       # print(final_day_diff)
        event_date = startdate_of_interest + timedelta(days = final_day_diff)
        # print(event_date)
        # print(type(event_date))
        if event_date <= enddate_of_interest: 
            #print("startdate:", startdate)
            #print("startdate_of_interest:", startdate_of_interest)
            #print("enddate:",enddate)
            #print("day_of_event:",day_of_event)
            #print(event_date)
            #print("--------")
            return event_date
        else:
            return(parse("1970-01-01"))  # event will not be shown if the event date ends up being after event end date
            
def is_event_date_in_range(event_date):
    today_date = date.today()
    #print(today_date)
    sevent_date = today_date + timedelta(days = 6)
    if today_date <= event_date and event_date <= sevent_date:
        return True
    else:
        return False


def lambda_handler(event, context):
    #
    # list of syracuse establishments
    syracuse_targets = [] # targets are establishments
    result = clients3.list_objects(Bucket=rawzone_bucket, Prefix=prefix, Delimiter='/')
    for o in result.get('CommonPrefixes'):
        #print(o.get('Prefix'))
        syracuse_targets.append(o.get('Prefix'))
    
    cum_rows_added_df = pd.DataFrame()
    cum_rows_removed_df = pd.DataFrame()
    today_date = date.today()
    seventh_date = today_date + timedelta(days = 6)
    # print(type(today_date))
    # print(type(seventh_date))
    
    for locs in syracuse_targets:
        # 1. calculate new updates recieved today - new events, updates to existing events
        #print(locs)
        ## func that returns diff, on none, for locs
        dates_list = []
        for object_summary in rawzone.objects.filter(Prefix=locs):
            #print(datetime.strptime(object_summary.key.split('/')[-2], "%Y-%m-%d").date())
            dates_list.append(datetime.strptime(object_summary.key.split('/')[-2], "%Y-%m-%d").date())
            # syracuse_targets.append(o.get('Prefix'))
        dates_list = sorted(dates_list) # ascending sort
       # print(len(dates_list))  ## Add an exception to handle if scrapper didn't run
        todays_prefix = locs + str(dates_list[-1]) +'/df.csv'
        todays_obj = clients3.get_object(Bucket= rawzone_bucket, Key= todays_prefix) 
        todays_df = pd.read_csv(todays_obj['Body'])
        # print(locs)
        # #todays_df.columns = todays_df.columns.str.replace(' ','')
        # print(list(todays_df.columns))
        # print(todays_df.shape)
        if todays_df.shape[0] > 0:
            todays_df = todays_df[columns_currently_used]
            cum_rows_added_df = pd.concat([cum_rows_added_df, todays_df], ignore_index = True)
        #cum_rows_removed_df = pd.concat([cum_rows_removed_df, rows_removed], ignore_index = True)
        
    
    ## filling in end_date = start_date for adhoc events
    cum_rows_added_df.end_date.fillna(cum_rows_added_df.start_date, inplace=True) 
    #print(cum_rows_added_df.shape[0])
    
    event_master_df = cum_rows_added_df
    
    # remove duplicate
    # Add sanity check to remove any duplicate event_urls... there should never be two rows with same event_urls
    event_master_df = event_master_df.drop_duplicates(subset=['ea_name','loc_address','day_of_event','start_date','end_date'], ignore_index= True) #subset=['event_url', 'lat','lng','day_of_event'],
    
    
    event_master_df['event_date'] = event_master_df.apply(lambda row: calc_event_date(row['start_date'], row['end_date'], row['day_of_event']), axis = 1)
    
    # print(event_master_df.shape)
    # event_master_df = event_master_df[ pd.to_datetime(event_master_df['event_date']).floor('D') >= today_date and pd.to_datetime(event_master_df['event_date']).floor('D') <= seventh_date ] 
    
    event_master_df['is_event_in_range'] = event_master_df.apply(lambda row: is_event_date_in_range(row['event_date']), axis = 1)
    
    event_master_df = event_master_df[event_master_df['is_event_in_range']]
    # print(event_master_df.shape)
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