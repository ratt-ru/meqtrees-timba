# file ../JEN/projects/MIM/GPS/GPSArray.py

from Timba.TDL import *
from Timba.Meq import meq

import Meow
import GPSPair
import IonosphereModel
import MIM

from copy import deepcopy
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
               simul_TecBias=dict(value=0.0, stddev=0.0),
               pair_based_TecBias=True,
               quals=[], kwquals={}):

    Meow.Parameterization.__init__(self, ns, name,
                                   quals=quals, kwquals=kwquals)

    self._nstat = nstat                      # Nr of GPS stations
    self._nsat = nsat                        # Nr of GPS satellites      
    self._longlat0 = longlat                 # (long,lat) of station array centre
    self._stddev_pos = stddev_pos            # stddev of positions (long,lat)
    self._simul_TecBias = simul_TecBias      # value and stddev of simulated TEC bias
    self._pair_based_TecBias = pair_based_TecBias # If False, use station/satellite-based TECs
 

    #---------------------
    # Define GPS stations:
    rr = dict(name=[], obj=[], longlat=[],
              stddev_pos=self._stddev_pos['stat'],
              simul_TecBias=self._simul_TecBias,
              plot=dict(color='blue', style='circle'))
    for k in range(self._nstat):
      sname = 'st'+str(k)
      longlat = [random.gauss(self._longlat0[0], rr['stddev_pos'][0]),
                 random.gauss(self._longlat0[1], rr['stddev_pos'][1])]
      obj = GPSPair.GPSStation(self.ns, sname, longlat=longlat,
                               simul=rr['simul_TecBias'])
      print obj.oneliner()
      rr['name'].append(sname)
      rr['obj'].append(obj)
      rr['longlat'].append(longlat)
    self._station = rr
      

    #---------------------
    # Define GPS satellites:
    rr = dict(name=[], obj=[], longlat=[],
              stddev_pos=self._stddev_pos['sat'],
              simul_TecBias=self._simul_TecBias,
              plot=dict(color='red', style='triangle'))
    sign = dict(direction=1, inclination=1)
    for k in range(self._nsat):
      longlat = [random.gauss(self._longlat0[0], rr['stddev_pos'][0]),
                 random.gauss(self._longlat0[1], rr['stddev_pos'][1])]
      sname = 'sat'+str(k)
      obj = GPSPair.GPSSatellite(self.ns, sname, longlat=longlat,
                                 simul=rr['simul_TecBias'],
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
              iistat=[], iisat=[],
              simul_TecBias=self._simul_TecBias,
              plot=dict(color='green', style='rectangle'))
    for istat,stat in enumerate(self._station['obj']):
      for isat,sat in enumerate(self._satellite['obj']):
        obj = GPSPair.GPSPair (self.ns, station=stat, satellite=sat,
                               pair_based_TecBias=self._pair_based_TecBias,
                               simul=rr['simul_TecBias'])
        print obj.oneliner()
        rr['name'].append(sname)
        rr['sat'].append(sat)
        rr['stat'].append(stat)
        rr['iisat'].append(isat)
        rr['iistat'].append(istat)
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
    ss += '  (pbTb='+str(self._pair_based_TecBias)+')'
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
      print '    * TecBias (TECU) = '+str(self._station['simul_TecBias'])

    print '  * GPSSatellites:'
    for s in self._satellite['obj']:
      print '    - '+s.oneliner()
    print '    * plotting: '+str(self._satellite['plot'])
    print '    * longlat scatter (rad) = '+str(self._satellite['stddev_pos'])
    for k,name in enumerate(self._satellite['name']):
      print '      - '+name+': longlat = '+str(self._satellite['longlat'][k])
    if not self._pair_based_TecBias:
      print '    * pair_based_TecBias = '+str(self._pair_based_TecBias)
      print '    * TecBias (TECU) = '+str(self._satellite['simul_TecBias'])

    print '  * GPSPairs:'
    for p in self._pair['obj']:
      print '    - '+p.oneliner()
    if self._pair_based_TecBias:
      print '    * pair_based_TecBias = '+str(self._pair_based_TecBias)
      print '    * TecBias (TECU) = '+str(self._pair['simul_TecBias'])
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

  def plot_geoSz(self, iom, bookpage='geoSz', show=False):
    """Make an inspector (plot) for the z-dependent slant-function
    of the various pairs."""
    qnode = self.ns['plot_geoSz']
    qnode = qnode.qmerge(iom.ns['GPSArray_dummy_qnode'])
    if not qnode.initialized():
      cc =[]
      labels = []
      for pair in self._pair['obj']:
        labels.append(pair.name)
        cc.append(pair.geoSz(iom))
      qnode << Meq.Composer(children=cc, plot_label=labels)
      JEN_bookmarks.create(qnode, page=bookpage,
                           viewer='Collections Plotter')
    if show: display.subtree(qnode, recurse=5)
    return qnode

  #--------------------------------------------------------------------

  def plot_modelTEC(self, iom, bookpage='modelTEC', show=False):
    """Make an inspector (plot) for the modelTEC-values of the various pairs.
    This includes the station/satellite TEC_biases."""
    qnode = self.ns['plot_modelTEC']
    if iom.is_simulated():
      qnode = self.ns['plot_simodelTEC']
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

  def solveIOM(self, iom, sim, solve_bias=False, num_iter=5, show=False):
    """Solve for the parameters of the specified IonosphereModel (iom),
    using the other IOM (sim) to generate predicted TEC values.
    If solve_bias==True, solve for the TEC_bias values as well."""

    name = 'solveIOM'
    qnode = self.ns[name]
    # qnode = qnode.qmerge(iom.ns['GPSArray_dummy_qnode'])
    # qnode = qnode.qmerge(sim.ns['GPSArray_dummy_qnode'])
    if not qnode.initialized():
      self.longlat_pierce(reset=True)
      condeqs =[]
      LHS = []
      RHS = []
      labels = []
      for pair in self._pair['obj']:
        label = pair.name
        labels.append(label)
        lhs = pair.modelTEC(iom)
        rhs = pair.modelTEC(sim)
        condeq = qnode('condeq')(label) << Meq.Condeq(lhs, rhs)
        condeqs.append(condeq)
        LHS.append(lhs)
        RHS.append(rhs)
        self.longlat_pierce(pair, qnode=qnode)
      self.longlat_pierce(qnode=qnode, bundle=True)

      reqseq = []                             # list of reqseq children

      # Get the IOM parameters to be solved for:
      solvable = iom.solvable()
      IOM_parms = solvable['nodes']
      IOM_labels = solvable['labels']
      JEN_bookmarks.create(IOM_parms, page='IOM_parms')

      if solve_bias:                                   
        # Add the TecBias parameters to the solvables 
        solvable = self.solvable(merge=solvable, show=show)
        # NB: The TecBias residuals are plotted (rvsi) below
      else:
        # Do not solve for TecBias, and unclutter the browser (roots):
        ignore = self.solvable(show=show)['nodes']
        if ignore:
          qnode('ignored_parms_bundle') << Meq.Composer(*ignore)

      # Make the solver itself:
      node = qnode('solver') << Meq.Solver(children=condeqs,
                                           num_iter=num_iter,
                                           solvable=solvable['nodes'])
      JEN_bookmarks.create(node, page=name)
      reqseq.append(node)

      # Visualization of (condeq) residuals:
      node = qnode('condeqs') << Meq.Composer(children=condeqs,
                                              plot_label=labels)
      JEN_bookmarks.create(node, page=name, viewer='Collections Plotter')
      reqseq.append(node)

      if False:
        # Visualization of condeq inputs (LHS, RHS)
        page = 'condeq_inputs'
        node = qnode('condeqs_LHS') << Meq.Composer(children=LHS,
                                                    plot_label=labels)
        JEN_bookmarks.create(node, page=page, viewer='Collections Plotter')
        reqseq.append(node)
        node = qnode('condeqs_RHS') << Meq.Composer(children=RHS,
                                                    plot_label=labels)
        JEN_bookmarks.create(node, page=page, viewer='Collections Plotter')
        reqseq.append(node)
      
      # Visualization of the IOM solvables (MeqParms):
      node = qnode('IOM_solvable') << Meq.Composer(children=IOM_parms,
                                                   plot_label=IOM_labels)
      JEN_bookmarks.create(node, page=name, viewer='Collections Plotter')
      reqseq.append(node)

      # Visualization of solvables (MeqParms):
      if solve_bias:
        dcoll = self.dcoll_TecBias_residuals(bookpage=name)
        reqseq.append(dcoll)

      # Make the final reqseq:
      qnode << Meq.ReqSeq(children=reqseq)
      
    if show:
      display.subtree(qnode, recurse=5)
    return qnode



  #-------------------------------------------------------
  # Visualisation
  #-------------------------------------------------------

  def dcoll_TecBias_residuals(self, bookpage='TecBias'):
    """Make an rvsi plot of the TecBias residuals, i.e. the residuals
    between simulated and estimated TecBiases"""
    cc1 = []
    cc2 = []
    for k,pair in enumerate(self._pair['obj']):
      istat = self._pair['iistat'][k]               # station nr (0,1,2,3,...)
      cc = pair.TEC_bias_residual()                 # list of 1 or 2 nodes
      if not cc[0] in cc1:
        cc1.append(Meq.ToComplex(istat, cc[0]))
      if len(cc)>1:
        if not cc[1] in cc2:
          isat = self._pair['iisat'][k]             # satellite nr (0,1,2,3,...)
          cc2.append(Meq.ToComplex(istat, cc[0]))

    size = 16                                       # symbol size
    if len(cc2)==0:
      # All residuals are pair-residuals:
      rr = MG_JEN_dataCollect.dcoll (self.ns, cc1,
                                     scope='TecBias', tag='residuals',
                                     bookpage=bookpage,
                                     color='magenta', style='diamond',
                                     size=size, pen=2,
                                     xlabel='station nr',
                                     ylabel='TecBias residual (TECU)',
                                     mean_circle=False,
                                     type='realvsimag', errorbars=False)

    else:
      # Plot the station- and satellite residuals with different colors:
      dcolls = []
      rr = MG_JEN_dataCollect.dcoll (self.ns, cc1,
                                     scope='TecBias', tag='stations',
                                     color='blue', size=size, pen=2,
                                     mean_circle=False,
                                     type='realvsimag', errorbars=False)
      dcolls.append(rr)
      rr = MG_JEN_dataCollect.dcoll (self.ns, cc2,
                                     scope='TecBias', tag='satellites',
                                     color='red', style='triangle',
                                     size=size, pen=2,
                                     mean_circle=False,
                                     xlabel='station or satellite nr',
                                     ylabel='TecBias residual (TECU)',
                                     type='realvsimag', errorbars=False)
      dcolls.append(rr)
      # Concatenate: NB: nodename -> dconc_scope_tag
      rr = MG_JEN_dataCollect.dconc(self.ns, dcolls,
                                    scope='TecBias', tag='residuals',
                                    bookpage=bookpage)
    return rr['dcoll']


  #----------------------------------------------------------------

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


