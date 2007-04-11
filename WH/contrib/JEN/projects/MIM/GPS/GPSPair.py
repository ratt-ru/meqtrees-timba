# file ../JEN/projects/MIM/GPS/GPSPair.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Vector import GeoLocation
from numarray import *

Settings.forest_state.cache_policy = 100


#================================================================
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
  
  def TEC_bias (self):
    """Returns the station TEC bias (node)"""
    return self._parm('TEC_bias')

  def solvable(self, tags='*'):
    """Return a list of solvable parms (nodes)"""
    return [self.TEC_bias()]





#================================================================
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
  
  def TEC_bias (self):
    """Returns the satellite TEC bias (node)"""
    return self._parm('TEC_bias')
        
  def solvable(self, tags='*'):
    """Return a list of solvable parms (nodes)"""
    return [self.TEC_bias()]








#================================================================
#================================================================

class GPSPair (Meow.Parameterization):
  """Represents a combination of a GPSStation and GPSSatellite"""
  
  def __init__(self, ns, station, satellite,
               name=None, quals=[],kwquals={}):

    # The object name. By default a combination of its station/satellite
    # names, but it can be overridden with the user-defined name.
    if not isinstance(name, str):
      name = str(station.name)+'|'+str(satellite.name)
    else:
      # Add the station/satellite names to the nodescope qualifiers:
      if quals==None: quals = []
      if not isinstance(quals,(list,tuple)): quals = [quals]
      quals.append(station.name)
      quals.append(satellite.name)

    Meow.Parameterization.__init__(self, ns=ns, name=name,
                                   quals=quals, kwquals=kwquals)

    self._station = station
    self._satellite = satellite
    return None

  #---------------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    # ss = 'GPSPair: '
    ss += '  '+str(self.name)
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

  #.......................................................

  def mimTEC(self, mim, show=False):
    """Return a node/subtree that produces a simulated TEC value for
    a specified time-range (in the request). It gets its information
    from the given (simulated) MIM object"""
    node = self.ns['mimTEC']
    if not node.initialized():
      TEC = mim.TEC(self.longlat_pierce(),
                    self.zenith_angle())
      node << Meq.Add(TEC, self._station.TEC_bias(),
                      self._satellite.TEC_bias())
    self._station._show_subtree(node, show=show, recurse=4)
    return node

  #-------------------------------------------------------

  def solvable(self, tags='*', show=True):
    """Return a list of solvable parms (nodes)"""
    ss = []
    ss.extend(self._station.solvable(tags=tags))
    ss.extend(self._satellite.solvable(tags=tags))
    if show:
      print '\n** .solvable(tags=',tags,') <-',self.oneliner()
      for node in ss:
        print '  -',str(node)
      print
    return ss

  #-------------------------------------------------------

  def zenith_angle(self, show=False):
    """Return the zenith angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    name = 'zenith_angle'
    node = self.ns[name]
    if not node.initialized():
      dxyz = self._satellite.binop('Subtract', self._station, show=show)
      encl = self._satellite.enclosed_angle(dxyz, show=show)
      node << Meq.Identity(encl)
    self._station._show_subtree(node, show=show, recurse=4)
    return node

  #-------------------------------------------------------

  def elevation(self, show=False):
    """Return the elevation angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    name = 'elevation'
    node = self.ns[name]
    if not node.initialized():
      zang = self.zenith_angle()
      node << Meq.Subtract(pi/2.0, zang)
    self._station._show_subtree(node, show=show, recurse=4)
    return node

  #-------------------------------------------------------

  def azimuth(self, show=False):
    """Return the azimuth angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    name = 'azimuth'
    node = self.ns[name]
    if not node.initialized():
      dll = self.longlat_diff()
      dlong = node('dlong') << Meq.Selector(dll, index=0)
      node = False                                # ... still needs a little thought .....
    self._station._show_subtree(node, show=show, recurse=4)
    return node

  #-------------------------------------------------------

  def azel (self, show=False):
    """Returns (azimuth,elevation) (tensor node)"""
    node = self.ns['azel']
    if not node.initialized():
      node << Meq.Composer(self.azimuth(),
                           self.elevation())
    self._station._show_subtree(node, show=show)
    return node

  #-------------------------------------------------------

  def azel_complex (self, show=False):
    """Returns azel (node) as complex (al+j*elev), for plotting"""
    node = self.ns['azel_complex']
    if not node.initialized():
      node << Meq.ToComplex(self.azimuth(),
                            self.elevation())
    self._station._show_subtree(node, show=show)
    return node
      
  #-------------------------------------------------------

  def longlat_diff(self, show=False):
    """Return the [longtitude,latitude] difference between
    its station and its satellite"""
    name = 'longlat_diff'
    node = self.ns[name]
    if not node.initialized():
      ll_stat = self._station.longlat()
      ll_sat = self._satellite.longlat()
      node << Meq.Subtract(ll_sat,ll_stat)
    self._station._show_subtree(node, show=show, recurse=4)
    return node

  #-------------------------------------------------------

  def longlat_pierce(self, h=3e5, show=False):
    """Return the [longtitude,latitude] of the pierce point through
    the ionsosphere, given an ionospheric altitude (node/number) h (m)"""
    name = 'longlat_pierce'
    node = self.ns[name]
    if not node.initialized():
      dll = self.longlat_diff()
      alt_sat = self._satellite.altitude()
      fraction = node('fraction') << Meq.Divide(h, alt_sat)
      ll_shift = node('dll_pierce') << Meq.Multiply(dll, fraction)
      ll_stat = self._station.longlat()
      node << Meq.Add(ll_stat,ll_shift)
    self._station._show_subtree(node, show=show, recurse=4)
    return node


  #-------------------------------------------------------
  #-------------------------------------------------------

  def insert_elevation_flagger(self, data, elmin=1.0, show=False):
    """Insert a zero-flagger that flags the vells if the satellite
    elevation is below a specified value (elmin)"""
    name = 'elevation_flagger'
    node = self.ns[name]
    if not node.initialized():
      elev = self.elevation()
      eldiff = node('eldiff') << Meq.Subtract(elmin, elev)
      zerof = node('zerof') << Meq.ZeroFlagger(eldiff,
                                               oper='GT',
                                               flag_bit=1)
      node << Meq.MergeFlags(data, zerof)
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
        display.subtree(st1.TEC_bias())

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
        display.subtree(sat1.TEC_bias())

      if 0:
        sat1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      pair = GPSPair (ns, station=st1, satellite=sat1)
      pair.display(full=True)

      if 0:
        pair.elevation(show=True)

      if 0: 
        pair.azimuth(show=True)

      if 1:
        pair.azel(show=True)
        pair.azel_complex(show=True)

      if 0:
        pair.zenith_angle(show=True)

      if 0:
        pair.longlat_diff(show=True)

      if 0:
        pair.longlat_pierce(show=True)

      if 0:
        pair.solvable(tags='*', show=True)

      if 0:
        data = ns['data'] << Meq.Constant(-56)
        pair.insert_elevation_flagger(data, elmin=1.0, show=True)



    
