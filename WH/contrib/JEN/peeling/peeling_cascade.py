# ../contrib/JEN/peeling/peeling_cascade.py
# A version of peeling.py with a cascade of solvers.
# This does not work (yet) due to request-problems.

# standard preamble
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq
import math

from Timba.Contrib.JEN.util import JEN_bookmarks

import Meow

# Run-time menu:
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,48,96]);
Meow.Utils.include_imaging_options();
TDLRuntimeMenu("Solver options",*Meow.Utils.solver_options());
  
# Compile-time menu:
TDLCompileMenu("Source distribution",
  TDLOption('grid_spacing',"grid_spacing (arcmin)",[1,2,3,4,5,10,20]),
  TDLOption('source_pattern',"source pattern",['cps','ps1','ps2','ps3','ps9']),
);
TDLCompileOption('flux_factor',"Successive flux reduction factor",[0.5,0.4,0.3,0.2,0.1]);
TDLCompileOption('predict_window',"nr of sources in predict-window",[1,2,3,4]);
TDLCompileOption('num_stations',"Number of stations",[5, 27,14,3]);
TDLCompileOption('insert_solver',"Insert solver(s)",[True, False]);

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
  
  # The input 'data' is a Patch with all (uncorrupted) sources:
  allsky = Meow.Patch(ns,'nominall',observation.phase_centre);

  # There is a separate solver for each source.
  # The predicted visibilities for each solver are in patches,
  # each of which contains the sum of the visibilities
  # from one or more sources: the source itself, and zero or more
  # fainter ones. The latter is to reduce the contamination.
  predicted = []
  corrupted = []
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
    node_groups = ['Parm',src]     
    for p in ANTENNAS:
      phase = ns.Ephase(src)(p) << Meq.Parm(0.0, node_groups=node_groups);
      gain = ns.Egain(src)(p) << Meq.Parm(1.0, node_groups=node_groups);
      solvable[src].extend([phase,gain])
      ns.E(src)(p) << Meq.Polar(gain,phase);
      # ns.E(src)(p) << Meq.Matrix22(1+0j,0,0,1+0j);
    corrupted.append(Meow.CorruptComponent(ns,source,'E',station_jones=ns.E(src)));

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
  # Start some lists for the accumulation of nodes for bookmark pages 
  ifr1 = (1,4)                                     # selected ifr
  bm_resid = []        
  bm_condeq = []                 
  bm_solver = []               

  #--------------------------------------------------------------------------
  # Make sequence of peeling stages:
  cohset = allsky.visibilities(array,observation);
  bm_resid.append(cohset(*ifr1))        

  for isrc in range(len(LM)):
    src = 'S'+str(isrc);                           # source label
    
    predict = predicted[isrc].visibilities(array,observation);
    corrupt = corrupted[isrc].visibilities(array,observation);

    # Optional: make a vector of condeqs for a solver:
    if insert_solver:
      condeqs = []
      for ifr in array.ifrs():
        condeq = ns.condeq(src)(*ifr) << Meq.Condeq(cohset(*ifr),predict(*ifr));
        condeqs.append(condeq);
        if ifr==ifr1: bm_condeq.append(condeq)     # append to bookmark list

    # Subtract the current peeling source:
    for ifr in array.ifrs():
      ns.residual(src)(*ifr) << Meq.Subtract(cohset(*ifr),corrupt(*ifr));
    cohset = ns.residual(src)                      # the new residuals

    # Optional: insert a reqseq for a solver:
    if insert_solver:
      solver = ns.solver(src) << Meq.Solver(children=condeqs,
                                            solvable=solvable[src],
                                            parm_group=hiid(src),
                                            # child_poll_order=cpo,
                                            num_iter=3);
      bm_solver.append(solver)                     # append to bookmark list
      for ifr in array.ifrs():
        ns.reqseq(src)(*ifr) << Meq.ReqSeq(solver, cohset(*ifr),
                                           result_index=1,
                                           cache_num_active_parents=1);
      cohset = ns.reqseq(src)
      
    bm_resid.append(cohset(*ifr1))                 # append to bookmark list


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
  return True




#==============================================================================
#==============================================================================

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('vdm',req,wait=False);
  
  
def _tdl_job_2_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("K Jones",["K:S0:1","K:S0:9"],["K:S1:2","K:S1:9"]),
  Meow.Bookmarks.PlotPage("E Jones",["E:S0","E:S1"],["E:S3","E:S4"]),
  Meow.Bookmarks.PlotPage("G Jones",["G:1","G:2"],["G:3","G:3"])
]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
