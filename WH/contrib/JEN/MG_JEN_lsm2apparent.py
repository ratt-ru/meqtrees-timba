# MG_JEN_lsm2apparent.py

# Short description:
#   A script for turning a given LSM into an apparent one.

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 29 jan 2006: creation, copied from MG_JEN_lsm_attach.py

# Copyright: The MeqTree Foundation

# Full description:


#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

   





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

from Timba.Contrib.JEN.util import TDL_Cohset
from Timba.Contrib.JEN.util import JEN_inarg
from Timba.Contrib.JEN.util import JEN_inargGui













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

MG = JEN_inarg.init('MG_JEN_lsm2apparent.pyt')

# To be copied to other scipts:
JEN_inarg.define (MG, 'last_changed', 'd27jan2006', editable=False)
JEN_inarg.define (MG, 'lsm', 'lsm_current.lsm', browse='*.lsm')
MG_JEN_Cohset.inarg_polrep(MG)
MG_JEN_Cohset.inarg_stations(MG)
MG_JEN_Cohset.inarg_parmtable(MG)



#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

#=======
if True:                                               # ... Copied from MG_JEN_Cohset.py ...
   inarg = MG_JEN_exec.stream_control(_getdefaults=True)
   JEN_inarg.modify(inarg,
                    tile_size=10,
                    _JEN_inarg_option=None)     
   JEN_inarg.attach(MG, inarg)


   inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
   JEN_inarg.modify(inarg,
                    _JEN_inarg_option=None)         
   JEN_inarg.attach(MG, inarg)
                 

   inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
   JEN_inarg.modify(inarg,
                    _JEN_inarg_option=None)          
   JEN_inarg.attach(MG, inarg)
                 

#----------------------------------------------------------------------------------

   # Specify the name qualifier for (the inarg records of) this 'predict and solve' group.
   # NB: The same qualifier should be used when using the functions in _define_forest()
   qual = None
   # qual = 'qual1'

   # Specify the sequence of zero or more (corrupting) Jones matrices:
   Jsequence = ['KJones'] 
   # Jsequence = ['GJones'] 
   
   inarg = MG_JEN_Cohset.Jones(_getdefaults=True, _qual=qual, slave=True) 
   JEN_inarg.modify(inarg,
                    Jsequence=Jsequence,                   # Sequence of corrupting Jones matrices 
                    _JEN_inarg_option=None)          
   # Insert non-default Jones matrix arguments here: 
   if 'GJones' in Jsequence: 
       JEN_inarg.modify(inarg,
                        shape_Ggain=[2,4],
                        subtile_size_Ggain=0,                 # used in tiled solutions         
                        subtile_size_Gphase='subtile_size_Ggain', # used in tiled solutions         
                        _JEN_inarg_option=None)     
   JEN_inarg.attach(MG, inarg)


   inarg = MG_JEN_Cohset.predict(_getdefaults=True, _qual=qual, slave=True)  
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
   lsm.load(MG['lsm'], ns) 
   # lsm.display()            # This locks the browser!

   # Make an empty vector of Cohsets:
   cs = []
 
   # Make MeqSpigot nodes that read the MS:
   Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                              polrep=MG['polrep'],
                              stations=MG['stations'])
   MG_JEN_Cohset.make_spigots(ns, Cohset, _inarg=MG)
   
   # Obtain the Sixpacks of the brightest punits.
   # Turn the point-sources in Cohsets with DFT KJonesets
   plist = lsm.queryLSM(count=4)
   print '\n** plist =',type(plist),len(plist)
   for punit in plist: 
       sp = punit.getSP()            # get_Sixpack()
       qual = str(sp.label())
       # sp.display()
       if sp.ispoint():                # point source (Sixpack object)
           # node = sp.iquv()
           # node = sp.coh22(ns)
           js = MG_JEN_Cohset.Jones(ns, Sixpack=sp, _inarg=MG)
           predicted = MG_JEN_Cohset.predict (ns, Sixpack=sp, Joneset=js, _inarg=MG)
           cs.append(predicted)
       else:	                    # patch (not a Sixpack object!)
           node = sp.root()
           cc.append(node)

   # Replace the mainstream Cohset with (the sum of) the Cohset(s) cs:
   Cohset.replace(ns, cs)
   Cohset.display('after replace')

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




