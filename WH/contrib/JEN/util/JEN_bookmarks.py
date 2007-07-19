# JEN_bookmarks.py

# Short description
#   Some functions to deal with creating bookmarks in the forest state record

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 05 jan 2006: creation (copied from MG_JEN_forest_state.py)
# - 12 mar 2006: .get_bookpage()
# - 20 mar 2006: revamped (especially including folders)
# - 25 mar 2006: separated the semi-obsolete functions
# - 09 aug 2006: inplement recurse argument in .create()
# - 03 oct 2006: refined autoplace()


# Copyright: The MeqTree Foundation 



#********************************************************************************


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
from Timba.Contrib.JEN.util import JEN_record

from string import *
from copy import deepcopy



#===============================================================================

def family (fam=[], node=None, recurse=0, step_children=False, nmax=9):
    """Recursive function to extract the family from the given node,
    i.e. a list if the node itself and its multi-generation offspring."""
    # First the children:
    for i in range(len(node.children)):
        if len(fam)<nmax:
            fam.append(node.children[i][1])
    # Then the step_children (if any):
    if step_children:
        for i in range(len(node.stepchildren)):
            if len(fam)<nmax:
                fam.append(node.stepchildren[i][1])
    # Then recurse to get grandchildren:
    if recurse>1:
        for i in range(len(node.children)):
            if len(fam)<nmax:
                family (fam, node.children[i][1],
                        recurse=recurse-1, nmax=nmax)
    return True

#------------------------------------------------------------------------------

def create (node=None, name=None, udi=None, viewer='Result Plotter',
            recurse=0, step_children=False,
            page=None, folder=None, perpage=9,
            save=True, trace=False):
    """Create a forest_state bookmark for the given node(s).
    - viewer = 'Result Plotter'   (default)
    - viewer = 'Collections Plotter'
    - viewer = 'History Plotter'
    - viewer = 'ParmFiddler'
    - viewer = 'Record Browser'
    - viewer = 'Executor'
    - udi += 'funklet/coeff'
    - udi += 'cache/result'
    If save==True (default), the bookmark will automatically be inserted
    in the specified page/folder, creating the latter if necessary. 
    NB: This is the only bookmark function that is needed normally.
    If node is a list (of nodes), make page(s) of multiple bookmarks.
    If recurse>0, make a page of the node and its children etc.
    """ 

    #------------------------------------------------------------------
    # If recurse>0, make a list of the node and its children

    if not isinstance(node, (list, tuple)):
        if recurse>0:
            if page==None:                                 # automatic pagename
                page = 'family of: '+node.name
            fam = [node]
            family (fam, node, recurse=recurse, step_children=step_children, nmax=9)
            node = fam                                     # replace with list


    #------------------------------------------------------------------
    # Page can be a list or a string (this requires a little thought...)

    pagelist = []
    if isinstance(page, (list,tuple)):
        pagelist = page
    elif isinstance(page, str):
        pagelist = [page]
    elif isinstance(node, (list, tuple)):
        pagelist = ['autopage']
    else:
        pagelist = [None]

    #------------------------------------------------------------------
    # If node is a list, make multiple bookmarks:

    if isinstance(node, (list, tuple)):
        if len(node)>=perpage:
            if not isinstance(folder, str): folder = '** AUTO_GROUPS **'
        if not isinstance(page, str): page = 'autopage'
        if isinstance(name, str): page = '_'+name          # ....?
        # if isinstance(name, str): page += '_'+name       # ....?
        n = _counter (page, increment=-1)
        if n<-1: page += '('+str(n)+')'
        pagecount = 1
        itemcount = 0
        for item in node:
            itemcount += 1                                 # increment
            if itemcount>perpage:                          # max nr of items per page
                itemcount = 1                              # reset
                pagecount += 1                             # increment
            pagename = page
            if pagecount>1: pagename = page+'_'+str(pagecount)
            # print '-',itemcount,pagecount,pagename,item.name
            create (item, name=name, udi=udi, viewer=viewer,
                    save=save, page=pagename, folder=folder,
                    perpage=perpage, trace=trace)
        return True
    #------------------------------------------------------------------

    # Initialise the bookmark record:
    bm = record(viewer=viewer, publish=True)

    # The udi:
    bm.udi = '/node/'+node.name                            # root part of udi
    if isinstance(udi, str):                               # extension specified
        bm.udi = bm.udi+'/'+udi                            #   append it
    
    # The name in the bookmark menu:
    bm.name = node.name                                    # automatic name
    if isinstance(name, str):                              # name specified
        bm.name = name                                     #   override

    # Dispose of the result:
    if save:
        return insert(bm, page=page, folder=folder, trace=trace)
    else:
        if trace: print '\n** JEN_bookmark (not saved):',bm,'\n'
        return bm


#-----------------------------------------------------------------------------

