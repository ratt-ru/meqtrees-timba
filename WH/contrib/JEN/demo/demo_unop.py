# demo_unop.py:

# Demonstrates the following MeqTree features:
# - All the nodes that provide unary math operations
# - Unary operations are performed cell-by-cell
# - The result has the same cells as the argument node

# Tips:
# - First execute with TDL Exec 'execute'
#   - If bm=True in _define_forest(), there are more bookmarks.

# - Try the other TDL Exec options with arguments that can be illegal. 
#   - Then check the state records of those unary ops that are not
#     be able to deal with zero or negativbee arguments.

# NB: Re-execute with new domain does NOT work!
# NB: Results of illegal arguments produce 'nan' (not-a-number)
#     but is not reported in any way (look at the vellset),
#     and is even used in further math operations!!


 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

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

   # Organised in named groups of related unary operations.
   # The nodes of each group are collected in a list (cc).
   # Groups are bundled by supplying the cc as children to an Add node.
   # (this has the added advantage of detecting errors per group).
   # The groups are bundled in the same way via child-list gg.
   
   gg = []

   # Make node(s) to serve as argument for the unary ops.
   # Variation over freq gives a nice 1D plot. 
   x = ns['x'] << Meq.Freq()
   x10 = ns['x10'] << Meq.Freq()/10
   cx = ns['cx'] << Meq.toComplex(1,x)
   xn = ns['xneg'] << Meq.Negate(x)

   # Optionally, make separate bookmarks for each group.
   # This produces a separate plot for each unary node.
   # This makes use of a utlity module JEN_bookmarks, which
   # generates named bookpages from lists (cc, bb) of nodes.
   # This is convenient, but not ecouraged in demo scripts.

   bm = False
   bm = True

   group = 'unop_expon'
   cc = [x]
   cc.append(ns << Meq.Exp(x)) 
   cc.append(ns << Meq.Log(x)) 
   cc.append(ns << Meq.Negate(x)) 
   cc.append(ns << Meq.Invert(x)) 
   cc.append(ns << Meq.Sqrt(x)) 
   cc.append(ns << Meq.Sqr(x)) 
   gg.append(ns[group] << Meq.Add(children=cc)) 
   if bm: JEN_bookmarks.create(cc, group)

   group = 'unop_pow'
   cc = [x]
   cc.append(ns << Meq.Pow2(x)) 
   cc.append(ns << Meq.Pow3(x)) 
   cc.append(ns << Meq.Pow4(x)) 
   cc.append(ns << Meq.Pow5(x)) 
   cc.append(ns << Meq.Pow6(x)) 
   cc.append(ns << Meq.Pow7(x)) 
   cc.append(ns << Meq.Pow8(x))
   gg.append(ns[group] << Meq.Add(children=cc)) 
   if bm: JEN_bookmarks.create(cc, group)

   group = 'unop_circular'
   cc = []
   cc.append(ns << Meq.Cos(x)) 
   cc.append(ns << Meq.Sin(x)) 
   cc.append(ns << Meq.Tan(x)) 
   cc.append(ns << Meq.Acos(x10)) 
   cc.append(ns << Meq.Asin(x10)) 
   cc.append(ns << Meq.Atan(x)) 
   cc.append(ns << Meq.Cosh(x)) 
   cc.append(ns << Meq.Sinh(x)) 
   cc.append(ns << Meq.Tanh(x)) 
   gg.append(ns[group] << Meq.Add(children=cc)) 
   if bm: JEN_bookmarks.create(cc, group)


   group = 'unop_complex'
   cc = [cx]
   cc.append(ns << Meq.Abs(cx)) 
   cc.append(ns << Meq.Norm(cx)) 
   cc.append(ns << Meq.Arg(cx)) 
   cc.append(ns << Meq.Real(cx)) 
   cc.append(ns << Meq.Imag(cx)) 
   cc.append(ns << Meq.Conj(cx)) 
   gg.append(ns[group] << Meq.Add(children=cc)) 
   if bm: JEN_bookmarks.create(cc, group)

   group = 'unop_round'
   cc = [xn]
   cc.append(ns << Meq.Abs(xn)) 
   cc.append(ns << Meq.Fabs(xn)) 
   cc.append(ns << Meq.Ceil(xn)) 
   cc.append(ns << Meq.Floor(xn)) 
   gg.append(ns[group] << Meq.Add(children=cc)) 
   if bm: JEN_bookmarks.create(cc, group)


   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Add(children=gg)

   # Optionally, make a bookpage for the group bundling nodes (gg).
   if bm:
      gg.append(result)
      JEN_bookmarks.create(gg, 'unop_overall')

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
       
def _tdl_job_zero (mqs, parent):
    """Execute the forest, with zero value(s) in the request"""
    domain = meq.domain(-0.25,9.25,0,1)                              # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    rqid = meq.requestid(domain_id=2)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result

def _tdl_job_negative (mqs, parent):
    """Execute the forest, with negative values in the request"""
    domain = meq.domain(-10,10,0,1)                               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    rqid = meq.requestid(domain_id=3)
    request = meq.request(cells, rqtype='ev', rqid=rqid)
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
#********************************************************************************
#********************************************************************************




