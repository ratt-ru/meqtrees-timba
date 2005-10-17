# Short description:
# demo of the resampler node

# History:
# Mon Oct 17 11:26:00 CEST 2005: creation
# $Date$

# Copyright: The MeqTree Foundation 

# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq
Settings.forest_state.cache_policy = 100;

# for bookmarks
from Timba.Contrib.JEN import MG_JEN_forest_state

#=====================================================================
#=====================================================================
def _define_forest (ns):
  ns.x<<Meq.Parm(meq.array([[1,0.2,0.11],[-0.3,0.1,0.21]]))
  n1=ns['node1']<<0.01*ns.x
  n2=ns['node2']<<0.02*ns.x
  n3=ns['add']<<Meq.ToComplex(n1,n2)
 # if flag_density>=1. upsampling
 # if it is <1, downsampling
  # if it is 0 or negitive, no sampling
  root=ns.root<<Meq.Resampler(n3,flag_density=0.1)
  ns.Resolve()

  MG_JEN_forest_state.bookmark(n3,page="Plots",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(root,page="Plots",viewer="Result Plotter");

#=====================================================================
#=====================================================================
def _test_forest (mqs, parent):
 f0 = 1200
 f1 = 1600
 t0 = 0.0
 t1 = 1.0
 nfreq = 50
 ntime = 50
 # create cells
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 request = meq.request(cells,eval_mode=1);
 b = mqs.meq('Node.Execute',record(name='root',request=request),wait=True);
 print "result=",b;

  

#=====================================================================
#=====================================================================
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns);
  ns.Resolve()
