"""
JonesClump.py: Base-class for an entire zoo of derived classes that
represent 2x2 Jones matrices (hhich describe instrumental effects)
"""

# file: ../JEN/Clump/JonesClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 11 nov 2008: creation (from templateLeafClump.py)
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
from Timba.Contrib.JEN.Clump import ParmClump
from Timba.Contrib.JEN.Clump import CorruptClump

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc



#********************************************************************************
# JonesClump.JonesClump is the baseclass of all Jones Clumps, and the template
#********************************************************************************

class JonesClump(Clump.LeafClump):
   """
   Derived class from LeafClump.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class LeafClump.
      """
      # This should be in every JonesClump class:
      self.datadesc(complex=True, dims=[2,2])

      # This bit is instrument-specific:
      treequals = range(8,10)+list('AB')          # default treequals (WSRT)
      treequals = ['RT8','RT9','RTA','RTB']       # default treequals (WSRT)
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # Polarization representation:
      self._polrep = kwargs.get('polrep', None)
      
      # This needs a little thought...:
      rr = dict()
      for key in ['use_previous','table_name']:
         rr['use_previous'] = kwargs.get('use_previous', True)
      self._MeqParm_parms = rr
      Clump.LeafClump.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def polrep (self):
      """Return the uv-data polarization representation that is assumed by
      this Jones matrix (linear[=default], circular, None).
      """
      return self._polrep

   #--------------------------------------------------------------------------

   def ParmClump(self, name, default=0.0, **kwargs):
      """Helper function to create a ParmClump in an organised way.
      If single=True, make a ParmClump with only one MeqParm.
      Otherwise, there will be one for each station.
      """
      clump = ParmClump.ParmClump(self, name=name,
                                  default=default,
                                  **kwargs)
                                  # single=single,
                                  # hide=True,
                                  # **self._MeqParm_parms)
      # Connect all the loose ends:
      self.connect_grafted_clump(clump)
      return clump


   #==========================================================================
   # To be re-implemented in derived classes
   #==========================================================================

   def initexec (self, **kwargs):
      """
      This is an example of how to fill a JonesClump with 2x2 matrices.
      To be re-implemented in derived classes (e.g. see WSRTJones.py,
      or the XXXJones, GJones, BJones classes below). 
      """
      prompt = 'Jones: '+self.name()
      help = 'define Jones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      if self.execute_body():

         # Create ParmClumps:
         r00 = self.ParmClump('real00', default=1.0)
         i00 = self.ParmClump('imag00', default=0.0)
         r10 = self.ParmClump('real10', default=1.0)
         i10 = self.ParmClump('imag10', default=0.0)
         r01 = self.ParmClump('real01', default=1.0)
         i01 = self.ParmClump('imag01', default=0.0)
         r11 = self.ParmClump('real11', default=1.0)
         i11 = self.ParmClump('imag11', default=0.0)

         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            elem00 = stub(qual)('00') << Meq.ToComplex(r00[i],i00[i])
            elem01 = stub(qual)('10') << Meq.ToComplex(r01[i],i01[i])
            elem10 = stub(qual)('01') << Meq.ToComplex(r01[i],i01[i])
            elem11 = stub(qual)('11') << Meq.ToComplex(r11[i],i11[i])
            self[i] = stub(qual) << Meq.Matrix22(elem00, elem01,
                                                 elem10, elem11)

         self.end_of_body(ctrl)
      return self.on_exit(ctrl)



#********************************************************************************
# GJones (electronic gain):
#********************************************************************************

