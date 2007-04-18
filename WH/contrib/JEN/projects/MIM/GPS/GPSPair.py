# file ../JEN/projects/MIM/GPS/GPSPair.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow

from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Vector import GeoLocation
from numarray import *

Settings.forest_state.cache_policy = 100


#================================================================
#================================================================

class GPSStation (GeoLocation.GeoLocation):
  """Represents a GPS station that measures TEC values"""

  def __init__(self, ns, name, longlat=None,
               simulate=False, stddev=1.0,
               quals=[],kwquals={}):

    GeoLocation.GeoLocation.__init__(self, ns=ns, name=name,
                                     longlat=longlat, radius=None,
                                     quals=quals, kwquals=kwquals,
                                     typename='GPSStation',
                                     tags=['GeoLocation','GPSStation'],
                                     solvable=False)

    # Define the station parameter (simulated or solvable):
    self._pnames = []                     # list of (solvable) MeqParm names
    self._simulate = simulate
    self._stddev = stddev
    pname = 'TEC_bias'
    if self._simulate:
      sp = SimulParm.SimulParm(self.ns, pname, value=0.0, stddev=self._stddev)
      self._add_parm(pname, sp.create(), tags=['GPSStation'])
      sp.display()
    else:
      self._add_parm(pname, Meow.Parm(), tags=['GPSStation'])
      self._pnames.append(pname)

    # Finished:
    return None

  #------------------------------------------------------------------

  def oneliner (self):
    """Return a one-line summary of this object."""
    ss = self.oneliner_common()
    if self._simulate:
      ss += ' (TEC stddev='+str(self._stddev)+')'
    return ss

  #---------------------------------------------------------------
  
  def TEC_bias (self, show=False):
    """Returns the station TEC bias (node)"""
    node = self._parm('TEC_bias')
    self._show_subtree(node, show=show)
    return node

  def solvable(self, tags='*'):
    """Return a list of solvable parms (nodes)"""
    ss = []
    for pname in self._pnames:
      ss.append(self._parm(pname))
    return ss


  #-------------------------------------------------------

  def mimTECz(self, mim, bookpage='MIM'):
    """Make an insector node for the TEC values as a function of time,
    for a range of different zenith-angles, as seen from the specified
    longitude and latitude (longlat) position. Default longlat=[0,0]."""
    name = 'mimTECz'
    qnode = self.ns[name]
    if not qnode.initialized():
      longlat = mim.longlat_pierce()     # <---------- !!
      cc = []
      labels = []
      for z in 0.1*array(range(6)):
        labels.append('z='+str(z))
        node = qnode(z) << self.TEC(longlat, z=z)
        print '- z=',z,str(node)
        cc.append(node)
      qnode << Meq.Composer(children=cc, plot_label=labels)
      JEN_bookmarks.create(qnode, name, page=bookpage,
                           viewer='Collections Plotter')
    return qnode



#================================================================
#================================================================

# 

