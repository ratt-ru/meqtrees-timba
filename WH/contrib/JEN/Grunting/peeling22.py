# ../contrib/JEN/Grunt/peeling22.py

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

from Timba.Contrib.JEN.Grunt import Joneset22
from Timba.Contrib.JEN.Grunt import Visset22

import Meow


# Run-time menu:
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[30,48,96,20,10,5,2,1]);
Meow.Utils.include_imaging_options();
TDLRuntimeMenu("Solver options",*Meow.Utils.solver_options());
  
# Compile-time menu:
TDLCompileOption('num_stations',"Number of stations",[5,27,14,3,4,5,6,7,8,9,10], more=int);
TDLCompileMenu("Source distribution",
               TDLOption('grid_spacing',"grid_spacing (arcmin)",[1,2,3,4,5,10,20], more=int),
               TDLOption('source_pattern',"source pattern",
                         ['ps1','ps2','ps3','ps4','ps5','ps9','cps'], more=str),
               );
TDLCompileMenu("Source parameters",
               TDLCompileOption('flux_factor',"Successive flux mult factor",
                                [1.0,0.5,0.4,0.3,0.2,0.1,2.0,5.0,10.0], more=float),
               TDLOption('polarization',"source polarization",
                         ['unpol','Q','U','V','QU','QUV','UV','QV'], more=str),
               );
TDLCompileOption('rmsNoise',"rms (gaussian) noise added to data",[0.0,0.01,0.1], more=float);
TDLCompileOption('predict_window',"nr of sources in predict-window",[1,2,3,4], more=int);
TDLCompileOption('peel_group',"nr of sources per peel-group",['all',2,3,4,5,10], more=int);
TDLCompileOption('insert_solver',"Insert solver(s)",[True, False]);
TDLCompileOption('repeel',"re-peel a second time",[True,False]);
TDLCompileOption('num_iter_peel',"max nr of peeling iterations",[3,1,2,4,5,10,20,None], more=int);
TDLCompileOption('num_iter_repeel',"max nr of re-peeling iterations",[3,1,2,4,5,10,20,None], more=int);
TDLCompileOption('cache_policy',"Node result caching policy",[100,0], more=int);

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

if peel_group=='all': peel_group = len(LM)


