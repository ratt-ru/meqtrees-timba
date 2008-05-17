# file: ../contrib/JEN/pylab/AGW/PyNodePlotXY_agw.py

# Author: J.E.Noordam
# 
# Short description:
#   PyNode classes for making x-y plots
#
# History:
#    - 29 apr 2008: creation
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
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba.Meq import meqds
import Meow.Bookmarks

# from Timba import pynode
import PyNodePlot

import math
# import inspect
# import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;



#========================================================================
# Base-class for x-y plots
#========================================================================

class PlotXY (PyNodePlot.PyNodePlot):
  """Base-class for classes that make x-y plots"""

  def __init__ (self, *args, **kwargs):
    PyNodePlot.PyNodePlot.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base-class for a range of classes that plot the results of one set
    of children against another set, in an x-y plot. The derived classes
    differ in the way the children are ordered. In this base-class, the
    children are assumed to be tensor-nodes (x,y). 
    """
    ss = self.attach_help(ss, PlotXY.help.__doc__,
                          classname='PlotXY',
                          level=level, mode=mode)
    return PyNodePlot.PyNodePlot.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Its children are assumed to be tensor nodes (2 vells each).
    self.groupspecs['x'] = record(children='*', vells=[0])
    self.groupspecs['y'] = record(children='*', vells=[1])

    # Finished:
    print self.help()           # temporary, for testing
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):
    """Make plotspec record.
    """
    ps = []
    ps.append(record(x='{x}', y='{y}'))
    self.plotspecs['graphics'] = ps

    self.plotspecs.setdefault('xlabel', 'x')
    self.plotspecs.setdefault('ylabel', 'y')
    self.plotspecs.setdefault('legend', None)
    self.plotspecs.setdefault('annotate', True)
    self.plotspecs.setdefault('plot_sigma_bars', True)
    return None

#========================================================================
# Base-class for x-y-z plots
#========================================================================

class PlotXYZ (PyNodePlot.PyNodePlot):
  """Base-class for classes that make x-y-z plots"""

  def __init__ (self, *args, **kwargs):
    PyNodePlot.PyNodePlot.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base-class for a range of classes that plot the results of one set
    of children against another set, in an x-y plot. The derived classes
    differ in the way the children are ordered. In this base-class, the
    children are assumed to be tensor-nodes (x,y). 
    """
    ss = self.attach_help(ss, PlotXYZ.help.__doc__,
                          classname='PlotXYZ',
                          level=level, mode=mode)
    return PyNodePlot.PyNodePlot.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Its children are assumed to be tensor nodes (3 vells each).
    self.groupspecs['x'] = record(children='*', vells=[0])
    self.groupspecs['y'] = record(children='*', vells=[1])
    self.groupspecs['z'] = record(children='*', vells=[2])

    # Finished:
    print self.help()           # temporary, for testing
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):
    """Make plotspec record.
    """
    ps = []
    ps.append(record(x='{x}', y='{y}', z='{z}'))
    self.plotspecs['graphics'] = ps

    self.plotspecs.setdefault('xlabel', 'x')
    self.plotspecs.setdefault('ylabel', 'y')
    self.plotspecs.setdefault('legend', None)
    self.plotspecs.setdefault('annotate', True)
    self.plotspecs.setdefault('plot_sigma_bars', False)
    return None



#========================================================================
# Classes derived from PlotXY:
#========================================================================

class PlotXXYY (PlotXY):
  """Derived from PlotXY"""

  def __init__ (self, *args, **kwargs):
    PlotXY.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Its children are assumed to come in two concatenated lists:
    First the x-children, then the y-children.
    """
    ss = self.attach_help(ss, PlotXXYY.help.__doc__,
                          classname='PlotXXYY',
                          level=level, mode=mode)
    return PlotXY.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Its children are assumed to be in two concatenated lists:
    # (and have a single vells...)
    self.groupspecs['x'] = record(children='1/2')
    self.groupspecs['y'] = record(children='2/2')

    # Finished:
    print self.help()           # temporary, for testing
    return None


#=====================================================================

class PlotCXY (PlotXY):
  """Derived from PlotXY"""

  def __init__ (self, *args, **kwargs):
    PlotXY.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Its children are assumed to be two pynodes of type PyNodeNamedGroups,
    each with one named group named 'x' and 'y' respectively. 
    """
    ss = self.attach_help(ss, PlotCXY.help.__doc__,
                          classname='PlotCXY',
                          level=level, mode=mode)
    return PlotXY.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Finished:
    print self.help()           # temporary, for testing
    return None





#========================================================================
# Classes derived from PlotXYZ:
#========================================================================

