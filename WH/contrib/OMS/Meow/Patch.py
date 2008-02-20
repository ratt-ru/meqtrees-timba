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

class Patch (SkyComponent):
  def __init__(self,ns,name,direction):
    SkyComponent.__init__(self,ns,name,direction);
    self._components = [];
    
  def add (self,*comps):
    """adds components to patch""";
    self._components += comps;
    
  def make_visibilities (self,nodes,array,observation):
    array = Context.get_array(array);
    # no components -- use 0
    if not self._components:
      [ nodes(*ifr) << 0.0 for ifr in array.ifrs() ];
    else:
      compvis = [ comp.visibilities(array,observation) for comp in self._components ];
      # add them up per-ifr
      # be clever -- having too many children to one node leads to a huge
      # memory footprint, so we add them in packs of two. cur_vis is the current
      # list of nodes to be added, it is reduced by a factor of 2 at each step.
      sums = compvis;
      while sums:
        # if down to two terms or less, generate final nodes
        if len(sums) <= 2:
          for ifr in array.ifrs():
            nodes(*ifr) << Meq.Add(*[x(*ifr) for x in sums])
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
              for ifr in array.ifrs():
                newnode(*ifr) << Meq.Add(*[x(*ifr) for x in sums[i:i+2]]);
              newsums.append(newnode);
          sums = newsums;
    return nodes;
