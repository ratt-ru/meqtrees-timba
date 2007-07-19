# TDL_Antenna.py
#
# Author: J.E.Noordam
#
# Short description:
#    An Antenna object represents an (array of) antenna element(s) 
#
# History:
#    - 16 oct 2005: creation
#    - 18 oct 2005: move Dipole to TDL_Dipole.py
#    - 03 dec 2005: TDL_display.py
#    - 28 mar 2005: added mt_polling=True to some Meq.Add nodes
#
# Full description:
# Various classes:
# All inherit from Antenna(TDL_common.Super):
# - phase centre pos0 (x,y,z)
# - size (dx,dy,dz) -> radius
# - polrep (linear, circular)
# - 1-3 voltage beams
# - 1-4 power beams

# Receptor classes (see TDL_Dipole.py):
# - Receptor(Antenna)
# - Dipole(Antenna)         
# - WSRT_21cm(Dipole)
# - HorizontalDipole(Dipole)
# - Rcp_LOFAR_LBA(HorizontalDipole)
# - Rcp_LOFAR_HBA(HorizontalDipole)
# - Rcp_LOFAR_ITS(HorizontalDipole)
# - Rcp_LOFAR_WHAT(HorizontalDipole)

# - Rcp_WSRT_21cm(...Dipole)

# Feed classes (2-3 co-located receptors):
# - Feed(Antenna)
# - TriDipole(Antenna)       
# - Dish(Antenna)       

# Arrays of various types:
# - Station(Array)
# - LOFAR_HBA_rack(Array)
# - LOFAR_WHAT(Array)
# - LOFAR_ITS(Array)
# - LOFAR_HBA(Array)
# - LOFAR_LBA(Array)
# - WSRT_MFFE(Array)



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

from Timba.Contrib.JEN.util import TDL_common
from Timba.Contrib.JEN.util import TDL_Leaf
# from Timba.Contrib.JEN.util import TDL_radio_conventions




#**************************************************************************************
# Class Antenna:
#**************************************************************************************

