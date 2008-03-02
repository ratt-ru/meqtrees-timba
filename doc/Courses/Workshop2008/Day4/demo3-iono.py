
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

# reuse previous function
from demo1_iono import make_sine_tid


positions = [ (0,0),(10000,10000) ];
tec_points = [ 0,1,'grid' ];

def _define_forest (ns,**kwargs):
  # make nodes for individual positions
  for p,(x,y) in enumerate(positions):
    ns.xy(p) << Meq.Composer(x,y);
  # make node for grid of positions
  lm = ns.lm << Meq.Composer(Meq.Grid(axis='l'),Meq.Grid(axis='m'));
  height = 300000;  # in meters
  # now derive xy using ionosphere height
  # x = h*tg(a), l=cos(a), so tg(a)=l/sqrt(1-l^2);
  ns.xy('grid') << height*lm/Meq.Sqrt(1-Meq.Sqr(lm));
  # now define tec trees 
  for p in tec_points:
    make_sine_tid(ns,ns.tec(1,p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10);
    make_sine_tid(ns,ns.tec(2,p),ns.xy(p),ampl=.05,size_km=65,speed_kmh=200,angle=math.pi/6);
    ns.tec(p) << ns.tec(1,p) + ns.tec(2,p);
  ns.difftec << ns.tec(0) - ns.tec(1);

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in tec_points:
  name = 'tec:'+str(p);
  Settings.forest_state.bookmarks.append(record(
      name=name,viewer='Result Plotter',udi='/node/'+name));
Settings.forest_state.bookmarks.append(record(
      name='difftec',viewer='Result Plotter',udi='/node/difftec'));


def _test_forest (mqs,parent):
  # make a domain in time,l,m
  domain = meq.gen_domain(time=[0,7200],l=[-.05,.05],m=[-.05,.05]);
  cells = meq.gen_cells(domain,num_time=100,num_l=100,num_m=100);

  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  # execute for every subtree
  for p in tec_points:
    result = mqs.execute('tec:'+str(p),request);
  mqs.execute('difftec',request);
