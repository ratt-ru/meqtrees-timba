# History:
# - 2006.11.06: creation
# - 2006.11.20: changed SourceList.custum_model a bit
# - 2006.11.23: added SourceList.copy()
#               added LM()
#               added SourceList.add_random()
# - 2006.11.29: added SourceList.maxrad



# standard preamble
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

from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow
import random
import pxk_tools



########################################################################
def LM(kind='circle', r=7, lm0=(0,0), nsrc=3, offset=-0.5*math.pi):
  """ create LM coordinate list
  """
  if kind=='circle':
    LM          = [(0,0)]
    for i in range(nsrc):
      th = offset + math.pi*2*i/nsrc
      LM.append((lm0[0] + r*math.cos(th),
                 lm0[1] + r*math.sin(th)))
      pass
    pass
  return LM




########################################################################
class SourceList:
  """ create source_list
  """
  
  DEG         = math.pi/180.    # useful constant: 1 deg in radians
  ARCMIN      = DEG/60 
  num_sources = 0
  

  def __init__ (self, ns=None, kind='custom',
                lm0=(0,0), dlm=(5,5), nsrc=2, LM=[(0,0)],
                I=1,  Q=0,  U=0,  V=0, LIST=None, LM_list=None):
    """ Create list of sources
    """
    self.sources     = []
    self.maxrad      = 0; # maximum radius of image

    
    # Create source list
    if   ns is None:
      if LIST is None:
        print "___ Creating empty SourceList"
        self.LM      = []
        pass
      pass
    elif kind=='custom':
      print "___ Creating custom SourceList"
      self.custom_model(ns, LM, I=I, Q=Q, U=U, V=V)
    elif kind=='cross':
      print "___ Creating cross SourceList"
      self.cross_model (ns, 'cross', I=I, Q=Q, U=U, V=V,
                        lm0=lm0, dlm=dlm, nsrc=nsrc)
    elif kind=='grid':
      print "___ Creating grid SourceList"
      self.grid_model  (ns, 'grid',  I=I, Q=Q, U=U, V=V,
                        lm0=lm0, dlm=dlm, nsrc=nsrc)
      pass

    # Copy source list
    if LIST is not None:
      self.copy_list(LIST)
      pass
    pass

  def test(self):
    return [(1,0)]


  def copy_list(self, LIST):
    print "___ Copying SourceList"
    self.sources = [src for src in LIST.sources]
    self.LM      = [lm  for lm  in LIST.LM]
    self.maxrad  = LIST.maxrad
    pass

  def copy(self):
    """ create copy of list and return it """
    list_copy = SourceList(LIST = self)
    return list_copy
    
  def set_lm (self, LM=[(0,0)]):
    """ Set LM coords per source in arcmin"""
    self.LM   = []
    for isrc in range(len(LM)):
      l           = LM[isrc][0]
      m           = LM[isrc][1]
      self.maxrad = max(abs(l)+.5, abs(m)+.5, self.maxrad);
      self.LM.append((l*self.ARCMIN, m*self.ARCMIN)) 
      pass
    pass

  def point_source (self, ns,name,l,m, I=1, Q=0, U=0, V=0):
    srcdir = Meow.LMDirection(ns,name,l,m) 
    return Meow.PointSource(ns,name,srcdir,I=I,Q=Q,U=U,V=V) 
  
  def gauss_source (self, ns,name,l,m, I=1, Q=0, U=0, V=0):
    srcdir = Meow.LMDirection(ns,name,l,m) 
    return Meow.GaussianSource(
      ns,name,srcdir,
      I     = I, Q=Q, U=U, V=V,
      size  = [6*self.ARCMIN,2*self.ARCMIN],
      phi   = math.pi/4.0,
      spi   = 2.0,
      freq0 = 1400e6) 

  def add_random(self, ns, nsrc=1, I=[0.1,1.0], Q=[0,0], U=[0,0], V=[0,0],
                 lm0=(0,0), rmax=15, kind=point_source):
    """ Add 'nsrc' number of random sources
    nsrc  : number of sources to add
    IQUV  : Stokes values vary in range [min,max]
    lm0   : pointing center
    r     : Max distance to x,y-axes (through pointing center)
    """
    for n in range(nsrc):
      
      # create random (l,m) coords
      l           = random.uniform(-rmax, rmax)
      m           = random.uniform(-rmax, rmax)
      self.maxrad = max(abs(l)+.5, abs(m)+.5, self.maxrad);
      l          *=  self.ARCMIN
      m          *=  self.ARCMIN
      self.LM.append((l, m))

      # create random Stokes parameters
      Ir  = random.uniform(I[0], I[1])
      Qr  = random.uniform(Q[0], Q[1])
      Ur  = random.uniform(U[0], U[1])
      Vr  = random.uniform(V[0], V[1])

      # add source
      name = "S%s" % (self.num_sources + n)
      self.add_source(kind(self, ns, name,l,m, I=Ir, Q=Qr, U=Ur, V=Vr))
      pass
    pass
  
  def create_list(self, ns, LIST, basename,
                  lm0=(0,0), dlm=(5,5), kind=point_source,I=1,Q=0,U=0,V=0):
    """ Create a source list from a given set of (l,m) coords
    """
    # Create LM list
    LM    = []
    names = []
    for n in LIST:
      dx,dy = n
      l     = lm0[0] + dlm[0]*dx
      m     = lm0[1] + dlm[1]*dy
      LM.append((l,m))
      #names.append("%s%+d%+d" % (basename,l,m))
      pass
    self.set_lm(LM) # convert to arc-minutes

    # create source list
    for isrc in range(len(self.LM)):
      names.append("S%s" % (isrc))
      l,m     = self.LM[isrc] 
      self.add_source(kind(self, ns, names[isrc],l,m, I=I, Q=Q, U=U, V=V))
      pass
    pass

  def cross_model (self, ns, basename, lm0=(0,0), dlm=(5,5), nsrc=2,
                   kind=point_source, I=1, Q=0, U=0, V=0):
    """ Creates source-list with sources arranged in a cross
    lm0     : coords of center of cross, in arcmin
    dlm     : separation between sources in arcmin
    """

    # Create LM list (source positions in arcmin)
    LIST = [(0,0)]
    for n in range(1,nsrc+1):
      for dx,dy in ((n,0),(-n,0),(0,n),(0,-n)):
        LIST.append((dx,dy))
        pass
      pass

    # create source list
    self.create_list(ns, LIST, basename, lm0=lm0, dlm=dlm,
                     kind=kind,I=I,Q=Q,U=U,V=V)

    pass

  def grid_model (self, ns,basename, lm0=(0,0), dlm=(5,5), nsrc=1,
                  kind=point_source, I=1, Q=0, U=0, V=0):
    """ Creates source-list with sources arranged in a square grid
    lm0     : coords of center of grid, in arcmin
    dlm     : separation between sources in arcmin
    """

    # Create LM list
    LIST = []
    for dx in range(-nsrc,nsrc+1):
      for dy in range(-nsrc,nsrc+1):
        LIST.append((dx,dy))
        pass
      pass

    # create source list
    self.create_list(ns, LIST, basename, lm0=lm0, dlm=dlm,
                     kind=kind,I=I,Q=Q,U=U,V=V)
    pass

  def custom_model (self, ns, LM=[(0,0)], I=1, Q=0, U=0, V=0,
                    kind=point_source):
    """ Create custom model of sources
    """
    self.set_lm(LM)
    
    # loop (l,m) in LM, then create source and append to list
    for isrc in range(len(self.LM)):
      l,m     = self.LM[isrc] 
      name    = 'S'+str(isrc)  
      self.add_source(kind(self, ns, name,l,m, I=I, Q=Q, U=U, V=V))
      pass
    pass

  def add_source(self, source=point_source):
    self.sources.append(source)
    self.num_sources +=1
    pass

  def add_moving_source(self, ns, LM=(0,0), I=1, Q=0, U=0, V=0,
                        v_min_hr=0.25, kind=point_source):
    """ Adds a moving source, speed depends on frequency
    v_min_hr : speed of moving source in arcmin per hour
    kind     : type of source (point/gaussian)
    """

    # set LM coords for moving source
    t0,t1,ts = pxk_tools.scaled_time(ns)
    f0,f1,fs = pxk_tools.scaled_freq(ns)
    l,m      = LM
    l        = (l + v_min_hr/3600*(Meq.Time()-t0)) * self.ARCMIN * (1+fs) 
    m        = (m + v_min_hr/3600*(Meq.Time()-t0)) * self.ARCMIN * (1+fs) 
    self.LM.append((l,m))

    # create source
    name     = 'S'+str(self.num_sources) 
    src      = kind(self, ns,name,l,m, I=I, Q=Q, U=U, V=V)
    self.add_source(src)

    pass

  def add_transient (self, ns, LM=(0,0), I=1, Q=0, U=0, V=0,
                     t_start=0.5, t_min=60,
                     f_start=0.5, nchan=3, kind='real'):
    """ Makes a transient source and returns corrupted component
    t_start : move start-time of transient
    t_min   : transient time in minutes
    f_start : move start-freq of narrow-band
    nchan   : width of band in channels
    kind    : 'real' transient or 'box' function
    """

    # set LM coords
    l,m     = LM
    l      *= self.ARCMIN
    m      *= self.ARCMIN
    self.LM.append((l,m))

    # create source
    name    = 'S'+str(self.num_sources)  
    src     = self.point_source(ns, name, l, m, I=I, Q=Q, U=U, V=V)

    # Create source-dependent G Jones for transient
    trans  = pxk_tools.time_band(ns, t_start, t_min, kind=kind)
    band   = pxk_tools.freq_band(ns, f_start, nchan) 
    gain   = trans * band
    GJones = ns.Trans(src.direction.name) << Meq.Matrix22(gain,0,0,gain)
    pxk_tools.Book_Mark(GJones, "t/nu band")

    # corrupt *source* with GJones and add to source list
    corrupt = Meow.CorruptComponent(
      ns, src, 'Trans', jones=ns.Trans(src.direction.name) ) 
    self.add_source(corrupt)
    pass
  
  pass


