script_name = 'MG_JEN_forest_state.py'

# Short description:
# Some functions to deal with the forest state record

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Standard preamble
from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
from string import *
from copy import deepcopy



#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

# NB: Since this module is imported by MG_JEN_exec, it cannot use its
#     standard functions. They have been emulated here. 

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
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
   bookfolder()
 
   # Make a named page with views of diferent nodes:
   page_name = 'sum=a+b'
   bookmark (a, page=page_name)
   bookmark (b, page=page_name)
   bookmark (sum, page=page_name)
   # bookfolder()
 
   # Make a named page with multiple views of the same node:
   page_name = 'views of sum'
   bookmark (sum, page=page_name)
   bookmark (sum, page=page_name, viewer='ParmFiddler')
   bookmark (sum, page=page_name, viewer='Record Browser')
   bookmark (sum, page=page_name, viewer='Executor')

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

   # Use of autoqual():
   bb = []
   for i in range(3):
      bb.append(ns.autoqual(autoqual(script_name)) << i)
   cc.append(ns << Meq.Add(children=bb))


   # Use a simple version of MG_JEN_exec.on_exit():
   # Make a (single) root node for use in _test_forest():
   global _test_root
   _test_root = script_name
   root = ns[_test_root] << Meq.Add(children=cc)
   return root    
   
 


#================================================================================
# Optional: Importable function(s): To be imported into user scripts 
#================================================================================


def init (script='<MG_JEN_xyz.py>', mode='MeqGraft'):

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

   if mode == 'MeqGraft':
      # Cache all node results:
      Settings.forest_state.cache_policy = 100
      # Orphan nodes should be retained:
      Settings.orphans_are_roots = True
   
 	
   return 



#------------------------------------------------------------------------------- 
# Attach MS (stream) info to the forest state record

def stream (**pp):
   pp.setdefault('MS', 'D1.MS')       #
   pp = record(pp)

   selection = record(channel_start_index=10,
                      channel_end_index=50)
   inputrec = record(ms_name=pp['MS'],
                     data_column_name='DATA',
                     selection=selection,
                     tile_size=1)
   outputrec = record(predict_column='MODEL_DATA')
   Settings.forest_state.stream = record(input=inputrec, output=outputrec)
   return True



#------------------------------------------------------------------------------- 
# Save the forest to a binary file(s):

def save_meqforest (mqs, filename=False, reference=False):
   if not isinstance(filename, str):
      filename = Settings.forest_state.savefile+'.meqforest'
   mqs.meq('Save.Forest',record(file_name=filename))

   # Optionally, store it in a reference-file, for auto-testing:
   if reference:
      filename = Settings.forest_state.savefile+'_reference.meqforest'
      mqs.meq('Save.Forest',record(file_name=filename))
      
   return filename



#------------------------------------------------------------------------------- 
# Create a bookmark:


def bookmark (node=0, name=0, udi=0, viewer='Result Plotter',
              page=0, save=True, clear=0, trace=0):
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
# Access/display/clear the bookmarks:

def bookmarks (clear=0, trace=0):
  if clear: Settings.forest_state.bookmarks = [] 
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks
  # if trace: JEN_display(bms,'bms')
  return bms


#----------------------------------------------------------------------
# Add the given bookmark to the named page, and reconfigure it

def bookpage (bm={}, name='page', trace=0):
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
# Collect a number of bokkmarks/pages into a named folder:

def bookfolder (name='bookfolder', item=None, trace=0):
  if (trace): print '\n** .bookfolder(',name,'):'
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks

  if item==None:              # if item=None, put ALL bookmarks in the folder
     pass
  elif not isinstance(item, (tuple, list)):
     item = [item]                      # assume string...
  elif len(item)==0:                # empty list
     return []                             # ignore

  folder = []
  bmsnew = []
  for i in range(len(bms)):
     print '-',i,':',bms[i]
     if item==None:
       folder.append(bms[i])
       if (trace): print 'append to folder:',bms[i]
     elif item.__contains__(bms[i].name):
       folder.append(bms[i]) 
       if (trace): print 'append to folder:',bms[i]
     else:
       bmsnew.append(bms[i]) 
       if (trace): print 'append to bmsnew:',bms[i]

  if len(folder)>0: 
	bmsnew.append(record(name=name, folder=folder)) 
        if (trace): print 'append folder to bmsnew:',folder

  Settings.forest_state.bookmarks = bmsnew
  return folder


#---------------------------------------------------------------------------
# Add the given named (kwitem) and unnamed (item) items to the forest_state

def trace (*item, **kwitem):
   return append ('trace', item, kwitem)

# Special case: for the result (list) of object.display()

def object(object, txt='<txt>'):
  ss = object.display(txt)
  trace(ss, key=object.label())
  return True

def history (*item, **kwitem):
   return append ('history', item, kwitem)

def error (*item, **kwitem):
   return append ('ERROR', item, kwitem)

def warning (*item, **kwitem):
   return append ('WARNING', item, kwitem)

def append (field, item, kwitem):
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
  field = '_test_result'
  r = mqs.meq('Set.Forest.State',record(state=record(**{field:result})),wait=False);
  return r


#---------------------------------------------------------------------------
# Counter service (use by autoqual)
# It can be inspected in the forest state record
# NB: if increment=0  (i.e. not specified):
#     - if key does not exist yet, initialise with 0
#     - just return the current value

def counter (key, increment=0, reset=False):
   field = 'jen_counter'
   Settings.forest_state.setdefault(field,record())
   rr = Settings.forest_state[field]
   rr.setdefault(key, 0)
   if reset: rr[key] = 0
   rr[key] += increment
   Settings.forest_state[field] = rr
   return rr[key]

# Generate a unique qualifier by using the counter service 

def uniqual (key='<MG_JEN_forest_state.autoqual>', qual=None, **pp):
   if isinstance(qual, str) and qual=='auto':
      print '**',script_name,'uniqual(',key,'): obsolete call: qual=',qual,'->',None
      qual = None
   if qual==None:
      n = counter(key, increment=-1)          # note negative increment!
      qual = str(n)
   return qual

# Old name (discouraged)

def autoqual (key='<MG_JEN_forest_state.autoqual>', qual=None, **pp):
   return uniqual (key=key, qual=qual, **pp)








#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

init(script_name)
stream()

#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   # Use a simple version of MG_JEN_exec.meqforest():
   cells = meq.cells(meq.domain(0,1,0,1),num_freq=6,num_time=4);
   request = meq.request(cells,eval_mode=0);
   global _test_root
   mqs.meq('Node.Execute',record(name=_test_root, request=request));
   return

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   print '\n****************\n** Local test of:',script_name,':\n'

   # Use a simple version of MG_JEN_exec.without_meqserver():
   ns = NodeScope()
   root = _define_forest(ns)
   ns.Resolve()

   from Timba.Contrib.JEN import MG_JEN_exec
   MG_JEN_exec.display_subtree(root, script_name, full=1)

   if 0:
      from Timba.Trees import TDL_common
      sp = TDL_common.Super()
      ss = sp.display(script_name)
      trace(ss, key=sp.label())
      
   if 1:
      from Timba.Trees import TDL_Cohset
      cs = TDL_Cohset.Cohset()
      ss = cs.display(script_name)
      trace(ss, key=cs.label())
      
   rr = Settings.forest_state
   MG_JEN_exec.display_object(rr, 'forest_state', script_name)

   print '\n** End of local test of:',script_name,'\n*************\n'

#********************************************************************************
#********************************************************************************






