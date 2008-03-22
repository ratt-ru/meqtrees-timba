# file: ../contrib/JEN/pylab/PyPlot.py

# Author: J.E.Noordam
# 
# Short description:
#   Various pyNode classes to make arbitrary xy-plots from child results
#
# History:
#    - 21 mar 2008: creation (from VisuPlotXY.py)
#
# Remarks:
#
# Description:
#   The PyPlot class actually makes the (SVG) plot from a list of
#   subplots in its plotinfo record. The subplots are a concatenation
#   if the subplots defined in the plotinfo records of its children.
#   Its children are PyNodes that collect values from node-results
#   in various ways and turn them into subplots.
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
# import pylab


Settings.forest_state.cache_policy = 100;


#=====================================================================================
# The PyPlot base class:
#=====================================================================================

class PyPlot (pynode.PyNode):
  """Make an plot of the results of its children"""

  def __init__ (self, *args, **kwargs):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution')
    self._count = -1
    return None


  def update_state (self, mystate):
    """Read information from the pynode state record. This is called
    when the node is first created and a full state record is available.
    But also when state changes, and only a partial state record is
    supplied....
    Instead of the state record, we  receive a clever object (mystate)
    which encapsulates the state record with some additional semantics.
    """

    trace = False
    # trace = True
    
    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    # print '** self.child_indices =',self.child_indices
    if not isinstance(self.child_indices,(list,tuple)):
      self.child_indices = [self.child_indices]
    self._num_children = len(self.child_indices)

    # NB: This number still includes the PyPlot children,
    #     which are used for concatenating plots.
    #     In any case the number is greater or equal to the
    #     number of 'regular' (plottable) children, which is
    #     OK for the generation of lists of plot-specifications....

    # Read the plotinfo record, and check it:
    mystate('plotinfo')
    self.check_plotinfo(trace=trace)
    return None

  #-------------------------------------------------------------------

  def show_plotinfo (self, txt=None, full=False, plotinfo=None):
    """Helper function to show the contents of self.plotinfo"""

    print '\n** PyPlot: self.plotinfo record (',txt,'):'

    if plotinfo:               # plotinfo record externally provided
      rr = plotinfo
    else:                      # use the internal one
      rr = self.plotinfo       

    # First the overall fields:
    for key in rr.keys():
      if key=='subplot':
        print ' - ',key,':',type(rr[key]),len(rr[key])
      else:
        print ' - ',key,'=',rr[key]
        
    # Then the subplot definitions:
    if rr.has_key('subplot'):
      for i,sp in enumerate(rr.subplot):
        self.show_subplot(sp)
    print
    return True

  #-------------------------------------------------------------------

  def show_subplot (self, sp, txt=None, full=False):
    """Helper function to show the contents of a subplot definition"""
    print ' - subplot definition (',txt,'):'
    for key in sp.keys():
      if key in ['xx','yy','dxx','dyy']:
        print '   - ',key,':',format_vv(sp[key])
      else:
        print '   - ',key,'=',sp[key]
    return True

  #-------------------------------------------------------------------

  def check_and_append_subplot(self, sp, trace=True):
    """Check the integrity of the given subplot definition,
    and append it to self.plotinfo.
    """

    if not sp.offset==0.0:
      sp.legend = str(sp.legend)
      if sp.offset>0.0:
        sp.legend += ' (+'+str(sp.offset)+')'
      elif sp.offset<0.0:
        sp.legend += ' ('+str(sp.offset)+')'

    if trace:
      print '\n** .append_subplot():'
      for key in sp.keys():
        print '  -',key,'=',sp[key]
      print

    # Append the valid subplot definition:
    if True:
      self.plotinfo.subplot.append(sp)
    return None


  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Required pyNode function."""

    trace = False
    trace = True
    
    self._count += 1

    # There are two classes of children:
    # - Those that are derived from PyPlot have a plotinfo field
    #   in their result. Its subplot definitions are appended to
    #   the local self.plotinfo.subplot list.
    # - The others are 'regular' children whose results are made
    #   into subplot definitions, which are appended to the
    #   local self.plotinfo.subplot list.
    # Thus, nodes derived from PyPlot may be concatenated to produce
    # complicated plots. But they can also be used by themselves.
    
    cc = []
    for c in children:
      if c.has_key('plotinfo'):
        # Copy the subplot definitions:
        for sp in c['plotinfo'].subplot:
          self.plotinfo.subplot.append(sp)
      else:
        # Append to the list of 'regular' children.
        cc.append(c)

    # Adjust the number of regular children:
    # self._num_children = len(cc)                    # ....!!              
    
    # Make subplots from its 'regular' children (if any),
    # and append them to the list self.plotinfo.subplot:
    if len(cc)>0:
      self.define_subplots(cc, trace=trace)

    # make an empty result record
    result = meq.result()

    # Optionally, make a plot:
    if not self.plotinfo.inhibit_svg:
      svg_list_of_strings = self.make_svg(trace=trace)
      result.svg_plot = svg_list_of_strings

    # Always attach the current plotinfo
    result.plotinfo = self.plotinfo
    
    # Finished:
    return result

  #-------------------------------------------------------------------

  def make_svg (self, trace=False):
    """Make an svg plot definition from the self.plotinfo.subplot definitions.
    """
    import Graphics
    import matplotlib
    matplotlib.use('SVG')
      
    # Create an empty Graphics object:
    grs = Graphics.Graphics(name=self.class_name,
                            # plot_type='polar',     # does not work in svg...!
                            plot_grid=True,
                            title=self.plotinfo.title+'_'+str(self._count),
                            xlabel=self.plotinfo.xlabel,
                            ylabel=self.plotinfo.ylabel)

    # Fill it with the subplots:
    for i,sp in enumerate(self.plotinfo.subplot):
      grs1 = Graphics.Scatter(yy=sp.yy, xx=sp.xx,
                              annot=sp.labels,
                              dyy=sp.dyy, dxx=sp.dxx,           
                              linestyle=sp.linestyle,
                              marker=sp.marker,
                              markersize=sp.markersize,
                              color=sp.color)
      grs.add(grs1)
      grs.legend(sp.legend, color=sp.color)

    if trace:
      grs.display('make_svg()')

    # Use the Figure class to make a pylab plot,
    # and to generate an svg definition string:
    import Figure
    fig = Figure.Figure()
    fig.add(grs)
    if trace:
      fig.display('make_svg()')
    svg_list_of_strings = fig.plot(dispose=['svg'],
                                   rootname=self.class_name,
                                   clear=False, trace=trace)
    # Finished:
    return svg_list_of_strings



  #-------------------------------------------------------------------
  # Re-implementable functions (for derived classes)
  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    Any re-implementation by derived classes should call this one too.
    """

    if trace:
      self.show_plotinfo('check_plotinfo() input')

    rr = self.plotinfo                                # convenience
    rr.setdefault('subplot',[])                       # subplot definitions 
    
    rr.setdefault('inhibit_svg', False)               # If True, do not make SVG plot

    title = 'PyPlot_'+self.class_name
    title += '_'+str(self._num_children)
    rr.setdefault('title', self.name) 
    rr.setdefault('xlabel', 'child') 
    rr.setdefault('ylabel', 'result') 

    # There must be as many labels as children:
    rr.setdefault('labels', self._num_children*[None]) 
    if not isinstance(rr['labels'], (list,tuple)):
      rr['labels'] = self._num_children*[None]
    elif not len(rr['labels'])==self._num_children:
      rr['labels'] = self._num_children*[None]

    # Subplot parameters (see self._spkeys): 
    # The keys are used to transfer information to subplot definitions:
    self._spkeys = ['color','linestyle','marker','markersize']
    self._spkeys.extend(['plot_error_bars','annotate'])
    self._spkeys.extend(['offset','legend'])
    self._spkeys.extend(['vlabels','index','xindex','yindex'])

    rr.setdefault('legend', [None])                   # subplot legend
    rr.setdefault('offset', [0.0])                    # optional v-offset
    rr.setdefault('xindex', [None])                   # index of x-coord Vells
    rr.setdefault('yindex', [None])                   # index of y-coord Vells
    rr.setdefault('index', [0])                       # index(es) of value Vells 
    rr.setdefault('vlabels', [None])                  # Vells label(s) 
    rr.setdefault('color', ['blue'])                  # Vells plot color(s)
    rr.setdefault('linestyle', [None])                # Vells plot line style(s)                  
    rr.setdefault('marker', ['o'])                    # Vells plot marker style(s)
    rr.setdefault('markersize', [5])                  # Vells plot markersize(s)
    rr.setdefault('annotate', [True])                 # Vells plot annotation(s)
    rr.setdefault('plot_error_bars', [True])          # Vells plot error-bar(s)

    # Make sure that all the suplot parameters are lists:
    for key in self._spkeys:
      if not isinstance(rr[key],(list,tuple)):     
        rr[key] = [rr[key]]                  

    if trace:
      self.show_plotinfo('check_plotinfo() checked')
    return None


  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """Define one or more subplot record(s) from self.plotinfo,
    and fill it with values read from the pyNode children.
    - If no labels, or len(labels)!=len(children), use implicit x (0,1,2,...)
    - If labels are present:
    --- x-child: label==None
    --- y-child: label is anything else (e.g. str or float) -> str
    Append the subplot(s) to the list self.plotinfo.subplot.
    This function will be re-implemented by derived classes.
    """
    
    rr = self.plotinfo                         # convenience

    # Create an empty subplot record, and initialize it:
    sp = record()
    for key in self._spkeys:                   # transfer standard fields
      print '-',key,'=',rr[key]
      sp[key] = rr[key][0]                     # the 1st element of each list

    import ChildResult
    rv = ChildResult.ResultVector(children,
                                  labels=self.plotinfo.labels,
                                  # select=sp.iiv, index=sp.index,
                                  offset=sp.offset)
    # rv.display(self.class_name)
    dyy = None
    sp.yy = rv.vv()
    sp.dyy = None
    if sp.plot_error_bars:
      sp.dyy = rv.dvv()
    sp.xx = rv.xx()
    sp.dxx = None
    sp.labels = rv.labels()

    # Check and append the subplot definition:
    self.check_and_append_subplot(sp)
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None








