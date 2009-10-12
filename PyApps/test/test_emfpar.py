# -*- coding: utf-8 -*-
# standard preamble
from Timba.TDL import *
from Timba.array import array
 
# Timba.TDL.Settings.forest_state is a standard TDL name. 
# This is a record passed to Set.Forest.State. 
Settings.forest_state.cache_policy = 100;

# Make sure our solver root node is not cleaned up
Settings.orphans_are_roots = True;

def _define_forest (ns):
  ns.xyz << Meq.Composer(6300000.,0,0);
  ns.azel << Meq.Composer(Meq.Grid(axis='m'),Meq.Grid(axis='l'));
  ns.emf1  << Meq.EMFPar(azel=ns.azel,xyz=ns.xyz,h=array([100000.,200000.,300000.]));
  ns.emf2  << Meq.EMFPar(azel=ns.azel,observatory='wsrt',h=array([100000.,200000.,300000.]));
  ns.cube << Meq.Time()*ns.emf2*Meq.Freq();

import math

def _test_forest (mqs,parent):
  from Timba.Meq import meq
  # run tests on the forest
  domain = meq.gen_domain(time=[0,7200],l=[0,math.pi/2],m=[0,2*math.pi],freq=[100,200]);
  cells = meq.gen_cells(domain,num_time=10,num_l=100,num_m=100,num_freq=10);
  request = meq.request(cells, rqtype='ev')
  mqs.execute('emf1',request);  
  mqs.execute('emf2',request);  
  mqs.execute('cube',request);  

