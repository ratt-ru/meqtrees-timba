from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.OMS.SkyComponent import *
import Timba.Contrib.OMS.Jones
  
STOKES = ("I","Q","U","V");

class PointSource(SkyComponent):
  def __init__(self,ns,name,direction,
               I=0.0,Q=0.0,U=0.0,V=0.0,
               Iorder=0,Qorder=0,Uorder=0,Vorder=0,
               spi=0.0,freq0=None,   
               parm_options=record(node_groups='Parm')):
    SkyComponent.__init__(self,ns,name,direction,parm_options=parm_options);
    # create flux polcs
    for stokes in STOKES:
      self._create_polc(stokes,locals()[stokes],locals()[stokes+"order"]);
    # see if a spectral index is present (freq0!=0 then), create polc
    self._freq0 = freq0;
    if freq0 is not None:
      # rename I polc to I0 
      self._rename_polc("I","I0");
      self._create_polc("spi",create_polc(spi));

  def iquv (self):
    """Returns an IQUV four-pack for this source""";
    iquv = self.ns.iquv;
    if not iquv.initialized():
      stokes = self.stokes();
      iquv << Meq.Composer(*[stokes(st) for st in STOKES]);
    return iquv;
    
  def has_spectral_index (self):
    return bool(self._freq0);
    
  def spectral_index (self):
    if not self.has_spectral_index():
      return None;
    return self._parm("spi");
    
  def stokes (self,st):
    """Returns flux node for this source. 'st' must be one of 'I','Q','U','V'.""";
    if st not in STOKES:
      raise ValueError,"st: must be one of 'I','Q','U','V'";
    stokes = self.ns[st];
    if not stokes.initialized():
      # if a ref frequency is given, use spectral index for I flux,
      # else just use a plain parm
      if st == "I" and self._freq0:
        i0 = self._parm("I0");
        spi = self._parm("spi");
        stokes << i0 * Meq.Pow((self.ns0.freq ** Meq.Freq())/self._freq0,spi);
      else:
        stokes = self._parm(st);
    return stokes;
    
  def coherency (self,observation):
    """Returns coherency matrix for this source, given an observation.
    Qualifiers from radec0 are added in.""";
    radec0 = observation.radec0();
    coh_node = self.ns.coherency.qadd(radec0);
    if not coh_node.initialized():
      if observation.circular():
        # create coherency elements
        rr = self.ns.rr.qadd(radec0) << (self.stokes("I") + self.stokes("V"))*0.5;
        rl = self.ns.rl.qadd(radec0) << Meq.ToComplex(self.stokes("Q"),self.stokes("U"))*0.5;
        lr = self.ns.lr.qadd(radec0) << Meq.Conj(rl);
        ll = self.ns.ll.qadd(radec0) << (self.stokes("I") - self.stokes("V"))*0.5;
        # create coherency node
        coh_node << Meq.Matrix22(rr,rl,lr,ll) / self.direction.n(radec0);
      else:
        # create coherency elements
        xx = self.ns.xx.qadd(radec0) << (self.stokes("I") + self.stokes("Q"))*0.5;
        yx = self.ns.yx.qadd(radec0) << Meq.ToComplex(self.stokes("U"),self.stokes("V"))*0.5;
        xy = self.ns.xy.qadd(radec0) << Meq.Conj(yx);
        yy = self.ns.yy.qadd(radec0) << (self.stokes("I") - self.stokes("Q"))*0.5;
        # create coherency node
        coh_node << Meq.Matrix22(xx,xy,yx,yy) / self.direction.n(radec0);
    return coh_node;
    
  def make_visibilities (self,nodes,array,observation):
    # use direction's phase shift method
    cohnode = lambda sta1,sta2: self.coherency(observation);
    self.direction.make_phase_shift(nodes,cohnode,array,observation.radec0());
   
