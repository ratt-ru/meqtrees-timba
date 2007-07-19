# Author : Paul Kemper (PXK)
#
# History:
# - 2006.10.23: creation
# - 2006.10.24: added EJones - wsrt beam cos^3(pi/2 rD/lambda)
# - 2006.10.25: made beam strached for X- and Y-feed direction
# - 2006.10.26: added transient in time and frequency
# - 2006.10.27: added moving source -- isn't working yet with Meow
#               since Meow.LMDirection(ns,name,l,m) expects numeric
#               values for 'l' and 'm'
# - 2006.10.30: added job that creates image and opens imager (not
#               working yet
# - 2006.10.31: created pxk_tools.py
#               created pxk_manual.py -- to simulate without Meow
#               manually added moving source to pxk_manual.py added
#               PJones
# - 2006.11.01: added possibility to write residuals
#               added possibility to read in MS
# - 2006.11.02: added possibility to write residuals WITH beam applied
#               to model, uncorrupted sources
# - 2006.11.06: splitted pxk_sourcelist.py from this file
# - 2006.11.07: moved all Jones matrices to pxk_jones.py
#               added RJones: Errors In Maps
# - 2006.11.08: added QJones to pxk_jones.py: for test purposes only!
#               added DJones to pxk_jones.py
# - 2006.11.17: separated uv-plane from image-plane effects in JM
# - 2006.11.27: moved creation of truesky to define forest
# - 2006.11.29: added possibility to auto-scale F.O.V.
# - 2006.12.04: added input improvements (for corruptions/channels)
# - 2006.12.05: improved automatic selection of FOV dependent on name
#               of MS.




# standard preamble
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

from   Timba.TDL  import *
from   Timba.Meq  import meq
import math
import Meow

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,60,120,240,720]) 
Meow.Utils.include_imaging_options()
TDLCompileMenu("JONES             :",
               TDLCompileOption('applyE', "E",False),
               TDLCompileOption('applyF', "F",False),
               TDLCompileOption('applyZ', "Z",False),
               TDLCompileOption('applyT', "T",False),
               TDLCompileOption('applyP', "P",False),
               TDLCompileOption('applyB', "B",False),
               TDLCompileOption('applyD', "D",False),
               TDLCompileOption('applyG', "G",False),
               TDLCompileOption('applyR', "R",False),
               TDLCompileOption('applyM', "M",False))

# FOV: LOFAR: 9.5 deg @ 30MHz - 1.4 deg @ 240MHz
TDLCompileOption('arcmin', "FOV (arcmin)      ",
                 ['auto', 1,2,5,10,15,30,60,120,240, 480, 600, 1200],default=0)
TDLCompileOption('antennas',  "antennas          ",
                 [14, 27, 32, 77], default=0) 
TDLCompileOption('channels',  "channels          ",
                 [32, 64], default=0) 
TDLCompileOption('data_input',"input             ", ['model', 'data']),
TDLCompileOption('residual',  "residual          ",[False, True])

ANTENNAS   = range(1,antennas+1)

# extra imports
import random
import pxk_manual
import pxk_sourcelist
import pxk_tools
from   pxk_jones  import *
TDLCompileOption('empty_line'," ", False),






