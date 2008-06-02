
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
#   - AGW: Middle-clicking a node in the browser could display its quickref_help
#     (field in the state record) just like right-click option in the various plotter(s)....
#     The quickref_help is in the form of a record.
#     Tony already has a popup uption for selecting from multiple vellsets,
#     which includes an expansion tree. The quickref_help popup needs the same.
#   - AGW: Left-clicking a node displays the state record, except the Composer...
#         It would be nice if it were easier to invoke the relevant plotter...
#         (at this moment it takes to many actions, and the new display is confusing)
#   - OMS:Can we plot the result of each request in a sequence while it is running....?
#         (this problem may have been solved....)
#
#   - OMS: TDLCompileMenu should have tick-box option (just like the TDLOption)
#     Or should I read the manual better?
#   - OMS: Meow.Bookmarks needs a folder option....
#   - Is there a way to attach fields like a quickref_help record to the
#     state record (initrec?) of an existing node?
#   - AGW: Right-click plotting in Log scale does not work if 1D data
#     (it only produces a colorbar...)
#     NB: it is only offered as an option when doing 1D after 2D...
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

import copy
import math
import time
# import random


#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

# NB: This QuickRef menu is included automatically in the menus of the QR_... modules,
#     since they import this QuickRef module for its functions....

TDLCompileMenu("QuickRef Categories:",
               TDLOption('opt_general',"general MeqTree",False),
               TDLOption('opt_MeqBrowser',"MeqBrowser features",False),
               TDLOption('opt_MeqNodes',"Available MeqNodes",True),
               TDLOption('opt_pynodes',"General PyNodes",False),
               # TDLCompileMenu('Submenu:',
               #                TDLOption('first_item','1',True),
               #                TDLOption('second_item','2',True)
               #                ),
               # TDLOption('opt_visualization',"JEN", False)
               )
  
#-------------------------------------------------------------------------------

def standard_child_nodes (ns):
   """Helper function to make some child nodes with standard names,
   to be used in the various nodes""" 
   bb = []
   bb.append(ns << Meq.Constant(2.3))
   bb.append(ns << 2.4)

   bb.append(ns.noise2 << Meq.GaussNoise(stddev=2.0))
   bb.append(ns.noise3 << Meq.GaussNoise(stddev=3.0))
   bb.append(ns.noise4 << Meq.GaussNoise(stddev=4.0))
   bb.append(ns.noise5 << Meq.GaussNoise(stddev=5.0))

   bb.append(ns.range2 << Meq.Constant(range(2)))
   bb.append(ns.range3 << Meq.Constant(range(3)))
   bb.append(ns.range4 << Meq.Constant(range(4)))
   bb.append(ns.range5 << Meq.Constant(range(5)))
   bb.append(ns.range9 << Meq.Constant(range(9)))

   bb.append(ns.x << Meq.Freq())
   bb.append(ns.y << Meq.Time())
   bb.append(ns.xy << Meq.Add(ns.x,ns.y))

   bb.append(ns.x2 << Meq.Pow2(ns.x))
   bb.append(ns.y2 << Meq.Pow2(ns.y))
   bb.append(ns.xy2 << Meq.Add(ns.x2,ns.y2))
   bb.append(ns.gaussian1D << Meq.Exp(ns << Meq.Negate(ns.x2)))
   bb.append(ns.gaussian2D << Meq.Exp(ns << Meq.Negate(ns.xy2)))

   bb.append(ns.nx << Meq.NElements(ns.x))
   bb.append(ns.ny << Meq.NElements(ns.y))
   bb.append(ns.nxy << Meq.NElements(ns.xy))

   bb.append(ns.cxx << Meq.ToComplex(ns.x,ns.x))
   bb.append(ns.cyy << Meq.ToComplex(ns.y,ns.y))
   bb.append(ns.cxy << Meq.ToComplex(ns.x,ns.y))
   bb.append(ns.cyx << Meq.ToComplex(ns.y,ns.x))

   bb.append(ns.f << Meq.Freq())
   bb.append(ns.t << Meq.Time())
   bb.append(ns.ft << Meq.Add(ns.f,ns.t))

   scn = ns['standard_child_nodes'] << Meq.Composer(children=bb)
   return scn

