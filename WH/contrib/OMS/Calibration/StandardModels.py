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
  
  


