script_name = 'MG_JEN_math.py'

# Short description:
#   Helper functions for easy generation of (math) expression subtrees

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Import Python modules:
from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
 


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   # Generate a list (cc) of one or more root nodes:
   cc = []

   # Make some (f,t) variable input node:
   freq = ns.freq(a=1, b=2) << Meq.Freq()
   time = ns.time(-5, b=2) << Meq.Time()
   input = ns.freqtime << Meq.Add(freq, time)
 
   # Test/demo of importable function: unop()
   unops = False
   unops = 'Cos'
   unops = ['Sin','Cos']
   cc.append(unop(ns, unops, input))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)










#================================================================================
# Optional: Importable function(s): To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------
# Function to apply zero or more unary operations on the given node:

def unop (ns, unop=False, node=0, right2left=False):
    if unop == None: return node                  # do nothing
    if isinstance(unop, bool): return node        # do nothing
    if isinstance(unop, str): unop = [unop]       # do nothing
    if not isinstance(unop, list): return node    # do nothing
    if len(unop)==0: return node                  # do nothing
    unops = unop                         # avoid mutation of unop
    if right2left: unops.reverse()       # perform in right2left order
    for unop1 in unops:                  # order: left2right of unops vector
        if isinstance(unop1, str):
            node = ns << getattr(Meq, unop1)(node)
    return node
   

#-------------------------------------------------------------------------------






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
# If not explicitly supplied, a default request will be used.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    if False:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n*******************\n** Local test of:',script_name,':\n'
       ns = NodeScope()
       node = ns << 0
       node = unop (ns, unop=['Cos','Sin'], node=node)
       MG_JEN_exec.display_subtree (node, 'unop', full=1)
       print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




