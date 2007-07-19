# MG_JEN_flagger.py

# Short description:
#   Flagging subtrees

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 





#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

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

from Timba.TDL import *

from numarray import *
# from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_historyCollect

#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_flagger.py',
                         last_changed='h04oct2005',
                         aa=13,
                         bb='aa',                 # replace with value of referenced field  
                         trace=False)             # If True, produce progress messages  

MG.test1 = record(stddev=1,
                  unop='Exp')

MG.testcx = record(stddev=1,
                  unop='Exp',
                  sigma=3)

MG.test22 = record(stddev=2,
                   unop='Exp',
                   sigma=3)


# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)





#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   mm = []

   # Test1: dims=[1]   
   nsub = ns.Subscope('d1')
   bb = []
   bb.append(MG_JEN_twig.gaussnoise(ns, stddev=MG.test1['stddev'],
                                    unop=MG.test1['unop']))
   node = flagger(nsub, bb[0])
   for child in node.children: bb.append(child[1]) 
   bb.append(node)
   mm.append(node)
   cc.append(MG_JEN_exec.bundle(ns, bb, 'dims=1', show_parent=False))


   if True:
      # Testcx: complex dims=[1]   
      nsub = ns.Subscope('cxd1')
      bb = []
      bb.append(MG_JEN_twig.gaussnoise(ns, mean=complex(0),
                                       stddev=MG.testcx['stddev'],
                                       unop=MG.testcx['unop']))
      node = flagger(nsub, bb[0], sigma=MG.testcx['sigma'])
      for child in node.children: bb.append(child[1]) 
      bb.append(node)
      mm.append(node)
      cc.append(MG_JEN_exec.bundle(ns, bb, 'cx_dims=1', show_parent=False))


   # Test22: dims=[2,2] 
   nsub = ns.Subscope('d22')
   bb = []
   bb.append(MG_JEN_twig.gaussnoise(ns, dims=[2,2],
                                    stddev=MG.test22['stddev'],
                                    unop=MG.test22['unop']))
   node = flagger(nsub, bb[0], sigma=MG.test22['sigma'])
   for child in node.children: bb.append(child[1])
   bb.append(node)
   mm.append(node)
   cc.append(MG_JEN_exec.bundle(ns, bb, 'dims=[2,2]', show_parent=False))

   # Finally, merge the flags of the root-nodes of the above tests:
   cc.append(ns.Mflag_overall << Meq.MergeFlags(children=mm))
 
   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)









#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************

#======================================================================================
# Generic flagger subtree:


def flagger (ns, input, **pp):
   """insert one or more flaggers for the input data"""


   pp.setdefault('sigma', 5.0)          # flagging threshold
   pp.setdefault('unop', 'Abs')         # data-operation(s) before flagging (e.g. Abs, Arg, Real, Imag)
   pp.setdefault('oper', 'GT')          # do flag if OPER zero
   pp.setdefault('flag_bit', 1)         # flag_bit to be affected
   pp.setdefault('merge', True)         # if True, merge the flags of tensor input
   pp.setdefault('hcoll', True)         # if True, insert a historyCollect node
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

   # Make historyCollect nodes for the solver metrics 
   if pp.hcoll:
      output = MG_JEN_historyCollect.insert_hcoll_flags(ns, output,
                                                        page='hcoll_flags')
   
   return output









#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)



# Execute the forest for a sequence of requests:

def _tdl_job_sequence(mqs, parent):
   """Execute the forest for a sequence of requests with changing domains"""
   for x in range(10):
      MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             increment=True,
                             save=False, trace=False, wait=False)
   MG_JEN_forest_state.save_meqforest(mqs) 
   return True



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   if 0:
      MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest)

   ns = NodeScope()

   if 0:
      input = ns << 0
      rr = flagger (ns, input)
      MG_JEN_exec.display_subtree (rr, 'rr', full=1)

   if 1:
       MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
       # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




