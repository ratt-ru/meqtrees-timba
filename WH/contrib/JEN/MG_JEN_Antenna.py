# MG_JEN_Antenna.py

# Short description:
#   Functions for simulating (LOFAR) station beams

# Keywords: ....

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

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Trees import TDL_Antenna
# from Timba.Contrib.MXM import MG_MXM_functional
# from Timba.Contrib.SBY import MG_SBY_dipole_beam


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_Antenna.py',
                         last_changed='h17oct2005',
                         aa=13,
                         bb='aa',                 # replace with value of referenced field  
                         trace=False)             # If True, produce progress messages  


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

   ant = TDL_Antenna.Antenna()
   dcoll = ant.dcoll_xy(ns)
   cc.append(dcoll)
   sensit = ant.subtree_sensit(ns)
   cc.append(sensit)

   dip = TDL_Antenna.Dipole()
   dcoll = dip.dcoll_xy(ns)
   cc.append(dcoll)

   arr = TDL_Antenna.Array()
   arr.testarr()
   dcoll = arr.dcoll_xy(ns)
   cc.append(dcoll)
   sensit = arr.subtree_sensit(ns)
   cc.append(sensit)

   stat = TDL_Antenna.Station()
   dcoll = stat.dcoll_xy(ns)
   cc.append(dcoll)


  # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)







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


def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    return MG_JEN_exec.meqforest (mqs, parent)





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




