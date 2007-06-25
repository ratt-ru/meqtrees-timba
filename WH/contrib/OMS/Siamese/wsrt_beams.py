from Timba.TDL import *
from Meow import Context

import random
import math

import ErrorGens


DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = DEG/3600;

def WSRT_cos3_beam (E,lm,*dum):
  """computes a gaussian beam for the given direction
  'E' is output node
  'lm' is direction (2-vector node)
  """
  ns = E.Subscope();
  ns.lmsq << Meq.Sqr(lm);
  ns.lsq  << Meq.Selector(ns.lmsq,index=0);
  ns.msq  << Meq.Selector(ns.lmsq,index=1);
  E << Meq.Pow(Meq.Cos(Meq.Sqrt(ns.lsq+ns.msq)*wsrt_beam_size_factor*Meq.Freq()),3);
  return E;
# this beam model is not per-station
WSRT_cos3_beam._not_per_station = True;

def compute_jones (Jones,sources,stations=None,pointing_offsets=None,**kw):
  """Computes beam gain for a list of sources.
  The output node, will be qualified with either a source only, or a source/station pair
  """;
  stations = stations or Context.array.stations();
  ns = Jones.Subscope();
  # are pointing errors configured?
  if pointing_offsets:
    # create nodes to compute actual pointing per source, per antenna
    for p in Context.array.stations():
      for src in sources:
        lm = ns.lm(src.direction,p) << src.direction.lm() + pointing_offsets(p);
        beam_model(Jones(src,p),lm,p);
  # no pointing errors
  else:
    # if not per-station, use same beam for every source
    if beam_model._not_per_station:
      for src in sources:
        beam_model(Jones(src),src.direction.lm());
        for p in Context.array.stations():
          Jones(src,p) << Meq.Identity(Jones(src));
    else:
      for src in sources:
        for p in Context.array.stations():
          beam_model(Jones(src,p),src.direction.lm(),p);
  return Jones;

_model_option = TDLCompileOption('beam_model',"Beam model",
  [WSRT_cos3_beam]
);

_wsrt_option_menu = TDLCompileMenu('WSRT beam model options',
  TDLOption('wsrt_beam_size_factor',"Beam size factor",[2e-6],more=float)
);

def _show_option_menus (model):
  _wsrt_option_menu.show(model==WSRT_cos3_beam);

_model_option.when_changed(_show_option_menus);
