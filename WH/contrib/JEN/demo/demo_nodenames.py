# demo_nodenames.py:

# Demonstrates the following MeqTree features:
# - The various ways that node names can be defined
# - Including qualifiers

# Tips:
# - All the information is in the Trees panel:
#   - Expand the various (groups of) nodes
#   - Check in _define_forest() how their names were generated



 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq
# from qt import *
# from numarray import *

# from Timba.Contrib.JEN.util import JEN_bookmarks

# Make sure that all nodes retain their results in their caches,
# for your viewing pleasure.
Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



#********************************************************************************
# The function under the 'blue button':
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   # Organise in groups (cc) of related nodes.
   # These are bundled by supplying the cc as children to a MeqComposer node.
   # Bundle the groups in the same way into a child-list (gg):

   gg = []


   group = 'qualifiers'
   sp1 = ns['station_phase'](s1=3) << 2.2
   sp2 = ns['station_phase'](s1=4) << -5.1
   cc = []
   cc.append(ns['ifr_phase'](s1=3, s2=4) << Meq.Subtract(sp1,sp2))
   cc.append(ns['qmerge'].qmerge(sp1,sp2) << Meq.Subtract(sp1,sp2))
   cc.append(ns['qadd'](q=8).qadd(sp1,sp2) << Meq.Subtract(sp1,sp2))
   gg.append(ns[group] << Meq.Composer(children=cc))

   # The root node of the tree can have any name, but in this example it
   # should be named 'result', because this name is used in the default
   # execute command (see below), and the bookmark.
   result = ns['result'] << Meq.Composer(children=gg)

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
#********************************************************************************




