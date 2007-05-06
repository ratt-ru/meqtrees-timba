# script_name = 'MG_AGW_LST.py'

# Short description:
#   Tests the Meqtree LST node

# Keywords: ....

# Author: Tony Willis (AGW), DRAO

# History:
# - 20 Apr 2007: first version checked in

# Copyright: The MeqTree Foundation

#
# Copyright (C) 2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
from Timba.Meq import meqds
 
# setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='LST',page=[
    record(udi="/node/LST",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/LST1",viewer="Result Plotter",pos=(1,0))]
)]);

# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

def _define_forest (ns):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
# ITRF station positions for one of the VLA telescopes - converted
# to an aips++ MVDirection object in the AzEl node (units are metres) 
  X_pos = -1597262.96
  Y_pos = -5043205.54
  Z_pos = 3554901.34
  ns.x_pos << Meq.Parm(X_pos,node_groups='Parm')
  ns.y_pos << Meq.Parm(Y_pos,node_groups='Parm')
  ns.z_pos << Meq.Parm(Z_pos,node_groups='Parm')

# create a  MeqComposer containing X_pos, Y_pos, Z_pos children
  ns.XYZ <<Meq.Composer(ns.x_pos, ns.y_pos, ns.z_pos)
                                                                                
# we should be able to create an LST node with X,Y,Z station positions
  ns.LST << Meq.LST(xyz=ns.XYZ)

# we should also be able to create an LST node with an Observatory name
  ns.LST1 << Meq.LST(observatory='VLA')

# create a ReqSeq node to call the two LST nodes
  ns.reqseq <<Meq.ReqSeq(ns.LST,ns.LST1)

def _test_forest (mqs,parent):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;

####
# time and frequency domain
# time - cover one day
  t0 = 0.01;
  t1 = 86400.01;

# any old frequency
  f1 =  299792458.0;
  f0 = 0.9*f1;

####
# Make cells array - we will compute Azimuth and Elevation over a period
# of one day divided into 120 segments

  cells = meq.cells(meq.domain(f0,f1,t0,t1),num_freq=1,num_time=120);

# define request 
  request = meq.request(cells,rqtype='e1')

# execute request
  a = mqs.meq('Node.Execute',record(name='reqseq',request=request),wait=True);

# The following is the testing branch, executed when the script is run directly
# via 'python script.py'
if __name__ == '__main__':
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
