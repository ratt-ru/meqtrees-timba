# MG_JEN_NodeSet.py

# Short description:
#   Demonstration of TDL_NodeSet functions

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 06 feb 2006: creation


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
from Timba.Meq import meq

from numarray import *

from Timba.Contrib.JEN.util import TDL_NodeSet
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_NodeSet.py',
                         last_changed='d12feb2006',
                         ntime=1,
                         nfreq=30,
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

   # Apply an unary operation on a group:
   nst.apply_unop(ns, 'Ggain', unop='Cos', bookpage=True)

   # Apply an binary operation on two groups:
   nst.apply_binop(ns, ['Ggain_Y','Gphase_Y'], binop='ToComplex', bookpage=True)

   # Compare the Nodeset with itself:
   # cc.append(nst.compare(ns, nst, ['Gphase_Y'], bookpage=True))

   # Make a subtree of all bookpages:
   cc.append(nst.bookmark_subtree(ns))

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
   a1 = nst.group('Ggain_X', rider=pp, aa=1, bb=1, cc=1, trace=True)
   a2 = nst.group('Ggain_Y', rider=pp, aa=1, bb=2, cc=1)
   p1 = nst.group('Gphase_X', rider=pp, aa=1, bb=3, cc=2)
   p2 = nst.group('Gphase_Y', rider=pp, aa=1, bb=4, cc=2)
   
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
         nst.set_MeqNode (node, group=Ggain)
         
      for Gphase in [p1,p2]:
         node = ns[Gphase](i=i) << Meq.Multiply(-i,freq)
         nst.set_MeqNode (node, group=Gphase)

   # Define some bookpages:
   # nst.bookmark('GX', [a1,p1])
   # nst.bookmark('GY', [a2,p2])
   nst.apply_binop(ns, [a1,p1], 'Polar', bookpage='GJones')
   nst.apply_binop(ns, [a2,p2], 'Polar', bookpage='GJones')
   nst.cleanup()
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




