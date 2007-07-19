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
import math
import iono_geometry
from Meow import Context

"""This module now implements the various ionospheric models used for
simulations. Each model is implemented by a function with the following
signature:
  model(ns,piercings,za_cos,source_list)
piercings and za_cos specify the per-source, per-station piercing points
The return value is something that can be qualified with (name,station)
to get the TEC value for that source and station.
""";


def sine_tid_model (ns,piercings,za_cos,source_list):
  """This implements a 1D sine wave moving over the array""";
  ns.delta_time = Meq.Time() - (ns.time0<<0);
  ns.tid_x_ampl << tid_x_ampl_0*TEC0 + (tid_x_ampl_1hr-tid_x_ampl_0)*TEC0/3600.*ns.delta_time;
  ns.tid_y_ampl << tid_y_ampl_0*TEC0 + (tid_y_ampl_1hr-tid_y_ampl_0)*TEC0/3600.*ns.delta_time;
  tid_x_rate = tid_x_speed_kmh/(2.*tid_x_size_km);   # number of periods per hour
  tid_y_rate = tid_y_speed_kmh/(2.*tid_y_size_km);   # number of periods per hour
  tecs = ns.tec;
  for src in source_list:
    for p in Context.array.stations():
      px = ns.px(src.name,p) << Meq.Selector(piercings(src.name,p),index=0); 
      py = ns.py(src.name,p) << Meq.Selector(piercings(src.name,p),index=1); 
      tecs(src.name,p) << (TEC0 +   \
            ns.tid_x_ampl*Meq.Sin(2*math.pi*(px/(2*1000*tid_x_size_km) + \
                                  ns.delta_time*tid_x_rate/3600.))     + \
            ns.tid_y_ampl*Meq.Cos(2*math.pi*(py/(2*1000*tid_y_size_km) + \
                                  ns.delta_time*tid_y_rate/3600.))       \
            ) / za_cos(src.name,p); 
      
  return tecs;
  
def wedge_model (ns,piercings,za_cos,source_list):
  """This implements a simple wedge over the array""";
  
  # at time 0, the wedge over [-50km,50km] is [TEC0-wedge_min/2,TEC0+wedge_min/2]
  # at time T, the wedge over [-50km,50km] is [TEC0-wedge_max/2,TEC0+wedge_max/2];
  ns.wedge_nt << (Meq.Time() - (ns.time0<<0))/(wedge_time*3600);
  ns.wedge_dist << (wedge_min + (wedge_max-wedge_min)*ns.wedge_nt)/100000.;
  tecs = ns.tec;
  for src in source_list:
    for p in Context.array.stations():
      px = ns.px(src.name,p) << Meq.Selector(piercings(src.name,p),index=0); 
      tecs(src.name,p) << (TEC0 + px*ns.wedge_dist)  \
            / za_cos(src.name,p); 
  return tecs;

def compute_zeta_jones (ns,source_list):
  """Creates the Z Jones for ionospheric phase, given TECs (per source, 
  per station).""";
  piercings = iono_geometry.compute_piercings(ns,source_list);
  za_cos = iono_geometry.compute_za_cosines(ns,source_list);
  tecs = iono_model(ns,piercings,za_cos,source_list);
  zeta = iono_geometry.compute_zeta_jones_from_tecs(ns,tecs,source_list);
  return zeta;

TDLCompileOption('iono_model',"Ionospheric model",
  [sine_tid_model,wedge_model]
);

TDLCompileOption('TEC0',"Base TEC value",[0,5,10],more=float);

TDLCompileMenu('Sine TID model options',
  TDLOption('tid_x_ampl_0',"Relative TID-X amplitude at t=0",[0,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_x_ampl_1hr',"Relative TID-X amplitude at t=1hr",[0,0.002,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_x_size_km',"TID-X size, in km",[25,50,100,200,1000],more=int),
  TDLOption('tid_x_speed_kmh',"TID-X speed, in km/h",[25,50,100,200,300,500],more=int),
  TDLOption('tid_y_ampl_0',"Relative TID-Y amplitude at t=0",[0,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_y_ampl_1hr',"Relative TID-Y amplitude at t=1hr",[0,0.002,0.01,0.02,0.05,0.1],more=float),
  TDLOption('tid_y_size_km',"TID-Y size, in km",[25,50,100,200,1000],more=int),
  TDLOption('tid_y_speed_kmh',"TID-Y speed, in km/h",[25,50,100,200,300,500],more=int),
);
TDLCompileMenu('Wedge model options',
  TDLOption('wedge_min','Min delta-TEC over 100km',[0,0.001,0.1,1,2,5],more=float),
  TDLOption('wedge_max','Max delta-TEC over 100km',[0,0.001,0.1,1,2,5],more=float),
  TDLOption('wedge_time','Time to reach max delta-TEC, hours',[1,2,4,8],more=float)
);


