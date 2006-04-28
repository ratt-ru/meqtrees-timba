from Timba.TDL import *
from Timba.Contrib.OMS.PointSource import *
from Timba.Contrib.OMS.GaussianSource import *

# reference frequency for IHPBW above, also for spectral index in sources below
ref_frequency = float(800*1e+6);
ref_bandwidth = float(600*1e+6);

# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

reuse_solutions = False;

def combined_extended_source (ns,tablename=''):
  """ define two extended sources: positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  

# 1" ~ 4.8e-6 rad

# extended sources at positions of radio_galaxy S4 and S5

  source_model.append( GaussianSource(ns,name="S4",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030761428, dec=0.57588593,
                  spi=0.0,freq0=ref_frequency,
                  size=.00008, symmetric=True,
                  parm_options=parm_options));

  source_model.append( GaussianSource(ns,name="S5",I=60.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030732848, dec=0.57585781,
                  spi=-0.75,freq0=ref_frequency,
                  size=0.0005, symmetric=True,
                  parm_options=parm_options));

  return source_model

def point_and_extended_sources (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
# first get radio galaxy components
  source_model = radio_galaxy(ns,tablename)

# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename)

  return source_model

def two_point_sources (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
  source_model.append( PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.03119776, dec=0.57632226,
                  spi=-0.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030732848, dec=0.57585781,
                  spi=0.5,freq0=ref_frequency,
                  parm_options=parm_options));

  return source_model

def radio_galaxy (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
  
  # 1" ~ 4.8e-6 rad

  # NE 'hot spot' 4 x 3 arcsec in PA 135 deg 
  source_model.append( GaussianSource(ns,name="S1",I=3.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.03119776, dec=0.57632226,
                  spi=-0.55,freq0=ref_frequency,
                  size=[1.9e-5,1.44e-5],phi=0.785,
                  parm_options=parm_options));

  # NE extended lobe 30 x 10 arcsec in PA 45 deg
  source_model.append( GaussianSource(ns,name="S2",I=20.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.031181034, dec=0.57629802,
                  spi=-0.8,freq0=ref_frequency,
                  size=[0.000144,4.8e-5],phi=2.3561945,
                  parm_options=parm_options));

  # central 'nuclear' point source with flat spectrum
  source_model.append( PointSource(ns,name="S3",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030906872, dec=0.5761041,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));
  
  # SW extended lobe 21 x 15 srcsec in PA 33 deg
  source_model.append( GaussianSource(ns,name="S4",I=15.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030761428, dec=0.57588593,
                  spi=-0.75,freq0=ref_frequency,
                  size=[0.0001,7.2e-5],phi=2.15,
                  parm_options=parm_options));

  # SW 'hot spot' 2 x 2 arc sec symmetric
  source_model.append( GaussianSource(ns,name="S5",I=5.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030732848, dec=0.57585781,
                  spi=-0.4,freq0=ref_frequency,
                  size=9.6e-6, symmetric=True,
                  parm_options=parm_options));
  return source_model

def additional_point_sources (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');

# define five simple point sources
  source_model = []
  source_model.append( PointSource(ns,name="S6",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0302269161, dec=0.57654043,
                  spi=-1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S7",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030120036, dec=0.576310965,
                  spi=-1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S8",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0304215356, dec=0.575777607,
                  spi=1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S9",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030272885, dec=0.575762621,
                  spi=1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S10",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306782675, dec=0.57537688,
                  spi=2.0,freq0=ref_frequency,
                  parm_options=parm_options));

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

