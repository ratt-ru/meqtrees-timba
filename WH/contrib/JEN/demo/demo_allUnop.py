# demo_allUnop.py: demonstrates the following MeqTree features:
# - all the nodes that provide unary math operations 

# Tips:
# - Try the three different execute options
#   - Then check the state records of the unary ops that should not
#     be able to deal with zero or negative arguments.



 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq
# from qt import *
# from numarray import *

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

   bb = []

   # Variation over freq gives a nice 1D plot: 
   x = ns['x'] << Meq.Freq()
   x10 = ns['x10'] << Meq.Freq()/10
   cx = ns['cx'] << Meq.toComplex(1,x)
   xn = ns['xneg'] << Meq.Negate(x)

   group = 'expon'
   cc = [x]
   cc.append(ns << Meq.Exp(x)) 
   cc.append(ns << Meq.Log(x)) 
   cc.append(ns << Meq.Negate(x)) 
   cc.append(ns << Meq.Invert(x)) 
   cc.append(ns << Meq.Sqrt(x)) 
   cc.append(ns << Meq.Sqr(x)) 
   JEN_bookmarks.create(cc, group)
   bb.append(ns[group] << Meq.Add(children=cc)) 

   group = 'pow'
   cc = [x]
   cc.append(ns << Meq.Pow2(x)) 
   cc.append(ns << Meq.Pow3(x)) 
   cc.append(ns << Meq.Pow4(x)) 
   cc.append(ns << Meq.Pow5(x)) 
   cc.append(ns << Meq.Pow6(x)) 
   cc.append(ns << Meq.Pow7(x)) 
   cc.append(ns << Meq.Pow8(x))
   JEN_bookmarks.create(cc, group)
   bb.append(ns[group] << Meq.Add(children=cc)) 

   group = 'circular'
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
   JEN_bookmarks.create(cc, group)
   bb.append(ns[group] << Meq.Add(children=cc)) 


   group = 'complex'
   cc = [cx]
   cc.append(ns << Meq.Abs(cx)) 
   cc.append(ns << Meq.Norm(cx)) 
   cc.append(ns << Meq.Arg(cx)) 
   cc.append(ns << Meq.Real(cx)) 
   cc.append(ns << Meq.Imag(cx)) 
   cc.append(ns << Meq.Conj(cx)) 
   JEN_bookmarks.create(cc, group)
   bb.append(ns[group] << Meq.Add(children=cc)) 

   group = 'round'
   cc = [xn]
   cc.append(ns << Meq.Abs(xn)) 
   cc.append(ns << Meq.Fabs(xn)) 
   cc.append(ns << Meq.Ceil(xn)) 
   cc.append(ns << Meq.Floor(xn)) 
   JEN_bookmarks.create(cc, group)
   bb.append(ns[group] << Meq.Add(children=cc)) 


   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Add(children=bb)

   bb.append(result)
   JEN_bookmarks.create(bb, 'overall')

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
    domain = meq.domain(0.1,10,0,1)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_zero (mqs, parent):
    """Execute the forest, with zero value(s) in the request"""
    domain = meq.domain(0,10,0,1)                              # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result

def _tdl_job_negative (mqs, parent):
    """Execute the forest, with negative values in the request"""
    domain = meq.domain(-10,10,0,1)                               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=20, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
#********************************************************************************
#********************************************************************************




