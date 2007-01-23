from Timba.TDL import *
from Timba.Meq import meq
import math
import cmath

TDLCompileOption('ser_order',"Max order of series",[3,5,10]);
TDLCompileOption('a_term',"'a' value",[0,5,10],more=float);
TDLCompileOption('b_term',"'b' value",[0,5,10],more=float);

def _define_forest (ns, **kwargs):
  x = ns.x << Meq.Time;
  y = ns.y << Meq.Freq;

  TERMS = range(-ser_order,ser_order+1);    # [-n,...,n]
  
  # ns.f(k,l) creates a node named "f:k:l", substituting the values of
  # k,l. This is useful if you need to create a series of trees
  # following some algorithm.
  for k in TERMS:
    for l in TERMS:
      a = cmath.exp(complex(0,1)*(a_term*k+b_term*l));
      ns.f(k,l) << a*Meq.Polar(1,-2*math.pi*(k*x+l*y));
      
  # and of course plain "f" is still available to be used for a node name.
  # Note how Python's '*' syntax and a list comprehension statement
  # can be used to create a list of children
  ns.f << Meq.Add(*[ns.f(k,l) for k in TERMS for l in TERMS]);
  

def _test_forest (mqs, parent):
  domain = meq.domain(-1,1,-1,1)                            
  cells = meq.cells(domain,num_freq=100, num_time=100)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);




Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f')
];
Settings.forest_state.cache_policy = 100;
