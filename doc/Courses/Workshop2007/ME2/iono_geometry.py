from Timba.TDL import *
import math
from Meow import Jones
from Meow import Context

H = 300000;           # height of ionospheric layer, in meters
Lightspeed = 3e+8;

TDLCompileOption("iono_rotate","Rotate ionosphere with sky",True);

def compute_piercings (ns,source_list):
  """Creates nodes to compute the "piercing points" of each
  source in source_list, for each antenna in array.""";
  stations = Context.array.stations();
  xyz = Context.array.xyz();
  radec0 = Context.observation.phase_centre.radec();
  
  # project our stations into an ionospheric coordinate system xyz1
  # for now, we just project everything to z=0, and take station 1 as origin
  for p in stations:
    # xyz_proj gives positions projected to equatorial plane (z=0)
    xyzp = ns.xyz_proj(p) << Meq.Paster(xyz(p),0,index=2);
    # xyz1 gives positions relative to station1
    xyz1 = ns.xyz1(p) << xyzp - ns.xyz_proj(stations[0]);
    # and extract the xy1 component
    ns.xy1(p) << Meq.Selector(xyz1,index=[0,1],multi=True);
    
  # if ionosphere is "stuck" to the sky, we need to rotate the antenna
  # coordinates as we go along. Otherwise we need to rotate the piercing 
  # coordinates. The angle of rotation is given by the P.A. _at the
  # projected antenna positions_.
  if iono_rotate:
    ns.pa0 << - Meq.ParAngle(xyz=ns.xyz_proj(stations[0]),radec=radec0);
    ns.P0 << Jones.define_rotation_matrix(ns.pa0);

    
  for p in stations:
    # if ionosphere is stuck to the sky, rotate antenna coordinates by P0
    if iono_rotate:
      ns.xy_r(p) << Meq.MatrixMultiply(ns.P0,ns.xy1(p));
    else:
    # else create P (p/a rotation matrix)
      ns.pa(p) << - Meq.ParAngle(xyz=ns.xyz_proj(p),radec=radec0);
      ns.P(p) << Jones.define_rotation_matrix(ns.pa(p));

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
        ns.pxy(src.name,p) << ns.xy1(p) + Meq.MatrixMultiply(ns.P(p),ns.dxy(src.name));
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
      zeta(src.name,p) << Meq.Polar(1,-25*Lightspeed*tecs(src.name,p)/Meq.Freq());
  return zeta;

