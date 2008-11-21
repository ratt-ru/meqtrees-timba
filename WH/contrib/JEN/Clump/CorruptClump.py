"""
CorruptClump.py: Contains a collecteion of Clump classes that may be used
to corrupt the trees. E.g. AddNoise, Scatter etc
"""

# file: ../JEN/Clump/CorruptClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 08 nov 2008: creation
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
import random



#********************************************************************************
# Class AddNoise
#********************************************************************************

class AddNoise(Clump.Clump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      Clump.Clump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """
      Add Gaussian noise with the specified stddev.
      """
      kwargs['select'] = True
      prompt = 'AddNoise'
      help = 'Add gaussian noise'
      ctrl = self.on_entry(self.initexec, prompt, help, **kwargs)

      dd = self.core.datadesc()                 # data description record
      self.add_option('stddev', [0.001,0.01,0.1,1.0,10.0,0.0])
      self.add_option('unops', [None,'Exp','Exp Exp','Sin Cos'], more=str)

      if self.execute_body():
         stddev = max(0.0, self.getopt('stddev'))
         unops = self.getopt('unops')
         if isinstance(unops,str):
            unops = unops.split(' ')
            
         if stddev>0.0:
            stub = self.unique_nodestub('stddev='+str(stddev))
            nelem = dd['nelem']
            for i,qual in enumerate(self.nodequals()):
               if nelem==1:
                  if dd['complex']:
                     real = stub('real')(qual) << Meq.GaussNoise(stddev=stddev)
                     imag = stub('imag')(qual) << Meq.GaussNoise(stddev=stddev)
                     noise = stub('noise')(qual) << Meq.ToComplex(real,imag)
                  else:
                     noise = stub('noise')(qual) << Meq.GaussNoise(stddev=stddev)
               else:
                  cc = []
                  for elem in dd['elems']:  
                     if dd['complex']:
                        real = stub('real')(qual)(elem) << Meq.GaussNoise(stddev=stddev)
                        imag = stub('imag')(qual)(elem) << Meq.GaussNoise(stddev=stddev)
                        noise = stub('noise')(qual)(elem) << Meq.ToComplex(real,imag)
                     else:
                        noise = stub('noise')(qual)(elem) << Meq.GaussNoise(stddev=stddev)
                     cc.append(noise)
                  noise = stub('noise')(qual) << Meq.Composer(*cc)     

               if isinstance(unops,list):
                  # Apply one or more unary operation(s), if required (e.g. Exp):
                  for unop in unops:
                     noise = noise(unop) << getattr(Meq,unop)(noise)
               self[i] = stub(qual) << Meq.Add(self[i], noise)

            self.visualize(select=False)

         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)






#********************************************************************************
#********************************************************************************
# Class Scatter
#********************************************************************************

class Scatter(Clump.Clump):
   """
   Derived class
   """

   def __init__(self, clump=None, **kwargs):
      """
      Derived from class Clump.
      """
      Clump.Clump.__init__(self, clump=clump, **kwargs)
      return None


   #==========================================================================
   # The function .initexec() must be re-implemented for 'leaf' Clumps,
   # i.e. Clump classes that contain leaf nodes. An example is given below,
   # and may be canibalized for derived (leaf) Clump clases.
   #==========================================================================

   def initexec (self, **kwargs):
      """Add different random (stddev) constants to the tree nodes.
      If stddev is complex, the scatter constants are complex too.
      """
      prompt = 'Scatter'
      help = 'Add different (stddev) constants to the tree nodes'
      ctrl = self.on_entry(self.initexec, prompt, help, **kwargs)

      dd = self.core.datadesc()                 # data description record
      self.add_option('stddev', [0.1,1.0,10.0,0.0])

      if self.execute_body():
         stddev = max(0.0,self.getopt('stddev'))
         if stddev>0.0:
            stub = self.unique_nodestub('stddev='+str(stddev))
            for i,qual in enumerate(self.nodequals()):
               nelem = dd['nelem']
               cc = []
               for elem in dd['elems']:  
                  if dd['complex']:
                     rscat = random.gauss(0.0, stddev)
                     iscat = random.gauss(0.0, stddev)
                     scat = Clump.EF.format_value(complex(rscat,iscat), nsig=2)
                     if nelem==1:
                        scat = stub('scat='+scat)(qual) << Meq.ToComplex(rscat,iscat)
                     else:
                        scat = stub('scat='+scat)(qual)(elem) << Meq.ToComplex(rscat,iscat)
                  else:
                     scat = random.gauss(0.0, stddev)
                     scat = Clump.EF.format_value(scat, nsig=2)
                     if nelem==1:
                        scat = stub('scat='+scat)(qual) << Meq.Constant(scat)
                     else:
                        scat = stub('scat='+scat)(qual)(elem) << Meq.Constant(scat)
                  cc.append(scat)

               if nelem>1:
                  scat = stub('scat')(qual) << Meq.Composer(*cc)     
               self[i] = stub(qual) << Meq.Add(self[i], scat)

            self.visualize(select=False)

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
   clump = None
   if TCM.submenu_is_selected():
      clump = Clump.LeafClump(ns=ns, TCM=TCM,
                              complex=True,
                              dims=[2,2],
                              trace=True)
      select = None
      # select = True
      clump = AddNoise(clump, select=select, trace=True).daisy_chain()
      clump = Scatter(clump, select=select, trace=True).daisy_chain()

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
   print '** Start of standalone test of: CorruptClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()

   if 1:
      tqs = range(10) + list('ABCD')
      tqs = None
      clump = Clump.LeafClump(trace=True,
                              complex=True,
                              dims=[2,2],
                              treequals=tqs)
      clump = AddNoise(clump, trace=True)
      clump = Scatter(clump, trace=True)
      clump.show('creation', full=True)

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: CorruptClump.py:\n' 

#=====================================================================================





