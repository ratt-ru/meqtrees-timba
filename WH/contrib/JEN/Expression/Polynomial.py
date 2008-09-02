# Polynomial.py
#
# Author: J.E.Noordam
# 
# Short description:
#   The Polynomial classes are specialisations of the class Expression
#
# History:
#    - 05may2007: creation, from Expression.py
#    - 02sep2008: removed numarray
#
# Remarks:
#
# Description:
#




#***************************************************************************************
# Preamble
#***************************************************************************************

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

from Timba.Meq import meq
from Timba.TDL import *                         # needed for type Funklet....

import Meow
#
from Timba.Contrib.JEN.Expression import Expression
from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.Grunt import display

Settings.forest_state.cache_policy = 100

# import SciPy                                    # not supported yet
linear_algebra = False  
# linear_algebra = True  
# try:
#     import SciPy.linear_algebra                 # redefines scipy.rank....
# except:
#     linear_algebra = False
    
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
                 polc=None, simul=False,
                 subexpr=dict(),
                 fiduc=dict(),
                 exclude_triangle=True,
                 descr=None, unit=None,
                 quals=[], kwquals={},
                 **pp):

        # The polynomial may also be specified in 'polc'-form:
        self._polc = polc
        if isinstance(polc, (list,tuple)):         # assume [tdeg,fdeg], one-relative
            dims = ['t^'+str(polc[0]-1), 'f^'+str(polc[1]-1)]

        self._dims = dims
        self._symbol = symbol
        self._exclude_triangle = exclude_triangle

        self._check_subexpr(subexpr)
        self._check_fiduc(fiduc)

        expr = self._makexpr (self._dims, symbol,
                              exclude_triangle=exclude_triangle,
                              trace=True)
        
        Expression.Expression.__init__(self, ns, name, expr=expr,
                                       descr=descr, unit=unit,
                                       quals=quals, kwquals=kwquals,
                                       typename='Polynomial',
                                       simul=simul,
                                       **pp)

        # Fill in the parameter sub-expressions collected in ._makexpr()
        # self.display('intermediate')
        # print '\n** modparm subexpr:'
        for key in self._subexpr.keys():
            if key in expr:
                # print '-',key,':',self._subexpr[key]
                self.modparm(key, self._subexpr[key],
                             redefine=True, unlock=True)
        # print

        # Finished:
        return None

    #----------------------------------------------------------------------------

    def _check_fiduc(self, fiduc):
        """Helper function to set and check self._fiduc.
        Called from __init__() only."""
        self._fiduc = fiduc
        if not isinstance(self._fiduc,(list,tuple)):
            self._fiduc = []
        # Make sure that all variable names are enclosed []:
        for k,rr in enumerate(self._fiduc):
            cc = dict()
            for key in rr.keys():
                if key in ['value','eval']:
                    cc[key] = str(rr[key])           # make str
                elif not key[0]=='[':
                    cc['['+key+']'] = rr[key]        # e.g. f -> [f]
            self._fiduc[k] = cc
        # NB: Check whether it has got values for all entries of self.variables()....!
        return True                  


    def _check_subexpr(self, subexpr):
        """Helper function to set and check self._subexpr.
        Called from __init__() only."""
        self._subexpr = subexpr
        # Make sure that all the subexpr are enclosed in ():
        if not isinstance(self._subexpr,dict):
            self._subexpr = dict()
        for key in self._subexpr.keys():
            s = self._subexpr[key]
            if not s[0]=='(':
                self._subexpr[key] = '('+s+')'
        return True

    #----------------------------------------------------------------------------
    # Some display functions:
    #----------------------------------------------------------------------------

    def oneliner(self, full=True):
        """Return a one-line summary of the Expression"""
        ss = '** Polynomial ('+str(self.name)+'):  '
        if self._polc:
            ss += '  polc='+str(self._polc)+' ->'
        ss += '  dims='+str(self._dims)
        if self._unit: ss += '('+str(self._unit)+') '
        if self._descr:
            ss += str(self._descr)
        return ss

    def display_specific(self, full=False):
        """Display the specific part of a class that is derived from an
        Expression object. This function is called by .display()."""
        print '  # Specific for class derived from Expression: '
        print '  # Polynomial terms ('+str(len(self._term))+'):'
        print '  # Fiducial points ('+str(len(self._fiduc))+'):'
        for k,rr in enumerate(self._fiduc):
            print '    - '+str(k)+': '+str(rr)
        return True

    #=============================================================================
    # Functions that generate the polynomial expression:
    #=============================================================================

    def _makexpr (self, dims=['t^2','f^3'], symbol='c',
                  exclude_triangle=True, trace=False):
        """Make the ND polynomial expression.""" 
        if trace: print '\n** _makexpr(',dims,symbol,'):'

        # Check (and make consistent) the input dims,
        # and collect the various polynomial terms accordingly:
        terms = []                         # list of terms
        maxdeg = 0                         # max degree of any term 
        for k,dim in enumerate(dims):
            dimin = dim                    # keep input for printing                
            dd = dim.split('^')            # look for ..^i

            if dd[0] in ['t','f','l','m']: # standard variables
                dd[0] = '['+dd[0]+']'      # enclose -> [t]

            if not dd[0][0] in ['{','[']:
                s = '** dim not enclosed in [] or {}: '+dd[0]
                raise ValueError,s

            if len(dd)==1:                 # no exponent (^) specified 
                maxdeg = max(maxdeg,1)
                dims[k] = dd[0]+'^1'       # modify, assume ^1
                terms = self._maketerms(terms, dim=dims[k], trace=trace)

            else:                          # exponent (^) specified
                dims[k] = dd[0]+'^'+dd[1]  # modify
                if int(dd[1])>0:           # exponent > 0
                    maxdeg = max(maxdeg,int(dd[1]))
                    terms = self._maketerms(terms, dim=dims[k], trace=trace)

            if trace: print '- collected terms from dim[',k,']:',dimin,'->',dims[k]

        # Make the full expr by adding the terms:
        if trace: print '\n Add the terms to make the expr:'
        expr = None
        self._term_order = []
        self._term = dict()
        for k,term in enumerate(terms):
            tt = term.split('_')
            isum = 0
            for c in tt[0]:
                isum += int(c)             # total degree of this term
            key = '{'+symbol+tt[0]+'}'     # e.g. {w021}
            s = key
            deriv = '1.0'                  # default (for c00)
            if len(tt[1])>0:
                s += '*'+tt[1]
                deriv = tt[1]
            if trace: print '-',isum,'/',maxdeg,':',s,
            if exclude_triangle and isum>maxdeg:
                if trace: print ' (ignored)',
                pass                       # ignore the highest order triangle
            else:
                if not expr:
                    expr = s               # first term
                else:
                    expr += ' + '+s        # other terms
                self._term_order.append(key)
                self._term[key] = dict(key=key, term=s, deriv=deriv)
            if trace: print
        self._check_terms(trace=trace)
        if expr==None: expr = '{'+symbol+'}'
        return expr


    #----------------------------------------------------------------------------

    def _check_terms(self, level=0, trace=False):
        """Helper function to process self._term"""
        if trace and level==0: print '\n** _check_terms():'
        recurse = False
        prefix = '..'*level
        for key in self._term_order:
            rr = self._term[key]
            for skey in self._subexpr.keys():
                if skey in rr['term']:
                    recurse = True
                    new = self._subexpr[skey]
                    if trace: print prefix,'-- replace: ',skey,' with: ',new
                    rr['term'] = rr['term'].replace(skey,new)
                    rr['deriv'] = rr['deriv'].replace(skey,new)
            if trace: print prefix,'-',self._term[key]
        if recurse:
            if level>10:
                raise ValueError,'_checkterm(): exceeded recursion limit' 
            self._check_terms(level=level+1, trace=trace)
        if trace and level==0: print '**\n'
        return True




    #----------------------------------------------------------------------------

    def _maketerms (self, terms=[], dim='[f]^3', trace=True):
        """Helper function to replace the given list of terms
        with new terms that include the specified dimension."""

        if trace: print '\n** _maketerms(',len(terms),dim,'):'

        # Analyse the dimension string (e.g. [t]^3, or {dt}^3):
        dd = dim.split('^')
        n = int(dd[1])+1
        dds = dd[0]                                         # deenclosed dd[0]
        for c in ['{','}','[',']']:
            dds = dds.replace(c,'')

        new = []
        if len(terms)==0:                                     # first dimension
            for i in range(n):
                if i==0:                                      # ignore [t]^0
                    s = str(i)+'_'
                else:
                    if i==1:
                        s = str(i)+'_'+dd[0]                  # ignore exponent **1
                    else:
                        subexpr = '('+dd[0]+'**'+str(i)+')' 
                        key = '{'+dds+'^'+str(i)+'}'          # e.g. {t^3}
                        s = str(i)+'_'+key                    # e.g. _{t^i}
                        self._subexpr[key] = subexpr
                if trace: print '-',i,':',s
                new.append(s)


        else:                                                         # non-first dimension
            for k,term in enumerate(terms): 
                for i in range(n):
                    subexpr = '('+dd[0]+'**'+str(i)+')' 
                    key = '{'+dds+'^'+str(i)+'}'                        # e.g. {t^3}
                    tt = term.split('_')

                    if i==0:                                            # ignore t^0
                        s = tt[0]+str(i)+'_'+tt[1]

                    elif tt[1]=='':                                     # first term     
                        if i==1:
                            s = tt[0]+str(i)+'_'+dd[0]                  # ignore exponent **1
                        else:
                            s = tt[0]+str(i)+'_'+key                    # e.g. _{t^i}
                            self._subexpr[key] = subexpr

                    else:
                        if i==1:
                            s = tt[0]+str(i)+'_'+tt[1]+'*'+dd[0]        # ignore exponent **1
                        else:
                            s = tt[0]+str(i)+'_'+tt[1]+'*'+key    
                            self._subexpr[key] = subexpr

                    if trace: print '-',k,i,':',s
                    new.append(s)

        # Finished:
        print '** len(new)=',len(new),'\n'
        return new


    #=============================================================================
    # Determine values for the polynomial coeff by fitting to fiducial points:
    #=============================================================================

    def fiducfit (self, trace=False):
        """Fit the expression to the fiducial points. I.e. find the polynomial
        coeff that make the polynomial go through these points. Modify the
        default values of the Polynomial accordingly."""
        
        # Initialize the (rectangular) condition matrix aa:
        nuk = len(self._term)                              # nr of unknowns
        neq = len(self._fiduc)                             # nr of equations
        aa = zeros([neq,nuk])                              # matrix
        vv = zeros(neq)                                    # driving values
        for ieq in range(neq):
            vv[ieq] = 0.0
            for iuk in range(nuk):
                aa[ieq,iuk] = iuk-ieq

        # Fill the matrix:
        for ieq,fc in enumerate(self._fiduc):              # for each fiducial point
            vv[ieq] = float(eval(fc['value']))             # string -> driving value
            for iuk,key in enumerate(self._term_order):    # for each term
                cc = self._term[key]
                deriv = cc['deriv']
                for v in self.variables():
                    deriv = deriv.replace(v, '('+str(fc[v])+')')
                veval = float(eval(deriv))
                aa[ieq,iuk] = veval

        # Solve for the unknown polynomial terms by inverting the matrix aa:
        # NB:  numpy.linear_algebra not supported on birch......
        if not linear_algebra:
            return False
        else:
            bb = SciPy.linear_algebra.linear_least_squares(aa,vv)
            solvec = bb[0]                                 # solution vector
            for iuk,key in enumerate(self._term_order):    # for each term
                self.modify_default(key,solvec[iuk])


        # Finally, evaluate the Polynomial with the new coeff at the
        # fiducual points, and store the value as 'eval':
        for ieq,fc in enumerate(self._fiduc):              # for each fiducial point
            tsum = 0.0
            for iuk,key in enumerate(self._term_order):    # for each term
                cc = self._term[key]
                term = cc['term']
                term = term.replace(key, '('+str(solvec[iuk])+')')
                for v in self.variables():
                    term = term.replace(v, '('+str(fc[v])+')')
                tsum += float(eval(term))                  # sum of the terms
            fc['eval'] = tsum

        # Finished
        return True