TDLCompileMenu('GPS Array',
               TDLCompileOption('TDL_nstat','nr of GPS stations',[3,1,2,3,4,5,10], more=int),
               TDLCompileOption('TDL_nsat','nr of GPS satellites',[3,1,2,3,4,5,10], more=int),
               TDLCompileOption('TDL_pair_based_bias','indep. bias per sat/stat pair',[True,False]),
               TDLCompileOption('TDL_value_TecBias','nominal (TECU) of simulated',
                                [0.0,-1.0,10.0], more=float),
               TDLCompileOption('TDL_stddev_TecBias','stddev (TECU) of simulated',
                                [20.0,1.0,5.0,10.0,100.0], more=float),
               TDLCompileOption('TDL_show_array','Show the GPSArray (rvsi)',[True,False]),
               )
TDLCompileMenu('SIM definition',
               TDLCompileOption('TDL_ndeg_SIM','poldeg of SIM TEC0(long,lat)',[2,0,1,2,3,4,5], more=int),
               )
TDLCompileMenu('MIM definition',
               TDLCompileOption('TDL_define_MIM','Just define the MIM',[True,False]),
               TDLCompileOption('TDL_ndeg_MIM','poldeg of MIM TEC0(long,lat)',[1,0,1,2,3,4,5], more=int),
               )
