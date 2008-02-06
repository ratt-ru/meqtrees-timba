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

has_table_interface = True
try:
  from pyrap_tables import *
except:
  try:
    from pycasatable import *
  except:
    has_table_interface = False

def usage( prog ):
  print 'usage : python %s <MS to be corrected>' % prog
  return 1

def main( argv ):
  if has_table_interface:
    print 'Inserting UVWs into MS ', argv[1]
# first load data from table
    t = table(argv[1],readonly=False)
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
    print 'number of rows processed ', row_number + 1
    t.flush()
    t.close()
  else:
    print 'python interface to aips++ tables does not appear to be present'
    print 'exiting'

if __name__ == "__main__":
  """ We need at least one argument: the name of the Measurement Set in which to insert UVWs """
  if len(sys.argv) < 2:
    usage(sys.argv[0])
  else:
    main(sys.argv)
