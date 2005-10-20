# TDL_Antenna.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Antenna object represents an (array of) antenna element(s) 
#
# History:
#    - 16 oct 2005: creation
#    - 18 oct 2005: move Dipole to TDL_Dipole.py
#
# Full description:
# Various classes:
# All are Antenna(TDL_common.Super):
# Inherited functions like:
# - .pos0()

# Single-antenna objects:
# - Array(Antenna)

# Dual-pol arrays of two co-located antennas
# - Feed(Array)
# - WSRT_dish(Feed)
# - LOFAR_LBA(Feed)
# - LOFAR_HBA(Feed)

# Special case: three co-located antennas:
# - TriDipole(Array)

# Arrays of various types:
# - Station(Array)
# - LOFAR_HBA_rack(Array)
# - LOFAR_WHAT(Array)
# - LOFAR_ITS(Array)
# - LOFAR_HB(Array)
# - LOFAR_LB(Array)
# - WSRT_MFFE(Array)


#=================================================================================
# Preamble:
#=================================================================================

from Timba.TDL import *
# from copy import deepcopy
from numarray import *
import math                         # for create_dipole_beam()

from Timba.Trees import TDL_common
from Timba.Trees import TDL_Leaf
# from Timba.Trees import TDL_radio_conventions



#**************************************************************************************
# Some useful helper functions:
#**************************************************************************************




#**************************************************************************************
# Class Antenna:
#**************************************************************************************

