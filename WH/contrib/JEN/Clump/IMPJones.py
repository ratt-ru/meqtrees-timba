"""
IMPJones.py: JonesClump classes that represent image-plane effects.
"""

# file: ../JEN/Clump/IMPJones.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 15 dec 2008: creation (from JonesClump.py)
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

from Timba.Contrib.JEN.Clump import JonesClump
from Timba.Contrib.JEN.Clump import ParmClump
# from Timba.Contrib.JEN.Clump import CorruptClump

from Timba.Contrib.JEN.Expression import Expression

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # 



#********************************************************************************
# The baseclass of all IMPJonesClumps. They contain the methods that are needed
# to generate a JonesClump with MeqCompounder nodes, that is valid for a
# specific direction (L,M).
#********************************************************************************

class IMPJonesClump(JonesClump.JonesClump):
   """
   Derived class from JonesClump.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class JonesClump.
      """
      JonesClump.JonesClump.__init__(self, clump=clump, **kwargs)
      return None


   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the method in JonesClump. This is a better
      default for image-plane effects (...). Specify the relevant
      choice of solution-specification parameters that will be offered in the
      .solspec() method of its ParmClump ojects.
      Syntax: A list value replaces the entire choice, a number is just used as
      the default, i.e. it is offered as the first value of the default choice list.
      An object-specific help-text may also be offered here. 
      """
      scp = JonesClump.JonesClump.get_solspec_choice_parameters(self)
      self.set_scp (scp, 'tdeg', [1,2], help='solve for low-order time polynomial')
      self.set_scp (scp, 'fdeg', [1,2], help='solve for low-order freq polynomial')
      self.set_scp (scp, 'ntime_subtile', [None], help='solve over all time cells')
      self.set_scp (scp, 'nfreq_subtile', [None], help='solve over all freq cells')
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
      ## self.add_option('mode',['amphas','realimag'])
      # exp(-([f]*25/3e8)(1.1*([l]-{l0})**2 + 0.9*([m]-{m0})**2)
      # beamshape = 'exp(-([f]*25/3e8)(1.1*[l]**2 + 0.9*[m]**2))'       # no parameters
      beamshape = '[l]+[m]'
      beamshape = '[l]*[t]+[m]*[f]+{p00}'

      self._beamshape = beamshape
      self.history('EJones beamshape = '+str(self._beamshape))

      self._validity = '([l]*[l]+[m]*[m])<1.2'
      self.history('EJones validity area: '+str(self._validity))

      if self.execute_body():
         ## mode = self.getopt('mode')

         # Create ParmClumps:
         EX = Expression.Expression(self.ns(), self.name()+'_X', beamshape)
         EY = Expression.Expression(self.ns(), self.name()+'_Y', beamshape)
         pcX = self.make_PExpressionClump(EX)
         pcY = self.make_PExpressionClump(EY)

         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            EXname = self.name()+'_X_'+str(qual)
            EYname = self.name()+'_Y_'+str(qual)
            EX = Expression.Expression(self.ns(), EXname, beamshape)
            pcX.replace_Expression_parms(EX)
            EY = Expression.Expression(self.ns(), EYname, beamshape)
            pcY.replace_Expression_parms(EY)
            XX = EX.MeqFunctional(qnode=stub(qual)('X'), show=False)
            YY = EY.MeqFunctional(qnode=stub(qual)('Y'), show=False)
            self[i] = stub(qual) << Meq.Matrix22(Meq.ToComplex(XX,0),0,
                                                 0,Meq.ToComplex(YY,0))
 
         self.end_of_body(ctrl)
      return self.on_exit(ctrl)

   #----------------------------------------------------------------------------
   
   def make_JonesClump(self, L=None, M=None, LM=None, trace=False):
      """Return a JonesClump that is valid for the given direction (L,M).
      It uses the (L,M)-dependent nodes that were defined in .initexec() above.
      The L,M coordinates may be numbers, or nodes, or a composer (L,M).
      NB: All image-plane IMPJoness have this function!
      NB: If the position (L,M) is outside the 'validity area' of the IMPJones,
      return a basic JonesClump that represents the (relative?) 'complex gain' in
      this direction.
      NB: Some internal bookkeeping avoids duplication of IMPJoness....
      """
      
      # Make sure of an extra_axes composer node (L,M)
      if LM:
         stub = self.unique_nodestub()  
         extra_axes = LM
      elif is_node(L) and is_node(M):
         stub = self.unique_nodestub()  
         extra_axes = stub('extra_axes') << Meq.Composer(L,M)
      elif isinstance(L,(float,int)) and isinstance(M,(float,int)):
         LMname = '(L='+str(L)+',M='+str(M)+')'
         stub = self.unique_nodestub()(LMname)  
         extra_axes = stub('extra_axes') << Meq.Composer(L,M)
      else:
         s = 'type of (L,M) not recocnised: '+str(type(L))+','+str(type(M)) 
         raise ValueError,s


      # Create the output JonesClump:
      if not self.inside_validity_area(L,M):
         # The given (L,M) may be outside the validity-area of the EJones:
         clump = self.outside_validity_area(LMname)
      else:
         # Create a IMPJones with MeqCompounder nodes for (L,M):
         clump = JonesClump.JonesClump(self, name=LMname)
         common_axes = [hiid('L'),hiid('M')]
         for i,qual in enumerate(self.nodequals()):
            node = stub('compounder')(qual) << Meq.Compounder(extra_axes, self[i],
                                                              common_axes=common_axes)
            # self.core._orphans.append(node)           # temporary
            clump[i] = node

      # Always return a JonesClump for the given (L,M):
      if trace:
         print '.make_JonesClump(',L,M,LM,') -> ',clump.oneliner()
      return clump


   #============================================================================
   # Functions related to the validity-area of this image-plane effect
   #============================================================================

   def inside_validity_area(self, L, M, trace=False):
      """Check whether (L,M) is outside the given validity-area of the EJones.
      Return True (inside) or False (outside).
      If no self._validity python expression found, return True (assume inside).
      """
      if not getattr(self,'_validity',None):      # no expression found
         return True                                # assume inside....
      expr = self._validity                       # Asssume python expression
      if trace:
         print '\n** outside_validity_area(',L,M,'):',expr
      expr = expr.replace('[l]',str(L))
      expr = expr.replace('[m]',str(M))
      try:
         inside = eval(expr)
      except:
         print '\n** outside_validity_area(',L,M,'):',expr,'  (ERROR)'
      if trace:
         print '       -> inside =',inside,'\n'
      # Return True or False
      return inside

   #----------------------------------------------------------------------------

   def outside_validity_area(self, LMname):
      """If (L,M) is outside the given validity-area of the EJones,
      return a general IMPJones that solves for the complex gain
      in that direction (i.e. peeling if sources in the beam sidelobes).
      """
      clump = JonesClump.JJones(self, name=LMname)
      self.history('outside validity area: '+clump.oneliner())
      return clump






#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
# EJones (primary beamshape):
#********************************************************************************

class EJones(IMPJonesClump):
   """
   Derived class from IMPJones.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class IMPJones.
      """
      IMPJonesClump.__init__(self, clump=clump, **kwargs)
      return None


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
      beamshape = '[l]*[t]+[m]*[f]+{p00}'

      self._beamshape = beamshape
      self.history('EJones beamshape = '+str(self._beamshape))

      self._validity = '([l]*[l]+[m]*[m])<1.2'
      self.history('EJones validity area: '+str(self._validity))

      if self.execute_body():
         # mode = self.getopt('mode')

         # Create ParmClumps:
         EX = Expression.Expression(self.ns(), self.name()+'_X', beamshape)
         EY = Expression.Expression(self.ns(), self.name()+'_Y', beamshape)
         pcX = self.make_PExpressionClump(EX)
         pcY = self.make_PExpressionClump(EY)

         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            EXname = self.name()+'_X_'+str(qual)
            EYname = self.name()+'_Y_'+str(qual)
            EX = Expression.Expression(self.ns(), EXname, beamshape)
            pcX.replace_Expression_parms(EX)
            EY = Expression.Expression(self.ns(), EYname, beamshape)
            pcY.replace_Expression_parms(EY)
            XX = EX.MeqFunctional(qnode=stub(qual)('X'), show=False)
            YY = EY.MeqFunctional(qnode=stub(qual)('Y'), show=False)
            print str(XX),str(YY)
            self[i] = stub(qual) << Meq.Matrix22(Meq.ToComplex(XX,0),0,
                                                 0,Meq.ToComplex(YY,0))
            print str(self[i])
 
         self.end_of_body(ctrl)
      return self.on_exit(ctrl)







#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************

class FullJones(JonesClump.JonesClump):
   """
   The FullJones class represents a sequence (multiplication) of all the
   (uv-plane) JonesClumps and (image-plane) IMPJonesClumps that fully describe
   the instrumental effects of a given radio telescope.
   For derived classes (e.g. WSRTJones or VLAJones etc) , just reimplement
   the method .define_jones_sequence() with one that contains another
   sequence of JonesClumps and IMPJonesClumps.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class JonesClump.
      """
      self._IMPJonesClumps = []       # list of image-plane IMPJonesClumps
      self._JonesClumps = []          # list of uv-plane JonesClumps
      self._UVPJones = None           # JonesClump with multiplied uv-plane matrices
      JonesClump.JonesClump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================

   def initexec (self, **kwargs):
      """
      Re-implemented version of the function in the baseclass (LeafClump).
      NB: This function is generic. Classes derived from FullJones should
      just re-implement its method .define_jones_sequence() below.
      See e.g. class WSRTJones.WSRTJones.
      """
      prompt = 'FullJones: '+str(self.name())
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
         self.define_jones_sequence(**kwargs)
         self.end_of_body(ctrl)

      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------

   def define_jones_sequence(self, **kwargs):
      """Function to be re-implemented in classes derived from UVPJones.
      See e.g. the class WSRTJones.WSRTJones, or VLAJones.VLAJones.
      """
      # The number and names of the stations/antennas of the array are
      # specified by means of a list of station/antenna tree qualifiers.
      treequals = range(1,5) 
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # Make a list of JonesClumps in the correct order (of the M.E.).
      # The ones selected (by the user) will be matrix-multiplied.

      # First the image-plane effects:
      self._IMPJonesClumps.append(IMPJonesClump(self, name='XJones', **kwargs))
      self._IMPJonesClumps.append(IMPJonesClump(self, name='YJones', **kwargs))
      self._IMPJonesClumps.append(IMPJonesClump(self, name='ZJones', **kwargs))

      # Then the uv-plane effects:
      self._JonesClumps.append(JonesClump.JonesClump(self, name='AJones', **kwargs))
      self._JonesClumps.append(JonesClump.JonesClump(self, name='BJones', **kwargs))
      self._JonesClumps.append(JonesClump.JonesClump(self, name='CJones', **kwargs))

      return True


   #============================================================================
   #============================================================================

   def make_JonesClump(self, L=None, M=None, LM=None, trace=False):
      """Make a single Jones matrix from the ones collected in .initexex()
      This function is generic, i.e. it should NOT be re-implemented in
      classes that are derived from IMPJones. It contains more specialist code,
      which should not be seen by the uninitiated.
      """

      # First make a single uv-plane JonesClump:
      self.make_UVPJones(trace=trace)

      # Then get the list of L,M-manifestations of the selected
      # (image-plane) IMPJonesClumps:
      jj = []                                   # list of selected Jones matrices
      notsel = []                               # list of not selected ones
      for i,jc in enumerate(self._IMPJonesClumps):
         if jc.is_selected():
            jj.append(jc.make_JonesClump(L=L, M=M, LM=LM, trace=trace))
         else:
            notsel.append(jc)

      # Make a single JonesClump that is valid for the given (L,M):
      if len(jj)==0:                            # No IMPJonesClumps selected:
         if not self._UVPJones==False:
            clump = self._UVPJones              # use the uv-plane effects only
         else:
            self.history('empty Jones list: make a 2x2 complex unit matrix')
            stub = self.unique_nodestub('unitmatrix')
            for i,qual in enumerate(self.nodequals()):
               self[i] = stub(qual) << Meq.Matrix22(complex(1,0), complex(0,0),
                                                    complex(0,0), complex(1,0))

      elif len(jj)==1 and self._UVPJones==False:
         clump = self                           # use the one IMPJonesClump

      else:                                     # MatrixMyultiply
         clump = JonesClump.JonesClump(self, name='IMPJones')
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            cc = []
            if self._UVPJones:
               cc.append(self._UVPJones[i])     # the uv-plane jones
            for jones in jj:
               cc.append(jones[i])              # the image-plane jones
            clump[i] = stub(qual) << Meq.MatrixMultiply(*cc)
         self. check_polarization(jj, trace=trace)

      # Almost finished:
      self.deal_with_notsel(notsel, trace=trace) 
      return clump
      

   #----------------------------------------------------------------------------

   def make_UVPJones(self, trace=False):
      """Make a uv-plane JonesClump by matrix-multiplication of the (selected)
      uv-plane JonesClumps in the list self._JonesClumps.
      Put the result in self._UVPJones (i.e. do this only once).
      If none selected, self._UVPJones = False (...?)
      """
      if not self._UVPJones==None:
         return True                               # do only once
         
      # First get the list of selected (uv-plane) JonesClumps:
      jj = []                                   # list of selected Jones matrices
      notsel = []                               # list of not selected ones
      for i,jc in enumerate(self._JonesClumps):
         if jc.is_selected():
            jj.append(jc)
         else:
            notsel.append(jc)

      if len(jj)==0:                            # None selected: 
         self._UVPJones = False
         self.history('no uv-plane Jones matrices selected')

      elif len(jj)==1:                          # only one selected: use itself
         self._UVPJones = self
      
      else:                                     # more than one: MatrixMyultiply
         clump = JonesClump.JonesClump(self, name='UVPJones')
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            cc = []
            for jones in jj:
               cc.append(jones[i])
            clump[i] = stub(qual) << Meq.MatrixMultiply(*cc)
         self. check_polarization(jj, trace=trace)
         self._UVPJones = clump

      # Almost finished:
      self.deal_with_notsel(notsel, trace=False) 
      return True

   #---------------------------------------------------------------------
         
   def check_polarization(self, jj, trace=False): 
      """Check the polarization representations (linear/circular/None)
      """
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
      return True
   

   #--------------------------------------------------------------------
   
   def deal_with_notsel(self, notsel, trace=False): 
      """Deal with the Jones matrices that were NOT selected"""
      if isinstance(notsel,list):
         for jones in notsel:
            # print '- not selected:',jones.oneliner()
            jones.connect_loose_ends (self, full=False)
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
                   ['IMPJonesClump','EJones',
                   'FullJones'],
                  prompt='test Jones:')
   TCM.add_option('simulate',False)

   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      simulate = TCM.getopt('simulate', submenu)
      if jones=='IMPJonesClump':
         clump = IMPJonesClump(ns=ns, TCM=TCM, simulate=simulate)
         c01 = clump.jonesLM(0,1)
         c01.show('c01', full=True)
         # c11 = clump.jonesLM(-1,1)
      elif jones=='EJones':
         clump = EJones(ns=ns, TCM=TCM, simulate=simulate)
         c01 = clump.jonesLM(0,1)
         c11 = clump.jonesLM(-1,1)
      else:
         clump = FullJones(ns=ns, TCM=TCM, simulate=simulate)
         
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
   print '** Start of standalone test of: IMPJones.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   simulate = False
   # simulate = True

   if 1:
      clump = IMPJonesClump(simulate=simulate, trace=True)
      if True:
         c01 = clump.make_JonesClump(0,1)
         # c01.show('c01', full=True)
         # c01 = clump.jonesLM(-1,1)
         # c01 = clump.jonesLM(0,1)

   if 0:
      clump = EJones(simulate=simulate, trace=True)
      if False:
         c01 = clump.jonesLM(0,1)
         c01 = clump.jonesLM(-1,1)
         c01 = clump.jonesLM(0,1)

   if 0:
      clump = FullJones(simulate=simulate, trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      solvable = clump.get_solvable(trace=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: IMPJones.py:\n' 

#=====================================================================================





