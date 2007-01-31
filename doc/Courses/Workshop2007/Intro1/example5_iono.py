from Timba.TDL import *
from Timba.Meq import meq
import math

def make_sine_tid (ns,tecnode,xy,ampl,size_km,speed_kmh,angle=0,tec0=0):
  """This implements a 1D sine wave moving over the array.
  'tecnode' is a node to which the TEC will be assigned.
  'xy' is an input node that supplies coordinates, as a 2-vector.
  Other inputs may be nodes or constants:
    'ampl' is amplitude of TID
    'size_km' is size, in km (half-period)
    'speed_kmh' is speed, in km/h
    'angle' is direction of movement, relative to X axis, in radians
    'tec0' is base TEC
  """;
  ns.time ** Meq.Time;  # '**' means define or redefine
  # rate of change of TID (in periods per second)
  rate = tecnode('rate') << (speed_kmh/(2.*size_km))/3600.; 
  # now rotate the xy coordinates over the given angle
  # first create a rotation matrix
  cos = tecnode('cosa') << Meq.Cos(angle);
  sin = tecnode('sina') << Meq.Sin(angle);
  rm = tecnode('RM') << Meq.Matrix22(cos,-sin,sin,cos);
  # rotate xy using the matrix
  rxy = tecnode('xy') << Meq.MatrixMultiply(rm,xy);
  # extract the X coordinate
  x = tecnode('x') << Meq.Selector(rxy,index=0);
  # build tree for TEC as a function of x and time
  tecnode << ampl*Meq.Sin(2*math.pi*(x/(2*1000*size_km) + ns.time*rate)) + tec0; 

  return tecnode;  

  # define positions for which we want TECs (in meters)
positions = [ (0,0),(10000,10000) ];

def _define_forest (ns,**kwargs):
  # loop over positions
  for p,(x,y) in enumerate(positions):
    ns.xy(p) << Meq.Composer(x,y);
    # define tec trees 
    print ns.tec(p).initialized();
    make_sine_tid(ns,ns.tec(p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10);
    print ns.tec(p).initialized();
    ns1 = ns.Subscope('foo',p);
    ns1.xcoord(p) << ns.tec(p,'x') + 1;
    ns1.xcoord1(p,12,2,3,'xxx')('yyy')('zzz') << ns.tec(p)('x')+1;   

Settings.forest_state.cache_policy = 100; # cache everything
Settings.forest_state.bookmarks = [];
# make some bookmarks on the fly
for p in range(len(positions)):
  name = 'tec:'+str(p);
  Settings.forest_state.bookmarks.append(record(
      name=name,viewer='Result Plotter',udi='/node/'+name));


def _test_forest (mqs,parent):
  domain  = meq.domain(0,1,0,7200);  # two hours
  cells   = meq.gen_cells(domain,num_freq=1,num_time=100);
  request = meq.request(cells, rqtype='ev')
  # execute for every subtree
  for p in range(len(positions)):
    result = mqs.execute('tec:'+str(p),request);


