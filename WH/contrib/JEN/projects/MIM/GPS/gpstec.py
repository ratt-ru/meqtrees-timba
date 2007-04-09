# file ../JEN/projects/MIM/GPS/gpstec.py

from Timba.TDL import *
from Timba.Meq import meq
# from Parameterization import *

import Meow

from Timba.Contrib.JEN.Grunt import display
# from Timba.Contrib.JEN.Vector import Vector
from Timba.Contrib.JEN.Vector import GeoLocation
from numarray import *

Settings.forest_state.cache_policy = 100

#================================================================

class GPSStation (GeoLocation.GeoLocation):
  """Represents a GPS station that measures TEC values"""

  def __init__(self, ns, name, xyz=[],
               longlat=None, 
               quals=[],kwquals={}):

    GeoLocation.GeoLocation.__init__(self, ns=ns, name=name, xyz=xyz,
                                     longlat=longlat, radius=None,
                                     quals=quals, kwquals=kwquals,
                                     tags=['GeoLocation','GPSStation'],
                                     solvable=False)

    self._add_parm('TEC_bias', Meow.Parm(), tags=['GPSStation'])
    return None

  #---------------------------------------------------------------
  
  def bias (self):
    """Returns the station TEC bias (node)"""
    return self._parm('TEC_bias')



#================================================================

class GPSSatellite (GeoLocation.GeoLocation):
  """Represents a GPS satellite"""

  def __init__(self, ns, name, xyz=[],
               longlat=None, radius=None,
               quals=[],kwquals={}):

    GeoLocation.GeoLocation.__init__(self, ns=ns, name=name, xyz=xyz,
                                     longlat=longlat, radius=radius,
                                     quals=quals, kwquals=kwquals,
                                     tags=['GeoLocation','GPSSatellite'],
                                     solvable=False)

    self._add_parm('TEC_bias', Meow.Parm(), tags=['GPSSatellite'])
    return None

  #---------------------------------------------------------------
  
  def bias (self):
    """Returns the satellite TEC bias (node)"""
    return self._parm('TEC_bias')
        




#================================================================
#================================================================

class GPSPair (object):
  """Represents a combination of a GPSStation and GPSSatellite"""
  
  def __init__(self, ns, station, satellite,
               name=None, quals=[],kwquals={}):

    self._station = station
    self._satellite = satellite

    # The object name. By default a combination of its station/satellite
    # names, but it can be overridden with the user-defined name.
    self._name = str(self._station.name)+'|'+str(self._satellite.name)
    if isinstance(name, str): self._name = name

    # Add the station/satellite names to the nodescope qualifiers:
    if not isinstance(quals,(list,tuple)): quals = [quals]
    quals.append(self._station.name)
    quals.append(self._satellite.name)
    self.ns0 = ns
    self.ns = Meow.QualScope(ns, quals=quals, kwquals=kwquals)

    return None

  #---------------------------------------------------------------

  def name (self):
    """Return the pair name (station_satellite)"""
    return self._name

  def oneliner (self):
    ss = 'GPSPair: '+str(self.name())
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * '+self.station().oneliner()
    print '  * '+self.satellite().oneliner()
    print
    return True

  #-------------------------------------------------------

  def station(self):
    """Return its station object"""
    return self._station

  def satellite(self):
    """Return its satellite object"""
    return self._satellite

  #-------------------------------------------------------

  def TEC(self):
    """Return a node/subtree that produces a measured TEC value for
    a specified time-range (in the request). It gets its information
    from external GPS data in a file or something."""
    node = None
    return node

  #-------------------------------------------------------

  def zenith_angle(self, show=False):
    """Return the zenith angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    name = 'zenith_angle'
    node = self.ns[name]
    if not node.initialized():
      dxyz = self._satellite.binop('Subtract', self._station, show=show)
      node = self._satellite.enclosed_angle(dxyz, show=show)
    return node


  #-------------------------------------------------------

  def longlat_piercing(self, h=3e5, show=False):
    """Return the [longtitude,latitude] of the piercing point through
    the ionsosphere, given an ionospheric altitude (node/number) h (m)"""
    name = 'longlat_piercing'
    node = self.ns[name]
    if not node.initialized():
      ll_stat = self._station.longlat()
      ll_sat = self._satellite.longlat()
      dll = node('dll') << Meq.Subtract(ll_sat,ll_stat)
      alt_sat = self._satellite.altitude()
      alpha = node('alpha') << Meq.Divide(h, alt_sat)
      node << Meq.Multiply(dll, alpha)
    self._station._show_subtree(node, show=show, recurse=4)
    return node







#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    xyz1 = array([1.0,-3.5,5.8])
    xyz2 = array([10*xyz1[0], 8*xyz1[1], 6*xyz1[2]])

    st1 = GPSStation(ns,'st1', xyz1)
    sat1 = GPSSatellite(ns,'sat1', xyz2)

    pair = GPSPair (ns, station=st1, satellite=sat1)
    pair.display(full=True)
    zang = pair.zenith_angle()
    
    cc.append(zang)

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,1,10)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       

#================================================================
# Test program
#================================================================
    
if __name__ == '__main__':
    """Test program"""
    print
    ns = NodeScope()

    if 1:
      # st1 = GPSStation(ns, 'st1', [1,2,12])
      st1 = GPSStation(ns, 'st1', longlat=[-0.1,1.0])
      print st1.oneliner()

      if 1:
        st1.node(show=True)
        st1.altitude(show=True)
        st1.test_result()

      if 0:
        display.subtree(st1.bias())

      if 0:
        st1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      sat1 = GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0], radius=8e6)
      print sat1.oneliner()

      if 1:
        sat1.node(show=True)
        sat1.altitude(show=True)
        sat1.test_result()

      if 0:
        display.subtree(sat1.bias())

      if 0:
        sat1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      pair = GPSPair (ns, station=st1, satellite=sat1)
      pair.display(full=True)

      if 0:
        pair.zenith_angle(show=True)

      if 1:
        pair.longlat_piercing(show=True)


    
