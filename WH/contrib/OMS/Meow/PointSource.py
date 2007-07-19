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
from Timba.Meq import meq
from SkyComponent import *
import Jones
import Context
  
STOKES = ("I","Q","U","V");

class PointSource(SkyComponent):
  def __init__(self,ns,name,direction,
               I=0.0,Q=None,U=None,V=None,
               spi=None,freq0=None,
               RM=None):
    """Creates a PointSource with the given name; associates with 
    direction. 
    'direction' is a Direction object or a (ra,dec) tuple
    'I' is I flux (constant, node, or Meow.Parm)
    Optional arguments:
      'Q','U','V' are constants, nodes, or Meow.Parms. If none of the three 
          are supplied, an unpolarized source representation is used.
      'spi' and 'freq0' are constants, nodes or Meow.Parms. If both are
          supplied, a spectral index is added, otherwise the fluxes are
          constant in frequency.
      'RM' is rotation measure (constants, nodes or Meow.Parms). If None,
          no intrinsic rotation measure is used.
    """;
    SkyComponent.__init__(self,ns,name,direction);
    self._add_parm('I',I,tags="flux");
    # check if polarized
    # NB: disable for now, as Sink can't handle scalar results
    self._polarized = True;
    # self._polarized = Q is not None or U is not None or V is not None or RM is not None:
    self._add_parm('Q',Q or 0.,tags="flux pol");
    self._add_parm('U',U or 0.,tags="flux pol");
    self._add_parm('V',V or 0.,tags="flux pol");
    # see if a spectral index is present (freq0!=0 then), create polc
    self._has_spi = spi is not None or freq0 is not None;
    if self._has_spi:
      self._add_parm('spi',spi or 0.,tags="spectrum");
      # for freq0, use placeholder node for first MS frequency,
      # unless something else is specified 
      self._add_parm('spi_fq0',freq0 or (ns.freq0 ** 0),tags="spectrum");
    # see if intrinsic rotation measure is present
    self._has_rm = RM is not None;
    if self._has_rm:
      self._add_parm("RM",RM,tags="pol");
      
  def stokes (self,st):
    """Returns flux node for this source. 'st' must be one of 'I','Q','U','V'.
    (This is the flux after RM has been applied, but without spi).
    """;
    if st not in STOKES:
      raise ValueError,"st: must be one of 'I','Q','U','V'";
    # rotation measure rotates Q-U with frequency. So if no RM is given,
    # or if we're just asked for an I or V node, return it as is
    if st == "I" or st == "V" or not self._has_rm:
      return self._parm(st);
    else:
      stokes = self.ns[st+'r'];
      if stokes.initialized():
        return stokes;
      q = self._parm("Q");
      u = self._parm("U");
      # squared wavelength
      freq = self.ns0.freq ** Meq.Freq;
      iwl2 = self.ns0.wavelength2 << Meq.Sqr(2.99792458e+8/freq);
      # rotation node
      farot = self.ns.farot << self._parm("RM")*iwl2;
      cosf = self.ns.cos_farot << Meq.Cos(farot);
      sinf = self.ns.sin_farot << Meq.Sin(farot);
      self.ns.Qr << cosf*q - sinf*u;
      self.ns.Ur << sinf*q + cosf*u;
      return self.ns[st+'r'];
      
  def norm_spectrum (self):
    """Returns spectrum normalized to 1 at the reference frequency.
    Flux should be multiplied by this to get the real spectrum""";
    if not self._has_spi:
      return 1;
    nsp = self.ns.norm_spectrum;
    if not nsp.initialized():
      freq = self.ns0.freq ** Meq.Freq;
      nsp << Meq.Pow(freq/self._parm('spi_fq0'),self._parm('spi'));
    return nsp;
    
  def coherency (self,observation=None):
    """Returns the coherency matrix for a point source.
    'observation' argument is used to select a linear or circular basis;
    if not supplied, the global context is used.""";
    observation = observation or Context.observation;
    if not observation:
      raise ValueError,"observation not specified in global Meow.Context, or in this function call";
    coh = self.ns.coherency;
    if not coh.initialized():
      # if not polarized, just return I
      if not self._polarized:
        coh << self.stokes("I")*0.5*self.norm_spectrum();
      elif observation.circular():
        # create coherency elements
        rr = self.ns.rr << (self.stokes("I") + self.stokes("V"));
        rl = self.ns.rl << Meq.ToComplex(self.stokes("Q"),self.stokes("U"));
        lr = self.ns.lr << Meq.Conj(rl);
        ll = self.ns.ll << (self.stokes("I") - self.stokes("V"));
        # create coherency node
        coh << Meq.Matrix22(rr,rl,lr,ll)*0.5*self.norm_spectrum();
      else:
        # create coherency elements
        xx = self.ns.xx << (self.stokes("I") + self.stokes("Q"));
        xy = self.ns.xy << Meq.ToComplex(self.stokes("U"),self.stokes("V"));
        yx = self.ns.yx << Meq.Conj(xy);
        yy = self.ns.yy << (self.stokes("I") - self.stokes("Q"));
        # create coherency node
        coh << Meq.Matrix22(xx,xy,yx,yy)*0.5*self.norm_spectrum();
    return coh;

  def make_visibilities (self,nodes,array=None,observation=None):
    observation = observation or Context.observation;
    # create lambda to return the same coherency at all baselines
    cohnode = lambda p,q: self.coherency(observation);
    # use direction's phase shift method
    self.direction.make_phase_shift(nodes,cohnode,array,observation.phase_center);
   
