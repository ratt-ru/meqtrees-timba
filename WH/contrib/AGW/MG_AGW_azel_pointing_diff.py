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

# This script uses a standard pointing model for AzEl mounted telescopes
# to generate an observation which has been corrupted by pointing errors.
# Adapted from Oleg's workshop script example10-tracking.py
# The script includes the possibility of a parallactic angle track tilt - 
# i.e we simulate a 'sky rotator' error.

from Timba.TDL import *
from Timba.Meq import meq
import math
import random
import numarray

import Meow

from Meow import Bookmarks
import Meow.StdTrees
import sky_models

Settings.forest_state.cache_policy = 100

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=sky_models.imagesize(),channels=[[32,1,1]]));

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = ARCMIN/60;

# define desired half-intensity width of power pattern (HPBW)
# as we are fitting total intensity I pattern (here .021 rad = 74.8 arcmin)
fwhm  = 0.021747 # beam FWHM

def ASKAP_voltage_response(E, lm):
  """This makes the nodes to compute the beam gain, E, given an lm position.
  'lm' is an input node, giving position of source 
  'E' is an output node to which the gain will be assigned""";
  ln_16  = -2.7725887
  # gaussian to which we want to optimize beams
  lmsq = E('lmsq') << Meq.Sqr(lm);
  lsq = E('lsq') << Meq.Selector(lmsq,index=0);
  msq = E('msq') << Meq.Selector(lmsq,index=1);
  lm_sq  = lsq + msq
  E << Meq.Sqrt(Meq.Exp((lm_sq * ln_16)/(fwhm * fwhm)))
  return E

# get Azimuth / Elevation telescope structural errors
TDLCompileMenu('Telescope Maximum Structural Errors - in arcsec',
  TDLOption('AS','Amount by which telescope azimuth axis is South of Vertical',[0,5,10,20],more=float),
  TDLOption('AW','Amount by which telescope azimuth axis is West of Vertical',[0,5,10,20],more=float),
  TDLOption('AZ_EN','Azimuth encoder offset',[0,5,10,20],more=float),
  TDLOption('EL_EN','Elevation encoder offset',[0,5,10,20],more=float),
  TDLOption('NPAE','Amount by which telescope elevation axis is not perpendicular to azimuth axis',[0,5,10,20],more=float),
  TDLOption('EX','Amount by which telescope elevation axis is decentered in X',[0,5,10,20],more=float),
  TDLOption('EZ','Amount by which telescope elevation axis is decentered in Z',[0,5,10,20],more=float),
  TDLOption('CX','Beam Collimation Error X',[0,5,10,20],more=float),
  TDLOption('CY','Beam Collimation Error Y',[0,5,10,20],more=float),
  TDLOption('PW','Parallactic Angle Tilt W',[0,5,10,20],more=float),
  TDLOption('PS','Parallactic Angle Tilt S',[0,5,10,20],more=float),
  TDLOption('GRAV','Gravitational deformation',[0,5,10,20],more=float),
  TDLOption('randomize_axes','Randomize above extremes for each telescope?',[True,False]),
);

