"""
WSRTJones.py: Contains all WSRT-specific Jones matrices (G,D,F,E etc),
and WSRTJones.WSRTJones(UVPJones) to produce a Jones sequence (multiplication).
"""

# file: ../JEN/Clump/WSRTJones.py:
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

from Timba.Contrib.JEN.Clump import JonesClump
# from Timba.Contrib.JEN.Clump import IMPJones
from Timba.Contrib.JEN.Clump import ParmClump
# from Timba.Contrib.JEN.Clump import CorruptClump

import math                 # support math.cos() etc
import numpy                # support numpy.array() etc




#********************************************************************************
#********************************************************************************
#********************************************************************************      


def fill_WSRT_rider(clump, **kwargs):
   """Helper function, to be called by all WSRTJones classes.
   It fills the 'rider' dict of the given (WSRT) JonesClump
   with WSRT-related information like telescope positions etc.
   """
   trace = kwargs.get('trace', False)

   # 1D positions of the WSRT telescopes (m):
   if clump.rider('xpos', default=None)==None:      # do only once
      sep9A = kwargs.get('sep9A', 72.0)             # separation 9-A (m)
      xx = numpy.array(range(14))*144.0
      xx[10] = xx[9] + sep9A                        # A
      xx[11] = xx[10] + 72                          # B
      xx[12] = xx[9] + (xx[10]-xx[0])               # C
      xx[13] = xx[12] + 72                          # D
      clump.rider('sep9A', set=sep9A)
      clump.rider('xpos', set=xx)

   if trace:
      clump.rider(trace=True)
   return None
   



#*****************************************************************************      
#********************************************************************************
# WSRTJones.WSRTJones is a multiplication of (WSRT) Jones Clumps
#********************************************************************************

class WSRTJones(JonesClump.UVPJones):
   """
   This JonesClump represents a sequence (multiplication) of JonesClumps,
   specific for the Westerbork Synthesis Radio Telescope (WSRT).
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      JonesClump.UVPJones.__init__(self, clump=clump, **kwargs)
      # fill_WSRT_rider(self, **kwargs):
      return None

   #------------------------------------------------------------------------

   def make_jones_sequence(self, **kwargs):
      """Function to be re-implemented in classes derived from UVPJones.
      Called by .initexec() above (which is generic in UVPJones classes). 
      """
      # The number and names of the stations/antennas of the array are
      # specified by means of a list of station/antenna tree qualifiers.
      treequals = range(10)+list('ABCD')          # list of WSRT telescopes
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # Make a list of JonesClumps in the correct order (of the M.E.).
      # The ones selected (by the user) will be matrix-multiplied. 
      # self.JonesClumps(EJones(self, **kwargs))
      # self.JonesClumps(RJones(self, **kwargs))
      self.JonesClumps(FJones(self, **kwargs))
      self.JonesClumps(GJones(self, **kwargs))
      self.JonesClumps(BJones(self, **kwargs))
      self.JonesClumps(BcJones(self, **kwargs))
      # self.JonesClumps(DJones(self, **kwargs))

      return True




#*****************************************************************************      
#*****************************************************************************      

class GJones(JonesClump.GJones):
   """
   Represents electronic gain.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Just use the JonesClump base class, with a different name.
      """
      kwargs['name'] = 'GJones'
      kwargs['qual'] = 'WSRT'
      kwargs['polrep'] = None
      JonesClump.GJones.__init__(self, clump=clump, **kwargs)
      fill_WSRT_rider(self, **kwargs)
      return None


#*****************************************************************************      
#*****************************************************************************      

class BJones(JonesClump.BJones):
   """
   Represents electronic bandpass.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Just use the JonesClump base class, with a different name.
      """
      kwargs['name'] = 'BJones'
      kwargs['qual'] = 'WSRT'
      kwargs['polrep'] = None
      JonesClump.BJones.__init__(self, clump=clump, **kwargs)
      fill_WSRT_rider(self, **kwargs)
      return None

#----------------------------------------------------------------------------

class BcJones(JonesClump.BcJones):
   """
   Represents channel-by-channel electronic bandpass.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Just use the JonesClump base class, with a different name.
      """
      kwargs['name'] = 'BcJones'
      kwargs['qual'] = 'WSRT'
      kwargs['polrep'] = None
      JonesClump.BcJones.__init__(self, clump=clump, **kwargs)
      fill_WSRT_rider(self, **kwargs)
      return None


#*****************************************************************************      
#*****************************************************************************      

class FJones(JonesClump.JonesClump):
   """
   Represents ionospheric Faraday rotation.
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class JonesClump.
      """
      kwargs['name'] = 'FJones'
      kwargs['qual'] = 'WSRT'
      kwargs['polrep'] = 'linear'
      JonesClump.JonesClump.__init__(self, clump=clump, **kwargs)
      fill_WSRT_rider(self, **kwargs)
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
      Fill the LeafClump object with suitable leaf nodes.
      The faraday rotation is a low-order polynomial over the 3km 1D array.
      """

      prompt = 'FJones: '+self.name()
      help = 'define FJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('poly',['{p0}+{p1}*[x]',
                              '{p0}+{p1}*[x]+{p2}*[x]*[x]'],
                      help='low-order polynomial over 1D array')

      if self.execute_body():
         poly = self.getopt('poly')

         # Make a Clump with parametrized MeqFunctionals:
         fill_WSRT_rider(self, **kwargs)                        # makes xpos
         varvals = dict(x=self.rider('xpos'))
         farot = self.make_PFunctionalClump('farot', expr=poly,
                                            varvals=varvals)
         # Generate nodes:
         stub = self.unique_nodestub()
         for i,qual in enumerate(self.nodequals()):
            cos = stub('cos')(qual) << Meq.Cos(farot[i])
            sin = stub('sin')(qual) << Meq.Sin(farot[i])
            neg = stub('neg')(qual) << Meq.Negate(sin)
            self[i] = stub(qual) << Meq.Matrix22(cos, sin,
                                                 neg, cos)
         self.end_of_body(ctrl)
      return self.on_exit(ctrl)





