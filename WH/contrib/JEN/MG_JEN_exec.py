# MG_JEN_exec.py

# Short description:
#   Convenience functions used in execution of MeqGraft (MG) scripts

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 10 dec 2005: introduced JEN_inarg.py for MG record
# - 03 jan 2006: selection_string etc
# - 05 jan 2006: made stream_control inarg-compatible
# - 16 jan 2006: added inarg_stream_control()
# - 03 feb 2006: added fullDomainMux()
# - 21 mar 2006: -> JEN_bookmarks.py
# - 21 mar 2006: -> JEN_object.py and TDL_display.py
# - 15 apr 2006: added cache_policy etc to stream_control
# - 05 oct 2006: implemented 'increment' option in .execute()

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
from Timba.Meq import meq                     # required in MG_JEN_exec !!
from Timba.Meq import meqds

# The following bit still requires a bit of thought.....
from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                         # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                       # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed


from copy import deepcopy       
import os       

from Timba.Contrib.JEN.util import JEN_inarg 
from Timba.Contrib.JEN.util import JEN_bookmarks 
from Timba.Contrib.JEN.util import TDL_display 
from Timba.Contrib.JEN.util import JEN_record 
from Timba.Contrib.JEN import MG_JEN_forest_state




#--------------------------------------------------------------------------------
# The following functions belong in the 'importable' section, but they have
# to be defined before they are used in this module:

def MG_init(script_name, **pp):
   """Initialise a MG script control record"""
   MG = record(script_name=script_name, **pp)
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
# NB: This function is largely replaced with JEN_inarg._replace_reference()....

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
                  # print prefix,'-',count,': MG_JEN_exec::replace_reference(): rr[',key,'] =',value,'->',rr[value]
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

entry_counter = 0

def on_entry (ns, MG, **pp):
   """Function called upon entry of _define_forest()"""

   pp.setdefault('create_ms_interface_nodes', False)   # see below

   global entry_counter
   entry_counter += 1

   # Check the MG-record:
   # display_object (MG, name='MG', txt='.on_entry(): before MG_check()', full=True)
   MG = MG_check(MG)
   # display_object (MG, name='MG', txt='.on_entry(): after MG_check()', full=True)

   # Now make sure (recursively) that MG is a TDL record:
   # Do this AFTER MG_check, because the latter may modify MG (replace_reference())
   # Until everything has settled down....
   MG_record = JEN_inarg.TDL_record(MG)

   # Transfer certain ctrl fields to the MG_JEN_stream_control record:
   if MG_record.has_key('stream_control'):
      stream_control (MG_record.stream_control)

   # Attach the script control field (MG) to the forest state record:
   Settings.forest_state.MG_JEN_script_ctrl = MG_record

   # Optionally, create the standard nodes expected by the MS
   # They are attached to the forest_state record, to be used by
   # other subtree-generating functions like MG_JEN_Joneset.KJones()
   if pp['create_ms_interface_nodes']:
      if entry_counter==1:
         # MG_JEN_forest_state.MS_interface_nodes(ns)
         pass
   
   # Return an empty list, to be filled with root nodes
   cc = []
   return cc



#-------------------------------------------------------------------------------
# Function called upon exit of _define_forest()
# Deal with the list (cc) of root nodes:

exit_counter = 0
   
def on_exit (ns, MG, cc=[], stepchildren=[], **pp):
   """Function called upon exit of _define_forest()"""

   global exit_counter
   exit_counter += 1

   # First make sure (recursively) that MG is a TDL record: 
   MG_record = JEN_inarg.TDL_record(MG)

   pp.setdefault('make_bookmark', True)                # if False, inhibit bookmarks

   # Make a (single) root node for use in _test_forest():
   global _test_root
   _test_root = MG_record.script_name
   if exit_counter>1:
      _test_root += '_'+str(exit_counter)

   # Make a page of bookmarks
   if True or exit_counter==1:
      pass

   root = bundle (ns, cc, _test_root, stepchildren=stepchildren,
                  show_parent=False, **pp)
   return root


#===============================================================================
# Bundle the given nodes by making them children of a new node:

