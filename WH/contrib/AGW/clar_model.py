from Timba.TDL import *
from Timba.Contrib.OMS.PointSource import *
from Timba.Contrib.OMS.GaussianSource import *

# some CLAR constants

# This is actually the inverse of the CLAR half-power beam width, in radians.
# base IHPW is 647.868 rad^-1 at 800 MHz
ihpbeam_width = 647.868

# reference frequency for IHPBW above, also for spectral index in sources below
ref_frequency = float(800*1e+6)

# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

reuse_solutions = False;


def point_and_extended_sources (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
  source_model.append( PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0307416105, dec=0.576347166,
                  spi=0.5,freq0=ref_frequency,
                  parm_options=parm_options));
  
  # 1" ~ 4.8e-6 rad

  source_model.append( GaussianSource(ns,name="S2e",I=4.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0302269161, dec=0.576333355,
                  spi=1,freq0=ref_frequency,
                  size=[0.0002,0.0001],phi=.5,
                  parm_options=parm_options));
                  
  source_model.append( PointSource(ns,name="S2p",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0302269161, dec=0.576333355,
                  spi=-1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S3",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030120036, dec=0.576310965,
                  spi=-1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( GaussianSource(ns,name="S4",I=5.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308948646, dec=0.5762655,
                  spi=4,freq0=ref_frequency,
                  size=[.00005,.0002],phi=0,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308043705, dec=0.576256621,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S6",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0301734016, dec=0.576108805,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( GaussianSource(ns,name="S7",I=4.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306878027, dec=0.575851951,
                  spi=0.5,freq0=ref_frequency,
                  size=[.00002,.0001],phi=1.5,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S8",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0304215356, dec=0.575777607,
                  spi=1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S9",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030272885, dec=0.575762621,
                  spi=1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( GaussianSource(ns,name="S10",  I=5.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306782675, dec=0.575526087,
                  spi=2.0,freq0=ref_frequency,
                  size=[.00002,.00003],phi=1.0,
                  parm_options=parm_options));

  return source_model


def point_sources_only (ns,tablename=''):
  """ define model source positions and flux densities """
  parm_options = record(
      use_previous=reuse_solutions,
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
  source_model.append( PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0307416105, dec=0.576347166,
                  spi=-2.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S2",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0302269161, dec=0.576333355,
                  spi=-1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S3",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030120036, dec=0.576310965,
                  spi=-1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S4",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308948646, dec=0.5762655,
                  spi=-0.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308043705, dec=0.576256621,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S6",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0301734016, dec=0.576108805,
                  spi=0.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S7",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306878027, dec=0.575851951,
                  spi=0.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S8",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0304215356, dec=0.575777607,
                  spi=1.0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S9",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030272885, dec=0.575762621,
                  spi=1.5,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S10",  I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306782675, dec=0.575526087,
                  spi=2.0,freq0=ref_frequency,
                  parm_options=parm_options));

  return source_model


def EJones (ns,array,sources,name="E"):
  """creates E nodes for simulating the CLAR beam, with elevation-dependent
  broadening.
  """;
  ns.freq << Meq.Freq;
  # this is the inverse half-power beam width at reference frequency
  width_polc = create_polc(c00=ihpbeam_width);
  ns.ihpbw0 << Meq.Parm(width_polc,real_polc=width_polc,
                        use_previous=reuse_solutions,node_groups='Parm');
  # this is the IHPBW at the given frequency
  ns.ihpbw << ns.ihpbw0 * ns.freq / ref_frequency;
  # ...squared
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
  width_polc = create_polc(c00=ihpbeam_width);
  ns.ihpbw0 << Meq.Parm(width_polc,real_polc=width_polc,
                        use_previous=reuse_solutions,node_groups='Parm');
  # this is the IHPBW at the given frequency
  ns.ihpbw << ns.ihpbw0 * ns.freq / ref_frequency;
  # ...squared
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
