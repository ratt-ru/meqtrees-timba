# MG_JEN_forest_state.py

# Short description:
#   Some functions to deal with the forest state record

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation
# - 30 nov 2005: args ra0=0.0, dec0=1.0 to .create_MS_interface_nodes()
# - 05 jan 2006: moved bookmark functions to JEN_bookmarks.py
# - 21 mar 2006: removed bookmark functions
# - 21 mar 2006: disabled MS_interface functions

# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
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
from Timba.Meq import meq

# from Timba.Contrib.JEN.util import create_MS_interface_nodes
from Timba.Contrib.JEN.util import JEN_bookmarks

# from numarray import *
from string import *
from copy import deepcopy

#------------------------------------------------------------------
# Script control record (may be edited here):

MG = record(script_name='MG_JEN_forest_state.py',
            last_changed='h03oct2005')





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
   # bm = JEN_bookmarks.create (..., viewer='Record Browser')           # <-----??
 
   # Make bookmark for a single node:
   bm = JEN_bookmarks.create (a)
   bm = JEN_bookmarks.create (b)
 
   # Make a named page with views of the same node:
   page_name = 'b+'
   folder_name = 'ab'
   JEN_bookmarks.create (b, page=page_name, folder=folder_name)
   JEN_bookmarks.create (b, udi='funklet/coeff', viewer='Record Browser',
                         page=page_name, folder=folder_name)
 
   # Make a named page with views of diferent nodes:
   page_name = 'sum=a+b'
   folder_name = 'sumab'
   JEN_bookmarks.create (a, page=page_name, folder=folder_name)
   JEN_bookmarks.create (b, page=page_name, folder=folder_name)
   JEN_bookmarks.create (sum, page=page_name, folder=folder_name)
 
   # Make a named page with multiple views of the same node:
   page_name = 'views of sum'
   folder_name = 'sum_views'
   JEN_bookmarks.create (sum, page=page_name, folder=folder_name)
   JEN_bookmarks.create (sum, page=page_name, folder=folder_name, viewer='ParmFiddler')
   JEN_bookmarks.create (sum, page=page_name, folder=folder_name, viewer='Record Browser')
   JEN_bookmarks.create (sum, page=page_name, folder=folder_name, viewer='Executor')

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


def init (MG, mode='MeqGraft'):
   """Initialise the forest_state record (called by all MG_JEN_ scripts)"""

   # Deal with some legacy:
   if isinstance(MG, str): MG = record(script_name=MG)

   # Reset the jen-record (see .trace(), .error() etc below)
   Settings.forest_state['MG_JEN'] = record()

   # Reset the bookmarks (if not, the old ones are retained) 
   Settings.forest_state.bookmarks = []
   # JEN_bookmarks.current_settings(clear=True)         # alternative....
     
   # The default name for the .meqforest save file:
   s1 = split(MG['script_name'],'.')
   if isinstance(s1, (list, tuple)): s1 = s1[0]
   Settings.forest_state.savefile = s1

   if mode == 'MeqGraft':
      # Cache all node results:
      Settings.forest_state.cache_policy = 100
      # Orphan nodes should be retained:
      Settings.orphans_are_roots = True
   
   return 


# Execute this function:
init(MG)




#------------------------------------------------------------------------------- 
# Save the forest to a binary file(s):

def save_meqforest (mqs, **pp):
   """Save the current meqforest, using the filename in the forest_state record.
   If save_reference=True, also save the result for later testing."""

   pp.setdefault('filename', False)       
   pp.setdefault('save_reference', False)
   pp = record(pp)

   filename = pp['filename']
   if not isinstance(filename, str):
      filename = Settings.forest_state.savefile+'.meqforest'
   mqs.meq('Save.Forest',record(file_name=filename))

   # Optionally, store it in a reference-file, for auto-testing:
   if pp['save_reference']:
      mqs.meq('Save.Forest',record(file_name=filename+'_reference'))
      
   return filename



  



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

  if True:
     ss = 'MG_JEN_forest_state.object(',txt,'): inhibited'
  else:
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
  jenfield = 'MG_JEN'
  Settings.forest_state.setdefault(jenfield,record())
  Settings.forest_state[jenfield].setdefault(field,record())
  rr = Settings.forest_state[jenfield][field]
  level = kwitem.get('level',1)
  indent = level*'..'
  key = str(len(rr))
  rr[key] = kwitem

  Settings.forest_state[jenfield][field] = rr
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
   field = 'MG_JEN_counter'
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









