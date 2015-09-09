import numpy as np

x_min = 1.5
x_max = 3.
y_min = 1.
y_max = 4.

mesh_space = 0.3

x,rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
y,ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")

#For any given point p
p=(x[2],y[3])

#That point corresponds to the l-th element in a matrix counting along rows,
#The count along the matrix starts from 1.
#for example matrix elements
#(1,1) (1,2)
#(2,1) (2,2)
#Correspond to 
#l=1 l=2
#l=3 l=4

l = int(round((p[1]-y_min)/ry))*(len(x))+int(round((p[0]-x_min)/rx))+1

print "l", l

#For an arbitrary grid point in space
s = (2.2,3.1)
#This point belongs to the grid (or cluster)
print int(round((s[1]-y_min)/ry))*(len(x))+int(round((s[0]-x_min)/rx))+1

#For another arbitrary grid point in space
s = (2.6,3.1)
#This point belongs to the grid (or cluster)
print int(round((s[1]-y_min)/ry))*(len(x))+int(round((s[0]-x_min)/rx))+1

#For yet another arbitrary grid point in space
s = (2.2,1.6)
#This point belongs to the grid (or cluster)
print int(round((s[1]-y_min)/ry))*(len(x))+int(round((s[0]-x_min)/rx))+1
