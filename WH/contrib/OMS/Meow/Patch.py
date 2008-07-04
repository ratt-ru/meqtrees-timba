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

from SkyComponent import *
import Context
import Parallelization

# This is a function to add a large number of visibilities in a clever way.
# The problem is that having too many children on a node leads to huge cache 
# usage. So instead we make a hierarchical tree to only add two things at a time.
#
# 'nodes' are output (sum) nodes
# 'visibilities' is a list of nodes containing visibilities (per component)
# 'ifrs' is a list of IFRs (so that for each i,p,q compvis[i](p,q) is a valid node)
def smart_adder (nodes,visibilities,ifrs,**kw):
  sums = visibilities;
  while sums:
    # if down to two terms or less, generate final nodes
    if len(sums) <= 2:
      for ifr in ifrs:
        nodes(*ifr) << Meq.Add(*[x(*ifr) for x in sums],**kw)
      break;
    # else generate intermediate sums
    else:
      newsums = [];
      for i in range(0,len(sums),2):
        # if we're dealing with the odd term out, propagate it to newsums list as-is
        if i == len(sums)-1:
          newsums.append(sums[i]);
        else:
          newnode = nodes('(%d,%d)'%(len(sums),i));  # create unique name for intermediate sum node
          for ifr in ifrs:
            newnode(*ifr) << Meq.Add(*[x(*ifr) for x in sums[i:i+2]],**kw);
          newsums.append(newnode);
      sums = newsums;
  return nodes;


class Patch (SkyComponent):
  def __init__(self,ns,name,direction):
    SkyComponent.__init__(self,ns,name,direction);
    self._components = [];
    
  def add (self,*comps):
    """adds components to patch""";
    self._components += comps;
    
  def make_visibilities (self,nodes,array,observation):
    array = Context.get_array(array);
    ifrs = array.ifrs();
    # no components -- use 0
    if not self._components:
      [ nodes(*ifr) << 0.0 for ifr in ifrs ];
    else:
      compvis = [ comp.visibilities(array,observation) for comp in self._components ];
      # use the intelligence in Parallelization to add in a smart way, depending on out
      # parallelization settings
      Parallelization.add_visibilities(nodes,compvis,ifrs);
    return nodes;
