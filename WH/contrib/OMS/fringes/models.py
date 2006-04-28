from Timba.TDL import *
from Timba.Contrib.OMS.PointSource import *
from Timba.Contrib.OMS.GaussianSource import *

# reference frequency for IHPBW above, also for spectral index in sources below
ref_frequency = float(800*1e+6);
ref_bandwidth = float(600*1e+6);

# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

def cps (ns,tablename=''):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');

  return [ PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                       Iorder=0, ra=0.0305432619099, dec=0.575958653158,
                       spi=0,freq0=ref_frequency,
                       parm_options=parm_options) ];
  
  
def cps_plus_faint_extended (ns,tablename=''):
  source_model = cps(ns,tablename) + \
                 faint_extended_source(ns,tablename);
  
  return source_model
  
def faint_extended_source (ns,tablename):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
      
  return [ GaussianSource(ns,name="S4",I=.1, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0304, dec=0.57632,
                  spi=0,freq0=ref_frequency,
                  size=[0.0001,7.2e-5],phi=2.15,
                  parm_options=parm_options) ];



def two_point_sources (ns,tablename=''):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
  source_model.append( PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.03119776, dec=0.57632226,
                  spi=0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030732848, dec=0.57585781,
                  spi=0,freq0=ref_frequency,
                  parm_options=parm_options));

  return source_model
  
  

def two_point_sources_plus_faint_extended (ns,tablename=''):
  
  source_model = two_point_sources(ns,tablename) + \
                 faint_extended_source(ns,tablename);

  return source_model
  
  
  
  
  
  

def main(args):
    print 'sources as two function calls'
    sources = radio_galaxy(None)
    sources = sources + additional_point_sources(None)
    print 'list length ', len(sources)
    for i in range(len(sources)):
       print sources[i].name

    print 'as single function call to point_and_extended_sources'
    sources = point_and_extended_sources(None)
    for i in range(len(sources)):
       print sources[i].name

    print 'as single function call to point_sources_only '
    sources = point_sources_only(None)
    for i in range(len(sources)):
       print sources[i].name


# Admire
if __name__ == '__main__':
    main(sys.argv)

