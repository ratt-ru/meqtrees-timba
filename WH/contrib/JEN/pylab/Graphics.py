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

    def __init__(self, **kwargs):
        """
        ** The Grapics class is derived from the Subplot class.
        It holds one or more Graphics objects.
        All Graphics clsses share some common features:
        - Input points xy may be specified in different ways:
          -- a list [x,y] 
          -- a tuple (x,y)         -> [x,y]
          -- complex (x+yj)        -> [x,y]
          -- a scalar (x)          -> [x,x]
          -- a list [x1,x2,x3,...] -> [x1,x2]
          -- a list [x]            -> [x,x]
          -- any other             -> None (error)
        - If centre_mark=<mark>, the centre/mean is indicated.
        """

        Subplot.Subplot.__init__(self, **kwargs)

        # Extract the keywords available to all Graphics classes,
        # and add them to the Subplot keyword dict self._kw:

        if isinstance(kwargs, dict):
            keys = ['centre_mark','auto_legend',
                    'plot_axes','plot_grid']
            for key in keys:
                if kwargs.has_key(key):
                    self._kw[key] = kwargs[key]

        self._kw.setdefault('plot_grid', True)
        self._kw.setdefault('plot_axes', True)
        self._kw.setdefault('auto_legend', False)
        self._kw.setdefault('centre_mark', None)

        if self._kw['centre_mark']==True: self._kw['centre_mark'] = '+'

        # The Graphics objects are kept in the named fields of a dict:
        self._order = []
        self._graphic = dict()

        # Finished:
        return None

    #-------------------------------------------------------------

    def add(self, graphic, key=None):
        """Add a named (key) plottable object to self._graphic"""
        if not isinstance(key, str):
            key = str(len(self._order))       # .....??
        self._graphic[key] = graphic
        self._order.append(key)

        # Transfer some keyword arguments to the new graphic:
        # (All graphics objects in the same subplot should be
        #  plotted in the same way, e.g. plot (linear), loglog etc)
        kwargs = dict()
        for key1 in ['plot_type','plot_mode']:
            print '-- key1 =',key1,
            if self._kw.has_key(key1):
                kwargs[key1] = self._kw[key1]
            print '-> kwargs =',kwargs
        self.last().kwupdate(**kwargs)

        # Finished:
        return key

    #............................................................

    def last (self):
        """Return (a reference to) the last graphic in the list"""
        if self.len()>0:
            key = self._order[self.len()-1]
            return self._graphic[key]
        return None

    #............................................................

    def remove(self, key):
        """Remove a named object from self._graphic"""
        if self.has_key(key):
            self._grahic.__delitem__(key)
            self._order.__delitem__(key)
        return True

    #-------------------------------------------------------------
    # Access routines:
    #-------------------------------------------------------------

    def len(self):
        """Return the number of its plottable objects"""
        return len(self._order)

    def order(self):
        """Return a list of keys of its plottable objects"""
        return self._order

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
        if not yr:
            # yr = [self._kw['ymin'],self._kw['ymax']]
            yr = [-1.0,1.0]
        return yr

    def xrange(self, margin=0.0, xrange=None):
        """Return [min,max] of all the x-coordinate(s)."""
        xr = None
        for key in self._order:
            xr = self._graphic[key].xrange(margin=margin, xrange=xr)
        if not xr:
            # xr = [self._kw['xmin'],self._kw['xmax']]
            xr = [-1.0,1.0]
        return xr


    #-------------------------------------------------------------
    # Display of the contents of this object:
    #-------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <Graphics> '+self.name()+':'
        ss += ' n='+str(self.len())
        ss += '  yrange='+str(self.yrange())
        ss += '  xrange='+str(self.xrange())
        return ss

    def display(self, txt=None):
        print '\n** (',txt,')'
        print ' * ',self.oneliner()
        for key in self._order:
            print '-',key,':',self._graphic[key].oneliner()
        print ' * keyword arguments (kwargs):'
        for key in self._kw:
            print '   - kw['+str(key)+'] = '+str(self._kw[key])
        print '**\n'
        return True

    def help(self):
        """Help"""
        Subplot.Subplot.help(self)
        print Graphics.__init__.__doc__
        print self.__init__.__doc__
        return True


    #-------------------------------------------------------------
    # Plot standalone (testing only?)
    #-------------------------------------------------------------

    def plot(self, figure=1, subplot=111, margin=0.1, dispose='show', trace=True):
        """Plot the group of points, using pylab"""
        if trace:
            print '\n** Graphics.plot(',figure,subplot,margin,dispose,')'
        fig = pylab.figure(figure)
        if trace: print '  -',fig
        sub= pylab.subplot(subplot)
        if trace: print '  -',sub
        if self._kw['plot_axes']:
            self.plot_axes(xaxis=True, yaxis=True)
        for key in self._order:
            self._graphic[key].plot(margin=0.0, dispose=None)
        self.set_plot_window(margin=margin, trace=False)
        if self._kw['plot_axis_labels']:
            self.plot_axis_labels()
        if self._kw['plot_legend']:
            self.plot_legend()
        if self._kw['auto_legend']:
            pylab.legend()             # NB: This causes problems with Qwt read svg...!!
        if self._kw['plot_grid']:
            if self._kw['plot_type']=='polar':
                pass
                # pylab.thetagrids(True)                 # see also .rgrids()
            else:
                pylab.grid(True)
        import Figure
        return Figure.pylab_dispose(dispose, origin='Graphics.plot()',
                                    rootname=self.name(), trace=trace)

    #------------------------------------------------

    def plot_centre_mark(self, xy0=[0,0], **kwargs):
        """Optional: Indicate the centre of the graph"""
        if self._kw['centre_mark']:
            kwargs['marker'] = self._kw['centre_mark']
            kwargs['markersize'] = 20
            [x0,y0] = PointsXY.xy2pair(xy0)
            self.add(PointsXY.PointsXY([y0], xx=[x0], **kwargs))
        return True

    #------------------------------------------------

    def plot_axes(self, xaxis=None, yaxis=None, color='black', linewidth=1):
        """Helper function for plotting x and y axis"""
        [xmin,xmax] = self.xrange()
        [ymin,ymax] = self.yrange()
        if xaxis and ((ymin*ymax)<=0.0):
            pylab.plot([xmin,xmax], [0.0,0.0],
                       label='_nolegend_',
                       color=color, linewidth=linewidth)
        if yaxis and ((xmin*xmax)<=0.0):
            pylab.plot([0.0,0.0], [ymin,ymax],
                       label='_nolegend_',
                       color=color, linewidth=linewidth)
        return True




