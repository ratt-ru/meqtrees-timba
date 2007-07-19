# History:
# - 2006.11.07: creation.
# - 2006.11.10: adjusted DJones: time dependency / randomness
# - 2006.11.16: added FJones
#               image-plane Jones now only corrupt sources so EJones
#               does not add the up in a patch anymore
# - 2006.11.20: added moving source to EJones



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
import pxk_tecs




def EJones (ns, slist, residual=0, alpha=0.0, beam="WSRT_moving"):
  """ create EJones (beam gain Jones) for each source. Beam is
  elongated in X-feed direction and squeezed in Y-feed direction.
  (image-plane effect)
  slist    : source list to apply EJones to
  residual : residuals will be made or not
  alpha    : ellipticity of feed-sensitivities
  beam     : type of beam
  """
  print "___ Applying E Jones", "[", str(residual), "]"
    
  for isrc in range(len(slist.sources)):

    # get l,m positions
    src     = slist.sources[isrc]    
    l,m     = slist.LM     [isrc] 

    if   beam[:4]=="WSRT": # pow = E^2 ~ cos^6
      
      if beam[-6:]=="moving" and not residual:
        l0      = pxk_tools.ARCMIN*-2.5 + pxk_tools.arcmin_per_obs(ns, 5.0)
        m0      = 0
        l       = l - l0
        m       = m - m0
        pass

      # create beam
      e     = []
      labda = 3e8/Meq.Freq()
      for feed in [['x',1], ['y',-1]]:
        r     = Meq.Sqrt(Meq.Pow2(l + alpha*feed[1]) +
                         Meq.Pow2(m - alpha*feed[1]))
        amp   = Meq.Pow(Meq.Cos((math.pi/2) * r*25/labda),3)
        phase = (r * 60.0)  # (r/ARCMIN) DEG
        e.append(Meq.Polar(amp, phase))
        pass
      pass
    
    # create EJones
    E  = ns.E(src.direction.name, residual) << Meq.Matrix22(e[0], 0, 0, e[1])
    
    if not residual and isrc<4:
      pxk_tools.Book_Mark(E,                 'E Jones')
      pxk_tools.Book_Mark(ns.K('S0',isrc+1), 'K Jones')
      pass
    
    # corrupt *source* with EJones (this uses MatrixMultiply)
    slist.sources[isrc] = Meow.CorruptComponent(
      ns, src, 'E'+str(residual), jones=E)
    pass

  return slist



def ZJones (ns, slist, array, observation):
  """ create ZJones (Ionospheric phase), given TECs (per source, per
  station). (image-plane effect).
  slist : source list to apply ZJones to
  """
  print "___ Applying Z Jones"  # Ionospheric phase

  tecs    = pxk_tecs.compute_tecs(ns, slist.sources, array, observation)
  labda   = pxk_tools.C/Meq.Freq()
  
  for isrc in range(len(slist.sources)):
    src   = slist.sources[isrc]

    # create Z Jones for ionospheric phase delay, with TECs (per source/stat.)
    for p in array.stations():
      phase = -25*tecs(src.name,p)*labda
      ns.Z(src.name,p) << Meq.Polar(1,phase);
      pass

    # corrupt *source* by Z term
    slist.sources[isrc] = Meow.CorruptComponent(
      ns,src,'Z',station_jones=ns.Z(src.name))
    pass
  
  # some bookmarks  (source S0, station i)
  for i in range(4): pxk_tools.Book_Mark(ns.Z('S0',i+1), 'Z Jones')
  return slist



