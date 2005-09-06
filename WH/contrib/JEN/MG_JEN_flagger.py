script_name = 'MG_JEN_flagger.py'

# Short description:
#   Flagging subtrees

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

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_twig


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []
   mm = []

   # Test: dims=[1]  (default)  
   nsub = ns.Subscope('d1')
   bb = []
   bb.append(MG_JEN_twig.gaussnoise(ns, stddev=1.5, unop='Exp'))
   node = flagger(nsub, bb[0])
   for child in node.children: bb.append(child[1]) 
   bb.append(node)
   mm.append(node)
   cc.append(MG_JEN_exec.bundle(ns, bb, 'dims=1', show_parent=False))

  # Test: dims=[2,2] (default) 
   nsub = ns.Subscope('d22')
   bb = []
   bb.append(MG_JEN_twig.gaussnoise(ns, dims=[2,2], stddev=2, unop='Exp'))
   node = flagger(nsub, bb[0], sigma=3)
   for child in node.children: bb.append(child[1])
   bb.append(node)
   mm.append(node)
   cc.append(MG_JEN_exec.bundle(ns, bb, 'dims=[2,2]', show_parent=False))

   # Finally, merge the flags of the root-nodes of the above tests:
   cc.append(ns.Mflag_overall << Meq.MergeFlags(children=mm))
 
  # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================


#======================================================================================
# Generic flagger subtree:


def flagger (ns, input, **pp):
   """insert one or more flaggers for the input data"""


   pp.setdefault('sigma', 5.0)          # flagging threshold
   pp.setdefault('unop', 'Abs')         # data-operation(s) before flagging (e.g. Abs, Arg, Real, Imag)
   pp.setdefault('oper', 'GT')          # do flag if OPER zero
   pp.setdefault('flag_bit', 1)         # flag_bit to be affected
   pp.setdefault('merge', True)         # if True, merge the flags of tensor input
   pp = record(pp)
   
   # Work on a stripped version, without derivatives, to save memory:
   stripped = ns.stripped << Meq.Stripper(input)

   # Make one or more flaggers for the various unops:
   if not isinstance(pp.unop, (list, tuple)): pp.unop = [pp.unop]
   zz = []
   for unop in pp.unop:
      # Work on real numbers (unop = Abs, Arg, Imag, Real)
      real = ns.real(unop) << getattr(Meq,unop)(stripped)
      # Make the subtree that calculates the zero-condition (zcond):
      mean = ns.mean(unop) << Meq.Mean(real)
      stddev = ns.stddev(unop) << Meq.StdDev(real)
      diff = ns.diff(unop) << (input - mean)
      absdiff = ns.absdiff(unop) << Meq.Abs(diff)
      sigma = ns.sigma(unop) << Meq.Constant(pp.sigma)
      threshold = ns.threshold(unop) << (stddev * sigma)
      zcond = ns.zcond(unop) << (absdiff - threshold)
      zz.append(zcond)

   # Flag the cells whose zcond values are 'oper' zero (e.g. oper=GT)
   # NB: Assume that ZeroFlagger can have multiple children
   zflag = ns.zflag << Meq.ZeroFlagger(children=zz,
                                        oper=pp.oper, flag_bit=pp.flag_bit)

   # The new flags are merged with those of the input node:
   output = ns.mflag << Meq.MergeFlags(children=[input,zflag])
   
   # Optional: merge the flags of multiple tensor elements of input/output:
   if pp.merge: output = ns.Mflag << Meq.MergeFlags(output)
   
   return output











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
   print '\n*******************\n** Local test of:',script_name,':\n'

   # This is the default:
   MG_JEN_exec.without_meqserver(script_name)

   # This is the place for some specific tests during development.
   ns = NodeScope()
   if 1:
      input = ns << 0
      rr = flagger (ns, input)
      MG_JEN_exec.display_subtree (rr, 'rr', full=1)

      
   print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




