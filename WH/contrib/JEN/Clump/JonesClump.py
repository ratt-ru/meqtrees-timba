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

from Timba.Contrib.JEN.Expression import Expression

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # 



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
      # All Jones matrices are 2x2 and complex.
      # The kwargs are picked up in Clump.__init__() below.
      kwargs['dims'] = [2,2]
      kwargs['complex'] = True

      # Its MeqParms may be simulated (MeqFunctionals): 
      self._simulate = kwargs.get('simulate',False)
      if self._simulate:
         # Append the qualifier 'simul' to all nodes:
         qual = 'simul'
         key = 'qual'
         if not kwargs.has_key(key):
            kwargs[key] = qual
         elif isinstance(kwargs[key],list):
            kwargs[key].append(qual)
         else:
            kwargs[key] = [kwargs[key],qual]

      # The form of some Jones matrices depends on the
      # polarization representation (linear,circular)
      # This may be specified by means of kwargs.
      self._polrep = kwargs.get('polrep', None)   # default: not specific 

      # Use the WSRT array as the default (overridden by kwargs):
      treequals = range(8,10)+list('AB')          # default treequals (WSRT)
      treequals = ['RT8','RT9','RTA','RTB']       # default treequals (WSRT)
      kwargs.setdefault('treequals', treequals)

      Clump.LeafClump.__init__(self, clump=clump, **kwargs)

      return None

   #-------------------------------------------------------------------------

   def polrep (self):
      """Return the uv-data polarization representation that is assumed by
      this Jones matrix (linear[=default], circular, None).
      """
      return self._polrep

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Placeholder function for the specification of solspec parameters,
      which are given as **kwargs arguments to ParmClump constructors.
      They are used to override the CHOICE of values (and the help) for
      MeqParm options, so that these are relevant for a specific Jones matrix.
      These choices (and helps) are used to allow the user to choose sensible
      values, e.g. in ParmClump.solspec(), which is called from a solver.
      This function may be re-implemented in derived JonesClump classes.
      In that case, it is recommended to first call this base-class method,
      so that the method starts with a dict (scp) that may contain some
      default fields (which then may or may not be overriden).
      """
      scp = dict(optionhelp=dict())
      self.set_scp (scp, 'table_name', None, help=None)
      self.set_scp (scp, 'use_previous', True, help=None)
      # self.set_scp (scp, 'tdeg', value, help=None)
      # self.set_scp (scp, 'fdeg', value, help=None)
      # self.set_scp (scp, 'nfreq_subtile', value, help=None)
      # self.set_scp (scp, 'ntime_subtile', value, help=None)
      return scp

   #..........................................................................

   def set_scp (self, scp, key, value, help=None):
      """Helper function to be called from .get_solspec_choice_parameters()
      (see above), also in re-implemented versions in derived classes.
      It sets the value of the specified (key) field, and generates some
      context-sensitive automatic help if no specific help string is specified.
      It just calls the function of the same name in the module ParmClump.py
      """
      return ParmClump.set_scp (scp, key=key, value=value, help=help)

   #--------------------------------------------------------------------------

   def make_ParmClump(self, name, default=0.0, trace=False):
      """Helper function to create a ParmClump in an organised way.
      """
      # NB: The following function will be re-implemented in a derived class
      self._solspec_choice = self.get_solspec_choice_parameters()
      clump = ParmClump.ParmClump(self, name=name,
                                  default=default,
                                  simulate=self._simulate,
                                  **self._solspec_choice)
      self.connect_grafted_clump(clump)       # connect the loose ends:
      if trace:
         clump.show('JonesClump.ParmClump()')
      return clump

   #--------------------------------------------------------------------------

   def make_PExpressionClump(self, Expression=None, default=0.0, trace=False):
      """Helper function to create a ParmClump using the given Expression object.
      """
      # NB: The following function will be re-implemented in a derived class
      self._solspec_choice = self.get_solspec_choice_parameters()
      clump = ParmClump.ParmClump(Expression=Expression,
                                  default=default,
                                  TCM=self.TCM(), ns=self.ns(),
                                  simulate=self._simulate,
                                  **self._solspec_choice)
      self.connect_grafted_clump(clump)       # connect the loose ends:
      if trace:
         clump.show('JonesClump.make_PExpressionClump()')
      return clump

   #--------------------------------------------------------------------------

   def make_PFunctionalClump(self, name, expr, varvals=None, trace=False):
      """Helper function to create a PFunctionalClump in an organised way.
      """
      # NB: The following function will be re-implemented in a derived class
      self._solspec_choice = self.get_solspec_choice_parameters()
      clump = ParmClump.PFunctionalClump(name=name,
                                         expr=expr, varvals=varvals,
                                         TCM=self.TCM(), ns=self.ns(),
                                         simulate=self._simulate,
                                         **self._solspec_choice)
      self.connect_grafted_clump(clump)      # connect the loose ends
      if trace:
         clump.show('JonesClump.PFunctionalClump()')
      return clump

   #----------------------------------------------------------------------------
   
   def make_JonesClump(self, L=None, M=None, LM=None, trace=False):
      """Return a JonesClump that is valid for the given direction (L,M).
      To be re-implemented in some derived classes:
      - in JonesClump: returns itself, which is valid for all (L,M) (uv-plane effect)
      - in IMPJonesClump: makes a JonesClump for the given direction (L,M)
      - in FullJones: multiplies a selected sequence of JonesClumps
      NB: The arguments L,M,LM are dummies in the JonesClump case, of course.
      """
      # Default implementation: just return itself.
      if trace:
         print '.make_JonesClump() -> itself:',self.oneliner()
      return self



   #==========================================================================
   # Placeholder, to be re-implemented in derived classes
   #==========================================================================

   def initexec (self, **kwargs):
      """
      Placeholder that creates dummy entries (None) for all Clump trees.
      To be re-implemented in derived classes (e.g. see WSRTJones.py,
      or the UVPJones, GJones, BJones classes below). 
      """
      prompt = 'JonesClump: '+self.name()
      help = 'define JonesClump: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)
      if self.execute_body(always=True):
         for i,qual in enumerate(self.nodequals()):
            self[i] = None
         self.end_of_body(ctrl)
      return self.on_exit(ctrl)



#********************************************************************************
# JJones (The most general case: 4 complex elements):
#********************************************************************************

class JJones(JonesClump):
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
      JJones is the most general Jones matrix for a uv-plane effect.
      It contains 8 ParmClumps for the real and imaginary parts of its
      4 complex matrix elements.
      """
      prompt = 'JJones: '+self.name()
      help = 'define Jones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      if self.execute_body():

         # Create ParmClumps:
         r00 = self.make_ParmClump('real00', default=1.0)
         i00 = self.make_ParmClump('imag00', default=0.0)
         r10 = self.make_ParmClump('real10', default=1.0)
         i10 = self.make_ParmClump('imag10', default=0.0)
         r01 = self.make_ParmClump('real01', default=1.0)
         i01 = self.make_ParmClump('imag01', default=0.0)
         r11 = self.make_ParmClump('real11', default=1.0)
         i11 = self.make_ParmClump('imag11', default=0.0)

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

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the method in JonesClump. Specify the relevant
      choice of solution-specification parameters that will be offered in the
      .solspec() method of its ParmClump ojects.
      Syntax: A list value replaces the entire choice, a number is just used as
      the default, i.e. it is offered as the first value of the default choice list.
      An object-specific help-text may also be offered here. 
      """
      scp = JonesClump.get_solspec_choice_parameters(self)
      self.set_scp (scp, 'tdeg', [1,2], help='solve for low-order time polynomial')
      self.set_scp (scp, 'fdeg', 0, help='default: no freq dependence')
      self.set_scp (scp, 'nfreq_subtile', [None], help='solve over all freq cells')
      self.set_scp (scp, 'ntime_subtile', [5,10], help='size of subtile solutions')
      return scp


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
            gerrX = self.make_ParmClump('gerrX', default=1.0)
            perrX = self.make_ParmClump('perrX', default=0.0)
            gerrY = self.make_ParmClump('gerrY', default=1.0)
            perrY = self.make_ParmClump('perrY', default=0.0)
         elif mode=='realimag':
            rerrX = self.make_ParmClump('rerrX', default=1.0)
            ierrX = self.make_ParmClump('ierrX', default=0.0)
            rerrY = self.make_ParmClump('rerrY', default=1.0)
            ierrY = self.make_ParmClump('ierrY', default=0.0)

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
# PJones (parallactic angle):
#********************************************************************************

class PJones(JonesClump):
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
      PJones represents the parallactic angle. It is a uv-plane effect.
      Rather generic, so most telescopes just reuse this class
      """
      prompt = 'PJones: '+self.name()
      help = 'define PJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      if self.execute_body():
         stub = self.unique_nodestub()
         parang = stub('parang') << Meq.Constant(0.0)    # temporary
         cosa = stub('cos') << Meq.Cos(parang)
         sina = stub('sin') << Meq.Sin(parang)
         nsin = stub('neg') << Meq.Negate(sina)
         parot = stub('parot') << Meq.Matrix22(cosa, sina,
                                               nsin, cosa)
         for i,qual in enumerate(self.nodequals()):
            self[i] = parot
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

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the method in JonesClump. Specify the relevant
      choice of solution-specification parameters that will be offered in the
      .solspec() method of its ParmClump ojects.
      Syntax: A list value replaces the entire choice, a number is just used as
      the default, i.e. it is offered as the first value of the default choice list.
      An object-specific help-text may also be offered here. 
      """
      scp = JonesClump.get_solspec_choice_parameters(self)
      self.set_scp (scp, 'tdeg', [1,2], help='solve for low-order time polynomial')
      self.set_scp (scp, 'fdeg', [1,2], help='solve for low-order freq polynomial')
      self.set_scp (scp, 'nfreq_subtile', [None], help='solve over all freq cells')
      self.set_scp (scp, 'ntime_subtile', [None], help='solve over all time cells')
      return scp


   #==========================================================================

   def initexec (self, **kwargs):
      """
      BJones represents electronic bandpass. It is a uv-plane effect.
      It is rather generic, so most telescopes just reuse this class.
      (e.g. see WSRTJones.py).
      """
      prompt = 'BJones: '+self.name()
      help = 'define BJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      # Menu option(s) (the menu itself is generated in .on_entry()):
      self.add_option('mode',['amphas','realimag'])

      if self.execute_body():
         mode = self.getopt('mode')

         # Create ParmClumps:
         if mode=='amphas':
            gerrX = self.make_ParmClump('gerrX', default=1.0)
            perrX = self.make_ParmClump('perrX', default=0.0)
            gerrY = self.make_ParmClump('gerrY', default=1.0)
            perrY = self.make_ParmClump('perrY', default=0.0)
         elif mode=='realimag':
            rerrX = self.make_ParmClump('rerrX', default=1.0)
            ierrX = self.make_ParmClump('ierrX', default=0.0)
            rerrY = self.make_ParmClump('rerrY', default=1.0)
            ierrY = self.make_ParmClump('ierrY', default=0.0)

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



#************************************************************************************

class BcJones(BJones):
   """
   Version of BJones that gives a channel-by-channel solution.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class BJones.
      """
      BJones.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the method in JonesClump. Specify the relevant
      choice of solution-specification parameters that will be offered in the
      .solspec() method of its ParmClump ojects.
      Syntax: A list value replaces the entire choice, a number is just used as
      the default, i.e. it is offered as the first value of the default choice list.
      An object-specific help-text may also be offered here. 
      """
      scp = JonesClump.get_solspec_choice_parameters(self)
      self.set_scp (scp, 'tdeg', [1,2], help='solve for low-order time polynomial')
      self.set_scp (scp, 'fdeg', 0, help='no further freq dependence per channel')
      self.set_scp (scp, 'nfreq_subtile', [1], help='channel-by-channel solutions')
      self.set_scp (scp, 'ntime_subtile', [5,10], help='size of subtile solutions')
      return scp





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
                  ['GJones','JJones','PJones',
                   'BJones','BcJones',
                   'EJones',
                   'JonesClump'],
                  prompt='test Jones:')
   TCM.add_option('simulate',False)

   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      simulate = TCM.getopt('simulate', submenu)
      if jones=='GJones':
         clump = GJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='JJones':
         clump = JJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='PJones':
         clump = PJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='BJones':
         clump = BJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='BcJones':
         clump = BcJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='EJones':
         clump = EJones(ns=ns, TCM=TCM, simulate=simulate)
         c01 = clump.jonesLM(0,1)
         c11 = clump.jonesLM(-1,1)
      else:
         clump = JonesClump(ns=ns, TCM=TCM, simulate=simulate)
         
      solvable = clump.get_solvable(trace=True)
      # clump = CorruptClump.Scatter(clump).daisy_chain()
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
   print '** Start of standalone test of: JonesClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   simulate = False
   # simulate = True

   if 0:
      clump = JonesClump(simulate=simulate, trace=True)

   if 1:
      clump = GJones(simulate=simulate, trace=True)

   if 0:
      clump = PJones(simulate=simulate, trace=True)

   if 0:
      clump = JJones(simulate=simulate, trace=True)

   if 0:
      clump = BJones(simulate=simulate, trace=True)

   if 0:
      clump = BcJones(simulate=simulate, trace=True)

   if 1:
      clump.show('creation', full=True)

   if 1:
      solvable = clump.get_solvable(trace=True)

   if 0:
      p0 = clump.ParmClumps()[0]
      p0.solspec()
      p0.show('p0', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: JonesClump.py:\n' 

#=====================================================================================





