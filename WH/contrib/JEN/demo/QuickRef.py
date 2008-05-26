
# file: ../JEN/demo/QuickRef.py:
#
# Author: J.E.Noordam
#
# Short description:
#    A quick reference to all MeqTree nodes and subtrees.
#    It makes actual nodes, and prints help etc

#
# History:
#   - 23 may 2008: creation
#
# Remarks:
#
#   - Meow.Bookmarks needs a folder option....
#   - Middle-clicking a node in the browser should display its quickref_help
#   - NB: Left-clicking a node displays the state record, except the Composer...
#         It would be nice if it were easier to invoke the relevant plotter...
#         (at this moment it takes to many actions, and the new display is confusing)
#   - TDLCompileMenu should have tick-box option.....
#   - Is there a way to attach fields like quickref_help to existing nodes?
#
# Description:
#


 
#********************************************************************************
# Initialisation:
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

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks

import math
# import random


#********************************************************************************
# The function under the 'blue button':
#********************************************************************************


TDLCompileMenu("Categories:",
               TDLOption('opt_MeqNodes',"Standard MeqNodes",True),
               TDLOption('opt_pynodes',"General PyNodes",False),
               TDLCompileMenu('Submenu:',
                              TDLOption('first_item','1',True),
                              TDLOption('second_item','2',True)
                              ),
               TDLOption('opt_visualization',"JEN", False)
               )
  
#-------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Make some standard child-nodes with standard names
   # These are used in the various bundles below.
   # They are bundles to avoid browser clutter.
   bb = []
   bb.append(ns << Meq.Constant(2.3))
   bb.append(ns << 2.4)
   bb.append(ns.x << Meq.Freq())
   bb.append(ns.y << Meq.Time())
   bb.append(ns.cxy << Meq.ToComplex(ns.x,ns.y))
   bb.append(ns.cyx << Meq.ToComplex(ns.y,ns.x))
   bb.append(ns.f << Meq.Freq())
   bb.append(ns.t << Meq.Time())
   bb.append(ns.ft << Meq.Multiply(ns.f,ns.t))
   bb.append(ns['f+t'] << Meq.Add(ns.f,ns.t))
   unc = ns['unclutter'] << Meq.Composer(children=bb)

   trace = True
   print '\n** Start of QuickRef _define_forest()'

   # Make bundles of (bundles of) categories of nodes/subtrees:
   cc = []
   cc = [unc]
   path = 'QuickRef'           # NB: This is also the name of the node to be executed...
   CHR = CollatedHelpRecord()
   if opt_MeqNodes:
      import QR_MeqNodes
      cc.append(QR_MeqNodes.MeqNodes(ns, path, chr=CHR))

   # Make the outer bundle (of node bundles):
   help = """help"""
   bundle (ns, path, nodes=cc, help=help, chr=CHR)
   CHR.show()

   TDLRuntimeMenu("parameters of the requested domain:",
                  TDLOption('runopt_nfreq',"nr of freq cells",
                            [20,21,50,1], more=int),
                  TDLOption('runopt_fmin',"min freq (edge)",
                            [0.1,1.0,3.0,0.01,0.0,-1.0,-math.pi,-2*math.pi,100e6,1400e6], more=float),
                  TDLOption('runopt_fmax',"max freq (edge)",
                            [2.0,1.0,math.pi,2*math.pi,110e6,200e6,1500e6], more=float),
                  TDLOption('runopt_ntime',"nr of time cells",
                            [1,20,21,50], more=int),
                  TDLOption('runopt_tmin',"min time (edge)",
                            [0.0,-1.0,-10.0], more=float),
                  TDLOption('runopt_tmax',"max time (edge)",
                            [1.0,0.1,3.0,10.0,100.0,1000.0], more=float),
                  )

   # Finished:
   print '** end of QuickRef _define_forest()/n'
   return True
   





#================================================================================
# Helper functions (called externally from QR_... modules):
#================================================================================


