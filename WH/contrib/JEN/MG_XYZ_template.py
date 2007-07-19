# MG_XYZ_template.py

# Short description:
#   A template for the generation of MG stripts

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 15 sep 2006: creation

# Copyright: The MeqTree Foundation

# Full description:

# MG scripts should (roughly) have the following parts:
# - PART   I: Organised specific information about this script
# - PART  II: Preamble (import etc) and initialisation (if any)
# - PART III: Optional: Importable functions (to be used by other scripts)
# - PART  IV: Required: Test/Demo function _define_forest(), called from the meqbrowser
# - PART   V: Forest execution routine(s), called from the meqbrowser
# - PART  VI: Recommended: Standalone test routines (no meqbrowser or meqserver)

# This template is a regular MG script, which may be executed from the
# browser (to see how things work).  It is hoped that it will lead to
# a large collection of user-contributed scripts, which are readily
# accessible to all via the MeqTree 'Water Hole'.

# How to use this template:
# - Copy it to a script file with a name like this:
#      MG_<authorinitials>_<function>.py
# - Put it into your Water Hole sub-directory:
#      /Timba/WH/contrib/<author initials>/
# - Fill in the correct script_name (and other info) at the top of part I and II
# - Fill in the author and the short (one-line) description
# - Replace the full description with a specific one
# - Replace the example importable function with specific ones
# - Make the specific _define_forest() function. Try to make this
#   a complete test and demonstration of all its importable functions.
# - Write lots of explanatory comments throughout, preferably in the
#   form of Python 'doc-strings' at the start of each function.
# - Test everything thoroughly, without and with the browser.
# - Make it known to your MG_XYZ_testall.py script (see MG_XYZ_testall.py)
# - Check it in via SVN. After that, it is available to all,
#   and visible to the MG catalog and testing systems

# Of course, it is also possible, and often preferrable to just copy a
# working script from someone else, and cannibalise it.

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

   




 
#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

# from qt import *
# from numarray import *
# from string import *
# from copy import deepcopy

# Make sure that all nodes retain their results in their caches,
# for your viewing pleasure.
Settings.forest_state.cache_policy = 100


# NB: Demonstrate the OMS parameter system here (because it has browser support)?


#********************************************************************************
#********************************************************************************
#******************** PART III: Optional: Importable functions ******************
#********************************************************************************
#********************************************************************************







#********************************************************************************
#********************************************************************************
#**************** PART IV: Required test/demo function **************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Make two 'leaf' nodes that show some variation over freq/time. 
   a = ns['a'] << Meq.Time()
   b = ns['b'] << Meq.Freq()

   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Add(a,b)

   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result', viewer='Result Plotter',
               udi='/node/result', publish=True)
   Settings.forest_state.bookmarks = [bm]

   # Finished:
   return True







#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

# The function with the standard name _test_forest(), and any function
# with name _tdl_job_xyz(m), will show up under the 'jobs' button in
# the browser, and can be executed from there.  The 'mqs' argument is
# a meqserver proxy object.
# NB: The function _test_forest() is always put at the end of the menu:

def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    trace = True
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    if trace: print '\n** domain =',domain
    cells = meq.cells(domain, num_freq=10, num_time=11)
    if trace: print '\n** cells =',cells
    request = meq.request(cells, rqtype='ev')
    if trace: print '\n** request =',request
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    if trace: print '\n** result =',result,'\n'
    return result


def _tdl_job_incl_zero (mqs, parent):
    """Execute the forest with a domain that includes f=0 and t=0"""
    domain = meq.domain(0,10,0,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result

def _tdl_job_incl_negative (mqs, parent):
    """Execute the forest with a domain that includes f<0 and t<0"""
    domain = meq.domain(-1,10,-10,10)                         # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result


def _tdl_job_sequence(mqs, parent):
   """Execute the forest for a sequence of requests with changing domains"""
   trace = True
   for x in range(10):
       domain = meq.domain(x,x+1,x,x+1)                       # (f1,f2,t1,t2)
       if trace: print '\n** x =',x,': -> domain =',domain
       cells = meq.cells(domain, num_freq=20, num_time=19)
       request = meq.request(cells, rqtype='ev')
       result = mqs.meq('Node.Execute',record(name='result', request=request0))
   return True


# NB: If you execute one after the other without recompiling first,
#     the domain does not change!!



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_XYZ_template.py

if __name__ == '__main__':
   print '\n*******************\n** Local test of: MG_XYZ_template.py :\n'

   ns = NodeScope()


   print '\n** End of local test of: MG_XYZ_template.py \n*******************\n'
       
#********************************************************************************
#********************************************************************************




