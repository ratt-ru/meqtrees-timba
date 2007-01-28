from Timba.TDL import *
from Timba.Meq import meq
from Parameterization import *
import Jones
import Context

class Direction (Parameterization):
  """A Direction represents an absolute direction on the sky.
  'name' may be None, this usually identifies the phase centre.
  """;
  def __init__(self,ns,name,ra,dec,
               quals=[],kwquals={}):
    Parameterization.__init__(self,ns,name,
                              quals=quals,kwquals=kwquals);
    self._jones = [];
    self._ra = self._parm('ra',ra,tags="direction");
    self._dec = self._parm('dec',dec,tags="direction");
      
  def add_jones (self,kind,jones,directional=False):
    """Associates a Jones matrix with this direction.
    'kind' is a string identifier for this Jones term.
    'jones' is an under-qualified node which will be qualified with
    station id.
    If directional=True, the matrix is direction-dependant, and will
    be plugged in via a Compounder node. If directional=False, 
    matrix will be plugged in as-is""";
    self._jones.append((kind,jones,directional));
    
  def radec (self):
    """Returns ra-dec 2-vector node for this direction.
    """;
    radec = self.ns.radec;
    if not radec.initialized():
      radec << Meq.Composer(self._ra,self._dec);
    return radec;
    
  def lmn (self,dir0=None):
    """Returns LMN 3-vector node for this direction, given a reference
    direction dir0, or using the global phase center if not supplied.
    Qualifiers from dir0 are added in.""";
    dir0 = Context.get_dir0(dir0);
    if self is dir0:
      # lmn relative to self is constant
      lmn = self.ns.lmn;
      if not lmn.initialized():
        lmn << Meq.Composer(0,0,1);
    else:
      # create coordinate nodes, add in qualifiers of radec0 since
      # we may have different LMN sets for different directions
      radec0 = dir0.radec0();
      lmn = self.ns.lmn.qadd(radec0);
      if not lmn.initialized():
        lmn << Meq.LMN(radec_0=radec0,radec=self.radec());
    return lmn;
    
  def lm (self,dir0=None):
    """Returns an LM 2-vector node for this component, given a reference
    direction dir0, or using the global phase center if not supplied.
    Qualifiers from dir0 are added in.""";
    dir0 = Context.get_dir0(dir0);
    if self is dir0:
      # lm relative to self is constant
      lm = self.ns.lm;
      if not lm.initialized():
        lm << Meq.Composer(0,0);
    else:
      # create coordinate nodes, add in qualifiers of radec0 since
      # we may have different LMN sets for different directions
      radec0 = dir0.radec0();
      lm = self.ns.lm.qadd(radec0);
      if not lm.initialized():
        lm << Meq.Selector(self.lmn(dir0),index=[0,1],multi=True);
    return lm;
    
  def n (self,dir0=None):
    """Returns N node for this direction, given a reference
    direction dir0, or using the global phase center if not supplied.
    Qualifiers from dir0 are added in.""";
    dir0 = Context.get_dir0(dir0);
    if self is dir0:
      # n relative to self is constant
      n = self.ns.n;
      if not n.initialized():
        n << 1;
    else:
      # create coordinate nodes, add in qualifiers of radec0 since
      # we may have different LMN sets for different directions
      radec0 = dir0.radec0();
      n = self.ns.n.qadd(radec0);
      if not n.initialized():
        n << Meq.Selector(self.lmn(dir0),index=[2]);
    return n;
    
  def lmn_1 (self,dir0=None):
    """Returns L,M,N-1 3-vector node for this direction, given a reference
    direction dir0, or using the global phase center if not supplied.
    Qualifiers from dir0 are added in.""";
    dir0 = Context.get_dir0(dir0);
    if self is dir0:
      # lmn relative to self is constant
      lmn_1 = self.ns.lmn_minus1;
      if not lmn_1.initialized():
        lmn_1 << Meq.Composer(0,0,0);
    else:
      # create coordinate nodes, add in qualifiers of radec0 since
      # we may have different LMN sets for different directions
      radec0 = dir0.radec0();
      lmn_1 = self.ns.lmn_minus1.qadd(radec0);
      if not lmn_1.initialized():
        lmn_1 << Meq.Paster(self.lmn(dir0),self.n(dir0)-1,index=2);
    return lmn_1;
    
  def KJones (self,array=None,dir0=None):
    """makes and returns a series of Kjones (phase shift) nodes
    for this direction, given a reference direction dir0, or using
    the global phase center if not supplied.
    Return value is an under-qualified node, which should be 
    qualified with a station index.
    """;
    dir0 = Context.get_dir0(dir0);
    array = Context.get_array(array);
    # if direction is same, K is identity for all stations
    if self is dir0:
      Kj = self.ns.K << 1;
      return lambda p: Kj;
    else:
      radec0 = dir0.radec();
      Kj = self.ns.K.qadd(radec0);
      stations = array.stations();
      if not Kj(stations[0]).initialized():
        # use L,M,(N-1) for lmn. NB: this could be made an option in the future
        lmn_1 = self.lmn_1(dir0);
        uvw = array.uvw(dir0);
        for p in stations:
          Kj(p) << Meq.VisPhaseShift(lmn=lmn_1,uvw=uvw(p));
      return Kj;

  def make_phase_shift (self,vis,vis0,array=None,dir0=None):
    """phase-shifts visibilities given by vis0(p,q) from dir0 
    (the global phase center by default) to the given direction. 
    Shifted visibilities are created as vis(p,q).
    """;
    dir0 = Context.get_dir0(dir0);
    array = Context.get_array(array);
    # if direction is the same, use an Identity transform
    if self is dir0:
      for p,q in array.ifrs():
        vis(p,q) << Meq.Identity(vis0(p,q));
    # else apply KJones
    else:
      Kj = self.KJones(array=array,dir0=dir0);
      Jones.apply_corruption(vis,vis0,Kj,array.ifrs());
