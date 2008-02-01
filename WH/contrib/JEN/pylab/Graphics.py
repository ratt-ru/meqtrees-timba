#!/usr/bin/env python

# file: ../contrib/JEN/pylab/Graphics.py

# Author: J.E.Noordam
# 
# Short description:
#   The Grapicset is derived from the Subplot class.
#   It holds a series of Graphics objects.
#
# History:
#    - 29 jan 2008: creation
#
# Remarks:
#
# Description:
#

#-------------------------------------------------------------------------------

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import pylab
import copy
import Subplot

import PointsXY

#======================================================================================

class Graphics (Subplot.Subplot):
    """The Grapicset is derived from the Subplot class.
    It holds one or more Graphics objects."""

    def __init__(self, **kwargs):

        Subplot.Subplot.__init__(self, **kwargs)

        # The objects are kept in the named fields of a dict:
        self._order = []
        self._graphic = dict()

        # Finished:
        return None


    #===============================================================


    def add(self, graphic, key=None):
        """Add a named (key) plottable object to self._graphic"""
        if not isinstance(key, str):
            key = str(len(self._order))       # .....??
        self._graphic[key] = graphic
        self._order.append(key)
        return key

    def remove(self, key):
        """Remove a named object from self._graphic"""
        if self.has_key(key):
            self._grahic.__delitem__(key)
            self._order.__delitem__(key)
        return True

    #===============================================================
    # Access routines:
    #===============================================================

    def len(self):
        """Return the number of its plottable objects"""
        return len(self._order)

    def order(self):
        """Return a list of keys of its plottable objects"""
        return self._order

    def name(self):
        """Return the name (label?) of this Graphics"""
        return self._name

    def has_key(self, key):
        """Check whether self._graphic has the specified key"""
        return self._graphic.has_key(key)

    def __getitem__(self, index):
        """Get the specified plottable object (key or index)"""
        key = None
        if isinstance(index,str):
            key = index
        elif isinstance(index,int):
            key = self._order[index]
        return self._graphic[key]

    #-------------------------------------------------------------

    def yrange(self, margin=0.0, yrange=None):
        """Return [min,max] of all the y-coordinate(s)."""
        yr = None
        for key in self._order:
            yr = self._graphic[key].yrange(margin=margin, yrange=yr)
        return yr

    def xrange(self, margin=0.0, xrange=None):
        """Return [min,max] of all the x-coordinate(s)."""
        xr = None
        for key in self._order:
            xr = self._graphic[key].xrange(margin=margin, xrange=xr)
        return xr


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <Graphics> '+self.name()+':'
        ss += ' n='+str(self.len())
        ss += '  yrange='+str(self.yrange())
        ss += '  xrange='+str(self.xrange())
        return ss

    def oneliners(self):
        """Print its own oneliner, and those of its graphics"""
        print '\n',self.oneliner()
        for key in self._order:
            print '-',key,':',self._graphic[key].oneliner()
        print
        return True


    #===============================================================
    # Plot standalone (testing only?)
    #===============================================================

    def plot(self, figure=1, subplot=111, margin=0.1, dispose='show'):
        """Plot the group of points, using pylab"""
        pylab.figure(figure)
        pylab.subplot(subplot)
        self.plot_axes(xaxis=True, yaxis=True)
        for key in self._order:
            self._graphic[key].plot(margin=0.0, dispose=None)
        self.pylab_window(margin=margin)
        self.pylab_labels()
        pylab.grid(True)
        import Figure
        return Figure.pylab_dispose(dispose)


#========================================================================
# Some convenient 'standard' Graphics classes:
#========================================================================

class Scatter (Graphics):
    """Class derived from Graphics. It represents a scatter-plot
    (markers) of the specified yy [and xx] coordinates.
    """

    def __init__(self, yy=None, xx=None,
                 **kwargs):

        Graphics.__init__(self, **kwargs)

        # Make the PointsXY object, and add it to the internal list:
        kwargs.setdefault('marker','o')
        kwargs.setdefault('markersize',20)
        kwargs['style'] = kwargs['marker']
        kwargs['linestyle'] = None
        self.add(PointsXY.PointsXY(yy, xx=xx, **kwargs))

        # Finished:
        return None

#------------------------------------------------------------------------

def xy2pair(xy):
    """Convert the given list/tuple or complex to [x,y]"""
    if xy==None:
        return None
    elif isinstance(xy,(list,tuple)):
        return [xy[0],xy[1]]
    elif isinstance(xy,complex):
        return [xy.real,xy.imag]
    else:
        s = 'xy has invalid type: '+str(type(xy))
        raise ValueError,s
    

