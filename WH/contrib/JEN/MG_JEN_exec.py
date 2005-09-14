script_name = 'MG_JEN_exec.py'
last_changed = 'h10sep2005'

# Short description:
#   Functions used in execution of MeqGraft (MG) scripts

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 










#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq              # required in MG_JEN_exec !!

from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_forest_state

#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)












#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
   # Perform some common functions, and return an empty list (cc=[]):
   cc = on_entry (ns, script_name)            

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
   return on_exit (ns, script_name, cc)            











#================================================================================
# Optional: Importable function(s): To be imported into user scripts. 
#================================================================================


#-------------------------------------------------------------------------------
# Function called upon entry of _define_forest()
   
def on_entry (ns, name='<script_name>', **pp):
   # Return an empty list, to be filled with root nodes
   cc = []
   return cc


#-------------------------------------------------------------------------------
# Function called upon exit of _define_forest()
# Deal with the list (cc) of root nodes:
   
def on_exit (ns, name='<script_name>', cc=[], **pp):
   
   pp.setdefault('make_bookmark', True)   # if False, inhibit bookmarks
   
   # Make a (single) root node for use in _test_forest():
   global _test_root
   _test_root = name
   return bundle (ns, cc, name, show_parent=False, **pp)



#-----------------------------------------------------------------------------
# Bundle the given nodes by making them children of a new node:

def bundle (ns, cc, name='bundle', **pp):
   
   pp.setdefault('make_bookmark', True)   # if False, inhibit bookmarks
   pp.setdefault('show_parent', False)    # if True, make bookmark for parent too

   if not isinstance(cc, list): cc = [cc]
   if len(cc) == 0:
      parent = ns[name] << -1.23456789
      if pp['make_bookmark']:
         # Make a page of bookmarks for the parent:
         MG_JEN_forest_state.bookmark(parent, page=name, viewer='Record Browser')

   elif len(cc) == 1:
      parent = ns[name] << Meq.Selector(cc[0])
      if pp['make_bookmark']:
         # Make a page of bookmarks for the parent:
         MG_JEN_forest_state.bookmark(parent, page=name) 
         MG_JEN_forest_state.bookmark(parent, page=name, viewer='Record Browser')

   else:
      # Make a single parent node to tie the various results (cc) together:
      parent = ns[name] << Meq.Add(children=cc)
      if pp['make_bookmark']:
         # Make a bookpage for all the elements of cc:
         for i in range(len(cc)):
            MG_JEN_forest_state.bookmark(cc[i], page=name)
         if pp['show_parent']:
            MG_JEN_forest_state.bookmark(parent, page=name) 
   
   return parent
   

#-------------------------------------------------------------------------------
# Used in _define_forest(), as a simpe example:

def importable_example(ns, qual='auto', **pp):

   # If necessary, make an automatic qualifier:
   qual = MG_JEN_forest_state.autoqual('MG_JEN_exec_example')

   default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
   node = ns << Meq.Parm(default)
   return node






#================================================================================
#================================================================================
#================================================================================
# The function that does the work for _test_forest()
#================================================================================

def meqforest (mqs, parent, request=None, **pp):

   from Timba.Meq import meq

   pp.setdefault('trace', False)
   pp.setdefault('save', True)       

   # Execute the meqforest with the specified (or default) request:
   request = make_request(request, **pp)
   global _test_root                                         # defined in .on_exit()
   # mqs.meq('Debug.Set.Level',record(debug_level=100))
   # mqs.meq('Node.Set.Breakpoint',record(name='solver:GJones:q=uvp',breakpoint=255))

   # Needed for the moment, until OMS has figured out the threading:
   # mqs.meq('Clear.Breakpoints',record(name='solver:GJones:q=uvp',breakpoint=255))

   result = mqs.meq('Node.Execute',record(name=_test_root, request=request), wait=True)
   MG_JEN_forest_state.attach_test_result (mqs, result)

   # Optionally, save the meqforest
   if pp['save']: save_meqforest (mqs, **pp)
   
   return True

