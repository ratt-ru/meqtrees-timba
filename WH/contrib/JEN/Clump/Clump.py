"""
Clump.py: Base-class for an entire zoo of derived classes that
represent 'clumps' of trees, i.e. sets of similar nodes.
Examples are ParmClump, JonesClump and VisClump.
"""

# file: ../JEN/Clump/Clump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 25 oct 2008: creation
#
# Description:
#
# Remarks:
#
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

from Timba.Contrib.JEN.control import TDLOptionManager as TOM

from Timba.Contrib.JEN.Easy import EasyNode as EN
from Timba.Contrib.JEN.Easy import EasyFormat as EF

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc

clump_counter = -1          # used in Clump.__init__()

#******************************************************************************** 

class Clump (object):
   """
   Base-class for an entire zoo of derived classes that
   represent 'clumps' of trees, i.e. sets of similar nodes.
   Examples are ParmClump, JonesClump and VisClump.
   """

   def __init__(self, name=None,
                qual=None, kwqual=None,
                treequals=None,
                ns=None, TCM=None,
                use=None, init=True,
                **kwargs):
      """
      Initialize the Clump object, according to its type (see .init()).
      If another Clump of the same class is specified (use), use its
      defining characteristics (self._treequals etc)
      """
      # Make a short version of the type name (e.g. Clump)
      self._typename = str(type(self)).split('.')[1].split("'")[0]

      # If another Clump object is given (use), use its contents
      if not isinstance(use,type(self)):
         use = None
      
      # The Clump node names are derived from name and qualifier:
      self._name = name       
      self._qual = qual  
      self._kwqual = kwqual
      self._kwargs = kwargs
      self._used = None
      if use:
         self._used = use.oneliner() 
         if not isinstance(name,str):          # name not specified
            self._name = '('+use._name+')'
         if qual==None:                        # qual not specified
            self._qual = use._qual
         if kwqual==None:                      # kwqual not specified
            self._kwqual = use._kwqual
      if not isinstance(self._name,str):
         self._name = self._typename           # e.g. 'Clump'    
         global clump_counter
         clump_counter += 1
         self._name += str(clump_counter)

      # The 'size' of the Clump is defined by the list of qualifiers:
      if use:
         self._treequals = use._treequals
      elif treequals==None:
         self._treequals = range(3)            # for testing
      elif isinstance(treequals,tuple):
         self._treequals = list(treequals)
      elif not isinstance(treequals,list):     # assume Clump of one
         self._treequals = [treequals]         #
      else:
         self._treequals = treequals           # just copy

      # Make sure that it has a nodescope (ns):
      self._ns = ns
      if use:
         self._ns = use._ns
      elif not ns:
         # If not supplied, make a local one.
         self._ns = NodeScope()

      # Make sure that it has an TDLOptionManager (TCM):
      self._TCM = TCM
      if use:
         self._TCM = use._TCM
      elif not self._TCM:
         # If not supplied, make a local one.
         self._TCM = TOM.TDLOptionManager(self._name)

      # Each Clump object has a special submenu, which is
      # started in .start_of_submenu(), which may be called
      # from .init() if that function defines any options,
      # or from another function (which one?)
      # In any case, any function that calls .start_of_submenu()
      # must end with: self._TCM.end_of_submenu()
      self._submenu = None   
      self._master = None
      if isinstance(kwargs,dict):
         if kwargs.has_key('master'):
            self._master = kwargs['master']

      # The nodes may be composed into a single tensor node.
      # In that case, the following qualifier will be used.
      # The list self._nodequals always has the same length as self._nodes.
      self._tensor_qual = 'tensor'+str(len(self._treequals))
      self._composed = False            # see .compose() and .decompose()
      self._nodequals = self._treequals     # self._nodequals is used for node generation

      # Initialize the object history:
      self.history(clear=True)

      # Finally: Initialize with suitable nodes (if required):
      # The function .init() is re-implemented in derived classes.
      # NB: See .copy() for an example where init=False.
      if init:
         self.init()

      return None

   #--------------------------------------------------------------------------

   def start_of_submenu(self, trace=False):
      """Convenience function to be called from .init().
      It generates the submenu that controls the object,
      in an organised way (this avoids errors when re-implementing
      .init() in derived classes.
      """
      self._submenu = self._TCM.start_of_submenu(self._name,
                                                 master=self._master,
                                                 qual=self._qual)
      return self._submenu

   #--------------------------------------------------------------------------

   def init (self, trace=False):
      """Initialize the object with suitable nodes.
      Called from __init__() only
      Place-holder: To be re-implemented for derived classes.
      """
      submenu = self.start_of_submenu()
      self._TCM.add_option('aa', range(1,4))
      self._TCM.add_option('bb', range(1,4))

      self._TCM.getopt('aa', submenu)
      self._TCM.getopt('bb', submenu)

      self._nodes = []
      stub = self.nodestub()
      for i,qual in enumerate(self._nodequals):
         node = stub(qual) << Meq.Constant(i)
         # print '  -',str(node)
         self._nodes.append(node)

      self.history('.init()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

   #-------------------------------------------------------------------------

   def commensurate(self, other, severe=False, trace=False):
      """Return True if the given (other) Clump is commensurate,
      i.e. it has the same self._nodequals (NOT self._treequals!)
      """
      cms = True
      if not self.size()==other.size():
         cms = False
      else:
         snq = self._nodequals
         onq = other._nodequals
         for i,qual in enumerate(snq):
            if not qual==onq[i]:
               cms = False
               break
      if not cms:
         s = '\n** '+self.oneliner()+'   ** NOT COMMENSURATE ** with:'
         s += '\n   '+other.oneliner()+'\n'
         if severe:
            raise ValueError,s
         if trace:
            print s
      return cms
         

   #=========================================================================
   # Copy operations (very important for building complex structures with Clumps)
   #=========================================================================

   def copy (self, name=None, qual=None, unop='Identity', trace=False):
      """
      Return a copy of this clump, with the same size, treequals, ns and TCM.
      If no name specified, derive a new name by enclosing self._name in brackets.
      The nodes are copied, possibly after applying a unary operation (unop) on them.
      (using unop=Identity, produces a 'deep' copy.....)
      NB: It does NOT matter whether the clump is 'composed' (i.e. one tensor node)
      """
      if not isinstance(name, str):
         name = 'copy('+self._name+')'

      # Create a new Clump of the same type:
      new = self.newinstance(name=name, qual=qual, init=False)

      # Copy the nodes, after optionally applying a unary operation on them:
      new._nodes = []
      stub = new.nodestub()
      for i,qual in enumerate(self._nodequals):
         node = self._nodes[i]
         if unop:
            node = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         new._nodes.append(node)

      new.history('copy(unop='+str(unop)+')', trace=trace)
      new.history('| copied from: '+self.oneliner(), trace=trace)
      return new

   #-------------------------------------------------------------------------

   def newinstance(self, name=None, qual=None, init=False):
      """Make a new instance of this class. Called by .copy().
      This function should be re-implemented in derived classes.
      """
      return Clump(name=name, qual=qual, use=self, init=init)

   #-------------------------------------------------------------------------

   def chain (self, name=None, qual=None, trace=False):
      """Version of .copy(), in which the nodes are just copied (unop=None).
      """
      return self.copy (name=name, qual=qual, unop=None, trace=trace)


   #==========================================================================
   # Various text display functions:
   #==========================================================================

   def oneliner (self):
      ss = self._typename+': '
      ss += ' '+str(self._name)
      if not self._qual==None:
         ss += ' qual='+str(self._qual)
      ss += '  size='+str(self.size())
      if self._master:
         ss += '  slaved'
      if self._composed:
         ss += '  (composed: '+self._tensor_qual+')'
      ss += '  treequals=['+str(self._treequals[0])+'..'+str(self._treequals[-1])+']'
      return ss

   #--------------------------------------------------------------------------

   def show (self, txt=None, full=True, doprint=True):
      """
      Format a summary of the contents of the object.
      If doprint=True, print it also.  
      """
      ss = '\n'
      ss += '\n** '+self.oneliner()
      if txt:
         ss += '   ('+str(txt)+')'
      ss += '\n * self._used: '+str(self._used)
      ss += '\n * self._kwqual: '+str(self._kwqual)
      ss += '\n * self._kwargs: '+str(self._kwargs)
      #.....................................................

      ss += '\n * nodes (.len()='+str(self.len())+', .size()='+str(self.size())+'):'
      n = len(self._nodes)
      if full:
         nmax = 2
         for i in range(min(nmax,n)):
            ss += '\n   - '+str(self._nodes[i])
         if n>nmax:
            if n>nmax+1:
               ss += '\n       ...'
            ss += '\n   - '+str(self._nodes[-1])
      else:
         ss += '\n   - node[0] = '+str(self._nodes[0])
         ss += '\n   - node[-1]= '+str(self._nodes[-1])
      #.....................................................

      nmax = 20
      qq = self._treequals
      ss += '\n * treequals(n='+str(len(qq))+'): '
      if len(qq)<=nmax:
         ss += str(qq)
      else:
         ss += str(qq[:nmax])+'...'+str(qq[-1])
      #.....................................................

      ss += '\n * self._ns: '+str(self._ns)
      if self._TCM:
         ss += '\n * self._TCM: '+str(self._TCM.oneliner())
      else:
         ss += '\n * self._TCM = '+str(self._TCM)
      ss += '\n * self._submenu = '+str(self._submenu)
      ss += '\n * self._master = '+str(self._master)
      #.....................................................

      ss += self.history(format=True, prefix='   | ')
      ss += '\n**\n'
      if doprint:
         print ss
      return ss

   #-------------------------------------------------------------------------

   def show_tree (self, index=-1, full=True):
      """Show the specified (index) subtree.
      """
      node = self._nodes[index]
      print EN.format_tree(node, full=full)
      return True

   #-------------------------------------------------------------------------

   def history (self, append=None, clear=False,
                format=False, prefix='',
                show=False, trace=False):
      """Interact with the object history (a list of strings).
      """
      if clear:
         self._history = []
         self._history.append('')
         s = '** Object history of: '+self.oneliner()
         self._history.append(s)
         if trace:
            print '** .history(clear)'

      if isinstance(append,str):
         if append[0]=='|':
            s = '    '+str(append)
         else:
            s = ' -- '+str(append)
            ilast = self.size()-1
            s += '   -> node['+str(ilast)+']: '+str(self._nodes[ilast])
         self._history.append(s)
         if trace:
            print '** .history(append): ',self._history[-1]

      if show or format:
         ss = ''
         for line in self._history:
            ss += '\n'+prefix+line
         ss += '\n'+prefix+'** Current oneliner(): '+str(self.oneliner())+'\n'
         if show:
            print ss
         if format:
            return ss

      # Always return the currently accumulated history (except when format=True)
      return self._history


   #=========================================================================
   # Some general helper functions
   #=========================================================================

   def nodestub (self, qual=None, trace=False):
      """Convenience function to generate a (unique) nodestub.
      """
      stub = EN.unique_stub(self._ns, self._name, self._qual, qual)
      if trace:
         print '\n** .nodestub(',qual,') ->',str(stub)
      return stub

   #--------------------------------------------------------------------------

   def len(self):
      """Return the number of nodes in the Clump (=1 if a tensor)
      """
      return len(self._nodes)

   #--------------------------------------------------------------------------

   def size(self):
      """Return the number of trees in the Clump (even if in a tensor)
      """
      return len(self._treequals)

   #--------------------------------------------------------------------------

   def __getitem__(self, index):
      """Get the specified (index) node.
      """
      return self._nodes[index]


   #=========================================================================
   # To and from tensor nodes:
   #=========================================================================

   def compose (self, trace=False):
      """Compose the Clump nodes into a single tensor node.
      See also .decompose()
      """
      if not self._composed:               # Only if in 'decomposed' state
         stub = self.nodestub('composed')(self._tensor_qual)
         node = stub << Meq.Composer(*self._nodes)
         self._nodes = [node]              # a list of a single node
         self._composed = True             # set the switch
         self._nodequals = [self._tensor_qual]
         self.history('.compose()', trace=trace)
      return True

   #-------------------------------------------------------------------------

   def decompose (self, trace=False):
      """Decompose the single tensor node into separate nodes again.
      The reverse of .compose()
      """
      if self._composed:                   # ONLY if in 'composed' state
         self._composed = False            # set the switch
         self._nodequals = self._treequals
         tensor = self._nodes[0]
         self._nodes = []
         stub = self.nodestub('decomposed')
         for index,qual in enumerate(self._nodequals):
            node = stub(qual) << Meq.Selector(tensor, index=index)
            self._nodes.append(node)
         self.history('.decompose()', trace=trace)
      return True

   #-------------------------------------------------------------------------

   def bundle (self, name=None, combine='Composer', trace=False):
      """Return a single node that bundles the Clump nodes,
      using the specified bundling mechanism (e.g. MeqComposer).
      """
      hist = '.bundle('+str(name)+','+str(combine)+'): '
      if not self._composed:
         stub = self.nodestub('bundle')
         node = stub << getattr(Meq,combine)(*self._nodes)
      elif combine=='Composer':
         node = self._nodes[0]         # OK
      else:
         pass                          # decompose first....?
      self.history(hist, trace=trace)
      return node

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------

   #-------------------------------------------------------------------------


   #=========================================================================
   # Unops and binops:
   #=========================================================================

   def apply_unop (self, unops, trace=False):
      """
      Apply one or more unary operation(s) (e.g. MeqCos) on its nodes.
      """
      # First condition the list of unary operations:
      if isinstance(unops,tuple):
         unops = list(unops)
      elif isinstance(unops,str):
         unops = [unops]

      # Then apply in order of specification:
      for unop in unops:
         stub = self.nodestub(unop)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,unop)(self._nodes[i])
         self.history('.unops('+unop+')', trace=trace)

      return True

   #-------------------------------------------------------------------------

   def apply_binop (self, binop=None, rhs=None, trace=False):
      """Apply a binary operation (e.g. MeqAdd) between its nodes
      and the given right-hand-side (rhs). The latter may be various
      things: a Clump, a node, a number etc.
      """
      hist = '.binop('+str(binop)+') '
      if isinstance(rhs,(int,float,complex)):    # rhs is a number
         hist += str(rhs)+' '
         rhs = self._ns << Meq.Constant(rhs)     # convert to MeqConstant
         
      if is_node(rhs):                           # rhs is a node
         hist += 'node '+str(rhs.name)
         stub = self.nodestub(binop)(rhs.name)
         for i,qual in enumerate(self._nodequals):
            self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs)

      elif isinstance(rhs,type(self)):           # rhs is a Clump object
         hist += rhs.oneliner()
         if self.commensurate(rhs, severe=True):
            stub = self.nodestub(binop)(rhs._name)
            for i,qual in enumerate(self._nodequals):
               self._nodes[i] = stub(qual) << getattr(Meq,binop)(self._nodes[i],rhs._nodes[i])
         
      self.history(hist, trace=trace)
      return True







      
   #=========================================================================
   # Some test-function that define options (TCM):
   #=========================================================================

   def testopt1 (self, trace=False):
      """
      Test-function
      """
      submenu = self._TCM.start_of_submenu(self.testopt1,
                                           qual=self._qual)
      self._TCM.add_option('clone', range(3))

      self._TCM.add_option('aa', range(3))
      self._TCM.add_option('bb', range(3))

      clone = self._TCM.getopt('clone', submenu)
      self._TCM.getopt('aa', submenu)
      self._TCM.getopt('bb', submenu)

      for i in range(clone):
         cp = Clump('clone', qual=i,
                    master=submenu,
                    ns=self._ns,
                    TCM=self._TCM)
         # cp.show('testopt1()', full=True)

      self.history('.testopt1()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True

   #-------------------------------------------------------------------------
      
   def testopt2 (self, trace=False):
      """
      Test-function
      """
      submenu = self._TCM.start_of_submenu(self.testopt2,
                                           qual=self._qual)
      self._TCM.add_option('aa', range(3))
      self._TCM.add_option('bb', range(3))

      self._TCM.getopt('aa', submenu)
      self._TCM.getopt('bb', submenu)

      self.history('.testopt2()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True




#********************************************************************************
#********************************************************************************
# Derived class (with re-implemented .init()):
#********************************************************************************
#********************************************************************************

class DerivedFromClump(Clump):
   """Derived class (with re-implemented .init())
   """

   def __init__(self, name=None,
                qual=None, kwqual=None,
                treequals=None,
                ns=None, TCM=None,
                use=None, init=True,
                **kwargs):
      """
      Derived from class Clump
      """
      Clump.__init__(self, name=name,
                     qual=qual, kwqual=kwqual,
                     treequals=treequals,
                     ns=ns, TCM=TCM,
                     use=use, init=init,
                     **kwargs)
      return None

   #-------------------------------------------------------------------------

   def newinstance(self, name=None, qual=None, init=False):
      """Reimplementation of placeholder function in Clump.
      Make a new instance of this class. Called by .copy().
      """
      return DerivedFromClump(name=name, qual=qual, use=self, init=init)

   #--------------------------------------------------------------------------

   def init (self, trace=False):
      """Reimplementation of placeholder function in Clump.
      Initialize the object with suitable nodes.
      Called from __init__() only
      """
      submenu = self.start_of_submenu()
      self._TCM.add_option('AA', range(1,4))
      self._TCM.add_option('BB', range(1,4))

      self._TCM.getopt('AA', submenu)
      self._TCM.getopt('BB', submenu)

      self._nodes = []
      stub = self.nodestub()
      for i,qual in enumerate(self._nodequals):
         node = stub(qual) << Meq.Parm(i)
         self._nodes.append(node)

      self.history('.init()', trace=trace)

      # The LAST statement:
      self._TCM.end_of_submenu()
      return True




#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************


def _define_forest (ns, **kwargs):
   """The expected function just calls do_define_forest().
   The latter is used outside _define_forest() also (see below)
   """
   if not enable_testing:
      print '\n**************************************************************'
      print '** TDLOptionManager _define_forest(): testing not enabled yet!!'
      print '**************************************************************\n'
      return False
   print '\n** _define_forest():'

   # Generate at least one node:
   node = ns.dummy << 1.0

   # Execute the function that does the actual work. It is the same
   # function that was called outside _define_forest(), where the
   # TDLOptions/Menus were configured (in TCM) and generated.
   # This second run uses the existing option values, which are
   # transferred by means of diskfiles (.TCM and .TRM)
   # It also re-defines the options/menus in a dummy TDLOptionManager,
   # but these are NOT converted into TDLOption/Menu objects. 

   if False:
      # NB: This call has been temporarily inhibited, because something very
      # strange happens: Even if NO TDLOptions are generated in this stage,
      # it gives an error complaining "TDLOption name must be a string".
      # Inhibition is OK for testing options concatenation, but it does
      # not generate any nodes in the browser this way....
      do_define_forest (ns, TCM=TOM.TDLCompileMenu(TCM))       

   return True

#------------------------------------------------------------------------------


def do_define_forest (ns, TCM):
   """The function that does the actual work for _define_forest()
   It is used twice, outside and inside _define_forest() 
   """

   cp = Clump(ns=ns, TCM=TCM)
   submenu = TCM.start_of_submenu(do_define_forest)
   TCM.add_option('testopt',[1,2,3])
   TCM.add_option('clump',[1,2,3])
   TCM.add_option('derived',[1,2,3])

   testopt = TCM.getopt('testopt', submenu)

   if testopt==1:
      cp.testopt1()
   elif testopt==2:
      cp.testopt2()
   elif testopt==3:
      cp.testopt1()
      cp.testopt2()

   # The LAST statement:
   TCM.end_of_submenu()
   return cp

#------------------------------------------------------------------------------

# This bit is executed whenever the module is imported (blue button etc)

itsTDLCompileMenu = None
TCM = TOM.TDLOptionManager(__file__)
# TCM.show('init')
enable_testing = False
enable_testing = True        # normally, this statement will be commented out
if enable_testing:
   ns = NodeScope()
   cp = do_define_forest (ns, TCM=TCM)
   itsTDLCompileMenu = TCM.TDLMenu(trace=False)
   # TCM.show('finished')

   

#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: Clump.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   # rider = QRU.create_rider()             # CollatedHelpRecord object

   if 1:
      cp = Clump(master='xxx')
      cp.show('creation', full=True)

   if 0:
      for node in cp:
         print str(node)
   if 0:
      for index in [0,1,-1,5]:
         print '-- cp[',index,'] -> ',str(cp[index])
   if 0:
      cp.show_tree(-1, full=True)

   if 0:
      cp.compose()
      cp.show('.compose()')
      if 0:
         cp.decompose()
         cp.show('.decompose()')

   if 0:
      unops = 'Cos'
      unops = ['Cos','Sin']
      cp.apply_unop(unops)

   if 0:
      rhs = math.pi
      # rhs = ns.rhs << Meq.Constant(2.3)
      # rhs = Clump('RHS', use=cp)
      cp.apply_binop('Add', rhs=rhs)

   if 1:
      unop = None
      unop = 'Identity'
      cp2 = cp.copy(unop=unop)
      cp2.show('.copy('+str(unop)+')', full=True)

   if 0:
      treequals = range(5)
      treequals = ['a','b','c']
      cp3 = Clump(treequals=treequals)
      cp.commensurate(cp3, severe=False, trace=True)
      cp3.show('.commensurate()')

   if 1:
      dcp = DerivedFromClump()
      dcp.show(full=True)
      if 1:
         unop = None
         dcp2 = dcp.copy(unop=unop)
         dcp2.show('.copy('+str(unop)+')', full=True)


   if 1:
      cp.show('final', full=True)

   
      
   print '\n** End of standalone test of: Clump.py:\n' 

#=====================================================================================





