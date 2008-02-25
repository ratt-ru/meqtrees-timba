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

def _define_forest (ns, **kwargs):
  ## This defines a tree for
  ##    f = alpha*sin(b*x+c*y+d)

  # this defines a leaf node named "alpha" of class Meq.Constant, 
  # initialized with the given value
  # (i.e. the Fine Structure Constant, in appropriate units)
  ns.alpha << Meq.Constant(value=297.61903062068177);
  
  # it's easier to just do <<(numeric value), this implicitly defines 
  # Constant nodes
  ns.b << 1;
  ns.c << 1;
  ns.x << 1;
  ns.y << 1;
  
  # bx = b*x, the hard way:
  # This defines a node named "bx" of class Meq.Multiply, with two children
  ns.bx << Meq.Multiply(ns.b,ns.x);
  
  # cy = c*y, the easy way: 
  # arithmetic on nodes implicitly defines the "right" things
  ns.cy << ns.c * ns.y;
  
  # sum = b*x+c*y+1, the easy way -- this will implictly create a 
  # Meq.Constant node for the "1", etc.
  ns.sum << ns.bx + ns.cy + 1;
  
  # The result. Note that an intermediate node of class Meq.Sin is
  # created for us automatically
  ns.f << ns.alpha*Meq.Sin(ns.sum);
  
  
  ### ...so in fact we could have accomplished the same thing with:
  # ns.f1 << ns.alpha*Meq.Sin(ns.b*ns.x + ns.c*ns.y + 1)
  
  

def _test_forest (mqs, parent):
  domain = meq.domain(1,10,1,10)                            
  cells = meq.cells(domain,num_freq=10, num_time=11)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);





Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f') 
];
Settings.forest_state.cache_policy = 100;
