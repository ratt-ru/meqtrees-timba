# file: ../contrib/JEN/pylab/PyNodePlot.py

# Author: J.E.Noordam
# 
# Short description:
#   PyNode baseclass for plotting child results
#
# History:
#    - 21 mar 2008: creation (from VisuPlotXY.py)
#    - 21 apr 2008: derived from PyNodeNamedGroups)
#    - 07 may 2008: Tony's version with pyfig
#    - 23 may 2008: implemented plotspec ignore=expr
#    - 03 jul 2008: implemented pynode_Plot() etc
#    - 07 jul 2008: introduced overall plot-legend
#
# Remarks:
#
#  AGW: If I try to import pylab_plotter.py twice, it complains that
#       it 'cannot import name PyNodeplot' ....?
#       It is OK again if I restart the browser....
#
#  OMS: When I edit something in a baseclass (PyNodeNamedGroups),
#       it only takes effect after killing the MeqServer(!)
#       It is NOT sufficient to kill the MeqBrowser
#
#  OMS: When I print something in the baseclass, it is not printed
#       on the screen when such a function is called from the
#       derived class (in which the function is re-implemented).
#       I call the baseclass version, of course, with self as an argument:
#           PNNG.PyNodeNamedGroups.update_state(self, mystate)
#       However, the function appears to be executed. Is there something
#       with stdout from inside a baseclass function when called from a
#       derived class...?
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
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

# from Timba import pynode
from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
from Timba.Contrib.JEN.QuickRef import EasyNode as EN
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyBundle as EB

import inspect
import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;


#=====================================================================================
# The PyNodePlot base class:
#=====================================================================================

