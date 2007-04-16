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
  
  def __init__(self, ns, name='gparr',
               nstat=2, nsat=3,
               longlat=[1.0,0.5],
               stddev=dict(stat=[0.1,0.1],
                           sat=[0.5,0.5]),
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
    sign = dict(direction=1, inclination=1)
    for k in range(self._nsat):
      longlat = [random.gauss(self._longlat0[0], rr['stddev'][0]),
                 random.gauss(self._longlat0[1], rr['stddev'][1])]
      sname = 'sat'+str(k)
      obj = GPSPair.GPSSatellite(self.ns, sname, longlat=longlat,
                                 sign=sign, move=move)
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
      # Change a different orbit parameter each time:
      if (k%2==0):
        sign['inclination'] *= -1
      else:
        sign['direction'] *= -1
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
    ss += '  longlat0='+str(self._longlat0)
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

  def longlat0(self, show=False):
    """Return the (long,lat) node for the array reference position"""
    name = 'longlat0'
    qnode = self.ns[name]
    if not qnode.initialized():
      lo = qnode('longitude') << Meq.Constant(self._longlat0[0])
      la = qnode('latitude') << Meq.Constant(self._longlat0[1])
      qnode << Meq.Composer(lo,la)
    if show: display.subtree(qnode)
    return qnode


  #-------------------------------------------------------
  # Visualisation
  #-------------------------------------------------------

  def rvsi_longlat(self, bookpage='GPSArray', folder=None):
    """Plot the station (blue) and satellite (red) positions"""

    dcolls = []
    scope = 'longlat'
    results_buffer = 100 

    # Station positions:
    cc = []
    for s in self._station['obj']:
      cc.append(s.longlat_complex())
    plot = self._station['plot']
    rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                   scope=scope, tag='stations',
                                   color=plot['color'], style=plot['style'],
                                   size=8, pen=2,
                                   results_buffer=results_buffer,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)

    # Satellite positions:
    cc = []
    for s in self._satellite['obj']:
      cc.append(s.longlat_complex())
    plot = self._satellite['plot']
    rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                   scope=scope, tag='satellites',
                                   color=plot['color'], style=plot['style'],
                                   size=18, pen=2,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)


    # Input satellite positions:
    if True:
      cc = []
      node = self.ns.longlat('input')
      for k,ll in enumerate(self._satellite['longlat']):
        cc.append(node(k) << Meq.ToComplex(ll[0],ll[1]))
      rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                     scope=scope, tag='input',
                                     color='cyan', style='diamond',
                                     # size=8, pen=2,
                                     type='realvsimag', errorbars=True)
      dcolls.append(rr)

    # Pair positions:
    if True:
      cc = []
      for s in self._pair['obj']:
        # cc.append(s.azang_complex())
        cc.append(s.azel_complex())
      plot = self._pair['plot']
      rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                     scope=scope, tag='pairs',
                                     color=plot['color'], style=plot['style'],
                                     size=8, pen=2,
                                     results_buffer=results_buffer,
                                     type='realvsimag', errorbars=True)
      dcolls.append(rr)



    # Lock the scale of the plot:
    trc = self.ns.trc(scope) << Meq.ToComplex(1.6,1.6)
    blc = self.ns.blc(scope) << Meq.ToComplex(-1.6,-1.6)
    rr = MG_JEN_dataCollect.dcoll (self.ns, [trc,blc],
                                   scope=scope, tag='scale',
                                   # xlabel='longitude(rad)', ylabel='latitude(rad)',
                                   xlabel='longitude or azimuth (rad)',
                                   ylabel='latitude or elevation(rad)',
                                   color='white', style='circle', size=1, pen=1,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)
    

    # Concatenate:
    # NB: nodename -> dconc_scope_tag
    rr = MG_JEN_dataCollect.dconc(self.ns, dcolls,
                                  scope=scope, tag='',
                                  bookpage=None)
    self._dcoll = rr['dcoll']
    JEN_bookmarks.create(self._dcoll, scope,
                         page=bookpage, folder=folder)
    # Return the dataConcat node:
    return self._dcoll


  #----------------------------------------------------------------------
  #----------------------------------------------------------------------

  def rvsi_azel(self, bookpage='GPSArray', folder=None):
    """Plot the pair view directions (az,el)"""

    dcolls = []
    scope = 'azel'
    results_buffer = 100 

    # Pair positions:
    cc = []
    for s in self._pair['obj']:
      cc.append(s.azel_complex())
    plot = self._pair['plot']
    rr = MG_JEN_dataCollect.dcoll (self.ns, cc,
                                   scope=scope, tag='pairs',
                                   xlabel='azimuth(rad)', ylabel='elevation(rad)',
                                   color=plot['color'], style=plot['style'],
                                   size=8, pen=2,
                                   results_buffer=results_buffer,
                                   type='realvsimag', errorbars=True)
    dcolls.append(rr)

    # Lock the scale of the plot:
    trc = self.ns.trc(scope) << Meq.ToComplex(1.6,1.6)
    blc = self.ns.blc(scope) << Meq.ToComplex(-1.6,-1.6)
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
                                  # results_buffer=100,
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

    gpa = GPSArray(ns,
                   nstat=4, nsat=5, 
                   # nstat=1, nsat=1, 
                   longlat=[0.5,0.1],
                   stddev=dict(stat=[0.1,0.1],
                               sat=[0.5,0.5]),
                   move=True)
    gpa.display(full=True)

    if 1:
      cc.append(gpa.rvsi_longlat())
    if 0:
      cc.append(gpa.rvsi_azel())

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------
#---------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
    """Execute the forest, starting at the named node"""
    t1 = 0                          
    t2 = t1+0.0001
    domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
       

def _tdl_job_sequence (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t in range(-50,50):
      t1 = t*100                                            # 30 sec steps 
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

    gpa = GPSArray(ns, nstat=2, nsat=1,
                   stddev=dict(stat=[0.1,0.1],
                               sat=[0.5,0.5]),
                   move=True)
    gpa.display(full=True)

    if 1:
      gpa.longlat0(show=True)

    if 0:
      node = gpa.rvsi_longlat()
      display.subtree(node,node.name)

    if 0:
      node = gpa.rvsi_azel()
      display.subtree(node,node.name)

      
#===============================================================

