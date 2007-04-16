# file ../JEN/projects/MIM/GPS/MIM.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair

from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Grunt import display
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
               ndeg=2, simulate=False):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

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
            term = dict(ampl=1.0/(1.0+i+j), Psec=1000,
                        stddev=dict(ampl=0.1, Psec=100))
            sp = SimulParm.SimulParm(ns, pname, value=0.0, term=term)
            self._SimulParm.append(sp)             # SimulParm objects          
            node = sp.create()  
            self._add_parm(pname, node, tags=['MIM'])
            self._usedval[pname] = sp._usedval     # actually used simulation values
          else:
            # Make a regular MeqParm:
            self._add_parm(pname, Meow.Parm(), tags=['MIM'])
            self._solvable.append(self._parm(pname))

    return None


  #---------------------------------------------------------------

  def oneliner (self):
    ss = 'MIM: '+str(self.name)
    ss += '  ndeg='+str(self._ndeg)
    if self._simulate:
      ss += '  (simulated)'
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * pname: '+str(self._pname)
    print '  * solvable ('+str(len(self._solvable))+'):'
    for k,p in enumerate(self._solvable):
      print '   - '+str(k)+': '+str(p)
    for k,sp in enumerate(self._SimulParm):
      print '   - '+str(k)+': '+sp.oneliner()
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

  #-------------------------------------------------------

  def TEC(self, longlat, z=None, show=False):
    """Return a node/subtree that produces a predicted TEC value for the
    specified (longitude,latitude) pierce point, and zenith angle (z).
    It calulates the vertical (z=0) TEC for the specified (long,lat),
    multiplie (if z is specified) by a function S(z) that corrects for
    the slanted path through the ionosphere. The simplest form of S(z)
    is sec(z)=1/cos(z), but more complicated versions take account of
    the curvature of the Earth. In all cases, S(z=0)=1."""

    name = 'TEC'
    qnode = self.ns[name].qadd(longlat)                              # <--------- !!
    if not qnode.initialized(): 

      # First make powers of long/lat
      long1 = qnode('pierce_long') << Meq.Selector(longlat, index=0)
      lat1 = qnode('pierce_lat') << Meq.Selector(longlat, index=1)
      llong = [None, long1]
      llat = [None, lat1]
      for k in range(2,self._ndeg[0]+1):
        llong.append(qnode('long^'+str(k)) << Meq.Multiply(llong[k-1],long1))
      for k in range(2,self._ndeg[1]+1):
        llat.append(qnode('lat^'+str(k)) << Meq.Multiply(llat[k-1],lat1))

      # Then make the various polynomial terms, and add them:
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

      # Multiply with S(z), if required:
      if z==None:
        qnode << Meq.Add(children=cc)    # zenith direction, not required
      else:
        TEC0 = qnode('z=0') << Meq.Add(children=cc)
        cosz = qnode('cosz') << Meq.Cos(z)
        qnode << Meq.Divide(TEC0, cosz)

    # Finished:
    if show:
      display.subtree(qnode, recurse=6, show_initrec=False)
    return qnode






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

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
    ns = NodeScope()


    mim = MIM(ns)
    mim.display(full=True)

    if 1:
      sim = MIM(ns, 'simul', ndeg=1, simulate=True)
      sim.display(full=True)

    #-----------------------------------------------------------------------

    if 0:
      st1 = GPSPair.GPSStation(ns, 'st1', longlat=[-0.1,1.0])
      sat1 = GPSPair.GPSSatellite(ns, 'sat1', longlat=[-0.1,1.0], radius=8e6)
      pair = GPSPair.GPSPair (ns, station=st1, satellite=sat1)
      pair.display(full=True)

      if 0:
        pair.zenith_angle(show=True)
      
      if 0:
        longlat = pair.longlat_pierce(show=True)
        node = mim.TEC(longlat, z=0.1, show=True)
        node = sim.TEC(longlat, z=0.1, show=True)

      if 1:
        pair.mimTEC(sim, show=True)


      
#===============================================================
