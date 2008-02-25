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
from Timba.Meq import meq
import math

def make_sine_tid (ns,tecnode,xy,ampl,size_km,speed_kmh,angle=0,tec0=0):
  """This implements a 1D sine wave moving over the array.
  'tecnode' is a node to which the TEC will be assigned.
  'xy' is an input node that supplies coordinates, as a 2-vector.
  Other inputs may be nodes or constants:
    'ampl' is amplitude of TID
    'size_km' is size, in km (half-period)
    'speed_kmh' is speed, in km/h
    'angle' is direction of movement, relative to X axis, in radians
    'tec0' is base TEC
  """;
  ns.time ** Meq.Time;  # '**' means define or redefine
  # rate of change of TID (in periods per second)
  rate = tecnode('rate') << (speed_kmh/(2.*size_km))/3600.; 
  # now rotate the xy coordinates over the given angle
  # first create a rotation matrix
  cos = tecnode('cosa') << Meq.Cos(angle);
  sin = tecnode('sina') << Meq.Sin(angle);
  rm = tecnode('RM') << Meq.Matrix22(cos,-sin,sin,cos);
  # rotate xy using the matrix
  rxy = tecnode('xy') << Meq.MatrixMultiply(rm,xy);
  # extract the X coordinate
  x = tecnode('x') << Meq.Selector(rxy,index=0);
  # build tree for TEC as a function of x and time
  tecnode << ampl*Meq.Sin(2*math.pi*(x/(2*1000*size_km) + ns.time*rate)) + tec0; 

  return tecnode;  

  # define positions for which we want TECs (in meters)
positions = [ (0,0),(10000,10000) ];

def _define_forest (ns,**kwargs):
  # loop over positions
  for p,(x,y) in enumerate(positions):
    ns.xy(p) << Meq.Composer(x,y);
    make_sine_tid(ns,ns.tec(p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10);

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in range(len(positions)):
  name = 'tec:'+str(p);
  Settings.forest_state.bookmarks.append(record(
      name=name,viewer='Result Plotter',udi='/node/'+name));


def _test_forest (mqs,parent):
  domain  = meq.domain(0,1,0,7200);  # two hours
  cells   = meq.gen_cells(domain,num_freq=1,num_time=100);
  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  for p in range(len(positions)):
    result = mqs.execute('tec:'+str(p),request);


