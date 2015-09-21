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

#cur = con.cursor()

def get_county(longitude, latitude):
    """
    For a given longitude, latitude it returns the county from the google maps api
    """
    
    #print longitude, latitude
    params = {'latitude': str(latitude), 'longitude':str(longitude), 'format':'json'}
    r=requests.get('http://www.broadbandmap.gov/broadbandmap/census/county',params=params)
    d = r.json()

    return d['Results']['county'][0]['name']
    

for id in range(4,174000):  #let's make this in chunks of data
    print 'id', id
    #sql_taxi_trips ="SELECT id, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude FROM taxi_trip WHERE id>"+str(id*1000)+" AND id<="+str((id+1)*1000)
    #df_taxi_trip = pd.read_sql_query(sql_taxi_trips, con, index_col='id')
    df_taxi_trip['pickup_county'] = df_taxi_trip.apply(lambda x: get_county(x['pickup_longitude'], x['pickup_latitude']), axis=1)
    df_taxi_trip['dropoff_county'] = df_taxi_trip.apply(lambda x: get_county(x['dropoff_longitude'], x['dropoff_latitude']), axis=1)
    df_taxi_trip['zone_id_pickup'] = df_taxi_trip.apply(lambda x: get_center_id(x['pickup_longitude'], x['pickup_latitude']), axis=1)
    df_taxi_trip['zone_id_dropoff'] = df_taxi_trip.apply(lambda x: get_center_id(x['dropoff_longitude'], x['dropoff_latitude']), axis=1)
    print 'writting to DB'
    df_taxi_trip[['zone_id_pickup','zone_id_dropoff','pickup_county','dropoff_county']].to_sql(con=con, name='trip_zones', index_label='id',if_exists='append', flavor='mysql')
    
#
#
#
#
#
#add_zone = ("INSERT INTO zone_centers "
#              "(longitude, latitude) "
#              "VALUES (%(longitude)s, %(latitude)s)")
#
#cur.execute(add_zone, zone_center)
#con.commit()
#
#r=requests.get('http://maps.googleapis.com/maps/api/geocode/json?latlng=40.759526,-73.923809&sensor=false')
#print r.json()
#
#for i in d['results'][0]['address_components']:
#    if i['types'] == [ "administrative_area_level_2", "political" ]:
#        print i['long_name']
#        