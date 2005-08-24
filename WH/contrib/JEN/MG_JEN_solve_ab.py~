script_name = 'MG_JEN_solve_ab.py'

# Short description:
#   Simplest possible demo of a solver


# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 23 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# How to use this template:
# - Copy it to a suitably named script file (e.g. MG_JEN_xyz.py)
# - Fill in the correct script_name at the top
# - Fill in the author and the short description
# - Enable the MG_JEN_template. calls in the required functions
# - Replace the importable functions with specific ones
# - Make the specific _define_forest() function


#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

import MG_JEN_template 
import MG_JEN_forest_state

# import MG_JEN_twig
# import MG_JEN_autoper

from numarray import *
# from string import *
# from copy import deepcopy



#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

	# Parameters:
	dflt_a = 1
	dflt_b = -1
	dflt_a = array([1,.3])
	dflt_b = array([-1,-.3])
	dflt_a = array([[1,.3,.1],[.1,.2,.3]])
	dflt_b = array([[-1,-.3,.1],[.1,.2,-.3]])

	# Make a solver with a single condeq, with children a and b:
	a = ns.a << Meq.Parm(dflt_a, node_groups='Parm')
	b = ns.b << Meq.Parm(dflt_b, node_groups='Parm')
	condeq = ns << Meq.Condeq(a,b)
	solver = ns << Meq.Solver(condeq, solvable=[a], num_iter=10, debug_level=10)

	# Make a page of bookmarks for easy viewing:
	page_name = 'solver'
	MG_JEN_forest_state.bookmark(a, page=page_name)
	MG_JEN_forest_state.bookmark(b, page=page_name)
	MG_JEN_forest_state.bookmark(solver, page=page_name)
	MG_JEN_forest_state.bookmark(condeq, page=page_name)
	MG_JEN_forest_state.bookmark(solver, page=page_name, viewer='ParmFiddler')

	# Finished: 
	return MG_JEN_template.on_exit (ns, solver)



#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
	return MG_JEN_template.execute_forest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
	MG_JEN_template.execute_without_mqs()






#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================


#********************************************************************************




