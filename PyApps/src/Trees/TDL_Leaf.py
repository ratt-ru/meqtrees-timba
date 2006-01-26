# TDL_Dipole.py
#
# Author: J.E.Noordam
#
# Short description:
#    Predefined MeqTree end-points (leaves) f various kinds.
#    An effort is made to generate unique node names....
#
# History:
#    - 19 oct 2005: creation
#    - 20 jan 2006: unary operations (unop=...)
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
from math import *        

from Timba.Trees import TDL_common
# from Timba.Trees import TDL_radio_conventions

#**************************************************************************************
# Constants:
#**************************************************************************************


def const_pi(ns): return MeqConstant(ns, 'pi', pi)
def const_2pi(ns): return MeqConstant(ns, '2pi', 2*pi)
def const_pi2(ns): return MeqConstant(ns, 'pi/2', pi/2)
def const_e(ns): return MeqConstant(ns, 'e_ln', e)
def const_sqrt2(ns): return MeqConstant(ns, 'sqrt(2)', sqrt(2.0))
def const_sqrt3(ns): return MeqConstant(ns, 'sqrt(3)', sqrt(3.0))

def const_c_light(ns): return MeqConstant(ns, 'c_light_m/s', 2.9979250e8)
def const_e_charge(ns): return MeqConstant(ns, 'e_charge_C', 1.6021917e-19)
h_Planck =  6.626196e-34
def const_h_Planck(ns): return MeqConstant(ns, 'h_Planck_Js', h_Planck)
def const_h2pi_Planck(ns): return MeqConstant(ns, 'h2pi_Planck_Js', h_Planck/(2*pi))
k_Boltzmann = 1.380622e-23
def const_k_Boltzmann(ns): return MeqConstant(ns, 'k_Boltzmann_J/K', k_Boltzmann)
def const_k_Jy(ns): return MeqConstant(ns, 'k_Jy/K', k_Boltzmann/1e-26)
def const_2k_Jy(ns): return MeqConstant(ns, '2k_Jy/Hz.K', 2*k_Boltzmann/1e-26)
def const_G_gravity(ns): return MeqConstant(ns, 'G_gravity_Nm2/kg2', 6.6732e-11)

def MeqConstant(ns, name='constant', value=-1.0, unop=None):
    uniqual = _counter (name, increment=True)
    node = ns[name](uniqual) << Meq.Constant(value)
    return apply_unop(ns, unop, node)
    



#**************************************************************************************
# Leaves built on regular nodes (e.g. MeqFreq):
#**************************************************************************************


def apply_unop(ns, unop=None, node=None):
    """Helper function to apply (optional) unary operation(s) to node"""
    if unop==None: return node
    if not isinstance(unop, (list, tuple)): unop = [unop]
    for unop1 in unop:
        node = ns << getattr(Meq,unop1)(node)
    return node

def MeqFreq(ns, name='MeqFreq', unop=None):
    uniqual = _counter (name, increment=True)
    node = ns[name](uniqual) << Meq.Freq()
    return apply_unop(ns, unop, node)

def MeqWavelength(ns, name='MeqWavelength', unop=None):
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)                          # Hz
    node = ns[name](uniqual) << Meq.Divide(const_c_light(ns), freq)
    return apply_unop(ns, unop, node)

def MeqInverseWavelength(ns, name='MeqInverseWavelength', unop=None):
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)                          # Hz
    node = ns[name](uniqual) << Meq.Divide(freq, const_c_light(ns))
    return apply_unop(ns, unop, node)

def MeqTime(ns, name='MeqTime', unop=None):
    uniqual = _counter (name, increment=True)
    node = ns[name](uniqual) << Meq.Time()
    return apply_unop(ns, unop, node)

def MeqFreqTimeComplex(ns, name='MeqFreqTime', unop=None):
    return MeqFreqTime(ns, combine='ToComplex', name=name)
    return apply_unop(ns, unop, node)

def MeqTimeFreqComplex(ns, name='MeqTimeFreq', unop=None):
    return MeqTimeFreq(ns, combine='ToComplex', name=name)

