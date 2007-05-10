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
    self._add_parm('ra',ra,tags="direction");
    self._add_parm('dec',dec,tags="direction");
    
  def radec (self):
    """Returns ra-dec 2-vector node for this direction.
    """;
    radec = self.ns.radec;
    if not radec.initialized():
      ra = self._parm('ra');
      dec = self._parm('dec');
      radec << Meq.Composer(ra,dec);
    return radec;
    
  def lmn (self,dir0=None):
    """Returns LMN 3-vector node for this direction, given a reference
    direction dir0, or using the global phase center if not supplied.
    Qualifiers from dir0 are added in.
    All other lmn-related methods below call on this one to get
    the basic lmn 3-vector.
    """;
    dir0 = Context.get_dir0(dir0);
    radec0 = dir0.radec();
    lmn = self.ns.lmn.qadd(radec0);
    if not lmn.initialized():
      if self is dir0:
        lmn << Meq.Composer(0,0,1);
      else:
        lmn << Meq.LMN(radec_0=radec0,radec=self.radec());
    return lmn;
    
  def _lmn_component (self,name,dir0,index):
    """Helper method for below, returns part of the LMN vector.""";
    lmn = self.lmn(dir0);
    comp = self.ns[name].qadd(lmn);  # use ns0: all qualifiers are in lmn already
    # if we used self.ns, we'd have duplicate qualifiers
    if not comp.initialized():
      comp << Meq.Selector(lmn,index=index,multi=True);
    return comp;

  def lm (self,dir0=None):
    """Returns an LM 2-vector node for this direction. All args are as
    per lmn().""";
    return self._lmn_component('lm',dir0,[0,1]);
  def l (self,dir0=None):
    """Returns an L node for this direction. All args are as per lmn().""";
    return self._lmn_component('l',dir0,0);
  def m (self,dir0=None):
    """Returns an M node for this direction. All args are as per lmn().""";
    return self._lmn_component('m',dir0,1);
  def n (self,dir0=None):
    """Returns an N node for this direction. All args are as per lmn().""";
    return self._lmn_component('n',dir0,2);
    
  def lmn_1 (self,dir0=None):
    """Returns L,M,N-1 3-vector node for this direction.
     All args are as per lmn().""";
    lmn = self.lmn(dir0);
    lmn_1 = self.ns.lmn_minus1.qadd(lmn);  # use ns0: all qualifiers are in lmn already
    if not lmn_1.initialized():
      lmn_1 << Meq.Paster(lmn,self.n(dir0)-1,index=2);
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
