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

    def __init__(self, **kwargs):
        """
        ** The Subplot class looks for the followin keywords in **kwargs:
        - name  [='<name>']:
        - title [=<type>]:
        - xunit [=None]:
        - yunit [=None]:
        - xlabel[=xx[(xunit)]]:
        - ylabel[=<name>[(yunit)]]:
        - xmin  [=None]: viewing window
        - xmax  [=None]: viewing window
        - ymin  [=None]: viewing window
        - ymax  [=None]: viewing window
        """

        # Extract the relevant keyword arguments from kwargs:
        kw = dict()
        if isinstance(kwargs, dict):
            keys = ['name','plot_mode','plot_type',
                    'title','xlabel','ylabel','xunit','yunit',
                    'xmin','xmax','ymin','ymax',
                    'plot_legend','plot_axis_labels']
            for key in keys:
                if kwargs.has_key(key):
                    kw[key] = kwargs[key]

        kw.setdefault('name',None)
        kw.setdefault('title',None)
        kw.setdefault('xlabel',None)
        kw.setdefault('ylabel',None)
        kw.setdefault('xunit',None)
        kw.setdefault('yunit',None)
        kw.setdefault('xmin',None)
        kw.setdefault('xmax',None)
        kw.setdefault('ymin',None)
        kw.setdefault('ymax',None)

        kw.setdefault('plot_mode', 'pylab')
        kw.setdefault('plot_type', 'plot')
        kw.setdefault('plot_axis_labels', True)
        kw.setdefault('plot_legend', True)

        if not isinstance(kw['name'],str): kw['name'] = '<name>'
        if not isinstance(kw['xlabel'],str): kw['xlabel'] = 'xx'
        if not isinstance(kw['ylabel'],str): kw['ylabel'] = 'yy'
        if not isinstance(kw['title'],str): kw['title'] = str(type(self))
        if isinstance(kw['xunit'],str): kw['xlabel'] += ' ('+kw['xunit']+')'
        if isinstance(kw['yunit'],str): kw['ylabel'] += ' ('+kw['yunit']+')'

        if False:
            if kw['plot_type'] in ['loglog','semilogy']:
                kw['ylabel'] = 'log('+kw['ylabel']+')'
            if kw['plot_type'] in ['loglog','semilogx']:
                kw['xlabel'] = 'log('+kw['xlabel']+')'

        self._kw = kw

        # Legend(s):
        self.legend(init=True)

        # Finished
        return None

    #---------------------------------------------------------------

    def kwupdate (self, **kwargs):
        """Update self._kw (see .__init__())."""
        if isinstance(kwargs,dict):
            for key in kwargs.keys():
                if self._kw.has_key(key):
                    was = self._kw[key]
                    self._kw[key] = kwargs[key]
                    print '** kwupdate():',key,':',was,'->',self._kw[key]
                else:
                    s = '** kwarg key not recognised: '+str(key)
                    raise ValueError,s
        return True

    #---------------------------------------------------------------

    def legend (self, new=None, init=False):
        """Legend control"""
        if init:
            self._legend = []
        if new:
            if isinstance(new, str):
                ss = new.split('\n')
                for s in ss:
                    self._legend.append(s)
            elif isinstance(new, list):
                for s in new:
                    self.legend(s)
            else:
                self._legend.append(str(new))
        return self._legend
                


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

    def display(self, txt=None):
        print '\n** (',txt,')'
        print ' * ',self.oneliner()
        for key in self._kw:
            print '   - kw['+str(key)+'] = '+str(self._kw[key])
        print ' * legend ('+str(len(self._legend))+' lines):'
        for s in self._legend:
            print '   - '+str(s)
        print '**\n'

    def help(self):
        """Return/print a help-string"""
        print Subplot.__init__.__doc__
        return True


    #===============================================================
    # Access routines (mostly placeholders, to be re-implemented):
    #===============================================================

    def name(self):
        """Return the name (label?) of this Subplot"""
        return self._kw['name']

    def len(self):
        """Return the number of internal objects"""
        return 0

    def yrange(self, margin=0.0, yrange=None):
        """Placeholder: Return [min,max] of all y-coordinate(s)."""
        return [self._kw['ymin'],self._kw['ymax']]

    def xrange(self, margin=0.0, xrange=None):
        """Placeholder: Return [min,max] of all x-coordinate(s)."""
        return [self._kw['xmin'],self._kw['xmax']]

    def title(self): return self._kw['title']
    def xlabel(self): return self._kw['xlabel']
    def ylabel(self): return self._kw['ylabel']
    def xunit(self): return self._kw['xunit']
    def yunit(self): return self._kw['yunit']

    #---------------------------------------------------------------
    
    def gca(self):
        """Return the current axes subplot...."""
        obj = pylab.gca()
        print '\n** Subplot.gca() ->',type(obj),'\n'
        # <matplotlib.axes.Subplot instance at 0xb7d0a66c>
        return obj


    #===============================================================
    # Plot standalone (testing only?)
    #===============================================================

    def plot(self, figure=1, subplot=111, margin=0.1, dispose='show'):
        """Make the subplot"""
        pylab.figure(figure)
        pylab.subplot(subplot)
        self.set_plot_window(margin=margin)
        if self._kw['plot_legend']:
            self.plot_legend()              
        if self._kw['plot_axis_labels']:
            self.plot_axis_labels()
        import Figure
        return Figure.pylab_dispose(dispose)


    #------------------------------------------------

    def plot_axis_labels(self):
        """Helper function to make axes labels, using internal info"""
        if isinstance(self._kw['xlabel'],str):
            pylab.xlabel(self._kw['xlabel'])
        if isinstance(self._kw['ylabel'],str):
            pylab.ylabel(self._kw['ylabel'])
        if isinstance(self._kw['title'],str):
            pylab.title(self._kw['title'])
        return True

    #------------------------------------------------

    def set_plot_window(self, margin=0.1, trace=False):
        """Helper function to set the plot_window, using internal info"""
        [xmin,xmax] = self._range(self.xrange(), margin=margin,
                                  vmin=self._kw['xmin'],
                                  vmax=self._kw['xmax'])
        [ymin,ymax] = self._range(self.yrange(), margin=margin,
                                  vmin=self._kw['ymin'],
                                  vmax=self._kw['ymax'])
        pylab.axis([xmin, xmax, ymin, ymax])
        if trace:
            print '** set_plot_window(): xrange =',[xmin,xmax],'  yrange =',[ymin,ymax]
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

    #---------------------------------------------------------------

    def plot_legend (self, ny=16, trace=False):
        """Plot the accumulated legend-strings (if any).
        The number ny(=16) determines the line-spacing,
        by specifying the number of lines that fit on the plot.
        """
        if trace: print '\n** plot_legend():'
        ss = self.legend()
        [xmin,xmax] = self.xrange()
        [ymin,ymax] = self.yrange()
        if trace: print '- xx =',xmin,xmax
        if trace: print '- yy =',ymin,ymax
        x = xmin + abs(xmax-xmin)/20.0
        dy = abs(ymax-ymin)/float(ny)
        y = ymax
        for i,s in enumerate(ss):
            y -= dy
            if trace:
                print '-',i,'(',x,y,dy,'):',s
            pylab.text(x,y,s)
        if trace: print
        return True








