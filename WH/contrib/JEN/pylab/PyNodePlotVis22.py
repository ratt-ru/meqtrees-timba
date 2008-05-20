# file: ../contrib/JEN/pylab/PyNodePlotVis22.py

# Author: J.E.Noordam
# 
# Short description:
#   PyNode classes for plotting visibilities
#
# History:
#    - 28 apr 2008: creation (from PyNodePlot.py)
#    - Tony's version
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
import random
# import pylab       # not here, but in the class....!


Settings.forest_state.cache_policy = 100;



#=====================================================================================
# The PlotVis22 base class:
#=====================================================================================


class PlotVis22 (PyNodePlot.PyNodePlot):
  """Base class for visibility plotting."""

  def __init__ (self, *args, **kwargs):
    PyNodePlot.PyNodePlot.__init__(self, *args)
    
    self.standard('color',
                  update=record(XX='red', XY='magenta', YX='green', YY='blue',
                                RR='red', RL='magenta', LR='green', LL='blue'))
    self.standard('marker',
                  update=record(XX='circle', XY='cross', YX='cross', YY='circle',
                                RR='circle', RL='cross', LR='cross', LL='circle'))
    self.standard('markersize',
                  update=record(XX=2, XY=3, YX=3, YY=2,
                                RR=2, RL=3, LR=3, LL=2))
    self.standard('fontsize',
                  update=record(XX=7, XY=7, YX=7, YY=7,
                                RR=7, RL=7, LR=7, LL=7))
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
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):
    """Make plotspec records for the 4 correlations
    """
    ps = []
    corr = 'XX'
    ps.append(record(xy='{xx}', legend=corr,
                     color=self.standard('color',corr),
                     marker=self.standard('marker',corr),
                     markersize=self.standard('markersize',corr),
                     fontsize=self.standard('fontsize',corr),
                     annotate=True))
    corr = 'XY'
    ps.append(record(xy='{xy}', legend=corr,
                     color=self.standard('color',corr),
                     marker=self.standard('marker',corr),
                     markersize=self.standard('markersize',corr),
                     fontsize=self.standard('fontsize',corr),
                     annotate=False))
    corr = 'YX'
    ps.append(record(xy='{yx}', legend=corr,
                     color=self.standard('color',corr),
                     marker=self.standard('marker',corr),
                     markersize=self.standard('markersize',corr),
                     fontsize=self.standard('fontsize',corr),
                     annotate=False))
    corr = 'YY'
    ps.append(record(xy='{yy}', legend=corr,
                     color=self.standard('color',corr),
                     marker=self.standard('marker',corr),
                     markersize=self.standard('markersize',corr),
                     fontsize=self.standard('fontsize',corr),
                     annotate=True))
    self.plotspecs['graphics'] = ps

    self.plotspecs.setdefault('plot_circle_mean', True)
    self.plotspecs.setdefault('xlabel', 'real part (Jy)')
    self.plotspecs.setdefault('ylabel', 'imag part (Jy)')
    return None



#========================================================================
#========================================================================

class PlotUV (PyNodePlot.PyNodePlot):
  """Plot uv-coordinates."""

  def __init__ (self, *args, **kwargs):
    PyNodePlot.PyNodePlot.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Plot uv-coordinates. The children are assumed to be tensor-nodes. 
    """
    ss = self.attach_help(ss, PlotUV.help.__doc__,
                          classname='PlotUV',
                          level=level, mode=mode)
    return PyNodePlot.PyNodePlot.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_groupspecs(self, trace=True):  
    """Class-specific re-implementation. It allows the specification
    of one or more specific groupspecs.
    """
    # Its children are assumed to be tensor nodes (2 vells each).
    self.groupspecs['u'] = record(children='*', vells=[0])
    self.groupspecs['v'] = record(children='*', vells=[1])

    # Finished:
    return None

  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):
    """Make plotspec record.
    """
    ps = []
    ps.append(record(x='{u}', y='{v}',
                     plot_sigma_bars=False,
                     annotate=True))
    self.plotspecs['graphics'] = ps
    
    self.plotspecs.setdefault('xlabel', 'u (wavelengths)')
    self.plotspecs.setdefault('ylabel', 'v (wavelengths)')
    return None



#=====================================================================================
# Classes derived from PlotVis22:
#=====================================================================================


class PlotCrossCorrs (PlotVis22):
  """Plot only the cross-corrs, derived from PlotVis22."""

  def __init__ (self, *args, **kwargs):
    PlotVis22.__init__(self, *args)
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Plot only the 2 cross-correlations (xy/rl and yx/lr).
    """
    ss = self.attach_help(ss, PlotVis22.help.__doc__,
                          classname='PlotVis22',
                          level=level, mode=mode)
    return PlotVis22.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):  
    """
    Make plotspec records for the two cross-corrs.
    """
    ps = []
    corr = 'XY'
    ps.append(record(xy='{xy}', legend=corr,
                     color=self.standard('color',corr),
                     marker=self.standard('marker',corr),
                     markersize=self.standard('markersize',corr),
                     fontsize=self.standard('fontsize',corr),
                     annotate=True))
    corr = 'YX'
    ps.append(record(xy='{yx}', legend=corr,
                     color=self.standard('color',corr),
                     marker=self.standard('marker',corr),
                     markersize=self.standard('markersize',corr),
                     fontsize=self.standard('fontsize',corr),
                     annotate=True))
    self.plotspecs['graphics'] = ps

    self.plotspecs.setdefault('annotate', True)
    self.plotspecs.setdefault('plot_circle_mean', True)
    return None



