# file ../JEN/projects/MIM/GPS/GPSArray.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair
import random
from numarray import *

from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

Settings.forest_state.cache_policy = 100



#================================================================

class GPSArray (Meow.Parameterization):
  """Represents a Minimum Ionospheric Model (MIM)
  as a function of Earth (longitude,latitude) and
  zenith angle."""
  
  def __init__(self, ns, name='gpa',
               nstat=2, nsat=3,
               longlat=[1.0,0.5],
               stddev=dict(stat=[0.01,0.01],
                           sat=[0.1,0.1]),
               move=False,
               quals=[], kwquals={}):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

    self._nstat = nstat               # Nr of GPS stations
    self._nsat = nsat                 # Nr of GPS satellites      
    self._longlat0 = longlat          # (long,lat) of station array centre
    self._stddev = stddev             # stddev of positions (long,lat)

    # Define GPS stations:
    rr = dict(name=[], obj=[], longlat=[], stddev=stddev['stat'],
              plot=dict(color='blue', style='circle'))
    for k in range(self._nstat):
      sname = 'st'+str(k)
      longlat = [random.gauss(self._longlat0[0], rr['stddev'][0]),
                 random.gauss(self._longlat0[1], rr['stddev'][1])]
      obj = GPSPair.GPSStation(self.ns, sname, longlat=longlat)
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
    self._station = rr
      
    # Define GPS satellites:
    rr = dict(name=[], obj=[], longlat=[], stddev=stddev['sat'],
              plot=dict(color='red', style='triangle'))
    stddev = self._stddev['sat']
    for k in range(self._nsat):
      longlat = [random.gauss(self._longlat0[0], rr['stddev'][0]),
                 random.gauss(self._longlat0[1], rr['stddev'][1])]
      sname = 'sat'+str(k)
      obj = GPSPair.GPSSatellite(self.ns, sname, longlat=longlat, move=move)
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
    self._satellite = rr

    # Define station-satellite pairs:
    rr = dict(name=[], sat=[], stat=[], obj=[],
              plot=dict(color='green', style='rectangle'))
    for stat in self._station['obj']:
      for sat in self._satellite['obj']:
        obj = GPSPair.GPSPair (self.ns, station=stat, satellite=sat)
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
    ss += '  longlat='+str(self._longlat0)
    ss += '  nsat='+str(len(self._satellite['obj']))
    ss += '  npair='+str(len(self._pair['obj']))
    return ss
  
  def display(self, full=False):
    """Display a summary of this object"""
    print '\n** '+self.oneliner()

    print '  * GPSStations:'
    for s in self._station['obj']:
      print '    - '+s.oneliner()
    print '    * plotting: '+str(self._station['plot'])
    print '    * longlat scatter: stddev(rad) = '+str(self._station['stddev'])
    for k,name in enumerate(self._station['name']):
      print '      - '+name+': longlat = '+str(self._station['longlat'][k])

    print '  * GPSSatellites:'
    for s in self._satellite['obj']:
      print '    - '+s.oneliner()
    print '    * plotting: '+str(self._satellite['plot'])
    print '    * longlat scatter: stddev(rad) = '+str(self._satellite['stddev'])
    for k,name in enumerate(self._satellite['name']):
      print '      - '+name+': longlat = '+str(self._satellite['longlat'][k])

    print '  * GPSPairs:'
    for s in self._pair['obj']:
      print '    - '+s.oneliner()
    print '    * plotting: '+str(self._pair['plot'])
    print
    return True


  #-------------------------------------------------------
  # Visualisation
  #-------------------------------------------------------

  def rvsi_longlat(self, bookpage='GPSArray', folder=None):
    """Plot the station (blue) and satellite (red) positions"""

    dcolls = []
    scope = 'longlat'

    # Station positions:
    cc = []
    for s in self._station['obj']:
      cc.append(s.longlat_complex())
    plot = self._station['plot']
    rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                   scope=scope, tag='stations',
                                   xlabel='longitude(rad)', ylabel='latitude(rad)',
                                   color=plot['color'], style=plot['style'],
                                   size=8, pen=2,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)

    # Satellite positions:
    cc = []
    for s in self._satellite['obj']:
      cc.append(s.longlat_complex())
    plot = self._satellite['plot']
    rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                   scope=scope, tag='satellites',
                                   xlabel='longitude(rad)', ylabel='latitude(rad)',
                                   color=plot['color'], style=plot['style'],
                                   size=8, pen=2,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)

    # Lock the scale of the plot:
    dll = 7*array(self._stddev['sat'])
    ll0 = array(self._longlat0)
    print '** dll =',dll,ll0+dll,ll0-dll
    trc = self.ns.trc(scope) << Meq.ToComplex(ll0[0]+dll[0],ll0[1]+dll[1])
    blc = self.ns.blc(scope) << Meq.ToComplex(ll0[0]-dll[0],ll0[1]-dll[1])
    rr = MG_JEN_dataCollect.dcoll (self.ns, [trc,blc],
                                   scope=scope, tag='scale',
                                   xlabel='longitude(rad)', ylabel='latitude(rad)',
                                   color='white', style='circle', size=1, pen=1,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)
    

    # Concatenate:
    # NB: nodename -> dconc_scope_tag
    rr = MG_JEN_dataCollect.dconc(self.ns, dcolls,
                                  scope=scope, tag='',
                                  xlabel='longitude(rad)', ylabel='latitude(rad)',
                                  bookpage=None)
    self._dcoll = rr['dcoll']
    JEN_bookmarks.create(self._dcoll, scope,
                         page=bookpage, folder=folder)
    # Return the dataConcat node:
    return self._dcoll

  #----------------------------------------------------------------------

  def rvsi_azel(self, bookpage='GPSArray', folder=None):
    """Plot the pair view directions (az,el)"""

    dcolls = []
    scope = 'azel'

    # Pair positions:
    cc = []
    for s in self._pair['obj']:
      cc.append(s.azel_complex())
    plot = self._pair['plot']
    rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                   scope=scope, tag='stations',
                                   xlabel='azimuth(rad)', ylabel='elevation(rad)',
                                   color=plot['color'], style=plot['style'],
                                   size=8, pen=2,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)

    # Lock the scale of the plot:
    trc = self.ns.trc(scope) << Meq.ToComplex(1.6,1.6)
    blc = self.ns.blc(scope) << Meq.ToComplex(-1.6,1.0)
    rr = MG_JEN_dataCollect.dcoll (self.ns, [trc,blc],
                                   scope=scope, tag='scale',
                                   xlabel='azimuth(rad)', ylabel='elevation(rad)',
                                   color='white', style='circle', size=1, pen=1,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)
    
    # Concatenate:
    # NB: nodename -> dconc_scope_tag
    rr = MG_JEN_dataCollect.dconc(self.ns, dcolls,
                                  scope=scope, tag='',
                                  xlabel='azimuth(rad)', ylabel='elevation(rad)',
                                  bookpage=None)
    self._dcoll = rr['dcoll']
    JEN_bookmarks.create(self._dcoll, scope,
                         page=bookpage, folder=folder)
    # Return the dataConcat node:
    return self._dcoll





#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    gpa = GPSArray(ns, nstat=2, nsat=2, move=True)
    gpa.display(full=True)

    if 1:
      cc.append(gpa.rvsi_longlat())
    if 1:
      cc.append(gpa.rvsi_azel())

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t in range(-50,50):
      t1 = t*300
      t2 = t1+0.0001
      domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
      cells = meq.cells(domain, num_freq=1, num_time=1)
      request = meq.request(cells, rqid=meq.requestid(t+100))
      result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       

#================================================================
# Test program
#================================================================
    
if __name__ == '__main__':
    """Test program"""
    ns = NodeScope()

    gpa = GPSArray(ns, nstat=2, nsat=2, move=True)
    gpa.display(full=True)

    if 0:
      node = gpa.rvsi_longlat()
      display.subtree(node,node.name)

    if 0:
      node = gpa.rvsi_azel()
      display.subtree(node,node.name)

      
#===============================================================

