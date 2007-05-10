# standard preamble
from Timba.TDL import *
from Timba.Meq import meq

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

TDLRuntimeOption('tile_size',"Tile size",[5,10,20,30,100]);


def _define_forest (ns):
  # loop over all baselines
  for p,q in IFRS:
    spigot = ( ns.spigot(p,q) << Meq.Spigot(input_column='DATA',
                    station_1_index=p-1,station_2_index=q-1) );
    ns.sink(p,q) << Meq.Sink(spigot,station_1_index=p-1,station_2_index=q-1);

  ns.inspector << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.spigot(p,q),reduction_axes="freq") for p,q in IFRS]
  );
  ns.VisDataMux = Meq.VisDataMux(post=ns.inspector);
  


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
  # execute    
  mqs.execute('VisDataMux',req,wait=False);


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='Spigots',page=[
    record(udi="/node/spigot:1:2",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/spigot:1:4",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/spigot:1:7",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/spigot:1:9",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='Inspector',page=[
    record(udi="/node/inspector",viewer="Collections Plotter",pos=(0,0))
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
