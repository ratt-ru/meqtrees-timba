# MG_JEN_cps_BJones.py

# Short description:
#   Bandpass calibration on a Central Point Source (cps) 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 25 sep 2005: creation

# Copyright: The MeqTree Foundation

# Full description:


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Trees import TDL_Cohset
from Timba.Contrib.JEN import MG_JEN_Cohset

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Contrib.JEN import MG_JEN_flagger


#-------------------------------------------------------------------------
# MG control record (may be edited here)

   # Some alternatives:
   # punit = 'unpol'
   # punit = '3c147'
   # punit = 'RMtest'
   # punit = 'QUV'
   # punit = 'QU'
   # punit =  'SItest'


MG = MG_JEN_exec.MG_init('MG_JEN_cps_BJones.py',
                         last_changed = 'd28sep2005',
                         punit='unpol',                        # name of calibrator source
                         stations=range(4),                   # specify the (subset of) stations to be used
                         parmtable=None,                        # name of MeqParm table
                         
                         fdeg_Breal=3,                          # degree of freq polynomial
                         fdeg_Bimag='fdeg_Breal',
                         tdeg_Breal=1,                          # degree of time polynomial
                         tdeg_Bimag='tdeg_Breal',
                         tile_size_Breal=None,                   # used in tiled solutions
                         tile_size_Bimag='tile_size_Breal', 
                         
                         num_iter=20,                             # (max) number of solver iterations per snippet
                         epsilon=1e-4,                            # iteration stop criterion (policy-free)
                         flag_spigots=False,                   # If True, insert a flagger before solving
                         flag_sinks=False,                      # If True, insert a flagger after solving
                         visu_spigots=True,                     # If True, insert built-in view(s) 
                         visu_solver=False,                    # If True, insert built-in view(s) 
                         visu_sinks=True,                          # If True, insert built-in view(s)
                         trace=False)                              # If True, produce progress messages  

MG.stream_control = record(ms_name='D1.MS',
                           data_column_name='DATA',
                           tile_size=10,                              # input tile-size
                           channel_start_index=10,
                           channel_end_index=50,          # -10 should indicate 10 from the end (OMS...)
                           output_col='RESIDUALS')

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




# Tree definition:

def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   # Make spigots for a specific set of ifrs:
   ifrs = TDL_Cohset.stations2ifrs(MG['stations'])
   stations = TDL_Cohset.ifrs2stations(ifrs)
   Cohset = TDL_Cohset.Cohset(label=MG.script_name, polrep='linear', stations=stations)

   # Make MeqSpigot nodes that read the MS:
   MG_JEN_Cohset.make_spigots(ns, Cohset, visu=MG['visu_spigots'],
                              flag=MG['flag_spigots'])

   # Make predicted data with a punit (see above) and corrupting Jones matrices
   Sixpack = MG_JEN_Cohset.punit2Sixpack (ns, punit=MG['punit'])
   Joneset = MG_JEN_Cohset.JJones(ns, jones=['B'], Sixpack=Sixpack, **MG)
   predicted = MG_JEN_Cohset.predict (ns, ifrs=ifrs, Sixpack=Sixpack, Joneset=Joneset)

   # Insert a solver for a named solvegroup of MeqParms.
   # After solving, the uv-data are corrected with the the improved Joneset. 
   MG_JEN_Cohset.insert_solver (ns, solvegroup='BJones', 
                                measured=Cohset, predicted=predicted, 
                                correct=Joneset, 
                                visu=MG['visu_solver'], **MG)

   # Make MeqSink nodes that write the MS:
   sinks = MG_JEN_Cohset.make_sinks(ns, Cohset, flag=MG['flag_sinks'],
                                    visu=MG['visu_sinks'])
   cc.extend(sinks)

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
   
   # Timba.TDL.Settings.forest_state is a standard TDL name. 
   # This is a record passed to Set.Forest.State. 
   Settings.forest_state.cache_policy = 100;
   
   # Make sure our solver root node is not cleaned up
   Settings.orphans_are_roots = True;

   # Start the sequence of requests issued by MeqSink:
   # NB: If save=True, the meqforest is saved to a file for EVERY tile....!!
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG.stream_control, save=False)
   return True




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG.script_name,':\n'

    if 1:
        MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=3)

    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG.script_name, ifrs=ifrs)

    if 0:   
        cs.display('initial')
       
    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    if 1:
       MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
    print '\n** End of local test of:',MG.script_name,'\n*******************\n'


#********************************************************************************
#********************************************************************************




