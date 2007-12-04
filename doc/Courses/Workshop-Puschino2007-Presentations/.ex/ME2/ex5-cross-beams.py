# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

import Meow
import Meow.StdTrees
import sky_models

# some GUI options
Meow.Utils.include_ms_options(has_input=False,tile_sizes=[16,32,48,96]);
TDLRuntimeMenu("Imaging options",
    *Meow.Utils.imaging_options(npix=256,arcmin=sky_models.imagesize(),channels=[[32,1,1]]));

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;


def pseudo_wsrt_beam (E,lm):
  """This makes the nodes to compute the beam gain, E, given an lm position.
  'lm' is an input node
  'E' is an output node to which the gain will be assigned""";
  lmsq = E('lmsq') << Meq.Sqr(lm);
  lsq = E('lsq') << Meq.Selector(lmsq,index=0);
  msq = E('msq') << Meq.Selector(lmsq,index=1);
  E << Meq.Pow(Meq.Cos(Meq.Sqrt(lsq+msq)*2e-6*Meq.Freq()),3);
  
  return E;

DEG = math.pi/180.;
ARCMIN = DEG/60;
ANTENNAS = range(1,28);

TDLCompileOption("beam_model","Beam model",[pseudo_wsrt_beam]);

def _define_forest (ns):
  # create an Array object
  array = Meow.IfrArray.VLA(ns);
  # create an Observation object
  observation = Meow.Observation(ns);
  # set global context
  Meow.Context.set(array=array,observation=observation);

  # make list of source lists for three crosses
  src_lists = [ 
    sky_models.make_model(ns,'S0',0       ,0       ),
    sky_models.make_model(ns,'S1',.5*ARCMIN,.5*ARCMIN),
    sky_models.make_model(ns,'S2',1*ARCMIN,1*ARCMIN)
  ];
    
  # make master source list
  all_sources = src_lists[0]+src_lists[1]+src_lists[2];

  # build a "precise" model, by corrupting all sources with the Ej
  # for their direction
  prec_sky = Meow.Patch(ns,'prec',observation.phase_centre);
  for src in all_sources:
    Ej = ns.E(src.name);
    beam_model(Ej,src.direction.lm());
    prec_sky.add(src.corrupt(Ej,per_station=False));
    
  # now make an approximate model
  approx_sky = Meow.Patch(ns,'approx',observation.phase_centre);
  # loop over all patches
  for (n,srclist) in enumerate(src_lists):
    # make the patch
    patch = Meow.Patch(ns,'patch'+str(n),observation.phase_centre);
    patch.add(*srclist);
    # corrupt whole patch with Ej for patch centre
    corrupt_patch = patch.corrupt(ns.E(srclist[0].name),per_station=False);
    # add to the "approx" patch
    approx_sky.add(corrupt_patch);
    
  # create set of nodes to compute visibilities...
  predict1 = prec_sky.visibilities(array,observation);
  predict2 = approx_sky.visibilities(array,observation);

  for p,q in array.ifrs():
    ns.diff(p,q) << predict1(p,q) - predict2(p,q);

  # make some useful inspectors. Collect them into a list, since we need
  # to give a list of 'post' nodes to make_sinks() below
  inspectors = [];
  inspectors.append(
    Meow.StdTrees.vis_inspector(ns.inspect_predict,ns.diff) );
    
  # make sinks and vdm. Note that we don't want to make any spigots...
  # The list of inspectors comes in handy here
  Meow.StdTrees.make_sinks(ns,ns.diff,spigots=False,post=inspectors);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  req = Meow.Utils.create_io_request();
  # execute    
  mqs.execute('VisDataMux',req,wait=False);
  
  

# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
