# file ../JEN/projects/MIM/GPS/GPSArray.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair
import IonosphereModel
import MIM
import random
from numarray import *

from Timba.Contrib.JEN.Grunt import display
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

Settings.forest_state.cache_policy = 100



#================================================================

class GPSArray (Meow.Parameterization):
  """Represents an array of GPS stations as a function of Earth
  (longitude,latitude), and a collection of GPS satellites."""
  
  def __init__(self, ns, name='gparr',
               nstat=2, nsat=3,
               longlat=[1.0,0.5],
               stddev_pos=dict(stat=[0.1,0.1],
                               sat=[0.5,0.5]),
               move=False,
               stddev_TecBias=0.0,
               pair_based_TecBias=True,
               quals=[], kwquals={}):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

    self._nstat = nstat                   # Nr of GPS stations
    self._nsat = nsat                     # Nr of GPS satellites      
    self._longlat0 = longlat              # (long,lat) of station array centre
    self._stddev_pos = stddev_pos         # stddev of positions (long,lat)
    self._stddev_TecBias = stddev_TecBias # stddev of TEC bias values
    self._pair_based_TecBias = pair_based_TecBias # If False, use station/satellite-based TECs
 

    #---------------------
    # Define GPS stations:
    rr = dict(name=[], obj=[], longlat=[],
              stddev_pos=self._stddev_pos['stat'],
              stddev_TecBias=self._stddev_TecBias,
              plot=dict(color='blue', style='circle'))
    for k in range(self._nstat):
      sname = 'st'+str(k)
      longlat = [random.gauss(self._longlat0[0], rr['stddev_pos'][0]),
                 random.gauss(self._longlat0[1], rr['stddev_pos'][1])]
      obj = GPSPair.GPSStation(self.ns, sname, longlat=longlat,
                               simul=dict(stddev=rr['stddev_TecBias']))
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
    self._station = rr
      

    #---------------------
    # Define GPS satellites:
    rr = dict(name=[], obj=[], longlat=[],
              stddev_pos=self._stddev_pos['sat'],
              stddev_TecBias=self._stddev_TecBias,
              plot=dict(color='red', style='triangle'))
    sign = dict(direction=1, inclination=1)
    for k in range(self._nsat):
      longlat = [random.gauss(self._longlat0[0], rr['stddev_pos'][0]),
                 random.gauss(self._longlat0[1], rr['stddev_pos'][1])]
      sname = 'sat'+str(k)
      obj = GPSPair.GPSSatellite(self.ns, sname, longlat=longlat,
                                 simul=dict(stddev=rr['stddev_TecBias']),
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


    #---------------------
    # Define station-satellite pairs:
    ss = dict(nodes=[], labels=[])
    rr = dict(name=[], sat=[], stat=[], obj=[],
              stddev_TecBias=self._stddev_TecBias,
              plot=dict(color='green', style='rectangle'))
    for stat in self._station['obj']:
      for sat in self._satellite['obj']:
        obj = GPSPair.GPSPair (self.ns, station=stat, satellite=sat,
                               pair_based_TecBias=self._pair_based_TecBias,
                               simul=dict(stddev=rr['stddev_TecBias']))
        print obj.oneliner()
        rr['name'].append(sname)
        rr['sat'].append(sat)
        rr['stat'].append(stat)
        rr['obj'].append(obj)
        # Collect solvable MeqParms:
        ss1 = obj.solvable()
        for k,node in enumerate(ss1['nodes']):
          if not node in ss['nodes']:
            ss['nodes'].append(node)
            ss['labels'].append(ss1['labels'][k])
    self._pair = rr
    self._solvable = ss
    self._longlat_pierce = []

    #---------------------
    # Finished:
    return None



  #---------------------------------------------------------------

  def oneliner (self):
    ss = str(type(self))
    ss = 'GPSArray'
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
    print '    * longlat scatter (rad) = '+str(self._station['stddev_pos'])
    for k,name in enumerate(self._station['name']):
      print '      - '+name+': longlat = '+str(self._station['longlat'][k])
    if not self._pair_based_TecBias:
      print '    * pair_based_TecBias = '+str(self._pair_based_TecBias)
      print '    * TecBias scatter (TECU) = '+str(self._station['stddev_TecBias'])

    print '  * GPSSatellites:'
    for s in self._satellite['obj']:
      print '    - '+s.oneliner()
    print '    * plotting: '+str(self._satellite['plot'])
    print '    * longlat scatter (rad) = '+str(self._satellite['stddev_pos'])
    for k,name in enumerate(self._satellite['name']):
      print '      - '+name+': longlat = '+str(self._satellite['longlat'][k])
    if not self._pair_based_TecBias:
      print '    * pair_based_TecBias = '+str(self._pair_based_TecBias)
      print '    * TecBias scatter (TECU) = '+str(self._satellite['stddev_TecBias'])

    print '  * GPSPairs:'
    for p in self._pair['obj']:
      print '    - '+p.oneliner()
    if self._pair_based_TecBias:
      print '    * pair_based_TecBias = '+str(self._pair_based_TecBias)
      print '    * TecBias scatter (TECU) = '+str(self._pair['stddev_TecBias'])
    ss = self._solvable
    print '    * solvable ('+str(len(ss['nodes']))+'):'
    for k,node in enumerate(ss['nodes']):
      print '      -',ss['labels'][k],': ',str(node)
    print '    * plotting: '+str(self._pair['plot'])
    print
    return True


  #-------------------------------------------------------

  def solvable(self, tags='*', merge=None, show=False):
    """Return a dict with (a selection (tags) of solvable nodes (MeqParms)
    and their labels. If merge is a dict, include its contents, while
    avoiding duplicates."""
    ss = dict(nodes=[], labels=[])
    for key in ss.keys():
      ss[key] = self._solvable[key]
    if isinstance(merge,dict):
      for k,node in enumerate(merge['nodes']):
        if not node in ss['nodes']:
          ss['nodes'].append(node)
          ss['labels'].append(merge['labels'][k])
    if show:
      print '\n** solvable (tags=',tags,') (merge=',type(merge),') from:',self.oneliner()
      for k,node in enumerate(ss['nodes']):
        print '  -',ss['labels'][k],': ',str(node)
      print
    return ss

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
  #-------------------------------------------------------

  def ploTEC(self, iom, bookpage='ploTEC', show=False):
    """Make an inspector (plot) for the TEC-values of the various pairs"""
    name = 'ploTEC'
    qnode = self.ns[name]
    qnode = qnode.qmerge(iom.ns['GPSArray_dummy_qnode'])
    if not qnode.initialized():
      self.longlat_pierce(reset=True)
      cc =[]
      labels = []
      for pair in self._pair['obj']:
        labels.append(pair.name)
        cc.append(pair.modelTEC(iom))
        self.longlat_pierce(pair, qnode=qnode)
      self.longlat_pierce(qnode=qnode, bundle=True)
      qnode << Meq.Composer(children=cc, plot_label=labels)
      JEN_bookmarks.create(qnode, page=bookpage,
                           viewer='Collections Plotter')
    if show: display.subtree(qnode, recurse=5)
    return qnode

  #--------------------------------------------------------------------

  def longlat_pierce(self, pair=None, qnode=None,
                     reset=False, bundle=False, show=False):
    """Helper function to deal with longlat_pierce values."""
    if reset: self._longlat_pierce = []
    if pair:
        pnode = qnode(pair.name)
        llp = pair._longlat_pierce    # obtained via pair.modelTEC(iom)
        lo = pnode('pierce_longitude') << Meq.Selector(llp, index=0)
        lat = pnode('pierce_latitude') << Meq.Selector(llp, index=1)
        longlat = pnode('pierce_longlat_complex') << Meq.ToComplex(lo,lat)
        self._longlat_pierce.append(longlat)
    if bundle:
      # Bundle them to limit clutter in the browser (root nodes)
      qnode('pierce_longlat_bundle') << Meq.Composer(*self._longlat_pierce)
    if show:
      pass
    return self._longlat_pierce

  #-------------------------------------------------------

  def solIOM(self, iom, sim, show=False):
    """Solve for the parameters of the specified Ionosphere Model (iom),
    using the other IOM (sim) to generate predicted TEC values."""

    name = 'solIOM'
    qnode = self.ns[name]
    # qnode = qnode.qmerge(iom.ns['GPSArray_dummy_qnode'])
    # qnode = qnode.qmerge(sim.ns['GPSArray_dummy_qnode'])
    if not qnode.initialized():
      self.longlat_pierce(reset=True)
      condeqs =[]
      labels = []
      for pair in self._pair['obj']:
        label = pair.name
        labels.append(label)
        condeq = qnode('condeq')(label) << Meq.Condeq(pair.modelTEC(iom),
                                                      pair.modelTEC(sim, sim=True))
        condeqs.append(condeq)
        self.longlat_pierce(pair, qnode=qnode)
      self.longlat_pierce(qnode=qnode, bundle=True)

      reqseq = []                             # list of reqseq children

      # Get the iom parameters to be solved for:
      solvable = iom.solvable()
      JEN_bookmarks.create(solvable['nodes'], page='iom_pp')

      if False:                                                      # <----- !!
        # Add the TecBias parameters to the solvables 
        solvable = self.solvable(merge=solvable, show=show)
      else:
        ignore = self.solvable(show=show)['nodes']
        print '\n*** ignore =',ignore
        if ignore:
          qnode('ignored_parms_bundle') << Meq.Composer(*ignore)

      # Make the solver itself:
      node = qnode('solver') << Meq.Solver(children=condeqs,
                                           solvable=solvable['nodes'])
      JEN_bookmarks.create(node, page=name)
      reqseq.append(node)

      # Visualization of (condeq) residuals:
      node = qnode('condeqs') << Meq.Composer(children=condeqs,
                                              plot_label=labels)
      JEN_bookmarks.create(node, page=name, viewer='Collections Plotter')
      reqseq.append(node)
      
      # Visualization of solvables (MeqParms):
      node = qnode('solvable') << Meq.Composer(children=solvable['nodes'],
                                               plot_label=solvable['labels'])
      JEN_bookmarks.create(node, page=name, viewer='Collections Plotter')
      reqseq.append(node)

      # Make the final reqseq:
      qnode << Meq.ReqSeq(children=reqseq)
      
    if show:
      display.subtree(qnode, recurse=5)
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
    if False:
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


    # Longlat of (pair) pierce points (if available):
    if self._longlat_pierce:
      rr = MG_JEN_dataCollect.dcoll (self.ns, self._longlat_pierce,
                                     scope=scope, tag='pierce',
                                     color='red', style='cross',
                                     size=8, pen=2,
                                     results_buffer=results_buffer,
                                     type='realvsimag', errorbars=True)
      dcolls.append(rr)


    # Alt-az of satellites, as seen from stations:
    if True:
      cc = []
      for s in self._pair['obj']:
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





#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    gpa = GPSArray(ns,
                   # nstat=3, nsat=4, 
                   nstat=1, nsat=1, 
                   longlat=[-0.1,0.1],
                   stddev_pos=dict(stat=[0.1,0.1],
                                   # sat=[0.2,0.2]),
                                   sat=[0.4,0.4]),
                   stddev_TecBias=1.0,
                   pair_based_TecBias=True,
                   move=True)
    gpa.display(full=True)

    if 1:
      # The simulated IOM provide the 'measured' GPS data
      sim = MIM.MIM(ns, 'sim', ndeg=2, simulate=True)
      sim.display(full=True)

    if 1:
      cc.append(gpa.ploTEC(sim))
      # NB: Do this AFTER MIM, because of pierce points
      cc.append(gpa.rvsi_longlat())

    if 0:
      # The MIM for whose parameters we solve
      tiling = None
      # tiling = 1
      time_deg = 0
      time_deg = 2
      mim = MIM.MIM(ns, 'mim', ndeg=1,
                    tiling=tiling, time_deg=time_deg)
      mim.display(full=True)
      if 1:
        reqseq = gpa.solIOM(mim, sim, show=True)
        cc.append(reqseq)

    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------