#------------------------------------------------------------------------
class Arrow (Graphics):
    """Class derived from Graphics. It represents an arrow
    from xy1(=[x1,y1]) to xy2(=[x2,y2]) or xy1+dxy(=[dx,dy]).
    """

    def __init__(self, xy1=[0.0,0.0], xy2=None, dxy=None,
                 **kwargs):

        Graphics.__init__(self, **kwargs)

        [x1,y1] = xy2pair(xy1)
        xx = [x1]
        yy = [y1]
        if xy2:
            [x2,y2] = xy2pair(xy2)
            xx.append(x2)
            yy.append(y2)
        elif dxy:
            [dx,dy] = xy2pair(dxy)
            xx.append(x1+dx)
            yy.append(y1+dx)
        else:
            raise ValueError,'either xy2 or dxy should be specified'

        # Calculate the polar coordinates (r,a):
        dx = (xx[1]-xx[0])
        dy = (yy[1]-yy[0])
        r = ((dx*dx)+(dy*dy))**0.5
        if dx<0.0: r = -r
        a = 0.0
        if not dx==0:
            a = pylab.arctan(dy/dx)

        # Make a horizontal line of length r, and make the arrow-head:
        yy[1] = yy[0]
        xx[1] = xx[0]+r
        ahlen = r/25.0          # arrow head length
        ahwid = r/75.0          # arrow head width
        xx.append(xx[1]-ahlen)
        yy.append(yy[1]+ahwid)
        xx.append(xx[2])
        yy.append(yy[1]-ahwid)
        xx.append(xx[1])
        yy.append(yy[1])

        # Make the PointsXY object and rotate it by angle a:
        pxy = PointsXY.PointsXY(yy, xx=xx, **kwargs)
        pxy.rotate(a, xy0=xy1)
        self.add(pxy)

        # Finished:
        return None

#------------------------------------------------------------------------

class Circle (Graphics):
    """Class derived from Graphics. It represents a circle
    with a given centre(x0,y0) and radius.
    A segment may be specified by the start and stop
    angles a1(=0) and a2(=2pi).
    """

    def __init__(self, xy0=[0.0,0.0], radius=1.0, 
                 a1=0.0, a2=None, close=False, centre=None,
                 **kwargs):

        Graphics.__init__(self, **kwargs)

        [x0,y0] = xy2pair(xy0)
        if a2==None: a2 = 2*pylab.pi           # default 2pi
        na = max(3,int((a2-a1)/0.1))           # nr of points
        xx = []
        yy = []
        aa = a1+(a2-a1)*pylab.array(range(na))/float(na-1)
        for a in aa:
            xx.append(x0+radius*pylab.cos(a))
            yy.append(y0+radius*pylab.sin(a))

        # Optionally, close the segment by drawing the end radii:
        if close:
            xx.insert(0,x0)
            yy.insert(0,y0)
            xx.append(x0)
            yy.append(y0)
            
        # Make the PointsXY object, and add it to the internal list:
        self.add(PointsXY.PointsXY(yy, xx=xx, **kwargs))

        # Optional: indicate the centre
        if centre:
            kwargs['marker'] = centre
            self.add(PointsXY.PointsXY([y0], xx=[x0], **kwargs))

        # Finished:
        return None

#------------------------------------------------------------------------

class Ellipse (Graphics):
    """Class derived from Graphics. It represents an ellipse
    with a given centre(x0,y0) and half-axes a and b, and position angle.
    """

    def __init__(self, xy0=[0.0,0.0], a=2.0, b=1.0, angle=0.0, 
                 centre='+', **kwargs):

        Graphics.__init__(self, **kwargs)

        [x0,y0] = xy2pair(xy0)
        na = 30
        xx = []
        yy = []
        gg = 2*pylab.pi*pylab.array(range(na))/float(na-1)
        for g in gg:
            xx.append(x0+a*pylab.cos(g))
            yy.append(y0+b*pylab.sin(g))

            
        # Make the PointsXY object, and add it to the internal list:
        pts = PointsXY.PointsXY(yy, xx=xx, **kwargs)
        pts.rotate(angle, xy0=xy0)
        self.add(pts)

        # Optional: indicate the centre
        if centre:
            kwargs['marker'] = centre
            self.add(PointsXY.PointsXY([y0], xx=[x0], **kwargs))

        # Finished:
        return None



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Graphics.py:\n'

    grs = Graphics()
        
    if 0:
        grs.add(PointsXY.test_line())
        grs.add(PointsXY.test_parabola())
        grs.add(PointsXY.test_sine())
        grs.add(PointsXY.test_cloud())

    if 0:
        grs = Circle([1,3],5,
                     a1=1, a2=2, close=True,
                     centre='cross',
                     linestyle='--', linewidth=3)

    if 1:
        grs = Ellipse([1,3],2,1, angle=1.0,
                      centre='cross',
                      linestyle='--', linewidth=3)

    if 0:
        grs = Scatter(range(6), marker='hexagon')

    if 0:
        # grs = Arrow(dxy=[1,1], linewidth=3)
        # grs = Arrow(xy2=[1,1], linewidth=3)
        grs = Arrow([-4,-8], dxy=[-1,-1], linewidth=3)

    #------------------------------------
        
    grs.oneliners()

    if 1:
        grs.plot(dispose='show')
        # grs.plot(dispose=['PNG','SVG','show'])

    print '\n** End of local test of: Graphics.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


