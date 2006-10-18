# JEN_leaves.py:

# Demonstrates the following MeqTree features:
# - Various kinds of end-point nodes ('leaves')
# - These are nodes without children
# - They have access to their own data to satisfy requests





 
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

# Leaves:
#   5691 2006-09-14 14:36 Parm.cc
#   5691 2006-09-14 14:36 Constant.cc
#   2201 2006-09-14 14:36 Freq.cc
#   2193 2006-09-14 14:36 Time.cc
#   3008 2006-09-14 14:36 Grid.cc
#   2466 2006-09-14 14:36 GridPoints.cc
#    759 2006-09-14 14:36 NoiseNode.cc
#   3568 2006-09-14 14:36 RandomNoise.cc
#     64 2006-09-14 14:36 BlitzRandom.cc
#   3432 2006-09-14 14:36 GaussNoise.cc
#                         Spigot?
#                         TDL_Leaves....?

   # Organise in groups (cc) of related nodes.
   # These are bundled by supplying the cc as children to a MeqComposer node.
   # Bundle the groups in the same way into a child-list (gg):

   gg = []

   # Freq, time etc 
   group = 'dims'
   cc = [
      ns << Meq.Freq(),
      ns << Meq.Time(),
      ns << Meq.GridPoints(),
      ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)


   stddev = 1.0
   g1 = ns['gaussnoise('+str(stddev)+')'] << Meq.GaussNoise(stddev=1.0)
   # r1 = ns['randomnoise('+str(stddev)+')'] << Meq.RandomNoise(stddev=1.0)  # crashes the browser
   # b1 = ns['blitzrandom('+str(stddev)+')'] << Meq.BlitzRandom(stddev=1.0)  # does not exist

   # Generate cell-by-cell noise: 
   group = 'noise'
   cc = [
      g1,
      ns << g1 + 1,
      ns << Meq.Exp(g1),
      # r1, 
      # b1, 
      ]
   gg.append(ns[group] << Meq.Composer(children=cc))
   JEN_bookmarks.create(cc, group)



   #==============================================================

   # Make a group of groups:
   result = ns.result << Meq.Composer(children=gg)
   gg.append(result)
   JEN_bookmarks.create(gg, 'overall')

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1,10,-100,100)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=19, num_time=19)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_sequence (mqs, parent):
    """Execute the forest a number of times"""
    domain = meq.domain(1,10,-100,100)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=19, num_time=19)
    for domain_id in range(10):
       rqid = meq.requestid(domain_id=domain_id)
       request = meq.request(cells, rqtype='ev', rqid=rqid)
       result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

#********************************************************************************
# Comments:
#********************************************************************************

#********************************************************************************
#********************************************************************************




