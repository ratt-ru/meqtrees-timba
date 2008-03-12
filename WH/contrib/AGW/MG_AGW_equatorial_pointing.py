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

# This script uses Lewis Knees's pointing model for the DRAO 
# equatorial mount telescope to simulate an array of equatorial
# mount telescopes that have pointing errors. Here we just use the
# first equation from his March 1997 DRAO technical memo and ignore
# gravitational loading, so things are very basic.

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
  TDLOption('A1','Non-orthogonality of radio beam axis and declination axis',[0,5,10,20],more=float),
  TDLOption('A2','Non-orthogonality of polar axis and declination axis',[0,5,10,20],more=float),
  TDLOption('A3','Hour Angle encoder zero point offset',[0,5,10,20],more=float),
  TDLOption('A4','E-W offset of polar axis with respect to the true pole',[0,5,10,20],more=float),
  TDLOption('A5','N-S offset of polar axis with respect to the true pole',[0,5,10,20],more=float),
  TDLOption('B1','Declination encoder zero point offset',[0,5,10,20],more=float),
  TDLOption('randomize_axes','Randomize above extremes for each telescope?',[True,False]),
);

TDLCompileOption("max_tr_error","Max tracking error, arcsec",[0,1,2,5],more=float);
TDLCompileOption("min_tr_period","Min time scale for tracking variation, hours",[0,1],more=float);
TDLCompileOption("max_tr_period","Max time scale for tracking variation, hours",[2,4],more=float);
  
def _define_forest (ns):
  # convert telescope structure errors to radians
  A1_rad = A1 * ARCSEC
  A2_rad = A2 * ARCSEC
  A3_rad = A3 * ARCSEC
  A4_rad = A4 * ARCSEC
  A5_rad = A5 * ARCSEC
  B1_rad = B1 * ARCSEC
  B2_rad = -1.0 * A5_rad
  B3_rad = A4_rad

  # create an Array object
  num_antennas = 30
  xntd_list = [ str(i) for i in range(1,num_antennas+1) ];
  array = Meow.IfrArray(ns,xntd_list,ms_uvw=False,mirror_uvw=False)
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);
 
  ampl = max_tr_error*DEG/3600; 

  # create nodes to compute tracking errors per antenna

  # get ra and declination for the observation
  ns.Ra << Meq.Selector(observation.phase_centre.radec(),index=0)
  ns.Dec << Meq.Selector(observation.phase_centre.radec(),index=1)
  ns.SinDec << Meq.Sin(ns.Dec)
  ns.CosDec << Meq.Cos(ns.Dec)

  for p in array.stations():
    # get LST for the station and convert to radians
    ns.LST(p) << Meq.LST(array.xyz(p)) * (2*math.pi / 86400)
    # get Hour Angle for the station
    ns.HA(p) << ns.LST(p) - Meq.Selector(observation.phase_centre.radec(),index=0)
    ns.SinHA(p) << Meq.Sin(ns.HA(p))
    ns.CosHA(p) << Meq.Cos(ns.HA(p))


    # to add random errors on top of systematic ones
    # pick random periods of dha/del variation, in seconds
    dha = random.uniform(min_tr_period*3600,max_tr_period*3600);
    ddec = random.uniform(min_tr_period*3600,max_tr_period*3600);
    # pick a random starting phase for the variations
    dha_0 = random.uniform(0,2*math.pi); 
    ddec_0 = random.uniform(0,2*math.pi);
    ns.dha(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/dha)+dha_0);
    ns.ddec(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/ddec)+ddec_0);

    if randomize_axes:
      axis_offset_A1 = random.uniform(-1.0,1.0)
      axis_offset_A2 = random.uniform(-1.0,1.0)
      axis_offset_A3 = random.uniform(-1.0,1.0)
      axis_offset_A4 = random.uniform(-1.0,1.0)
      axis_offset_A5 = random.uniform(-1.0,1.0)
      axis_offset_B1 = random.uniform(-1.0,1.0)
    else:
      axis_offset_A1 = 1.0
      axis_offset_A2 = 1.0
      axis_offset_A3 = 1.0
      axis_offset_A4 = 1.0
      axis_offset_A5 = 1.0
      axis_offset_B1 = 1.0
    ns.HA_offset(p) << ns.dha(p) + axis_offset_A1 * A1_rad + axis_offset_A2 * A2_rad * ns.SinDec - axis_offset_A3 * A3_rad * ns.CosDec + axis_offset_A4 * A4_rad * ns.SinHA(p) * ns.SinDec + axis_offset_A5 * A5_rad * ns.CosHA(p) * ns.SinDec

    ns.Dec_offset(p) << ns.ddec(p) + axis_offset_B1 * B1_rad - axis_offset_A5 * A5_rad * ns.SinHA(p) + axis_offset_A4 * A4_rad * ns.CosHA(p) 
    
    ns.Ra_obs(p) << ns.Ra + ns.HA_offset(p)
    ns.Dec_obs(p) << ns.Dec + ns.Dec_offset(p)
    ns.Pos_obs(p) << Meq.Composer(ns.Ra_obs(p), ns.Dec_obs(p))

  # create a source model and make list of corrupted sources
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  sources = sky_models.make_model(ns,"S");
  for src in sources:
    lm = src.direction.lm();
    # get RA,DEC for the source
    ns.LMRaDec(src.name) << Meq.LMRaDec(observation.phase_centre.radec(),lm)
    E = ns.E(src.name);
    for p in array.stations():
      ns.LMN(src.name,p) << Meq.LMN(ns.Pos_obs(p), ns.LMRaDec(src.name))
      # compute E for apparent position
      ASKAP_voltage_response(E(p),ns.LMN(src.name,p))
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
  
# this is a useful thing to have at the bottom of the script,  
# it allows us to check the tree for consistency simply by 
# running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
