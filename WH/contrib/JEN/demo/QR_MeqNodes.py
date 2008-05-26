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


# Settings.forest_state.cache_policy = 100
# Settings.forest_state.bookmarks = []

# import Meow.Bookmarks
# from Timba.Contrib.JEN.util import JEN_bookmarks

import math
# import random



#********************************************************************************
# Top function, called from QuickRef.py:
#********************************************************************************

def MeqNodes (ns, path, chr=None):
   """Top function, called from QuickRef.py"""
   cc = []
   path = QR.add2path(path,'MeqNodes')
   cc.append(unops (ns, path, chr=chr))
   cc.append(binops (ns, path, chr=chr))
   cc.append(leaves (ns, path, chr=chr))
   help = 'standard nodes: ns[name] << Meq.XYZ(children,kwargs)'
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def unops (ns, path, chr=None):
   """Make a bundle of bundles of MeqNodes"""
   cc = [] 
   path = QR.add2path(path,'unops')
   cc.append(unops_elementary (ns, path, chr=chr))
   cc.append(unops_goniometric (ns, path, chr=chr))
   cc.append(unops_hyperbolic (ns, path, chr=chr))
   cc.append(unops_power (ns, path, chr=chr))
   cc.append(unops_misc (ns, path, chr=chr))
   cc.append(unops_cell_statistics (ns, path, chr=chr))
   cc.append(unops_complex (ns, path, chr=chr))
   help = 'unary nodes have one child, which may be a tensor' 
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def binops (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'binops')
   help = 'binary operation on two children, which may be tensor(s)'
   for q in ['Add','Multiply']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y,t)',
                            help=help, chr=chr, children=[ns.x,ns.y,ns.t]))
   help = 'binary operation on two or more children, which may be tensor(s)'
   for q in ['Subtract','Divide']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x,y)',
                            help=help, chr=chr, children=[ns.x,ns.y]))
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def leaves (ns, path, chr=None):
   """Make a bundle of bundles of MeqNodes"""
   cc = []
   path = QR.add2path(path,'leaves')
   cc.append(leaves_constant (ns, path, chr=chr))
   # cc.append(leaves_parm (ns, path, chr=chr))
   # cc.append(leaves_grid (ns, path, chr=chr))
   # cc.append(leaves_noise (ns, path, chr=chr))
   help = 'leaf nodes have no children' 
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)





#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************



#================================================================================
# leaves_...
#================================================================================

def leaves_constant (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'constant')
   help = 'Constant node created with: '
   cc.append(QR.MeqNode (ns, path, node=(ns << 2.5),
                         help=help+'ns << 2.5'))
   cc.append(QR.MeqNode (ns, path, node=(ns.xxxx << 2.4),
                         help=help+'ns.xxxx << 2.4'))
   cc.append(QR.MeqNode (ns, path, meqclass='Constant', name=None,
                         value=1.2))
   help = 'A constant may be complex, or a tensor'
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)



#================================================================================
# unops_...
#================================================================================

def unops_goniometric (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'goniometric')
   help = 'Unary operation on a single child (angle, rad)'
   for q in ['Sin','Cos','Tan']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, chr=chr, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def unops_elementary (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'elementary')
   help = """Unary operation on a single child.
   The rain in Spain
   Falls mainly in the plain
   """
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, chr=chr, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def unops_hyperbolic (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'hyperbolic')
   help = 'Unary operation on a single child'
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, chr=chr, children=[ns.x]))
   help = 'unary nodes have one child, which may be a tensor' 
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def unops_complex (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'complex')
   help = 'Unary operation on a single child, which usually is complex'
   for q in ['Abs','Norm','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(cxy)',
                            help=help, chr=chr, children=[ns.cxy]))
      # ns << Meq.Norm(cxy),       # same as Abs() 
      # ns << Meq.Log(cxy),        # elog(), show 10log()?
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def unops_power (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'power')
   help = 'Unary operation on a single child'
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, chr=chr, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def unops_misc (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'misc')
   help = 'Unary operation on a single child'
   for q in ['Abs','Ceil','Floor','Stripper','Identity']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, chr=chr, children=[ns.x]))
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#--------------------------------------------------------------------------------

def unops_cell_statistics (ns, path, chr=None):
   """Make a bundle of MeqNodes"""
   cc = []
   path = QR.add2path(path,'cell_statistics')
   help = 'Unary operation on a single child'
   for q in ['Nelements','Sum','Mean','StdDev','Min','Max','Product']:
      cc.append(QR.MeqNode (ns, path, meqclass=q, name=q+'(x)',
                            help=help, chr=chr, children=[ns.x]))
   # Cell_statistics are Operations that calculate properties of
   # the values of all the cells in the requested domain.
   # Note that they produce a 'scalar' result, which will be
   # expanded to a domain in which all cells have the same value
   # when needed.
   return QR.bundle (ns, path, nodes=cc, help=help, chr=chr)

#================================================================================
#================================================================================







