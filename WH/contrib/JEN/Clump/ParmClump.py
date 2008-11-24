"""
ParmClump.py: A Clump of MeqParms, e.g. Ggain:0...D
"""

# file: ../JEN/Clump/ParmClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 07 nov 2008: creation (from templateClump.py)
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

from Timba.Contrib.JEN.Clump import Clump

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc



#********************************************************************************
#********************************************************************************

class ParmClump(Clump.LeafClump):
   """
   Derived class
   """

   def __init__(self, clump=None, default=0.0, **kwargs):
      """
      Derived from class LeafClump.
      """

      # The following are used in the Meq.Parm() constructor:
      # See .initexec() below
      self._default = default
      mpp = dict()
      mpp['use_previous'] = kwargs.get('use_previous', True) 
      mpp['table_name'] = kwargs.get('table_name', None) 
      self._MeqParm_parms = mpp

      # The following are used in .solspec() to modify MeqParm.initrec()
      # See also the helper function .make_choice()
      ssp = dict()
      keys = ['tdeg','fdeg','ntime_subtile','nfreq_subtile']
      for key in keys:
         if kwargs.has_key(key):
            ssp[key] = kwargs[key]
      self._solspec_parms = ssp

      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the ParmClump object with suitable MeqParm nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      help = 'definition of a set of similar MeqParms: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           

         mpp = self._MeqParm_parms
         default = self._default

         # Generate the MeqParm node(s):
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            qd = 'dflt='+str(default)
            self[i] = stub(qual)(qd) << Meq.Parm(default, **mpp)
            print '-',i,qual,qd,str(self[i])

         # A ParmClump object is itself the only entry in its list of ParmClumps:
         self.ParmClumps(append=self)

         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


   #============================================================================
   #============================================================================

   def get_choice (self, key, choice=None, trace=False):
      """Helper function to make a choice list for the named (key) TDLOption.
      Normally, the specified choice list is used, but this may be modified by
      means of ParmClump constructor kwargs in two ways:
      - if key=value, prepend value to the choice list. This makes it the default.
      - if key=[list], use that as the choice list.
      """
      ssp = self._solspec_parms                # convenience
      hist = 'solspec('+str(key)+'): '
      if not ssp.has_key(key):                 # not specified by kwargs
         cc = choice                           # use the default choice
         hist += 'use default choice -> '+str(cc)
      else:
         c = ssp[key]
         if isinstance(c,list):
            cc = c
            hist += 'use external (kwargs) choice -> '+str(cc) 
         else:
            cc = [c] + choice
            hist += 'use external (kwargs) default (='+str(c)+') -> '+str(cc) 
      self.history(hist, trace=trace)
      return cc
            
   #----------------------------------------------------------------------------
   
   def solspec (self, **kwargs):
      """
      A menu for the specification of the solving parameters for its MeqParms.
      It returns a list of solvable parms, to be given to a MeqSolver.
      This routine called by the solver object(!), not the ParmClump constructor.
      This means that the menu-options are also settable in the solver!! 
      """
      help = 'specify solving parameters for the MeqParms of: '+self.oneliner()
      prompt = 'solve for: '+self.name()
      ctrl = self.on_entry(self.solspec, prompt=prompt, help=help, **kwargs)

      self.add_option('fdeg', self.get_choice('fdeg', range(6)),
                      help='freq deg of polc',
                      prompt='freq deg')

      self.add_option('tdeg', self.get_choice('tdeg', range(6)),
                      help='time deg of polc',
                      prompt='time deg')

      choice = self.get_choice('nfreq_subtile', [None,1,2,3,4,5,10])
      self.add_option('nfreq_subtile', choice, more=int,
                      # hide=True,
                      help="size (freq-cells) of solving subtile")

      choice = self.get_choice('ntime_subtile', [None,1,2,3,4,5,10])
      self.add_option('ntime_subtile', choice, more=int,
                      # hide=True,
                      help="size (time-cells) of solving subtile")

      solvable = []                               # return a list of solvable MeqParm names
      always = kwargs.get('always',False)         # see e.g. SolverUnit.py
      if self.execute_body(always=always):           

         tdeg = self.getopt('tdeg')
         fdeg = self.getopt('fdeg')
         nt = self.getopt('ntime_subtile')
         nf = self.getopt('nfreq_subtile')
         tiling = record(freq=nf, time=nt)

         for i,qual in enumerate(self.nodequals()):
            rr = self[i].initrec()
            rr.shape = [tdeg+1,fdeg+1] 
            rr.tiling = tiling,
            solvable.append(self[i])

         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl, result=solvable)



   

