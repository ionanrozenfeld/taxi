import mysql.connector
import itertools
import string
from datetime import datetime
from mysql.connector import FieldType
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime, time
from roundTime import roundTime

try:
    connect = mysql.connector.connect(host="localhost", user="hernan",  passwd="hernan", db="trips")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

#cur = con.cursor()

t1 = '2013-01-01 00:00:00'
t2 = '2013-01-01 23:59:59'
t1_datetime = pd.to_datetime(t1)
t2_datetime = pd.to_datetime(t2)

#pickup_longitude
#pickup_latitude
#radius = 20 #Number of blocks around the current location.

sql_query = "SELECT id, fare_amount, trip_distance, trip_time_in_secs, pickup_datetime FROM \
    taxi_trip WHERE pickup_datetime BETWEEN '"+t1+"' AND '"+t2+"'"

#intervals = 1000
#offset = pd.DateOffset(seconds=(t2-t1).total_seconds()/intervals)

time_resolution_in_minutes = 15 #Note that 15 mins this is the default on the roundTime function called later.

offset = pd.DateOffset(minutes=time_resolution_in_minutes)

time_bins = pd.date_range(start=t1_datetime,end=t2_datetime, freq = offset)

#sql_query = "SELECT id, pickup_longitude, pickup_latitude, pickup_datetime FROM taxi_trip WHERE pickup_datetime BETWEEN t1 AND t2"

df_binned = pd.DataFrame([], index=time_bins, columns=['id','fare_amount','trip_distance','trip_time_in_secs'])
fun = lambda x : np.empty(0)
for ccc in df_binned.columns:
    df_binned[ccc] = df_binned[ccc].apply(fun)

df_mysql = pd.read_sql(sql_query, con=connect)  
connect.close()

#Rounding times in pickup_datetime
df_mysql['pickup_datetime']=df_mysql['pickup_datetime'].apply(roundTime)

