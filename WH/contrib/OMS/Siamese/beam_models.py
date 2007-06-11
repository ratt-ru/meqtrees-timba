from Timba.TDL import *
from Meow import Context

import random
import math

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
  if include_pointing_errors:
    # work out pointing error (dlm per station)
    ampl = max_pe_error*ARCSEC; 
    ns = Ej.Subscope("pe");
    dlm = ns.dlm;
    # create nodes to compute pointing errors per antenna
    for p in Context.array.stations():
      # pick random periods of dl/dm variation, in seconds
      dlp = random.uniform(min_pe_period*3600,max_pe_period*3600);
      dmp = random.uniform(min_pe_period*3600,max_pe_period*3600);
      # pick a random starting phase for the variations
      dlp_0 = random.uniform(0,2*math.pi); 
      dmp_0 = random.uniform(0,2*math.pi);
      dlm(p) << Meq.Composer( 
        ns.dl(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/dlp)+dlp_0),
        ns.dm(p) << ampl*Meq.Sin(Meq.Time()*(2*math.pi/dmp)+dmp_0)
      );
    # now work out "error" direction per source, 
    # and compute the beam gain in that direction
      for src in sources:
        lm = ns.lm(src.direction.name,p) << src.direction.lm() + dlm(p);
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

TDLCompileMenu('Include pointing errors',
  TDLOption("max_pe_error","Max pointing error, arcsec",[1,2,5],more=float),
  TDLOption("min_pe_period","Min time scale for pointing variation, hours",
            [0,1],more=float),
  TDLOption("max_pe_period","Max time scale for pointing variation, hours",
            [2,4],more=float),
  toggle='include_pointing_errors'
);

# show/hide options based on selected model
def _show_option_menus (model):
  _wsrt_option_menu.show(model==WSRT_cos3_beam);

_model_option.when_changed(_show_option_menus);