def FJones_zenith (ns, slist, array):
  """ create FJones (Faraday Rotation) for each station.  (image-plane
  effect).
  NOTE : Make sure that there is flux in either Stoke Q or Stokes U,
  else F Jones will not do anything (since it interchanges flux
  between Q and U).
  slist : source list to apply FJones to
  """
  
  print "___ Applying F Jones"  # Faraday rotation
  from pxk_tools import Rot

  ENHANCE_RM  = 20.0  # set to 1 for no effect
  t0,t1,time = pxk_tools.scaled_time(ns)
  f0,f1,freq = pxk_tools.scaled_freq(ns)
  lambda2  = ns.lambda2 << Meq.Pow2(pxk_tools.C / (Meq.Freq()*(1+freq) )) # (!)
  pxk_tools.Book_Mark(lambda2, 'lambda^2')

  for isrc in range(len(slist.sources)):

    # get l,m positions
    src      = slist.sources[isrc]    
    l,m      = slist.LM     [isrc] 
    r        = math.sqrt(l*l + m*m)

    # get far rot per station, per source position
    for p in array.stations():    # some (l,m) var.
      RM      = ns.RM(src.direction.name, p) << \
                (1.0 + r) * Meq.Negate(Meq.Cos(time*math.pi))
      pxk_tools.Book_Mark(RM, 'RM')
      
      F       = ns.F (src.direction.name, p) << Rot(RM*ENHANCE_RM*lambda2)
      pass
    
    # and corrupt *source* by F term
    slist.sources[isrc] = Meow.CorruptComponent(
      ns,src,'F', station_jones=ns.F(src.direction.name))
    
    pass
  
  # some bookmarks  (source S0, station i)
  for i in range(4): pxk_tools.Book_Mark(ns.F('S0',i+1), 'F Jones')
  return slist



def FJones (ns, slist, array, observation):
  """ create FJones (Faraday Rotation), given TECs (per source,
  station).  (image-plane effect).  NOTE : Make sure that there is
  flux in either Stoke Q or Stokes U, else F Jones will not do
  anything (since it interchanges flux between Q and U).
  
  slist : source list to apply FJones to
  """
  print "___ Applying F Jones"  # Faraday rotation

  tecs    = pxk_tecs.compute_tecs (ns,slist.sources,array,observation);
  labda   = pxk_tools.C / Meq.Freq()
  
  for isrc in range(len(slist.sources)):
    src      = slist.sources[isrc]
    
    # get Far Rot per station, per source position
    for p in array.stations():
      phase = 2*math.pi * -25 * tecs(src.direction.name,p) * labda
      ns.F(src.direction.name,p) << pxk_tools.Rot(phase * labda * labda)
      pass

    # and corrupt *source* by F term
    slist.sources[isrc] = Meow.CorruptComponent(
      ns,src,'F', station_jones=ns.F(src.direction.name))
    pass
  
  # some bookmarks  (source S0, station i)
  for i in range(4): pxk_tools.Book_Mark(ns.F('S0',i+1), 'F Jones')
  return slist



def GJones (ns, patch, array, kind='noise'):
  """ create GJones (electronic gain) for each station (uv-plane
  effect)
  dphi   : max amp of phase variation
  damp   : max amp of gain  variation
  """
  print "___ Applying G Jones" # electronic gain
  
  for p in array.stations():

    if    kind=='periodic':
      f0   = ns.freq0 << 0
      damp = 1e-9
      dphi = math.pi*0.02
      ap   = random.uniform(-damp, damp)
      for feed in ['gx', 'gy']:
        a = random.uniform(-dphi,dphi)           # amp of phase variation
        b = 2*math.pi/random.uniform(3600,7200)  # period of variation 
        c = random.uniform(0,2*math.pi)          # initial phase of variation
        d = 1 + ap * (Meq.Freq()-f0)             # amp of freq. variation
        g = ns[feed](p) << Meq.Polar(d,a*Meq.Sin(Meq.Time()*b+c))
        pass
      pass

    elif kind=='noise':
      damp = 0.2 # sigma
      dphi = 10  # degrees
      for feed in ['gx', 'gy']:
        amp   = Meq.GaussNoise(1.0, damp)
        phase = Meq.RandomNoise(-dphi, dphi) * pxk_tools.DEG
        g = ns[feed](p) << Meq.Polar(amp,phase)
        pass
      pass

    G  = ns.G(p)  << Meq.Matrix22(ns.gx(p),0,0,ns.gy(p)) 
    if p<5: pxk_tools.Book_Mark(G,   'G Jones')
    pass

  # and corrupt patch by G term
  corrupt = Meow.CorruptComponent(ns,patch,'G',station_jones=ns.G) 
  return corrupt



