# MG_JEN_forest_state.py

# Short description:
# Some functions to deal with the forest state record

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


#================================================================================
# Preamble
#================================================================================

from Timba.TDL import *
# from Timba.Meq import meq

MG = record(script_name='MG_JEN_forest_state.py', last_changed='h22sep2005')

# from numarray import *
from string import *
from copy import deepcopy




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

   # Make an empty list:
   cc = []

   # Parameters:
   a = ns.a << Meq.Parm(array([[1,0.2],[-0.3,0.1]]))
   b = ns.b << Meq.Parm(array([[1,-0.2],[0.3,0.1]]))
   sum = ns << Meq.Add (a, b)
   cc.append(sum)

   # Make bookmark for the forest state record:
   # bm = bookmark (..., viewer='Record Browser')           # <-----??
 
   # Make bookmark for a single node:
   bm = bookmark (a)
   bm = bookmark (b)
   bookfolder()
 
   # Make a named page with views of the same node:
   page_name = 'b+'
   bookmark (b, page=page_name)
   bookmark (b, udi='funklet/coeff', viewer='Record Browser', page=page_name)
   bookfolder('ab')
 
   # Make a named page with views of diferent nodes:
   page_name = 'sum=a+b'
   bookmark (a, page=page_name)
   bookmark (b, page=page_name)
   bookmark (sum, page=page_name)
   bookfolder('absum')
 
   # Make a named page with multiple views of the same node:
   page_name = 'views of sum'
   bookmark (sum, page=page_name)
   bookmark (sum, page=page_name, viewer='ParmFiddler')
   bookmark (sum, page=page_name, viewer='Record Browser')
   bookmark (sum, page=page_name, viewer='Executor')
   bookfolder('sum-views')

   # Append items to the forest state record:
   for i in [1,2]:
     rr = record(i=i, a=4, b=True)
     trace(i, 'a', [1,2], (3,4), x=False, rr=rr)
     error(i, 'b', [1,2], (3,4))
     warning(x=False, rr=rr)
     history(i)

   # Counter service (check in forest state record):
   counter('key1', increment=True)
   counter('key1', increment=True)
   counter('key2', increment=True)

   # Use of uniqual():
   bb = []
   for i in range(3):
      bb.append(ns.uniqual(uniqual(MG.script_name)) << i)
   cc.append(ns << Meq.Add(children=bb))


   # Use a simple version of MG_JEN_exec.on_exit():
   # Make a (single) root node for use in _test_forest():
   global _test_root
   _test_root = MG.script_name
   root = ns[_test_root] << Meq.Add(children=cc)
   return root    
   
 











#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


def init (script='<MG_JEN_xyz.py>', mode='MeqGraft'):
   """Initialise the forest_state record (called by all MG_JEN_ scripts)"""

   # Reset the forest history record (retained otherwise...?)
   # Obsolete, replaced by .history(), which uses jen-record
   # Settings.forest_state.forest_history = record()

   # Reset the jen-record (see .trace(), .error() etc below)
   Settings.forest_state['jen'] = record()

   # Reset the bookmarks (if not, the old ones are retained) 
   Settings.forest_state.bookmarks = []
     
   # The default name for the .meqforest save file:
   s1 = split(script,'.')
   if isinstance(s1, (list, tuple)): s1 = s1[0]
   Settings.forest_state.savefile = s1

   # Initialise the (MS-related) stream control records:
   # See also MG_JEN_exec.py
   stream = record(initrec=record(), inputinit=record(), outputinit=record())
   Settings.forest_state.stream = stream

   if mode == 'MeqGraft':
      # Cache all node results:
      Settings.forest_state.cache_policy = 100
      # Orphan nodes should be retained:
      Settings.orphans_are_roots = True
   
 	
   return 

# Execute this function:
init(MG.script_name)




#------------------------------------------------------------------------------- 
# Save the forest to a binary file(s):

def save_meqforest (mqs, filename=False, save_reference=False):
   """Save the current meqforest, using the filename in the forest_state record.
   If save_reference=True, also save the result for later testing."""
   
   if not isinstance(filename, str):
      filename = Settings.forest_state.savefile+'.meqforest'
   mqs.meq('Save.Forest',record(file_name=filename))

   # Optionally, store it in a reference-file, for auto-testing:
   if save_reference:
      mqs.meq('Save.Forest',record(file_name=filename+'_reference'))
      
   return filename



#===============================================================================
# Bookmark related functions:
#===============================================================================

#------------------------------------------------------------------------------- 
# Create a bookmark record (optionally, save in forest_state):


