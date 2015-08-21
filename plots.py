from string import *
import time
from math import *
import matplotlib.pyplot as plt

pick_up_time = []
distance = []
time_series1 = {}
time_series2 = {}
with open('trip_data_1.csv', 'r') as f:
    for line in f:
        if "medallion" in line:
            continue
        ld=split(line,",")
        ld[-1] = ld[-1].strip()
        try:
            if float(ld[-1]) != 0.0:
                t = time.strptime(ld[5], "%Y-%m-%d %H:%M:%S")
                t2 = (t.tm_hour)*4 + (t.tm_min)/15
                pick_up_time.append(t2)
                distance.append(sqrt((float(ld[-1])-float(ld[-3]))**2 + (float(ld[-2])-float(ld[-4]))**2 ))
                if float(ld[-4]) >= -73.977637 and float(ld[-4]) < -73.970969 and float(ld[-3]) >= 40.757924 and float(ld[-3]) < 40.758359:
                    #print  "time_series1",ld[-4], ld[-3]
                    try:
                        time_series1[t2] += 1
                    except KeyError:
                        time_series1[t2] = 1
                elif float(ld[-4]) >= -74.007291 and float(ld[-4]) < -73.996965 and float(ld[-3]) >= 40.742209 and float(ld[-3]) < 40.743481:
                    #print  "time_series1",ld[-4], ld[-3]
                    try:
                        time_series2[t2] += 1
                    except KeyError:
                        time_series2[t2] = 1
        except ValueError:
            continue

f1 = plt.figure()
ax1 = f1.add_subplot(111)
dist_dict = {}
for i in range(len(pick_up_time)):
    try:
        dist_dict[pick_up_time[i]/4.].append(distance[i])
    except KeyError:
        dist_dict[pick_up_time[i]/4.] = [distance[i]]
d1 = [[],[]]
for i in dist_dict:
    d1[0].append(i)
    d1[1].append(sum(dist_dict[i])/float(len(dist_dict[i])))
    
ax1.plot(d1[0],d1[1],marker='o',linestyle='None',color='b')
ax1.set_xlabel('time of the day (in hours)')
ax1.set_ylabel('mean distance (arbitrary units)')

#Time series
norm_time_series1 = sum(time_series1.values())
norm_time_series2 = sum(time_series2.values())
t1= [[],[]]
for i in time_series1:
    t1[0].append(i/4.)
    t1[1].append(time_series1[i]/float(norm_time_series1))

t2= [[],[]]
for i in time_series2:
    t2[0].append(i/4.)
    t2[1].append(time_series2[i]/float(norm_time_series2))

f2 = plt.figure()
ax2 = f2.add_subplot(111)

ax2.plot(t1[0],t1[1],marker='o',linestyle='-',color='b',label='Midtown')
ax2.plot(t2[0],t2[1],marker='+',linestyle='-.',color='r',label='Chelsea')
ax2.set_xlabel('time of the day (in hours)')
ax2.set_ylabel('fraction of pick-ups')

plt.show()
    
