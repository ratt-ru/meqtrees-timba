script_name = 'MG_JEN_testall.py'

# Short description:
#   Script that tests all MG_JEN_*.py scripts 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 


#================================================================================
# Import of Python modules:

from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                    # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                  # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed


from Timba.TDL import *
# Possibly better, namespace-wise?
#   from Timba import TDL
#   from Timba.TDL import dmi_type, Meq, record, hiid

from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_template

from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_util

from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_matrix

from Timba.Contrib.JEN import MG_JEN_flagger
from Timba.Contrib.JEN import MG_JEN_solver
from Timba.Contrib.JEN import MG_JEN_dataCollect

# from Timba.Contrib.JEN import MG_JEN_Sixpack
from Timba.Contrib.JEN import MG_JEN_sixpack

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   # Generate a list (cc) of root nodes:
   cc = []

   global nseq                # used in test_module()
   nseq = -1

   cc.append(test_module(ns, 'forest_state'))
   cc.append(test_module(ns, 'exec'))
   cc.append(test_module(ns, 'template'))
   cc.append(test_module(ns, 'util'))
   
   cc.append(test_module(ns, 'funklet'))
   
   cc.append(test_module(ns, 'math'))
   cc.append(test_module(ns, 'matrix'))
   cc.append(test_module(ns, 'twig'))
   
   cc.append(test_module(ns, 'dataCollect'))
   # cc.append(test_module(ns, 'historyCollect'))
   
   cc.append(test_module(ns, 'flagger'))
   cc.append(test_module(ns, 'solver'))
   
   cc.append(test_module(ns, 'sixpack'))
   # cc.append(test_module(ns, 'Sixpack'))

   cc.append(test_module(ns, 'Joneset'))
   cc.append(test_module(ns, 'Cohset'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc, make_bookmark=False)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================

def test_module(ns, name):
   global nseq
   nseq += 1
   nsub = ns.Subscope(str(nseq))
   s = 'result = MG_JEN_'+name+'._define_forest(nsub)'
   exec s
   return result


#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)



#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   # The following call shows the default settings explicity:
   # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False) 

   # There are some predefined domains:
   # return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')   # (100-110 MHz)
   # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')    # (1350-1420 MHz)

   # NB: It is also possible to give an explicit request, cells or domain
   # NB: In addition, qualifying keywords will be used when sensible

   # If not explicitly supplied, a default request will be used.
   return MG_JEN_exec.meqforest (mqs, parent)



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',script_name,':\n'

   if 1:
      MG_JEN_exec.without_meqserver(script_name, callback=_define_forest, recurse=1)

   ns = NodeScope()

   if 0:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   if 0:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




