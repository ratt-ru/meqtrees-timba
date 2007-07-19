# TDL_Dipole.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Dipole object represents an dipole antenna element 
#
# History:
#    - 18 oct 2005: creation
#    - 03 dec 2005: TDL_display.py
#
# Full description:
#


#=================================================================================
# Preamble:
#=================================================================================

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
from Timba.Meq import meq                     # required for _create_beam()
# from copy import deepcopy
from numarray import *
from math import *

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
    """A Dipole object represents a single linear dipole antenna"""
    
    def __init__(self, **pp):
        
        pp.setdefault('type', 'Dipole')       # object type
        pp.setdefault('length', 1.0)          # dipole length
        pp.setdefault('groundplane', True)    # if True, has a groundplane
        pp.setdefault('height', 0.5)          # height above groundplane
        pp.setdefault('plot_color', 'green')
        pp.setdefault('plot_style', 'square')

        TDL_Antenna.Antenna.__init__(self, **pp)

        self.plot_color(pp['plot_color'])
        self.plot_style(pp['plot_style'])
        self.__length = pp['length']
        self.__groundplane = pp['groundplane']
        self.__height = pp['height']
        self.Dipole_calc_derived()

    def Dipole_calc_derived(self):
        TDL_Antenna.Antenna.calc_derived(self)
        return True

    def length(self): return self.__length
    def height(self): return self.__height
    def groundplane(self): return self.__groundplane

    def oneliner(self):
        """Return a one-line summary of the Dipole"""
        s = TDL_Antenna.Antenna.oneliner(self)
        s = s+'      length='+str(self.length())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Dipole"""
        indent1 = TDL_Antenna.Antenna.display_indent1(self)
        indent2 = TDL_Antenna.Antenna.display_indent2(self)
        ss = TDL_Antenna.Antenna.display(self, txt=txt, end=False)
        ss.append(indent1+' - groundplane:   '+str(self.groundplane()))
        if self.groundplane():
            ss.append(indent1+' - height:        '+str(self.height())+' (m)')
        if end: TDL_Antenna.Antenna.display_end(self, ss)
        return ss






#============================================================================

class HorizontalDipole (Dipole):
    """A Dipole object represents a horizontal Dipole"""
    
    def __init__(self, **pp):
        
        pp.setdefault('azimuth', 0.0)         # orientation 
        pp.setdefault('plot_color', 'green')
        pp.setdefault('plot_style', 'square')

        Dipole.__init__(self, type='HorizontalDipole', **pp)

        self.plot_color(pp['plot_color'])
        self.plot_style(pp['plot_style'])
        self.__azimuth = pp['azimuth']
        self.HorizontalDipole_calc_derived()

    def HorizontalDipole_calc_derived(self):
        # TDL_Antenna.Antenna.calc_derived(self)
        Dipole.calc_derived(self)
        return True

    def azimuth(self, new=None, add=None):
        """Get/set the azimuth angle of the HorizontalDipole"""
        if add: new = self.__azimuth + add
        if new: self.__azimuth = new
        # Not yet implemented:
        if self.__azimuth==0.0:
            self.plot_style()       
        else:
            self.plot_style()
        return self.__azimuth

    def oneliner(self):
        """Return a one-line summary of the HorizontalDipole"""
        s = Dipole.oneliner(self)
        s = s+' azimuth='+str(self.azimuth())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the HorizontalDipole"""
        ss = Dipole.display(self, txt=txt, end=False)
        indent1 = TDL_Antenna.Antenna.display_indent1(self)
        indent2 = TDL_Antenna.Antenna.display_indent2(self)
        ss.append(indent1+' - azimuth:       '+str(self.azimuth())+' (rad)')
        if end: TDL_Antenna.Antenna.display_end(self, ss)
        return ss

    # Re-implementation of Antenna class method:
    def rotate_xy(self, total=None, add=None, recurse=0):
        """Rotate the Dipole by the given angle (rad) azimuth"""
        cs = Antenna.rotate_xy(self, total=total, add=add)
        if not cs: return True                # no rotation needed
        pos0 = self.pos0()                    # Array reference pos
        if total:                             # total rotation angle specified
            add = total - self.__azimuth      # -> incremental rotation angle
        self.__azimuth += add                 # total azimuth rotation angle
        self.HorizontalDipole_calc_derived()
        return True


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
            wvl = TDL_Leaf.MeqWavelength(ns)
            k2_Jy = TDL_Leaf.const_2k_Jy(ns)  # 2*k_Boltzmann/1e-26
            Aeff = ns['Aeff_m2_'+self.tlabel()](uniqual) << Meq.Sqr(wvl)/omega
            Tsky = self.subtree_Tsky(ns)
            Tsys = ns['Tsys_K_'+self.tlabel()](uniqual) << Tsky + pp['Trec']
            if True:
                name = 'bw_Hz_'+self.tlabel()
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
    def subtree_voltage_beam(self, ns=None, **pp):
        """Return a subtree for Dipole beam calculation"""
        pp.setdefault('height', 0.25)                # wavelengths above groundplane
        pp.setdefault('funklet', True)               # if True, use 4D funklet
        if ns and not TDL_Antenna.Antenna.subtree_voltage_beam(self):
            if pp['funklet']:
                # Use a 4D funklet for the Dipole beamshape:
                name = 'voltage_beam_'+self.tlabel()
                node = _voltage_beam_HorizontalDipole(ns, name=name,
                                                      azimuth=self.azimuth(),
                                                      height=pp['height'])
            else:
                # Alternative: use separate nodes:
                name = 'voltage_beam_nodes_'+self.tlabel()
                node = _voltage_beam_HorizontalDipole_nodes(ns, name=name,
                                                            azimuth=self.azimuth(),
                                                            height=pp['height'])

            # A dipole is an Antenna with only a singe voltage beam:
            TDL_Antenna.Antenna.subtree_voltage_beam(self, clear=True, append=node)
        return TDL_Antenna.Antenna.subtree_voltage_beam(self)










