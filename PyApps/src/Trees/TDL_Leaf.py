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
# from Timba.Trees import TDL_radio_conventions

#**************************************************************************************
# Constants:
#**************************************************************************************


def const_pi(ns): return MeqConstant(ns, pi, name='pi')
def const_2pi(ns): return MeqConstant(ns, 2*pi, name='2pi')
def const_pi2(ns): return MeqConstant(ns, pi/2, name='pi/2')

def const_e(ns): return MeqConstant(ns, e, name='e_ln')
def const_sqrt2(ns): return MeqConstant(ns, sqrt(2.0), name='sqrt(2)')
def const_sqrt3(ns): return MeqConstant(ns, sqrt(3.0), name='sqrt(3)')
def const_sqrt5(ns): return MeqConstant(ns, sqrt(5.0), name='sqrt(5)')

def const_c_light(ns): return MeqConstant(ns, 2.9979250e8, name='c_light_m/s')
def const_e_charge(ns): return MeqConstant(ns, 1.6021917e-19, name='e_charge_C')

h_Planck =  6.626196e-34
def const_h_Planck(ns): return MeqConstant(ns, h_Planck, name='h_Planck_Js')
def const_h2pi_Planck(ns): return MeqConstant(ns, h_Planck/(2*pi), name='h_Planck_Js/2pi')

k_Boltzmann = 1.380622e-23
def const_k_Boltzmann(ns): return MeqConstant(ns, k_Boltzmann, name='k_Boltzmann_J/K')
def const_k_Jy(ns): return MeqConstant(ns, k_Boltzmann/1e-26, name='k_Jy/K')
def const_2k_Jy(ns): return MeqConstant(ns, 2*k_Boltzmann/1e-26, name='2k_Jy/HzK')
def const_G_gravity(ns): return MeqConstant(ns, 6.6732e-11, name='G_gravity_Nm2/kg2')

#---------------------------------------------------------------------------------------

def str2num (value):
    """Helper function to convert a string value to numeric"""
    if isinstance(value, str):
        if value=='pi': value = pi
        if value=='2pi': value = 2*pi
        if value=='e': value = e
        if value=='c': value = 2.9979250e8
        if value=='k': value = 1.380622e-23
        if value=='G': value = 6.6732e-11
        if value=='h': value = 6.626196e-34
    if isinstance(value, str):
        value = eval(str)
    return value

#---------------------------------------------------------------------------------------

def MeqConstant(ns, value=-1.23456789,
                name=None, qual='uniqual',
                binop=None, rhs=None,
                unop=None):
    """Make a MeqConstant node, with some services"""

    # Prepare:
    str_val = str(value)
    str_rhs = str(rhs)
    if name==None: name = str_val
    if isinstance(value, str): value = str2num(value)

    # Optional: apply a binary operation:
    if isinstance(binop, str):
        rhs = str2num (rhs)
        if binop=='+': value += rhs
        if binop=='-': value -= rhs
        if binop=='*': value *= rhs
        if binop=='/': value /= rhs
        if binop=='^': value ^= rhs
        name += binop+str_rhs
        if unop==None: name = '('+name+')'

    # Optional: apply one or more unary operations:
    if not unop==None:
        if not isinstance(unop, (list, tuple)): unop = [unop]
        for unop1 in unop:
            unop1 = unop1.lower()
            try:
                seval = unop1+'('+str(value)+')'
                value = eval(seval)
            except:
                print '\n**',seval,'\n  ',sys.exc_info(),'\n'
                return seval
            name = unop1+'('+name+')'

    # Make the node:
    if qual==None:
        node = ns[name] << Meq.Constant(value)
    elif isinstance(qual, dict):
        node = ns[name](**qual) << Meq.Constant(value)
    elif qual=='uniqual':
        uniqual = _counter (name, increment=True)
        node = ns[name](uniqual) << Meq.Constant(value)
    else:
        node = ns[name](qual) << Meq.Constant(value)
    return node


#**************************************************************************************
# Leaves built on regular nodes (e.g. MeqFreq):
#**************************************************************************************


def apply_unop(ns, node=None, unop=None):
    """Helper function to apply (optional) unary operation(s) to node"""
    if unop==None: return node
    if not isinstance(unop, (list, tuple)): unop = [unop]
    for unop1 in unop:
        node = ns << getattr(Meq,unop1)(node)
    return node

def apply_unop_to_constant(ns, value=None, unop=None):
    """Helper function to apply (optional) unary operation(s) to a constant"""
    if unop==None: return node
    if not isinstance(unop, (list, tuple)): unop = [unop]
    for unop1 in unop:
        node = ns << getattr(Meq,unop1)(node)
    return node

