# TDL_display.py:
#
# Author: J.E.Noordam
#
# Short description:
#    Some useful TDL-related display functions 
#
# History:
#    - 04 dec 2005: creation
#
# Full description:
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

# The following bit still requires a bit of thought.....
from Timba import utils
_dbg = utils.verbosity(0, name='tutorial')
_dprint = _dbg.dprint                         # use: _dprint(2, "abc")
_dprintf = _dbg.dprintf                       # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed

from Timba.Trees import JEN_record
from copy import deepcopy




#----------------------------------------------------------------------------------
# Recursively display the subtree underneath a NodeStub object (node):
#----------------------------------------------------------------------------------

def subtree (node, txt='<txt>', level=0, cindex=0, recurse=1000, count={}, full=0):
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
      if full: print '       (see above)'

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
               if not full: c5 = stepchild.name[0:5]
               subtree (stepchild, level=level+1, cindex=cindex,
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
               if not full: c5 = child.name[0:5]
               subtree (child, level=level+1, cindex=cindex,
                        recurse=recurse-1, count=count, full=full)
            count[inhibited] += inhibit
          

   # Finished (outer level):
   if level==0:
      print '** Some subtree statistics:'
      for klass in count[klasses].keys():
         print '**   class:',klass,':',count[klasses][klass]
      print '** Total nr of nodes scanned:',count[total]
      if count[inhibited]>0:
         print '** Further recursion inhibited for: ',count[inhibited],'children and/or stepchildren'
      print

   return True


#--------------------------------------------------------------------------------
# Display the given nodescope (ns):
#--------------------------------------------------------------------------------

def nodescope (ns, txt='<txt>', trace=1):
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
   JEN_record.display_object (ns.AllNodes(), 'ns.AllNodes()')
   print '** - ns.AllNodes() : ',type(ns.AllNodes()),'[',len(ns.AllNodes()),']'
   print '** - ns.Repository() : ',type(ns.Repository()),'[',len(ns.Repository()),']'
   print '** - ns.RootNodes() : ',type(ns.RootNodes()),'[',len(ns.RootNodes()),']'
   print '** - ns.RootNodes() -> ',ns.RootNodes()
   JEN_record.display_object (ns.RootNodes(), 'ns.RootNodes()')
   root = ns.RootNodes()
   for key in root.keys(): subtree (root[key],'root['+key+']', full=False)
      
   print '**'
   print '** - ns.__doc__ -> ',ns.__doc__
   print '*** End of NodeScope ()\n'
   return



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n****************\n** Local test of: TDL_display.py :\n'

   ns = NodeScope()

   if 1:
      p1 = ns << Meq.Parm(9)
      c1 = ns << Meq.Constant(9)
      root = ns << Meq.Add(p1,c1)

   if 1:
      nodescope(ns)

   if 1:
      subtree(root, full=True)

      
   print '\n** End of local test of: TDL_display.py \n*************\n'

#********************************************************************************



