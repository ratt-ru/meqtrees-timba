#!/usr/bin/env python

# file: ../contrib/JEN/pylab/Figure.py

# Author: J.E.Noordam
# 
# Short description:
#   Class that represents a pylab Figure. It holds a series
#   of pylab Subplot objects.
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


import Subplot
import pylab

import time
import copy



#======================================================================================

class Figure (Subplot.Subplot):
    """Encapsulation of a pylab subplot
    """

    def __init__(self, nrow=1, ncol=1, name=None, clear=True): 

        # Deal with the specified name (label):
        self._name = name
        if not isinstance(self._name,str): self._name = '<name>'
        
        self._nrow = nrow                        # nr of rows (1-relative)                        
        self._ncol = ncol                        # nr of cols (1-relative)

        # The Subplot objects are kept in the named fields of a dict:
        self._order = []
        self._subplot = dict()
        self._plopos = dict()

        # If no figure object (figob) is supplied to .make_plot(),
        # a "pylab" figure is used by default:
        self._figob = None               
        self._pylab_figure = False 

        # Clear any existing pylab figure (kludge?)
        if clear:
            pylab.clf()

        # Finished:
        return None


    #===============================================================

    def make_plopos(self):
        """Make the plopos (dict) of the next Subplot"""

        # ctrl.setdefault('subplot', None)       # integer: nrow*100+ncol*10+iplot (all 1-relative)
        # ctrl.setdefault('plopos', dict(iplot=1, irow=1, icol=1, nrow=1, ncol=1))
        # k = ctrl['subplot']
        # pp = ctrl['plopos']                # convenience
        # pp['nrow'] = k/100
        # pp['ncol'] = (k-100*pp['nrow'])/10
        # pp['iplot'] = k-100*pp['nrow']-10*pp['ncol']
        # pp['irow'] = 1+(pp['iplot']-1)/pp['ncol'] 
        # pp['icol'] = pp['iplot']-pp['ncol']*(pp['irow']-1)

        nrow = self._nrow
        ncol = self._ncol
        iplot = len(self._order)+1
        subplot = nrow*100 + ncol*10 + iplot
        irow = 1 + (iplot-1)/ncol 
        icol = iplot - ncol*(irow-1)
        plopos = dict(iplot=iplot, subplot=subplot,
                      nrow=nrow, ncol=ncol, irow=irow, icol=icol)
        return plopos
        

    def add(self, graphic, key=None):
        """Add a named (key) plottable object to self._subplot"""
        if not isinstance(key, str):
            key = str(len(self._order))              # .....??
        self._subplot[key] = graphic
        self._plopos[key] = self.make_plopos()
        self._order.append(key)
        return key

    def remove(self, key):
        """Remove a named object from self._subplot"""
        if self.has_key(key):
            self._subplot.__delitem__(key)
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
        """Return the name (label?) of this Figure"""
        return self._name

    def has_key(self, key):
        """Check whether self._subplot has the specified key"""
        return self._subplot.has_key(key)

    def __getitem__(self, index):
        """Get the specified plottable object (key or index)"""
        key = None
        if isinstance(index,str):
            key = index
        elif isinstance(index,int):
            key = self._order[index]
        return self._subplot[key]


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <Figure> '+self.name()+':'
        ss += ' n='+str(self.len())
        ss += ' nrow='+str(self._nrow)
        ss += ' ncol='+str(self._ncol)
        return ss

    def display(self, txt=None):
        """Display a summary of this Figure"""
        print '\n** (',txt,')'
        print ' * ',self.oneliner()
        for key in self._order:
            subplot = self._plopos[key]['subplot']
            print '   -',key,'('+str(subplot)+'):',self._subplot[key].oneliner()
        if True:
            print ' * plopos:'
            for key in self._order:
                print '   -',key,':',self._plopos[key]
        print
        return True

    #===============================================================
    # Make the plot(s), using the given figure object:
    #===============================================================

    def make_plot(self, figob=None, margin=0.1, show=True, trace=False):
        """Make the plot(s) in the various panels (subplots)"""

        # trace = True

        # If no figure object specified, assume standalone:
        if figob==None:
            self._figob = pylab.figure(1)
            self._pylab_figure = True
        else:
            self._figob = figob
            show = False
            self._pylab_figure = False

        if trace:
            print '\n** Figure.make_plot(',figob, margin,'):',self._figob

        for key in self._order:
            subplot = self._plopos[key]['subplot']
            if trace:
                print '  -',key,': subplot =',subplot,self._plopos[key]
            axob = self._figob.add_subplot(subplot)
            if trace:
                print '    axob =',axob
            self._subplot[key].make_plot(axob=axob, trace=trace)

        # Finished:
        if show:
            self.show()
        return self._figob

    #====================================================================

    def show (self):
        """Show the internal figure"""
        if self._pylab_figure:
            pylab.show()
        else:
            print '\n** Internal figure not a pylab figure....\n'
        return True
        

    #====================================================================
    # Save the figure in a file:
    #====================================================================

    def save (self, rootname='rootname', ext='png',
              clear=False, trace=False):
        """Save the figure in a file"""

        # If no plot has been made yet, make a pylab one:
        if self._figob==None:
            self.make_plot(show=False)

        if ext in ['svg','SVG']:
            import matplotlib             # Tony says...??
            matplotlib.use('SVG')         # Tony says...??
            filename = rootname+'.svg'
            # svgname = filename            # used below...
            # since we are using backend 'SVG', svg is
            # automatically added to filename
            # r = pylab.savefig(rootname)
            # if trace: print '  - pylab.savefig(',rootname,') ->',r

        elif ext in ['png','PNG']:
            filename = rootname+'.png'

        else:
            filename = rootname+'.'+ext

        # OK, save the internal figure, and check the resulting file:
        r = self._figob.savefig(filename)
        if trace:
            print '\n** Figure.save(): .savefig(',filename,') ->',r,'\n'
        if True:
            file = open(filename,'r')
            file.close()
        
        # Optional: clear the current pylab (!) figure AFTER .savefig()
        if clear:
            self._figob.clf()

        # Finished:
        return filename


    #====================================================================
    # Make SVG XML definition (list of strings) of the figure
    #====================================================================

    def make_svg (self, rootname='rootname', trace=False):
        """Return a a SVG XML definition as a list of strings"""

        filename = self.save(rootname=rootname, ext='svg', trace=trace)

        file = open(filename,'r')
        xml = file.readlines()
        file.close()

        if trace:
            n = len(xml)
            print '\n - read:',filename,'->',type(xml),n,'\n'
            for i in range(min(6,n-1)):
                print '  -',i,': ',xml[i]
            print '  ........'
            print '  ........'
            print
            for i in range(max(0,n-5),n):
                print '  -',i,': ',xml[i]
            print

        if True:
            import os
            os.system("%s -size 640x480 %s" % ('display',filename))
            # -> error: "display: Opening and ending tag mismatch: name line 0 and text"

        # Finished:
        return xml
        


#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Figure.py:\n'

    # import Subplot

    fig = Figure(nrow=2, ncol=2)

    if 0:
        sub = Subplot.Subplot(xmin=-3,xmax=6,ymin=-7,ymax=8)
        fig.add(sub)

    if 0:
        fig.add(Subplot.test_line())

    if 1:
        fig.add(Subplot.test_line())
        fig.add(Subplot.test_parabola())
        fig.add(Subplot.test_sine())
        fig.add(Subplot.test_cloud(xmin=-10))

    if 0:
        plot_types = ['plot','loglog','semilogy','semilogx']
        plot_types = ['plot','polar','scatter','quiver']
        for plot_type in plot_types:
            fig.add(Subplot.test_line(plot_type=plot_type, title=plot_type, marker='o'))
        
    fig.display()

    if 1:
        fig.make_plot(show=True, trace=False)

    if 0:
        fig.save(trace=True)

    if 0:
        fig.make_svg(trace=True)

    print '\n** End of local test of: Figure.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


