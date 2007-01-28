# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math
import random

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# useful constant: 1 deg in radians
DEG = math.pi/180.;
ARCMIN = DEG/60;

# source flux (same for all sources)
I = 1; Q = .2; U = .2; V = .2;

# we'll put the sources on a grid (positions in arc min)
LM = [(-1,-1),(-1,0),(-1,1),
      ( 0,-1),( 0,0),( 0,1), 
      ( 1,-1),( 1,0),( 1,1)];
SOURCES = range(len(LM));       # 0...N-1

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
  
  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q);
  
  # source l,m,n-1 vectors
  for src in SOURCES:
    l,m = LM[src];
    l = l*ARCMIN;
    m = m*ARCMIN;
    n = math.sqrt(1-l*l-m*m);
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1);
    # and the projected brightness...
    ns.B(src) << ns.B0 / n;
  
  # define K-jones matrices
  for p in ANTENNAS:
    for src in SOURCES:
      ns.K(p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src),uvw=ns.uvw(p));
      ns.Kt(p,src) << Meq.ConjTranspose(ns.K(p,src));
    # create random time-dependent G variation
    # ... for gx
    a = random.uniform(math.pi/2,math.pi);   # amplitude of phase variation
    b = 2*math.pi/random.uniform(3600,7200); # period of variation 
    c = random.uniform(0,2*math.pi);         # initial phase of variation
    gx = ns.gx(p) << Meq.Polar(1,a*Meq.Sin(Meq.Time()*b+c));

    # ... for gy
    a = random.uniform(math.pi/2,math.pi);   # amplitude of phase variation
    b = 2*math.pi/random.uniform(3600,7200); # period of variation 
    c = random.uniform(0,2*math.pi);        # initial phase of variation
    gy = ns.gy(p) << Meq.Polar(1,a*Meq.Sin(Meq.Time()*b+c));

    ns.G(p) << Meq.Matrix22(gx,0,0,gy);
    ns.Gt(p) << Meq.ConjTranspose(ns.G(p));
  
  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:
    # make per-source predicted visibilities
    for src in SOURCES:
      ns.predict(p,q,src) << \
        Meq.MatrixMultiply(ns.K(p,src),ns.B(src),ns.Kt(q,src));
    # and sum them up via an Add node
    predict = ns.predict(p,q) << Meq.MatrixMultiply(
                ns.G(p),
                Meq.Add(*[ns.predict(p,q,src) for src in SOURCES]),
                ns.Gt(q));
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define a couple of inspector nodes
  ns.inspect_G << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s"%(p) for p in ANTENNAS],
    *[Meq.Mean(ns.G(p),reduction_axes="freq") for p in ANTENNAS]
  );
  ns.inspect_predict(0) << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.predict(p,q,0),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspect_predict(4) << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.predict(p,q,4),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspect_predict(5) << Meq.Composer(
    dims=[0],   # compose in tensor mode
    plot_label=["%s-%s"%(p,q) for p,q in IFRS],
    *[Meq.Mean(ns.predict(p,q,5),reduction_axes="freq") for p,q in IFRS]
  );
  ns.inspectors = Meq.ReqMux(ns.inspect_G,ns.inspect_predict(0),ns.inspect_predict(4),ns.inspect_predict(5));
  
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
      data_column = 'DATA' 
    )
  );
  # execute    
  mqs.execute('vdm',req,wait=False);

def _tdl_job_2_make_image (mqs,parent):
  import os
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g','DATA',
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
  record(name='Predicted visibilities',page=[
    record(udi="/node/predict:1:2:0",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/predict:1:9:0",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/predict:1:2:4",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/predict:1:9:4",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='K Jones',page=[
    record(udi="/node/K:2:0",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/K:9:0",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/K:2:1",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/K:9:1",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='G Jones',page=[
    record(udi="/node/G:1",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/G:2",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/G:3",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/G:4",viewer="Result Plotter",pos=(1,1)) \
  ]),
  record(name='Inspectors',page=[
    record(udi="/node/inspect_predict:0",viewer="Collections Plotter",pos=(0,0)),
    record(udi="/node/inspect_predict:4",viewer="Collections Plotter",pos=(0,1)),
    record(udi="/node/inspect_predict:5",viewer="Collections Plotter",pos=(1,0)),
    record(udi="/node/inspect_G",viewer="Collections Plotter",pos=(1,1))
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
