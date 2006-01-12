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
from Timba.Contrib.JEN import MG_JEN_Cohset

from Timba.Trees import TDL_Cohset
from Timba.Trees import JEN_inarg
from Timba.Trees import JEN_inargGui













#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = JEN_inarg.init('MG_JEN_lsm_attach.pyt')

# To be copied to other scipts:
JEN_inarg.define (MG, 'last_changed', 'd11jan2006', editable=False)
JEN_inarg.define (MG, 'lsm_current', 'lsm_current.lsm')
MG_JEN_Cohset.inarg_polrep(MG)
MG_JEN_Cohset.inarg_stations(MG)
MG_JEN_Cohset.inarg_parmtable(MG)



#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

#=======
if True:                                               # ... Copied from MG_JEN_Cohset.py ...
   MG['stream_control'] = dict()
   MG_JEN_Cohset.inarg_stream_control(MG['stream_control'])
   JEN_inarg.modify(MG['stream_control'],
                    tile_size=10,
                    _JEN_inarg_option=None)            # optional, not yet used 


   inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
   JEN_inarg.modify(inarg,
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 

   inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
   JEN_inarg.modify(inarg,
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 

#----------------------------------------------------------------------------------

   # Specify the name qualifier for (the inarg records of) this 'predict and solve' group.
   # NB: The same qualifier should be used when using the functions in _define_forest()
   qual = None
   qual = 'qual1'

   # Specify the sequence of zero or more (corrupting) Jones matrices:
   Jsequence = ['GJones'] 
   # Jsequence = ['BJones'] 
   # Jsequence = ['FJones'] 
   # Jsequence =['DJones_WSRT']             
   # Jsequence = ['GJones','DJones_WSRT']
   
   # Specify a list of MeqParm solvegroup(s) to be solved for:
   solvegroup = ['GJones']
   # solvegroup = ['DJones']
   # solvegroup = ['GJones','DJones']

   # Extra condition equations to be used:
   condition = []
   condition.append('Gphase_X_sum=0.0')
   condition.append('Gphase_Y_sum=0.0')
   # condition.append('Gphase_X_first=0.0')
   # condition.append('Gphase_Y_last=0.0')
   # condition.append('Bimag_X_sum=0.0')
   # condition.append('Bimag_Y_sum=0.0')
   # condition = []

   inarg = MG_JEN_Cohset.JJones(_getdefaults=True, _qual=qual, expect=Jsequence) 
   JEN_inarg.modify(inarg,
                    stations=MG['stations'],               # List of array stations
                    parmtable=MG['parmtable'],             # MeqParm table name
                    unsolvable=False,                      # If True, no solvegroup info is kept
                    polrep=MG['polrep'],                   # polarisation representation
                    Jsequence=Jsequence,                   # Sequence of corrupting Jones matrices 
                    _JEN_inarg_option=None)                # optional, not yet used 

   # Insert non-default Jones matrix arguments here: 
   #    (This is easiest by copying lines from MG_JEN_Joneset.py)
   if 'GJones' in Jsequence: 
       JEN_inarg.modify(inarg,
                        fdeg_Gampl=3,                      # degree of default freq polynomial         
                        fdeg_Gphase='fdeg_Gampl',          # degree of default freq polynomial          
                        tdeg_Gampl=1,                      # degree of default time polynomial         
                        tdeg_Gphase='tdeg_Gampl',          # degree of default time polynomial       
                        subtile_size_Gampl=0,                 # used in tiled solutions         
                        subtile_size_Gphase='subtile_size_Gampl', # used in tiled solutions         
                        _JEN_inarg_option=None)            # optional, not yet used 

   if 'BJones' in Jsequence: 
       JEN_inarg.modify(inarg,
                        fdeg_Breal=3,                      # degree of default freq polynomial        
                        fdeg_Bimag='fdeg_Breal',           # degree of default freq polynomial          
                        tdeg_Breal=0,                      # degree of default time polynomial         
                        tdeg_Bimag='tdeg_Breal',           # degree of default time polynomial    
                        subtile_size_Breal=0,                 # used in tiled solutions         
                        subtile_size_Bimag='subtile_size_Breal', # used in tiled solutions         
                        _JEN_inarg_option=None)            # optional, not yet used 

   inarg = MG_JEN_Cohset.predict(_getdefaults=True, _qual=qual)  
   JEN_inarg.modify(inarg,
                    ifrs=MG['ifrs'],                       # list of Cohset ifrs 
                    polrep=MG['polrep'],                   # polarisation representation
                    _JEN_inarg_option=None)                # optional, not yet used 
   JEN_inarg.attach(MG, inarg)




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
   print '\n*******************\n** Local test of:',MG['script_name'],':\n'

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 1:
      igui = JEN_inargGui.ArgBrowser()
      igui.input(MG, name=MG['script_name'], set_open=False)
      igui.launch()
       

   if 0:
      MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
      # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
   print '\n** End of local test of:',MG['script_name'],'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




