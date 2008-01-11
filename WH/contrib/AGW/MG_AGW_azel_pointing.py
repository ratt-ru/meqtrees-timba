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

from Timba.TDL import *
from Timba.Meq import meq
import math
import random

import Meow
import Meow.StdTrees
import sky_models

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
  TDLOption('AN','Amount by which telescope azimuth axis is North of Vertical',[0,5,10,20],more=float),
  TDLOption('AE','Amount by which telescope azimuth axis is East of Vertical',[0,5,10,20],more=float),
  TDLOption('AZ_EN','Azimuth encoder offset',[0,5,10,20],more=float),
  TDLOption('NPAE','Amount by which telescope elevation axis is not perpendicular to azimuth axis',[0,5,10,20],more=float),
  TDLOption('GRAV','Gravitational deformation',[0,5,10,20],more=float),
  TDLOption('randomize_axes','Randomize above extremes for each telescope?',[True,False]),
);

TDLCompileOption("max_tr_error","Max tracking error, arcsec",[0,1,2,5],more=float);
TDLCompileOption("min_tr_period","Min time scale for tracking variation, hours",[0,1],more=float);
TDLCompileOption("max_tr_period","Max time scale for tracking variation, hours",[2,4],more=float);
  
def _define_forest (ns):
  # convert telescope structure errors to radians
  AN_rad = AN * ARCSEC
  AE_rad = AE * ARCSEC
  NPAE_rad = NPAE * ARCSEC
  AZ_EN_rad = AZ_EN * ARCSEC
  GRAV_rad = GRAV * ARCSEC

  # create an Array object
  num_antennas = 30
  xntd_list = [ str(i) for i in range(1,num_antennas+1) ];
  array = Meow.IfrArray(ns,xntd_list);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
 
  ampl = max_tr_error*DEG/3600; 
  # create nodes to compute tracking errors per antenna
  for p in array.stations():

    # to add random errors on top of systematic ones
    # pick random periods of daz/del variation, in seconds
    daz = random.uniform(min_tr_period*3600,max_tr_period*3600);
    dell = random.uniform(min_tr_period*3600,max_tr_period*3600);
    # pick a random starting phase for the variations
    daz_0 = random.uniform(0,2*math.pi); 
    del_0 = random.uniform(0,2*math.pi);
    ns.daz(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/daz)+daz_0);
    ns.dell(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/dell)+del_0);

    # systematic variations due to telescope axis errors
    ns.AzEl(p) << Meq.AzEl(observation.phase_centre.radec(), array.xyz(p)) 
    ns.Az(p) << Meq.Selector(ns.AzEl(p), index=0)
    ns.El(p) << Meq.Selector(ns.AzEl(p), index=1)
    ns.SinAz(p) << Meq.Sin(ns.Az(p))
    ns.CosAz(p) << Meq.Cos(ns.Az(p))
    ns.SinEl(p) << Meq.Sin(ns.El(p))
#   ns.CosEl(p) << Meq.Cos(ns.El(p))
    
    if randomize_axes:
      axis_offset_NPAE = random.uniform(-1.0,1.0)
      axis_offset_AE = random.uniform(-1.0,1.0)
      axis_offset_AN = random.uniform(-1.0,1.0)
      axis_offset_AZ_EN = random.uniform(-1.0,1.0)
      axis_offset_GRAV = random.uniform(-1.0,0.0)
    else:
      axis_offset_NPAE = 1.0
      axis_offset_AE = 1.0
      axis_offset_AN = 1.0
      axis_offset_AZ_EN = 1.0
      axis_offset_GRAV = -1.0

    ns.AzCorr_sky(p) << axis_offset_AZ_EN * AZ_EN_rad + axis_offset_NPAE * NPAE_rad * ns.SinEl(p) - axis_offset_AE * AE_rad * ns.SinEl(p) * ns.CosAz(p) - axis_offset_AN * AN_rad * ns.SinAz(p) * ns.SinEl(p)
    ns.AzPoint(p) << ns.AzCorr_sky(p) + ns.daz(p)

    ns.ElCorr(p) << axis_offset_GRAV * GRAV_rad + axis_offset_AN * AN_rad * ns.CosAz(p) - axis_offset_AE * AE_rad * ns.SinAz(p) 
    ns.ElPoint(p) << ns.ElCorr(p) + ns.dell(p)
    ns.AzElPoint(p) << Meq.Composer(ns.AzPoint(p), ns.ElPoint(p))

    # get Parallactic Angle for the station
    pa= ns.ParAngle(p) << Meq.ParAngle(observation.phase_centre.radec(), array.xyz(p))
    ns.rot_matrix(p) << Meq.Matrix22(Meq.Cos(pa),-Meq.Sin(pa),Meq.Sin(pa),Meq.Cos(pa))
 
  # create a source model and make list of corrupted sources
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  sources = sky_models.make_model(ns,"S");
  for src in sources:
    lm = src.direction.lm();
    E = ns.E(src.name);
    for p in array.stations():
      # compute "apparent" position of source per each antenna
      ns.lm_rot(src.name,p) << Meq.MatrixMultiply(ns.rot_matrix(p),lm) 
      lm1 = ns.lm1(src.name,p) << ns.lm_rot(src.name,p) + ns.AzElPoint(p)
      # compute E for apparent position
      ASKAP_voltage_response(E(p),lm1);
    allsky.add(src.corrupt(E));

  predict = allsky.visibilities();

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,predict) );
  for src in sources[:5]:
    inspectors.append( 
      Meow.StdTrees.jones_inspector(ns.inspect_E(src.name),ns.E(src.name)) );
    inspectors.append( 
      Meow.StdTrees.jones_inspector(ns.inspect_lm1(src.name),ns.lm1(src.name)) );
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=inspectors);
  
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("K Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 3
    for src in sources[:4]:            # use sources 0 through 3
      pg.add(src.direction.KJones()(p));
      
  # make a few more bookmarks
  pg = Meow.Bookmarks.Page("E Jones",2,2);
  for p in array.stations()[1:4]:      # use stations 1 through 3
    for src in sources[:4]:            # use sources 0 through 3
      pg.add(ns.E(src.name,p));

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);
  
  
# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
