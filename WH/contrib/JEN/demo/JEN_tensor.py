# JEN_tensor.py:

# Demonstrates the following MeqTree features:
# - Various node 'tensor' operations




 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

# from Timba.Contrib.JEN.util import JEN_bookmarks

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

# Tensor/cell ops:
#   1306 2006-09-14 14:36 StdDev.cc
#   1426 2006-09-14 14:36 Sum.cc
#   1920 2006-09-14 14:36 Min.cc
#   1921 2006-09-14 14:36 Max.cc
#   1257 2006-09-14 14:36 Rms.cc
#   1817 2006-09-14 14:36 Mean.cc
#   1935 2006-09-14 14:36 WMean.cc
#   1448 2006-09-14 14:36 Product.cc
#   2391 2006-09-14 14:36 WSum.cc
#   1747 2006-09-14 14:36 NElements.cc

   # Make two 'leaf' nodes that show some variation over freq/time. 
   a = ns['a'] << Meq.Time()
   b = ns['b'] << Meq.Freq()

   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Add(a,b)

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

#********************************************************************************
#********************************************************************************




