from Timba.TDL import *
from Timba.Meq import meq
import math

# reuse previous function
from example5_iono import make_sine_tid


positions = [ (0,0),(10000,10000),(None,None) ];

def _define_forest (ns,**kwargs):
  for p,(x,y) in enumerate(positions):
    if x is None:
      # for None,None make a special xy position
      # start with an l,m pair
      lm = ns.lm(p) << Meq.Composer(Meq.Grid(axis='l'),Meq.Grid(axis='m'));
      # now derive xy using ionosphere height
      # x = h*tg(a), l=cos(a), so tg(a)=l/sqrt(1-l^2);
      height = 300000;  # in meters
      ns.xy(p) << height*lm/Meq.Sqrt(1-Meq.Sqr(lm));
    else:
      ns.xy(p) << Meq.Composer(x,y);
    # define tec trees 
    make_sine_tid(ns,ns.tec(p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10,angle=0);

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in range(len(positions)):
  name = 'tec:'+str(p);
  Settings.forest_state.bookmarks.append(record(
      name=name,viewer='Result Plotter',udi='/node/'+name));


def _test_forest (mqs,parent):
  # make a domain in time,l,m
  domain = meq.gen_domain(time=[0,7200],l=[-.05,.05],m=[-.05,.05]);
  cells = meq.gen_cells(domain,num_time=100,num_l=100,num_m=100);

  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  for p in range(len(positions)):
    result = mqs.execute('tec:'+str(p),request);
