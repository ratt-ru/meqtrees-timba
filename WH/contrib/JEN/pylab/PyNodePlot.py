# file: ../contrib/JEN/pylab/PyNodePlot.py

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
#   The PyNodePlot class actually makes the (SVG) plot from a list of
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
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

# from Timba import pynode
import PyNodeNamedGroups

import inspect
import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;


#=====================================================================================
# The PyNodePlot base class:
#=====================================================================================

class PyNodePlot (PyNodeNamedGroups.PyNodeNamedGroups):
  """Make an plot of the results of its children"""

  def __init__ (self, *args, **kwargs):
    PyNodeNamedGroups.PyNodeNamedGroups.__init__(self,*args);
    # self.set_symdeps('domain','resolution')
    # self._count = -1
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base class for an entire zoo of plotting pyNodes.
    Itself derived from the class PyNodeNamedGroups, which
    takes care of reading the results of its children.
    Its central function is .define_subplots(), which is usually
    reimplemented by derived classes. It defines one or more subplots,
    i.e. makes one or more subplot definition records in the list
    self.plotinfo.subplot. These are used in various ways:
    - The subplots are converted into a SVG list (of strings),
    which is attached to the pyNode result as svg_string. It is
    used by the 'svg plotter' to make a (clumsy) plot.
    - The subplot definition records are also attached to the
    pyNode result. If the parent is also derived from PyNodePlot,
    it will append these subplots to its won new subplots.
    This allows the building of complicated plots by concatenation.
    A PyNodePlot node recognises PyNodePlot children from the plotinfo record
    in its result, and will ignore them for its normal function.
    
    When defining a PyNodePlot node, specific instructions are passed to it
    via a record named plotinfo:
    ns.plot << Meq.PyNode(class_name='PyNodePlotXY', module_name=__file__,
    plotinfo=record(title=..., xlabel=...)

    Possible keywords are (base class defaults in []):
    - labels     [=None]         a list of node labels
    - annotate   [=True]         if True, annotate points with labels
    - make_plot  [=True]         plotting may be inhibited if concatenated
    - offset     [=0.0]          concatenated plots maye be offset vertically
    - title      [=<classname>]  plot title
    - xlabel     [='child']      x-axis label
    - ylabel     [='result']     y-axis label

    - xindex     [=0]            Vells index of x-coordinate
    - yindex     [=1]            Vells index of y-coordinate

    - legend     [=None]         subplot legend string
    - color      [='blue']       subplot color
    - linestyle  [=None]         subplot linestyle ('-','--',':')
    - marker     [='o']          subplot marker style ('+','x', ...)
    - markersize [=5]            subplot marker size (points)
    - plot_sigma_bars [=True]    if True, indicate domain variation

    - msmin      [=2]            min marker size (z-values)
    - msmax      [=20]           max marker size (z-values)
    - plot_circle_mean [=False]  if True, plot a circle (0,0,rmean)
    
    The .define_subplots() function of this baseclass is quite general
    and robust: it may be used to plot the resuts of a list of arbitrary
    child-nodes. It defines a single subplot of all the Vells of all its
    children: 
    - The horizontal axis is child-number (0,1,2,...,n-1).
    - Multiple Vells of the same node have the same x-coordinate.
    - The vertical axis is the mean over the domain (complex?).
    """
    ss = self.attach_help(ss, PyNodePlot.help.__doc__, classname='PyNodePlot',
                          level=level, mode=mode)
    return ss

  #--------------------------------------------------------------------

  def oneliner(self):
    ss = PyNodeNamedGroups.PyNodeNamedGroups.oneliner()
    ss += ' <more from PyNodePlot>...'
    return ss

  def display(self, txt, full=False, level=0):
    PyNodeNamedGroups.PyNodeNamedGroups.display(self, txt, full=full)
    print '  ',self.oneliner()
    print ' <more from PyNodePlot>...'
    print
    return True

  #-------------------------------------------------------------------
    
  def update_state (self, mystate):
    """Read information from the pynode state record. This is called
    when the node is first created and a full state record is available.
    But also when state changes, and only a partial state record is
    supplied....
    Instead of the state record, we  receive a clever object (mystate)
    which encapsulates the state record with some additional semantics.
    """

    trace = False
    trace = True

    PyNodeNamedGroups.PyNodeNamedGroups.update_state(self, mystate)

    # Read the plotinfo record, and check it:
    mystate('plotinfo')
    self.check_plotinfo(trace=trace)
    return None

  #-------------------------------------------------------------------

  def getval (self, vv, index=0, trace=False):
    """Helper function to get the specified (index) element from vv.
    """
    if not isinstance(vv,(list,tuple)):
      v = vv                            # e.g. 'blue'
    elif index>=len(vv) or index<0:     # out of range
      v = vv[0]                         #  always return a value
    else:
      v = vv[index]                     # ok
    if trace:
      print ' - getval(',vv,index,') ->',v
    return v


  #-------------------------------------------------------------------

  def show_plotinfo (self, txt=None, full=False, plotinfo=None):
    """Helper function to show the contents of self.plotinfo"""

    print '\n** PyNodePlot: self.plotinfo record (',txt,'):'
    print ' *',type(self),self.class_name,self.name
    print ' *',self._num_children,self.child_indices

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
      if key in ['xx','yy','zz','dxx','dyy','dzz']:
        print '   - ',key,': (LIST)',format_vv(sp[key])
      else:
        print '   - ',key,'=',sp[key]
    return True

  #-------------------------------------------------------------------

  def zz2markersize(self, sp, trace=False):
    """Helper function to translate the values sp.zz in the given subplot
    definition into a vector of integer values sp.markersize, between the
    specified (plotinfo) miniumum and maximum sizes (in points)
    """
    rr = self.plotinfo             # convenience, contains msmin and msmax
    sp.zmin = min(sp.zz)
    sp.zmax = max(sp.zz)
    sp.legend = 'z-range=['+format_float(sp.zmin)+', '+format_float(sp.zmax)+']'
    q = (rr.msmax-rr.msmin)/(sp.zmax-sp.zmin)
    ms = []
    for i,z in enumerate(sp.zz):
      ms.append(int(rr.msmin+q*(z-sp.zmin)))
    sp.markersize = ms
    return True

  #-------------------------------------------------------------------

  def check_and_append_subplot(self, sp, trace=False):
    """Check the integrity of the given subplot definition,
    and append it to self.plotinfo.subplot.
    """
    trace = True

    # Make sure of some fields:
    sp.setdefault('dxx',None)
    sp.setdefault('dyy',None)

    # Add some fields with statistics:
    import pylab
    yy = pylab.array(sp.yy)
    if len(yy)>0:
      sp.min = yy.min()
      sp.max = yy.max()
      sp.mean = yy.mean()
      sp.stddev = 0.0
      if len(yy)>1:
        if not isinstance(yy[0],complex):
          sp.stddev = yy.stddev()       
    
    if trace:
      self.show_subplot(sp, '.append_subplot()')
      print

    # Append the valid subplot definition:
    if True:
      self.plotinfo.subplot.append(sp)
    return None


  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """Required pyNode function."""

    trace = False
    # trace = True
    
    self._count += 1

    # Fill self._namedgroups with named groups from its children.
    # These are also attached to the result, for concatenation.
    result = PyNodeNamedGroups.PyNodeNamedGroups(self, request, *children)

    # There are two classes of children:
    # - Those that are derived from PyNodePlot have a plotinfo field
    #   in their result. Its subplot definitions are appended to
    #   the local self.plotinfo.subplot list.
    # - The others are 'regular' children whose results are used
    #   to make named groups (see PyNodeNamedGroups.py)
    # Nodes derived from PyNodePlot may be concatenated to produce
    # complicated plots. But they can also be used by themselves.

    # First copy the concatenable subplot definitions:
    self.plotinfo.subplot = [] 
    for c in children:
      if c.has_key('plotinfo'):
        # Copy the subplot definitions:
        for sp in c['plotinfo'].subplot:
          self.plotinfo.subplot.append(sp)
    
    # Make new subplot definition records from the available
    # named groups, as specified .
    # Append them to the list self.plotinfo.subplot:
    self.define_subplots(trace=trace)

    # Optionally, generate info for the "svg plotter":
    result.svg_plot = None
    if self.plotinfo.make_plot:
      svg_list_of_strings = self.make_svg(trace=trace)
      result.svg_plot = svg_list_of_strings

    # Always attach the subplots (etc) of the current plotinfo
    rr = record(subplot=self.plotinfo.subplot)
    for key in self._ovkeys:
      rr[key] = self.plotinfo[key]
    result.plotinfo = rr

    # Finished:
    return result

  #-------------------------------------------------------------------

  def make_svg (self, trace=False):
    """Make an svg plot definition from the self.plotinfo.subplot definitions.
    """
    import Graphics
    import matplotlib
    matplotlib.use('SVG')
    rr = self.plotinfo                              # convenience
    # trace = True
      
    # Create an empty Graphics object:
    grs = Graphics.Graphics(name=self.class_name,
                            # plot_type='polar',     # does not work in svg...!
                            plot_grid=True,
                            title=rr.title+'_'+str(self._count),
                            xlabel=rr.xlabel,
                            ylabel=rr.ylabel)

    # Fill it with the subplots:
    for i,sp in enumerate(rr.subplot):
      offset = i*rr.offset
      # offset += -10                    # testing only
      yy = sp.yy
      if not offset==0.0:
        yy = list(yy)                    # tuple does not support item assignment...      
        for i,y in enumerate(yy):
          yy[i] += offset
      labels = len(yy)*[None]
      if sp.annotate:
        labels = sp.labels
      grs1 = Graphics.Scatter(yy=yy, xx=sp.xx,
                              annot=labels,
                              dyy=sp.dyy, dxx=sp.dxx,           
                              linestyle=sp.linestyle,
                              marker=sp.marker,
                              markersize=sp.markersize,
                              plot_circle_mean=sp.plot_circle_mean,
                              color=sp.color)
      grs.add(grs1)
      legend = sp.legend
      if not offset==0.0:
        if legend==None: legend = 'offset'
        if not isinstance(legend,str): legend = str(legend)
        if offset>0.0: legend += ' (+'+str(offset)+')'
        if offset<0.0: legend += ' ('+str(offset)+')'
      grs.legend(legend, color=sp.color)

    # Optionally, set the plot-window:
    if False:
      self.set_window(grs)

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


#--------------------------------------------------------------------

  def set_window(self, grs, trace=False):
    """Set the plot window"""

    margin = 0.1
    [xmin, xmax] = grs.xrange(margin=margin, trace=trace)
    [ymin, ymax] = grs.yrange(margin=margin, trace=trace)

    if trace:
      print '\n**',type(self),'.set_window():',self._count
      print '  [xmin,xmax] =',[xmin,xmax]
      print '  [ymin,ymax] =',[ymin,ymax]
    # return None

    q = 0.2                                # dampening factor
    if self._count==0:
      # First time: Get the general size
      self._xmin = xmin
      self._xmax = xmax
      self._ymin = ymin
      self._ymax = ymax
    else:
      self._xmin += (xmin - self._xmin)*q
      self._xmax += (xmax - self._xmax)*q
      self._ymin += (ymin - self._ymin)*q
      self._ymax += (ymax - self._ymax)*q

    if trace:
        print '  [dxmin,dxmax] =',[(xmin-self._xmin)*q,(xmax-self._xmax)*q]
        print '  [dymin,dymax] =',[(ymin-self._ymin)*q,(ymax-self._ymax)*q]

    # Update the Subplot (grs) window:
    if True:
      grs.kwupdate(**dict(xmin=self._xmin, xmax=self._xmax,
                          ymin=self._ymin, ymax=self._ymax))
    return None



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

    # Some node control parameters:
    rr.setdefault('make_plot', True)                  # if True, make the plot
    rr.setdefault('offset', 0.0)                      # offset multiple subplots

    # There must be as many labels as 'value-nodes'
    # (i.e. no labels are needed for x-coordinate nodes etc)
    # If no labels are specified, it is safe to have a list
    # of None-values for all the children....
    rr.setdefault('labels', self._num_children*[None]) 
    if not isinstance(rr['labels'], (list,tuple)):
      rr['labels'] = self._num_children*[None]

    # Overall parameters 
    # These keys are used to transfer fields to the node result:
    self._ovkeys = ['title','xlabel','ylabel']
    self._ovkeys.extend(['xunit','yunit'])

    title = 'PyNodePlot_'+self.class_name
    title += '_'+str(self._num_children)
    rr.setdefault('title', self.name) 
    rr.setdefault('xlabel', 'child') 
    rr.setdefault('ylabel', 'result') 
    rr.setdefault('xunit', None) 
    rr.setdefault('yunit', None) 
    rr.setdefault('xindex', 0)                      # index of x-coordinate Vells 
    rr.setdefault('yindex', 1)                      # index of y-coordinate Vells  
    rr.setdefault('zindex', 2)                      # index of z-coordinate Vells  

    # Subplot parameters: 
    # These keys are used to transfer information to subplot definitions:
    self._spkeys = ['color','linestyle','marker','markersize']
    self._spkeys.extend(['legend','plot_sigma_bars','annotate'])
    self._spkeys.extend(['plot_circle_mean'])

    rr.setdefault('subplot',[])                     # subplot definitions 
    rr.setdefault('legend', None)                   # subplot legend
    rr.setdefault('color', 'blue')                  # plot color
    rr.setdefault('linestyle', None)                # line style                  
    rr.setdefault('marker', 'o')                    # marker style
    rr.setdefault('markersize', 5)                  # markersize
    rr.setdefault('msmin',2)                        # min marker size (zmin)
    rr.setdefault('msmax',20)                       # max marker size (zmax)
    rr.setdefault('annotate', True)                 # do annotation
    rr.setdefault('plot_sigma_bars', True)          # plot error-bars
    rr.setdefault('plot_circle_mean', False)         # plot circle around (0,0) with radius=mean

    if trace:
      self.show_plotinfo('check_plotinfo() checked')
    return None


  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    # trace = True
    if trace:
      print '\n** .define_subplots():'

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children,
                                  extend_labels=True,
                                  labels=rr.labels)
    if trace:
      rv.display(self.class_name)

    # Create an empty subplot definition record, and initialize it:
    sp = record()
    for key in self._spkeys:
      sp[key] = rr[key]

    # Fill in the data from the child result(s):
    sp.yy = rv.vv()
    sp.dyy = None
    if sp.plot_sigma_bars:
      sp.dyy = rv.dvv()
    sp.xx = rv.xx()
    sp.dxx = None
    sp.labels = rv.labels()

    # Check and append the subplot definition:
    self.check_and_append_subplot(sp, trace=trace)
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None




#=====================================================================================
#=====================================================================================
#=====================================================================================
# Classes derived from PyNodePlot:
#=====================================================================================
#=====================================================================================
#=====================================================================================


class PyNodePlotTensorVells (PyNodePlot):
  """Class derived from PyNodePlot."""

  def __init__ (self, *args, **kwargs):
    PyNodePlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Define one or more subplot record(s).
    Assume that its children are tensor nodes of the same kind,
    i.e. each with the same number of Vells.
    Make separate subplots for each of the Vells.
    Parameters like color, marker, markersize, etc may be lists,
    with different values for each subplot.
    """
    ss = self.attach_help(ss, PyNodePlotTensorVells.help.__doc__,
                          classname='PyNodePlotTensorVells',
                          level=level, mode=mode)
    return PyNodePlot.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    # trace = True

    rr = self.plotinfo                                # convenience

    rr.setdefault('index', '*')                       # indices of Vells to be plotted
    rr.setdefault('xindex', None)                     # index of x-coord Vells
    rr.setdefault('yindex', None)                     # index of y-coord Vells
    
    # First do the generic checks (mandatory!) 
    PyNodePlot.check_plotinfo(self, trace=trace)
    return None


  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    # trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children, labels=rr.labels,
                                  extend_labels=False,
                                  xindex=rr.xindex,
                                  yindex=rr.yindex)
    if trace:
      rv.display(self.class_name)

    # The Vells to be plotted are specified by rr.index:
    nvells = rv[0].len()                       # nr of Vells in 1st (!) child
    if rr.index=='*':
      rr.index = range(nvells)      
    elif isinstance(rr.index, int):
      rr.index = [rr.index]

    # Make separate suplot definitions for each Vells:
    for index in rr.index:
      if index<0 or index>=nvells:
        pass                                   # out of range
      elif index==rr.xindex:
        pass                                   # x-coord Vells: ignore
      elif index==rr.yindex:
        pass                                   # y-coord Vells: ignore
      else:
        sp = record()
        for key in self._spkeys:               # transfer standard fields
          sp[key] = self.getval(rr[key], index=index, trace=trace)  
        sp.yy = rv.vv(index=index)
        sp.xx = rv.xx(index=index)
        sp.labels = rv.labels(index=index)
        sp.dyy = None
        sp.dxx = None
        if sp.plot_sigma_bars:
          sp.dyy = rv.dvv(index=index)
          sp.dxx = rv.dxx(index=index)
        self.check_and_append_subplot(sp, trace=trace)

    # Finished:
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None


