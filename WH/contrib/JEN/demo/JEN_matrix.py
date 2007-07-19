# JEN_matrix.py:

# Demonstrates the following MeqTree features:
# - Various matrix operations
# - Especially 2x2 matrices




 
#********************************************************************************
# Initialisation:
#********************************************************************************

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

from Timba.Contrib.JEN.util import JEN_bookmarks

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   gg = []

   # Matrix ops:
   #   3039 2006-09-14 14:36 Matrix22.cc
   #   3039 2006-09-14 14:36 Transpose.cc
   #   3039 2006-09-14 14:36 ConjTranspose.cc
   #  16019 2006-09-14 14:36 MatrixMultiply.cc
   #   7603 2006-09-14 14:36 MatrixInvert22.cc
   #   3139 2006-09-14 14:36 Stokes.cc            ??

   v2 = ns.v2 << Meq.Composer(-1,-2)

   m22 = ns.m22 << Meq.Composer(1,2,3,4, dims=[2,2])
   minv22 = ns.minv22 << Meq.MatrixInvert22(m22)

   mx22 = ns.mx22 << Meq.Composer(1+1j,2+2j,3+3j,4+4j, dims=[2,2])
   mxinv22 = ns.mxinv22 << Meq.MatrixInvert22(mx22)

   #-------------------------------------------------------------
   # Some basic matrix operations:
   
   group = 'basic'
   cc = [m22,mx22,
         ns << Meq.Transpose(m22),
         ns << Meq.Transpose(mx22),
         ns['hermitian(mx22)'] << Meq.ConjTranspose(mx22),
         ns << Meq.MatrixMultiply(m22,v2),
         ns << Meq.MatrixMultiply(v2,m22),
         ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)

   #-------------------------------------------------------------
   # Test of 2x2 matrix inversion: multiplications should be unity

   group = 'invert22'
   cc = [m22,minv22,mx22,mxinv22,
         ns << Meq.MatrixMultiply(m22,minv22),
         ns << Meq.MatrixMultiply(mx22,mxinv22),
         ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)

   #-------------------------------------------------------------
   # Make linear and circular visibility vectors by multiplying
   # a 4-element (I,Q,U,V) flux vector by a 4x4 Stokes matrix 

   group = 'Stokes'
   q = '3c286'
   I = ns.I(q=q) << 10
   Q = ns.Q(q=q) << 1.0
   U = ns.U(q=q) << -0.5
   V = ns.V(q=q) << -0.01
   iquv4 = ns.IQUV(q=q) << Meq.Composer(I,Q,U,V)
   slin44 = ns.slin44 << Meq.Composer(1,1,0,0,
                                      0,0,1,0+1j,
                                      0,0,1,0-1j,
                                      1,-1,0,0, dims=[4,4])
   scir44 = ns.scir44 << Meq.Composer(1,0,0,1,
                                      0,1,0+1j,0,
                                      0,1,0-1j,0,
                                      1,0,0,-1, dims=[4,4])
   cc = [iquv4,slin44,scir44,
         ns.XXYY(q=q) << Meq.MatrixMultiply(slin44,iquv4),
         ns.RRLL(q=q) << Meq.MatrixMultiply(scir44,iquv4),
         ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)

   #------------------------------------------------------------
   # The preferred way to apply instrumental Jones matrices:
   # Use 2x2 cohaerency matrices rather than 4-element IQUV vectors.

   group = 'Jones'
   iU = ns.iU << Meq.ToComplex(0,U)
   iV = ns.iV << Meq.ToComplex(0,V)
   cohlin22 = ns.cohlin22(q=q) << Meq.Composer(I+Q, U+iV, U-iV, I-Q, dims=[2,2])
   cohcir22 = ns.cohcir22(q=q) << Meq.Composer(I+V, Q+iU, Q-iU, I-V, dims=[2,2])
   s1 = 3                              # station 1(i)
   gi11 = ns.g11(s=s1) << 1+1j
   gi22 = ns.g22(s=s1) << 2-1j
   Gi = ns.GJones(s=s1) << Meq.Composer(gi11, 0, 0, gi22, dims=[2,2])
   s2 = 5                              # station 2(j)
   gj11 = ns.g11(s=s2) << -1+1j
   gj22 = ns.g22(s=s2) << 3+1j
   Gj = ns.GJones(s=s2) << Meq.Composer(gj11, 0, 0, gj22, dims=[2,2])
   Gjh = ns << Meq.ConjTranspose(Gj)   # hermitian conjugate

   cc = [cohlin22,cohcir22,Gi,Gj,
         ns.XYG(q=q, s1=s1, s2=s2) << Meq.MatrixMultiply(Gi, cohlin22, Gjh),
         ns.RLG(q=q, s1=s1, s2=s2) << Meq.MatrixMultiply(Gi, cohcir22, Gjh),
         ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)

   
   #=========================================================

   result = ns.result << Meq.Composer(children=gg)

   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result', viewer='Result Plotter',
               udi='/node/result', publish=True)
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

#********************************************************************************
# Comments:
#********************************************************************************

# Use the bookmarks. They are very convenient!
# The matrix/vector plots only show the first element. This is a bug!

# Click on the nodes to study the vellsets.
# Click on node 'basic' to see all vellsets of its children.

# MatrixMultiply(v2,m22) gives an error (red). Why?


#********************************************************************************
#********************************************************************************




