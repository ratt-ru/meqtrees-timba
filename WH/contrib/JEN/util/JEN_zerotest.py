# JEN_zerotest. py:


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
   """Test of zerotest(node) function"""

   # Make a node that produces some variation in two dimensions(f,t):
   y = ns.y << Meq.Time()
   x = ns.x << Meq.Freq()
   xy = ns.xy << Meq.Add(x,y)

   # Apply zerotest() to various nodes whose result should be zero.
   # Collect these nodes into a vector cc (to be added below)
   cc = []
   cc.append(zerotest(ns, ns << Meq.Subtract(xy,xy)), recurse=2)
   cc.append(zerotest(ns, ns << Meq.Multiply(xy,xy)), recurse=3)

   # Do a final zerotest on the sum of all zerotest nodes (in cc).
   # The name of the sum node should be used in _tdl_job_execute() below.
   zerotest(ns, ns.zerotest << Meq.Add(children=cc))

   # Finished:
   return True




#===============================================================================
# Function to be called by other zerotest functions:
#===============================================================================

def zerotest(ns, node, recurse=1):
   """This function is to be called from zerotest functions."""
   
   # Make a bookmark to plot the given node. It should be bright green(=0).
   # The argument recurse=1 causes its children to be plotted also.
   JEN_bookmarks.create(node, recurse=recurse)

   # Make a bookmark of the root node on its own:
   if node.name=='zerotest':
      JEN_bookmarks.create(node)

   # Return the input node.
   return node



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='zerotest', request=request))
    return result
       

#********************************************************************************
#********************************************************************************


