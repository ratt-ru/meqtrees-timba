script_name = 'MG_JEN_template.py'

# Short description:
# Template for the generation of MeqGraft scripts

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# How to use this template:
# - Copy it to a suitably named script file (e.g. MG_JEN_xyz.py)
# - Fill in the correct script_name at the top
# - Fill in the author and the short description
# - Enable the MG_JEN_template. calls in the required functions
# - Replace the importable functions with specific ones
# - Make the specific _define_forest() function
# - Remove this 'how to' recipe

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

import MG_JEN_template 
import MG_JEN_forest_state
# import MG_JEN_util

# import MG_JEN_twig
# import MG_JEN_math

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

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Test/demo of importable function:
   bb = []
   bb.append(importable_example (ns, arg1=1, arg2=2))
   bb.append(importable_example (ns, arg1=3, arg2=4))
   cc.append(bundle(ns, bb, 'bundle_1'))
   # cc.append(MG_JEN_template.bundle(ns, bb, 'bundle_1')

   bb = []
   bb.append(importable_example (ns, arg1=1, arg2=5))
   bb.append(importable_example (ns, arg1=1, arg2=6))
   cc.append(bundle(ns, bb, 'bundle_2'))
   # cc.append(MG_JEN_template.bundle(ns, bb, 'bundle_2')

   # Finished: 
   return on_exit (ns, cc)            
   # return MG_JEN_template.on_exit (ns, cc)



#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return execute_forest (mqs, parent)
   # return MG_JEN_template.execute_forest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   execute_without_mqs(script_name)
   # MG_JEN_template.execute_without_mqs(script_name)









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------
# Example:

global_counter = 0                              # used for automatic qualifier

def importable_example(ns, qual='auto', **pp):

	# If necessary, make an automatic qualifier:
	if isinstance(qual, str) and qual=='auto':
		global global_counter
		global_counter += 1
		qual = str(global_counter)

	default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
	node = ns.dummy(qual) << Meq.Parm(default)
	return node



#-------------------------------------------------------------------------------
# Deal with the list (cc) of root nodes:
# NB: This function may be imported from MG_JEN_template.py by other functions
# NB: Remove this function when turning this template into a new MG script
   
def on_exit (ns, cc, name='_test_root'):
	# Make a (single) root node for use in _test_forest():
	global _test_root
	_test_root = name
	return bundle (ns, cc, name, show_parent=False)

#-----------------------------------------------------------------------------
# Bundle the given nodes by making them children of a new node:

def bundle (ns, cc, name='bundle', show_parent=True):
	if not isinstance(cc, list): cc = [cc]
	if len(cc) == 1:
		parent = ns[name] << Meq.Selector(cc[0])
		# Make a page of bookmarks for the parent:
		MG_JEN_forest_state.bookmark(parent, page=name) 
		MG_JEN_forest_state.bookmark(parent, page=name, viewer='Record Browser')

	else:
		# Make a single parent node to tie the various results (cc) together:
		parent = ns[name] << Meq.Add(children=cc)

                # Make a bookpage for all the elements of cc:
                for i in range(len(cc)):
                   MG_JEN_forest_state.bookmark(cc[i], page=name)
                if show_parent:
                   MG_JEN_forest_state.bookmark(parent, page=name) 
   
	return parent
   

#-------------------------------------------------------------------------------- 
# The function that does the work for _test_forest()
# NB: This function may be imported from MG_JEN_template.py by other functions
# NB: Remove this function when turning this template into a new MG script

def execute_forest (mqs, parent, nfreq=20, ntime=19):

	# Execute the forest with a 'suitable' request:
	cells = meq.cells(meq.domain(0,1,0,1), num_freq=nfreq, num_time=ntime);
	request = meq.request(cells,eval_mode=0);
	global _test_root                                         # see on_exit()
	mqs.meq('Node.Execute',record(name=_test_root, request=request));

	# Save the meqforest in a file:
	MG_JEN_forest_state.save(mqs)

	return


#-------------------------------------------------------------------------------- 
# NB: This function may be imported from MG_JEN_template.py by other functions
# NB: Remove this function when turning this template into a new MG script

def execute_without_mqs(script_name='<script_name>'):
	ns = NodeScope();
	_define_forest(ns);
	ns.Resolve();
        display_nodescope(ns, script_name)
	return 

# Used by .execute_without_mqs(): 

def display_nodescope (ns, txt='<txt>', trace=1):
   print '\n*** display of NodeScope (',txt,'):'
   print '** - ns.__class__ -> ',ns.__class__
   print '** - ns.__repr__ -> ',ns.__repr__
   # print '** - ns.__init__() -> ',ns.__init__()              # don't !!
   print '** - ns.__str__ -> ',ns.__str__
   print '** - ns.__new__ -> ',ns.__new__
   print '** - ns.__hash__ -> ',ns.__hash__
   # print '** - ns.__reduce__() -> ',ns.__reduce__()
   # print '** - ns.__reduce_ex__() -> ',ns.__reduce_ex__()
   print '** - ns._name -> ',ns._name
   print '** - ns.name -> ',ns.name
   print '** - ns._constants -> ',ns._constants
   print '** - ns._roots -> ',ns._roots
   print '** - ns.ROOT -> ',ns.ROOT
   print '** - ns.__weakref__ -> ',ns.__weakref__
   print '** - ns.__dict__ -> ',type(ns.__dict__),'[',len(ns.__dict__),']'
   print '** - ns.__contains__ -> ',ns.__contains__
   print '** - ns.GetErrors() -> ',ns.GetErrors()
   # print '** - ns.MakeConstant(1) -> ',ns.MakeConstant(1)
   print '** - ns.MakeUniqueName -> ',ns.MakeUniqueName
   print '** - ns._uniqueName_counters -> ',ns._uniqueName_counters
   print '** - ns.SubScope() -> ',ns.SubScope()
   print '** - ns.Subscope -> ',ns.Subscope                   # takes 2 arguments
   print '** - ns.Resolve() -> ',ns.Resolve()
   print '**'
   print '** - dir(ns) -> ',dir(ns)
   
   print '**'
   # JEN_display (ns.AllNodes(),'ns.AllNodes()', full=1)
   print '** - ns.AllNodes() : ',type(ns.AllNodes()),'[',len(ns.AllNodes()),']'
   print '** - ns.Repository() : ',type(ns.Repository()),'[',len(ns.Repository()),']'
   print '** - ns.RootNodes() : ',type(ns.RootNodes()),'[',len(ns.RootNodes()),']'
   print '** - ns.RootNodes() -> ',ns.RootNodes()
   # JEN_display (ns.RootNodes(),'ns.RootNodes()', full=1)
   root = ns.RootNodes()
   # for key in root.keys(): JEN_display_subtree (root[key],'root['+key+']', full=1)
      
   print '**'
   print '** - ns.__doc__ -> ',ns.__doc__
   print '*** End of NodeScope ()\n'
   return

#********************************************************************************




