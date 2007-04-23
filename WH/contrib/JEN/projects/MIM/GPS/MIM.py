# file ../JEN/projects/MIM/GPS/MIM.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair
import IonosphereModel

from Timba.Contrib.JEN.Vector import GeoLocation
from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.util import JEN_bookmarks
from numarray import *

Settings.forest_state.cache_policy = 100



#================================================================

class MIM (IonosphereModel.IonosphereModel):
  """Represents a Minimum Ionospheric Model (MIM)
  as a function of Earth (longitude,latitude) and
  zenith angle."""
  
  def __init__(self, ns, name='MIM',
               quals=[], kwquals={},
               tags=[],
               # solvable=True,
               tiling=None,
               time_deg=0,
               refloc=None,
               effalt_km=300,
               ndeg=2, simulate=False):

    IonosphereModel.IonosphereModel.__init__(self, ns, name,
                                             refloc=refloc,
                                             effalt_km=effalt_km,
                                             quals=quals, kwquals=kwquals)

    #-------------------------------------------------
    # Define the MIM:
    self._ndeg = ndeg
    if isinstance(self._ndeg,int):
      self._ndeg = [ndeg,ndeg]                     # [nlong,nlat]
    if not isinstance(self._ndeg,(list,tuple)):
      s = 'MIM ndeg should be int or list of two ints, rather than: '+str(self._ndeg)
      raise ValueError,s

    self._simulate = simulate
    self._SimulParm = []
    ss = dict(nodes=[], labels=[])                 # for self._solvable
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
            atij = 1.0/(1.0+i+j)                   # attenuation factor
            ampl = (atij*atij)                     # time variation amplitude
            phase = 0.0                            # time variation phase (rad) 
            # phase = (i+j)*(pi/2)                                # <----!?
            term = dict(ampl=ampl, Psec=1000, phase=phase,
                        stddev=dict(ampl=ampl/10.0, Psec=100))
            sp = SimulParm.SimulParm(ns, pname, value=0.0, term=term)
            self._SimulParm.append(sp)             # SimulParm objects          
            node = sp.create()  
            self._add_parm(pname, node, tags=['MIM'])
            self._usedval[pname] = sp._usedval     # actually used simulation values

          else:
            # Make a regular MeqParm, using Meow.Parm():
            # parm = Meow.Parm()
            # tiling = dmi.record(time=2, freq=4)
            # tiling = 1                             # assumes time
            parm = Meow.Parm(value=0, tags=[], time_deg=time_deg, tiling=tiling)
            self._add_parm(pname, parm, tags=['MIM'])
            node = self._parm(pname)
            ss['nodes'].append(node)               # for self._solvable
            ss['labels'].append(pname)             # for self._solvable
          self._pnode.append(node)                 # Parm/SimulParm nodes
      self._solvable = ss

    # Finished:
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
    print '  * solvable ('+str(len(self._solvable['nodes']))+'):'
    ss = self._solvable
    for k,node in enumerate(ss['nodes']):
      print '   - '+str(ss['labels'][k])+': '+str(node)
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






  #======================================================================
  # Return a subtree for the MIM TEC as seen from a GeoLocation on Earth
  # towards a GPS satellite (another GeoLocation). This subtree is NOT
  # suitable for calculating the MIM in the direction of a celestial source.
  #======================================================================


  def _geoTEC(self, qnode, seenfrom=None, towards=None,
              ll_seenfrom=None, ll_piercing=None, z=0.0):
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

    # OK, create the geoMIM subtree (if required)
    if not qnode.initialized():
      if ll_piercing:
        dlonglat = qnode('dlonglat') << Meq.Subtract(ll_piercing,
                                                     ll_seenfrom)
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
    return True






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    mim = MIM(ns, 'mim')
    mim.display(full=True)
    cc.append(mim.inspector())

    if 1:
      sim = MIM(ns, 'sim', ndeg=1, simulate=True)
      sim.display(full=True)
      cc.append(sim.inspector())


    if 1:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,0.1])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[0.1,0.1])

      if 0:
        cc.append(sim.longlat_pierce(st1, sat1, show=True))

      if 0:
        qnode = ns.qnode('xxx')
        cc.append(sim.slant_function(qnode, z=1, flat_Earth=True, show=True))

      if 0:
        cc.append(sim.geoTEC(st1, sat1, show=True))
        # cc.append(sim.geoTEC(st1, show=True))
        # cc.append(sim.geoTEC(show=True))

      if 1:
        pair = GPSPair.GPSPair(ns, station=st1, satellite=sat1)
        pair.display(full=True)
        if 0:
          cc.append(pair.mimTEC(sim, show=True))
        if 1:
          cc.append(pair.simTEC(sim, show=True))

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


    mim = MIM(ns, 'mim')
    mim.display(full=True)

    if 1:
      sim = MIM(ns, 'sim', ndeg=1, simulate=True)
      sim.display(full=True)

      if 0:
        sim.geoTEC(show=True)

      if 0:
        sim.inspector(show=True)
      

    #-----------------------------------------------------------------------

    if 1:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,1.0])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0])

      if 0:
        sim.longlat_pierce(st1, sat1, show=True)

      if 0:
        qnode = ns.qnode('xxx')
        sim.slant_function(qnode, z=1, flat_Earth=True, show=True)

      if 1:
        sim.geoTEC(st1, sat1, show=True)
        # sim.geoTEC(st1, show=True)
        # sim.geoTEC(show=True)


      if 0:
        pair = GPSPair.GPSPair (ns, station=st1, satellite=sat1)
        pair.display(full=True)

        if 1:
          pair.mimTEC(sim, show=True)

      

      
#===============================================================

