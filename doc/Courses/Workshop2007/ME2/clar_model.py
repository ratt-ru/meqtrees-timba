
#% $Id: clar_model.py 4096 2006-10-09 14:41:48Z oms $ 

#
# Copyright (C) 2006
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Meow.Utils import *
from Meow.Direction import *
from Meow.PointSource import *
from Meow.GaussianSource import *
import sets

# some CLAR constants

# base HPBW is 5.3 arcmin at 800 MHz
hpbeam_width = 5.3

# reference frequency for IHPBW above, also for spectral index in sources below
ref_frequency = float(800*1e+6)

# MEP table for various derived quantities 
mep_derived = 'CLAR_DQ_27-480.mep';

reuse_solutions = False;

# Global dictionary of known source directions
# Keep all this in one place, this way we can do a single clar_fit_dq run
# for all directions appearing in any model.
_directions = dict(
  S1=(0.03119776,0.57632226),
  S2=(0.031181034,0.57629802),
  S3=(0.030906872,0.5761041),
  S4=(0.030761428,0.57588593),
  S5=(0.030732848,0.57585781),
  S6=(0.0302269161,0.57654043),
  S7=(0.030120036,0.576310965),
  S8=(0.0304215356,0.575777607),
  S9=(0.030272885,0.575762621),
  S10=(0.0306782675,0.57537688),
  S11=(0.03037222,0.57590435)
);

direction = None;  # record of Directions, populated below

def init_directions (ns,tablename=''):
  """Inits global direction record of all Directions in all models""";
      
  global _directions;
  global direction;
  if direction is None:
    direction = recdict();
    for name,(ra,dec) in _directions.iteritems():
      direction[name] = Direction(ns,name,ra,dec);
    
  return direction;
  

def combined_extended_source (ns,tablename=''):
  """ define two extended sources: positions and flux densities """
  

# 1" ~ 4.8e-6 rad

# extended sources at positions of radio_galaxy S4 and S5

  source_model.append( GaussianSource(ns,name="S4",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S4,
                  spi=0.0,freq0=ref_frequency,
                  size=.00008, symmetric=True));

  source_model.append( GaussianSource(ns,name="S5",I=60.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S5,
                  spi=-0.75,freq0=ref_frequency,
                  size=0.0005, symmetric=True));

  return source_model

def point_and_extended_sources (ns,tablename=''):
  """ define model source positions and flux densities """
# first get radio galaxy components
  source_model = radio_galaxy(ns,tablename)

# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename) +faint_source(ns,tablename)

  return source_model

def solve_point_and_extended_sources (ns,tablename=''):
  """ define model source positions and flux densities """
# first get radio galaxy components
  source_model = radio_galaxy(ns,tablename)

# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename) 
  return source_model

def point_sources_only (ns,tablename=''):
  """ define model source positions and flux densities """
  
  source_model = radio_galaxy_point_sources(ns,tablename) 
# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename) + faint_source(ns,tablename)
  return source_model

def solve_point_sources_only (ns,tablename=''):
  """ define model source positions and flux densities """
  
  source_model = radio_galaxy_point_sources(ns,tablename) 
# add other point sources 
  source_model = source_model + additional_point_sources(ns,tablename) 
  return source_model

def radio_galaxy_point_sources (ns,tablename=''):
  """ define model source positions and flux densities """
  
  source_model = []
######## point sources at radio galaxy positions ########
  source_model.append( PointSource(ns,name="S1",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S1,
                  spi=-1.5,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S2",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S2,
                  spi=-1.0,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S3",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S3,
                  spi=0.0,freq0=ref_frequency));
  
  source_model.append( PointSource(ns,name="S4",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S4,
                  spi=1.0,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S5",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S5,
                  spi=1.5,freq0=ref_frequency));
  return source_model

def radio_galaxy (ns,tablename=''):
  """ define model source positions and flux densities """
  
  source_model = []
  
  # 1" ~ 4.8e-6 rad

  # NE 'hot spot' 4 x 3 arcsec in PA 135 deg 
  source_model.append( GaussianSource(ns,name="S1",I=3.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S1,
                  spi=-0.55,freq0=ref_frequency,
                  size=[1.9e-5,1.44e-5],phi=0.785));

  # NE extended lobe 30 x 10 arcsec in PA 45 deg
  source_model.append( GaussianSource(ns,name="S2",I=20.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S2,
                  spi=-0.8,freq0=ref_frequency,
                  size=[0.000144,4.8e-5],phi=2.3561945));

  # central 'nuclear' point source with flat spectrum
  source_model.append( PointSource(ns,name="S3",I=1.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S3,
                  spi=0.0,freq0=ref_frequency));
  
  # SW extended lobe 21 x 15 srcsec in PA 33 deg
  source_model.append( GaussianSource(ns,name="S4",I=15.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S4,
                  spi=-0.75,freq0=ref_frequency,
                  size=[0.0001,7.2e-5],phi=2.15));

  # SW 'hot spot' 2 x 2 arc sec symmetric
  source_model.append( GaussianSource(ns,name="S5",I=5.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S5,
                  spi=-0.4,freq0=ref_frequency,
                  size=9.6e-6, symmetric=True));
  return source_model

