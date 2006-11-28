# History:
# - 2006.11.27: creation.


# standard preamble
from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow
import random
import pxk_tools






def ZJones (ns, slist, array, observation):
  """ create ZJones (Ionospheric phase) for each station.  (image-plane
  effect).
  slist : source list to apply ZJones to
  """
  print "___ Applying Z Jones"  # Ionospheric phase

  H        = 300000;    # height of ionospheric layer, in meters
  TEC0     = 10;        # base TEC, in TECU
  TIDAmpl  = 0.05;      # TID amplitude, relative to base TEC
  TIDSize  = 200000;    # TID extent, in meters (one half of a sine wave)
  TIDSpeed = 600.0;     # TID time scale, in seconds


  def compute_piercings (ns,slist,array,observation):
    """Creates nodes to compute the 'piercing points' of each
    source in slist, for each antenna in array.
    """
  
    xyz    = array.xyz();
    xyz_p0 = xyz(array.stations()[0])
    for p in array.stations():
      ns.xy(p) << Meq.Selector(xyz(p) - xyz_p0,index=[0,1],multi=True);
      pass
    
    for src in slist:
      lm    = src.direction.lm(); # (l,m)
      lm_sq = ns.lm_sq(src.name) << Meq.Sqr(lm);
      # dxy is the relative X,Y coord of the piercing point for this
      # source, relative to centre. Its equals H*tan(z), where z is
      # the zenith angle
      ns.dxy(src.name) << H*lm/Meq.Sqrt(1-lm_sq);
      
      # now compute absolute piercings per source, per antenna
      for p in array.stations():
        ns.pxy(src.name,p) << ns.xy(p) + ns.dxy(src.name);
        pass
      pass
    return ns.pxy;
  

  def compute_za_cosines (ns,slist,array,observation):
    """Creates nodes to compute the zenith angle cosine of each
    source in slist, for each antenna in array.
    """
    za_cos = ns.za_cos;
    for src in slist:
      for p in array.stations():
        za_cos(src.name,p) <<  Meq.Identity(
          src.direction.n(observation.phase_centre))
        pass
      pass
    return za_cos


  def compute_tecs (ns,piercings,za_cos,slist,array,observation):
    """Creates nodes to compute the TEC for each piercing (per
    source, per station).
    """
    tecs = ns.tec;
    for src in slist:
      for p in array.stations():
        px  = ns.px(src.name,p) << \
              Meq.Selector(piercings(src.name,p),index=0)
        amp = (TIDAmpl*TEC0)
        sin = Meq.Sin(2*math.pi*(px/(2*TIDSize) + Meq.Time()/TIDSpeed))
        tecs(src.name,p) << (TEC0 + amp*sin) / za_cos(src.name,p);
        pass
      pass
    return tecs;
  


  """Creates the Z Jones for ionospheric phase, given TECs (per source, 
  per station).
  """
  piercings = compute_piercings(ns,slist.sources,array,observation);
  za_cos    = compute_za_cosines(ns,slist.sources,array,observation);
  tecs      = compute_tecs(
    ns,piercings,za_cos,slist.sources,array,observation);

  labda     = pxk_tools.C / Meq.Freq()  
  for isrc in range(len(slist.sources)):
    src     = slist.sources[isrc]
    
    # get Ionospheric phase per station, per source position
    for p in array.stations():
      ns.Z(src.direction.name,p) << Meq.Polar(
        1, 2*math.pi * -25 * tecs(src.direction.name,p) * labda)
      pass

    # and corrupt *source* by Z term
    slist.sources[isrc] = Meow.CorruptComponent(
      ns,src,'Z', station_jones=ns.Z(src.direction.name))
    pass
  
  # some bookmarks  (source S0, station i)
  for i in range(4): pxk_tools.Book_Mark(ns.Z('S0',i+1), 'Z Jones')
  return slist