#===================================================================
#===================================================================

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);

  # Make a solver-chain object:
  # sc = JEN_SolverChain.SolverChain(ns, array=array)

  #-------------------------------------------------------------------------- 
  # The input 'data' is a Patch with all (uncorrupted) sources:
  allsky = Meow.Patch(ns,'nominall',observation.phase_centre);

  # There is a separate solver for each source.
  # The predicted visibilities for each solver are in patches,
  # each of which contains the sum of the visibilities
  # from one or more sources: the source itself, and zero or more
  # fainter ones. The latter is to reduce the contamination.
  predicted = []
  corrupted = []
  jones = []
  for isrc in range(len(LM)):
    jones.append('placeholder')
    predicted.append(Meow.Patch(ns,'predicted_S'+str(isrc),
                                observation.phase_centre));

  #-----------------------------------------------------------------------
  # create sources
  global I,Q,U,V

  for isrc in range(len(LM)):
    # Create source nr isrc:
    src = 'S'+str(isrc);                          # source label
    l,m = LM[isrc];                               # arcmin
    print '\n**',src,': [I,Q,U,V]=',[I,Q,U,V],' [l,m]=',[l,m],'arcmin\n'

    l *= ARCMIN;                                  # rad
    m *= ARCMIN;                                  # rad
    src_dir = Meow.LMDirection(ns,src,l,m);
    source = Meow.PointSource(ns,src,src_dir, I=I, Q=Q, U=U, V=V);

    # Add the uncorrupted source to the allsky patch
    allsky.add(source);

    # Convert the source to visibilities and corrupt it with EJones. 
    # Then add it to the list of corrupted components.
    node_groups = ['Parm',src]     
    for p in ANTENNAS:
      # v = 0.5*(1+isrc)
      v = 1.0
      # phase = ns.Ephase(src)(p) << Meq.Parm(v/10, node_groups=node_groups,
      #                                       tags=[src,'Ephase','EJones']);
      # gain = ns.Egain(src)(p) << Meq.Parm(1+v, node_groups=node_groups,
      #                                     tags=[src,'Egain','EJones']);
      # cxparm = ns.E(src)(p) << Meq.Polar(gain,phase);
      # sc.cxparm(cxparm, scope=src)
      # sc.cxparm(cxparm, scope='repeel_'+src)

    jones[isrc] = Joneset22.GJones(ns, quals=src, stations=ANTENNAS)
    jones[isrc].display(full=True)
    # corrupted.append(Meow.CorruptComponent(ns,source,'E',station_jones=ns.E(src)));
    corrupted.append(Meow.CorruptComponent(ns, source, 'G',
                                           station_jones=jones[isrc].matrixet()));

    # Add the corrupted source to the relevant prediction patches,
    # i.e. the patch that contains the source itself, and also the patches
    # for predict_window - 1 earlier (brighter) sources. The idea is to
    # reduce contamination by fainter sources by including them in the
    # predict when solving for parameters in the direction of the
    # peeling source. 
    for i in range(predict_window):
      if isrc-i>=0:
        predicted[isrc-i].add(corrupted[isrc]);

    # Adjust the flux for the next source:
    I *= flux_factor 
    Q *= flux_factor      
    U *= flux_factor      
    V *= flux_factor      

  # return True

  # Convert the corrupted and predicted cohsets into Visset22 objects:
  for isrc in range(len(LM)):
    # Create source nr isrc:
    src = 'S'+str(isrc);                          # source label
    corrupted[isrc] = Visset22.Visset22 (ns, quals=src, label='corrupted', polrep='linear',
                                         cohset=corrupted[isrc].visibilities(array,observation),
                                         array=array)
    corrupted[isrc]._pgm.merge(jones[isrc]._pgm)
    predicted[isrc] = Visset22.Visset22 (ns, quals=src, label='predicted', polrep='linear',
                                         cohset=predicted[isrc].visibilities(array,observation),
                                         array=array)
    predicted[isrc]._pgm.merge(jones[isrc]._pgm)
    predicted[isrc].display(full=True)

  # return True

  # The input 'measured' uv-data (cohset) is the sum of the uncorrupted sources: 
  # sc.cohset(allsky.visibilities(array,observation))
  vis = Visset22.Visset22 (ns, quals=[], label='data',
                           polrep='linear',
                           simulate=True,
                           cohset=allsky.visibilities(array,observation),
                           array=array)
  vis.display(full=True)

  if rmsNoise>0.0:
    vis.addGaussianNoise(stddev=0.1, visu=True)

  # return True


  #--------------------------------------------------------------------------
  # If the sources are to be repeeled, they are are treated in groups.
  # The reason is that it is pointless to peel sources whose visibilities
  # are smaller than the peeling remnants of brighter sources.
  
  global peel_group
  isrc1 = 0
  
  while isrc1<len(LM):
    iisrc = range(isrc1,min(isrc1+peel_group, len(LM)))
    print '\n**',len(LM),peel_group,isrc1,':',iisrc
    
    # Make sequence of peeling stages for sources iisrc:
    for isrc in iisrc:
      src = 'S'+str(isrc);                           # source label
      scope = src
      print '--',scope
      
      predict = predicted[isrc]
      corrupt = corrupted[isrc]

      # Optional: insert a solver for the parameters related to this source:
      if insert_solver:
        vis.make_solver(predict, qual=['peel',src],
                        # parm_tags=src, parm_group=src,
                        num_iter=num_iter_peel)
      
      # Subtract (peel) the current peeling source:
      vis.binop('Subtract', corrupt, qual=['peel',src], visu=True)

    # -----------------------------------------------------------------------
    if insert_solver and repeel:
      # Second series: re-peel the residuals with each source added-in
      # sequentially. This is equivalent to peeling without contamination
    
      for isrc in iisrc:
        src = 'S'+str(isrc);                         # source label
        scope = 'repeel_'+src
        print '  --',scope
        
        predict = predicted[isrc]
        corrupt = corrupted[isrc]
        
        # Add the (slightly wrong) current peeling source:
        vis.binop('Add', corrupt, qual=['unpeel',src])
        
        vis.make_solver(predict, qual=['repeel',src],
                        # parm_tags=src, parm_group=src,
                        num_iter=num_iter_repeel)

        # Subtract the current peeling source:
        vis.binop('Subtract', corrupt, qual=['repeel',src], visu=True)

    # Continue peeling (and re-peeling) the next peel_group:
    isrc1 += peel_group
          
  #----------------------------------------------------------------------
  # Insert reqseq that first executes the solvers in order of creation,
  # and then passes on the final residuals (in cohset):
  if insert_solver:
    vis.insert_accumulist_reqseq()

  # Attach the current cohset to the sinks
  vis.make_sinks(output_col='RESIDUALS', vdm='vdm')
  vis.display(full=True)

  # Finished: 
  return True




#==============================================================================
#==============================================================================

def _tdl_job_1_peel_away (mqs,parent):
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