TDLCompileMenu('solution',
               TDLCompileOption('TDL_solve_MIM','Solve (for the MIM parameters)',[True,False]),
               TDLCompileOption('TDL_time_deg_MIM','poldeg of pp time-solution',[2,0,1,2,3,4], more=int),
               TDLCompileOption('TDL_subtiling_MIM','subtiling (time)',[None,1,2,3,4], more=int),
               TDLCompileOption('TDL_num_iter','max nr of solver iterations',[10,3,5,20,50], more=int),
               TDLCompileOption('TDL_solve_for_TecBias','Solve for TEC bias as well',[False,True]),
               )
# TDLCompileOption('TDL_cache_policy','Node result caching policy',[100,0], more=int);


#-----------------------------------------------------------------------------------------

def _define_forest(ns):

  cc = []
  
  gpa = GPSArray(ns,
                 nstat=TDL_nstat, nsat=TDL_nsat, 
                 longlat=[-0.1,0.1],
                 stddev_pos=dict(stat=[0.4,0.4],
                                 # sat=[0.2,0.2]),
                                 sat=[0.4,0.4]),
                 simul_TecBias=dict(stddev=TDL_stddev_TecBias, value=TDL_value_TecBias),
                 pair_based_TecBias=TDL_pair_based_bias,
                 move=True)
  gpa.display(full=True)

  if 1:
    # The simulated IOM provide the 'measured' GPS data
    sim = MIM.MIM(ns, 'sim', ndeg=TDL_ndeg_SIM, simulate=True)
    sim.display(full=True)

    if 1:
      cc.append(gpa.plot_modelTEC(sim))
      cc.append(gpa.plot_geoSz(sim))

    if TDL_show_array:
      # NB: Do this AFTER MIM, because of pierce points
      cc.append(gpa.rvsi_longlat())

  if TDL_solve_MIM or TDL_define_MIM:
    # Define the MIM for whose parameters (pp) we solve:
    mim = MIM.MIM(ns, 'mim', ndeg=TDL_ndeg_MIM,
                  tiling=TDL_subtiling_MIM,
                  time_deg=TDL_time_deg_MIM)
    mim.display(full=True)
    # cc.append(gpa.plot_modelTEC(mim))

    if TDL_solve_MIM:
      reqseq = gpa.solveIOM(mim, sim,
                            solve_bias=TDL_solve_for_TecBias,
                            num_iter=TDL_num_iter,
                            show=True)
      cc.append(reqseq)

  ns.result << Meq.Composer(children=cc)
  return True

