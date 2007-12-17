# standard preamble
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

# This script reads a MS and calculates UWV tracks in 'ASTRON' format,
# which is opposite to that of the VLA. We store the UV tracks in
# a meqlog.mql file. That file can then be read in by a python script
# (see MG_AGW_insert_UVWs_astron.py) which reads the MS and replaces the 
# UVWs calculated by the aips++ newsimulator with the 'ASTRON' UVW 
# positions.

from Timba.TDL import *
from Timba.Meq import meq
import Meow
from Meow import Utils
import math

def _define_forest (ns):
  Utils.include_ms_options(has_output=False)
  array = Meow.IfrArray.VLA(ns);
  spigot = array.spigots()

  # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);
  
  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);
  
  # now define per-station stuff: XYZs and UVWs 
  for p in array.stations():
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p));
  
  for p,q in array.ifrs():
    ns.baseline(p,q) << Meq.Subtract(ns.uvw(q),ns.uvw(p))

  ns.baselines << Meq.Composer(log_policy=100,
    *[ns.baseline(p,q) for p,q in array.ifrs()]);
  
  # create VDM and attach request to generate baselines
  vdm = ns.VisDataMux << Meq.VisDataMux(post=ns.baselines);
  vdm.add_stepchildren(*[spigot(p,q) for p,q in array.ifrs()]);

def _test_forest (mqs,parent):
  req = Meow.Utils.create_io_request();
  mqs.execute('VisDataMux',req,wait=False);

# this is a useful thing to have at the bottom of the script; 
# it allows us to check the tree for consistency simply by 
# running 'python script.py'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
