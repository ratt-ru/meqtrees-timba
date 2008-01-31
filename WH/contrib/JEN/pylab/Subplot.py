#!/usr/bin/env python

# file: ../contrib/JEN/pylab/Subplot.py

# Author: J.E.Noordam
# 
# Short description:
#   Base-class for pylab subplots (e.g. Graphics) that can be plotted
#   either standalone or as part of a pylab Figure
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


#======================================================================================

class Subplot (object):
    """Encapsulation of a pylab subplot
    """

    def __init__(self, name=None, **kwargs):

        # Deal with the specified name (label):
        self._name = name
        if not isinstance(self._name,str): self._name = '<name>'

        # Deal with the keyword arguments (kwargs)
        self._kw = dict()
        if isinstance(kwargs, dict):
            keys = ['title','xlabel','ylabel','xunit','yunit',
                    'xmin','xmax','ymin','ymax']
            for key in keys:
                if kwargs.has_key(key):
                    self._kw[key] = kwargs[key]

        self._kw.setdefault('title',None)
        self._kw.setdefault('xlabel',None)
        self._kw.setdefault('ylabel',None)
        self._kw.setdefault('xunit',None)
        self._kw.setdefault('yunit',None)
        self._kw.setdefault('xmin',None)
        self._kw.setdefault('xmax',None)
        self._kw.setdefault('ymin',None)
        self._kw.setdefault('ymax',None)

        self._title = self._kw['title']
        self._xlabel = self._kw['xlabel']
        self._ylabel = self._kw['ylabel']
        self._xunit = self._kw['xunit']
        self._yunit = self._kw['yunit']
        self._xmin = self._kw['xmin']
        self._xmax = self._kw['xmax']
        self._ymin = self._kw['ymin']
        self._ymax = self._kw['ymax']

        if not isinstance(self._title,str): self._title = self._name
        if not isinstance(self._xlabel,str): self._xlabel = 'xx'
        if not isinstance(self._ylabel,str): self._ylabel = self._name
        if isinstance(self._xunit,str): self._xlabel += ' ('+self._xunit+')'
        if isinstance(self._yunit,str): self._ylabel += ' ('+self._yunit+')'

        # Finished:
        return None


    #===============================================================
    # Access routines (mostly placeholders, to be re-implemented):
    #===============================================================

    def name(self):
        """Return the name (label?) of this Subplot"""
        return self._name

    def len(self):
        """Placeholder for the number of internal objects"""
        return 0

    def yrange(self, margin=0.0, yrange=None):
        """Placeholder: Return [min,max] of the y-coordinate(s)."""
        return None

    def xrange(self, margin=0.0, xrange=None):
        """Placeholder: Return [min,max] of the x-coordinate(s)."""
        return None

    def title(self): return self._title
    def xlabel(self): return self._xlabel
    def ylabel(self): return self._ylabel
    def xunit(self): return self._xunit
    def yunit(self): return self._yunit


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <Subplot> '+self.name()+':'
        ss += ' n='+str(self.len())
        ss += '  yrange='+str(self.yrange())
        ss += '  xrange='+str(self.xrange())
        return ss


    #===============================================================
    # Plot standalone (testing only?)
    #===============================================================

    def plot(self, figure=1, subplot=111, margin=0.1, dispose='show'):
        """Plot the group of points, using pylab"""
        pylab.figure(figure)
        pylab.subplot(subplot)
        self.plot_axes(xaxis=True, yaxis=True)
        self.pylab_window(margin=margin)
        self.pylab_labels()
        return self.dispose(dispose)

    #------------------------------------------------

    def dispose(self, dispose='show'):
        """Generic routine to dispose of the pylab figure"""
        if dispose=='show':
            # pylab.show._needmain = False
            pylab.show()
            # pylab.ion()
            # pylab.draw()
            # pylab.close()
        return True


    #------------------------------------------------

    def pylab_labels(self):
        """Helper function to make labels, using internal info"""
        if isinstance(self._xlabel,str):
            pylab.xlabel(self._xlabel)
        if isinstance(self._ylabel,str):
            pylab.ylabel(self._ylabel)
        if isinstance(self._title,str):
            pylab.title(self._title)
        return True

    #------------------------------------------------

    def pylab_window(self, margin=0.1):
        """Helper function to set the plot_window, using internal info"""
        [xmin,xmax] = self._range(self.xrange(), margin=margin,
                                  vmin=self._xmin, vmax=self._xmax)
        [ymin,ymax] = self._range(self.yrange(), margin=margin,
                                  vmin=self._ymin, vmax=self._ymax)
        # print '** .pylab_window(): xrange =',[xmin,xmax],'    yrange =',[ymin,ymax]
        pylab.axis([xmin, xmax, ymin, ymax])
        return True

    def _range(self, vv, margin=0.0, vmin=None, vmax=None):
        """Helper function to calculate [min,max] of the coordinate(s).
        An extra margin (fraction of the span) may be specified."""
        if margin>0.0:
            dv2 = 0.5*(vv[1]-vv[0])*margin
            if vv[1]==vv[0]:
                dv2 = 0.0004
                if not vv[1]==0.0:
                    dv2 *= vv[1]
            vv[0] -= dv2
            vv[1] += dv2
        if not vmin==None: vv[0] = vmin
        if not vmax==None: vv[1] = vmax
        return vv

    #------------------------------------------------

    def plot_axes(self, xaxis=None, yaxis=None, color='black', linewidth=1):
        """Helper function for plotting x and y axis"""
        [xmin,xmax] = self.xrange()
        [ymin,ymax] = self.yrange()
        if xaxis and ((ymin*ymax)<=0.0):
            pylab.plot([xmin,xmax], [0.0,0.0], color=color, linewidth=linewidth)
        if yaxis and ((xmin*xmax)<=0.0):
            pylab.plot([0.0,0.0], [ymin,ymax], color=color, linewidth=linewidth)
        return True




#========================================================================
# Some test objects:
#========================================================================

def test_line (n=6, **kwargs):
    """Graphics (=Subplot) with Points2D object for a straight line"""
    import Points2D
    import Graphics
    sub =  Graphics.Graphics(**kwargs)
    sub.add(Points2D.test_line(n=n, **kwargs))
    return sub

def test_parabola (n=6, **kwargs):
    """Graphics (=Subplot) with Points2D object for a parabola"""
    import Points2D
    import Graphics
    sub =  Graphics.Graphics(**kwargs)
    sub.add(Points2D.test_parabola(n=n, **kwargs))
    return sub

def test_sine (n=10, **kwargs):
    """Graphics (=Subplot) with Points2D object for sine-wave"""
    import Points2D
    import Graphics
    sub =  Graphics.Graphics(**kwargs)
    sub.add(Points2D.test_sine(n=n, **kwargs))
    return sub

def test_cloud (n=10, mean=-1.0, stddev=3.0, **kwargs):
    """Graphics (=Subplot) with Points2D object for a cloud of random points"""
    import Points2D
    import Graphics
    sub =  Graphics.Graphics(**kwargs)
    sub.add(Points2D.test_cloud(n=n, mean=mean, stddev=stddev, **kwargs))
    return sub



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Subplot.py:\n'

    sub = Subplot()
    # import Graphics
    # sub = Graphics.test()
    print sub.oneliner()

    if 0:
        sub.plot()

    print '\n** End of local test of: Subplot.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