class PyNodePlot (PNNG.PyNodeNamedGroups):
  """
  Base class for a range of plotting pyNodes.
  It is derived from the class PyNodeNamedGroups, which
  manipulates one or more 'named groups' of values.
  The latter may be obtained from the results of nodes, so these
  can be plotted. They may also be provided directly as lists of
  values. For more information see the PyNodeNamedGroups.py.

  When defining a PyNodePlot node, specific instructions are passed
  to it via plotspecs record (ps). The latter has lists of subplot
  definitions which are plotted together in a single plot. For the
  moment, only plots of type 'graphics' are supported, i.e. the
  plotspecs record has a 'graphics' field which is a list of records:
  In addition, the plotspecs record may have overall attributes
  (title, xlabel, ylabel, window etc) which control the entire plot.

  .   psg = []
  .   psg.append(record(y='{y}', color='red'))
  .   psg.append(record(y='{a}*{b}', x='{c}', color='blue'))
  .
  .   ps = record(graphics=psg,
  .               title=.., ylabel=.., ...)
  
  The PyNode may be generated in the following way (for the optional
  groupspecs definition, see the class PyNodeNamedGroups):

  .   from Timba.Contrib.JEN.pylab import PyNodePlot as PNP
  .   ns[nodename] << Meq.PyNode(children=[nodes],
  .                              child_labels=[strings],
  .                              class_name='PyNodePlot',
  .                              module_name=PNP.__file__,
  .                              [groupspecs=record(....),]
  .                              plotspecs=ps)
  
  In practice, it is recommended to use the function pynode_Plot()
  in this module PyNodePlot.py. 

  Possible keywords for individual graphics subplots are:
  - color      [='blue']       subplot color
  - linestyle  [=None]         subplot linestyle ('-','--',':')
  - marker     [='o']          subplot marker style ('+','x', ...)
  - markersize [=5]            subplot marker size (points)
  - plot_sigma_bars [=True]    if True, indicate domain variation
  - legend     [=[]]           subplot legend string(s)
  - annotate   [=True]         if True, annotate points with labels
  - fontsize   [=7]            annotation font size (points)
  - msmin      [=2]            min marker size (z-values)
  - msmax      [=20]           max marker size (z-values) 
  - plot_circle_mean [=False]  if True, plot a circle (0,0,rmean)
  - plot_ellipse_stddev [=False]  if True, plot an ellipse (xc,yc,stddev)

  Overall plotspecs keywords are:
  - labels     [=None]         a list of node labels
  - offset     [=0.0]          concatenated plots maye be offset vertically
  - title      [=<classname>]  plot title
  - xlabel     [='child']      x-axis label
  - ylabel     [='result']     y-axis label
  - xunit      [=None]         x-axis unit (string)
  - yunit      [=None]         y-axis unit (string)
  - zunit      [=None]         z-axis unit (string)
  - xmin       [=None]         plot-window
  - xmax       [=None]         plot-window
  - ymin       [=None]         plot-window
  - ymax       [=None]         plot-window
  - include_origin [=False]    plot-window, if True, include the origin (0,0)
  - include_xaxis [=False]     plot-window, if True, include y=0
  - include_yaxis [=False]     plot-window, if True, include x=0
  - legend     [=[]]           plot legend string(s)
  - make_svg   [=False]        (legacy, ignore)

  NB: Many subplot keywords (e.g. linestyle) may be specified as overall
  keywords also. In that case, it becomes the default for subplots which
  do not have this keyword specified explicitly. 
 """

  def __init__ (self, *args, **kwargs):
    # print '\n** entering PyNodePlot.__init__()\n'
    PNNG.PyNodeNamedGroups.__init__(self,*args);
    # print '\n** after PNNG.PyNodeNamedGroups.__init__()\n'

    self._plotypes = ['graphics']                # supported plot types
    self._plotypes.append('other')               # testing only

    self._pskeys = record(overall=[])
    for plotype in self._plotypes:
      self._pskeys[plotype] = []

    self.plotspecs = record()                    
    self._plotdefs = record()
    
    self._standard = record()
    self.standard('color', clear=True, update=record(default='yellow'))
    self.standard('marker', clear=True, update=record(default='triangle'))
    # print self.help()
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    """
    ss = self.attach_help(ss, PyNodePlot.__doc__,
                          classname='PyNodePlot',
                          level=level, mode=mode)
    return PNNG.PyNodeNamedGroups.help(self, ss, level=level+1, mode=mode) 

  #--------------------------------------------------------------------

  def oneliner(self):
    ss = PNNG.PyNodeNamedGroups.oneliner(self)
    for plotype in self._plotypes:
      nn = [0,0]
      if self.plotspecs.has_key(plotype):
        nn[0] = len(self.plotspecs[plotype])
      if self._plotdefs.has_key(plotype):
        nn[1] = len(self._plotdefs[plotype])
      if True or  sum(nn)>0:
        ss += '  '+plotype+'('+str(nn)+')'
    return ss

  #---------------------------------------------------------------

  def display(self, txt, full=False, level=0):
    """Display a summary of the contents of this object"""
    prefix = self._preamble(level, txt=txt)

    print prefix,' * self._pskeys:'
    rr = self._pskeys
    for key in rr.keys():
      print prefix,' - ',key,':',rr[key]

    print prefix,' * self._standard:'
    rr = self._standard
    for key in rr.keys():
      print prefix,' - ',key,'(keys):',rr[key].keys()

    print prefix,' * self.plotspecs (user-input records, and default values):'
    rr = self.plotspecs                      # convenience
    for key in self._pskeys['overall']:
      print prefix,'   -',key,'=',rr[key]
    for plotype in self._plotypes:
      if rr.has_key(plotype):
        print prefix,'   - plotype:',plotype,'(n='+str(len(rr[plotype]))+'):'
        for key in self._pskeys[plotype]:
          print prefix,'     -',key,'=',rr[key]
        for i,ps in enumerate(rr[plotype]):
          print prefix,'     -',plotype+'['+str(i)+']:'
          for key in ps.keys():    
            print prefix,'       -',key,'=',ps[key]

    print prefix,' * self._plotdefs (new, and copied from children):'
    rr = self._plotdefs                      # convenience
    for key in self._pskeys['overall']:
      if rr.has_key(key):
        print prefix,'   -',key,'=',rr[key]
    for plotype in self._plotypes:
      if rr.has_key(plotype):
        print prefix,'   - plotype:',plotype,'(n='+str(len(rr[plotype]))+'):'
        for i,pd in enumerate(rr[plotype]):
          print prefix,'     -',plotype+'['+str(i)+']:'
          for key in pd.keys():
            if not isinstance(pd[key],(list,tuple)):
              print prefix,'       - ',key,'=',pd[key]
            elif key in ['xx','yy','zz','dxx','dyy','dzz']:
              # print prefix,'       - ',key,': (LIST)',format_vv(pd[key])
              print prefix,'       - ',key,': (LIST)',EN.format_value(pd[key])
            else:
              print prefix,'       - ',key,'=',pd[key]


    # NB: It is probably best to display the base-class info here...
    PNNG.PyNodeNamedGroups.display(self, txt, full=full, level=level+1)
    self._postamble(level)
    return True


  #-------------------------------------------------------------------
  #-------------------------------------------------------------------
    
  def update_state (self, mystate):
    """
    in PyNodePlot.py
    Read information from the pynode state record. This is called
    when the node is first created and a full state record is available.
    But also when state changes, and only a partial state record is
    supplied....
    Instead of the state record, we  receive a clever object (mystate)
    which encapsulates the state record with some additional semantics.
    """

    trace = False
    # trace = True

    # First update all the namedgroup specifications:
    # This creates self.groupspecs (and self._gs_order) and
    # self._namedgroups (and self._ng_order).
    # print '** BEFORE:'
    # print type(PNNG.PyNodeNamedGroups.update_state)
    # print PNNG.PyNodeNamedGroups.update_state.__doc__
    r = PNNG.PyNodeNamedGroups.update_state(self, mystate)
    # print '** AFTER:',r

    # Read the plotspecs record, and check it:
    mystate('plotspecs', None)
    if not isinstance(self.plotspecs, record):
      self.plotspecs = record()              # make sure it is a record

    rr = self.plotspecs                      # convenience
    for plotype in self._plotypes:
      if not rr.has_key(plotype):
        rr[plotype] = []                     # e.g. rr['graphics'] = []
      else:
        rr[plotype] = list(rr[plotype])      # convert tuple into list

    # Define (extra) class-specific plotspecs (if any), using
    # the (re-implementable) class-specific function.
    self.define_specific_plotspecs()

    if False:
      # NOT a good idea(?), especially since allvells is not guaranteed...
      # Make sure that there is at least one plot specification....?
      n = 0
      for plotype in self._plotypes:         # for each plotype
        n += len(self.plotspecs[plotype])    #   count the plotspecs
      if n==0:                            
        ps = record(y='{allvells}', color='cyan') 
        self.plotspecs['graphics'].append(ps)

    # Check the final self.plotspecs:
    self._check_plotspecs(trace=trace)
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=False):  
    """
    Placeholder for class-specific function, to be re-implemented
    by classes that are derived from PyNodePlot. Called by ._update_state().
    It allows the specification of one or more specific plotspecs.
    """
    return None

  #-------------------------------------------------------------------

  def standard (self, attrib=None, key=None, 
                update=None, clear=False, trace=False):
    """
    Helper function to get a standard attribute (e.g. color) for the
    specified key: color = self.standard('color','a').
    Used in (re-implementation of) define_specific_plotspecs().
    The named (key) attributes are defined in __init__():
    self.standard('color', update=record(a='red', b='green') etc.
    """
    if clear or not self._standard.has_key(attrib):
      self._standard[attrib] = record()
    if isinstance(update, record):
      self._standard[attrib].update(update)
      if trace:
        print '\n** standard.update(',attrib,') ->',self._standard[attrib]
    rr = self._standard[attrib]
    if rr.has_key(key):
      return rr[key]
    if rr.has_key('default'):
      return rr['default']
    return False

  #-------------------------------------------------------------------

  def _check_plotspecs (self, trace=False):
    """
    Check the contents of the input self.plotspecs record.
    """
    if trace:
      self.display('_check_plotspecs() input')

    rr = self.plotspecs                               # convenience

    # Some node control parameters:
    rr.setdefault('make_svg', False)                  # if True, make the SVG plot

    # These keys are used to transfer fields to self._plotdefs:
    self._pskeys = record(overall=[])
    for plotype in self._plotypes:
      self._pskeys[plotype] = []

    # Overall parameters 
    ss = ['title','xlabel','ylabel','xunit','yunit','zunit']
    ss.extend(['xmin','xmax','ymin','ymax'])
    ss.extend(['include_origin','include_xaxis','include_yaxis'])
    ss.extend(['offset'])                             # ....?
    ss.extend(['make_svg'])                           # ....?
    ss.extend(['legend'])                             # .. a special case ..
    self._pskeys['overall'] = ss

    title = 'PyNodePlot_'+self.class_name
    title += '_'+str(len(self.child_indices))
    rr.setdefault('title', self.name) 
    rr.setdefault('xlabel', 'child') 
    rr.setdefault('ylabel', 'result') 
    rr.setdefault('xmin', None) 
    rr.setdefault('xmax', None) 
    rr.setdefault('ymin', None) 
    rr.setdefault('ymax', None) 
    rr.setdefault('include_origin', False)            # include (0,0)
    rr.setdefault('include_xaxis', False)             # include y=0
    rr.setdefault('include_yaxis', False)             # include x=0
    rr.setdefault('xunit', None) 
    rr.setdefault('yunit', None) 
    rr.setdefault('zunit', None) 
    rr.setdefault('offset', 0.0)                      # offset multiple subplots
    rr.setdefault('legend', [])                       # plot-legend

    # Parameters used in (sub)plot definitions of various types.
    # They all have default values in the overall section.
    # These keys are used to transfer defaults to self._plotdefs:
    ss = ['color','linestyle','marker','markersize']
    ss.extend(['plot_sigma_bars','annotate','fontsize'])
    ss.extend(['ignore'])                           # ....?
    ss.extend(['plot_circle_mean','plot_ellipse_stddev'])
    self._pskeys['graphics'] = ss

    rr.setdefault('legend', [])                     # subplot legend
    rr.setdefault('ignore', None)                   # python expression (string)
    rr.setdefault('color', 'blue')                  # plot color
    rr.setdefault('linestyle', None)                # line style                  
    rr.setdefault('marker', 'o')                    # marker style
    rr.setdefault('markersize', 5)                  # markersize (points)
    rr.setdefault('msmin',2)                        # min marker size (zmin)
    rr.setdefault('msmax',20)                       # max marker size (zmax)
    rr.setdefault('annotate', True)                 # do annotation
    rr.setdefault('fontsize', 7)                    # font size (points)
    rr.setdefault('plot_sigma_bars', True)          # plot error-bars
    rr.setdefault('plot_circle_mean', False)        # plot circle around (0,0) with radius=mean
    rr.setdefault('plot_ellipse_stddev', False)     # plot ellipse around (mean) with radii=stddev

    # Deal with the plotspecs, dependent on their plot-type (e.g. graphics): 
    for plotype in self._plotypes:
      if rr.has_key(plotype):                       # e.g. plotspecs[graphics] = [list]
        if plotype=='graphics':
          self._check_plotspecs_graphics()

    # Finished:
    if trace:
      self.display('_check_plotspecs() output')
    return None

  #-------------------------------------------------------------------

  def _check_plotspecs_graphics (self, trace=False):
    """
    Check the plotspecs of plotype graphics
    """
    if trace:
      print '\n** _check_plotspecs_graphics():'
    for i,rr in enumerate(self.plotspecs['graphics']):
      s = 'plotspecs.graphics['+str(i)+']: '
      if not rr.has_key('yy'):
        s += 'no key yy in keys: '+str(rr.keys())
        # raise ValueError, s
      if trace:
        print '**',s,rr
    # Finished:
    if trace: print
    return True


  #-------------------------------------------------------------------
  #-------------------------------------------------------------------

  def get_result (self, request, *children):
    """
    Required pyNode function.
    """

    trace = False
    # trace = True
    
    self._count += 1

    # Fill self._namedgroups with named groups from its children.
    # These are also attached to the result, for concatenation.
    result = PNNG.PyNodeNamedGroups.get_result(self, request, *children)

    # Re-initialize the record that contains the plot definitions:
    self._plotdefs = record()

    for key in self._pskeys['overall']:           # title, ylabel etc
      self._plotdefs[key] = self.plotspecs[key]
    self._plotdefs['xlabel'] = self._expr2lcs(self._plotdefs['xlabel'])
    self._plotdefs['ylabel'] = self._expr2lcs(self._plotdefs['ylabel'])

    for plotype in self._plotypes:                # for all plot types
      self._plotdefs[plotype] = []          

    # There are two classes of children:
    # - Those that are derived from PyNodePlot have a plotdefs field
    #   in their result. Its (sub)plot definitions are appended to
    #   the local self._plotdefs.graphics list (etc).
    # - The others are 'regular' children whose results are used
    #   to make named groups (see PyNodeNamedGroups.py)
    # Nodes derived from PyNodePlot may be concatenated to produce
    # complicated plots. But they can also be used by themselves.

    # First copy the concatenable (sub)plot definitions:
    for child in children:
      if child.has_key('plotdefs'):             
        for plotype in self._plotypes:
          for plodef in child['plotdefs'][plotype]:
            self._plotdefs[plotype].append(plodef)
    
    # Make new (sub)plot definition records from the available
    # named groups, using the user-defined self.plotspecs record.
    # Append them to the relevant self._plotdefs[plotype] lists.
    if True:
      self._plotspecs2plotdefs_graphics(trace=trace)

    if False:
      self.display('PyNodePlot.get_result()')

    # Optionally, generate info for the "svg plotter":
    result.svg_plot = None
    if self.plotspecs.make_svg: 
      svg_list_of_strings = self.make_svg(trace=False)
      result.svg_plot = svg_list_of_strings

    # Always attach the self._plotdefs record to the result,
    # to be used for concatenation (and inspection):
    result.plotdefs = self._plotdefs

    # Finished:
    return result

  #-------------------------------------------------------------------

  def _plotspecs2plotdefs_graphics(self, trace=False):
    """
    Helper function to turn the graphics plotspecs into
    graphics plot definition records in self._plotdefs"""

    # trace = True

    plotype = 'graphics'
    for i,rr in enumerate(self.plotspecs[plotype]):

      # Initialize a new plot definition record:
      pd = record(xx=None, yy=None, zz=None,
                  dxx=None, dyy=None, ignore=None)

      # Transfer the various options (e.g. color):
      for key in self._pskeys[plotype]:
        if rr.has_key(key):
          pd[key] = rr[key]                      # user-specified
        else:
          pd[key] = self.plotspecs[key]          # general default

      # Condition the plot-legend (list of strings):
      pd.legend = []
      if rr.has_key('legend'):
        pd['legend'] = rr['legend']
      if not isinstance(pd.legend,(list,tuple)):
        pd.legend = [pd.legend]
      pd.legend = list(pd.legend)                # tuple does not support item assignment

      # Get the xx and yy vectors by evaluating python expressions:
      if rr.has_key('xy'):                       # expr
        pd.yexpr = 'complex('+str(rr.xy)+').imag'
        pd.xexpr = 'complex('+str(rr.xy)+').real'
        pd.yy = self._evaluate(pd.yexpr, trace=trace)
        pd.xx = self._evaluate(pd.xexpr, trace=trace)
        pd.labels = self._expr2labels(pd.yexpr, trace=trace)
        
      elif rr.has_key('y'):                      # y expr specified                       
        pd.yexpr = str(rr.y)
        pd.yy = self._evaluate(pd.yexpr, trace=trace)
        pd.labels = self._expr2labels(rr.y, trace=trace)
        if rr.has_key('x'):                      # x expr specified
          pd.xexpr = str(rr.x)
          pd.xx = self._evaluate(pd.xexpr, trace=trace)
        else:                                    # use child numbers for x
          pd.xx = self._expr2childnos(pd.yexpr, trace=trace)
          if not isinstance(self._plotdefs.xlabel,str): 
            self._plotdefs.xlabel = 'pynode child no'   

      else:
        s = '** neither y nor xy expression in graphics plotspec'
        raise ValueError,s

      # Temporary (testing): Make sure that all values are slightly different:
      if False:
        rms = 0.0000001
        for i,v in enumerate(pd.yy):
          pd.yy[i] += random.gauss(0,rms)
          pd.xx[i] += random.gauss(0,rms)

      # If pd.ignore is a python expression (string), evaluate it: 
      if isinstance(pd.ignore, str):
        pd.legend.append('(ignore='+pd.ignore+')')
        pd.ignore = self._evaluate(pd.ignore, trace=trace)
        

      # If a z-expr is specified, make a XYZ plot:
      if rr.has_key('z'):                        # z expr specified                       
        pd.zexpr = str(rr.z)
        pd.zz = self._evaluate(pd.zexpr, trace=trace)
        pd.labels = self._expr2labels(pd.zexpr, trace=trace)
        self._zz2markersize(pd)
        if pd.plot_sigma_bars:
          pd.dzz = self._expr2dvv(pd.zexpr, trace=trace)
        self._plotdef_statistics(pd,'zz')
      else:
        if pd.plot_sigma_bars:
          pd.dyy = self._expr2dvv(pd.yexpr, trace=trace)
        self._plotdef_statistics(pd,'yy')

      # Adjust the legend string(s), if necessary:
      for i,s in enumerate(pd.legend):
        if getattr(pd,'xexpr',None):
          pd.legend[i] = pd.legend[i].replace('xexpr',str(pd.xexpr))
        if getattr(pd,'yexpr',None):
          pd.legend[i] = pd.legend[i].replace('yexpr',str(pd.yexpr))
        if getattr(pd,'zexpr',None):
          pd.legend[i] = pd.legend[i].replace('zexpr',str(pd.zexpr))
          
      # Append the new plot
      if trace:
        print pd
      self._plotdefs[plotype].append(pd)
      
    # Finished:
    return True

  #-------------------------------------------------------------------

  def _zz2markersize (self, pd, trace=False):
    """
    Helper function to translate the values pd.zz in the given plot
    definition (pd) into a vector of integer values pd.markersize,
    between the specified (plotspecs) miniumum and maximum sizes (in points)
    """
    rr = self.plotspecs             # convenience, contains msmin and msmax
    pd.zmin = min(pd.zz)
    pd.zmax = max(pd.zz)
    nsig = 3                        # nr of significant digits
    s = 'z-range=['+EN.format_value(pd.zmin, nsig=nsig)
    s += ', '+EN.format_value(pd.zmax, nsig=nsig)+']'
    pd.legend.append(s)
    q = (rr.msmax-rr.msmin)/(pd.zmax-pd.zmin)
    ms = []
    for i,z in enumerate(pd.zz):
      ms.append(int(rr.msmin+q*(z-pd.zmin)))
    pd.markersize = ms
    return True

  #-------------------------------------------------------------------

  def _plotdef_statistics(self, pd, key):
    """
    Helper function to calculate some statistics for the specified
    (key) vector in the given plot definition (pd) record, and attach them.
    """
    import pylab
    vv = pylab.array(pd[key])  
    if len(vv)>0:
      pd.min = vv.min()
      pd.max = vv.max()
      pd.mean = vv.mean()
      pd.stddev = 0.0
      if len(vv)>1:
        if not isinstance(vv[0],complex):
          pd.stddev = vv.std()       
    return True


  #-------------------------------------------------------------------
  #-------------------------------------------------------------------

  def make_svg (self, trace=False):
    """
    Make an svg plot definition from all items in self._plotdefs.
    (NB: This is semi-obsolete, but retained for the future.....)
    Using the same function that is called by Tony's pylab_plotter.
    """
    fig = make_pylab_figure(self._plotdefs, figob=None,
                            target='svg', trace=trace)
    svg_list_of_strings = fig.make_svg(rootname=self.class_name)
    return svg_list_of_strings

#--------------------------------------------------------------------

  def set_window(self, grs, trace=False):
    """
    Set the plot window
    """

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

  def define_subplots_obsolete (self, children, trace=False):
    """
    See .help() for details.
    """
    rr = self.plotspecs                         # convenience
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
      self.show_plotspecs('.define_subplots()')
    return None







#=====================================================================================
#=====================================================================================
#=====================================================================================
# Classes derived from PyNodePlot:
#=====================================================================================
#=====================================================================================
#=====================================================================================


class ExampleDerivedClass (PyNodePlot):
  """
  Example of a class derived from PyNodePlot.
  NB: The (preferred) alternative to derived classes is the use of
  functions like pynode_Plot(), as defined in this module.
  """

  def __init__ (self, *args, **kwargs):
    PyNodePlot.__init__(self, *args)

    # Set some standard colors/markers, which may be retrieved with
    self.standard('color', update=record(a='red', b='green', x='blue'))
    self.standard('marker', update=record(c='diamond', d='hexagon'))
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    This is an exmple of a class derived from PyNodePlot.
    """
    ss = self.attach_help(ss, ExampleDerivedClass.help.__doc__,
                          classname='ExampleDerivedClass',
                          level=level, mode=mode)
    return PyNodePlot.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=False):  
    """
    Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    if True:
      # Used for operations (e.g. plotting) on separate correlations.
      # Its children are assumed to be 2x2 tensor nodes (4 vells each).
      self.groupspecs['xx'] = record(children='*', vells=[0])
      self.groupspecs['xy'] = record(children='*', vells=[1])
      self.groupspecs['yx'] = record(children='*', vells=[2])
      self.groupspecs['yy'] = record(children='*', vells=[3])

    # Finished:
    # print self.help()
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=False):  
    """
    Class-specific re-implementation. It allows the specification
    of one or more specific plotspecs.
    """
    ps = []

    if True:
      # Used for operations (e.g. plotting) on separate correlations.
      # Its children are assumed to be 2x2 tensor nodes (4 vells each).
      ps.append(record(xy='{xx}',
                       legend='XX',
                       color=self.standard('color','b'),
                       marker=self.standard('marker','d'),
                       markersize=10))
      ps.append(record(xy='{xy}',
                       ignore='abs({xy})>4',
                       # ignore='abs({yy})>4',
                       legend='XY',
                       color='magenta',
                       markersize=10,
                       annotate=False))
      ps.append(record(xy='{yx}',
                       legend='YX',
                       color='green', 
                       marker='cross',
                       annotate=False))
      ps.append(record(xy='{yy}',
                       ignore='abs({yy})>4',
                       legend='YY: \expr',
                       color='blue',
                       markersize=10))

    # Finished:
    self.plotspecs['graphics'] = ps

    self.plotspecs.setdefault('markersize', 20)
    self.plotspecs.setdefault('xlabel', 'real part')
    self.plotspecs.setdefault('ylabel', 'imag part')
    return None





#=====================================================================================
# Make a pylab figure (also called externally):
#=====================================================================================

def make_pylab_figure(plotdefs, figob=None, target=None, trace=False):
  """Make a pylab figure from all items in the plot_defs record.
  The figob is a matplotlib/pylab figure object.
  If the target is 'svg', there are some restrictions.
  """
  # trace = True

  rr = plotdefs                                    # convenience
  if trace:
    print '\n** PyNodePlot.make_pylab_figure(',figob,target,'):'
    # print '** plotdefs: rr =',type(rr),rr.keys()
    print

  # If none supplied, make an empty pylab figure object (e.g. make_svg)
  if figob==None:
    import pylab
    figob = pylab.figure()
       
  # Create an empty Graphics object:
  import Graphics
  grs = Graphics.Graphics(name="pylab_plot",
                          # plot_type='polar',     # does not work in svg...!
                          plot_grid=True,
                          title=rr.title,
                          xlabel=rr.xlabel,
                          ylabel=rr.ylabel)

  # First write any overall legend-string(s):
  if rr.has_key('legend'):
    if isinstance(rr.legend,str):
      rr.legend = [rr.legend]
    if isinstance(rr.legend,(list,tuple)):
      for s in rr.legend:
        grs.legend(s)
      if trace:
        print 'overall legend:',rr.legend

  # Fill the Graphics object with Scatter plots:
  plotype = 'graphics'
  if trace:
    print '** rr[',plotype,'] =',type(rr[plotype]),'\n'

  for i,pd in enumerate(rr[plotype]):
    offset = i*rr.offset
    # offset += -10                    # testing only
    yy = pd.yy
    if not offset==0.0:
      yy = list(yy)                    # tuple does not support item assignment...      
      for i,y in enumerate(yy):
        yy[i] += offset
    labels = len(yy)*[None]
    if pd.annotate:
      labels = pd.labels
    grs1 = Graphics.Scatter(yy=yy, xx=pd.xx,
                            annot=labels,
                            dyy=pd.dyy, dxx=pd.dxx,           
                            ignore=pd.ignore,
                            linestyle=pd.linestyle,
                            marker=pd.marker,
                            markersize=pd.markersize,
                            fontsize=pd.fontsize,
                            plot_circle_mean=pd.plot_circle_mean,
                            plot_ellipse_stddev=pd.plot_ellipse_stddev,
                            color=pd.color)
    grs.add(grs1)

    # Write the plotdef legend-string(s):
    if not isinstance(pd.legend,(list,tuple)):
      pd.legend = [pd.legend]
    for legend in pd.legend:
      if not offset==0.0:
        if legend==None: legend = 'offset'
        if not isinstance(legend,str): legend = str(legend)
        if offset>0.0: legend += ' (+'+str(offset)+')'
        if offset<0.0: legend += ' ('+str(offset)+')'
      grs.legend(legend, color=pd.color)
    if trace:
      print grs1.oneliner(),':',pd.legend

  # Plot window (if relevant):
  if True:
    grs.kwupdate(**dict(xmin=rr['xmin'], xmax=rr['xmax'],
                        ymin=rr['ymin'], ymax=rr['ymax']))
  if True:
    grs.kwupdate(**dict(include_origin=rr['include_origin'],
                        include_xaxis=rr['include_xaxis'],
                        include_yaxis=rr['include_yaxis']))

  if trace:
    print '********* grs is ', grs
    print grs.oneliner()
    # grs.display('pylab_plotter: make_plot()')

  # Use the JEN Figure class to make a pylab plot,
  import Figure
  fig = Figure.Figure(nrow=1, ncol=1)   
  fig.add(grs)
  fig.make_plot(figob=figob, show=True, trace=trace)

  # Finished: Return the JEN Figure object (e.g. for make_svg()).
  return fig











#=====================================================================================
# pynode_Plot() convenience function (preferred alternative to derived classes)
#=====================================================================================


def pynode_Plot (ns, nodes=None, groupspecs=None,
                 plotspecs=None, labels=None,
                 nodename=None, quals=None, kwquals=None,
                 **kwargs):
  """
  Convenience function to create and return a MeqPyNode of class PyNodePlot.
  Syntax:
  .   import PyNodePlot as PNP
  .   pynode = PNP.pynode_Plot (ns, nodes, groupspecs=None,
  .                             plotspecs=None, labels=None,
  .                             nodename=None, quals=None, kwquals=None,
  .                             **kwargs)
  Mandatory arguments:
  - ns:          nodescope
  - nodes:       list of (child) nodes whose results are to be used.
  .              NB: Some or all of these child nodes may be other pynodes of
  .              the PyNodeNamedGroups class. The named groups in their results
  .              will be copied to the new pynode. This mechanism allows concatenation
  .              of PyNodeNamedGroups pynodes, which is very powerful.
  Optional arguments:
  - groupspecs:  group specification(s) may have different types:
  .              - string (e.g. 'XXYY'): convenient way to specify standard plots
  .              - record(): (advanced use) a valid groupspecs record 
  .              - None: (if children are PyNodeNamedGroups pynodes)
  - plotspecs:   record with further plot specification(s).
  .                (advanced use, to be elaborated)
  - labels:      list of labels for the node results. If not supplied, or the wrong
  .                length, they will be derived from the node names.
  - nodename:    name of the resulting pynode
  - quals:       list of nodenamed qualifiers [=None]
  - kwquals:     dict of nodename keyword qualifiers [=None]
  - **kwargs:    Standard plots (e.g. 'XXYY') may be customized by means of keyword arguments.
  .              They override default plotspecs values like xlabel, ylabel, title etc.

  The fun is in the combination of groupspecs [=None] and plotspecs [=None].
  There are various possibilities:
  
  - gs=string, ps=None:   One of the standard plots (e.g. gs='XXYY') -> gs and ps. 
  - gs=None, ps=None:     The simplest possible case: interpreted as gs='YY'
  - gs=None, ps=string:   Assume that the child nodes are pynodes containing named groups.
  .                       A standard ps string specified how they are to be plotted.
  - gs=None, ps=dict:     The same, but ps specifies a more advanced plot.
  - gs=dict, ps=dict:     Black-belt: User defined groups, and user-defined plots.  
  - 
  
  """

  trace = False
  # trace = True

  if not isinstance(nodename, str):
    nodename = 'pynode_Plot'
  else:
    nodename = 'pynode_Plot_'+nodename

  ps = plotspecs
  gs = None
  if isinstance(groupspecs, str):
    # Certain standard group-specs may be specified by a string:
    nodename += '_'+str(groupspecs)
    gs = PNNG.string2groupspecs(groupspecs, nodes=nodes)
    ps = string2plotspecs(groupspecs, plotspecs=plotspecs)
  elif not isinstance(groupspecs, dict):       # i.e. groupspecs=None
    pass
    # gs = PNNG.string2groupspecs('YY', nodes=nodes)
  else:
    # Assume a valid groupspecs record....? 
    nodename += '___gs'
    gs = groupspecs

  # If no labels specified, derive them from the child nodenames:
  [child_names, labels] = PNNG.child_labels(nodes, labels, trace=False)

  # Condition the plotspecs record (if required):
  if isinstance(plotspecs, str):             # a standard plot.... (does this happen?)
    nodename += '__'+str(plotspecs)   
    ps = string2plotspecs(plotspecs)         
  elif isinstance(ps, dict):                 # assume valid plotspecs
    pass
  else:                                      # e.g. plotspecs==None
    ps = string2plotspecs('YY')
    
  # Update the plotspecs record with any kwargs:
  ps.update(**kwargs)               # this overrides already existing keyword values! 
  ps.setdefault('title',nodename)   # this does NOT overridde any existing (e.g. from kwargs) 

  # Make a unique nodestub:
  stub = EN.unique_stub(ns, nodename, quals=quals, kwquals=kwquals)

  # Make the quickref_help list of strings:
  qhelp = ['']
  qhelp.append('   This pynode has been specified by means of a convenience function:')
  qhelp.append('     import PyNodePlot as PNP')
  qhelp.append('     pynode = PNP.pynode_Plot(ns, nodes,')
  if isinstance(groupspecs, str):
    qhelp.append('                     groupspecs='+str(groupspecs)+',')
  else:
    qhelp.append('                     groupspecs='+str(type(groupspecs))+',')
  qhelp.append('                     plotspecs='+str(type(plotspecs))+',')
  for key in kwargs.keys():
    qhelp.append('                    '+str(key)+'='+str(kwargs[key])+',')
  qhelp.append('                    )')
  qhelp.append('   NB: Note the customisation by means of **kwargs.')
  qhelp.append('')
  qhelp.append('   The convenience function has defined the actual MeqPyNode:')
  qhelp.append('     stub = EasyNode.unique_stub(ns,nodename,quals,kwquals) -> '+str(stub))
  qhelp.append('     pynode = stub << Meq.PyNode(')
  qhelp.append('                    children=nodes,')
  qhelp.append('                    child_labels=labels,')
  qhelp.append('                    child_names=child_names,')
  qhelp.append('                    plotspecs=ps,')
  qhelp.append('                    groupspecs=gs,')
  qhelp.append('                    class_name=pyNodePlot,')
  qhelp.append('                    module_name='+str(__file__)+')')
  qhelp.append('')
  qhelp.append('   in which:')
  if isinstance(nodes,(list,tuple)):
    qhelp.append('       nodes (list) = '+str(nodes[0])+' ... ('+str(len(nodes))+')')
  else:
    qhelp.append('       nodes = '+str(nodes))
  if isinstance(labels,(list,tuple)):
    qhelp.append('       labels (list) = '+str(labels[0])+' ... ('+str(len(labels))+')')
  else:
    qhelp.append('       nodes = '+str(nodes))
  qhelp.append('       ps (record) = '+str(ps))
  qhelp.append('       gs (record) = '+str(gs))
  qhelp.append('')
    
  # Create the PyNode:
  pynode = stub << Meq.PyNode(children=nodes,
                              child_labels=labels,
                              child_names=child_names,
                              groupspecs=gs,
                              plotspecs=ps,
                              quickref_help=qhelp,
                              class_name='PyNodePlot',
                              module_name=__file__)
  if trace:
    print '->',str(pynode)
  return pynode


#-------------------------------------------------------------------

def kwargs2legend(**kwargs):
  """
  Helper function to turn the given keyword arguments into a list of strings,
  and attach them as kwargs['legend']. The result may be given to pyNode_Plot()
  and will appear as legends on the plot. Used in QR_PyNodePlot.py etc.
  """
  ss = ['Keyword arguments used:']
  legend = None
  for key in kwargs.keys():
    v = kwargs[key]
    if key=='legend':
      legend = v
    s = ' - '+str(key)+' = '
    if isinstance(v,str):
      s += '\''+str(v)+'\''
    else:
      s += str(v)
    ss.append(s)
              
  if isinstance(legend,(list,tuple)):
    ss.extend(legend)
  elif isinstance(legend,str):
    ss.append(legend)
  kwargs['legend'] = ss
  return kwargs


#--------------------------------------------------------------------------------------

def string2plotspecs(ss, plotspecs=None, trace=False):
  """
  Make a plotspecs record from the given string spec.
  If input plotspecs is a record, just add to it.
  Recognized strings are:
  - Y or YY:   Plot group {y} against index nr (child no)
  - XY:        Plot group {y} vs group {x}
  - XYZ:       Same as XY, but markersize controlled by group {z}
  - XXYYZZ:    Same as XYZ 
  - VELLS_ijk: Vells indices i[jk] control groups {x},{y},{z}
  - XXYY:      Assume single list of equal nrs of x,y nodes
  - VIS22:     Assume groups {xx},{xy},{yx},{yy}
  - VIS22C:     Assume groups {rr},{rl},{lr},{ll}
  """

  # Prepare the output plotspecs record (ps):
  ps = record()
  if isinstance(plotspecs,dict):        # given by the user         
    ps = plotspecs                      # just add new items
  ps.setdefault('graphics',[])
  if not isinstance(ps.graphics,list):
    ps.graphics = []
  ps.setdefault('xlabel','{x}')
  ps.setdefault('ylabel','{y}')

  # Standard graphics subplot records (used below): 
  gy = record(y='{y}', legend='y=yexpr')
  gxy = record(x='{x}', y='{y}', legend=['x=xexpr','y=yexpr'])
  gcxy = record(x='{y}.real', y='{y}.imag')
  gxyz = record(x='{x}', y='{y}', z='{z}', legend=['x=xexpr','y=yexpr','z=zexpr'])

  # Convert the input string (ss) into sub-plot record(s):
  if ss in ['YY']:
    ps.graphics.append(gy)
    ps.xlabel = 'child no'
  elif ss in ['XX']:
    ps.graphics.append(gy)                            # .....??
    ps.xlabel = 'child no'
  elif ss in ['ZZ']:
    ps.graphics.append(gy)                            # .....??
    ps.xlabel = 'child no'

  elif ss in ['CY']:
    ps.graphics.append(gcxy)          # x={y}.real and y={y}.imag (1 group)
    ps.xlabel = 'real part of: {y}'
    ps.ylabel = 'imag part of: {y}'
  elif ss in ['CXY']:
    # NB: This does not work (yet), see string2groupspecs()
    ps.graphics.append(gxy)           # x={x} and y={y} (2 groups)
    ps.xlabel = 'real'
    ps.ylabel = 'imag'

  elif ss in ['XXYY','XY']:
    ps.graphics.append(gxy)

  elif ss in ['XXYYZZ','XYZ']:
    ps.graphics.append(gxyz)
    ps.zlabel = 'z'

  elif 'VELLS_' in ss:
    vv = ss.split('VELLS_')[1]                 # VELLS_34 -> vv = '34'
    if len(vv)==1:
      ps.graphics.append(gy)
      ps.xlabel = 'child no'
      ps.ylabel = 'vells['+vv[0]+']'
    elif len(vv)==2:
      ps.graphics.append(gxy)
      ps.xlabel = 'vells['+vv[0]+']'
      ps.ylabel = 'vells['+vv[1]+']'
    elif len(vv)==3:
      ps.graphics.append(gxyz)
      ps.xlabel = 'vells['+vv[0]+']'
      ps.ylabel = 'vells['+vv[1]+']'
      ps.zlabel = 'vells['+vv[2]+']'

  elif 'VIS22' in ss:
    ps =  string2plotspecs_VIS22(ss, trace=trace)

  if trace:
    print '\n** string2plotspecs(',ss,'):\n    ',ps,'\n'
  return ps

#-------------------------------------------------------------------------------------

def string2plotspecs_VIS22 (ss, trace=False):
  """
  Special case....
  See also PyNodePlotVIS22.py
  """
  rr = PNNG.string2record_VIS22 (ss, trace=trace)
  ps = record(graphics=[])
  ii = rr.stokes                              # stokes (IQUV or QUV)
  if len(ii)==0:
    ii = rr.corrs                             # corrs (XX,YY etc)
  for i in ii:
    psc = record(y=rr.expr[i],                # keep as complex values, i.e. NOT xy=..
                 color=rr.color[i],
                 legend=rr.name[i]+': yexpr',
                 marker=rr.marker[i],
                 markersize=rr.markersize[i],
                 annotate=rr.annotate[i])
    if trace:
      print '-',i,psc
    ps.graphics.append(psc)
  ps.xlabel = rr.xlabel
  ps.ylabel = rr.ylabel
  ps.plot_circle_mean = True
  return ps


#=====================================================================================
# Make a test-forest:
#=====================================================================================
def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  viewer = 'Pylab Plotter'
  cc = []

  nodes = EB.cloud(ns,'n6s2')

  if False:
    # The simplest possible case:
    node = pynode_Plot(ns, nodes)
    Meow.Bookmarks.Page('Plot').add(node, viewer=viewer)
    Meow.Bookmarks.Page('Plot_state_record').add(node, viewer="Record Browser")
    cc.append(node)

  if True:
    node = pynode_Plot(ns, nodes+nodes, groupspecs='XXYY')
    Meow.Bookmarks.Page('XXYY').add(node, viewer=viewer)
    Meow.Bookmarks.Page('XXYY_state_record').add(node, viewer="Record Browser")
    cc.append(node)
  
  if False:
    # Plotting of concatenated pynodes:
    node = PNNG.pynode_NamedGroup(ns, nodes, groupspecs='XX')
    Meow.Bookmarks.Page('XGroup').add(node, viewer="Record Browser")
    cc.append(node)
    node = PNNG.pynode_NamedGroup(ns, nodes, groupspecs='YY')
    Meow.Bookmarks.Page('YGroup').add(node, viewer="Record Browser")
    cc.append(node)
    # Concatenate the pynodes in cc:
    node = pynode_PlotXY(ns, cc, 'concat')
    Meow.Bookmarks.Page('concat').add(node, viewer=viewer)
    Meow.Bookmarks.Page('concat_state_record').add(node, viewer="Record Browser")
    cc.append(node)
    
   
  # Finished:
  ns['rootnode'] << Meq.Composer(*cc)
  return True

#--------------------------------------------------------------------

def _define_forest_old (ns,**kwargs):
  """Make trees with the various pyNodes"""

  viewer = "Svg Plotter"
  viewer = "Pylab Plotter"

  time = ns['time'] << Meq.Time()
  cc = []
  labels = []
  n = 6
  for i in range(n):
    vv = []
    for j,corr in enumerate(['xx','xy','yx','yy']):
      v = (j+1)+10*(i+1)
      v = complex(i,j)
      v = ns[corr](i)(j) << v
      v = ns[corr](i) << Meq.Add(v,time)
      vv.append(v)
    cc.append(ns['child'](i) << Meq.Composer(*vv))
    labels.append('c'+str(i))

  gs = None
  ps = None
  # labels = None

  if False:
    # Optional: make concatenation pynode:
    gs = None
    ps = None
    # gs = record(concat=record(vells=[2]))
    # ps = record(make_svg=False)
    ns['concat'] << Meq.PyNode(children=cc, child_labels=labels,
                               class_name='PyNodePlot',
                               groupspecs=gs,
                               plotspecs=ps,
                               module_name=__file__)
    cc.append(ns['concat'])
    # cc.insert(0,ns['concat'])
    # cc.insert(2,ns['concat'])
    Meow.Bookmarks.Page('concat').add(ns['concat'], viewer=viewer)


  # Make the group specification record:
  gs = None
  # gs = record(gs0=record(children=range(1,3)))
  # gs = record(gs0=record(children='2/3', vells='*'))
  # gs = record(gs0=record(children=range(1,3), vells=[0,1]))
  # gs = record(gs0=record(children=range(1,3), vells=2))

  # Make the plot specification record:
  ps = None
  # ps = record(title='test')
  # ps = record(title='test', graphics=[record(y='{a}'), record(x='{b}')])
  # ps = record(title='test', graphics=[record(xy='{xx}'))])

  ns['rootnode'] << Meq.PyNode(children=cc,
                               child_labels=labels,
                               # class_name='PyNodePlot',
                               class_name='ExampleDerivedClass',
                               groupspecs=gs,
                               plotspecs=ps,
                               module_name=__file__)
  # Meow.Bookmarks.Page('pynode').add(ns['rootnode'], viewer="Record Viewer")
  Meow.Bookmarks.Page('pynode').add(ns['rootnode'], viewer=viewer)

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


if True:
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

  print '\n** Start of standalone test of: PyNodePlot.py:\n' 
  ns = NodeScope()

  nodes = EB.cloud(ns,'n64s2')

  if True:
    pynode = pynode_Plot(ns, nodes)

  if False:
    pynode = pynode_Plot(ns, nodes, 'user')

  if False:
    xx = pynode_XGroup(ns, nodes)
    yy = pynode_YGroup(ns, nodes)
    if False:
      concat = pynode_PlotXY(ns, [xx,yy], 'concat')
    
  
  _define_forest(ns);
  ns.Resolve();

  print '\n** End of standalone test of: PyNodePlot.py:\n' 

#========================================================================


