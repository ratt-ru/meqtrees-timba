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
    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    mystate('plotinfo')
    self.plotinfo.setdefault('labels',None) 
    return None

  #-------------------------------------------------------------------

  def on_entry(self, trace=False):
    """Called on entry of .get_result()"""
    self._count += 1

    # We need the following two lines (AWG)
    import matplotlib
    matplotlib.use('SVG')

    # Create a Graphics object:
    import Graphics
    grs = Graphics.Scatter(None, name=self.class_name,
                           # plot_type='polar',     # does not work in svg...!
                           plot_grid=True,
                           title=self.plotinfo.title,
                           xlabel=self.plotinfo.xlabel,
                           ylabel=self.plotinfo.ylabel)
    grs.legend(self.name, color='red')
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
    grs = self.on_entry()
    xx = self.read_results(children, self.plotinfo.iix)
    yy = self.read_results(children, self.plotinfo.iiy, error_bars=True)
    labels = self.read_labels(self.plotinfo.iiy)
    for i,y in enumerate(yy):
      grs[0].append(y=yy[i], x=xx[i], annot=labels[i], dy=self._dvv[i])
    return self.on_exit(grs)


  #-------------------------------------------------------------------


  def read_labels (self, ii=None, index=None, trace=True):
    """Return a vector with a subset (ii) of labels (strings)
    selected from self.plotinfo.labels.
    """

    if trace:
      print '\n** .read_labels(): index =',index,ii

    labels = self.plotinfo.labels
    if labels==None:
      labels = n*None                         # vector of None values
    if not len(labels)==n:
      labels = n*'?'                          # vector of question marks

    jj = self.check_indices(ii, index=index, trace=trace)

    # Select a vector of (string) labels:
    ss = []
    for i in jj:
      ss.append(labels[i])

    # Finished:
    if trace:
      print '  -> selected labels =',ss,'\n'
    return labels

  #-------------------------------------------------------------------

  def check_indices (self, ii=None, index=None, trace=True):
    """Return a valid vector of indices into the list of children.
    If index is specified (integer), assume that ii is a list of lists,
    and use ii[index].
    """
    n = len(self.child_indices)               # nr of children
    if ii==None:
      return range(n)

    if isinstance(index,int):
      return ii[index]

    return ii

  #-------------------------------------------------------------------

  def read_results (self, children, ii=None, index=None,
                    error_bars=True, trace=True):
    """Return a vector of numbers from the results of the specified (ii) children.
    If index is integer, assume use ii[index].
    """

    if trace:
      print '\n** .read_results(): index =',index,ii

    jj = self.check_indices(ii, index=index, trace=trace)

    # Select a vector of child results:
    cc = []
    for i in jj:
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
    grs = self.on_entry()
    yy = self.read_results(children, error_bars=True)
    labels = self.read_labels()
    for i,y in enumerate(yy):
      grs[0].append(y=y, x=i, annot=labels[i], dy=self._dvv[i])
    return self.on_exit(grs)


#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================



#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  cc = []
  
  if True:
    ftx= ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())
    ft= ns.freqtime << Meq.Add(Meq.Time(),Meq.Freq())

    n = 5
    ccXY = []
    ccY = []
    iix = []
    iiy = []
    labelsXY = []
    labelsY = []
    for i in range(n):
      x = ns.x(i) << i
      # y = ns.y(i) << random.gauss(i,0.5)
      y = ns.y(i) << (ft + random.gauss(i,0.5))

      # For VisuPlotXY (x and y children):
      ccXY.append(x)
      labelsXY.append(x.name)   
      iix.append(len(ccXY)-1)

      ccXY.append(y)
      labelsXY.append(y.name)   
      iiy.append(len(ccXY)-1)
      
      # For VisuPlotY (y children only):
      ccY.append(y)
      labelsY.append(y.name)   

    bookpage = Meow.Bookmarks.Page('pynodes')
    pn = []

    #----------------------------
    classname = 'VisuPlotXY'
    plotinfo = record(labels=labelsXY, title='title',
                      iix=iix, iiy=[iiy],
                      xlabel='xlabel', ylabel='ylabel')
    pynode = ns[classname] << Meq.PyNode(children=ccXY,
                                         class_name=classname,
                                         plotinfo=plotinfo,
                                         module_name=__file__)
    pn.append(pynode)
    Meow.Bookmarks.Page(classname).add(pynode, viewer="Svg Plotter")
    bookpage.add(pynode, viewer="Svg Plotter")

    #----------------------------
    classname = 'VisuPlotY'
    plotinfo = record(labels=labelsY, title='title',
                      xlabel='xlabel', ylabel='ylabel')
    pynode = ns[classname] << Meq.PyNode(children=ccY,
                                         class_name=classname,
                                         plotinfo=plotinfo,
                                         module_name=__file__)
    pn.append(pynode)
    Meow.Bookmarks.Page(classname).add(pynode, viewer="Svg Plotter")
    bookpage.add(pynode, viewer="Svg Plotter")


    #----------------------------
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