#---------------------------------------------------------------------------

def _voltage_beam_HorizontalDipole (ns, name='<name>', azimuth=0.0, height=0.25):
  """ Create the beam of a HorizontalDipole with given azimuth
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
  x,y should be given as polynomials of x2 and x3 respectively."""

  # dipole height from ground plane in wavelengths
  # make dipole height above ground=lambda/4 to get peak at top
  
  # creation of a compiled funklet - using MXM code
  # polynomials in t,f

  tfpoly = ['1','1','1','1']
  tfpoly = ['p0+p1*x0+p2*x1+p3*x0*x1','p4+p5*x0+p6*x1+p7*x0*x1',\
            'p8+p9*x0+p10*x1+p11*x0*x1','p12+p13*x0+p14*x1+p15*x0*x1']
  if len(tfpoly)<4:
      print "Invalid No. of Polynomials, should be 4"
      return None

  # Default polynomial coefficients
  coeff = [[1],[1],[1],[1]]
  coeff = [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]]

  # Altenative: to see some time variation
  # The third polynomial should model variation of dipole height
  # with freqency                        \/ -- this models height
  # coeff = [[1,0.1,0,0],[1,0.2,0,0],[1,0.10,0.5,0],[1,0.30,0,0]]
  # print 'coeff:',coeff

  # Make the beamshape function:
  h_str=str(height)
  pi = str(math.pi)
  pi2 = str(math.pi/2)
  x = 'x2-'+str(azimuth)      
  y = 'x3'                                # SBY implementation
  y = pi2+'-x3'                           # theta is zenith angle (!)
  # voltage beam, so do not take ^2
  beamshape = 'sqrt((1-(sin(('+tfpoly[0]+')*('+x+'))*sin(('+tfpoly[1]+')*('+y+')))^2)*(sin(2*'+pi+'*'+h_str+'*('+tfpoly[2]+')*cos(('+tfpoly[3]+')*('+y+'))))^2)'
  # print 'beamshape:',beamshape

  # Create the funklet and the MeqParm 
  funklet = meq.polc(coeff=coeff, subclass=meq._funklet_type)
  funklet.function = beamshape;
  uniqual = _counter ('_create_dipole_voltage_beam()', increment=True)
  root = ns[name](uniqual) << Meq.Parm(funklet, node_groups='Parm')
  return root



