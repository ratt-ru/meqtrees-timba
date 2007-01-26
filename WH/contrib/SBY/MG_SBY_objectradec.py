from Timba.TDL import *
from Timba.Meq import meq
Settings.forest_state.cache_policy = 100;

Settings.orphans_are_roots = True;

def _define_forest (ns):
   ns.cb<<Meq.ObjectRADec(obj_name="MOON")

def _test_forest (mqs, parent):

 f0 = 1200
 f1 = 1600
 t0 = 54126*3600*24 # UTC in days converted to seconds
 t1 = 55126*3600*24
 nfreq =20
 ntime =100

 freqtime_domain = meq.domain(startfreq=f0, endfreq=f1, starttime=t0, endtime=t1);
 cells =meq.cells(domain=freqtime_domain, num_freq=nfreq,  num_time=ntime);
 request = meq.request(cells,rqtype='e1');
 b = mqs.meq('Node.Execute',record(name='cb',request=request),wait=True);
 
if __name__ == '__main__':
  ns=NodeScope()
  _define_forest(ns)
  print ns.AllNodes()