#=====================================================================================
# Classes derived from PyPlot:
#=====================================================================================

class PyPlotTensorVells (pynode.PyNode):
  """Class derived from PyPlot."""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """Define one or more subplot record(s) from self.plotinfo,
    and fill it with values read from the pyNode children.
    Assume that its children are tensor nodes of the same kind,
    i.e. each with the same number of Vells.
    Make separate subplots for each of the Vells.
    """
    
    rr = self.plotinfo                         # convenience

    # Create an empty subplot record, and initialize it:
    sp = record()
    for key in self._spkeys:                   # transfer standard fields
      print '-',key,'=',rr[key]
      sp[key] = rr[key][0]                     # the 1st element of each list

    import ChildResult
    rv = ChildResult.ResultVector(children,
                                  labels=self.plotinfo.labels,
                                  # select=sp.iiv, index=sp.index,
                                  offset=sp.offset)
    # rv.display(self.class_name)
    dyy = None
    sp.yy = rv.vv()
    sp.dyy = None
    if sp.plot_error_bars:
      sp.dyy = rv.dvv()
    sp.xx = rv.xx()
    sp.dxx = None
    sp.labels = rv.labels()

    # Check and append the subplot definition:
    self.check_and_append_subplot(sp)
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None







#=====================================================================================
# Helper function(s): (May be called from other modules)
#=====================================================================================


