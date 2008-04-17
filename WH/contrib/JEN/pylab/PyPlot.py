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
# import pylab       # not here, but in the class....!


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

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base class for an entire zoo of plotting pyNodes.
    Its central function is .define_subplots(), which is usually
    reimplemented by derived classes. It defines one or more subplots,
    i.e. makes one or more subplot definition records in the list
    self.plotinfo.subplot. These are used in various ways:
    - The subplots are converted into a SVG list (of strings),
    which is attached to the pyNode result as svg_string. It is
    used by the 'svg plotter' to make a (clumsy) plot.
    - The subplot definition records are also attached to the
    pyNode result. If the parent is also derived from PyPlot,
    it will append these subplots to its won new subplots.
    This allows the building of complicated plots by concatenation.
    A PyPlot node recognises PyPlot children from the plotinfo record
    in its result, and will ignore them for its normal function.
    
    When defining a PyPlot node, specific instructions are passed to it
    via a record named plotinfo:
    ns.plot << Meq.PyNode(class_name='PyPlotXY', module_name=__file__,
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
    ss = self.attach_help(ss, PyPlot.help.__doc__, classname='PyPlot',
                          level=level, mode=mode)
    return ss

  #...................................................................

  def attach_help(self, ss, s, classname='PyPlot',
                  level=0, mode=None, header=True):
    """
    This is the generic routine that does all the work for .help(). 
    It attaches the given help-string (s, in triple-quotes) to ss.
    The following modes are supported:
    - mode=None: interpreted as the default mode (e.g. 'list').
    - mode='list': ss is a list of strings (lines), to be attached to
    the node state. This is easier to read with the meqbrowser.
    - mode='str': ss is a string, in which lines are separated by \n.
    This is easier for just printing the help-text.
    """
    if mode==None:           # The default mode is specified here
      mode = 'list'
    if mode=='list':  
      if not isinstance(ss,(list,tuple)): ss = []
    else:                    # e.g. mode=='str'
      if not isinstance(ss,str): ss = ''
    sunit = '**'             # prefix unit string

    if header:
      h = sunit+(level*sunit)+'** Help for class: '+str(classname)
      if mode=='list':
        ss.append(h)
      else:
        ss += '\n'+h

    prefix = sunit+(level*sunit)+'   '
    cc = s.split('\n')
    for c in cc:
      if mode=='list':
        ss.append(prefix+c)
      else:
        ss += '\n'+prefix+c
    return ss
    
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

    if True:
      # Attach the help for this class to the state record.
      # It may be read with the browser after building the tree.
      if getattr(self, 'help', None):
        ss = self.help(mode='list')
        mystate('pyplot_node_help',ss)
        if trace:
          print '\n** Help attached to node state record:'
          print '\n** self.help(mode=list):\n'
          for s in ss:
            print s
          print '\n** self.help(mode=str):\n'
          print self.help(mode='str')
          print ' '

    mystate('name')
    mystate('class_name')
    mystate('child_indices')
    # print '** self.child_indices =',self.child_indices
    if isinstance(self.child_indices,int):
      self.child_indices = [self.child_indices]
    self._num_children = len(self.child_indices)

    # NB: This number still includes the PyPlot children,
    #     which are used for concatenating plots.
    #     In any case the number is greater or equal to the
    #     number of 'regular' (plottable) children, which is
    #     OK for the generation of lists of plot-specifications....

    if trace:
      print '\n*******************************************'
      print '** .update_state()',self.class_name,self.name,self.child_indices
      print '*******************************************\n'
    
    # Read the plotinfo record, and check it:
    mystate('plotinfo')
    self.check_plotinfo(trace=trace)
    return None

  #-------------------------------------------------------------------

  def iisubset (self, nc, part=1, nparts=1, trace=False):
    """Helper function that returns a list of indices for a subset
    of the nc child nodes. It assumes that the children are grouped in
    nparts equal parts (e.g. 3 equal-sized groups of x-nodes, y-nodes
    and z-nodes). It returns indices for the specified part.
    """
    # trace = True
    npp = nc/nparts           # nr per part (should be integer...)
    offset = (part-1)*npp
    ii = []
    for i in range(npp):
      ii.append(i+offset)
    if trace:
      print '\n** iisubset(',n,part,nparts,'):',npp,offset,'->',ii,'\n'
    return ii

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

    print '\n** PyPlot: self.plotinfo record (',txt,'):'
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

    # There are two classes of children:
    # - Those that are derived from PyPlot have a plotinfo field
    #   in their result. Its subplot definitions are appended to
    #   the local self.plotinfo.subplot list.
    # - The others are 'regular' children whose results are made
    #   into subplot definitions, which are appended to the
    #   local self.plotinfo.subplot list.
    # Thus, nodes derived from PyPlot may be concatenated to produce
    # complicated plots. But they can also be used by themselves.
    
    self.plotinfo.subplot = []            # If not, subplots accumulate.....
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

    title = 'PyPlot_'+self.class_name
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
# Classes derived from PyPlot:
#=====================================================================================
#=====================================================================================
#=====================================================================================


class PyPlotTensorVells (PyPlot):
  """Class derived from PyPlot."""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
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
    ss = self.attach_help(ss, PyPlotTensorVells.help.__doc__,
                          classname='PyPlotTensorVells',
                          level=level, mode=mode)
    return PyPlot.help(self, ss, level=level+1, mode=mode) 

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
    PyPlot.check_plotinfo(self, trace=trace)
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

class PyPlotCoh22 (PyPlotTensorVells):
  """Class derived from PyPlotTensorVells"""

  def __init__ (self, *args, **kwargs):
    PyPlotTensorVells.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Special version of PlotTensorVells to plot 2x2 cohaerency matrices,
    using standard colors for each of the 4 correlations.
    For each correlation, a dotted circle (0,0,<abs>) is drawn.
    To avoid clutter, the cross-corrs are not annotated.
    """
    ss = self.attach_help(ss, PyPlotCoh22.help.__doc__,
                          classname='PyPlotCoh22',
                          level=level, mode=mode)
    return PyPlotTensorVells.help(self, ss, level=level+1, mode=mode) 

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
    PyPlotTensorVells.check_plotinfo(self, trace=trace)
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




#=====================================================================

class PyPlotCrossCorrs22 (PyPlotCoh22):
  """Class derived from PyPlot."""

  def __init__ (self, *args, **kwargs):
    PyPlotCoh22.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Version of PyPlotCoh22 that only plots the cross-correlations
    (i.e. index 1 and 2). By default, annotate=True.
    """
    ss = self.attach_help(ss, PyPlotCrossCorrs22.help.__doc__,
                          classname='PyPlotCrossCorrs22',
                          level=level, mode=mode)
    return PyPlotCoh22.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    
    # Then do the generic checks (mandatory!) 
    PyPlotCoh22.check_plotinfo(self, trace=trace)

    # Set the specific values:
    rr.index = [1,2]
    rr.annotate = [True,True,True,True]

    # Finished:
    if True:
      self.show_plotinfo('.check_plotinfo()')
    return None






#=====================================================================
#=====================================================================
#=====================================================================
# Classes to plot x,y[,z] plots:
#=====================================================================


class PyPlotXY (PyPlot):
  """Class derived from PyPlot"""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Defines one plotinfo.subplot record.
    Assumes that its children are tensor nodes with at least 2 Vells.
    - Vells[xindex] represents the x-coordinate, and
    - Vells[yindex] represents the y-coordinate.
    """
    ss = self.attach_help(ss, PyPlotXY.help.__doc__,
                          classname='PyPlotXY',
                          level=level, mode=mode)
    return PyPlot.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.setdefault('xindex',0)
    rr.setdefault('yindex',1)
    rr.setdefault('xlabel','x')
    rr.setdefault('ylabel','y')
    
    # Then do the generic checks (mandatory!) 
    PyPlot.check_plotinfo(self, trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children,
                                  xindex=rr.xindex,
                                  yindex=rr.yindex)
    if trace:
      rv.display(self.class_name)

    # Make separate suplot definitions for each Vells:
    sp = record()
    for key in self._spkeys:               # transfer standard fields
      sp[key] = self.getval(rr[key], index=0, trace=trace)  
    sp.yy = rv.yy()     
    sp.xx = rv.xx()         
    sp.labels = rr.labels                  # use the input labels themselves
    sp.dyy = None
    sp.dxx = None
    if sp.plot_sigma_bars:
      sp.dyy = rv.dyy()
      # sp.dxx = rv.dxx()
    self.check_and_append_subplot(sp, trace=trace)

    # Finished:
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None


#=====================================================================

class PyPlotUV (PyPlotXY):
  """Class derived from PyPlotXY"""

  def __init__ (self, *args, **kwargs):
    PyPlotXY.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Version of PyPlotXY, used for plotting uv-points.
    """
    ss = self.attach_help(ss, PyPlotUV.help.__doc__,
                          classname='PyPlotUV',
                          level=level, mode=mode)
    return PyPlotXY.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.setdefault('xindex',0)
    rr.setdefault('yindex',1)
    rr.setdefault('xlabel','u')
    rr.setdefault('ylabel','v')
    
    # Then do the generic checks (mandatory!) 
    PyPlotXY.check_plotinfo(self, trace=trace)
    return None


#=====================================================================

class PyPlotXXYY (PyPlot):
  """Class derived from PyPlot"""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Defines one plotinfo.subplot record.
    Assumes that its children are single nodes:
    - The first half represent the x-coordinates, and
    - The second half represent the y-coordinates.
    """
    ss = self.attach_help(ss, PyPlotXXYY.help.__doc__,
                          classname='PyPlotXXYY',
                          level=level, mode=mode)
    return PyPlot.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.setdefault('xlabel','x')
    rr.setdefault('ylabel','y')
    
    # Then do the generic checks (mandatory!) 
    PyPlot.check_plotinfo(self, trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    ii = self.iisubset(len(children),1,2)
    rvx = ChildResult.ResultVector(children, select=ii)
    ii = self.iisubset(len(children),2,2)
    rvy = ChildResult.ResultVector(children, select=ii)
    if trace:
      rvx.display(self.class_name)
      rvy.display(self.class_name)

    # Make separate suplot definitions for each Vells:
    sp = record()
    for key in self._spkeys:               # transfer standard fields
      sp[key] = self.getval(rr[key], index=0, trace=trace)  
    sp.yy = rvy.vv()     
    sp.xx = rvx.vv()         
    sp.labels = rr.labels                  # use the input labels themselves
    sp.dyy = None
    sp.dxx = None
    if sp.plot_sigma_bars:
      sp.dyy = rvy.dvv()
      # sp.dxx = rvx.dvv()
    self.check_and_append_subplot(sp, trace=trace)

    # Finished:
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None




#=====================================================================
# Plots that also have a z-value (controls marker size)
#=====================================================================

class PyPlotXYZ (PyPlot):
  """Class derived from PyPlot"""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Defines one plotinfo.subplot record.
    Assumes that its children are tensor nodes with 3 Vells.
    - Vells[xindex] represents the x-coordinate, and
    - Vells[yindex] represents the y-coordinate.
    The remaining Vells of each node is assumed to represent z-values,
    which are translated into the size of the point markers.
    """
    ss = self.attach_help(ss, PyPlotXYZ.help.__doc__,
                          classname='PyPlotXYZ',
                          level=level, mode=mode)
    return PyPlot.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.setdefault('xindex',0)
    rr.setdefault('yindex',1)
    rr.setdefault('xlabel','x')
    rr.setdefault('ylabel','y')
    
    # Then do the generic checks (mandatory!) 
    PyPlot.check_plotinfo(self, trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    rv = ChildResult.ResultVector(children,
                                  xindex=rr.xindex,
                                  yindex=rr.yindex)
    if trace:
      rv.display(self.class_name)

    # Make separate suplot definitions for each Vells:
    sp = record()
    for key in self._spkeys:               # transfer standard fields
      sp[key] = self.getval(rr[key], index=0, trace=trace)  
    sp.yy = rv.yy()     
    sp.xx = rv.xx()         
    sp.zz = rv.vv()
    self.zz2markersize(sp)
    sp.labels = rr.labels  
    self.check_and_append_subplot(sp, trace=trace)

    # Finished:
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None



#=====================================================================

class PyPlotXYZZ (PyPlot):
  """Class derived from PyPlot"""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Defines one plotinfo.subplot record.
    Assume that half of its children are tensor nodes, in which
    - Vells[xindex] represents the x-coordinate, and
    - Vells[yindex] represents the y-coordinate.
    The other half of the chidren are assumed to represent z-values
    which are used to control the size of the point markers.
    """
    ss = self.attach_help(ss, PyPlotXYZZ.help.__doc__,
                          classname='PyPlotXYZZ',
                          level=level, mode=mode)
    return PyPlot.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """
    Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.setdefault('xindex',0)
    rr.setdefault('yindex',1)
    rr.setdefault('xlabel','x')
    rr.setdefault('ylabel','y')
    
    # Then do the generic checks (mandatory!) 
    PyPlot.check_plotinfo(self, trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    trace = True

    # The child result(s) are read by special objects: 
    import ChildResult
    ii = self.iisubset(len(children),1,2)
    rvxy = ChildResult.ResultVector(children, select=ii,
                                    xindex=rr.xindex,
                                    yindex=rr.yindex)
    ii = self.iisubset(len(children),2,2)
    rvz = ChildResult.ResultVector(children, select=ii)

    if trace:
      rvxy.display(self.class_name)
      rvz.display(self.class_name)

    # Make separate suplot definitions for each Vells:
    sp = record()
    for key in self._spkeys:               # transfer standard fields
      sp[key] = self.getval(rr[key], index=0, trace=trace)  
    sp.yy = rvxy.yy()     
    sp.xx = rvxy.xx()         
    sp.zz = rvz.vv()
    self.zz2markersize(sp)
    sp.labels = rr.labels  
    self.check_and_append_subplot(sp, trace=trace)

    # Finished:
    if trace:
      self.show_plotinfo('.define_subplots()')
    return None



#=====================================================================

class PyPlotXXYYZZ (PyPlot):
  """Class derived from PyPlot"""

  def __init__ (self, *args, **kwargs):
    PyPlot.__init__(self, *args);
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Defines one plotinfo.subplot record.
    Assumes that the list of children contains three groups:
    - The first third are nodes representing x-coordinates
    - The second third are nodes representing y-coordinates
    - The third third are nodes representing z-values.
    The latter are converted to the marker sizes (msmin<>msmax).
    """
    ss = self.attach_help(ss, PyPlotXXYYZZ.help.__doc__,
                          classname='PyPlotXXYYZZ',
                          level=level, mode=mode)
    return PyPlot.help(self, ss, level=level+1, mode=mode) 

  #-------------------------------------------------------------------

  def check_plotinfo (self, trace=False):
    """Check the contents of the input self.plotinfo record.
    """
    rr = self.plotinfo                        # convenience
    # trace = True

    # Set the specific values:
    rr.setdefault('xlabel','x')
    rr.setdefault('ylabel','y')
    
    # Then do the generic checks (mandatory!) 
    PyPlot.check_plotinfo(self, trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_subplots (self, children, trace=False):
    """
    Reimplementation of baseclass function.
    See .help() for details.
    """
    rr = self.plotinfo                         # convenience
    trace = True

    # The child result(s) are read by a special object: 
    import ChildResult
    ii = self.iisubset(len(children),1,3)
    rvx = ChildResult.ResultVector(children, select=ii)
    ii = self.iisubset(len(children),2,3)
    rvy = ChildResult.ResultVector(children, select=ii)
    ii = self.iisubset(len(children),3,3)
    rvz = ChildResult.ResultVector(children, select=ii)
    if trace:
      rvx.display(self.class_name)
      rvy.display(self.class_name)
      rvz.display(self.class_name)

    # Make separate suplot definitions for each Vells:
    sp = record()
    for key in self._spkeys:               # transfer standard fields
      sp[key] = self.getval(rr[key], index=0, trace=trace)  
    sp.xx = rvx.vv()         
    sp.yy = rvy.vv()     
    sp.zz = rvz.vv()         
    self.zz2markersize(sp)
    sp.labels = rr.labels                  # use the input labels themselves
    sp.dyy = None
    sp.dxx = None
    if sp.plot_sigma_bars:
      # sp.dyy = rvy.dvv()
      # sp.dxx = rvx.dvv()
      pass
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

  children = dict()
  rr = dict()
  classnames = dict()

  ftx= ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())
  ft= ns.freqtime << Meq.Add(Meq.Time(),Meq.Freq())
  gsx = ns.cx_gauss << Meq.ToComplex(Meq.GaussNoise(stddev=0.1),
                                     Meq.GaussNoise(stddev=0.1))
  gs = ns.gauss << Meq.GaussNoise(stddev=0.5)

  tfrac = ns.tfrac << Meq.Multiply(Meq.Time(),0.1)
  ffrac = ns.ffrac << Meq.Multiply(Meq.Freq(),0.1)


  #----------------------------------------------------------------------
  
  if False:
    ccx = []
    ccy = []
    ccz = []
    ccxy = []
    ccxyz = []
    labz = []
    labxy = []
    labxyz = []
    yname = 'y1p'
    xname = 'x1p'
    zname = 'z1p'
    vname = 'v1p'
    
    n = 5
    for i in range(n):

      x = ns[xname](i) << (gs + random.gauss(i,0.3))
      ccx.append(x)

      y = ns[yname](i) << (gs + random.gauss(i,0.5))
      ccy.append(y)

      z = ns[zname](i) << (gs + random.gauss(i,0.3))
      ccz.append(z)
      labz.append('z_'+str(i))    

      xy = ns.xy(i) << Meq.Composer(x,y)
      ccxy.append(xy)
      labxy.append('xy_'+str(i))    

      xyz = ns.xyz(i) << Meq.Composer(x,y,z)
      ccxyz.append(xyz)
      labxyz.append('xyz_'+str(i))    

    if 1:
      classname = 'PyPlotXY'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        markersize=10,
                        labels=labxy,
                        plot_sigma_bars=True)
      children[name] = ccxy

      if 1:
        classname = 'PyPlotUV'
        name = classname
        classnames[name] = classname
        rr[name] = rr['PyPlotXY']
        rr[name]['title'] = name
        children[name] = children['PyPlotXY']


    if 0:
      classname = 'PyPlotXXYY'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        markersize=5,
                        color='magenta',
                        plot_sigma_bars=True,
                        labels=labz)
      children[name] = ccx+ccy


    if 0:
      classname = 'PyPlotXYZ'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        color='red',
                        labels=labxyz)
      children[name] = ccxyz

    if 0:
      classname = 'PyPlotXYZZ'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        color='green',
                        labels=labz)
      children[name] = ccxy+ccz

    if 0:
      classname = 'PyPlotXXYYZZ'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        color='yellow',
                        plot_sigma_bars=True,
                        labels=labz)
      children[name] = ccx+ccy+ccz


  #----------------------------------------------------------------------

  if False:
    classname = 'PyPlot'
    name = classname+'m'              # minimal PyPlot
    cc = []
    labels = []
    yname = 'y1m'
    xname = 'x1m'
    n = 5
    for i in range(n):
      # y = ns[yname](i) << (gs + random.gauss(i,0.5))
      y = ns[yname](i) << (gsx + random.gauss(i,0.5))
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

  #----------------------------------------------------------------------

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

  #----------------------------------------------------------------------

  if True:
    cc = []
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
        XY = ns.XY(i)(j) << Meq.Polar(random.gauss(0.1,rmsa),
                                      random.gauss(0.5,0.1))
        YX = ns.YX(i)(j) << Meq.Polar(random.gauss(0.1,rmsa),
                                      random.gauss(-0.5,0.1))
        if False:
          YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa),
                                        random.gauss(0.0,1.0))
        elif False:
          YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa),
                                        random.gauss(0.0,0.0)+ffrac)
        else:
          YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,rmsa)+tfrac,
                                        random.gauss(0.0,1.0)+ffrac)

        vis22 = ns.vis22(i)(j) << Meq.Matrix22(XX,XY,YX,YY)
        # vis22 = ns.vis22plus(i)(j) << Meq.Add(vis22, ftx)
        vis22 = ns.vis22plus(i)(j) << Meq.Add(vis22, gsx)
        cc.append(vis22)

    if True:
      classname = 'PyPlotCoh22'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name, labels=labels)
      children[name] = cc

    if True:
      classname = 'PyPlotCrossCorrs22'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name,
                        markersize=20,
                        plot_sigma_bars=False,
                        labels=labels)
      children[name] = cc

      
  #-----------------------------------------------------------------------
      
  if False:
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

    if False:
      classname = 'PyPlot'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name, labels=labels,
                        xindex=1,
                        color='green', marker='x', markersize=20)
      children[name] = cc

    if True:
      classname = 'PyPlotTensorVells'
      name = classname
      classnames[name] = classname
      rr[name] = record(title=name, labels=labels,
                        color=['blue','red','cyan'])
      children[name] = cc
      
  #-----------------------------------------------------------------------


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
    rr[name].make_plot = True
    pynode = ns[name] << Meq.PyNode(children=children[name],
                                    class_name=classnames[name],
                                    plotinfo=rr[name],
                                    module_name=__file__)
    pn.append(pynode)
    if rr[name].make_plot:
      Meow.Bookmarks.Page(name).add(pynode, viewer="Svg Plotter")
      bookpage.add(pynode, viewer="Svg Plotter")

  # Make a root node:
  if False:
    # Just bundle all into a single root node:
    ns.rootnode << Meq.Composer(*pn)
  else:
    # Concatenation of all PyPlot nodes:
    plotinfo = record(title='combined', make_plot=True, offset=-2.0)
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

  elif True:
    pp = PyPlotXY()
    print pp.help()

  else:
    #  from Timba.Meq import meqds 
    # Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