#---------------------------------------------------------------
#---------------------------------------------------------------


TDLRuntimeMenu('single domain',
               TDLRuntimeOption('TDL_time_interval','time interval (s)',
                                [300,1,30,90,300,900,3600,3*3600,12*3600], more=float),
               )

def _tdl_job_exec_single_domain (mqs, parent):
    """Execute the forest, starting at the named node"""
    # mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    dt = float(TDL_time_interval)
    domain = meq.domain(1.0e8,1.1e8,-dt/2,dt/2)          # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=max(1,int(dt/30)))
    request = meq.request(cells, rqid=meq.requestid(int(1000*random.random())))
    result = mqs.meq('Node.Execute',record(name='result', request=request))


TDLRuntimeMenu('sequence',
               TDLRuntimeOption('TDL_num_time_steps','nr of time steps',[10,1,3,10,30,100], more=int),
               TDLRuntimeOption('TDL_time_step_size','time-step size (s)',[30,100,300], more=int),
               )

def _tdl_job_exec_sequence (mqs, parent):
    """Execute the forest, starting at the named node"""
    # mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    n2 = int(TDL_num_time_steps/2)
    for it in range(-n2,n2):
      t1 = it*TDL_time_step_size                     # usually: 30 sec steps 
      t2 = t1+0.0001                                 # ....?
      domain = meq.domain(1.0e8,1.1e8,t1,t2)         # (f1,f2,t1,t2)
      cells = meq.cells(domain, num_freq=1, num_time=1)
      request = meq.request(cells, rqid=meq.requestid(it+TDL_num_time_steps))
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
                   simul_TecBias=dict(stddev=1.0, value=0.0),
                   pair_based_TecBias=True,
                   move=True)
    gpa.display(full=True)

    if 0:
      xxx = dict(nodes=range(3), labels=['xxx','yy','z'])
      gpa.solvable(merge=xxx, show=True)

    if 0:
      gpa.longlat0(show=True)

    if 0:
      node = gpa.rvsi_longlat()
      display.subtree(node,node.name)

    if 1:
      sim = MIM.MIM(ns, 'sim', ndeg=1, simulate=True)
      sim.display(full=True)

      if 1:
        gpa.plot_geoSz(sim, show=True)

      if 0:
        gpa.plot_modelTEC(sim, show=True)

      if 0:
        mim = MIM.MIM(ns, 'mim', ndeg=1)
        mim.display(full=True)
        gpa.solveIOM(mim, sim, show=True)


      
#===============================================================

