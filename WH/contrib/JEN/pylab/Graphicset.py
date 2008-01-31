#!/usr/bin/env python

# file: ../contrib/JEN/pylab/Graphicset.py

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

import Points2D

#======================================================================================

class Graphicset (Subplot.Subplot):
    """The Grapicset is derived from the Subplot class.
    It holds one or more Graphics objects."""

    def __init__(self, name=None, **kwargs):

        Subplot.Subplot.__init__(self, name=name, **kwargs)

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
        """Return the name (label?) of this Graphicset"""
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
        ss = '** <Graphicset> '+self.name()+':'
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
        return self.dispose(dispose)


#========================================================================
# Some convenient 'standard' Graphics classes:
#========================================================================

class Circle (Graphicset):
    """The Grapicset is derived from the Subplot class.
    It holds a series of Graphics objects."""

    def __init__(self, x0=0.0, y0=0.0, radius=1.0, name=None,
                 a1=0.0, a2=None, close=False, centre=None,
                 **kwargs):
        """Make a circle with a given centre(x0,y0) and radius.
        A circle segment may be specified by the start and stop
        angles a1(=0) and a2(=2pi)."""

        Graphicset.__init__(self, name=name, **kwargs)

        if a2==None: a2 = 2*pylab.pi           # default 2pi
        na = max(3,int((a2-a1)/0.1))           # nr of points
        xx = []
        yy = []
        aa = a1+(a2-a1)*pylab.array(range(na))/float(na-1)
        for a in aa:
            xx.append(x0+radius*pylab.cos(a))
            yy.append(y0+radius*pylab.sin(a))

        # Optionally, close the segment by drawing end radii:
        if close:
            xx.insert(0,x0)
            yy.insert(0,y0)
            xx.append(x0)
            yy.append(y0)
            
        # Make the Points2D object, and add it to the internal list:
        self.add(Points2D.Points2D(yy, xx=xx, **kwargs))

        # Optional: indicate the centre
        if centre:
            kwargs['marker'] = centre
            self.add(Points2D.Points2D([y0], xx=[x0], **kwargs))

        # Finished:
        return None



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Graphicset.py:\n'

    grs = Graphicset()
        
    if 0:
        grs.add(Points2D.test_line())
        grs.add(Points2D.test_parabola())
        grs.add(Points2D.test_sine())
        grs.add(Points2D.test_cloud())

    if 1:
        grs = Circle(1,3,5,
                     a1=1, a2=2, close=True,
                     centre='cross',
                     linestyle='--', linewidth=3)

    #------------------------------------
        
    grs.oneliners()

    if 1:
        grs.plot()

    print '\n** End of local test of: Graphicset.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


