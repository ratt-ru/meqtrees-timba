# TDL_Dipole.py
#
# Author: J.E.Noordam
#
# Short description:
#    Predefined MeqTree end-points (leaves) 
#
# History:
#    - 19 oct 2005: creation
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
# from Timba.Trees import TDL_radio_conventions



#**************************************************************************************
# Leaves built on regular nodes (e.g. MeqFreq):
#**************************************************************************************


def MeqFreq(ns, name='MeqFreq'):
    uniqual = _counter (name, increment=True)
    return ns[name](uniqual) << Meq.Freq()

def MeqWavelength(ns, name='MeqWavelength'):
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)                          # Hz
    clight = 2.9979250e8                        # m/s
    return ns[name](uniqual) << Meq.Divide(clight, freq)

def MeqTime(ns, name='MeqTime'):
    uniqual = _counter (name, increment=True)
    return ns[name](uniqual) << Meq.Time()

def MeqFreqTimeComplex(ns, name='MeqFreqTime'):
    return MeqFreqTime(ns, combine='ToComplex', name=name)

def MeqTimeFreqComplex(ns, name='MeqTimeFreq'):
    return MeqTimeFreq(ns, combine='ToComplex', name=name)

def MeqFreqTime(ns, combine='Add', name='MeqFreqTime'):
    name += '_'+combine                         # -> MeqFreqTime_Add
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)
    time = MeqTime(ns)
    return ns[name](uniqual) << getattr(Meq,combine)(children=[freq, time])

def MeqTimeFreq(ns, combine='Add', name='MeqTimeFreq'):
    name += '_'+combine                         # -> MeqTimeFreq_Add
    uniqual = _counter (name, increment=True)
    freq = MeqFreq(ns)
    time = MeqTime(ns)
    return ns[name](uniqual) << getattr(Meq,combine)(children=[time, freq])



#**************************************************************************************
# Leaves built on multi-dimensional funklets (dicey!) 
#**************************************************************************************

def MeqAzimuth(ns, name='MeqAzimuth'):
    uniqual = _counter (name, increment=True)
    funklet = meq.polc(coeff=1.0, subclass=meq._funklet_type)
    funklet.function = 'x2'
    return ns[name](uniqual) << Meq.Parm(funklet, node_groups='Parm')

def MeqElevation(ns, name='MeqElevation'):
    uniqual = _counter (name, increment=True)
    funklet = meq.polc(coeff=1.0, subclass=meq._funklet_type)
    funklet.function = 'x3'
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
        cc.append(MeqTime(ns))
        cc.append(MeqFreqTime(ns))
        cc.append(MeqTimeFreq(ns))
        cc.append(MeqFreqTimeComplex(ns))
        cc.append(MeqTimeFreqComplex(ns))

    if 1:
        cc.append(MeqFreqTime(ns, 'Subtract'))
        cc.append(MeqFreqTime(ns, 'Divide'))
        cc.append(MeqFreqTime(ns, 'Multiply'))

    if 1:
        cc.append(MeqAzimuth(ns))
        cc.append(MeqElevation(ns))

    if 1:
        for node in cc:
            MG_JEN_exec.display_subtree(node, node.name, full=True, recurse=5)
    print '\n*******************\n** End of local test of: TDL_Dipole.py:\n'



#============================================================================================









 

