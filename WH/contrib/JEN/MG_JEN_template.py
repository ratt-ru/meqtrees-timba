# script_name = 'MG_JEN_template.py'

# Short description (see also the full description below):
#   A template for the generation of MeqGraft (MG) scripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation

# Full description (try to be complete, and up-to-date!):

# MG (from MeqGraft) scripts (modules, really) are multi-purpose
# MeqTree building blocks.  Their importable functions may be
# 'grafted' onto user scripts.  Obviously, these functions may be
# imported into any Python script, but if the latter are MG scripts
# themselves they may be called (and edited) from the meqbrowser.
# Since this has huge advantages (as you will soon appreciate), it is
# recommended that all MeqTree scripts take the form of MG scripts.
# This includes advanced, and perhaps quite specific, data reduction
# scripts. In this way, the MG mechanism will bring the old dream of
# code reuse, and the sharing of ideas, finally a little closer....

# MG scripts should (roughly) have the following parts:
# - PART   I: Organised specific information about this script
# - PART  II: Preamble (import etc) and initialisation
# - PART III: Required: Test/Demo function _define_forest(), called from the meqbrowser
# - PART  IV: Optional: Importable functions (to be used by other scripts)
# - PART   V: Recommended: Forest execution routine(s), called from the meqbrowser
# - PART  VI: Recommended: Standalone test routines (no meqbrowser or meqserver)

# This template is a regular MG script, which may be executed from the
# browser (to see how things work).  It is hoped that it will lead to
# a large collection of user-contributed scripts, which are readily
# accessible to all via the MeqTree 'Water Hole'.  Our role-models
# are modern successes like Matlab, Python and Linux.

# This template is a convenient starting point, which provides some
# convenient services (in MG_JEN_exec.py and MG_JEN_forest_state.py).
# But it would be disappointing if no competing templates would
# emerge. In any case, the user is actively encouraged to browse the
# entire collection of available MG_XYZ scripts for useful functions.
# The script naming convention (MG_XYZ_...) and the directory structure
# is used to

# How to use this template:
# - Copy it to a script file with a name like this:
#      MG_<authorinitials>_<function>.py
# - Put it into your Water Hole directory:
#      /Timba/WH/contrib/<author initials>/
# - Fill in the correct script_name (and other info) at the top of part II
# - Fill in the author and the short (one-line) description
# - Replace the full description with a specific one
# - Replace the example importable function with specific ones
# - Make the specific _define_forest() function. Try to make this
#   a complete test and demonstration of all its importable functions.
# - Write lots of explanatory comments throughout
# - Test everything thoroughly, without and with the browser.
# - Make it known to your MG_XYZ_testall.py script (see MG_JEN_testall.py)
# - Check it in via CVS

# Of course, it is also possible, and often preferrable to just copy a
# working script from someone else, and cannibalise it.

   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

script_name = 'MG_JEN_template.py'
last_changed = 'h10sep2005'

from Timba.TDL import *
# from Timba.Meq import meq

from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                         # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                       # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed

from numarray import *
# from string import *
# from copy import deepcopy

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

# Other MG_JEN scripts (uncomment as necessary):
# NB: Also browse the list of other available scripts!

# from Timba.Trees import TDL_Cohset
# from Timba.Trees import TDL_Joneset
# from Timba.Trees import TDL_Sixpack

# from Timba.Contrib.JEN import MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_funklet
# from Timba.Contrib.JEN import MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_math
# from Timba.Contrib.JEN import MG_JEN_matrix

# from Timba.Contrib.JEN import MG_JEN_dataCollect
# from Timba.Contrib.JEN import MG_JEN_historyCollect

# from Timba.Contrib.JEN import MG_JEN_flagger
# from Timba.Contrib.JEN import MG_JEN_solver

# from Timba.Contrib.JEN import MG_JEN_Sixpack
# from Timba.Contrib.JEN import MG_JEN_Joneset
# from Timba.Contrib.JEN import MG_JEN_Cohset



