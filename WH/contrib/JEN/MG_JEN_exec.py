script_name = 'MG_JEN_exec.py'

# Short description:
#   Functions used in execution of MeqGraft (MG) scripts

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN import MG_JEN_forest_state as MG_JEN_forest_state



#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Test/demo of importable function:
   bb = []
   bb.append(importable_example (ns, arg1=1, arg2=2))
   bb.append(importable_example (ns, arg1=3, arg2=4))
   cc.append(bundle(ns, bb, 'bundle_1'))

   bb = []
   bb.append(importable_example (ns, arg1=1, arg2=5))
   bb.append(importable_example (ns, arg1=1, arg2=6))
   cc.append(bundle(ns, bb, 'bundle_2'))

   # Finished: 
   return on_exit (ns, cc)            









#================================================================================
# Optional: Importable function(s): To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------
# Example:

def importable_example(ns, qual='auto', **pp):

   # If necessary, make an automatic qualifier:
   qual = MG_JEN_forest_state.autoqual('MG_JEN_exec_example')

   default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
   node = ns << Meq.Parm(default)
   return node



#-------------------------------------------------------------------------------
# Deal with the list (cc) of root nodes:
   
def on_exit (ns, cc, name='_test_root'):
	# Make a (single) root node for use in _test_forest():
	global _test_root
	_test_root = name
	return bundle (ns, cc, name, show_parent=False)

#-----------------------------------------------------------------------------
# Bundle the given nodes by making them children of a new node:

def bundle (ns, cc, name='bundle', show_parent=True):
	if not isinstance(cc, list): cc = [cc]
	if len(cc) == 0:
		parent = ns[name] << -1.23456789
		# Make a page of bookmarks for the parent:
		MG_JEN_forest_state.bookmark(parent, page=name, viewer='Record Browser')

	elif len(cc) == 1:
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

def meqforest (mqs, parent, request=None, **pp):
   pp.setdefault('trace', False)

   # Execute the meqforest with the specified (or default) request:
   request = make_request(request, **pp)
   global _test_root                                         # defined in .on_exit()
   # mqs.meq('Debug.Set.Level',record(debug_level=100));
   # mqs.meq('Node.Set.Breakpoint',record(name='solver:GJones:q=uvp',breakpoint=255));
   mqs.meq('Node.Execute',record(name=_test_root, request=request));

   # Save the meqforest in a file:
   pp.setdefault('save', True)       
   if pp['save']: MG_JEN_forest_state.save(mqs)
   
   return

#---------------------------------------------------------
# Helper function to make sure of a request:

def make_request (request=None, **pp):
   pp.setdefault('trace', False)
   s = '** make_request('+str(type(request))+'):'
   if request==None:
      pp.setdefault('cells', None)
      cells = pp['cells']
      pp.__delitem__('cells')
      cells = make_cells(cells, **pp)
      if True:
         # Simplest, but a bit limited:
         request = meq.request(cells, eval_mode=0);
      else:
         # Better? (make sure that the domain/cell parameters in pp are not in the way)
         pp.setdefault('eval_mode', 0)
         request = meq.request(cells, **pp);
      if pp['trace']: print s,'pp =',pp
   if pp['trace']: print s,'->',request
   return request


#---------------------------------------------------------
# Helper function to make sure of a cells:

def make_cells (cells=None, **pp):
   pp.setdefault('trace', False)
   s = '** make_cells('+str(type(cells))+'):'
   if cells==None:
      pp.setdefault('domain', None)
      pp.setdefault('nfreq', 20)
      pp.setdefault('ntime', 19)
      domain = pp['domain']
      pp.__delitem__('domain')
      domain = make_domain(domain, **pp)
      cells = meq.cells(domain, num_freq=pp['nfreq'], num_time=pp['ntime'])
      if pp['trace']: print s,'pp =',pp
   if pp['trace']: print s,'-> cells =',cells
   return cells

#---------------------------------------------------------
# Helper function to make sure of a domain:

