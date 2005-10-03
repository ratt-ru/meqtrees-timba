# MG_JEN_exec.py

# Short description:
#   Convenience functions used in execution of MeqGraft (MG) scripts

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

# Full description:
#
# This MG script contains convenience functions that are called by all
# MG_JEN_xyz.py scripts. They are not necessary for MG scripts, but they
# keep them small, and easy to upgrade with common services.
# It is a regular MG script in the sense that it has the usual functions
# to define a demonstration forest, and to execute it.
#











#================================================================================
# Preamble
#================================================================================

from Timba.TDL import *
from Timba.Meq import meq              # required in MG_JEN_exec !!

from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                         # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                       # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed

from copy import deepcopy       
import os       

from Timba.Contrib.JEN import MG_JEN_forest_state




#--------------------------------------------------------------------------------
# The following functions belong in the 'importable' section, but they have
# to be defined before they are used in this module:

def MG_init(script_name, **pp):
   """Initialise a MG script control record"""
   MG = record(script_name=script_name, **pp)
   # MG.setdefault('stream_control',record())
   return MG

#-------------------------------------------------------------------------------
# Helper function:

def MG_check(MG):
   """Make sure that MG is a record with some expected fields"""
   if isinstance(MG, str):
      MG = record(script_name=MG)            # deal with legacy code
   if True:
      replace_reference(MG)
   return MG

# Helper function that replaces 'referenced' values with actual ones:

def replace_reference(rr, up=None, level=1):
   """If the value of a field in the given record (rr) is a field name
   in the same record, replace it with the value of the referenced field"""
   if level>10: return False                 # escape from eternal loop (error!)
   count = 0
   prefix = str(level)+':'+(level*'.')
   for key in rr.keys():                     # for all fields
      value = rr[key]                        # field value
      if isinstance(value, dict):            # if field value is dict: recurse
         replace_reference(rr[key], up=rr, level=level+1)
      elif isinstance(value, str):           # if field value is a string
         if value[:3]=='../':                # if upward reference
            if isinstance(up, dict):         # if 'parent' record given      
               upfield = value.split('/')[1] # 
               for upkey in up.keys():       # search for upfield in parent record
                  count += 1                 # count the number of replacements
                  # print prefix,'-',count,'replace_with_upward: rr[',key,'] =',value,'->',up[upkey]
                  if upkey==upfield: rr[key] = up[upkey]  # replace if found
         else:
            if not value==key:                # ignore self-reference
               if rr.has_key(value):          # if field value is the name of another field
                  count += 1                  # count the number of replacements
                  # print prefix,'-',count,': replace_reference(): rr[',key,'] =',value,'->',rr[value]
                  rr[key] = rr[value]         # replace with the value of the referenced field
   if count>0: replace_reference(rr, level=level+1)       # repeat if necessary
   return count



#--------------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_init('MG_JEN_exec.py',
             last_changed='h22sep2005',
             aa='referenced value',
             bb='aa',
             cc='bb',
             trace=False)
MG = MG_check(MG)


#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)












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
   cc = on_entry (ns, MG)
   display_object (MG, 'MG', 'after on_entry()')


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
   return on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


#-------------------------------------------------------------------------------
# Function called upon entry of _define_forest()
   
def on_entry (ns, MG, **pp):
   """Function called upon entry of _define_forest()"""

   # Check the MG-record:
   MG = MG_check(MG)

   # Transfer certain ctrl fields to the MG_JEN_stream_control record:
   if MG.has_key('stream_control'): stream_control (MG.stream_control)

   # Attach the script control field (MG) to the forest state record:
   Settings.forest_state.MG_JEN_script_ctrl = MG
   
   # Return an empty list, to be filled with root nodes
   cc = []
   return cc



#-------------------------------------------------------------------------------
# Function called upon exit of _define_forest()
# Deal with the list (cc) of root nodes:
   
