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
from PyParmTable import *

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []

#new_table='new.mep'
new_table=None
old_table='/home/mevius/Timba/PyApps/test/103.mep'
parmname = 'GAmp:X:8';
global t;

def _define_forest (ns, **kwargs):
   """Definition of a solver node with 1 solvable parameter"""
   global t;

   # Make a Parm  node, initialize it with constant 1.
   # The node_groups='Parm' options is needed to be recognized by the solver
   parm = ns['new_parm1'] << Meq.Parm(2,node_groups='Parm',spline = record(freq=50),table_name=new_table)
   parm2 = ns['new_parm2'] << Meq.Parm(2,shape=[1,1],node_groups='Parm',table_name=new_table)
   old_parm = ns[parmname] << Meq.Parm(1.,table_name=old_table)

   subtract = ns['subtract']<<Meq.Subtract(parm,parm2)

   # The Condeq has exactly 2 children: the 'model' (in this case the parm)
   # and the 'data' on which you want to fit the 'model'.
   # solvable parm can be on both sides, so there is no real distinction between 'model' and 'data' here.
   condeq = ns['condeq'] << Meq.Condeq(children=(parm,old_parm*1e3))
   condeq2 = ns['condeq2'] << Meq.Condeq(children=(parm2,old_parm*1e3))
   # Now create a solver node. A solver can have several children, but they all must be condeqs.
   solver = ns['solver'] << Meq.Solver(children=(condeq,condeq2),
                                       solvable = [parm,parm2], #list of solvable parameters 
                                       num_iter = 50,       #max number of iterations
                                       epsilon = 1e-4,      #convergence limit, good default
                                       last_update=True,
                                       save_funklets=True
                                       )
   ns.reqseq <<Meq.ReqSeq(solver,subtract);
   # Make a bookmark of the result node, for easy viewing:
   parm = ns['test_parm'] << Meq.Parm([[0.,0.,1.,0.,0.,0.,0.,0.]],node_groups='Parm',spline = record(freq=100),table_name=new_table)
   condeq3 = ns['condeq3'] << Meq.Condeq(children=(parm,old_parm*1e3))
   # Now create a solver node. A solver can have several children, but they all must be condeqs.
   solver2 = ns['solver2'] << Meq.Solver(children=(condeq3),
                                       solvable = [parm], #list of solvable parameters 
                                       num_iter = 1,       #max number of iterations
                                       epsilon = 1e-4,      #convergence limit, good default
                                       last_update=True,
                                       save_funklets=True
                                       )
   ns.reqseq <<Meq.ReqSeq(solver,subtract);
   bm = record(name='result',page=
               [record(viewer='Result Plotter',udi='/node/solver', publish=True, pos=(0,0)),
                record(viewer='Result Plotter',udi='/node/GAmp:X:8', publish=True, pos=(0,1)),
                record(viewer='Result Plotter',udi='/node/condeq', publish=True, pos=(1,0)),
                record(viewer='Result Plotter',udi='/node/new_parm1', publish=True, pos=(1,1)),
                record(viewer='Result Plotter',udi='/node/condeq2', publish=True, pos=(2,0)),
                record(viewer='Result Plotter',udi='/node/subtract', publish=True, pos=(0,2)),
                record(viewer='Result Plotter',udi='/node/new_parm2', publish=True, pos=(2,1))])
   Settings.forest_state.bookmarks.append(bm)


   t=ParmTable(old_table,ns,"GAmp:X:1*",fit=True);
   # Finished:
   return True



#********************************************************************************
# The function under the TDL Exec button:
#********************************************************************************

def _tdl_job_execute (mqs, parent):
    """Execute the solver"""
    global t;
    domain = meq.domain(1391119000.845,1406763532.095,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=801, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='reqseq', request=request))
    return result
 
def _tdl_job_execute2 (mqs, parent):
    """Execute the newparm"""
    domain = meq.domain(0,1,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=801, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='solver2', request=request))
    return result

def _tdl_job_table_inspector (mqs, parent):
    result = t.Inspector(mqs);
       
#********************************************************************************
#********************************************************************************
# The solver plot contains a lot of information about the number of iterations,
# the number of parameters, the chi^2 surface, the change of the parameters per iteration