def bundle (ns, cc, name='bundle', folder=None, stepchildren=[], **pp):
   """Bundles the given nodes (cc) by making them children of a new node"""
   
   pp.setdefault('make_bookmark', True)   # if False, inhibit bookmarks
   pp.setdefault('show_parent', False)    # if True, make bookmark for parent too

   if not isinstance(cc, list): cc = [cc]
   if len(cc) == 0:
      parent = ns[name] << Meq.Selector(-1.23456789)

      if pp['make_bookmark']:
         # Make a page of bookmarks for the parent:
         JEN_bookmarks.create(parent, page=name, folder=folder,
                              viewer='Record Browser')

   elif len(cc) == 1:
      parent = ns[name] << Meq.Selector(cc[0])
         
      if pp['make_bookmark']:
         # Make a page of bookmarks for the parent:
         JEN_bookmarks.create(parent, page=name, folder=folder) 
         JEN_bookmarks.create(parent, page=name, folder=folder,
                              viewer='Record Browser')

   else:
      # Make a single parent node to tie the various results (cc) together:
      parent = ns[name] << Meq.Composer(children=cc)
         
      if pp['make_bookmark']:
         # Make a bookpage for all the elements of cc:
         for i in range(len(cc)):
            JEN_bookmarks.create(cc[i], page=name, folder=folder)
         if pp['show_parent']:
            JEN_bookmarks.create(parent, page=name, folder=folder) 

   # If any stepchildren are specified, attach them to the parent node:
   if len(stepchildren)>0: ns[name].add_stepchildren(*stepchildren)
   return parent
   

#-------------------------------------------------------------------------------
# OMS: I have added add_children(...) and add_stepchildren(...) methods to the 
# NodeStub class. Their usage is pretty much intuitive, but you can also 
# see PyApps/test/tdl_tutorial.py for an example (search for 'add_child').


#===============================================================================
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

   # display_object(pp,'pp', 'MG_JEN_exec.noexec()')
   return pp
   




#===============================================================================
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
# Execute the tree under (MS) stream_control:
#================================================================================

def fullDomainMux (mqs, parent, ctrl=None, parmlist=None):
   """Execute the fullDomainMux with a large domain"""

   from Timba.Meq import meq

   # NB: The above will be replaced by a function that allows changing the state of
   # all MeqParm nodes (e.g. to set reset_funklet=False), without the kludge of sending
   # a request with a rider up the tree (does OMS agree with this?)

   if isinstance(parmlist, list):
      for parm in parmlist:
         meqds.set_node_state(parm, reset_funklet=False, solvable=False)

   # This opens the possibility to have a range of TDL_job functions that allow operations
   # on the tree, without having to rebuild the tree....! This requires access to the
   # nodescope, and the various Cohset/ParmSet/LeafSet objects.......

   # Make a minimum request:
   ss = stream_control (_inarg=ctrl, mqs=mqs)
   ss.inputrec.tile_size = 1000
   req = meq.request()
   req.input = record(ms=ss.inputrec)

   # NB: The name of the node is defined in TDL_Cohset.sinks():
   mqs.clearcache('Cohset_fullDomainMux')
   mqs.execute('Cohset_fullDomainMux', req, wait=False)
   return True


#----------------------------------------------------------------------------

def spigot2sink (mqs, parent, ctrl=None, **pp):
   """Execute the tree under MS stream_control()"""

   from Timba.Meq import meq

   pp.setdefault('wait', False)       
   pp.setdefault('trace', False)
   pp.setdefault('save', False)       

   ss = stream_control (_inarg=ctrl, mqs=mqs)
   path = os.environ['HOME']+'/LOFAR/Timba/PyApps/src/Trees/'
   python_init = path+'read_MS_auxinfo.py'
   
   req = meq.request()
   req.input = record(ms=ss.inputrec, python_init=python_init)
   req.output = record(ms=ss.outputrec)

   # See also bug 404: Add a "dataset" dependency to VisDataMux....
   # Make sure that part of the request ID is incremented in test_forest.
   # Otherwise, the VisDataMux node can only be properly executed once, since aftewards it
   # persists in returning a result from the cache.....

   # NB: The name of the node is defined in TDL_Cohset.sinks():
   # mqs.execute('VisDataMux', req, wait=False)
   mqs.execute('Cohset_VisDataMux', req, wait=False)

   # Optionally, save the meqforest
   # NB: If save=True, the meqforest is saved to a file for EVERY tile....!!
   #     This might be connected to the wait=False policy....
   if pp['save']:
      MG_JEN_forest_state.save_meqforest(mqs, **pp)
   
   return True


#-------------------------------------------------------------------------
# Default stream control input arguments (see e.g. MG_JEN_Cohset.py)


#--------------------------------------------------------------------------