class Antenna (TDL_common.Super):
    """A Antenna object represents a device that converts
    between EM radiation and a signal in a wire. It may be
    anything from a single receptor to an array of stations.
    It can return MeqTrees for sensitivity, 1-3 voltage beams,
    1-4 power beams, or array visualisation"""
    
    def __init__(self, **pp):
        
        pp.setdefault('type', 'Antenna')
        pp.setdefault('label', pp['type'])

        pp.setdefault('pos0', array([0.0,0.0,0.0]))
        pp.setdefault('size', array([1.0,1.0,1.0]))
        pp.setdefault('polrep', 'linear')

        pp.setdefault('plot_color', 'red')
        pp.setdefault('plot_style', 'circle')
        pp.setdefault('plot_size', 10)
        pp.setdefault('plot_pen', 2)

        # Some checks:
        for key in ['pos0','size']:
            if isinstance(pp[key], (tuple,list)): pp[key] = array(pp[key])
        key = 'polrep'
        pols = ['linear','circular']
        if not isinstance(pp[key], str): pp[key] = pols[0]
        if not pols.__contains__(pp[key]): pp[key] = pols[0]
        
        TDL_common.Super.__init__(self, **pp)

        self.__pos0 = pp['pos0']
        self.__size = pp['size']
        self.__polrep = pp['polrep']
        self.__plot_color = pp['plot_color']
        self.__plot_style = pp['plot_style']
        self.__plot_size = pp['plot_size']
        self.__plot_pen = pp['plot_pen']
        self.__rotated_xy = 0.0
        self.clear()
        self.calc_derived()
    
    def clear(self):
        self.__leaf_xx = None
        self.__leaf_yy = None
        self.__leaf_zz = None
        self.__dcoll_xy = None
        self.__subtree_sensit = None
        self.__subtree_Tsky = None
        self.__subtree_voltage_beam = None
        self.__subtree_voltage_diff = None
        self.__subtree_voltage_peak = None
        self.__subtree_power_beam = None
        self.__subtree_power_diff = None
        self.__subtree_power_peak = None
        return True

    def calc_derived(self):
        r2 = 0.0
        for i in range(len(self.__size)):
            r2 += (self.__size[i] * self.__size[i])
        self.__radius = sqrt(r2/4)         # envelope radius
        return True

    def pos0(self, new=None, shift=None):
        """Get/set the [x,y,z] antenna position (m)""" 
        if (not new==None) or (not shift==None):
            if isinstance(new, (tuple,list)): new = array(new)
            if isinstance(shift, (tuple,list)): shift = array(shift)
            was = self.__pos0
            if isinstance(new, type(array([0]))):
                self.__pos0 = new
                self.calc_derived()
            elif isinstance(shift, type(array([0]))):
                self.__pos0 += shift
                self.calc_derived()
            hist = '.pos0(new='+str(new)+', shift='+str(shift)+'): '
            self.history(hist+str(was)+' -> '+str(Antenna.pos0(self)))
        return self.__pos0

    
    # Re-implementation of TDL_common.Super method:
    def copy(self):
        """Return a copy of the Antenna object"""
        vb = self.subtree_voltage_beam()
        new = TDL_common.Super.copy(self)
        # The nodestubs are not copied, so do it explicitly:
        new.subtree_voltage_beam(replace=vb)
        return new


    def rotate_xy(self, total=None, add=None, recurse=0):
        """Rotate the Antenna by the given angle (rad) around pos0, in the xy-plane"""
        if total:                               # total rotation angle specified
            add = total - self.__rotated_xy     # -> incremental rotation angle
        if not add: return None                 # no change     
        self.__rotated_xy += add                # remember the total rotation angle
        cs = [cos(add)]
        cs.append(sin(add))
        s1 = '.rotate_xy('+str(add)+')'
        s1 += ', total='+str(self.__rotated_xy)+' rad'
        self.history(s1)
        return cs

    def rotated_xy(self):
        """Return the accumulated rotation angle in the xy-plane (rad)""" 
        return self.__rotated_xy
    
    def radius(self):
        """Return the radius of its envelope (m)""" 
        return self.__radius
    
    def polrep(self, new=None):
        """Return the polarisation representation (polrep) of the antenna""" 
        if isinstance(new, str): self.__polrep = new
        return self.__polrep
    
    def plot_color(self, new=None):
        """Get/set the color for plotting the Antenna"""
        if isinstance(new, str): self.__plot_color = new
        return self.__plot_color
    def plot_style(self, new=None):
        """Get/set the symbol style for plotting the Antenna"""
        if isinstance(new, str): self.__plot_style = new
        return self.__plot_style
    def plot_size(self, new=None):
        """Get/set the symbol size for plotting the Antenna"""
        if isinstance(new, str): self.__plot_size = new
        return self.__plot_size
    def plot_pen(self, new=None):
        """Get/set the pen thicness for plotting the Antenna"""
        if isinstance(new, str): self.__plot_pen = new
        return self.__plot_pen

    def oneliner(self):
        """Return a one-line summary of the Antenna object"""
        s = TDL_common.Super.oneliner(self)
        s = s+' pos0='+str(self.pos0())
        rotxy = self.rotated_xy()
        if rotxy!=0: s = s+' (rotxy='+str(rotxy)+' rad)'
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Antenna object"""
        ss = TDL_common.Super.display(self, txt=txt, end=False)
        indent1 = TDL_common.Super.display_indent1(self)
        indent2 = TDL_common.Super.display_indent2(self)
        ss.append(indent1+' - polrep:  '+str(self.polrep()))
        ss.append(indent1+' - envel. radius: '+str(self.radius())+' (m)')
        splot = str(self.plot_color())+' '+str(self.plot_style())
        splot += ' (size='+str(self.plot_size())+', pen='+str(self.plot_pen())+')'
        ss.append(indent1+' - plotting:      '+splot)
        ss.append(indent1+'* Subtrees (root nodes):')
        if self.leaf_xx():
            ss.append(indent1+'    - leaf_xx:   << '+str(self.leaf_xx()))
        if self.leaf_yy():
            ss.append(indent1+'    - leaf_yy:   << '+str(self.leaf_yy()))
        if self.leaf_zz():
            ss.append(indent1+'    - leaf_zz:   << '+str(self.leaf_zz()))
        if self.dcoll_xy():
            ss.append(indent1+'    - dcoll_xy:  << '+str(self.dcoll_xy()))
        if self.subtree_sensit(): 
            ss.append(indent1+'    - sensit:    << '+str(self.subtree_sensit()))
        if self.subtree_voltage_beam():
            ss.append(indent1+'    - voltage_beam(s):')
            bb = self.subtree_voltage_beam()
            for vb in bb:
                ss.append(indent1+'                 << '+str(vb))
        if self.subtree_voltage_diff():
            ss.append(indent1+'    - vb_diff:   << '+str(self.subtree_voltage_diff()))
        if self.subtree_Tsky():
            ss.append(indent1+'    - Tsky:      << '+str(self.subtree_Tsky()))
        if end: return TDL_common.Super.display_end(self, ss)
        return ss

    def xx(self): return self.__pos0[0]
    def yy(self): return self.__pos0[1]
    def zz(self): return self.__pos0[2]

    def leaf_xx(self, ns=None):
        """Return a (tensor) MeqConstant for all xx"""
        if ns and not self.__leaf_xx:
            uniqual = _counter ('leaf_xx()', increment=True)
            self.__leaf_xx = ns.leaf_xx(uniqual) << Meq.Constant(array(self.xx()))
        return self.__leaf_xx

    def leaf_yy(self, ns=None):
        """Return a (tensor) MeqConstant for all yy"""
        if ns and not self.__leaf_yy:
            uniqual = _counter ('leaf_yy()', increment=True)
            self.__leaf_yy = ns.leaf_yy(uniqual) << Meq.Constant(array(self.yy()))
        return self.__leaf_yy

    def leaf_zz(self, ns=None):
        """Return a (tensor) MeqConstant for all zz"""
        if ns and not self.__leaf_zz:
            uniqual = _counter ('leaf_zz()', increment=True)
            self.__leaf_zz = ns.leaf_zz(uniqual) << Meq.Constant(array(self.zz()))
        return self.__leaf_zz


    #---------------------------------------------------------------------------

    def dcoll_xy(self, ns=None, new=None):
        """Return a subtree for Antenna configuration display"""
        if new:
            new.initrec().cache_policy = 100
            self.__dcoll_xy = new
        if ns and not self.__dcoll_xy:
            xx = self.leaf_xx(ns)
            yy = self.leaf_yy(ns)
            xy = ns << Meq.ToComplex(xx, yy)
            attrib = record(tag='tag', plot=record())
            attrib['plot'] = record(type='realvsimag',
                                    # title=pp.title,
                                    color=self.plot_color(),
                                    symbol=self.plot_style(),
                                    symbol_size=self.plot_size())
            uniqual = _counter ('dcoll_xy()', increment=True)
            name = 'dcoll_xy_'+self.tlabel()
            node = ns[name](uniqual) << Meq.DataCollect(xy, attrib=attrib,
                                                        top_label=hiid('visu'))
            node.initrec().cache_policy = 100
            self.__dcoll_xy = node 
        return self.__dcoll_xy

    #---------------------------------------------------------------------------

    def subtree_sensit(self, ns=None, new=None, **pp):
        """Return a subtree for Antenna sensitivity calculation.
        This is a dummy implementation, to be re-implemented by
        classes that inherit from Antenna"""
        if new:
            new.initrec().cache_policy = 100
            self.__subtree_sensit = new
        if ns and not self.__subtree_sensit:
            uniqual = _counter ('subtree_sensit()', increment=True)
            name = 'sensit_'+self.tlabel()
            node = ns[name](uniqual) << 1.0 
            node.initrec().cache_policy = 100
            self.__subtree_sensit = node
        return self.__subtree_sensit

    def subtree_Tsky (self, ns=None, **pp):
        """Return a subtree for the sky tenperature (K)"""
        pp.setdefault('Tsky_index',-2.6)              # Tsky spectral index  
        if ns and not self.__subtree_Tsky:
            node = TDL_Leaf.MeqTsky(ns, index=pp['Tsky_index'])
            node.initrec().cache_policy = 100
            self.__subtree_Tsky = node
        return self.__subtree_Tsky

    #---------------------------------------------------------------------------

    def subtree_voltage_beam(self, ns=None, clear=False, append=None, replace=None, **pp):
        """Return subtree(s) for Antenna voltage beam calculation
        This is a dummy implementation, to be re-implemented by
        classes that inherit from Antenna"""

        if clear:
            self.__subtree_voltage_beam = None           # disable
            self.__subtree_voltage_diff = None           # disable
            self.__subtree_voltage_peak = None           # disable
            self.__subtree_power_beam = None             # disable
            self.__subtree_power_diff = None             # disable
            self.__subtree_power_peak = None             # disable

        if append:                                       # assume root node
            if not self.__subtree_voltage_beam:          
                self.__subtree_voltage_beam = []         # empty list
            append.initrec().cache_policy = 100
            self.__subtree_voltage_beam.append(append)   # new element

        if replace:                                      # assume root node
            self.__subtree_voltage_beam = replace        # replace (assume list)

        # Make a dummy subtree, if necessary:
        if ns and not self.__subtree_voltage_beam:
            self.__subtree_voltage_diff = None           # disable
            self.__subtree_power_beam = None             # disable
            self.__subtree_power_peak = None             # disable
            self.__subtree_power_diff = None             # disable
            uniqual = _counter ('subtree_voltage_beam()', increment=True)
            name = 'dummy_voltage_beam_'+self.tlabel()
            dummy = ns[name](uniqual) << 1.0
            dummy.initrec().cache_policy = 100
            self.__subtree_voltage_beam = [dummy]        # list
            name = 'dummy_voltage_peak_'+self.tlabel()
            self.__subtree_voltage_peak = dummy 
        return self.__subtree_voltage_beam

    #-------------------------------------------------------------------------

    def subtree_voltage_diff(self, ns=None, **pp):
        """Return a subtree with the difference of the two voltage beams"""
        if ns and not self.__subtree_voltage_diff:
            vb = self.subtree_voltage_beam(ns)
            uniqual = _counter ('subtree_voltage_diff()', increment=True)
            if len(vb)>1:
                name = 'voltage_diff_'+self.tlabel()
                diff = ns[name](uniqual) << Meq.Subtract(vb[0], vb[1])
                maxabs = ns << Meq.Max(ns << Meq.Abs(vb[0]))
                name = 'voltage_norm_diff_'+self.tlabel()
                diff = ns[name](uniqual) << Meq.Divide(diff, maxabs)
            else:
                name = 'dummy_voltage_diff_'+self.tlabel()
                diff = ns[name](uniqual) << 0.0
            diff.initrec().cache_policy = 100
            self.__subtree_voltage_diff = diff
        return self.__subtree_voltage_diff

    #---------------------------------------------------------------------------
        
    def subtree_diff_voltage_beam(self, ns=None, other=None, **pp):
        """Return subtree(s) for diff_voltage beams with another Antenna"""
        uniqual = _counter ('subtree_diff_voltage_beam()', increment=True)
        bb1 = self.subtree_voltage_beam(ns)           # get its own voltage beam(s)
        bb2 = other.subtree_voltage_beam(ns)          # get the other voltage beam(s)
        result = []                                   # initialise the output list
        s1 = '_'+self.tlabel()+' - '+other.label()
        for i in range(len(bb1)):
            name = 'diff_voltage_beam_'+str(i+1)+s1
            diff = ns[name](uniqual) << Meq.Subtract(bb1[i], bb2[i])
            if i==0:
                maxabs = ns << Meq.Max(ns << Meq.Abs(bb1[0]))
            name = 'diff_voltage_beam_norm_'+str(i+1)+s1
            diff = ns[name](uniqual) << Meq.Divide(diff, maxabs)
            diff.initrec().cache_policy = 100
            result.append(diff)
        return result

    #---------------------------------------------------------------------------
    
    def subtree_power_beam(self, ns=None, refresh=False, **pp):
        """Return subtree(s) for Antenna power beam calculation"""
        if ns and not self.__subtree_power_beam:
            uniqual = _counter ('subtree_power_beam()', increment=True)
            bb = self.subtree_voltage_beam(ns)           # get the voltage beam(s)
            self.__subtree_power_beam = []               # start a list
            for i in range(len(bb)):
                for j in range(len(bb)):
                    name = 'power_beam_'+str(i+1)+str(j+1)+'_'+self.tlabel()
                    node = ns[name](uniqual) << Meq.Multiply(bb[i], bb[j])
                    node.initrec().cache_policy = 100
                    self.__subtree_power_beam.append(node)
        return self.__subtree_power_beam

   

#**************************************************************************************

# def plot_styles():
#   ss = ['circle', 'rectangle', 'square', 'ellipse',
#         'xcross', 'cross', 'triangle', 'diamond']


#**************************************************************************************
# Class Receptor:
#**************************************************************************************

class Receptor (Antenna):
    """A Receptor object represents a single receiving element.
    It is an Antenna with one polarisaton (linear or circular)"""
    
    def __init__(self, **pp):

        pp.setdefault('polrep', 'linear')
        pp.setdefault('plot_color', 'cyan')
        pp.setdefault('plot_style', 'circle')

        Antenna.__init__(self, type='Receptor', **pp)

        self.plot_color(pp['plot_color'])
        self.plot_style(pp['plot_style'])
        self.Receptor_calc_derived()
        return None

    def Receptor_calc_derived(self):
        """Calculate derived values from primary ones"""
        Antenna.calc_derived(self)
        return True


#**************************************************************************************
# Class Dipole: (example of a receptor)
#**************************************************************************************

# See TDL_Dipole.py


#**************************************************************************************
# Class Feed:
#**************************************************************************************

class Feed (Antenna):
    """A Feed object represents a group of 2-3 co-located receptors."""
    
    def __init__(self, rcp1=None, rcp2=None, rcp3=None, **pp):

        pp.setdefault('plot_color', 'blue')
        pp.setdefault('plot_style', 'cross')

        Antenna.__init__(self, type='Feed', **pp)

        self.plot_color(pp['plot_color'])
        self.plot_style(pp['plot_style'])

        self.__rcp = []
        # NB: Use rcp.copy().....?
        if not rcp1: rcp1 = Antenna(label='rcp1')
        self.__rcp.append(rcp1)                      # at least one rcp required
        if not rcp2: rcp2 = Antenna(label='rcp2')
        self.__rcp.append(rcp2)                      # 2 rcp's are expected, really
        if rcp3: self.__rcp.append(rcp3)             # e.g. TriDipole....

        self.Feed_calc_derived()
        return None

    def Feed_calc_derived(self):
        """Calculate derived values from primary ones"""
        Antenna.calc_derived(self)
        self.nrcp()
        # The receptor elements are at the Feed position
        for k in range(self.nrcp()):
            self.__rcp[k].pos0(new=self.pos0())
        return True

    # Re-implementation of Antenna class method:
    def pos0(self, new=None, shift=None):
        """Get/set the [x,y,z] Feed position (m)""" 
        if (new!=None) or (shift!=None):
            was = Antenna.pos0(self)
            Antenna.pos0(self, new=new, shift=shift)
            self.Feed_calc_derived()
        return Antenna.pos0(self)

    def nrcp(self):
        """Return the number of Feed receptors"""
        self.__nrcp = len(self.__rcp)
        return self.__nrcp

    def rcp(self):
        """Return the list of 1-3 Feed receptors"""
        return self.__rcp

    def oneliner(self):
        """Return a one-line summary of the Feed object"""
        s = Antenna.oneliner(self)
        s = s+' nrcp='+str(self.nrcp())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Feed object"""
        ss = Antenna.display(self, txt=txt, end=False)
        indent1 = Antenna.display_indent1(self)
        indent2 = Antenna.display_indent2(self)

        ss.append(indent1+'* Receptors ('+str(self.nrcp())+'):')    
        for k in range(self.nrcp()):
            ss.append(indent2+'-'+self.rcp()[k].oneliner())
            
        if end: return Antenna.display_end(self, ss)
        return ss


    # Re-implementation of Antenna class method:
    def dcoll_xy(self, ns=None, new=None):
        """Return a subtree for Antenna configuration display"""
        # The plot-symbol depends on the orientation:
        if self.rotated_xy()==0.0:
            self.plot_style('cross')
        else:
            self.plot_style('xcross')
        return Antenna.dcoll_xy(self, ns)

    # Re-implementation of Antenna class method:
    def subtree_voltage_beam(self, ns=None, **pp):
        """Return a list of 2-3 subtree(s) for Feed voltage beam calculation"""
        if ns and not Antenna.subtree_voltage_beam(self):
            for k in range(self.nrcp()):
                vb = self.rcp()[k].subtree_voltage_beam(ns)
                Antenna.subtree_voltage_beam(self, clear=(k==0), append=vb[0])
        return Antenna.subtree_voltage_beam(self)



