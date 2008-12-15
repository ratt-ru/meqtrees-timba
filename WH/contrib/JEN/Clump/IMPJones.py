"""
IMPJones.py: Base-class for JonesClumps that represent image-plane effects.
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

class IMPJonesClump(JonesClump):
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
      scp = JonesClump.get_solspec_choice_parameters(self)
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

   #--------------------------------------------------------------------------

   def jonesLM (self, L=None, M=None, LM=None, **kwargs):
      """Create and return a new IMPJones for EJones in the given direction (L,M).
      It uses the (L,M)-dependent nodes that were defined in .initexec() above.
      The L,M coordinates may be numbers, or nodes, or a composer (L,M).
      NB: All image-plane IMPJoness have this function!
      NB: If the position (L,M) is outside the 'validity area' of the IMPJones,
      return a basis IMPJones that represents the (relative?) 'complex gain' in
      this direction.
      NB: Some internal bookkeeping avoids duplication of IMPJoness....
      """
      if LM:
         stub = self.unique_nodestub()  
         extra_axes = LM
      elif is_node(L) and is_node(M):
         stub = self.unique_nodestub()  
         extra_axes = stub('extra_axes') << Meq.Composer(L,M)
      elif isinstance(L,(float,int)) and isinstance(M,(float,int)):
         LMname = '(L='+str(L)+',M='+str(M)+')'
         stub = self.unique_nodestub()(L=L)(M=M)  
         extra_axes = stub('extra_axes') << Meq.Composer(L,M)
      else:
         s = 'type of (L,M) not recocnised: '+str(type(L))+','+str(type(M)) 
         raise ValueError,s

      # Check if a clump with this particular LMname already exists:
      clump = self.IMPJoness(LMname)
      if clump:
         # The clump LMname has been defined already. Return it.
         pass
      elif not self.inside_validity_area(L,M):
         # The given (L,M) may be outside the validity-area of the EJones:
         clump = self.outside_validity_area(LMname)
      else:
         # Create a IMPJones with MeqCompounder nodes for (L,M):
         clump = IMPJones(self, name=LMname)
         common_axes = [hiid('L'),hiid('M')]
         for i,qual in enumerate(self.nodequals()):
            node = stub('compounder')(qual) << Meq.Compounder(extra_axes, self[i],
                                                              common_axes=common_axes)
            self.core._orphans.append(node)           # temporary
            clump[i] = node
         self.IMPJoness(LMname, clump)              # keep for (possible) later use

      # Always return a IMPJones for the given (L,M):
      return clump


   #----------------------------------------------------------------------------

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
      clump = JJones(self, name=LMname)
      self.IMPJoness(LMname, clump)              # keep for (possible) later use
      self.history('outside validity area: '+clump.oneliner())
      return clump




#********************************************************************************
#********************************************************************************
# EJones (primary beamshape):
#********************************************************************************

class EJones(IMPJones):
   """
   Derived class from IMPJones.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class IMPJones.
      """
      IMPJones.__init__(self, clump=clump, **kwargs)
      return None

   #-------------------------------------------------------------------------

   def get_solspec_choice_parameters(self):
      """Re-implementation of the method in IMPJones. Specify the relevant
      choice of solution-specification parameters that will be offered in the
      .solspec() method of its ParmClump ojects.
      Syntax: A list value replaces the entire choice, a number is just used as
      the default, i.e. it is offered as the first value of the default choice list.
      An object-specific help-text may also be offered here. 
      """
      scp = IMPJones.get_solspec_choice_parameters(self)
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
# IMPJones.IMPJones is a multiplication of JonesClumps that are valid for a
# specific sky direction (L,M). It may contain uv-plane JonesClumps, and
# the (L,M) versions of image-plane ones.  
#********************************************************************************

class IMPJones(IMPJonesClump):
   """
   This IMPJones represents a sequence (multiplication) of JonesClumps
   that represent uv-plane effects (for image-plane, see IMPJones.py)
   For derived classes, just replace .initexec() with your own sequence of
   uv-plane JonesClumps.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      IMPJones.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================

   def initexec (self, **kwargs):
      """
      Re-implemented version of the function in the baseclass (LeafClump).
      NB: This function is generic. Classes derived from IMPJones should
      just re-implement its method .make_jones_sequence() below.
      See e.g. class WSRTJones.WSRTJones.
      """
      prompt = 'IMPJones: '+str(self.name())
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
         (jj,notsel) = self.make_jones_sequence(**kwargs)
         self.make_single_jones(jj, notsel)
         self.end_of_body(ctrl)

      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------

   def make_jones_sequence(self, **kwargs):
      """Function to be re-implemented in classes derived from IMPJones.
      See e.g. the class WSRTJones.WSRTJones, or VLAJones.VLAJones.
      Called by .initexec() above (which is generic in IMPJones classes). 
      """
      # The number and names of the stations/antennas of the array are
      # specified by means of a list of station/antenna tree qualifiers.
      treequals = range(8,10)+list('AB')                   # default: WSRT 
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # Make a list of JonesClumps in the correct order (of the M.E.).
      # The ones selected (by the user) will be matrix-multiplied. 
      jj = []                       # list of selected Jones matrices
      notsel = []                   # list of not selected ones
      IMPJones(self, name='AJones', **kwargs).append_if_selected(jj, notsel)
      IMPJones(self, name='BJones', **kwargs).append_if_selected(jj, notsel)
      IMPJones(self, name='CJones', **kwargs).append_if_selected(jj, notsel)
      return (jj,notsel)


   #============================================================================
   #============================================================================

   def make_single_jones(self, jj, notsel=None):
      """Make a single Jones matrix from the ones collected in .initexex()
      This function is generic, i.e. it should NOT be re-implemented in
      classes that are derived from IMPJones. It contains more specialist code,
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
      # its own list of ParmClumps (self.make_ParmClumps()).
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
                   ['EJones',
                   'IMPJones'],
                  prompt='test Jones:')
   TCM.add_option('simulate',False)

   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      simulate = TCM.getopt('simulate', submenu)
      if jones=='EJones':
         clump = EJones(ns=ns, TCM=TCM, simulate=simulate)
         c01 = clump.jonesLM(0,1)
         c11 = clump.jonesLM(-1,1)
      else:
         clump = IMPJones(ns=ns, TCM=TCM, simulate=simulate)
         
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

   if 0:
      clump = IMPJones(simulate=simulate, trace=True)

   if 0:
      clump = EJones(simulate=simulate, trace=True)
      if False:
         c01 = clump.jonesLM(0,1)
         c01 = clump.jonesLM(-1,1)
         c01 = clump.jonesLM(0,1)

   if 1:
      clump.show('creation', full=True)

   if 1:
      solvable = clump.get_solvable(trace=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: IMPJones.py:\n' 

#=====================================================================================





