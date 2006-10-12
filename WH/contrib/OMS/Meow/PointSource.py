from Timba.TDL import *
from Timba.Meq import meq
from SkyComponent import *
import Jones
  
STOKES = ("I","Q","U","V");

class PointSource(SkyComponent):
  def __init__(self,ns,name,direction,
               I=0.0,Q=0.0,U=0.0,V=0.0,
               Iorder=0,Qorder=0,Uorder=0,Vorder=0,
               spi=0.0,freq0=None,RM=None,
               parm_options=record(node_groups='Parm')):
    SkyComponent.__init__(self,ns,name,direction,parm_options=parm_options);
    # create flux polcs
    for stokes in STOKES:
      self._create_polc(stokes,locals()[stokes],locals()[stokes+"order"]);
    # see if a spectral index is present (freq0!=0 then), create polc
    self._freq0 = freq0;
    self._rm=RM
    if freq0 is not None:
      # rename I polc to I0 
      self._rename_polc("I","I0");
      self._create_polc("spi",create_polc(spi));
    if self._rm is not None:
      self._create_polc("rm",create_polc(self._rm));
      # change original Q,U values
      self._rename_polc("Q","Q0");
      self._rename_polc("U","U0");
      
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
      elif (self._rm and (st=="Q" or st=="U")):
        # squared wavelength
        iwl2 = self.ns0.wavelength2 << Meq.Sqr(2.99792458e+8/(self.ns0.freq<<Meq.Freq));
        # rotation node
        farot=self.ns.farot<<self._parm("rm")*iwl2
        cosf=self.ns.cosf<<Meq.Cos(farot)
        sinf=self.ns.sinf<<Meq.Sin(farot)
        if st=="Q":
         stokes<<cosf*self._parm("Q0")-sinf*self._parm("U0")
        else:
         stokes<<sinf*self._parm("Q0")+cosf*self._parm("U0")
      else:
        stokes = self._parm(st);
    return stokes;
    
  def coherency (self,observation):
    """Returns the intrinsic (i.e. non-projected) coherency matrix for this source,
    given an observation.""";
    radec0 = observation.radec0();
    coh_node = self.ns.coherency.qadd(radec0);
    if not coh_node.initialized():
      if observation.circular():
        # create coherency elements
        rr = self.ns.rr << (self.stokes("I") + self.stokes("V"));
        rl = self.ns.rl << Meq.ToComplex(self.stokes("Q"),self.stokes("U"));
        lr = self.ns.lr << Meq.Conj(rl);
        ll = self.ns.ll << (self.stokes("I") - self.stokes("V"));
        # create coherency node
        coh_node << Meq.Matrix22(rr,rl,lr,ll)*0.5;
      else:
        # create coherency elements
        xx = self.ns.xx << (self.stokes("I") + self.stokes("Q"));
        xy = self.ns.xy << Meq.ToComplex(self.stokes("U"),self.stokes("V"));
        yx = self.ns.yx << Meq.Conj(xy);
        yy = self.ns.yy << (self.stokes("I") - self.stokes("Q"));
        # create coherency node
        coh_node << Meq.Matrix22(xx,xy,yx,yy)*0.5;
    return coh_node;
    
  def make_visibilities (self,nodes,array,observation):
    # use direction's phase shift method
    cohnode = lambda sta1,sta2: self.coherency(observation);
    self.direction.make_phase_shift(nodes,cohnode,array,observation.radec0());
   
