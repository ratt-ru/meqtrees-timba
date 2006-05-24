from Timba.TDL import *
from Timba.Contrib.OMS.PointSource import *
from Timba.Contrib.OMS.GaussianSource import *
import random

# reference frequency for IHPBW above, also for spectral index in sources below
ref_frequency = float(800*1e+6);
ref_bandwidth = float(600*1e+6);

def cps_3C345 (ns,tablename=''):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');

  return [ PointSource(ns,name="3C345",I=1.0, Q=0.0, U=0.0, V=0.0,
                       Iorder=0, ra=-1.90685874937,dec=0.694820394218,
                       spi=0,freq0=ref_frequency,
                       parm_options=parm_options) ];
  
  
# Admire
if __name__ == '__main__':
    main(sys.argv)

