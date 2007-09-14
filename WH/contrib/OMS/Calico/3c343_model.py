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
from ParmGroup import ParmGroup

TDLCompileOption("spectral_index","Spectral index, 3C343",[None,0.],more=float,
    doc="""Spectral index of source, use None for a flat spectrum""");
TDLCompileOption("spectral_index1","Spectral index, 3C343.1",[None,0.],more=float,
    doc="""Spectral index of source, use None for a flat spectrum""");
TDLCompileOption("ref_freq","SpI reference frequency, MHz",1421,more=float);

options = [];

def runtime_options ():
  return options;

def source_list (ns):
  # figure out spectral index parameters
  if spectral_index is not None:
    spi_def = Meow.Parm(spectral_index);
    freq0_def  = ref_freq;
  else:
    spi_def = freq0_def = None;
  if spectral_index1 is not None:
    spi_def1 = Meow.Parm(spectral_index1);
    freq0_def1  = ref_freq;
  else:
    spi_def1 = freq0_def1 = None;
  # and flux parameters
  i_def = Meow.Parm(1);
  quv_def = Meow.Parm(0);
  
  dir1 = Meow.LMDirection(ns,"3C343.1",4.356645791155902,1.092208429052697);
  dir0 = Meow.LMDirection(ns,"3C343",4.3396003966265599,1.0953677174056471);
  
  src1 = Meow.PointSource(ns,"3C343.1",dir1,I=i_def,Q=quv_def,U=quv_def,V=quv_def,
                          spi=spi_def1,freq0=freq0_def1);
  src0 = Meow.PointSource(ns,"3C343",dir0,I=i_def,Q=quv_def,U=quv_def,V=quv_def,
                          spi=spi_def1,freq0=freq0_def1);
  
  # define a parmgroup for source parameters
  # now make a solvejobs for the source
  pg_src = ParmGroup("source",
              src1.coherency().search(tags="solvable") + src0.coherency().search(tags="solvable"),
              individual=True,
              bookmark=True);
  # now make a solvejobs for the source
  options.append(pg_src.make_solvejob_menu("Calibrate source fluxes"));
  
  return [ src1,src0 ];
