# MG_JEN_cps.py

# Short description:
#   Script for reducing Central Point Source (cps) data:

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 21 jan 2006: creation (starting from MG_JEN_Cohset.py

# Copyright: The MeqTree Foundation 

#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble *********************************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *

from Timba.Trees import JEN_inarg
from Timba.Trees import JEN_inargGui
from Timba.Trees import TDL_Cohset
from Timba.Trees import TDL_Joneset
# from Timba.Trees import TDL_MSauxinfo
# from Timba.Trees import TDL_Sixpack

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset
# from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_dataCollect
# from Timba.Contrib.JEN import MG_JEN_historyCollect
# from Timba.Contrib.JEN import MG_JEN_flagger


try:
    from qt import *
except:
    pass;


#********************************************************************************
#********************************************************************************
#****************** PART II: Definition of importable functions *****************
#********************************************************************************
#********************************************************************************









#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

def description():
    """
    MG_JEN_cps_GJones.inarg: Estimate gain and phase (GJones) values that
    are valid for the entire field (uvplane effect).

    The MG_JEN_cps script is the basis for a range of uv-data operations
    that require only a Central Point Source (cps) as a selfcal model. This is
    particularly useful for reducing calibrator observations, i.e. fields with
    a strong point source with known parameters, in the centre of the field.
    But it can also be used for initial calibration of observations that have
    significant other sources in the field (but a dominating point-like source
    in the centre.

    Different operations may be specified by loading (and editing) socalled
    'inarg' records from files. These contain input arguments for generating
    a suitable MeqTree forest for the desired operation.
    
    - The selfcal model is a point source in the centre of the field.
      A range of source models for standard calibrators (e.g. 3c147 etc)
      is available, and also some customised source models (for experimentation)
    - uvplane_effect=True: All instrumental MeqParms have qualifier q=uvp.
    - solves for MeqParms that vary slowly in time, over large domains.
      This minimises contamination from other sources on the solution.

    """
    return True



#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_cps', description=description.__doc__)

JEN_inarg.define (MG, 'insert_solver', tf=True,
                  help='if True, insert a solver')
JEN_inarg.define (MG, 'insert_flagger', tf=False,
                  help='if True, insert a flagger')

# Define some overall arguments:
MG_JEN_Cohset.inarg_Cohset_common (MG, last_changed='d30jan2006')
JEN_inarg.modify(MG,
                 # A uvplane effect (q=uvp) is valid for the entire field
                 # (These are used by Cohset.precorrect()....
                 # parmtable name...?
                 uvplane_effect=True,
                 # Use large 'snippet' domains to minimise peeling contamination: 
                 tile_size=100,
                 _JEN_inarg_option=None)     


#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
JEN_inarg.attach(MG, inarg)


#----------------------------------------------------------------------------------------------------
# Operations on the raw uv-data:
#----------------------------------------------------------------------------------------------------

# inarg = MG_JEN_Cohset.insert_flagger(_getdefaults=True) 
# JEN_inarg.attach(MG, inarg)
   

#----------------------------------------------------------------------------------------------------
# Insert a solver:
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_Cohset.JJones(_getdefaults=True, slave=True) 
JEN_inarg.modify(inarg,
                 # Do a single solution over the (large) domain:
                 # NB: Do we need something like: subtile_size_*=None....?
                 subtile_size_Gampl=None,
                 subtile_size_Breal=None,
                 subtile_size_dang=None,
                 subtile_size_RM=None,
                 # Allow for slow variations in time:
                 # NB: The tdeg_Gphase etc are @tdeg_Gampl etc
                 # NB: Do we need something like: tdeg_*=None....?
                 tdeg_Gampl=3,
                 tdeg_Breal=3,
                 tdeg_dang=3,
                 tdeg_RM=3,
                 _JEN_inarg_option=None)     
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.predict(_getdefaults=True, slave=True)  
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, slave=True) 
JEN_inarg.attach(MG, inarg)
                 
#----------------------------------------------------------------------------------------------------
# Operations on the processed uv-data:
#----------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
JEN_inarg.attach(MG, inarg)
                 




#====================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG['script_name'])




#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _tdl_predefine (mqs, parent, **kwargs):
    res = True
    if parent:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        try:
            igui = JEN_inargGui.ArgBrowser(parent)
            igui.input(MG, set_open=False)
            res = igui.exec_loop()
            if res is None:
                raise RuntimeError("Cancelled by user");
        finally:
            QApplication.restoreOverrideCursor()
    return res




#**************************************************************************

def _define_forest (ns, **kwargs):
    """This is the triple-quote description string"""

    # The MG may be passed in from _tdl_predefine():
    # In that case, override the global MG record.
    global MG
    if len(kwargs)>1: MG = kwargs

    # Perform some common functions, and return an empty list (cc=[]):
    cc = MG_JEN_exec.on_entry (ns, MG)

    # Make MeqSpigot nodes that read the MS:
    Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                               polrep=MG['polrep'],
                               stations=MG['stations'])
    MG_JEN_Cohset.make_spigots(ns, Cohset, _inarg=MG)


    if False and MG['insert_flagger']:
        MG_JEN_Cohset.insert_flagger (ns, Cohset, **MG)
        MG_JEN_Cohset.visualise (ns, Cohset)
        MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')


    if MG['insert_solver']:
        Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=MG['punit'])
        Joneset = MG_JEN_Cohset.JJones(ns, Sixpack=Sixpack, _inarg=MG)
        predicted = MG_JEN_Cohset.predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)
        MG_JEN_Cohset.insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG)

    # Make MeqSink nodes that write the MS:
    sinks = MG_JEN_Cohset.make_sinks(ns, Cohset, _inarg=MG)
    cc.extend(sinks)

    # Finished: 
    return MG_JEN_exec.on_exit (ns, MG, cc)




#********************************************************************************
#********************************************************************************
#*******************  PART V: Forest execution routine(s) ***********************
#********************************************************************************
#********************************************************************************



def _test_forest (mqs, parent):
   
   # Timba.TDL.Settings.forest_state is a standard TDL name. 
   # This is a record passed to Set.Forest.State. 
   Settings.forest_state.cache_policy = 100;
   
   # Make sure our solver root node is not cleaned up
   Settings.orphans_are_roots = True;

   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   return True


def _tdl_job_noMS (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)


# Execute the forest for a sequence of requests:

def _tdl_job_sequence(mqs, parent):
    for x in range(10):
        MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                               f1=x, f2=x+1, t1=x, t2=x+1,
                               save=False, trace=False, wait=False)
    MG_JEN_exec.save_meqforest(mqs) 
    return True




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routine(s) ***********************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG['script_name'],':\n'

    # This is the default:
    if 0:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

    # This is the place for some specific tests during development.
    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG['script_name'], ifrs=ifrs)

    if 1:
        igui = JEN_inargGui.ArgBrowser()
        igui.input(MG, set_open=False)
        igui.launch()
       
    if 0:   
       cs.display('initial')
       
    if 0:
       cs.spigots (ns)

    if 0:
       punit = 'unpol'
       # punit = '3c147'
       # punit = 'RMtest'
       Sixpack = punit2Sixpack(ns, punit)

           
    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




