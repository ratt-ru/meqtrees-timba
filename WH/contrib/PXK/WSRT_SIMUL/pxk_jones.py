# History:
# - 2006.11.07: creation.
# - 2006.11.10: adjusted DJones: time dependency / randomness

# standard preamble
from   Timba.TDL import *
from   Timba.Meq import meq
import math
import Meow
import random
import pxk_tools



def EJones (ns, patch, source_list, residual=0):
  """ create EJones (beam gain Jones) for each source. Beam is
  elongated in X-feed direction and squeezed in Y-feed direction.
  (image-plane effect)
  patch       : the patch to add the corrupted sources
  source_list : provided to apply EJones to particular set of sources
  """
  print "___ Applying E Jones", "[", str(residual), "]"
  
  alpha  = 0.0      # ellipticity of feed-sensitivities

  for isrc in range(len(source_list.sources)):

    # get l,m positions
    src     = source_list.sources[isrc]    
    l,m     = source_list.LM     [isrc] 
    
    # create wsrt beam (diff for X/Y-feed /freq); pow = E^2 ~ cos^6
    labda   = 3e8/Meq.Freq()
    r_X     = math.sqrt(l*l*(1+alpha)**2 + m*m*(1-alpha)**2)
    r_Y     = math.sqrt(l*l*(1-alpha)**2 + m*m*(1+alpha)**2)
    wsrt_X  = Meq.Pow(Meq.Cos((math.pi/2) * r_X*25/labda),3)
    wsrt_Y  = Meq.Pow(Meq.Cos((math.pi/2) * r_Y*25/labda),3)

    E       = ns.E(src.direction.name, residual) << \
              Meq.Matrix22(wsrt_X,0,0,wsrt_Y)
    name = "E Jones" + str(residual)
    if not residual: pxk_tools.Book_Mark(E, "E Jones")

    # corrupt *source* with EJones (this uses MatrixMultiply)
    corrupt = Meow.CorruptComponent(
      ns, src, 'E'+str(residual), jones=E)

    patch.add(corrupt)  # add to patch
    pass

  # some bookmarks
  pxk_tools.Book_Mark(ns.K('S0',1), 'K Jones') # different sources, stations
  pxk_tools.Book_Mark(ns.K('S0',2), 'K Jones')
  pxk_tools.Book_Mark(ns.K('S0',3), 'K Jones')
  pxk_tools.Book_Mark(ns.K('S0',4), 'K Jones')

  return patch



def GJones (ns, patch, array, damp=1e-9, dphi=math.pi):
  """ create GJones (electronic gain) for each station (uv-plane
  effect)
  dphi   : max amp of phase variation
  damp   : max amp of gain  variation
  """

  print "___ Applying G Jones"
  
  types     = ['', 'random_sine', 'sine_phase', 'sine_amp']
  gain_type = types[0]

  # create GJones: electronic gain
  for p in array.stations():

    if    gain_type is 'random_sine':
      f0 = ns.freq0 << 0
      ap = random.uniform(0.0, damp)
      for feed in ['gx', 'gy']:
        a = random.uniform(0,dphi)               # amp of phase variation
        b = 2*math.pi/random.uniform(3600,7200)  # period of variation 
        c = random.uniform(0,2*math.pi)          # initial phase of variation
        d = 1 + ap * (Meq.Freq()-f0)             # amp of freq. variation
        g = ns[feed](p) << Meq.Polar(d,a*Meq.Sin(Meq.Time()*b+c))
        pass
      pass
    
    elif gain_type is 'sine_phase':
      for feed in ['gx', 'gy']:
        period = 2*math.pi/3600
        ns[feed](p) << Meq.Polar(1, Meq.Sin(Meq.Time()*period))
        pass
      pass

    elif gain_type is 'sine_amp':
      t0, t1, time = pxk_tools.scaled_time(ns)
      for feed in ['gx', 'gy']:
        ns[feed](p) << Meq.Sin(math.pi*(2*time-1))
        pass
      pass

    else: # default
      for feed in ['gx', 'gy']:
        ns[feed](p) << 1
        pass
      pass

    G  = ns.G(p)  << Meq.Matrix22(ns.gx(p),0,0,ns.gy(p)) 
    if p<5: pxk_tools.Book_Mark(G,   'G Jones')
    pass

  # and corrupt patch by G term
  corrupt = Meow.CorruptComponent(ns,patch,'G',station_jones=ns.G) 
  return corrupt



def PJones (ns, patch, array, observation):
  """ create PJones (sky rotation) for each station to account for
  rotating sky in case of alt-az mounts. This is NOT necessary for
  WSRT or other equatorial mounts  (uv-plane effect).
  """
  print "___ Applying P Jones"

  # create PJones: rotation matrix  
  for p in array.stations():
    par_angle = ns.par_angle(p) << \
                Meq.ParAngle(radec = observation.radec0(),
                             xyz   = array.xyz()(p))
    P  = ns.P (p) << pxk_tools.Rot(par_angle)
    if p<5: pxk_tools.Book_Mark(P,   'P Jones')
    pass

  # and corrupt patch by P term
  corrupt = Meow.CorruptComponent(ns,patch,'P',station_jones=ns.P) 
  return corrupt



