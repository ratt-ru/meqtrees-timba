
# standard preamble
from Timba.TDL import *

# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

# Make sure our root node is not cleaned up
Settings.orphans_are_roots = True;

def _define_forest_1 (ns,**kwargs):
  # constant side is a t+f thingy,
  # parm is subtiled 2x2
  ns.c = Meq.Freq() + Meq.Time();
  ns.x = Meq.Parm(0,node_groups='Parm',tiling=record(time=2,freq=2));
  
  ns.solver <<Meq. Solver(
        num_iter=5,debug_level=10,solvable="x",
        children = Meq.Condeq(ns.x,ns.c) );
        
def _define_forest_2 (ns,**kwargs):
  # constant side is a t+f thingy,
  # parm is subtiled 2x2
  ns.c = Meq.Freq + Meq.Time;
  ns.x = Meq.Parm(0,node_groups='Parm',tiling=record(time=2,freq=2));
  
  ns.solver << Meq.Solver(
        num_iter=5,debug_level=10,solvable="x",
        children = Meq.Condeq(ns.x,ns.c) );
        
    
_define_forest = _define_forest_1
    

def _test_forest (mqs,parent,**kwargs):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=20);
  request = meq.request(cells,rqtype='ev');
#  mqs.meq('Node.Set.Breakpoint',record(name='solver'));
#  mqs.meq('Debug.Set.Level',record(debug_level=100));
  a = mqs.meq('Node.Execute',record(name='solver',request=request),wait=False);


# this is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