class GPSSatellite (GeoLocation.GeoLocation):
  """Represents a GPS satellite"""


  def __init__(self, ns, name, xyz=None, longlat=None, 
               move=False, sign=dict(direction=1,inclination=1),
               simulate=False, stddev=1.0,
               quals=[],kwquals={}):

    # Orbit radius is 21000 km plus the Earth radius (6378 km)
    # Orbital period is 12 hrs
    # Orbit inclination is 52 degr (i.e. it gets up to 52 degr latitude)
    # Coordinate systems:
    # - longitude is POSITIVE towards the East (right-handed!)
    # - xyz: z-axis positive alonf the Earth axis
    #        x-axis intersects with Greenwich meridian
    #        y-axis is positive towards the East
    # - movement:
    #   - longitude varies linearly with time
    #   - latitide varies sinusoidally

    self._Earth = dict(radius=6378, unit='km', flattening=3.36e-6)
    radius = self._Earth['radius'] + 21000       # orbit radius (km)

    if longlat:                                  # specified as longlat
      if move:                                   # make time-dependent
        node = ns['longlat']('orbit')(name)(*quals)(**kwquals)

        # The longitude varies linearly with time
        # It is equal to longlat[0] for t=0
        period = 12.0*3600.0                     # orbital period (s)
        period *= sign['direction']
        omega = 2*pi/period                      # rad/s
        longitude = node('longitude') << (longlat[0] + omega*Meq.Time())
        
        # The latitude varies sinusoidally with time
        # It is equal to longlat[1] for t=0 (see phase below)
        inclination = 52.0                       # orbit inclination (degr)
        inclination *= sign['inclination']
        arg = node('latitude')('arg') << (2*pi/period) * Meq.Time()
        ampl = inclination*pi/180                # rad
        phase = node('latitude')('phase') << Meq.Asin(longlat[1]/ampl)
        sinarg = node('latitude')('sinarg') << Meq.Sin(arg+phase)
        latitude = node('latitude') << Meq.Multiply(ampl,sinarg)
        longlat = [longitude,latitude]
        if False:
          longlat = node << Meq.Composer(longitude,latitude)
          display.subtree(longlat)

    elif xyz:
      pass
    else:
      raise ValueError,'specify location either as xyz or as longlat'
    
    GeoLocation.GeoLocation.__init__(self, ns=ns, name=name,
                                     longlat=longlat, radius=radius,
                                     xyz=xyz, 
                                     quals=quals, kwquals=kwquals,
                                     typename='GPSSatellite',
                                     tags=['GeoLocation','GPSSatellite'],
                                     solvable=False)

    # Define the station parameter (simulated or solvable):
    self._pnames = []                     # list of (solvable) MeqParm names
    self._simulate = simulate
    self._stddev = stddev
    pname = 'TEC_bias'
    if self._simulate:
      sp = SimulParm.SimulParm(self.ns, pname, value=0.0, stddev=self._stddev)
      self._add_parm(pname, sp.create(), tags=['GPSSatellite'])
      sp.display()
    else:
      self._add_parm(pname, Meow.Parm(), tags=['GPSSatellite'])
      self._pnames.append(pname)

    # Finished:
    return None

  #------------------------------------------------------------------

  def oneliner (self):
    """Return a one-line summary of this object."""
    ss = self.oneliner_common()
    if self._simulate:
      ss += ' (TEC stddev='+str(self._stddev)+')'
    return ss

  #---------------------------------------------------------------
  
  def TEC_bias (self, show=False):
    """Returns the satellite TEC bias (node)"""
    node = self._parm('TEC_bias')
    self._show_subtree(node, show=show)
    return node

  def solvable(self, tags='*'):
    """Return a list of solvable parms (nodes)"""
    ss = []
    for pname in self._pnames:
      ss.append(self._parm(pname))
    return ss








#================================================================
#================================================================

