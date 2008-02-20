from Timba.TDL import *
from Timba.Meq import meq

def _define_forest (ns, **kwargs):
  ## This defines a tree for
  ##    f = a*sin(t*cos(2*f))
  
  ns.x << Meq.Time;
  ns.y << Meq.Freq;
  
  r = ns.r << Meq.Sqrt(Meq.Sqr(ns.x)+Meq.Sqr(ns.y));
  cosrr = ns.cosrr << Meq.Cos(r)*Meq.Exp(-Meq.Abs(r/30)); 
  
  ns.f << cosrr + Meq.Abs(cosrr);



  

def _test_forest (mqs, parent):
  domain = meq.domain(-30,30,-30,30)                            
  cells = meq.cells(domain,num_freq=100, num_time=100)
  request = meq.request(cells, rqtype='ev')
  result = mqs.execute('f',request);




Settings.forest_state.bookmarks = [
  record(name="result of 'f'",viewer='Result Plotter',udi='/node/f')
];
Settings.forest_state.cache_policy = 100;