#---------------------------------------------------------------------------
# The same, but with standard nodes (i.e. no special funklet)
# This is to check the relative performance of such funklets
#---------------------------------------------------------------------------

def _voltage_beam_HorizontalDipole_nodes (ns, name='<name>', azimuth=0.0, height=0.25):
  """ Create the beam of a HorizontalDipole with given azimuth
  The theoretical (power) beam shape is:
  z=(1-sin(x)^2 sin(y)^2)*sin(2*pi*h*cos(y)))^2;
  where
  x:azimuth angle (phi)
  y:elevation angle (theta) (both in radians)
  h: dipole height from ground
  we create a voltage beam, using square root of power as the r.m.s.
  voltage, and add polynomials for time,freq as given by {TF}
  z=(1-sin({TF0}x)^2 sin({TF1}y)^2)*sin(2*pi*h*{TF2}cos({TF3}y))^2
  so we need 4 polynomials, which must be given as tfpoly array.
  The coefficients for these polynomials should be given by coeff array.
  x,y should be given as polynomials of x2 and x3 respectively."""


  az = TDL_Leaf.MeqAzimuth(ns, ref=azimuth)
  el = TDL_Leaf.MeqElevation(ns)
  sinaz2 = ns << Meq.Sqr(ns << Meq.Sin(az))
  sinel2 = ns << Meq.Sqr(ns << Meq.Sin(el))
  factor1 = 1 - (sinaz2 * sinel2)

  pi2 = TDL_Leaf.const_2pi(ns)
  h = Meq.Constant(height)
  cosel = ns << Meq.Cos(el)
  factor2 = ns << Meq.Sqr(ns << Meq.Sin(ns << pi2 * h * cosel))
  
  uniqual = _counter ('_create_dipole_voltage_beam_nodes()', increment=True)
  root = ns[name](uniqual) << Meq.Multiply(factor1,factor2)
  return root


  #------------------------------------------------------------------------
  # dipole height from ground plane in wavelengths
  # make dipole height above ground=lambda/4 to get peak at top
  
  # creation of a compiled funklet - using MXM code
  # polynomials in t,f

  tfpoly = ['1','1','1','1']
  tfpoly = ['p0+p1*x0+p2*x1+p3*x0*x1','p4+p5*x0+p6*x1+p7*x0*x1',\
            'p8+p9*x0+p10*x1+p11*x0*x1','p12+p13*x0+p14*x1+p15*x0*x1']
  if len(tfpoly)<4:
      print "Invalid No. of Polynomials, should be 4"
      return None

  # Default polynomial coefficients
  coeff = [[1],[1],[1],[1]]
  coeff = [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]]

  # Altenative: to see some time variation
  # The third polynomial should model variation of dipole height
  # with freqency                        \/ -- this models height
  # coeff = [[1,0.1,0,0],[1,0.2,0,0],[1,0.10,0.5,0],[1,0.30,0,0]]
  # print 'coeff:',coeff

  # Make the beamshape function:
  h_str=str(height)
  pi = str(math.pi)
  pi2 = str(math.pi/2)
  x = 'x2-'+str(azimuth)      
  y = 'x3'                                # SBY implementation
  y = pi2+'-x3'                           # theta is zenith angle (!)
  # voltage beam, so do not take ^2
  beamshape = 'sqrt((1-(sin(('+tfpoly[0]+')*('+x+'))*sin(('+tfpoly[1]+')*('+y+')))^2)*(sin(2*'+pi+'*'+h_str+'*('+tfpoly[2]+')*cos(('+tfpoly[3]+')*('+y+'))))^2)'
  # print 'beamshape:',beamshape


  # Create the funklet and the MeqParm 
  funklet = meq.polc(coeff=coeff, subclass=meq._funklet_type)
  funklet.function = beamshape;
  uniqual = _counter ('_create_dipole_voltage_beam()', increment=True)
  root = ns[name](uniqual) << Meq.Parm(funklet, node_groups='Parm')
  return root

      


