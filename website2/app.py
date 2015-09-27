from flask import Flask, render_template, request, redirect, Markup
from bokeh.plotting import figure, output_file, show, gridplot
from bokeh.models import Range1d
from bokeh.embed import components
from datetime import date, timedelta, datetime
import requests
import simplejson as json
import numpy as np
import pandas as pd
from identify_points import get_center_id, get_center_coordinates
import mysql.connector
import pickle

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
        if request.form.get("address"):
            app.address = request.form['address']
        else:
            app.address = False
        app.dayofweek = request.form['dayofweek']        
        app.direction = request.form['direction']
        app.timeofday = int(request.form['timeofday'])
        app.ampm = request.form['ampm']
        
        if app.address == False:
            app.msg = 'You must enter your desired address.'
            return render_template('error_page.html', msg = app.msg)
         
        params = {'address':str(app.address)}        
        r=(requests.get('https://maps.googleapis.com/maps/api/geocode/json',params=params)).json()
                
        app.formatted_address = r['results'][0]['formatted_address']
        my_latitude = r['results'][0]['geometry']['location']['lat']
        my_longitude = r['results'][0]['geometry']['location']['lng']
                
    	app.mapscript = """<script>

    		var map = L.map('map').setView([40.75506, -73.98605], 14);

    		L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6IjZjNmRjNzk3ZmE2MTcwOTEwMGY0MzU3YjUzOWFmNWZhIn0.Y8bhBaUMqFiPrDRW9hieoQ', {
    			maxZoom: 18,
    			attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
    				'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
    				'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    			id: 'mapbox.streets'
    		}).addTo(map);


    		L.marker([40.75506, -73.98605]).addTo(map)
    			.bindPopup("<b>Hello world!</b><br />I am a popup.").openPopup();

    		L.circle([40.75506, -73.98605], 250, {
    			color: 'red',
    			fillColor: '#f03',
    			fillOpacity: 0.5
    		}).addTo(map).bindPopup("I am a circle.");

    		L.polygon([
    			[40.74006+0.0025, -73.98605+0.0025],
    			[40.74006+0.0025, -73.98605-0.0025],
    			[40.74006-0.0025, -73.98605-0.0025],
    			[40.74006-0.0025, -73.98605+0.0025]
    		], {color: 'red',
    			fillColor: '#f03',
    			fillOpacity: 0.5
    		}).addTo(map).bindPopup("I am a polygon.");


    		var popup = L.popup();

    		function onMapClick(e) {
    			popup
    				.setLatLng(e.latlng)
    				.setContent("You clicked the map at " + e.latlng.toString())
    				.openOn(map);
    		}

    		map.on('click', onMapClick);

    	</script>"""
        
        return redirect('/graph_page')

@app.route('/graph_page')
def graph_page():
    return render_template('graph.html', mapscript = Markup(app.mapscript))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
