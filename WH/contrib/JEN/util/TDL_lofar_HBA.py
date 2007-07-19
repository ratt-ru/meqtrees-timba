# TDL_lofar_HBA.py
#
# Author: J.E.Noordam
#
# Short description:
#    Hierarchy of LOFAR High Band Array antennas 
#
# History:
#    - 29 oct 2005: creation
#
# Full description:



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
# from copy import deepcopy
from numarray import *
from math import *

# from Timba.Contrib.JEN.util import TDL_common
from Timba.Contrib.JEN.util import TDL_Leaf
from Timba.Contrib.JEN.util import TDL_Antenna
from Timba.Contrib.JEN.util import TDL_Dipole
# from Timba.Contrib.JEN.util import TDL_radio_conventions





#**************************************************************************************
# Class LOFAR_HBA_rack:
#**************************************************************************************

class LOFAR_HBA_rack (TDL_Antenna.Array):
    """A LOFAR High Band Antenna rack is a 4x4 Array object.
    It is an Antenna object itself"""
    
    def __init__(self, ns=None, **pp):

        pp.setdefault('nx', 4)
        pp.setdefault('ny', 4)
        pp.setdefault('xsep', 1.0)
        pp.setdefault('ysep', 1.0)

        TDL_Antenna.Array.__init__(self, type='LOFAR_HBA_rack', **pp)

        self.__nx = pp['nx']
        self.__ny = pp['ny']
        self.__xsep = pp['xsep']
        self.__ysep = pp['xsep']

        self.clear()
        pos0 = self.pos0()
        if True:
            # Different Feeds (very expensive in processing):
            for i in range(self.__nx):
                x = float(i*self.__xsep)
                for j in range(self.__ny):
                    y = float(j*self.__ysep)
                    name = 'dip_X_'+str(i+1)
                    dip_X = TDL_Dipole.HorizontalDipole(label=name)
                    name = 'dip_X_'+str(i+1)
                    dip_Y = TDL_Dipole.HorizontalDipole(label=name, azimuth=pi/2)
                    name = 'antel_'+str(i+1)+str(j+1)
                    antel = TDL_Antenna.Feed(dip_X, dip_Y, label=name, pos0=array([x,y,0.0]))
                    self.new_element(antel, wgt=1.0, calc_derived=False)

        else:
            # obsolete....
            # Share the same Feed object for all 4x4 feeds:
            dip_X = TDL_Dipole.HorizontalDipole(label='dip_X')
            dip_Y = TDL_Dipole.HorizontalDipole(label='dip_Y', azimuth=pi/2)
            antel = TDL_Antenna.Feed(dip_X, dip_Y, label='antel')
            # Generate subtree(s) before copying the object:
            vb = antel.subtree_voltage_beam(ns)
            for i in range(self.__nx):
                x = float(i*self.__xsep)
                for j in range(self.__ny):
                    y = float(j*self.__ysep)
                    antel1 = antel.copy()
                    antel1.pos0(array([x,y,0.0]))
                    self.new_element(antel1, wgt=1.0, calc_derived=False)
        self.Array_calc_derived()
        self.pos0(new=pos0)


    def xsep(self): return self.__xsep
    def ysep(self): return self.__ysep

    def oneliner(self):
        """Return a one-line summary of the Station object"""
        s = TDL_Antenna.Array.oneliner(self)
        s = s+'  (xsep='+str(self.xsep())+' ysep='+str(self.ysep())+' m)'
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Station object"""
        ss = TDL_Antenna.Array.display(self, txt=txt, full=full, end=False)
        indent1 = TDL_Antenna.Array.display_indent1(self)
        indent2 = TDL_Antenna.Array.display_indent2(self)
        if end: return TDL_Antenna.Array.display_end(self, ss)
        return ss



#**************************************************************************************
# Class LOFAR_HBA_station:
#**************************************************************************************

class LOFAR_HBA_station (TDL_Antenna.Array):
    """A LOFAR_HBA_station object represents a specific type of Array.
    It is an Antenna object itself"""
    
    def __init__(self, **pp):

        pp.setdefault('aspect_ratio', 1.4)
        pp.setdefault('nx', 8)
        pp.setdefault('xsep', 4.0)
        pp.setdefault('ysep', 4.0)

        TDL_Antenna.Array.__init__(self, type='LOFAR_HBA_station', **pp)

        self.__aspect_ratio = pp['aspect_ratio']
        self.__nx = pp['nx']
        self.__xsep = float(pp['xsep'])
        self.__ysep = float(pp['ysep'])

        # Calculate the half-axis lengths of the ellipse:
        sax = pp['nx']*pp['xsep']/2.0   
        lax = sax * pp['aspect_ratio']
        nx2 = ceil(sax/pp['xsep'])
        ny2 = ceil(lax/pp['ysep'])

        xx = array(range(-nx2,nx2)) * self.__xsep
        yy = array(range(-ny2,ny2)) * self.__ysep
        print 'xx =',xx
        print 'yy =',yy
        xx -= xx.mean()
        yy -= yy.mean()
        print 'xx =',xx
        print 'yy =',yy
        print 'xx.max() =',xx.max()
        print 'yy.max() =',yy.max()

        self.clear()
        pos0 = self.pos0()
        for i in range(len(xx)):
            print
            for j in range(len(yy)):
                r2 = (xx[i]/sax)**2 + (yy[j]/lax)**2
                print i,j,'  ',xx[i],yy[j],'   r2 =',r2,
                if r2<1:
                    print 'include'
                    name = 'rack_'+str(i+1)+str(j+1)
                    antel = LOFAR_HBA_rack(label=name, pos0=array([xx[i],yy[j],0.0]))
                    self.new_element(antel, wgt=1.0, calc_derived=False)
                else:
                    print 'ignore'
        self.Array_calc_derived()
        self.pos0(new=pos0)


    def xsep(self): return self.__xsep
    def ysep(self): return self.__ysep

    def oneliner(self):
        """Return a one-line summary of the LOFAR_HBA_station object"""
        s = TDL_Antenna.Array.oneliner(self)
        s = s+'  (xsep='+str(self.xsep())+' ysep='+str(self.ysep())+' m)'
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Station object"""
        ss = TDL_Antenna.Array.display(self, txt=txt, full=full, end=False)
        indent1 = TDL_Antenna.Array.display_indent1(self)
        indent2 = TDL_Antenna.Array.display_indent2(self)
        if end: return TDL_Antenna.Array.display_end(self, ss)
        return ss