class Antenna (TDL_common.Super):
    """A Antenna object represents an (array of) antenna element(s)"""
    
    def __init__(self, **pp):
        
        pp.setdefault('type', 'Antenna')
        pp.setdefault('label', pp['type'])

        pp.setdefault('pos0', array([0.0,0.0,0.0]))
        pp.setdefault('size', array([1.0,1.0,0.0]))
        pp.setdefault('polarisation', 'linear')
        pp.setdefault('azimuth', 0.0)
        pp.setdefault('tilt', 0.0)
        pp.setdefault('groundplane', True)

        pp.setdefault('plot_color', 'red')
        pp.setdefault('plot_style', 'circle')
        pp.setdefault('plot_size', 10)
        pp.setdefault('plot_pen', 2)

        # Some checks:
        for key in ['pos0','size']:
            if isinstance(pp[key], (tuple,list)): pp[key] = array(pp[key])
        key = 'polarisation'
        pols = ['linear','circular','X','Y','Z','R','L',]
        if not isinstance(pp[key], str): pp[key] = pols[0]
        if not pols.__contains__(pp[key]): pp[key] = pols[0]
        
        TDL_common.Super.__init__(self, **pp)

        self.__pos0 = pp['pos0']
        self.__size = pp['size']
        self.__polarisation = pp['polarisation']
        self.__azimuth = pp['azimuth']
        self.__tilt = pp['tilt']
        self.__groundplane = pp['groundplane']
        self.__plot_color = pp['plot_color']
        self.__plot_style = pp['plot_style']
        self.__plot_size = pp['plot_size']
        self.__plot_pen = pp['plot_pen']
        self.calc_derived()
    
    def calc_derived(self):
        self.__leaf_xx = None
        self.__leaf_yy = None
        self.__leaf_zz = None
        self.__dcoll_xy = None
        self.__subtree_sensit = None
        self.__subtree_beam = None
        self.__subtree_Tsky = None
        r2 = 0.0
        for i in range(len(self.__size)):
            r2 += (self.__size[i] * self.__size[i])
        self.__radius = sqrt(r2/4)         # envelope radius
        return True

    def pos0(self, new=None):
        """Get/set the [x,y,z] antenna position (m)""" 
        if isinstance(new, type(array([0]))): self.__pos0 = new
        return self.__pos0

    def radius(self):
        """Return the radius of its envelope (m)""" 
        return self.__radius
    
    def polarisation(self, new=None):
        """Return the polarisation of the antenna""" 
        if isinstance(new, str): self.__polarisation = new
        return self.__polarisation
    
    def azimuth(self, new=None):
        """Get/set the orientation angle in xy-plane (rad)""" 
        if new: self.__azimuth = new
        return self.__azimuth

    def tilt(self, new=None):
        """Get/set the orientation angle w.r.t the z-axis (rad)""" 
        if new: self.__tilt = new
        return self.__tilt

    def plot_color(self): return self.__plot_color
    def plot_style(self): return self.__plot_style
    def plot_size(self): return self.__plot_size
    def plot_pen(self): return self.__plot_pen

    def oneliner(self):
        """Return a one-line summary of the Antenna object"""
        s = TDL_common.Super.oneliner(self)
        s = s+' pos0='+str(self.pos0())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Antenna object"""
        ss = TDL_common.Super.display(self, txt=txt, end=False)
        indent1 = TDL_common.Super.display_indent1(self)
        indent2 = TDL_common.Super.display_indent2(self)
        ss.append(indent1+' - polarisation:  '+str(self.polarisation()))
        sor = 'azimuth='+str(self.azimuth())
        sor += ', tilt='+str(self.tilt())
        ss.append(indent1+' - orientation:   '+sor+' (rad)')
        ss.append(indent1+' - envel. radius: '+str(self.radius())+' (m)')
        splot = str(self.plot_color())+' '+str(self.plot_style())
        splot += ' (size='+str(self.plot_size())+', pen='+str(self.plot_pen())+')'
        ss.append(indent1+' - plotting:      '+splot)
        if self.leaf_xx():
            ss.append(indent1+' - leaf_xx:       '+str(self.leaf_xx()))
        if self.leaf_yy():
            ss.append(indent1+' - leaf_yy:       '+str(self.leaf_yy()))
        if self.leaf_zz():
            ss.append(indent1+' - leaf_zz:       '+str(self.leaf_zz()))
        if self.dcoll_xy():
            ss.append(indent1+' - dcoll_xy:      '+str(self.dcoll_xy()))
        if self.subtree_sensit():
            ss.append(indent1+' - subtree_sensit:'+str(self.subtree_sensit()))
        if self.subtree_beam():
            ss.append(indent1+' - subtree_beam:  '+str(self.subtree_beam()))
        if self.subtree_Tsky():
            ss.append(indent1+' - subtree_Tsky:  '+str(self.subtree_Tsky()))
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


    def dcoll_xy(self, ns=None):
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
            name = 'dcoll_xy_'+self.type()+'_'+self.label()
            self.__dcoll_xy = ns[name](uniqual) << Meq.DataCollect(xy, attrib=attrib,
                                                                   top_label=hiid('visu'))
        return self.__dcoll_xy


    def subtree_sensit(self, ns=None, new=None, **pp):
        """Return a subtree for Antenna sensitivity calculation"""
        if new: self.__subtree_sensit = new
        if ns and not self.__subtree_sensit:
            uniqual = _counter ('subtree_sensit()', increment=True)
            name = 'Antenna_sensitivity'
            node = ns[name](uniqual) << 1.0 
            self.__subtree_sensit = node
        return self.__subtree_sensit

    def subtree_beam(self, ns=None, new=None, **pp):
        """Return a subtree for Antenna beam calculation"""
        if new: self.__subtree_beam = new
        if ns and not self.__subtree_beam:
            uniqual = _counter ('subtree_beam()', increment=True)
            name = 'Antenna_beam'
            self.__subtree_beam = ns[name](uniqual) << 1.0
        return self.__subtree_beam

    def subtree_Tsky (self, ns=None, **pp):
        """Return a subtree for the sky tenperature (K)"""
        pp.setdefault('Tsky_index',-2.6)              # Tsky spectral index  
        if ns and not self.__subtree_Tsky:
            uniqual = _counter ('subtree_Tsky()', increment=True)
            name = 'Tsky('+str(pp['Tsky_index'])+')'
            wvl = TDL_Leaf.MeqWavelength(ns)
            self.__subtree_Tsky = ns[name](uniqual) << Meq.Pow(wvl, -pp['Tsky_index']) * 50
        return self.__subtree_Tsky
    

#**************************************************************************************

# def plot_styles():
#   ss = ['circle', 'rectangle', 'square', 'ellipse',
#         'xcross', 'cross', 'triangle', 'diamond']


#**************************************************************************************
# Class Dipole: (example of single-element Antenna)
#**************************************************************************************

# See TDL_Dipole.py


#**************************************************************************************
# Class Array:
#**************************************************************************************

class Array (Antenna):
    """An Array object represents an array of Antenna objects.
    It is an Antenna object itself"""
    
    def __init__(self, **pp):
        
        pp.setdefault('type', 'Array')
        pp.setdefault('polarisation', 'linear')

        key = 'polarisation'
        pols = ['linear','circular']
        if not isinstance(pp[key], str): pp[key] = pols[0]
        if not pols.__contains__(pp[key]): pp[key] = pols[0]

        Antenna.__init__(self, **pp)

        self.clear()
        self.Array_calc_derived()

    def clear(self):
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
            pol = self.__antel[k].polarisation()
            if ['X','Y','Z','linear'].__contains__(pol):
                self.polarisation('linear')
            elif ['R','L','circular'].__contains__(pol):
                self.polarisation('circular')
        if wtot>0:
            wpos0 /= wtot                        # normalise
            self.pos0(new=wpos0)                 # array centre position
        return True

    def testarr(self):
        """Generate a test-array"""
        for i in range(2):
            x = float(i)
            for j in range(2):
                y = float(j)
                label = 'antel_'+str(self.nantel())
                antel = Antenna(label=label, pos0=[x,y,0.0])
                self.new_element(antel, wgt=1.0, calc_derived=False)
        self.Array_calc_derived()
        return True
    
    def xy_rotate(self, angle=0):
        """Rotate the array by the given angle (rad) in the xy-plane"""
        if angle==0: return True             # not needed
        self.__rotated_xy += angle
        c = cos(pp.rotangle)
        s = sin(pp.rotangle)
        for k in range(self.nantel()):
            xpos = c*self.__xpos[k] + s*self.__ypos[k]
            ypos = c*self.__ypos[k] - s*self.__xpos[k]
            self.__xpos[k] = xpos
            self.__ypos[k] = ypos
        self.Array_calc_derived()
        self.history('.xy_rotate('+str(angle)+')')
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

    # Re-implementation of Antenna methods:
    def xx(self): return self.__xx
    def yy(self): return self.__yy
    def zz(self): return self.__zz
    def wgt(self): return self.__wgt

    # Re-implementation of Antenna method:
    def subtree_sensit(self, ns=None, **pp):
        """Return a subtree for Array sensitivity calculation"""
        if ns and not Antenna.subtree_sensit(self):
            uniqual = _counter ('subtree_sensit()', increment=True)
            name = 'Array_sensitivity'
            cc = []
            for k in range(self.nantel()):
                cc.append(self.antel()[k].subtree_sensit(ns, **pp))
            node = ns[name](uniqual) << Meq.Add(children=cc) 
            Antenna.subtree_sensit(self, new=node)
        return Antenna.subtree_sensit(self)


    # Re-implementation of Antenna method:
    def subtree_beam(self, ns=None, **pp):
        """Return a subtree for Array beam calculation"""
        if ns and not Antenna.subtree_beam(self):
            uniqual = _counter ('subtree_beam()', increment=True)
            # az = TDL_Leaf.MeqAzimuth(ns)
            cosel = ns.cosel(uniqual) << Meq.Cos(TDL_Leaf.MeqElevation(ns))
            pi2 = TDL_Leaf.pi2(ns)
            wvlinv = TDL_Leaf.MeqInverseWavelength(ns)
            q1 = ns.q1(uniqual) << Meq.Multiply(cosel, wvlinv, pi2)   # 2pi*cos(el)/wvl
            q2 = ns.q2(uniqual) << Meq.Multiply(q1, self.leaf_yy(ns)) # yy = tensor node
            bf_wgt = ns.bf_wgts(uniqual) << Meq.Cos(q2)               # beam-former weights
            name = 'beam_'+self.tlabel()
            node = ns[name] << Meq.Add(bf_wgt)                        # add all array elements
            Antenna.subtree_beam(self, new=node)
        return Antenna.subtree_beam(self)






#**************************************************************************************
# Class Station:
#**************************************************************************************

class Station (Array):
    """A Station object represents a specific type of Array.
    It is an Antenna object itself"""
    
    def __init__(self, **pp):

        pp.setdefault('nx', 5)
        pp.setdefault('ny', 5)
        pp.setdefault('dx', 1.0)
        pp.setdefault('dy', 1.0)

        Array.__init__(self, type='Station', **pp)

        self.__nx = pp['nx']
        self.__ny = pp['ny']
        self.__dx = pp['dx']
        self.__dy = pp['dy']

        self.Station_make_array()


    def oneliner(self):
        """Return a one-line summary of the Station object"""
        s = Array.oneliner(self)
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Station object"""
        ss = Array.display(self, txt=txt, full=full, end=False)
        indent1 = Array.display_indent1(self)
        indent2 = Array.display_indent2(self)
        if end: return Array.display_end(self, ss)
        return ss

    def Station_make_array(self, **pp):
        Array.clear(self)
        for i in range(self.__nx):
            x = float(i*self.__dx)
            for j in range(self.__ny):
                y = float(j*self.__dy)
                name = 'antel_'+str(i)+str(j)
                antel = Antenna(label=name, pos0=array([x,y,0.0]))
                Array.new_element(self, antel, wgt=1.0, calc_derived=False)
        Array.Array_calc_derived(self)
        return True



