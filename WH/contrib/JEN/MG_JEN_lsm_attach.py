# MG_JEN_lsm_attach.py

# Short description:
#   A script to test attaching an lsm to a user tree

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 sep 2005: creation

# Copyright: The MeqTree Foundation

# Full description:


   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

# from numarray import *
# from string import *
# from copy import deepcopy
from random import *

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *
from Timba.Contrib.JEN import MG_JEN_Sixpack
from Timba.Contrib.SBY import MG_SBY_grow_tree

from Timba.Contrib.JEN import MG_JEN_Cohset
from Timba.Trees import TDL_Cohset


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_lsm_attach.py',
                         last_changed='h29sep2005',
                         lsm_current='lsm_current.lsm', 
                         stations=range(2),      
                         trace=False)        

# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)

# NB: Using False here does not work, because it regards EVERYTHING
#        as an orphan, and deletes it.....!?
# Settings.orphans_are_roots = True


# Create an empty global lsm, just in case:
lsm = LSM()



#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns):
   """Dummy function, just to define global nodescope my_ns"""
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)  

   # Load the specified lsm into the global lsm object:
   global lsm
   lsm.load(MG['lsm_current'],ns) 
   # lsm.display() 

   # Make an empty vector of Cohsets:
   cs = []
 
   ifrs = TDL_Cohset.stations2ifrs(MG['stations'])
   # stations = TDL_Cohset.ifrs2stations(ifrs)

   # Obtain the Sixpacks of the brightest punits.
   # Turn the point-sources in Cohsets with DFT KJonesets
   plist = lsm.queryLSM(count=2)
   for punit in plist: 
      sp = punit.getSP()            # get_Sixpack()
      sp.display()
      if sp.ispoint():                # point source (Sixpack object)
         # node = sp.iquv()
         # node = sp.coh22(ns) 
         cs.append(MG_JEN_Cohset.simulate(ns, ifrs, Sixpack=sp, jones=['K']))
      else:	                    # patch (not a Sixpack object!)
         node = sp.root()
         cc.append(node)

   # Add the point-source Cohsets together, doing the DFT:
   cs[0].add(ns, cs, exclude_itself=True)

   # Tie the trees for the different ifrs together in an artificial 'sink':
   cc.append(cs[0].simul_sink(ns))

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
    return MG_JEN_exec.meqforest (mqs, parent, domain='21cm',
                               nfreq=100, ntime=100, t1=0, t2=100)
    # return MG_JEN_exec.meqforest (mqs, parent)





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

   if 0:
      MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
      # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




