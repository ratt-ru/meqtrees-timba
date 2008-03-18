from Timba.TDL import *
from Timba.Meq import meq
import math

# reuse previous function
from demo1_iono import make_sine_tid


positions = [ (0,0),(10000,10000) ];
tec_points = [ 0,1,'grid' ];

def _define_forest (ns,**kwargs):
  # make nodes for individual positions
  for p,(x,y) in enumerate(positions):
    ns.xy(p) << Meq.Composer(x,y);
  # make node for grid of positions
  lm = ns.lm << Meq.Composer(Meq.Grid(axis='l'),Meq.Grid(axis='m'));
  height = 300000;  # in meters
  # now derive xy using ionosphere height
  # x = h*tg(a), l=cos(a), so tg(a)=l/sqrt(1-l^2);
  ns.xy('grid') << height*lm/Meq.Sqrt(1-Meq.Sqr(lm));
  # now define tec trees 
  for p in tec_points:
    make_sine_tid(ns,ns.tec(p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10,angle=10);

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in tec_points:
  name = 'tec:'+str(p);
  Settings.forest_state.bookmarks.append(record(
      name=name,viewer='Result Plotter',udi='/node/'+name));


def _test_forest (mqs,parent):
  # make a domain in time,l,m
  domain = meq.gen_domain(time=[0,7200],l=[-.05,.05],m=[-.05,.05]);
  cells = meq.gen_cells(domain,num_time=100,num_l=100,num_m=100);

  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  for p in tec_points:
    result = mqs.execute('tec:'+str(p),request);
