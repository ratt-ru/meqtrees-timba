"""
QuickRef module: QuickRefNodeHelp.py:
"""

# file: ../JEN/QuickRef/QuickRefNodeHelp.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Attaches specific help (string) to the quickref_help field
#   of the state-record of the given node (or subtree)
#
# History:
#   - 257 jul 2008: creation (from QuickRef.py)
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

# from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
# from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN


# import math
# import random
# import numpy


#******************************************************************************** 


def node_help (node, detail=1, rider=None, mode='html', trace=False):
   """
   Attach specific help to the quickref_help field of the given node.
   If a rider (CollatedHelpRecord) is specified, attach it too.
   """

   if is_node(node):
      ss = '<br><dl><dt><font color="blue">\n'
      ss += EN.format_node(node)
      ## qhead += ' &lt &lt &#32 Meq.'+str(meqclass)         # escape char &lt = <
      ss += '\n</font><dd>\n'
      cname = node.classname
      rr = node.initrec()
   else:
      cname = str(node)
      ss = None
      rr = None

   ss = class_help (cname, header=ss, rr=rr,
                           detail=detail, rider=rider,
                           mode=mode, trace=False)

   # Attach to quickref_help field of the node state record:
   if is_node(node):
      EN.quickref_help (node, append=ss, trace=trace)

   if trace:
      print '\n** QRNH.node_help(',str(node),'):\n  ',ss,'\n'
      
   return ss
      

#-----------------------------------------------------------------------------------

def class_help (cname, header=None, rr=None,
                       detail=1, rider=None,
                       mode='html', trace=False):
   """
   Attach specific help to the quickref_help field of the given
   node-class name (cname).
   If a rider (CollatedHelpRecord) is specified, attach it too.
   """

   if header==None:
      ss = '<br><dl><dt><font color="blue">\n'
      ss += 'MeqNode of class: '+str(cname)
      ss += '\n</font><dd>\n'
      rr = record()
   else:
      # Assume that this is called by node_help()
      ss = header

   more = 'specific: '
   if cname=='MeqConstant':
      more += 'constant leaf node, dims='+str(getattr(rr,'dims',None))
      more += ' value = '+str(getattr(rr,'value',None))

   elif cname in ['MeqFreq','MeqTime','MeqGrid']:
      pass

   elif cname in ['MeqAbs','MeqNorm','MeqArg','MeqReal',
                  'MeqImag','MeqConj','MeqExp','MeqLog']:
      help = record(Abs='', Norm='like Abs', Arg='-> rad', Real='', Imag='',
                    Conj='complex conjugate: a+bj -> a-bj',
                    Exp='exp(a+bj) = exp(a)*exp(bj), i.e. cos with increasing ampl',
                    Log='e-log (ln)')

   elif cname in ['MeqAbs','MeqCeil','MeqFloor','MeqStripper','MeqIdentity']:
      help = record(Abs='Take the absolute value.',
                    Ceil='Round upwards to integers.',
                    Floor='Round downwards to integers.',
                    Stripper="""Remove all derivatives (if any) from the result.
                    This saves space and can be used to control solving.""",
                    Identity='Make a copy node with a different name.'
                    )

   elif cname in ['MeqSubtract','MeqDivide','MeqPow',
                  'MeqToComplex','MeqPolar','MeqMod']:
      help = record(Subtract='lhs-rhs', Divide='lhs/rhs', Pow='lhs^rhs',
                    Mod='lhs%rhs',
                    ToComplex='(real, imag)', Polar='(amplitude, phase)')
      # Problem: MeqMod() crashes the meqserver.... Needs integer children??

   elif cname in ['MeqAdd','MeqMultiply']:
      pass
   elif cname in ['MeqSubtract','MeqDivide','MeqPower']:
      pass


   #---------------------------------------------------------------------------

   elif cname in ['MeqCos','MeqSin','MeqTan']:
      help = record(Sin='(rad)', Cos='(rad)', Tan='(rad)')

   elif cname in ['MeqAcos','MeqAsin','MeqAtan']:
      help = record(Asin='abs('+str('twig.name')+') &lt 1',
                    Acos='abs('+str('twig.name')+') &lt 1',
                    Atan='')

   elif cname in ['MeqCosh','MeqSinh','MeqTanh']:
      pass

   elif cname in ['MeqPow2','MeqPow3','MeqPow4','MeqPow5',
                  'MeqPow6','MeqPow7','MeqPow8','MeqSqr']:
      pass
   elif cname in ['MeqAbs','MeqNegate','MeqInvert','MeqExp','MeqLog','MeqSqrt']:
      help = record(Negate='-c', Invert='1/c', Exp='exp(c)', Sqrt='square root',
                    Log='e-log (for 10-log, divide by Log(10))')

   elif cname in ['MeqNelements','MeqSum','MeqMean','MeqProduct',
                  'MeqStdDev','MeqRms', 'MeqMin','MeqMax']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['Transpose','MatrixMultiply','ConjTranspose']:
      pass
   elif cname in ['Matrix22','MatrixInvert22']:
      pass

   elif cname in ['GaussNoise','RandomNoise']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqReqSeq','MeqReqMux']:
      pass

   elif cname in ['MeqComposer','MeqSelector','Paster']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['Compounder']:
      pass
   elif cname in ['ModRes','Resampler']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqSolver','MeqCondeq']:
      pass
   elif cname=='MeqParm':
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqZeroFlagger','MeqMergeFlags']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqSpigot','MeqFitsSpigot']:
      pass
   elif cname in ['MeqSink','MeqVisDataMux']:
      pass
   elif cname in ['MeqFITSReader','MeqFITSImage','MeqFITSSpigot','','','']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqUVBrick','MeqUVInterpol']:
      pass
   elif cname in ['MeqVisPhaseShift']:
      pass

   #---------------------------------------------------------------------------

   elif cname in ['MeqCoordTransform','MeqAzEl','MeqLST','MeqLMN','MeqLMRaDec']:
      pass
   elif cname in ['MeqObjectRADec','MeqParAngle','MeqRaDec','MeqUVW']:
      pass


   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------

   else:
      ss += '<font color="red" size=20>'
      ss += '** class_name not recognized: '+str(cname)+' **'
      ss += '</font>\n'
      trace = True

   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------

   # Finishing touches:
   ss += more
   ss += '\n</dl><br>\n'

   if rider:
      rider.insert_help(rider.path(temp='node'), help=ss, append=True, trace=trace)

   if trace:
      print '\n** QRNH.class_help(',cname,'):\n  ',ss,'\n'
      
   return ss
      



