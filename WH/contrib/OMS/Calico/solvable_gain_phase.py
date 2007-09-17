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
import Meow
from Meow import Context
from Meow import Jones
from ParmGroup import ParmGroup

class AmplPhaseJones (object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

  def compute_jones (self,nodes,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    g_ampl_def = Meow.Parm(1);
    g_phase_def = Meow.Parm(0);
    nodes = Jones.gain_ap_matrix(nodes,g_ampl_def,g_phase_def,tags=tags,series=stations);

    # now make solvejobs for phases and gains
    self.pg_phase = ParmGroup(label+":phase",nodes.search(tags="solvable phase"));
    self.options.append(self.pg_phase.make_solvejob_menu("Calibrate %s phases"%label));
    self.pg_gain  = ParmGroup(label+":ampl",nodes.search(tags="solvable ampl"));
    self.options.append(self.pg_gain.make_solvejob_menu("Calibrate %s amplitudes"%label));

    return nodes;
