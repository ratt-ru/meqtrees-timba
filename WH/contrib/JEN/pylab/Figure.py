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

import pylab

import time
import copy

import Subplot


#======================================================================================

class Figure (Subplot.Subplot):
    """Encapsulation of a pylab subplot
    """

    def __init__(self, figure=1, nrow=1, ncol=1, name=None): 

        # Deal with the specified name (label):
        self._name = name
        if not isinstance(self._name,str): self._name = '<name>'

        # ctrl.setdefault('figure', None)        # integer: 1,2,3,...
        self._figure = figure
        self._nrow = nrow                        # nr of rows (1-relative)                        
        self._ncol = ncol                        # nr of cols (1-relative)

        # The Subplot objects are kept in the named fields of a dict:
        self._order = []
        self._subplot = dict()
        self._plopos = dict()

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
            key = str(len(self._order))       # .....??
        self._subplot[key] = graphic
        self._plopos[key] = self.make_plopos()
        self._order.append(key)
        return key

    def remove(self, key):
        """Remove a named object from self._subplot"""
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
    # Plot standalone (testing only?)
    #===============================================================

    def plot(self, figure=1, margin=0.1, dispose='show',
             rootname='Figure', trace=False):
        """Plot the pylab figure, with its Subplots"""
        pylab.figure(figure)
        if trace: print '\n** Figure.plot(',figure, margin,dispose,'):'
        for key in self._order:
            subplot = self._plopos[key]['subplot']
            if trace:
                print '  -',key,': subplot =',subplot,self._plopos[key]
                print '  - before:', self._subplot[key].oneliner()
            self._subplot[key].plot(figure=figure, subplot=subplot,
                                    dispose=None)
            if trace: print '  - after:', self._subplot[key].oneliner()
        # Finsished: dispose of the pylab figure:
        if trace: print ' - before Figure.plot(dispose=',dispose,')'
        return pylab_dispose(dispose, origin='Figure.plot()',
                             rootname=rootname, trace=trace)



#========================================================================
# Some helper functions (also used externally)
#========================================================================

def pylab_dispose(dispose='show', rootname='ZZZ', origin='<unknown>', trace=True):
    """Generic routine to dispose of the pylab figure.
    Dipose can be a string (show, svg), or a list of strings"""

    if trace: print '\n** Figure.dispose(',dispose,origin,') rootname=',rootname,
    if dispose==None:
        if trace: print ' (done nothing)\n' 
        return None
    if isinstance(dispose,str):
        dispose = [dispose]
    result = None
    svgname = None
    if trace: print dispose

    file_extensions = ['png','PNG','svg','SVG']
    for ext in file_extensions:
        if ext in dispose:
            filename = rootname+'.'+ext
            delay = 0.0
            if ext in ['svg','SVG']:
                import matplotlib
                matplotlib.use('SVG')
                svgname = filename
                delay = 0.0
            if delay>0.0:
                time.sleep(delay)
                if trace: print '  - sleep(',delay,') before savefig(',filename,')'
            r = pylab.savefig(filename)
            if trace: print '  - pylab.savefig(',filename,') ->',r
            if delay>0.0:
                time.sleep(delay)
                if trace: print '  - sleep(',delay,') after savefig(',filename,')'

    if 'show' in dispose:
        if trace: print '  doing pylab.show()'
        # pylab.show._needmain = False
        pylab.show()
        # pylab.ion()
        # pylab.draw()
        # pylab.close()
        
    if isinstance(svgname,str):
        file = open(filename,'r')
        result = file.readlines()
        file.close()
        if trace:
            n = len(result)
            print '\n - read:',filename,'->',type(result),n,'\n'
            for i in range(min(6,n-1)): print '  -',i,': ',result[i]
            print '  ........'
            print '  ........'
            print
            for i in range(max(0,n-5),n): print '  -',i,': ',result[i]
            print
        if False:
            import os
            os.system("%s -size 640x480 %s" % ('display',filename))
            # -> error: "display: Opening and ending tag mismatch: name line 0 and text"
        
    # Finished: return the result (if any):
    return result



#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Figure.py:\n'

    import Subplot

    fig = Figure(nrow=2, ncol=2)

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
        dispose = 'show'
        dispose = 'svg'
        # dispose = ['svg','show']
        fig.plot(dispose=dispose, trace=True)

    print '\n** End of local test of: Figure.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


