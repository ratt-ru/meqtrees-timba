from Timba.TDL import *
from Meow import Context

import math

DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = DEG/3600;
C = 299792458;  # speed of light

def compute_jones (Jones,sources,stations=None,**kw):
  """Computes conjugate N for a list of sources.
  """;
  stations = stations or Context.array.stations();
  ns = Jones.Subscope();
  for p in stations:
    ns.w(p) << Meq.Selector(Context.array.uvw(Context.observation.phase_centre)(p),index=2);
  
  ns.wl << (2*math.pi*Meq.Freq())/C;
  
  for src in sources:
    n1 = ns.n1(src) << ns.wl*(src.direction.n()-1);
    for p in stations:
      Jones(src,p) << Meq.Polar(1.,n1*ns.w(p));
  
  return Jones;

