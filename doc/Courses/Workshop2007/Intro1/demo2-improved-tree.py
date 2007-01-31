from Timba.TDL import *
from Timba.Meq import meq

def _define_forest (ns, **kwargs):
  ## This defines a tree for
  ##    f = a*sin(t*cos(2*f))
  
  ns.x << Meq.Time;
  ns.y << Meq.Freq;
  
  a = ns.alpha << 297.61903062068177;
  # note that here we've declared a Constant node named "alpha", and that
  # the Python variable 'a' now refers _TO THAT NODE_...

  # ...so the variable can subsequently be used elsewhere:
  ns.f << a*Meq.Sin(ns.x*Meq.Cos(2*ns.y));

  # and for comparison, a tree without Time/Freq:
  # note how node definitions are nested
  ns.f1 << a*Meq.Sin((ns.x1<<1)*Meq.Cos(2*(ns.y1<<1)))
  


  

def _test_forest (mqs, parent):
  domain = meq.domain(10,20,0,10)                            
  cells = meq.cells(domain,num_freq=200, num_time=100)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);
  result = mqs.execute('f1',request);




Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f'),
  record(name="result of 'f1'",viewer='Result Plotter',udi='/node/f1') 
];
Settings.forest_state.cache_policy = 100;
