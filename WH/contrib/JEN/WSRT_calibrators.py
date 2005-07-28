# ../Timba/PyApps/test/WSRT_calibrators.py:  
#   Calibrator sources for WSRT Central Point Source reduction

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq

# forest_state is a standard TDL name. If defined in the script, this
# record is passed to Set.Forest.State. 
forest_state = record(cache_policy=100);

# some global bits  
STATIONS = range(1,15);

IFRS   = [ (s1,s2) for s1 in STATIONS for s2 in STATIONS if s1<s2 ];

STOKES = ("I","Q","U","V");

SOURCES = [ record(name="3C343_1",I=1,Q=0,U=0,V=0,
                   ra=4.356645791155902,dec=1.092208429052697),
            record(name="3C343"  ,I=1,Q=0,U=0,V=0,
                   ra=4.3396003966265599,dec=1.0953677174056471)
          ];

POLC_SCALE  = [1e+5, 1e+6];
POLC_OFFSET = [4.47204e9,1.175e9];



def make_source_subtree (ns,src):
  ns.IQUV(src.name) << Meq.Matrix22( 
    *[ ns.stokes(st,src.name) << Meq.Parm(meq.polc(src[st],scale=POLC_SCALE,offset=POLC_OFFSET)) for st in STOKES ] );
  coher = ns.coherency(src.name) << Meq.Matrix22( 
      ns.xx(src.name) << ns.stokes('I',src.name) + ns.stokes('Q',src.name),
      ns.yx(src.name) << Meq.ToComplex(ns.stokes('U',src.name),ns.stokes('V',src.name)),
      ns.xy(src.name) << Meq.Conj(ns.yx(src.name)),
      ns.yy(src.name) << ns.stokes('I',src.name) - ns.stokes('Q',src.name)
    ) * 0.5;
  lmn = ns.lmn(src.name) << Meq.LMN(
          ra_0  = ns.ra0,
          dec_0 = ns.dec0,
          ra    = ns.ra(src.name) << Meq.Parm(src.ra,groups="a"),
          dec   = ns.dec(src.name) << Meq.Parm(src.dec,groups="a")
    );
  ns.lmn_minus1(src.name) << Meq.Paster(lmn,(ns.n(src.name) << Meq.Selector(lmn,index=2)) - 1,index=2);
  ns.coherency_n(src.name) << coher / ns.n(src.name);
  


# SAelf-test:

if __name__ == '__main__': pass
 
