import math
from Timba.TDL import *
from Timba.Meq import meq
from PointSource import *
  
STOKES = ("I","Q","U","V");

class GaussianSource(PointSource):
  def __init__(self,ns,name,direction,
               I=0.0,Q=0.0,U=0.0,V=0.0,
               Iorder=0,Qorder=0,Uorder=0,Vorder=0,
               spi=0.0,freq0=None,
               size=None,phi=0,symmetric=False,
               parm_options=record(node_groups='Parm')):
    PointSource.__init__(self,ns,name,direction,I,Q,U,V,
                Iorder,Qorder,Uorder,Vorder,
                spi,freq0,
                parm_options=parm_options);
    # create polc(s) for size
    self._symmetric = symmetric;
    if symmetric:
      self._create_polc('size',size);
    else:
      if isinstance(size,(int,float)):
        s1 = s2 = size;
      elif isinstance(size,(tuple,list)):
        if len(size) != 2:
          raise TypeError,"size: two numeric values expected";
        s1,s2 = size;
      else:
        raise TypeError,"size: two numeric values expected";
      self._create_polc('sigma1',s1);
      self._create_polc('sigma2',s2);
    # setup orientation
    # note: the orientation angle, phi, of the major axis
    # is defined in the direction East through South; i.e.
    # an angle of zero defines a Gaussian oriented east-west
    self._create_polc('phi',phi);
    
  def is_symmetric (self):
    return self._symmetric;
    
  def sigma (self):
    """Returns the size for this source (single node for symmetric,
    two-pack for elliptic).""";
    if self._symmetric:
      return self._parm('sigma');
    else:
      return self.ns.sigma ** Meq.Composer(self._parm("sigma1"),self._parm("sigma2"));
    return size;
      
  def phi (self):
    """Returns the orientation node for this source""";
    return self._parm("phi");
    
  def transformation_matrix (self):
    xfm = self.ns.xfmatrix;
    if not xfm.initialized():
      phi = self.phi();
      # get direction sin/cos
      cos_phi = self.ns.cos_phi << Meq.Cos(phi);
      sin_phi = self.ns.sin_phi << Meq.Sin(phi);
      # get sigma parameters
      if self.is_symmetric():
        sigma = self._parm("sigma");
        (a,b) = (sigma,sigma);
      else:
        (a,b) = (self._parm("sigma1"),self._parm("sigma2"));
      xfm << Meq.Matrix22(
          a*cos_phi,Meq.Negate(a*sin_phi),
          b*sin_phi,b*cos_phi);
    return xfm;

  def make_visibilities (self,nodes,array,observation):
    radec0 = observation.radec0();
    # 1/wl = freq/c
    iwl = self.ns0.inv_wavelength << ((self.ns0.freq<<Meq.Freq) / 2.99792458e+8);
    # -1/(wl^2): scaling factor applied to exp() argument below
    m_iwlsq = self.ns0.m_inv_wavelength_sq << Meq.Negate(Meq.Sqr(iwl));
    # scaling factor of gaussian for unit flux
    gscale = self.ns0.gaussiancomponent_scale << Meq.Constant(0.5*math.pi);
    # baseline UVs
    uv_ifr = array.uv_ifr(radec0);
    # rotation matrix
    xfm = self.transformation_matrix();\
    # flux scale -- coherency multiplied by scale constant above
    fluxscale = self.ns.fluxscale.qadd(radec0()) \
          << self.coherency(observation) * gscale;
    # transformed uv's (rotated and scaled)
    uv1sq = self.ns.uv1sq.qadd(radec0);
    u1sq = self.ns.u1sq.qadd(radec0);
    v1sq = self.ns.v1sq.qadd(radec0);
    # gaussian coherencies go here
    gcoh = self.ns.gauss_coh.qadd(radec0);
    # now generate nodes
    for ifr in array.ifrs():
      # rotate uvs and scale to wavelength
      uv1s = uv1sq(*ifr) << Meq.Sqr(Meq.MatrixMultiply(xfm,uv_ifr(*ifr)));
      u1s = u1sq(*ifr) << Meq.Selector(uv1s,index=0); 
      v1s = v1sq(*ifr) << Meq.Selector(uv1s,index=1); 
      gcoh(*ifr) << fluxscale * Meq.Exp((u1s+v1s)*m_iwlsq);
    # phase shift to source position
    self.direction.make_phase_shift(nodes,gcoh,array,radec0);
