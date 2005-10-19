# TDL_Dipole.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Dipole object represents an dipole antenna element 
#
# History:
#    - 18 oct 2005: creation
#
# Full description:
#


#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *
from Timba.Meq import meq                     # required for _create_beam()
# from copy import deepcopy
from numarray import *
import math                         # for create_dipole_beam()

from Timba.Trees import TDL_common
from Timba.Trees import TDL_Antenna
from Timba.Trees import TDL_Leaf
# from Timba.Trees import TDL_radio_conventions



#**************************************************************************************
# Some useful helper functions:
#**************************************************************************************




#**************************************************************************************
# Class Dipole: (example of single-element Antenna)
#**************************************************************************************

class Dipole (TDL_Antenna.Antenna):
    """A Dipole object represents an (array of) antenna element(s)"""
    
    def __init__(self, **pp):
        
        pp.setdefault('length', 1.0)          # dipole length
        pp.setdefault('height', 0.5)          # dipole height above groundplane
        pp.setdefault('polarisation', 'X')
        pp.setdefault('plot_color', 'green')
        pp.setdefault('plot_style', 'square')

        key = 'polarisation'
        pols = ['X','Y','Z','R','L']
        if not isinstance(pp[key], str): pp[key] = pols[0]
        if not pols.__contains__(pp[key]): pp[key] = pols[0]

        TDL_Antenna.Antenna.__init__(self, type='Dipole', **pp)

        self.__length = pp['length']
        self.__height = pp['height']
        self.Dipole_calc_derived()

    def Dipole_calc_derived(self):
        TDL_Antenna.Antenna.calc_derived(self)
        return True

    def length(self): return self.__length
    def height(self): return self.__height

    def oneliner(self):
        """Return a one-line summary of the Dipole"""
        s = TDL_Antenna.Antenna.oneliner(self)
        s = s+' pol='+str(self.polarisation())
        s = s+' length='+str(self.length())
        s = s+' height='+str(self.height())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Dipole"""
        ss = TDL_Antenna.Antenna.display(self, txt=txt, end=False)
        indent1 = TDL_Antenna.Antenna.display_indent1(self)
        indent2 = TDL_Antenna.Antenna.display_indent2(self)
        if end: TDL_Antenna.Antenna.display_end(self, ss)
        return ss



    # Re-implementation of TDL_Antenna.Antenna method:
    def subtree_sensit(self, ns=None, **pp):
        """Return a subtree for Dipole sensitivity calculation"""

        pp.setdefault('bandwidth', 1e4)       # bandwidth in Hz
        pp.setdefault('interval', 10)         # integration time (sec)
        pp.setdefault('Trec', 75)             # receiver Temp (K)
        pp.setdefault('groundplane', True)    # conducting/reflecting

        # NB: The sensitivity does NOT depend on dipole length,
        #     as long as it is short w.r.t. the wavelength
        # NB: What about the height above the groundplane?

        if ns and not TDL_Antenna.Antenna.subtree_sensit(self):
            uniqual = _counter ('subtree_sensit()', increment=True)
            omega = 4.0*3.14                  # isotropic radiator
            omega = 4.0                       # use for LOFAR, with separation lambda/2...?
            if pp['groundplane']: omega = 3.0 # above reflecting groundplane
            omega = ns['omega_sterad_'+self.tlabel()](uniqual) << omega
            wvl = self.subtree_wvl(ns)
            k_Boltzmann = 1.4*1e-23           # J/Hz.K
            k_Jy = k_Boltzmann/1e-26          # Jy/Hz.K
            k2_Jy = 2*k_Jy                    # 
            Aeff = ns['Aeff_m2_'+self.tlabel()](uniqual) << Meq.Sqr(wvl)/omega
            Tsky = self.subtree_Tsky(ns)
            Tsys = ns['Tsys_K_'+self.tlabel()](uniqual) << Tsky + pp['Trec']
            if True:
                name = 'bw_Hz'+self.tlabel()
                bw = ns[name](uniqual) << Meq.Parm(pp['bandwidth'])
                name = 'dt_sec_'+self.tlabel()
                dt = ns[name](uniqual) << Meq.Parm(pp['interval'])
                name = 'sqrt(Bt)_'+self.tlabel()
                # NB: The factor 2.0 comes from full polarisation.....?
                SqrtBt = ns << Meq.Sqrt((ns << Meq.Multiply(2.0,bw,dt)))
            name = 'sensit_Jy_'+self.tlabel()
            Srcp = ns[name](uniqual) << k2_Jy * Tsys / (Aeff * SqrtBt)
            TDL_Antenna.Antenna.subtree_sensit(self, new=Srcp)
        return TDL_Antenna.Antenna.subtree_sensit(self)



    # Re-implementation of TDL_Antenna.Antenna method:
    def subtree_beam(self, ns=None, **pp):
        """Return a subtree for Dipole beam calculation"""
        pp.setdefault('height', 0.25)     # wavelengths above groundplane
        if ns and not TDL_Antenna.Antenna.subtree_beam(self):
            pol = self.polarisation()
            node = _create_dipole_beam(ns, pol=pol, height=pp['height'])
            TDL_Antenna.Antenna.subtree_beam(self, new=node)
        return TDL_Antenna.Antenna.subtree_beam(self)


#---------------------------------------------------------------------------
def _create_dipole_beam(ns, pol='X', height=0.25):
  """ We create two horizontal dipoles, perpendicular to one another
      and multiply their Voltage (not Power) beam shapes. The voltage
      beam is taken to be the positive square root of the power beam.
  """;

  # dipole height from ground plane in wavelengths
  # make dipole height above ground=lambda/4 to get peak at top
  

  # creation of a compiled funklet - using MXM code
  # polynomials in t,f

  par=['p0+p1*x0+p2*x1+p3*x0*x1','p4+p5*x0+p6*x1+p7*x0*x1',\
       'p8+p9*x0+p10*x1+p11*x0*x1','p12+p13*x0+p14*x1+p15*x0*x1']

  # polynomial coefficients
  #coeff=[[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]]
  # choose this to see some time variation
  # the third polynomial should model variation of dipole height
  # with freqency                        \/ -- this models height

  coeff=[[1,0.1,0,0],[1,0.2,0,0],[1,0.10,0.5,0],[1,0.30,0,0]]


  # value of pi (string)
  pi=str(math.pi)

  print par
  print coeff

  uniqual = _counter ('_create_dipole_beam()', increment=True)
  name = 'beam_Dipole_'+pol
  if pol=='Y':
      # create voltage beam for Y dipole:
      root = ns[name](uniqual) << _create_dipole_beam_h(par,coeff,height,'x2-'+pi+'/2')
  else:
      # create voltage beam for X dipole:
      root = ns[name](uniqual) << _create_dipole_beam_h(par,coeff, height)

  # create product beam as root
  # root = ns.z << Meq.Multiply(ns.x,ns.y)

  # ns.Resolve()
  return root


#------------------------------------------------------------------------------------------------
def _create_dipole_beam_h(tfpoly=['1','1','1','1'],coeff=[[1],[1],[1],[1]],h=0.25,x='x2',y='x3'):
  """ Create Horizontal Dipole beam:
      The theoretical (power) beam shape is:
      z=(1-sin(x)^2 sin(y)^2)*sin(2*pi*h*cos(y)))^2;
      where x:azimuth angle (phi)
            y:elevation angle (theta) (both in radians)
            h: dipole height from ground
      we create a voltage beam, using square root of power as the r.m.s.
      voltage, and add polynomials for time,freq as given by {TF}
      z=(1-sin({TF0}x)^2 sin({TF1}y)^2)*sin(2*pi*h*{TF2}cos({TF3}y))^2
      so we need 4 polynomials, which must be given as tfpoly array.
      The coefficients for these polynomials should be given by coeff array.
      x,y should be given as polynomials of x2 and x3 respectively.
  """
  if len(tfpoly)<4:
   print "Invalid No. of Polynomials, should be 4"
   return None

  h_str=str(h)
  pi=str(math.pi)
  # voltage beam, so do not take ^2
  beamshape='sqrt((1-(sin(('+tfpoly[0]+')*('+x+'))*sin(('+tfpoly[1]+')*('+y+')))^2)*(sin(2*'+pi+'*'+h_str+'*('+tfpoly[2]+')*cos(('+tfpoly[3]+')*('+y+'))))^2)'
  polc = meq.polc(coeff=coeff,subclass=meq._funklet_type)
  print beamshape
  print coeff
  polc.function = beamshape;

  root = Meq.Parm(polc,node_groups='Parm')

  return root

      


#------------------------------------------------------------------------------------------------
def _create_dipole_beam_v(tfpoly=['1','1','1','1'],coeff=[[1],[1],[1],[1]],h=0.25,x='x2',y='x3'):
  """ Create Vertical Dipole beam:
      The theoretical (power) beam shape is:
      z=(sin(y)*cos(2*pi*h*cos(y)))^2;
      where x:azimuth angle
            y:elevation angle (both radians)
            h: dipole height from ground
      we create a voltage beam, using square root of power as the r.m.s.
      voltage, and add polynomials for time,freq as given by {TF}
      z=({TF0}*sin({TF1}y)*cos(2*pi*h*{TF2}cos({TF3}y)))^2
      so we need 4 polynomials, which must be given as tfpoly array.
      The coefficients for these polynomials should be given by coeff array.
      x,y should be given as polynomials of x2 and x3 respectively.
  """
  if len(tfpoly)<4:
   print "Invalid No. of Polynomials, should be 4"
   return None

  h_str=str(h)
  pi=str(math.pi)
  # voltage beam, so do not take ^2
  #beamshape='abs(cos('+pi+'/2*('+tfpoly[0]+')*cos(('+tfpoly[1]+')*('+x+')))/sin(('+tfpoly[2]+')*('+x+'))*sin(2*'+pi+'*'+h_str+'*('+tfpoly[3]+')*sin(('+tfpoly[4]+')*('+y+'))))'
  beamshape='abs(('+tfpoly[0]+')*sin(('+tfpoly[1]+')*('+y+'))*cos(2.0*'+pi+'*'+h_str+'*('+tfpoly[2]+')*cos(('+tfpoly[3]+')*('+y+'))))'
  polc = meq.polc(coeff=coeff,subclass=meq._funklet_type)
  print beamshape
  print coeff
  polc.function = beamshape;

  root = Meq.Parm(polc,node_groups='Parm')

  return root






#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] -= increment
    if trace: print '** Dipole: _counters(',key,') =',_counters[key]
    return _counters[key]






#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Dipole.py:\n'
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    
    if 1:
        obj = Dipole(label='initial')

    if 0:
        dip1 = Dipole(label='dip1', polarisation='X')
        dip2 = Dipole(label='dip2', polarisation='Y')
        obj = TDL_Antenna.Feed(dip1, dip2, label='initial')

    if 0:
        rcp1 = Dipole(label='rcp1', polarisation='R')
        rcp2 = Dipole(label='rcp2', polarisation='L')
        obj = TDL_Antenna.Feed(rcp1, rcp2, label='initial')

    if 0:
        dip1 = Dipole(label='dip1', polarisation='X')
        dip2 = Dipole(label='dip2', polarisation='Y')
        dip3 = Dipole(label='dip3', polarisation='Z')
        obj = TDL_Antenna.TriDipole(dip1, dip2, dip3, label='initial')


    if 1:
        print dir(obj)
        obj.display('initial')
        if 0:
            dcoll = obj.dcoll_xy(ns)
            MG_JEN_exec.display_subtree(dcoll, 'dcoll_xy()', full=True, recurse=5)
        if 1:
            sensit = obj.subtree_sensit(ns)
            MG_JEN_exec.display_subtree(sensit, 'subtree_sensit()', full=True, recurse=5)
        if 0:
            Tsky = obj.subtree_Tsky(ns)
            MG_JEN_exec.display_subtree(Tsky, 'subtree_Tsky()', full=True, recurse=5)
        obj.display('final')

    if 0:
        # Display the final result:
        # MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        obj.display('final result')
    print '\n*******************\n** End of local test of: TDL_Dipole.py:\n'



#============================================================================================









 

