from flask import Flask, render_template, request, redirect, Markup
from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d
from bokeh.embed import components
from datetime import date, timedelta, datetime, time
import requests
import simplejson as json
import numpy as np
import pandas as pd
from identify_points import get_center_id, get_center_coordinates
import mysql.connector

from bokeh.browserlib import view
from bokeh.document import Document
from bokeh.embed import file_html
from bokeh.models.glyphs import Circle, Line
from bokeh.models import (
    GMapPlot, Range1d, ColumnDataSource, LinearAxis,
    PanTool, WheelZoomTool, BoxSelectTool,
    BoxSelectionOverlay, GMapOptions,
    NumeralTickFormatter, PrintfTickFormatter)
from bokeh.resources import INLINE
from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d
from bokeh.embed import components

try:
    connect = mysql.connector.connect(host="localhost", user="hernan",  passwd="hernan", db="trips")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
    
app = Flask(__name__)

app.script = ''
app.div = ''

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        
        return render_template('index.html')
    else:
        #app.address = request.form['address']
        #app.current_location = request.form['current_location']
        #if request.form.get("traffic"):
        #    app.traffic = request.form['traffic']
        #else:
        #    app.traffic = False
        #app.optimize = request.form['radial']        
        #if app.current_location == "" and app.current_location == False:
        #    app.msg = 'You must either enter your desired address or use your current location.'
        #    return render_template('error_page.html', msg = app.msg)

        x_min = -75.500000 #longitude
        x_max = -71.750000 #longitude
        y_min = 39.853000 #latitude
        y_max = 41.430000 #latitude
        mesh_space = 0.006
        
        centers_x,centers_rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
        centers_y,centers_ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")
        
        my_latitude = 40.748347 
        my_longitude = -73.999425
        my_datetime = pd.to_datetime('2015-09-15 15:00:00')
        mesh_space = 0.006 #Corresponds to an area of about 4 by 4 blocks in Manhattan
        time_resolution_in_minutes = 30
        my_day_of_week = my_datetime.dayofweek
        my_time = my_datetime.time()
        time_delta = timedelta(minutes=time_resolution_in_minutes)
        my_time_plus_delta = (my_datetime + time_delta).time()
        
        my_center_id = get_center_id(my_longitude,my_latitude,x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,mesh_space=mesh_space)
        
        sql_query = 'SELECT taxi_trip.id, taxi_trip.fare_amount, taxi_trip.trip_distance, taxi_trip.trip_time_in_secs, taxi_trip.pickup_longitude, taxi_trip.pickup_latitude, taxi_trip.dropoff_longitude, taxi_trip.dropoff_latitude, trip_centers.pickup_center, trip_centers.dropoff_center FROM taxi_trip JOIN trip_centers ON (taxi_trip.id = trip_centers.id) WHERE WEEKDAY(pickup_datetime) = '+str(my_day_of_week)+ ' AND TIME(pickup_datetime) >= "' + str(my_time) + '" AND TIME(pickup_datetime) < "' + str(my_time_plus_delta) + '" AND trip_centers.pickup_center = '+str(my_center_id)+ ' LIMIT 20'
        
        df_mysql2 = pd.read_sql(sql_query, con=connect)
        
        counts=df_mysql2['dropoff_center'].value_counts()
        counts = pd.DataFrame(counts)        
        counts['centers'] = counts.index
        #counts['dropoff_latitude'] = centers_y[(counts['centers']-1)/len(centers_x)]
        #counts['dropoff_longitude'] = centers_x[(counts['centers']%len(centers_x))-1]
        
        
        ##################################################
        ########Bokeh block##############################
        x_range = Range1d()
        y_range = Range1d()
        
        
        # JSON style string taken from: https://snazzymaps.com/style/1/pale-dawn
        map_options = GMapOptions(lat=my_latitude, lng=my_longitude, map_type="roadmap", zoom=13, styles="""
        [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},{"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},{"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}]
        """)
        
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title = ""
        )
        
        source = ColumnDataSource(
            data=dict(
                lat=[my_latitude],
                lon=[my_longitude],
                fill=['orange', 'blue', 'green']
            )
        )
        
        circle = Circle(x="lon", y="lat", size=15, fill_color="fill", line_color="black")
        plot.add_glyph(source, circle)
        
        widths = [9,8,8,7,6,5,4,3,2,1]
        ww = 0
        for index, row in counts.iterrows():
                        
            p = get_center_coordinates(row['centers'],x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)
            print p
            ss = ColumnDataSource(
            data=dict(
                lat=[my_latitude,p[1]],
                lon=[my_longitude,p[0]],
            ))
            line = Line(x="lon", y="lat", line_width=widths[ww])
            plot.add_glyph(ss, line)
            ww += 1
            if ww == 10:
                break
            
        #hover.tooltips = [
        #    ("index", "$index"),
        #    ("(x,y)", "($x, $y)"),
        #    ("radius", "@radius"),
        #    ("fill color", "$color[hex, swatch]:fill_color"),
        #    ("foo", "@foo"),
        #    ("bar", "@bar"),
        #]
        
        
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_select = BoxSelectTool()
        
        plot.add_tools(pan, wheel_zoom, box_select)
        
        xaxis = LinearAxis(axis_label="lat", major_tick_in=0, formatter=NumeralTickFormatter(format="0.000"))
        plot.add_layout(xaxis, 'below')
        
        yaxis = LinearAxis(axis_label="lon", major_tick_in=0, formatter=PrintfTickFormatter(format="%.3f"))
        plot.add_layout(yaxis, 'left')
        
        overlay = BoxSelectionOverlay(tool=box_select)
        plot.add_layout(overlay)
                
        app.script, app.div = components(plot)

        ##################################################
        ##################################################
        
        
        return redirect('/graph_page') 
            
@app.route('/graph_page')
def graph_page():
    return render_template('graph.html', scr = Markup(app.script), diiv = Markup(app.div))

if __name__ == '__main__':
  app.run(host='0.0.0.0')