#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class ParmListClump:
#********************************************************************************

class ParmListClump(Clump.ListClump, ParmClump):
   """
   A ParmClump may also be created from a list of nodes (nodelist).
   They do not have to be MeqParms. The nodescope is searched for MeqParms.
   """

   def __init__(self, nodelist=None, **kwargs):
      """
      Derived from classes Clump.ListClump and ParmClump.
      """
      #.................................................
      # NB: This calls the .initexec() function of class ParmClump!
      Clump.ListClump.__init__(self, nodelist, **kwargs)
      # There is NO need to call ParmClump.__init__()
      #.................................................

      # Check if the input nodes are MeqParms 
      parms = []
      for node in self.get_nodelist():
         if node.classname=='MeqParm':
            parms.append(node)

      # If not MeqParms, search the nodescope for MeqParms.
      if len(parms)==0:
         nodes = self.ns().Search(class_name='MeqParm')
         parms = []
         for node in nodes:
            if node.classname=='MeqParm':
               parms.append(node)
         if len(parms)==0:
            self.ERROR('** no MeqParms found')
         else:
            np = len(parms)
            self.datadesc(treequals=range(np))
            self.core._nodes = parms
            self.history('used '+str(np)+' MeqParms found in nodescope')
 
      # A ParmClump object is itself the only entry in its list of ParmClumps:
      self.ParmClumps(append=self)

      # self.history('Created from list of nodes', show_node=True)
      return None


#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class PolyCoeff:
#********************************************************************************

class PolyCoeff(ParmClump):
   """
   Contains the coefficients of a 2D polynomial c0 + c1*x + c2*x*x + ....
   """

   def __init__(self, **kwargs):
      """
      Derived from clas ParmClump.
      """
      
      ParmClump.__init__(self, **kwargs)
      return None

   #--------------------------------------------------------------------

   def initexec (self, **kwargs):
      """Fill the ParmClump object with suitable MeqParm nodes.
      """
      help = 'definition of ndeg MeqParm polynomial coeff: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)

      self._xdeg = max(0,kwargs.get('xdeg',0))    # degree in x-direction
      self._ydeg = max(0,kwargs.get('ydeg',0))    # degree in y-direction

      if self.execute_body(always=True):           

         # Generate the MeqParm node(s):
         rr = dict()
         default = 0.0
         stub = self.unique_nodestub()
         self._terms = dict()
         self.clear()
         for i in range(self._xdeg):
            for j in range(self._ydeg):
               qual = str(i)+str(j)
               node = stub(qual) << Meq.Parm(default, **rr)
               self._terms[qual] = node           # see .effixy() 
               self.append(node)
               
         # Adjust the data-description:
         self.datadesc(treequals=self._terms.keys())

         # A ParmClump object is itself the only entry in its list of ParmClumps:
         self.ParmClumps(append=self)

         self.end_of_body(ctrl)
      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------

   def factor(self, qual='00', x=0, y=0, trace=False):
      """
      """

   #----------------------------------------------------------------------------

   def effixy (self, x=0.0, y=0.0, name='effixy', trace=False):
      """Return a node that represents f(x,y), for given values/nodes (x,y).
      """
      terms = []
      stub = self.unique_nodestub(name=name)
      if isinstance(x,int):
         x = float(x)

      for i,node in enumerate(self.get_nodelist()):
         terms.append(self[i])
         if i==1:
            terms[-1] = stub(i) << Meq.Multiply(terms[-1],x)
         elif i>1:
            if is_node(x):
               powx = stub(i)('powx') << getattr(Meq,'Pow'+str(i))(x)
            elif isinstance(x,float):
               powx = x**i
            elif isinstance(x,int):
               powx = float(x)**i
            else:
               self.ERROR('type of x not recognized: '+str(type(x)))
            terms[-1] = stub(i) << Meq.Multiply(terms[-1],x**i)

      if len(terms)==0:
         self.ERROR('terms list is empty')
      elif len(terms)==1:
         node = terms[0]
      else:
         node = stub(x=x) << Meq.Add(*terms)

      # Finished
      return node




