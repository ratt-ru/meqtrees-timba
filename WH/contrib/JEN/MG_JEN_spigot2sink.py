script_name = 'MG_JEN_spigot2sink.py'
last_changed = 'h10sep2005'

# Short description:
#   Simple demo of actually dealing with uvdata from an MS 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 10 sep 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Trees import TDL_Cohset
# from Timba.Trees import TDL_Joneset
# from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_flagger


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)





#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns): 
   cc = MG_JEN_exec.on_entry (ns, script_name)

   visu = True

   # Attach data-stream info to the forest_state record:
   # MG_JEN_forest_state.stream(MS='D1.MS')

   # Make the Cohset ifrs (and the Joneset stations):
   ifrs = TDL_Cohset.stations2ifrs(range(4))
   stations = TDL_Cohset.ifrs2stations(ifrs)

   Cohset = TDL_Cohset.Cohset(label=script_name, polrep='linear', stations=stations)
   Cohset.spigots(ns)
   Cohset.display('initial')

   if visu:
	MG_JEN_Cohset.visualise (ns, Cohset)
	MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

   if False:
       MG_JEN_Cohset.insert_flagger (ns, Cohset, scope='residual', unop=['Real','Imag'], visu=True)
       if visu: MG_JEN_Cohset.visualise (ns, Cohset)

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
       jones = ['D']
       jones = ['G','D']  
       jones = ['B']
       # jones = ['G']
       Joneset = MG_JEN_Cohset.JJones(ns, stations, punit=punit, jones=jones,
                                                                fdeg_Gampl=0, tdeg_Gampl=0,
                                                                fdeg_Gphase=0, tdeg_Gphase=0)
       predicted = MG_JEN_Cohset.predict (ns, punit=punit, ifrs=ifrs, Joneset=Joneset)

       # Then specify the solvegroup of MeqParms to be solved for: 
       # solvegroup = 'DJones'
       solvegroup = ['DJones', 'GJones']
       solvegroup = 'BJones'
       # solvegroup = 'GJones'
       MG_JEN_Cohset.insert_solver (ns, solvegroup=solvegroup,
                                    measured=Cohset, predicted=predicted, 
                                    correct=Joneset, num_iter=10, visu=visu)
       # NB: The data are corrected with the the improved Joneset:
       if visu:
	MG_JEN_Cohset.visualise (ns, Cohset)
	MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')


   Cohset.sinks(ns)
   for sink in Cohset: cc.append(sink)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc,
                               create_ms_interface_nodes=True)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================













#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

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




#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    print '\n*******************\n** Local test of:',script_name,':\n'

    # This is the default:
    if 1:
        MG_JEN_exec.without_meqserver(script_name, callback=_define_forest, recurse=3)

    # This is the place for some specific tests during development.
    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=script_name, ifrs=ifrs)

    if 0:   
        cs.display('initial')
       

    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




