from Timba.TDL import *
import math
from Meow import Context
from Meow import StdTrees

from Calico import wsrt_beams
TDLCompileMenu("Beam model options",wsrt_beams);

def compute_jones (Jones,sources,stations=None,inspectors=[],label="R",**kw):
  """Creates the Z Jones for ionospheric phase, given TECs (per source, 
  per station).""";
  stations = stations or Context.array.stations;
  ns = Jones.Subscope();
  
  bf = ns.beamscale << wsrt_beams.wsrt_beam_size_factor*1e-9;
  # assume same PA over field
  pa = ns.pa(0) << Meq.ParAngle(sources[0].direction.radec(),Context.array.xyz0());
  # now loop over sources
  for isrc,src in enumerate(sources):
    # az-el of source
    azel = ns.azel(src) << Meq.AzEl(src.direction.radec(),Context.array.xyz0());
    el = ns.el(src) << Meq.Selector(azel,index=1);
    # the refraction offset is DF*tg(ZA) = DF/tg(el), since ZA=90-el
    # immediately take the sine of it, since we work with sine angles (l,m)
    dEl = ns.dEl(src) << Meq.Sin((refraction_arcsec*math.pi/(180*3600))/Meq.Tan(el));
    # in diff-mode, convert to d(d(el)) relative to source 0
    if diff_mode:
      if isrc:
        dEl = ns.ddEl(src) << ns.dEl(src) - ns.dEl(sources[0]);
      # else source 0: d(d(el))=0
      else: 
        dEl = 0;
    # dl is then sin(offset)*sin(PA), and dm is sin(offset)*cos(PA)
    dl = ns.dl(src) << -dEl*Meq.Sin(pa);
    dm = ns.dm(src) << dEl*Meq.Cos(pa);
    dlm = ns.dlm(src) << Meq.Composer(dl,dm);
    lm1 = ns.lm1(src) << src.direction.lm() + dlm;
    # compute beam
    if wsrt_beams.beam_model._not_per_station:
      if normalize:
        wsrt_beams.beam_model(Jones(0,src),src.direction.lm(),bf);
        wsrt_beams.beam_model(Jones(1,src),lm1,bf);
        Jones(src) << Jones(1,src)/Jones(0,src);
      else:
        wsrt_beams.beam_model(Jones(src),lm1,bf);
    else:
      for p in Context.array.stations():
        if normalize:
          wsrt_beams.beam_model(Jones(0,src),src.direction.lm(),bf,p);
          wsrt_beams.beam_model(Jones(1,src),lm1,bf,p);
          Jones(src) << Jones(1,src)/Jones(0,src);
        else:
          beam_model(Jones(name,p),lm1,bf,p);
      inspectors.append(ns.inspector(label) << \
          StdTrees.define_inspector(Jones,sources,stations,label=label));
  # make inspectors
  if wsrt_beams.beam_model._not_per_station:
    inspectors.append(ns.inspector(label) << \
        StdTrees.define_inspector(Jones,sources,label=label));
  else:
    inspectors.append(ns.inspector(label) << \
        StdTrees.define_inspector(Jones,sources,label=label));
  if diff_mode:
    inspectors.append(ns.inspector(label,'ddEl') << \
        StdTrees.define_inspector(ns.ddEl,sources,label='d(d(el))'));
  else:
    inspectors.append(ns.inspector(label,'dEl') << \
        StdTrees.define_inspector(ns.dEl,sources,label='d(el)'));
  inspectors += [
    ns.inspector(label,'dlm') << \
        StdTrees.define_inspector(ns.dlm,sources,label='d(lm)'),
  ];
  
  if wsrt_beams.beam_model._not_per_station:
    return wsrt_beams.SourceBeam(Jones,p0=Context.array.stations()[0]);
  else:
    return Jones;

TDLCompileOption('refraction_arcsec',"Refraction at ZA=45deg (arcsec)",[60],more=float);
TDLCompileOption('diff_mode',"Simulate differential refraction",False,
    doc="""Enable this option if you want to simulate an observation where the
    telescope pointings and phase reference has been corrected for refraction""");
TDLCompileOption('normalize',"Normalize beam gain to unity",False,
    doc=""" """);