#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...
# See MG_JEN_forest_state.py

MG_JEN_forest_state.init(script_name)






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, script_name)

   # Test/demo of importable function: .example1()
   bb = []
   bb.append(example1 (ns, arg1=1, arg2=2))
   bb.append(example1 (ns, arg1=-1, arg2=4))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.example1()'))

   # Test/demo of importable function: .example2()
   bb = []
   bb.append(example2 (ns, arg1=1, arg2=5))
   bb.append(example2 (ns, arg1=1, arg2=6))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.example2()'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)


# NB: See MG_JEN_exec.py to see which services its functions provide
# exactly.  In general, _define_forest() should define a number of
# carefully designed 'experiments' in the form of subtrees. Their root
# nodes are appended to the list cc. Groups of experiments may be
# bundled The function .on_ext() ties the nodes in cc together by
# making them the children of a single root node, with the specified
# name (default is <script_name>). The latter is executed by the
# function _test_forest() and its relatives (see below).

# Groups of experiments may be bundled with the .bundle() function in
# exactly the same way (indeed, .on_exit() uses .bundle()). The bundle
# names, which should be unique, are used to generate bookmarks for the
# inspection of the bundle results. This is highly convenient.








#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************

# Functions that may be imported into user scripts (very important!!).
# This MG script should be used to test them thoroughly.


#-------------------------------------------------------------------------------
# Example:

def example1(ns, qual=None, **pp):

    pp.setdefault('arg1', 1)
    pp.setdefault('arg2', 2)
    pp = record(pp)

    # If necessary, make an automatic qualifier (unique number):
    qual = MG_JEN_forest_state.autoqual('MG_JEN_template_example1')

    default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
    node = ns.dummy(qual) << Meq.Parm(default)
    return node

def example2(ns, qual=None, **pp):

    pp.setdefault('arg1', 1)
    pp.setdefault('arg2', 2)
    pp = record(pp)

    default = array([[1, pp['arg1']/100],[pp['arg2']/100,0.1]])
    node = ns.dummy << Meq.Parm(default)
    return node







#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

# The function with the standard name _test_forest(), and any function
# with name _tdl_job_xyz(m), will show up under the 'jobs' button in
# the browser, and can be executed from there.  The 'mqs' argument is
# a meqserver proxy object.

# In the default function, the forest is executed once:
# If not explicitly supplied, a default request will be used:

def _tdl_job_default (mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent)

# NB: The function _test_forest() is always put at the end of the menu:

def _test_forest (mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent)

# The following call shows the default settings explicity:
# NB: It is also possible to give an explicit request, cells or domain
#     In addition, qualifying keywords will be used when sensible

def _tdl_job_custom(mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                                 f1=0, f2=1, t1=0, t2=1, trace=False) 

# There are some predefined domains:

def _tdl_job_lofar(mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')   # (100-110 MHz)

def _tdl_job_21cm(mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')    # (1350-1420 MHz)

# Special version for (MS-controlled) stream control:

def _tdl_job_spigot2sink(mqs, parent):
    return MG_JEN_exec.spigot2sink (mqs, parent)

# Execute the forest for a sequence of requests:

def _tdl_job_sequence(mqs, parent):
    for x in range(100):
        MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                               f1=x, f2=x+1, t1=x, t2=x+1,
                               save=False, trace=False, wait=False)
    MG_JEN_exec.save_meqforest(mqs) 
    return True


# NB: One may determine the order of these functions in the menu
#     by means of the following list. If empty, the menu will be empty.
# _tdl_job_list = []





#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_JEN_template.py

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',script_name,':\n'

   # Generic test:
   if 1:
       MG_JEN_exec.without_meqserver(script_name, callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 0:
      rr = 0
      # ............
      # MG_JEN_exec.display_object (rr, 'rr', script_name)
      # MG_JEN_exec.display_subtree (rr, script_name, full=1)

   print '\n** End of local test of:',script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