#======================================================================

class PlotIQUV (PlotVis22):
  """Plot Stokes I,Q,U,V visibilities. Derived from PlotVis22."""

  def __init__ (self, *args, **kwargs):
    PlotVis22.__init__(self, *args)

    self.standard('color',
                  update=record(I='red', Q='magenta', U='green', V='blue'))
    self.standard('marker',
                  update=record(I='circle', Q='cross', U='cross', V='plus'))
    self.standard('markersize', update=record(I=2, Q=3, U=3, V=3))
    self.standard('fontsize', update=record(I=7, Q=7, U=7, V=7))
    return None

  #-------------------------------------------------------------------

  def help (self, ss=None, level=0, mode=None):
    """
    Plot the I,Q,U,V visibilities (complex).
    """
    ss = self.attach_help(ss, PlotVis22.help.__doc__,
                          classname='PlotVis22',
                          level=level, mode=mode)
    return PlotVis22.help(self, ss, level=level+1, mode=mode) 


  #-------------------------------------------------------------------

  def define_specific_plotspecs(self, trace=True):  
    """
    Make plotspec records for I,Q,U,iV.
    """
    ps = []
    stokes = 'I'
    ps.append(record(xy='({xx}+{yy})/2',
                     legend='I: \expr',
                     color=self.standard('color',stokes),
                     marker=self.standard('marker',stokes),
                     markersize=self.standard('markersize',stokes),
                     fontsize=self.standard('fontsize',stokes),
                     annotate=True))
    stokes = 'Q'
    ps.append(record(xy='({xx}-{yy})/2',
                     legend='Q: \expr',
                     color=self.standard('color',stokes),
                     marker=self.standard('marker',stokes),
                     markersize=self.standard('markersize',stokes),
                     annotate=False))
    stokes = 'U'
    ps.append(record(xy='({xy}+{yx})/2',
                     legend='U: \expr',
                     color=self.standard('color',stokes),
                     marker=self.standard('marker',stokes),
                     markersize=self.standard('markersize',stokes),
                     annotate=False))
    stokes = 'V'
    ps.append(record(xy='({xy}-{yx})/2',
                     legend='iV: \expr',
                     color=self.standard('color',stokes),
                     marker=self.standard('marker',stokes),
                     markersize=self.standard('markersize',stokes),
                     annotate=False))
    self.plotspecs['graphics'] = ps

    self.plotspecs.setdefault('plot_circle_mean', True)
    self.plotspecs.setdefault('xlabel', 'real part (Jy)')
    self.plotspecs.setdefault('ylabel', 'imag part (Jy)')
    return None








