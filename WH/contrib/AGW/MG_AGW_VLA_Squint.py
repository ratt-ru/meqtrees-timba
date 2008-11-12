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

# This script simulates the VLA squint beam behavior

from Timba.TDL import *
from Timba.Meq import meq
import math
import random
import numpy
import math

import Meow
import Meow.StdTrees

import Meow.LSM
lsm = Meow.LSM.MeowLSM(include_options=True);

from Meow import MeqMaker
meqmaker = MeqMaker.MeqMaker(use_jones_inspectors=True);
meqmaker.add_sky_models([lsm]);


Settings.forest_state.cache_policy = 100

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = ARCMIN/60;

# Define desired VLA half-intensity width of power pattern (HPBW)
# Use ABridle approximate formula from
# http://www.cv.nrao.edu/vla/hhg2vla/node41.html#SECTION000115000000000000000
# ghz = 1.4
# fwhm  = (45/ghz) * ARCMIN

# VLA beam squint taken from Fomalont & Perley
# (P108 of Synthesis Imaging in Radio Astronomy II)
# They give squint separation as fwhm * 0.05
# Assume squint offset along diagonal and centred at L,M = 0
# Then squint offset in L, M given by
# squint = (fwhm * 0.05) *  0.5 * 0.707

# NVSS survey uses the parameters: squint separation is 1.71 arcmin 
# in PA 134.6 deg. Primary Beam has FWHM of 30.9 arcmin
# We will use these ...

fwhm = 30.9  * ARCMIN
squint = 1.71 * ARCMIN * 0.5
squint_pa =  134.6 * DEG
squint_sine = math.sin(squint_pa)
squint_cos = math.cos(squint_pa)
l_beam_R = squint * squint_cos 
m_beam_R = squint * squint_sine * -1 
l_beam_L = -1 * l_beam_R 
m_beam_L = -1 * m_beam_R


def VLA_squint_response(E, lm):
  """This makes the nodes to compute the beam gain, E, given an lm position.
  'lm' is an input node, giving position of source 
  'E' is an output node to which the gain will be assigned""";

 # constant for gaussian half-intensity determination
  ln_16  = -2.7725887

  l = E('l_extracted') << Meq.Selector(lm,index=0);
  m = E('m_extracted') << Meq.Selector(lm,index=1);

  # For this example we just approximate beam shapes by a gaussian
  # first specify L, M central location of R voltage pattern
  lm_x_sq_R = E('lm_x_sq_R') << Meq.Sqr(l - l_beam_R) + Meq.Sqr(m - m_beam_R)
  # total intensity response for R
  gaussian_R = E('gaussian_R') << Meq.Exp((lm_x_sq_R * ln_16)/Meq.Sqr(fwhm));
  # take sqrt to get voltage response for R
  voltage_R = E('voltage_R') << Meq.Sqrt(gaussian_R)

  lm_x_sq_L = E('lm_x_sq_L') << Meq.Sqr(l - l_beam_L) + Meq.Sqr(m - m_beam_L)
  # total intensity response for R
  gaussian_L = E('gaussian_L') << Meq.Exp((lm_x_sq_L * ln_16)/Meq.Sqr(fwhm));
  # take sqrt to get voltage response for L
  voltage_L = E('voltage_L') << Meq.Sqrt(gaussian_L)

  # create the E-Jones matrix for a VLA antenna; we assume no RL, LR leakage here
  E << Meq.Matrix22(voltage_R, 0.0, 0.0, voltage_L)
  return E


def _define_forest (ns):

  # create an Array object
  num_antennas = 30
  xntd_list = [ str(i) for i in range(1,num_antennas+1) ];
  array = Meow.IfrArray(ns,xntd_list,ms_uvw=True,mirror_uvw=False);
# array = Meow.IfrArray.VLA(ns)
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);

  for p in array.stations():
    # get Parallactic Angle for the station
    pa= ns.ParAngle(p) << Meq.ParAngle(observation.phase_centre.radec(), array.xyz(p))
    ns.CosPa(p) << Meq.Cos(pa)
    ns.SinPa(p) << Meq.Sin(pa)
# we have a fixed position/vector on the (Ra,Dec) sky and want to obtain the 
# position in the 'rotated' AzEl coordinate frame, which is rotated 
# counter-clockwise relative to the sky by the parallactic angle
# (see http://mathworld.wolfram.com/RotationMatrix.html and
# http://www.petermeadows.com/html/parallactic.html), so we
# use the following form of the rotation matrix ...
    ns.rot_matrix(p) << Meq.Matrix22(ns.CosPa(p), ns.SinPa(p), -1.0 * ns.SinPa(p),ns.CosPa(p))

# here are the full pointing equations ...
#   ns.AzPoint(p) << ns.saw_daz(p) + ns.daz(p) - ns.AZ_EN(p) * ns.CosEl(p) + ns.NPAE(p) *ns.SinEl(p)  + ns.AW(p) * ns.SinEl(p) * ns.CosAz(p) - ns.AS(p) * ns.SinAz(p) * ns.SinEl(p) + ns.CX(p) + ns.PS(p) * ns.SinPa(p) + ns.PW(p) * ns.CosPa(p)

#   ns.ElPoint(p) << ns.saw_dell(p) + ns.dell(p) - ns.AS(p) * ns.CosAz(p) - ns.AW(p) * ns.SinAz(p) - ns.EX(p) * ns.SinEl(p)  - (ns.EZ(p) + ns.GRAV(p)) * ns.CosEl(p) - ns.EL_EN(p)  - ns.CY(p) - ns.PS(p) * ns.CosPa(p) + ns.PW(p) * ns.SinPa(p)

    # combine azimuth and elevation errors into one node
    # and convert to radians
#   ns.AzElPoint(p) << Meq.Composer(ns.AzPoint(p), ns.ElPoint(p)) * ARCSEC

  # create a source model and make list of corrupted sources
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  for src in meqmaker.get_source_list(ns):
    lm = src.direction.lm();
    E = ns.E(src.name);
    for p in array.stations():
      # compute "apparent" position of source per each antenna
      lm_rot = ns.lm_rot(src.name,p) << Meq.MatrixMultiply(ns.rot_matrix(p),lm) 
#     lm1 = ns.lm1(src.name,p) << ns.lm_rot(src.name,p) + ns.AzElPoint(p)
      # compute E for apparent position
#     VLA_squint_response(E(p),lm1);
      VLA_squint_response(E(p),lm_rot);
    allsky.add(src.corrupt(E));
  observed = allsky.visibilities();

  Meow.StdTrees.make_sinks(ns,observed,spigots=False);

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
