script_name = 'MG_JEN_solve_ab.py'

# Short description:
#   Simplest possible demo of a solver


# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 23 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec as MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state as MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_util as MG_JEN_util
# from Timba.Contrib.JEN import MG_JEN_twig as MG_JEN_twig
# from Timba.Contrib.JEN import MG_JEN_math as MG_JEN_math
# from Timba.Contrib.JEN import MG_JEN_funklet as MG_JEN_funklet



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
	return MG_JEN_exec.on_exit (ns, solver)



#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
	return MG_JEN_exec.meqforest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
	MG_JEN_exec.without_meqserver(script_name)






#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================


#********************************************************************************