class GJones(JonesClump):
   """
   Derived class from JonesClump.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class LeafClump.
      """
      JonesClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================

   def initexec (self, **kwargs):
      """
      GJones represents electronic gain. It is a uv-plane effect.
      Rather generic, so most telescopes just reuse this class
      (e.g. see WSRTJones.py).
      """
      prompt = 'GJones: '+self.name()
      help = 'define GJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      # Menu option(s) (the menu itself is generated in .on_entry()):
      self.add_option('mode',['amphas','realimag'])

      if self.execute_body():
         mode = self.getopt('mode')

         # Create ParmClumps:
         if mode=='amphas':
            gerrX = self.ParmClump('gerrX', default=1.0)
            perrX = self.ParmClump('perrX', default=0.0)
            gerrY = self.ParmClump('gerrY', default=1.0)
            perrY = self.ParmClump('perrY', default=0.0)
         elif mode=='realimag':
            rerrX = self.ParmClump('rerrX', default=1.0)
            ierrX = self.ParmClump('ierrX', default=0.0)
            rerrY = self.ParmClump('rerrY', default=1.0)
            ierrY = self.ParmClump('ierrY', default=0.0)

         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            elem00 = complex(1,0)
            elem01 = complex(0,0)
            elem10 = complex(0,0)
            elem11 = complex(1,0)
            if mode=='amphas':                
               elem00 = stub(qual)('00') << Meq.Polar(gerrX[i],perrX[i])
               elem11 = stub(qual)('11') << Meq.Polar(gerrY[i],perrY[i])
            elif mode=='realimag':
               elem00 = stub(qual)('00') << Meq.ToComplex(rerrX[i],ierrX[i])
               elem11 = stub(qual)('11') << Meq.ToComplex(rerrY[i],ierrY[i])
            self[i] = stub(qual) << Meq.Matrix22(elem00, elem01,
                                                 elem10, elem11)

         self.end_of_body(ctrl)
      return self.on_exit(ctrl)


#********************************************************************************
# BJones (electronic bandpass):
#********************************************************************************

class BJones(JonesClump):
   """
   Derived class from JonesClump.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class JonesClump.
      """
      JonesClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================

   def initexec (self, **kwargs):
      """
      GJones represents electronic bandpass. It is a uv-plane effect.
      Rather generic, so most telescopes just reuse this class
      (e.g. see WSRTJones.py).
      """
      prompt = 'BJones: '+self.name()
      help = 'define BJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      # Menu option(s) (the menu itself is generated in .on_entry()):
      self.add_option('mode',['amphas','realimag'])

      if self.execute_body():
         mode = self.getopt('mode')

         pp = dict(nfreq_subtile=[1,2],
                   ntime_subtile=[None],
                   fdeg=0,
                   tdeg=[1,2])

         # Create ParmClumps:
         if mode=='amphas':
            gerrX = self.ParmClump('gerrX', default=1.0, **pp)
            perrX = self.ParmClump('perrX', default=0.0, **pp)
            gerrY = self.ParmClump('gerrY', default=1.0, **pp)
            perrY = self.ParmClump('perrY', default=0.0, **pp)
         elif mode=='realimag':
            rerrX = self.ParmClump('rerrX', default=1.0, **pp)
            ierrX = self.ParmClump('ierrX', default=0.0, **pp)
            rerrY = self.ParmClump('rerrY', default=1.0, **pp)
            ierrY = self.ParmClump('ierrY', default=0.0, **pp)

         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            elem00 = complex(1,0)
            elem01 = complex(0,0)
            elem10 = complex(0,0)
            elem11 = complex(1,0)
            if mode=='amphas':                
               elem00 = stub(qual)('00') << Meq.Polar(gerrX[i],perrX[i])
               elem11 = stub(qual)('11') << Meq.Polar(gerrY[i],perrY[i])
            elif mode=='realimag':
               elem00 = stub(qual)('00') << Meq.ToComplex(rerrX[i],ierrX[i])
               elem11 = stub(qual)('11') << Meq.ToComplex(rerrY[i],ierrY[i])
            self[i] = stub(qual) << Meq.Matrix22(elem00, elem01,
                                                 elem10, elem11)
         self.end_of_body(ctrl)
      return self.on_exit(ctrl)



#********************************************************************************
#********************************************************************************
#********************************************************************************
# JonesClump.XXXJones is a multiplication of Jones Clumps
#********************************************************************************

