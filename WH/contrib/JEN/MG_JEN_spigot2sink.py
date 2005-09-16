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

   # Attach data-stream info to the forest_state record:
   MG_JEN_forest_state.stream(MS='D1.MS')

   # Make the Cohset ifrs (and the Joneset stations):
   ifrs = TDL_Cohset.stations2ifrs(range(3,7))
   stations = TDL_Cohset.ifrs2stations(ifrs)

   Cohset = TDL_Cohset.Cohset(label=script_name, polrep='linear', stations=stations)
   Cohset.spigots(ns)
   Cohset.display('initial')

   MG_JEN_Cohset.visualise (ns, Cohset)
   MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

   if False:
       MG_JEN_Cohset.insert_flagger (ns, Cohset, scope='residual', unop=['Real','Imag'], visu=True)
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
       jones = ['D']
       jones = ['G','D']  
       jones = ['B']
       jones = ['G']
       Joneset = MG_JEN_Cohset.JJones(ns, stations, punit=punit, jones=jones,
                                                                fdeg_Gampl=0, tdeg_Gampl=0,
                                                                fdeg_Gphase=0, tdeg_Gphase=0)
       predicted = MG_JEN_Cohset.predict (ns, punit=punit, ifrs=ifrs, Joneset=Joneset)

       # Then specify the solvegroup of MeqParms to be solved for: 
       # solvegroup = 'DJones'
       solvegroup = ['DJones', 'GJones']
       solvegroup = 'BJones'
       solvegroup = 'GJones'
       MG_JEN_Cohset.insert_solver (ns, solvegroup=solvegroup,
                                    measured=Cohset, predicted=predicted, 
                                    correct=Joneset, num_iter=10)
       # NB: The data are corrected with the the improved Joneset:

       MG_JEN_Cohset.visualise (ns, Cohset)
       MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')


   Cohset.sinks(ns)
   for sink in Cohset: cc.append(sink)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)






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
   # from Timba.TDL import *
   from Timba.Meq import meq
   
   # Timba.TDL.Settings.forest_state is a standard TDL name. 
   # This is a record passed to Set.Forest.State. 
   Settings.forest_state.cache_policy = 100;
   
   # Make sure our solver root node is not cleaned up
   Settings.orphans_are_roots = True;


   inputrec = dmi.record();
   inputrec.sink_type = 'ms_in';
   inputrec.ms_name = 'D1.MS';
   inputrec.data_column_name = 'DATA';
   inputrec.tile_size = 1;

   inputrec.selection = dmi.record();
   # inputrec.selection.channel_start_index = 0;
   # inputrec.selection.channel_end_index = -1;
   inputrec.selection.channel_start_index = 10;
   inputrec.selection.channel_end_index = 50;
   
   outputrec = dmi.record();
   outputrec.sink_type = 'ms_out';
   outputrec.predict_column_name = 'PREDICT';
   outputrec.residuals_column_name = 'RESIDUALS';
   
   initrec = dmi.record()
   initrec.output_col = 'RESIDUALS'
   # initrec.python_init = 'read_msvis_header.py'
   
   mqs.init(initrec, inputinit=inputrec, outputinit=outputrec);






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