#========================================================================
# Some convenient 'standard' Graphics classes:
#========================================================================

class Scatter (Graphics):

    def __init__(self, yy=range(3), annot=None,
                 xx=None, dxx=None, dyy=None,
                 **kwargs):
        """
        The Scatter class is derived from the Graphics class.
        It represents a scatter-plot (markers) of the specified
        lists of yy [and xx] coordinates.
        - If xx is not specified, xx=0,1,2,...,nyy-1 is used.
        - If yy is complex, xx=real(yy) and yy=imag(yy).
        - A single point may be specified as scalar(s).
        - Any dyy and/or dxx are converted to error bars.
        - Annotations are supplied via annot and annotpos.
        """
        Graphics.__init__(self, **kwargs)

        # Make the PointsXY object, and add it to the internal list:
        kwargs.setdefault('style','o')
        kwargs.setdefault('markersize',5)
        # kwargs['linestyle'] = None
        self.add(PointsXY.PointsXY(yy=yy, annot=annot,
                                   xx=xx, dxx=dxx, dyy=dyy,
                                   **kwargs))

        # Finished:
        return None


#========================================================================

class Rectangle (Graphics):

    def __init__(self, xy0=[0,0], sxy=[1,1],
                 blc=None, trc=None,
                 **kwargs):
        """
        The Rectangle class is derived from the Graphics class.
        It can be specified in different ways:
        - by centre xy0(=[0,0]) and size sxy(=[1,1])
        - by corners blc(=None) and trc(=None)
        If blc and trc are specified, they take precedence.
        """

        Graphics.__init__(self, **kwargs)

        if blc and trc:
            [x1,y1] = PointsXY.xy2pair(blc)
            [x2,y2] = PointsXY.xy2pair(trc)
        else:
            [x0,y0] = PointsXY.xy2pair(xy0)
            [dx,dy] = PointsXY.xy2pair(sxy)
            [x1,y1] = [x0-dx/2.0,y0-dy/2.0]
            [x2,y2] = [x0+dx/2.0,y0+dy/2.0]

        xx = [x1,x2,x2,x1,x1]
        yy = [y1,y1,y2,y2,y1]
        kwargs.setdefault('linewidth',2)

        # Make the PointsXY object, and add it to the internal list:
        self.add(PointsXY.PointsXY(yy, xx=xx, **kwargs))

        # Finished:
        return None


