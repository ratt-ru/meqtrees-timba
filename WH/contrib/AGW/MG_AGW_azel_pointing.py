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
  TDLOption('CX','Beam Collimation Error X',[0,5,10,20],more=float),
  TDLOption('CY','Beam Collimation Error Y',[0,5,10,20],more=float),
  TDLOption('PX','Parallactic Angle Tilt X',[0,5,10,20],more=float),
  TDLOption('PY','Parallactic Angle Tilt Y',[0,5,10,20],more=float),
  TDLOption('GRAV','Gravitational deformation',[0,5,10,20],more=float),
  TDLOption('randomize_axes','Randomize above extremes for each telescope?',[True,False]),
  TDLOption('do_solve','Solve for Structure Parameters?',[True,False]),
);

mep_table = 'pointing_coeffs.mep'
# first, make sure that any previous version of the mep table is
# obliterated so nothing strange happens in succeeding steps
if do_solve:
  try:
    os.system("rm -fr "+ mep_table);
  except:   pass


# get Azimuth / Elevation telescope random tracking errors
TDLCompileOption("max_tr_error","Max tracking error, arcsec",[0,1,2,5],more=float);
TDLCompileOption("min_tr_period","Min time scale for tracking variation, hours",[0,1],more=float);
TDLCompileOption("max_tr_period","Max time scale for tracking variation, hours",[2,4],more=float);
  
# support functions for polcs
def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(numarray.zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
                  table_name=mep_table);

