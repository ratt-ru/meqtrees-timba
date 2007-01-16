# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# useful constant: 1 deg in radians
DEG = math.pi/180.;

# source parameters
I = 1; Q = .2; U = .2; V = .2;
L = 1*(DEG/60);
M = 1*(DEG/60);
N = math.sqrt(1-L*L-M*M);


def _define_forest (ns):
  # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);
  
  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);
  
  # now define per-station stuff: XYZs and UVWs 
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p));
  
  # source l,m,n-1 vector
  ns.lmn_minus1 << Meq.Composer(L,M,N-1);
  
  # define K-jones matrices
  for p in ANTENNAS:
    ns.K(p) << Meq.VisPhaseShift(lmn=ns.lmn_minus1,uvw=ns.uvw(p));
    ns.Kt(p) << Meq.ConjTranspose(ns.K(p));
  
  # define source brightness, B
  ns.B << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);
  
  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    predict = ns.predict(p,q) << \
      Meq.MatrixMultiply(ns.K(p),ns.B,ns.Kt(q));
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);
  

def _test_forest (mqs,parent):
  # create an I/O request
  req = meq.request();
  req.input = record( 
    ms = record(  
      ms_name          = 'demo.MS',
      tile_size        = 30
    ),
    python_init = 'Meow.ReadVisHeader'
  );
  req.output = record( 
    ms = record( 
      data_column = 'MODEL_DATA' 
    )
  );
  # execute    
  mqs.execute('vdm',req,wait=False);


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='K Jones',page=[
    record(udi="/node/K:1",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/K:2",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/K:9",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/K:26",viewer="Result Plotter",pos=(1,1)) \
  ])]);



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
