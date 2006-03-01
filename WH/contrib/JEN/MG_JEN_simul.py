# MG_JEN_simul.py

# Short description:
#   Script for putting simulated visibilities into an existing MS:

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 27 feb 2006: creation (starting from MG_JEN_cps.py

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

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset
from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


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

def _description():
    """
    Description of the input argument record: MG_JEN_simul_xxx.inarg
    (to be used with the MeqTree TDL stript MG_JEN_simul.py) 
    
    ....

    --------------------------------------------------------------------------
    General description of the MeqTree TDL script MG_JEN_simul.py:

    The MG_JEN_simul.py script is used to put simulated visibilities into the
    CORRECTED_DATA column of an existing Measurement Set (MS). The original DATA
    in the MS are untouched. The advantage of this approach is that it is not
    necessary to specify pointing centre, uv-coverage, spectral-window etc.

    * The input source model is either an existing Local Sky Model (LSM),
    or a 'punit' point source in the centre of the field.

    * The nominal source visibilities may be corrupted by:
      - various (uv-plane) Jones matrices
      - image-plane effects from EJones and IJones (MIM)
      - ifr-based errors (additive, multiplicative)
      - noise

    * Optionally, the simulated visibilities may be added to the existing uv-data,
    either from the DATA column or the CORRECTED_DATA column of the MS

    Different types of simulations may be specified by loading (and editing) socalled
    'inarg' records from files (like this one). These contain input arguments
    for generating a suitable MeqTree forest for the desired operation.


    --------------------------------------------------------------------------
    Brief descriptions of the various sub-modules:

    """
    return True



#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_simul', description=_description.__doc__)

# Define some overall arguments:
MG_JEN_Cohset.inarg_Cohset_common (MG, last_changed='d30jan2006')
JEN_inarg.modify(MG,
                 # A uvplane effect (q=uvp) is valid for the entire field
                 uvplane_effect=True,
                 # Use large 'snippet' domains: 
                 # tile_size=100,
                 _JEN_inarg_option=None)     

JEN_inarg.define (MG, 'add_to_existing', tf=False,
                  help='if True, add to existing uv-data (from MS column)')

JEN_inarg.define (MG, 'rms_noise_Jy', 0.0, choice=[0,0.01,0.1,1],
                  help='rms noise, to be added')

#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
JEN_inarg.modify(inarg,
                 data_column_name='CORRECTED_DATA',
                 channel_start_index=0,
                 channel_end_index=-1,
                 _JEN_inarg_option=None)     
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
JEN_inarg.attach(MG, inarg)

#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_Sixpack.newstar_source(_getdefaults=True) 
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.Jones(_getdefaults=True, slave=True, simul=True) 
JEN_inarg.attach(MG, inarg)

inarg = MG_JEN_Cohset.predict(_getdefaults=True, slave=True)  
JEN_inarg.attach(MG, inarg)

    
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
JEN_inarg.attach(MG, inarg)
                 


#====================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)



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
    """See _description()"""

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

    # Make a source Sixpack (I,Q,U,V,RA,Dec) from punit/LSM:
    Sixpack = MG_JEN_Sixpack.newstar_source(ns, _inarg=MG)

    # Optional: get corrupting (uv-plane) Jones matrices:
    Joneset = MG_JEN_Cohset.Jones(ns, Sixpack=Sixpack, simul=True, _inarg=MG)

    # Predict nominal/corrupted visibilities: 
    predicted = MG_JEN_Cohset.predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)

    # Opionally, add (gaussian) noise:
    if MG['rms_noise_Jy']>0:
        Cohset.addNoise(ns, MG['rms_noise_Jy'])

    # Replace/add the uv-data with/to the predicted visibilities: 
    if MG['add_to_existing']:
        Cohset.add(ns, predicted)
    else:
        Cohset.replace(ns, predicted)
    MG_JEN_Cohset.visualise (ns, Cohset)
    MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

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



# def _test_forest (mqs, parent):
def _tdl_job_execute (mqs, parent):
   """Execute the tree""" 
   
   # Timba.TDL.Settings.forest_state is a standard TDL name. 
   # This is a record passed to Set.Forest.State. 
   Settings.forest_state.cache_policy = 100;
   
   # Make sure our solver root node is not cleaned up
   Settings.orphans_are_roots = True;

   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   return True



def _tdl_job_fullDomainMux (mqs, parent):
   """Special for post-visualisation""" 
   
   # Timba.TDL.Settings.forest_state is a standard TDL name. 
   # This is a record passed to Set.Forest.State. 
   Settings.forest_state.cache_policy = 100;
   
   # Make sure our solver root node is not cleaned up
   Settings.orphans_are_roots = True;

   # Start the sequence of requests issued by MeqSink:
   MG_JEN_exec.fullDomainMux(mqs, parent, ctrl=MG)
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
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




