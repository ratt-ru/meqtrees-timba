from Timba.TDL import *
from Meow import Context

import random
import math
import ErrorGens

DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = DEG/3600;

def compute_jones (Jones,stations=None,**kw):
  stations = stations or Context.array.stations();
  freq0 = Context.observation.freq0();
  
  for p in stations:
    Jj = Jones(p);
    ns = Jj.Subscope();
    
    a = random.uniform(1e-10,1e-9);

    Jj << Meq.Matrix22(1+a*(Meq.Freq()-freq0),0,0,1-a*(Meq.Freq()-freq0));
    
  return Jones;

