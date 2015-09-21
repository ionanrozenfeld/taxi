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
        
        if app.address == False:
            app.msg = 'You must enter your desired address.'
            return render_template('error_page.html', msg = app.msg)
                
        params = {'address':str(app.address)}        
        r=(requests.get('https://maps.googleapis.com/maps/api/geocode/json',params=params)).json()
        
        #r = r.json()
        #print r['results'][0]['geometry']['location']['lat']
        
        app.my_latitude = r['results'][0]['geometry']['location']['lat']
        app.my_longitude = r['results'][0]['geometry']['location']['lng']
                
        app.x_min = -74.293396 #longitude  SW: 40.481965, -74.293396 NE:40.911486, -73.733866
        app.x_max = -73.733866 #longitude
        app.y_min = 40.481965 #latitude
        app.y_max = 40.911486 #latitude
        app.mesh_space = 0.01

        if app.my_latitude < app.y_min or app.my_latitude >= app.y_max or app.my_longitude < app.x_min or app.my_longitude>= app.x_max or app.address == "" or app.address == False:
            app.msg = 'The address you entered is outside the boundaries of NYC.'
            return render_template('error_page.html', msg = app.msg)

        app.centers_x,app.centers_rx=np.linspace(app.x_min,app.x_max,(app.x_max-app.x_min)/app.mesh_space,retstep="True")
        app.centers_y,app.centers_ry=np.linspace(app.y_min,app.y_max,(app.y_max-app.y_min)/app.mesh_space,retstep="True")
                
        app.my_center_id = get_center_id(app.my_longitude,app.my_latitude,x_min=app.x_min,x_max=app.x_max,y_min=app.y_min,y_max=app.y_max,mesh_space=app.mesh_space)
        
        
        app.input = open('network_mesh_space=0.01_day='+str(app.dayofweek)+'.pickle','rb')        
        app.network_df = pickle.load(app.input)
        (app.input).close()

        #input = open('../main_data_space=0.01_day='+str(app.dayofweek)+'.pickle','rb')
        #data_df = pickle.load(input)
        #input.close()
        
        #print (app.network_df).head()
        
        ##################################################
        ########Bokeh block##############################
        x_range = Range1d()
        y_range = Range1d()
        
        
        # JSON style string taken from: https://snazzymaps.com/style/1/pale-dawn
        map_options = GMapOptions(lat=app.my_latitude, lng=app.my_longitude, map_type="roadmap", zoom=13, styles="""
        [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},{"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},{"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},{"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},{"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},{"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},{"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}]
        """)
                
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title = ""
            #plot_width=750, plot_height=750
        )
        
        source = ColumnDataSource(
            data=dict(
                lat=[app.my_latitude],
                lon=[app.my_longitude],
                fill=['orange', 'blue', 'green']
            )
        )
        
        
        circle = Circle(x="lon", y="lat", size=3, fill_color="fill", line_color="black")
        plot.add_glyph(source, circle)
                
        n0 = app.network_df[0]
        n0.sort(ascending=False,axis=1)
        n0=n0[0:20]
        #print n0
        
        
        #widths = [9,8,8,7,6,5,4,3,2,1]
        #ww = 0
        for index, row in n0.iteritems():
                        
            p_i = get_center_coordinates(index[0],x_min=app.x_min, x_max=app.x_max, y_min=app.y_min, y_max=app.y_max,mesh_space=app.mesh_space)
            p_f = get_center_coordinates(index[1],x_min=app.x_min, x_max=app.x_max, y_min=app.y_min, y_max=app.y_max,mesh_space=app.mesh_space)
            #
            #ss = ColumnDataSource(
            #data=dict(
            #    lat=[p_i[1],p_f[1]],
            #    lon=[p_i[0],p_f[0]],
            #))
            #line = Line(x="lon", y="lat", line_width=1)
            #plot.add_glyph(ss, line)
            print "ddd", index, row, p_i, p_f
        
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
