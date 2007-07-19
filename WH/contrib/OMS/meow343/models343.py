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

TDLCompileMenu("Source model options",
  TDLOption("_343_1_Iorder","3C343.1 I freq degree",[0,1,2,3],more=int,default=1),
  TDLOption("_343_1_Qorder","3C343.1 Q freq degree",[0,1,2,3],more=int,default=1),
  TDLOption("_343_Iorder","3C343 I freq degree",[0,1,2,3],more=int,default=3),
  TDLOption("_343_Qorder","3C343 Q freq degree",[0,1,2,3],more=int,default=3)
);

def m343_bright_duo (ns,tablename=''):
  return [ 
    Meow.PointSource(ns,name="3C343.1",
                     I=Meow.Parm(1,freq_deg=_343_1_Iorder,table_name=tablename,tags="bright"),
                     Q=Meow.Parm(0,freq_deg=_343_1_Qorder,table_name=tablename,tags="bright"),
                     direction=(4.356645791155902,1.092208429052697)),
    Meow.PointSource(ns,name='3C343',
                     I=Meow.Parm(1,freq_deg=_343_Iorder,table_name=tablename,tags="bright"),
                     Q=Meow.Parm(0,freq_deg=_343_Qorder,table_name=tablename,tags="bright"),
                     direction=(4.3396003966265599,1.0953677174056471)),
  ];

def m343_bright_duo_spi (ns,tablename=''):
  return [ 
    Meow.PointSource(ns,name="3C343.1",
                     I=Meow.Parm(1,freq_deg=_343_1_Iorder,table_name=tablename,tags="bright"),
                     Q=Meow.Parm(0,freq_deg=_343_1_Qorder,table_name=tablename,tags="bright"),
                     spi=Meow.Parm(0,table_name=tablename),
                     direction=(4.356645791155902,1.092208429052697)),
    Meow.PointSource(ns,name='3C343',
                     I=Meow.Parm(1,freq_deg=_343_Iorder,table_name=tablename,tags="bright"),
                     Q=Meow.Parm(0,freq_deg=_343_Qorder,table_name=tablename,tags="bright"),
                     spi=Meow.Parm(0,table_name=tablename),
                     direction=(4.3396003966265599,1.0953677174056471)),
  ];
