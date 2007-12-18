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

# This script reads a meqlog.mql file and insets the UVW locations
# stored in that file (created by script MG_AGW_UVWs_astron.py)
# into a MS

from Timba import dmi
from Timba import mequtils
from Timba.Plugins.VellsData import *
from numarray import *
from pyrap_tables import *

# Insert the name of your favourite MS in the following line
t = table('TEST_XNTD_27_960.MS',readonly=False)

boio = mequtils.open_boio("meqlog.mql")
vells_data = VellsData()
vells_data.setInitialSelection(False)
row_number = -1
while True:
  entry = mequtils.read_boio(boio);
  if entry is None:
    break;
  for key,val in entry.iteritems():
    if isinstance(val,dmi.record):
      if key == 'result':
        vells_data.StoreVellsData(val,key)
        num_UVWs = vells_data.getNumPlanes() / 3
        vells_data.setActivePlane(0)
        num_tile_points = len(vells_data.getActiveData())
        # for each point in time we have to read and process all baselines
        for i in range(num_tile_points): 
          k = -1
          for j in range(num_UVWs):
            k = k + 1
            vells_data.setActivePlane(k)
            plane = vells_data.getActiveData()
            U = plane[i]
            k = k + 1
            vells_data.setActivePlane(k)
            plane = vells_data.getActiveData()
            V = plane[i]
            k = k + 1
            vells_data.setActivePlane(k)
            plane = vells_data.getActiveData()
            W = plane[i]
            row_number = row_number + 1
            uvw_group = t.getcell('UVW',row_number)
            uvw_group[0] = U
            uvw_group[1] = V
            uvw_group[2] = W
            t.putcell('UVW',row_number,uvw_group)
#   else:
#     print key,val;

print 'number of rows processed ', row_number + 1
t.flush()
t.close()
