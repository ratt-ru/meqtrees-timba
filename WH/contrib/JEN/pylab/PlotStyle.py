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

        # The keyword arguments for the various plot-routines
        # come from kwargs, and are held in separate dicts.

        self._kw = dict(plot=dict(), text=dict()) 

        # Some generic keywords:
        if not isinstance(kwargs,dict):
            kwargs = dict()
        kwargs.setdefault('name','name')
        self._name = kwargs['name']
        
        # Specific extraction functions:
        self.extract_kw_plot(**kwargs)
        self.extract_kw_text(**kwargs)
        self.extract_kw_scatter(**kwargs)

        # Finished:
        return None


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <PlotStyle> '+str(self._name)+': '
        ss += self.summary() 
        return ss

    #------------------------------------------------------------

    def display(self, txt=None):
        """Display the contents of this obkect"""
        print '\n**',self.oneliner()
        if txt: print ' * (',txt,')'
        for func in ['plot','text']:
            print ' * keywords for:  pylab.'+str(func)+'():'
            kw = self._kw[func]
            for key in kw.keys():
                print '   - '+str(func)+'['+str(key)+'] =',kw[key]
        print ' '
        return True



    #===============================================================
    # Access routines:
    #===============================================================

    def kwargs(self, func='plot'):
        """Return the keyword arguments to be used for a particular
        pylab function (e.g. plot, text, loglog, etc)"""
        if self._kw.has_key(func):
            return self._kw[func]
        elif func in ['loglog','semilogx','semilogy']:
            return self._kw['plot']
        # Always return something. It might work.
        return self._kw['plot']


    def color(self):
        """Return 'the' color (string)"""
        if self._kw['plot'].has_key('color'):
            return self._kw['plot']['color']
        # Always return a color, albeit an unattractive one:
        return 'yellow'





    #===============================================================
    # Start of specific part (for pylab). Make derived class....? 
    #===============================================================

    def extract_kw_plot(self, **kwargs):
        """Extract pylab.plot() keywords from kwargs"""

        trace = True
        trace = False
        
        kw = dict()
        if isinstance(kwargs, dict):
            keys = ['color','style',
                    'linewidth','linestyle',
                    'marker','markerfacecolor','markeredgecolor',
                    'markersize','markeredgewidth',
                    'alpha']
            for key in keys:
                if kwargs.has_key(key):
                    kw[key] = kwargs[key]
        if trace:
            self._kw['plot'] = kw
            self.display('from kwargs')

        # Generic (specifies line or marker):
        kw.setdefault('color', 'red')
        kw.setdefault('style', None)              # must be removed again....

        # See page 37 of the Greenfield manual:

        # Line style:
        kw.setdefault('linestyle', None)
        kw.setdefault('linewidth', 1)             # in points, non-zero float 

        # Marker style:
        kw.setdefault('marker', None)
        kw.setdefault('markerfacecolor', kw['color'])
        kw.setdefault('markeredgecolor', kw['color'])
        kw.setdefault('markersize', 5)            # in points, non-zero float 
        kw.setdefault('markeredgewidth', 1)       # in points, non-zero float 

        # Miscellaneous:
        kw.setdefault('alpha', 0.5)               # transparency (0.0<=alpha<=1.0)
        # kw.setdefault('data_clipping', True)    # not recognised...?

        # Finsihed:
        self._kw['plot'] = kw

        # if trace: self.display('before checks')
        self._check_colors()
        self._check_styles()
        if trace: self.display('checked')
        return True

    #------------------------------------------------------------

    def extract_kw_scatter(self, **kwargs):
        """Extract pylab.scatter() keywords from kwargs"""

        trace = True
        trace = False
        
        kw = dict()
        if isinstance(kwargs, dict):
            keys = ['color',
                    # 'style',
                    'linewidth',
                    # 'facecolor','edgecolor',
                    'alpha']
            for key in keys:
                if kwargs.has_key(key):
                    kw[key] = kwargs[key]
        if trace:
            self._kw['scatter'] = kw
            self.display('from kwargs')

        # Generic (specifies line or marker):
        kw.setdefault('color', 'red')
        # kw.setdefault('style', None)              # must be removed again....

        # See page 37 of the Greenfield manual:

        # Line style:
        kw.setdefault('linewidth', 1)             # in points, non-zero float 

        # Marker style:
        # kw.setdefault('facecolor', kw['color'])
        # kw.setdefault('edgecolor', kw['color'])

        # Miscellaneous:
        kw.setdefault('alpha', 0.5)               # transparency (0.0<=alpha<=1.0)

        # Finsihed:
        self._kw['scatter'] = kw

        # if trace: self.display('before checks')
        # self._check_colors()
        # self._check_styles()
        if trace: self.display('checked')
        return True


    #------------------------------------------------------------
    
    def summary(self):
        """Return a short string summarizing the plot-style"""
        kw = self._kw['plot']
        ss = ' ('
        if kw.has_key('color'):
            ss += str(kw['color'])
        if kw.has_key('marker') and kw['marker']:
            ss += ' '+str(kw['marker'])
        if kw.has_key('linestyle') and kw['linestyle']:
            ss += ' '+str(kw['linestyle'])
        ss += ')'
        return ss


    #---------------------------------------------------------
        
    def extract_kw_text(self, **kwargs):
        """Extract pylab.text() keywords from kwargs"""

        trace = True
        trace = False
        
        kw = dict()
        if isinstance(kwargs, dict):
            keys = ['fontsize']
            for key in keys:
                if kwargs.has_key(key):
                    kw[key] = kwargs[key]
        if trace:
            self._kw['text'] = kw
            self.display('from kwargs')

        # See page 38 of the Greenfield manual:
        kw.setdefault('color', self.color())
        # kw.setdefault('family', 'normal')          # e.g. 'sans-serif','cursive','fantasy'
        # kw.setdefault('variant', 'normal')         # e.g. 'normal','small-caps'
        # kw.setdefault('fontangle', 'normal')           # 'normal','italic','oblique'
        kw.setdefault('fontsize', 10)                  # in points 
        kw.setdefault('rotation', 0)                  # degrees
        # kw.setdefault('verticalalignment', 'top')      # 'top','bottom','center'
        # kw.setdefault('horizontalalignment', 'left')  # 'left','right','center'

        # Only for multi-line strings:
        # kw.setdefault('multialignment', 'center')      # 'left','right','center'

        # Finsihed:
        self._kw['text'] = kw
        if trace: self.display('checked')
        return True
    



    #===============================================================
    # Routines dealing with style:
    #===============================================================

    def _check_styles(self):
        """Check the specified plot-styles"""
        kw = self._kw['plot']                   # convenience

        # If only lines or markers are required, their style may be
        # specified via the 'style' keyword. If they are both required
        # the more specific 'marker' and 'linestyle' must be used.
        if not kw['style'] or kw['marker'] or kw['linestyle']:
            kw['style'] = '-'
        if kw['style'] in self.line_styles():
            if not kw['linestyle']:
                kw['linestyle'] = kw['style']
        elif kw['style'] in self.marker_styles():
            if not kw['marker']:
                kw['marker'] = kw['style']
                kw['linestyle'] = None
        kw.__delitem__('style')            # not recognized by pylab.plot(): delete

        # Some local extensions to the pylab linestyles:
        ls = kw['linestyle']
        if ls=='solid': kw['linestyle'] = '-'
        if ls=='dashed': kw['linestyle'] = '--'
        if ls=='dotted': kw['linestyle'] = ':'
        if ls=='dashdot': kw['linestyle'] = '-.'

        # Some local extensions to the pylab marker styles:
        ms = kw['marker']
        if ms=='circle': kw['marker'] = 'o'
        if ms=='triangle': kw['marker'] = '^'
        if ms=='square': kw['marker'] = 's'
        if ms=='plus': kw['marker'] = '+'
        if ms=='cross': kw['marker'] = 'x'
        if ms=='diamond': kw['marker'] = 'D'
        if ms=='thindiamond': kw['marker'] = 'd'
        if ms=='tripod': kw['marker'] = '1'
        if ms=='tripod_down': kw['marker'] = '2'
        if ms=='tripod_left': kw['marker'] = '3'
        if ms=='tripod_right': kw['marker'] = '4'
        if ms=='hexagon': kw['marker'] = 'h'
        if ms=='pentagon': kw['marker'] = 'p'
        if ms=='horizontal': kw['marker'] = '_'
        if ms=='vertical': kw['marker'] = '|'

        # Temporary kludge(s) to solve SVG poblems:
        if True:
            s = '\n** .PlotStyle: temporary SVG kludge: '
            if kw['linestyle']==None:
                kw['linestyle'] = '.'             # not recognized, ignored...  
                # print s,' avoided linestyle=None ->',kw['linestyle']

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
        kw = self._kw['plot']
        for key in ['color','markerfacecolor','markeredgecolor']:
            color = kw[key]
            # Make sure that color is valid:
            if not color in cc: kw[key] = 'yellow'
            # Some have to be translated to pylab colors:
            if color=='grey': kw[key] = 'gray'
            if color in ['lightgrey','lightgray']: kw[key] = 0.1   # 0.0<grayscale<1.0
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


