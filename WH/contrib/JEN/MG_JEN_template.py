script_name = 'MG_JEN_template.py'

# Short description:
#   Template for the generation of MeqGraft scripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# How to use this template:
# - Copy it to a suitably named script file (e.g. MG_JEN_xyz.py)
# - Fill in the correct script_name at the top
# - Fill in the author and the short description
# - Replace the example importable function with specific ones
# - Make the specific _define_forest() function
# - Remove this 'how to' recipe

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

# from Timba.Contrib.JEN import MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_math
# from Timba.Contrib.JEN import MG_JEN_funklet


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Test/demo of importable function: .example1()
   bb = []
   bb.append(example1 (ns, arg1=1, arg2=2))
   bb.append(example1 (ns, arg1=3, arg2=4))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.example1()', show_parent=False))

   # Test/demo of importable function: .example2()
   bb = []
   bb.append(example2 (ns, arg1=1, arg2=5))
   bb.append(example2 (ns, arg1=1, arg2=6))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.example2()', show_parent=True))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================

#-------------------------------------------------------------------------------
# Example:

def example1(ns, qual='auto', **pp):

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_template_example')

    default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
    node = ns.dummy(qual) << Meq.Parm(default)
    return node

def example2(ns, qual='auto', **pp):

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_template_example')

    default = array([[1, pp['arg1']/100],[pp['arg2']/100,0.1]])
    node = ns.dummy(qual) << Meq.Parm(default)
    return node






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

   # Generic test:
   MG_JEN_exec.without_meqserver(script_name)

   # Various specific tests:
   # ns = TDL.NodeScope()          # if used: from Timba import TDL
   ns = NodeScope()                # if used: from Timba.TDL import *

   if 1:
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




