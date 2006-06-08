from Timba.TDL import *
from Timba.Contrib.OMS.PointSource import *
from Timba.Contrib.OMS.GaussianSource import *
import random
import math

# reference frequency for spectral index in sources below
ref_frequency = float(800*1e+6);


def cps (ns,observation,tablename=''):
  """Defines a model consisting of a point source at phase centre""";
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');

  return [ PointSource(ns,name="cs",I=1.0, Q=0.0, U=0.0, V=0.0,
                       direction = observation.phase_centre,
                       Iorder=4,Vorder=3,
                       spi=0,freq0=ref_frequency,
                       parm_options=parm_options) ];
                       
                       
  
def cgs (ns,observation,tablename=''):
  """Defines a model consisting of a gaussian source at phase centre""";
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
  arcsec = math.pi/(180*3600); 

  return [ GaussianSource(ns,name="cs",I=10.0, Q=0.0, U=0.0, V=0.0,
                       direction = observation.phase_centre,
                       Iorder=3,Vorder=3,size=[.0002*arcsec,.0001*arcsec],
                       spi=0,freq0=ref_frequency,
                       parm_options=parm_options) ];
  
  


# Admire
if __name__ == '__main__':
    main(sys.argv)

