# ../JEN/demo/QuickRef.py:

# Author: J.E.Noordam
# 
# Short description:
#   A quick reference to all MeqTree nodes and subtrees.
#   It makes actual nodes, and prints help etc
#
# History:
#   - 23 may 2008: creation
#
# Remarks:
#
#   - Meow.Bookmarks needs a folder option....
#   - Middle-clicking a node in the browser should display its quickref_help
#   - NB: Left-clicking a node displays the state record, except the Composer...
#         It would be nice if it were easier to invoke the relevant plotter...
#         (at this moment it takes to many actions, and the new display is confusing)
#
# Description:
#


 
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


Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

import Meow.Bookmarks
from Timba.Contrib.JEN.util import JEN_bookmarks




#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest_old (ns, **kwargs):
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


#================================================================================
#================================================================================

TDLCompileMenu("Categories:",
               TDLOption('opt_standard_nodes',"Standard MeqNodes",True),
               TDLOption('opt_pynodes',"General PyNodes",False),
               TDLOption('opt_visualization',"JEN", False)
               )
  

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Make some standard child-nodes with standard names
   # These are used in the various bundles below.
   # They are bundles to avoid browser clutter.
   bb = []
   bb.append(ns.x << Meq.Freq())
   bb.append(ns.y << Meq.Time())
   bb.append(ns.cx << Meq.ToComplex(ns.x,ns.y))
   bb.append(ns.f << Meq.Freq())
   bb.append(ns.t << Meq.Time())
   unc = ns['unclutter'] << Meq.Composer(children=bb)

   trace = True
   print '\n** Start of QuickRef _define_forest()'

   # Make bundles of (bundles of) categories of nodes/subtrees:
   cc = []
   if opt_standard_nodes:
      cc.append(bundle_standard_nodes(ns, level=1, trace=trace))

   # Finished: Make the outer bundle (of node bundles):
   help = 'help'
   bundle (ns, name='rootnode', nodes=cc, help=help,
           level=0, trace=trace)

   print '** end of QuickRef _define_forest()/n'
   return True
   


#================================================================================
# Functions that make categories of nodes/subtrees:
#================================================================================

