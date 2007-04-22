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

class TecBias (Meow.Parameterization):
  """Represents a TEC bias value (MeqParm and/or simulated).
  This class is used by GPSStation, GPSSatellite and GPSPair."""

  def __init__(self, ns, name, tags=[],
               simul=dict(value=0.0, stddev=1.0),
               quals=[],kwquals={}):

    Meow.Parameterization.__init__(self, ns=ns, name=name,
                                   quals=quals, kwquals=kwquals)

    self._tags = tags
    
    # The only parameter is the TecBias.
    self._pname = 'TecBias'
    self._pnames = [self._pname]
    self._add_parm(self._pname, Meow.Parm(), tags=self._tags)

    # The TecBias has a simulated version, which is created if necessary.
    self._simulated = None     # its simulation subtree
    ss = simul                 # dict with simulation parameters
    if not isinstance(ss, dict): ss = dict()
    ss.setdefault('value', 0.0)
    ss.setdefault('stddev', 1.0)
    self._simul = ss

    # Finished:
    return None

  #------------------------------------------------------------------

  def oneliner (self):
    """Return a one-line summary of this object."""
    stddev = self._simul['stddev']
    ss = 'TecBias: '+str(self.name)
    ss += ' tags='+str(self._tags)
    ss += ' (stddev='+str(stddev)+')'
    return ss


  #---------------------------------------------------------------
  
  def node (self, sim=False, show=False):
    """Returns the station TEC bias (node). If sim==True, return the
    subtree for the simulated value. Otherwise, a MeqParm."""
    if sim:
      if not self._simulated:        # create if necessary
        sp = SimulParm.SimulParm(self.ns, self._pname,
                                 tags=self._tags,
                                 value=self._simul['value'],
                                 stddev=self._simul['stddev'])
        self._simulated = sp.create()
      node = self._simulated
    else:
      node = self._parm(self._pname)
    if show:
      display.subtree(node)
    return node

  #---------------------------------------------------------------

  def residual (self, show=False):
    """Returns a subtree with the difference of the simulated and the
    MeqParm version of TecBias. For plotting and other diagnostics."""
    qnode = self.ns['TecBias_residual']
    if not qnode.initialized():
      qnode << Meq.Subtract(self.node(sim=False),
                            self.node(sim=True))
    if show:
      display.subtree(qnode)
    return qnode

  #---------------------------------------------------------------

  def solvable(self, tags='*'):
    """Return a dict of solvable parms (nodes) and their (plot) labels"""
    ss = dict(nodes=[], labels=[])
    for pname in self._pnames:
      # ss['labels'].append(pname+'_'+str(self.name))
      ss['labels'].append(str(self.name))
      ss['nodes'].append(self._parm(pname))
    return ss







#=========================================================================

class GPSStation (GeoLocation.GeoLocation):
  """Represents a GPS station that measures TEC values"""

  def __init__(self, ns, name, longlat=None,
               simul=dict(value=0.0, stddev=1.0),
               quals=[],kwquals={}):

    GeoLocation.GeoLocation.__init__(self, ns=ns, name=name,
                                     longlat=longlat, radius=None,
                                     quals=quals, kwquals=kwquals,
                                     typename='GPSStation',
                                     tags=['GeoLocation','GPSStation'],
                                     solvable=False)

    # The only parameter is the TecBias.
    self.TecBias = TecBias(ns, name,
                           quals=quals, kwquals=kwquals,
                           tags=['GPSStation'],
                           simul=simul)

    # Finished:
    return None

  #------------------------------------------------------------------

  def oneliner (self):
    """Return a one-line summary of this object."""
    ss = self.oneliner_common()
    ss += '  '+self.TecBias.oneliner()
    return ss

  #------------------------------------------------------------------

  def solvable(self, tags='*'):
    """Return a dict of solvable parms (nodes) and their (plot) labels"""
    return self.TecBias.solvable(tags=tags)



#================================================================
#================================================================

# 

