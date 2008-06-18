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

# this contains parallelization-related options
from Timba.TDL import *

mpi_enable = False;
parallelize_by_source = False;
mpi_nproc = False;

_options = [ 
    TDLMenu('Enable MPI',
              toggle='mpi_enable',
      *[ 
          TDLOption('mpi_nproc',"Number of processors to distribute to",[2,4,8],more=int),
          TDLOption('parallelize_by_source',"Enable parallelization by source",False),
        ]
    )
];

def compile_options ():
  global _options;
  return _options;

