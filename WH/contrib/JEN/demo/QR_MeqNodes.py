# file: ../JEN/demo/QR_MeqNodes.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Functions that make subtrees that demonstrate MeqNodes
#   Called from QuickRef.py
#
# History:
#   - 25 may 2008: creation (from QuickRef.py)
#
# Remarks:
#
# Description:
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

import QuickRef as QR

# import math
# import random



#********************************************************************************
# Top function, called from QuickRef.py:
#********************************************************************************

def MeqNodes (ns, path, rider=None):
   """
   Standard nodes: ns[name] << Meq.XYZ(children,kwargs)'
   """
   cc = []
   path = QR.add2path(path,'MeqNodes')
   cc.append(unops (ns, path, rider=rider))
   cc.append(binops (ns, path, rider=rider))
   cc.append(leaves (ns, path, rider=rider))
   help = MeqNodes.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def unops (ns, path, rider=None):
   """
   Unary nodes perform operations on one child, which may be a tensor. 
   """
   cc = [] 
   path = QR.add2path(path,'unops')
   cc.append(unops_elementary (ns, path, rider=rider))
   cc.append(unops_goniometric (ns, path, rider=rider))
   cc.append(unops_hyperbolic (ns, path, rider=rider))
   cc.append(unops_power (ns, path, rider=rider))
   cc.append(unops_misc (ns, path, rider=rider))
   cc.append(unops_cell_statistics (ns, path, rider=rider))
   cc.append(unops_complex (ns, path, rider=rider))
   help = unops.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def binops (ns, path, rider=None):
   """
   Binary nodes perform operations on two or more children.
   If two children
   """
   cc = []
   path = QR.add2path(path,'binops')
   help = 'binary operation on two children, which may be tensor(s)'
   for q in ['Add','Multiply']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y,t)',
                            help=help, rider=rider, children=[ns.x,ns.y,ns.t]))
   help = 'binary operation on two or more children, which may be tensor(s)'
   for q in ['Subtract','Divide']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y)',
                            help=help, rider=rider, children=[ns.x,ns.y]))
   help = binops.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def leaves (ns, path, rider=None):
   """
   Leaf nodes have no children. Some have access to an external
   source of information (like a file) to satisfy a request. 
   """
   cc = []
   path = QR.add2path(path,'leaves')
   cc.append(leaves_constant (ns, path, rider=rider))
   # cc.append(leaves_parm (ns, path, rider=rider))
   # cc.append(leaves_grid (ns, path, rider=rider))
   # cc.append(leaves_noise (ns, path, rider=rider))
   help = leaves.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)





#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************



#================================================================================
# leaves_...
#================================================================================

def leaves_constant (ns, path, rider=None):
   """
   A constant may be complex, or a tensor. There are various ways to define one.
   """
   cc = []
   path = QR.add2path(path,'constant')
   help = 'Constant node created with: '
   cc.append(QR.MeqNode (ns, path, node=(ns << 2.5),
                         help=help+'ns << 2.5'))
   cc.append(QR.MeqNode (ns, path, node=(ns.xxxx << 2.4),
                         help=help+'ns.xxxx << 2.4'))
   cc.append(QR.MeqNode (ns, path, meqclass='Constant', name=None,
                         value=1.2))
   help = leaves_constant.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)



#================================================================================
# unops_...
#================================================================================


def unops_elementary (ns, path, rider=None):
   """
   Elementary unary operations.
   """
   cc = [ns.x]
   path = QR.add2path(path,'elementary')
   help = ''
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      # NB: explain log...
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, rider=rider, children=[ns.x]))
   help = unops_elementary.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def unops_goniometric (ns, path, rider=None):
   """
   Goniometric functions turn an angle (rad) into a fraction.
   """
   cc = [ns.x]
   path = QR.add2path(path,'goniometric')
   help = ''
   for q in ['Sin','Cos','Tan']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, rider=rider, children=[ns.x]))
   help = unops_goniometric.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def unops_hyperbolic (ns, path, rider=None):
   """
   Hyperbolic functions convert a fraction into an angle (rad).
   """
   cc = [ns.x]
   path = QR.add2path(path,'hyperbolic')
   help = ''
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, rider=rider, children=[ns.x]))
   help = unops_hyperbolic.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def unops_complex (ns, path, rider=None):
   """
   Operations on a (usually) complex child.
   """
   cc = [ns.cxy]
   path = QR.add2path(path,'complex')
   help = ' of it single child'
   for q in ['Abs','Norm','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(cxy)',
                            help=q+help, rider=rider, children=[ns.cxy]))
      # ns << Meq.Norm(cxy),       # same as Abs() 
      # ns << Meq.Log(cxy),        # elog(), show 10log()?
   help = unops_complex.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def unops_power (ns, path, rider=None):
   """
   Nodes that take some power of its child.
   """
   cc = [ns.x]
   path = QR.add2path(path,'power')
   help = ' of its single child'
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=q+help, rider=rider, children=[ns.x]))
   help = unops_power.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def unops_misc (ns, path, rider=None):
   """
   Miscellaneous unary operations.
   """
   cc = [ns.x]
   path = QR.add2path(path,'misc')
   help = record(Abs='Take the absolute value.',
                 Ceil='Round upwards to integers.',
                 Floor='Round downwards to integers.',
                 Stripper="""Remove all derivatives (if any) from the result.
                 This saves space and can be used to control solving.""",
                 Identity='Make a copy node with a different name.'
                 )
   for q in ['Abs','Ceil','Floor','Stripper','Identity']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help[q], rider=rider, children=[ns.x]))
   help = unops_misc.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#--------------------------------------------------------------------------------

def unops_cell_statistics (ns, path, rider=None):
   """
   Cell_statistics are Operations that calculate properties of
   the values of all the cells in the requested domain.
   Note that they produce a 'scalar' result, which will be
   expanded to a domain in which all cells have the same value
   when needed.
   """
   cc = [ns.x]
   path = QR.add2path(path,'cell_statistics')
   help = ' over all cell values.'
   for q in ['Nelements','Sum','Mean','StdDev','Min','Max','Product']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=q+help, rider=rider, children=[ns.x]))
   help = unops_cell_statistics.__doc__
   return QR.bundle (ns, path, nodes=cc, help=help, rider=rider)

#================================================================================
#================================================================================