#**************************************************************************************
# Class Array:
#**************************************************************************************

class Array (Antenna):
    """An Array object represents an array of Antenna objects.
    It is an Antenna object itself"""
    
    def __init__(self, **pp):
        
        pp.setdefault('type', 'Array')

        Antenna.__init__(self, **pp)

        self.clear()
        self.Array_calc_derived()

    def clear(self):
        Antenna.clear(self)
        self.__antel = []                # list of antenna element (objects)
        self.__wgt = []                  # complex weights
        return True

    def new_element(self, antel, wgt=1.0, calc_derived=True):
        """Add a new antenna element to the array""" 
        self.__antel.append(antel)  
        self.__wgt.append(wgt)
        if calc_derived: self.Array_calc_derived()
        return self.nantel()

    def Array_calc_derived(self):
        """Calculate derived values from primary ones"""
        Antenna.calc_derived(self)
        wpos0 = array([0.0,0.0,0.0])
        wtot = 0.0
        self.__xx = []
        self.__yy = []
        self.__zz = []
        for k in range(self.nantel()):
            wgt = self.__wgt[k]
            wtot += wgt
            pos0 = self.__antel[k].pos0()        # array (x,y,z)
            wpos0 += (pos0*wgt)                  # weighted sum
            self.__xx.append(pos0[0])            # list of x-positions
            self.__yy.append(pos0[1])
            self.__zz.append(pos0[2])
            self.polrep(self.__antel[k].polrep())
        if wtot>0:
            wpos0 /= wtot                        # normalise
            Antenna.pos0(self, new=wpos0)           

        # Antel positions w.rt. reference position pos0:
        pos0 = self.pos0()
        self.__dx = list(array(self.__xx) - pos0[0])
        self.__dy = list(array(self.__yy) - pos0[1])
        self.__dz = list(array(self.__zz) - pos0[2])
        self.__leaf_dx = None
        self.__leaf_dy = None
        self.__leaf_dz = None
        return True

    # Re-implementation of Antenna class method:
    def pos0(self, new=None, shift=None):
        """Get/set the [x,y,z] Array position (m)""" 
        if (new!=None) or (shift!=None):
            old = Antenna.pos0(self)
            if (new!=None): shift = array(new)-old
            for antel in self.antel():
                antel.pos0(shift=shift)
            Antenna.pos0(self, shift=shift)
            self.Array_calc_derived()
        return Antenna.pos0(self)

    # Re-implementation of Antenna class method:
    def rotate_xy(self, total=None, add=None, recurse=0):
        """Rotate the Array by the given angle (rad) in the xy-plane"""
        cs = Antenna.rotate_xy(self, total=total, add=add)
        if not cs: return True                # no rotation needed
        pos0 = self.pos0()                    # Array reference pos
        dx = self.dx()                        # w.r.t. pos0 
        dy = self.dy()                        # w.r.t. pos0 
        # Move the Array antenna elements to their new positions:
        for k in range(self.nantel()):
            dxk = cs[0]*dx[k] + cs[1]*dy[k]
            dyk = cs[0]*dy[k] - cs[1]*dx[k]
            self.__antel[k].pos0(new=pos0 + array([dxk,dyk,0]))
            # Optionally, rotate the array elements themselves also:
            if recurse>0:
                self.__antel[k].rotate_xy(total=total, add=add, recurse=recurse-1)
        self.Array_calc_derived()
        return True

    def nantel(self):
        """Return the number of antenna elements in the array"""
        self.__nantel = len(self.__antel)
        return self.__nantel

    def antel(self):
        """Return the list of antenna elements"""
        return self.__antel

    def oneliner(self):
        """Return a one-line summary of the Array object"""
        s = Antenna.oneliner(self)
        s = s+' nantel='+str(self.nantel())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Array object"""
        ss = Antenna.display(self, txt=txt, end=False)
        indent1 = Antenna.display_indent1(self)
        indent2 = Antenna.display_indent2(self)

        if self.leaf_dx():
            ss.append(indent1+'    - leaf_dx:   << '+str(self.leaf_dx()))
        if self.leaf_dy():
            ss.append(indent1+'    - leaf_dy:   << '+str(self.leaf_dy()))
        if self.leaf_dz():
            ss.append(indent1+'    - leaf_dz:   << '+str(self.leaf_dz()))

        xx = array(self.xx())
        yy = array(self.yy())
        zz = array(self.zz())
        ss.append(indent1+'- xx: mean='+str(xx.mean())+' m  ('+str(xx.min())+' <-> '+str(xx.max())+')')
        ss.append(indent1+'- yy: mean='+str(yy.mean())+' m  ('+str(yy.min())+' <-> '+str(yy.max())+')')
        ss.append(indent1+'- zz: mean='+str(zz.mean())+' m  ('+str(zz.min())+' <-> '+str(zz.max())+')')

        dx = array(self.dx())
        dy = array(self.dy())
        dz = array(self.dz())
        ss.append(indent1+'- dx: mean='+str(dx.mean())+' m  ('+str(dx.min())+' <-> '+str(dx.max())+')')
        ss.append(indent1+'- dy: mean='+str(dy.mean())+' m  ('+str(dy.min())+' <-> '+str(dy.max())+')')
        ss.append(indent1+'- dz: mean='+str(dz.mean())+' m  ('+str(dz.min())+' <-> '+str(dz.max())+')')

        ss.append(indent1+'* Antenna elements ('+str(self.nantel())+'):')    
        if full or self.nantel()<5:
            for k in range(self.nantel()):
                ss.append(indent2+'-'+self.__antel[k].oneliner())
        else:
            ss.append(indent2+self.__antel[0].oneliner())
            ss.append(indent2+'............')
            k = self.nantel()-1
            ss.append(indent2+self.__antel[k].oneliner())
            
        if end: return Antenna.display_end(self, ss)
        return ss


    # Re-implementation of Antenna class methods:
    # NB: The latter return the reference position (x,y,z) pos0[0,1,2]
    #     This is a bit of a kludge, perhaps, especially since it was done
    #     originally to avoid re-implementation of subtree_dcoll().....
    def xx(self): return self.__xx
    def yy(self): return self.__yy
    def zz(self): return self.__zz
    def wgt(self): return self.__wgt

    # Antel positions w.r.t. the Array reference pos:
    def dx(self): return self.__dx
    def dy(self): return self.__dy
    def dz(self): return self.__dz

    def leaf_dx(self, ns=None):
        """Return a (tensor) MeqConstant for all dx"""
        if ns and not self.__leaf_dx:
            uniqual = _counter ('leaf_dx()', increment=True)
            self.__leaf_dx = ns.leaf_dx(uniqual) << Meq.Constant(array(self.dx()))
        return self.__leaf_dx

    def leaf_dy(self, ns=None):
        """Return a (tensor) MeqConstant for all dy"""
        if ns and not self.__leaf_dy:
            uniqual = _counter ('leaf_dy()', increment=True)
            self.__leaf_dy = ns.leaf_dy(uniqual) << Meq.Constant(array(self.dy()))
        return self.__leaf_dy

    def leaf_dz(self, ns=None):
        """Return a (tensor) MeqConstant for all dz"""
        if ns and not self.__leaf_dz:
            uniqual = _counter ('leaf_dz()', increment=True)
            self.__leaf_dz = ns.leaf_dz(uniqual) << Meq.Constant(array(self.dz()))
        return self.__leaf_dz

    #---------------------------------------------------------------------------

    # Re-implementation of Antenna class method:
    def dcoll_xy(self, ns=None):
        """Return a subtree for Array configuration display"""
        if ns and not Antenna.dcoll_xy(self):
            uniqual = _counter ('dcoll_xy()', increment=True)
            cc = []                             # initialise list of dcoll children
            if True:
                # Indicate the phase centre (pos0):
                if False:
                    cc.append(Antenna.dcoll_xy(self, ns))    # Does not work!
                else:
                    pos0 = self.pos0()
                    xy0 = ns << Meq.ToComplex(pos0[0], pos0[1])
                    attrib = record(tag='tag0', plot=record())
                    attrib['plot'] = record(type='realvsimag',
                                            # color=Antenna.plot_color(self),
                                            # symbol=Antenna.plot_style(self),
                                            # symbol_size=Antenna.plot_size(self))
                                            color=self.plot_color(),
                                            symbol=self.plot_style(),
                                            symbol_size=self.plot_size())
                    name = 'dcoll_xy0_'+Antenna.tlabel(self)
                    node = ns[name](uniqual) << Meq.DataCollect(xy0, attrib=attrib,
                                                                top_label=hiid('visu'))
                    cc.append(node)

            # Indicate the antenna elements (recursively):
            for antel in self.antel():
                cc.append(antel.dcoll_xy(ns))
            # Make the dcoll parent:
            # attrib = record(tag=['tag','tag0'], plot=record())
            attrib = record(tag=['dconc'], plot=record())
            name = 'dcoll_xy_'+self.tlabel()
            node = ns[name](uniqual) << Meq.DataCollect(children=cc, attrib=attrib,
                                                        top_label=hiid('visu'))
            Antenna.dcoll_xy(self, new=node)
        return Antenna.dcoll_xy(self)


    #---------------------------------------------------------------------------

    # Re-implementation of Antenna class method:
    def subtree_sensit(self, ns=None, **pp):
        """Return a subtree for Array sensitivity calculation"""
        if ns and not Antenna.subtree_sensit(self):
            uniqual = _counter ('subtree_sensit()', increment=True)
            cc = []
            for k in range(self.nantel()):
                cc.append(self.antel()[k].subtree_sensit(ns, **pp))
            name = 'sensit_'+self.tlabel()
            node = ns[name](uniqual) << Meq.Add(children=cc, mt_polling=True)
            Antenna.subtree_sensit(self, new=node)
        return Antenna.subtree_sensit(self)


    # Re-implementation of Antenna class method:
    def subtree_voltage_beam(self, ns=None, **pp):
        """Return a list of 1-3 subtree(s) for Array voltage beam calculation"""
        # pp.setdefault('dissimilar_name', True)      # if True, tamper with the name...
        pp.setdefault('az0', pi)                      # Az (rad) of pointing direction
        pp.setdefault('el0', 1.0)                     # El (rad) of pointing direction
        pp.setdefault('uniform', True)                # If True, assume identical antel voltage beams

        if ns and not Antenna.subtree_voltage_beam(self):
            uniqual = _counter ('subtree_voltage_beam()', increment=True)
            az = TDL_Leaf.MeqAzimuth(ns)
            el = TDL_Leaf.MeqElevation(ns)
            dxcosaz = ns.xcosaz(uniqual) << Meq.Multiply(Meq.Cos(az),self.leaf_dx(ns))
            dysinaz = ns.ysinaz(uniqual) << Meq.Multiply(Meq.Sin(az),self.leaf_dy(ns))
            xyaz = ns << Meq.Add(dxcosaz, dysinaz, mt_polling=True)
            cosel = ns << Meq.Cos(el)
            pi2 = TDL_Leaf.const_2pi(ns)
            wvlinv = TDL_Leaf.MeqInverseWavelength(ns)
            delay = ns.delay(uniqual) << Meq.Multiply(cosel, wvlinv, pi2, xyaz)          # 2pi*cos(el)*xyaz/wvl
            if True:
                # Off-set pointing (away from zenith):
                az0 = ns.az0(uniqual) << Meq.Parm(pp['az0'])
                el0 = ns.el0(uniqual) << Meq.Parm(pp['el0'])
                dxcosaz0 = ns.xcosaz0(uniqual) << Meq.Multiply(Meq.Cos(az0),self.leaf_dx(ns))
                dysinaz0 = ns.ysinaz0(uniqual) << Meq.Multiply(Meq.Sin(az0),self.leaf_dy(ns))
                xyaz0 = ns << Meq.Add(dxcosaz0, dysinaz0, mt_polling=True)
                cosel0 = ns << Meq.Cos(el0)
                delay0 = ns.delay0(uniqual) << Meq.Multiply(cosel0, wvlinv, pi2, xyaz0)  # 2pi*sin(el0)*xyaz0/wvl
                delay = ns.ddelay(uniqual) << Meq.Subtract(delay,delay0)
            bf_wgts = ns.bf_wgts(uniqual) << Meq.Cos(delay)            # beam-former weights

            # Extract the bf_wgts as a list (bfw) of individual nodes,
            # and calculate a list of antel voltage beams:
            bf_wgt = []
            vbeam = []
            npol = 1
            antel = self.antel()                                       # list of antenna elements
            for i in range(len(antel)):
                cname = 'bf_wgt_'+str(i)
                bf_wgt.append(ns[cname](uniqual) << Meq.Selector(bf_wgts, index=i))
                if pp['uniform'] and i>0: continue                     # only vbeam[0] is needed
                vb = antel[i].subtree_voltage_beam(ns)                 # list of 1-3 voltage beams
                npol = len(vb)                                     
                vbeam.append(vb)                                       # used below

            # Form the array voltage beams by weighted addition of antel beams:
            for k in range(npol):                                      # all polarisations
                cc = []
                for i in range(len(antel)):
                    name = 'weighted_voltage_beam_'+str(i)+'_'+str(k+1)+'_'+self.tlabel()
                    if pp['uniform']:
                        # Assume that elements have identical voltage beams:
                        cc.append(ns[name](uniqual) << Meq.Multiply(bf_wgt[i],vbeam[0][k]))
                    else:
                        # Assume that elements have different voltage beams:
                        cc.append(ns[name](uniqual) << Meq.Multiply(bf_wgt[i],vbeam[i][k]))
                name = 'voltage_beam_'+str(k+1)+'_'+self.tlabel()
                vb = ns[name](uniqual) << Meq.Add(children=cc, mt_polling=True)
                Antenna.subtree_voltage_beam(self, clear=(k==0), append=vb)

                    
        return Antenna.subtree_voltage_beam(self)


 









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
    if trace: print '** Antenna: _counters(',key,') =',_counters[key]
    return _counters[key]





#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Antenna.py:\n'
    from Timba.Contrib.JEN.util import TDL_display
    # from Timba.Contrib.JEN.util import JEN_record
    ns = NodeScope()
    
    if 0:
        obj = Antenna(label='whatever')

    if 0:
        obj = Receptor(label='rcp_1_11')

    if 1:
        obj = Feed(label='feed_11', pos0=[1,2,3])

    if 0:
        obj = Array(label='arr')
        for i in range(2):
            x = float(i+1)
            for j in range(2):
                y = float(j+1)
                label = 'antel_'+str(obj.nantel())
                if True:
                    antel = Antenna(label=label, pos0=[x,y,0.0])
                else:
                    antel = Feed(label=label, pos0=[x,y,0.0])
                obj.new_element(antel, wgt=1.0, calc_derived=False)
        obj.Array_calc_derived()

    #--------------------------------------------------------------------------

    if 1:
        obj.display('before rotate_xy()')
        obj.rotate_xy(0.1)

    if 0:
        obj.display('before pos0()')
        obj.pos0(new=[6,7,8])
        obj.pos0(shift=[1,2,3])

    if 1:
        print dir(obj)
        # obj.display('common')
        cc = []
        if 1:
            cc.append(obj.dcoll_xy(ns))
        if 0:
            cc.append(obj.subtree_sensit(ns))
            cc.append(obj.subtree_Tsky(ns))
        if 0:
            bb = obj.subtree_voltage_beam(ns)
            for vb in bb: cc.append(vb)
            cc.append(obj.subtree_voltage_diff(ns))
        if 0:
            bb = obj.subtree_power_beam(ns)
            for vb in bb: cc.append(vb)
        root = ns.root << Meq.Composer(children=cc)
        TDL_display.subtree(root, 'TDL_Antenna: root', full=True, recurse=5)
        obj.display('final')

    if 0:
        # Display the final result:
        # TDL_display.subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        obj.display('final result')
    print '\n*******************\n** End of local test of: TDL_Antenna.py:\n'



#============================================================================================









 

