# Polynomial.py
#
# Author: J.E.Noordam
# 
# Short description:
#   The Polynomial classes are specialisations of the class Expression
#
# History:
#    - 05may2007: creation, from Expression.py
#
# Remarks:
#
# Description:
#




#***************************************************************************************
# Preamble
#***************************************************************************************

from Timba.Meq import meq
from Timba.TDL import *                         # needed for type Funklet....

import Meow
#
from Timba.Contrib.JEN.util import Expression
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Grunt import display

Settings.forest_state.cache_policy = 100

from numarray import *
# import random
from copy import deepcopy


# from Timba.Contrib.MXM.TDL_Funklet import *   # needed for type Funklet.... 
# from Timba.Contrib.MXM import TDL_Funklet


# Replacement for is_numeric(): if isinstance(x, NUMMERIC_TYPES):
NUMERIC_TYPES = (int, long, float, complex)


#***************************************************************************************
#***************************************************************************************

class Polynomial (Expression.Expression):
    """Represents a ND polynomial Expression.
    It must be specified by means of a list of dimensions, e.g. ['f^2','t^3'].
    Each item specified the variable of a dimension, and the rank in that dim."""

    def __init__(self, ns, name, 
                 dims=['t^2','f^3'], symbol='c',
                 exclude_triangle=True,
                 descr=None, unit=None,
                 quals=[], kwquals={}):

        self._dims = dims
        self._symbol = symbol
        self._exclude_triangle = exclude_triangle

        expr = self._makexpr (dims, symbol,
                              exclude_triangle=exclude_triangle,
                              trace=True)
        
        Expression.Expression.__init__(self, ns, name, expr=expr,
                                       descr=descr, unit=unit,
                                       quals=quals, kwquals=kwquals)

        # Finished:
        return None


    #----------------------------------------------------------------------------
    # Some display functions:
    #----------------------------------------------------------------------------

    def oneliner(self, full=True):
        """Return a one-line summary of the Expression"""
        ss = '** Polynomial ('+str(self.name)+'):  '
        ss += '  dims='+str(self._dims)
        if self._unit: ss += '('+str(self._unit)+') '
        if self._descr:
            ss += str(self._descr)
        return ss


    #=============================================================================
    # Functions that generate the polynomial expression:
    #=============================================================================

    def _makexpr (self, dims=['t^2','f^3'], symbol='c',
                  exclude_triangle=True, trace=False):
        """Make the ND polynomial expression.""" 
        if trace: print '\n** _multex(',dims,symbol,'):'
        self._vv = []
        terms = []
        isumax = 0
        for dim in dims:
            dd = dim.split('^')
            isumax = max(isumax,int(dd[1]))
            if int(dd[1])>0:
                terms = self._maketerms(terms, dim=dim, trace=trace)
        if isumax==1: isumax += 1

        expr = None
        for k,term in enumerate(terms):
            tt = term.split('_')
            isum = 0
            for c in tt[0]:
                isum += int(c)
            if tt[1]=='':
                s = '{'+symbol+tt[0]+'}'
            else:
                s = '{'+symbol+tt[0]+'}*'+tt[1]
            if trace: print '-',isum,'/',isumax,':',s,
            if exclude_triangle and isum>isumax:
                if trace: print ' (ignored)',
                pass                       # ignore the highest order triangle
            elif not expr:
                expr = s                   # first term
            else:
                expr += ' + '+s            # other terms
            if trace: print

        if expr==None: expr = '{'+symbol+'}'
        return expr

    #----------------------------------------------------------------------------

    def _maketerms (self, terms=[], dim='f3', trace=True):
        """Helper function to replace the given list of terms
        with new terms that include the specified dimension."""
        new = []
        dd = dim.split('^')
        vs = dd[0]+'^'
        n = int(dd[1])+1
        if trace: print '\n** _multex(',len(terms),dim,'):'

        if len(terms)==0:                                   # first dimension
            for i in range(n):
                if i==0:
                    s = str(i)+'_'
                else:
                    v = vs+str(i)
                    if i==1: v = dd[0]                      # t^1 = t
                    s = str(i)+'_['+v+']'
                    if not v in self._vv:
                        self._vv.append(v)
                if trace: print '-',i,':',s
                new.append(s)

        else:                                               # later dimension
            for k,term in enumerate(terms): 
                for i in range(n):
                    tt = term.split('_')
                    v = None                             
                    if i==0:                                    # ignore t^0
                        s = tt[0]+str(i)+'_'+tt[1]
                    elif tt[1]=='':
                        v = vs+str(i)                           # e.g. t^i
                        if i==1: v = dd[0]                      # t^1 = t
                        s = tt[0]+str(i)+'_['+v+']'
                    else:
                        v = vs+str(i)                           # e.g. t^i
                        if i==1: v = dd[0]                      # t^1 = t
                        s = tt[0]+str(i)+'_'+tt[1]+'*['+v+']'
                    if v and not v in self._vv:
                        self._vv.append(v)
                    if trace: print '-',k,i,':',s
                    new.append(s)

        # Finished:
        print '** len(new)=',len(new),'\n'
        return new






