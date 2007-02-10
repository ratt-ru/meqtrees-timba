from Timba.TDL import *
from Timba.Meq import meq
from Direction import Direction
from Parameterization import Parameterization
import Context
import math

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
    if isinstance(l,(int,float)) and isinstance(m,(int,float)):
      self._add_parm('n',math.sqrt(1-l*l-m*m),tags="direction");
      self._const_n = True;
    else:
      self._const_n = False;
      
  def radec (self):
    """Returns ra-dec two-pack for this direction.""";
    radec = self.ns.radec;
    if not radec.initialized():
      radec << Meq.LMRaDec(radec_0=self._dir0.radec(),lm=self.lm(self._dir0));
    return radec;
 
  def _lm (self,dir0=None):
    """Helper function: creates L,M nodes as needed, returns them as an (l,m) 
    tuple. dir0 is a direction relative to which lm is computed, at the
    moment it is not used.
    """;
    return (self._parm("l"),self._parm("m"));

  def lmn (self,dir0=None):
    """Returns LMN three-pack for this component.
    dir0 is a direction relative to which lm is computed, at the
    moment it is not used.""";
    lmn = self.ns.lmn;
    if not lmn.initialized():
      l,m = self._lm();
      if self._const_n:
        n = self._parm("n");
      else:
        n = self.ns.n << Meq.Sqrt(1-Meq.Sqr(l)-Meq.Sqr(m));
      lmn << Meq.Composer(l,m,n);
    return lmn;
    