def make_domain (domain=None, **pp):
   pp.setdefault('trace', False)
   s = '** make_domain('+str(type(domain))+'):'
   if domain==None: domain = 'default'
   if isinstance(domain, str):
      s = '** make_domain('+str(domain)+'):'
      if domain=='lofar':
         pp.setdefault('f1', 100e6)
         pp.setdefault('f2', 110e6)
      elif domain=='21cm':
         pp.setdefault('f1', 1300e6)
         pp.setdefault('f2', 1420e6)
      pp.setdefault('f1', 0)
      pp.setdefault('f2', 1)
      pp.setdefault('t1', 0)
      pp.setdefault('t2', 10)
      domain = meq.domain(pp['f1'],pp['f2'],pp['t1'],pp['t2'])
      if pp['trace']: print s,'pp =',pp
   if pp['trace']: print s,'-> domain =',domain
   return domain



#-------------------------------------------------------------------------------- 
# Execute the script without a meqserver:

def without_meqserver(script_name='<script_name>'):
	ns = NodeScope();
	_define_forest(ns);
	ns.Resolve();
        display_nodescope(ns, script_name)
	return 


# Used by .without_meqserver(): 

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
   for key in root.keys(): display_subtree (root[key],'root['+key+']', full=1)
      
   print '**'
   print '** - ns.__doc__ -> ',ns.__doc__
   print '*** End of NodeScope ()\n'
   return

#----------------------------------------------------------------------------------
# Recursively display the subtree underneath a NodeStub object (node):

def display_subtree (node, txt='<txt>', level=0,
                     recurse=1000, count={}, full=0):
   indent = level*'..'
   total = '_total_count'
   klasses = '_classes'
   if level == 0:
      print
      print '** TDL subtree (',txt,') ( recurse =',recurse,'):'
      print level,indent,node,'  ',node.initrec()
      if not full: print '   (use full=1 to display the subtree itself)'
      key = str(node)
      count = {}
      count[key] = 1
      count[total] = 1
      count[klasses] = {}
      count[klasses][node.classname] = 1
      if recurse>0:
         for j in range(len(node.stepchildren)):
            print ' ',indent,'    .stepchildren[',j,']:',node.stepchildren[j][1]
         for i in range(len(node.children)):
            display_subtree (node.children[i], level=level+1,
                             recurse=recurse-1, count=count, full=full)
      print '** some subtree statistics:'
      for klass in count[klasses].keys():
         print '**   class:',klass,':',count[klasses][klass]
      print '** total nr of nodes scanned:',count[total]
      print

   else:
      if full: print level,indent,node[0],':',node[1],
      key = str(node[1])
      if key in count.keys():
         count[key] += 1
         if full: print '      (see above)'
      else:
         count[key] = 1
         count[total] += 1
         klass = node[1].classname
         if not count[klasses].has_key(klass): count[klasses][klass] = 0
         count[klasses][klass] += 1
         rr = node[1].initrec()
         if len(rr.keys()) > 1:
            rr = rr.copy()
            rr.__delitem__('class')
            if full: print '  ',rr,
         if recurse>0:
            if full: print
            for j in range(len(node[1].stepchildren)):
               print ' ',indent,'    .stepchildren[',j,']:',node[1].stepchildren[j][1]
               # display_subtree (node[1].stepchildren[j], level=level+1,
               #                     recurse=recurse-1, count=count, full=full)
            for i in range(len(node[1].children)):
               display_subtree (node[1].children[i], level=level+1,
                                recurse=recurse-1, count=count, full=full)
          
         else:
            if full: print '      (further recursion inhibited)'




#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...
# NB: Inhibited, because this gives an error for this particular script

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return meqforest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   if True:
      # This is the default
      without_meqserver(script_name)
   
   else:
      # Some local tests
      print '\n**',script_name,':\n'
      if 0:
         domain = make_domain(trace=True)
         domain = make_domain('21cm', trace=True)
         domain = make_domain('lofar', trace=True)
         domain = make_domain('lofar', f1=10, trace=True)
         domain = make_domain(domain, trace=True)
         print

      if 0:
         # cells = make_cells(trace=True)
         cells = make_cells(domain='lofar', f1=10, trace=True)
         cells = make_cells(cells, trace=True)
         print

      if 0:
         # request = make_request(trace=True)
         request = make_request(domain='lofar', trace=True)
         request = make_request(request, trace=True)
         print

      print '\n** end of',script_name,'\n'




#********************************************************************************



