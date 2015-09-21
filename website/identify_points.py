import numpy as np


def get_center_id(px,py):
    """
    For a given point p=(px,py) within the boundary (x_min,x_max,y_min,y_max)
    it returns an integer that identifies the location of that point
    in a grid of a given mesh_space.
    
    Numpy is required.
    
    In other words, it return the value of l as exemplified below.
    
    That point corresponds to the l-th element in a matrix counting along rows,
    The count along the matrix starts from 1.
    for example matrix elements
    p=(1,1) p=(1,2)
    p=(2,1) p=(2,2)
    Correspond to 
    l=1 l=2
    l=3 l=4
    """    
    
    if px<x_min or px>x_max or py<y_min or py>y_max:
        return -1;
        #raise ValueError("Error: data point outside of grid boundaries")
    
    x,rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
    y,ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")
    
    l = int(round((py-y_min)/ry))*(len(x))+int(round((px-x_min)/rx))+1
    
    return l
    

def get_center_coordinates(l):
    """
    This is the inverse of function <get_center_id>.
    For an integer value l it returns a tuple p=(x,y) where
    p corresponds to the coordinates of a grid center.
    
    Example:
    That point corresponds to the l-th element in a matrix counting along rows,
    The count along the matrix starts from 1.
    for example
    l=1 l=2
    l=3 l=4    
    Corresponds to 
    p=(1,1) p=(1,2)
    p=(2,1) p=(2,2)
    """
    
    x,rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
    y,ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")    
    
    if l<=0 or l>len(x)*len(y):
        return -1
        #raise ValueError("Value of l is not in the grid")
        
    p = (x[(l%len(x))-1],y[(l-1)/len(x)])
    
    return p


if __name__ == '__main__':
    x_min = -74.293396 #longitude  SW: 40.481965, -74.293396 NE:40.911486, -73.733866
    x_max = -73.733866 #longitude
    y_min = 40.481965 #latitude
    y_max = 40.911486 #latitude
    mesh_space = 0.01
    
    
    #x_min = 1.5
    #x_max = 3.
    #y_min = 1.
    #y_max = 4.
    #mesh_space = 0.6
    
    #x,rx=np.linspace(x_min,x_max,(x_max-x_min)/mesh_space,retstep="True")
    #y,ry=np.linspace(y_min,y_max,(y_max-y_min)/mesh_space,retstep="True")
    #
    #print x
    #print y
    #
    #print len(x), rx
    #print len(y), ry
    ##For another arbitrary grid point in space
    #s = (2.9,79)
    #print s
    #This point belongs to the grid (or cluster)
    s=(-73.979567307692307, 40.759321839080464)
    l = get_center_id(s[0],s[1],x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)
    print l
    
    l=332
    p = get_center_coordinates(l, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max,mesh_space=mesh_space)
    print p