def bundle_standard_nodes (ns, folder=None, level=0, trace=True):
   """Make bundle of bundles of all standard nodes"""
   cc = []
   subfolder = 'standard_nodes'
   subfolder = None
   cc.append(bundle_unop (ns, folder=subfolder, level=level+1, trace=True))
   cc.append(bundle_binop (ns, folder=subfolder, level=level+1, trace=True))
   help = 'standard nodes: ns[name] << Meq.XYZ(children,kwargs)'
   return bundle (ns, name='standard_nodes', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#================================================================================


def bundle_unop (ns, level=0, folder=None, trace=False):
   """Make a bundle of bundles of MeqNodes"""
   cc = []
   subfolder = 'unary_operations'
   cc.append(bundle_unop_elementary (ns, folder=subfolder, level=level+1, trace=trace))
   cc.append(bundle_unop_goniometric (ns, folder=subfolder, level=level+1, trace=trace))
   cc.append(bundle_unop_hyperbolic (ns, folder=subfolder, level=level+1, trace=trace))
   cc.append(bundle_unop_power (ns, folder=subfolder, level=level+1, trace=trace))
   cc.append(bundle_unop_misc (ns, folder=subfolder, level=level+1, trace=trace))
   cc.append(bundle_unop_cell_statistics (ns, folder=subfolder, level=level+1, trace=trace))
   cc.append(bundle_unop_complex (ns, folder=subfolder, level=level+1, trace=trace))
   help = 'unary nodes have one child, which may be a tensor' 
   return bundle (ns, name=subfolder, nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_goniometric (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child (angle, rad)'
   for q in ['Sin','Cos','Tan']:
      node = MeqNode (ns, name=q+'(x)', help=help,
                      meqclass=q, children=[ns.x],
                      level=level+1, trace=trace)
      cc.append(node)
   return bundle (ns, name='goniometric', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_elementary (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child'
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      cc.append(MeqNode (ns, name=q+'(x)', help=help,
                         meqclass=q, children=[ns.x],
                         level=level+1, trace=trace))
   return bundle (ns, name='elementary', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_hyperbolic (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child'
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(MeqNode (ns, name=q+'(x)', help=help,
                         meqclass=q, children=[ns.x],
                         level=level+1, trace=trace))
   help = 'unary nodes have one child, which may be a tensor' 
   return bundle (ns, name='hyperbolic', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_complex (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child, which usually is complex'
   for q in ['Abs','Norm','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(MeqNode (ns, name=q+'(cx)', help=help,
                         meqclass=q, children=[ns.cx],
                         level=level+1, trace=trace))
      # ns << Meq.Norm(cx),       # same as Abs() 
      # ns << Meq.Log(cx),        # elog(), show 10log()?
   return bundle (ns, name='complex', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_power (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child'
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(MeqNode (ns, name=q+'(x)', help=help,
                         meqclass=q, children=[ns.x],
                         level=level+1, trace=trace))
   return bundle (ns, name='power', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_misc (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child'
   for q in ['Abs','Ceil','Floor','Stripper','Identity']:
      cc.append(MeqNode (ns, name=q+'(x)', help=help,
                         meqclass=q, children=[ns.x],
                         level=level+1, trace=trace))
   return bundle (ns, name='misc', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#--------------------------------------------------------------------------------

def bundle_unop_cell_statistics (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'Unary operation on a single child'
   for q in ['Nelements','Sum','Mean','StdDev','Min','Max','Product']:
      cc.append(MeqNode (ns, name=q+'(x)', help=help,
                         meqclass=q, children=[ns.x],
                         level=level+1, trace=trace))
   # Cell_statistics are Operations that calculate properties of
   # the values of all the cells in the requested domain.
   # Note that they produce a 'scalar' result, which will be
   # expanded to a domain in which all cells have the same value
   # when needed.
   return bundle (ns, name='cell_statistics', nodes=cc, help=help,
                  folder=folder, level=level, trace=trace)

#================================================================================
#================================================================================


def bundle_binop (ns, folder=None, level=0, trace=False):
   """Make a bundle of MeqNodes"""
   cc = []
   help = 'binary operation on two children, which may be tensor(s)'
   for q in ['Add','Multiply']:
      cc.append(MeqNode (ns, name=q+'(x,y,t)', help=help,
                         meqclass=q, children=[ns.x,ns.y,ns.t],
                         level=level+1, trace=trace))
   help = 'binary operation on two or more children, which may be tensor(s)'
   for q in ['Subtract','Divide']:
      cc.append(MeqNode (ns, name=q+'(x,y)', help=help,
                         meqclass=q, children=[ns.x,ns.y],
                         level=level+1, trace=trace))
   name = 'binary_operations'
   page = name
   if isinstance(folder, str):
      page = None
   return bundle (ns, name=name, nodes=cc, help=help,
                  page=page, folder=folder, level=level, trace=trace)




#================================================================================
# Helper functions(may be called externally):
#================================================================================

def prefix (level=0):
   """Used to indent"""
   prefix = (level*'**')+' '
   return prefix

#-------------------------------------------------------------------------------

def bundle (ns=None, name=None, nodes=None, help=None,
            page=None, folder=None, viewer="Result Plotter",
            level=0, trace=False):
   """Make a bundle of nodes in an organized way"""

   # Make a single parent node, with the given nodes as children:
   if True:
      # NB: When a Composer node is left-clicked in the browser,
      # it plots an inspector, not its state record (with help...)   
      parent = ns[name] << Meq.Composer(children=nodes,
                                        quickref_help=help)
   else:
      # Alternative: ReqSeq?
      parent = ns[name] << Meq.Add(children=nodes,
                                   quickref_help=help)

   # Make a meqbrowser bookmark for this bundle, if required:
   if folder or page:
      if True:
         # Temporary, until Meow folder problem (?) is solved....
         JEN_bookmarks.create(nodes, name, page=page, folder=folder,
                              viewer=viewer)
      else:
         # NB: There does not seem to be a way to assign a folder....
         bookpage = Meow.Bookmarks.Page(name, folder=bookfolder)
         for node in nodes:
            bookpage.add(node, viewer=viewer)

   if trace:
      print prefix(level),name,'->',str(parent)
   return parent

#-------------------------------------------------------------------------------

def MeqNode (ns=None, name=None, meqclass=None,
             children=None, help=None,
             level=0, trace=False, **kwargs):
   """Define the specified node an an organised way"""
   nodename = str(name)
   # nodename = 'Meq.'+nodename        # ....this clutters the browser....
   node = ns[nodename] << getattr(Meq,meqclass)(children=children,
                                                quickref_help=help)
   if trace:
      print prefix(level),name,meqclass,'->',str(node)
   return node


#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(0.1,10,0,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=200, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
    return result
       
def _tdl_job_negapos (mqs, parent):
    """Execute the forest, with negative and positive values in the request"""
    domain = meq.domain(-10,10,0,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    rqid = meq.requestid(domain_id=2)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
    return result
       

def _tdl_job_zero (mqs, parent):
    """Execute the forest, with one-cell request (x=0)"""
    domain = meq.domain(-1,1,-1,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    rqid = meq.requestid(domain_id=3)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='rootnode', request=request))
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