class GPSPair (Meow.Parameterization):
  """Represents a combination of a GPSStation and GPSSatellite"""
  
  def __init__(self, ns, station, satellite,
               simulate=False, stddev=1.0,
               pair_based_TEC=True,
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

    self._station = station           # its station
    self._satellite = satellite       # its satellite

    # Some extra information:
    self._longlat_pierce = None       # innocent kludge (see .mimTEC())

    # Define the station parameter (simulated or solvable):
    self._pair_based_TEC = pair_based_TEC 
    self._pnames = []                 # list of (solvable) MeqParm names
    self._simulate = simulate
    self._stddev = stddev
    pname = 'TEC_bias'
    if self._pair_based_TEC:          # if 
      if self._simulate:
        sp = SimulParm.SimulParm(self.ns, pname, value=0.0, stddev=self._stddev)
        self._add_parm(pname, sp.create(), tags=['GPSPair'])
        sp.display()
      else:
        self._add_parm(pname, Meow.Parm(), tags=['GPSPair'])
        self._pnames.append(pname)

    # Finished:
    return None

  #---------------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    ss += '  '+str(self.name)
    if self._simulate and self._pair_based_TEC:
      ss += ' (TEC stddev='+str(self._stddev)+')'
    return ss
  

  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * simulate = '+str(self._simulate)+'  (stddev='+str(self._stddev)+')'
    print '  * '+self.station().oneliner()
    print '  * '+self.satellite().oneliner()
    print '  * pair_based_TEC = '+str(self._pair_based_TEC)
    if self._pair_based_TEC:
      print '  * (solvable) pnames: '+str(self._pnames)
      for pname in self._pnames:
        print '    - '+str(self._parm(pname))
    print
    return True


  #---------------------------------------------------------------
  
  def TEC_bias (self, show=False):
    """Returns the station TEC bias (node)"""
    if self._pair_based_TEC:
      node = self._parm('TEC_bias')
    else:
      node = self.ns['TEC_bias']
      if not node.initialized():
        node << Meq.Add(self._station.TEC_bias(),
                        self._satellite.TEC_bias())
    self._station._show_subtree(node, show=show)
    return node


  def solvable(self, tags='*'):
    """Return a list of solvable parms (nodes)"""
    ss = []
    if self._pair_based_TEC:
      for pname in self._pnames:
        ss.append(self._parm(pname))
    else:
      ss.append(self._station.solvable(tags=tags),
                self._satellite.solvable(tags=tags))
    return ss

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
    qnode = None
    return qnode

  #.......................................................

  def mimTEC(self, mim, show=False):
    """Return a node/subtree that produces a simulated TEC value, which
    includes that station- and satellite TEC bias values. It gets its
    information from the given (simulated) MIM object"""
    qnode = self.ns['mimTEC']
    if not qnode.initialized():
      TEC = mim.TEC(self._station, self._satellite)
      self._longlat_pierce = mim._last_longlat_pierce   # innocent kludge
      qnode << Meq.Add(TEC, self._station.TEC_bias(),
                       self._satellite.TEC_bias())
    self._station._show_subtree(qnode, show=show, recurse=8)
    return qnode

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

  def longlat_diff(self, show=False):
    """Return the [longtitude,latitude] difference between
    its station and its satellite"""
    return self._station.longlat_diff(self._satellite, show=show)

  #-------------------------------------------------------

  def zenith_angle(self, show=False):
    """Return the zenith angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    return self._station.zenith_angle(self._satellite, show=show)

  #-------------------------------------------------------

  def elevation(self, show=False):
    """Return the elevation angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    return self._station.elevation(self._satellite, show=show)

  #-------------------------------------------------------

  def azimuth(self, show=False):
    """Return the azimuth angle (node) of its satellite, as seen
    from its station. This is time-dependent, of course."""
    return self._station.azimuth(self._satellite, show=show)

  #-------------------------------------------------------

  def azel (self, show=False):
    """Returns (azimuth,elevation) (tensor node)"""
    qnode = self.ns['azel']
    if not qnode.initialized():
      qnode << Meq.Composer(self.azimuth(),
                            self.elevation())
    self._station._show_subtree(qnode, show=show)
    return qnode

  def azel_complex (self, show=False):
    """Returns azel (node) as complex (az+j*elev), for plotting"""
    qnode = self.ns['azel_complex']
    if not qnode.initialized():
      qnode << Meq.ToComplex(self.azimuth(),
                             self.elevation())
    self._station._show_subtree(qnode, show=show)
    return qnode
      
  def azang_complex (self, show=False):
    """Returns azang (node) as complex (az+j*zang), for plotting"""
    qnode = self.ns['azang_complex']
    if not qnode.initialized():
      qnode << Meq.ToComplex(self.azimuth(),
                             self.zenith_angle())
    self._station._show_subtree(qnode, show=show)
    return qnode
      
  #-------------------------------------------------------
  #-------------------------------------------------------

  def insert_elevation_flagger(self, data, elmin=1.0, show=False):
    """Insert a zero-flagger that flags the vells if the satellite
    elevation is below a specified value (elmin)"""
    name = 'elevation_flagger'
    qnode = self.ns[name]
    if not qnode.initialized():
      elev = self.elevation()
      eldiff = qnode('eldiff') << Meq.Subtract(elmin, elev)
      zerof = qnode('zerof') << Meq.ZeroFlagger(eldiff,
                                               oper='GT',
                                               flag_bit=1)
      qnode << Meq.MergeFlags(data, zerof)
    self._station._show_subtree(qnode, show=show, recurse=4)
    return qnode





#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    st1 = GPSStation(ns, 'st1', longlat=[-0.1,1.0])
    sat1 = GPSSatellite(ns, 'sat1', longlat=[0.1,1.0])

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

    simulate = False

    if 1:
      st1 = GPSStation(ns, 'st1', longlat=[-0.1,1.0],
                       simulate=simulate)
      print st1.oneliner()

      if 1:
        print 'solvable:',st1.solvable()
        print st1.TEC_bias(show=True)

      if 0:
        st1.tensornode(show=True)
        st1.altitude(show=True)
        st1.test_result()

      if 0:
        display.subtree(st1.TEC_bias())

      if 0:
        st1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      sat1 = GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0],
                          move=True, simulate=simulate)
      print sat1.oneliner()

      if 0:
        print 'solvable:',sat1.solvable()
        print sat1.TEC_bias(show=True)


      if 0:
        sat1.tensornode(show=True)

      if 0:
        sat1.altitude(show=True)
        sat1.test_result()

      if 0:
        display.subtree(sat1.TEC_bias())

      if 0:
        sat1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      pair = GPSPair (ns, station=st1, satellite=sat1,
                      simulate=simulate, pair_based_TEC=False)
      pair.display(full=True)

      if 1:
        print 'solvable:',pair.solvable()
        print pair.TEC_bias(show=True)


      if 0:
        pair.elevation(show=True)

      if 0: 
        pair.azimuth(show=True)

      if 0:
        pair.azel(show=True)
        pair.azel_complex(show=True)

      if 0:
        pair.zenith_angle(show=True)

      if 0:
        pair.longlat_diff(show=True)

      if 0:
        pair.solvable(tags='*', show=True)

      if 0:
        data = ns['data'] << Meq.Constant(-56)
        pair.insert_elevation_flagger(data, elmin=1.0, show=True)



    
