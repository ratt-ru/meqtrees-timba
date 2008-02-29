# file: ../contrib/JEN/pylab/VisuPlotXY.py

# Author: J.E.Noordam
# 
# Short description:
#   Various pyNode classes to make arbitrary xy-plots from child results
#
# History:
#    - 23 feb 2008: creation
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
#-------------------------------------------------------------------------------

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

import inspect
import random


Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='VisuPlotXY');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;



#=====================================================================================
# The VisuPlotXY base class:
#=====================================================================================

class VisuPlotXY (pynode.PyNode):
  """Make an xy-plot of the results of its children"""

  def __init__ (self, *args, **kwargs):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution')
    self._count = -1
    self._dvv = None
    return None

  def update_state (self, mystate):
    """Read information from the pynode state record"""
    trace = False
    trace = True
    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    nc = len(self.child_indices)       # nr of children
    mystate('plotinfo')
    print '\n** update_state(): self.plotinfo:',self.plotinfo,'\n'
    self._subplot = []
    if self.plotinfo.has_key('subplot'):
      for rr in self.plotinfo.subplot:
        if trace: print '\n-- subplot:',rr
        rr.setdefault('iix', range(nc)) 
        rr.setdefault('iiy', range(nc)) 
        rr.setdefault('labels', nc*[None]) 
        rr.setdefault('color','red') 
        # rr.setdefault('style','--')
        if trace:
          for key in rr.keys():
            print '  -',key,':',rr[key]
          print
        self._subplot.append(rr)
    return None

  #-------------------------------------------------------------------

  def on_entry(self, trace=False):
    """Called on entry of .get_result()"""
    self._count += 1

    # We need the following two lines (AWG)
    import matplotlib
    matplotlib.use('SVG')

    # Create an empty Graphics object:
    import Graphics
    grs = Graphics.Graphics(name=self.class_name,
                            # plot_type='polar',     # does not work in svg...!
                            plot_grid=True,
                            title=self.plotinfo.title,
                            xlabel=self.plotinfo.xlabel,
                            ylabel=self.plotinfo.ylabel)

    if trace:
      grs.display('empty')
      grs[0].display('filled')
    return grs

  #-------------------------------------------------------------------

  def on_exit (self, grs, trace=False):
    """Called on exit of .get_result().
    Put the given pylab Graphics (grs) into a pylab Figure (fig).
    Turn the Figure into an svg string, and attach it to a result"""
    import Figure
    fig = Figure.Figure()
    fig.add(grs)
    if trace:
      s = str(self.class_name)+'.on_exit()'
      grs.display(s)
      grs[0].display('filled')
      fig.display(s)
    svg_list_of_strings = fig.plot(dispose=['svg'],
                                   rootname=self.class_name,
                                   clear=False, trace=trace)
    result = meq.result()
    result.svg_plot = svg_list_of_strings
    return result

  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Placeholder, to be re-implemented in derived classes"""
    import Graphics
    grs = self.on_entry()
    # Make separate Graphics/Subplot objects for the various subplots:
    for rr in self._subplot:
      xx = self.read_results(children, rr.iix)
      yy = self.read_results(children, rr.iiy, error_bars=True)
      labels = self.read_labels(rr.labels, rr.iiy)
      grs1 = Graphics.Scatter(yy=yy, xx=xx, annot=labels,
                              dyy=self._dvv,
                              style='o', markersize=10,
                              color=rr.color)
      grs.add(grs1)
      grs.legend(self.name, color=rr.color)
    # Finished:
    return self.on_exit(grs, trace=True)

  #-------------------------------------------------------------------

  def read_labels (self, labels, ii=None, trace=True):
    """Return a vector with a subset (ii) of labels (strings)
    selected from self.plotinfo.labels.
    """

    if trace:
      print '\n** .read_labels(',ii,'):'

    n = len(self.child_indices)               # nr of children
    if ii==None: ii = range(n)

    # Select a vector of (string) labels:
    ss = []
    for i in ii:
      ss.append(labels[i])

    # Finished:
    if trace:
      print '  -> selected labels =',ss,'\n'
    return ss

  #-------------------------------------------------------------------

  def read_results (self, children, ii=None, 
                    error_bars=True, trace=True):
    """Return a vector of numbers from the results of the specified (ii) children.
    """

    if trace:
      print '\n** .read_results(',ii,'):'

    n = len(self.child_indices)               # nr of children
    if ii==None: ii = range(n)

    # Select a vector of child results:
    cc = []
    for i in ii:
      cc.append(children[i])

    # Read the child results and fill the vector(s):
    import ChildResult
    vv = []                                   # vv is a vector of y-values
    self._dvv = []                            # self._dvv is a vector of error-bars
    for i in range(len(cc)):
      cr = ChildResult.Result(cc[i])          # cc[i] is MeqResult class
      if trace:
        # cr.display()
        # print '--',i,':',cr.oneliner()
        pass
      Vells = cr[0]
      if trace:
        print '---',i,':',Vells.oneliner()
      vv.append(Vells.mean())
      # Optional, read error-bar info into self._dvv
      if error_bars:
        self._dvv.append(Vells.errorbar())

    # Finished:
    if trace:
      print '  -> vv =',vv,'\n'
      if error_bars:
        print '  -> dvv =',self._dvv,'\n'
    return vv



#=====================================================================================
# Classes derived from VisuPlotXY:
#=====================================================================================

class VisuPlotY (VisuPlotXY):
  """Make an xy-plot of the results of its children"""

  def __init__ (self, *args, **kwargs):
    VisuPlotXY.__init__(self,*args);
    return None

  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Re-implementation of the function in baseclass VisuPlotXY"""
    import Graphics
    grs = self.on_entry()
    # Make separate Graphics/Subplot objects for the various subplots:
    for rr in self._subplot:
      yy = self.read_results(children, rr.iiy, error_bars=True)
      xx = range(len(yy))
      labels = self.read_labels(rr.labels, rr.iiy)
      grs1 = Graphics.Scatter(yy=yy, xx=xx, annot=labels,
                              dyy=self._dvv,
                              style='o', markersize=10,
                              color=rr.color)
      grs.add(grs1)
      grs.legend(self.name, color=rr.color)
    # Finished
    return self.on_exit(grs, trace=True)


