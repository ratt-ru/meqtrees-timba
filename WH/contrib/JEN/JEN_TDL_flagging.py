# ../Timba/WH/contrib/JEN/JEN_TDL_flagging.py:  
#   Functions that deal with data-flagging subtrees

print '\n',100*'*'
print '** JEN_TDL_flagging.py    h09aug2005'

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
from copy import deepcopy

from JEN_util_TDL import *
from JEN_util import *
# Better: put the JEN stuff in a sub-directory....
# from JEN.JEN_util_TDL import *
# from JEN.JEN_util import *




#======================================================================================
# Generic flagger subtree:
#======================================================================================


def JEN_flagger (ns, input, **pp):
    """insert one or more flaggers for the input data"""

    # Deal with input parameters (pp):
    pp = record(JEN_pp (pp, 'JEN_TDL_flagging::flagger(ns, input, **pp)',
                        _help=dict(sigma='flagging threshold',
                                   unop='data-operation(s) before flagging (e.g. Abs, Arg, Real, Imag)',
                                   oper='do flag if OPER zero',
                                   flag_bit='flag_bit to be affected',
                                   merge='if True, merge the flags of tensor input',),
                        sigma=5.0, unop='Abs', oper='GT',
                        flag_bit=1, merge=True))
    if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

    # Work on a stripped version, without derivatives, to save memory:
    stripped = ns.stripped << Meq.Stripper(input)

    # Make one or more flaggers for the various unops:
    if not isinstance(pp.unop, (list, tuple)): pp.unop = [pp.unop]
    zz = []
    for unop in pp.unop:
      # Work on real numbers (unop = Abs, Arg, Imag, Real)
      real = ns.real(unop) << getattr(Meq,unop)(stripped)
      # Make the subtree that calculates the zero-condition (zcond):
      mean = ns.mean(unop) << Meq.Mean(real)
      stddev = ns.stddev(unop) << Meq.StdDev(real)
      diff = ns.diff(unop) << (input - mean)
      absdiff = ns.absdiff(unop) << Meq.Abs(diff)
      sigma = ns.sigma(unop) << Meq.Constant(pp.sigma)
      threshold = ns.threshold(unop) << (stddev * sigma)
      zcond = ns.zcond(unop) << (absdiff - threshold)
      zz.append(zcond)

    # Flag the cells whose zcond values are 'oper' zero (e.g. oper=GT)
    # NB: Assume that ZeroFlagger can have multiple children
    zflag = ns.zflag << Meq.ZeroFlagger(children=zz,
                                        oper=pp.oper, flag_bit=pp.flag_bit)

    # The new flags are merged with those of the input node:
    output = ns.mflag << Meq.MergeFlags(children=[input,zflag])

    # Optional: merge the flags of multiple tensor elements of input/output:
    if pp.merge: output = ns.Mflag << Meq.MergeFlags(output)

    # Finished:
    if pp.trace: JEN_display_subtree(output, 'JEN_flagger()', full=1)

    return output




#======================================================================================
# Make an input node that varies with freq and time:
#======================================================================================

def JEN_freqtime (ns, **pp):
    """Make an input node that varies with freq and time:"""

    # Deal with input parameters (pp):
    pp = record(JEN_pp (pp, 'JEN_TDL_flagging::freqtime(ns, **pp)',
                        _help=dict(combine='time/freq combination mode',
                                   unop='optional output data-operation',),
                        combine='Add', unop=False))
    if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

    # Make the basic freq-time node by combining (e.g. adding) MeqFreq and MeqTime:
    freq = ns << Meq.Freq()
    time = ns << Meq.Time()
    output = ns.freqtime << getattr(Meq,pp.combine)(children=[freq, time])

    # Optional: Apply zero or more unary operations on the output:
    output = JEN_apply_unop (ns, pp.unop, output) 

    # Finished:
    if pp.trace:
      JEN_display_subtree(output, 'JEN_freqtime()', full=1)

    return output



