# MXM_demo_solve.py:

# Demonstrates the following MeqTree features:
# Simple Tree to solve a parameter 

# Tips:
#For more parameter options, see demo_parm.py


 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



def _define_forest (ns, **kwargs):
   """Definition of a solver node with 1 solvable parameter"""

   # Make a Parm  node, initialize it with constant 1.
   # The node_groups='Parm' options is needed to be recognized by the solver
   parm = ns['parm'] << Meq.Parm(1.,node_groups='Parm')

   #We are going to fit the constant to a node varying in frequency
   freq = ns.freq << Meq.Freq()

   # The Condeq has exactly 2 children: the 'model' (in this case the parm)
   # and the 'data' on which you want to fit the 'model'.
   # solvable parm can be on both sides, so there is no real distinction between 'model' and 'data' here.
   condeq = ns['condeq'] << Meq.Condeq(children=(parm,freq))

   # Now create a solver node. A solver can have several children, but they all must be condeqs.
   solver = ns['solver'] << Meq.Solver(children=(condeq),
                                       solvable = ['parm'], #list of solvable parameters 
                                       num_iter = 10,       #max number of iterations
                                       epsilon = 1e-4       #convergence limit, good default
                                       )
   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result',page=
               [record(viewer='Result Plotter',udi='/node/solver', publish=True, pos=(0,0)),
                record(viewer='Result Plotter',udi='/node/condeq', publish=True, pos=(0,1)),
                record(viewer='Result Plotter',udi='/node/parm', publish=True, pos=(1,0)),
                record(viewer='Result Plotter',udi='/node/freq', publish=True, pos=(1,1))])
   Settings.forest_state.bookmarks.append(bm)

   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the solver"""
    domain = meq.domain(1,10,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='solver', request=request))
    return result
       
#********************************************************************************
#********************************************************************************
# The solver plot contains a lot of information about the number of iterations,
# the number of parameters, the chi^2 surface, the change of the parameters per iteration



