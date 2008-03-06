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

from Timba.TDL import *
from Meow import Context

import random
import math

import ErrorGens


DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = DEG/3600;

def WSRT_cos3_beam (E,lm,*dum):
  """computes a gaussian beam for the given direction
  'E' is output node
  'lm' is direction (2-vector node)
  """
  beamsize = wsrt_beam_size_factor*1e-9;
  ns = E.Subscope();
  ns.lmsq << Meq.Sqr(lm);
  ns.lsq  << Meq.Selector(ns.lmsq,index=0);
  ns.msq  << Meq.Selector(ns.lmsq,index=1);
  if wsrt_beam_eccentricity:
    ns.lsqex << ns.lsq*(1-wsrt_beam_eccentricity)**2;
    ns.lsqey << ns.lsq*(1+wsrt_beam_eccentricity)**2;
    ns.msqex << ns.msq*(1+wsrt_beam_eccentricity)**2;
    ns.msqey << ns.msq*(1-wsrt_beam_eccentricity)**2;
    ns.Ex << Meq.Pow(Meq.Cos(Meq.Sqrt(ns.lsqex+ns.msqex)*Meq.Freq()*beamsize),3);
    ns.Ey << Meq.Pow(Meq.Cos(Meq.Sqrt(ns.lsqey+ns.msqey)*Meq.Freq()*beamsize),3);
    E << Meq.Matrix22(ns.Ex,0,0,ns.Ey);
  else:
    E << Meq.Pow(Meq.Cos(Meq.Sqrt(ns.lsq+ns.msq)**Meq.Freq()*beamsize),3);
  return E;
# this beam model is not per-station
WSRT_cos3_beam._not_per_station = True;

def compute_jones (Jones,sources,stations=None,pointing_offsets=None,**kw):
  """Computes beam gain for a list of sources.
  The output node, will be qualified with either a source only, or a source/station pair
  """;
  stations = stations or Context.array.stations();
  ns = Jones.Subscope();
  # are pointing errors configured?
  if pointing_offsets:
    # create nodes to compute actual pointing per source, per antenna
    for p in Context.array.stations():
      for src in sources:
        lm = ns.lm(src.direction,p) << src.direction.lm() + pointing_offsets(p);
        beam_model(Jones(src,p),lm,p);
  # no pointing errors
  else:
    # if not per-station, use same beam for every source
    if beam_model._not_per_station:
      for src in sources:
        beam_model(Jones(src),src.direction.lm());
        for p in Context.array.stations():
          Jones(src,p) << Meq.Identity(Jones(src));
    else:
      for src in sources:
        for p in Context.array.stations():
          beam_model(Jones(src,p),src.direction.lm(),p);
  return Jones;

_model_option = TDLCompileOption('beam_model',"Beam model",
  [WSRT_cos3_beam]
);

_wsrt_option_menu = TDLCompileMenu('WSRT beam model options',
  TDLOption('wsrt_beam_size_factor',"Beam size factor",[68],more=float),
  TDLOption('wsrt_beam_eccentricity',"Beam eccentricity",[None,.01,.1],more=float)
);

def _show_option_menus (model):
  _wsrt_option_menu.show(model==WSRT_cos3_beam);

_model_option.when_changed(_show_option_menus);
