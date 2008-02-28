# file: ../contrib/JEN/pylab/VisuVis22.py

# Author: J.E.Noordam
# 
# Short description:
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

_dbg = utils.verbosity(0,name='VisuVis22');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;



#=====================================================================================
# The VisuVis22 base class:
#=====================================================================================

class VisuVis22 (pynode.PyNode):
  """Make a scatter-plot of the means of the results of its children"""

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
    return None
                              
  def get_result (self, request, *children):
    """Placeholder, to be re-implemented in derived classes"""
    grs = self.on_entry()
    return self.on_exit(grs)

  #-------------------------------------------------------------------

  def on_entry(self, trace=False):
    """Called on entry of .get_result()"""
    self._count += 1
    self._title = 'VisuVis22.'+self.class_name+'_'+str(self._count)
    self._xlabel = 'real part (Jy)'
    self._ylabel= 'imag part (Jy)'

    # we need the following two lines
    import matplotlib
    matplotlib.use('SVG')

    # Create a Graphics object:
    import Graphics
    grs = Graphics.Graphics(name=self.class_name,
                            # plot_type='polar',     # does not work in svg...!
                            title=self._title,
                            xlabel=self._xlabel, ylabel=self._ylabel)
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
      fig.display(s)
    svg_list_of_strings = fig.plot(dispose=['svg'],
                                   rootname=self.class_name,
                                   clear=False, trace=trace)
    result = meq.result()
    result.svg_plot = svg_list_of_strings
    return result

  #-------------------------------------------------------------------

  def read_children (self, grs, children, corrs=['XX','XY','YX','YY'],
                     error_bars=True, annotate=True, trace=False):
    """Accumulate the point(s) representing the child result(s)"""

    # Fill the input Graphics object with a 'standard' Graphics object
    # for each of the 1-4 specified correlations:
    iicorr = []
    for corr in corrs:
      iicorr.append(corr_index(corr))
      grs.add(corr_Graphics(corr))
      grs.legend(corr, color=corr_color(corr))

    # The plot-labels for the various children should have been
    # attached to the pynode state-record when the pynode was defined
    # (see _define_forest() below):

    if annotate==True:
      annotate = corrs
    if not isinstance(annotate,(list,tuple)):
      annotate = []
    if len(annotate)>0:
      annot = self.plot_labels
      if not isinstance(annot,(list,tuple)):
        annot = range(len(children))
      elif not len(annot)==len(children):
        annot = range(len(children))

    # Read the child results and fill the Graphics objects:
    import ChildResult
    for i,child in enumerate(children):
      chires = ChildResult.Result(child)     # child is MeqResult class
      if trace:
        # chires.display()
        print '--',i,':',chires.oneliner()
      dy = None
      for igrs,icorr in enumerate(iicorr):
        corr = corrs[icorr]
        Vells = chires[icorr]
        if trace:
          print '---',i,igrs,icorr,corr,':',Vells.oneliner()
        mean = Vells.mean()                  # complex number
        if error_bars:
          dy = Vells.errorbar()              # real
        label = None
        if corr in annotate:
          label = annot[i]
        grs[igrs][0].append(y=mean, annot=label, dy=dy)
        
    # Finished: Return the modified Graphics object
    return grs



#=====================================================================================
# Classes derived from VisuVis22:
#=====================================================================================


class AllCorrs (VisuVis22):
  """Make a scatter-plot of the means of the results of its children"""

  def __init__ (self, *args, **kwargs):
    VisuVis22.__init__(self,*args);
    return None
                              
  def get_result (self, request, *children):
    """Re-implementation of the VisuVis22 placeholder function"""
    grs = self.on_entry()
    grs = self.read_children(grs, children, corrs=['XX','XY','YX','YY'],
                             annotate=['XX','YY'])
    return self.on_exit(grs)


#=====================================================================================

class CrossCorrs (VisuVis22):
  """Make a scatter-plot of the means of the results of its children"""

  def __init__ (self, *args, **kwargs):
    VisuVis22.__init__(self,*args);
    return None
                              
  def get_result (self, request, *children):
    """Re-implementation of the VisuVis22 placeholder function"""
    grs = self.on_entry()
    grs = self.read_children(grs, children, corrs=['XY','YX'])
    return self.on_exit(grs)


#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================

def corr_index (corr):
  """Convert the given corr (string) into a vells index"""
  if corr in ['XX','RR']:
    return 0
  elif corr in ['XY','RL']:
    return 1
  elif corr in ['YX','LR']:
    return 2
  elif corr in ['YY','LL']:
    return 3
  else:
    raise ValueError,'corr not recognized'
  return None
  
def corr_color (corr):
  """Convert the given corr (string) into a color"""
  if corr in ['XX','RR']:
    return 'red'
  elif corr in ['XY','RL']:
    return 'green'
  elif corr in ['YX','LR']:
    return 'magenta'
  elif corr in ['YY','LL']:
    return 'blue'
  else:
    raise ValueError,'corr not recognized'
  return None
  

def corr_style (corr):
  """Convert the given corr (string) into a plot-marker style"""
  if corr in ['XX','RR']:
    return '+'
  elif corr in ['XY','RL']:
    return 'x'
  elif corr in ['YX','LR']:
    return 'x'
  elif corr in ['YY','LL']:
    return '+'
  else:
    raise ValueError,'corr not recognized'
  return None
  

def corr_Graphics (corr, trace=False):
  """Create a standard Graphics object for the specified correlation.
  This imposes uniformity on the rendering of the various correlations."""
  import Graphics
  grs = Graphics.Scatter(None, name=corr,
                         color=corr_color(corr),
                         style=corr_style(corr),
                         plot_circle_mean=True,
                         markersize=10)
  return grs




#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  cc = []
  
  if True:
    ftx= ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())

    nstat = 5
    rmsa = 0.01
    labels = []
    for i in range(nstat-1):
      for j in range(i+1,nstat):
        label = str(i)+'.'+str(j)
        labels.append(label)
        # print '-- (i,j)=',i,j
        XX = ns.XX(i)(j) << Meq.Polar(random.gauss(1.1,rmsa),
                                      random.gauss(0.0,1.0))
        YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa),
                                      random.gauss(0.0,1.0))
        XY = ns.XY(i)(j) << Meq.Polar(random.gauss(0.1,rmsa),
                                      random.gauss(0.5,0.1))
        YX = ns.YX(i)(j) << Meq.Polar(random.gauss(0.1,rmsa),
                                      random.gauss(-0.5,0.1))
        vis22 = ns.vis22(i)(j) << Meq.Matrix22(XX,XY,YX,YY)
        # vis22 = ns.vis22plus(i)(j) << Meq.Add(vis22, ftx)
        cc.append(vis22)
      
    bookpage = Meow.Bookmarks.Page('pynodes')
    # bookpage.add(ns.cx_freqtime, viewer="Result Plotter")                
    pn = []
    for classname in ['AllCorrs','CrossCorrs']:
    # for classname in ['AllCorrs']:
    # for classname in ['CrossCorrs']:
      pynode = ns[classname] << Meq.PyNode(children=cc,
                                           class_name=classname,
                                           plot_labels=labels,
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
