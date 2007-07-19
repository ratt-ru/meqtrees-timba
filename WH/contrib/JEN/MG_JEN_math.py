# MG_JEN_math.py

# Short description:
#   Helper functions for easy generation of (math) expression subtrees

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

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

MG = record(script_name='MG_JEN_math.py', last_changed = 'h22sep2005')

# from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
 
#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG.script_name)





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
   return MG_JEN_exec.on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


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
# Testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG.script_name,':\n'

    if 1:
        MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest)

    ns = NodeScope()

    if 0:
       node = ns << 0
       node = unop (ns, unop=['Cos','Sin'], node=node)
       MG_JEN_exec.display_subtree (node, 'unop', full=1)

    print '\n** End of local test of:',MG.script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




