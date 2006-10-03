# demo_binop.py:

# Demonstrates the following MeqTree features:
# - All the nodes that provide binary math operations (2 children)
# - Binary operations are performed cell-by-cell
# - The result has the same cells as the argument node

# Tips:
# - First execute with TDL Exec 'execute'
#   - If bm=True in _define_forest(), there are more bookmarks.


 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq
# from qt import *
# from numarray import *

# Optional:
from Timba.Contrib.JEN.util import JEN_bookmarks

# Make sure that all nodes retain their results in their caches,
# for your viewing pleasure.
Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

# Binop:
#   1367 2006-09-14 14:36 Pow.cc
#   1373 2006-09-14 14:36 Polar.cc
#   1409 2006-09-14 14:36 ToComplex.cc
#   1395 2006-09-14 14:36 Add.cc
#   1903 2006-09-14 14:36 Multiply.cc
#   1367 2006-09-14 14:36 Divide.cc
#   1479 2006-09-14 14:36 Subtract.cc
#   1935 2006-09-14 14:36 WMean.cc



   # Organised in named groups of related unary operations.
   # The nodes of each group are collected in a list (cc).
   # Groups are bundled by supplying the cc as children to an Add node.
   # (this has the added advantage of detecting errors per group).
   # The groups are bundled in the same way via child-list gg.
   
   gg = []

   # Make node(s) to serve as argument for the unary ops.
   # Variation over freq gives a nice 1D plot. 
   x = ns['x'] << Meq.Freq()
   y = ns['y'] << Meq.Time()

   # Optionally, make separate bookmarks for each group.
   # This produces a separate plot for each unary node.
   # This makes use of a utlity module JEN_bookmarks, which
   # generates named bookpages from lists (cc, bb) of nodes.
   # This is convenient, but not ecouraged in demo scripts.

   bm = False
   bm = True

   group = 'binop'
   cc = [x,y]
   cc.append(ns << Meq.Add(x,y)) 
   cc.append(ns << Meq.Subtract(x,y)) 
   cc.append(ns << Meq.Multiply(x,y)) 
   cc.append(ns << Meq.Divide(x,y)) 
   cc.append(ns << Meq.Pow(x,y)) 
   cc.append(ns << Meq.toComplex(x,y)) 
   cc.append(ns << Meq.Polar(x,y)) 
   gg.append(ns[group] << Meq.Add(children=cc)) 
   if bm: JEN_bookmarks.create(cc, group)


   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Add(children=gg)

   # Optionally, make a bookpage for the group bundling nodes (gg).
   if bm:
      gg.append(result)
      JEN_bookmarks.create(gg, 'binop_overall')

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
    domain = meq.domain(0.1,10,0.5,10.5)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=12, num_time=10)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result

              
#********************************************************************************
#********************************************************************************