class GPSSatellite (GeoLocation.GeoLocation):
  """Represents a GPS satellite"""


  def __init__(self, ns, name, xyz=None, longlat=None, 
               move=False, sign=dict(direction=1,inclination=1),
               simul=dict(stddev=1.0),
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

    # The only parameter is the TecBias.
    self.TecBias = TecBias(ns, name,
                           quals=quals, kwquals=kwquals,
                           tags=['GPSSatellite'],
                           simul=simul)

    # Finished:
    return None

  #------------------------------------------------------------------

  def oneliner (self):
    """Return a one-line summary of this object."""
    ss = self.oneliner_common()
    ss += '  '+self.TecBias.oneliner()
    return ss

  #------------------------------------------------------------------

  def solvable(self, tags='*'):
    """Return a dict of solvable parms (nodes) and their (plot) labels"""
    return self.TecBias.solvable(tags=tags)






#================================================================
#================================================================

class GPSPair (Meow.Parameterization):
  """Represents a combination of a GPSStation and GPSSatellite"""
  
  def __init__(self, ns, station, satellite,
               simul=dict(stddev=1.0),
               pair_based_TecBias=True,
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

    # Define the pair parameter (simulated or solvable):
    self._pair_based_TecBias = pair_based_TecBias 
    self.TecBias = TecBias(ns, name,
                           quals=quals, kwquals=kwquals,
                           tags=['GPSPair'],
                           simul=simul)

    # Finished:
    return None

  #---------------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    ss = 'GPSPair:'
    ss += '  '+str(self.name)
    ss += '  '+self.TecBias.oneliner()
    return ss
  

  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    # print '  * simul = '+str(self._simul)
    print '  * '+self.station().oneliner()
    print '  * '+self.satellite().oneliner()
    print '  * pair_based_TecBias = '+str(self._pair_based_TecBias)
    print '  * solvable:'
    ss = self.solvable()
    for k,node in enumerate(ss['nodes']):
      print '    -',ss['labels'][k],': ',str(node)
    print '**\n'
    return True


  #---------------------------------------------------------------
  
  def TEC_bias (self, sim=False, show=False):
    """Returns the combined TEC bias (node) of this pair"""
    if self._pair_based_TecBias:
      node = self.TecBias.node(sim=sim)
    else:
      node = self.ns['TecBias']
      if not node.initialized():
        node << Meq.Add(self._station.TecBias(sim=sim),
                        self._satellite.TecBias(sim=sim))
    self._station._show_subtree(node, show=show)
    return node


  #-------------------------------------------------------

  def station(self):
    """Return its station object"""
    return self._station

  def satellite(self):
    """Return its satellite object"""
    return self._satellite

  #-------------------------------------------------------

  def solvable(self, tags='*', show=False):
    """Return a list of solvable parms (nodes)"""
    ss = dict(nodes=[], labels=[])
    if self._pair_based_TecBias:
      ss = self.TecBias.solvable(tags=tags)
    else:
      for ss1 in [self._station.solvable(tags=tags),
                  self._satellite.solvable(tags=tags)]:
        for key in ss.keys():
          ss[key].extend(ss1[key])
    if show:
      print '\n** .solvable(tags=',tags,') <-',self.oneliner()
      for k,node in enumerate(ss['nodes']):
        print '    -',ss['labels'][k],': ',str(node)
      print
    return ss

  #=================================================================

  def gpsTEC(self):
    """Return a node/subtree that produces a measured TEC value for
    a specified time-range (in the request). It gets its information
    from external GPS data in a file or something."""
    qnode = None          # ..... not yet implemented .....
    return qnode



  #=================================================================

  def simTEC(self, mim, show=False):
    """Special version of mimTEC() that uses the simulated value
    for the TecBias (rather than MeqParms"""
    return self.mimTEC(mim, sim=True, show=show)


  def mimTEC(self, mim, sim=False, show=False):
    """Return a node/subtree that produces a simulated TEC value, which
    includes that station- and satellite TEC bias values. It gets its
    information from the given (simulated) MIM object"""
    qnode = self.ns['mimTEC']
    qnode = qnode.qmerge(mim.ns['GPSPair_dummy_qnode'])
    if not qnode.initialized():
      # First get a subtree for the MIM TEC:
      TEC = mim.geoTEC(self._station, self._satellite)
      self._retrieve_last_longlat_pierce_for_plotting(mim)
      # Then add the TecBias for this station-satellite pair:
      qnode << Meq.Add(TEC, self.TEC_bias(sim=sim))
    self._station._show_subtree(qnode, show=show, recurse=8)
    return qnode


  def _retrieve_last_longlat_pierce_for_plotting(self, mim):
    """Helper function for retrieving the (long,lat) of the
    ionospheric piercing point that was calculated by the last
    call to mim.geoTEC(). This can be used for plotting (see
    GPSArray.py). It is a bit of a kludge, but useful and innocent"""
    return True

  #=================================================================

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
      
  #=================================================================

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

    if 0:
      tb = TecBias(ns, 'tb',
                   tags=['GPSElement'],
                   simul=dict(stddev=1.0))
      print tb.oneliner()

      if 1:
        print 'tb.solvable:',tb.solvable()

      if 1:
        print tb.node(sim=False, show=True)
        print tb.node(sim=True, show=True)
        print tb.residual(show=True)


    #----------------------------------------------------
        
    if 1:
      st1 = GPSStation(ns, 'st1', longlat=[-0.1,1.0],
                       simul=dict(stddev=1.0))
      print st1.oneliner()

      if 0:
        print 'solvable:',st1.solvable()

      if 0:
        print st1.TecBias.node(sim=False, show=True)
        print st1.TecBias.node(sim=True, show=True)
        print st1.TecBias.residual(show=True)

      if 0:
        st1.tensornode(show=True)
        st1.altitude(show=True)
        st1.test_result()

      if 0:
        st1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      sat1 = GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0],
                          move=True,
                          simul=dict(stddev=1.0))
      print sat1.oneliner()

      if 0:
        print 'solvable:',sat1.solvable()

      if 0:
        print sat1.TecBias.node(sim=False, show=True)
        print sat1.TecBias.node(sim=True, show=True)
        print sat1.TecBias.residual(show=True)


      if 0:
        sat1.tensornode(show=True)

      if 0:
        sat1.altitude(show=True)
        sat1.test_result()

      if 0:
        display.subtree(sat1.TecBias())

      if 0:
        sat1.longlat(show=True)

    #-------------------------------------------------------

    if 1:
      pair = GPSPair (ns, station=st1, satellite=sat1,
                      simul=dict(stddev=1.0),
                      pair_based_TecBias=True)
      pair.display(full=True)

      if 1:
        print 'solvable:',pair.solvable(show=True)

      if 1:
        print pair.TEC_bias(sim=True, show=True)
        print pair.TEC_bias(sim=False, show=True)

      if 0:
        print pair.TecBias.node(sim=True, show=True)
        print pair.TecBias.node(sim=False, show=True)
        print pair.TecBias.residual(show=True)


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



    