class XXXJones(JonesClump):
   """
   This JonesClump represents a sequence (multiplication) of JonesClumps,
   It is a baseclass for classes like WSRTJones, VLAJones etc.
   Just replace .initexec() with your own sequence of JonesClumps.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      JonesClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================

   def initexec (self, **kwargs):
      """
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      prompt = 'Jones: '+str(self.name())
      help = """Specify a sequence (product) of zero or more Jones matrices.
      If zero are selected, a placeholder 2x2 (constant) unit-matrix is used.
      """
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('use_previous', True,
                      hide=True,
                      help='if True, use the previous solution',
                      prompt='use_previous')
      self.add_option('table_name', [None,'test.mep'], more=str,
                      hide=True,
                      help='name of the file that contains the parmtable',
                      prompt='.mep file')
      
      if self.execute_body(always=True):
         for key in ['use_previous','table_name']:
            self._MeqParm_parms[key] = self.getopt(key)
            
         (jj,notsel) = self.make_jones_sequence(**kwargs)
         self.make_single_jones(jj, notsel)

         self.end_of_body(ctrl)
      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------

   def make_jones_sequence(self, **kwargs):
      """Function to be re-implemented in derived classes.
      """
      treequals = range(8,10)+list('AB')          # default treequals (WSRT)
      self.datadesc(treequals=kwargs.get('treequals', treequals))
      jj = []
      notsel = []
      JonesClump(self, name='AJones').append_if_selected(jj, notsel)
      JonesClump(self, name='BJones').append_if_selected(jj, notsel)
      JonesClump(self, name='CJones').append_if_selected(jj, notsel)
      return (jj,notsel)


   #============================================================================
   #============================================================================

   def make_single_jones(self, jj, notsel=None):
      """Make a single Jones matrix from the ones collected in .initexex()
      This function is generic, i.e. it should NOT be re-implemented in
      classes that are derived from XXXJones. It contains more specialist code,
      which should not be seen by the uninitiated.
      """
      if len(jj)==0:
         self.history('empty Jones list: make a 2x2 complex unit matrix')
         stub = self.unique_nodestub('unitmatrix')
         for i,qual in enumerate(self.nodequals()):
            self[i] = stub(qual) << Meq.Matrix22(complex(1,0), complex(0,0),
                                                 complex(0,0), complex(1,0))

      elif len(jj)==1:
         # one only: copy its nodes
         for i,qual in enumerate(self.nodequals()):
            self[i] = jj[0][i]
      
      else:
         # more than one: MatrixMyultiply
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            cc = []
            for jones in jj:
               cc.append(jones[i])
            self[i] = stub(qual) << Meq.MatrixMultiply(*cc)
         
      # Connect orphans, stubtree etc, and add the ParmClumps to
      # its own list of ParmClumps (self.ParmClumps()).
      for jones in jj:
         # self.history('include Jones: '+jones.oneliner())
         # jones.show('make_single_jones()')
         self.connect_grafted_clump(jones)

      # Check the polarization representations (linear/circular/None):
      self._polrep = None                 # polrep of combined Jones
      for jones in jj:
         pol = jones.polrep()
         if pol==None:                    # jones is not pol-specific
            pass
         elif not pol in ['linear','circular']:
            print jones.oneliner()
            self.ERROR('Jones polrep not recognized: '+str(pol))
         elif self._polrep==None:         # combined polrep not (yet) specific
            self._polrep = pol
         elif not pol==self._polrep:      # not compatible
            print jones.oneliner()
            self.ERROR('Jones polreps are incompatible: '+str(pol)+ '!= '+str(self.polrep()))

      # Deal with the Jones matrices that were NOT selected:
      if isinstance(notsel,list):
         for jones in notsel:
            # print '- not selected:',jones.oneliner()
            jones.connect_loose_ends (self, full=False)

      # Finished:
      return True
      




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
   TCM.add_option('jones',
                  ['XXXJones','JonesClump',
                   'GJones','BJones'],
                  prompt='test WSRT Jones:')
   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      if jones=='GJones':
         clump = GJones(ns=ns, TCM=TCM)
      elif jones=='BJones':
         clump = BJones(ns=ns, TCM=TCM)
      elif jones=='XXXJones':
         clump = XXXJones(ns=ns, TCM=TCM)
      else:
         clump = JonesClump(ns=ns, TCM=TCM)
         
      # clump = CorruptClump.Scatter(clump).daisy_chain()
      clump.visualize()

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
   print '** Start of standalone test of: JonesClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 0:
      clump = JonesClump(trace=True)
   else:
      clump = XXXJones(trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: JonesClump.py:\n' 

#=====================================================================================





