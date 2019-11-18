# -*- coding: utf-8 -*-
from Timba.TDL import *

# define some compile-time options
TDLCompileOption('a',"Value of a",1,more=float);
TDLCompileOption('b',"Value of b",0,more=float);

# define some runtime options
TDLRuntimeOption('t0',"Start time",0,more=float);
TDLRuntimeOption('t1',"End time",1,more=float);

# import a module -- this defines some options of its own
import pipeline_test_constants

#
# This makes a tree to evaluate a*t+b, where a and b are compile-time options
#
def _define_forest (ns,**kw):
  ns.a << a;
  ns.b << b;
  ns.root << ns.a*Meq.Time() + ns.b;


#
# This evaluates the tree for t=t0,...,t1 (t0 and t1 are runtime options)
#
def _test_forest (mqs,parent,wait=False,**kw):
  print("=== Evaluating %g*t%+g for t=[%g,%g]"%(a,b,t0,t1));
  print("=== Dummy values: %g %g"%(pipeline_test_constants.c0,pipeline_test_constants.c1));
  from Timba.Meq import meq
  # run tests on the forest
  domain = meq.gen_domain(time=[t0,t1]);
  cells = meq.gen_cells(domain,num_time=10);
  request = meq.request(cells,rqtype='ev',new_domain=True);
  res = mqs.execute('root',request,wait=wait);
  if wait:
    print(res.result.vellsets[0].value);

# This defines some more TDL jobs. Both of these will in fact be equivalent to calling _test_forest, but
# we give them different IDs to show off the job-finding codes in run_pipeline_test.py
TDLRuntimeJob(_test_forest,"Run job 1",job_id='job1');
TDLRuntimeMenu("Runtime menu",
  TDLJob(_test_forest,"Run job 2",job_id='job2')
);


if __name__ == '__main__':
  print("""Please use "python run_pipeline_test.py" to run this script in pipeline mode""");