def _define_forest (ns):

  # create an Array object
  num_antennas = 30
  xntd_list = [ str(i) for i in range(1,num_antennas+1) ];
  array = Meow.IfrArray(ns,xntd_list);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);

  if do_solve:
    solvables = []
 
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

    # systematic variations due to telescope axis errors
    ns.AzEl(p) << Meq.AzEl(observation.phase_centre.radec(), array.xyz(p)) 
    ns.Az(p) << Meq.Selector(ns.AzEl(p), index=0)
    ns.El(p) << Meq.Selector(ns.AzEl(p), index=1)
    ns.SinAz(p) << Meq.Sin(ns.Az(p))
    ns.CosAz(p) << Meq.Cos(ns.Az(p))
    ns.SinEl(p) << Meq.Sin(ns.El(p))
    ns.CosEl(p) << Meq.Cos(ns.El(p))
    
    if randomize_axes:
      axis_offset_NPAE = random.uniform(-1.0,1.0)
      axis_offset_AW = random.uniform(-1.0,1.0)
      axis_offset_AS = random.uniform(-1.0,1.0)
      axis_offset_AZ_EN = random.uniform(-1.0,1.0)
      axis_offset_EL_EN = random.uniform(-1.0,1.0)
      axis_offset_CX = random.uniform(-1.0,1.0)
      axis_offset_CY = random.uniform(-1.0,1.0)
      axis_offset_PX = random.uniform(-1.0,1.0)
      axis_offset_PY = random.uniform(-1.0,1.0)
      axis_offset_GRAV = random.uniform(-1.0,0.0)
    else:
      axis_offset_NPAE = 1.0
      axis_offset_AW = 1.0
      axis_offset_AS = 1.0
      axis_offset_AZ_EN = 1.0
      axis_offset_EL_EN = 1.0
      axis_offset_CX = 1.0
      axis_offset_CY = 1.0
      axis_offset_PX = 1.0
      axis_offset_PY = 1.0
      axis_offset_GRAV = -1.0

    ns.AZ_EN(p) << Meq.Constant(axis_offset_AZ_EN * AZ_EN)
    ns.EL_EN(p) << Meq.Constant(axis_offset_EL_EN * EL_EN)
    ns.NPAE(p) << Meq.Constant(axis_offset_NPAE * NPAE)
    ns.AW(p) << Meq.Constant(axis_offset_AW * AW)
    ns.AS(p) << Meq.Constant(axis_offset_AS * AS)
    ns.GRAV(p) << Meq.Constant(axis_offset_GRAV * GRAV)
    ns.CX(p) << Meq.Constant(axis_offset_CX * CX)
    ns.CY(p) << Meq.Constant(axis_offset_CY * CY)
    ns.PX(p) << Meq.Constant(axis_offset_PX * PX)
    ns.PY(p) << Meq.Constant(axis_offset_PY * PY)
    ns.AzPoint(p) << ns.daz(p) - ns.AZ_EN(p) * ns.CosEl(p) + ns.NPAE(p) *ns.SinEl(p)  + ns.AW(p) * ns.SinEl(p) * ns.CosAz(p) - ns.AS(p) * ns.SinAz(p) * ns.SinEl(p) + ns.CX(p) + ns.PX(p)

    ns.ElPoint(p) << ns.dell(p) + ns.GRAV(p) - ns.AS(p) * ns.CosAz(p) - ns.AW(p) * ns.SinAz(p) - ns.EL_EN(p)  - ns.CY(p) - ns.PY(p)

    # combine azimuth and elevation errors into one node
    # and convert to radians
    ns.AzElPoint(p) << Meq.Composer(ns.AzPoint(p), ns.ElPoint(p)) * ARCSEC

    if do_solve:
      # give initial guesses that are opposite of actual values for everything
      ns.solve_AZ_EN(p) << tpolc(0, -1.0 * axis_offset_AZ_EN * AZ_EN)
      ns.solve_EL_EN(p) << tpolc(0, -1.0 * axis_offset_EL_EN * EL_EN)
      ns.solve_NPAE(p) << tpolc(0, -1.0 * axis_offset_NPAE * NPAE)
      ns.solve_AW(p) << tpolc(0, -1.0 * axis_offset_AW * AW)
      ns.solve_AS(p) << tpolc(0, -1.0 * axis_offset_AS * AS)
      ns.solve_GRAV(p) << tpolc(0, -1.0 * axis_offset_GRAV * GRAV)
      ns.solve_CX(p) << tpolc(0, -1.0 * axis_offset_CX * CX)
      ns.solve_CY(p) << tpolc(0, -1.0 * axis_offset_CY * CY)
      ns.solve_PX(p) << tpolc(0, -1.0 * axis_offset_PX * PX)
      ns.solve_PY(p) << tpolc(0, -1.0 * axis_offset_PY * PY)

      solvables.append(ns.solve_AZ_EN(p))
      solvables.append(ns.solve_EL_EN(p))
      solvables.append(ns.solve_NPAE(p))
      solvables.append(ns.solve_AW(p))
      solvables.append(ns.solve_AS(p))
      solvables.append(ns.solve_GRAV(p))
      solvables.append(ns.solve_CX(p))
      solvables.append(ns.solve_CY(p))
      solvables.append(ns.solve_PX(p))
      solvables.append(ns.solve_PY(p))

      ns.solve_AzPoint(p) << ns.solve_NPAE(p) *ns.SinEl(p)  - ns.solve_AZ_EN(p) * ns.CosEl(p) + ns.solve_AW(p) * ns.SinEl(p) * ns.CosAz(p) - ns.solve_AS(p) * ns.SinAz(p) * ns.SinEl(p) + ns.solve_CX(p) + ns.solve_PX(p)
      ns.solve_ElPoint(p) << ns.solve_GRAV(p) - ns.solve_AS(p) * ns.CosAz(p) - ns.solve_AW(p) * ns.SinAz(p) - ns.solve_EL_EN(p) - ns.solve_CY(p) - ns.solve_PY(p) 

      # combine azimuth and elevation errors into one node
      # and convert to radians
      ns.solve_AzElPoint(p) << Meq.Composer(ns.solve_AzPoint(p), ns.solve_ElPoint(p)) * ARCSEC


    # get Parallactic Angle for the station
    pa= ns.ParAngle(p) << Meq.ParAngle(observation.phase_centre.radec(), array.xyz(p))
    ns.rot_matrix(p) << Meq.Matrix22(Meq.Cos(pa),-Meq.Sin(pa),Meq.Sin(pa),Meq.Cos(pa))
 
  # create a source model and make list of corrupted sources
  allsky = Meow.Patch(ns,'all',observation.phase_centre);
  if do_solve:
    solve_sky = Meow.Patch(ns,'solve',observation.phase_centre);
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
    if do_solve:
      solve_E = ns.solve_E(src.name);
      for p in array.stations():
        lm2 = ns.lm2(src.name,p) << ns.lm_rot(src.name,p) + ns.solve_AzElPoint(p)
        # compute E for apparent position
        ASKAP_voltage_response(solve_E(p),lm2);
      solve_sky.add(src.corrupt(solve_E));

  observed = allsky.visibilities();

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  pg = Bookmarks.Page("Inspectors",1,2);
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_observed,observed) );
  pg.add(ns.inspect_observed,viewer="Collections Plotter");

  if do_solve:
    expected = solve_sky.visibilities()

 # create spigots, condeqs, residuals
  if do_solve:
    pg1= Bookmarks.Page("Solving",1,3);
    for p,q in array.ifrs():
      ns.ce(p,q) << Meq.Condeq(observed(p,q), expected(p,q));
      ns.residual(p,q) << observed(p,q) - expected(p,q);
    pg1.add(ns.ce(1,2), viewer="Result Plotter")
    pg1.add(ns.ce(10,20), viewer="Result Plotter")

    inspectors.append(
      Meow.StdTrees.vis_inspector(ns.inspect_residuals,ns.reqseq) );
    pg.add(ns.inspect_residuals,viewer="Collections Plotter");

    # create solver
    ns.solver << Meq.Solver(solvable=solvables,num_iter=5,epsilon=1e-4,save_funklets=True,*[ns.ce(p,q) for p,q in array.ifrs()]);
    pg1.add(ns.solver, viewer="Result Plotter")

    # create sequencer
    for p,q in array.ifrs():
      ns.reqseq(p,q) << Meq.ReqSeq(ns.solver,ns.residual(p,q),result_index=1);
    # make sinks and vdm. Note that we don't want to make any spigots...
    # The list of inspectors comes in handy here
    Meow.StdTrees.make_sinks(ns, ns.reqseq,spigots=False,post=inspectors);
  else:
    Meow.StdTrees.make_sinks(ns,observed,spigots=False,post=inspectors);


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
