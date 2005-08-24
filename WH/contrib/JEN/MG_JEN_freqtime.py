script_name = 'MG_JEN_freqtime.py'

# Short description:
# Make a leaf node that varies with freq and time

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Import Python modules:
from Timba.TDL import *
from Timba.Meq import meq

import MG_JEN_forest_state
import MG_JEN_bookmark

from numarray import *
# from string import *
# from copy import deepcopy

# import MG_JEN_....


#================================================================================
# Importable function(s): The essence of a MeqGraft script.
# To be imported into user scripts (see _def_forest() below) 
#================================================================================


def freqtime (ns, combine='Add', unop=False):
    """Make an input node that varies with freq and time:"""

    # Make the basic freq-time nodes:
    freq = ns << Meq.Freq()
    time = ns << Meq.Time()

    # Combine them (e.g. e.g. adding):
    output = ns.freqtime << getattr(Meq,combine)(children=[freq, time])

    # Optional: Apply zero or more unary operations on the output:
    # output = JEN_apply_unop (ns, unop, output) 

    # Finished:
    return output






#================================================================================
#================================================================================
#================================================================================
# Executable routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Parameters:
   combine = 'Add'
   # combine = 'ToComplex'
   unop = False
   # unop = 'Cos'
   unop = ['Cos','Sin']
   output = freqtime (ns, combine=combine, unop=unop)

   # Make some (pages of) bookmarks for easy viewing of the result:
   MG_JEN_bookmark.bookmark(output, page='result') 
   MG_JEN_bookmark.bookmark(output, page='result', viewer='Record Browser')

   # Make a (single) root node for use in _test_forest() below:
   global _test_root
   _test_root = '_test_root'
   root = ns[_test_root] << Meq.Selector(output)
   
   
#================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...
#================================================================================

MG_JEN_forest_state.init(script_name)


#================================================================================
# Test routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
#================================================================================


def _test_forest (mqs, parent):

   # Execute the forest with a 'suitable' request:
   cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=19);
   request = meq.request(cells,eval_mode=0);
   global _test_root                         # see _define_forest()
   mqs.meq('Node.Execute',record(name=_test_root, request=request));

   # Save the meqforest in a file:
   MG_JEN_forest_state.save(mqs)



#================================================================================
# Test routine to check the tree for consistency, in the absence of a browser
#================================================================================

if __name__ == '__main__':
   ns = NodeScope();
   define_forest(ns);
   ns.Resolve();
  
