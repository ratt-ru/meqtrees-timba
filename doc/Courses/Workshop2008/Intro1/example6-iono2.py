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
from example5_iono import make_sine_tid


positions = [ (0,0),(10000,10000),(None,None) ];

def _define_forest (ns,**kwargs):
  for p,(x,y) in enumerate(positions):
    if x is None:
      # for None,None make a special xy position
      # start with an l,m pair
      lm = ns.lm(p) << Meq.Composer(Meq.Grid(axis='l'),Meq.Grid(axis='m'));
      # now derive xy using ionosphere height
      # x = h*tg(a), l=cos(a), so tg(a)=l/sqrt(1-l^2);
      height = 300000;  # in meters
      ns.xy(p) << height*lm/Meq.Sqrt(1-Meq.Sqr(lm));
    else:
      ns.xy(p) << Meq.Composer(x,y);
    # define tec trees 
    make_sine_tid(ns,ns.tec(p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10,angle=0);

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in range(len(positions)):
  name = 'tec:'+str(p);
  Settings.forest_state.bookmarks.append(record(
      name=name,viewer='Result Plotter',udi='/node/'+name));


def _test_forest (mqs,parent):
  # make a domain in time,l,m
  domain = meq.gen_domain(time=[0,7200],l=[-.05,.05],m=[-.05,.05]);
  cells = meq.gen_cells(domain,num_time=100,num_l=100,num_m=100);

  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  for p in range(len(positions)):
    result = mqs.execute('tec:'+str(p),request);
