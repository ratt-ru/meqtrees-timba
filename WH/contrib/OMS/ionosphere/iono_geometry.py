from Timba.TDL import *
import math

H = 300000;           # height of ionospheric layer, in meters
Lightspeed = 3e+8;

def compute_piercings (ns,source_list,array,observation):
  """Creates nodes to compute the "piercing points" of each
  source in source_list, for each antenna in array.""";
  
  xyz = array.xyz();
  for p in array.stations():
    ns.xy(p) << Meq.Selector(xyz(p) - xyz(array.stations()[0]),index=[0,1],multi=True);

  for src in source_list:
    lm = src.direction.lm();
    lm_sq = ns.lm_sq(src.name) << Meq.Sqr(lm);
    # dxy is the relative X,Y coordinate of the piercing point for this source,
    # relative to centre. In each direction it's to H*tg(alpha), where
    # alpha is the direction of the source w.r.t. center (i.e., arccos l).
    ns.dxy(src.name) << H*lm/Meq.Sqrt(1-lm_sq);
    
    # now compute absolute piercings per source, per antenna
    for p in array.stations():
      ns.pxy(src.name,p) << ns.xy(p) + ns.dxy(src.name);
      
  return ns.pxy;
  
def compute_za_cosines (ns,source_list,array,observation):
  """Creates nodes to compute the zenith angle cosine of each
  source in source_list, for each antenna in array.""";
  
  za_cos = ns.za_cos;
  for src in source_list:
    for p in array.stations():
      za_cos(src.name,p) << Meq.Identity(src.direction.n(observation.phase_centre));
      
  return za_cos;

def compute_zeta_jones_from_tecs (ns,tecs,source_list,array,observation):
  """Creates the Z Jones for ionospheric phase, given TECs (per source, 
  per station).""";
  zeta = ns.Z;
  for src in source_list:
    for p in array.stations():
      zeta(src.name,p) << Meq.Polar(1,-25*2*math.pi*Lightspeed*tecs(src.name,p)/Meq.Freq());
  return zeta;

