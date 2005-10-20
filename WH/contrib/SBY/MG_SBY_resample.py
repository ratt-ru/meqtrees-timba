script_name = 'MG_SBY_resample.py'

# Short description:
# Demo of the resampler node

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
# you need to change in this case is 'num_cells'. This is an array giving
# the dimensions you would like the result to be. For instance, if your
# original Request/Result had a cell of size [50,50] and if you give 
#   num_cells=[10,5],
# it will downsample. On the other hand, if you give
#   num_cells=[100,100],
# it will upsample. There are various wierd ways of giving the shape
# of num_cells, (go ahead! try giving values like [1,1], [100,1] or [1,100])
# 
# Note that in case of an error, the result will fall back to [1,1] and if
# you try to resample a scalar, you should get a [1,1] result.

# In order to calculate its performance, this script downsamples the Result
# in one node and  downsamples the Request in another. Ideally, both should
# produce the same output. We can see the error of downsampling by 
# substracting the two.
# This script also downsamples and then upsamples the same result to get 
# a result at original resolution to calculate error.

# Import of Python modules:
from Timba.TDL import *
from Timba.Meq import meq
Settings.forest_state.cache_policy = 100;
Settings.orphans_are_roots = True;

# for bookmarks
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Contrib.JEN import MG_JEN_exec

##########################################################################
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init(script_name,
                         last_changed='$Date$',
                         trace=False) # If True, produce progress messages  
MG.parm = record(my_resample_shape=[10,10],
               # this is the final shape of the cells we want
               # try giving it weird values like [1,10] or [10,1] or [1,1] etc...
                my_request_shape=[50,50],
               # this is the shape of the request sent to the server
                my_downsample_shape=[5,5], # shape of downsampling
)   

#=====================================================================
#=====================================================================
def _define_forest (ns):
  # this is the final shape of the cells we want
  # try giving it weird values like [1,10] or [10,1] or [1,1] etc...
  my_num_cells=MG.parm['my_resample_shape']
  # 2D resampling
  ns.x<<Meq.Parm(meq.array([[1,0.2,0.01],[-0.3,0.1,0.21]]))
  ns.y<<Meq.Parm(meq.array([[1,0.2,0.01],[-0.3,0.1,0.21]]))
  nxr=ns['nodex']<<0.01*ns.x
  nxi=ns['nodexi']<<-0.01*ns.x

  nyr=ns['nodey']<<0.01*ns.y
  nyi=ns['nodeyi']<<-0.01*ns.y

  n1=ns['n1']<<Meq.ToComplex(nxr,nxi)
  n2=ns['n2']<<Meq.ToComplex(nyr,nyi)

  # if flag_bit ==0, resample the request
  # if flag_bit !=0, resample the result
  rootxc=ns.rootxc<<Meq.Resampler(n1,flag_bit=1,num_cells=my_num_cells)
  rootxd=ns.rootxd<<Meq.Resampler(n2,flag_bit=0,num_cells=my_num_cells)
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
  rootac=ns.rootac<<Meq.Resampler(n3,flag_bit=1,num_cells=my_num_cells)
  rootbd=ns.rootbd<<Meq.Resampler(n4,flag_bit=0,num_cells=my_num_cells)
  root2=ns['1D_Error']<<(rootac-rootbd)


  MG_JEN_forest_state.bookmark(root1,page="DownSampling Error",viewer="Result Plotter");
  MG_JEN_forest_state.bookmark(root2,page="DownSampling Error",viewer="Result Plotter");

  # Downsample/Upsample error ###############################
  ns.ddx<<Meq.Parm(meq.array([[1,0.2,0.01],[-0.3,0.1,0.21]])) #2D
  ns.ddy<<Meq.Parm(meq.array([1,20,-0.01])) # 1D
  ns.ddz<<Meq.Parm(0) # constant
  nxr=ns['ddnodex']<<0.01*ns.ddx
  nyr=ns['ddnodey']<<0.1*ns.ddy
  nzr=ns['ddnodez']<<0.01*ns.ddz
  nxi=ns['ddnodexi']<<-0.01*ns.ddx
  nyi=ns['ddnodeyi']<<-0.01*ns.ddy*ns.ddy
  nzi=ns['ddnodezi']<<-0.01*ns.ddz

  n1=ns['ddcom1']<<Meq.ToComplex(nxr,nxi)
  n2=ns['ddcom2']<<Meq.ToComplex(nyr,nyi)
  n3=ns['ddcom3']<<Meq.ToComplex(nzr,nzi)
  # First downsample to [5,5]
  # and then upsample again to [50,50] which will
  # be the resolution used in the request.
  my_shape_down=MG.parm['my_downsample_shape']
  rootx=ns.ddrootx<<Meq.Resampler(nxr,num_cells=my_shape_down)
  rooty=ns.ddrooty<<Meq.Resampler(nyr,num_cells=my_shape_down)
  rootz=ns.ddrootz<<Meq.Resampler(nzr,num_cells=my_shape_down)
  root_real=ns.ddrootr<<Meq.Composer(rootx,rooty,rootz)

  rootxc=ns.ddrootxc<<Meq.Resampler(n1,num_cells=my_shape_down)
  rootyc=ns.ddrootyc<<Meq.Resampler(n2,num_cells=my_shape_down)
  rootzc=ns.ddrootzc<<Meq.Resampler(n3,num_cells=my_shape_down)
  root_complex=ns.ddrooti<<Meq.Composer(rootxc,rootyc,rootzc)

  # in order to calculate error, upsample and substract
  # from original result 
  my_shape_up=MG.parm['my_request_shape']
  rootxe=ns.xe<<(Meq.Resampler(rootxc,num_cells=my_shape_up)-n1)
  rootye=ns.ye<<(Meq.Resampler(rootyc,num_cells=my_shape_up)-n2)
  rootze=ns.ze<<(Meq.Resampler(rootzc,num_cells=my_shape_up)-n3)
  root_error=ns.ddroote<<Meq.Composer(rootxe,rootye,rootze)
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
 
  MG_JEN_forest_state.bookmark(root_error,page="DownSample/UpSample Errors",viewer="Result Plotter");

#=====================================================================
#=====================================================================
def _test_forest (mqs, parent):
 f0 = 1200
 f1 = 1600
 t0 = 0.0
 t1 = 1.0
 
 my_shape_request=MG.parm['my_request_shape']
 nfreq =my_shape_request[0] 
 ntime =my_shape_request[1]
 # create cells
 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 request = meq.request(cells,eval_mode=1);
 b = mqs.meq('Node.Execute',record(name='1D_Error',request=request),wait=True);
 b = mqs.meq('Node.Execute',record(name='2D_Error',request=request),wait=True);
 b = mqs.meq('Node.Execute',record(name='ddrootr',request=request),wait=True);
 b = mqs.meq('Node.Execute',record(name='ddrooti',request=request),wait=True);
 b = mqs.meq('Node.Execute',record(name='ddroote',request=request),wait=True);
 #print "Complex result=",b;
 

#=====================================================================
#=====================================================================
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns);
  ns.Resolve()