#=============================================================================
#=============================================================================
#=============================================================================


def polc_Expression(shape=[1,1], coeff=None, name='pE', unit=None,
                    ignore_triangle=True,
                    nonzero_default=True, stddev=0.1,
                    type='MeqPolc', f0=1e6, t0=1.0,
                    fit=None, plot=False, trace=False):
    """Create an Expression object for a polc with the given shape (and type).
    Parameters can be initialized by specifying a list of coeff.
    The coeff will be assumed 0 for all those missing in the list.
    If type==MeqPolcLog, the variables [t] and/or [f] are replaced by
    Expression parameters {tvar}= log([t]/{t0}) and {fvar}=log([f]/{f0}),
    with the constants t0 and f0 given by input arguments.
    Optionally, the polc coeff may be determined by fitting to a given
    set of polc function values vv(t,f): fit=dict(vv=, tt=, ff=)."""

    if trace:
        print '\n** polc_Expression(',shape,coeff,name,type,'):'
        if fit: print '       fit =',fit
    if coeff==None: coeff = []
    if not isinstance(coeff, (list,tuple)): coeff = [coeff]
    coeff = array(coeff).flat
    if len(shape)==1: shape.append(1)
    if shape[0]==0: shape[0] = 1
    if shape[1]==0: shape[1] = 1
    if name==None: name = 'polc'+str(shape[0])+str(shape[1])

    # Whereas the MeqPolc just has variables ([f],[t]),
    # the MeqPolcLog has parameters that are Expressions:
    fvar = '[f]'
    tvar = '[t]'
    if type=='MeqPolcLog':
        fvar = '{logf}'
        tvar = '{logt}'

    func = ""
    k = -1
    pp = dict()
    testinc = dict()
    help = dict()
    sunit = ''
    if isinstance(unit, str): sunit = unit
    uunit = dict()
    first = True
    tdep = False
    fdep = False
    include = True
    sign = -1
    ijmax = max(shape[0],shape[1])
    for i in range(shape[1]):
        if i>0: fdep = True                          # depends on freq
        for j in range(shape[0]):
            if j>0: fdep = True                      # depends on time
            if ignore_triangle:                      # optional:
                if (i+j)>=ijmax: include = False     # ignore higher-order cross-terms
            if include:                              # include this term
                k += 1
                sign *= -1
                pk = 'c'+str(j)+str(i)                   # e.g. c01
                testinc[pk] = sign*(10**(-i-j))          # test-increment 
                pp[pk] = 0.0                             # default value = 0
                if nonzero_default:
                    pp[pk] = testinc[pk]                 # non-zero default value ....
                if len(coeff)>k:                         # explicitly specified
                    pp[pk] = coeff[k]                    # override
                help[pk] = name+'_'+str(j)+str(i)
                uunit[pk] = sunit
                if not first: func += '+'
                func += '{'+pk+'}'                       # {c01}
                for i2 in range(j):
                    func += '*'+tvar                     # e.g:  *[t] or *{logt}
                    uunit[pk] += '/s'
                for i1 in range(i):
                    func += '*'+fvar                     # e.g:  *[f] or *{logf}
                    uunit[pk] += '/Hz'
                first = False
                if trace: print '-',i,j,' (',i+j,ijmax,') ',k,pk,':',func
    result = Expression(ns, name, func,
                        descr='polc_Expression')
    result._expression_type = type

    # Define the Expression parms:
    for key in pp.keys():
        result.parm('{'+key+'}', pp[key], unit=uunit[key])

    # Define the Expression 'variable' parms, if necessary:
    if type=='MeqPolcLog':
        if fdep:
            logf = Expression('log([f]/{f0})', name='fvar')
            logf.parm('f0', f0)
            logf.var('f', 1.e8, testinc=0.5*1e7)  
            result.parm('logf', logf)
        if tdep:
            logf = Expression('log([t]/{t0})', name='tvar')
            logf.parm('t0', t0)
            result.parm('logt', logt)

    # Optionally, fit the new polc to a given set of values(f,t):
    if isinstance(fit, dict):
        result.fit(**fit)

    # insert help......?

    # Finished: return the polc Expression:
    if trace: result.display()
    if plot: result.plot(_plot='loglog')
    return result




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = [ns.dummy<<45]

    dims = ['t^3']
    dims = ['t^4','f^4']
    # dims = ['t^1','mm^2']
    dims = ['t^1','f^2','l^2','m^3']                    # ND plotter sees NaN's that are not there
    # dims = ['t^1','f^2','m^3']                        # crashes when executed...
    p0 = Polynomial(ns, 'p0', dims=dims, symbol='w')
    p0.display('initial')

    if 0:
        c1 = p0.MeqNode(show=True)
        c2 = p0.MeqFunctional(show=True)
        cc.append(ns.diff << Meq.Subtract(c1,c2)) 

    if 1:
        c = p0.MeqCompounder()
        cc.append(c)
        JEN_bookmarks.create(c, page='compounder', recurse=1)

    if 0:
        #----------------------------------------------------------
        # Compare the FunkletParm en MeqFunctional solutions
        #----------------------------------------------------------
        reqseq = []
        sincos = ns.sincos << Meq.Multiply(ns<<Meq.Sin(ns<<Meq.Time),
                                           ns<<Meq.Cos(ns<<Meq.Freq))
        JEN_bookmarks.create(sincos, page='condeqs')

        if 1:
            c2 = p0.FunkletParm(show=True) 
            p0.display('after p0.FunkletParm()')
            solvable = p0.solvable(trace=True)
            condeq2 = ns.condeq_FunkletParm << Meq.Condeq(sincos,c2)
            solver2 = ns.solver_FunkletParm << Meq.Solver(condeq2,
                                                          num_iter=10,
                                                          solvable=solvable)
            reqseq.append(solver2)
            JEN_bookmarks.create(c2, page='solvers')
            JEN_bookmarks.create(solver2, page='solvers')
            JEN_bookmarks.create(condeq2, page='condeqs')

        if 1:
            c1 = p0.MeqFunctional(show=True) 
            p0.display('after p0.MeqFunctional()')
            solvable = p0.solvable(trace=True)
            condeq1 = ns.condeq_Functional << Meq.Condeq(sincos,c1)
            solver1 = ns.solver_Functional << Meq.Solver(condeq1,
                                                         num_iter=10,
                                                         solvable=solvable)
            reqseq.append(solver1)
            JEN_bookmarks.create(c1, page='solvers')
            JEN_bookmarks.create(condeq1, page='condeqs')
            JEN_bookmarks.create(solver1, page='solvers')


        if 1:
            cdiff = ns.cdiff << Meq.Subtract(condeq1,condeq2) 
            reqseq.append(cdiff)
            JEN_bookmarks.create(cdiff, page='condeqs')

        cc.append(ns.solver_reqseq << Meq.ReqSeq(children=reqseq))
        #----------------------------------------------------------


    # p0.display('final')
    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1,5,0,5)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