def on_exit (ns, MG, cc=[], **pp):
   """Function called upon exit of _define_forest()"""
   
   pp.setdefault('make_bookmark', True)                # if False, inhibit bookmarks
   pp.setdefault('create_ms_interface_nodes', True)   # see below

   # Optionally, create the standard nodes expected by the MS
   if pp['create_ms_interface_nodes']:
      create_ms_interface_nodes(ns)
   
   # Make a (single) root node for use in _test_forest():
   global _test_root
   _test_root = MG.script_name
   root = bundle (ns, cc, _test_root, show_parent=False, **pp)
   return root



#-----------------------------------------------------------------------------
# Bundle the given nodes by making them children of a new node:

def bundle (ns, cc, name='bundle', **pp):
   """Bundles the given nodes (cc) by making them children of a new node"""
   
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
# Helper function:

def noexec(pp=None, MG=None, help=None):
   """Function that returns a somewhat organised record of the
   specified record (pp) of function input arguments,
   and its associated information (e.g. help)"""

   # Make sure that pp is a record
   if pp==None: pp = record()
   pp = record(pp)

   # Make sure of the help record, and attach it to pp:
   if help==None: help = record()
   help = record(help)
   for key in pp.keys():
      if not help.has_key(key):
         help[key] = '.. no help available for argument: '+key
   pp['_help'] = help

   # Check the MG-record, and attach it to pp:
   MG = MG_check(MG)
   pp['_MG'] = MG

   display_object(pp,'pp', 'MG_JEN_exec.noexec()')
   return pp
   

#-------------------------------------------------------------------------------
# Create a small subtree of nodes that are expected by the function
# that reads information from the MS:

def create_ms_interface_nodes(ns):
   """Create a small subtree of nodes with reserved names, that are expected by
   the function that reads information from the MS"""
   cc = []

   # Field (pointing) centre:
   cc.append(ns.ra0 << 0.0)
   cc.append(ns.dec0 << 1.0)

   # Antenna positions:
   nant = 14
   coords = ('x','y','z')
   for iant in range(nant):
      sn = str(iant+1)
      for (j,label) in enumerate(coords):
         cc.append(ns[label+'.'+sn] << 0.0)

   # Array reference position (x,y,z):
   for (j,label) in enumerate(coords):
      cc.append(ns[label+'0'] << 0.0)

   # Tie them all together by a single root node.
   # This is to avoid clutter of the list of root-nodes in the browser,
   # in the case where they are not connected to the tree for some reason.
   root = ns.ms_interface_nodes << Meq.Add(*cc)

   return root


#-------------------------------------------------------------------------------
# Used in _define_forest(), as a simpe example:

def importable_example(ns=None, **pp):
   """Example importable function"""

   # Deal with input arguments:
   pp.setdefault('arg1', 1)
   pp.setdefault('arg2', 2)
   pp = record(pp)
   # If called without arguments (), an organised pp-record is returned.
   help = dict(arg1='help for arg1')
   if ns==None: return noexec(pp, MG, help=help)

   default = array([[1, pp['arg1']/10],[pp['arg2']/10,0.1]])
   node = ns << Meq.Parm(default)
   return node











#================================================================================
#================================================================================
#================================================================================
# Execute the tree under (MS) stream_control:
#================================================================================

def spigot2sink (mqs, parent, ctrl={}, **pp):
   """Execute the tree under MS stream_control()"""

   from Timba.Meq import meq

   pp.setdefault('wait', False)       
   pp.setdefault('trace', False)
   pp.setdefault('save', True)       

   # Transfer certain ctrl fields to the MG_JEN_stream_control record:
   stream_control (ctrl)

   # Get the stream control record from forest_state record:
   ss = stream_control()
   mqs.init(ss.initrec, inputinit=ss.inputinit, outputinit=ss.outputinit)

   # Optionally, save the meqforest
   # NB: If save=True, the meqforest is saved to a file for EVERY tile....!!
   #     This might be connected to the wait=False policy....
   if pp['save']: MG_JEN_forest_state.save_meqforest(mqs, **pp)
   
   return True