def BJones (ns, patch, array):
  """ create BJones (bandpass) for each station (image-plane effect)
  """
  print "___ Applying B Jones"  # bandpass


  # create sawtooth and BSR
  f0,f1,freq = pxk_tools.scaled_freq(ns)
  sawtooth   = ns.sawtooth << 0.01 * (pxk_tools.sawtooth(
    ns,nparts=16, dir="freq", combine=True) - freq*0.5 - 0.25)
  smooth     = ns.smooth   << 0.1 * Meq.Sin(freq*2*math.pi)
  BSR        = ns.BSR      << (freq-0.5)  # 1.0 + sawtooth + smooth
  pxk_tools.Book_Mark(sawtooth, "Sawtooth")
  pxk_tools.Book_Mark(smooth,   "Smooth")
  pxk_tools.Book_Mark(BSR,      "BSR")
  
  for p in array.stations():
    
    # create gains
    B    = ns.B(p)  << Meq.Matrix22(BSR,0,0,BSR)
    if p<5: pxk_tools.Book_Mark(B,   'B Jones')
    pass

  # and corrupt patch by B term
  corrupt = Meow.CorruptComponent(ns,patch,'B',station_jones=ns.B) 
  return corrupt



def PJones (ns, patch, array, observation):
  """ create PJones (sky rotation) for each station to account for
  rotating sky in case of alt-az mounts. This is NOT necessary for
  WSRT or other equatorial mounts  (uv-plane effect).
  """
  print "___ Applying P Jones"  # sky rotation
  
  for p in array.stations():
    par_angle = ns.par_angle(p) << \
                Meq.ParAngle(radec = observation.radec0(),
                             xyz   = array.xyz()(p))
    if p==1: pxk_tools.Book_Mark(par_angle,   'par_angle')
    P  = ns.P (p) << pxk_tools.Rot(par_angle)
    if p<5: pxk_tools.Book_Mark(P,   'P Jones')
    pass

  # and corrupt patch by P term
  corrupt = Meow.CorruptComponent(ns,patch,'P',station_jones=ns.P) 
  return corrupt



def DJones (ns, patch, array, dphi=2, dtheta=1):
  """ create DJones (receptor cross-leakage) for each station.
  Receptor leakage is the extent to which each receptor is sensitive
  to radiation that is supposed to be picked up by the other
  one (uv-plane effect).
  phi   : deviation from nominal receptor position angle
  theta : deviation from nominal receptor ellipticities
  """

  print "___ Applying D Jones"  # receptor cross-leakage

  t0, t1, time = pxk_tools.scaled_time(ns)
  dphi        *= pxk_tools.DEG
  dtheta      *= pxk_tools.DEG

  for p in array.stations():
    rnd_phi   = random.uniform(dphi  *0.9, dphi  *1.1)
    rnd_theta = random.uniform(dtheta*0.9, dtheta*1.1)
    
    ns.phi_a  (p) << (time*2-1) * rnd_phi
    ns.theta_a(p) << rnd_theta
    ns.phi_b  (p) << Meq.Identity(ns.phi_a  (p))  # phi_b = phi_a
    ns.theta_b(p) << Meq.Negate  (ns.theta_a(p))  # th_b  = -th_a
    
    D  = ns.D (p) << (pxk_tools.Ell(ns.theta_a(p), ns.theta_b(p)) *
                      pxk_tools.Rot(ns.phi_a  (p), ns.phi_b  (p)))
    if p<5: pxk_tools.Book_Mark(D, 'D Jones')
    pass

  # and corrupt patch by D term
  corrupt = Meow.CorruptComponent(ns,patch,'D',station_jones=ns.D) 
  return corrupt



