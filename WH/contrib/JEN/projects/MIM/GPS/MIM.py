# file ../JEN/projects/MIM/GPS/MIM.py

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

class MIM (Meow.Parameterization):
  """Represents a Minimum Ionospheric Model (MIM)
  as a function of Earth (longitude,latitude) and
  zenith angle."""
  
  def __init__(self, ns, name='MIM',
               quals=[], kwquals={},
               tags=[], solvable=True,
               refloc=None,
               effalt_km=300,
               ndeg=2, simulate=False):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

    # The 'effective altitude' of the ionosphere. It has the dimension of
    # a length (km!), but is just a coupling parameter, which may be solved for.
    # For the moment, it is just a constant
    self._effalt_km = effalt_km

    # The MIM reference location (refloc) is a GeoLocation object.
    # If not specified, use longlat=(0,0), on the Eart surface.
    self._refloc = refloc
    if not isinstance(refloc, GeoLocation.GeoLocation):
      self._refloc = GeoLocation.GeoLocation(self.ns, name='refloc',
                                             longlat=[0,0], radius=None,
                                             tags=['GeoLocation','MIM'],
                                             solvable=False)
    self._Earth = self._refloc._Earth              # copy the Earth dict (radius etc)
      

    # Define the MIM:
    self._ndeg = ndeg
    if isinstance(self._ndeg,int):
      self._ndeg = [ndeg,ndeg]                     # [nlong,nlat]
    if not isinstance(self._ndeg,(list,tuple)):
      s = 'MIM ndeg should be int or list of two ints, rather than: '+str(self._ndeg)
      raise ValueError,s

    self._simulate = simulate
    self._SimulParm = []
    self._solvable = []
    self._pname = []
    self._pnode = []
    self._usedval = dict()
    for i in range(self._ndeg[0]+1):
      for j in range(self._ndeg[1]+1):
        pname = 'p'+str(i)+str(j)
        if not pname in self._pname:               # avoid duplication of diagonal (j=i)
          self._pname.append(pname)
          if self._simulate:
            # Make simulated parms (subtrees) with average value of zero,
            # but with a cosine time-variation with given ampl and period.
            # The latter may be randomized with a given stddev.
            ampl = 1.0/(1.0+i+j)
            ampl = ampl*ampl
            term = dict(ampl=ampl, Psec=1000,
                        stddev=dict(ampl=ampl/10.0, Psec=100))
            sp = SimulParm.SimulParm(ns, pname, value=0.0, term=term)
            self._SimulParm.append(sp)             # SimulParm objects          
            node = sp.create()  
            self._add_parm(pname, node, tags=['MIM'])
            self._usedval[pname] = sp._usedval     # actually used simulation values
          else:
            # Make a regular MeqParm:
            self._add_parm(pname, Meow.Parm(), tags=['MIM'])
            node = self._parm(pname)
            self._solvable.append(node)
          self._pnode.append(node)                 # Parm/SimulParm nodes

      self._pierce_points = []
    return None


  #---------------------------------------------------------------

  def oneliner (self):
    ss = 'MIM: '+str(self.name)
    ss += '  ndeg='+str(self._ndeg)
    ss += '  effalt='+str(int(self._effalt_km))+'km'
    if self._simulate:
      ss += '  (simulated)'
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * refloc: '+self._refloc.oneliner()
    print '  * Earth: '+str(self._Earth)
    print '  * pname: '+str(self._pname)
    print '  * solvable ('+str(len(self._solvable))+'):'
    for k,p in enumerate(self._solvable):
      print '   - '+str(k)+': '+str(p)
    if self._simulate:
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

  #-------------------------------------------------------

  def solvable(self, tags='*'):
    """Return its list of solvable parms (nodes), if any"""
    return self._solvable


  def inspector(self, bookpage='MIM', show=False):
    """Make an inspector for the p-nodes (MeqParms or SimulParms)"""
    if self._simulate:
      name = 'SimulParm'
    else:
      name = 'solvable'
    qnode = self.ns[name]
    if not qnode.initialized():
      qnode << Meq.Composer(children=self._pnode, plot_label=self._pname)
      JEN_bookmarks.create(qnode, page=bookpage,
                           viewer='Collections Plotter')
    if show: display.subtree(qnode)
    return qnode



  #======================================================================
  # The difficult bits.....
  #======================================================================

  def effective_altitude(self):
    """Return the 'effective altitude' (km!) of the ionosphere.
    Since the MIM does NOT assume a thin layer, this is NOT a physical
    altitude, but rather a coupling parameter to relate longlat with z"""
    return self._effalt_km


  #-------------------------------------------------------

  def longlat_pierce_old(self, seenfrom, towards, show=False):
    """Return the longlat (node) of the pierce point through this (MIM) ionsosphere,
    as seen from the given GeoLocation, towards the other (usually a GPS satellite)."""
    name = 'longlat_pierce_old'
    qnode = self.ns[name]     
    qnode = qnode.qmerge(seenfrom.ns['MIM_dummy_qnode'])  
    qnode = qnode.qmerge(towards.ns['MIM_dummy_qnode'])  
    if not qnode.initialized():
      dll = seenfrom.longlat_diff(towards)
      alt_ionos = self.effective_altitude()     # ionospheric coupling parameter (h)....
      alt_satellite = towards.altitude()
      fraction = qnode('fraction') << Meq.Divide(alt_ionos, alt_satellite)
      ll_shift = qnode('dll_pierce') << Meq.Multiply(dll, fraction)
      qnode << Meq.Add(seenfrom.longlat(),ll_shift)
    seenfrom._show_subtree(qnode, show=show, recurse=4)
    self._last_longlat_pierce = qnode           # innocent kludge, read by GPSPair.mimTEC()
    return qnode

  #-------------------------------------------------------

  def longlat_pierce(self, seenfrom, towards, show=False):
    """Return the longlat (node) of the pierce point through this (MIM) ionsosphere,
    as seen from the given GeoLocation, towards the other (usually a GPS satellite).
    xyz_pierce = xyz_station (seenfrom) + fraction * dxyz (satellite - station)
    The fraction is l(z)/magn(dxyz) = (h/cos(z))/magn(dxyz).
    Assuming that the base angle of the triangle through the Earth centre, the station
    and the pierce-point is close enough to 90 degr so that sin(a)~tg(a)~a"""

    name = 'longlat_pierce'
    qnode = self.ns[name]     
    qnode = qnode.qmerge(seenfrom.ns['MIM_dummy_qnode'])  
    qnode = qnode.qmerge(towards.ns['MIM_dummy_qnode'])  
    if not qnode.initialized():
      dxyz = towards.binop('Subtract', seenfrom)    # (dx,dy,dz) from station to satellite
      m = dxyz.magnitude()
      z = seenfrom.zenith_angle(towards)
      cosz = qnode('cosz') << Meq.Cos(z)
      mcos = qnode('mcos') << Meq.Multiply(m,cosz)
      h = self.effective_altitude()                 # ionospheric coupling parameter (h)....
      fraction = qnode('fraction') << Meq.Divide(h, mcos)
      dxyz_fraction = dxyz.binop('Multiply',fraction)     # -> GeoLocation object
      xyz_pierce = seenfrom.binop('Add', dxyz_fraction)  
      qnode = xyz_pierce.longlat()
    seenfrom._show_subtree(qnode, show=show, recurse=4)
    self._last_longlat_pierce = qnode               # innocent kludge, read by GPSPair.mimTEC()
    return qnode




  #======================================================================
  # The main function:
  #======================================================================

  def TEC(self, seenfrom=None, towards=None, show=False):
    """Return a node/subtree that predicts an integrated TEC value,
    as seen from the specified location (seenfrom==GeoLocation or None)
    in the direction of the specified (towards) location. The latter
    may be a GeoLocation object, or None (assume zenith direction).
    It first calculates the (long,lat) of the ionosphere piercing point,
    and the zenith angle (z). Then the vertical (z=0) TEC for the piercing
    (long,lat), which is then multiplied by a function S(z) that corrects
    for the slanted path through the ionosphere. The simplest form of S(z)
    is sec(z)=1/cos(z), but more complicated versions take account of
    the curvature of the Earth. In all cases, S(z=0)=1."""

    name = 'TEC'
    qnode = self.ns[name]                                   

    # Check the first location (if any):
    if seenfrom==None:
      qnode = qnode('refloc')
      ll_from = self._refloc.longlat()
    elif isinstance(seenfrom, GeoLocation.GeoLocation):
      qnode = qnode.qmerge(seenfrom.ns['MIM_dummy_qnode'])  
      ll_from = seenfrom.longlat()
    else:
      s = 'MIM.TEC(): from should be a GeoLocation, not: '+str(type(seenfrom))
      raise ValueError,s

    # Check the second location (if any):
    if towards==None:
      # Assume zenith direction:
      qnode = qnode('zenith')
      ll_piercing = None
      z = None
    elif isinstance(towards, GeoLocation.GeoLocation):
      qnode = qnode.qmerge(towards.ns['MIM_dummy_qnode'])  
      ll_piercing = self.longlat_pierce(seenfrom, towards)
      z = seenfrom.zenith_angle(towards)
    else:
      s = 'MIM.TEC(): towards should be a GeoLocation, not: '+str(type(towards))
      raise ValueError,s


    # Only if not yet initialized:
    if not qnode.initialized():
      if ll_piercing:
        dlonglat = qnode('dlonglat') << Meq.Subtract(ll_piercing, ll_from)
        dlong1 = qnode('dlong') << Meq.Selector(dlonglat, index=0)
        dlat1 = qnode('dlat') << Meq.Selector(dlonglat, index=1)
      else:
        dlong1 = qnode('dlong') << Meq.Constant(0.0)
        dlat1 = qnode('dlat') << Meq.Constant(0.0)
        
      # First make powers of dlong/dlat (relative to self._refloc)
      llong = [None, dlong1]
      llat = [None, dlat1]
      for k in range(2,self._ndeg[0]+1):
        llong.append(qnode('long^'+str(k)) << Meq.Multiply(llong[k-1],dlong1))
      for k in range(2,self._ndeg[1]+1):
        llat.append(qnode('lat^'+str(k)) << Meq.Multiply(llat[k-1],dlat1))

      # Then make the various MIM polynomial terms:
      cc = []
      for pname in self._pname:
        i = int(pname[1])
        j = int(pname[2])
        p = self._parm(pname)
        tname = 'term'+pname[1:3]
        if i>0 and j>0:
          n = qnode(tname) << Meq.Multiply(p,llong[i],llat[j])
        elif i>0:
          n = qnode(tname) << Meq.Multiply(p,llong[i])
        elif j>0:
          n = qnode(tname) << Meq.Multiply(p,llat[j])
        else:
          n = qnode(tname) << Meq.Identity(p)
        cc.append(n)

      # Finally, add the polynomial terms, and multiply the result with
      # the ionospheric slant-function S(z), if required:
      if z==None:
        qnode << Meq.Add(children=cc)                  # zenith direction (z=0)
      else:                                          
        TEC0 = qnode('z=0') << Meq.Add(children=cc)    # zenith direction (z=0)
        sz = self.slant_function(qnode('slant'), z=z)
        qnode << Meq.Multiply(TEC0, sz)                # TEC0*sec(z')
          
    # Finished:
    if show:
      display.subtree(qnode, recurse=4, show_initrec=False)
    return qnode

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
    