def DJones (ns, patch, array,
            dphi   = 0.1,
            dtheta = 0.01):
  """ create DJones (receptor cross-leakage) for each station.
  Receptor leakage is the extent to which each receptor is sensitive
  to radiation that is supposed to be picked up by the other
  one.(uv-plane effect).
  phi   : deviation from nominal receptor position angle
  theta : deviation from nominal receptor ellipticities
  """

  print "___ Applying D Jones"

  t0, t1, time = pxk_tools.scaled_time(ns)

  # create DJones: receptor cross-leakage
  for p in array.stations():
    rnd_phi   = random.uniform(0, dphi*pxk_tools.DEG)
    rnd_theta = random.uniform(0, dtheta*pxk_tools.DEG)
    #print pxk_tools.format_array([rnd_phi, rnd_theta], "%7.5f")
    
    ns.phi_a  (p) << (time*2-1) * rnd_phi
    ns.theta_a(p) << rnd_theta
    ns.phi_b  (p) << Meq.Identity(ns.phi_a  (p))  # phi_b = phi_a
    ns.theta_b(p) << Meq.Negate  (ns.theta_a(p))  # th_b  = -th_a
    
    D  = ns.D (p) << (pxk_tools.Ell(ns.theta_a(p), ns.theta_b(p)) *
                      pxk_tools.Rot(ns.phi_a  (p), ns.phi_b  (p)))
    if p<5:
      pxk_tools.Book_Mark(D,             'D Jones')
      pxk_tools.Book_Mark(ns.phi_a  (p),   'phi_a')
      pxk_tools.Book_Mark(ns.theta_a(p), 'theta_a')
      pass
    pass

  # and corrupt patch by D term
  corrupt = Meow.CorruptComponent(ns,patch,'D',station_jones=ns.D) 
  return corrupt



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
  
  - Field measures: 512*512 pixels ( _ x _ degrees)
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

  def scaledParm(polc=[0.]):
    """ returns a parm scaled to time-domain [0,1] == 0hr-12hr """
    #HA      = ns["HA"] << scaledParm([-math.pi/2, math.pi])
    starttime  = 4647002189.5  # ns.time0
    startfreq  = 1401000000.0  # ns.freq0
    time_extent= 43008.0       # ns.time1 - ns.time0
    freq_extent= 62e6          # ns.freq1 - ns.freq0
    funk       = meq.polc(polc)
    funk.offset= [float(starttime),   float(startfreq)  ]
    funk.scale = [float(time_extent), float(freq_extent)]
    return Meq.Parm(funk)

  def tile_time(ns, nparts=12):
    """ returns a composed parm by tiling the time
    nparts : num timeslots that the full timerange will be divided in
    """
    t0,t1,ts = pxk_tools.scaled_time(ns)
    parm     = []
    for part in range(nparts):
      t_start  = t0 + part/float(nparts)*(t1-t0)
      time     = (Meq.Time()-t_start)/(t1-t0)
      x        = Meq.Max(Meq.Ceil(1.0/nparts - time) *time*nparts,0)
      y        = Meq.Ceil(x)   # block function
      parm.append(x)
      pass
    return parm
  

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
        # (!) The following line doesn't work anymore!
        # HA      = scaledParm([-math.pi/2, math.pi], ns, p)
        # So use Meq.Time() function instead
        t0, t1, ts = pxk_tools.scaled_time(ns)
        HA         = ns["HA"](s=str(p)) << math.pi*0.5 * (ts*2 - 1)
        #pxk_tools.Book_Mark(HA, "HA"+str(p))
        
        CST     = math.pi*0.5 #scaledParm([math.pi*0.5])
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
        CST     = math.pi*0.5 #scaledParm([math.pi*0.5])
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


    elif ERROR=="3.6": 
      """______________________________________________________
      |______ Composed Parm ___________________________________|
      """
      
      if   p == 1:     # Just baseline 02 (288 m)
        INCLUDE  = 1
        nparts   = 3
        compparm = tile_time(ns, nparts=nparts)
        #LIST     = []
        #for part in range(nparts):
        #  x   = compparm[part]
        #  LIST.append(x)
        #  pass
        #gain     = ns["composed_parm"] << Meq.Add(*LIST)
        gain     = ns["composed_parm"] << Meq.Add(*compparm)

        pxk_tools.Book_Mark(gain, "composed_parm")
        amp      = Meq.Identity(gain)
        phase    = 0
        pass
      
      elif p == 3:     # include antenna 2
        INCLUDE  = 1
        amp      = 1
        phase    = 0
        pass
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
    #pxk_tools.Book_Mark(AMP,   "AMP")
    #pxk_tools.Book_Mark(PHASE, "PHASE")
    
    # change rx, ry
    rx  = ns.rx(p) << Meq.Polar(AMP, PHASE)
    ry  = ns.ry(p) << Meq.Polar(AMP, PHASE)

    R   = ns.R(p) << Meq.Matrix22(rx, 0, 0, ry)
    if p<5: pxk_tools.Book_Mark(R,   'R Jones')
    pass

  # and corrupt patch by R term
  corrupt = Meow.CorruptComponent(ns,patch,'R',station_jones=ns.R)
  return corrupt
  







def QJones(ns, patch, array):
  """ TEST JONES """ ### TEST JONES ###
  import pxk_sourcelist

  source_list = pxk_sourcelist.SourceList(ns, LM=[(1e-100,0)])
  patch.add(*source_list.sources)

  # Missing HA
  t0,t1,ts = pxk_tools.scaled_time(ns)
  gain     = Meq.Ceil(ts - 1.0/12)

  for p in array.stations():
    Q        = ns.Q(p) << Meq.Matrix22(gain, 0, 0, gain) 
    if p<5: pxk_tools.Book_Mark(Q,   'Q Jones')
    pass


  corrupt = Meow.CorruptComponent(ns,patch,'Q',station_jones=ns.Q)
  return corrupt
  
