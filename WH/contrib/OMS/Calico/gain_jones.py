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
from Meow import ParmGroup

class DiagonalAmplPhase (object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

  def compute_jones (self,nodes,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    g_ampl_def = Meow.Parm(1);
    g_phase_def = Meow.Parm(0);
    nodes = Jones.gain_ap_matrix(nodes,g_ampl_def,g_phase_def,tags=tags,series=stations);

    # make parmgroups for phases and gains
    self.pg_phase = ParmGroup.ParmGroup(label+"_phase",
                    nodes.search(tags="solvable phase"),
                    table_name="%s_phase.mep"%label,bookmark=4);
    self.pg_ampl  = ParmGroup.ParmGroup(label+"_ampl",
                    nodes.search(tags="solvable ampl"),
                    table_name="%s_ampl.mep"%label,bookmark=4);

    # make solvejobs
    ParmGroup.SolveJob("cal_"+label+"_phase","Calibrate %s phases"%label,self.pg_phase);
    ParmGroup.SolveJob("cal_"+label+"_ampl","Calibrate %s amplitudes"%label,self.pg_ampl);

    return nodes;

class FullRealImag (object):
  def __init__ (self):
    self.options = [];

  def runtime_options (self):
    return self.options;

  def compute_jones (self,jones,stations=None,tags=None,label='',**kw):
    stations = stations or Context.array.stations();
    p1 = Meow.Parm(1);
    p0 = Meow.Parm(0);
    diags = [];
    offdiags = [];
    for p in stations:
      rxx = Parameterization.resolve_parameter("diag",jones(p,'rxx'),p1,tags=tags);
      ixx = Parameterization.resolve_parameter("diag",jones(p,'ixx'),p0,tags=tags);
      ryy = Parameterization.resolve_parameter("diag",jones(p,'ryy'),p1,tags=tags);
      iyy = Parameterization.resolve_parameter("diag",jones(p,'iyy'),p0,tags=tags);
      rxy = Parameterization.resolve_parameter("offdiag",jones(p,'rxy'),p0,tags=tags);
      ixy = Parameterization.resolve_parameter("offdiag",jones(p,'ixy'),p0,tags=tags);
      ryx = Parameterization.resolve_parameter("offdiag",jones(p,'ryx'),p0,tags=tags);
      iyx = Parameterization.resolve_parameter("offdiag",jones(p,'iyx'),p0,tags=tags);
      diags += [ rxx,ixx,ryy,iyy ];
      offdiags += [rxy,ixy,ryx,iyx ];
      jones(p) << Meq.Matrix22(
        jones(p,"xx") << Meq.ToComplex(rxx,ixx),
        jones(p,"xy") << Meq.ToComplex(rxy,ixy),
        jones(p,"yx") << Meq.ToComplex(ryx,iyx),
        jones(p,"yy") << Meq.ToComplex(ryy,iyy),
      );
    # make parmgroups for diagonal and off-diagonal terms
    self.pg_diag     = ParmGroup.ParmGroup(label+"_diag",diags,
                          table_name="%s_diag.mep"%label,bookmark=False);
    self.pg_offdiag  = ParmGroup.ParmGroup(label+"_offdiag",offdiags,
                          table_name="%s_offdiag.mep"%label,bookmark=False);
    
    # make bookmarks
    pg = Bookmarks.Page("%s diagonal terms"%label);
    for parm in diags:
      pg.add(parm);
    pg = Bookmarks.Page("%s off-diagonal terms"%label);
    for parm in offdiags:
      pg.add(parm);

    # make solvejobs
    ParmGroup.SolveJob("cal_"+label+"_diag","Calibrate %s diagonal terms"%label,self.pg_diag);
    ParmGroup.SolveJob("cal_"+label+"_offdiag","Calibrate %s off-diagonal terms"%label,self.pg_offdiag);
    
    return jones;