#========================================================================

class Arrow (Graphics):

    def __init__(self, xy0=[0.0,0.0], xy1=None, dxy=[-1.0,-1.0],
                 **kwargs):
        """
        The Arrow class is derived from the Graphics class.
        It can be specified in different ways:
        - from xy0(=[0,0]) to xy1(=None)
        - from xy0(=[0,0]) to xy0+dxy(=None).
        """

        Graphics.__init__(self, **kwargs)

        [x0,y0] = PointsXY.xy2pair(xy0)
        if xy1:
            [x1,y1] = PointsXY.xy2pair(xy1)
            [dx,dy] = [x1-x0,y1-y0]
        elif dxy:
            [dx,dy] = PointsXY.xy2pair(dxy)
        else:
            raise ValueError,'either xy1 or dxy should be specified'


        # Make the PointsXY object:
        pxy = PointsXY.PointsXY(y0, xx=x0, dxx=dx, dyy=dy, **kwargs)
        self.add(pxy)
        self.last().kwupdate(**dict(plot_type='quiver'))

        # Finished:
        return None


#========================================================================

class Arrow_old (Graphics):

    def __init__(self, xy1=[0.0,0.0], xy2=None, dxy=None,
                 **kwargs):
        """
        The Arrow class is derived from the Graphics class.
        It can be specified in different ways:
        - from xy1(=[0,0]) to xy2(=None)
        - from xy1(=[0,0]) to xy1+dxy(=None).
        """

        Graphics.__init__(self, **kwargs)

        [x1,y1] = PointsXY.xy2pair(xy1)
        xx = [x1]
        yy = [y1]
        if xy2:
            [x2,y2] = PointsXY.xy2pair(xy2)
            xx.append(x2)
            yy.append(y2)
        elif dxy:
            [dx,dy] = PointsXY.xy2pair(dxy)
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


#========================================================================

class Circle (Graphics):

    def __init__(self, xy0=[0.0,0.0], radius=1.0, 
                 a1=0.0, a2=None, na=None,
                 angle=0.0, close=False,
                 **kwargs):
        """
        The Circle class is derived from the Graphics class.
        It defines a circle with centre xy0(=[0,0]) and radius (=1.0).
        - xy0 may be a list [x,y], a tuple (x,y) or complex (x+yj). 
        - A segment may be specified by the start and stop angles
        a1(=0) and a2(=2pi).
        - The entire graph may be rotated by angle(=0) rad.
        - If close==True, the end radii are drawn (useful for segment).
        """

        Graphics.__init__(self, **kwargs)

        [x0,y0] = PointsXY.xy2pair(xy0)
        if a2==None: a2 = 2*pylab.pi           # default 2pi
        if not isinstance(na,int):
            na = max(3,int((a2-a1)/0.1))       # nr of points
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
        pts = PointsXY.PointsXY(yy, xx=xx, **kwargs)
        pts.rotate(angle, xy0=xy0)
        self.add(pts)

        # Optional: indicate the centre
        self.plot_centre_mark(xy0, **kwargs)

        # Finished:
        return None


#========================================================================

