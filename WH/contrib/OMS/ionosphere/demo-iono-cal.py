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

import Meow
import sky_models
import mims
import iono_geometry


# some GUI options
Meow.Utils.include_ms_options(has_input=True,tile_sizes=[1,2,5,30,48,96]);
Meow.Utils.include_imaging_options();

# solver runtime options
TDLRuntimeMenu("Solver options",*Meow.Utils.solver_options());


TDLCompileOption("sky_model","Sky model",
            [sky_models.Grid9,
             sky_models.PerleyGates,
             sky_models.PerleyGates_ps]);
TDLCompileOption("grid_stepping","Grid step, in minutes",[1,5,10,30,60,120,240]);
TDLCompileOption("ionospheric_model","Ionospheric model",
            [ mims.mim_poly,
              mims.center_tecs_only,
              mims.per_direction_tecs,
            ]);
TDLCompileOption("output_type","Output visibilities",["corrected","residual"]);

# define antenna list
ANTENNAS = range(1,28);

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;
     
def get_mep_table ():
  return "iono.mep";
  
def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray(ns,ANTENNAS);
  # create an Observation object
  observation = Meow.Observation(ns);
  
  # create a Patch for the entire observed sky
  allsky = Meow.Patch(ns,'all',observation.phase_centre);

  tecs = ns.tec;
  # create sources
  sources = [];
  global maxrad;
  maxrad = 0;
  for i,srctuple in enumerate(sky_model()):  # sky_model comes from GUI option
    l = srctuple[0]*grid_stepping; 
    m = srctuple[1]*grid_stepping;
    # figure out max image radius in arcmin
    maxrad = max(abs(l)+.5,abs(m)+.5,maxrad);
    # convert to radians
    l *= ARCMIN;
    m *= ARCMIN;
    # generate an ID for direction and source
    src = 'S'+str(i);
    # create Direction object
    src_dir = Meow.LMDirection(ns,src,l,m);
    # create source with this direction, depending on tuple type
    if len(srctuple) == 2:
      sources.append(Meow.PointSource(ns,src,src_dir,I=I,Q=Q,U=U,V=V));
    else:
      l,m,iflux,sx,sy,pa = srctuple;
      sources.append(Meow.GaussianSource(ns,src,src_dir,I=iflux,
                                         size=[sx*ARCMIN,sy*ARCMIN],phi=pa));
  # create ionospheric model
  global parmlist;
  tecs,parmlist = ionospheric_model(ns,sources,array,observation);
  
  # compute zeta-jones from model tecs
  zetas = iono_geometry.compute_zeta_jones_from_tecs(ns,tecs,sources,array,observation);
  
  for src in sources:
    # create corrupted source
    corrupt = Meow.CorruptComponent(ns,src,'Z',station_jones=zetas(src.name));
    # add to patch
    allsky.add(corrupt);
  
  # create set of nodes to compute visibilities...
  predict = allsky.visibilities(array,observation);

  # create condeqs and spigots
  condeqs = [];
  for p,q in array.ifrs():
  
    spigot = ns.spigot(p,q) << Meq.Spigot( station_1_index=p-1,
                                           station_2_index=q-1,
                                           input_col='DATA');
    pred = predict(p,q);
    ce = ns.ce(p,q) << Meq.Condeq(spigot,pred);
    condeqs.append(ce);
    if output_type == "residual":
      residual = ns.residual(p,q) << spigot - pred;
  
  # create corrected or residual data if needed
  # use zeta-jones of center source
  Z0 = zetas(sources[0].direction.name);
  if output_type == "corrected":
    what_to_correct = ns.spigot;
  else:
    what_to_correct = ns.residual;
  Meow.Jones.apply_correction(ns.corrected,what_to_correct,Z0,array.ifrs());

  # create solver node
  ns.solver << Meq.Solver(children=condeqs);
  
  # create sinks and reqseqs 
  for p,q in array.ifrs():
    reqseq = Meq.ReqSeq(ns.solver,ns.corrected(p,q),
                  result_index=1,cache_num_active_parents=1);
    ns.sink(p,q) << Meq.Sink(station_1_index=p-1,
                             station_2_index=q-1,
                                 output_col='DATA',
                                 children=reqseq
                            );
                            
  # do some searches
  
  print "Zs: ",ns.Search(name="Z:.*");
  print "Zs by name: ",ns.Search(return_names=True,name="Z:.*");
  print "Parms: ",ns.Search(return_names=True,class_name="MeqParm");
  print "Sinks or Spigots: ",ns.Search(return_names=True,class_name="MeqSink|MeqSpigot");
  print "MIM nodes: ",ns.Search(return_names=True,tags="mim");
  print "MIM solvables: ",ns.Search(return_names=True,tags=("mim","solvable"));
  print "Z family: ",[node.name for node in zetas.family()];
  print "MIM solvables from Z: ",zetas.search(return_names=True,tags=("mim","solvable"));
  print "This should be empty: ",zetas.search(no_family=True,return_names=True,tags=("mim","solvable"));
                                   
  

def _tdl_job_1_calibrate_ionosphere (mqs,parent):
  print parmlist;
  Meow.Utils.run_solve_job(mqs,parmlist);

def _tdl_job_8_clear_out_all_previous_solutions (mqs,parent,**kw):
  os.system("rm -fr iono.mep");

def _tdl_job_9_make_image (mqs,parent):
  Meow.Utils.make_dirty_image(npix=1024,arcmin=grid_stepping*2.5,
                              channels=[32,1,1]);
                              
                          



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  Meow.Bookmarks.PlotPage("TECs",["tec:S1:1","tec:S1:9"],["tec:S8:1","tec:S8:9"]),
  Meow.Bookmarks.PlotPage("TECs + Solver",["solver","tec:S1:9"],["tec:S8:1","tec:S8:9"]),
  Meow.Bookmarks.PlotPage("TECs per station",["tec:1","tec:9"],["tec:27","solver"]),
  Meow.Bookmarks.PlotPage("Z Jones",["Z:S1:1","Z:S1:9"],["Z:S8:1","Z:S8:9"])
]);


# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
