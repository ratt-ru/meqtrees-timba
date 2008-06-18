from Timba.TDL import *

Settings.forest_state.cache_policy = 1;

def _define_forest (ns,**kwargs):
  ns.x1 << Meq.Time;
  ns.y1 << Meq.Freq;
  ns.sum1 << Meq.Add(ns.x1,ns.y1);
  ns.x2 << Meq.Time(proc=0);
  ns.y2 << Meq.Freq(proc=0);
  ns.sum2 << Meq.Add(ns.x2,ns.y2);
  ns.s1 << Meq.Sin(ns.sum1);
  ns.c1 << Meq.Cos(ns.sum1);
  ns.s2 << Meq.Cos(ns.sum2);
  ns.c2 << Meq.Sin(ns.sum2);
  ns.add1 << Meq.Add(ns.s1,ns.c1,proc=0);
  ns.add2 << Meq.Add(ns.s2,ns.c2,proc=1);
  ns.root << Meq.Add(ns.add1,ns.add2,mt_polling=True);

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,10,0,10),
               num_freq=2000,num_time=2000);
  mqs.execute('root',meq.request(cells));

  