#---------------------------------------------------------------

def _tdl_job_dom0s (mqs, parent):
    """Execute the forest, starting at the named node"""
    dt = 0.001
    t1 = -dt/2                          
    t2 = dt/2
    domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
       
def _tdl_job_dom30s (mqs, parent):
    """Execute the forest, starting at the named node"""
    dt = 30
    t1 = -dt/2                          
    t2 = dt/2
    domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=1)
    # request = meq.request(cells, rqtype='ev')
    request = meq.request(cells, rqid=meq.requestid(t2))
    result = mqs.meq('Node.Execute',record(name='result', request=request))
       

def _tdl_job_dom300s (mqs, parent):
    """Execute the forest, starting at the named node"""
    dt = 300
    t1 = -dt/2                          
    t2 = dt/2
    domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=10)
    # request = meq.request(cells, rqtype='ev')
    request = meq.request(cells, rqid=meq.requestid(t2))
    result = mqs.meq('Node.Execute',record(name='result', request=request))
       

def _tdl_job_dom3000s (mqs, parent):
    """Execute the forest, starting at the named node"""
    dt = 3000
    t1 = -dt/2                          
    t2 = dt/2
    domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    # request = meq.request(cells, rqtype='ev')
    request = meq.request(cells, rqid=meq.requestid(t2))
    result = mqs.meq('Node.Execute',record(name='result', request=request))
       