#**************************************************************************************
# Class Feed:
#**************************************************************************************

class Feed (Array):
    """A Feed object is an Array of two colocated receptors (rcp).
    It is an Antenna object itself"""
    
    def __init__(self, rcp1, rcp2, **pp):

        pp.setdefault('plot_color', 'blue')
        pp.setdefault('plot_style', 'cross')

        Array.__init__(self, type='Feed', **pp)

        Array.clear(self)
        Array.new_element(self, rcp1, wgt=1.0, calc_derived=False)
        Array.new_element(self, rcp2, wgt=1.0, calc_derived=False)
        Array.Array_calc_derived(self)


#**************************************************************************************
# Class TriDipole:
#**************************************************************************************

class TriDipole (Array):
    """A TriDipole object is an Array of two colocated receptors (rcp).
    It is an Antenna object itself"""
    
    def __init__(self, rcp1, rcp2, rcp3, **pp):

        pp.setdefault('plot_color', 'blue')
        pp.setdefault('plot_style', 'triangle')

        Array.__init__(self, type='TriDipole', **pp)

        Array.clear(self)
        Array.new_element(self, rcp1, wgt=1.0, calc_derived=False)
        Array.new_element(self, rcp2, wgt=1.0, calc_derived=False)
        Array.new_element(self, rcp3, wgt=1.0, calc_derived=False)
        Array.Array_calc_derived(self)

      





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
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()
    
    if 0:
        obj = Antenna(label='initial')

    if 1:
        obj = Array(label='initial')
        obj.testarr()

    if 0:
        obj = Station(label='initial')

    if 1:
        print dir(obj)
        obj.display('initial')
        if 0:
            dcoll = obj.dcoll_xy(ns)
            MG_JEN_exec.display_subtree(dcoll, 'dcoll_xy()', full=True, recurse=5)
        if 0:
            sensit = obj.subtree_sensit(ns)
            MG_JEN_exec.display_subtree(sensit, 'subtree_sensit()', full=True, recurse=5)
        if 1:
            beam = obj.subtree_beam(ns)
            MG_JEN_exec.display_subtree(beam, 'subtree_beam()', full=True, recurse=5)
        if 0:
            Tsky = obj.subtree_Tsky(ns)
            MG_JEN_exec.display_subtree(Tsky, 'subtree_Tsky()', full=True, recurse=5)
        obj.display('final')

    if 0:
        # Display the final result:
        # MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        obj.display('final result')
    print '\n*******************\n** End of local test of: TDL_Antenna.py:\n'



#============================================================================================









 

