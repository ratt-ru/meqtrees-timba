from Timba.TDL import *
from Timba.Contrib.OMS.PointSource import *
from Timba.Contrib.OMS.GaussianSource import *

# some CLAR constants

# base HPBW is 5.3 arcmin at 800 MHz
hpbeam_width = 5.3

# reference frequency for IHPBW above, also for spectral index in sources below
ref_frequency = float(800*1e+6)

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
  source_model = source_model + additional_point_sources(ns,tablename) +faint_source(ns,tablename)

  return source_model

def solve_point_and_extended_sources (ns,tablename=''):
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

def point_sources_only (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = radio_galaxy_point_sources(ns,tablename) 
# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename) + faint_source(ns,tablename)
  return source_model

def solve_point_sources_only (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = radio_galaxy_point_sources(ns,tablename) 
# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename) 
  return source_model

def radio_galaxy_point_sources (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
######## point sources at radio galaxy positions ########
  source_model.append( PointSource(ns,name="S1",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.03119776, dec=0.57632226,
                  spi=-1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S2",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.031181034, dec=0.57629802,
                  spi=-1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S3",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030906872, dec=0.5761041,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));
  
  source_model.append( PointSource(ns,name="S4",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030761428, dec=0.57588593,
                  spi=1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S5",I=2.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030732848, dec=0.57585781,
                  spi=1.5,freq0=ref_frequency,
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

def faint_source (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
# note - with 16 channels and sample step of 60 sec a source of 0.01
# turns out to be ~ 5 sigma with 600 MHz BW if we use test noise units of 1
  source_model.append( PointSource(ns,name="S11",I=0.01, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.03037222, dec=0.57590435,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));
  return source_model

def EJones (ns,array,sources,name="E"):
  """creates E nodes for simulating the CLAR beam, with elevation-dependent
  broadening.
  """;
  ns.freq << Meq.Freq;
  # this is the inverse half-power beam width at reference frequency
  width_polc = create_polc(c00=hpbeam_width);
  ns.hpbw0 << Meq.Parm(width_polc,real_polc=width_polc,
                        use_previous=reuse_solutions,node_groups='Parm');
  # this is the IHPBW at the given frequency
  ns.hpbw << ns.hpbw0 * ref_frequency / ns.freq 
  # take inverse and square
  arcmin_radian = ns.arcmin_radian << 3437.75
  ns.ihpbw = arcmin_radian / ns.hpbw
  ns.ihpbw_sq << Meq.Sqr(ns.ihpbw)

  Ejones = ns[name];
  # create per-source,per-station E Jones matrices and attach them
  # to sources
  for src in sources:
    for station in array.stations():
      # voltage gain parameter read from mep_derived table (see clar_beam_fit)
      vgain = ns.V_GAIN(station,src.name) << Meq.Parm(table_name=mep_derived);
      # derive diagonal term
      ediag = ns.ediag(station,src.name) << Meq.Sqrt(Meq.Exp(vgain*ns.ihpbw_sq));
      # create E matrix
      Ejones(src.name,station) << Meq.Matrix22(ediag,0,0,ediag);
      
  return Ejones;

def EJones_unbroadened (ns,observation,sources,name="E0"):
  """creates E nodes for simulating the CLAR beam without
  elevation-dependent broadening.
  """;
  ns.freq << Meq.Freq;
  # this is the inverse half-power beam width at reference frequency
  width_polc = create_polc(c00=hpbeam_width);
  ns.hpbw0 << Meq.Parm(width_polc,real_polc=width_polc,
                        use_previous=reuse_solutions,node_groups='Parm');
  # this is the IHPBW at the given frequency
  ns.hpbw << ns.hpbw0 * ref_frequency / ns.freq 
  # take inverse and square
  arcmin_radian = ns.arcmin_radian << 3437.75
  ns.ihpbw = arcmin_radian / ns.hpbw
  ns.ihpbw_sq << Meq.Sqr(ns.ihpbw)
  ln16 = ns.ln16 << -2.7725887;
 
  Ejones = ns[name];
  # create per-source,per-station E Jones matrices and attach them
  # to sources
  for src in sources:
    lmn = src.lmn(observation.radec0());
    l = ns.l(src.name) << Meq.Selector(lmn,index=0);
    m = ns.m(src.name) << Meq.Selector(lmn,index=1);

    # compute CLAR voltage gain as seen for this source at this station
    # first square L and M
    l_sq = ns.l_sq(src.name) << Meq.Sqr(l);
    m_sq = ns.m_sq(src.name) << Meq.Sqr(m);

    # add L and M gains together, then multiply by log 16
    vgain = ns.v_gain(name,src.name) << ( l_sq + m_sq )*ln16;

    # this now needs to be multiplied by width and exponent taken to get the
    # true beam power
    ediag = ns.ediag(name,src.name) << Meq.Sqrt(Meq.Exp(vgain*ns.ihpbw_sq));
    
    Ejones(src.name) << Meq.Matrix22(ediag,0,0,ediag);
      
  return Ejones;

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