#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  time = ns['time'] << Meq.Time()
  freq = ns['freq'] << Meq.Freq()
  clight = ns['clight'] << 3e8
  pi2 = ns['2pi'] << 2*math.pi
  wvl = ns['lambda'] << freq/clight
  HA = ns['HA'] << time*(math.pi/(12.0*3600.0))
  DEC = ns['DEC'] << math.pi/6.0
  cosHA = ns << Meq.Cos(HA)
  sinHA = ns << Meq.Sin(HA)
  sinDEC = ns << Meq.Sin(DEC)
  sinHAsinDEC = ns << Meq.Multiply(sinHA,sinDEC)
  
  I = ns['stokesI'] << 10.0
  Q = ns['stokesQ'] << -1.0
  U = ns['stokesU'] << 0.5
  iV = ns['stokesV'] << Meq.ToComplex(0.0,0.001)
  lpos = ns['lpos'] << 0.01         # rad
  mpos = ns['mpos'] << 0.001        # rad

  uu = []        # list of uv-pairs (for plotting)
  cc = []
  labels = []
  n = 4
  xpos = range(n)
  for i in range(n-1):
    for j in range(i+1,n):
      basel = ns['basel'](i)(j) << (xpos[j] - xpos[i])
      bwvl = ns['bwvl'](i)(j) << basel/wvl
      u = ns['u'](i)(j) << bwvl*cosHA
      v = ns['v'](i)(j) << bwvl*sinHAsinDEC
      uvlm = ns['ulvm'](i)(j) << Meq.Add(u*lpos,v*mpos)
      karg = ns['karg'](i)(j) << Meq.ToComplex(0.0, pi2*uvlm) 
      K = ns['KJones'](i)(j) << Meq.Exp(karg)
      XX = ns['XX'](i)(j) << (I+Q)
      XY = ns['XY'](i)(j) << (U+iV)
      YX = ns['YX'](i)(j) << (U-iV)
      YY = ns['YY'](i)(j) << (I-Q)
      cps = ns['cps'](i)(j) << Meq.Matrix22(XX,XY,YX,YY)
      coh = ns['coh'](i)(j) << Meq.Multiply(cps,K)
      if True:
        q = 0.1
        noise = ns['noise'](i)(j) << Meq.Matrix22(complex(random.gauss(0,q),random.gauss(0,q)),
                                                  complex(random.gauss(0,q),random.gauss(0,q)),
                                                  complex(random.gauss(0,q),random.gauss(0,q)),
                                                  complex(random.gauss(0,q),random.gauss(0,q)))
        coh = ns['noisy'](i)(j) << Meq.Add(coh,noise)
        

      cc.append(coh)
      labels.append(str(i)+'_'+str(j))
      uv = ns['uv'](i)(j) << Meq.Composer(u,v)
      uu.append(uv)                


  #---------------------------------------------------------------------
  # Make the pynode(s):
  pp = []
  pypage = Meow.Bookmarks.Page('pynode')
  viewer = "Pylab Plotter"

  if True:
    class_names = ['PlotVis22']
    class_names = ['PlotVis22','PlotCrossCorrs','PlotIQUV']
    # class_names = ['PlotIQUV']
    for class_name in class_names:
      gs = None
      ps = None
      pynode = ns[class_name] << Meq.PyNode(children=cc,
                                            child_labels=labels,
                                            class_name=class_name,
                                            # groupspecs=gs,
                                            plotspecs=ps,
                                            module_name=__file__)
      pp.append(pynode)
      pypage.add(ns[class_name], viewer=viewer)
      Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)


  #---------------------------------------------------------------------
  # Optional: uv-coordinates:
  if True:
    class_name = 'PlotUV'
    svg = True
    ps = None
    if svg: ps = record(make_svg=True)                     # just for testing.....
    pynode = ns[class_name] << Meq.PyNode(children=uu,
                                          child_labels=labels,
                                          class_name=class_name,
                                          plotspecs=ps,
                                          module_name=__file__)
    pp.append(pynode)
    pypage.add(ns[class_name], viewer=viewer)
    Meow.Bookmarks.Page(class_name).add(ns[class_name], viewer=viewer)
    if svg: Meow.Bookmarks.Page(class_name+'_SVG').add(ns[class_name], viewer="Svg Plotter")

  else:
    # Bundle them, to limit browser clutter:
    ns['uu'] << Meq.Composer(*uu)


  #---------------------------------------------------------------------
  # Finished:
  ns['rootnode'] << Meq.Composer(*pp)
  return True
  


#=====================================================================================
# Execute a test-forest:
#=====================================================================================

def _test_forest (mqs,parent,wait=False):
  from Timba.Meq import meq
  f1 = 100e6
  f2 = 110e6
  t1 = 0
  t2 = 1000
  cells = meq.cells(meq.domain(f1,f2,t1,t2),
                    num_freq=11,num_time=5);
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
