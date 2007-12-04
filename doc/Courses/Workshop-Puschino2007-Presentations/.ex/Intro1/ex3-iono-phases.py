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
      # x = h*sin(a), l=cos(a), so sin(a)=l/sqrt(1-l^2);
      height = 300000;  # in meters
      ns.xy(p) << height*lm/Meq.Sqrt(1-Meq.Sqr(lm));
    else:
      ns.xy(p) << Meq.Composer(x,y);
    # define tec trees 
    make_sine_tid(ns,ns.tec(1,p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10);
    make_sine_tid(ns,ns.tec(2,p),ns.xy(p),ampl=.05,size_km=10,speed_kmh=200,angle=math.pi/6);
    ns.tec(p) << ns.tec(1,p) + ns.tec(2,p);
    
    # define zeta
    ns.zeta(p) << 2*math.pi*50*3e+8/Meq.Freq()*ns.tec(p);

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in range(len(positions)):
  name = 'tec:'+str(p);
  name2 = 'zeta:'+str(p);
  Settings.forest_state.bookmarks += [ 
    record(name=name,viewer='Result Plotter',udi='/node/'+name),
    record(name=name2,viewer='Result Plotter',udi='/node/'+name2)
  ];


def _test_forest (mqs,parent):
  # make a domain in time,l,m
  domain = meq.gen_domain(freq=[30*1e+6,200*1e+6],time=[0,7200],l=[-.05,.05],m=[-.05,.05]);
  cells = meq.gen_cells(domain,num_freq=30,num_time=30,num_l=30,num_m=30);

  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  for p in range(len(positions)):
    result = mqs.execute('zeta:'+str(p),request);