def apply_binop(ns, node=None, binop=None, rhs=None):
    """Helper function to apply (optional) binary operation to node:
    result = node binop rhs (right-hand-side)"""
    if rhs==None: return node
    if not isinstance(binop, str): return node
    if binop=='+': binop = 'Add'
    if binop=='-': binop = 'Subtract'
    if binop=='*': binop = 'Multiply'
    if binop=='/': binop = 'Divide'
    if binop=='^': binop = 'Pow'
    node = ns << getattr(Meq,binop)(node,rhs)
    return node

def shift_mean(ns, node=None, mean=0.0):
    """Helper function to shift the mean to the given value"""
    oldmean = ns << Meq.Mean(node)
    node = ns << Meq.Subtract(node, oldmean)
    if mean: node = ns << Meq.Add(node, mean)
    return node

def normalise(ns, node=None, interval=[0.0,1.0]):
    """Helper function to normalise the node on the given range"""
    if not isinstance(interval, (list, tuple)): return node
    if not len(interval)==2: return node
    vmin = ns << Meq.Min(node)
    vmax = ns << Meq.Max(node)
    dv = ns << Meq.Subtract(vmax,vmin)
    node = ns << Meq.Subtract(node, vmin)
    dr = interval[1] - interval[0]
    factor = ns << Meq.Divide(dr, dv)
    node = ns << Meq.Multiply(node, factor)
    if interval[0]==0:
        node = ns << Meq.Add(node, vmin)
    else:
        node = ns << Meq.Add(node, vmin, interval[0])
    return node

def post_process(ns, node=None, **pp):
    """Helper function to post-process the given node"""
    pp.setdefault('unop', None)
    pp.setdefault('mean', None)
    pp.setdefault('normalise', None)
    if not pp['mean']==None:
        node = shift_mean(ns, node, pp['mean'])
    if pp['unop']:
        node = apply_unop(ns, node, pp['unop'])
    if pp['normalise']:
        node = normalise(ns, node, pp['normalise'])
    return node

#-----------------------------------------------------------------------------

def MeqFreq(ns, name='MeqFreq', **pp):
    """Make a MeqFreq node with optional post-processing"""
    uniqual = _counter (name, increment=True)
    node = ns[name](uniqual) << Meq.Freq()
    return post_process(ns, node, **pp)

def MeqWavelength(ns, name='MeqWavelength', **pp):
    """Make a wavelength node with optional post-processing"""
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)                          # Hz
    node = ns[name](uniqual) << Meq.Divide(const_c_light(ns), freq)
    return post_process(ns, node, **pp)

def MeqInverseWavelength(ns, name='MeqInverseWavelength', **pp):
    """Make 1/wavelength node with optional post-processing"""
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)                          # Hz
    node = ns[name](uniqual) << Meq.Divide(freq, const_c_light(ns))
    return post_process(ns, node, **pp)

def MeqTime(ns, name='MeqTime', **pp):
    """Make a MeqTime node with optional post-processing"""
    uniqual = _counter (name, increment=True)
    node = ns[name](uniqual) << Meq.Time()
    return post_process(ns, node, **pp)

def MeqFreqTimeComplex(ns, name='MeqFreqTime', **pp):
    """Make a complex node that depends on time and freq,
    with optional post-processing"""
    return MeqFreqTime(ns, combine='ToComplex', name=name, **pp)

def MeqTimeFreqComplex(ns, name='MeqTimeFreq', **pp):
    """Make a complex node that depends on freq and time,
    with optional post-processing"""
    return MeqTimeFreq(ns, combine='ToComplex', name=name, **pp)

def MeqFreqTime(ns, combine='Add', name='MeqFreqTime', **pp):
    """Make a real node that depends on freq and time,
    with optional post-processing"""
    name += '_'+combine                         # -> MeqFreqTime_Add
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)
    time = MeqTime(ns)
    node = ns[name](uniqual) << getattr(Meq,combine)(children=[freq, time])
    return post_process(ns, node, **pp)

def MeqTimeFreq(ns, combine='Add', name='MeqTimeFreq', **pp):
    """Make a real node that depends on time and freq,
    with optional post-processing"""
    name += '_'+combine                         # -> MeqTimeFreq_Add
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)
    time = MeqTime(ns)
    node = ns[name](uniqual) << getattr(Meq,combine)(children=[time, freq])
    return post_process(ns, node, **pp)

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
    return apply_unop(ns, node, unop)
    


#**************************************************************************************
# Leaves built on multi-dimensional funklets (dicey!) 
#**************************************************************************************

