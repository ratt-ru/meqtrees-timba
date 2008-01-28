#!/usr/bin/env python

# file: ../contrib/JEN/pylab/Figure.py

# Author: J.E.Noordam
# 
# Short description:
#   Class that makes a pylab Figure, consisting of one or more Subplots,
#   which each have a number of plottable units...
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
# from pylab import *



#======================================================================================

class Figure (object):
    """Encapsulation of a set of 2D points, for (pylab) plotting
    """

    def __init__(self, name=None):

        #------------------------------------------------------------------

        # Deal with the specified name (label):
        self._name = name
        if not isinstance(self._name,str): self._name = 'Figure'

        # Some placeholders (to be used for standalone plotting, or for
        # automatic generation of labels etc when plotted in a subplot)
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._xunit = xunit
        self._yunit = yunit

        if not isinstance(self._title,str): self._title = self._name
        if not isinstance(self._xlabel,str): self._xlabel = 'xx'
        if not isinstance(self._ylabel,str): self._ylabel = self._name
        if isinstance(self._xunit,str): self._xlabel += ' ('+self._xunit+')'
        if isinstance(self._yunit,str): self._ylabel += ' ('+self._yunit+')'


        #------------------------------------------------------------------

        # Finished:
        return None


    #===============================================================
    # Access routines:
    #===============================================================

    def name(self):
        """Return the name (label?) of this set of points"""
        return self._name

    def __getitem__(self,index):
        """Get value yy[index]"""
        yy = self._yy.tolist()
        return yy[index]
        # return self.__yy[index]

    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <Figure> '+self.name()+':'
        ss += ' n='+str(self.len())
        ss += ' '+self.plot_style_summary()
        ss += '  yrange='+str(self.yrange())
        ss += '  xrange='+str(self.xrange())
        return ss


    #===============================================================
    # Plot standalone (testing only?)
    #===============================================================

    def plot(self, figure=1, margin=0.2):
        """Plot the group of points, using pylab"""
        pylab.figure(figure)
        pylab.plot(self.xx(), self.yy(), **self._ps)
        if margin>0.0:
            [xmin,xmax] = self.xrange(margin=margin)
            [ymin,ymax] = self.yrange(margin=margin)
            print [xmin,xmax]
            print [ymin,ymax]
            pylab.axis([xmin, xmax, ymin, ymax])
        if isinstance(self._xlabel,str): pylab.xlabel(self._xlabel)
        if isinstance(self._ylabel,str): pylab.ylabel(self._ylabel)
        if isinstance(self._title,str): pylab.title(self._title)
        pylab.show()
        return True




#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Figure.py:\n'

    ps = dict()
    ps = dict(color='magenta', style='o', markersize=5, markeredgecolor='blue')

    pts = Figure(range(6), 'list', annot=4, **ps)
    # pts = Figure(pylab.array(range(6)), 'numarray', **ps)
    # pts = Figure(-2, 'scalar', **ps)
    # pts = Figure(3+5j, 'complex scalar', **ps)
    # pts = Figure([3,-2+1.5j], 'complex list', **ps)
    # pts = Figure([0,0,0,0], 'zeroes', **ps)
    print pts.oneliner()

    if 1:
        pts.plot()

    if 0:
        print '- pts[1] -> ',pts[1]
        print '- .yy() -> ',pts.yy(),type(pts.yy())
        print '- .yy(tolist=True) -> ',pts.yy(tolist=True),type(pts.yy(tolist=True))
        print '- .yrange(margin=0.1) -> ',pts.yrange(margin=0.1)
        print '- .xrange(margin=0.1, xrange=[-2,3]) -> ',pts.xrange(margin=0.1, xrange=[-2,3])
        print '- .mean(xalso=True) -> ',pts.mean(xalso=True)
        print '- .stddev(xalso=True) -> ',pts.stddev(xalso=True)
        print '- .sum(xalso=True) -> ',pts.sum(xalso=True)

    if 0:
        print '- .shift(dy=-10, dx=100) -> ',pts.shift(dy=-10, dx=100), pts.oneliner()
        print '- .rotate(angle=0.2) -> ',pts.rotate(angle=0.2), pts.oneliner()
        print '- .rotate(angle=0.2, xy0=[-10,100]) -> ',pts.rotate(angle=0.2, xy0=[-10,100]), pts.oneliner()
        # pts.plot()

    print '\n** End of local test of: Figure.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


