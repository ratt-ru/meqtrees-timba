from Timba.TDL import *
from Meow import Context

import random
import math
import ErrorGens

DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = DEG/3600;

def compute_G_jones(Gjones):
  """Computes G Jones (antenna gain/phase).
  """;
  # get error generator function for gain and phase
  gaingen = _gain_errgen.node_maker();
  phasegen = _phase_errgen.node_maker();
  for p in Context.array.stations():
    Gj = Gjones(p);
    ns = Gj.Subscope();
    # generate nodes
    gaingen(ns.xa,station=p);
    gaingen(ns.ya,station=p);
    phasegen(ns.xp,station=p);
    phasegen(ns.yp,station=p);
    # put them together into matrix
    Gj << Meq.Matrix22(
      ns.x << Meq.Polar(ns.xa,ns.xp),0,0,ns.y << Meq.Polar(ns.ya,ns.yp)
    );
  return Gjones;

_gain_errgen = ErrorGens.Selector("gain",1,[.5,1.5]);
_phase_errgen = ErrorGens.Selector("phase",0,60,unit=("deg",DEG));

TDLCompileOptions(*_gain_errgen.options());
TDLCompileOptions(*_phase_errgen.options());