#-------------------------------------------------------------------------
# Access to MG_JEN_stream_control record (kept in the forest state record):

def stream_control (ctrl=None, display=False, init=False):
   """Access to the MG_JEN_stream_control record in the forest_state record
   If init==True, initialise it with default settings."""

   field = 'MG_JEN_stream_control'     # field name in forest state record

   if init:
      ss = record(initrec=record(), inputinit=record(), outputinit=record())

      ss.inputinit.sink_type = 'ms_in';
      ss.inputinit.data_column_name = 'DATA';
      ss.inputinit.tile_size = 1;
      if True:
         # path = os.environ['HOME']+'/LOFAR/Timba/WH/contrib/JEN/'
         path = os.environ['HOME']+'/LOFAR/Timba/PyApps/src/Trees/'
         ss.inputinit.python_init = path+'read_MS_auxinfo.py'
         # ss.inputinit.python_init = path+'read_msvis_header.py'
      
      ss.inputinit.selection = record();
      ss.inputinit.selection.channel_start_index = 0;
      ss.inputinit.selection.channel_end_index = -1;
      
      ss.outputinit.sink_type = 'ms_out';
      ss.outputinit.predict_column_name = 'PREDICT';
      ss.outputinit.residuals_column_name = 'RESIDUALS';
      
      ss.initrec.output_col = 'RESIDUALS'
   
      Settings.forest_state[field] = ss


   # Modify the MG_JEN_stream_control record, if required:
   if not ctrl==None:
      ss = Settings.forest_state[field]
      for key in ['ms_name','data_column_name','tile_size']:
         if ctrl.has_key(key): ss.inputinit[key] = ctrl[key]
      for key in ['channel_start_index','channel_end_index']:
         if ctrl.has_key(key): ss.inputinit.selection[key] = ctrl[key]
      for key in []:
         if ctrl.has_key(key): ss.outputinit[key] = ctrl[key]
      for key in ['output_col']:
         if ctrl.has_key(key): ss.initrec[key] = ctrl[key]
      Settings.forest_state[field] = ss


   if display:
      ss = Settings.forest_state[field]
      display_object(ss, field)
   return Settings.forest_state[field]

stream_control(init=True)





#================================================================================
#================================================================================
#================================================================================
# The function that does the work for _test_forest()
#================================================================================

def meqforest (mqs, parent, request=None, **pp):
   """Obsolete name for .execute()"""
   return execute (mqs, parent, request, **pp)


def execute (mqs, parent, request=None, **pp):
   """The function that does the actual work for the _test_forest()
   functions in the various MG_JEN_ scripts."""

   display_object (MG, 'MG', 'inside .execute()')

   from Timba.Meq import meq

   pp.setdefault('trace', False)
   pp.setdefault('save', True)       
   pp.setdefault('wait', True)       

   # Execute the meqforest with the specified (or default) request:
   request = make_request(request, **pp)
   global _test_root                                         # defined in .on_exit()
   # mqs.meq('Debug.Set.Level',record(debug_level=100))
   # mqs.meq('Node.Set.Breakpoint',record(name='solver:GJones:q=uvp',breakpoint=255))

   # Needed for the moment, until OMS has figured out the threading:
   # mqs.meq('Clear.Breakpoints',record(name='solver:GJones:q=uvp',breakpoint=255))

   result = mqs.meq('Node.Execute',record(name=_test_root, request=request), wait=pp['wait'])
   MG_JEN_forest_state.attach_test_result (mqs, result)

   # Optionally, save the meqforest
   if pp['save']: MG_JEN_forest_state.save_meqforest(mqs, **pp)
   
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






	# NB: output_col tells the server what output columns to initialize 
	#     in the TILES(!). This should match the output column of the Sink.
	# The 'output' record configures the MS output agent. The three optional
	# fields are:
	#  - data_column:
	#  - predict_column:
	#  - residuals_column:
	# The presence of one of these fields will cause the corresponding tile
	# column to be mapped to the named MS column (e.g. 'DATA' or 'MODEL_DATA').
	# New columns can be inserted, but this does not yet work (16 dec)

	# Similarly, reading an MS is done by means of an input record:
	# inputrec := [ms_name='test.ms', data_column_name='DATA', tile_size=10, selection=[=]];
	#   - The data_column_name maps an MS column to the DATA column of the tile.
	#   - tile_size determines the tile size, and therefore the domain size,
	#     in # timeslots
        #   - selection can be used to apply a selection to the MS. It can contain
	#     the following fields:
	#     - channel_start_index: first channel (1-based) 
	#     - channel_end_index:   last channel (1-based)
	#     - ddid_index:          DATA_DESCRIPTION_ID (default=1)
	#     - field_index:         FIELD_ID (default=1)
	#     - selection_string:    any TAQL string
	# mqsv.init (initrec=F, input=inputrec, ouput=F, 
	#            update_gui=T, set_default=F, priority=5);


