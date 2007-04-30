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
               tiling=None,
               time_deg=0,
               refloc=None,
               effalt_km=300,
               ndeg=2, simulate=False):

    IonosphereModel.IonosphereModel.__init__(self, ns, name,
                                             refloc=refloc,
                                             effalt_km=effalt_km,
                                             simulate=simulate,
                                             quals=quals, kwquals=kwquals)

    #-------------------------------------------------
    # Define the MIM:
    self._ndeg = ndeg
    if isinstance(self._ndeg,int):
      self._ndeg = [ndeg,ndeg]                     # [nlong,nlat]
    if not isinstance(self._ndeg,(list,tuple)):
      s = 'MIM ndeg should be int or list of two ints, rather than: '+str(self._ndeg)
      raise ValueError,s

    self._SimulParm = []
    # ss = dict(nodes=[], labels=[])               # for self._solvable
    ss = self.solvable_parms()                     # dict(nodes=[], labels=[])  
    self._pname = []
    self._pnode = []
    self._usedval = dict()
    for i in range(self._ndeg[0]+1):
      for j in range(self._ndeg[1]+1):
        pname = 'p'+str(i)+str(j)
        if not pname in self._pname:               # avoid duplication of diagonal (j=i)
          self._pname.append(pname)

          if self.is_simulated():
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

          self._pnode.append(node)                 # Parm/SimulParm nodes
          ss['nodes'].append(node)               # for self._solvable
          ss['labels'].append(pname)             # for self._solvable

    if self.is_simulated():
      self._simulated = ss
    else:
      self._solvable = ss

    # Finished:
    return None



  #---------------------------------------------------------------

  def oneliner (self):
    ss = 'MIM: '+str(self.name)
    ss += '  ndeg='+str(self._ndeg)
    ss += '  effalt='+str(int(self._effalt_km))+'km'
    if self.is_simulated():
      ss += '  (simulated)'
    return ss
  


  #======================================================================

  def TEC0(self, qnode=None, dlong=0, dlat=0, show=False):
    """Return a node/subtree that predicts the vertical (z=0) TEC value,
    at the relative position (dlong,dlat). This function is usually called
    by the function .geoTEC() of the base class IonosphereModel.py"""

    # For testing only:
    if qnode==None: qnode = self.ns['TEC0']
    
    # First make powers of dlong/dlat (relative to self._refloc)
    llong = [None, dlong]
    llat = [None, dlat]
    for k in range(2,self._ndeg[0]+1):
      llong.append(qnode('long^'+str(k)) << Meq.Multiply(llong[k-1],dlong))
    for k in range(2,self._ndeg[1]+1):
      llat.append(qnode('lat^'+str(k)) << Meq.Multiply(llat[k-1],dlat))

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

    # Finally, add the polynomial terms:
    TEC0 = qnode << Meq.Add(children=cc) 
    if show:
      display.subtree(TEC0, recurse=5, show_initrec=True)
    return TEC0




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    mim = MIM(ns, 'mim')
    mim.display(full=True)
    cc.append(mim.plot_parms())

    if 1:
      sim = MIM(ns, 'sim', ndeg=1, simulate=True)
      sim.display(full=True)
      cc.append(sim.plot_parms())


    if 1:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,0.1])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[0.1,0.1])

      if 0:
        cc.append(sim.longlat_pierce(st1, sat1, show=True))

      if 0:
        qnode = ns.qnode('xxx')
        cc.append(sim.slant_function(qnode, z=1, flat_Earth=True, show=True))

      if 1:
        cc.append(sim.geoTEC(st1, sat1, show=True))
        # cc.append(sim.geoTEC(st1, show=True))
        # cc.append(sim.geoTEC(show=True))

      if 0:
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
        sim.TEC0(show=True)

      if 0:
        sim.plot_parms(show=True)
      

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

