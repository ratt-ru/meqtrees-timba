from Timba.TDL import *
from Meow import Context

import math

import ErrorGens

DEG = math.pi/180.;
ARCMIN = DEG/60;
ARCSEC = DEG/3600;

def compute_pointings(nodes,stations=None,**kw):
  """Computes pointing errors for a list of stations.""";
  # if the error generator is set to "no error", return None
  if not _pe_errgen.has_errors():
    return None;
  node_maker = _pe_errgen.node_maker();
  ns = nodes.Subscope();
  # create nodes to compute pointing errors per antenna
  for p in stations or Context.array.stations():
    node_maker(ns.l(p),station=p);
    node_maker(ns.m(p),station=p);
    nodes(p) << Meq.Composer(ns.l(p),ns.m(p));
  return nodes

# make an error generator for pointings
_pe_errgen = ErrorGens.Selector("pointing",0,10,label="pe",unit=("arcsec",ARCSEC));

TDLCompileOptions(*_pe_errgen.options());

