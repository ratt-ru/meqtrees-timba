from Timba.TDL import *
from Timba.Meq import meq
from Direction import Direction
from Parameterization import Parameterization
import Jones
import Context

class LMDirection (Direction):
  """A LMDirection represents a direction on the sky, specified
  in l,m coordinates relative to some other direction dir0 
  (the phase center of the global observation in Meow.Context, by default).
  """;
  def __init__(self,ns,name,l,m,dir0=None,
               quals=[],kwquals={}):
    Parameterization.__init__(self,ns,name,
                              quals=quals,kwquals=kwquals);
    self._dir0 = Context.get_dir0(dir0);
    self._add_parm('l',l,tags="direction");
    self._add_parm('m',m,tags="direction");
      
  def radec (self):
    """Returns ra-dec two-pack for this direction.""";
    radec = self.ns.radec;
    if not radec.initialized():
      radec << Meq.LMRaDec(radec_0=self._dir0.radec(),lm=self.lm());
    return radec;
    
  def _lm (self,dir0=None):
    """Creates L,M nodes as needed, returns them as an (l,m) tuple.
    dir0 is a direction relative to which lm is computed, at the 
    moment it is not used.
    """;
    return (self._parm("l"),self._parm("m"));
    
  def lm (self,dir0=None):
    """Returns LM two-pack for this source.
    dir0 is a direction relative to which lm is computed, at the 
    moment it is not used.""";
    lm = self.ns.lm;
    if not lm.initialized():
      lm << Meq.Composer(*self._lm());
    return lm;

  def n (self,dir0=None):
    """Returns 'n' coordinate for this source.
    dir0 is a direction relative to which lm is computed, at the 
    moment it is not used.""";
    n = self.ns.n;
    if not n.initialized():
      l,m = self._lm();
      n << Meq.Sqrt(1-Meq.Sqr(l)-Meq.Sqr(m));
    return n;
    
  def lmn (self,dir0=None):
    """Returns LMN three-pack for this component.
    dir0 is a direction relative to which lm is computed, at the 
    moment it is not used.""";
    lmn = self.ns.lmn;
    if not lmn.initialized():
      l,m = self._lm();
      n = self.n();
      lmn << Meq.Composer(l,m,n);
    return lmn;
    
  def lmn_1 (self,dir0=None):
    """Returns LMN-1 three-pack for this component.
    dir0 is a direction relative to which lm is computed, at the 
    moment it is not used.""";
    lmn_1 = self.ns.lmn_minus1;
    if not lmn_1.initialized():
      l,m = self._lm();
      n = self.n();
      lmn_1 << Meq.Composer(l,m,n-1);
    return lmn_1;
    
