# MG_JEN_lsm_attach.py

# Short description:
#   A script to test attaching an lsm to a user tree

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 sep 2005: creation
# - 18 jan 2006: introduced TDL_Parmset.py

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
from Timba.Contrib.JEN import MG_JEN_Joneset

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

def _description():
    """
    Description of the input argument record: MG_JEN_lsm_attach.inarg
    (to be used with the MeqTree TDL stript MG_JEN_lsm_attach.py) 
    
    ....

    --------------------------------------------------------------------------
    General description of the MeqTree TDL script MG_JEN_lsm_attach.py:



    --------------------------------------------------------------------------
    Brief descriptions of the various sub-modules:

    """
    return True


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = JEN_inarg.init('MG_JEN_cps', description=_description.__doc__)

JEN_inarg.define (MG, 'last_changed', 'd11jan2006', editable=False)
JEN_inarg.define (MG, 'LSM', 'lsm_current.lsm', browse='*.lsm')
MG_JEN_exec.inarg_ms_name(MG)
MG_JEN_exec.inarg_tile_size(MG)
MG_JEN_Cohset.inarg_polrep(MG)
MG_JEN_Cohset.inarg_stations(MG)
MG_JEN_Cohset.inarg_parmtable(MG)
MG_JEN_Joneset.inarg_uvplane_effect(MG)    



#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------


inarg = MG_JEN_exec.stream_control(_getdefaults=True, slave=True)
JEN_inarg.modify(inarg,
                 tile_size=1,
                 _JEN_inarg_option=None)     
JEN_inarg.attach(MG, inarg)


inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
JEN_inarg.modify(inarg,
                 _JEN_inarg_option=None)         
JEN_inarg.attach(MG, inarg)



#----------------------------------------------------------------------------------

   
inarg = MG_JEN_Cohset.JJones(_getdefaults=True, slave=True) 
JEN_inarg.modify(inarg,
                 Jsequence=['KJones'],   
                 _JEN_inarg_option=None)          
JEN_inarg.attach(MG, inarg)


inarg = MG_JEN_Cohset.predict(_getdefaults=True, slave=True)  
JEN_inarg.modify(inarg,
                 _JEN_inarg_option=None)   
JEN_inarg.attach(MG, inarg)


#-------------------------------------------------------------------------

inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
JEN_inarg.modify(inarg,
                 _JEN_inarg_option=None)          
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

#-------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """..."""

   # The MG may be passed in from _tdl_predefine():
   # In that case, override the global MG record.
   global MG
   if len(kwargs)>1: MG = kwargs

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)  


   # Load the specified lsm into the global lsm object:
   global lsm
   lsm.load(MG['LSM'], ns) 
   # lsm.display()            # This locks the browser!

   # Make an empty vector of Cohsets:
   cs = []
 
   # Make MeqSpigot nodes that read the MS:
   Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                              polrep=MG['polrep'],
                              stations=MG['stations'])
   MG_JEN_Cohset.make_spigots(ns, Cohset, _inarg=MG)
   # Cohset.display('before')
   
   # Get the two-pack (nodes) for the position of the phase-centre:
   radec0 = MG_JEN_Cohset.MSauxinfo().radec0()
   print radec0

   # Obtain the Sixpacks of the brightest punits.
   # Turn the point-sources in Cohsets with DFT KJonesets
   plist = lsm.queryLSM(count=2)
   print '\n** plist =',type(plist),len(plist)
   for punit in plist: 
       sp = punit.getSP()            # get_Sixpack()
       qual = str(sp.label())
       # sp.display()
       if sp.ispoint():                # point source (Sixpack object)
           # node = sp.iquv()
           # node = sp.coh22(ns)
           js = MG_JEN_Cohset.JJones(ns, Sixpack=sp, _inarg=MG)
           predicted = MG_JEN_Cohset.predict (ns, Sixpack=sp, Joneset=js, _inarg=MG)
           cs.append(predicted)
       else:	                    # patch (not a Sixpack object!)
           node = sp.root()
           cc.append(node)

   # Add the point-source Cohsets to the mainstream Cohset:
   Cohset.add(ns, cs, exclude_itself=True)
   Cohset.display('after add')

   # Make MeqSink nodes that write the MS:
   sinks = MG_JEN_Cohset.make_sinks(ns, Cohset, _inarg=MG)
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
    """Execute the forest with a default domain"""
    # Timba.TDL.Settings.forest_state is a standard TDL name. 
    # This is a record passed to Set.Forest.State. 
    Settings.forest_state.cache_policy = 100;
    
    # Make sure our solver root node is not cleaned up
    Settings.orphans_are_roots = True;

    # Start the sequence of requests issued by MeqSink:
    MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
    return True





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
      igui.input(MG, set_open=False)
      igui.launch()
       

   if 0:
      MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
      # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
   print '\n** End of local test of:',MG['script_name'],'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




