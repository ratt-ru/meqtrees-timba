# MG_JEN_NodeSet.py

# Short description:
#   Demonstration of TDL_NodeSet functions

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 06 feb 2006: creation


# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *

from Timba.Trees import TDL_NodeSet
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_NodeSet.py',
                         last_changed='d12feb2006',
                         ntime=1,
                         nfreq=10,
                         trace=False)    


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


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   nst = make_NodeSet(ns)

   # Make a bookpage for all node groups:
   cc.append(nst.make_bookpage(ns, nst.group_keys(), 'all_groups'))

   # Make a bookpage for a particular group:
   cc.append(nst.make_bookpage(ns, ['Ggain_X']))

   # Make a bookpage for a particular group-of-groups (gog):
   cc.append(nst.make_bookpage(ns, 'Gphase'))

   # Apply an unary operation on a group:
   cc.append(nst.apply_unop(ns, 'Ggain', unop='Cos', bookpage=True))

   # Apply an binary operation on two groups:
   cc.append(nst.apply_binop(ns, ['Ggain_Y','Gphase_Y'], binop='Polar', bookpage=True))

   # Compare the Nodeset with itself:
   cc.append(nst.compare(ns, nst, ['Gphase_Y'], bookpage=True))

   # Show the contents of the final NodeSet:
   nst.display(MG['script_name'], full=True)

   #---------------------------------------------------------------------------
   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)







#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


def make_NodeSet(ns):

   nst = TDL_NodeSet.NodeSet(label='test')
    
   # Register the nodegroups:
   pp = dict(a=10, b=11)
   a1 = nst.group('Ggain_X', aa=1, bb=1, cc=1, **pp)
   a2 = nst.group('Ggain_Y', aa=1, bb=2, cc=1)
   p1 = nst.group('Gphase_X', aa=1, bb=3, cc=2)
   p2 = nst.group('Gphase_Y', aa=1, bb=4, cc=2)
   
   # Define extra gog(s) from combinations of nodegrouns:
   nst.gog('GJones', [a1, p1, a2, p2])
   nst.gog('Gpol1', [a1, p1])
   nst.gog('Gpol2', [a2, p2])
   nst.gog('Ggain', [a1, a2])
   nst.gog('Gphase', [p1, p2])
   nst.gog('grogog', [a1, p2, 'GJones'])

   # Make nodes themselves:
   freq = ns.freq << Meq.Freq()
   for i in range(12):
      for Ggain in [a1,a2]:
         node = ns[Ggain](i=i) << Meq.Multiply(i,freq)
         nst.MeqNode (Ggain, node=node)
         
      for Gphase in [p1,p2]:
         node = ns[Gphase](i=i) << Meq.Multiply(-i,freq)
         nst.MeqNode (Gphase, node=node)

   # Define some bookpages:
   nst.bookpage('GX', [a1,p1])
   nst.bookpage('GY', [a2,p2])
   nst.cleanup(ns)
   return nst


#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

x = 0

def _test_forest (mqs, parent):
   """One request at a time"""
   global x
   x += 1
   MG_JEN_exec.meqforest (mqs, parent, nfreq=MG['nfreq'], ntime=MG['ntime'],
                             f1=x, f2=x+1, t1=x, t2=x+1,
                             save=True, trace=False) 
   return True



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG['script_name'],':\n'

   if 1:
      MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=10)

   ns = NodeScope()                # if used: from Timba.TDL import *


   if 1:
       MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
       # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
   print '\n** End of local test of:',MG['script_name'],'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




