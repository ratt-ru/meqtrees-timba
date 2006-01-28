
# standard preamble
from Timba.TDL import *
from Timba.Meq import meq

# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;
Settings.forest_state.bookmarks = [
 record(name='Parms',page=[
    record(viewer="Result Plotter",udi="/node/x",pos=(0,0)),
    record(viewer="Result Plotter",udi="/node/y",pos=(0,1)),
    record(viewer="Result Plotter",udi="/node/add(x,y)",pos=(1,0)),
    record(viewer="Result Plotter",udi="/node/condeq",pos=(1,1))
 ])
]; 
    
  
# Make sure our root node is not cleaned up
Settings.orphans_are_roots = True;

def _define_forest_1 (ns,**kwargs):
  # constant side is a t+f thingy,
  # two parms: a const thingy with size-2 tiles
  # and a linear-n-freq thingy with size-3 tiles
  ns.c = Meq.Freq() + Meq.Time();
  ns.x = Meq.Parm(0,node_groups='Parm',tiling=record(time=2));
  ns.y = Meq.Parm(meq.polc([0,0],shape=(1,2)),node_groups='Parm',tiling=record(time=3));
  
  ns.solver <<Meq. Solver(
        num_iter=30,epsilon=1e-5,debug_level=10,solvable=["x","y"],
        children = ns.condeq << Meq.Condeq(ns.x+ns.y,ns.c) );
                

def _define_forest_2 (ns,**kwargs):
  # constant side is a t slope, plus a sine wave
  # two parms: c00 with tile size 2 (expecting to fit the slope in steps)
  # and 4-th degree polc in time with tile size 10 (expecting to fit the sine)
  # Fit should be on a 100x1 grid.
  ns.c = Meq.Time()*5 + Meq.Sin(Meq.Time()*6.28*7);  # a bit more than one period over a tile
  ns.x = Meq.Parm([0,0],node_groups='Parm',tiling=record(time=20));
  ns.y = Meq.Parm(meq.polc([0,0,0,0],shape=(4,1)),node_groups='Parm',tiling=record(time=12));
  
  ns.solver <<Meq. Solver(
        num_iter=30,epsilon=1e-5,debug_level=10,solvable=["x","y"],
        children = ns.condeq << Meq.Condeq(ns.x+ns.y,ns.c) );
    
_define_forest = _define_forest_2
    

def _test_forest (mqs,parent,**kwargs):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=1,num_time=100);
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
