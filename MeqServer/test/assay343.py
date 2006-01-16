# pull this first to skip all GUI definitions and includes
from Timba.Apps import app_nogui
from Timba.Apps import assayer

import sys
import traceback
import os
import numarray

def vs_stats (res):
  """helper function to convert a result to a list of
  (min,max,mean) values corresponding to each vellset."""
  stats = [];
  for vs in res.vellsets:
    a = vs.value;
    stats.append((a.min(),a.max(),a.mean()));
  return stats;

# testing branch
if __name__ == '__main__':
  # just to make sure
  os.system("killall -9 meqserver meqserver-opt");
  
  # flush parm tables
  os.system("rm -fr *.mep");
  
  ass = assayer.assayer("assay343");
  ass.compile("matrix343.py");
  
  # test source fluxes
  
  ass.init_test("source-flux");
  ass.watch("stokes:I:3C343/cache.result",rqtype="ev");
  ass.watch("stokes:Q:3C343/cache.result",rqtype="ev");
  ass.watch("stokes:I:3C343_1/cache.result",rqtype="ev");
  ass.watch("stokes:Q:3C343_1/cache.result",rqtype="ev");
  for s1 in range(1,15):
    for s2 in range(s1+1,15):
      node = ":".join(("corrected",str(s1),str(s2)));
      ass.watch(node+"/cache.result",rqtype="ev",functional=vs_stats);
## watching the solver is not necessarily a good idea since we may change the 
## layout of the solver metrics. In any case simply verifying the actual
## solvables have the same values is sufficient.
#  ass.watch("solver/cache.result");
#  ass.watch("VisDataMux/cache.result");
  ass.run("_tdl_job_source_flux_fit_no_calibration",write=False);
  
  # print some stuff for easy reference
  print '3C343 I flux:',ass.mqs.getnodestate("stokes:I:3C343").funklet.coeff.tolist();
  print '3C343_1 I flux:',ass.mqs.getnodestate("stokes:I:3C343_1").funklet.coeff.tolist();

  stat = ass.finish_test();
  if stat:
    print "ASSAY FAILED: ",stat;
    sys.exit(stat);

# we watch all the solvables to verify that their final fitted values are 
# the same. The rqtype argument to watch() restricts the watched results
# to "ev"-type requests only, which are generated after a solution has
# converged. Not only does this keep the recorded values to a reasonable number,
# it is also more robust against, e.g., improvements in the solver algorithm.
# As long as the final values are the same, we don't care how the solver got 
# there (and if it took too long, the runtime assay will catch it).
  ass.init_test("phase-all-values");
#  for patch in ("centre","edge"):
#    for st in range(1,15):
#      node = ":".join(("J",str(st),patch));
#      ass.watch(node+"/cache.result",rqtype="ev");
  for s1 in range(1,15):
    for s2 in range(s1+1,15):
      node = ":".join(("corrected",str(s1),str(s2)));
      ass.watch(node+"/cache.result",rqtype="ev",functional=vs_stats);
      
## Watching the solver is not necessarily a good idea since we may change the 
## layout of the solver metrics. In any case simply verifying the actual
## solvables have the same values is sufficient.
#  ass.watch("solver/cache.result.solver_result.incremental_solutions",1e-4);
#  ass.watch("VisDataMux/cache.result");
  ass.run("_tdl_job_phase_solution_with_given_fluxes_all",write=False);
    
  stat = ass.finish_test();
  if stat:
    print "ASSAY FAILED: ",stat;
    sys.exit(stat);
    
    
  ass.finish();

