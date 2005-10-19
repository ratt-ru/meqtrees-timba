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
  ns.y<<Meq.Parm(meq.array([[1,0.2,0.01],[-0.3,0.1,0.21]]))
  nxr=ns['nodex']<<0.01*ns.x
  nxi=ns['nodexi']<<-0.01*ns.x

  nyr=ns['nodey']<<0.01*ns.y
  nyi=ns['nodeyi']<<-0.01*ns.y

  n1=ns['n1']<<Meq.ToComplex(nxr,nxi)
  n2=ns['n2']<<Meq.ToComplex(nyr,nyi)
  # if flag_density>=1. upsampling
  # if it is <1, downsampling
  # if it is 0 or negitive, no sampling
  rootxc=ns.rootxc<<Meq.Resampler(n1,flag_density=0.1,flag_bit=1)
  rootxd=ns.rootxd<<Meq.Resampler(n2,flag_density=0.1,flag_bit=0)
  root1=ns.root1<<(rootxc-rootxd)

  ns.a<<Meq.Parm(meq.array([1,20,0.01])) #2D
  ns.b<<Meq.Parm(meq.array([1,20,0.01]))
  nar=ns['nodea']<<0.01*ns.a
  nai=ns['nodeai']<<-0.01*ns.a

  nbr=ns['nodeb']<<0.01*ns.b
  nbi=ns['nodebi']<<-0.01*ns.b

  n3=ns['n3']<<Meq.ToComplex(nar,nai)
  n4=ns['n4']<<Meq.ToComplex(nbr,nbi)
  # if flag_density>=1. upsampling
  # if it is <1, downsampling
  # if it is 0 or negitive, no sampling
  rootac=ns.rootac<<Meq.Resampler(n3,flag_density=0.1,flag_bit=1)
  rootbd=ns.rootbd<<Meq.Resampler(n4,flag_density=0.1,flag_bit=0)
  root2=ns.root2<<(rootac-rootbd)

  ns.Resolve()

  #MG_JEN_forest_state.bookmark(n1,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(root1,page="Complex Resampling",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(root2,page="Complex Resampling",viewer="Result Plotter");

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
 b = mqs.meq('Node.Execute',record(name='root1',request=request),wait=True);
 b = mqs.meq('Node.Execute',record(name='root2',request=request),wait=True);
 #print "Real result=",b;
 #b = mqs.meq('Node.Execute',record(name='n1',request=request),wait=True);
 #print "Complex result=",b;
  

#=====================================================================
#=====================================================================
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns);
  ns.Resolve()