#********************************************************************************
#********************************************************************************
# Function called from _define_forest() in ClumpExec.py
#********************************************************************************
#********************************************************************************

def do_define_forest (ns, TCM):
   """
   Testing function for the class(es) in this module.
   It is called by ClumpExec.py
   """
   submenu = TCM.start_of_submenu(do_define_forest,
                                  prompt=__file__.split('/')[-1],
                                  help=__file__)
   TCM.add_option('test_class',['ParmClump','ParmListClump','PolyCoeff'],
                                prompt='class to be tested:')
   clump = None
   if TCM.submenu_is_selected():
      test_class = TCM.getopt('test_class', submenu)

      if test_class=='PolyCoeff':
         clump = PolyCoeff(ndeg=3, ns=ns, trace=True)
         if True:
            for x in [3,-4]:
               node = clump.effixy(x)
               print '.effix(',x,') -> ',str(node)

      elif test_class=='ParmListClump':
         cc = []
         for i in range(4):
            node = ns.ddd(i) << Meq.Parm(i)
            cc.append(node)
         clump = ParmListClump(cc, ns=ns, name='polyparm', trace=True)

      else:
         clump = ParmClump(ns=ns, TCM=TCM,
                           name='GgainY', default=2.3,
                           treequals=range(10)+list('ABCD'),         # WSRT
                           tdeg=4, fdeg=[4,5],                       # override
                           select=True)

      solvable = clump.get_solvable(trace=True)
      # solvable = clump.solspec(select=True)
      # tdeg=2,                                   # override
      # clump.visualize()

   # The LAST statement:
   TCM.end_of_submenu()
   return clump





#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: ParmClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   TCM = None
   if 0:
      TCM = Clump.TOM.TDLOptionManager()
      print TCM.oneliner()

   if 1:
      c1 = None
      if 1:
         c1 = Clump.LeafClump(treequals=range(5))
         c1.show('input clump (c1)')
      # clump = ParmClump(c1, trace=True)
      clump = ParmClump(c1, trace=True, tdeg=[2,3], nfreq_subtile=2)

   if 0:
      clump = PolyCoeff(ndeg=3, trace=True)
      for x in [3,-4]:
         node = clump.effixy(x)
         print '.effix(',x,') -> ',str(node)

   if 0:
      cc = []
      for i in range(4):
         node = ns.ddd(i) << Meq.Parm(i)
         cc.append(node)
      clump = ParmListClump(cc, ns=ns, name='polyparm', trace=True)

   if 0:
      tqs = range(10) + list('ABCD')
      clump = ParmClump(treequals=tqs,
                        # ns=ns, TCM=TCM,
                        name='GgainX',
                        default=1.0,
                        # single=True,
                        tdeg=4, fdeg=[4,5],                       # override
                        trace=True)

   #--------------------------------------------------------
   
   if 1:
      clump.show('creation', full=True)

   if 0:
      clump1 = ParmClump(clump, name='other')
      clump1.show('clump1')

   if 1:
      solvable = clump.solspec()
      print '-> solvable:'
      for i,node in enumerate(solvable):
         print '-',i,':',str(node),'\n    ',node.initrec()
      print
      clump.show('after solspec()')

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: ParmClump.py:\n' 

#=====================================================================================