#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = [ns.dummy<<45]

    if 1:
        # Regular polynomial:
        dims = ['t^3']
        dims = ['t^4','f^4']
        # dims = ['t^1','mm^2']
        dims = ['t^1','f^2','l^2','m^3']             
        dims = ['t^1','f^2','m^3']
        # dims = ['ff^2']
        # dims = ['sin(t)^2']
        dims = ['t^2','f^2']
        # dims = ['t^6']
        p0 = Polynomial(ns, 'p0', dims=dims, symbol='w', simul=True)
        p0.display('initial')

    elif 0:
        # Polclog (used for Spectral Index):
        sex = dict()
        fiduc = []
        dims = ['{logff}^5']
        sex['{logff}'] = 'log([f]/1e6)'                    # f0 = 1 MHz
        fiduc.append(dict(f=1e6, value=5))                 # I0 (@f0) Jy
        fiduc.append(dict(f=100e6, value=3))
        fiduc.append(dict(f=200e6, value=3))
        p0 = Polynomial(ns, 'polclog', dims=dims, symbol='s',
                        subexpr=sex, fiduc=fiduc)
        p0.display('initial')
        p0.fiducfit(trace=True)
        p0.display('fiducfit')

    if 0:
        c = p0.FunckDiff(show=True)
        cc.append(c)
        JEN_bookmarks.create(c, page='FunckDiff', recurse=1)

    if 1:
        cc.append(p0.inspector(bookpage=True))

    if 0:
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
    domain = meq.domain(1,5,0.5,1000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=50)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       
