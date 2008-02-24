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

import ChildResult

import inspect
import random


Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='VisuVis22');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;



#=====================================================================================
# The basic VisuVis22 pynode class:
#=====================================================================================



class VisuVis22 (pynode.PyNode):
  """Make a scatter-plot of the means of the results of its children"""


  def __init__ (self, *args, **kwargs):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain','resolution');
    return None
                              
  def get_result (self, request, *children):

    classname = 'VisuVis22'

    # AWG: needed to prevent hangup at 'executing' phase...??
    import matplotlib
    matplotlib.use('SVG')
    
    # Make an Graphics(=Subplot) object that has 4 Graphics objects:
    import Graphics
    grs = Graphics.Scatter(None, name='allcors',
                           title='VisuNodes.'+classname,
                           xlabel='real part', ylabel='imag part',
                           color='red', style='+')
    grs.add(Graphics.Scatter(None, name='XY', color='green', style='x'))
    grs.add(Graphics.Scatter(None, name='YX', color='magenta', style='x'))
    grs.add(Graphics.Scatter(None, name='YY', color='blue', style='+'))
    

    # Accumulate the point(s) representing the child result(s):
    for i,child in enumerate(children):
      # _dprint(0,'- child',i,':',dmi.dmi_typename(child))
      chires = ChildResult.Result(child)     # child is MeqResult class
      # chires.display()
      print '--',i,':',chires.oneliner()
      for icorr in range(grs.len()-1):
        Vells = chires[icorr]                
        print '---',i,icorr,':',Vells.oneliner()
        grs[icorr][0].append(y=Vells.mean(), annot=i,
                             dy=Vells.errorbar(),
                             trace=False)

    # When complete, add the Subplot object to a pylab Figure:
    grs.display('accumulated')
    import Figure        
    fig = Figure.Figure()
    fig.add(grs)
    fig.display()

    # Turn the Figure into an svg string, and attach it to the pynode result:
    svg_list_of_strings = fig.plot(dispose=['svg'], rootname=classname, trace=False)
    result = meq.result()
    result.svg_plot = svg_list_of_strings
    return result





#=====================================================================================
# Make a test-forest:
#=====================================================================================

def _define_forest (ns,**kwargs):
  """Make trees with the various pyNodes"""

  cc = []
  
  if True:
    ns.cx_freqtime << Meq.ToComplex(Meq.Time(),Meq.Freq())

    nstat = 3
    for i in range(nstat-1):
      for j in range(i+1,nstat):
        print '-- (i,j)=',i,j
        XX = ns.XX(i)(j) << Meq.Polar(random.gauss(1.1,0.1),
                                      random.gauss(0.0,1.0))
        YY = ns.YY(i)(j) << Meq.Polar(random.gauss(0.9,0.1),
                                      random.gauss(1.0,0.1))
        XY = ns.XY(i)(j) << Meq.Polar(random.gauss(0.1,0.01),
                                      random.gauss(0.5,0.1))
        YX = ns.YX(i)(j) << Meq.Polar(random.gauss(0.1,0.01),
                                      random.gauss(-0.5,0.1))
        vis22 = ns.vis22(i)(j) << Meq.Matrix22(XX,XY,YX,YY)
        cc.append(vis22)
      
    bookpage = Meow.Bookmarks.Page('pynodes')
    bookpage.add(ns.cx_freqtime, viewer="Result Plotter")                
    pn = []
    for classname in ['VisuVis22']:
      pynode = ns[classname] << Meq.PyNode(children=cc, class_name=classname,
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
  # mqs.execute('rootnode',request,wait=wait);
  a = mqs.meq('Node.Execute',record(name='rootnode',request=request),wait=wait)
  return True


def _tdl_job_sequence (mqs,parent,wait=False):
  from Timba.Meq import meq
  for i in range(5):
    cells = meq.cells(meq.domain(i,i+1,i,i+1),num_freq=20,num_time=10);
    rqid = meq.requestid(i)
    print '\n--',i,rqid,': cells =',cells,'\n'
    # request = meq.request(cells, rqtype='e1');
    request = meq.request(cells, rqid=rqid);
    # mqs.execute('rootnode',request,wait=wait);
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
