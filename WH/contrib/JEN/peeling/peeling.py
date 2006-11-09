# ../contrib/JEN/peeling/peeling.py
# copied from Day3/demo3_...

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN import MG_JEN_dataCollect

import Meow

# Run-time menu:
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,48,96,20,10,5,2,1]);
Meow.Utils.include_imaging_options();
TDLRuntimeMenu("Solver options",*Meow.Utils.solver_options());
  
# Compile-time menu:
TDLCompileMenu("Source distribution",
  TDLOption('grid_spacing',"grid_spacing (arcmin)",[1,2,3,4,5,10,20]),
  TDLOption('source_pattern',"source pattern",['cps','ps1','ps2','ps3','ps4','ps5','ps9']),
);
TDLCompileOption('flux_factor',"Successive flux mult factor",[1.0,0.5,0.4,0.3,0.2,0.1]);
TDLCompileOption('condeq_group',"nr of ifrs in condeq-group",[1,2,3,4]);
TDLCompileOption('predict_window',"nr of sources in predict-window",[1,2,3,4]);
TDLCompileOption('num_stations',"Number of stations",[5, 27,14,3]);
TDLCompileOption('insert_solver',"Insert solver(s)",[True, False]);
TDLCompileOption('num_iter',"max nr of solver iterations",[1,2,3,5,10,20,None]);
TDLCompileOption('cache_policy',"Node result caching policy",[0,100]);

# Alternative: see tdl_job below
# Settings.forest_state.cache_policy = 100

#================================================================================

# define antenna list
ANTENNAS = range(1,num_stations+1);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
# I = 1; Q = .2; U = .1; V = -0.02;
I = 1.0; Q = 0.0; U = 0.0; V = 0.0;

a = grid_spacing
if source_pattern=='cps':
  # NB: Problems with result shape if LM=[(0,0)]: 1D result!
  LM = [(0,0)]
elif source_pattern=='ps1':
  LM = [(0,a)]
elif source_pattern=='ps2':
  # NB: Non-first solvers cannot find solvable parms (spids)
  #     (i.e. only the solver closest to the sinks works)
  LM = [(0,0),(a,a)]
elif source_pattern=='ps3':
  LM = [(0,0),(a,a),(0,a)]
elif source_pattern=='ps4':
  LM = [(0,0),(a,a),(0,a),(0,-a)]
elif source_pattern=='ps5':
  LM = [(0,0),(a,a),(0,a),(0,-a),(-a,-a)]
elif source_pattern=='ps9':
  LM = [(-a,-a),(-a,0),(-a,a),
        ( 0,-a),( 0,0),( 0,a), 
        ( a,-a),( a,0),( a,a)];
else:
  LM = [(0,0),(a,a),(0,a)]