#-------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """
   The QuickRef module offers a quick reference to MeqTrees.
   When used in the meqbrowser, it generates example subtrees
   for user-selected categories, which can be executed (with
   user-defined request domains) to inspect the result.
   Lots of bookmarks are generated for easy inspection.
   In addition, the relevant section of the hierarchical
   help-string can be inspected at each level, by displaying
   any node in the tree with the Record Browser. Look for
   the field 'quickref_help'.
   QuickRef gets its information from an arbitrary number
   of contributing QR_... modules. These may be generated by
   any MeqTrees contributor, following a number of simple rules.
   (Look for instance at the module QR_MeqNodes.py)
   """

   trace = False
   # trace = True

   # Make some standard child-nodes with standard names
   # These are used in the various bundles below.
   # They are bundles to avoid browser clutter.
   scnodes = standard_child_nodes(ns)

   if trace:
      print '\n** Start of QuickRef _define_forest()'

   # Make bundles of (bundles of) categories of nodes/subtrees:
   rootnodename = 'QuickRef'                # The name of the node to be executed...
   path = rootnodename                      # Root of the path-string
   global rider
   rider = CollatedHelpRecord()             # Helper class
   cc = []
   cc = [scnodes]
   if opt_MeqNodes:                         # specified in compile-options
      import QR_MeqNodes                    # import the relevant module
      cc.append(QR_MeqNodes.MeqNodes(ns, path, rider=rider))

   # Make the outer bundle (of node bundles):
   bundle_help = _define_forest.__doc__     # use module help...?
   bundle (ns, path, nodes=cc, help=bundle_help, rider=rider)

   if trace:
      rider.show('_define_forest()')

   # Finished:
   if trace:
      print '** end of QuickRef _define_forest()/n'
   return True
   


#********************************************************************************
# Forest exection functions (also used externally from QR_... modules):
#********************************************************************************

# NB: This QuickRef menu is included automatically in the menus of the QR_... modules,
#     since they import this QuickRef module for its functions....

TDLRuntimeMenu("Parameters of the Request domain(s):",
               TDLOption('runopt_nfreq',"nr of cells in freq direction",
                         [20,21,50,100,1000], more=int),
               TDLOption('runopt_fmin',"min freq (domain edge)",
                         [0.1,0.001,1.0,0.0,-math.pi,100.0,1e8,1.4e9], more=float),
               TDLOption('runopt_fmax',"max freq (domain edge)",
                         [2.0,math.pi,2*math.pi,100.0,2e8,1.5e9], more=float),
               TDLOption('runopt_separator',"",['']),
               TDLOption('runopt_ntime',"nr of cells in time direction",
                         [3,1,2,4,5,10,11,100,1000], more=int),
               TDLOption('runopt_tmin',"min time (domain edge)",
                         [0.0,1.0,-1.0,-10.0], more=float),
               TDLOption('runopt_tmax',"max time (domain edge)",
                         [2.0,10.0,100.0,1000.0], more=float),
               TDLOption('runopt_separator',"",['']),
               TDLOption('runopt_seq_ntime',"nr of steps in time-sequence",
                         [1,2,3,5,10], more=int),
               TDLOption('runopt_seq_tstep',"time-step (fraction of domain)",
                         [0.5,0.1,0.9,1.0,2.0,10.0,-0.5,-1.0], more=float),
               TDLOption('runopt_separator',"",['']),
               TDLOption('runopt_seq_nfreq',"nr of steps in freq-sequence",
                         [1,2,3,5,10], more=int),
               TDLOption('runopt_seq_fstep',"freq-step (fraction of domain)",
                         [0.5,0.1,0.9,1.0,math.pi,2*math.pi,-0.5,-1.0], more=float),
               TDLOption('runopt_separator',"",['']),
               )

#----------------------------------------------------------------------------

request_counter = 0
def make_request (cells, rqtype=None):
   """Make a request"""
   global request_counter
   request_counter += 1
   rqid = meq.requestid(request_counter)
   if isinstance(rqtype,str):
      # e.g. rqtype='ev' (for sequences, when the domain has changed)....
      return meq.request(cells, rqtype=rqtype)
      # return meq.request(cells, rqtype=rqtype, rqid=rqid)
   else:
      return meq.request(cells, rqid=rqid)

#----------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent, rootnode='QuickRef'):
   """Execute the forest with a 1D (freq) domain.
   """
   domain = meq.domain(runopt_fmin,runopt_fmax,
                       runopt_tmin,runopt_tmax)       
   cells = meq.cells(domain, num_freq=runopt_nfreq, num_time=1)
   request = make_request(cells)
   result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
   return result

#----------------------------------------------------------------------------

def _tdl_job_execute_2D (mqs, parent, rootnode='QuickRef'):
   """Execute the forest with a 2D domain.
   """
   domain = meq.domain(runopt_fmin,runopt_fmax,
                       runopt_tmin,runopt_tmax)       
   cells = meq.cells(domain, num_freq=runopt_nfreq, num_time=runopt_ntime)
   request = make_request(cells)
   result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
   return result

#----------------------------------------------------------------------------

def _tdl_job_execute_sequence (mqs, parent, rootnode='QuickRef'):
   """Execute a sequence, moving the 2D domain.
   """
   for ifreq in range(runopt_seq_nfreq):
      foffset = (runopt_fmax - runopt_fmin)*ifreq*runopt_seq_fstep
      print '** ifreq =',ifreq,' foffset =',foffset
      for itime in range(runopt_seq_ntime):
         toffset = (runopt_tmax - runopt_tmin)*itime*runopt_seq_tstep
         print '   - itime =',itime,' toffset =',toffset
         domain = meq.domain(runopt_fmin+foffset,runopt_fmax+foffset,
                             runopt_tmin+toffset,runopt_tmax+toffset)       
         cells = meq.cells(domain, num_freq=runopt_nfreq, num_time=runopt_ntime)
         request = make_request(cells)
         result = mqs.meq('Node.Execute',record(name=rootnode, request=request))
         # NB: It executes the entire sequence before showing any plots!
         # The things I have tried to make it display each result:
         # request = make_request(cells, rqtype='ev')
         # result = mqs.meq('Node.Execute',record(name='QuickRef', request=request), wait=True)
         # time.sleep(1)
   return result

#----------------------------------------------------------------------------

def _tdl_job_print_doc (mqs, parent, rr=None, header='QuickRef'):
   if rr==None:
      rr = rider             # i.e. the CollatedHelpObject
   print rr.format()
   return True

def _tdl_job_popup_doc (mqs, parent, rr=None, header='QuickRef'):
   if rr==None:
      rr = rider             # i.e. the CollatedHelpObject
   print '\n** popup doc not yet implemented **\n'
   return True

def _tdl_job_save_doc (mqs, parent, rr=None, filename='QuickRef'):
   if rr==None:
      rr = rider             # i.e. the CollatedHelpObject
   rr.save(filename)
   return True








#================================================================================
# Helper functions (called externally from QR_... modules):
#================================================================================


def add2path (path, name=None, trace=False):
   """Helper function to form the path to a specific bundle.
   NB: This function is called from all QR_... modules!
   """
   s = str(path)
   if isinstance(name,str):
      s += '.'+str(name)
   if trace:
      print '\n** QR.add2path(',path,name,') ->',s
   return s

#-------------------------------------------------------------------------------

def MeqNode (ns, path,
             meqclass=None, name=None,
             # quals=None, kwquals=None,
             node=None, children=None, unop=None,
             help=None, rider=None,
             trace=False, **kwargs):
   """Define (make) the specified node an an organised way.
   NB: This function is called from all QR_... modules!
   """

   # First replace the dots(.) in the node-name (name): They cause trouble
   # in the browser (and elsewhere?)
   qname = str(name)
   qname = qname.replace('.',',')

   # Condition the help-string: prepend the node name, and make a list of lines:
   if isinstance(help, str):
      # May be multi-line (in triple-quotes, or containing \n): 
      qhelp = help.split('\n')                            # -> list
      qhelp[0] = str(qname)+': '+str(qhelp[0])            # prepend
   else:                                                  # should not happen...?
      qhelp = str(qname)+': '+str(help)                   # ...show something...

   # Dispose of the conditioned help (qhelp):
   kwargs['quickref_help'] = qhelp                        # -> node state record
   if rider:
      # The rider is a CollatedHelpRecord object, which collects the
      # hierarchical help items, using the path string:
      rider.add(add2path(path,name), qhelp) 

   # Optionally, apply a one or more unary math operations (e.g. Abs)
   # on all the children (if any):
   if unop:
      if isinstance(unop,str):
         unop = [unop]
      if isinstance(unop,(list,tuple)): 
         for unop1 in unop:
            if isinstance(children,(list,tuple)):
               for i,child in enumerate(children):
                  children[i] = ns << getattr(Meq, unop1)(child)
            elif is_node(children):
               children = ns << getattr(Meq, unop1)(children)


   # Make the specified node:
   if is_node(node):
      # The node already exists. Just attach the help-string....
      # node = ns << Meq.Identity(node, quickref_help=qhelp)         # confusing...
      # NB: Is there a way to attach it to the existing node itself...?
      # node.initrec.quickref_help = qhelp               # causes error....
      pass
      
   elif isinstance(children,(list,tuple)):              
      if isinstance(name,str):
         stub = uniquestub(ns, name)
         node = stub << getattr(Meq,meqclass)(*children, **kwargs)
      else:
         node = ns << getattr(Meq,meqclass)(*children, **kwargs)

   elif is_node(children):
      child = children
      if isinstance(name,str):
         stub = uniquestub(ns, name)
         node = stub << getattr(Meq,meqclass)(child, **kwargs)
      else:
         node = ns << getattr(Meq,meqclass)(child, **kwargs)

   else:                           
      if isinstance(name,str):
         stub = uniquestub(ns, name)
         node = stub << getattr(Meq,meqclass)(**kwargs)
      else:
         node = ns << getattr(Meq,meqclass)(**kwargs)


   if trace:
      nc = None
      if isinstance(children,(list,tuple)):
         nc = len(children)
      print '- QR.MeqNode():',path,meqclass,name,'(nc=',nc,') ->',str(node)
   return node


#-------------------------------------------------------------------------------

def bundle (ns, path,
            nodes=None, unop=None,
            help=None, rider=None,
            parentclass='Composer', result_index=0,
            bookmark=True, viewer="Result Plotter",
            trace=False):
   """Make a single parent node, with the given nodes as children.
   Make bookmarks if required, and collate the help-strings.
   NB: This function is called from all QR_... modules!
   """

   # The name of the bundle (node, page, folder) is the last
   # part of the path string, i.e. after the last dot ('.')
   ss = path.split('.')
   nss = len(ss)
   name = ss[nss-1]
   qname = name
   if nss>1:
      qname = '*'+str(nss-2)+'* '+ss[nss-2]+'_'+ss[nss-1]
      
   # Condition the help-string and update the CollatedHelpRecord (rider):
   if isinstance(help, str):
      qhelp = help.split('\n')
      qhelp[0] = qname+': '+qhelp[0]
   else:
      qhelp = qname+': '+str(help)
      
   if rider:
      rider.add(path, qhelp)                    # add qhelp to the rest
      # The relevant subset of help is attached to this bundle node:
      qhelp = rider.subrec(path, trace=trace)   # get (a copy of) the relevant sub-record 
      qhelp = rider.cleanup(qhelp)              # clean it up (remove order fields etc) 

   # Optionally, apply a one or more unary math operations (e.g. Abs)
   # on all the nodes to be bundled:
   if unop:
      if isinstance(unop,str):
         unop = [unop]
      if isinstance(unop,(list,tuple)):
         for unop1 in unop:
            for i,node in enumerate(nodes):
               nodes[i] = ns << getattr(Meq, unop1)(node)

   # OK, bundle the given nodes by making them children of the
   # specified parentclass:
   # First make a nodestub with an unique name
   parent = uniquestub(ns, name)
   
   if parentclass=='ReqSeq':
      if not isinstance(result_index,int):
         if result_index=='last':
            result_index = len(nodes)-1
         else:
            result_index = 0
      parent << Meq.ReqSeq(children=nodes,
                           result_index=result_index,
                           quickref_help=qhelp)

   elif parentclass in ['Add','Multiply']:
      parent << getattr(Meq,parentclass)(children=nodes,
                                         quickref_help=qhelp)
   else:
      plot_label = []
      for node in nodes:
         plot_label.append(node.name)
      parent << Meq.Composer(children=nodes,
                             plot_label=plot_label,
                             quickref_help=qhelp)

   # Make a meqbrowser bookmark for this bundle, if required:
   if bookmark:
      # By default, all nodes in the bundle will be bookmarked.
      # However, a different selection may be passed via the bookmark argument.
      if is_node(bookmark):
         nodes = [bookmark]
      elif isinstance(bookmark,(list,tuple)):
         nodes = bookmark

      # The rider object has a service for extracting page and folder from path.
      [page, folder] = rider.bookmark(path, trace=trace)

      if folder or page:
         if True:
            # Temporary, until Meow folder problem (?) is solved....
            # JEN_bookmarks.create(nodes, name, page=page, folder=folder, viewer=viewer)
            JEN_bookmarks.create(nodes, name=page, folder=folder, viewer=viewer)
         else:
            # NB: There does not seem to be a Meow way to assign a folder....
            bookpage = Meow.Bookmarks.Page(name, folder=bookfolder)
            for node in nodes:
               bookpage.add(node, viewer=viewer)

   if trace:
      print '** QR.bundle():',path,name,'->',str(parent),'\n'
   return parent




#====================================================================================
# Functions for (unique) nodename generation:
#====================================================================================

def nodename (ns, rootname, *quals, **kwquals):
   """
   Helper function that forms a nodename from the given rootname and
   list (*) and keyword (**) qualifiers.
   """
   stub = nodestub (ns, rootname, *quals, **kwquals)
   return stub.name

#-------------------------------------------------------------------------

def uniquename (ns, rootname, *quals, **kwquals):
   """
   Helper function that forms a unique nodename from the given rootname and
   list (*) and keyword (**) qualifiers.
   """
   stub = uniquestub (ns, rootname, *quals, **kwquals)
   return stub.name

#-------------------------------------------------------------------------

def nodestub (ns, rootname, *quals, **kwquals):
   """
   Helper function that forms a nodestub from the given rootname and
   list (*) and keyword (**) qualifiers.
   """
   stub = ns[rootname]
   if len(quals)>0:
      stub = stub(*quals)
   if len(kwquals)>0:
      stub = stub(**kwquals)

   if False:
      s = '** QR.nodestub('+str(rootname)+','+str(quals)+','+str(kwquals)+')'
      s += ' -> '+str(stub)
      print s
   return stub

#-------------------------------------------------------------------------

def uniquestub (ns, rootname, *quals, **kwquals):
   """Helper function that forms a unique (i.e. uninitialized) nodestub
   from the given information.
   NB: Checking whether the proposed node has already been initialized
   in the given nodescope (ns) may be not an entirely safe method,
   when using unqualified nodes....
   """
   # First make a nodestub:
   stub = nodestub(ns, rootname, *quals, **kwquals)

   # Decode the uniquifying parameter (see below):
   ss = rootname.split('|')
   n = 0
   nameroot = rootname
   if len(ss)==3:                       # assume: <nameroot>|<n>|
      n = int(ss[1])
      nameroot = ss[0]

   # Safety valve:
   if n>100:
      print s1
      raise ValueError,'** max of uniqueness parameter exceeded'

   # Testing:
   if False:
      if n<3:
         stub << n               
      s = (n*'--')+' initialized: '
      s += ' '+str(stub.initialized())            # the correct way
      s += ' '+str(ns[stub].initialized())        # .....?
      s += ' '+str(ns[stub.name].initialized())   # .....
      print s

   # Check whether the node already exists (i.e. initialized...):
   if stub.initialized():
      # Recursive: Try again with a modified rootname.
      # (using the incremented uniquifying parameter n)
      newname = nameroot+'|'+str(n+1)+'|'
      return uniquestub(ns, newname, *quals, **kwquals)

   # Return the unique (!) nodestub:
   return stub
   


#=================================================================================
# Helper Class, to be used as rider:
#=================================================================================

class CollatedHelpRecord (object):
   """This object collects and handles the hierarchical set of QuickRef help strings
   into a record. This is controlled by the path, e.g. 'QuickRef.MeqNodes.unops'
   It is used in the functions .MeqNode() and .bundle() in this module, but has
   to be passed (as rider) through all contributing QR_... modules.
   """

   def __init__(self):
      self.clear()
      return None

   def clear (self):
      self._chrec = record(help=None, order=[])
      self._folder = record()
      return None

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

   def show(self, txt=None, rr=None, full=False, key=None, level=0):
      """Show the record (recursive)"""
      if level==0:
         print '\n** CollatedHelpRecord.show(',txt,' full=',full,' rr=',type(rr),'):'
         if rr==None:
            rr = self._chrec
      prefix = self.prefix(level)

      if not rr.has_key('order'):                # has no 'order' key
         for key in rr.keys():
            if isinstance(rr[key], (list,tuple)):
               if len(rr[key])>1:
                  print prefix,key,':',rr[key][0]
                  for s in rr[key][1:]:
                     print prefix,len(key)*' ',s
               else:
                  print prefix,key,':',rr[key]
            else:
               print prefix,key,'(no order):',type(rr[key])

      else:                                      # has 'order' key
         for key in rr.keys():
            if isinstance(rr[key], (list,tuple)):
               if key in ['order']:              # ignore 'order'
                  if full:
                     print prefix,key,':',rr[key]
               elif len(rr[key])>1:
                  print prefix,key,':',rr[key][0]
                  for s in rr[key][1:]:
                     print prefix,len(key)*' ',s
               else:
                  print prefix,key,'(',len(rr[key]),'):',rr[key]
            elif not isinstance(rr[key], (dict,Timba.dmi.record)):
               print prefix,key,'(',type(rr[key]),'??):',rr[key]
               
         for key in rr['order']:
            if isinstance(rr[key], (dict,Timba.dmi.record)):
               self.show(rr=rr[key], key=key, level=level+1, full=full) 
            else:
               print prefix,key,'(',type(rr[key]),'??):',rr[key]

      if level==0:
         print '**\n'
      return None


   #---------------------------------------------------------------------

   def format(self, rr=None, ss=None, key=None, level=0, trace=False):
      """
      Recursively format a help-string, to be printed.
      """
      if level==0:
         ss = '\n'
         if rr==None:
            rr = self._chrec
         if trace:
            print '\n** Start of .format():'
            
      prefix = '\n'+self.prefix(level)

      # First attach the overall help, if available:
      if rr.has_key('help'):
         help = rr['help']
         if isinstance(help, str):
            ss += prefix+str(help)
         elif isinstance(help, (list,tuple)):
            ss += prefix+str(help[0])
            if len(help)>1:
               s1 = str(len(str(key))*' ')
               for s in help[1:]:
                  ss += prefix+s1+str(s)

      # Then recurse in the proper order, if possible:
      keys = rr.keys()
      if rr.has_key('order'):                # has no 'order' key
         keys = rr['order']
      for key in keys:
         if isinstance(rr[key], (dict,Timba.dmi.record)):
            ss = self.format(rr=rr[key], ss=ss, key=key,
                             level=level+1, trace=trace) 
      # Finished:
      if len(keys)>1:
         ss += prefix
      if level==0:
         ss += '**\n'
         if trace:
            print '\n** End of .format():\n'
            print ss
      return ss

   #---------------------------------------------------------------------

   def save (self, rr=None, filename='CollatedHelpString'):
      """Save the formatted help-string in the specified file"""
      if not '.' in filename:
         filename += '.meqdoc'
      file = open (filename,'w')
      ss = self.format()
      file.writelines(ss)
      file.close()
      print '\n** Saved the doc string in file: ',filename,'**\n'
      return filename
      

   #---------------------------------------------------------------------

   def subrec(self, path, rr=None, trace=False):
      """Extract (a deep copy of) the specified (path) subrecord
      from the given record (if not specified, use self._chrec)
      """
      if trace:
         print '\n** .extract(',path,' rr=',type(rr),'):'

      if rr==None:
         rr = copy.deepcopy(self._chrec)
      else:
         rr = copy.deepcopy(rr)

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

   def cleanup (self, rr=None, level=0, trace=False):
      """Clean up the given record (rr)"""
      if level==0:
         if trace:
            print '\n** .cleanup(rr=',type(rr),'):'
         if rr==None:
            rr = self._chrec
            
      if isinstance(rr, dict):
         if rr.has_key('order'):
            rr.__delitem__('order')                   # remove the order field
            for key in rr.keys():
               if isinstance(rr[key], dict):          # recursive
                  rr[key] = self.cleanup(rr=rr[key], level=level+1)
      # Finished:
      if level==0:
         if trace:
            print '** finished .cleanup() -> rr=',type(rr)
      return rr

   #---------------------------------------------------------------------

   def bookmark (self, path, trace=False):
      """A little service to determine [page,folder] from path.
      It is part of this class because it initializes each time.
      This is necessary to avoid extra pages/folders.
      """
      # trace = True
      ss = path.split('.')
      nss = len(ss)

      page = None
      page = ss[nss-1]                          # the last one, always there
      if nss>1:
         page = ss[nss-2]+'_'+ss[nss-1]

      folder = None
      if len(ss)>3:
         folder = ss[nss-3]+'_'+ss[nss-2]       # same format as page above (essential!)

      if folder:
         self._folder.setdefault(folder,0)
         self._folder[folder] += 1
      elif page and self._folder.has_key(page):
         folder = page                          # works well for ...regridding_modres....
         self._folder[folder] += 1              # ....?
         page = None                            # produces 'autopage' pages in the folder
         page = '..dummy..'                     # still there, clean up later

      # Finished:
      if trace:
         print '*** .bookmark():',len(ss),ss,' page=',page,' folder=',folder
      return [page,folder]







#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QuickRef.py:\n' 
   ns = NodeScope()

   if 1:
      rider = CollatedHelpRecord()

   if 0:
      path = 'aa.bb.cc.dd'
      help = 'xxx'
      rider.add(path=path, help=help, trace=True)

   if 1:
      import QR_MeqNodes
      QR_MeqNodes.MeqNodes(ns, 'test', rider=rider)
      # rider.show('testing', full=True)
      # print rider.format()

      if 1:
         path = 'test.MeqNodes.binops'
         # path = 'test.MeqNodes'
         rr = rider.subrec(path, trace=True)
         rider.show('subrec('+path+')',rr, full=False)
         rider.show('subrec('+path+')',rr, full=True)
         rider.format(rr, trace=True)

         if 0:
            print 'before cleanup(): ',type(rr)
            rr = rider.cleanup(rr=rr)
            print 'after cleanup(): ',type(rr)
            # The order fields should now have disappeared: (no order)
            rider.show('after cleanup',rr, full=True)
            # Finally, test whether the original self._chrec still has order fields:
            # rider.show('self._chrec after cleanup', full=True)
            
   if 0:
      stub = nodestub(ns,'xxx',5,-7,c=8,h=9)
      print '\n nodestub() ->',str(stub),type(stub)
      stub << 5.6
      stub = uniquestub(ns,'xxx',5,-7,c=8,h=9)
      print '\n uniquestub() ->',str(stub),type(stub)
      if 0:
         if 1:
            print '\n dir(stub):',dir(stub),'\n'
         print '- stub.name:',stub.name
         print '- stub.basename:',stub.basename
         print '- stub.classname:',stub.classname
         print '- stub.quals:',stub.quals
         print '- stub.kwquals:',stub.kwquals
         print '- stub.initialized():',stub.initialized()
      if 0:
         node = stub << 3.4
         print '\n node = stub << 3.4   ->',str(node),type(node)
         if 1:
            print '\n dir(node):',dir(node),'\n'
         print '- node.name:',node.name
         print '- node.basename:',node.basename
         print '- node.classname:',node.classname
         print '- node.quals:',node.quals
         print '- node.kwquals:',node.kwquals
         print '- node.initialized():',node.initialized()

      if 1:
         print '.nodename() ->',nodename(ns,'xxx',5,-7,c=8,h=9)
         print '.uniquename() ->',uniquename(ns,'xxx',5,-7,c=8,h=9)

   print '\n** End of standalone test of: QuickRef.py:\n' 

#=====================================================================================



