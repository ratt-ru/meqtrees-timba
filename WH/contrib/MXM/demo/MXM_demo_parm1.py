# MXM_demo_parm.py:

# Simple Tree with a solver and several  parameters, demonstrates parameter options 
### For more information please visit
### http://lofar9.astron.nl/meqwiki/MeqParm

# Tips:

# The parameters are stored in the meptable. you can browse this to view the solutions


 
#********************************************************************************
# Initialisation:
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

Settings.forest_state.cache_policy = 100
Settings.forest_state.bookmarks = []



def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""
   #You can attach a meptable to a Parm by setting the field table_name,
   # the funklet will then be initialized (if available) from 
   # and (after solving) stored in the table.
   meptable ="test1.mep"
   #set this as the table for all our parms

   
   # a parm is initialized with a 'funklet'. The most common funklet is the 'polc' a
   # 2-dim polynomial in freq. and time. You can define the polc by giving a 2d array of its coefficients
   # The shape of the array determinse the polynomial
   polc = meq.polc([[1.,.02,.03],[.04,.005,.00001]]); #1.+0.02*f +0.03*f^2 +0.04*t +0.005*t*f +0.00001*t*f^2
   #polc = meq.polc([[1.,.02,.03],[.04,.005,0.]]); #1.+0.02*f +0.03*f^2 +0.04*t +0.005*t*f 
   polc_parm = ns['polc_parm'] <<Meq.Parm(init_funklet = polc,node_groups='Parm',table_name=meptable);


   # Alternatively, you can fix the shape of the Polc by setting the shape field of the connected Parm.
   # All missing coeffs will be initialized wiht zero's.
   shape_parm = ns['shape_parm']<<Meq.Parm(1.,shape=[2,3],node_groups = 'Parm',table_name=meptable); #results in a [[1,0.0],[0.0.0]] polc.
   
   # Now lets fit shape_parm to polc_parm. You can set any parm solvable or non-solvable.
   # In this case we set shape_parm solvable and polc_parm non-solvable.
   #
   
   condeq_polc_shape = ns['condeq_polc_shape'] << Meq.Condeq(children=(polc_parm,shape_parm))

   # Now create a solver node. A solver can have several children, but they all must be condeqs.
   solver = ns['solver'] << Meq.Solver(children=(condeq_polc_shape,),
                                       solvable = ['shape_parm'], #list of solvable parameters 
                                       num_iter = 10,       #stop after 10 iterations or after convergence
                                       epsilon = 1e-4,       #convergence limit, good default
                                       last_update=True,    #sends last update to parms after convergence, needed for saving funklets
                                       save_funklets=True   #needed to save funklets in parmtable
                                       )


   # When running the script, first display the bookmarks, since some of the nodes wont have a result cached after the run
   bm = record(name='result',page=
               [ record(viewer='Result Plotter',udi='/node/polc_parm', publish=True, pos=(0,0)),
                 record(viewer='Result Plotter',udi='/node/shape_parm', publish=True, pos=(0,1)),
                 record(viewer='Result Plotter',udi='/node/condeq_polc_shape', publish=True, pos=(1,0)),
                 record(viewer='Result Plotter',udi='/node/solver', publish=True, pos=(1,1))
                 ])
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
# Comments:
#
# The final difference between the shape_parm and the polc_parm can be explained by the fact that for
# solvable polcs per default the lower right triangle of coefficients is kept to 0.
# i.e. all c_nm with (n+m) > max(n,m). (0-based)
#
# You can check the solution by looking at the coefficients of the funklet in the record browser or in the meptable
# if you set the 6th coefficient of the polc_parm to 0. instead of 0.00001, you should get a near perfect solution





