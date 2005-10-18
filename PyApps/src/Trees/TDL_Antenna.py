# TDL_Antenna.py
#
# Author: J.E.Noordam
#
# Short description:
#    A Antenna object represents an (array of) antenna element(s) 
#
# History:
#    - 16 oct 2005: creation
#
# Full description:
# Various classes:
# All are Antenna(TDL_common.Super):
# Inherited functions like:
# - .pos0()

# Single-antenna objects:
# - Dipole(Antenna)
# - Array(Antenna)

# Colocated dual-pol arrays of two antennas
# - DiDipole(Array)
# - WSRT_dish(DiDipole)
# - LOFAR_LBA(DiDipole)
# - LOFAR_HBA(DiDipole)

# Special case: three colocated antannas:
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

from Timba.Trees import TDL_common
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
        pp.setdefault('pos0', array([0.0,0.0,0.0]))
        pp.setdefault('size', array([1.0,1.0,0.0]))
        pp.setdefault('azimuth', 0.0)
        pp.setdefault('tilt', 0.0)
        pp.setdefault('groundplane', True)
        pp.setdefault('plot_color', 'red')
        pp.setdefault('plot_style', 'circle')
        pp.setdefault('plot_size', 10)
        pp.setdefault('plot_pen', 2)
        if isinstance(pp['pos0'], (tuple,list)): pp['pos0'] = array(pp['pos0'])
        if isinstance(pp['size'], (tuple,list)): pp['size'] = array(pp['size'])
        
        TDL_common.Super.__init__(self, **pp)

        self.__pos0 = pp['pos0']
        self.__size = pp['size']
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
        sor = 'azimuth='+str(self.azimuth())
        sor += ', tilt='+str(self.tilt())
        ss.append(indent1+' - orientation:   '+sor+' (rad)')
        ss.append(indent1+' - env. radius:   '+str(self.radius())+' (m)')
        splot = str(self.plot_color())+' '+str(self.plot_style())
        splot += ' (size='+str(self.plot_size())+', pen='+str(self.plot_pen())+')'
        ss.append(indent1+' - plotting:      '+splot)
        ss.append(indent1+' - leaf_xx:       '+str(self.leaf_xx()))
        ss.append(indent1+' - leaf_yy:       '+str(self.leaf_yy()))
        ss.append(indent1+' - leaf_zz:       '+str(self.leaf_zz()))
        ss.append(indent1+' - dcoll_xy:      '+str(self.dcoll_xy()))
        ss.append(indent1+' - subtree_sensit:'+str(self.subtree_sensit()))
        ss.append(indent1+' - subtree_beam:  '+str(self.subtree_beam()))
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


    def subtree_sensit(self, ns=None):
        """Return a subtree for Antenna sensitivity calculation"""
        if ns and not self.__subtree_sensit:
            uniqual = _counter ('subtree_sensit()', increment=True)
            name = 'Antenna_sensitivity'
            node = ns[name](uniqual) << 1.0 
            self.__subtree_sensit = node
        return self.__subtree_sensit

    def subtree_beam(self, ns=None):
        """Return a subtree for Antenna beam calculation"""
        if ns and not self.__subtree_beam:
            self.__subtree_beam = None
        return self.__subtree_beam



#**************************************************************************************
# Class Dipole: (example of single-element Antenna)
#**************************************************************************************

