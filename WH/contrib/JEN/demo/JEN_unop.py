# JEN_unop.py:

# Demonstrates the following MeqTree features:
# - All the nodes that provide unary math operations
# - Unary operations are performed cell-by-cell
# - The result has the same cells as the argument node


 
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

   # Organised in named groups of related unary operations.
   # The nodes of each group are collected in a list (cc).
   # Groups are bundled by supplying the cc as children to an Add node.
   # (this has the added advantage of detecting errors per group).
   # The groups are bundled in the same way via child-list gg.
   
   gg = []

   # Make node(s) to serve as argument for the unary ops.
   # Variation over freq gives a nice 1D plot. 
   x = ns.x << Meq.Freq()
   x10 = ns.x10 << Meq.Freq()/10
   cx = ns.cx << Meq.toComplex(1,x)

   # Optionally, make separate bookmarks for each group.
   # This produces a separate plot for each unary node.
   # This makes use of a utlity module JEN_bookmarks, which
   # generates named bookpages from lists (cc, bb) of nodes.
   # This is convenient, but not ecouraged in demo scripts.

   bms = False
   bms = True

   group = 'elementary'
   cc = [x,
         ns << Meq.Negate(x), 
         ns << Meq.Invert(x), 
         ns << Meq.Exp(x), 
         ns << Meq.Log(x), 
         ns << Meq.Sqrt(x), 
         ns << Meq.Cos(x), 
         ns << Meq.Sin(x), 
         ns << Meq.Tan(x), 
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   group = 'inverse_circular'
   cc = [x,x10,
      ns << Meq.Acos(x), 
      ns << Meq.Asin(x), 
      ns << Meq.Atan(x),
      ns << Meq.Acos(x10), 
      ns << Meq.Asin(x10), 
      ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   group = 'hyperbolic'
   cc = [x,
      ns << Meq.Cosh(x), 
      ns << Meq.Sinh(x), 
      ns << Meq.Tanh(x),
      ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   group = 'complex'
   cc = [cx,
         ns << Meq.Abs(cx), 
         ns << Meq.Norm(cx),       # same as Abs() 
         ns << Meq.Arg(cx), 
         ns << Meq.Real(cx), 
         ns << Meq.Imag(cx), 
         ns << Meq.Conj(cx),
         ns << Meq.Exp(cx), 
         ns << Meq.Log(cx),        # elog(), show 10log()?
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   group = 'power'
   cc = [x,
         ns << Meq.Sqr(x),
         ns << Meq.Pow2(x), 
         ns << Meq.Pow3(x), 
         ns << Meq.Pow4(x), 
         ns << Meq.Pow5(x), 
         ns << Meq.Pow6(x), 
         ns << Meq.Pow7(x), 
         ns << Meq.Pow8(x),
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   group = 'misc'
   cc = [x,
         ns << Meq.Abs(x), 
         # ns << Meq.Fabs(x),         # same as Abs, needed?
         ns << Meq.Ceil(x), 
         ns << Meq.Floor(x),
         ns << Meq.Stripper(x),     # just strips the derivatives off the result 
         ns << Meq.Identity(x),     # just makes a copy....
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   # Cell_statistics are Operations that calculate properties of
   # the values of all the cells in the requested domain.
   # Note that they produce a 'scalar' result, which will be
   # expanded to a domain in which all cells have the same value
   # when needed.
   
   group = 'cell_statistics'
   cc = [x,
         ns << Meq.NElements(x),
         ns << Meq.Sum(x),
         ns << Meq.Mean(x),
         ns << Meq.StdDev(x),
         ns << Meq.Min(x),
         ns << Meq.Max(x),
         ns << Meq.Product(x),
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   # With multiple children, the operations are done over
   # all the children. The results are per cell.

   a1 = ns.a1 << Meq.Freq()
   a2 = ns.a2 << Meq.Cos(a1)
   a3 = ns.a3 << Meq.Sin(a1)

   group = 'child_ops'
   cc = [a1,a2,a3,
         ns << Meq.Min(a1,a2,a3),
         ns << Meq.Max(a1,a2,a3),
         ns << Meq.Min(a2,a3),
         ns << Meq.Max(a2,a3),
         ns << Meq.Mean(a1,a2,a3)
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   # Some child-ops have weighted versions.
   # Children with weight=0 are ignored (i.e. not evaluated).

   group = 'weighted_child_ops'
   wgt = [3.0,1.0,2.0]
   wgt = [3,1,2]
   wtot = ns.wtot << sum(wgt)
   wsum = ns['wsum(3*a1,1*a2,2*a3)'] << Meq.WSum(a1,a2,a3, weights=wgt)
   wmean = ns['wmean(3*a1,1*a2,2*a3)'] << Meq.WMean(a1,a2,a3, weights=wgt)
   cc = [a1,a2,a3,
         wsum,wmean,wtot,
         ns << wmean - wsum/wtot,          # result should be zero
         ]
   gg.append(ns[group] << Meq.Add(children=cc))
   if bms: JEN_bookmarks.create(cc, group)

   # It is possible to add children (and step_children) to
   # an existing node:

   group = 'add_children'
   c1 = ns.c1 << Meq.Freq()
   c2 = ns.c2 << Meq.Cos(c1)
   sc = ns.step_child << Meq.Sin(c1)
   parent = ns.parent << Meq.Add(c1)
   parent.add_children(c2)
   parent.add_stepchildren(sc)
   gg.append(parent)
   if bms: JEN_bookmarks.create(parent, group, recurse=1, step_children=True)



   #==============================================================
   
   result = ns.result << Meq.Add(children=gg)

   # Optionally, make a bookpage for the group bundling nodes (gg).
   if bms:
      gg.append(result)
      JEN_bookmarks.create(gg, 'overall')

   # Standard: make a bookmark of the result node, for easy viewing:
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
    domain = meq.domain(0.1,10,0,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

def _tdl_job_negapos (mqs, parent):
    """Execute the forest, with negative and positive values in the request"""
    domain = meq.domain(-10,10,0,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    rqid = meq.requestid(domain_id=2)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

def _tdl_job_zero (mqs, parent):
    """Execute the forest, with one-cell request (x=0)"""
    domain = meq.domain(-1,1,-1,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    rqid = meq.requestid(domain_id=3)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

#********************************************************************************
# Comments:
#********************************************************************************

# - First execute with TDL Exec 'execute'
#   - If bms=True in _define_forest(), there are more bookmarks.

# - Try the other TDL Exec options with arguments that can be illegal. 
#   - Then check the state records of those unary ops that are not
#     be able to deal with zero or negativbee arguments.

# NB: Results of illegal arguments produce 'nan' (not-a-number)
#     but is not reported in any way (look at the vellset),
#     and is even used in further math operations!!

#********************************************************************************
#********************************************************************************




