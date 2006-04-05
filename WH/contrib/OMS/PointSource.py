from numarray import *
from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.OMS.SkyComponent import *
  
STOKES = ("I","Q","U","V");

class PointSource(SkyComponent):
  def __init__(self,ns,name,ra=0.0,dec=0.0,
               I=0.0,Q=0.0,U=0.0,V=0.0,
               Iorder=0,Qorder=0,Uorder=0,Vorder=0,
               spi=0.0,freq0=None,   
               parm_options=record(node_groups='Parm')):
    SkyComponent.__init__(self,ns,name,ra,dec,parm_options=parm_options);
    # create flux polcs
    for stokes in STOKES:
      # if given stokes variable is not a polc, create a polc from it
      flux = locals()[stokes];
      if not isinstance(flux,POLC_TYPE):
        flux = create_polc(flux,locals()[stokes+"order"]);
      self._polcs[stokes] = flux;
    # see if a spectral index is present, create polc
    if freq0 is not None:
      if not isinstance(spi,(int,float)):
        raise TypeError,"spi: numeric value expected";
      if not isinstance(freq0,(int,float)):
        raise TypeError,"freq0: numeric value or 'None' expected";
      self._polcs.spi = create_polc(c00=spi);
      self._freq0 = freq0;
      # rename I polc to I0 polc
      self._polcs.I0 = self._polcs.I;
      del self._polcs["I"];
    else:
      self._freq0 = None;

  def iquv (self):
    """Returns an IQUV four-pack for this source""";
    iquv = self.ns.iquv(self.name);
    if not iquv.initialized():
      stokes = self.stokes();
      iquv << Meq.Composer(*[stokes(st) for st in STOKES]);
    return iquv;
    
  def stokes (self,st):
    """Returns flux node for this source. 'st' must be one of 'I','Q','U','V'.""";
    if st not in STOKES:
      raise ValueError,"st: must be one of 'I','Q','U','V'";
    stokes = self.ns[st](self.name);
    if not stokes.initialized():
      # if a ref frequency is given, use spectral index for I flux,
      # else just use a plain parm
      if st == "I" and self._freq0:
        i0 = self._parm("I0");
        spi = self._parm("spi");
        stokes << i0 * Meq.Pow((self.ns.freq ** Meq.Freq())/self._freq0,spi);
      else:
        stokes = self._parm(st);
    return stokes;
    
  def n (self,radec0):
    """Returns 'n' coordinate for this source and phase center""";
    lmn = self.lmn(radec0);
    n = self.ns.n.qadd(lmn);
    if not n.initialized():
      n << Meq.Selector(lmn,index=2);
    return n;
    
  def coherency (self,radec0):
    """Returns coherency matrix for this source, given a phase centre.
    Qualifiers from radec0 are added in.""";
    coh_node = self.ns.coherency(self.name).qadd(radec0);
    if not coh_node.initialized():
      # create coherency elements
      xx = self.ns.xx.qadd(coh_node) << (self.stokes("I") + self.stokes("Q"))*0.5;
      yx = self.ns.yx.qadd(coh_node) << Meq.ToComplex(self.stokes("U"),self.stokes("V"))*0.5;
      xy = self.ns.xy.qadd(coh_node) << Meq.Conj(yx);
      yy = self.ns.yy.qadd(coh_node) << (self.stokes("I") - self.stokes("Q"))*0.5;
      # create coherency node
      coh_node << Meq.Matrix22(xx,xy,yx,yy) / self.n(radec0);
    return coh_node;
    
  def make_phase_shift (self,vis,vis0,array,observation):
    radec0 = observation.radec0();
    # create station-based K Jones (phase shift) for this source.
    # use L,M,(N-1) for lmn (fringe stopping?). NB: this could be made
    # an Array option in the future
    lmn = self.lmn(radec0);
    lmn_1 = self.ns.lmn_minus1.qadd(lmn) << Meq.Paster(lmn,self.n(radec0)-1,index=2);
    uvw = array.uvw(observation);
    Kj = self.ns.K(self.name).qadd(radec0);
    for station in array.stations():
      Kj(station) << Meq.VisPhaseShift(lmn=lmn_1,uvw=uvw(station));
    # work out visibilities
    for (sta1,sta2) in array.ifrs():
      vis(sta1,sta2) << Meq.MatrixMultiply(
        Kj(sta1),
        vis0(sta1,sta2),
        Kj(sta2,'conj') ** Meq.ConjTranspose(Kj(sta2)));
    pass;
    
  def make_visibilities (self,nodes,array,observation):
    cohnode = lambda sta1,sta2: self.coherency(observation.radec0());
    self.make_phase_shift(nodes,cohnode,array,observation);
    return nodes;
   
