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
import pierce_points
import Meow
from Meow import Context
from Meow import Jones,ParmGroup,Bookmarks
from Meow.Parameterization import resolve_parameter

lightspeed = 3.0E8 #(m/s)

class Iono (object):
  # don't know what this does
  def __init__ (self):
    self.options = [];

  # don't know what this does either
  def runtime_options (self):
    return self.options;
  
# Below the code is adjusted to solve for the parameters of an ionospheric model.
# For now we are using the MIM approach.

# 'Sources' needs to be a function qualifier, since pierce-points are a function
# of station AND source position. Sources has no default value, and is not defined
# in the Meow context (could this be done?)

  def compute_jones (self,nodes,sources,stations=None,label='',**kw):
    stations = stations or Context.array.stations();
    # 'nodes' is a NodeStub object and not a NodeScope. The NodeScope has to be
    # exported from the NodeStub before we can use it.
    ns = nodes.Subscope();
    # Define four parameters to solve for. Can we make this an arbitrary number depending
    # on the MIM-order? Eg FOR i = 0 to mimorder DO parm(i)=Meow.Parm(0) ?
    mim_0 = Meow.Parm(0); # dit is in feite TEC0
    mim_x = Meow.Parm(0);
    mim_y = Meow.Parm(0);
    mim_xy = Meow.Parm(0);

    # Set the tagname 
    tags="mim"
    # Now initialize the parameters, name them properly and tag them as solvable
    # nodename nodes.source:station:c NB: nodescope is now 'nodes', and not 'ns'
    # tags: tagname as set above
    m0 = resolve_parameter("mim_0",nodes('m0'),mim_0,tags=tags);
    mx = resolve_parameter("mim_x",nodes('mx'),mim_x,tags=tags);
    my = resolve_parameter("mim_y",nodes('my'),mim_y,tags=tags);
    mxy = resolve_parameter("mim_xy",nodes('mxy'),mim_xy,tags=tags);

    # make the collection of pierce-points on which we will define the MIM function
    # We now make the pierce-points in a NodeScope that knows everything I have
    # generated in the routine by setting piercings = ....
    piercings = pierce_points.compute_pierce_points(nodes,sources);

    # Now we define the TEC function for the pierce-points, which is per source, per station
    for src in sources:
      for p in stations:
        # select the X and Y values of the pierce-points. These are in ENU with reference
        # antenna as defined in the routine (so not ENU per antenna but per ARRAY!)
        # The values are called x_trans and y_trans
        x = piercings.x_trans(src,p)
        y = piercings.y_trans(src,p)
        # Since Z is not a matrix, we can now define a Z-value per source per station
        # First generate the actual TEC value by defining a polynomial
        # This needs to become a separate routine that is called with a specific model
        ns.tec(src,p) << m0 + mx * x + my * y + mxy * x * y
        # Second convert this into a Z-jones and put it in a node
        # nodes is the NodeStub we use for meqmaker, does not need to be ns.nodes
        nodes(src,p) << Meq.Polar(1,-25*lightspeed*ns.tec(src,p)/Meq.Freq())
      
    # ParmGroup makes a group of solvable parms and names the table to which they
    # will be written. It searches for solvable parameters, in our case the ones
    # tagged as "solvable mim".
    # moet er een ParmGroup komen voor elke mim parameter, of gaan ze samen in 1 tabel?
    self.pg_mim = ParmGroup.ParmGroup(label,
                                      nodes.search(tags="solvable mim"),
                                      table_name="mim.mep",
                                      bookmark=4);

    # make solvejobs 
    # is dit niet dezelfde als in calico-ivb?
    ParmGroup.SolveJob("cal_"+label,"Calibrate ionosphere",self.pg_mim);

    return nodes;
