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
from Meow.Utils import *
from Meow.Direction import *
from Meow.PointSource import *
from Meow.GaussianSource import *
#from Meow.Shapelet import *

from Timba.LSM.LSM import LSM


def point_and_extended_sources (ns,lsm,tablename='',count=100):
  """ define two extended sources: positions and flux densities """
  parm_options = record(
      use_previous=False,
      table_name=tablename,
      node_groups='Parm');
  

  source_model = []

##
## Note: conversion from AIPS++ componentlist Gaussians to Gussian Nodes
### eX, eY : multiply by 2
### eP: change sign

  plist=lsm.queryLSM(count=count)

  for pu in plist:
     (ra,dec,sI,sQ,sU,sV,SIn,f0,RM)=pu.getEssentialParms(ns)
     (eX,eY,eP)=pu.getExtParms()
     # scale 2 difference
     eX=eX*2
     eY=eY*2
     eP=-eP
     if eX!=0 or eY!=0 or eP!=0:
         # Gaussians
         source_model.append( GaussianSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0,
                  size=[eX,eY],phi=eP,
                  parm_options=parm_options));
     else:
         # point Sources
         source_model.append( PointSource(ns,name=pu.name,I=sI, Q=sQ, U=sU, V=sV,
                  Iorder=0, direction=Direction(ns,pu.name,ra,dec,parm_options=parm_options),
                  spi=SIn,freq0=f0, RM=RM,
                  parm_options=parm_options));



  return source_model
