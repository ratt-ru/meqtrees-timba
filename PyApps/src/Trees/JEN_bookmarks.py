# JEN_bookmarks.py

# Short description
#   Some functions to deal with creating bookmarks in the forest state record

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 05 jan 2006: creation (copied from MG_JEN_forest_state.py)
# - 12 mar 2006: .get_bookpage()


# Copyright: The MeqTree Foundation 


#********************************************************************************


from Timba.TDL import *
# from Timba.Meq import meq
# from numarray import *
from string import *
from copy import deepcopy



#===============================================================================
# Bookmark related functions:
#===============================================================================


#------------------------------------------------------------------------------- 
# Create a bookmark record (optionally, save in forest_state):


def bookmark (node=None, name=None, udi=0, viewer='Result Plotter',
              page=0, save=True, clear=0, trace=0):
    """Create a forest_state bookmark for the given node""" 
    
    if clear: Settings.forest_state.bookmarks = [] 
    if not node: return True                               # e.g. clear only
    
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
# Get the named bookmark (None = all):

def get_bookmark (name=None, level=0, trace=False):
    """Get the definition of the specified (name) bookmark"""
    if trace: print '\n** .get_bookmark(',name,') ->',
    Settings.forest_state.setdefault('bookmarks',[])
    bms = Settings.forest_state.bookmarks
    marks = []
    names = []
    for i in range(len(bms)):
      if bms[i].has_key('mark'):
        marks.append(bms[i])
        names.append(bms[i].name)
        if isinstance(name, str):
          if bms[i].name == name:
            if trace: print bms[i]
            return bms[i]
    # Not found:
    if isinstance(name, str):          # markname specified
      if trace: print '(not found)',False
      return False                     # 
    if trace: print len(marks),':',names
    return marks                       # return list of bookmarks

#----------------------------------------------------------------------
# Get the named bookpage (None = all):

def get_bookpage (name=None, level=0, trace=False):
    """Get the definition of the specified (name) bookpage"""
    if trace: print '\n** .get_bookpage(',name,') ->',
    Settings.forest_state.setdefault('bookmarks',[])
    bms = Settings.forest_state.bookmarks
    pages = []
    names = []
    for i in range(len(bms)):
      if bms[i].has_key('page'):
        pages.append(bms[i])
        names.append(bms[i].name)
        if isinstance(name, str):
          if bms[i].name == name:
            if trace: print bms[i]
            return bms[i]
    # Not found:
    if isinstance(name, str):          # pagename specified
      if trace: print '(not found)',False
      return False                     # 
    if trace: print len(pages),':',names
    return pages                       # return list of bookpages

#----------------------------------------------------------------------
# Get the named bookfolder (None = all):

def get_bookfolder (name=None, level=0, trace=False):
    """Get the definition of the specified (name) bookfolder"""
    if trace: print '\n** .get_bookfolder(',name,') ->',
    Settings.forest_state.setdefault('bookmarks',[])
    bms = Settings.forest_state.bookmarks
    folders = []
    names = []
    for i in range(len(bms)):
      if bms[i].has_key('folder'):
        folders.append(bms[i])
        names.append(bms[i].name)
        if isinstance(name, str):
          if bms[i].name == name:
            if trace: print bms[i]
            return bms[i]
    # Not found:
    if isinstance(name, str):          # foldername specified
      if trace: print '(not found)',False
      return False                     # 
    if trace: print len(folders),':',names
    return folders                     # return list of bookfolders


#----------------------------------------------------------------------
# Compare two bms records:

def is_equal (bms1, bms2, trace=False):
  """Check whether two bookmark records are equal"""
  if not isinstance(bms1, dict): return False
  if not isinstance(bms2, dict): return False
  for key in ['name','udi','viewer']:
    if not bms1.has_key(key): return False
    if not bms2.has_key(key): return False
    if not bms1[key]==bms2[key]: return False
  return True


#----------------------------------------------------------------------
# Add the given bookmark to the named page, and reconfigure it

def bookpage (bm={}, name='page', trace=False):
  """Add the given bookmark (record) to the specified bookpage"""

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

        new = True
        for bm in bms[i].page:
          if is_equal(bm, bmc): new = False

        if new:
          bms[i].page.append(bmc)
          if trace: print '- appended (',n,') to existing page:',bmc
        else:
          if trace: print '- not appended (double) to existing page:',bmc
          

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

def bookfolder (name='bookfolder', item=None, trace=False):
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
     if trace: print '-',i,':',bms[i]
     if item==None:                        # none specified
       if (bms[i].has_key('folder')):     # already a folder:
          bmsnew.append(bms[i]) 
          if trace: print 'append to bmsnew:',bms[i]
       else:                      
          folder.append(bms[i])
          if trace: print 'append to folder:',bms[i]
     elif item.__contains__(bms[i].name):
       folder.append(bms[i]) 
       if trace: print 'append to folder:',bms[i]
     else:
       bmsnew.append(bms[i]) 
       if trace: print 'append to bmsnew:',bms[i]

  # Make the new folder, and attach it to bmsnew:
  if len(folder)>0: 
     bmsnew.append(record(name=name, folder=folder)) 
     if (trace): print 'append folder to bmsnew:',folder

  Settings.forest_state.bookmarks = bmsnew

  return folder





#=======================================================================
# Stand-alone test routine:
#=======================================================================

if __name__ == '__main__':
   print '\n****************\n** Local test of: JEN_bookmarks.py :\n'
   # from Timba.Trees import TDL_display
   from Timba.Trees import JEN_record

   ns = NodeScope()

   # Parameters:
   a = ns.a << Meq.Parm(array([[1,0.2],[-0.3,0.1]]))
   b = ns.b << Meq.Parm(array([[1,-0.2],[0.3,0.1]]))
   sumab = ns << Meq.Add (a, b)

   if True:
     # Make bookmark for a single node:
     bm = bookmark (a)
     bm = bookmark (b)
     get_bookmark(trace=True)
     bookfolder()

   if True:
     # Make a named page with views of the same node:
     page_name = 'b+'
     bookmark (b, page=page_name)
     bookmark (b, udi='funklet/coeff', viewer='Record Browser', page=page_name)
     get_bookpage(page_name, trace=True)
     get_bookpage('xxx', trace=True)
     get_bookpage(trace=True)
     bookfolder('ab')
     get_bookfolder(trace=True)
     get_bookfolder('ab', trace=True)

   if True:
     # Make a named page with views of diferent nodes:
     page_name = 'sumab=a+b'
     bookmark (a, page=page_name)
     bookmark (b, page=page_name)
     bookmark (sumab, page=page_name)
     get_bookpage(trace=True)
     bookfolder('absum')
     get_bookfolder(trace=True)
 
   if True:
     # Make a named page with multiple views of the same node:
     page_name = 'views of sumab'
     bookmark (sumab, page=page_name)
     bookmark (sumab, page=page_name, viewer='ParmFiddler')
     bookmark (sumab, page=page_name, viewer='ParmFiddler')
     bookmark (sumab, page=page_name, viewer='Record Browser')
     bookmark (sumab, page=page_name, viewer='Executor')
     get_bookpage(trace=True)
     bookfolder('sumab-views')
     get_bookfolder(trace=True)


   if 0:
      JEN_record.display_object(Settings.forest_state, 'forest_state', 'JEN_bookmarks.py')

   if 1:
     get_bookmark(trace=True)
     get_bookpage(trace=True)
     get_bookfolder(trace=True)

   if 0:
      print dir(__name__)
      
   print '\n** End of local test of: JEN_bookmarks.py \n*************\n'

#********************************************************************************
#********************************************************************************