########################################################################
def _define_forest (ns):
  print "\n____________________________________________________________"

  global maxrad                             # set global maxrad
  array       = Meow.IfrArray(ns,ANTENNAS)  # create Array object
  observation = Meow.Observation(ns)        # create Observation object
  patch       = Meow.Patch(ns,'predict', observation.phase_centre) 
  model       = Meow.Patch(ns,'truesky', observation.phase_centre)

  
  # create source list
  slist       = pxk_sourcelist.SourceList(ns, kind="grid", nsrc=1,
                                          lm0=(1E-100,0),dlm=(180,180))
  s_all       = slist.copy()
  maxrad      = slist.maxrad
 

  # apply source-DE-pendent image-plane effects
  if applyE:
    slist = EJones(ns,slist)
    s_all = EJones(ns,s_all, residual=1)
    pass
  if applyF: slist = FJones(ns,slist,array, observation)
  if applyZ: slist = ZJones(ns,slist,array, observation)
  if applyT: pass
  patch.add (*slist.sources)
  model.add (*s_all.sources)

  # apply source-IN-dependent uv-plane effects
  if applyP: patch = PJones(ns,patch,array, observation)
  if applyB: patch = BJones(ns,patch,array)
  if applyD: patch = DJones(ns,patch,array)
  if applyG: patch = GJones(ns,patch,array)
  if applyR: patch = RJones(ns,patch,array, "3.7")
  if applyM:
    patch = MJones(ns,patch,array, parts=channels)
    model = MJones(ns,model,array, parts=channels, residual=1)
    pass
  
  # create set of nodes to compute visibilities
  predict = patch.visibilities(array,observation) 
  truesky = model.visibilities(array,observation)
  
  write_data(ns, array, observation, predict, truesky)
  pass




########################################################################
def get_data(ns, array):
  # get source data from MS
  if data_input=='data':
    for p,q in array.ifrs():
      ns.spigot(p,q) << Meq.Spigot(
        input_column='DATA', station_1_index = p-1, station_2_index = q-1)
      pass
    pass
  pass


def write_data (ns, array, observation, predict, model=None):
  """ Create nodes for writing the data. If residual==1, then model
  must also be supplied.
  """
  if residual:
    print "___ Creating residuals nodes"
    output      = ns.residual
    for p,q in array.ifrs(): output(p,q) << predict(p,q) - model(p,q)
    pass
  else:
    print "___ Creating corrupted nodes"
    output = predict
    pass

  # attach visibilities to sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(output(p,q),
                             station_1_index=p-1,
                             station_2_index=q-1, output_col='DATA') 
    pass
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in array.ifrs()])
  pass




########################################################################
def _tdl_job_1_simulate_MS (mqs,parent):
  """ Simulate the MS """
  req = Meow.Utils.create_io_request() 
  req.input.python_init = '~/Timba/WH/contrib/PXK/SIM/pxk_visheader.py'
  # execute    
  mqs.execute('vdm',req,wait=False) 
  pass

  
def _tdl_job_2_make_image (mqs,parent):
  """ Use the AIPS++ imager to image the MS """
  FOV          = pxk_tools.calc_FOV(arcmin, maxrad)
  npix         = 512.0
  cellsize     = str(FOV/npix)+"arcsec"  # cellsize*npix = FOV
  Meow.Utils.make_dirty_image(npix     = npix,
                              cellsize = cellsize,
                              channels = [channels,1,1],
                              msselect="ANTENNA1 != ANTENNA2") 
  pass
  

def _tdl_job_3_make_movie (mqs,parent):
  """ Use AIPS++ and karma to make a movie """
  FOV          = pxk_tools.calc_FOV(arcmin, maxrad)
  npix         = 512.0
  cellsize     = str(FOV/npix)+"arcsec"  # cellsize*npix = FOV

  import os
  import os.path
  print Meow._meow_path
  script_name = os.path.join("./SCRIPTS/",'time_movie.g');
  script_name = os.path.realpath(script_name);  # glish don't like symlinks...
  args = [ 'glish','-l',
           script_name,
           Meow.Utils.output_column,
           'ms='      + Meow.Utils.msname,
           'mode='    + 'mfs',
           'weight='  + Meow.Utils.imaging_weight,
           'stokes='  + Meow.Utils.imaging_stokes,
           'npix='    + str(npix),
           'cell='    + cellsize,
           'msselect='+"ANTENNA1 != ANTENNA2"
           ];
  print args;
  os.spawnvp(os.P_NOWAIT,'glish',args);

  pass
  


# 'python script.tdl'
if __name__ == '__main__':
  ns = NodeScope() 
  _define_forest(ns) 
  # resolves nodes
  ns.Resolve()   
  print len(ns.AllNodes()),'nodes defined' 
  pass
