'''
Created on Jun 15, 2009

@author: pankaj
http://blenderartists.org/forum/showthread.php?t=9521
'''

######################################################################
#
# NACA 4-digit airfoil plotter
# 
# (C) march 2003 Wim Van Hoydonck
#
#######################################################################

import numpy

def get_NACA4_data(number):
    p = (number // 1000) / 100.0
    m = (number // 100)%10 / 10.0
    xx = (number % 100) / 100.0
    return get_NACA_data(p, m, xx)

def get_NACA_data(p=0.05, m=0.5, xx=0.1, nv=100, nvbl=10, le=0.01):
    '''    
	p = max camber (in percent of chord)
	xx = airfoil thickness in percent of chord
	nv = (half) number of (total) vertices
	nvbl = number of vertices before le
	le = point on chord
	m = chordwise location of max camber (0 <= m < 1)
    '''
    
    # constants in thickness equation of NACA 4-series (from NASA TM 4741) 
    a0 = 0.2969
    a1 = -0.1260
    a2 = -0.3516
    a3 = 0.2843
    a4 = -0.1015

    pointsx = []
    pointsy = []
    # calculate position of verts
    i = 0.0
    for i in range(2*nv):
        if i <= nv:        # upper surface calculations
            if i < nvbl:        # x distribution before le
                x = i*le/(nvbl-1.0)
            else:                # x distribution after le
                x = le + (1.0-le)*(i-nvbl+1.0)/(nv-nvbl+1.0)
            if x <= m:            # camber line equation before max camber
                # Edit: added condition - pankaj
                if m>0:
                    yc = (p/m**2.0) * ((2.0*m*x)-(x*x))
                else:
                    yc = 0
            else:                # after maxcamber
                yc = (p/((1-m)**2.0))*((1.0-2.0*m) + 2.0*m*x - x**2.0)
            yt = (xx/0.2)*(a0*x**(0.5) + a1*x + a2*x**2.0 + a3*x**3.0 + a4*x**4.0)    # thickness equation
            y = yc + yt            # add thickness to camber for upper surface
            z = 0
        else:                # lower surface
            if i < 2.0*nv - nvbl+1.0:
                x = 1.0 - (i-nv)*(1.0-le)/(nv-nvbl+1.0)
            else:
                x = le*(1.0-(i-2.0*nv+nvbl)/(nvbl-1.0))
            if x <= m:
                # Edit: added condition - pankaj
                if m>0:
                    yc = (p/m**2.0) * ((2.0*m*x)-(x)**2.0)
                else:
                    yc = 0
            else:
                yc = (p/((1-m)**2.0))*((1.0-2.0*m) + 2.0*m*x - x**2.0)
            yt = (xx/0.2)*(a0*x**(0.5) + a1*x + a2*x**2.0 + a3*x**3.0 + a4*x**4.0)
            y = yc - yt
            z = 0
        pointsx.append(x)
        pointsy.append(y)
    ret = numpy.array([pointsx,pointsy])
    return ret.T


if __name__ == '__main__':
    from pylab import plot, show
    points = get_NACA_data()
    plot(points[:,0], points[:,1], '.-')
    #plot(points[0][2:3], points[1][2:3], '.r')
    show()
