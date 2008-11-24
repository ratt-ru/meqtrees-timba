"""
WSRTJones.py: Contains all WSRT-specific Jones matrices (G,D,F,E etc),
and WSRTJones.WSRTJones(XXXJones) to produce a Jones sequence (multiplication).
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
from Timba.Contrib.JEN.Clump import ParmClump
# from Timba.Contrib.JEN.Clump import CorruptClump

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc



#********************************************************************************
#********************************************************************************

#********************************************************************************
# WSRTJones.XXXJones is a multiplication of Jones Clumps
#********************************************************************************

class WSRTJones(JonesClump.XXXJones):
   """
   This JonesClump represents a sequence (multiplication) of JonesClumps,
   specific for the Westerbork Synthesis Radio Telescope (WSRT).
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      JonesClump.XXXJones.__init__(self, clump=clump, **kwargs)
      return None

   #------------------------------------------------------------------------

   def make_jones_sequence(self, **kwargs):
      """Function to be re-implemented in classes derived from XXXJones.
      Called by .initexec() above (which is generic in XXXJones classes). 
      """
      # The number and names of the stations/antennas of the array are
      # specified by means of a list of station/antenna tree qualifiers.
      treequals = range(10)+list('ABCD')          # list of WSRT telescopes
      self.datadesc(treequals=kwargs.get('treequals', treequals))

      # Make a list of JonesClumps in the correct order (of the M.E.).
      # The ones selected (by the user) will be matrix-multiplied. 
      jj = []                       # list of selected Jones matrices
      notsel = []                   # list of not selected ones
      # EJones(self).append_if_selected(jj, notsel)
      # RJones(self).append_if_selected(jj, notsel)
      FJones(self).append_if_selected(jj, notsel)
      GJones(self).append_if_selected(jj, notsel)
      BJones(self).append_if_selected(jj, notsel)
      # DJones(self).append_if_selected(jj, notsel)

      return (jj,notsel)




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
      return None

   #==========================================================================

   def initexec (self, **kwargs):
      """
      Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      prompt = 'Jones: '+self.name()
      help = 'define FJones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('mode',['single','multiple'])

      if self.execute_body():
         mode = self.getopt('mode')

         # Create ParmClumps:
         if mode=='single':
            # Assume that the Faraday rotation is the same for all telescopes
            farot = self.ParmClump(name='farot', default=0.0, single=True)
         elif mode=='multiple':
            # Assume that the Faraday rotation is different for all telescopes
            farot = self.ParmClump(name='farot', default=0.0)

         # Generate nodes:
         stub = self.unique_nodestub()
         if mode=='single':                
            print str(farot[0])
            print farot[0].initrec();
            node = farot[0]
            cos = stub('cos') << Meq.Cos(node)
            print str(cos)
            sin = stub('sin') << Meq.Sin(farot[0])
            print str(sin)
            neg = stub('neg') << Meq.Negate(sin)
            node = stub('single') << Meq.Matrix22(cos, sin,
                                                  neg, cos)
         for i,qual in enumerate(self.nodequals()):
            if mode=='multiple':
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
      return None


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the LeafClump object with suitable leaf nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      prompt = 'Jones: '+self.name()
      help = 'define Jones matrix: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, prompt=prompt, help=help, **kwargs)

      self.add_option('mode',['amphas','realimag'])

      if self.execute_body():
         mode = self.getopt('mode')

         # Create ParmClumps:
         if mode=='amphas':
            gerrX = self.ParmClump(name='gerrX', default=1.0)
            perrX = self.ParmClump(name='perrX', default=0.0)
            gerrY = self.ParmClump(name='gerrY', default=1.0)
            perrY = self.ParmClump(name='perrY', default=0.0)
         elif mode=='realimag':
            rerrX = self.ParmClump(name='rerrX', default=1.0)
            ierrX = self.ParmClump(name='ierrX', default=0.0)
            rerrY = self.ParmClump(name='rerrY', default=1.0)
            ierrY = self.ParmClump(name='ierrY', default=0.0)

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
                   'RJones','EJones','ZJones',
                   'GJones','BJones','FJones'],
                  prompt='test WSRT Jones:')
   clump = None
   if TCM.submenu_is_selected():
      jones = TCM.getopt('jones', submenu)
      if jones=='WSRTJones':
         clump = WSRTJones(ns=ns, TCM=TCM)
      elif jones=='GJones':
         clump = GJones(ns=ns, TCM=TCM)
      elif jones=='BJones':
         clump = BJones(ns=ns, TCM=TCM)
      elif jones=='FJones':
         clump = FJones(ns=ns, TCM=TCM)
                  
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

   if 1:
      clump = WSRTJones(trace=True)


   if 0:
      clump = GJones(trace=True)

   if 0:
      clump = BJones(trace=True)

   if 0:
      clump = FJones(trace=True)

   if 1:
      clump.show('creation', full=True)

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: WSRTJones.py:\n' 

#=====================================================================================





