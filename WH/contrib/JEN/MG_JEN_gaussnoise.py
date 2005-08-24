script_name = 'MG_JEN_gausnoise.py'

# Short description:
# Make a leaf node with gaussian noise

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


def gaussnoise (ns, stddev=1, mean=0, complex=False, dims=[1], unop=False):
    """makes gaussian noise"""

    # Determine the nr (nel) of tensor elements:
    if not isinstance(dims, (list, tuple)): dims = [dims]
    nel = sum(dims)
    # print 'nel =',nel

    # NB: What about making/giving stddev as a MeqParm...?

    # The various tensor elements have different noise, of course:
    # NB: Is this strictly necessary? A single GaussNoise node would
    #     be requested separately by each tensor element, and produce
    #     a separate set of values (would it, for the same request..........?)
    #     So a single GaussNoise would be sufficient (for all ifrs!)
    #     provided they would have the same stddev
    cc = []
    for i in range(nel):
      if complex:
        real = ns.real(i) << Meq.GaussNoise(stddev=stddev)
        imag = ns.imag(i) << Meq.GaussNoise(stddev=stddev)
        cc.append (ns.gaussnoise(i) << Meq.ToComplex(children=[real, imag]))
      else:
        cc.append (ns.gaussnoise(i) << Meq.GaussNoise(stddev=stddev))

    # Make into a tensor node, if necessary:
    output = cc[0]
    if nel>1: output = ns.gaussnoise << Meq.Composer(children=cc, dims=dims)

    # Optional: Add the specified mean:
    if abs(mean)>0:
      if not complex and isinstance(mean, complex): mean = mean.real
      output = output + mean

    # Optional: Apply zero or more unary operations on the output (e.g Exp):
    # output = JEN_apply_unop (ns, unop, output) 

    return output



#================================================================================
#================================================================================
#================================================================================
# Executable routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Parameters:
   dims = [1]
   dims = [2,2]
   unop = False
   unop = 'Exp'
   noisy = gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims, unop=unop)

   # Make some (pages of) bookmarks for easy viewing of the result:
   MG_JEN_bookmark.bookmark(noisy, page='result') 
   MG_JEN_bookmark.bookmark(noisy, page='result', viewer='Record Browser')

   # Make a (single) root node for use in _test_forest() below:
   global _test_root
   _test_root = '_test_root'
   root = ns[_test_root] << Meq.Selector(noisy)
   
   
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
  