class PlotXXYYZZ (PlotXYZ):
  """Derived from PlotXYZ"""

  def __init__ (self, *args, **kwargs):
    PlotXYZ.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Its children are assumed to come in two concatenated lists:
    First the x-children, then the y-children.
    """
    ss = self.attach_help(ss, PlotXXYYZZ.help.__doc__,
                          classname='PlotXXYYZZ',
                          level=level, mode=mode)
    return PlotXYZ.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Its children are assumed to be in three concatenated lists:
    # (and have a single vells...)
    self.groupspecs['x'] = record(children='1/3')
    self.groupspecs['y'] = record(children='2/3')
    self.groupspecs['z'] = record(children='3/3')

    # Finished:
    print self.help()           # temporary, for testing
    return None






#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  time = ns['time'] << Meq.Time()
  freq = ns['freq'] << Meq.Freq()

  xx = []          # list of nodes that represent x-coors
  yy = []          # list of y-nodes
  zz = []          # list of z-nodes
  ttxy = []        # list of tensor nodes with 2 vells (x,y)
  ttxyz = []       # list of tensor nodes with 3 vells (x,y,z)
  xyxy = []        # concatenation of node-pairs (x,y)
  xyzxyz = []      # concatenation of node-trios (x,y,z)
  xxyy = []        # first all x-nodes, then all y-nodes
  xxyyzz = []      # same, followed by all z-nodes

  tt_labels = [] 
  xx_labels = []
  yy_labels = []
  zz_labels = []
  xxyy_labels = []
  xxyyzz_labels = []
  xyxy_labels = []
  xyzxyz_labels = []

  n = 7
  for i in range(n):
    x = ns['x'](i) << 11*(i-2)+time
    y = ns['y'](i) << 12*(i-1)+freq
    z = ns['z'](i) << (i-3)

    xlabel = 'x'+str(i)       # x-node label
    ylabel = 'y'+str(i)
    zlabel = 'z'+str(i)
    tlabel = 't'+str(i)       # tensor node label

    xy = ns['xy'](i) << Meq.Composer(x,y)
    xyz = ns['xyz'](i) << Meq.Composer(x,y,z)
    ttxy.append(xy)                
    ttxyz.append(xyz)                
    tt_labels.append(tlabel)

    xx.append(x)                
    xx_labels.append(xlabel)

    yy.append(y)                
    yy_labels.append(ylabel)

    zz.append(z)                
    zz_labels.append(zlabel)

    xyxy.extend([x,y])                
    xyxy_labels.extend([xlabel,ylabel])                

    xyzxyz.extend([x,y,z])                
    xyzxyz_labels.extend([xlabel,ylabel,zlabel])                


  xxyy = xx+yy
  xxyy_labels = xx_labels + yy_labels
  xxyyzz = xx+yy+zz
  xxyyzz_labels = xx_labels + yy_labels + zz_labels


  # Bundle things, to minimize browser clutter:
  bb = []
  bb.append(ns['xx'] << Meq.Composer(*xx))
  bb.append(ns['yy'] << Meq.Composer(*yy))
  bb.append(ns['zz'] << Meq.Composer(*zz))
  bb.append(ns['ttxy'] << Meq.Composer(*ttxy))
  bb.append(ns['ttxyz'] << Meq.Composer(*ttxyz))
  bb.append(ns['xxyy'] << Meq.Composer(*xxyy))
  bb.append(ns['xxyyzz'] << Meq.Composer(*xxyyzz))
  bb.append(ns['xyxy'] << Meq.Composer(*xyxy))
  bb.append(ns['xyzxyz'] << Meq.Composer(*xyzxyz))
  ns['bb'] << Meq.Composer(*bb)



  #---------------------------------------------------------------------
  # Make the pynode(s):
  pp = []
  pypage = Meow.Bookmarks.Page('pynode')
  viewer = "Pylab Plotter"
  # viewer = "Svg Plotter"

  if True:
    class_name = 'PlotXY'
    ps = record(xlabel='xx', ylabel='ert', title='nnn',
                legend='fgh: \expr',
                plot_sigma_bars=True, annotate=True, markersize=20)
    ps = None
    pynode = ns[class_name] << Meq.PyNode(children=ttxy,
                                          child_labels=tt_labels,
                                          class_name=class_name,
                                          plotspecs=ps,
                                          module_name=__file__)
    pp.append(pynode)
    pypage.add(ns[class_name], viewer=viewer)
    Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)


  if False:
    class_name = 'PlotXYZ'
    pynode = ns[class_name] << Meq.PyNode(children=ttxyz,
                                          child_labels=tt_labels,
                                          class_name=class_name,
                                          module_name=__file__)
    pp.append(pynode)
    pypage.add(ns[class_name], viewer=viewer)
    Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)


  if True:
    class_name = 'PlotXXYY'
    pynode = ns[class_name] << Meq.PyNode(children=xxyy,
                                          child_labels=xxyy_labels,
                                          class_name=class_name,
                                          module_name=__file__)
    pp.append(pynode)
    pypage.add(ns[class_name], viewer=viewer)
    Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)

  if False:
    class_name = 'PlotXXYYZZ'
    pynode = ns[class_name] << Meq.PyNode(children=xxyyzz,
                                          child_labels=xxyyzz_labels,
                                          class_name=class_name,
                                          module_name=__file__)
    pp.append(pynode)
    pypage.add(ns[class_name], viewer=viewer)
    Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)


  if False:
    class_name = 'PyNodeNamedGroups'
    module_name = 'PyNodeNamedGroups'
    gxx = ns['gxx'] << Meq.PyNode(children=xx,
                                  child_labels=xx_labels,
                                  groupspecs=record(x=record()),
                                  class_name=class_name,
                                  module_name=module_name)
    gyy = ns['gyy'] << Meq.PyNode(children=yy,
                                  child_labels=yy_labels,
                                  groupspecs=record(y=record()),
                                  class_name=class_name,
                                  module_name=module_name)
    gzz = ns['gzz'] << Meq.PyNode(children=zz,
                                  child_labels=zz_labels,
                                  groupspecs=record(z=record()),
                                  class_name=class_name,
                                  module_name=module_name)

    if False:
      class_name = 'PlotCXY'
      pynode = ns[class_name] << Meq.PyNode(class_name=class_name,
                                            children=[gxx, gyy],
                                            # child_labels=xxyyzz_labels,
                                            module_name=__file__)
      pp.append(pynode)
      pypage.add(ns[class_name], viewer=viewer)
      Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)



  #---------------------------------------------------------------------
  # Finished:
  if len(pp)>0:
    ns['rootnode'] << Meq.Composer(*pp)
  else:
    ns['rootnode'] << Meq.Composer(*bb)
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
    # Timba.TDL._dbg.set_verbose(5);
    ns = NodeScope();
    _define_forest(ns);
    ns.Resolve();
