from Timba.TDL import *
from Timba.Meq import meq
from Direction import Direction
from Parameterization import Parameterization
import Jones

class LMDirection (Direction):
  """A LMDirection represents a direction on the sky relative
  to phase center, i.e. given in L/M coordinates.
  If constant=True, MeqConstants are used for the direction components, 
  else MeqParms.
  """;
  def __init__(self,ns,name,l,m,
               constant=False,
               parm_options=record(node_groups='Parm'),
               quals=[],kwquals={}):
    Parameterization.__init__(self,ns,name,parm_options=parm_options,
                              quals=quals,kwquals=kwquals);
    self._constant = constant;
    self._jones = [];
    if constant:
      self._l = self._const_node('l',l);
      self._m = self._const_node('m',m);
    else:
      self._create_polc('l',l);
      self._create_polc('m',m);
      
  def add_jones (self,kind,jones,directional=False):
    """Associates a Jones matrix with this direction.
    'kind' is a string identifier for this Jones term.
    'jones' is an under-qualified node which will be qualified with
    station id.
    If directional=True, the matrix is direction-dependant, and will
    be plugged in via a Compounder node. If directional=False, 
    matrix will be plugged in as-is""";
    self._jones.append((kind,jones,directional));
    
  def radec (self,radec0):
    """Returns ra-dec two-pack for this direction, given a reference
    direction radec0.
    Qualifiers from radec0 are added in.""";
    radec = self.ns.radec.qadd(radec0);
    if not radec.initialized():
      raise RuntimeError;
      radec << Meq.LMRaDec(radec_0=radec0,lm=self.lm());
    return radec;
    
  def _lm (self):
    """Creates L,M nodes as needed, returns them as an (l,m) tuple""";
    l = self.ns.l;
    m = self.ns.m;
    if not l.initialized():
      if self._constant:
        l = self._l;
        m = self._m;
      else:
        l = self._parm("l");
        m = self._parm("m");
    return (l,m);
    
  def lm (self):
    """Returns LM two-pack for this source.
    Radec0 argument is ignored; it is provided here for compatibility
    with Direction.lm().
    """;
    lm = self.ns.lm;
    if not lm.initialized():
      lm << Meq.Composer(*self._lm());
    return lm;

  def n (self,radec0=None):
    """Returns 'n' coordinate for this source.
    Radec0 argument is ignored; it is provided here for compatibility
    with Direction.n().
    """;
    n = self.ns.n;
    if not n.initialized():
      l,m = self._lm();
      n << Meq.Sqrt(1-Meq.Sqr(l)-Meq.Sqr(m));
    return n;
    
  def lmn (self,radec0=None):
    """Returns LMN three-pack for this component.
    Radec0 argument is ignored; it is provided here for compatibility
    with Direction.lmn().
    """;
    lmn = self.ns.lmn;
    if not lmn.initialized():
      l,m = self._lm();
      n = self.n();
      lmn << Meq.Composer(l,m,n);
    return lmn;
    
  def lmn_1 (self,radec0=None):
    """Returns LMN-1 three-pack for this component.
    Radec0 argument is ignored; it is provided here for compatibility
    with Direction.lmn().
    """;
    lmn_1 = self.ns.lmn_minus1;
    if not lmn_1.initialized():
      l,m = self._lm();
      n = self.n();
      lmn_1 << Meq.Composer(l,m,n-1);
    return lmn_1;
    
  def _same_as (self,radec0):
    """Returns True if this direction is same as radec0
    In this case returns False, since there's no way to know.""";
    return False;
