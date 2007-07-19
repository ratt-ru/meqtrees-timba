#!/usr/bin/python

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

from Timba.meqkernel import set_state

def process_vis_header (hdr):
  """handler for the standard MS visheader""";
  # phase center
  (ra0,dec0) = hdr.phase_ref;
  set_state('ra0',value=ra0);
  set_state('dec0',value=dec0);
  # antenna positions
  pos = hdr.antenna_pos;
  if pos.rank != 2 or pos.shape[0] != 3:
    raise ValueError,'incorrectly shaped antenna_pos';
  nant = pos.shape[1];
  coords = ('x','y','z');
  for iant in range(nant):
    sn = str(iant+1);
    # since some antennas may be missing from the tree,
    # ignore errors
    try:
      for (j,label) in enumerate(coords):
        set_state(label+'.'+sn,value=pos[j,iant]);
    except: pass;
  # array reference position
  for (j,label) in enumerate(coords):
    set_state(label+'0',value=pos[j,0]);

