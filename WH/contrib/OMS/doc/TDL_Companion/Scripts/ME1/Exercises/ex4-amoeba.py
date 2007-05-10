# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

from example5_iono import make_sine_tid

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# useful constant: 1 deg in radians
DEG = math.pi/180.;

# source parameters
I = 1; Q = .2; U = .2; V = .2;
L = 0.; # 1*(DEG/60);
M = 0.; # 1*(DEG/60);
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
    
    ns.xy(p) << Meq.Composer(ns.x(p),ns.y(p));
    make_sine_tid(ns,ns.tec(p),ns.xy(p),ampl=.1,size_km=50,speed_kmh=200,tec0=10);
    ns.Z(p) << Meq.Polar(1,-2*math.pi*50*3e+8/Meq.Freq()*ns.tec(p));
    ns.Zt(p) << Meq.ConjTranspose(ns.Z(p));


  # define source brightness, B
  ns.B << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);
  
  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    predict = ns.predict(p,q) << \
      Meq.MatrixMultiply(ns.Z(p),ns.K(p),ns.B,ns.Kt(q),ns.Zt(q));
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define a couple of inspector nodes
  ns.inspect_Z << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s"%(p) for p in ANTENNAS],
    *[Meq.Mean(ns.Z(p),reduction_axes="freq") for p in ANTENNAS]
  ),
  ns.inspect_tec << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s"%(p) for p in ANTENNAS],
    *[ns.tec(p) for p in ANTENNAS]
  ),
  ns.inspect_predict << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.predict(p,q),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspectors = Meq.ReqMux(ns.inspect_Z,ns.inspect_tec,ns.inspect_predict);
  
  # create VDM and attach inspectors
  ns.vdm = Meq.VisDataMux(post=ns.inspectors);
  

def _tdl_job_1_simulate_MS (mqs,parent):
  # create an I/O request
  req = meq.request();
  req.input = record( 
    ms = record(  
      ms_name          = 'demo.MS',
      tile_size        = 32
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

def _tdl_job_2_make_image (mqs,parent):
  import os
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g','MODEL_DATA',
    'ms=demo.MS','mode='+imaging_mode,
    'weight='+imaging_weight,
    'stokes='+imaging_stokes]);

# some options for the imager -- these will be automatically placed
# in the "TDL Exec" menu
TDLRuntimeOption('imaging_mode',"Imaging mode",["mfs","channel"]);
TDLRuntimeOption('imaging_weight',"Imaging weights",["natural","uniform","briggs"]);
TDLRuntimeOption('imaging_stokes',"Stokes parameters to image",["I","IQUV"]);


# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='K Jones',page=[
    record(udi="/node/K:1",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/K:2",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/K:9",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/K:26",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='Z Jones',page=[
    record(udi="/node/Z:1",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/Z:2",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/Z:9",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/Z:26",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='TECs',page=[
    record(udi="/node/tec:1",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/tec:2",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/tec:9",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/tec:26",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='Inspectors',page=[
    record(udi="/node/inspect_Z",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_tec",viewer="Collections Plotter",pos=(0,1)),
    record(udi="/node/inspect_predict",viewer="Collections Plotter",pos=(1,0))
  ]),
]);



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.py'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
