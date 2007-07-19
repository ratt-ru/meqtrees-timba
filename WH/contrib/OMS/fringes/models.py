#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
import Meow
from Meow.PointSource import *
from Meow.GaussianSource import *
import random

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
                       Iorder=0, direction=(0.0305432619099,0.575958653158),
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
                  Iorder=0, direction=(0.0304,0.57632),
                  spi=0,freq0=ref_frequency,
                  size=[0.0001,7.2e-5],phi=2.15,
                  parm_options=parm_options) ];
                  
# limits for distributing sources on grid
ra_lim  = [ 0.0300,0.0312 ];
dec_lim = [ 0.5764,0.5754 ];
                

def random_sources (ns,tablename,count=25,next=8,flux=.1,prefix='F'):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
  source_model = [];
  for i in range(count):
    ra = random.uniform(*ra_lim);
    dec = random.uniform(*dec_lim);
    # add a point source or a gaussian 
    if i >= next:
      source_model.append(PointSource(ns,name=prefix+str(i),
                  I=random.uniform(flux/2,flux), Q=0.0, U=0.0, V=0.0,
                  Iorder=0, direction=(ra,dec),
                  spi=0,freq0=ref_frequency,
                  parm_options=parm_options)); 
    else:
      source_model.append(GaussianSource(ns,name=prefix+str(i),
                  I=random.uniform(flux,flux*3), Q=0.0, U=0.0, V=0.0,
                  Iorder=0, direction=(ra,dec),
                  spi=0,freq0=ref_frequency,
                  size=[random.uniform(1e-5,1e-4),random.uniform(1e-5,1e-4)],
                  phi=random.uniform(0,3.14),
                  parm_options=parm_options)); 
      
  return source_model;
  
def grid_of_faint_sources (ns,tablename):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
  ngrid = 4;
  source_model = [];
  for i in range(ngrid):
    for j in range(ngrid):
      ra = ra_lim[0] + i*(ra_lim[1]-ra_lim[0])/(ngrid-1);
      dec = dec_lim[0] + j*(dec_lim[1]-dec_lim[0])/(ngrid-1);
      # add a point source or a gaussian (2/3 point sources)
      if random.choice([0,1]):
        source_model.append(PointSource(ns,name="F"+str(i)+str(j),
                    I=random.uniform(.05,.1), Q=0.0, U=0.0, V=0.0,
                    Iorder=0, direction=(ra,dec),
                    spi=0,freq0=ref_frequency,
                    parm_options=parm_options)); 
      else:
        source_model.append(GaussianSource(ns,name="F"+str(i)+str(j),
                    I=random.uniform(.1,.3), Q=0.0, U=0.0, V=0.0,
                    Iorder=0, direction=(ra,dec),
                    spi=0,freq0=ref_frequency,
                    size=[random.uniform(1e-5,1e-4),random.uniform(1e-5,1e-4)],
                    phi=random.uniform(0,3.14),
                    parm_options=parm_options)); 
      
  return source_model;

def faint_point_source (ns,tablename):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
      
  return [ PointSource(ns,name="S4",I=.1, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, direction=(0.0304,0.57632),
                  spi=0,freq0=ref_frequency,
                  parm_options=parm_options) ];


def two_point_sources (ns,tablename=''):
  parm_options = record(
      table_name=tablename,
      node_groups='Parm');
  
  source_model = []
  source_model.append( PointSource(ns,name="S1",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, direction=(0.0307473161,0.575848368),
                  spi=0,freq0=ref_frequency,
                  parm_options=parm_options));

  source_model.append( PointSource(ns,name="S5",I=1.0, Q=0.0, U=0.0, V=0.0,
                  Iorder=0, direction=(0.0303428649,0.575848368),
                  spi=0,freq0=ref_frequency,
                  parm_options=parm_options));

  return source_model
  
def two_bright_one_faint_point_source (ns,tablename=''):
  source_model = two_point_sources(ns,tablename) + \
                 faint_point_source(ns,tablename);

  return source_model

def two_point_sources_plus_grid (ns,tablename=''):
  source_model = two_point_sources(ns,tablename) + \
                 grid_of_faint_sources(ns,tablename);
  return source_model

def two_point_sources_plus_random (ns,tablename=''):
  source_model = two_point_sources(ns,tablename) + \
                 random_sources(ns,tablename,flux=.1);
  return source_model

def two_point_sources_plus_random_uJy (ns,tablename=''):
  source_model = two_point_sources(ns,tablename) + \
                 random_sources(ns,tablename,flux=1e-6);
  return source_model
  
def two_point_sources_plus_random_nJy (ns,tablename=''):
  source_model = two_point_sources(ns,tablename) + \
                 random_sources(ns,tablename,count=25,next=8,flux=1e-8,prefix='n');
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