def _tdl_job_4D_tflm (mqs, parent):
    """Execute the forest with a 4D request (freq,time,l,m).
    NB: This does NOT work on a Compounder node!"""
    domain = meq.gen_domain(time=(0.0,1.0),freq=(1,10),l=(-0.1,0.1),m=(-0.1,0.1))
    cells = meq.gen_cells(domain=domain, num_time=4, num_freq=5, num_l=6, num_m=7)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       





#========================================================================
# Test routine (without meqbrowser):
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Expression.py:\n'
    ns = NodeScope()

    dims = ['t^3']
    dims = ['dt^1','ff^1']
    # dims = ['t^1','mm^2']
    dims = ['dt^1','f^2','m^3']
    p0 = Polynomial(ns, 'p0', dims=dims, symbol='w')
    p0.display('initial')

    if 0:
        p0.MeqNode(show=True)
        p0.solvable(trace=True)
    if 0:
        p0.FunkletParm(show=True)
        p0.solvable(trace=True)
    if 0:
        p0.MeqFunctional(show=True)
        p0.solvable(trace=True)
        if 0:
            p0.MeqNode(show=True)
            p0.solvable(trace=True)

    if 1:
        p0.MeqCompounder(show=True)
        # p0.solvable(trace=True)

    p0.display('final')

    print '\n*******************\n** End of local test of: Expression.py:\n'




#============================================================================================

    