#-------------------------------------------------------------------------------
# Save the meqforest in a file (and perhapes a reference file, for auto-testing):

def save_meqforest (mqs, **pp):
   pp.setdefault('trace', False)
   pp.setdefault('save_reference', True)       
   MG_JEN_forest_state.save_meqforest(mqs, reference=pp['save_reference'])
   return True



#---------------------------------------------------------
# Various possible commands (from MeqForest.g)

# r := private.mqsv.meq('Clear.Cache', [name='MeqSolver', recursive=T], wait_reply=T)
#      private.mqsv.meq('Clear.Funklets', wait_reply=T);
#      private.mqsv.meq('Save.Forest', [file_name=tempfile], wait_reply=T);
#      private.mqsv.meq('Clear.Forest', wait_reply=T);
# Remove all funklets of the specified MeqParms:
#      private.mqp.reset(mepname, parmname=parmname, trace=trace);
# Load AFTER resetting the table....?
#      private.mqsv.meq('Load.Forest', [file_name=tempfile], wait_reply=T);
# r := private.mqsv.meq('Set.Forest.State', [state=state], wait_reply=T);
# rr := private.mqsv.meq('Get.Forest.State', [=], wait_reply=T);
# rr := private.mqsv.meq('Node.Get.State', [name=name], wait_reply=T);
# r := private.mqsv.meq('Node.Set.State', [name=name, state=vv], wait_reply=T);
# r := private.mqsv.meq ('Create.Node', cc, wait_reply=T, silent=F);
#      private.mqsv.meq('Debug.Set.Level', [debug_level=100], wait_reply=T);
# result := private.mqsv.meq('Node.Execute', rr, wait_reply=T);
# ii := private.mqsv.meq('Get.Nodeindex', [name=defrec.name], wait_reply=T);
# r := private.mqsv.meq('Resolve', [name=rname], wait_reply=T);
#      private.mqsv.meq := function (command=F, opt=[=], wait_reply=F, silent=F) {
# rr := [command=command, opt=opt, wait_reply=wait_reply, silent=silent];
# else if (command=='Node.Set.BreakPoint') {
# else if (command=='Node.Clear.BreakPoint') {
# else if (command=='Node.Publish.Results') {
# private.mqsv.resolve := function (name=F) {
# private.mqsv.getnodestate := function (name=F) {
# private.mqsv.getnodelist := function (children=T) {
#   return [class="", name="", nodeindex=[], children=[=]];
# private.mqsv.execute := function (name=F, request=F) {



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
      pp.setdefault('t2', 1)
      domain = meq.domain(pp['f1'],pp['f2'],pp['t1'],pp['t2'])
      if pp['trace']: print s,'pp =',pp
   if pp['trace']: print s,'-> domain =',domain
   return domain







#================================================================================
# Execute the script without a meqserver:
#================================================================================

def without_meqserver(script_name='<script_name>', callback=None, **pp):

   pp.setdefault('recurse', 5)
   pp.setdefault('full', True)
   pp = record(pp)

   # Execute the tree definition function:
   ns = NodeScope();
   # _define_forest(ns);
   root = callback(ns)
   ns.Resolve();

   display_forest_state()

   # Display the result at the specified recursion level:
   display_subtree (root, script_name, full=pp['full'], recurse=pp['recurse'])

   # Also display it at some of the lowset recursion levels:
   if False:
      for always in [2,1]:
         if pp['full'] and always<pp['recurse']:
            display_subtree (root, script_name, full=True, recurse=always)

   # display_nodescope (ns, script_name)
   return 


#--------------------------------------------------------------------------------

def display_forest_state():
   rr = Settings.forest_state
   display_object (rr, 'forest_state')
   


#================================================================================
# Some useful display functions:
#================================================================================

