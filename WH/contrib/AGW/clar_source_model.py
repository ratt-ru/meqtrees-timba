from numarray import *
from Timba.TDL import *

class PointSource:
  name = ''
  ra   = 0.0
  dec  = 0.0
  IQUV      = zeros(4)*0.0
  IQUVorder = zeros(4)*0.0
  table  = ''

  def __init__(self, name='', ra=0.0, dec=0.0,
               I=0.0, Q=0.0, U=0.0, V=0.0,
               Iorder=0, Qorder=0, Uorder=0, Vorder=0,
               spi=0.0,
               table=''):
    self.name   = name
    self.ra     = ra
    self.dec    = dec
    self.IQUV   = array([I,Q,U,V])
    self.IQUVorder = array([Iorder,Qorder,Uorder,Vorder])
    self.spi    = spi
    self.table  = table
    pass
  pass

def create_source_model(tablename=''):
  """ define model source positions and flux densities """
  source_model = []
  source_model.append( PointSource(name="src_1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030272885, dec=0.575762621,
                  spi=-0.71,
                  table=tablename))

  source_model.append( PointSource(name="src_2",  I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306782675, dec=0.575526087,
                  spi=-0.62,
                  table=tablename))

  source_model.append( PointSource(name="src_3",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308948646, dec=0.5762655,
                  spi=-0.53,
                  table=tablename))

  source_model.append( PointSource(name="src_4",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0308043705, dec=0.576256621,
                  spi=-0.44,
                  table=tablename))

  source_model.append( PointSource(name="src_5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.030120036, dec=0.576310965,
                  spi=-0.35,
                  table=tablename))

  source_model.append( PointSource(name="src_6",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0301734016, dec=0.576108805,
                  spi=-0.26,
                  table=tablename))

  source_model.append( PointSource(name="src_7",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0302269161, dec=0.576333355,
                  spi=-0.17,
                  table=tablename))

  source_model.append( PointSource(name="src_8",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0304215356, dec=0.575777607,
                  spi=-0.28,
                  table=tablename))

  source_model.append( PointSource(name="src_9",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0307416105, dec=0.576347166,
                  spi=-0.39,
                  table=tablename))

  source_model.append( PointSource(name="src_10",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, ra=0.0306878027, dec=0.575851951,
                  spi=-0.40,
                  table=tablename))

  return source_model

