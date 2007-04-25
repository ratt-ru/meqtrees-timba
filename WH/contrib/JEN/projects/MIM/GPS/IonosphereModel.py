# file ../JEN/projects/MIM/GPS/IonosphereModel.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair

from Timba.Contrib.JEN.Vector import GeoLocation
from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.util import JEN_bookmarks
from numarray import *

Settings.forest_state.cache_policy = 100



#================================================================

class IonosphereModel (Meow.Parameterization):
  """Baseclass for various ionospheric models (IOM, e.g. see MIM.py)
  defined in terms of Earth (longitude,latitude)"""
  
  def __init__(self, ns, name='IonosphereModel',
               quals=[], kwquals={},
               simulate=False,
               refloc=None, effalt_km=300):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

    # The 'effective altitude' of the ionosphere. It has the dimension of
    # a length (km!), but is just a coupling parameter, which may be solved for.
    # For the moment, it is just a constant
    self._effalt_km = effalt_km

    # The IonosphereModel reference location (refloc) is a GeoLocation object.
    # If not specified, use longlat=(0,0), on the Eart surface.
    self._refloc = refloc
    if not isinstance(refloc, GeoLocation.GeoLocation):
      self._refloc = GeoLocation.GeoLocation(self.ns, name='refloc',
                                             longlat=[0,0], radius=None,
                                             tags=['GeoLocation','IonosphereModel'],
                                             solvable=False)
    self._Earth = self._refloc._Earth              # copy the Earth dict (radius etc)

    # This is returned by the function .is_simulated()
    self._simulate = simulate

    # Some extra info:
    self._pierce_points = []                       # an innocent kludge

    #-------------------------------------------------
    # Define the IonosphereModel:
    self._solvable = dict(nodes=[], labels=[])     # expected by .solvable()
    self._pnode = []                               # expected by .inspector()
    self._pname = []                               # expected by .inspector()
    self._SimulParm = []
    self._usedval = dict()
    #-------------------------------------------------

    # Finished:
    return None


  #---------------------------------------------------------------

  def oneliner (self):
    ss = 'IonosphereModel: '+str(self.name)
    ss += '  effalt='+str(int(self._effalt_km))+'km'
    if self.is_simulated():
      ss += '  (simulated)'
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * refloc: '+self._refloc.oneliner()
    print '  * Earth: '+str(self._Earth)
    print '  * pname: '+str(self._pname)
    print '  * solvable ('+str(len(self._solvable['nodes']))+'):'
    ss = self._solvable
    for k,node in enumerate(ss['nodes']):
      print '   - '+str(ss['labels'][k])+': '+str(node)
    if self.is_simulated():
      print '  * SimulParm ('+str(len(self._SimulParm))+'):'
      for k,sp in enumerate(self._SimulParm):
        print '   - '+str(k)+': '+sp.oneliner()
      for k,p in enumerate(self._pnode):
        print '   - '+str(k)+': '+str(p)
      print '  * Actually used simulation values:'
      for key in self._pname:
        if self._usedval.has_key(key):
          print '   - '+str(key)+': '+str(self._usedval[key])
    print
    return True


  #---------------------------------------------------------------

  def is_simulated(self):
    """True if the object has SimulParm subtrees, rather than MeqParms.
    The latter are potentially solvable"""
    return self._simulate

  #----------------------------------------------------------------

  def solvable(self, tags='*', show=False):
    """Return a dict of solvable parms (nodes), and their labels"""
    if show:
      ss = self._solvable
      print '\n** solvable MeqParms of:',self.oneliner()
      for k,node in enumerate(ss['nodes']):
        print '  -',ss['labels'][k],': ',str(node)
      print
    return self._solvable

  #-----------------------------------------------------------------

  def plot_parms(self, bookpage='IonosphereModel', show=False):
    """Make an 'inspector' subtree for the IOM parameter nodes
    (MeqParms or SimulParms)"""
    if self.is_simulated():
      name = 'SimulParm'
    else:
      name = 'solvable'
    qnode = self.ns[name]
    if not qnode.initialized():
      if len(self._pnode)==0:                         # nothing to plot
        qnode << Meq.Constant(-1)                     # return a dummy node
      else:
        qnode << Meq.Composer(children=self._pnode,
                              plot_label=self._pname)
        JEN_bookmarks.create(qnode, page=bookpage,
                             viewer='Collections Plotter')
    if show:
      display.subtree(qnode)
    return qnode



  #====================================================================
  # Functions depending on the 'effective altitude' of the ionosphere
  #====================================================================

  def effective_altitude(self):
    """Return the 'effective altitude' (km!) of the ionosphere.
    Since the IonosphereModel does NOT assume a thin layer, this is NOT a physical
    altitude, but rather a coupling parameter to relate longlat with z"""
    return self._effalt_km

  #--------------------------------------------------------------------

  def slant_function(self, qnode, z=None, flat_Earth=False, show=False):
    """Helper function to calculate the ionospheric slant-function S(z),
    i.e. the function that indicates how much longer the path through the
    ionosphere is as a function of zenith angle(z).
    The simplest (flat-Earth) form of S(z) is sec(z)=1/cos(z), but more
    complicated versions take account of the curvature of the Earth.
    In all cases, S(z=0)=1."""

    if flat_Earth:
      cosz = qnode('cosz') << Meq.Cos(z)

    else:
      R = self._Earth['radius']                             # km
      h = self.effective_altitude()                         # km
      Rh = qnode('R/(R+h)') << Meq.Divide(R,R+h)
      sinz = qnode('sinz') << Meq.Sin(z)
      Rhsin = qnode('Rhsinz') << Meq.Multiply(Rh,sinz)
      asin = qnode('asin') << Meq.Asin(Rhsin)
      cosz = qnode('cosasin') << Meq.Cos(asin)

    # S(z') = sec(z') = 1/cos(z')
    sz = qnode('Sz') << Meq.Divide(1.0,cosz)

    if show: 
      display.subtree(sz, recurse=4, show_initrec=False)
    return sz
   
  #-------------------------------------------------------------------------------
  
  def longlat_pierce(self, seenfrom, towards, show=False):
    """Return the longlat (node) of the pierce point through this (IonosphereModel) ionsosphere,
    as seen from the given GeoLocation, towards the other (usually a GPS satellite).
    xyz_pierce = xyz_station (seenfrom) + fraction * dxyz (satellite - station)
    The fraction is l(z)/magn(dxyz) = (h/cos(z))/magn(dxyz).
    Assuming that Earth radius is so much greater than h that the max angle between
    station position and pierce position (as seen from the Earth centre) is so small
    that sin(a)~tg(a)~a"""

    name = 'longlat_pierce'
    qnode = self.ns[name]
    qnode = qnode.qmerge(seenfrom.ns['IonosphereModel_dummy_qnode'])  
    qnode = qnode.qmerge(towards.ns['IonosphereModel_dummy_qnode'])  
    if not qnode.initialized():
      dxyz = towards.binop('Subtract', seenfrom)    # (dx,dy,dz) from station to satellite
      m = dxyz.magnitude()
      z = seenfrom.zenith_angle(towards)
      cosz = qnode('cosz') << Meq.Cos(z)
      mcos = qnode('mcos') << Meq.Multiply(m,cosz)
      h = self.effective_altitude()                 # ionospheric coupling parameter (h)....
      fraction = qnode('fraction') << Meq.Divide(h, mcos)
      dxyz_fraction = dxyz.binop('Multiply',fraction)     # -> GeoLocation object
      xyz_pierce = seenfrom.binop('Add', dxyz_fraction)   # -> GeoLocation object  
      qnode << Meq.Identity(xyz_pierce.longlat())
    seenfrom._show_subtree(qnode, show=show, recurse=4)
    self._last_longlat_pierce = qnode               # innocent kludge, read by GPSPair.mimTEC()
    return qnode

 



  #======================================================================
  # Return a subtree for the IonosphereModel TEC as seen from a GeoLocation
  # on Earth, towards a GPS satellite (another GeoLocation). This subtree is
  # NOT suitable for calculating the IonosphereModel in the direction of a
  # celestial source.
  #======================================================================


  def geoTEC(self, seenfrom=None, towards=None, show=False):
    """Return a node/subtree that predicts an integrated TEC value,
    as seen from the specified location (seenfrom==GeoLocation or None)
    in the direction of the specified (towards) location. The latter
    may be a GeoLocation object, or None (assume zenith direction).
    NB: This is just a front-end function, which is common to various
    classes that are derived from this one. It calls the specific function
    ._geoTEC(), which must be implemented in each derived class. 
    """

    qnode = self.ns['geoTEC']                                   

    # Check the first location (if any):
    if seenfrom==None:
      qnode = qnode('refloc')
      ll_seenfrom = self._refloc.longlat()
    elif isinstance(seenfrom, GeoLocation.GeoLocation):
      qnode = qnode.qmerge(seenfrom.ns['IonosphereModel_dummy_qnode'])  
      ll_seenfrom = seenfrom.longlat()
    else:
      s = '.geoTEC(): from should be a GeoLocation, not: '+str(type(seenfrom))
      raise ValueError,s

    # Check the second location (if any):
    if towards==None:
      # Assume zenith direction:
      qnode = qnode('zenith')
      ll_piercing = None
      z = None
    elif isinstance(towards, GeoLocation.GeoLocation):
      qnode = qnode.qmerge(towards.ns['IonosphereModel_dummy_qnode'])  
      ll_piercing = self.longlat_pierce(seenfrom, towards)
      z = seenfrom.zenith_angle(towards)
    else:
      s = '.geoTEC(): towards should be a GeoLocation, not: '+str(type(towards))
      raise ValueError,s

    # Call the function that does the actual work:
    self._geoTEC(qnode, seenfrom=seenfrom, towards=towards,
                 ll_seenfrom=ll_seenfrom, ll_piercing=ll_piercing, z=z)

    # Finished:
    if show:
      display.subtree(qnode, recurse=4, show_initrec=False)
    return qnode


  #--------------------------------------------------------------------------

  def _geoTEC(self, qnode, seenfrom=None, towards=None,
              ll_seenfrom=None, ll_piercing=None, z=0.0):
    """NB: This is a placeholder dummy function, which should be
    re-implemented by each ionosphere model that is derived from
    this class (see MIM.py).
    -------------------------------------------------------------------
    Return a node/subtree that predicts an integrated TEC value,
    as seen from the specified location (seenfrom==GeoLocation or None)
    in the direction of the specified (towards) location. The latter
    may be a GeoLocation object, or None (assume zenith direction).
    It first calculates the (long,lat) of the ionosphere piercing point,
    and the zenith angle (z). Then the vertical (z=0) TEC for the piercing
    (long,lat), which is then multiplied by a function S(z) that corrects
    for the slanted path through the ionosphere. The simplest form of S(z)
    is sec(z)=1/cos(z), but more complicated versions take account of
    the curvature of the Earth. In all cases, S(z=0)=1."""

    if not qnode.initialized():
      # First calculate (dlong,dlat) of the ionospheric pierce location
      # relative to the viewing location on Earth (seenfrom):
      if ll_piercing:
        dlonglat = qnode('dlonglat') << Meq.Subtract(ll_piercing,
                                                     ll_seenfrom)
        dlong = qnode('dlong') << Meq.Selector(dlonglat, index=0)
        dlat = qnode('dlat') << Meq.Selector(dlonglat, index=1)
      else:
        dlong = qnode('dlong') << Meq.Constant(0.0)
        dlat = qnode('dlat') << Meq.Constant(0.0)
        
      # Make a dummy 'TEC' by making a complex number from (dlong,dlat),
      # Multiply the result with the ionospheric slant-function S(z), if required.
      if z==None:
        qnode << Meq.ToComplex(dlong,dlat)             # zenith direction (z=0)
      else:                                          
        TEC0 = qnode('z=0') << Meq.ToComplex(dlong,dlat) # zenith direction (z=0)
        sz = self.slant_function(qnode('slant'), z=z)
        qnode << Meq.Multiply(TEC0, sz)                # TEC0*sec(z')
          
    # Finished:
    return True


  #===============================================================================

  def geoSz (self, seenfrom=None, towards=None, show=False):
    """Return a node/subtree that predicts the slant-function S(z),
    as seen from the specified location (seenfrom==GeoLocation or None)
    in the direction of the specified (towards) location. The latter
    may be a GeoLocation object, or None (assume zenith direction)."""

    qnode = self.ns['geoSz']                                   

    # Check the first location (if any):
    if seenfrom==None:
      qnode = qnode('refloc')
    elif isinstance(seenfrom, GeoLocation.GeoLocation):
      qnode = qnode.qmerge(seenfrom.ns['IonosphereModel_dummy_qnode'])  
    else:
      s = '.geoTEC(): from should be a GeoLocation, not: '+str(type(seenfrom))
      raise ValueError,s

    # Check the second location (if any):
    if towards==None:
      # Assume zenith direction:
      qnode = qnode('zenith')
      z = None
    elif isinstance(towards, GeoLocation.GeoLocation):
      qnode = qnode.qmerge(towards.ns['IonosphereModel_dummy_qnode'])  
      z = seenfrom.zenith_angle(towards)
    else:
      s = '.geoTEC(): towards should be a GeoLocation, not: '+str(type(towards))
      raise ValueError,s

    # Make the node itself, if required:
    if not qnode.initialized():
      if z==None:
        qnode << Meq.Constant(1.0)                     # zenith direction (z=0)
      else:                                          
        sz0 = qnode('z=0') << Meq.Constant(1.0)        # zenith direction (z=0)
        sz = self.slant_function(qnode('slant'), z=z)
        qnode << Meq.Multiply(sz0, sz)                 # TEC0*sec(z')
          
    # Finished:
    if show:
      display.subtree(qnode, recurse=10, show_initrec=True)
    return qnode