def inarg_ms_name (inarg, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (inarg, 'ms_name', 'D1.MS', slave=kwargs['slave'], 
                      choice=['D1.MS'], browse='*.MS',
                      help='name of the (AIPS++) Measurement Set')
    return False

#--------------------------------------------------------------------------

def inarg_tile_size (inarg, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define (inarg, 'tile_size', 10, slave=kwargs['slave'],
                      choice=[1,2,3,5,10,20,50,100],
                      help='(inputrec) size (in time-slots) of the input data-tile')
    return False


#--------------------------------------------------------------------------

def inarg_selection (inarg, **kwargs):
   JEN_inarg.inarg_common(kwargs)
   # Temporarily disabled (empty string ' ' does not play well with inargGui...)
   JEN_inarg.define (inarg, 'selection_string', ' ',
                     choice=['TIME_CENTROID<4615466159.46'],
                     help='(inputrec.sel) TaQL (AIPS++ Table Query Language) data-selection')
   return False


#-------------------------------------------------------------------------
# Access to MG_JEN_stream_control record (kept in the forest state record):


def stream_control (mqs=None, slave=False, display=False, **inarg):
   """Access to the MG_JEN_stream_control record in the forest_state record
   If init==True, initialise it with default settings."""

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_exec::stream_control()', version='20jan2006')
   # MeqServer.execute() inputrec fields:
   inarg_ms_name(pp, slave=slave)
   inarg_tile_size(pp, slave=slave)
   JEN_inarg.define (pp, 'data_column_name', 'DATA',
                     choice=['DATA','CORRECTED_DATA'],
                     help='(inputrec) MS input column')

   # MeqServer.execute() inputrec.selection fields:
   JEN_inarg.define (pp, 'channel_start_index', 10, choice=[0,5,10,20],
                     help='(inputrec.sel) index of first selected freq channel')
   JEN_inarg.define (pp, 'channel_end_index', 50, choice=[-1,25,50,100],
                     help='(inputrec.sel) index of last selected freq channel')
   JEN_inarg.define (pp, 'channel_increment', 1, choice=[1,2,3,5,10],
                     help='(inputrec.sel) take every nth channel (1=all)')
   if False:
      JEN_inarg.define (pp, 'ddid_index', 0, choice=[0,1],
                        help='(inputrec.sel) MS data descriptor index')
      JEN_inarg.define (pp, 'field_index', 0, choice=[0,1],
                        help='(inputrec.sel) MS field index')
      inarg_selection(pp)

   # MeqServer.execute() outputrec fields:
   JEN_inarg.define (pp, 'write_flags', tf=False,
                     help='(outputrec) if True, write flags to MS')
   JEN_inarg.define (pp, 'predict_column', 'CORRECTED_DATA',
                     choice=['DATA','CORRECTED_DATA','MODEL_DATA',None],
                     help='MS output column to be associated with the VisTile predict-column')
   if False:
      JEN_inarg.define (pp, 'data_column', 'DATA',
                        choice=['DATA','CORRECTED_DATA','MODEL_DATA'],
                        help='MS output column to be associated with the VisTile data-column')
      JEN_inarg.define (pp, 'residuals_column', 'MODEL_DATA',
                        choice=['DATA','CORRECTED_DATA','MODEL_DATA'],
                        help='MS output column to be associated with the VisTile residuals-column')

   # Control of MeqTree operation:
   JEN_inarg.define (pp, 'cache_policy', 0,
                     choice=[-10,-1,0,100],
                     help='MeqTree caching policy (0=smart, 100=all)')
   JEN_inarg.define (pp, 'orphans_are_roots', tf=True,
                     help='If False, delete all orphaned nodes')

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)

   # display_object(pp, funcname+'(pp)')


   # Specify the MG_JEN_stream_control record(s):
   ss = record(inputrec=record(selection=record()), outputrec=record()) 

   keys = ['ms_name', 'data_column_name', 'tile_size']
   for key in keys:
      # print key
      if pp.has_key(key):
         # print '  ',key,pp[key]
         ss['inputrec'][key] = pp[key]

   keys = ['channel_start_index','channel_end_index','channel_increment']
   keys.extend(['ddid_index','field_index','selection_string'])
   for key in keys:
      # print key
      if pp.has_key(key): ss['inputrec']['selection'][key] = pp[key]

   keys = ['write_flags', 'predict_column', 'residuals_column']
   for key in keys:
      # print key
      if pp.has_key(key): ss['outputrec'][key] = pp[key]

   # Attach to the forest state control record:
   field = 'MG_JEN_stream_control' 
   Settings.forest_state[field] = record()
   for key in ss.keys():
      Settings.forest_state[field][key] = ss[key]

   # Set other control parameters:
   if mqs:
      mqs.meq('Set.Forest.State',
              record(state=record(cache_policy=pp['cache_policy'],
                                  orphans_are_roots = pp['orphans_are_roots'])))

   # Return the stream_control record:
   return Settings.forest_state[field]










#================================================================================
# The function that does the work for _test_forest()
#================================================================================

def meqforest (mqs, parent, request=None, **pp):
   """Obsolete name for .execute()"""
   return execute (mqs, parent, request, **pp)


def execute (mqs, parent, request=None, **pp):
   """The function that does the actual work for the _test_forest()
   functions in the various MG_JEN_ scripts."""

   # display_object (MG, 'MG', 'inside MG_JEN_exec.execute()')

   from Timba.Meq import meq

   pp.setdefault('trace', False)
   pp.setdefault('save', False)       
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






#================================================================================
# Request generation functions:
#================================================================================

domain_id = 0

def make_request (request=None, **pp):
   """Helper function to make sure of a request"""
   pp.setdefault('trace', False)
   pp.setdefault('increment', False)       

   global domain_id
   if pp['increment']:
      domain_id += 1
   rqid = meq.requestid(domain_id=domain_id)

   s = '** make_request('+str(type(request))+'):'
   if request==None:
      pp.setdefault('cells', None)
      cells = pp['cells']
      pp.__delitem__('cells')
      cells = make_cells(cells, **pp)
      if True:
         # Simplest, but a bit limited:
         # request = meq.request(cells, eval_mode=0);
         request = meq.request(cells, rqtype='ev', rqid=rqid);
      else:
         # Better? (make sure that the domain/cell parameters in pp are not in the way)
         # pp.setdefault('eval_mode', 0)
         pp.setdefault('rqtype', 'ev')
         pp.setdefault('rqid', rqid)
         request = meq.request(cells, **pp);
      if pp['trace']: print s,'pp =',pp
   if pp['trace']: print s,'->',request
   return request


# ** 27 January 2006:
# *** WARNING: the eval_mode argument to meq.request() is now deprecated.
# *** Please replace it with rqtype='ev', 'e1' or 'e2'
# *** for eval_mode 0, 1 or 2.


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

   # display_object (MG, 'MG', 'after callback(_define_forest())')

   # display_forest_state()

   # Display the result at the specified recursion level:
   display_subtree (root, MG.script_name, full=pp['full'], recurse=pp['recurse'])

   # Also display it at some of the lowset recursion levels:
   if False:
      for always in [2,1]:
         if pp['full'] and always<pp['recurse']:
            display_subtree (root, MG.script_name, full=True, recurse=always)

   # display_nodescope (ns, MG.script_name)
   return 









#================================================================================
# Some useful display functions:
# NB: Should be moved to more specialised modules....
#================================================================================

#--------------------------------------------------------------------------------

def display_forest_state():
   """Display the current forest state record"""
   rr = Settings.forest_state
   JEN_record.display_object (rr, 'forest_state')
   return True

#--------------------------------------------------------------------------------

def display_nodescope (ns, txt='<txt>', trace=1):
   """Display the given nodescope in an organised way"""
   #=======================================================
   return TDL_display.nodescope(ns, txt=txt, trace=trace)
   #=======================================================
   

#----------------------------------------------------------------------------------
# Recursively display the subtree underneath a NodeStub object (node):

def display_subtree (node, txt='<txt>', level=0, cindex=0,
                     recurse=1000, count={}, full=0):
   """Recursively display the subtree starting at the given node"""
   #=======================================================
   return TDL_display.subtree(node, txt=txt, recurse=recurse,
                              cindex=cindex, full=full)
   #=======================================================


#----------------------------------------------------------------------------------
# Display any Python object(v):

def display_object (v, name='<name>', txt='', full=False, indent=0):
    """Display the given Python object"""
    #============================================================================
    return JEN_record.display_object (v, name, txt=txt, full=full, indent=indent)
    #============================================================================











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
   from Timba.Contrib.JEN.util import JEN_inargGui 

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

   if 1:
      inarg = stream_control(_getdefaults=True)  
      JEN_inarg.modify(inarg,
                       tile_size=12,       
                       _JEN_inarg_option=None)       
      if True:
         igui = JEN_inargGui.ArgBrowser()
         igui.input(inarg, MG['script_name'])
         igui.launch()
      else:
         stream_control(_inarg=inarg)  


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
      
   if 0:
      display_forest_state()
   print '\n** End of local test of:',MG.script_name,'\n*************\n'

#********************************************************************************



