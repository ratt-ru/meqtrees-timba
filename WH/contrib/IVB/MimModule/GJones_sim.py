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
from Meow import Jones,ParmGroup,Bookmarks
from Meow.Parameterization import resolve_parameter

# can I import the class from the original module?
# from solvable_sky_jones import DiagAmplPhase
class DiagAmplPhase (object):
##  def __init__ (self):
##    self.options = [];
  def __init__ (self,label=''):
    self.tdloption_namespace = label+".diagamplphase";
    subset_opt = TDLOption('subset',"Apply this Jones term to a subset of sources",
        [None],more=str,namespace=self,doc="""Selects a subset of sources to which this 
        Jones term is applied. 'None' applies to all sources.
        You may specify individual indices (0-based) separated by commas or spaces, or ranges, e.g. "M:N" (M to N inclusive), or ":M" (0 to M), or "N:" (N to last).
        Example subset: ":3 5 8 10:12 16:".""");
    self._subset_parser = Meow.Utils.ListOptionParser(minval=0,name="sources");
    subset_opt.set_validator(self._subset_parser.validator);
    self.options = [ subset_opt ];
    self.subset = None;


  def compile_options (self):
    # Here I should add some options on the time dependence of phase and amplitude
    return self.options;

  def compute_jones (self,nodes,sources,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    # figure out which sources to apply to
    if self.subset:
      srclist = self._subset_parser.parse_list(self.subset);
      sources = [ sources[i] for i in srclist ];
    # add function for amplitude and phase here:
    time = Meq.Time # Meq.Time is time in seconds 
    # Amplitude coefficients:
    AA = 0.1
    AB = 1/3600.0
    AC = 0.0001
    # Phase coefficients:
    PA = 2.0
    PB = 1/60.0
    PC = 0.0
    # Sine wave + slow drift in time
    g_ampl_def = AA*Meq.Sin(AB*time) + AC*time
    g_phase_def = PA*(math.pi/180.0)*Meq.Sin(PB*time) + PC*time
    # loop over sources
    for src in sources:
      jones = Jones.gain_ap_matrix(nodes(src),g_ampl_def,g_phase_def,tags=tags,series=stations);
    # do I still need this if not solving?
    # make parmgroups for phases and gains
    self.pg_phase = ParmGroup.ParmGroup(label+"_phase",
                    nodes.search(tags="solvable phase"),
                    table_name="%s_phase.mep"%label,bookmark=4);
    self.pg_ampl  = ParmGroup.ParmGroup(label+"_ampl",
                    nodes.search(tags="solvable ampl"),
                    table_name="%s_ampl.mep"%label,bookmark=4);

    return nodes;