#--------------------------------------------------------------------------------

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
   display_object (ns.AllNodes(), 'ns.AllNodes()')
   print '** - ns.AllNodes() : ',type(ns.AllNodes()),'[',len(ns.AllNodes()),']'
   print '** - ns.Repository() : ',type(ns.Repository()),'[',len(ns.Repository()),']'
   print '** - ns.RootNodes() : ',type(ns.RootNodes()),'[',len(ns.RootNodes()),']'
   print '** - ns.RootNodes() -> ',ns.RootNodes()
   display_object (ns.RootNodes(), 'ns.RootNodes()')
   root = ns.RootNodes()
   for key in root.keys(): display_subtree (root[key],'root['+key+']', full=False)
      
   print '**'
   print '** - ns.__doc__ -> ',ns.__doc__
   print '*** End of NodeScope ()\n'
   return



#----------------------------------------------------------------------------------
# Recursively display the subtree underneath a NodeStub object (node):

def display_subtree (node, txt='<txt>', level=0, cindex=0,
                     recurse=1000, count={}, full=0):

   # General:
   indent = level*'..'
   indent1 = (level+1)*'..'
   total = '_total_count'
   klasses = '_classes'
   inhibited = '_inhibited'

   # Start (outer level):
   if level == 0:
      print
      print '** TDL subtree (',txt,') ( recurse =',recurse,'):'
      if not full: print '   (use full=1 to display the subtree itself)'
      count = {}
      count[total] = 1
      count[inhibited] = 0
      count[klasses] = {}
      

   # Display the node:
   if full: print level,indent,cindex,':',node,
   key = str(node)

   if key in count.keys():
      count[key] += 1
      if full: print '      (see above)'

   else:
      count[key] = 1
      count[total] += 1
      klass = node.classname
      if not count[klasses].has_key(klass): count[klasses][klass] = 0
      count[klasses][klass] += 1
      initrec = deepcopy(node.initrec())

      if len(initrec.keys()) > 1:
         hide = ['name','class','defined_at','children','stepchildren','step_children']
         for field in hide:
            if initrec.has_key(field): initrec.__delitem__(field)
         if initrec.has_key('default_funklet'):
            coeff = initrec.default_funklet.coeff
            initrec.default_funklet.coeff = [coeff.shape,coeff.flat]
         if full: print '  ',initrec,

      if not recurse>0:
         if full: print
         inhibit = 0
         for i in range(len(node.children)):
            inhibit += 1
            print ' ',indent,'      .children[',i,']:',node.children[i][1]
         for i in range(len(node.stepchildren)):
            inhibit += 1
            print ' ',indent,'      .stepchildren[',-1-i,']:',node.stepchildren[i][1]
         if inhibit>0:
            print ' ',indent,'      (further recursion inhibited)'
            count[inhibited] += inhibit

      else:
         if full: print
         inhibit = 0

         classname = None
         c5 = None
         for i in range(len(node.stepchildren)):
            stepchild = node.stepchildren[i][1]
            cindex = '('+str(i)+')'
            if stepchild.classname == classname and stepchild.name[0:5]==c5:
               inhibit += 1
               print level+1,indent1,cindex,':',node.stepchildren[i][1],' (similar stepchild, not shown)'
            else:
               classname = stepchild.classname
               c5 = stepchild.name[0:5]
               display_subtree (stepchild, level=level+1, cindex=cindex,
                                recurse=recurse-1, count=count, full=full)
            count[inhibited] += inhibit

         classname = None
         c5 = None
         for i in range(len(node.children)):
            child = node.children[i][1]
            cindex = str(i)
            if child.classname == classname and child.name[0:5]==c5:
               # print child.name,len(child.name),child.name[0:5]
               inhibit += 1
               print level+1,indent1,cindex,':',node.children[i][1],' (similar child, not shown)'
            else:
               classname = child.classname
               c5 = child.name[0:5]
               display_subtree (child, level=level+1, cindex=cindex,
                                recurse=recurse-1, count=count, full=full)
            count[inhibited] += inhibit
          

   # Finished (outer level):
   if level==0:
      print '** Some subtree statistics:'
      for klass in count[klasses].keys():
         print '**   class:',klass,':',count[klasses][klass]
      print '** Total nr of nodes scanned:',count[total]
      print '** Further recursion inhibited for',count[inhibited],'children and/or stepchildren'
      print

   return True


