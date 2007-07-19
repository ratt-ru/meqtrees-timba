# MG_JEN_Antenna.py

# Short description:
#   Functions for testing TDL_Antenna objects 

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 16 oct 2005: creation

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

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.util import TDL_Antenna
from Timba.Contrib.JEN.util import TDL_Dipole

Settings.forest_state.cache_policy=100;

#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_Antenna.py',
                         last_changed='h17oct2005',
                         trace=False)             # If True, produce progress messages  

MG.parm = record(height=0.25, # dipole height from ground plane, in wavelengths
                              # note that this varies with freq. in order to 
                              # model this variation, use the t,f polynomial
                              # given below
                 ntime=5,     # no. of grid points in time [0,1]
                 nfreq=10,     # no. of grid points in frequency [0,1]
                 naz=50,     # no. of grid points in azimuth [0,2*pi]
                 nel=50,     # no. of grid points in elevation [0,pi/2]
                 debug_level=10)    # debug level

MG.Array = record(nx=2,       # no. of Array antenna elements in x-direction
                  ny=2,      # no. of Array antenna elements in y-direction
                  dx=5,       # separatuin (m) in x-direction
                  dy=7,       # separatuin (m) in y-direction
                  Feed='hdip')  # type of antenna element (Feed)

# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)






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



   # Various antennas:

   if False:
      obj = TDL_Antenna.Antenna()
      if False:
         # Make a bookmark for the sky temperature:
         node = obj.subtree_Tsky(ns)
         cc.append(node)
         JEN_bookmarks.create(node, page='Tsky')
      _experiment(ns, obj, cc)
   
   if True:
      dip_X = TDL_Dipole.HorizontalDipole(label='dip_X', azimuth=0)
      dip_Y = TDL_Dipole.HorizontalDipole(label='dip_Y', azimuth=pi/2)
      _experiment(ns, dip_X, cc, sensit=True, vbeam=True)
      _experiment(ns, dip_Y, cc, sensit=True, vbeam=True)
      obj = TDL_Antenna.Feed(dip_X, dip_Y)
      _experiment(ns, obj, cc, sensit=True, vbeam=True)

   if False:
      obj = TDL_Antenna.Feed()
      _experiment(ns, obj, cc, sensit=True, vbeam=True)


   if False:
      obj = TDL_Antenna.Array()
      for i in range(MG.Array['nx']):
         x = float(i+1)*MG.Array['dx']
         for j in range(MG.Array['ny']):
            y = float(j+1)*MG.Array['dy']
            label = 'antel_'+str(obj.nantel())
	    print label,x,y
            if False:
               antel = TDL_Antenna.Feed(label=label, pos0=[x,y,0.0])
            else:
               antel = TDL_Antenna.Feed(dip_X.copy(), dip_Y.copy(), label=label, pos0=[x,y,0.0])
            obj.new_element(antel, wgt=1.0, calc_derived=False)
      obj.Array_calc_derived()
      obj.pos0([1,2,3])
      obj.rotate_xy(0.1, recurse=1)
      _experiment(ns, obj, cc, sensit=False, vbeam=False)
   

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc, make_bookmark=False)



#----------------------------------------------------------------------------
# Helper function:
#----------------------------------------------------------------------------

def _experiment(ns, obj, cc=[], dcoll=True, sensit=False,
                vbeam=False, pbeam=False):

   if True:
      obj.display('MG_JEN_Antenna._experiment()')
      # MG_JEN_exec.display_subtree(obj, full=True, recurse=5)

   if dcoll:
      node = obj.dcoll_xy(ns)
      node = obj.dcoll_xy(ns)
      node = obj.dcoll_xy(ns)
      node = obj.dcoll_xy(ns)
      cc.append(node)
      JEN_bookmarks.create(node, page='config')

   if sensit:
      node = obj.subtree_sensit(ns)
      cc.append(node)
      JEN_bookmarks.create(node, page='sensitivity')

   if vbeam:
      bb = obj.subtree_voltage_beam(ns)
      bb = obj.subtree_voltage_beam(ns)
      bb = obj.subtree_voltage_beam(ns)
      for node in bb:
         cc.append(node)
         JEN_bookmarks.create(node, page='voltage_beam')
      node = obj.subtree_voltage_diff(ns)
      cc.append(node)
      JEN_bookmarks.create(node, page='voltage_diff')

   if pbeam:
      bb = obj.subtree_power_beam(ns)
      for node in bb:
         cc.append(node)
         JEN_bookmarks.create(node, page='power_beam')

   return True



#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


   
# NB: Put TDL_lofar_HBA.py classes here?





#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')
    # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')
    # return MG_JEN_exec.meqforest (mqs, parent)

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