#------------------------------------------------------------------------------------------------

def _voltage_beam_VerticalDipole (ns, name='<name>', height=0.25):
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
      x,y should be given as polynomials of x2 and x3 respectively."""

  tfpoly = ['1','1','1','1']
  if len(tfpoly)<4:
      print "Invalid No. of Polynomials, should be 4"
      return None

  coeff = [[1],[1],[1],[1]]

  h_str=str(height)
  pi=str(math.pi)
  x='x2'
  y='x3'
  # voltage beam, so do not take ^2
  #beamshape='abs(cos('+pi+'/2*('+tfpoly[0]+')*cos(('+tfpoly[1]+')*('+x+')))/sin(('+tfpoly[2]+')*('+x+'))*sin(2*'+pi+'*'+h_str+'*('+tfpoly[3]+')*sin(('+tfpoly[4]+')*('+y+'))))'
  beamshape = 'abs(('+tfpoly[0]+')*sin(('+tfpoly[1]+')*('+y+'))*cos(2.0*'+pi+'*'+h_str+'*('+tfpoly[2]+')*cos(('+tfpoly[3]+')*('+y+'))))'

  
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
    from Timba.Trees import TDL_display
    from Timba.Trees import JEN_record
    ns = NodeScope()
    
    if 0:
        obj = Dipole(label='initial')

    if 1:
        obj = HorizontalDipole(label='hdip_X', azimuth=pi/2)

    if 0:
        dip_X = HorizontalDipole(label='dip_X', azimuth=0)
        dip_Y = HorizontalDipole(label='dip_Y', azimuth=pi/2)
        obj = TDL_Antenna.Feed(dip_X, dip_Y, label='feed')

    if 0:
        dip_X = HorizontalDipole(label='dip_X', azimuth=0)
        dip_Y = HorizontalDipole(label='dip_Y', azimuth=pi/2)
        dip_Z = VerticalDipole(label='dip_Z')           
        obj = TDL_Antenna.Feed(dip_X, dip_Y, dip_Z, label='tridip')

    if 0:
        obj = TDL_Antenna.Array(label='arr')
        dip_X = HorizontalDipole(label='dip_X', azimuth=0)
        dip_Y = HorizontalDipole(label='dip_Y', azimuth=pi/2)
        for i in range(2):
            x = float(i+1)
            for j in range(2):
                y = float(j+1)
                label = 'antel_'+str(obj.nantel())
                # antel = TDL_Antenna.Antenna(label=label, pos0=[x,y,0.0])
                antel = TDL_Antenna.Feed(dip_X.copy(), dip_Y.copy(), label=label, pos0=[x,y,0.0])
                antel.display(label)
                obj.new_element(antel, wgt=1.0, calc_derived=False)
        obj.Array_calc_derived()

    if 1:
        print dir(obj)
        obj.display('initial')
        cc = []
        if 1: cc.append(obj.dcoll_xy(ns))
        if 0: cc.append(obj.subtree_Tsky(ns))
        if 1: cc.append(obj.subtree_sensit(ns))
        if 1: cc.extend(obj.subtree_voltage_beam(ns))
        if 0: cc.extend(obj.subtree_power_beam(ns))
        root = ns.root << Meq.Composer(children=cc)
        TDL_display.subtree(root, 'TDL_Dipole root', full=True, recurse=5)
        obj.display('final')

    if 0:
        # Display the final result:
        # MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        obj.display('final result')
    print '\n*******************\n** End of local test of: TDL_Dipole.py:\n'



#============================================================================================









 