def MeqAzimuth(ns, name='MeqAzimuth', qual=None, axis='x2', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

def MeqElevation(ns, name='MeqElevation', qual=None, axis='x3', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

def MeqL(ns, name='MeqLcoord', qual=None, axis='x2', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

def MeqM(ns, name='MeqMcoord', qual=None, axis='x3', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

# def MeqN(ns, name='MeqNcoord', qual=None, axis='x4', ref=0.0):         # <--------------???
#     return MeqFunklet(ns, name, qual, axis, ref=ref)

def MeqU(ns, name='MeqUcoord', qual=None, axis='x2', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

def MeqV(ns, name='MeqVcoord', qual=None, axis='x3', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

def MeqW(ns, name='MeqWcoord', qual=None, axis='x4', ref=0.0):
    return MeqFunklet(ns, name, qual, axis, ref=ref)

# Common function (can also be used stand-alone):

def MeqFunklet(ns, name='<name>', qual=None, axis='<xi>', ref=0.0):
    uniqual = _counter (name, increment=True)
    funklet = meq.polc(coeff=[1.0], subclass=meq._funklet_type)
    funklet.function = 'p0*'+axis
    if ref:                          # non-zero reference value
        funklet.function = 'p0*('+axis+'-'+str(ref)+')'
        name = '('+name+'-'+str(ref)+')'
    node = _unique_node (ns, name, qual)
    node << Meq.Parm(funklet, node_groups='Parm')
    return node



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


#--------------------------------------------------------------------------

def _unique_node (ns, name, qual=None, trace=False):
    """Helper function to generate a unique node-name"""

    # First try without extra qualifier:
    if isinstance(qual, dict):
        node = ns[name](**qual)
    elif qual==None:
        node = ns[name]
    else:
        node = ns[name](qual)

    if not node.initialized():
        # OK, does not exist yet
        if trace: print '\n** _unique_node(',name,qual,') ->',node
        return node

    # Add an extra qualifier to make the nodename unique:
    uniqual = _counter (name, increment=-1)
    if isinstance(qual, dict):
        node = ns[name](**qual)(uniqual)
    elif qual==None:
        node = ns[name](uniqual)
    else:
        node = ns[name](qual)(uniqual)
    if trace: print '\n** _unique_node(',name,qual,') ->',node
    return node

#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: TDL_Dipole.py:\n'
    from Timba.Contrib.JEN import MG_JEN_exec
    ns = NodeScope()

    cc = []

    if 0:
        cc.append(MeqFreq(ns))
        cc.append(MeqWavelength(ns))
        cc.append(MeqWavelength(ns, unop='Sqr'))
        cc.append(MeqWavelength(ns, unop=['Cos','Sqr']))
        cc.append(MeqTime(ns))
        cc.append(MeqFreqTime(ns, mean=0.0, unop='Cos'))
        cc.append(MeqTimeFreq(ns, normalise=[-1,1]))
        cc.append(MeqFreqTimeComplex(ns))
        cc.append(MeqTimeFreqComplex(ns))

    if 0:
        cc.append(MeqTsky(ns))

    if 0:
        cc.append(MeqFreqTime(ns, 'Subtract'))
        cc.append(MeqFreqTime(ns, 'Divide'))
        cc.append(MeqFreqTime(ns, 'Multiply'))

    if 1:
        qual = None
        qual = dict(q='3c84')
        cc.append(MeqAzimuth(ns, qual=qual))
        cc.append(MeqElevation(ns, qual=qual))
        cc.append(MeqL(ns, qual=qual))
        cc.append(MeqM(ns, qual=qual))

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

    if 0:
        node = MeqTime(ns)
        cc.append(apply_binop(ns, node, 'Add', 3))
        cc.append(apply_binop(ns, node, 'Subtract', 3))
        cc.append(apply_binop(ns, node, 'Multiply', 3))
        cc.append(apply_binop(ns, node, 'Divide', 3))
        cc.append(apply_binop(ns, node, 'Pow', 3))
        cc.append(apply_binop(ns, node, '+', 3))
        cc.append(apply_binop(ns, node, '-', 3))
        cc.append(apply_binop(ns, node, '*', 3))
        cc.append(apply_binop(ns, node, '/', 3))
        cc.append(apply_binop(ns, node, '^', 3))

    if 0:
        cc.append(MeqConstant(ns, 'pi', binop='+', rhs=3))
        cc.append(MeqConstant(ns, 'pi', binop='/', rhs=2.5, unop=['Cos','Sin']))
        cc.append(MeqConstant(ns, 'pi', binop='/', rhs='pi'))
        cc.append(MeqConstant(ns, 'pi', binop='/', rhs='pi'))

    if 1:
        root = ns.root << Meq.Composer(children=cc)
        MG_JEN_exec.display_subtree(root, root.name, full=True, recurse=5)
    print '\n*******************\n** End of local test of: TDL_Dipole.py:\n'



#============================================================================================









 

