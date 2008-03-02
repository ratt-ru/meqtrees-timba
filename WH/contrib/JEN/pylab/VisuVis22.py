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


#=====================================================================================
# The VisuVis22 base class:
#=====================================================================================

class VisuVis22 (pynode.PyNode):
  """Make a scatter-plot of the means of the results of its children"""

  def __init__ (self, *args, **kwargs):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution')
    self._count = 0
    self._xmin = None
    self._xmax = None
    self._ymin = None
    self._ymax = None
    return None


  def update_state (self, mystate):
    """Read information from the pynode state record"""
    trace = False
    # trace = True

    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    self._num_children = len(self.child_indices) 

    # Read the plotinfo record:
    mystate('plotinfo')
    self.set_plotinfo_defaults()
    return None

  #-------------------------------------------------------------------

  def set_plotinfo_defaults(self, trace=False):
    """Set default values in self.plotinfo"""
    if trace:
      print '\n** set_plotinfo_defaults (before):',self.plotinfo,'\n'

    rr = self.plotinfo                                 # convenience

    title = 'VisuVis22_'+self.class_name
    title += '_'+str(self._num_children)
    rr.setdefault('corr_names', ['XX','XY','YX','YY']) 
    rr.setdefault('title', title) 
    rr.setdefault('xlabel', 'real part (Jy)') 
    rr.setdefault('ylabel', 'imag part (Jy)') 
    rr.setdefault('labels', self._num_children*[None]) 
    rr.setdefault('iicorr_plot', range(4)) 
    rr.setdefault('iicorr_annotate', range(4)) 
    rr.setdefault('plot_error_bars', False) 

    # Make sure that there is one annotation label per child: 
    if not isinstance(rr.labels,(list,tuple)):
      rr.labels = self._num_children*[None]
    elif not len(rr.labels)==self._num_children:
      rr.labels = self._num_children*[None]

    # Only annotate the specified corrs:
    if rr.iicorr_annotate==True:
      rr.iicorr_annotate = iicorr                      # all
    elif not isinstance(rr.iicorr_annotate,(list,tuple)):
      rr.iicorr_annotate = []                          # none

    if trace:
      print '\n** set_plotinfo_defaults (after):',self.plotinfo,'\n'
    return None

  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Make the pynode result from its children."""
    grs = self.on_entry()
    grs = self.read_children(grs, children)
    return self.on_exit(grs)

  #-------------------------------------------------------------------

  def on_entry(self, trace=False):
    """Called on entry of .get_result()"""
    self._count += 1

    # we need the following two lines
    import matplotlib
    matplotlib.use('SVG')

    # Create a Graphics object:
    import Graphics
    grs = Graphics.Graphics(name=self.class_name,
                            # plot_type='polar',                  # does not work in svg...!
                            title=self.plotinfo.title+'_'+str(1+self._count),
                            xlabel=self.plotinfo.xlabel,
                            ylabel=self.plotinfo.ylabel)
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

  def read_children (self, grs, children, trace=False):
    """Accumulate the point(s) representing the child result(s)"""

    import Graphics
    import ChildResult

    labels = self.plotinfo.labels        
    corr_names = self.plotinfo.corr_names
    iicorr = self.plotinfo.iicorr_plot
    annotate = self.plotinfo.iicorr_annotate
    plot_error_bars = self.plotinfo.plot_error_bars

    # Fill the input Graphics object with an empty Graphics object
    # for each of the 1-4 specified (iicorr) correlations:
    for icorr in iicorr:
      grs.add(Graphics.Scatter(name=corr_names[icorr],
                               color=corr_color(icorr),
                               style=corr_style(icorr),
                               plot_circle_mean=True,
                               # plot_ellipse_stddev=True,
                               markersize=5))
      grs.legend('corr('+corr_names[icorr]+')', color=corr_color(icorr))

    # Read the child results and fill the 1-4 Graphics objects:
    for i,child in enumerate(children):
      chires = ChildResult.Result(child)     # child is MeqResult class
      if trace:
        # chires.display()
        print '--',i,':',chires.oneliner()
      for igrs,icorr in enumerate(iicorr):
        Vells = chires[icorr]
        if trace:
          print '---',i,igrs,icorr,corr_names[icorr],':',Vells.oneliner()
        mean = Vells.mean()                  # complex number
        dy = None
        if plot_error_bars:
          dy = Vells.errorbar()              # real number
        label = None
        if icorr in annotate:
          label = labels[i]
        grs[igrs][0].append(y=mean, annot=label, dy=dy)

    # Fix the window:
    if self._count==1:
      [self._xmin,self._xmax] = grs.xrange(margin=0.5)
      [self._ymin,self._ymax] = grs.yrange(margin=0.5)
      grs.kwupdate(**dict(xmin=self._xmin, xmax=self._xmax,
                          ymin=self._ymin, ymax=self._ymax))
        
    # Finished: Return the modified Graphics object
    return grs






#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================

def corr_color (icorr):
  """Convert the given icorr (integer) into a color"""
  colors = ['red','green','magenta','blue']
  if icorr<0 or icorr>3:
    # raise ValueError,'icorr out of range'
    return 'yellow'
  return colors[icorr]
  

def corr_style (icorr):
  """Convert the given icorr (integer) into a plot-marker style"""
  styles = ['o','o','o','o']
  if icorr<0 or icorr>3:
    # raise ValueError,'icorr out of range'
    return 'x'
  return styles[icorr]
  


#=====================================================================================
# Classes derived from VisuVis22:
#=====================================================================================


class AllCorrs (VisuVis22):
  """Make a scatter-plot of the means of the results of its children"""

  def __init__ (self, *args, **kwargs):
    VisuVis22.__init__(self,*args);
    return None

  def set_plotinfo_defaults(self, trace=True):
    """Set class-specific defaults in self.plotinfo"""
    self.plotinfo.setdefault('iicorr_annotate', [0,3])
    self.plotinfo.setdefault('plot_error_bars', True)
    return VisuVis22.set_plotinfo_defaults(self, trace=trace)
                                                            

#=====================================================================================

class CrossCorrs (VisuVis22):
  """Make a scatter-plot of the means of the results of its children"""

  def __init__ (self, *args, **kwargs):
    VisuVis22.__init__(self, *args);
    return None

  def set_plotinfo_defaults(self, trace=True):
    """Set class-specific defaults in self.plotinfo"""
    self.plotinfo.setdefault('iicorr_plot', [1,2])
    self.plotinfo.setdefault('plot_error_bars', False)
    return VisuVis22.set_plotinfo_defaults(self, trace=trace)
                              



#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  cc = []
  
  if True:
    ftx = ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())
    gsx = ns.cx_gauss << Meq.ToComplex(Meq.GaussNoise(stddev=0.1),
                                       Meq.GaussNoise(stddev=0.1))

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
        if False:
          YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa),
                                        random.gauss(0.0,1.0))
        elif True:
          YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa),
                                        random.gauss(0.0,1.0)+Meq.Freq())
        else:
          YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa)+Meq.Time(),
                                        random.gauss(0.0,1.0)+Meq.Freq())
        XY = ns.XY(i)(j) << Meq.Polar(random.gauss(0.1,rmsa),
                                      random.gauss(0.5,0.1))
        YX = ns.YX(i)(j) << Meq.Polar(random.gauss(0.1,rmsa),
                                      random.gauss(-0.5,0.1))
        vis22 = ns.vis22(i)(j) << Meq.Matrix22(XX,XY,YX,YY)
        # vis22 = ns.vis22plus(i)(j) << Meq.Add(vis22, ftx)
        vis22 = ns.vis22plus(i)(j) << Meq.Add(vis22, gsx)
        cc.append(vis22)

    # The plotinfo record may have title, xlabel, ylabel, etc
    plotinfo = record(labels=labels,
                      corr_names=['aa','ab','ba','bb'])

    # Make a bookpage with auxiliary info:
    auxpage = Meow.Bookmarks.Page('aux')
    auxpage.add(ftx, viewer="Result Plotter")
    auxpage.add(gsx, viewer="Result Plotter")

    # Make the pynode(s):
    bookpage = Meow.Bookmarks.Page('pynodes')
    pn = []
    for classname in ['AllCorrs','CrossCorrs']:
    # for classname in ['AllCorrs']:
    # for classname in ['CrossCorrs']:
      pynode = ns[classname] << Meq.PyNode(children=cc,
                                           class_name=classname,
                                           plotinfo=plotinfo,
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
  nf2 = 10
  nt2 = 5
  q = 0.1
  cells = meq.cells(meq.domain(-nf2*q,nf2*q,-nt2*q,nt2*q),
                    num_freq=2*nf2+1,num_time=2*nt2+1)
  print '\n-- cells =',cells,'\n'
  request = meq.request(cells,rqtype='e1');
  a = mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True


def _tdl_job_sequence (mqs,parent,wait=False):
  from Timba.Meq import meq
  for i in range(10):
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
