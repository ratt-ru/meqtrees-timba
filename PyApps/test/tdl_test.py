# -*- coding: utf-8 -*-
# standard preamble
from Timba.TDL import *

TDLCompileMenu('menu',TDLCompileOption('dum','Dummy',True));

menu1 = TDLCompileMenu('another menu',
   TDLCompileOption('dum2','dummy',True),summary='summary',toggle='dum3');
 
# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;
Settings.forest_state.log_policy = 0;
Settings.forest_state.a = None;

# Make sure our solver root node is not cleaned up
Settings.orphans_are_roots = True;

def _define_forest (ns,**kwargs):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  print("_define_solver() kwargs",kwargs);
  ns['solver'] << Meq.Solver(
      num_iter=15,debug_level=10,solvable="x",epsilon=1e-5,last_update=True,save_funklets=True,
      children = Meq.Condeq(
        Meq.Parm([0,2]),
        5 + (ns.x << Meq.Parm(0,node_groups='Parm',table_name='test2345',shape=[2,3],log_policy=100)),
        a=None
      ),
    );
  # make solver2 fail deliberately by specifying a non-existent solvable
  # this tests our error handling
  ns.solver2 << Meq.Solver(
      num_iter=5,debug_level=10,solvable="x",
      children = Meq.Condeq(
        Meq.Parm([0,1]),
        5 + (ns.y << Meq.Parm(0,node_groups='Parm')),
        a=None
      ),
    );
  # make a test branch for other purposes
  ns.t << Meq.Time();
  ns.f << Meq.Freq();
  ns.xy = ns.t + ns.f;
  ns.flag1 << Meq.ZeroFlagger(ns.t-.5,oper="ge");
  ns.flag2 << Meq.ZeroFlagger(ns.f-.5,oper="ge");
  ns.test << Meq.Composer(
    Meq.ReplaceFlaggedValues(ns.xy,ns.flag1,ns.flag2,value=1+1j),
  );
  ns.reqseq = Meq.ReqSeq(ns.solver,ns.solver2,ns.test);
    

def _test_forest (mqs,parent,**kwargs):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=6,num_time=4);
  request = meq.request(cells,rqtype='ev');
  mqs.meq('Node.Execute',record(name='x',request=request));
  mqs.meq('Save.Forest',record(file_name='tile_test.forest.save'));
  # execute request on solver
  request = meq.request(cells,rqtype='ev');
#  mqs.meq('Node.Set.Breakpoint',record(name='solver'));
#  mqs.meq('Debug.Set.Level',record(debug_level=100));
  a = mqs.meq('Node.Execute',record(name='reqseq',request=request),wait=False);

def _tdl_job_test1 (mqs,parent):
  """this is a test job. You can see it appear in the menu automatically."""
  pass;

def _tdl_job_test2 (mqs,parent):
  """this is another test job. You can see it appear in the menu automatically."""
  pass;


# this is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
