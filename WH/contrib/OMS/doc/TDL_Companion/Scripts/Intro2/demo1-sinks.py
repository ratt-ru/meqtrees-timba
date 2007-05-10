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
    ft = Meq.Composer(
            ns.freq(p,q) << Meq.Freq(),
            ns.time(p,q) << Meq.Time()
    );
    ns.sink(p,q) << Meq.Sink(ft,station_1_index=p-1,station_2_index=q-1);


def _test_forest (mqs,parent):
  # create an I/O request
  req = meq.request();
  req.input = record( 
    ms = record(  
      ms_name          = 'demo.MS',
      tile_size        = tile_size
    ),
  );
  # execute    
  mqs.execute('VisDataMux',req,wait=False);


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='MS Grids',page=[
    record(udi="/node/freq:1:2",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/freq:9:20",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/time:1:2",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/time:9:20",viewer="Result Plotter",pos=(1,1)) \
  ])]);





# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
