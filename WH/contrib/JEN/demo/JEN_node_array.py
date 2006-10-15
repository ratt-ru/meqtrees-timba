# JEN_node_array.py:

# Demonstrates the following MeqTree features:
# - Various operations on node-arrays
#   (see also JEN_matrix.py)




 
#********************************************************************************
# Initialisation:
#********************************************************************************

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

   # Tensor ops:
   #   3500 2006-09-14 14:36 Composer.cc
   #   5174 2006-09-14 14:36 Paster.cc
   #   5654 2006-09-14 14:36 Selector.cc
   #   5654 2006-09-14 14:36 Transpose.cc  ??
   
   gg = []

   # Make 'leaf' nodes that show some variation over freq/time. 
   y = ns.y << Meq.Time()
   x = ns.x << Meq.Freq()

   s = ns.scalar << -1.0
   v2 = ns.v2 << Meq.Composer(1,2)
   v3 = ns.v3 << Meq.Composer(1,2,3)
   m22 = ns.m22 << Meq.Composer(1,2,3,4, dims=[2,2])

   group = 'unops'
   cc = [v2,
         ns << Meq.NElements(v2),
         ns << Meq.Sum(v2),
         ns << Meq.Min(v2),
         ns << Meq.Cos(v2),
         ns << Meq.Cos(m22),
         ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)

   group = 'binops'
   cc = [v2,
         ns << Meq.Add(v2,s),
         ns << Meq.Add(v2,v2),
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
    cells = meq.cells(domain, num_freq=1, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

#********************************************************************************
# Comments:
#********************************************************************************

#********************************************************************************
#********************************************************************************




