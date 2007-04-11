# file ../JEN/projects/MIM/GPS/GPSArray.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair
import random
from numarray import *

from Timba.Contrib.JEN.Grunt import display

Settings.forest_state.cache_policy = 100



#================================================================

class GPSArray (Meow.Parameterization):
  """Represents a Minimum Ionospheric Model (MIM)
  as a function of Earth (longitude,latitude) and
  zenith angle."""
  
  def __init__(self, ns, name='gpa',
               nstat=2, nsat=3, longlat=[1.0,1.0],
               stddev=dict(stat=[0.01,0.01],
                           sat=[0.02,0.02]),
               quals=[], kwquals={}):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

    self._nstat = nstat               # Nr of GPS stations
    self._nsat = nsat                 # Nr of GPS satellites      
    self._longlat = longlat           # (long,lat) of station array centre
    self._stddev = stddev             # stddev of positions (long,lat)

    # Define GPS stations:
    rr = dict(name=[], obj=[], longlat=[])
    stddev = self._stddev['stat']
    for k in range(self._nstat):
      sname = 'st'+str(k)
      longlat = [random.gauss(self._longlat[0], stddev[0]),
                 random.gauss(self._longlat[1], stddev[1])]
      obj = GPSPair.GPSStation(ns, sname, longlat=longlat)
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
    self._station = rr
      
    # Define GPS satellites:
    rr = dict(name=[], obj=[], longlat=[])
    stddev = self._stddev['sat']
    for k in range(self._nsat):
      longlat = [random.gauss(self._longlat[0], stddev[0]),
                 random.gauss(self._longlat[1], stddev[1])]
      sname = 'sat'+str(k)
      obj = GPSPair.GPSSatellite(ns, sname, longlat=longlat, radius=8e6)
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
    self._satellite = rr

    # Define station-satellite pairs:
    rr = dict(name=[], sat=[], stat=[], obj=[])
    for stat in self._station['obj']:
      for sat in self._satellite['obj']:
        obj = GPSPair.GPSPair (ns, station=stat, satellite=sat)
        print obj.oneliner()
        rr['name'].append(sname)
        rr['sat'].append(sat)
        rr['stat'].append(stat)
        rr['obj'].append(obj)
    self._pair = rr


    return None


  #---------------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    ss += '  '+str(self.name)
    ss += '  nstat='+str(len(self._station['obj']))
    ss += '  longlat='+str(self._longlat)
    ss += '  nsat='+str(len(self._satellite['obj']))
    ss += '  npair='+str(len(self._pair['obj']))
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()
    print '  * longlat(rad): '+str(self._longlat)
    print '  * stddev(rad) : '+str(self._stddev)
    print '  * GPSStations:'
    for s in self._station['obj']:
      print '    '+s.oneliner()
    print '  * GPSSatellites:'
    for s in self._satellite['obj']:
      print '    '+s.oneliner()
    print '  * GPSPairs:'
    for s in self._pair['obj']:
      print '    '+s.oneliner()
    print
    return True


  #-------------------------------------------------------






#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

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

    gpa = GPSArray(ns)
    gpa.display(full=True)


      
#===============================================================