def MeqNode (ns, path,
             meqclass=None, name=None,
             # quals=None, kwquals=None,
             children=None, help=None, chr=None,
             node=None,
             trace=False, **kwargs):
   """Define the specified node an an organised way."""

   # Condition the help-string and update the CollatedHelpRecord (chr):
   qhelp = quickref_help(name, help)
   if chr:
      chr.add(add2path(path,name), qhelp)


   if is_node(node):
      # The node already exists. Just attach the help-string....
      # NB: Is there a way to attach it to the existing node itself...?
      node = ns << Meq.Identity(node, quickref_help=qhelp)
      
   elif not isinstance(children,(list,tuple)):           # No children specified: 
      if isinstance(name,str):
         node = ns[name] << getattr(Meq,meqclass)(quickref_help=qhelp, **kwargs)
      else:
         node = ns << getattr(Meq,meqclass)(quickref_help=qhelp, **kwargs)

   else:                          
      if isinstance(name,str):
         node = ns[name] << getattr(Meq,meqclass)(children=children,
                                                  quickref_help=qhelp,
                                                  **kwargs)
      else:
         node = ns << getattr(Meq,meqclass)(children=children,
                                            quickref_help=qhelp,
                                            **kwargs)
   if trace:
      nc = None
      if isinstance(children,(list,tuple)):
         nc = len(children)
      print '- QR.MeqNode():',path,meqclass,name,'(nc=',nc,') ->',str(node)
   return node


#-------------------------------------------------------------------------------

def bundle (ns, path,
            nodes=None, help=None, chr=None,
            page=False, folder=True, viewer="Result Plotter",
            trace=False):
   """Make a single parent node, with the given nodes as children.
   Make bookmarks if required, and collate the help-strings.
   """

   # The name of the bundle (node, page, folder) is the last
   # part of the path string, i.e. after the last dot ('.')
   ss = path.split('.')
   name = ss[len(ss)-1]
   if folder:
      folder = name
   # level = len(ss)

   # Condition the help-string and update the CollatedHelpRecord (chr):
   qhelp = quickref_help(name, help)
   if chr:
      chr.add(path, qhelp)
      qhelp = chr.subrec(path, trace=True)
      qhelp = chr.cleanup(qhelp)


   if True:
      # NB: When a Composer node is left-clicked in the browser,
      # it plots an inspector, not its state record (with help...)   
      parent = ns[name] << Meq.Composer(children=nodes,
                                        quickref_help=qhelp)
   else:
      # Alternative: ReqSeq?
      parent = ns[name] << Meq.Add(children=nodes,
                                   quickref_help=qhelp)

   # Make a meqbrowser bookmark for this bundle, if required:
   if folder or page:
      if True:
         # Temporary, until Meow folder problem (?) is solved....
         JEN_bookmarks.create(nodes, name, page=page, folder=folder,
                              viewer=viewer)
      else:
         # NB: There does not seem to be a Meow way to assign a folder....
         bookpage = Meow.Bookmarks.Page(name, folder=bookfolder)
         for node in nodes:
            bookpage.add(node, viewer=viewer)

   if trace:
      print '** QR.bundle():',path,name,'->',str(parent),'\n'
   return parent


#--------------------------------------------------------------------------------

def prefix (level=0):
   """Used to indent"""
   prefix = (level*'**')+' '
   return prefix

#-------------------------------------------------------------------------------

def quickref_help (name, help, test=False):
   """Convert the help-string into a list of strings, by splitting it
   on the newline chars. This makes easier reading in the mewbrowser.
   If test==True, return another type of qhelp.
   """
   qhelp = str(help)
   if test:
      if False:
         qhelp = [range(2),range(3),[range(4),range(5),[range(6)]]]
      elif False:
         qhelp = record(a=record(text='a',
                                 d=record(text='c'),
                                 c=record(text='d')),
                        b=record(e=record(text='e'),
                                 text=quickref_help('\naa\nbb\ncc\n'),
                                 a=record(text='a')))
   elif isinstance(help,str):
      qhelp = help.split('\n')
      if isinstance(name, str):
         qhelp[0] = name+': '+qhelp[0]
   else:
      qhelp = str(help)
   return qhelp

#-------------------------------------------------------------------------------

def add2path (path, name=None, trace=False):
   """Helper function to form the path to a specific bundle."""
   s = str(path)
   if isinstance(name,str):
      s += '.'+str(name)
   if trace:
      print '\n** QR.add2path(',path,name,') ->',s
   return s

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------