#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================



#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  children = dict()
  rr = dict()
  classname = []

  ftx= ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())
  ft= ns.freqtime << Meq.Add(Meq.Time(),Meq.Freq())
  
  if True:
    name = 'VisuPlotXY'
    yname = 'y1'
    xname = 'x1'
    cc = []
    iix = []
    iiy = []
    labels = []
    n = 5
    for i in range(n):
      x = ns[xname](i) << random.gauss(i,0.3)
      # y = ns[yname](i) << random.gauss(i,0.5)
      y = ns[yname](i) << (ft + random.gauss(i,0.5))
      cc.append(x)
      labels.append(x.name)   
      iix.append(len(cc)-1)
      cc.append(y)
      labels.append(y.name)   
      iiy.append(len(cc)-1)
    classname.append(name)
    children[name] = cc
    rr[name] = record(title=name, xlabel=xname, ylabel=yname, subplot=[])
    rr[name].subplot.append(record(iix=iix, iiy=iiy, labels=labels))
      
  if True:
    name = 'VisuPlotY'
    cc = []
    labels = []
    n = 6
    yname = 'y2'
    xname = 'range(n)'
    for i in range(n):
      # y = ns[yname](i) << random.gauss(i,0.5)
      y = ns[yname](i) << (ft + random.gauss(i,0.5))
      cc.append(y)
      labels.append(y.name)   
    classname.append(name)
    children[name] = cc
    rr[name] = record(title=name, xlabel=xname, ylabel=yname, subplot=[])
    rr[name].subplot.append(record(labels=labels, color='blue'))
      
      
  # Make the pynode(s):
  bookpage = Meow.Bookmarks.Page('pynodes')
  pn = []
  for name in classname:
    print '\n** rr[',name,'] =',rr[name],'\n'
    pynode = ns[name] << Meq.PyNode(children=children[name],
                                    class_name=name,
                                    plotinfo=rr[name],
                                    module_name=__file__)
    pn.append(pynode)
    Meow.Bookmarks.Page(name).add(pynode, viewer="Svg Plotter")
    bookpage.add(pynode, viewer="Svg Plotter")
  ns.rootnode << Meq.Composer(*pn) 

  # Finished:
  return True
  


#=====================================================================================
# Execute a test-forest:
#=====================================================================================

def _test_forest (mqs,parent,wait=False):
  from Timba.Meq import meq
  i = 0
  cells = meq.cells(meq.domain(i,i+1,i,i+1),num_freq=20,num_time=10);
  print '\n--',i,': cells =',cells,'\n'
  request = meq.request(cells,rqtype='e1');
  a = mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True


def _tdl_job_sequence (mqs,parent,wait=False):
  from Timba.Meq import meq
  for i in range(5):
    cells = meq.cells(meq.domain(i,i+1,i,i+1),num_freq=20,num_time=10);
    rqid = meq.requestid(i)
    print '\n--',i,rqid,': cells =',cells,'\n'
    request = meq.request(cells, rqid=rqid);
    a = mqs.meq('Node.Execute',record(name='rootnode',request=request), wait=wait)
  return True


#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':
 # run in batch mode?
 if '-run' in sys.argv:
   from Timba.Apps import meqserver
   from Timba.TDL import Compile

   # this starts a kernel.
   mqs = meqserver.default_mqs(wait_init=10);

   # This compiles a script as a TDL module. Any errors will be thrown as
   # an exception, so this always returns successfully. We pass in
   # __file__ so as to compile ourselves.
   (mod,ns,msg) = Compile.compile_file(mqs,__file__);

   # this runs the _test_forest job.
   mod._test_forest(mqs,None,wait=True);

 else:
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  ns.Resolve();
