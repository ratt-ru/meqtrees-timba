# MG_XYZ_template.py

# Short description:
#   A template for the generation of MG stripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 15 sep 2006: creation

# Copyright: The MeqTree Foundation

# Full description:

# MG scripts should (roughly) have the following parts:
# - PART   I: Organised specific information about this script
# - PART  II: Preamble (import etc) and initialisation
# - PART III: Optional: Importable functions (to be used by other scripts)
# - PART  IV: Required: Test/Demo function _define_forest(), called from the meqbrowser
# - PART   V: Recommended: Forest execution routine(s), called from the meqbrowser
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
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   if True:
       a = ns['a'] << Meq.Time()
       b = ns['b'] << Meq.Freq()

   sum_ab = ns['sum'] << Meq.Add(a,b)

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
    domain = meq.domain(1,10,-10,10)                            # (f1,f2,t1,t2)
    if trace: print '\n** domain =',domain
    cells = meq.cells(domain, num_freq=10, num_time=11)
    if trace: print '\n** cells =',cells
    request = meq.request(cells, rqtype='ev')
    if trace: print '\n** request =',request
    result = mqs.meq('Node.Execute',record(name='sum', request=request), wait=True)
    if trace: print '\n** result =',result,'\n'
    return result






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