#==============================================================================
#==============================================================================

def tree_help (node, detail=1, level=0, recurse=True,
               rider=None, mode='html',
               trace=False):
   """
   Attach specific help to the quickref_help field of the nodes of
   the given subtree (to the specified recursion level).
   """
   prefix = level*'..|..'
   if level==0:
      if isinstance(recurse,bool):
         if not recurse: recurse=0
         if recurse: recurse=1000
      if trace:
         print '\n** QRNH.tree_help('+str(node)+'):'

   ss = node_help(node)
   if trace:
      print prefix,ss.split('<<')[1].split('\n')[0]
   
   if level<=recurse and getattr(node,'children', None):
      for child in node.children:
         tree_help(child[1], detail=detail, level=level+1,
                          rider=rider, recurse=recurse,
                          trace=trace)
   if level==0:
      if trace:
         print '**\n'
   return True
    




















#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QuickRefNodeHelp.py:\n' 

   ns = NodeScope()

   rider = None
   if 0:
      rider = QRU.create_rider()             # CollatedHelpRecord object

   if 0:
      node = ns << 1.3
      node_help(node, rider=rider, trace=True)

   if 1:
      a = ns << Meq.Constant(range(3))
      b = ns << 78
      node = ns << Meq.Add(a,b)
      class_help(node.classname, rider=rider, trace=True)
      node_help(node, rider=rider, trace=True)
      tree_help(node, rider=rider, trace=True)
            
   print '\n** End of standalone test of: QuickRefNodeHelp.py:\n' 

#=====================================================================================





