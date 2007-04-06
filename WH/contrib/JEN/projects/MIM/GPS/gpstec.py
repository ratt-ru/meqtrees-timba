# file ../JEN/projects/MIM/GPS/gpstec.py

from Timba.TDL import *
from Timba.Meq import meq
# from Parameterization import *

import Meow

#================================================================

class GPSStation (Meow.Position):
  """Represents a GPS station that measures TEC values"""

  def __init__(self, ns, name, pos=[], refpos=None,
               quals=[],kwquals={}):

    Meow.Position.__init__(self, ns=ns, name=name,
                           x=pos[0], y=pos[1], z=pos[2],
                           quals=quals, kwquals=kwquals)
    if not isinstance(refpos,(list,tuple)) or not len(refpos)==3:
      refpos = [0.0,0.0,0.0]
    self._relpos = [pos[0]-refpos[0], pos[1]-refpos[1], pos[2]-refpos[2]]
    self._bias = None
    return None
  
  def oneliner (self):
    ss = 'GPSStation: '+self.name
    ss += '  (rel)pos='+str(self._relpos)
    return ss
  
  def bias (self):
    """Returns the station TEC bias (node)"""
    return self._bias
        

#================================================================

class GPSSatellite (Meow.Position):
  """Represents a GPS satellite"""

  def __init__(self, ns, name,
               x=None, y=None, z=None, 
               quals=[],kwquals={}):

    self._bias = None
    Meow.Position.__init__(self, ns=ns, name=name, x=x, y=y, z=z,
                           quals=quals, kwquals=kwquals)
    return None

  def oneliner (self):
    ss = 'GPSSatellite: '+self.name
    return ss
  
  def bias (self):
    """Returns the satellite TEC bias (node)"""
    return self._bias
        

#================================================================

class GPSPair (object):
  """Represents a combination of a GPSStation and GPSSatellite"""
  
  def __init__(self, ns, name=None, station=None, satellite=None,
               quals=[],kwquals={}):

    self._station = station
    self._satellite = satellite
    self._name = name
    self._label = str(self._name)+'('+str(self._station.name)+'|'+str(self._satellite.name)+')'

    if not isinstance(quals,(list,tuple)): quals = [quals]
    quals.append(self._station.name)
    quals.append(self._satellite.name)
    self._ns = Meow.QualScope(ns, quals=quals, kwquals=kwquals)
    
    return None

  def label (self):
    """Return the pair label (station_satellite)"""
    return self._label

  def oneliner (self):
    ss = 'GPSPair: '+str(self.label())
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * '+self._station.oneliner()
    print '  * '+self._satellite.oneliner()
    print
    return True


  #-------------------------------------------------------

  def zenith_angle(self):
    """Return the zenith angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course"""
    zang = self._ns.zenith_angle
    if not zang.initialized():
      xyz1 = self._satellite.xyz()
      xyz2 = self._station.xyz()
      dxyz = zang('dxyz') << Meq.Subtract(xyz1,xyz2)
      prod11 = zang('prod11') << Meq.Sqr(xyz2)
      prod22 = zang('prod22') << Meq.Sqr(dxyz)
      prod12 = zang('prod12') << Meq.Multiply(xyz2,dxyz)
      cc11 = []
      cc22 = []
      cc12 = []
      for index in [0,1,2]:
        cc11.append(zang('cc11')(index) << Meq.Selector(prod11, index=index))
        cc22.append(zang('cc22')(index) << Meq.Selector(prod22, index=index))
        cc12.append(zang('cc12')(index) << Meq.Selector(prod12, index=index))
      sum12 = zang('sum12') << Meq.Add(*cc12)
      ssq12 = zang('ssq12') << Meq.Multiply((zang('ssq1') << Meq.Add(*cc11)),
                                            (zang('ssq2') << Meq.Add(*cc22)))
      norm = zang('norm') << Meq.Sqrt(ssq12)
      cosz = zang('cos') << Meq.Divide(sum12, norm)
      zang << Meq.Acos(cosz)
    return zang


#================================================================
    
if __name__ == '__main__':
    """Test program"""
    from Timba.Contrib.JEN.Grunt import display
    
    ns = NodeScope()
    st1 = GPSStation(ns,'st1', [1,2,12])
    if 0:
      xyz = st1.xyz()
      display.subtree(xyz, 'st1')

    sat1 = GPSSatellite(ns,'sat1', x=4, y=7, z=8)
    if 0:
      xyz = sat1.xyz()
      display.subtree(xyz, 'sat1')

    if 1:
      pair = GPSPair (ns, 'p1', station=st1, satellite=sat1)
      pair.display(full=True)
      zang = pair.zenith_angle()
      display.subtree(zang, 'zang')
    
