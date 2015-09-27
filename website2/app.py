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
import folium
from bs4 import BeautifulSoup as bs

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
        #if request.form.get("address"):
        #    app.address = request.form['address']
        #else:
        #    app.address = False
        app.dayofweek = request.form['dayofweek']        
        app.month = request.form['month']        
        #app.direction = request.form['direction']
        app.timeofday = int(request.form['timeofday'])
        app.ampm = request.form['ampm']
        
        #if app.address == False:
        #    app.msg = 'You must enter your desired address.'
        #    return render_template('error_page.html', msg = app.msg)
         
        #params = {'address':str(app.address)}        
        #r=(requests.get('https://maps.googleapis.com/maps/api/geocode/json',params=params)).json()
                
        #app.formatted_address = r['results'][0]['formatted_address']
        #my_latitude = r['results'][0]['geometry']['location']['lat']
        #my_longitude = r['results'][0]['geometry']['location']['lng']
                
        # Make the dataframe
        f=open('../network_mesh_space=0.005_month='+str(app.month)+'_day='+str(app.dayofweek)+'.pickle','rb')
        network = pickle.load(f)
        f.close()
                
        trips = {} #{center_id: [outgoing trips, incoming trips]}

        count_pick_ups = network.loc[(app.timeofday,slice(None),slice(None),slice(None)),:]
        count_pick_ups_index = count_pick_ups.index.values
        for i in count_pick_ups_index:
            try:
                trips[str(int(i[2]))][0] += int(count_pick_ups.ix[i])
            except KeyError:
                trips[str(int(i[2]))] = [int(count_pick_ups.ix[i]),0]

        count_drop_offs = network.loc[(slice(None),app.timeofday,slice(None),slice(None)),:]
        count_drop_offs_index = count_drop_offs.index.values
        for i in count_drop_offs_index:
            try:
                trips[str(int(i[3]))][1] += int(count_drop_offs.ix[i])
            except KeyError:
                trips[str(int(i[3]))] = [0,int(count_drop_offs.ix[i])]
        
        
        tk = trips.keys()
        tv = trips.values()

        map_data = pd.DataFrame({'centers': tk, 'activity' : [i[0]+i[1] for i in tv], 
                                 'attractiveness': [i[1]-i[0] for i in tv]})
        
        
        # Make the grid
        
        f=open('../centers_long_lat_id_mesh_space=0.005.pickle','rb')
        grid = pickle.load(f)
        f.close()
        grid_json = {"type":"FeatureCollection", "features":[]}
        
        add_mesh = 0.005/2
        for index, row in grid.iterrows():
            if str(int(row[2])) in trips.keys():
                popup_content= "Incoming: "+str(trips[str(int(row[2]))][0])+"<br /> outgoing: "+str(trips[str(int(row[2]))][1]) +"<br /> Activity: "+str(trips[str(int(row[2]))][1] + trips[str(int(row[2]))][0]) +"<br /> Attractiveness: "+str(trips[str(int(row[2]))][1] - trips[str(int(row[2]))][0])
                coord = [[row[0]+add_mesh,row[1]+add_mesh],[row[0]+add_mesh,row[1]-add_mesh],[row[0]-add_mesh,row[1]-add_mesh],[row[0]-add_mesh,row[1]+add_mesh],[row[0]+add_mesh,row[1]+add_mesh]]
                dd = {"type":"Feature","id":str(int(row[2])),
                      "properties":{"name":str(int(row[2])),"popupContent":popup_content},
                     "geometry":{"type":"Polygon","coordinates":[coord]}
                     }
                grid_json['features'].append(dd)
        
        
        with open('static/grid.json', 'w') as outfile:
            json.dump(grid_json, outfile)
        
        # Make the map
        
        map_1 = folium.Map(location=[40.74006, -73.98605], zoom_start=12,
                           tiles='Stamen Terrain')
        map_1.lat_lng_popover()
        
        map_1.geo_json(geo_path='static/grid.json', data=map_data,
                       columns=['centers', 'activity'],
                       data_out='static/data.json',
                       threshold_scale=[0, 250, 500, 750, 1000, 2000],
                       key_on='feature.id',fill_color='BuPu', fill_opacity=0.5, line_weight=1,
                       line_opacity=0.8,line_color='black',
                       legend_name='Activity Rate',reset=True)
                       
        map_1.create_map(path='nyc.html')        
        soup = bs(open('nyc.html'), 'html.parser') 
        app.map_head = soup.head
        app.map_div = str(soup.body.div).replace("100%","600px")        
        app.map_script= soup.body.script
                       
        
                       
        return redirect('/graph_page')

@app.route('/graph_page')
def graph_page():
    return render_template('graph.html', maphead = Markup(app.map_head), mapdiv=Markup(app.map_div) ,mapscript=Markup(app.map_script))

if __name__ == '__main__':
    app.run()
