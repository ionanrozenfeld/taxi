from flask import Flask, render_template, request, redirect, Markup
from bokeh.plotting import figure, output_file, show
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

        x_min = -74.293396 #longitude  SW: 40.481965, -74.293396 NE:40.911486, -73.733866
        x_max = -73.733866 #longitude
        y_min = 40.481965 #latitude
        y_max = 40.911486 #latitude
        mesh_space = 0.01
        
        if my_latitude < y_min or my_latitude >= y_max or my_longitude < x_min or my_longitude>= x_max or app.address == "" or app.address == False:
            app.msg = 'The address you entered is outside the boundaries of NYC.'
            return render_template('error_page.html', msg = app.msg)


        centers_x,centers_rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
        centers_y,centers_ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")
          
        my_center_id = get_center_id(my_longitude,my_latitude,x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max,mesh_space=mesh_space)
        
        input = open('../network_mesh_space=0.01_day='+str(app.dayofweek)+'.pickle','rb')        
        network_df = pickle.load(input)
        input.close()
        
        input = open('../main_data_mesh_space=0.01_day='+str(app.dayofweek)+'.pickle','rb')
        data_df = pickle.load(input)
        input.close()
                
                
        ##################################################
        ########Bokeh MAP block##############################
        x_range = Range1d()
        y_range = Range1d()
        
        # JSON style string taken from: https://snazzymaps.com/style/1/pale-dawn
        map_options = GMapOptions(lat=my_latitude, lng=my_longitude, map_type="roadmap", zoom=13, styles="""
        [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},
        {"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},
        {"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},
        {"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},
        {"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},
        {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},
        {"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},
        {"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},
        {"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}]""")
         
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title = ""
            #plot_width=750, plot_height=750
        )
        
        plot.plot_width = 750
        plot.plot_height = 750
        
        source = ColumnDataSource(
            data=dict(
                lat=[my_latitude],
                lon=[my_longitude],
                fill=['orange', 'blue', 'green']
            )
        )
        
        circle = Circle(x="lon", y="lat", size=10, fill_color="fill", line_color="black")
        plot.add_glyph(source, circle)
           
        #hover.tooltips = [
            #("index", "$index"),
            #("(x,y)", "($x, $y)"),
            #("radius", "@radius"),
            #("fill color", "$color[hex, swatch]:fill_color"),
            #("foo", "@foo"),
            #("bar", "@bar"),
        #]
        
        if app.ampm == "pm":
            app.timeofday = app.timeofday +24
        
        if app.direction == "from":
            n0 = network_df[app.timeofday][my_center_id]
            n0.sort(ascending=False,axis=1)
            n0 = n0.irow(range(10))
        elif app.direction == "to":
            n0 = network_df[app.timeofday][:,my_center_id]
            n0.sort(ascending=False,axis=1)
            n0 = n0.irow(range(10))
        
        #widths = [9,8,8,7,6,5,4,3,2,1]
        ww = 0.
        for index, row in n0.iteritems():
            ww += 0.5
            #p_i = get_center_coordinates(my_center_id,x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)
            p_f = get_center_coordinates(index,x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)

            ss = ColumnDataSource(
            data=dict(
                lat=[my_latitude,p_f[1]],
                lon=[my_longitude,p_f[0]],
            ))
            line = Line(x="lon", y="lat", line_width=ww)
            plot.add_glyph(ss, line)
            
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_select = BoxSelectTool()
        
        plot.add_tools(pan, wheel_zoom, box_select)
        
        #xaxis = LinearAxis(axis_label="lat", major_tick_in=0, formatter=NumeralTickFormatter(format="0.000"))
        #plot.add_layout(xaxis, 'below')
        
        #yaxis = LinearAxis(axis_label="lon", major_tick_in=0, formatter=PrintfTickFormatter(format="%.3f"))
        #plot.add_layout(yaxis, 'left')
        
        overlay = BoxSelectionOverlay(tool=box_select)
        plot.add_layout(overlay)
                
        app.script, app.div = components(plot)

        ##################################################
        ##################################################
        
        ##################################################
        ########Bokeh FIG block##############################
    
        # select the tools we want
        TOOLS="pan,wheel_zoom,box_zoom,reset,save"
    
        #print datetime.datetime(hour=int(33)/2, minute=int(33)%2*30)
        #print data_df.index
        
        p1 = figure(tools=TOOLS, plot_width=400, plot_height=400, x_axis_label='Time',y_axis_label='Number of trips')#,x_axis_type='datetime')
        p1.line((data_df.index)/2, data_df['number_of_pickups_at_time_slot'],line_width=2, color="blue", legend="Total number of pickups in NYC in a typical day")
        p1.line((data_df.index)/2, data_df['number_of_dropoffs_at_time_slot'],line_width=2, color="red",legend="Total number of dropoffs in NYC in a typical day")
        #p1.circle(dates, closing_prices, fill_color="red", size=6)

        plots = {'Red': p1}
    
        script_graph1, div_graph1 = components(plots)        
        app.script_graph1 = script_graph1
        app.div_graph1 = div_graph1.values()[0]
        ##################################################
        
        ##################################################

        ###ADD plot of NUMBER OF TRIPS (PICK UP AND DROPOFF FROM LOCATION)
        pickup_count = [0 for i in range(48)]
        dropoff_count = [0 for i in range(48)]
        for ind in network_df.index.levels[0]:
            try:
                pickup_count[ind] = network_df[ind][my_center_id].count()
            except KeyError:
                pass
            try:
                dropoff_count[ind] = network_df[ind][:,my_center_id].count()
            except KeyError:
                continue
        
        TOOLS="pan,wheel_zoom,box_zoom,reset,save"
                
        p2 = figure(tools=TOOLS, plot_width=400, plot_height=400, x_axis_label='Time',y_axis_label='Number of trips')#,x_axis_type='datetime')
        p2.line(np.array(range(48))/2, pickup_count,line_width=2, color="blue", legend="Average pickups from your location")
        p2.line(np.array(range(48))/2, dropoff_count,line_width=2, color="red",legend="Average dropoffs at your location")
        #p1.circle(dates, closing_prices, fill_color="red", size=6)
        
        plots2 = {'Red': p2}
        
        script_graph2, div_graph2 = components(plots2)        
        app.script_graph2 = script_graph2
        app.div_graph2 = div_graph2.values()[0]
        print "here"
        return redirect('/graph_page')

@app.route('/graph_page')
def graph_page():
    return render_template('graph.html', formatted_address = app.formatted_address, scr = Markup(app.script), diiv = Markup(app.div), 
                            scr_script_graph1 = Markup(app.script_graph1), diiv_div_graph1 = Markup(app.div_graph1),
                            scr_script_graph2 = Markup(app.script_graph2), diiv_div_graph2 = Markup(app.div_graph2))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
