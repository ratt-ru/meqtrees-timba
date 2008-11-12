"""
ClumpExec.py: TDL Script that executes Clump scripts.
"""

# file: ../JEN/Clump/ClumpExec.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 05 nov 2008: creation
#
# Description:
#
# Remarks:
#
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

from Timba.Contrib.JEN.control import TDLOptionManager as TOM

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc


#==============================================================================
# Import a ClumpClass to be used in the 2-pass system:
# NB: Un-commenting more than one is OK. ClumpClass refers to the last one.
#==============================================================================



from Timba.Contrib.JEN.Clump import Clump as ClumpClass 

from Timba.Contrib.JEN.Clump import templateClump as ClumpClass
# from Timba.Contrib.JEN.Clump import templateLeafClump as ClumpClass
# from Timba.Contrib.JEN.Clump import TwigClump as ClumpClass

from Timba.Contrib.JEN.Clump import ParmClump as ClumpClass
# from Timba.Contrib.JEN.Clump import SolverUnit as ClumpClass

# from Timba.Contrib.JEN.Clump import CorruptClump as ClumpClass

#### The base-class has all the specific functions, e.g. .visualize()
from Timba.Contrib.JEN.Clump import JonesClump as ClumpClass

#### The following contain multiple classes (GJones,FJones,EJones etc):
# from Timba.Contrib.JEN.Clump import templateJonesClump as ClumpClass
# from Timba.Contrib.JEN.Clump import WSRTJones as ClumpClass
# from Timba.Contrib.JEN.Clump import VLAJones as ClumpClass
# from Timba.Contrib.JEN.Clump import ATCAJones as ClumpClass
# from Timba.Contrib.JEN.Clump import LOFARJones as ClumpClass

#### Specific operations: .corrupt(jones), .correct(), .shiftPhaseCentre()
#### Also: visualize() reimplementation
# from Timba.Contrib.JEN.Clump import VisClump as ClumpClass

# from Timba.Contrib.JEN.Clump import SpigotClump as ClumpClass
# from Timba.Contrib.JEN.Clump import PeelingUnit as ClumpClass
# from Timba.Contrib.JEN.Clump import CatIISubtractUnit as ClumpClass
# from Timba.Contrib.JEN.Clump import FlaggingUnit as ClumpClass


#------------------------------------------------------------------------------
# First pass:
# This bit is executed whenever the module is imported (blue button etc)
#------------------------------------------------------------------------------


TCM = TOM.TDLOptionManager(__file__)
ns = NodeScope().Subscope('dryrun')
clump = ClumpClass.do_define_forest (ns=ns, TCM=TCM)
itsTDLCompileMenu = TCM.TDLMenu(trace=False)


#------------------------------------------------------------------------------
# Second pass:
#------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """
   This required function just calls ClumpClass.do_define_forest() for its second pass.
   """

   # Remove any bookmarks that were generated in the first pass:
   Settings.forest_state.bookmarks = []

   # The second pass through do_define_forest():
   # NB: NO TDLOptions are generated after this pass.
   localTCM = TOM.TDLOptionManager(TCM)
   clump = ClumpClass.do_define_forest (ns, TCM=localTCM)

   if clump:
      clump.rootnode()
      clump.show('ClumpExec._define_forest()', full=True)
   else:
      rootnode = ns.rootnode << Meq.Constant(-0.123456789)

   # Generate at least one node (just in case):
   node = ns.dummy << 1.0

   return True


#---------------------------------------------------------------
#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the node 'rootnode'
    """
    # domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    domain = meq.domain(1,10,-10,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=11, num_time=21)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
    return result
       

   



#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: ClumpExec.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   print '\n** End of standalone test of: ClumpExec.py:\n' 

#=====================================================================================