#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    mim = MIM(ns)
    mim.display(full=True)
    # cc.append(mim.inspector())

    if 1:
      sim = MIM(ns, 'simul', ndeg=1, simulate=True)
      sim.display(full=True)
      cc.append(sim.inspector())
      cc.append(sim.visualize())


    if False:
      st1 = GPSStation(ns,'st1', pos1)
      sat1 = GPSSatellite(ns,'sat1', x=pos2[0], y=pos2[1], z=pos2[2])
      pair = GPSPair (ns, station=st1, satellite=sat1)
      pair.display(full=True)
      cc.append(zang)

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


    mim = MIM(ns)
    mim.display(full=True)

    if 1:
      sim = MIM(ns, ndeg=1, simulate=True)
      sim.display(full=True)

      if 0:
        sim.TEC(show=True)

      if 0:
        sim.inspector(show=True)
      

    #-----------------------------------------------------------------------

    if 1:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,1.0])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0])

      if 1:
        sim.longlat_pierce(st1, sat1, show=True)

      if 0:
        qnode = ns.qnode('xxx')
        sim.slant_function(qnode, z=1, flat_Earth=True, show=True)

      if 0:
        sim.TEC(st1, sat1, show=True)
        # sim.TEC(st1, show=True)
        # sim.TEC(show=True)


      if 0:
        pair = GPSPair.GPSPair (ns, station=st1, satellite=sat1)
        pair.display(full=True)

        if 1:
          pair.mimTEC(sim, show=True)

      

      
#===============================================================