#----------------------------------------------------------------------------------
# Display any Python object(v):

def display_object (v, name='<name>', txt='', full=0, indent=0):
    if indent==0: print '\n** display of Python object:',name,': (',txt,'):'
    print '**',indent*'.',name,':',
    
    if isinstance(v, (str, list, tuple, dict, record)):
        # sizeable types (otherwise, len(v) gives an error):
        vlen = len(v)
        slen = '['+str(vlen)+']'

        if isinstance(v, str):
            print 'str',slen,
            print '=',v
      
        elif isinstance(v, list):
            print 'list',slen,
            separate = False
            types = {}
            for i in range(vlen):
                stype = str(type(v[i]))
                types[stype] = 1
                s1 = stype.split(' ')
                if s1[0] == '<class': separate = True
                if isinstance(v[i], (dict, record)): separate = True
            if len(types) > 1: separate = True

            if separate:
                print ':'
                for i in range(vlen): display_object (v[i], '['+str(i)+']', indent=indent+2)
            elif vlen == 1:
                print '=',[v[0]]
            elif vlen < 5:
                print '=',v
            else:
                print '=',[v[0],'...',v[vlen-1]]

        elif isinstance(v, tuple):
            print 'tuple',slen,
            print '=',v
          
        elif isinstance(v, (dict, record)):
            if isinstance(v, record):
                print 'record',slen,':'
            elif isinstance(v, dict):
                print 'dict',slen,':'
            keys = v.keys()
            n = len(keys)
            types = {}
            for key in keys: types[str(type(v[key]))] = 1
            if len(types) > 1:
                for key in v.keys(): display_object (v[key], key, indent=indent+2)
            elif n < 10:
                for key in v.keys(): display_object (v[key], key, indent=indent+2)
            elif full:
                for key in v.keys(): display_object (v[key], key, indent=indent+2)
            else:
                for key in [keys[0]]: display_object (v[key], key, indent=indent+2)
                if n > 20:
                    print '**',(indent+2)*' ','.... (',n-2,'more fields of the same type )'
                else:
                    print '**',(indent+2)*' ','.... ( skipped keys:',keys[1:n-1],')'
                for key in [keys[n-1]]: display_object (v[key], key, full=full, indent=indent+2) 
        

        else: 
            print type(v),'=',v

    else: 
        # All other types:
        print type(v),'=',v

    if indent == 0: print












#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************



#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return meqforest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n****************\n** Local test of:',script_name,':\n'

   # Generic test:
   without_meqserver(script_name, callback=_define_forest, recurse=3)
   
   # Various local tests:
   if 0:
      domain = make_domain(trace=True)
      domain = make_domain('21cm', trace=True)
      domain = make_domain('lofar', trace=True)
      domain = make_domain('lofar', f1=10, trace=True)
      domain = make_domain(domain, trace=True)
      display_object (domain, 'domain', 'MG_JEN_exec')
      
   if 0:
      # cells = make_cells(trace=True)
      cells = make_cells(domain='lofar', f1=10, trace=True)
      cells = make_cells(cells, trace=True)
      display_object (cells, 'cells', 'MG_JEN_exec')
      
   if 0:
      # request = make_request(trace=True)
      request = make_request(domain='lofar', trace=True)
      request = make_request(request, trace=True)
      display_object (request, 'request', 'MG_JEN_exec')

   print '\n** End of local test of:',script_name,'\n*************\n'


#********************************************************************************