#===================================================================
#===================================================================

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);

  #--------------------------------------------------------------------------
  # Start some lists for the accumulation of nodes for bookmark pages 
  ifr1 = (1,4)                                     # selected ifr
  p1 = 1                                           # selected station
  bm_resid = []        
  bm_condeq = []                 
  bm_solver = []               
  bm_cxparm = []               
  
  # The input 'data' is a Patch with all (uncorrupted) sources:
  allsky = Meow.Patch(ns,'nominall',observation.phase_centre);

  # There is a separate solver for each source.
  # The predicted visibilities for each solver are in patches,
  # each of which contains the sum of the visibilities
  # from one or more sources: the source itself, and zero or more
  # fainter ones. The latter is to reduce the contamination.
  predicted = []
  corrupted = []
  dc_cxparm = []
  for isrc in range(len(LM)):
    predicted.append(Meow.Patch(ns,'predicted_S'+str(isrc),
                                observation.phase_centre));

  # create sources
  solvable = dict()
  I = 1.0/flux_factor                             # needed...?
  print 'I,Q,U,V =',I,Q,U,V

  #-----------------------------------------------------------------------

  for isrc in range(len(LM)):
    # Create source nr isrc:
    I *= flux_factor                              # In order of decreasing flux
    src = 'S'+str(isrc);                          # source label
    l,m = LM[isrc];                               # arcmin
    l *= ARCMIN;                                  # rad
    m *= ARCMIN;                                  # rad
    src_dir = Meow.LMDirection(ns,src,l,m);
    source = Meow.PointSource(ns,src,src_dir, I=I, Q=Q, U=U, V=V);

    # Add the source to the allsky patch
    allsky.add(source);

    # Make a corrupted source:
    solvable[src] = []
    cxparms = []
    node_groups = ['Parm',src]     
    for p in ANTENNAS:
      phase = ns.Ephase(src)(p) << Meq.Parm(0.0, node_groups=node_groups);
      gain = ns.Egain(src)(p) << Meq.Parm(1.0, node_groups=node_groups);
      solvable[src].extend([phase,gain])
      cxparm = ns.E(src)(p) << Meq.Polar(gain,phase);
      # ns.E(src)(p) << Meq.Matrix22(1+0j,0,0,1+0j);
      cxparms.append(cxparm)
    corrupted.append(Meow.CorruptComponent(ns,source,'E',station_jones=ns.E(src)));
    if True:
      dc = MG_JEN_dataCollect.dcoll (ns, cxparms, 
                                     scope=src, tag='parm',
                                     color='red',
                                     # style=Cohset.plot_style()[corr],
                                     # size=Cohset.plot_size()[corr],
                                     # pen=Cohset.plot_pen()[corr],
                                     type='realvsimag', errorbars=True)
      dc_cxparm.append(dc['dcoll'])              # to be appended to reqseq list
      bm_cxparm.append(dc['dcoll'])              #   append to bookmark list

    # Add the corrupted source to the relevant prediction patches,
    # i.e. the patch for the source itself, and the patches for
    # predict_window-1 earlier (brighter) sources. The idea is to reduce
    # contamination by fainter sources by including them in the
    # predict when solving for parameters in the direction of the
    # peeling source. 
    for i in range(predict_window):
      if isrc-i>=0:
        print 'isrc=',isrc,': i=',i
        predicted[isrc-i].add(corrupted[isrc]);

  #--------------------------------------------------------------------------
  # Make sequence of peeling stages:
  cohset = allsky.visibilities(array,observation);
  bm_resid.append(cohset(*ifr1))        
  cc_reqseq = []

  for isrc in range(len(LM)):
    src = 'S'+str(isrc);                           # source label
    print src
    
    predict = predicted[isrc].visibilities(array,observation);
    corrupt = corrupted[isrc].visibilities(array,observation);

    # Optional: insert a solver for the parameters related to this source:
    if insert_solver:
      condeqs = []
      condeqs_XX = []
      if condeq_group==1:
        # Direct comparison of measured with predicted
        for ifr in array.ifrs():
          condeq = ns.condeq(src)(*ifr) << Meq.Condeq(cohset(*ifr),
                                                      predict(*ifr));
          condeqs.append(condeq)
          condeqs_XX.append(ns.condeq_XX(src)(*ifr) << Meq.Selector(condeq, index=0))
        bm_condeq.append(ns.condeq(src)(*ifr1))      # append to bookmark list

      else:
        # Comparison of groups of multiplied ifrs (contamination reduction)
        ifrs = array.ifrs()      
        for i in range(len(ifrs)-1-condeq_group):
          meas = []
          pred = []
          for j in range(i,i+condeq_group):
            print '** i=',i,': ifrs[',j,'] =',ifrs[j]
            meas.append(cohset(*ifrs[j]))
            pred.append(predict(*ifrs[j]))
          condeq = ns.condeq(src)(i) << Meq.Condeq(ns.meas(src)(i) << Meq.Multiply(children=meas),
                                                   ns.pred(src)(i) << Meq.Multiply(children=pred));
          condeqs.append(condeq)
          condeqs_XX.append(ns.condeq_XX(src)(i) << Meq.Selector(condeq, index=0))
        bm_condeq.append(ns.condeq(src)(2))        # append to bookmark list

          
      solver = ns.solver(src) << Meq.Solver(children=condeqs,
                                            solvable=solvable[src],
                                            parm_group=hiid(src),
                                            # child_poll_order=cpo,
                                            num_iter=num_iter);
      cc_reqseq.append(solver)                     # append to reqseq list
      bm_solver.append(solver)                     # append to bookmark list
      if True:
        dc = MG_JEN_dataCollect.dcoll (ns, condeqs_XX, 
                                       scope=src, tag='condeq_XX',
                                       color='blue',
                                       # style=Cohset.plot_style()[corr],
                                       # size=Cohset.plot_size()[corr],
                                       # pen=Cohset.plot_pen()[corr],
                                       type='realvsimag', errorbars=True)
        cc_reqseq.append(dc['dcoll'])              # append to reqseq list
        cc_reqseq.append(dc_cxparm[isrc])          # append to reqseq list
        if isrc == len(LM)-1:                      # last one only:
          bm_condeq.append(dc['dcoll'])            #   append to bookmark list
          bm_cxparm.append(dc['dcoll'])            #   append to bookmark list
                          

    # Subtract the current peeling source:
    for ifr in array.ifrs():
      ns.residual(src)(*ifr) << Meq.Subtract(cohset(*ifr),
                                             corrupt(*ifr));
    cohset = ns.residual(src)                      # the new residuals
    bm_resid.append(cohset(*ifr1))                 # append to bookmark list


  #----------------------------------------------------------------------
  # Insert reqseq that first executes the solvers in order of creation,
  # and then passes on the final residuals (in cohset):
  if insert_solver:
    n = len(cc_reqseq)
    cc_reqseq.append(0)                            # dummy
    for ifr in array.ifrs():
      cc_reqseq[n] = cohset(*ifr)
      ns.reqseq_solvers(*ifr) << Meq.ReqSeq(children=cc_reqseq,
                                            result_index=n,
                                            cache_num_active_parents=1);
    cohset = ns.reqseq_solvers


  #----------------------------------------------------------------------
  # Attach the current cohset to the sinks
  for p,q in array.ifrs():
    ns.sink(p,q) << Meq.Sink(cohset(p,q),
                             station_1_index=p-1,
                             station_2_index=q-1,
                             output_col='DATA');
  ns.vdm << Meq.VisDataMux(*[ns.sink(*ifr) for ifr in array.ifrs()]);

  # Finished: Make bookmark page(s) for the accumulated nodes:
  JEN_bookmarks.create(bm_resid, 'residuals')
  JEN_bookmarks.create(bm_condeq, 'condeqs')
  JEN_bookmarks.create(bm_solver, 'solvers')
  JEN_bookmarks.create(bm_cxparm, 'parms')
  return True




#==============================================================================
#==============================================================================

def _tdl_job_1_simulate_MS (mqs,parent):
  mqs.meq('Set.Forest.State', record(state=record(cache_policy=cache_policy)))
  req = Meow.Utils.create_io_request();
  mqs.execute('vdm',req,wait=False);
  return True
                                     
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);
  return True




#==============================================================================
# This is a useful thing to have at the bottom of the script.
# It allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
