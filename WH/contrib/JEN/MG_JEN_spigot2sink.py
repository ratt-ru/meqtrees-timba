# MG_JEN_spigot2sink.py

# Short description:
#   Simple demo of actually dealing with uvdata from an MS 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 10 sep 2005: creation
# - 09 dec 2005: switched to Cohset.coll()

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


MG = MG_JEN_exec.MG_init('MG_JEN_spigot2sink.py',
                         last_changed = 'd09dec2005',
                         punit='unpol',                        # name of calibrator source
                         stations=range(4),                   # specify the (subset of) stations to be used
                         parmtable=None,                      # name of MeqParm table
                         MS_corr_index = [0,1,2,3],              # correlations to be used
                         # MS_corr_index = [0,-1,-1,1],          # only XX/YY available
                         # MS_corr_index = [0,-1,-1,3],          # all available, but use only XX/YY
                         # output_col='RESIDUALS',
                         output_col='PREDICT',
                         
                         insert_solver=True,                   # if True, insert a GJones solver
                         # num_cells=[2,5],                       # resampling [ntime, nfreq] (None=ignore)
                         # num_cells=[10,10],                       # resampling [ntime, nfreq] (None=ignore)
                         num_iter=20,                             # (max) number of solver iterations per snippet
                         epsilon=1e-4,                            # iteration stop criterion (policy-free)
                         subtract_cps=True,                   # if True, subtract the cps
                         correct_data=False,                   # if True, correct the uv-data

                         fdeg_Gampl=2,                          # degree of freq polynomial
                         fdeg_Gphase='fdeg_Gampl',
                         tdeg_Gampl=1,                          # degree of time polynomial
                         tdeg_Gphase='tdeg_Gampl',
                         tile_size_Gampl=None,                   # used in tiled solutions
                         tile_size_Gphase='tile_size_Gampl',
                         
                         fdeg_dang=2,                          # degree of freq polynomial
                         fdeg_dell='fdeg_dang',
                         tdeg_dang=1,                          # degree of time polynomial
                         tdeg_dell='tdeg_dang',
                         tile_size_dang=None,                   # used in tiled solutions
                         tile_size_dell='tile_size_dang',
                         
                         flag_spigots=False,                   # If True, insert a flagger before solving
                         flag_sinks=False,                      # If True, insert a flagger after solving
                         visu_spigots=True,               # If True, insert built-in view(s) 
                         visu_solver=True,                    # If True, insert built-in view(s) 
                         visu_sinks=True,                # If True, insert built-in view(s)
                         trace=False)                              # If True, produce progress messages  

MG.stream_control = record(ms_name='D1.MS',
                           data_column_name='DATA',
                           tile_size=10,                              # input tile-size
                           channel_start_index=10,
                           channel_end_index=50,          # -10 should indicate 10 from the end (OMS...)
                           # output_col='RESIDUALS')
                           predict_column='CORRECTED_DATA')

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

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   # Make the Cohset ifrs (and the Joneset stations):
   ifrs = TDL_Cohset.stations2ifrs(MG['stations'])
   stations = TDL_Cohset.ifrs2stations(ifrs)
   Cohset = TDL_Cohset.Cohset(label=MG['script_name'], polrep='linear', stations=stations)

   # Make MeqSpigot nodes that read the MS:
   MG_JEN_Cohset.make_spigots(ns, Cohset, MS_corr_index=MG['MS_corr_index'],
                              visu=MG['visu_spigots'], flag=MG['flag_spigots'])

   if MG['insert_solver']:
       # Optional: Insert a solver for a named group of MeqParms (e.g. 'GJones'):
       # First make predicted data with a punit (see above) and corrupting Jones matrices
       jones = ['D']
       jones = ['G','D']  
       jones = ['B']
       jones = ['G']
       Sixpack = MG_JEN_Cohset.punit2Sixpack (ns, MG['punit'])
       Joneset = MG_JEN_Cohset.JJones (ns, jones=jones, Sixpack=Sixpack, **MG)
       predicted = MG_JEN_Cohset.predict (ns, ifrs=ifrs, Sixpack=Sixpack, Joneset=Joneset)

       # After solving, the predicted (punit) uv-model may be subtracted: 
       subtract = None
       if MG['subtract_cps']: subtract = predicted
       # After solving, the uv-data are corrected with the the improved Joneset. 
       correct = None
       if MG['correct_data']: correct = Joneset

       # Then specify the solvegroup of MeqParms to be solved for: 
       # solvegroup = 'DJones'
       solvegroup = ['DJones', 'GJones']
       solvegroup = 'BJones'
       solvegroup = 'GJones'
       MG_JEN_Cohset.insert_solver (ns, solvegroup=solvegroup, 
                                    measured=Cohset, predicted=predicted, 
                                    subtract=subtract, correct=correct,
                                    visu=MG['visu_solver'], **MG)

   # Make MeqSink nodes that write the MS:
   sinks = MG_JEN_Cohset.make_sinks(ns, Cohset,  output_col=MG['output_col'],
                                    flag=MG['flag_sinks'], visu=MG['visu_sinks'])
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
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG['stream_control'])
   return True




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG['script_name'],':\n'

    if 1:
        MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG['script_name'], ifrs=ifrs)

    if 0:   
        cs.display('initial')
       
    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'


#********************************************************************************
#********************************************************************************




