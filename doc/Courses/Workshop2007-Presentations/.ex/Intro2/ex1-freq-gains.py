# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

TDLRuntimeOption('tile_size',"Tile size",[5,10,20,30,100]);


def _define_forest (ns):
  # loop over all baselines
  ns.fscale << (Meq.Freq()-8e+8)/5e+8;
  for p,q in IFRS:
    spigot = ns.spigot(p,q) << Meq.Spigot(input_column='DATA',station_1_index=p-1,station_2_index=q-1);
    ga = ns.ga(p,q) << 1 + .1*p*ns.fscale;
    gp = ns.gp(p,q) << 2*math.pi*q/3.*ns.fscale;
    modvis = ns.mod_vis(p,q) << spigot*(ns.gain(p,q) << Meq.Polar(ga,gp));
    ns.sink(p,q) << Meq.Sink(modvis,station_1_index=p-1,station_2_index=q-1,output_col='DATA');
    
  ns.inspector1 << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.spigot(p,q),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspector2 << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.mod_vis(p,q),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspectors = Meq.ReqMux(ns.inspector1,ns.inspector2);
  ns.VisDataMux = Meq.VisDataMux(post=ns.inspectors);


def _test_forest (mqs,parent):
  # create an I/O request
  req = meq.request();
  req.input = record( 
    ms = record(  
      ms_name          = 'demo.MS',
      tile_size        = tile_size,
      data_column_name = 'DATA',
    ),
  );
  req.output = record( 
    ms = record(  
      data_column = 'MODEL_DATA',
    ),
  );
  # execute    
  mqs.execute('VisDataMux',req,wait=False);


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Spigots',page=[
    record(udi="/node/spigot:1:2",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/spigot:9:27",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/mod_vis:1:2",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/mod_vis:9:27",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='Inspector',page=[
    record(udi="/node/inspector1",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspector2",viewer="Collections Plotter",pos=(1,0))
  ]),
]);



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