def _tdl_job_dom20000s (mqs, parent):
    """Execute the forest, starting at the named node"""
    dt = 20000
    t1 = -dt/2                          
    t2 = dt/2
    domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    # request = meq.request(cells, rqtype='ev')
    request = meq.request(cells, rqid=meq.requestid(t2))
    result = mqs.meq('Node.Execute',record(name='result', request=request))
       

def _tdl_job_step30s (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t in range(-50,50):
      t1 = t*30                                            # 30 sec steps 
      t2 = t1+0.0001
      domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
      cells = meq.cells(domain, num_freq=1, num_time=1)
      request = meq.request(cells, rqid=meq.requestid(t+100))
      result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       
def _tdl_job_step100s (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t in range(-50,50):
      t1 = t*100                                           # 100 sec steps 
      t2 = t1+0.0001
      domain = meq.domain(1.0e8,1.1e8,t1,t2)               # (f1,f2,t1,t2)
      cells = meq.cells(domain, num_freq=1, num_time=1)
      request = meq.request(cells, rqid=meq.requestid(t+100))
      result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
       
def _tdl_job_step300s (mqs, parent):
    """Execute the forest, starting at the named node"""
    for t in range(-50,50):
      t1 = t*300                                           # 300 sec steps 
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
                   stddev_pos=dict(stat=[0.1,0.1],
                                   sat=[0.5,0.5]),
                   stddev_TecBias=1.0,
                   pair_based_TecBias=True,
                   move=True)
    gpa.display(full=True)

    if 1:
      xxx = dict(nodes=range(3), labels=['xxx','yy','z'])
      gpa.solvable(merge=xxx, show=True)

    if 0:
      gpa.longlat0(show=True)

    if 0:
      node = gpa.rvsi_longlat()
      display.subtree(node,node.name)

    if 0:
      sim = MIM.MIM(ns, 'sim', ndeg=1, simulate=True)
      sim.display(full=True)
      gpa.ploTEC(sim, show=True)

      if 0:
        mim = MIM.MIM(ns, 'mim', ndeg=1)
        mim.display(full=True)
        gpa.solIOM(mim, sim, show=True)


      
#===============================================================