#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

class LOFAR_HBA_station_old (TDL_Antenna.Array):
    """A LOFAR_HBA_station object represents a specific type of Array.
    It is an Antenna object itself"""
    
    def __init__(self, **pp):

        pp.setdefault('nx', 5)
        pp.setdefault('ny', 5)
        pp.setdefault('xsep', 4.0)
        pp.setdefault('ysep', 4.0)

        TDL_Antenna.Array.__init__(self, type='LOFAR_HBA_station', **pp)

        self.__nx = pp['nx']
        self.__ny = pp['ny']
        self.__xsep = float(pp['xsep'])
        self.__ysep = float(pp['ysep'])

        xx = array(range(self.__nx)) * self.__xsep
        yy = array(range(self.__ny)) * self.__ysep
        print 'xx =',xx
        print 'yy =',yy
        xx -= xx.mean()
        yy -= yy.mean()
        print 'xx =',xx
        print 'yy =',yy
        print 'xx.max() =',xx.max()
        print 'yy.max() =',yy.max()
        rmax = max(array([xx.max(),yy.max()])) * 1.1
        if self.__nx<3: rmax = xx.max() + yy.max()      # use all
        if self.__ny<3: rmax = xx.max() + yy.max()      # use all
        print 'rmax =',rmax

        self.clear()
        pos0 = self.pos0()
        for i in range(len(xx)):
            for j in range(len(yy)):
                r = sqrt(xx[i]*xx[i] + yy[j]*yy[j])
                print i,j,r,rmax,
                if r<rmax:
                    print 'include'
                    name = 'rack_'+str(i+1)+str(j+1)
                    antel = LOFAR_HBA_rack(label=name, pos0=array([xx[i],yy[j],0.0]))
                    self.new_element(antel, wgt=1.0, calc_derived=False)
                else:
                    print 'ignore'
        self.Array_calc_derived()
        self.pos0(new=pos0)


    def xsep(self): return self.__xsep
    def ysep(self): return self.__ysep

    def oneliner(self):
        """Return a one-line summary of the LOFAR_HBA_station object"""
        s = TDL_Antenna.Array.oneliner(self)
        s = s+'  (xsep='+str(self.xsep())+' ysep='+str(self.ysep())+' m)'
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Station object"""
        ss = TDL_Antenna.Array.display(self, txt=txt, full=full, end=False)
        indent1 = TDL_Antenna.Array.display_indent1(self)
        indent2 = TDL_Antenna.Array.display_indent2(self)
        if end: return TDL_Antenna.Array.display_end(self, ss)
        return ss





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
    if trace: print '** LOFAR_HBA: _counters(',key,') =',_counters[key]
    return _counters[key]





#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_lofar_HBA.py:\n'
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    

    if 0:
        obj = LOFAR_HBA_rack(label='rack_11', pos0=[1,2,3])

    if 0:
        obj = LOFAR_HBA_rack(ns=ns, label='rack_11', pos0=[1,2,3])

    if 0:
      rack1 = LOFAR_HBA_rack(label='rack1', pos0=[6,0,0])
      rack1.display('rack1')
      rack2 = LOFAR_HBA_rack(label='rack2')
      rack2.rotate_xy(0.1)
      rack2.display('rack2')
      diff = rack1.subtree_diff_voltage_beam(ns, rack2)
      MG_JEN_exec.display_subtree(diff[0], 'TDL_lofar_HBA: diff[0]', full=True, recurse=5)

    if 1:
        obj = LOFAR_HBA_station()


    #--------------------------------------------------------------------------

    if 0:
        obj.display('before rotate_xy()')
        obj.rotate_xy(0.1)

    if 0:
        obj.display('before pos0()')
        obj.pos0(new=[6,7,8])
        obj.pos0(shift=[1,2,3])
        
    if 0:
        obj.subtree_voltage_beam(ns)
        obj.display('before copy()')
        vb = obj.subtree_voltage_beam()
        print vb

        obj1 = obj.copy()
        obj1.display('after copy()')
        vb = obj1.subtree_voltage_beam()
        print vb
        
    if 1:
        print dir(obj)
        # obj.display('common')
        cc = []
        if 1:
            cc.append(obj.dcoll_xy(ns))
        if 0:
            cc.append(obj.subtree_sensit(ns))
            cc.append(obj.subtree_Tsky(ns))
        if 1:
            bb = obj.subtree_voltage_beam(ns)
            for vb in bb: cc.append(vb)
            cc.append(obj.subtree_voltage_diff(ns))
        if 0:
            bb = obj.subtree_power_beam(ns)
            for vb in bb: cc.append(vb)
        root = ns.root << Meq.Composer(children=cc)
        MG_JEN_exec.display_subtree(root, 'TDL_lofar_HBA: root', full=True, recurse=5)
        obj.display('final')

    if 0:
        # Display the final result:
        # MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        obj.display('final result')
    print '\n*******************\n** End of local test of: TDL_lofar_HBA.py:\n'



#============================================================================================









 

