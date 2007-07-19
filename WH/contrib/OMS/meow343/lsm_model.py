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


def LSMToMeowList (ns,lsm,count=999999999,**kw):
  """Reads in up to 'count' sources from the given LSM object,
  and constructs a list of Meow components.
  To represent the source parameters by Parms, pass in Meow parms using
  the following keywords: I,Q,U,V,ra,dec,spi,freq0,RM,sx,sy,phi. You
  can also override these parameters by supplying constants.
  """
  source_model = []

## Note: conversion from AIPS++ componentlist Gaussians to Gaussian Nodes
### eX, eY : multiply by 2
### eP: change sign

  plist = lsm.queryLSM(count=count);
  
  for pu in plist:
    src = {};
    ( src['ra'],src['dec'],
      src['I'],src['Q'],src['U'],src['V'],
      src['spi'],src['freq0'],src['RM']    ) = pu.getEssentialParms(ns)
    (eX,eY,eP) = pu.getExtParms()
    # scale 2 difference
    src['sx'] = eX*2
    src['sy'] = eY*2
    src['phi'] = -eP
    # override zero values with None so that Meow can make smaller trees
    if not src['spi']:
      src['spi'] = src['freq0'] = None;
    if not src['RM']:
      src['RM'] = None;
    # construct parms or constants for source attributes
    for key,value in src.iteritems():
      meowparm = kw.get(key);
      if isinstance(meowparm,Meow.Parm):
        src[key] = meowparm.new(value);
      elif meowparm is not None:
        src[key] = value;
      
    direction = Meow.Direction(ns,pu.name,src['ra'],src['dec']);

    if eX or eY or eP:
      # Gaussians
      source_model.append( 
         Meow.GaussianSource(ns,name=pu.name,
             I=src['I'],Q=src['Q'],U=src['U'],V=src['V'],
             direction=direction,
             spi=src['spi'],freq0=src['freq0'],
             size=[src['sx'],src['sy']],phi=src['phi']));
    else:
      # point Sources
      source_model.append( 
         Meow.PointSource(ns,name=pu.name,
             I=src['I'],Q=src['Q'],U=src['U'],V=src['V'],
             direction=direction,
             spi=src['spi'],freq0=src['freq0'],RM=src['RM']));

  return source_model
