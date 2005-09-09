script_name = 'MG_JEN_solver.py'

# Short description:
#   Simplest possible demo(s) of a solver


# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 23 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_funklet

# from Timba.Contrib.JEN import MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_math



#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   cc = []

   # Parameters:
   dflt_a = 1
   dflt_b = -1
   dflt_a = array([1,.3])
   dflt_b = array([-1,-.3])
   dflt_a = array([[1,.3,.1],[.1,.2,.3]])
   dflt_b = array([[-1,-.3,.1],[.1,.2,-.3]])
   
   # Make a solver with a single condeq, with children a and b:
   a = ns.a << Meq.Parm(dflt_a, node_groups='Parm')
   b = ns.b << Meq.Parm(dflt_b, node_groups='Parm')
   condeq = ns << Meq.Condeq(a,b)
   solver = ns << Meq.Solver(condeq, solvable=[a], num_iter=10, debug_level=10)
   cc.append(solver)
   
   # Make a page of bookmarks for easy viewing:
   page_name = 'solver'
   MG_JEN_forest_state.bookmark(a, page=page_name)
   MG_JEN_forest_state.bookmark(b, page=page_name)
   MG_JEN_forest_state.bookmark(solver, page=page_name)
   MG_JEN_forest_state.bookmark(condeq, page=page_name)
   MG_JEN_forest_state.bookmark(solver, page=page_name, viewer='ParmFiddler')
   
   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)




#================================================================================
# OPtional: Importable function(s): To be imported into user scripts. 
#================================================================================








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
   ns = NodeScope()

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




