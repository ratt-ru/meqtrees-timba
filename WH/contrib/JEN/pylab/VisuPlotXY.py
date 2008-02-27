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
    return None

  def update_state (self, mystate):
    # put the node-name into self.name
    mystate('name')
    mystate('class_name')
    mystate('plot_labels')
    mystate('plot_xlabel')
    mystate('plot_ylabel')
    mystate('plot_title')
    mystate('plot_iix')
    mystate('plot_iiy')
    return None
                              
  def get_result (self, request, *children):
    """Placeholder, to be re-implemented in derived classes"""
    self.on_entry()
    grs = self.read_children(children)
    return self.on_exit(grs)

  #-------------------------------------------------------------------

  def on_entry(self, trace=False):
    """Called on entry of .get_result()"""
    self._count += 1

    # We need the following two lines (AWG)
    import matplotlib
    matplotlib.use('SVG')

    return True

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
      fig.display(s)
    svg_list_of_strings = fig.plot(dispose=['svg'],
                                   rootname=self.class_name,
                                   clear=False, trace=trace)
    result = meq.result()
    result.svg_plot = svg_list_of_strings
    return result

  #-------------------------------------------------------------------

  def read_children (self, children, error_bars=False, trace=True):
    """Accumulate the point(s) representing the child result(s)"""

    # Create a Graphics object:
    import Graphics
    grs = Graphics.Scatter(name=self.class_name,
                           # plot_type='polar',     # does not work in svg...!
                           title=self.plot_title,
                           xlabel=self.plot_xlabel,
                           ylabel=self.plot_ylabel)
    grs.legend(self.name, color='red')
    grs.display()

    # Sort the x and y children, using self.ixx and self.iyy:
    xx = []
    yy = []
    for i in self.plot_iix:
      xx.append(children[i])
    for i in self.plot_iiy:
      yy.append(children[i])

    # Read the child results and fill the Graphics objects:
    import ChildResult
    for i in range(len(yy)):
      cry = ChildResult.Result(yy[i])        # yy[i] is MeqResult class
      crx = ChildResult.Result(xx[i])        # xx[i] is MeqResult class
      if trace:
        # crx.display()
        # cry.display()
        print '--',i,':',crx.oneliner()
        print '--',i,':',cry.oneliner()
      Vellsy = cry[0]
      Vellsx = crx[0]
      if trace:
        print '---',i,':',Vellsx.oneliner()
        print '---',i,':',Vellsy.oneliner()
      dy = None
      if error_bars:
        dy = Vellsy.errorbar()          
      grs[0].append(y=Vellsy.mean(), x=Vellsx.mean(),
                    annot=self.plot_labels[i], dy=dy)
        
    # Finished: Return the modified Graphics object
    return grs



#=====================================================================================
# Classes derived from VisuPlotXY:
#=====================================================================================



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

    n = 5
    cc = []
    iix = []
    iiy = []
    labels = []
    for i in range(n):
      labels.append(str(i))
      cc.append(ns.x(i) << i)
      iix.append(len(cc)-1)
      cc.append(ns.y(i) << random.gauss(i,0.1))
      iiy.append(len(cc)-1)


    bookpage = Meow.Bookmarks.Page('pynodes')
    # bookpage.add(ns.cx_freqtime, viewer="Result Plotter")                
    pn = []
    for classname in ['VisuPlotXY']:
      pynode = ns[classname] << Meq.PyNode(children=cc,
                                           class_name=classname,
                                           plot_iix=iix,
                                           plot_iiy=iiy,
                                           plot_labels=labels,
                                           plot_title='<plot-title>',
                                           plot_xlabel='<plot-xlabel>',
                                           plot_ylabel='<plot-ylabel>',
                                           module_name=__file__)
      pn.append(pynode)
      Meow.Bookmarks.Page(classname).add(pynode, viewer="Svg Plotter")
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
