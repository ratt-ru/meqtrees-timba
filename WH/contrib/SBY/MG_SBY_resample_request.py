# Short description:
# demo of the resampler node, especially when downsampling

# History:
# Mon Oct 17 11:26:00 CEST 2005: creation
# $Date$

# Copyright: The MeqTree Foundation 


# Full description:
# This script tests the Meq.Resampler node.
# The Resampler node can act in 2 distinct ways:
#
# 1) Resample the result obtained from its child node
# 2) Resample the request before passing it to the child node
#
# The above two ways of acting are mutually exclusive. The way to
# change its behaviour is by changing the variable 'flag_bit' in 
# the init record of the Resampler node. 
#
# You can make the Resampler node to act in the way of (1) if you make
#   flag_bit=0 
# and  this is the default behaviour. If you make 'flag_bit' take any other
# value, it will act as (2).

# Each Resampler can have only one child node. The resampler can work in
# both directions, i.e. downsampling and upsampling. The amount of resampling
# can be given when the node is created using the init record. The variable
# you need to change in this case is 'flag_density'. If you make 
#   flag_density < 1,   
# it will downsample. If you make 
#   flag_density >1, it will upsample.

# Note that flag_density cannot be negative.

#
# In order to calculate its performance, this script downsamples the Result
# in one node and  downsamples the Request in another. Ideally, both should
# produce the same output. We can see the error of downsampling by 
# substracting the two.


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
  # 2D resampling
  ns.x<<Meq.Parm(meq.array([[1,0.2,0.01],[-0.3,0.1,0.21]]))
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

  # if flag_bit ==0, resample the request
  # if flag_bit !=0, resample the result
  rootxc=ns.rootxc<<Meq.Resampler(n1,flag_density=0.1,flag_bit=1)
  rootxd=ns.rootxd<<Meq.Resampler(n2,flag_density=0.1,flag_bit=0)
  root1=ns['2D_Error']<<(rootxc-rootxd)


  # 1D resampling
  ns.a<<Meq.Parm(meq.array([1,20,0.01]))
  ns.b<<Meq.Parm(meq.array([1,20,0.01]))
  nar=ns['nodea']<<0.01*ns.a
  nai=ns['nodeai']<<-0.01*ns.a

  nbr=ns['nodeb']<<0.01*ns.b
  nbi=ns['nodebi']<<-0.01*ns.b

  n3=ns['n3']<<Meq.ToComplex(nar,nai)
  n4=ns['n4']<<Meq.ToComplex(nbr,nbi)
  rootac=ns.rootac<<Meq.Resampler(n3,flag_density=0.1,flag_bit=1)
  rootbd=ns.rootbd<<Meq.Resampler(n4,flag_density=0.1,flag_bit=0)
  root2=ns['1D_Error']<<(rootac-rootbd)

  ns.Resolve()

  MG_JEN_forest_state.bookmark(root1,page="Error",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(root2,page="Error",viewer="Result Plotter");

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
 b = mqs.meq('Node.Execute',record(name='1D_Error',request=request),wait=True);
 b = mqs.meq('Node.Execute',record(name='2D_Error',request=request),wait=True);
  

#=====================================================================
#=====================================================================
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns);
  ns.Resolve()
