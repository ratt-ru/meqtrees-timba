# file: ../contrib/JEN/pylab/PyNodePlotVis22.py

# Author: J.E.Noordam
# 
# Short description:
#   PyNode classes for plotting visibilities
#
# History:
#    - 28 apr 2008: creation (from PyNodePlot.py)
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



#=====================================================================================
# The PlotVis22 base class:
#=====================================================================================



class PlotVis22 (PyNodePlot.PyNodePlot):
  """Base class for visibility plotting, derived from PyNodePlot."""

  def __init__ (self, *args, **kwargs):
    PyNodePlot.PyNodePlot.__init__(self, *args)
    self._color = record()
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Base class for visibility plotting, derived from PyNodePlot.
    It specifies four named groups (xx,xy,yx,yy) for the 4 corrs,
    and four plots with standard colors and styles for all corrs.
    """
    ss = self.attach_help(ss, PlotVis22.help.__doc__,
                          classname='PlotVis22',
                          level=level, mode=mode)
    return PyNodePlot.PyNodePlot.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Its children are assumed to be 2x2 tensor nodes (4 vells each).
    self.groupspecs['xx'] = record(children='*', vells=[0])
    self.groupspecs['xy'] = record(children='*', vells=[1])
    self.groupspecs['yx'] = record(children='*', vells=[2])
    self.groupspecs['yy'] = record(children='*', vells=[3])

    # Finished:
    print self.help()
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):  
    """Placeholder for class-specific function, to be redefined by classes
    that are derived from PyNodePlot. Called by ._update_state().
    It allows the specification of one or more specific plotspecs.
    """
    ps = []
    ps.append(record(xy='{xx}', color='red', marker='plus'))
    ps.append(record(xy='{xy}', color='magenta', annotate=False))
    ps.append(record(xy='{yx}', color='green', marker='cross', annotate=False))
    ps.append(record(xy='{yy}', color='blue', markersize=10))
    self.plotspecs['graphics'] = ps

    self.plotspecs['xlabel'] = 'real part (Jy)'
    self.plotspecs['ylabel'] = 'imag part (Jy)'
    # self.plotspecs['title'] = 'title without underscores'
    return None








#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  time = ns['time'] << Meq.Time()
  HArad = ns['HArad'] << time*(math.pi/(12.0*3600.0))
  cosHA = ns['cosHA'] << Meq.Cos(HArad)
  sinHA = ns['sinHA'] << Meq.Sin(HArad)
  DECrad = ns['DECrad'] << math.pi/6.0
  sinDEC = ns['sinDEC'] << Meq.Sin(DECrad)
  
  I = ns['stokesI'] << 10.0
  Q = ns['stokesQ'] << -1.0
  U = ns['stokesU'] << 0.5
  V = ns['stokesV'] << 0.0
  lpos = ns['lpos'] << 0.01         # rad
  mpos = ns['mpos'] << 0.001        # rad

  cc = []
  labels = []
  n = 6
  xpos = range(n)
  for i in range(n-1):
    for j in range(i+1,n):
      dx = xpos[j] - xpos[i]
      u = ns['u'](i)(j) << dx*cosHA
      v = ns['v'](i)(j) << dx*sinHA*sinDEC
      ulvm = ns['ulvm'](i)(j) << Meq.Add()

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
  ns['rootnode'] << Meq.PyNode(children=cc,
                               child_labels=labels,
                               class_name='PlotVis22',
                               groupspecs=gs,
                               plotspecs=ps,
                               module_name=__file__)
  Meow.Bookmarks.Page('pynode').add(ns['rootnode'], viewer="Svg Plotter")

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