#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Get/create the record of NAMES of the standard nodes that are expected by
# the function Timba.Contrib.JEN.util/read_MS_auxinfo.py.
# This record is kept in the forest state record (where else?) 
#-------------------------------------------------------------------------------

def MS_interface_nodes_obsolete(ns=None, ra0=0.0, dec0=0.0):
  """Get/create the standard MS interface nodes"""

  field = 'MS_interface_nodes'
  Settings.forest_state.setdefault(field,False)

  # Create if necessary (and if nodescope (ns) supplied):
  rr = Settings.forest_state[field]
  if isinstance(rr,bool) and ns:           
    rr = create_MS_interface_nodes.create_MS_interface_nodes(ns, ra0=ra0, dec0=dec0)
    Settings.forest_state[field] = rr

  # Return the current:
  return Settings.forest_state[field]

#---------------------------------------------------------
# Display them:

def display_MS_interface_nodes_obsolete(ns=None, rr=None, level=1):
   if level==1:
      rr = MS_interface_nodes(ns)
      print '\n*** Start of MS_interface_nodes:'
   for key in rr.keys():
      v = rr[key]
      if isinstance(v, str):
         print '_',level,key,v,':',ns[v]
      else:
         display_MS_interface_nodes(ns, v, level=level+1)
   if level==1:
      print '*** End of MS_interface_nodes ***\n'
   return True

#---------------------------------------------------------
# Make a page of bookmarks for its dcoll nodes:
# The show the array layout, etc

def bookpage_MS_interface_nodes_obsolete(ns):
   rr = MS_interface_nodes(ns)
   cc = []
   for key in rr.dcoll.keys():
      cc.append(ns[rr.dcoll[key]])
      JEN_bookmarks.create(ns[rr.dcoll[key]], page='array_configuration')
   # Return a list of dcoll nodes (to be made step-children)
   return cc














#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
   """Meqforest execution routine"""
   # Use a simple version of MG_JEN_exec.meqforest():
   cells = meq.cells(meq.domain(0,1,0,1),num_freq=6,num_time=4);
   # request = meq.request(cells,eval_mode=0)
   request = meq.request(cells, rqtype='ev')
   global _test_root
   mqs.meq('Node.Execute',record(name=_test_root, request=request));
   return


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

   # NB: Importing a module resets the forest_state record!!
   from Timba.Contrib.JEN import MG_JEN_exec

   # Use a simple version of MG_JEN_exec.without_meqserver():
   ns = NodeScope()
   root = _define_forest(ns)
   ns.Resolve()
   MG_JEN_exec.display_subtree(root, MG.script_name, full=1)
   MG_JEN_exec.display_object(Settings.forest_state, 'forest_state', MG.script_name)

   if 0:
      from Timba.Contrib.JEN.util import TDL_common
      sp = TDL_common.Super()
      ss = sp.display(MG.script_name)
      trace(ss, key=sp.label())
      
   if 0:
      from Timba.Contrib.JEN.util import TDL_Cohset
      cs = TDL_Cohset.Cohset()
      ss = cs.display(MG.script_name)
      trace(ss, key=cs.label())

   if 0:
      MG_JEN_exec.display_object(Settings.forest_state, 'forest_state', MG.script_name)

   if 0:
      print dir(__name__)
      
   print '\n** End of local test of:',MG.script_name,'\n*************\n'

#********************************************************************************
#********************************************************************************






