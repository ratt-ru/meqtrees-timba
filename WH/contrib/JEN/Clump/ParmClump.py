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

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class LeafClump.
      """
      kwargs['fixture'] = True              # A ParmClump is always selected
      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def show_specific(self):
      """
      Format the specific (non-generic) contents of the class.
      Placeholder for re-implementation in derived class.
      """
      ss = '\n + Specific (derived class '+str(self._typename)+'):'
      ss += '\n + MeqParm[0].initrec(): '+str(self[0].initrec())
      # ss += '\n + ...'
      return ss

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

      default = kwargs.get('default',0.0)

      if False:
         # See self.solspec() below
         self.add_option('fdeg', range(6),
                         help='freq deg of polc',
                         prompt='freq deg')
         self.add_option('tdeg', range(6),
                         help='time deg of polc',
                         prompt='time deg')
         
         self.add_option('nftile', [None,1,2,3,4,5,10], more=int,
                         help="size (freq-cells) of solving subtile")
         self.add_option('nttile', [None,1,2,3,4,5,10], more=int,
                         help="size (time-cells) of solving subtile")
         
         self.add_option('solvable', False,
                         prompt='solvable')
      
      self.add_option('use_previous', True, hide=True,
                      help='if True, use the previous solution',
                      prompt='use_previous')
      self.add_option('mepfile', [None,'test.mep'], more=str, hide=True,
                      help='name of the file that contains the parmtable',
                      prompt='.mep file')

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           

         mepfile = self.getopt('mepfile')
         use_previous = self.getopt('use_previous')
         if False:
            tdeg = self.getopt('tdeg')
            fdeg = self.getopt('fdeg')
            nt = self.getopt('nttile')
            nf = self.getopt('nftile')
            tiling = record(freq=nf, time=nt)
            # See self.solvable_parms()
            self._solvable = self.getopt('solvable')

         self._nodes = []
         self._parmnames = []
         stub = self.unique_nodestub()
         for i,qual in enumerate(self._nodequals):
            qd = 'dflt='+str(default)
            node = stub(qual)(qd) << Meq.Parm(default,
                                              table_name=mepfile,
                                              use_previous=use_previous,
                                              # shape=[2,1],                # testing...
                                              # tiling=tiling,
                                              # tags=['tag1','tag2'],
                                              node_groups='Parm')
            self._nodes.append(node)
            self._parmnames.append(node.name)
            # print '\n -',str(node),' initrec: ',node.initrec()

         # A ParmClump object is itself the only entry in its list of ParmClumps:
         self._ParmClumps = [self]

         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


   #============================================================================
   #============================================================================

   
   def solspec (self, **kwargs):
      """
      A menu for the specification of the solving parameters for its MeqParms.
      It returns a list of solvable parms, to be given to a MeqSolver. 
      """
      help = 'specify solving parameters for the MeqParms of: '+self.oneliner()
      ctrl = self.on_entry(self.solspec, help=help, **kwargs)


      self.add_option('fdeg', range(6),
                      help='freq deg of polc',
                      prompt='freq deg')
      self.add_option('tdeg', range(6),
                      help='time deg of polc',
                      prompt='time deg')

      self.add_option('nfreq_subtile', [None,1,2,3,4,5,10], more=int, hide=True,
                      help="size (freq-cells) of solving subtile")
      self.add_option('ntime_subtile', [None,1,2,3,4,5,10], more=int, hide=True,
                      help="size (time-cells) of solving subtile")

      solvable = []         # return a list of solvable MeqParm names
      if self.execute_body(always=True):           

         tdeg = self.getopt('tdeg')
         fdeg = self.getopt('fdeg')
         nt = self.getopt('ntime_subtile')
         nf = self.getopt('nfreq_subtile')
         tiling = record(freq=nf, time=nt)

         for i,qual in enumerate(self._nodequals):
            rr = self._nodes[i].initrec()
            rr.shape = [tdeg+1,fdeg+1] 
            rr.tiling = tiling,
            solvable.append(self._nodes[i])

         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl, result=solvable)


   #============================================================================

   

#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class ListClump:
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

      # Search for MeqParms:
      # - First check if the input nodes are MeqParms 
      # - If not, search the nodescope for MeqParms.
      parms = []
      for node in self._nodes:
         if node.classname=='MeqParm':
            parms.append(node)

      if len(parms)==0:
         parms = self._ns.Search(class_name='MeqParm')

      if len(parms)==0:
         self.ERROR('** no MeqParms found')
      else:
         self._ParmClumps = [self]

      # self.history('Created from list of nodes', show_node=True)
      return None




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
   clump = None
   if TCM.submenu_is_selected():
      clump = ParmClump(ns=ns, TCM=TCM,
                        name='GgainY', default=2.3,
                        treequals=range(10)+list('ABCD'),         # WSRT
                        select=True,
                        trace=True)
      solvable = clump.solspec(select=True)
                        # tdeg=2,                                   # override
      print '\n** solvable =',solvable,'\n'
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
   if 1:
      TCM = Clump.TOM.TDLOptionManager()
      print TCM.oneliner()

   if 0:
      clump = ParmClump(trace=True)

   if 1:
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
                        trace=True)

   #--------------------------------------------------------
   
   if 1:
      clump.show('creation', full=True)

   if 0:
      clump1 = ParmClump(clump, name='other')
      clump1.show('clump1')

   if 1:
      solvable = clump.solspec()
      print '-> solvable =',solvable
      clump.show('after solspec()')

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: ParmClump.py:\n' 

#=====================================================================================





