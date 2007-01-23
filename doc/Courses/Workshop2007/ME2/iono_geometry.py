from Timba.TDL import *
import math
from Meow import Jones
from Meow import Context

H = 300000;           # height of ionospheric layer, in meters
Lightspeed = 3e+8;

TDLCompileOption("iono_rotate","Rotatate ionosphere with sky",True);

def compute_piercings (ns,source_list):
  """Creates nodes to compute the "piercing points" of each
  source in source_list, for each antenna in array.""";
  stations = Context.array.stations();
  xyz = Context.array.xyz();
  xyz0 = Context.array.xyz0();
  radec0 = Context.observation.phase_centre.radec();
  # if ionosphere is "stuck" to the sky, we need to rotate the antenna
  # coordinates. Otherwise we need to rotate the piercing coordinates.
  # pa0 refers to the P.A. at the start of the observation (time0) 
  ns.pa_time0 = Meq.Compounder(
      Meq.Composer(ns.time0<<0,0),
      ns.pa_time00 << Meq.ParAngle(xyz=xyz0,radec=radec0),
      common_axes=[hiid("time"),hiid("freq")]);
  if iono_rotate:
    ns.pa1 << ns.pa_time0 - (ns.pa << Meq.ParAngle(xyz=xyz0,radec=radec0));
    ns.P0 << Jones.define_rotation_matrix(ns.pa1);
    
  for p in stations:
    xy = ns.xy(p) << Meq.Selector(xyz(p) - xyz(stations[0]),index=[0,1],multi=True);
    # if ionosphere is stuck to the sky, create P (p/a rotation matrix)
    if iono_rotate:
      ns.xy_r(p) << Meq.MatrixMultiply(ns.P0,xy);
    else:
      ns.pa1(p) << ns.pa_time0-(ns.pa(p)<<Meq.ParAngle(xyz=xyz(p),radec=radec0));
      ns.P(p) << Jones.define_rotation_matrix(ns.pa1(p));

  for src in source_list:
    lm = src.direction.lm();
    lm_sq = ns.lm_sq(src.name) << Meq.Sqr(lm);
    # dxy is the relative X,Y coordinate of the piercing point for this source,
    # relative to centre. In each direction it's to H*tg(alpha), where
    # alpha is the direction of the source w.r.t. center (i.e., arccos l).
    ns.dxy(src.name) << H*lm/Meq.Sqrt(1-lm_sq);
    # now compute absolute piercings per source, per antenna
    for p in Context.array.stations():
      if iono_rotate:
        ns.pxy(src.name,p) << ns.xy_r(p) + ns.dxy(src.name);
      else:
        ns.pxy(src.name,p) << ns.xy(p) + Meq.MatrixMultiply(ns.P(p),ns.dxy(src.name));
  return ns.pxy;
  
def compute_za_cosines (ns,source_list):
  """Creates nodes to compute the zenith angle cosine of each
  source in source_list, for each antenna in array.""";
  za_cos = ns.za_cos;
  for src in source_list:
    for p in Context.array.stations():
      za_cos(src.name,p) << Meq.Identity(src.direction.n(Context.observation.phase_centre));
      
  return za_cos;

def compute_zeta_jones_from_tecs (ns,tecs,source_list):
  """Creates the Z Jones for ionospheric phase, given TECs (per source, 
  per station).""";
  zeta = ns.Z;
  for src in source_list:
    for p in Context.array.stations():
      zeta(src.name,p) << Meq.Polar(1,-25*2*math.pi*Lightspeed*tecs(src.name,p)/Meq.Freq());
  return zeta;