def MeqFreqTime(ns, combine='Add', name='MeqFreqTime', unop=None):
    name += '_'+combine                         # -> MeqFreqTime_Add
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)
    time = MeqTime(ns)
    node = ns[name](uniqual) << getattr(Meq,combine)(children=[freq, time])
    return apply_unop(ns, unop, node)

def MeqTimeFreq(ns, combine='Add', name='MeqTimeFreq', unop=None):
    name += '_'+combine                         # -> MeqTimeFreq_Add
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)
    time = MeqTime(ns)
    node = ns[name](uniqual) << getattr(Meq,combine)(children=[time, freq])
    return apply_unop(ns, unop, node)

#-------------------------------------------------------------------------------------
# Some 'leaves' with parameters:
#-------------------------------------------------------------------------------------

def MeqTsky (ns, index=-2.6, unop=None):
    """Return a subtree for the sky temperature (K).
    The argument index specifies the default(=-2.6) spectral index"""
    uniqual = _counter ('MeqTsky', increment=True)
    pindex = ns.Tsky_spectral_index(uniqual) << Meq.Parm(index)    
    wvl = MeqWavelength(ns)
    # NB: I have no idea where the 50 comes from....
    node = ns.Tsky_K(uniqual) << Meq.Pow(wvl, pindex) * 50
    return apply_unop(ns, unop, node)
    


#**************************************************************************************
# Leaves built on multi-dimensional funklets (dicey!) 
#**************************************************************************************

def MeqAzimuth(ns, name='MeqAzimuth', axis='x2', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

def MeqElevation(ns, name='MeqElevation', axis='x3', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

def MeqL(ns, name='MeqL', axis='x2', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

def MeqM(ns, name='MeqM', axis='x3', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

# def MeqN(ns, name='MeqN', axis='x4', ref=0.0):         # <--------------???
#     return MeqFunklet(ns, name, axis, ref=ref)

def MeqU(ns, name='MeqU', axis='x2', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

def MeqV(ns, name='MeqV', axis='x3', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

def MeqW(ns, name='MeqW', axis='x4', ref=0.0):
    return MeqFunklet(ns, name, axis, ref=ref)

# Common function (can also be used stand-alone):

def MeqFunklet(ns, name='<name>', axis='<xi>', ref=0.0):
    uniqual = _counter (name, increment=True)
    funklet = meq.polc(coeff=[1.0], subclass=meq._funklet_type)
    funklet.function = 'p0*'+axis
    if ref:                          # non-zero reference value
        funklet.function = 'p0*('+axis+'-'+str(ref)+')'
        name = '('+name+'-'+str(ref)+')'
    return ns[name](uniqual) << Meq.Parm(funklet, node_groups='Parm')




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

    cc = []

    if 1:
        cc.append(MeqFreq(ns))
        cc.append(MeqWavelength(ns))
        cc.append(MeqWavelength(ns, unop='Sqr'))
        cc.append(MeqWavelength(ns, unop=['Cos','Sqr']))
        cc.append(MeqTime(ns))
        cc.append(MeqFreqTime(ns))
        cc.append(MeqTimeFreq(ns))
        cc.append(MeqFreqTimeComplex(ns))
        cc.append(MeqTimeFreqComplex(ns))

    if 0:
        cc.append(MeqTsky(ns))

    if 0:
        cc.append(MeqFreqTime(ns, 'Subtract'))
        cc.append(MeqFreqTime(ns, 'Divide'))
        cc.append(MeqFreqTime(ns, 'Multiply'))

    if 0:
        cc.append(MeqAzimuth(ns))
        cc.append(MeqElevation(ns))

    if 0:
        ss = ['pi','pi2','2pi']
        ss.extend(['e','sqrt2', 'sqrt3'])
        ss.extend(['G_gravity','h_Planck', 'h2pi_Planck', 'e_charge'])
        ss.extend(['k_Boltzmann','k_Jy','2k_Jy'])
        for s in ss:
            func = 'const_'+s+'(ns)'
            v = eval(func)
            cc.append(v)
            print '- TDL_Leaf.'+func,' ->',v.name,v.initrec()

    if 1:
        root = ns.root << Meq.Composer(children=cc)
        MG_JEN_exec.display_subtree(root, root.name, full=True, recurse=5)
    print '\n*******************\n** End of local test of: TDL_Dipole.py:\n'



#============================================================================================









 

