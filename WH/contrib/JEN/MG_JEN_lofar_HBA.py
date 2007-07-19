# MG_JEN_lofar_HBA.py

# Short description:
#   Functions for simulating lofar HBA properties

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 oct 2005: creation
# - 21 mar 2006: -> JEN_bookmarks.py

# Copyright: The MeqTree Foundation

# Full description:






#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

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
# from Timba.Meq import meq

from numarray import *
from math import *
# from string import *
# from copy import deepcopy

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Contrib.MXM import MG_MXM_functional

from Timba.Contrib.JEN import MG_JEN_Antenna
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.util import TDL_Antenna
from Timba.Contrib.JEN.util import TDL_Dipole
from Timba.Contrib.JEN.util import TDL_lofar_HBA


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_lofar_HBA.py',
                         last_changed='h29oct2005',
                         trace=False)             # If True, produce progress messages  

MG.parm = record(height=0.25, # dipole height from ground plane, in wavelengths
                              # note that this varies with freq. in order to 
                              # model this variation, use the t,f polynomial
                              # given below
                 ntime=1,     # no. of grid points in time [0,1]
                 nfreq=20,     # no. of grid points in frequency [0,1]
                 naz=200,      # no. of grid points in azimuth [0,2*pi]
                 nel=200,      # no. of grid points in elevation [0,pi/2]
                 debug_level=10)    # debug level

# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ....
MG_JEN_forest_state.init(MG)

# Minimise the caching in view of the 4D funklet size
# (except the nodes that have explicit cache_policy set)
Settings.forest_state.cache_policy = 0






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   if True:
      # add Azimuth and Elevation axes as the 3rd and 4th axes
      MG_MXM_functional._add_axes_to_forest_state(['A','E']);
      # create the dummy node (needed for the funklet)
      ns.dummy<<Meq.Parm([[0,1],[1,0]],node_groups='Parm');


   if False:
      obj = TDL_lofar_HBA.LOFAR_HBA_rack(ns)
      MG_JEN_Antenna._experiment(ns, obj, cc, sensit=True, vbeam=True)

   if False:
      rack1 = TDL_lofar_HBA.LOFAR_HBA_rack(label='rack1', pos0=[6,0,0])
      rack2 = TDL_lofar_HBA.LOFAR_HBA_rack(label='rack2')
      rack2.rotate_xy(0.2, recurse=5)
      MG_JEN_Antenna._experiment(ns, rack1, cc, sensit=True, vbeam=True)
      MG_JEN_Antenna._experiment(ns, rack2, cc, sensit=True, vbeam=True)
      diff = rack1.subtree_diff_voltage_beam(ns, rack2)
      for node in diff:
         node.initrec().cache_policy = 100
         cc.append(node)
         JEN_bookmarks.create(node, page='diff_rack_rack')

   if True:
      obj = TDL_lofar_HBA.LOFAR_HBA_station()
      MG_JEN_Antenna._experiment(ns, obj, cc, sensit=True, vbeam=True)

   if False:
      station1 = TDL_lofar_HBA.LOFAR_HBA_station(label='station1', pos0=[20,0,0])
      station2 = TDL_lofar_HBA.LOFAR_HBA_station(label='station2')
      station2.rotate_xy(0.2, recurse=5)
      MG_JEN_Antenna._experiment(ns, station1, cc, sensit=False, vbeam=True)
      MG_JEN_Antenna._experiment(ns, station2, cc, sensit=False, vbeam=True)
      if True: 
	diff = station1.subtree_diff_voltage_beam(ns, station2)
        for node in diff:
           node.initrec().cache_policy = 100
           cc.append(node)
           JEN_bookmarks.create(node, page='diff_station_station')



   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc, make_bookmark=False)





#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


   






#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


#def _test_forest (mqs, parent):
#  """Execute the forest with a default domain"""
#   return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')
#    # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')
#    # return MG_JEN_exec.meqforest (mqs, parent)

def _tdl_job_4D_request (mqs,parent):
   """ evaluate beam pattern for the upper hemisphere
   for this create a grid in azimuth(az) [0,2*pi], pi/2-elevation(el) [0,pi/2]
   """;
   # run dummy first, to make python know about the extra axes (some magic)
   MG_MXM_functional._dummy(mqs, parent);

   time_range = [0.,1.]
   freq_range = [0.,1.]
   freq_range = [100e6,200e6]                # 100-200 MHz
   az_range = [0.,math.pi*2.0]
   el_range = [0.,math.pi/2.0]
   dom_range = [freq_range, time_range, az_range, el_range]
   nr_cells = [MG.parm['ntime'],MG.parm['nfreq'],MG.parm['naz'],MG.parm['nel']]
   request = MG_MXM_functional._make_request(Ndim=4, dom_range=dom_range,
                                             nr_cells=nr_cells)

   return MG_JEN_exec.meqforest (mqs, parent, request=request)



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 1:
      rr = station_config(ns)
      MG_JEN_exec.display_object (rr, 'rr', 'station_config', full=True)
      
      

   if 0:
       MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
       # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