def bookmark (node=0, name=0, udi=0, viewer='Result Plotter',
              page=0, save=True, clear=0, trace=0):
  """Create a forest_state bookmark for the given node""" 
   
  if clear: Settings.forest_state.bookmarks = [] 
  if isinstance(node, int): return True                     # e.g. clear only

  bm = record(viewer=viewer, publish=True)
  bm.udi = '/node/'+node.name
  if isinstance(udi, str):  bm.udi = bm.udi+'/'+udi                 

  # The name in the bookmark menu:
  bm.name = node.name                                    # automatic
  if isinstance(name, str): bm.name = name;              # override
  if trace: print '\n** JEN_bookmark:',bm,'\n'

  # If a bookpage is specified, do not make a separate bookmark (save),
  # but add it to the named page:

  if isinstance(page, str):
    # Add the bookmark (bm) to the named page
    bookpage (bm, name=page, trace=trace)
  elif save:
    # Save the bookmark in the forest_state record
    Settings.forest_state.setdefault('bookmarks',[]).append(bm)

  return bm


#----------------------------------------------------------------------
# Access/display/clear the current bookmarks:

def bookmarks (clear=0, trace=0):
  """Access function to the current forest_state bookbark record"""
  if clear: Settings.forest_state.bookmarks = [] 
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks
  return bms


#----------------------------------------------------------------------
# Add the given bookmark to the named page, and reconfigure it

def bookpage (bm={}, name='page', trace=0):
  """Add the given bookmark (record) to the specified bppkpage"""
  
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks

  # Check whether the specified page already exists:
  found = 0
  # bmc = record(bm.copy())
  bmc = deepcopy(bm)
  for i in range(len(bms)):
    if bms[i].has_key('page'):
      if bms[i].name == name:
        found = True                                    # used below
      
        # Automatic placement of the panel:
        n = len(bms[i].page)                      # current length
        if n==0: bmc.pos = [0,0]               # superfluous

        # 1st col:
        if n==1: bmc.pos = [1,0]

        # 2nd col:
        if n==2: bmc.pos = [0,1]
        if n==3: bmc.pos = [1,1]

        # 3rd row:
        if n==4: bmc.pos = [2,0]
        if n==5: bmc.pos = [2,1]

        # 3rd col:
        if n==6: bmc.pos = [0,2]
        if n==7: bmc.pos = [1,2]
        if n==8: bmc.pos = [2,2]

        # 4th row:
        if n==9: bmc.pos = [3,0]
        if n==10: bmc.pos = [3,1]
        if n==11: bmc.pos = [3,2]

        # 4th col:
        if n==12: bmc.pos = [0,3]
        if n==13: bmc.pos = [1,3]
        if n==14: bmc.pos = [2,3]
        if n==15: bmc.pos = [3,3]


        bms[i].page.append(bmc)
        if trace: print '- appended (',n,') to existing page:',bmc

  # Make a new page, if it does not yet exists
  if not found:
    bmc.pos = [0,0]
    if trace: print '- created new bookpage:',bmc
    bms.append(record(name=name, page=[bmc]))
      
  Settings.forest_state.bookmarks = bms
  return bms


#----------------------------------------------------------------------
# Collect the specified (item) bookmarks/pages into a named folder:
# If none specified, collect all the non-folder bookmarks.

def bookfolder (name='bookfolder', item=None, trace=0):
  """Collect the specified bookmarks/pages into a bookmark folder"""
  
  if (trace): print '\n** .bookfolder(',name,'):'

  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks

  if item==None:     # if item=None, put ALL non-folder bookmarks in the folder
     pass
  elif not isinstance(item, (tuple, list)):
     item = [item]                         # assume string...
  elif len(item)==0:                       # empty list
     return []                             # ignore

  # Collect items for the folder, and attach the rest to bmsnew:
  folder = []
  bmsnew = []
  for i in range(len(bms)):
     print '-',i,':',bms[i]
     if item==None:                        # none specified
       if (bms[i].has_key('folder')):     # already a folder:
          bmsnew.append(bms[i]) 
          if (trace): print 'append to bmsnew:',bms[i]
       else:                      
          folder.append(bms[i])
          if (trace): print 'append to folder:',bms[i]
     elif item.__contains__(bms[i].name):
       folder.append(bms[i]) 
       if (trace): print 'append to folder:',bms[i]
     else:
       bmsnew.append(bms[i]) 
       if (trace): print 'append to bmsnew:',bms[i]

  # Make the new folder, and attach it to bmsnew:
  if len(folder)>0: 
	bmsnew.append(record(name=name, folder=folder)) 
        if (trace): print 'append folder to bmsnew:',folder

  Settings.forest_state.bookmarks = bmsnew

  return folder





#===========================================================================
# Routines to attach information to the forest_state record:
#===========================================================================

#--------------------------------------------------------------------------
# Add the given named (kwitem) and unnamed (item) items to the forest_state

def trace (*item, **kwitem):
   """Add the named and unnammed items to the forest_state trace"""
   return append ('trace', item, kwitem)

# Special case: for the result (list) of object.display()

