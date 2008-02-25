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

TDLCompileOption('ser_order',"Max order of series",[3,5,10],more=int);

def _define_forest (ns, **kwargs):
  x = ns.x << Meq.Time;
  y = ns.y << Meq.Freq;

  TERMS = range(-ser_order,ser_order+1);    # [-n,...,n]
  
  # ns.f(k,l) creates a node named "f:k:l", substituting the values of
  # k,l. This is useful if you need to create a series of trees
  # following some algorithm.
  for k in TERMS:
    for l in TERMS:
      ns.f(k,l) << Meq.Polar(1,-2*math.pi*(k*x+l*y));
      
  # and of course plain "f" is still available to be used for a node name.
  # Note how Python's '*' syntax and a list comprehension statement
  # can be used to create a list of children
  ns['f'] << Meq.Add(*[ns.f(k,l) for k in TERMS for l in TERMS]);
  
  # Note also, ns['f'] does the same thing as ns.f. However, since the [] 
  # operator takes any expression, it allows things like:
  #   name = 'f'
  #   ns[name] << ...
  # i.e. "computing" a node name if necessary.
  

def _test_forest (mqs, parent):
  domain = meq.domain(-1,1,-1,1)                            
  cells = meq.cells(domain,num_freq=100, num_time=100)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);




Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f')
];
if ser_order <= 10:
  Settings.forest_state.cache_policy = 100;
else:
  Settings.forest_state.cache_policy = 1;
