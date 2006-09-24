# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math

# define antenna list
ANTENNAS = range(27);
# derive interferometer list
IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ];

# useful constant: 1 deg in radians
DEG = 2*math.pi/180.;

# source parameters
I = 1; Q = .2; U = .2; V = .2;
L = 2*(DEG/60);
M = 2*(DEG/60);
N = math.sqrt(1-L*L-M*M);


def _define_forest (ns):
  # nodes for phase center
  ns.radec0 = Meq.Composer(ns.ra0<<Meq.Parm,ns.dec0<<Meq.Parm);
  
  # nodes for array and antenna positions
  ns.xyz0 = Meq.Composer(ns.x0<<Meq.Parm,ns.y0<<Meq.Parm,ns.z0<<Meq.Parm);
  # define per-station stuff
  for p in ANTENNAS:
    # positions and uvw
    ns.xyz(p) << Meq.Composer(ns.x(p) << Meq.Parm,
                              ns.y(p) << Meq.Parm,
                              ns.z(p) << Meq.Parm);
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p));
  
  # source LMN
  ns.lmn_minus1 << Meq.Composer(L,M,N-1);
  
  # define K-jones matrices
  for p in ANTENNAS:
    ns.K(p) << Meq.VisPhaseShift(lmn=ns.lmn_minus1,uvw=ns.uvw(p));
    ns.conjK(p) << Meq.ConjTranspose(ns.K(p));
  
  # define source brightness, B
  ns.B << Meq.Matrix22(I+Q,Meq.ToComplex(U,-V),Meq.ToComplex(U,V),I-Q);
  # and B/n
  ns.B_n = ns.B/N;
  
  # define predicted visibilities, attach to sinks
  for p,q in IFRS:
    predict = ns.predict(p,q) << \
      Meq.MatrixMultiply(ns.K(p),ns.B_n,ns.conjK(q));
    ns.sink(p,q) << Meq.Sink(predict,station_1_index=p,station_2_index=q,output_col='DATA');

  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);
  
  



def _test_forest (mqs):
  """test_forest() is a standard TDL name. When a forest script is
  loaded by, e.g., the browser, and the "test" option is set to true,
  this method is automatically called after define_forest() to run a 
  test on the forest. The 'mqs' argument is a meqserver proxy object.
  """;
  from Timba.Meq import meq



# this is a useful thing to have at the bottom of the script, it allows us to check the tree for consistency
# simply by running 'python script.tdl'

if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