def additional_point_sources (ns,tablename=''):
  """ define model source positions and flux densities """

# define five simple point sources
  source_model = []
  source_model.append( PointSource(ns,name="S6",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S6,
                  spi=-1.5,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S7",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S7,
                  spi=-1.0,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S8",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S8,
                  spi=1.0,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S9",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S9,
                  spi=1.5,freq0=ref_frequency));

  source_model.append( PointSource(ns,name="S10",I=2.0, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S10,
                  spi=2.0,freq0=ref_frequency));

  return source_model

def faint_source (ns,tablename=''):
  """ define model source positions and flux densities """
  
  source_model = []
# note - with 16 channels and sample step of 60 sec a source of 0.01
# turns out to be ~ 5 sigma with 600 MHz BW if we use test noise units of 1
  source_model.append( PointSource(ns,name="S11",I=0.01, Q=0.0, U=0.0, V=0.0,
                   direction=direction.S11,
                  spi=0.0,freq0=ref_frequency));
  return source_model

def EJones_pretab (ns,array,sources,name="E"):
  """creates E nodes for simulating the CLAR beam, with elevation-dependent
  broadening. The V_GAIN:src parameter is read from a MEP table, i.e it 
  should have been pre-tabulated by running clar_fit_dq.
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
  
  Ej0 = ns[name];
  # create per-direction, per-station E Jones matrices
  for src in sources:
    dirname = src.direction.name;
    Ej = Ej0(dirname);
    vgain = ns.V_GAIN(dirname);
    if not Ej(array.stations()[0]).initialized():
      for station in array.stations():
        # voltage gain parameter read from mep (filled by clar_fit_dq)
        vg = vgain(station) << Meq.Parm(table_name=mep_derived);
        # derive diagonal term
        ediag = ns.ediag(dirname,station) << Meq.Sqrt(Meq.Exp(vg*ns.ihpbw_sq));
        # create E matrix
        Ej(station) << Meq.Matrix22(ediag,0,0,ediag);
  return Ej0;

def EJones (ns,array,observation,sources,name="E"):
  """creates E nodes for simulating the CLAR beam, with elevation-dependent
  broadening. V_GAIN is computed from scratch
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
  
  Ej0 = ns[name];
  # create per-direction, per-station E Jones matrices
  for st in array.stations():
    # get station position node
    xyz = array.xyz()(st);
    # first create AzEl node for field_centre as seen from this station
    azel0 = ns.azel0(st) << Meq.AzEl(radec=observation.radec0(),xyz=xyz)
    # get squared sine of elevation of field centre - used later to determine 
    # CLAR beam broadening
    sin_el_sq = ns.sin_el_sq(st) << Meq.Sqr(Meq.Sin(ns.el0(st) << Meq.Selector(azel0,index=1)));
    # now for every source...
    for src in sources:
      name = src.direction.name;
      Ej = Ej0(name,st);
      if not Ej.initialized():
        # create AzEl node for source as seen from this station
        azel = ns.azel(name,st) << Meq.AzEl(radec=src.radec(),xyz=xyz);

        # do computation of LMN of source wrt field centre in AzEl frame
        lmn_azel = ns.lmn_azel(name,st) << Meq.LMN(radec_0=azel0,radec=azel);
        l_azel = ns.l_azel(name,st) << Meq.Selector(lmn_azel,index=0);
        m_azel = ns.m_azel(name,st) << Meq.Selector(lmn_azel,index=1);

        # compute CLAR voltage gain as seen for this source at this station
        # first square L and M
        l_sq = ns.l_sq(name,st) << Meq.Sqr(l_azel);
        m_sq = ns.m_sq(name,st) << Meq.Sqr(m_azel);

        # add L and M gains together, then multiply by log 16
        vgain = ns.v_gain(name,st) << ( l_sq + m_sq*sin_el_sq )*ln16;
        # make scalar matrix
        Ej << Meq.Sqrt(Meq.Exp(vgain*ns.ihpbw_sq));
  return Ej0;
      
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
 
  # create per-source,per-station E Jones matrices and attach them
  # to sources
  Ej0 = ns[name];
  for src in sources:
    dirname = src.direction.name;
    Ej = Ej0(src.direction.name);
    if not Ej.initialized():
      lmn = src.lmn(observation.radec0());
      l = ns.l(dirname) << Meq.Selector(lmn,index=0);
      m = ns.m(dirname) << Meq.Selector(lmn,index=1);

      # compute CLAR voltage gain as seen for this source at this station
      # first square L and M
      l_sq = ns.l_sq(dirname) << Meq.Sqr(l);
      m_sq = ns.m_sq(dirname) << Meq.Sqr(m);

      # add L and M gains together, then multiply by log 16
      vgain = ns.v_gain(dirname) << ( l_sq + m_sq )*ln16;

      # this now needs to be multiplied by width and exponent taken to get the
      # true beam power
      ediag = ns.ediag(dirname) << Meq.Sqrt(Meq.Exp(vgain*ns.ihpbw_sq));

      Ej << Meq.Matrix22(ediag,0,0,ediag);
  return Ej0;

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

