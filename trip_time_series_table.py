import requests
import simplejson as json
import mysql.connector
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from identify_points import get_center_id

try:
    con = mysql.connector.connect(host="localhost", user="hernan",  passwd="hernan", db="trips")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

for id in range(1001,1741):  #let's make this in chunks of data
    print 'id', id
    sql_taxi_trips ="SELECT id, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude FROM taxi_trip WHERE id>"+str(id*100000)+" AND id<="+str((id+1)*100000)
    df_taxi_trip = pd.read_sql_query(sql_taxi_trips, con, index_col='id')
    #df_taxi_trip['pickup_county'] = df_taxi_trip.apply(lambda x: get_county(x['pickup_longitude'], x['pickup_latitude']), axis=1)
    #df_taxi_trip['dropoff_county'] = df_taxi_trip.apply(lambda x: get_county(x['dropoff_longitude'], x['dropoff_latitude']), axis=1)
    df_taxi_trip['pickup_center'] = df_taxi_trip.apply(lambda x: get_center_id(x['pickup_longitude'], x['pickup_latitude']), axis=1)
    df_taxi_trip['dropoff_center'] = df_taxi_trip.apply(lambda x: get_center_id(x['dropoff_longitude'], x['dropoff_latitude']), axis=1)
    df_taxi_trip[['pickup_center','dropoff_center']].to_sql(con=con, name='trip_centers', index_label='id',if_exists='append', flavor='mysql')
