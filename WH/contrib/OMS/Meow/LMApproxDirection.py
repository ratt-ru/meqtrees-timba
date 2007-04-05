# file: .../Meow/LMApproxDirection.py

from Timba.TDL import *
from Timba.Meq import meq
from LMDirection import LMDirection
import math


class LMApproxDirection (LMDirection):
  """A LMApproxDirection is a (temporary) approximate version of LMDirection.
  It allows the relative shift of the uv-data phase-centre relative to a given
  Direction (dir0), which is not yet implemented properly in LMDirection."""

  def __init__(self,ns, name,
               l, m, dir0=None,
               quals=[], kwquals={}):
    LMDirection.__init__(self, ns, name,
                         l=l, m=m, dir0=dir0,
                         quals=quals, kwquals=kwquals)
    
  #----------------------------------------------------------------------------

  def lmn (self, dir0=None):
    """Returns LMN three-pack for this component. dir0 is a direction relative
    to which lm is computed. This is a re-implementation of the method in
    LMDirection, where dir0 is ignored at the moment."""
    lmn = self.ns.lmn;
    if not lmn.initialized():
      l,m = self._lm();
      if isinstance(dir0,(LMDirection,LMApproxDirection)):
        l0,m0 = dir0._lm()
        l = self.ns.dl << Meq.Subtract(l, l0)
        m = self.ns.dm << Meq.Subtract(m, m0)
        n = self.ns.n << Meq.Sqrt(1-Meq.Sqr(l)-Meq.Sqr(m));
      elif self._const_n:
        n = self._parm("n");
      else:
        n = self.ns.n << Meq.Sqrt(1-Meq.Sqr(l)-Meq.Sqr(m));
      lmn << Meq.Composer(l,m,n);
    return lmn;
    
  #----------------------------------------------------------------------------

  def mirror(self, axes='lm'):
    """Make a new object for its mirror direction (w.r.t. l=0, m=0).
    The argument axes can be 'lm', 'l' and 'm'. NB: Move to LMDirection..."""
    if not axes in ['l','m','lm']:
      print 'axes =',axes,', should be in:',['l','m','lm']
      raise ValueError,'mirror axes not recognised: '+str(axes)
    l,m = self._lm()
    if axes in ['l','lm']:
      l = self.ns.mirror_l << Meq.Negate(l)
    if axes in ['m','lm']:
      m = self.ns.mirror_m << Meq.Negate(m)
    name = 'mirror_'+axes+'_'+self.name
    new = LMApproxDirection(self.ns, name, l=l, m=m, dir0=self._dir0)  
    return new


#==================================================================

if __name__ == '__main__':

  from IfrArray import IfrArray
  from  Observation import Observation
  import Context
  from Direction import Direction
  
  ns = NodeScope();

  num_stations = 3
  ANTENNAS = range(1,num_stations+1)
  array = IfrArray(ns,ANTENNAS)
  observation = Observation(ns)
  Context.set(array, observation)

  dl = 0.001
  dm = dl
  quals= ['xxx']
  lma = LMApproxDirection(ns, 'lma', l=dl, m=dm, quals=quals)

  if 0:
    ref = LMApproxDirection(ns, 'ref', l=2*dl, m=2*dm, quals=quals)
    # ref = LMDirection(ns, 'ref', l=2*dl, m=2*dm, quals=quals)
    # ref = Direction(ns, 'ref', ra=0.0, dec=1.0, quals=quals)
    lmn = lma.lmn(dir0=ref)
    print 'lmn:',str(lmn)


  if 1:
    mir = lma.mirror()
    print str(mir)