def insert (bm=None, page=None, folder=None, level=0, bmlist=None, trace=False):
    """Insert the specified bookmark (record) to the specified bookpage
    [of the specified folder]. Create the latter if necessary."""

    s1 = str(level)+(level*'..')+'.insert('
    s1 += str(bm.name)
    s1 += ','+str(page)+','+str(folder)+'): '
    if trace: print '\n**',s1
    
    if level==0:
        if isinstance(page, bool): page = None               # upwards compatibility
        if isinstance(folder, bool): folder = None           # upwards compatibility
        bmlist = current_settings()                          # bmlist is a list
        if not isinstance(bmlist, list): bmlist = []
    
    # Check whether the specified page already exists:
    found = 0
    # bmc = record(bm.copy())
    bmc = deepcopy(bm)

    # Go through the list (of records):
    inserted = 0
    new = True
    for i in range(len(bmlist)):
        item = bmlist[i]                                  # convenience
        if not isinstance(item, dict):
            print s1,'** ERROR ** item not a dict, but:',type(item)

        elif not item.has_key('name'):
            print s1,'** ERROR ** item does not have name-field:',item.keys()

        elif item.has_key('folder'):                      # item is a folder (record)
            if not isinstance(item.folder, list):
                print s1,'** ERROR ** item.folder not a list, but:',type(item.folder)
            elif not isinstance(folder, str):             # folder not specified, or inside correct one
                pass                                      # ignore this folder
            elif not item.name == folder:                 # other folder
                # NB: Do we have folders of folders..?
                # NB: Do we allow multiple folders (lists)..?
                pass                                      # ignore this folder
            else:                                         # found specified folder
                # Insert the bookmark into this folder (somehow):
                if trace: print '- insert bookmark into specified folder:',folder,'(',page,bm.name,')'
                inserted += insert (bm, page=page, folder=None,
                                    level=level+1, bmlist=bmlist[i].folder,
                                    trace=trace)

        elif isinstance(folder, str):                     # folder specified explicitly
            pass                                          # ignore page/bookmark items

        elif item.has_key('page'):                        # item is a page (record)
            if not isinstance(item.page, list):
                print s1,'** ERROR ** item.page not a list, but:',type(item.page)
            elif isinstance(page, str) and (not item.name == page):   # wrong page
                pass                                      # ignore this page
            else:                                         # found specified page
                # Append the bookmark to bmlist[i].page (mutable):
                new = True
                for bm1 in item.page:                     # avoid doubles
                    if is_equal(bm1, bm):
                        new = False                       # bookmark already exists
                if new:
                    bmc = deepcopy(bm)
                    n = len(bmlist[i].page)               # current page length
                    autoplace(bmc, n)                     # Automatic placement of the panel:
                    bmlist[i].page.append(bmc)            # append to page
                    if trace: print '- appended (',n,') to existing page:',page,bmc
                else:
                    if trace: print '- not appended (double) to existing page:',page,bmc
                inserted += 1

        else:                                             # assume: item is bookmark (record)
            if is_equal(bm, item):
                new = False                               # used below
          


    # The bookmark (bm) should always be inserted somewhere:
    if inserted==0:                                       # none inserted

        # Create a new page, if required:
        newpage = False
        if isinstance(page, str):                 
            bmc = deepcopy(bm)
            bmc.pos = [0,0]
            newpage = record(name=page, page=[bmc])

        # Create a new folder, if required:
        if isinstance(folder, str):               
            if newpage:
                newfolder = record(name=folder, folder=[newpage])
            else:
                newfolder = record(name=folder, folder=[bmc])
            bmlist.append(newfolder)
            if trace: print '- created new folder:',newfolder

        elif newpage:
            bmlist.append(newpage)
            if trace: print '- created new page:',newpage
        else:
            bmlist.append(bm)
            if trace: print '- attached new bookmark:',bm
        inserted = 1

    # Finished: Replace the current settings:
    current_settings(bmlist, txt='end of bmark', trace=False)
    return inserted



#----------------------------------------------------------------------

def autoplace(bm, n=0):
    """Automatic placement of the given bookmark (bm) as the
    nth panel on a bookpage"""

    if n==0: bm.pos = [0,0]               # superfluous
    
    # 1st col:
    if n==1: bm.pos = [1,0]
    
    # 2nd col:
    if n==2: bm.pos = [0,1]
    if n==3: bm.pos = [1,1]
    
    # 3rd row:
    if n==4: bm.pos = [2,0]
    if n==5: bm.pos = [2,1]
    
    # 3rd col:
    if n==6: bm.pos = [0,2]
    if n==7: bm.pos = [1,2]
    if n==8: bm.pos = [2,2]
    
    # 4th row:
    if n==9: bm.pos = [3,0]
    if n==10: bm.pos = [3,1]
    if n==11: bm.pos = [3,2]

    # 4th col:
    if n==12: bm.pos = [0,3]
    if n==13: bm.pos = [1,3]
    if n==14: bm.pos = [2,3]
    if n==15: bm.pos = [3,3]

    # print '** bookmarks.autoplace(n=',n,bm.name,'): bm.pos =',bm.pos
    return True


