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
import networkx as nx

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
        if request.form.get("address"):
            app.address = request.form['address']
        else:
            app.address = False
        
        app.dayofweek = request.form['dayofweek']        
        app.month = int(request.form['month'])        
        app.direction = request.form['direction']
        app.timeofday = int(request.form['timeofday'])
        app.ampm = request.form['ampm']
        
        if app.ampm == "pm":
            app.timeofday+=12
            
        #print "address", app.address
        #print "dayofweek" , app.dayofweek
        #print "month", app.month
        #print "direction", app.direction
        #print "timeofday", app.timeofday
        #print "ampm", app.ampm
        
        if app.address != False:
         
            params = {'address':str(app.address)}        
            r=(requests.get('https://maps.googleapis.com/maps/api/geocode/json',params=params)).json()
                   
            app.formatted_address = r['results'][0]['formatted_address']
            my_latitude = r['results'][0]['geometry']['location']['lat']
            my_longitude = r['results'][0]['geometry']['location']['lng']
            
            x_min = -74.293396 #longitude  SW: 40.481965, -74.293396 NE:40.911486, -73.733866
            x_max = -73.733866 #longitude
            y_min = 40.481965 #latitude
            y_max = 40.911486 #latitude
            mesh_space = 0.0025
        
            if my_latitude < y_min or my_latitude >= y_max or my_longitude < x_min or my_longitude>= x_max or app.address == "" or app.address == False:
                app.msg = 'The address you entered is outside the boundaries of NYC.'
                return render_template('error_page.html', msg = app.msg)
        
        
            centers_x,centers_rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
            centers_y,centers_ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")
          
            my_center_id = get_center_id(my_longitude,my_latitude,x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,mesh_space=mesh_space)
            
        # Make the dataframe
        f=open('../network_mesh_space=0.0025_month='+str(app.month)+'_day='+str(app.dayofweek)+'.pickle','rb')
        network = pickle.load(f)
        f.close()
               
        if app.address != False: 
            if app.direction == "from":
                #n0 = network.loc(axis=0)[:,:,my_center_id,:].reset_index()
                n0 = network.loc(axis=0)[0,0,:,:].reset_index()
                rows = [ 4309, 19125,  6619, 13648, 21587,  6194, 22422,  8247, 10405,  1773, 17665,  1911,
                         9502, 10573, 10028, 19780, 23623,  5649, 24906,  4656,   213, 14772, 26234, 25437,
                        14741,  2265, 21974,  1639,  3720, 13809,  7272, 27489,  9211,  3625,  9885, 12534,
                        22791,  9720, 11411,  9722, 12769, 22393, 16275,  5585,   288,  8995, 27861, 10421,
                         3379, 19055, 16321,  2058, 18610, 20557, 10360, 26626, 13097,  7304, 12535, 18328,
                         2825, 25743, 26901, 28509, 14744, 23308,  9451, 21275,    46, 18453, 18003, 13028,
                        16514,  4399, 28852, 22544, 27117,  4448,  6113,  1891, 25475, 28014, 24150, 11133,
                        15311,  7725,  1907,  2831,  2432,    71, 24829, 21427,  8710, 10858, 16413,   503,
                        18146, 12381, 26018, 13411,  1211, 28883, 24705,  2996, 25022,  7968,  3822, 12439,
                        22254, 11898, 17638, 24629, 13408,  5508, 18977, 21079,  5197,  7006, 19837,  4839,
                        13180, 21963, 20695, 24777, 20128, 16570, 12167, 22923,  7314,   919,  4058, 16426,
                        13154, 23515, 27967, 28810, 12379, 23697, 14048, 14816, 18752,  9806, 28308, 24397,
                        22059,    46, 24013,  1409, 22342, 23886]
                n00 = n0.ix[rows[0:150]]
                gr = n0[['dropoff_center',0]].groupby('dropoff_center', as_index=True).sum()
                gr = gr.sort(columns=0,ascending=False).iloc[0:10]
            elif app.direction == "to":
                n0 = network.loc(axis=0)[:,:,:,my_center_id].reset_index()
                gr = n0[['pickup_center',0]].groupby('pickup_center', as_index=True).sum()
                gr = gr.sort(columns=0,ascending=False).iloc[0:10]        
                
        trips = {} #{center_id: [outgoing trips, incoming trips]}
        count_pick_ups = network.loc(axis=0)[app.timeofday,:,:,:]
        count_pick_ups_index = count_pick_ups.index.values
        for i in count_pick_ups_index:
            try:
                trips[str(int(i[2]))][0] += int(count_pick_ups.ix[i])
            except KeyError:
                trips[str(int(i[2]))] = [int(count_pick_ups.ix[i]),0]
        count_drop_offs = network.loc(axis=0)[:,app.timeofday,:,:]
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
        
        f=open('../centers_long_lat_id_mesh_space=0.0025.pickle','rb')
        grid = pickle.load(f)
        f.close()
        grid_json = {"type":"FeatureCollection", "features":[]}
        
        add_mesh = 0.0025/2
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
        
        map_1 = folium.Map(location=[40.7114, -73.9088], zoom_start=12, tiles='Stamen Terrain',width=900, height = 900)
        map_1.lat_lng_popover()
        
        #############################################################################
        ###############ADD MAIN IN AND OUT NETWORK HUBS##############################
        
        #net = network.loc(axis=0)[app.timeofday,:,:,:]
        #net = net.reset_index()
        #net = net[['pickup_center','dropoff_center',0]]
        #net = np.array(net)
        #net = net.astype(int)
        #g=nx.MultiDiGraph()
        #g.add_weighted_edges_from(net,weight='weight')
        #outdegrees = g.out_degree(weight='weight')
        #outdegrees = [[i, outdegrees[i]] for i in outdegrees]
        #outdegrees = sorted(outdegrees,key=lambda x: x[1])
        #outdegrees = outdegrees[-5:]
        #
        #net = network.loc(axis=0)[:,app.timeofday,:,:]
        #net = net.reset_index()
        #net = net[['pickup_center','dropoff_center',0]]
        #net = np.array(net)
        #net = net.astype(int)
        #g=nx.MultiDiGraph()
        #g.add_weighted_edges_from(net,weight='weight')
        #indegrees = g.in_degree(weight='weight')
        #indegrees = [[i, indegrees[i]] for i in indegrees]
        #indegrees = sorted(indegrees,key=lambda x: x[1])
        #indegrees = indegrees[-5:]
        #
        #for i in outdegrees:
        #    location = get_center_coordinates(i[0],x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,mesh_space=mesh_space)
        #    map_1.circle_marker(location=(location[1],location[0]), radius=80, popup="Number of trips from hub: "+str(i[1]),
        #                    fill_color='green',line_color='green',fill_opacity=0.7)        
        #
        #for i in indegrees:
        #    location = get_center_coordinates(i[0],x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,mesh_space=mesh_space)
        #    map_1.circle_marker(location=(location[1],location[0]), radius=50, popup="Number of trips to hub: "+str(i[1]),
        #                        fill_color='blue',line_color='blue',fill_opacity=0.7)
        
        ##########################################################################################
        ##########################################################################################
        
        ##########################################################################################
        ###############ADD MARKER AT CHOSEN ADDRESS###############################################
        
        #if app.address != False: #add a marker at my address
        #    map_1.circle_marker(location=(my_latitude,my_longitude),radius=60,popup=str(app.formatted_address),line_color='red',
        #          fill_color='red', fill_opacity=0.4)

        ##########################################################################################
        ##########################################################################################
        
        ##########################################################################################
        #############ADD LINES TO MAP#############################################################
        
        if app.address != False:
            for index, row in n00.iterrows():
                p_f = get_center_coordinates(int(row['pickup_center']),x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)
                p_i = get_center_coordinates(int(row['dropoff_center']),x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)
                map_1.line(locations=[(p_i[1], p_i[0]), (p_f[1], p_f[0])],line_weight=2,line_opacity=1,line_color='black',popup=0)            
        
        ##########################################################################################
        ##########################################################################################

        ##########################################################################################
        #############Add grid to map##############################################################
        
        #map_1.geo_json(geo_path='static/grid.json', data=map_data,
        #               columns=['centers', 'activity'],
        #               data_out='static/data.json',
        #               threshold_scale=[10, 100, 200, 300, 500, 600],
        #               key_on='feature.id',fill_color='BuPu', fill_opacity=0.5, line_weight=1,
        #               line_opacity=0.2,line_color='black',
        #               legend_name='Activity Rate',reset=True)

        ##########################################################################################
        ##########################################################################################
        
        ##########################################################################################
        ##############Create map and prepare Flask variables######################################
        
        map_1.create_map(path='nyc.html')        
        soup = bs(open('nyc.html'), 'html.parser') 
        app.map_head = soup.head
        app.map_div = str(soup.body.div) #.replace("100%","800px")        
        app.map_script= soup.body.script
        ##########################################################################################
        ##########################################################################################
        
        ##########################################################################################
        ###ADD plot of NUMBER OF TRIPS (PICK UP AND DROPOFF FROM LOCATION)########################
        ###BOKEH BLOCK############################################################################
        app.script_graph2 = None
        app.div_graph2 = None
        if app.address != False: #This get plotted only if the user entered a location
            pickup_count = [0 for i in range(24)]
            dropoff_count = [0 for i in range(24)]
            idx = pd.IndexSlice
            for ind in network.index.levels[0]:
                pickup_count[ind] = int(network.loc(axis=0)[ind,:,26241,:].sum())
                dropoff_count[ind] = int(network.loc(axis=0)[:,ind,:,26241].sum()[0])            
            TOOLS="pan,wheel_zoom,box_zoom,reset,save"
            
            p2 = figure(tools=TOOLS, plot_width=400, plot_height=400, x_axis_label='Time',y_axis_label='Number of trips')#,x_axis_type='datetime')
            p2.line(np.array(range(24)), pickup_count,line_width=2, color="blue", legend="Average pickups from your location")
            p2.line(np.array(range(24)), dropoff_count,line_width=2, color="red",legend="Average dropoffs at your location")
            
            script_graph2, div_graph2 = components(p2)        
            app.script_graph2 = script_graph2
            app.div_graph2 = div_graph2
        
        ###END BOKEH BLOCK########################################################################
        ##########################################################################################
             
        return redirect('/graph_page')

@app.route('/graph_page')
def graph_page():
    return render_template('graph.html', maphead = Markup(app.map_head), mapdiv=Markup(app.map_div) ,mapscript=Markup(app.map_script),
                            script_graph2=Markup(app.script_graph2) ,div_graph2=Markup(app.div_graph2))

if __name__ == '__main__':
    app.run()