# get Azimuth / Elevation telescope random tracking errors
TDLCompileOption("max_tr_error","Max tracking error, arcsec",[0,1,2,5],more=float);
TDLCompileOption("min_tr_period","Min time scale for tracking variation, hours",[0,1],more=float);
TDLCompileOption("max_tr_period","Max time scale for tracking variation, hours",[2,4],more=float);
TDLOption('subtract_perfect_obs','Subtract perfect observation from error observation?',[True,False]),

  
def _define_forest (ns):

  # create an Array object
  num_antennas = 30
  xntd_list = [ str(i) for i in range(1,num_antennas+1) ];
  array = Meow.IfrArray(ns,xntd_list);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);

  # create nodes to compute tracking errors per antenna
  for p in array.stations():
    if max_tr_error > 0.0:
      # to add random errors on top of systematic ones
      # convert random periods of daz/del variation from hours to seconds
      daz = random.uniform(min_tr_period*3600,max_tr_period*3600);
      dell = random.uniform(min_tr_period*3600,max_tr_period*3600);
      # pick a random starting phase for the variations
      daz_0 = random.uniform(0,2*math.pi); 
      del_0 = random.uniform(0,2*math.pi);
      ns.daz(p) << max_tr_error*Meq.Sin(Meq.Time()*(2*math.pi/daz)+daz_0);
      ns.dell(p) << max_tr_error*Meq.Sin(Meq.Time()*(2*math.pi/dell)+del_0);
    else:
      ns.daz(p) << Meq.Constant(0.0)
      ns.dell(p) << Meq.Constant(0.0)

    # get Parallactic Angle for the station
    pa= ns.ParAngle(p) << Meq.ParAngle(observation.phase_centre.radec(), array.xyz(p))
 

    # systematic variations due to telescope axis errors
    ns.AzEl(p) << Meq.AzEl(observation.phase_centre.radec(), array.xyz(p)) 
    ns.Az(p) << Meq.Selector(ns.AzEl(p), index=0)
    ns.El(p) << Meq.Selector(ns.AzEl(p), index=1)
    ns.SinAz(p) << Meq.Sin(ns.Az(p))
    ns.CosAz(p) << Meq.Cos(ns.Az(p))
    ns.SinEl(p) << Meq.Sin(ns.El(p))
    ns.CosEl(p) << Meq.Cos(ns.El(p))
    ns.CosPa(p) << Meq.Cos(pa)
    ns.SinPa(p) << Meq.Sin(pa)

    ns.rot_matrix(p) << Meq.Matrix22(ns.CosPa(p),-1.0 * ns.SinPa(p),ns.SinPa(p),ns.CosPa(p))
    
    if randomize_axes:
      axis_offset_NPAE = random.uniform(-1.0,1.0)
      axis_offset_AW = random.uniform(-1.0,1.0)
      axis_offset_AS = random.uniform(-1.0,1.0)
      axis_offset_AZ_EN = random.uniform(-1.0,1.0)
      axis_offset_EL_EN = random.uniform(-1.0,1.0)
      axis_offset_CX = random.uniform(-1.0,1.0)
      axis_offset_CY = random.uniform(-1.0,1.0)
      axis_offset_PW = random.uniform(-1.0,1.0)
      axis_offset_PS = random.uniform(-1.0,1.0)
      axis_offset_EZ = random.uniform(-1.0,1.0)
      axis_offset_EX = random.uniform(-1.0,1.0)
      axis_offset_GRAV = random.uniform(0.0, 1.0)
    else:
      axis_offset_NPAE = 1.0
      axis_offset_AW = 1.0
      axis_offset_AS = 1.0
      axis_offset_AZ_EN = 1.0
      axis_offset_EL_EN = 1.0
      axis_offset_CX = 1.0
      axis_offset_CY = 1.0
      axis_offset_PW = 1.0
      axis_offset_PS = 1.0
      axis_offset_EX = 1.0
      axis_offset_EZ = 1.0
      axis_offset_GRAV = 1.0

    ns.AZ_EN(p) << Meq.Constant(axis_offset_AZ_EN * AZ_EN)
    ns.EL_EN(p) << Meq.Constant(axis_offset_EL_EN * EL_EN)
    ns.NPAE(p) << Meq.Constant(axis_offset_NPAE * NPAE)
    ns.AW(p) << Meq.Constant(axis_offset_AW * AW)
    ns.AS(p) << Meq.Constant(axis_offset_AS * AS)
    ns.GRAV(p) << Meq.Constant(axis_offset_GRAV * GRAV)
    ns.CX(p) << Meq.Constant(axis_offset_CX * CX)
    ns.CY(p) << Meq.Constant(axis_offset_CY * CY)
    ns.PW(p) << Meq.Constant(axis_offset_PW * PW)
    ns.PS(p) << Meq.Constant(axis_offset_PS * PS)
    ns.EX(p) << Meq.Constant(axis_offset_EX * EX)
    ns.EZ(p) << Meq.Constant(axis_offset_EZ * EZ)

# here are the full pointing equations ...
    ns.AzPoint(p) << ns.daz(p) - ns.AZ_EN(p) * ns.CosEl(p) + ns.NPAE(p) *ns.SinEl(p)  + ns.AW(p) * ns.SinEl(p) * ns.CosAz(p) - ns.AS(p) * ns.SinAz(p) * ns.SinEl(p) + ns.CX(p) + ns.PS(p) * ns.SinPa(p) + ns.PW(p) * ns.CosPa(p)

    ns.ElPoint(p) << ns.dell(p) - ns.AS(p) * ns.CosAz(p) - ns.AW(p) * ns.SinAz(p) - ns.EX(p) * ns.SinEl(p)  - (ns.EZ(p) + ns.GRAV(p)) * ns.CosEl(p) - ns.EL_EN(p)  - ns.CY(p) - ns.PS(p) * ns.CosPa(p) + ns.PW(p) * ns.SinPa(p)

    # combine azimuth and elevation errors into one node
    # and convert to radians
    ns.AzElPoint(p) << Meq.Composer(ns.AzPoint(p), ns.ElPoint(p)) * ARCSEC

  # create a source model and make list of corrupted sources
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  if subtract_perfect_obs:
    perfectsky = Meow.Patch(ns,'perfect',observation.phase_centre);
  sources = sky_models.make_model(ns,"S");
  for src in sources:
    lm = src.direction.lm();
    E = ns.E(src.name);
    if subtract_perfect_obs:
      EP = ns.EP(src.name);
    for p in array.stations():
      # compute "apparent" position of source per each antenna
      ns.lm_rot(src.name,p) << Meq.MatrixMultiply(ns.rot_matrix(p),lm) 
      lm1 = ns.lm1(src.name,p) << ns.lm_rot(src.name,p) + ns.AzElPoint(p)
      # compute E for apparent position
      ASKAP_voltage_response(E(p),lm1);
      if subtract_perfect_obs:
        ASKAP_voltage_response(EP(p),ns.lm_rot(src.name,p));
    allsky.add(src.corrupt(E));
    if subtract_perfect_obs:
      perfectsky.add(src.corrupt(EP));
  observed = allsky.visibilities();

  if subtract_perfect_obs:
    perfect = perfectsky.visibilities()
    for p,q in array.ifrs():
      ns.diff(p,q) << observed(p,q) - perfect(p,q);

  # make sinks and vdm. Note that we don't want to make any spigots...
    Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False);
  else:
    Meow.StdTrees.make_sinks(ns,ns.observed,spigots=False);

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);
  
# this is a useful thing to have at the bottom of the script,  
# it allows us to check the tree for consistency simply by 
# running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