#-----------------------------------------------------------------------------

def current_settings(new=None, txt='JEN_bookmarks.py', clear=False, trace=False):
    """Get/set the current bookmark (list) from/to the global Settings"""
    Settings.forest_state.setdefault('bookmarks',[])
    if new:                                            # replace with new
        Settings.forest_state.bookmarks = new
    if clear:                                          # clear all
        Settings.forest_state.bookmarks = []
    if trace:
        JEN_record.display_object(Settings.forest_state.bookmarks,
                                  'forest_state.bookmarks', txt)
    return Settings.forest_state.bookmarks


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







#===================================================================================
#===================================================================================
#===================================================================================
#===================================================================================
# semi-obsolete:
#===================================================================================


#------------------------------------------------------------------------------- 
# Create a bookmark record (optionally, save in forest_state):


def bookmark (node=None, name=None, udi=0, viewer='Result Plotter',
              page=None, folder=None,
              save=True, clear=False, trace=False):
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
    return current_settings(clear=clear, trace=trace)


#----------------------------------------------------------------------
# Get the named bookmark (None = all) on the specified page of the specified folder:

def get_bookmark (name=None, page=None, folder=None, level=0, trace=False):
    """Get a list of definition(s) of the specified (name) bookmark(s)
    on the specified page(s) of the specified folder(s). None is all."""
    if trace: print '\n** .get_bookmark(',name,page,folder,') ->',
    bms = current_settings()
    marks = []
    names = []
    for i in range(len(bms)):
      if not bms[i].has_key('name'):
          pass                         # error
      elif bms[i].has_key('folder'):
          pass
      elif bms[i].has_key('page'):
          pass
      else:
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
# Get the named bookpage (None = all) of the specified folder:

def get_bookpage (name=None, folder=None, level=0, trace=False):
    """Get a list of definition(s) of the specified (name) bookpage(s)
    in the specified folder(s). In all cases, None means all"""
    if trace: print '\n** .get_bookpage(',name,folder,') ->',
    bms = current_settings()
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
    bms = current_settings()
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
# Get the named bookmark (None = all) on the specified page of the specified folder:

def set_bookmark (bm, page=None, folder=None, replace=True, level=0, trace=False):
    """Put the specified bookmark(s) on the specified page(s) of the
    specified folder(s)."""
    return True



#----------------------------------------------------------------------
# Add the given bookmark to the named page/folder, and reconfigure it

def bookpage (bm={}, name='page', folder=None, trace=False):
  """Add the given bookmark (record) to the specified bookpage
  [of the specified folder]"""

  bms = current_settings()

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
        autoplace(bmc, n)

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
      
  # Replace (and return) the current settings:
  return current_settings(bms)


    
#----------------------------------------------------------------------
# Collect the specified (item) bookmarks/pages into a named folder:
# If none specified, collect all the non-folder bookmarks.

def bookfolder (name='bookfolder', item=None, trace=False):
  """Collect the specified bookmarks/pages into a bookmark folder"""
  
  if (trace): print '\n** .bookfolder(',name,'):'

  bms = current_settings()

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

  # Replace the current settings:
  current_settings(bmsnew)
  return folder





#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** JEN_bookmarks: _counters(',key,') =',_counters[key]
    return _counters[key]





#=======================================================================
# Stand-alone test routine:
#=======================================================================

if __name__ == '__main__':
   print '\n****************\n** Local test of: JEN_bookmarks.py :\n'
   # from Timba.Contrib.JEN.util import TDL_display
   from Timba.Contrib.JEN.util import JEN_record

   if 0:
      print dir(__name__)

   # Make some nodes:
   ns = NodeScope()
   a = ns.a << Meq.Parm(array([[1,0.2],[-0.3,0.1]]))
   b = ns.b << Meq.Parm(array([[1,-0.2],[0.3,0.1]]))
   c = ns.c << Meq.Parm(array([[6,-0.2],[0.3,0.1]]))
   sumab = ns << Meq.Add (a, b)

      
   if 0:
       # Make bookmark for a single node:
       create (a, page=None, folder='folder_1', trace=True)
       create (a, page='page_1', folder='folder_1', trace=True)
       create (b, page='page_2', folder='folder_1', trace=True)
       create (c, page='page_2', folder='folder_1', trace=True)
       create (b, page=None, folder=None, trace=True)
       create (a, page='page_2', folder=None, trace=True)
       create (b, page='page_2', folder=None, trace=True)
       create (c, page='page_2', folder=None, trace=True)
       create (c, page='page_2', folder='folder_2', trace=True)
       create (c, page='page_2', folder='folder_1', trace=True)

   if 1:
       # List of nodes:
       cc = [a,b,c,a,b,c,a,b,c]
       create (cc, perpage=2, trace=True)

   if 1:
       current_settings(trace=True)

   print '\n** End of local test of: JEN_bookmarks.py \n*************\n'

#********************************************************************************
#********************************************************************************






