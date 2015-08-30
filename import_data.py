import mysql.connector
import itertools
import string
from datetime import datetime

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


add_trip = ("INSERT INTO taxi_trip "
              "(medallion, hack_license, vendor_id, rate_code, store_and_fwd_flag, pickup_datetime, dropoff_datetime, passenger_count, trip_time_in_secs, trip_distance, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, payment_type, fare_amount, surcharge, mta_tax, tip_amount, tolls_amount, total_amount) "
              "VALUES (%(medallion)s, %(hack_license)s, %(vendor_id)s, %(rate_code)s, %(store_and_fwd_flag)s, %(pickup_datetime)s, %(dropoff_datetime)s, %(passenger_count)s, %(trip_time_in_secs)s, %(trip_distance)s, %(pickup_longitude)s, %(pickup_latitude)s,%(dropoff_longitude)s, %(dropoff_latitude)s, %(payment_type)s, %(fare_amount)s, %(surcharge)s, %(mta_tax)s,%(tip_amount)s, %(tolls_amount)s, %(total_amount)s)")


for i in [11,12]:
    data = open('/Users/hernan/Desktop/DI/taxi/source_data/tripData2013/trip_data_'+str(i)+'.csv')
    fare = open('/Users/hernan/Desktop/DI/taxi/source_data/faredata2013/trip_fare_'+str(i)+'.csv')
    for d,f in itertools.izip(data,fare):
        if 'medallion' in d:
            continue
        splt_d = string.split(d,',')
        splt_f = string.split(f,',')
        try:
            trip = {
                'medallion': splt_d[0],
                'hack_license': splt_d[1],
                'vendor_id': splt_d[2],
                'rate_code': int(splt_d[3]),
                'store_and_fwd_flag': splt_d[4],
                'pickup_datetime': datetime.strptime(splt_d[5], '%Y-%m-%d %H:%M:%S'),
                'dropoff_datetime': datetime.strptime(splt_d[6], '%Y-%m-%d %H:%M:%S'),
                'passenger_count': int(splt_d[7]),
                'trip_time_in_secs': int(splt_d[8]),
                'trip_distance': float(splt_d[9]),
                'pickup_longitude': float(splt_d[10]),
                'pickup_latitude': float(splt_d[11]),
                'dropoff_longitude': float(splt_d[12]),
                'dropoff_latitude': float(splt_d[13]),
                'payment_type': splt_f[4],
                'fare_amount': float(splt_f[5]),
                'surcharge': float(splt_f[6]),
                'mta_tax': float(splt_f[7]),
                'tip_amount': float(splt_f[8]),
                'tolls_amount': float(splt_f[9]),
                'total_amount': float(splt_f[10])
            }
            cur.execute(add_trip, trip)
            con.commit()
        except mysql.connector.errors.DataError: #This happens when latitude or longitude have exorbitant values (mysql fails because it doesn't allow for numbers with more than 2 digits before the decimal point)
            efile=open('errors','a')
            print >>efile, "DataError", 'trip_data_'+str(i)+'.csv'
            print >>efile, splt_d
            print >>efile, splt_f
            print >> efile, ''
            efile.close()
        except ValueError: #This can happen because some lines are incomplete (e.g., don't have drop-off latitude/longitude)
            efile=open('errors','a')
            print >>efile,"ValueError", 'trip_data_'+str(i)+'.csv'
            print >>efile, splt_d
            print >>efile, splt_f
            print >> efile, ''
            efile.close()

#cur.execute("SELECT * FROM taxi_trip limit 10")



# print all the first cell of all the rows
#for row in cur.fetchall() :
#    print row[0]


con.close()