#*****************************************************************************      
#*****************************************************************************      
#*****************************************************************************      
#*****************************************************************************      

class XJones(JonesClump.JonesClump):
   """
   Derived class 
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class JonesClump.
      """
      JonesClump.JonesClump.__init__(self, clump=clump, **kwargs)
      fill_WSRT_rider(self, **kwargs)
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
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      prompt = 'XJones: '+self.name()
      help = 'define Jones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('mode',['amphas','realimag'])

      if self.execute_body():
         mode = self.getopt('mode')

         # Create ParmClumps:
         if mode=='amphas':
            gerrX = self.make_ParmClump(name='gerrX', default=1.0)
            perrX = self.make_ParmClump(name='perrX', default=0.0)
            gerrY = self.make_ParmClump(name='gerrY', default=1.0)
            perrY = self.make_ParmClump(name='perrY', default=0.0)
         elif mode=='realimag':
            rerrX = self.make_ParmClump(name='rerrX', default=1.0)
            ierrX = self.make_ParmClump(name='ierrX', default=0.0)
            rerrY = self.make_ParmClump(name='rerrY', default=1.0)
            ierrY = self.make_ParmClump(name='ierrY', default=0.0)

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
                  ['WSRTJones',
                   # 'RJones','EJones','ZJones',
                   'GJones','BJones','BcJones','FJones'],
                  prompt='test WSRT Jones:')
   TCM.add_option('simulate',False)

   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      simulate = TCM.getopt('simulate', submenu)
      treequals = range(10)+list('ABCD')          # list of WSRT telescopes

      if jones=='WSRTJones':
         clump = WSRTJones(ns=ns, TCM=TCM, treequals=treequals, simulate=simulate)
      elif jones=='GJones':
         clump = GJones(ns=ns, TCM=TCM, treequals=treequals, simulate=simulate)
      elif jones=='BJones':
         clump = BJones(ns=ns, TCM=TCM, treequals=treequals, simulate=simulate)
      elif jones=='BcJones':
         clump = BcJones(ns=ns, TCM=TCM, treequals=treequals, simulate=simulate)
      elif jones=='FJones':
         clump = FJones(ns=ns, TCM=TCM, treequals=treequals, simulate=simulate)
                  
      solvable = clump.get_solvable(trace=True)
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
   print '** Start of standalone test of: WSRTJones.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   treequals = range(10)+list('ABCD')          # list of WSRT telescopes
   simulate = False

   if 0:
      clump = WSRTJones(treequals=treequals,
                        simulate=simulate,
                        trace=True)

   if 0:
      clump = GJones(treequals=treequals,
                     simulate=simulate,
                     trace=True)

   if 0:
      clump = BJones(treequals=treequals,
                     simulate=simulate,
                     trace=True)

   if 1:
      clump = FJones(treequals=treequals,
                     simulate=simulate,
                     trace=True)

   if 0:
      clump = XJones(treequals=treequals,
                     simulate=simulate,
                     trace=True)

   #------------------------------------------------
   if 1:
      clump.show('creation', full=True)
   #------------------------------------------------

   if 0:
      pc = clump.ParmClumps()[0]
      pc.show('PC[0]')

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: WSRTJones.py:\n' 

#=====================================================================================





