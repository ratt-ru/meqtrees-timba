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

      # Make a dict of MeqParm arguments (used in Meq.Parm() below)
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

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Placeholder function for the specification of solspec parameters.
      """
      # The following dict is a placeholder for "solspec" parameters,
      # which are given as **kwargs arguments to ParmClump constructors.
      # It may be re-specified in .__init__() of derived JonesClump classes.
      scp = dict()
      # set_scp (scp, 'tdeg', value, help=None)
      # set_scp (scp, 'fdeg', value, help=None)
      # set_scp (scp, 'nfreq_subtile', value, help=None)
      # set_scp (scp, 'ntime_subtile', value, help=None)
      return scp

   #..........................................................................

   def set_scp (self, rr, name, value, help=None):
      """Helper function to be called from .get_solspec_choice_parameters()
      """
      rr[name] = value
      hname = 'optionhelp'
      if not isinstance(help,str):
         help = 'autohelp'               # generate automatic help, using value
      rr[hname] = help
      return rr

   #--------------------------------------------------------------------------

   def ParmClump(self, name, default=0.0, trace=False):
      """Helper function to create a ParmClump in an organised way.
      """
      # NB: The following function will be re-implemented in a derived class
      self._solspec_choice = self.get_solspec_choice_parameters()
      clump = ParmClump.ParmClump(self, name=name,
                                  default=default,
                                  simulate=self._simulate,
                                  **self._solspec_choice)
      if trace:
         clump.show('JonesClump.ParmClump()')
      self.connect_grafted_clump(clump)       # connect the loose ends:
      return clump

   #--------------------------------------------------------------------------

   def PFunctionalClump(self, name, expr, varvals=None, trace=False):
      """Helper function to create a PFunctionalClump in an organised way.
      """
      # NB: The following function will be re-implemented in a derived class
      self._solspec_choice = self.get_solspec_choice_parameters()
      clump = ParmClump.PFunctionalClump(name=name,
                                         expr=expr, varvals=varvals,
                                         TCM=self.TCM(), ns=self.ns(),
                                         simulate=self._simulate,
                                         **self._solspec_choice)
      if trace:
         clump.show('JonesClump.PFunctionalClump()')
      self.connect_grafted_clump(clump)      # connect the loose ends
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
         # r00.show('inside')
         # self.show('inside')
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            # print '-',i,qual,r00[i],i00[i]
            elem00 = stub(qual)('00') << Meq.ToComplex(r00[i],i00[i])
            elem01 = stub(qual)('10') << Meq.ToComplex(r01[i],i01[i])
            elem10 = stub(qual)('01') << Meq.ToComplex(r01[i],i01[i])
            elem11 = stub(qual)('11') << Meq.ToComplex(r11[i],i11[i])
            self[i] = stub(qual) << Meq.Matrix22(elem00, elem01,
                                                 elem10, elem11)

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

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the function in JonesClump.
      Specify the relevant choice of solution-specification parameters that
      will be offered in the .solspec() function of its ParmClump ojects.
      (A list repaces the default choice, a number is used as default.) 
      """
      scp = dict(nfreq_subtile=[None],   # solve over all freq cells 
                 ntime_subtile=[5,10],   # size of subtile solutions
                 fdeg=0,                 # default: no freq dependence
                 tdeg=[1,2])             # solve for low-order time polynomial
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

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the function in JonesClump.
      Specify the relevant choice of solution-specification parameters that
      will be offered in the .solspec() function of its ParmClump ojects.
      (A list repaces the default choice, a number is used as default.) 
      """
      scp = dict(ntime_subtile=[None],   # solve over all freq cells 
                 nfreq_subtile=[5,10],   # size of subtile solutions
                 fdeg=0,                 # default: no freq dependence
                 tdeg=[1,2])             # solve for low-order time polynomial
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
      """Re-implementation of the function in JonesClump/BJones.
      Specify the relevant choice of solution-specification parameters that
      will be offered in the .solspec() function of its ParmClump ojects.
      (A list repaces the default choice, a number is used as default.) 
      """
      scp = dict(ntime_subtile=[None],   # solve over all time cells 
                 nfreq_subtile=[1],      # channel-by-channel solution
                 fdeg=0,                 # default: no freq dependence
                 tdeg=[1,2])             # solve for low-order time polynomial
      return scp



#********************************************************************************
# EJones (primary beamshape):
#********************************************************************************

class EJones(JonesClump):
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
      """Re-implementation of the function in JonesClump.
      Specify the relevant choice of solution-specification parameters that
      will be offered in the .solspec() function of its ParmClump ojects.
      (A list repaces the default choice, a number is used as default.) 
      """
      scp = dict(ntime_subtile=[None],   # solve over all freq cells 
                 nfreq_subtile=[5,10],   # size of subtile solutions
                 fdeg=0,                 # default: no freq dependence
                 tdeg=[1,2])             # solve for low-order time polynomial
      return scp


   #==========================================================================

   def initexec (self, **kwargs):
      """
      EJones represents the primary beamshape. It is an image-plane effect.
      """
      prompt = 'EJones: '+self.name()
      help = 'define EJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      # Menu option(s) (the menu itself is generated in .on_entry()):
      # self.add_option('mode',['amphas','realimag'])
      # exp(-([f]*25/3e8)(1.1*([l]-{l0})**2 + 0.9*([m]-{m0})**2)
      beamshape = 'exp(-([f]*25/3e8)(1.1*[l]**2 + 0.9*[m]**2))'       # no parameters
      beamshape = '[l]+[m]'
      self._beamshape = beamshape

      if self.execute_body():
         # mode = self.getopt('mode')

         # Create ParmClumps:
         # E = Expression.Expression(self.ns(), self.name(), beamshape)
         # pc = E.ParmClump()...?

         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            Ename = self.name()+'_'+str(qual)
            E = Expression.Expression(self.ns(), Ename, beamshape)
            self[i] = E.MeqFunctional(qnode=stub(qual), show=False)
 
         self.end_of_body(ctrl)
      return self.on_exit(ctrl)

   #--------------------------------------------------------------------------

   def jonesLM (self, L=None, M=None, LM=None, **kwargs):
      """Create and return a new JonesClump for EJones in the given direction (L,M).
      It uses the (L,M)-dependent nodes that were defined in .initexec() above.
      The L,M coordinates may be numbers, or nodes, or a composer (L,M).
      NB: All image-plane JonesClumps have this function!
      NB: If the position (L,M) is outside the 'validity area' of the JonesClump,
      return a basis JonesClump that represents the (relative?) 'complex gain' in
      this direction.
      NB: Some internal bookkeeping avoids duplication of JonesClumps....
      """
      common_axes = [hiid('L'),hiid('M')]
      if LM:
         stub = self.unique_nodestub()  
         extra_axes = LM
      elif is_node(L):
         stub = self.unique_nodestub()  
         extra_axes = stub('extra_axes') << Meq.Composer(L,M)
      else:
         stub = self.unique_nodestub()(L=L)(M=M)  
         extra_axes = stub('extra_axes') << Meq.Composer(L,M)

      clump = JonesClump(self, name='jonesLM')
      for i,qual in enumerate(self.nodequals()):
         node = stub('compounder')(qual) << Meq.Compounder(extra_axes, self[i],
                                                           common_axes=common_axes)
         clump[i] = node
      clump.show('jonesLM')
      return clump

   


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
      NB: This function is generic. Classes derived from XXXJones should
      re-implement .make_jones_sequence() below.
      See e.g. class WSRTJones.WSRTJones.
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
      """Function to be re-implemented in classes derived from XXXJones.
      See e.g. the class WSRTJones.WSRTJones, or VLAJones.VLAJones.
      Called by .initexec() above (which is generic in XXXJones classes). 
      """
      # The number and names of the stations/antennas of the array are
      # specified by means of a list of station/antenna tree qualifiers.
      treequals = range(8,10)+list('AB')                   # default: WSRT 
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # Make a list of JonesClumps in the correct order (of the M.E.).
      # The ones selected (by the user) will be matrix-multiplied. 
      jj = []                       # list of selected Jones matrices
      notsel = []                   # list of not selected ones
      JonesClump(self, name='AJones', **kwargs).append_if_selected(jj, notsel)
      JonesClump(self, name='BJones', **kwargs).append_if_selected(jj, notsel)
      JonesClump(self, name='CJones', **kwargs).append_if_selected(jj, notsel)
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
                   'GJones','BJones','EJones'],
                  prompt='test WSRT Jones:')
   TCM.add_option('simulate',False)

   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      simulate = TCM.getopt('simulate', submenu)
      if jones=='GJones':
         clump = GJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='BJones':
         clump = BJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='EJones':
         clump = EJones(ns=ns, TCM=TCM, simulate=simulate)
      elif jones=='XXXJones':
         clump = XXXJones(ns=ns, TCM=TCM, simulate=simulate)
      else:
         clump = JonesClump(ns=ns, TCM=TCM, simulate=simulate)
         
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
   simulate = False

   if 0:
      clump = JonesClump(simulate=simulate, trace=True)

   if 1:
      clump = JJones(simulate=simulate, trace=True)

   if 0:
      clump = GJones(simulate=simulate, trace=True)

   if 0:
      clump = EJones(simulate=simulate, trace=True)
      c01 = clump.jonesLM(0,1)

   if 0:
      clump = BJones(simulate=simulate, trace=True)

   if 0:
      clump = BcJones(simulate=simulate, trace=True)

   if 0:
      clump = XXXJones(simulate=simulate, trace=True)

   if 1:
      clump.show('creation', full=True)

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