def MJones(ns, patch, array, parts=32, residual=0):
  """ Movie Jones. Makes a 'movie' by putting different timeslots in
  different channels. Works best when number of channels and number of
  time-slots are both integer multiple of 'parts'.
  """
  print "___ Applying M Jones", "[", str(residual), "]"

  # Create time-frequency band
  if ns.time_freq_band.initialized():
    band = ns.time_freq_band
  else:
    band  = pxk_tools.time_freq_band(ns, parts=parts, bookmarks=False)
    pass
  
  for p in array.stations():
    M  = ns.M(p) << Meq.Identity(band)
    if p<5: pxk_tools.Book_Mark(M,   'M Jones')
    pass

  corrupt = Meow.CorruptComponent(ns,patch,'M',station_jones=ns.M) 
  return corrupt



def addNoise(ns, array, predict, noise_level=0):
  """ add noise if needed """
  if noise_level != 0:
    Noise = Meq.GaussNoise(stddev=noise_level); # "reusable" node definition
    for p,q in array.ifrs():
      ns.noisy_predict(p,q) << predict(p,q) + \
                            Meq.Matrix22(Noise,Noise,Noise,Noise);
      pass
    return ns.noisy_predict;
  pass






def RJones(ns, patch, array, ERROR="3.1a"):
  # Errors In Maps
  """
  uv source model:
  
  - All beams shown for inclination of 80 degrees, which is nearly
  circular.
  
  - All examples are created from 12 hours of simulated synthesis
  data.
  
  - declination of the source = 80deg. so the synthesized beam is
  nearly perfectly circular. This makes that the cross-section is
  not a perfect bessel-function.
  
  - Included telescopes: all of WSRT, maxi-short:
  144,144,...,36,54,1242,72
  
  - Field measures: 512*512 pixels (cell=1arcsec => 8x8 arcmin FOV)
  """
  
  # Symmetries of errors 
  """
  - G(l,m) = difference between error-corrupted beams and the
  ideal synthesized beam
  
  - Gain errors produce error patterns symmetric w.r.t. the beam
  center: G(l,m) = G(-l,-m)
  
  - Small phase errors result in anti-symmetrical error patterns,
  i.e.: G(l,m) = -G(-l,-m). For these errors: e^{i phi} = 1 + {i
  phi}. If the phase error phi is too big for this approx. to be
  valid, then a symmetrical error is superimposed upon the
  anti-symmetrical one.
  
  - Errors that are (anti-) symmetric in hour angle (or time
  w.r.t. meridian transit) give rise to a similar beam symmetry
  relative to the horizontal axis, i.e.: G(l,m) = +/- G(l,-m)
  """

  print "___ Applying R Jones", "[", ERROR, "]"

  for p in array.stations():
    
    # Set defaults
    rx = gamx = gamy = ry = 0
    INCLUDE = 0
    
    
    if   ERROR=="3.1a": 
      """ _____________________________________________________
      |______ Contribution of single ifr ______________________|
      
      The contribution from single interferometer (288 meter
      spacing) to the WSRT beam is a circularly symmetric beam
      (for \delta is 90 deg) and equals a constant gain error on
      this particular baseline. An extreme case if that of an
      interferometer completely absent (shown). In the case of a
      perfectly symmetric beam, the cross-section is a
      bessel-function, G_L(r,phi) ~ J_0(2piLr) (Where polar beam
      coordinates are used instead of the conventional l,m).
      """
      if p in [1,3]:   # Just baseline 02 (288 m)
        INCLUDE = 1
        amp     = 1     # constant gain offset
        phase   = 0
        pass
      pass
    
    
    elif ERROR=="3.1b": 
      """______________________________________________________
      |______ Varying phase error _____________________________|
      
      Contribution from single interferometer (288 meter
      spacing) to the WSRT beam for a varying phase error on
      this particular baseline is a circularly anti-symmetric
      beam. Error = 1rad * (sin(HA)+cos(HA))      
      """
      # in pxk_simul: set residuals = True   
      
      if   p == 1:     # Just baseline 02 (288 m)
        INCLUDE  = 1
        t0,t1,ts = pxk_tools.scaled_time(ns)
        HA       = ns["HA"] << math.pi*0.5 * (ts*2 - 1)
        pxk_tools.Book_Mark(HA, "HA")
        amp      = 1
        phase    = Meq.Sin(HA) + Meq.Cos(HA)
        pass
      
      elif p == 3:     # include antenna 2
        INCLUDE  = 1
        amp      = 1
        phase    = 0
        pass
      pass
    
    
    elif (ERROR[:3]=="3.2" or
          ERROR[:3]=="3.4"   ):
      """______________________________________________________
      |______ Cst phase offset / Var gain Errors ______________|
      
      3.2: Contribution from single interferometer (288 meter
      spacing) to the WSRT beam for a constant phase offset
      results in discontinuities at (r,phi) = (baselinelength L,
      +/- pi/2), since this is where the observed ifr track and
      its unobserved hermitian meet. Similar effects occur for
      gain errors whenever a linear drift component is present.
      
      3.4: A-B rings: Errors in a single movable telescope
      affects 10 interferometers spaced at 144 meters
      simultaneously. These AB-rings are specifically for
      0A=AB=72 meters, so I can't reproduce them exactly here
      and also they are very WSRT specific.
      """

      
      if ((ERROR[:3]=="3.2" and p == 1) or # Just baseline 02 (288 m)
          (ERROR[:3]=="3.4" and p == 11)): # all bl, error in A
        
        INCLUDE = 1
        # set HA from [-6hr, 6hr]
        t0, t1, ts = pxk_tools.scaled_time(ns)
        HA         = ns["HA"] << math.pi*0.5 * (ts*2 - 1)
        #pxk_tools.Book_Mark(HA, "HA")
        
        CST     = math.pi*0.5
        amp     = 1
        phase   = 0
        
        if   len(ERROR)==3: pass
        elif ERROR[3:]=="a": phase = CST;          pass
        elif ERROR[3:]=="b": amp   = Meq.Sin(HA);  pass
        elif ERROR[3:]=="c": amp   = Meq.Cos(HA);  pass
        elif ERROR[3:]=="d": amp   = Meq.Cos(HA) - Meq.Sin(HA); pass
        elif ERROR[3:]=="e": phase = Meq.Sin(HA);  pass
        pass
      
      elif ((ERROR[:3]=="3.2" and p == 3 ) or
            (ERROR[:3]=="3.4" )):
        INCLUDE = 1
        amp     = 1
        phase   = 0
        pass
      pass
    
    
    elif ERROR[:3]=="3.3":
      """______________________________________________________
      |______ Errors in a fixed telescope _____________________|
      
      Same contribution from a single antenna in 2
      interferometers with baselines L1 and L2 (L1 = 288m, L2 =
      432m spacing) to the WSRT beam gives rise to beats at a
      quasi-frequency (L1-L2)/2.
      """
      # Just baselines 02 and 03 (288 m and )
      if   p == 1:
        INCLUDE = 1
        CST     = math.pi*0.5
        amp     = 1
        if   ERROR[3:]=="a": phase = 0;   pass # cst gain offset
        elif ERROR[3:]=="c": phase = CST; pass # cst phase offset
        pass
      
      elif (p == 3 or p == 4 ):             # include ants 2, 3
        INCLUDE = 1
        amp     = 1
        phase   = 0
        pass
      
      pass
    
    
    elif ERROR=="3.5a":
      """______________________________________________________
      |______ Baseline Pole ___________________________________|
      
      The angle between the 'average' bl of SRT (w-coord ) and
      equatorial plane is known as the 'baseline pole'. It varies
      slowly in time (over 30000 years or so, but not during 1
      measurement) and must therefore be calibrated for each
      observation period. Errors in this calibration result in
      
      --- phase offsets in all interferometers ---
      
      prop to L: E_L ~ L \delta_p sin(\delta). The resulting
      image pattern consists of an EW positive-negative tail
      pair for the WSRT, and is very similar to the error
      pattern from a constant phase offset in a movable
      telescope, but has no A-B rings (since the error affects
      all ifrs rather than only half of them).
      """

      pxk_tools.set_uvw_node(ns, p)
      
      # Include all baselines
      INCLUDE = 1
      amp     = 1
      U,V,W   = ns.u(p), ns.v(p), ns.w(p)
      L       = ns.L(p) << Meq.Sqrt(U*U + V*V + W*W)
      if 0:
        pxk_tools.Book_Mark(U, "u-coords")  # u = b*cos(HA)
        pxk_tools.Book_Mark(V, "v-coords")  # v = b*sin(HA)*sin(DEC)
        pxk_tools.Book_Mark(W, "w-coords")  # w = 0 (for small field, etc)
        pass
      delta_p = 5                           # baseline pole error [arcmin]
      phase   = L * (delta_p*pxk_tools.ARCMIN) * Meq.Sin(ns.dec)
      pass

    
    elif ERROR=="3.5b":
      """______________________________________________________
      |______ Missing HA ______________________________________|
      """
      INCLUDE = 1
      
      if p==1:
        t      = 20
        tband1 = pxk_tools.time_band(ns, t_from=0,     t_min=t, kind='box')
        tband2 = pxk_tools.time_band(ns, t_from_end=t, t_min=t, kind='box')
        ns.tband1 << Meq.Identity(tband1)
        ns.tband2 << Meq.Identity(tband2)
        pass
      amp     = 1.0 - (ns.tband1+ns.tband2)
      phase   = 0

      # Add some noise
      Noise   = False
      if Noise:
        lim     = 0.5
        Noise   = ns.the_noise << Meq.RandomNoise(-lim, lim)
        pxk_tools.Book_Mark(Noise, "The Noise")
        amp     = amp * (1.0 + Noise)
        phase   = Noise*math.pi
        pass
      pass


    elif ERROR=="3.7": 
      """______________________________________________________
      |______ Composed Parm ___________________________________|
      """
      
      # make a parm tiled in time
      coeff    = pxk_tools.random_coeff(12, min=-math.pi/2, max=math.pi/2)
      polcparm = pxk_tools.polc_parm(ns, coeff)

      INCLUDE  = 1
      amp      = 1
      phase    = Meq.Identity(polcparm)
      pass
      

    else:
      raise ValueError, \
            "ERROR not set correctly" + "[Errors_In_Maps()]"
    
    
    # create jones matrices with errors #########################
    if not INCLUDE:
      amp = 0
      phi = 0
      pass

    AMP     = ns.amp(s=str(p)) << amp
    PHASE   = ns.phi(s=str(p)) << phase
    if 0:
      pxk_tools.Book_Mark(AMP,   "AMP")
      pxk_tools.Book_Mark(PHASE, "PHASE")
      pass
    
    # change rx, ry
    rx  = ns.rx(p) << Meq.Polar(AMP, PHASE)
    ry  = ns.ry(p) << Meq.Polar(AMP, PHASE)

    R   = ns.R(p) << Meq.Matrix22(rx, 0, 0, ry)
    if p<5: pxk_tools.Book_Mark(R,   'R Jones')
    pass

  # and corrupt patch by R term
  corrupt = Meow.CorruptComponent(ns,patch,'R',station_jones=ns.R)
  return corrupt




  
  