def format_float(v, name=None, n=2):
  """Helper function to format a float for printing"""
  if isinstance(v, complex):
     s1 = format_float(v.real)
     s2 = format_float(v.imag)
     s = '('+s1+'+'+s2+'j)'
  else:
     q = 100.0
     v1 = int(v*q)/q
     s = str(v1)
  if isinstance(name,str):
    s = name+'='+s
  # print '** format_float(',v,name,n,') ->',s
  return s

#-----------------------------------------------------------

def format_vv (vv):
  if not isinstance(vv,(list,tuple)):
    return str(vv)
  elif len(vv)==0:
    return 'empty'
  import pylab              # must be done here, not above....
  ww = pylab.array(vv)
  # print '\n** ww =',type(ww),ww
  s = '  length='+str(len(ww))
  s += format_float(ww.min(),'  min')
  s += format_float(ww.max(),'  max')
  s += format_float(ww.mean(),'  mean')
  s += format_float(ww.stddev(),'  stddev')
  return s



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
  
  if False:
    classname = 'PyPlot'
    name = classname+'p'              # pairs PyPlot
    cc = []
    labels = []
    yname = 'y1p'
    xname = 'x1p'
    n = 5
    for i in range(n):
      y = ns[yname](i) << (gs + random.gauss(i,0.5))
      x = ns[xname](i) << (gs + random.gauss(i,0.3))
      xy = ns.pair(i) << Meq.Composer(x,y)
      cc.append(xy)
      labels.append('pair_'+str(i))    
    rr[name] = record(title=name, labels=labels, xindex=0)
    classnames[name] = classname
    children[name] = cc


  if False:
    classname = 'PyPlot'
    name = classname+'m'              # minimal PyPlot
    cc = []
    labels = []
    yname = 'y1m'
    xname = 'x1m'
    n = 5
    for i in range(n):
      y = ns[yname](i) << (gs + random.gauss(i,0.5))
      cc.append(y)
      labels.append('y_'+str(i))        # <---!
    for i in range(n):
      if True:
        x = ns[xname](i) << random.gauss(i,0.3)
        cc.append(x)
        labels.append(None)             # <---!
    rr[name] = record(title=name, labels=labels)
    classnames[name] = classname
    children[name] = cc


  if False:
    classname = 'PyPlot'
    name = classname
    cc = []
    labels = []
    rr[name] = record(title=name, xlabel='x', ylabel='y',
                      offset=-2.0, subplot=[])
    colors = ['blue','magenta','cyan']
    for k in range(3):
      iix = []
      iiv = []
      yname = 'y1_'+str(k)
      xname = 'x1_'+str(k)
      for i in range(2):
        x = ns[xname](i) << random.gauss(i,0.3)
        # y = ns[yname](i) << random.gauss(i,0.5)
        y = ns[yname](i) << (gs + random.gauss(i,0.5))
        cc.append(x)
        labels.append(x.name)   
        iix.append(len(cc)-1)
        cc.append(y)
        labels.append(y.name)   
        iiv.append(len(cc)-1)
      rr[name].subplot.append(record(iix=iix, iiv=iiv, color=colors[k]))
    classnames[name] = classname
    rr[name].labels = labels
    children[name] = cc

  #-----------------------------------------------------------------------
      
  if True:
    classname = 'PyPlot'
    name = classname
    cc = []
    labels = []
    for k in range(2):
      yname = 'y2_'+str(k)
      for i in range(2):
        ee = []
        for j in range(3):
          y = ns[yname](i)(j) << (gs + random.gauss(i,0.5))
          ee.append(y)
        c = ns[yname](i) << Meq.Composer(*ee)
        cc.append(c)
        labels.append(y.name)   
    classnames[name] = classname
    rr[name] = record(title=name, labels=labels, offset=-2.0, color='green')
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

  # Make a root node:
  if False:
    ns.rootnode << Meq.Composer(*pn)
  else:
    plotinfo = record(inhibit_svg=False, title='combined')
    ns.rootnode << Meq.PyNode(children=pn,
                              plotinfo=plotinfo,
                              class_name='PyPlot',
                              module_name=__file__)
    bookpage.add(ns.rootnode, viewer="Svg Plotter")

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
