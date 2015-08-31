import mysql.connector
import numpy as np

try:
    con = mysql.connector.connect(host="localhost", user="hernan",  passwd="hernan", db="trips")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

cur = con.cursor()


add_zone = ("INSERT INTO zone_centers "
              "(longitude, latitude) "
              "VALUES (%(longitude)s, %(latitude)s)")

#start 
#
#Delaware County
#PA
#39.853000, -75.381000
#
#end
#
#Hopkinton, RI
#41.430000, -71.750000
#
#with a mesh space of 0.001

min_x = -75.500000 #longitude
max_x = -71.750000 #longitude
min_y = 39.853000 #latitude
max_y = 41.430000 #latitude
mesh_space = 0.001

x = np.linspace(min_x, max_x, (max_x-min_x)/mesh_space)
y = np.linspace(min_y, max_y, (max_y-min_y)/mesh_space)
#xv, yv = np.meshgrid(x, y)

for x in range(-75500, -71750):
    for y in range(39853, 41430):
        zone_center = {
            'longitude': x/1000.,
            'latitude': y/1000.
        }
        cur.execute(add_zone, zone_center)
        con.commit()



#for i in [11,12]:
#    data = open('/Users/hernan/Desktop/DI/taxi/source_data/tripData2013/trip_data_'+str(i)+'.csv')
#    fare = open('/Users/hernan/Desktop/DI/taxi/source_data/faredata2013/trip_fare_'+str(i)+'.csv')
#    for d,f in itertools.izip(data,fare):
#        if 'medallion' in d:
#            continue
#        splt_d = string.split(d,',')
#        splt_f = string.split(f,',')
#        try:
#            trip = {
#                'medallion': splt_d[0],
#                'hack_license': splt_d[1],
#                'vendor_id': splt_d[2],
#                'rate_code': int(splt_d[3]),
#                'store_and_fwd_flag': splt_d[4],
#                'pickup_datetime': datetime.strptime(splt_d[5], '%Y-%m-%d %H:%M:%S'),
#                'dropoff_datetime': datetime.strptime(splt_d[6], '%Y-%m-%d %H:%M:%S'),
#                'passenger_count': int(splt_d[7]),
#                'trip_time_in_secs': int(splt_d[8]),
#                'trip_distance': float(splt_d[9]),
#                'pickup_longitude': float(splt_d[10]),
#                'pickup_latitude': float(splt_d[11]),
#                'dropoff_longitude': float(splt_d[12]),
#                'dropoff_latitude': float(splt_d[13]),
#                'payment_type': splt_f[4],
#                'fare_amount': float(splt_f[5]),
#                'surcharge': float(splt_f[6]),
#                'mta_tax': float(splt_f[7]),
#                'tip_amount': float(splt_f[8]),
#                'tolls_amount': float(splt_f[9]),
#                'total_amount': float(splt_f[10])
#            }
#            cur.execute(add_trip, trip)
#            con.commit()
#        except mysql.connector.errors.DataError: #This happens when latitude or longitude have exorbitant values (mysql fails because it doesn't allow for numbers with more than 2 digits before the decimal point)
#            efile=open('errors','a')
#            print >>efile, "DataError", 'trip_data_'+str(i)+'.csv'
#            print >>efile, splt_d
#            print >>efile, splt_f
#            print >> efile, ''
#            efile.close()
#        except ValueError: #This can happen because some lines are incomplete (e.g., don't have drop-off latitude/longitude)
#            efile=open('errors','a')
#            print >>efile,"ValueError", 'trip_data_'+str(i)+'.csv'
#            print >>efile, splt_d
#            print >>efile, splt_f
#            print >> efile, ''
#            efile.close()




# print all the first cell of all the rows
#for row in cur.fetchall() :
#    print row[0]


con.close()