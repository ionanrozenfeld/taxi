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

for x in range(-75500, -71751):
    for y in range(39853, 41431):
        zone_center = {
            'longitude': x * mesh_space,
            'latitude': y * mesh_space
        }
        cur.execute(add_zone, zone_center)
        con.commit()

con.close()