# initrec.python_init = 'read_msvis_header.py'





#---------------------------------------------------------
# Helper function to make sure of a request:

def make_request (request=None, **pp):
   """Helper function to make sure of a request"""
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
   """Helper function to make sure of a cells"""
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
   """Helper function to make sure of a domain"""
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

def without_meqserver(MG=None, callback=None, **pp):
   """Execute the MG script without a meqserver"""
   # Check the MG-record:
   MG = MG_check(MG)

   pp.setdefault('recurse', 5)
   pp.setdefault('full', True)
   pp = record(pp)

   # Execute the tree definition function:
   ns = NodeScope();
   # _define_forest(ns);
   root = callback(ns)
   ns.Resolve();

   display_object (MG, 'MG', 'after callback(_define_forest())')

   display_forest_state()

   # Display the result at the specified recursion level:
   display_subtree (root, MG.script_name, full=pp['full'], recurse=pp['recurse'])

   # Also display it at some of the lowset recursion levels:
   if False:
      for always in [2,1]:
         if pp['full'] and always<pp['recurse']:
            display_subtree (root, MG.script_name, full=True, recurse=always)

   # display_nodescope (ns, MG.script_name)
   return 


#--------------------------------------------------------------------------------

def display_forest_state():
   """Display the current forest state record"""
   rr = Settings.forest_state
   display_object (rr, 'forest_state')
   


#================================================================================
# Some useful display functions:
#================================================================================

#--------------------------------------------------------------------------------

def display_nodescope (ns, txt='<txt>', trace=1):
   """Display the given nodescope in an organised way"""
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
   """Recursively display the subtree starting at the given node"""

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
    """Display the given Python object"""
   
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



# display_object (MG, 'MG', 'intial')









#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
   """Standard tree execution routine"""
   return meqforest (mqs, parent)



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_JEN_template.py


if __name__ == '__main__':
   print '\n****************\n** Local test of:',MG.script_name,':\n'

   # Generic test:
   if 1:
      without_meqserver(MG, callback=_define_forest, recurse=3)
   
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

   if 0:
      pp = importable_example()

   if 0:
      MG.ms_name = '...DD....MS'
      MG.channel_start_index = -111
      MG.output_col = '<initrec>'
      MG.predict_column_name = 'PREDICT'
      stream_control(MG, display=True)

   if 0:
      rr = record(aa='bb', bb=6, ee='cc', cc='aa', dd='cc')
      display_object (rr, 'rr', 'before')
      replace_reference(rr)
      display_object (rr, 'rr', 'after')
      
   if 1:
      display_forest_state()
   print '\n** End of local test of:',MG.script_name,'\n*************\n'

#********************************************************************************