def object(object, txt='<txt>'):
  """Special case of trace(), where the input is a Python object"""
  ss = object.display(txt)
  if ss==None:
     ss = MG.script_name+' '+object.type()+' '+object.label()+': '
     ss += '.display() -> None (?)'
     print '\n***',MG.script_name,object.type(),object.label(),ss,'\n'
  trace(ss, key=object.label())
  return True

# Same for history items:

def history (*item, **kwitem):
   """Add the named and unnammed items to the forest_state history"""
   return append ('history', item, kwitem)

# Same for error messages:

def error (*item, **kwitem):
   """Add the named and unnammed items to the forest_state errors"""
   return append ('ERROR', item, kwitem)

# Same for warning messages:

def warning (*item, **kwitem):
   """Add the named and unnammed items to the forest_state warnings"""
   return append ('WARNING', item, kwitem)

# Common routine that does the work:

def append (field, item, kwitem):
  """Common helper function for trace/object/history/error/warning"""
  # Make a record of the named arguments:
  kwitem = record(kwitem)

  # Attach the list of unnamed items:
  # print '** len(item):',len(item)
  if len(item)>0:
     key = kwitem.get('key','*item')
     # kwitem.__delitem__('key')
     kwitem[key] = item
     if len(item)==1: kwitem[key] = item[0]
  # print '** kwitem.keys():',kwitem.keys()

  # Attach the kwitem record as a numbered field
  Settings.forest_state.setdefault('jen',record())
  Settings.forest_state['jen'].setdefault(field,record())
  rr = Settings.forest_state['jen'][field]
  level = kwitem.get('level',1)
  indent = level*'..'
  key = str(len(rr))
  rr[key] = kwitem

  Settings.forest_state['jen'][field] = rr
  return rr[key]

#---------------------------------------------------------------------------
# Functions for automatic testing
# Attach the test-result to the forest state record 

def attach_test_result (mqs, result):
  """Attach the test result to the forest state record"""
  field = '_test_result'
  r = mqs.meq('Set.Forest.State',record(state=record(**{field:result})),wait=False);
  return r


#---------------------------------------------------------------------------
# Counter service (use by uniqual)
# It can be inspected in the forest state record
# NB: if increment=0  (i.e. not specified):
#     - if key does not exist yet, initialise with 0
#     - just return the current value

def counter (key, increment=0, reset=False):
   """Convenience function to for named counters"""
   field = 'jen_counter'
   Settings.forest_state.setdefault(field,record())
   rr = Settings.forest_state[field]
   rr.setdefault(key, 0)
   if reset: rr[key] = 0
   rr[key] += increment
   Settings.forest_state[field] = rr
   return rr[key]

# Generate a unique qualifier by using the counter service 

def uniqual (key='<MG_JEN_forest_state.uniqual>', qual=None, **pp):
   """Helper function to generate unique qualifiers for node categories.
   Every time it is called, it decrements an internal counter for the
   specified key, and returns its new value. This can be used in node names"""
   
   if isinstance(qual, str) and qual=='auto':
      print '**',MG.script_name,'uniqual(',key,'): obsolete call: qual=',qual,'->',None
      qual = None
   if qual==None:
      n = counter(key, increment=-1)          # note negative increment!
      qual = str(n)
   return qual

# Old name (discouraged)

def autoqual (key='<MG_JEN_forest_state.autoqual>', qual=None, **pp):
   """Obsolete version of uniqual()"""
   return uniqual (key=key, qual=qual, **pp)








#********************************************************************************
# Testing routines
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   """Meqforest execution routine"""
   # Use a simple version of MG_JEN_exec.meqforest():
   cells = meq.cells(meq.domain(0,1,0,1),num_freq=6,num_time=4);
   request = meq.request(cells,eval_mode=0);
   global _test_root
   mqs.meq('Node.Execute',record(name=_test_root, request=request));
   return


#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n****************\n** Local test of:',MG.script_name,':\n'

   # NB: Importing a module resets the forest_state record!!
   from Timba.Contrib.JEN import MG_JEN_exec

   # Use a simple version of MG_JEN_exec.without_meqserver():
   ns = NodeScope()
   root = _define_forest(ns)
   ns.Resolve()
   MG_JEN_exec.display_subtree(root, MG.script_name, full=1)
   MG_JEN_exec.display_object(Settings.forest_state, 'forest_state', MG.script_name)

   if 0:
      from Timba.Trees import TDL_common
      sp = TDL_common.Super()
      ss = sp.display(MG.script_name)
      trace(ss, key=sp.label())
      
   if 0:
      from Timba.Trees import TDL_Cohset
      cs = TDL_Cohset.Cohset()
      ss = cs.display(MG.script_name)
      trace(ss, key=cs.label())

   MG_JEN_exec.display_object(Settings.forest_state, 'forest_state', MG.script_name)

   if 0:
      print dir(__name__)
      
   print '\n** End of local test of:',MG.script_name,'\n*************\n'

#********************************************************************************
#********************************************************************************






