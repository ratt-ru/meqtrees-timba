from Timba.TDL import *
from Timba.Meq import meq
import math

TDLCompileOption('ser_order',"Max order of series",[3,5,10],more=int);

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
      
  # and of course plain "f" is still available to be used for a node name.
  # Note how Python's '*' syntax and a list comprehension statement
  # can be used to create a list of children
  ns['f'] << Meq.Add(*[ns.f(k,l) for k in TERMS for l in TERMS]);
  
  # Note also, ns['f'] does the same thing as ns.f. However, since the [] 
  # operator takes any expression, it allows things like:
  #   name = 'f'
  #   ns[name] << ...
  # i.e. "computing" a node name if necessary.
  

def _test_forest (mqs, parent):
  domain = meq.domain(-1,1,-1,1)                            
  cells = meq.cells(domain,num_freq=100, num_time=100)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);




Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f')
];
if ser_order <= 10:
  Settings.forest_state.cache_policy = 100;
else:
  Settings.forest_state.cache_policy = 1;