class Dipole (Antenna):
    """A Dipole object represents an (array of) antenna element(s)"""
    
    def __init__(self, **pp):
        
        pp.setdefault('length', 1.0)     # dipole length
        pp.setdefault('height', 0.5)     # dipole height above groundplane
        pp.setdefault('plot_color', 'blue')
        pp.setdefault('plot_style', 'cross')

        Antenna.__init__(self, type='Dipole', **pp)

        self.__length = pp['length']
        self.__height = pp['height']
        self.Dipole_calc_derived()

    def Dipole_calc_derived(self):
        Antenna.calc_derived(self)
        self.__subtree_sensit = None
        self.__subtree_beam = None
        return True

    def length(self): return self.__length
    def height(self): return self.__height

    def oneliner(self):
        """Return a one-line summary of the Dipole"""
        s = Antenna.oneliner(self)
        s = s+' length='+str(self.length())
        s = s+' height='+str(self.height())
        return s

    def display(self, txt=None, full=False, end=True):
        """Display (print) the contents of the Dipole"""
        ss = Antenna.display(self, txt=txt, end=False)
        indent1 = Antenna.display_indent1(self)
        indent2 = Antenna.display_indent2(self)
        if end: Antenna.display_end(self, ss)
        return ss

    # Re-implementation of Antenna method:
    def subtree_sensit(self, ns=None):
        """Return a subtree for Dipole sensitivity calculation"""
        if ns and not self.__subtree_sensit:
            uniqual = _counter ('subtree_sensit()', increment=True)
            name = 'Dipole_sensitivity'
            node = ns[name](uniqual) << 1.0 
            self.__subtree_sensit = node
        return self.__subtree_sensit

    # Re-implementation of Antenna method:
    def subtree_beam(self, ns=None):
        """Return a subtree for Dipole beam calculation"""
        if ns and not self.__subtree_beam:
            self.__subtree_beam = None
        return self.__subtree_beam





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
        self.__subtree_sensit = None
        self.__subtree_beam = None
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
                antel = Dipole(label=label, pos0=[x,y,0.0])
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
    def subtree_sensit(self, ns=None):
        """Return a subtree for Array sensitivity calculation"""
        if ns and not self.__subtree_sensit:
            uniqual = _counter ('subtree_sensit()', increment=True)
            name = 'Array_sensitivity'
            cc = []
            for k in range(self.nantel()):
                cc.append(self.antel()[k].subtree_sensit(ns))
            node = ns[name](uniqual) << Meq.Add(children=cc) 
            self.__subtree_sensit = node
        return self.__subtree_sensit

    # Re-implementation of Antenna method:
    def subtree_beam(self, ns=None):
        """Return a subtree for Array beam calculation"""
        if ns and not self.__subtree_beam:
            self.__subtree_beam = None
        return self.__subtree_beam






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
                antel = Dipole(label=name, pos0=array([x,y,0.0]))
                Array.new_element(self, antel, wgt=1.0, calc_derived=False)
        Array.Array_calc_derived(self)
        return True

         
      





#========================================================================
# Helper routines:
#========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
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
        ant = Antenna(label='initial')
        print dir(ant)
        ant.display('initial')
        dcoll = ant.dcoll_xy(ns)
        MG_JEN_exec.display_subtree(dcoll, 'Antenna.dcoll_xy()', full=True, recurse=5)
        sensit = ant.subtree_sensit(ns)
        MG_JEN_exec.display_subtree(sensit, 'Antenna.subtree_sensit()', full=True, recurse=5)
        ant.display('final')

    if 0:
        dip = Dipole(label='initial')
        print dir(dip)
        dip.display('initial')
        dcoll = dip.dcoll_xy(ns)
        MG_JEN_exec.display_subtree(dcoll, 'Dipole.dcoll_xy()', full=True, recurse=5)
        dip.display('final')

    if 1:
        arr = Array(label='initial')
        print dir(arr)
        arr.testarr()
        arr.display('initial')
        dcoll = arr.dcoll_xy(ns)
        MG_JEN_exec.display_subtree(dcoll, 'Array.dcoll_xy()', full=True, recurse=5)
        sensit = arr.subtree_sensit(ns)
        MG_JEN_exec.display_subtree(sensit, 'Array.subtree_sensit()', full=True, recurse=5)
        arr.display('final')

    if 0:
        stat = Station(label='initial')
        print dir(stat)
        stat.display('initial')
        dcoll = stat.dcoll_xy(ns)
        MG_JEN_exec.display_subtree(dcoll, 'Station.dcoll_xy()', full=True, recurse=5)
        stat.display('final')

    if 0:
        # Display the final result:
        # MG_JEN_exec.display_subtree(cs[k], 'cs['+str(k)+']', full=True, recurse=5)
        ant.display('final result')
    print '\n*******************\n** End of local test of: TDL_Antenna.py:\n'



#============================================================================================









 

