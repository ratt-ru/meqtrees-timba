# MG_JEN_testall.py

# Short description:
#   Script that tests all MG_JEN_*.py scripts 

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

# from Timba.Meq import meq
from Timba.Contrib.JEN.util import JEN_bookmarks

from numarray import *

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_template

from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_util

from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_matrix

from Timba.Contrib.JEN import MG_JEN_flagger
from Timba.Contrib.JEN import MG_JEN_solver
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_historyCollect

from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Cohset
from Timba.Contrib.JEN import MG_JEN_spigot2sink


#-------------------------------------------------------------------------

MG = MG_JEN_exec.MG_init('MG_JEN_testall.py',
                         last_changed = 'h22sep2005')


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

   global nseq                # used in test_module()
   nseq = -1

   cc.append(test_module(ns, 'forest_state'))
   cc.append(test_module(ns, 'exec'))
   cc.append(test_module(ns, 'template'))
   # cc.append(test_module(ns, 'util'))
   
   cc.append(test_module(ns, 'funklet'))
   
   cc.append(test_module(ns, 'math'))
   cc.append(test_module(ns, 'matrix'))
   cc.append(test_module(ns, 'twig'))
   
   cc.append(test_module(ns, 'dataCollect'))
   cc.append(test_module(ns, 'historyCollect'))
   
   cc.append(test_module(ns, 'flagger'))
   cc.append(test_module(ns, 'solver'))
   
   cc.append(test_module(ns, 'Sixpack'))
   cc.append(test_module(ns, 'lsm'))

   cc.append(test_module(ns, 'Joneset'))
   cc.append(test_module(ns, 'Cohset'))

   cc.append(test_module(ns, 'spigot2sink'))
   cc.append(test_module(ns, 'cps_BJones'))
   cc.append(test_module(ns, 'cps_GJones'))
   cc.append(test_module(ns, 'cps_GDJones'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)









#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


def test_module(ns, name):

   # To avoid nodename clashes, give each MG script a different subscope:
   global nseq
   nseq += 1
   nsub = ns.Subscope(str(nseq))

   # Execute the function. The result is a root node:
   s = 'result = MG_JEN_'+name+'._define_forest(nsub)'
   exec s

   # Collect all the non-folder bookmarks into a nemed folder bookmark:
   # JEN_bookmarks.bookfolder('MG_JEN_'+name)

   # Return the resulting root node:
   return result




#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


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



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   if 0:
      MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=1)

   ns = NodeScope()

   if 1:
       MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
       # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