#======================================================================================
# Make a (tensor) node of with gaussian noise:
#======================================================================================

def JEN_gaussnoise (ns, **pp):
    """makes gaussian noise"""

    # Deal with input parameters (pp):
    pp = record(JEN_pp (pp, 'JEN_TDL_flagging::gaussnoise(ns, **pp)',
                        _help=dict(dims='dimensions of the output tensor node',
                                   stddev='stddev value of the noise',
                                   complex='if True, generate complex noise',
                                   mean='mean value of the noise',
                                   unop='optional output data-operation',),
                        dims=[1], mean=0, stddev=1,
                        complex=False, unop=False))
    if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

    # Determine the nr (nel) of tensor elements:
    if not isinstance(pp.dims, (list, tuple)): pp.dims = [pp.dims]
    nel = sum(pp.dims)
    # print 'nel =',nel

    # NB: What about making/giving stddev as a MeqParm...?

    # The various tensor elements have different noise, of course:
    # NB: Is this strictly necessary? A single GaussNoise node would
    #     be requested separately by each tensor element, and produce
    #     a separate set of values (would it, for the same request..........?)
    #     So a single GaussNoise would be sufficient (for all ifrs!)
    #     provided they would have the same pp.stddev
    cc = []
    for i in range(nel):
      if pp.complex:
        real = ns.real(i) << Meq.GaussNoise(stddev=pp.stddev)
        imag = ns.imag(i) << Meq.GaussNoise(stddev=pp.stddev)
        cc.append (ns.gaussnoise(i) << Meq.ToComplex(children=[real, imag]))
      else:
        cc.append (ns.gaussnoise(i) << Meq.GaussNoise(stddev=pp.stddev))

    # Make into a tensor node, if necessary:
    output = cc[0]
    if nel>1: output = ns.gaussnoise << Meq.Composer(children=cc, dims=pp.dims)

    # Optional: Add the specified mean:
    if abs(pp.mean)>0:
      if not pp.complex and isinstance(pp.mean, complex): pp.mean = pp.mean.real
      output = output + pp.mean

    # Optional: Apply zero or more unary operations on the output (e.g Exp):
    output = JEN_apply_unop (ns, pp.unop, output) 

    # Finished:
    if pp.trace:
      JEN_display_subtree(output, 'JEN_gaussnoise()', full=1)

    return output



#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  ns = NodeScope()

  if 0:
    xxx = ns.xxx(s1=2, s2=5)('3c84') << -1
    print 'xxx =',xxx
    print 'xxx.quals =',xxx.quals
    print 'xxx.kwquals =',xxx.kwquals
    nsub = ns.Subscope('sub', *xxx.quals, **xxx.kwquals)
    node = nsub << -1
    print node
    nsubsub = nsub.Subscope('subsub')
    node = nsubsub << -1
    print node

  if 1:
    input = ns.input(a=1,b=2)('c') << Meq.Constant([0,1,2,3])
    nsub = ns.Subscope('flagger', s1=2, s2=3)
    print JEN_flagger(nsub, input, unop=['Abs','Arg'], trace=1)

  if 0:
    nsub = ns.Subscope('freqtime', s1=2, s2=3)
    print JEN_freqtime(nsub, unop='Cos', trace=1)

  if 0:
    aa = array([[1,2,3],[4,5,6]])
    print dir(aa)
    print 'len(aa) =',len(aa)
    print 'sum(aa) =',sum(aa)
    print 'aa.sum() =',aa.sum()
    print 'aa.flat =',aa.flat,' len =',len(aa.flat)

  if 0:
    nsub = ns.Subscope('gaussnoise', s1=2, s2=3)
    print JEN_gaussnoise(nsub, dims=[2,2], complex=True, mean=complex(1,2), unop='Exp', trace=1)

  if 0:
    JEN_display_NodeScope(ns, 'test')

