# Short description:
# demo of the resampler node

# History:
# Mon Oct 17 11:26:00 CEST 2005: creation
# $Date$

# Copyright: The MeqTree Foundation 


# Full description:
# This script tests the Meq.Resampler node. Unlike Meq.ModRes node,
# the Resampler resamples the Result obtained from the child node.
# Each Resampler can have only one child node. The resampler can work in
# both directions, i.e. downsampling and upsampling. The amount of resampling
# can be given when the node is created using the init record. In order 
# to calculate its performance, this script downsamples and then upsamples
# the same result to get a result at original resolution. It then calculates
# the error by substracting the original result by the resampled result.


# Import of Python modules:
from Timba.TDL import *
from Timba.Meq import meq
Settings.forest_state.cache_policy = 100;
Settings.orphans_are_roots = True;

# for bookmarks
from Timba.Contrib.JEN import MG_JEN_forest_state

#=====================================================================
#=====================================================================
def _define_forest (ns):
  ns.x<<Meq.Parm(meq.array([[1,0.2,0.01],[-0.3,0.1,0.21]])) #2D
  ns.y<<Meq.Parm(meq.array([1,20,-0.01])) # 1D
  ns.z<<Meq.Parm(0) # constant
  nxr=ns['nodex']<<0.01*ns.x
  nyr=ns['nodey']<<0.1*ns.y
  nzr=ns['nodez']<<0.01*ns.z
  nxi=ns['nodexi']<<-0.01*ns.x
  nyi=ns['nodeyi']<<-0.01*ns.y*ns.y
  nzi=ns['nodezi']<<-0.01*ns.z

  n1=ns['com1']<<Meq.ToComplex(nxr,nxi)
  n2=ns['com2']<<Meq.ToComplex(nyr,nyi)
  n3=ns['com3']<<Meq.ToComplex(nzr,nzi)
  # if flag_density>=1. upsampling
  # if it is <1, downsampling
  # if it is 0 or negitive, no sampling
  rootx=ns.rootx<<Meq.Resampler(nxr,flag_density=0.1)
  rooty=ns.rooty<<Meq.Resampler(nyr,flag_density=0.1)
  rootz=ns.rootz<<Meq.Resampler(nzr,flag_density=0.1)
  root_real=ns.rootr<<Meq.Composer(rootx,rooty,rootz)

  rootxc=ns.rootxc<<Meq.Resampler(n1,flag_density=0.1)
  rootyc=ns.rootyc<<Meq.Resampler(n2,flag_density=0.1)
  rootzc=ns.rootzc<<Meq.Resampler(n3,flag_density=0.1)
  root_complex=ns.rooti<<Meq.Composer(rootxc,rootyc,rootzc)

  # in order to calculate error, upsample and substract
  # from original result 
  rootxe=ns.xe<<(Meq.Resampler(rootxc,flag_density=10.0)-n1)
  rootye=ns.ye<<(Meq.Resampler(rootyc,flag_density=10.0)-n2)
  rootze=ns.ze<<(Meq.Resampler(rootzc,flag_density=10.0)-n3)
  root_error=ns.roote<<Meq.Composer(rootxe,rootye,rootze)
  ns.Resolve()

  MG_JEN_forest_state.bookmark(nxr,page="Real Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(rootx,page="Real Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(nyr,page="Real Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(rooty,page="Real Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(nzr,page="Real Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(rootz,page="Real Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(n1,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(rootxc,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(n2,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(rootyc,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(n3,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(rootzc,page="Complex Resampling",viewer="Result Plotter");
 
  MG_JEN_forest_state.bookmark(root_error,page="Errors",viewer="Result Plotter");

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
 b = mqs.meq('Node.Execute',record(name='rootr',request=request),wait=True);
 #print "Real result=",b;
 b = mqs.meq('Node.Execute',record(name='rooti',request=request),wait=True);
 #print "Complex result=",b;
 b = mqs.meq('Node.Execute',record(name='roote',request=request),wait=True);
 #print "Error result=",b;
  

#=====================================================================
#=====================================================================
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns);
  ns.Resolve()
