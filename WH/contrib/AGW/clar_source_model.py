from Timba.Contrib.OMS.PointSource import PointSource    

def create_clar_sources (ns,tablename='',freq0=None):
  """ define model source positions and flux densities """
  source_model = []
  source_model.append( PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0307416105, dec=0.576347166,
                  spi=-2.0,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S2",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0302269161, dec=0.576333355,
                  spi=-1.5,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S3",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030120036, dec=0.576310965,
                  spi=-1.0,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S4",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308948646, dec=0.5762655,
                  spi=-0.5,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308043705, dec=0.576256621,
                  spi=0.0,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S6",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0301734016, dec=0.576108805,
                  spi=0.0,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S7",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306878027, dec=0.575851951,
                  spi=0.5,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S8",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0304215356, dec=0.575777607,
                  spi=1.0,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S9",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030272885, dec=0.575762621,
                  spi=1.5,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  source_model.append( PointSource(ns,name="S10",  I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306782675, dec=0.575526087,
                  spi=2.0,freq0=freq0,
                  table=tablename,node_groups='Parm'))

  return source_model