#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    iom = IonosphereModel(ns, 'iom')
    iom.display(full=True)
    cc.append(iom.plot_parms())


    if 1:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,0.1])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[0.1,0.1])

      if 1:
        cc.append(iom.longlat_pierce(st1, sat1, show=True))

      if 1:
        qnode = ns.qnode('xxx')
        cc.append(iom.slant_function(qnode, z=1, flat_Earth=True, show=True))

      if 1:
        cc.append(iom.geoTEC(st1, sat1, show=True))
        # cc.append(iom.geoTEC(st1, show=True))
        # cc.append(iom.geoTEC(show=True))



      if 1:
        pair = GPSPair.GPSPair(ns, station=st1, satellite=sat1)
        pair.display(full=True)
        if 1:
          cc.append(pair.modelTEC(iom, sim=True, show=True))
        if 1:
          cc.append(pair.modelTEC(iom, sim=False, show=True))

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       

#================================================================
# Test program
#================================================================
    
if __name__ == '__main__':
    """Test program"""
    ns = NodeScope()

    if 1:
      iom = IonosphereModel(ns, 'iom')
      iom.display(full=True)

      if 0:
        iom.geoTEC(show=True)

      if 0:
        iom.geoSz(show=True)

      if 0:
        iom.plot_parms(show=True)
      


    #-----------------------------------------------------------------------

    if 1:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,1.0])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0])
      print st1.oneliner()
      print sat1.oneliner()

      if 0:
        iom.longlat_pierce(st1, sat1, show=True)

      if 0:
        qnode = ns.qnode('xxx')
        iom.slant_function(qnode, z=1, flat_Earth=True, show=True)

      if 0:
        iom.geoTEC(st1, sat1, show=True)
        # iom.geoTEC(st1, show=True)
        # iom.geoTEC(show=True)

      if 1:
        iom.geoSz(st1, sat1, show=True)

      if 0:
        pair = GPSPair.GPSPair (ns, station=st1, satellite=sat1)
        pair.display(full=True)

        if 1:
          pair.modelTEC(iom, show=True)

      

      
#===============================================================