#========================================================================
#========================================================================
#========================================================================
#========================================================================
# Derived classes:
#========================================================================

class Legend (Subplot):

    def __init__(self, **kwargs):
        """
        The Legend class is derived from the Subplot class.
        It provides an empty panel for text descriptions,
        e.g. about the other Subplots in a figure.
        """

        Subplot.__init__(self, **kwargs)

        self._kw['xmin'] = -1
        self._kw['xmax'] = 1
        self._kw['ymin'] = -1
        self._kw['ymax'] = 1

        self._kw['plot_legend'] = True

        self._kw['plot_axis_labels'] = True
        self._kw['title'] = 'Legend'
        self._kw['xlabel'] = ' '
        self._kw['ylabel'] = ' '

        # Finished:
        return None




#========================================================================
# Some test objects:
#========================================================================

def test_line (n=6, **kwargs):
    """Graphics (=Subplot) with PointsXY object for a straight line"""
    import PointsXY
    import Graphics
    grs =  Graphics.Graphics(**kwargs)
    grs.add(PointsXY.test_line(n=n, **kwargs))
    return grs

def test_parabola (n=6, **kwargs):
    """Graphics (=Subplot) with PointsXY object for a parabola"""
    import PointsXY
    import Graphics
    grs =  Graphics.Graphics(**kwargs)
    grs.add(PointsXY.test_parabola(n=n, **kwargs))
    return grs

def test_sine (n=10, **kwargs):
    """Graphics (=Subplot) with PointsXY object for sine-wave"""
    import PointsXY
    import Graphics
    grs =  Graphics.Graphics(**kwargs)
    grs.add(PointsXY.test_sine(n=n, **kwargs))
    return grs

def test_cloud (n=10, mean=-1.0, stddev=3.0, **kwargs):
    """Graphics (=Subplot) with PointsXY object for a cloud of random points"""
    import PointsXY
    import Graphics
    grs =  Graphics.Graphics(**kwargs)
    grs.add(PointsXY.test_cloud(n=n, mean=mean, stddev=stddev, **kwargs))
    return grs



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Subplot.py:\n'

    sub = Subplot(xmin=-1,xmax=1,ymin=-1,ymax=1)

    if 1:
        sub = Legend()

    print sub.oneliner()
    sub.display('init')

    if 0:
        sub.help()

    if 1:
        sub.legend('line 1')
        sub.legend('line 2')
        sub.legend('line 3')
        sub.display('legend')

    if 1:
        sub.plot()

    print '\n** End of local test of: Subplot.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


