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
WSRT_cos3_beam._per_station = False;


def compute_E_jones(Ej,sources):
  """Computes E Jones (beam gain) for a list of sources.
  Ej is an output node, which will be qualified with either a source only,
  or a source/station pair.
  """;
  # are pointing errors configured?
  if _pe_errgen.has_errors():
    node_maker = _pe_errgen.node_maker();
    ns = Ej.Subscope("pe");
    # create nodes to compute pointing errors per antenna
    for p in Context.array.stations():
      node_maker(ns.dl(p),station=p);
      node_maker(ns.dm(p),station=p);
      ns.dlm(p) << Meq.Composer(ns.dl(p),ns.dm(p));
      # now work out "error" direction per source, 
      # and compute the beam gain in that direction
      for src in sources:
        lm = ns.lm(src.direction.name,p) << src.direction.lm() + ns.dlm(p);
        beam_model(Ej(src.direction.name,p),lm,p);
  # no pointing errors
  else:
    if beam_model._per_station:
      for src in sources:
        for p in Context.array.stations():
          beam_model(Ej(src.direction.name,p),src.direction.lm(),p);
    else:
      for src in sources:
        beam_model(Ej(src.direction.name),src.direction.lm());
  # all done
  pass;
  
_model_option = TDLCompileOption('beam_model',"Beam model",
  [WSRT_cos3_beam]
);

_wsrt_option_menu = TDLCompileMenu('WSRT beam model options',
  TDLOption('wsrt_beam_size_factor',"Beam size factor",[2e-6],more=float)
);

_pe_errgen = ErrorGens.Selector("pointing",0,10,label="pe",unit=("arcsec",ARCSEC));

TDLCompileOptions(*_pe_errgen.options());

# show/hide options based on selected model
def _show_option_menus (model):
  _wsrt_option_menu.show(model==WSRT_cos3_beam);

_model_option.when_changed(_show_option_menus);