class RegularPolygon (Circle):

    def __init__(self, n=5, xy0=[0.0,0.0], radius=1.0, 
                 angle=0.0, **kwargs):
        """
        The RegularPolygon class is derived from the Graphics class.
        It is specified by n(=5), centre xy0(=[0,0]) and radius(=1.0).
        - It may be rotated by an angle(=0) rad.
        """

        Circle.__init__(self, xy0=xy0, radius=radius,
                        na=n+1, angle=angle+pylab.pi/2.0,
                        **kwargs)

        # Finished:
        return None


#========================================================================

class Ellipse (Graphics):

    def __init__(self, xy0=[0.0,0.0], a=2.0, b=1.0, angle=0.0, 
                 **kwargs):
        """
        The Ellipse class derived from the Graphics class.
        It is specified by a centre xy0(=[0,0]),
        half-axes a(=2) and b(=1), and (position) angle(=0).
        """

        Graphics.__init__(self, **kwargs)

        [x0,y0] = PointsXY.xy2pair(xy0)
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
        self.plot_centre_mark(xy0, **kwargs)

        # Finished:
        return None



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Graphics.py:\n'

    grs = Graphics()

        
    if 0:
        grs = Circle([1,3],5,
                     a1=1, a2=2, close=True,
                     centre_mark='cross',
                     linestyle='--', linewidth=3)

    if 0:
        grs = Ellipse([1,3],2,1, angle=1.0,
                      centre_mark='cross',
                      linestyle='--', linewidth=3)

    if 1:
        grs = Scatter(None, style='hexagon')
        # grs = Scatter(range(6), style='hexagon')
        # grs = Scatter(range(6), style='hexagon', plot_type='polar')

    if 0:
        grs = Rectangle()
        # grs = Rectangle(xy0=complex(2.5,3), sxy=complex(4,5))

    if 0:
        grs = RegularPolygon(n=5, xy0=complex(2.5,3), radius=3,
                             centre_mark='+')

    if 0:
        # grs = Arrow(dxy=[1,1], linewidth=3)
        # grs = Arrow(xy2=[1,1], linewidth=3)
        grs = Arrow([-4,-8], dxy=[-1,-1], linewidth=3)

    if 0:
        grs.add(PointsXY.test_line())
        grs.add(PointsXY.test_parabola())
        grs.add(PointsXY.test_sine())
        grs.add(PointsXY.test_cloud())

    if 0:
        import Figure
        fig = Figure.Figure(nrow=2,ncol=3)
        fig.add(Scatter())
        fig.add(Rectangle())
        fig.add(RegularPolygon())
        fig.add(Circle())
        fig.add(Ellipse())
        fig.add(Arrow())
        fig.plot(dispose='show')

    #------------------------------------

    if 0:
        grs.help()

    grs.display()

    if 1:
        grs.plot(dispose='show')
        # grs.plot(dispose=['PNG','SVG','show'])

    #------------------------------------

    if 0:
        print pylab.quiver.func_doc
        if 1:
            X = pylab.array([[1,2],[3,4]])
            Y = pylab.array([[1,-2],[3,4]])
            U = -pylab.array([[1,2],[3,4]])
            V = 2*pylab.array([[1,2],[3,4]])
        if 1:
            X = pylab.array([[3],[3]])
            Y = pylab.array([[10],[10]])
            U = -pylab.array([[1],[0]])
            V = 2*pylab.array([[1],[0]])
        S = 0.0
        S = 1.0
        [dx,dy] = [1,1]
        [xmin,xmax] = [X.min()-dx,X.max()+dx]
        [ymin,ymax] = [Y.min()-dy,Y.max()+dy]
        print '-- X =',X,[xmin,xmax]
        print '-- Y =',Y,[ymin,ymax]
        print '-- U =',U
        print '-- V =',V
        print '-- S =',S
        # pylab.quiver(U,V)
        # pylab.quiver(U,V,S)
        pylab.quiver(X,Y,U,V, width=1.0, color='red')
        # pylab.quiver(X,Y,U,V,S)
        pylab.plot(X,Y, marker='o', linestyle=None)
        pylab.axis([xmin,xmax,ymin,ymax])
        pylab.grid()
        pylab.show()

    print '\n** End of local test of: Graphics.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


