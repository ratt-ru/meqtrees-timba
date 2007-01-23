from Timba.TDL import *
from Timba.Meq import meq

def _define_forest (ns, **kwargs):
  ## This defines a tree for
  ##    f = alpha*sin(b*x+c*y+d)

  # this defines a leaf node named "alpha" of class Meq.Constant, 
  # initialized with the given value
  # (i.e. the Fine Structure Constant, in appropriate units)
  ns.alpha << Meq.Constant(value=297.61903062068177);
  
  # it's easier to just do <<(numeric value), this implicitly defines 
  # Constant nodes
  ns.b << 1;
  ns.c << 1;
  ns.x << 1;
  ns.y << 1;
  
  # bx = b*x, the hard way:
  # This defines a node named "bx" of class Meq.Multiply, with two children
  ns.bx << Meq.Multiply(ns.b,ns.x);
  
  # cy = c*y, the easy way: 
  # arithmetic on nodes implicitly defines the "right" things
  ns.cy << ns.c * ns.y;
  
  # sum = b*x+c*y+1, the easy way -- this will implictly create a 
  # Meq.Constant node for the "1", etc.
  ns.sum << ns.bx + ns.cy + 1;
  
  # The result. Note that an intermediate node of class Meq.Sin is
  # created for us automatically
  ns.f << ns.alpha*Meq.Sin(ns.sum);
  
  
  ### ...so in fact we could have accomplished the same thing with:
  # ns.f1 << ns.alpha*Meq.Sin(ns.b*ns.x + ns.c*ns.y + 1)
  
  

def _test_forest (mqs, parent):
  domain = meq.domain(1,10,1,10)                            
  cells = meq.cells(domain,num_freq=10, num_time=11)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);





Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f') 
];
Settings.forest_state.cache_policy = 100;
