from numarray import *
from Timba.TDL import *

class Observation (object):
  def __init__(self,ns,*quals,**kwquals):
    self.ns = ns;
    self._quals = quals;
    self._kwquals = kwquals;
    
  def radec0 (self):
    """returns radec0 node""";
    radec0 = self.ns.radec0(*self._quals,**self._kwquals);
    if not radec0.initialized():
      radec0 << Meq.Composer(
          self.ns.ra0(*self._quals,**self._kwquals) << 0,
          self.ns.dec0(*self._quals,**self._kwquals) << 0);
    return radec0;
