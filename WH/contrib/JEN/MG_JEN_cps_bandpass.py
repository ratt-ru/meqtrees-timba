# MG_JEN_cps_bandpass.py

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

MG = record(script_name='MG_JEN_spigot2sink.py', last_changed = 'h22sep2005')

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
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG.script_name)






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   visu = True         # If True, insert visualisers at various points

   # Make the Cohset ifrs (and the Joneset stations):
   ifrs = TDL_Cohset.stations2ifrs(range(4))
   stations = TDL_Cohset.ifrs2stations(ifrs)

   Cohset = TDL_Cohset.Cohset(label=MG.script_name, polrep='linear', stations=stations)
   Cohset.spigots(ns)

   if visu:
	MG_JEN_Cohset.visualise (ns, Cohset)
	MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

   if False:
       MG_JEN_Cohset.insert_flagger (ns, Cohset, scope='residual',
                                     unop=['Real','Imag'], visu=False)
       if visu:
          MG_JEN_Cohset.visualise (ns, Cohset)

   # Source/patch to be used for selfcal:
   punit = 'unpol'
   # punit = '3c147'
   # punit = 'RMtest'
   # punit = 'QUV'
   # punit = 'QU'
   # punit =  'SItest'

   if True:
       # Insert a solver for a named group of MeqParms (e.g. 'GJones'):
       # First make predicted data with a punit (see above) and corrupting Jones matrices
       Joneset = MG_JEN_Cohset.JJones(ns, stations, punit=punit, jones=['B'],
                                      parmtable='calibrator',
                                      fdeg_Breal=3, tdeg_Breal=0,
                                      fdeg_Bimag=3, tdeg_Bimag=0)
       predicted = MG_JEN_Cohset.predict (ns, punit=punit, ifrs=ifrs, Joneset=Joneset)

       # Then specify the solvegroup of MeqParms to be solved for: 
       reqseq = MG_JEN_Cohset.insert_solver (ns, solvegroup='BJones', 
                                             measured=Cohset, predicted=predicted, 
                                             correct=Joneset, num_iter=3, visu=visu)
       # NB: The data are corrected with the the improved Joneset:
       if visu:
          MG_JEN_Cohset.visualise (ns, Cohset)
          MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

   # Make MeqSinks
   Cohset.sinks(ns)
   for sink in Cohset: cc.append(sink)

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

   # Modify the stream_control record, if required:
   MG_JEN_exec.stream_inputinit('ms_name', 'D1.MS')
   MG_JEN_exec.stream_selection('channel_start_index', 10)
   MG_JEN_exec.stream_selection('channel_end_index', 50)

   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent)
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

    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG.script_name,'\n*******************\n'


#********************************************************************************
#********************************************************************************




