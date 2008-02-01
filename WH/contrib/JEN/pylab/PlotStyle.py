#!/usr/bin/env python

# file: ../contrib/JEN/pylab/PlotStyle.py

# Author: J.E.Noordam
# 
# Short description:
#   A PlotStyle object contains a style-record, which can be passed
#   to a pylab.plot() command: pylab.plot(x,y,...,**kwargs)
#   Base class, and PlotStylePylab derived class 
#
# History:
#    - 20 jan 2008: creation (extracted from Points2D.py)
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
import random



#======================================================================================

class PlotStyle (object):
    """Encapsulation of a set of 2D points, for (pylab) plotting
    """

    def __init__(self, **kwargs):

        # The PlotStyle specifications are via the kwargs
        self.check_PlotStyle(**kwargs)

        # Finished:
        return None

    #---------------------------------------------------------

    def check_PlotStyle(self, **kwargs):
        """Check (and adjust) the self._ps (PlotStyle) record"""
        
        self._ps = dict()
        if isinstance(kwargs, dict):
            keys = ['color','style',
                    'linewidth','linestyle',
                    'marker','markerfacecolor','markeredgecolor',
                    'markersize','markeredgewidth',
                    'alpha']
            for key in keys:
                if kwargs.has_key(key):
                    self._ps[key] = kwargs[key]

        self.display('from kwargs')

        # Generic (specifies line or marker):
        self._ps.setdefault('color', 'red')
        self._ps.setdefault('style', '-')               # must be removed again....

        # Line style:
        self._ps.setdefault('linestyle', None)
        self._ps.setdefault('linewidth', 1)             # in points, non-zero float 

        # Marker style:
        self._ps.setdefault('marker', None)
        self._ps.setdefault('markerfacecolor', self._ps['color'])
        self._ps.setdefault('markeredgecolor', self._ps['color'])
        self._ps.setdefault('markersize', 5)            # in points, non-zero float 
        self._ps.setdefault('markeredgewidth', 1)       # in points, non-zero float 

        # Miscellaneous:
        self._ps.setdefault('alpha', 0.5)               # transparency (0.0<=alpha<=1.0)
        # self._ps.setdefault('data_clipping', True)    # not recognised...?

        # Finsihed:
        self.display('before checks')
        self._check_colors()
        self._check_styles()
        self.display('checked')
        return True


    def display(self, txt=None):
        """Display the contents of this obkect"""
        print '\n** PlotStyle (',txt,'):'
        for key in self._ps.keys():
            print '-- self._ps[',key,'] =',self._ps[key]
        print ' '
        return True



    #===============================================================
    # Access routines:
    #===============================================================

    def kwargs(self, func='plot'):
        """Return the keyword arguments to be used for a particular pylab function"""
        if func=='plot':
            return self._ps
        return None

    def color(self):
        return self._ps['color']


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <PlotStyle>: '
        ss += self.summary() 
        return ss

    #------------------------------------------------------------
    
    def summary(self):
        """Return a short string summarizing the plot-style"""
        ss = ' ('+str(self._ps['color'])
        if self._ps['marker']:
            ss += ' '+str(self._ps['marker'])
        if self._ps['linestyle']:
            ss += ' '+str(self._ps['linestyle'])
        ss += ')'
        return ss
        



    #===============================================================
    # Routines dealing with style:
    #===============================================================

    def _check_styles(self):
        """Check the specified plot-styles"""
        if self._ps['style'] in self.line_styles():
            if not self._ps['linestyle']:
                self._ps['linestyle'] = self._ps['style']
        elif self._ps['style'] in self.marker_styles():
            if not self._ps['marker']:
                self._ps['marker'] = self._ps['style']
                self._ps['linestyle'] = None
        self._ps.__delitem__('style')                    # <-------- !!

        ls = self._ps['linestyle']
        if ls=='solid': self._ps['linestyle'] = '-'
        if ls=='dashed': self._ps['linestyle'] = '--'
        if ls=='dotted': self._ps['linestyle'] = ':'
        if ls=='dashdot': self._ps['linestyle'] = '-.'

        ms = self._ps['marker']
        if ms=='circle': self._ps['marker'] = 'o'
        if ms=='triangle': self._ps['marker'] = '^'
        if ms=='square': self._ps['marker'] = 's'
        if ms=='plus': self._ps['marker'] = '+'
        if ms=='cross': self._ps['marker'] = 'x'
        if ms=='diamond': self._ps['marker'] = 'D'
        if ms=='thindiamond': self._ps['marker'] = 'd'
        if ms=='tripod': self._ps['marker'] = '1'
        if ms=='tripod_down': self._ps['marker'] = '2'
        if ms=='tripod_left': self._ps['marker'] = '3'
        if ms=='tripod_right': self._ps['marker'] = '4'
        if ms=='hexagon': self._ps['marker'] = 'h'
        if ms=='pentagon': self._ps['marker'] = 'p'
        if ms=='horizontal': self._ps['marker'] = '_'
        if ms=='vertical': self._ps['marker'] = '|'
        return True

    #---------------------------------------------------------

    def line_styles(self):
        """Return a list of the available line-styles"""
        ll = ['-','--',':','-.']
        ll.extend(['solid','dashed','dotted','dashdot'])
        return ll

    #---------------------------------------------------------

    def marker_styles(self):
        """Return a list of the available marker-styles"""
        mm = list('o^v><s+xDd1234hp|_')
        mm.append('steps')
        mm.extend(['circle','triangle','square','plus','cross','diamond'])
        mm.extend(['tripod','hexagon','pentagon'])
        return mm


    #===============================================================
    # Routines dealing with color:
    #===============================================================

    def _check_colors(self):
        """Check the specified colors"""
        cc = self.colors()
        for key in ['color','markerfacecolor','markeredgecolor']:
            color = self._ps[key]
            # Make sure that color is valid:
            if not color in cc: self._ps[key] = 'yellow'
            # Some have to be translated to pylab colors:
            if color=='grey': self._ps[key] = 'gray'
            if color in ['lightgrey','lightgray']: self._ps[key] = 0.1   # 0.0<grayscale<1.0
        return True

    #---------------------------------------------------------

    def colors(self):
        """Return a list of available plot colors"""
        cc = list('bgrcmykw')
        cc.extend(['blue','green','red','cyan','magenta','yellow','black','white','gray'])
        cc.extend(['wheat'])
        cc.extend(['grey','lightgrey','lightgray'])
        return cc
    
    #---------------------------------------------------------

    def print_colors(self):
        print '\n** Available plot-colors:'
        print ' Style 1:'
        print '  b: blue'
        print '  g: green'
        print '  r: red'
        print '  c: cyan'
        print '  m: magenta'
        print '  y: yellow'
        print '  k: black'
        print '  w: white'
        print ' Style 2: standard color string, e.g. yellow, wheat, etc'
        print ' Style 3: grayscale intensity (between 0. and 1., inclusive)'
        print ' Style 4: RGB hex color triple, e.g. #2F4F4F'
        print ' Style 5: RGB tuple, e.g. (0.18, 0.31, 0.31)'
        print
        return True







#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: PlotStyle.py:\n'

    kw = dict()
    kw = dict(color='magenta', style='o', markersize=5, markeredgecolor='blue')

    ps = PlotStyle(**kw)
    print ps.oneliner()

    print ps.kwargs()

    print '\n** End of local test of: PlotStyle.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