def _tdl_job_polclog (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1e6,200e6,0.5,10)                      # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=30, num_time=1)
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

    if 0:
        _define_forest(ns)

    if 1: 
        sex = dict()
        fiduc = []
        dims = ['dt^1','ff^1']
        dims = ['t^1','f^2','m^3']
        dims = ['t^3','t^2','f^2']
        dims = ['t^3', 'f^2']
        dims = ['{dt}^2']
        dims = ['t^2']
        dims = ['[t]^3','m^2','{logff}','l^0','{dt}']
        # dims = ['{dt}^2']
        sex['{dt}'] = '[t]-2.3'
        # dims = ['{logff}^2']
        sex['{logff}'] = 'log([f]/2.3)'
        dims = ['t^2']
        dims = ['t^2','f^1']
        fiduc.append(dict(t=-2, value=5))
        fiduc.append(dict(t=0, value=-3))
        fiduc.append(dict(t=2, value=5))
        p0 = Polynomial(ns, 'p0',
                        dims=dims,
                        symbol='w',
                        # polc=[3,2],                        # overrides dims
                        simul=True,
                        subexpr=sex, fiduc=fiduc)
        p0.display('initial')

    if 0:
        sex = dict()
        fiduc = []
        dims = ['{logff}^4']
        sex['{logff}'] = 'log([f]/1e6)'                    # f0 = 1 MHz
        fiduc.append(dict(f=1e6, value=5))                 # I0 (@f0) Jy
        fiduc.append(dict(f=100e6, value=3))
        fiduc.append(dict(f=200e6, value=3))
        p0 = Polynomial(ns, 'polclog',
                        dims=dims,
                        symbol='s',
                        subexpr=sex, fiduc=fiduc)
        p0.display('initial')
        p0.fiducfit(trace=True)
        p0.display('fiducfit')
        p0.plot()    

    if 0:
        p0.fiducfit(trace=True)

    if 0:
        p0.plot()             # t=[-5,5,0.5])
        # p0.plot(w1=[-1,1])      # t=[-5,5,0.5])

    if 0:
        p0.FunckDiff(show=True)

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

    if 0:
        p0.MeqCompounder(show=True)
        # p0.solvable(trace=True)

    p0.display('final')
    print '\n** linear_algebra =',linear_algebra

    print '\n*******************\n** End of local test of: Expression.py:\n'




#============================================================================================

    