#=====================================================================
# Classes to plot 2x2 complex cohaerency matrices:
#=====================================================================

class PyNodePlotCoh22 (PyNodePlotTensorVells):
  """Class derived from PyNodePlotTensorVells"""

  def __init__ (self, *args, **kwargs):
    PyNodePlotTensorVells.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Special version of PlotTensorVells to plot 2x2 cohaerency matrices,
    using standard colors for each of the 4 correlations.
    For each correlation, a dotted circle (0,0,<abs>) is drawn.
    To avoid clutter, the cross-corrs are not annotated.
    """
    ss = self.attach_help(ss, PyNodePlotCoh22.help.__doc__,
                          classname='PyNodePlotCoh22',
                          level=level, mode=mode)
    return PyNodePlotTensorVells.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.index = [0,1,2,3]
    rr.legend = ['XX','XY','YX','YY']
    rr.color = ['red','green','magenta','blue']
    rr.marker = ['o','x','x','o']
    rr.markersize = [5,5,5,5]
    rr.annotate = [True,False,False,True]
    rr.plot_circle_mean = [True,True,True,True]
    rr.xlabel = 'real part (Jy)'
    rr.ylabel = 'imag part (Jy)'
    
    # Then do the generic checks (mandatory!) 
    PyNodePlotTensorVells.check_plotinfo(self, trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    # trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children, labels=rr.labels,
                                  extend_labels=False,
                                  xindex=rr.xindex,
                                  yindex=rr.yindex)
    if trace:
      rv.display(self.class_name)

    # Make separate suplot definitions for each Vells:
    for index in rr.index:
      sp = record()
      for key in self._spkeys:               # transfer standard fields
        sp[key] = self.getval(rr[key], index=index, trace=trace)  
      sp.yy = rv.vcx(index=index)            # complex
      sp.xx = None                           # from complex
      sp.labels = rv.labels(index=index)
      sp.dyy = None
      sp.dxx = None
      if sp.plot_sigma_bars:
        sp.dyy = rv.dvv(index=index)
        sp.dxx = rv.dxx(index=index)
      self.check_and_append_subplot(sp, trace=trace)

    # Finished:
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
  if len(ww)>1:                       
    if not isinstance(ww[0],complex):
      s += format_float(ww.stddev(),'  stddev')
  return s



#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""
  

  cc = []
  labels = []
  n = 6
  for i in range(n):
    vv = []
    for j,corr in enumerate(['XX','XY','YX','YY']):
      v = (j+1)+10*(i+1)
      v = complex(i,j)
      vv.append(ns[corr](i) << v)
    cc.append(ns['c'](i) << Meq.Composer(*vv))
    labels.append('c'+str(i))

  exg = None
  # labels = None

  if False:
    # Optional: make concatenation pynode:
    exg = record(concat=record(vells=[2]))
    ns['concat'] << Meq.PyNode(children=cc, child_labels=labels,
                               class_name='PyNodeNamedGroups',
                               extractgroups=exg,
                               module_name=__file__)
    cc.append(ns['concat'])
    # cc.insert(0,ns['concat'])
    # cc.insert(2,ns['concat'])


  # Make the root pynode:
  # exg = record(extra=record(children=range(1,3)))
  # exg = record(extra=record(children='2/3', vells='*'))
  # exg = record(extra=record(children=range(1,3), vells=[0,1]))
  # exg = record(extra=record(children=range(1,3), vells=2))

  ns['rootnode'] << Meq.PyNode(children=cc,
                               child_labels=labels,
                               class_name='PyNodePlot',
                               extractgroups=exg,
                               module_name=__file__)
  # Meow.Bookmarks.Page('pynode').add(rootnode, viewer="Record Viewer")

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


if False:
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

  elif False:
    pp = PyNodePlotXY()
    print pp.help()

  else:
    #  from Timba.Meq import meqds 
    # Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
