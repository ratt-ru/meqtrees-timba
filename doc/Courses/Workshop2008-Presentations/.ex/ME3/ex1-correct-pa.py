# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math
import random

# define antenna list
ANTENNAS = range(1,28);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];


def _define_forest (ns):
  # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra<<0,ns.dec<<0);
  
  # nodes for array reference position
  ns.xyz0 = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0);
  
  # now define per-station stuff: XYZs and UVWs 
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0);

  # nu - nu_0
  ns.delta_freq = Meq.Freq() - (ns.freq0<<0);   

  # define G and K-jones, and invert/conjugate them
  for p in ANTENNAS:
    a = p*1e-10;
    gx = ns.gx(p) << 1+a*ns.delta_freq;
    gy = ns.gy(p) << 1-a*ns.delta_freq;
    ns.G(p) << Meq.Matrix22(gx,0,0,gy);
    ns.Ginv(p) << Meq.MatrixInvert22(ns.G(p));
    ns.Ginvt(p) << Meq.ConjTranspose(ns.Ginv(p));
    
    pa = ns.pa(p) << Meq.ParAngle(radec=ns.radec0,xyz=ns.xyz(p));
    cospa = ns << Meq.Cos(pa);
    sinpa = ns << Meq.Sin(pa);
    ns.Pinv(p) << Meq.Matrix22(cospa,sinpa,-sinpa,cospa);
    ns.Pinvt(p) << Meq.ConjTranspose(ns.Pinv(p));

  
  # now define spigots, corrections, attach to sinks
  for p,q in IFRS:
    spig = ns.spigot(p,q) << Meq.Spigot(station_1_index=p-1,station_2_index=q-1);
    correct = ns.correct(p,q) << \
      Meq.MatrixMultiply(ns.Pinv(p),ns.Ginv(p),spig,ns.Ginvt(q),ns.Pinvt(q));
    ns.sink(p,q) << Meq.Sink(correct,station_1_index=p-1,station_2_index=q-1,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);
  

def _tdl_job_1_correct_MS (mqs,parent):
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
      data_column = 'CORRECTED_DATA' 
    )
  );
  # execute    
  mqs.execute('vdm',req,wait=False);

def _tdl_job_2_make_image (mqs,parent):
  import os
  os.spawnvp(os.P_NOWAIT,'glish',['glish','-l','make_image.g',imaging_column,
    'ms=demo.MS','mode='+imaging_mode,
    'weight='+imaging_weight,
    'stokes='+imaging_stokes]);


# some options for the imager -- these will be automatically placed
# in the "TDL Exec" menu
TDLRuntimeOption('imaging_column',"MS column to image",["DATA","CORRECTED_DATA"]);
TDLRuntimeOption('imaging_mode',"Imaging mode",["channel","mfs"]);
TDLRuntimeOption('imaging_weight',"Imaging weights",["briggs","natural","uniform"]);
TDLRuntimeOption('imaging_stokes',"Stokes parameters to image",["IQUV","I"]);



# setup a few bookmarks
Settings.forest_state = record(bookmarks=[
  record(name='G Jones, inverted',page=[
    record(udi="/node/Ginv:1",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/Ginv:2",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/Ginv:3",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/Ginv:4",viewer="Result Plotter",pos=(1,1)) \
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
