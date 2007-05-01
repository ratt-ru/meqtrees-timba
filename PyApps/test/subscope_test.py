# standard preamble
from Timba.TDL import *

# Timba.TDL.Settings.forest_state is a standard TDL name. 
Settings.forest_state.cache_policy = 100;

def _define_forest (ns,**kwargs):
  """define_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, this method is automatically called to
  define the forest. The 'ns' argument is a NodeScope object in which
  the forest is to be defined, usually this is simply the global scope.
  """;
  ns.foo << 1;
  ns.foo(1,x=2) << 1;
  ns1 = ns.Subscope('a',1,x=2);
  ns1.foo << 1;
  ns1.foo1(1,x=2) << 1;
  ns2 = ns1.Subscope('b',3,y=4);
  ns2.foo << ns.foo + ns1.foo;
  ns2.foo2(1,x=2) << 1;
  ns3 = ns.QualScope(5,z=6);
  ns3.foo << ns.foo + ns2.foo;
  ns3.foo3(1,x=2) << 1;
  ns4 = ns3.QualScope(7,x=8);
  ns4.foo << ns3.foo + ns2.foo;
  ns4.foo4(1,x=2) << 1;
  ns5 = ns3.Subscope('c',9,y=10);
  ns5.foo << ns4.foo + ns3.foo;
  ns5.foo5(1,x=2) << 1;
  ns6 = ns5(10,z=11);   # equivalent to QualScope
  ns6.foo << ns5.foo + ns4.foo;
  ns6.foo6(1,x=2) << 1;
  ns7 = ns2.QualScope(12,x=13);
  ns7.foo << ns6.foo + ns5.foo;
  ns7.foo7(1,x=2) << 1;
  ns7 << Meq.Freq;
  ns6 << Meq.Freq;
  ns5 << Meq.Freq;
  ns4 << Meq.Freq;
  ns3 << Meq.Freq;
  ns2 << Meq.Freq;
  ns1 << Meq.Freq;
  # now test node scopifying
  ns8 = ns5.foo5(11,x=22).Subscope();
  ns8.foo << Meq.Time;
  ns9 = ns6.foo6(11,x=22).QualScope();
  ns9.foo6a(1,x=2) << 1;

  # this tests for conflicting node, by contriving to create two nodes with the same
  # fully-qualified name, via qualscopes.
  # The node below gives the same name as ns3.foo. If uncommented, this should produce
  # a NodeRedefinedError
  # ns.foo(5,z=6) << 1;

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

# this is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
