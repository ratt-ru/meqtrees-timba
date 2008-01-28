#!/usr/bin/env python

# file: ../contrib/JEN/pylab/Graphics.py

# Author: J.E.Noordam
# 
# Short description:
#   Class that represents a pylab sholds a series
#   of plottable objects like Points2D etc
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


#======================================================================================

class Graphics (Subplot.Subplot):
    """Encapsulation of a pylab subplot
    """

    def __init__(self, name=None,
                 title=None, xlabel=None, ylabel=None, xunit=None, yunit=None,
                 xmin=None, xmax=None, ymin=None, ymax=None,
                 **kwargs):

        Subplot.Subplot.__init__(self, name=name, title=title,
                                 xlabel=xlabel, ylabel=ylabel,
                                 xunit=xunit, yunit=yunit,
                                 xmin=xmin, xmax=xmax,
                                 ymin=ymin, ymax=ymax)

        #------------------------------------------------------------------

        # The Points2d objects are kept in the named fields of a dict:
        self._order = []
        self._graphic = dict()


        #------------------------------------------------------------------

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

    def plot(self, figure=1, margin=0.2, show=True):
        """Plot the group of points, using pylab"""
        pylab.figure(figure)
        for key in self._order:
            self._graphic[key].plot(figure=figure, margin=0.0, show=False)
        [xmin,xmax] = self._range(self.xrange(), margin=margin,
                                  vmin=self._xmin, vmax=self._xmax)
        [ymin,ymax] = self._range(self.yrange(), margin=margin,
                                  vmin=self._ymin, vmax=self._ymax)
        print '** .plot(): xrange =',[xmin,xmax],'    yrange =',[ymin,ymax]
        pylab.axis([xmin, xmax, ymin, ymax])
        if isinstance(self._xlabel,str): pylab.xlabel(self._xlabel)
        if isinstance(self._ylabel,str): pylab.ylabel(self._ylabel)
        if isinstance(self._title,str): pylab.title(self._title)
        if show: pylab.show()
        return True

    #------------------------------------------------

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



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Graphics.py:\n'

    import Points2D

    grs = Graphics()
    grs.add(Points2D.test_line())
    grs.add(Points2D.test_parabola())
    grs.add(Points2D.test_sine())
    grs.add(Points2D.test_cloud())
    grs.oneliners()

    if 1:
        grs.plot()

    print '\n** End of local test of: Graphics.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


