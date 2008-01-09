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

# This script is just Oleg's sky_models.py script from the January 2007
# workshop 

from Timba.TDL import *
import Meow
import math

# define desired half-intensity width of power pattern (HPBW)
# as we are fitting total intensity I pattern (here .021 rad = 74.8 arcmin)
FWHM  = 0.021747 # beam FWHM


def imagesize ():
  """Returns current image size, based on grid size and step""";
  return grid_size*grid_step;

def point_source (ns,name,l,m,I=1):
  """shortcut for making a pointsource with a direction""";
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=I);

def cross_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a cross""";
  model = [point_source(ns,basename+"+0+0",l0,m0,I)];
  dy = 0;
  for dx in range(-nsrc,nsrc+1):
    if dx:
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  dx = 0;
  for dy in range(-nsrc,nsrc+1):
    if dy:
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

def mbar_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a line along the m axis""";
  model = [];
  model.append(point_source(ns,basename+"+0",l0,m0,I));
  for dy in range(-nsrc,nsrc+1):
    if dy:
      name = "%s%+d" % (basename,dy);
      model.append(point_source(ns,name,l0,m0+dm*dy,I));
  return model;

def lbar_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a line along the m axis""";
  model = [];
  model.append(point_source(ns,basename+"+0",l0,m0,I));
  for dx in range(-nsrc,nsrc+1):
    if dx:
      name = "%s%+d" % (basename,dx);
      model.append(point_source(ns,name,l0+dl*dx,m0,I));
  return model;
  
def star8_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in an 8-armed star""";
  model = [ point_source(ns,basename+"+0+0",l0,m0,I) ];
  for n in range(1,nsrc+1):
    for dx in (-n,0,n):
      for dy in (-n,0,n):
        if dx or dy:
          name = "%s%+d%+d" % (basename,dx,dy);
          model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

def grid_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a grid""";
  model = [ point_source(ns,basename+"+0+0",l0,m0,I) ];
  for dx in range(-nsrc,nsrc+1):
    for dy in range(-nsrc,nsrc+1):
      if dx or dy:
        name = "%s%+d%+d" % (basename,dx,dy);
        model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

def make_model (ns,basename="S",l0=0,m0=0,I=1):
  """Creates and returns selected model""";
  return model_func(ns,basename,l0,m0,grid_step*FWHM,grid_step*FWHM,(grid_size-1)/2,I);


# model options
TDLCompileOption("model_func","Model type",[cross_model,grid_model,star8_model,lbar_model,mbar_model]);
TDLCompileOption("grid_size","Number of sources in each direction",[1,3,5,7],more=int);
TDLCompileOption("grid_step","Grid step, in units of FWHM",[.1,0.25,.5,1],more=float);


