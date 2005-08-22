#   ../Timba/PyApps/test/JEN_forest_state.py:  
#   JEN utility functions for interacting with the forest_state record

# preamble
from Timba.TDL import *
from Timba.Meq import meq
from copy import deepcopy

from JEN_util import *
# from JEN.JEN_util import *



#==================================================================================
# Initialisation of the forest state (in .tdl scripts)
#==================================================================================

def JEN_forest_state_init(script='<TDL_script>', **pp):

  # Cache all node results:
  Settings.forest_state.cache_policy = 100

  # see also JEN_forest_savefile ()
  Settings.forest_state.savefile = script

  # Orphan nodes should be retained:
  Settings.orphans_are_roots = True

  # Some stuff related to MS (kludge!):
  selection = record(channel_start_index=10,
                     channel_end_index=50)
  inputrec = record(ms_name='D1.MS',
                    data_column_name='DATA',
                    selection=selection,
                    tile_size=1)
  outputrec = record(predict_column='MODEL_DATA')
  Settings.forest_state.stream = record(input=inputrec, output=outputrec)

  # See JEN_bookmark() below:
  Settings.forest_state.bookmarks = []

  return

#---------------------------------------------------------------------------------
# Append a substring to the save-file:

def JEN_forest_savefile (append=0, origin='<origin>', trace=1):
  s = Settings.forest_state.savefile
  if isinstance(append, str):
    s = s+str(append)
    Settings.forest_state.savefile = s
  if trace: print '\n** Settings.forest_state.savefile (',origin,'):',s
  return s

#==================================================================================
# Add a (line) item to the forest generation log:

def JEN_forest_history (item=0, error=0, warning=0, level=1, show=0, trace=0):
  return JEN_history (Settings.forest_state,
                      item=item, error=error, warning=warning,
                      level=level, hkey='_forest_history', htype='record',
                      show=show, trace=trace)

  
#==================================================================================
# Bookmark functions
#==================================================================================

# Make a bookmark definition (bm) for the given node:

def JEN_bookmark (node=0, name=0, udi=0, viewer='Result Plotter',
                  page=0, save=True, clear=0, trace=0):
  if clear: Settings.forest_state.bookmarks = [] 
  if isinstance(node, int): return T                     # e.g. clear only

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
    JEN_bookpage (bm, name=page, trace=trace)
  elif save:
    # Save the bookmark in the forest_state record
    Settings.forest_state.setdefault('bookmarks',[]).append(bm)

  return bm

# 	if (any(viewer=="plot plotter")) viewer := 'Result Plotter';
# 	if (any(viewer=="browse browser")) viewer := 'Result Browser';
# 	if (any(viewer=="fiddler fidler")) viewer := 'ParmFiddler';
# 	if (any(viewer=="exec executor")) viewer := 'Executor';


#----------------------------------------------------------------------
# Access/display/clear the bookmarks:

def JEN_bookmarks (clear=0, trace=0):
  if clear: Settings.forest_state.bookmarks = [] 
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks
  if trace: JEN_display(bms,'bms')
  return bms

#----------------------------------------------------------------------
# Add the given bookmark to the named page, and reconfigure it

def JEN_bookpage (bm={}, name='page', trace=0):
  if trace: print '\n** JEN_bookpage(',bm,')'
  Settings.forest_state.setdefault('bookmarks',[])
  bms = Settings.forest_state.bookmarks

  # Check whether the specified page already exists:
  found = 0
  # bmc = record(bm.copy())
  bmc = deepcopy(bm)
  for i in range(len(bms)):
    if bms[i].has_key('page'):
      if bms[i].name == name:
        found = 1                                # used below

        # Automatic placement of the panel:
        n = len(bms[i].page)                     # current length
        if n==0: bmc.pos = [0,0]                 # superfluous

        # 1st col:
        if n==1: bmc.pos = [1,0]

        # 2nd col:
        if n==2: bmc.pos = [0,1]
        if n==3: bmc.pos = [1,1]

        # 3rd col:
        if n==4: bmc.pos = [0,2]
        if n==5: bmc.pos = [1,2]

        # 3rd row:
        if n==6: bmc.pos = [2,0]
        if n==7: bmc.pos = [2,1]
        if n==8: bmc.pos = [2,2]

        # 4th col:
        if n==9: bmc.pos = [0,3]
        if n==10: bmc.pos = [1,3]
        if n==11: bmc.pos = [2,3]

        # 4th row:
        if n==12: bmc.pos = [3,0]
        if n==13: bmc.pos = [3,1]
        if n==14: bmc.pos = [3,2]
        if n==15: bmc.pos = [3,3]

        bms[i].page.append(bmc)
        if trace: print '- appended (',n,') to existing page:',bmc

  # Make a new one, if not yet exists
  if not found:
    bmc.pos = [0,0]
    if trace: print '- created new bookpage:',bmc
    bms.append(record(name=name, page=[bmc]))
      
  Settings.forest_state.bookmarks = bms
  return bms






#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  ns = NodeScope()


  if 1:
    # JEN_forest_history('xxx')
    JEN_forest_history(show=True)

  if 0:
#    JEN_bookmark (clear=1, trace=1)
    xxx = ns.xxx << Meq.Parm(6)
    yyy = ns.yyy << Meq.Parm(6)
    JEN_bookmark (xxx, udi=0, viewer='Result Plotter', clear=0, trace=1)
    JEN_bookmark (xxx, udi=0, viewer='Result Plotter', clear=0, page='page1', trace=1)
    JEN_bookmark (yyy, udi=0, viewer='Result Plotter', clear=0, page='page1', trace=1)
    JEN_bookmark (yyy, udi=0, viewer='Result Plotter', clear=0, page='page1', trace=1)
    bms = JEN_bookmarks(trace=1)


  if 0:
    JEN_display_NodeScope(ns, 'test')

  print

