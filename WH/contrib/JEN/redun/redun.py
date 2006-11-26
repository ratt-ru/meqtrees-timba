# ../contrib/JEN/redun/redun.py

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

from Timba.Contrib.JEN.util import JEN_SolverChain
# from Timba.Contrib.JEN.util import JEN_bookmarks
# from Timba.Contrib.JEN import MG_JEN_dataCollect

import Meow

# Run-time menu:
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,48,96,20,10,5,2,1]);
Meow.Utils.include_imaging_options();
TDLRuntimeMenu("Solver options",*Meow.Utils.solver_options());
  
# Compile-time menu:
TDLCompileMenu("Source distribution",
               TDLOption('grid_spacing',"grid_spacing (arcmin)",[1,2,3,4,5,10,20]),
               TDLOption('source_pattern',"source pattern",
                         ['ps1','ps2','ps3','ps4','ps5','ps9','cps']),
               );
TDLCompileMenu("Source parameters",
               TDLCompileOption('flux_factor',"Successive flux mult factor",
                                [1.0,0.5,0.4,0.3,0.2,0.1,2.0,5.0,10.0]),
               TDLOption('polarization',"source polarization",
                         ['unpol','Q','U','V','QU','QUV','UV','QV']),
               );
# TDLCompileOption('predict_window',"nr of sources in predict-window",[1,2,3,4]);
# TDLCompileOption('repeel',"re-peel a second time",[True,False]);
TDLCompileOption('num_stations',"Number of stations",[5, 27,14,3]);
TDLCompileOption('rms_noise',"Rms noise (Jy)",[0.1,0.01,0.001,0.0,1.0]);
# TDLCompileOption('insert_solver',"Insert solver(s)",[True, False]);
TDLCompileOption('num_iter',"max nr of solver iterations",[3,1,2,4,5,10,20,None]);
TDLCompileOption('cache_policy',"Node result caching policy",[100,0]);
TDLCompileOption('visualization_mode',"Visualization",['full','min','off']);

# Alternative: see tdl_job below
# Settings.forest_state.cache_policy = 100

#================================================================================

# define antenna list
ANTENNAS = range(1,num_stations+1);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = 0.1; U = -0.1; V = -0.02;
I = 1.0; Q = 0.0; U = 0.0; V = 0.0;
if True:
  if polarization in ['Q','QU','QUV']: Q = 0.1
  if polarization in ['U','QU','QUV']: U = -0.1
  if polarization in ['V','UV','QV','QUV']: V = 0.02

a = grid_spacing
if source_pattern=='cps':
  # NB: Problems with result shape if LM=[(0,0)]: 1D result!!!!!!!!!!!!!!1    
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

  # Make a solver-chain object:
  sc = JEN_SolverChain.SolverChain(ns, array=array)

  #-------------------------------------------------------------------------- 
  # Make the cohset of input visbilities
  # (a Patch with all (uncorrupted) sources)
  allsky = Meow.Patch(ns,'nominall',observation.phase_centre);
  global I,Q,U,V
  for isrc in range(len(LM)):
    src = 'S'+str(isrc);                          # source label
    l,m = LM[isrc];                               # arcmin
    print '\n**',src,': [I,Q,U,V]=',[I,Q,U,V],' [l,m]=',[l,m],'arcmin\n'
    l *= ARCMIN;                                  # rad
    m *= ARCMIN;                                  # rad
    src_dir = Meow.LMDirection(ns,src,l,m);
    source = Meow.PointSource(ns,src,src_dir, I=I, Q=Q, U=U, V=V);
    # Add the source to the allsky patch
    allsky.add(source);
  sc.cohset(allsky.visibilities(array,observation))

  # Corrupt the input visibilities:
  scope = 'corrupt'
  for p in ANTENNAS:
    v = (p+1)/10.0
    print 'p =',p,'->',v
    phase = ns.Ephase(scope)(p) << Meq.Constant(0.0)
    gain = ns.Egain(scope)(p) << Meq.Constant(1+v)
    cxparm = ns.E(scope)(p) << Meq.Polar(gain,phase);
    sc.cxparm(cxparm, scope=scope)
  sc.corrupt(jones=ns.E(scope), rms=rms_noise, page='e2e')


  # Attach the correction Jones matrices (to be solved for):
  scope = 'correct'
  node_groups = ['Parm',scope]     
  for p in ANTENNAS:
    phase = ns.Ephase(scope)(p) << Meq.Parm(0.0, node_groups=node_groups,
                                            tags=[scope,'Ephase','EJones']);
    gain = ns.Egain(scope)(p) << Meq.Parm(1.0, node_groups=node_groups,
                                          tags=[scope,'Egain','EJones']);
    cxparm = ns.E(scope)(p) << Meq.Polar(gain,phase);
    sc.cxparm(cxparm, scope=scope)
  sc.correct(jones=ns.E(scope))


  # Constrain the sum of phases and the product of gains:
  constraint = []
  if True:
    constraint = [dict(tags='Ephase', unop='Add', value=0.0),
                  dict(tags='Egain', unop='Multiply', value=1.0)]

  # Make a solver with condeqs that compare redundant spacings:
  sc.make_solver(scope=scope,
                 parm_tags=scope, parm_group=scope,
                 constraint=constraint,
                 num_iter=num_iter)

  #----------------------------------------------------------------------
  # Insert reqseq that first executes the solvers in order of creation,
  # and then passes on the final residuals (in cohset):
  sc.insert_reqseq()

  # Attach the current cohset to the sinks
  sc.make_sinks(output_col='DATA', vdm='vdm')

  # Finished: 
  return True




#==============================================================================
#==============================================================================

def _tdl_job_1_redundandize (mqs,parent):
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