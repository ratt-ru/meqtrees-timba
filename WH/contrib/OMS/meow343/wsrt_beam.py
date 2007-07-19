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

import Meow.Utils

DEG = math.pi/180;

def wsrt_beam (ns,E,sources):
  """This makes the nodes to compute the beam gain, E, given a list of sources.
  The beam gain is cos^3(C*freq_ghz*sqrt(l^2+m^2))
  (see http://www.astron.nl/wsrt/wsrtGuide/node6.html)
  C is made into a Parm with tags "beam width", intial value is 68
  """;
  ns.freq_ghz ** (Meq.Freq()*1e-9);
  ec = E("C") << Meq.Parm(68,table_name=Meow.Utils.get_mep_table(),tags="beam width solvable");
  outlist = [];
  for src in sources:
    dd = src.direction;
    name = dd.name;
    Ej = E(name);  # output node qualified by direction name
    lmdist = Ej('lmdist') << Meq.Sqrt(Meq.Sqr(dd.l())+Meq.Sqr(dd.m()));
    Ej << Meq.Pow3(Meq.Cos(Meq.Multiply(ec,lmdist,ns.freq_ghz)));
    outlist.append(src.corrupt(Ej,per_station=False));
  return outlist;
    
def wsrt_pol_beam (ns,E,sources):
  """This makes the nodes to compute the beam gain, E, given a list of sources.
  This is my crude approximation of a beam with instrumental polarization:
  for lmdistance, we use sqrt(e*l^2+m^2) for X, and sqrt(l^2+e*m^2) for y,
  e is then an "eccentricity" parameter.
  """;
  ns.freq_ghz ** (Meq.Freq()*1e-9);
  ec = E("C") << Meq.Parm(68,table_name=Meow.Utils.get_mep_table(),tags="beam width solvable");
  ee = E("E") << Meq.Parm(1,table_name=Meow.Utils.get_mep_table(),tags="beam eccentricity solvable");
  outlist = [];
  for src in sources:
    dd = src.direction;
    name = dd.name;
    Ej = E(name);  # output node qualified by direction name
    lmdist_x = Ej('lmdist','x') << Meq.Sqrt(ee*Meq.Sqr(dd.l())+Meq.Sqr(dd.m()));
    lmdist_y = Ej('lmdist','y') << Meq.Sqrt(Meq.Sqr(dd.l())+ee*Meq.Sqr(dd.m()));
    ex = Ej('x') << Meq.Pow3(Meq.Cos(Meq.Multiply(ec,lmdist_x,ns.freq_ghz)));
    ey = Ej('y') << Meq.Pow3(Meq.Cos(Meq.Multiply(ec,lmdist_y,ns.freq_ghz)));
    Ej << Meq.Matrix22(ex,0,0,ey);
    
    outlist.append(src.corrupt(Ej,per_station=False));
  return outlist;
 
def wsrt_pol_beam_with_pointing_errors (ns,E,sources):
  """This makes the nodes to compute the beam gain, E, given a list of sources.
  This is my crude approximation of a beam with instrumental polarization:
  for lmdistance, we use sqrt(e*l^2+m^2) for X, and sqrt(l^2+e*m^2) for y,
  e is then an "eccentricity" parameter.
  """;
  ns.freq_ghz ** (Meq.Freq()*1e-9);
  ec = E("C") << Meq.Parm(68,table_name=Meow.Utils.get_mep_table(),tags="beam width solvable");
  ee = E("E") << Meq.Parm(1,table_name=Meow.Utils.get_mep_table(),tags="beam eccentricity solvable");
  outlist = [];
  for p in Meow.Context.array.stations():
    ns.dl(p) << Meq.Parm(0,time_deg=1,table_name=Meow.Utils.get_mep_table(),tags="beam tracking solvable");
    ns.dm(p) << Meq.Parm(0,time_deg=1,table_name=Meow.Utils.get_mep_table(),tags="beam tracking solvable");
  for src in sources:
    dd = src.direction;
    name = dd.name;
    Ej = E(name);  # output node qualified by direction name
    for p in Meow.Context.array.stations():
      l1 = ns.l1(name,p) << dd.l() + ns.dl(p);
      m1 = ns.m1(name,p) << dd.m() + ns.dm(p);
      lmdist_x = Ej('lmdist',p,'x') << Meq.Sqrt(ee*Meq.Sqr(l1)+Meq.Sqr(m1));
      lmdist_y = Ej('lmdist',p,'y') << Meq.Sqrt(Meq.Sqr(l1)+ee*Meq.Sqr(m1));
      ex = Ej(p,'x') << Meq.Pow3(Meq.Cos(Meq.Multiply(ec,lmdist_x,ns.freq_ghz)));
      ey = Ej(p,'y') << Meq.Pow3(Meq.Cos(Meq.Multiply(ec,lmdist_y,ns.freq_ghz)));
      Ej(p) << Meq.Matrix22(ex,0,0,ey);
    outlist.append(src.corrupt(Ej));
  return outlist;
