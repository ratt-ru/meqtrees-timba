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


# The following parameters may be edited to change operation:

cps_parm = dict(ms_name='D1.MS',
                stations=range(7),                   # specify the (subset of) stations to be used
                data_column_name='DATA',
                tile_size=1,
                channel_start_index=10,
                channel_end_index=50,          # -10 should indicate 10 from the end
                output_col='RESIDUALS',
                punit='unpol',                        # name of calibrator source
                parmtable='cal_BJones',     # name of MeqParm table
                fdeg_Breal=3,                          # degree of freq polynomial
                fdeg_Bimag=3,
                tdeg_Breal=0,                          # degree of time polynomial
                tdeg_Bimag=0,
                num_iter=3,                             # number of solver iterations per snippet
                flag_before=False,                   # If True, insert a flagger before solving
                flag_after=False,                      # If True, insert a flagger after solving
                visu_rawdata=True,                # If True, insert built-in view(s) 
                visu_solver=True,                    # If True, insert built-in view(s) 
                visu_corrected=True,                # If True, insert built-in view(s)
                trace=False)                              # If True, produce progress messages  

   # Some alternatives:
   # punit = 'unpol'
   # punit = '3c147'
   # punit = 'RMtest'
   # punit = 'QUV'
   # punit = 'QU'
   # punit =  'SItest'


# Tree definition:

def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   # The control parameters are specified above:
   global cps_parm

   # Make spigots for a specific set of ifrs:
   ifrs = TDL_Cohset.stations2ifrs(cps_parm['stations'])
   stations = TDL_Cohset.ifrs2stations(ifrs)
   Cohset = TDL_Cohset.Cohset(label=MG.script_name, polrep='linear', stations=stations)
   # Cohset = TDL_Cohset.Cohset(label=MG.script_name, polrep='linear', ifrs=ifrs)
   Cohset.spigots(ns)

   if cps_parm['visu_rawdata']:
	MG_JEN_Cohset.visualise (ns, Cohset)
	MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

   if cps_parm['flag_before']:
       MG_JEN_Cohset.insert_flagger (ns, Cohset, scope='residual',
                                     unop=['Real','Imag'], visu=False)
       if cps_parm['visu_rawdata']: MG_JEN_Cohset.visualise (ns, Cohset)

   # Make predicted data with a punit (see above) and corrupting Jones matrices
   Joneset = MG_JEN_Cohset.JJones(ns, stations, punit=cps_parm['punit'], jones=['B'],
                                  fdeg_Breal=cps_parm['fdeg_Breal'],
                                  fdeg_Bimag=cps_parm['fdeg_Bimag'],
                                  tdeg_Breal=cps_parm['tdeg_Breal'],
                                  tdeg_Bimag=cps_parm['tdeg_Bimag'],
                                  parmtable=cps_parm['parmtable'])
   predicted = MG_JEN_Cohset.predict (ns, punit=cps_parm['punit'], ifrs=ifrs, Joneset=Joneset)

   # Insert a solver for a named solvegroup of MeqParms:
   reqseq = MG_JEN_Cohset.insert_solver (ns, solvegroup='BJones', 
                                         measured=Cohset, predicted=predicted, 
                                         correct=Joneset, 
					 num_iter=cps_parm['num_iter'], 
                                         visu=cps_parm['visu_solver'])
   # NB: The data are corrected with the the improved Joneset:
   if cps_parm['visu_corrected']:
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
   global cps_parm                             # specified above
   for key in ['ms_name','data_column_name','tile_size']:
      MG_JEN_exec.stream_inputinit(key, cps_parm[key])
   for key in ['channel_start_index','channel_end_index']:
      MG_JEN_exec.stream_selection(key, cps_parm[key])
   for key in []:
      MG_JEN_exec.stream_outputinit(key, cps_parm[key])
   for key in ['output_col']:
      MG_JEN_exec.stream_initrec(key, cps_parm[key])

   # Start the sequence of requests issued by MeqSink:
   # NB: If save=True, the meqforest is saved to a file for EVERY tile....!!
   MG_JEN_exec.spigot2sink(mqs, parent, save=False)
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




