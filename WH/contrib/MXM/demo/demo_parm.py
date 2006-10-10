# demo_parm.py:

# Demonstrates the following MeqTree features:
# Simple Tree with a solver and several  parameters, demonstartes paramter options 

# Tips:

# The parameters are stored in the meptable. you can browse this to view the solutions


 
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
   #You can attach a meptable to a Parm by setting the field table_name,
   # the funklet will then be initialized (if available) from 
   # and (after solving) stored in the table.
   meptable ="test.mep"
   #set this as the table for all our parms

   
   # Make a Parm  node, initialize it with constant 1.
   # The node_groups='Parm' options is needed to be recognized by the solver
   #tiling means that you have independent solutions for different time/freq slots.
   #We make our simple_parm less simple, by tiling it in freq and time:

   
   simple_parm = ns['simple_parm'] << Meq.Parm(1.,node_groups='Parm',table_name=meptable,
                                               tiling= record(freq=1,time=2)
                                               #Gives an independent solution per freq. cell
                                               # and per 2 time cells
                                               )

   # a parm is initialized with a 'funklet' the most common funklet is the 'polc' a
   # 2-dim polynomial in freq. and time, you can define the polc by giving a 2d array of its coefficients
   # The shape of the array determinse the polynomial
   polc = meq.polc([[1.,.02,.03],[.04,.005,.00001]]); #1.+0.02*f +0.03*f^2 +0.04*t +0.005*t*f +0.00001*t*f^2
   polc_parm = ns['polc_parm'] <<Meq.Parm(init_funklet = polc,node_groups='Parm',table_name=meptable);


   # Alternatively, you can fix the shape of the Polc by setting the shape field of the connected Parm.
   # All missing coeffs will be initialized wiht zero's.
   shape_parm = ns['shape_parm']<<Meq.Parm(1.,shape=[2,3],node_groups = 'Parm',table_name=meptable); #results in a [[1,0.0],[0.0.0]] polc.
   
   # A more general, but sometimes slow, option is to make use of the Aips++ functional interpreter
   # to create any real function. This is done by setting the "function" field of the polc.
   functional = meq.polc([1.,2.,1.5]); # The number of coeffs should match the number of p# in function 
   functional.function = "p0+p1*exp(-0.01*x0^2)*sin(x1*p2)";
   functional_parm =  ns['functional_parm'] <<Meq.Parm(init_funklet = functional ,node_groups='Parm',table_name=meptable);





 
   # Now a nonsense fit. lets fit simple_parm to the functional_parm, and shape_parm to polc_parm
   # The final difference between the shape_parm and the polc_parm can be explained by the fact that for
   # solvable polcs per default the lower right triangle of coefficients is kept to 0.
   # i.e. all c_nm with (n+m) > max(n,m)
   #
   # The Condeq has exactly 2 children: the 'model' (in this case the parm)
   # and the 'data' on which you want to fit the 'model'.
   # solvable parm can be on both sides, so there is no real distinction between 'model' and 'data' here.
   condeq_polc_shape = ns['condeq_polc_shape'] << Meq.Condeq(children=(polc_parm,shape_parm))
   condeq_simple_functional = ns['condeq_simple_functional'] << Meq.Condeq(children=(simple_parm,functional_parm))

   # Now create a solver node. A solver can have several children, but they all must be condeqs.
   solver = ns['solver'] << Meq.Solver(children=(condeq_polc_shape,
                                                 condeq_simple_functional),
                                       solvable = ['simple_parm','shape_parm'], #list of solvable parameters 
                                       num_iter = 10,       #stop after 10 iterations or after convergence
                                       epsilon = 1e-4,       #convergence limit, good default
                                       last_update=True,    #sends last update to parms after convergence
                                       save_funklets=True  #needed to save funklets in parmtable
                                       )
   # Make a bookmark of the result node, for easy viewing:
   bm = record(name='result',page=
               [record(viewer='Result Plotter',udi='/node/simple_parm', publish=True, pos=(0,0)),
                record(viewer='Result Plotter',udi='/node/polc_parm', publish=True, pos=(1,0)),
                record(viewer='Result Plotter',udi='/node/functional_parm', publish=True, pos=(0,1)),
                record(viewer='Result Plotter',udi='/node/shape_parm', publish=True, pos=(1,1)),
                record(viewer='Result Plotter',udi='/node/condeq_polc_shape', publish=True, pos=(1,2)),
                record(viewer='Result Plotter',udi='/node/condeq_simple_functional', publish=True, pos=(0,2)),
                record(viewer='Result Plotter',udi='/node/solver', publish=True, pos=(2,0))
                ])
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
    result = mqs.meq('Node.Execute',record(name='solver', request=request))
    return result
       
#********************************************************************************
#********************************************************************************




