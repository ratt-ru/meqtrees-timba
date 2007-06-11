 # standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees

# MS options first
mssel = Meow.MSUtils.MSSelector(has_input=False,tile_sizes=[8,16,32]);
# MS compile-time options
TDLCompileOptions(*mssel.compile_options());
# MS run-time options
TDLRuntimeOptions(*mssel.runtime_options());
## also possible:
# TDLRuntimeMenu("MS selection options",open=True,*mssel.runtime_options());

import sky_models
TDLCompileMenu("Sky model options",sky_models);

import iono_geometry
import iono_model
TDLCompileMenu("Include ionosphere",iono_geometry,iono_model,toggle='include_ionosphere');

import beam_models
TDLCompileMenu("Include beam",beam_models,toggle='include_beam');

import gain_models
TDLCompileMenu("Include gain/phase errors",gain_models,toggle='include_gains');

TDLCompileOption("noise_stddev","Add noise, Jy",[None,1e-6,1e-3],more=float);

def _define_forest (ns):
  ANTENNAS = mssel.get_antenna_set(range(1,28));
  array = Meow.IfrArray(ns,ANTENNAS);
  observation = Meow.Observation(ns);
  Meow.Context.set(array,observation);
  stas = array.stations();

  # note how we set default image size from our current sky model
  imsel = mssel.imaging_selector(npix=512,arcmin=sky_models.imagesize());
  TDLRuntimeMenu("Imaging options",*imsel.option_list());
  
  # list of inspector nodes
  inspectors = [];
    
  # create source list
  sources = sky_models.make_model(ns,"S0");
  
  if include_ionosphere:
    # make Zjones for all positions in source list (and all stations)
    # this returns Zj which sould be qualified as Zj(srcname,station)
    # Therefore we can use Zj(srcname) as a per-stations Jones series.
    Zj = iono_model.compute_zeta_jones(ns,sources);
    # corrupt all sources with the Zj for their direction
    sources = [ src.corrupt(Zj(src.direction.name)) for src in sources ];
    # add inspectors
    inspectors += [
      ns.inspect_TECs << Meq.Composer(
        plot_label = [ "%s:%s"%(p,src.direction.name) for src in sources for p in stas ],
        *[ ns.tec(src.direction.name,p) for src in sources for p in stas ]
      ),
      ns.inspect_Z_phase << Meq.Composer(
        plot_label = [ "%s:%s"%(p,src.direction.name) for src in sources for p in stas ],
        *[ Meq.Mean(Meq.Arg(Zj(src.direction.name,p),reduction_axes="freq")) for src in sources for p in stas ]
      )
    ];
    
  if include_beam:
    # make Ejones for all positions in source list (and all stations)
    Ej = ns.E;
    beam_models.compute_E_jones(Ej,sources);
    # if E:src0:sta0 is initialized, this is a per-station matrix
    # else it is a per-source only
    per_station = Ej(sources[0].direction.name,stas[0]).initialized();
    sources = [ src.corrupt(Ej(src.direction.name),per_station=per_station) 
                for src in sources ];
    # add inspectors
    if per_station:
      ns.inspect_E_jones << Meq.Composer(dims=[0],
        plot_label = [ "%s:%s"%(p,src.direction.name) for src in sources for p in stas ],
        *[ Meq.Mean(Ej(src.direction.name,p),reduction_axes="freq")
           for src in sources for p in stas ]
      );
    else:
      ns.inspect_E_jones << Meq.Composer(dims=[0],
        plot_label = [ src.direction.name for src in sources ],
        *[ Meq.Mean(Ej(src.direction.name),reduction_axes="freq")
           for src in sources ]
      );
    inspectors.append(ns.inspect_E_jones);
    
  # now form up patch
  allsky = Meow.Patch(ns,'sky',observation.phase_centre);
  allsky.add(*sources);
  
  # add uv-plane effects
  if include_gains:
    Gj = ns.G;
    gain_models.compute_G_jones(Gj);
    allsky = allsky.corrupt(Gj);
    inspectors.append(
      ns.inspect_G_jones << Meq.Composer(dims=[0],
        plot_label = map(str,stas),
        *[ Gj(p) for p in stas  ]
      )
    );

  # get predicted visibilities
  predict = allsky.visibilities();
  
  # throw in a bit of noise
  if noise_stddev:
    # make two complex noise terms per station (x/y)
    noisedef = Meq.GaussNoise(stddev=noise_stddev)
    noise_x = ns.sta_noise('x');
    noise_y = ns.sta_noise('y');
    for p in array.stations():
      noise_x(p) << Meq.ToComplex(noisedef,noisedef);
      noise_y(p) << Meq.ToComplex(noisedef,noisedef);
    # now combine them into per-baseline noise matrices
    for p,q in array.ifrs():
      noise = ns.noise(p,q) << Meq.Matrix22(
        noise_x(p)+noise_x(q),noise_x(p)+noise_y(q),
        noise_y(p)+noise_x(q),noise_y(p)+noise_y(q)
      );
      ns.noisy_predict(p,q) << predict(p,q) + noise;
    predict = ns.noisy_predict;
    
  
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,predict,spigots=False,post=(inspectors or None));
  
  # make bookmarks for inspectors
  for node in inspectors:
    name = node.name.replace('_',' ');
    Meow.Bookmarks.Page(name).add(node,viewer="Collections Plotter");
  
  ### Make some visualizations
  ## Choose four "interesting" stations for inspection
  ## since we don't know in advance how many antennas we're going to be running with,
  ## just make a list of candidate stations, and then pick four stations from the list
  #inspect_sta_candidates = [ 10,9,18,27 ] + ANTENNAS;
  #inspect_sta = [];
  #for p in inspect_sta_candidates:
    #if p in ANTENNAS:
      #stas.append(p);
      #if len(stas) > 4:
        #break;


def _tdl_job_1_simulate_MS (mqs,parent,wait=False):
  mqs.execute('VisDataMux',mssel.create_io_request(),wait=wait);
  
  
# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
