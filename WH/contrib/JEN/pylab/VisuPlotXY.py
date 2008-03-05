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
    # trace = True
    
    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    self._num_children = len(self.child_indices)

    # Read the plotinfo record, and set defaults:
    mystate('plotinfo')
    self.set_plotinfo_defaults()
    self.read_plotinfo_subplots()
    return None

  #-------------------------------------------------------------------

  def set_plotinfo_defaults(self, trace=False):
    """Set default values in self.plotinfo.
    This routine may be re-implemented by a derived class."""
    if trace:
      print '\n** set_plotinfo_defaults (before):',self.plotinfo,'\n'

    rr = self.plotinfo                                 # convenience

    title = 'VisuPlotXY_'+self.class_name
    title += '_'+str(self._num_children)
    rr.setdefault('title', self.name) 
    rr.setdefault('xlabel', 'x') 
    rr.setdefault('ylabel', 'y') 
    rr.setdefault('xoffset', 0.0) 
    rr.setdefault('yoffset', 0.0) 
    rr.setdefault('color', 'blue') 
    rr.setdefault('linestyle', None) 
    rr.setdefault('marker', 'o') 
    rr.setdefault('markersize', 5) 
    rr.setdefault('plot_error_bars', False)
    rr.setdefault('labels', self._num_children*[None])

    # The following keys are used in other routines; 
    self._spkeys = ['color','linestyle','marker','markersize']
    self._spkeys.extend(['plot_error_bars'])

    if trace:
      print '\n** set_plotinfo_defaults (after):',self.plotinfo,'\n'
    return None

  #-------------------------------------------------------------------

  def read_plotinfo_subplots(self, trace=False):
    """Transfer the subplot definition(s) from self.plotinfo"""
    rr = self.plotinfo                                 # convenience
    self._subplot = []
    if rr.has_key('subplot'):
      for i,sp in enumerate(rr.subplot):
        if trace:
          print '\n-- subplot:',sp
        sp.setdefault('iix', range(self._num_children)) 
        sp.setdefault('iiy', range(self._num_children)) 
        sp.xoffset = i*rr.xoffset
        sp.yoffset = i*rr.yoffset
        for key in self._spkeys:            
          sp.setdefault(key, rr[key]) 
        sp.setdefault('legend', str(i))
        sp.legend = str(sp.legend)
        if sp.yoffset>0.0:
          sp.legend += ' (+'+str(sp.yoffset)+')'
        elif sp.yoffset<0.0:
          sp.legend += ' ('+str(sp.yoffset)+')'
        if trace:
          for key in sp.keys():
            print '  -',key,':',sp[key]
          print
        self._subplot.append(sp)

    # Make a default subplot if none supplied:
    if len(self._subplot)==0:
      self.make_default_plotinfo_subplot(trace=trace)
    return None

  #-------------------------------------------------------------------

  def make_default_plotinfo_subplot(self, trace=False):
    """If there are no subplots, make a default one from the children.
    This routine may be re-implemented for derived classes"""
    rr = self.plotinfo                         # convenience
    sp = record()                              # empty subplot record
    sp.iix = range(self._num_children/2)       # first half of children
    sp.iiy = range(self._num_children/2, self._num_children) # second half
    for k,iy in enumerate(sp.iiy):
      if rr.labels[iy]==None:
        rr.labels[iy] = k
    sp.xoffset = 0.0
    sp.yoffset = 0.0
    sp.setdefault('legend', 'legend')
    sp.legend = str(sp.legend)
    for key in self._spkeys:
      sp.setdefault(key, rr[key]) 
    if trace:
      for key in sp.keys():
        print '  -',key,':',sp[key]
      print
    self._subplot.append(sp)
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
                            title=self.plotinfo.title+'_'+str(self._count),
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
    for i,rr in enumerate(self._subplot):
      xx = self.read_results(children, rr.iix, offset=rr.xoffset)
      yy = self.read_results(children, rr.iiy, offset=rr.yoffset,
                             error_bars=rr.plot_error_bars)
      labels = self.read_labels(rr.iiy)
      grs1 = Graphics.Scatter(yy=yy, xx=xx, annot=labels,
                              dyy=self._dvv,           
                              linestyle=rr.linestyle,
                              marker=rr.marker,
                              markersize=rr.markersize,
                              color=rr.color)
      grs.add(grs1)
      grs.legend(rr.legend, color=rr.color)
    # Finished:
    return self.on_exit(grs, trace=False)

  #-------------------------------------------------------------------

  def read_labels (self, ii=None, trace=False):
    """Return a vector with a subset (ii) of labels (strings)
    selected from self.plotinfo.labels.
    """
    if trace:
      print '\n** .read_labels(',ii,'):'
    if ii==None:
      ii = range(self._num_children)
    labels = []
    for i in ii:
      labels.append(self.plotinfo.labels[i])
    if trace:
      print '  -> selected labels =',labels,'\n'
    return labels

  #-------------------------------------------------------------------

  def read_results (self, children, ii=None, offset=0.0, 
                    error_bars=True, trace=False):
    """Return a vector of numbers from the results of the specified (ii) children.
    """

    if trace:
      print '\n**',self.name,'.read_results(',ii,'):'

    if ii==None:
      ii = range(self._num_children)

    # Select a vector of child results:
    cc = []
    for i in ii:
      cc.append(children[i])

    # A vector of error-bars
    self._dvv = None
    if error_bars:
      self._dvv = []

    # Read the child results and fill the vector(s):
    import ChildResult
    vv = []                                   # vv is a vector of y-values
    for i in range(len(cc)):
      cr = ChildResult.Result(cc[i])          # cc[i] is MeqResult class
      if trace:
        # cr.display()
        # print '--',i,':',cr.oneliner()
        pass
      Vells = cr[0]
      if trace:
        print '---',i,':',Vells.oneliner()
      vv.append(offset+Vells.mean())
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
    VisuPlotXY.__init__(self, *args);
    return None

  def set_plotinfo_defaults(self, trace=False):
    """Set class-specific defaults in self.plotinfo"""
    return VisuPlotXY.set_plotinfo_defaults(self, trace=trace)
                                                            
  #-------------------------------------------------------------------

  def get_result_notneeded (self, request, *children):
    """Re-implementation of the function in baseclass VisuPlotXY"""
    import Graphics
    grs = self.on_entry()
    # Make separate Graphics/Subplot objects for the various subplots:
    for i,rr in enumerate(self._subplot):
      yy = self.read_results(children, rr.iiy, offset=rr.yoffset,
                             error_bars=rr.plot_error_bars)
      xx = range(len(yy))
      labels = self.read_labels(rr.iiy)
      grs1 = Graphics.Scatter(yy=yy, xx=xx, annot=labels,
                              dyy=self._dvv,
                              linestyle=rr.linestyle,
                              marker=rr.marker,
                              markersize=rr.markersize,
                              color=rr.color)
      grs.add(grs1)
      grs.legend(rr.legend, color=rr.color)
    # Finished
    return self.on_exit(grs, trace=False)


  #-------------------------------------------------------------------

  def get_result_base (self, request, *children):
    """Placeholder, to be re-implemented in derived classes"""
    import Graphics
    grs = self.on_entry()
    # Make separate Graphics/Subplot objects for the various subplots:
    for i,rr in enumerate(self._subplot):
      xx = self.read_results(children, rr.iix, offset=rr.xoffset)
      yy = self.read_results(children, rr.iiy, offset=rr.yoffset,
                             error_bars=rr.plot_error_bars)
      labels = self.read_labels(rr.iiy)
      grs1 = Graphics.Scatter(yy=yy, xx=xx, annot=labels,
                              dyy=self._dvv,           
                              linestyle=rr.linestyle,
                              marker=rr.marker,
                              markersize=rr.markersize,
                              color=rr.color)
      grs.add(grs1)
      grs.legend(rr.legend, color=rr.color)
    # Finished:
    return self.on_exit(grs, trace=False)




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
  classnames = dict()

  ftx= ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())
  ft= ns.freqtime << Meq.Add(Meq.Time(),Meq.Freq())
  gsx = ns.cx_gauss << Meq.ToComplex(Meq.GaussNoise(stddev=0.1),
                                     Meq.GaussNoise(stddev=0.1))
  gs = ns.gauss << Meq.GaussNoise(stddev=0.5)
  
  if True:
    classname = 'VisuPlotXY'
    name = classname+'m'              # minimal VisuPlotXY
    cc = []
    yy = []
    yname = 'y1m'
    xname = 'x1m'
    n = 5
    for i in range(n):
      x = ns[xname](i) << random.gauss(i,0.5)
      cc.append(x)
      y = ns[yname](i) << (gs + random.gauss(i,0.5))
      yy.append(y)
    cc.extend(yy)
    rr[name] = record(title=name)
    classnames[name] = classname
    children[name] = cc


  if True:
    classname = 'VisuPlotXY'
    name = classname
    cc = []
    labels = []
    rr[name] = record(title=name, xlabel='x', ylabel='y',
                      yoffset=-2.0, subplot=[])
    colors = ['blue','magenta','cyan']
    for k in range(3):
      iix = []
      iiy = []
      yname = 'y1_'+str(k)
      xname = 'x1_'+str(k)
      for i in range(5):
        x = ns[xname](i) << random.gauss(i,0.3)
        # y = ns[yname](i) << random.gauss(i,0.5)
        y = ns[yname](i) << (gs + random.gauss(i,0.5))
        cc.append(x)
        labels.append(x.name)   
        iix.append(len(cc)-1)
        cc.append(y)
        labels.append(y.name)   
        iiy.append(len(cc)-1)
      rr[name].subplot.append(record(iix=iix, iiy=iiy, color=colors[k]))
    classnames[name] = classname
    rr[name].labels = labels
    children[name] = cc

      
  if True:
    classname = 'VisuPlotY'
    name = classname
    cc = []
    labels = []
    rr[name] = record(title=name, ylabel='y', labels=None,
                      yoffset=2.0, subplot=[])
    colors = ['blue','magenta','cyan']
    for k in range(2):
      yname = 'y2_'+str(k)
      iiy = []
      for i in range(6):
        y = ns[yname](i) << (gs + random.gauss(i,0.5))
        cc.append(y)
        iiy.append(len(cc)-1)
        labels.append(y.name)   
      rr[name].subplot.append(record(iiy=iiy, color=colors[k], legend=k))
    classnames[name] = classname
    rr[name].labels = labels
    children[name] = cc
      


  # Make a bookpage with auxiliary info:
  auxpage = Meow.Bookmarks.Page('aux')
  auxpage.add(ftx, viewer="Result Plotter")
  auxpage.add(ft, viewer="Result Plotter")
  auxpage.add(gsx, viewer="Result Plotter")
  auxpage.add(gs, viewer="Result Plotter")
      
  # Make the pynode(s):
  bookpage = Meow.Bookmarks.Page('pynodes')
  pn = []
  for name in rr.keys():
    print '\n** make_pynode: rr[',name,'] =',rr[name],'\n'
    pynode = ns[name] << Meq.PyNode(children=children[name],
                                    class_name=classnames[name],
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
  nf2 = 10
  nt2 = 5
  cells = meq.cells(meq.domain(-nf2,nf2,-nt2,nt2),
                    num_freq=2*nf2+1,num_time=2*nt2+1);
  print '\n-- cells =',cells,'\n'
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