class CollatedHelpRecord (object):

   def __init__(self):
      self.clear()
      return None

   def clear (self):
      self._chrec = record(help=None, order=[])
      return self._chrec

   def chrec (self):
      return self._chrec

   #---------------------------------------------------------------------

   def add (self, path=None, help=None, rr=None,
            level=0, trace=False):
      """Add a help-item (recursive)"""
      if level==0:
         rr = self._chrec
      if isinstance(path,str):
         path = path.split('.')

      key = path[0]
      if not rr.has_key(key):
         rr.order.append(key)
         rr[key] = record(help=None)
         if len(path)>1:
            rr[key].order = []

      if len(path)>1:                        # recursive
         self.add(path=path[1:], help=help, rr=rr[key],
                  level=level+1, trace=trace)
      else:
         rr[key].help = help                 # may be list of strings...
         if trace:
            prefix = self.prefix(level)
            print '.add():',prefix,key,':',help
      # Finished:
      return None

   #---------------------------------------------------------------------
   
   def prefix (self, level=0):
      """Indentation string"""
      return ' '+(level*'..')+' '

   #---------------------------------------------------------------------

   def show(self, txt=None, rr=None, full=True, key=None, level=0):
      """Show the record (recursive)"""
      if level==0:
         print '\n** CollatedHelpRecord.show(',txt,' full=',full,' rr=',type(rr),'):'
         if rr==None:
            rr = self._chrec
      prefix = self.prefix(level)
      if not rr.has_key('order'):                # has no 'order' key
         for key in rr.keys():
            print prefix,key,':',rr[key]
      else:                                      # has 'order' key
         for key in rr.keys():
            if not isinstance(rr[key], dict):
               if full or (not key in ['order']):  # ignore 'order'
                  print prefix,key,':',rr[key]
            elif not key in rr['order']:         # should not happen
               print prefix,key,':','...record...??'
         for key in rr['order']:
            if isinstance(rr[key], dict):        # recursive 
               self.show(rr=rr[key], key=key, level=level+1, full=full) 
            else:                                # should not happen
               print prefix,key,':',rr[key],'..??..'

      if level==0:
         print '**\n'
      return None

   #---------------------------------------------------------------------

   def subrec(self, path, rr=None, trace=False):
      """Extract the specified (path) subrecord
      from the given record (if not specified, use self._chrec)
      """
      if trace:
         print '\n** .extract(',path,' rr=',type(rr),'):'
      if rr==None:
         rr = self._chrec

      ss = path.split('.')
      for key in ss:
         if trace:
            print '-',key,ss,rr.keys()
         if not rr.has_key(key):
            s = '** key='+key+' not found in: '+str(ss)
            raise ValueError,s
         else:
            rr = rr[key]
      if trace:
         self.show(txt=path, rr=rr)
      return rr
      
   #---------------------------------------------------------------------

   def cleanup (self, rr=None, level=0):
      """Clean up the given record (rr)"""
      if level==0:
         print '\n** .cleanup(rr=',type(rr),'):'
         if rr==None:
            rr = self._chrec
            
      if isinstance(rr, dict):
         if rr.has_key('order'):
            rr.__delitem__('order')
            for key in rr.keys():
               if isinstance(rr[key], dict):          # recursive
                  rr[key] = self.cleanup(rr=rr[key], level=level+1)
      # Finished:
      if level==0:
         print '** finished .cleanup() -> rr=',type(rr)
      return rr







#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute_1D_freq (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(runopt_fmin,runopt_fmax,
                        runopt_tmin,runopt_tmax)       
    cells = meq.cells(domain, num_freq=runopt_nfreq, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='QuickRef', request=request))
    return result

def _tdl_job_execute_2D (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(runopt_fmin,runopt_fmax,
                        runopt_tmin,runopt_tmax)       
    cells = meq.cells(domain, num_freq=runopt_nfreq, num_time=runopt_ntime)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='QuickRef', request=request))
    return result

if False:
   def _tdl_job_print_selected_help (mqs, parent):
      """Print the help-text of the selected categories"""
      print '\n** Not yet implemented **\n'
      return True

   def _tdl_job_popup_selected_help (mqs, parent):
      """Show the help-text of the selected categories"""
      print '\n** Not yet implemented **\n'
      return True



#********************************************************************************

#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QuickRef.py:\n' 
   ns = NodeScope()

   if 1:
      CHR = CollatedHelpRecord()

   if 0:
      path = 'aa.bb.cc.dd'
      help = 'xxx'
      CHR.add(path=path, help=help, trace=True)

   if 1:
      import QR_MeqNodes
      QR_MeqNodes.MeqNodes(ns, 'test', chr=CHR)
      CHR.show('testing')

      if 1:
         path = 'test.MeqNodes.binops'
         # path = 'test.MeqNodes'
         rr = CHR.subrec(path, trace=True)
         CHR.show('subrec',rr, full=False)
         CHR.show('subrec',rr, full=True)
         if 1:
            print 'before cleanup(): ',type(rr)
            rr = CHR.cleanup(rr=rr)
            print 'after cleanup(): ',type(rr)
            CHR.show('cleanup',rr, full=True)
            CHR.show('cleanup',rr, full=False)
            
         
   print '\n** End of standalone test of: QuickRef.py:\n' 

#=====================================================================================



