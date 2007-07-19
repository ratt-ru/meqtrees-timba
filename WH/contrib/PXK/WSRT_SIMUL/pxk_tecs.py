# History:
# - 2006.11.29: creation.


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

from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow
import random
import pxk_tools


H  = 300000;    # height of ionospheric layer, in meters


def compute_piercings (ns,srcs,array,observation):
  """Creates nodes to compute the "piercing points" of each
  source in srcs, for each antenna in array.""";
  
  xyz    = array.xyz();
  xyz_p0 = xyz(array.stations()[0])
  for p in array.stations():
    ns.xy(p) << Meq.Selector(xyz(p) - xyz_p0,index=[0,1],multi=True);
    pass
  
  for src in srcs:
    lm = src.direction.lm();
    lm_sq = ns.lm_sq(src.name) << Meq.Sqr(lm);
    # dxy is the relative X,Y coordinate of the piercing point for
    # this source, relative to centre. In each direction it's to
    # H*tg(alpha), where alpha is the direction of the source
    # w.r.t. center (i.e., arccos l).
    ns.dxy(src.name) << H*lm/Meq.Sqrt(1-lm_sq);
    
    # now compute absolute piercings per source, per antenna
    for p in array.stations():
      ns.pxy(src.name,p) << ns.xy(p) + ns.dxy(src.name);
      pass
    pass
  
  return ns.pxy;


def compute_za_cosines (ns,srcs,array,observation):
  """Creates nodes to compute the zenith angle cosine of each source
  in srcs, for each antenna in array.""";
  
  za_cos = ns.za_cos;
  for src in srcs:
    src_n = src.direction.n(observation.phase_centre)
    for p in array.stations():
      za_cos(src.name,p) << Meq.Identity(src_n);
      pass
    pass
  return za_cos;


def compute_tecs (ns,srcs,array,observation):
  """This implements a 1D sine wave moving over the array""";
  
  # get the piercings and zenith-angle cosines (z == n == sqrt(1-l^2-m^2))
  piercings = compute_piercings (ns,srcs,array,observation);
  za_cos    = compute_za_cosines(ns,srcs,array,observation);

  # get TID amplitude and rate
  ns.dt_hr   = (Meq.Time() - (ns.time0<<0))/3600.0
  amp_x      = tid_x_ampl_0hr
  amp_y      = tid_y_ampl_0hr
  amp_dx     = tid_x_ampl_1hr - tid_x_ampl_0hr
  amp_dy     = tid_y_ampl_1hr - tid_y_ampl_0hr
  ns.tid_x_ampl << amp_x + amp_dx*ns.dt_hr
  ns.tid_y_ampl << amp_y + amp_dy*ns.dt_hr
  tid_x_rate = tid_x_speed_kmh/(2.*tid_x_size_km)    # num periods per hour
  tid_y_rate = tid_y_speed_kmh/(2.*tid_y_size_km)

  # get TECs
  tecs = ns.tec;
  for isrc in range(len(srcs)):
    src    = srcs[isrc]
    #  for src in srcs:
    for p in array.stations():
      px   = ns.px(src.name,p) << Meq.Selector(piercings(src.name,p),index=0) 
      py   = ns.py(src.name,p) << Meq.Selector(piercings(src.name,p),index=1)
      X    = px/(2*1000*tid_x_size_km)
      Y    = py/(2*1000*tid_y_size_km)
      TAU_X= ns.dt_hr * tid_x_rate
      TAU_Y= ns.dt_hr * tid_y_rate
      SIN  = ns.tid_x_ampl * Meq.Sin(2*math.pi*(X + TAU_X))
      COS  = ns.tid_y_ampl * Meq.Cos(2*math.pi*(Y + TAU_Y))
      tec = tecs(src.name,p) << (TEC0 + SIN + COS) / za_cos(src.name,p)
      if isrc==0 and p<5: pxk_tools.Book_Mark(tec, 'TECS')
      pass
    pass
  
  return tecs;
  


# Some compile menu options
TDLCompileMenu(
  'TID model options :',

  TDLOption('TEC0',"TEC0  ",[0,5,10]),

  TDLMenu(
  'X-dir :',
  TDLOption('tid_x_ampl_0hr', "Relative TID-X amp @ t=0hr ",
            [0,0.05,0.10,0.25,0.5]),
  TDLOption('tid_x_ampl_1hr', "Relative TID-X amp @ t=1hr ",
            [0,0.05,0.10,0.25,0.5]),
  TDLOption('tid_x_size_km',  "TID-X size, in km          ",
            [25,50,100,200,1000]),
  TDLOption('tid_x_speed_kmh',"TID-X speed, in km/h       ",
            [25,50,100,200,300,500])
  ),

  TDLMenu(
  'Y-dir :',
  TDLOption('tid_y_ampl_0hr', "Relative TID-Y amp @ t=0hr ",
            [0,0.05,0.10,0.25,0.5]),
  TDLOption('tid_y_ampl_1hr', "Relative TID-Y amp @ t=1hr ",
            [0,0.05,0.10,0.25,0.5]),
  TDLOption('tid_y_size_km',  "TID-Y size, in km          ",
            [25,50,100,200,1000]),
  TDLOption('tid_y_speed_kmh',"TID-Y speed, in km/h       ",
            [25,50,100,200,300,500]),
  )
  )
