# History:
# - 2006.10.31: creation

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
import pxk_tools as tools


def moving_source(ns, ANTENNAS=14):
  """ Create moving source manually """
  
  # Set l,m position of moving source
  v_min_hr = 2.5
  ARCMIN   = (math.pi/180.)/60.0 
  t0,t1,ts = tools.scaled_time(ns)
  f0,f1,fs = tools.scaled_freq(ns)
  l0,m0    = (0,0)
  l        = ns.L << (l0 - (v_min_hr/3600)*(Meq.Time()-t0)) * ARCMIN * fs 
  m        = ns.M << (m0 - (v_min_hr/3600)*(Meq.Time()-t0)) * ARCMIN * fs 
  n        = Meq.Sqrt(1-l*l-m*m) 
  ns.lmn_minus1 << Meq.Composer(l,m,n-1)     
  tools.Book_Mark(ns.L, 'L')
  tools.Book_Mark(ns.M, 'M')
  ns.radec0= Meq.Composer(ns.ra<<0,ns.dec<<0) 
  ns.xyz0  = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0) 

  # Make transient function
  hours    = 12
  func2    = tools.time_band(ns, 0.0, 60*hours, 'box')
    
  for p in ANTENNAS:
    # xyz-pos and uvw-coords
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0) 
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)) 

    # K Jones
    ns.K(p)   << Meq.VisPhaseShift(lmn=ns.lmn_minus1,uvw=ns.uvw(p)) 
    ns.Kt(p)  << Meq.ConjTranspose(ns.K(p)) 

    # G Jones
    ns.G(p)   << Meq.Identity(func2)
    ns.Gt(p)  << Meq.ConjTranspose(ns.G(p))
    if p<5: tools.Book_Mark(ns.G(p), "G Jones"); pass
    pass

  # Create source
  I=1; Q=0; U=0; V=0;
  ns.B << 0.5 * Meq.Matrix22(I+Q,Meq.ToComplex(U,V),Meq.ToComplex(U,-V),I-Q) 

  # Corrupt source
  IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ] 
  for p,q in IFRS:
    predict = ns.predict(p,q) << Meq.MatrixMultiply(
      ns.G(p),
      ns.K(p),
      ns.B,
      ns.Kt(q),
      ns.Gt(q))
    ns.sink(p,q) << Meq.Sink(predict,
                             station_1_index=p-1,
                             station_2_index=q-1,output_col='DATA')
    pass

  # Write data
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS])
  pass


def KGE(ns, ANTENNAS=14):
  """ Manually aply K, G, and E Jones """
  IFRS   = [ (p,q) for p in ANTENNAS for q in ANTENNAS if p<q ]
  ARCMIN = (math.pi/180.)/60.0
  I=1; Q=.2; U=.2; V=.2;

  # nodes for phase center and array reference position
  ns.radec0= Meq.Composer(ns.ra<<0,ns.dec<<0) 
  ns.xyz0  = Meq.Composer(ns.x0<<0,ns.y0<<0,ns.z0<<0) 

  # define per-station xyz-pos / uvw-coords
  for p in ANTENNAS:
    ns.xyz(p) << Meq.Composer(ns.x(p)<<0,ns.y(p)<<0,ns.z(p)<<0) 
    ns.uvw(p) << Meq.UVW(radec=ns.radec0,xyz_0=ns.xyz0,xyz=ns.xyz(p)) 
    pass
  
  # define source brightness B0 (unprojected, same for all sources)
  ns.B0 << 0.5 * Meq.Matrix22(I+Q, Meq.ToComplex(U,V),
                              Meq.ToComplex(U,-V),I-Q)

  a  = 3  # arcmin separation
  n  = 4  # even number works best
  LM = []
  for i in range(n+1):
    for j in range(n+1):
      LM.append(((i-n/2)*a, (j-n/2)*a))
      pass
    pass

  SOURCES = range(len(LM))

  # source l,m,n-1 vectors
  for src in SOURCES:
    l,m = LM[src]
    l   = l*ARCMIN
    m   = m*ARCMIN
    n   = math.sqrt(1-l*l-m*m)
    ns.lmn_minus1(src) << Meq.Composer(l,m,n-1)
    ns.B(src) << Meq.Identity(ns.B0)    # projected brightness
    pass

  
  # define Jones matrices
  for p in ANTENNAS:

    # define G-jones matrices, source INdependent 
    ns.G(p)  << Meq.Matrix22(1,0,0,1)
    ns.Gt(p) << Meq.ConjTranspose(ns.G(p))

    for src in SOURCES:
      # define K-jones matrices; source DEpendent
      ns.K (p,src) << Meq.VisPhaseShift(lmn=ns.lmn_minus1(src), uvw=ns.uvw(p))
      ns.Kt(p, src) << Meq.ConjTranspose(ns.K(p,src))

      # define E-jones matrices; station DEpendent
      l,m     = LM[src];
      l       = l * ARCMIN
      m       = m * ARCMIN
      f0,f1,fs= tools.scaled_freq(ns)
      labda   = 3e8/(Meq.Freq() * (1+fs))  # freq-dependency of beam
      r       = math.sqrt(l*l + m*m)
      ns.E (p,src) << Meq.Pow(Meq.Cos((math.pi/2) * r*25/labda),3)
      ns.Et(p,src) << Meq.ConjTranspose(ns.E(p,src));
      pass
    pass
  
  # now define predicted visibilities, attach to sinks
  for p,q in IFRS:

    # make source DEpendent predicted visibilities (image-plane effects)
    for src in SOURCES:
      ns.predict_s_dep(p,q,src) << Meq.MatrixMultiply(
        ns.E (p,src),
        ns.K (p,src),
        ns.B (src),
        ns.Kt(q,src),
        ns.Et(q,src));
      pass

    # and sum them up via an Add node
    predict_s_dep = ns.predict_s_dep(p,q) << Meq.Add(\
      *[ns.predict_s_dep(p,q,src) for src in SOURCES]);

    # make source INdependent predicted visibilities (uv-plane effects)
    predict = ns.predict(p,q) << Meq.MatrixMultiply(
      ns.G (p),
      predict_s_dep,
      ns.Gt(q));
    
    ns.sink(p,q) << Meq.Sink(predict,
                             station_1_index = p-1,
                             station_2_index = q-1,output_col='DATA');
    pass
  
  # define VisDataMux
  ns.vdm << Meq.VisDataMux(*[ns.sink(p,q) for p,q in IFRS]);

  # some bookmarks
  tools.Book_Mark(ns.K(2,0), 'K Jones') # different stations, sources
  tools.Book_Mark(ns.K(9,0), 'K Jones')
  tools.Book_Mark(ns.K(2,1), 'K Jones')
  tools.Book_Mark(ns.K(9,1), 'K Jones')

  tools.Book_Mark(ns.E(1,0), 'E Jones') # different stations, sources
  tools.Book_Mark(ns.E(2,0), 'E Jones')
  tools.Book_Mark(ns.E(3,1), 'E Jones')
  tools.Book_Mark(ns.E(4,1), 'E Jones')

  tools.Book_Mark(ns.G(1),   'G Jones') # different stations
  tools.Book_Mark(ns.G(2),   'G Jones')
  tools.Book_Mark(ns.G(3),   'G Jones')
  tools.Book_Mark(ns.G(4),   'G Jones')
  pass

