from Timba.TDL import *
from Timba.Meq import meq
import math

TDLCompileOption('ser_order',"Max order of series",[3,5,10]);

TERMS = range(-ser_order,ser_order+1);    # [-n,...,n]

def sum_series (sumnode,fnodes):
  sumnode << Meq.Add(*[fnodes(k,l) for k in TERMS for l in TERMS]);
  
def sum_sq_series (sumnode,fnodes):
  sumnode << Meq.Add(*[Meq.Sqr(fnodes(k,l)) for k in TERMS for l in TERMS]);
  

def _define_forest (ns, **kwargs):
  x = ns.x << Meq.Time;
  y = ns.y << Meq.Freq;

  TERMS = range(-ser_order,ser_order+1);    # [-n,...,n]
  
  # ns.f(k,l) creates a node named "f:k:l", substituting the values of
  # k,l. This is useful if you need to create a series of trees
  # following some algorithm.
  for k in TERMS:
    for l in TERMS:
      ns.f(k,l) << Meq.Polar(1,-2*math.pi*(k*x+l*y));
      
  # make nodes for sum of series, and sum of series squared
  sum_series(ns.sum,ns.f);
  sum_sq_series(ns.sum_sq,ns.f);

def _test_forest (mqs, parent):
  domain = meq.domain(-1,1,-1,1)                            
  cells = meq.cells(domain,num_freq=100, num_time=100)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('sum',request);
  result = mqs.execute('sum_sq',request);


Settings.forest_state.bookmarks = [
  record(name="result of 'sum'",viewer='Result Plotter',udi='/node/sum'),
  record(name="result of 'sum_sq'",viewer='Result Plotter',udi='/node/sum_sq')
];
Settings.forest_state.cache_policy = 100;
