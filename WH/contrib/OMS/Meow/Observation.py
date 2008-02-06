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
from Direction import *


class Observation (object):
  """An observation object represents observation-related properties.
  These are polarization type (circular or linear), plus the phase center
  direction. An observation also has an optional set of qualifiers 
  which are applied to all nodes created via this object (i.e. the ra/dec
  nodes of the phase center).
  """;
  def __init__(self,ns,circular=False,linear=False,
               quals=[],kwquals={}):
    self.ns = ns;
    if circular and linear:
      raise ValueError,"either circular=True or linerar=True must be specified, not both";
    self._circular = circular;
    self._quals = quals;
    self._kwquals = kwquals;
    self.phase_centre = self.phase_center = \
        Direction(ns,None,0,0,quals=quals,kwquals=kwquals);

  def circular (self):
    return self._circular;
    
  def radec0 (self):
    """returns radec node for the phase center direction""";
    return self.phase_centre.radec();

  def freq0(self):
    """return start frequency """;
    if not self.ns.freq0.initialized():
      self.ns.freq0 << Meq.Constant(59e6);
    return self.ns.freq0;

  def freq1(self):
    """return end frequency """;
    if not self.ns.freq1.initialized():
      self.ns.freq1 << Meq.Constant(60e6);
    return self.ns.freq1;
