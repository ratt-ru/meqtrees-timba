# JEN_parse.py
#
# Author: J.E.Noordam
#
# Short description:
#   Contains a series of text parsing functions
#
# History:
#    - 02 jul 2006: creation, from TDL_Expression.py
#    - 07 aug 2006: implement .find_unop()
#    - 07 may 2007: .find_enclosed(): add arg: enclose=False
#    - 09 may 2007: .find_function()
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

from copy import deepcopy
import re

# Replacement for is_numeric(): if isinstance(x, NUMMERIC_TYPES):
NUMERIC_TYPES = (int, long, float, complex)


#***************************************************************************************
#***************************************************************************************


#-------------------------------------------------------------------------------
# Functions dealing with brackets:
#----------------------------------------------------------------------------

def enclose (key, brackets='{}', trace=False):
    """Make sure that the given key is enclosed by the specified brackets"""
    bopen = str(brackets[0])
    bclose = str(brackets[1])
    if not isinstance(key, str):
        return bopen+str(key)+bclose
    if not key[0]==bopen:
        return bopen+str(key)+bclose
    return key

#----------------------------------------------------------------------------

def deenclose (key, brackets='{}', trace=False):
    """Make sure that the given key is NOT enclosed by the specified brackets"""
    # trace = True
    if trace: print '** .deenclose(',key,brackets,'):'
    keyin = key
    if not isinstance(key, str): return key
    bopen = str(brackets[0])
    if not key[0]==bopen:
        if trace: print '   first bracket is not',bopen,'->',key
        return key                              # not enclosed
    bclose = str(brackets[1])
    n = len(key)
    # if n<1: return key                        # too short
    if not key[n-1]==bclose:
        if trace: print '   last bracket is not',bclose,'->',key
        return key                              # not enclosed
    level = 0
    lmax = 0
    for i in range(n):
        if key[i]==bopen:
            level += 1
            lmax = max(level,lmax)
        elif key[i]==bclose:
            level -= 1
            if level<1 and i<(n-1):
                if trace: print '   intermediate drop to level',level,i,n-1,'->',key
                return key                      # not enclosed
    # OK, enclosed: remove enclosing brackets:
    key = key[:(n-1)]
    key = key[1:]
    if trace: print '   OK: (lmax=',lmax,level,') ->',key
    return key

#----------------------------------------------------------------------------

def make_global (expr, trace=False):
    """Make sure that all Expression parameters {a} are global {_a}"""
    if trace: print '\n** make_global(',expr,'):'
    cc = find_enclosed (expr, brackets='{}', trace=False)
    for s in cc:
        if trace: print '- replace:',s,':',
        if s[0]=='_':                           # ignore if already global
            print 'already global'
        else:
            expr = expr.replace('{'+s+'}','{_'+s+'}')
            if trace: print expr
    if trace: print ' ->',expr
    return expr

#----------------------------------------------------------------------------

def find_enclosed (expr, brackets='{}', enclose=False, trace=False):
    """Return a list of substrings that are enclosed in the specified brackets.
    e.g. expr='{A}+{B}*{A}' would produce ['A','B'].
    If enclose==True, enclose the substrings in their original brackets."""
    if trace: print '\n** find_enclosed(',brackets,'): ',expr
    b1 = brackets[0]                            # opening bracket
    b2 = brackets[1]                            # closing bracket
    cc = []
    level = 0
    for i in range(len(expr)):
        if expr[i]==b1:
            if not level==0:                    # nested brackets should not exist...!
                return False
            else:
                level += 1
                i1 = i
        elif expr[i]==b2:
            if not level==1:                    # wrong order....
                return False
            else:
                level -= 1
                substring = expr[i1:(i+1)]
                substring = deenclose(substring, brackets)
                if not substring in cc:
                    if enclose:
                        cc.append(b1+substring+b2)    # re-enclose substring
                    else:
                        cc.append(substring)          # unenclosed substring
                    if trace: print '-',i,level,cc
    # Some checks:
    if not level==0:
        return False
    if trace: print '   -> (',len(cc),level,'):',cc
    return cc

#----------------------------------------------------------------------------

def find_function (expr, func=None, done=[], level=0, trace=False):
    """Return a record with the essentials of the specified function, e.g sin()"""
    prefix = level*'  '
    if trace:
        print '\n',prefix,'** find_function(',func,'): ',expr
    ff = []
    rr = None
    nf = len(func)
    nest = 0
    i0 = 0
    i1 = 0
    active = False
    for i,c in enumerate(expr):
        if trace: print prefix,'-',i,':',c,nest,i0,i1,active,':',
        if c=='(':
            nest += 1
            if nest==1:
                i0 = i
                if i>(nf-1):
                    lastf = expr[(i-nf):i]
                    if trace: print 'lastf=',lastf,
                    if lastf==func:
                        if trace: print 'found',
                        i1 = i
                        active = True
                        
        elif c==')':
            nest -= 1
            if nest==0:
                ff1 = find_function(expr[(i0+1):i], func=func, done=done,
                                    level=level+1, trace=trace)
                ff.extend(ff1)
                if trace and len(ff1)>0: print '\n',prefix,'ff1=',ff1
                if active:
                    active = False
                    substring = expr[(i1-nf):(i+1)]
                    if not substring in done:                # avoid duplication
                        done.append(substring)
                        rr = dict(func=func, arg=expr[(i1+1):i],
                                  substring=substring)
                        ff.append(rr)
                        if trace: print '\n',prefix,'rr=',rr
                               
        if trace: print 'len(ff)=',len(ff)
    # Finished:
    if trace and level==0:
        for rr in ff: print ' - ',rr
        print '**\n'
    return ff


#----------------------------------------------------------------------------
# Split into top-level additive (+/-) terms:
#----------------------------------------------------------------------------

def find_terms (expr, level=0, trace=False):
    """Find the additive (+/-) terms of the given mathematical expression (string),
    i.e. the top-level subexpressions separated by plus and minus signs.
    Return a record with two lists: pos and neg."""

    # trace = True
    if trace: print '\n** find_terms(): ',expr

    rr = dict(pos=[],neg=[])                     # initialise output record
    nest = 0
    i1 = 0
    ncpt = 0
    n2 = 0
    expr = deenclose(expr, '()', trace=False)    # remove enclosing brackets
    nchar = len(expr)
    key = 'pos'
    for i in range(len(expr)):
        last = (i==(nchar-1))                    # True if last char
        if last:
            term = expr[i1:(i+1)]
            append_term (rr, term, key, n2, i, nest, trace=trace)
            if expr[i]==')': nest -= 1           # closing bracket
        elif expr[i]=='(':                       # opening bracket
            nest += 1
        elif expr[i]==')':                       # closing bracket
            nest -= 1
        elif nest>0:                             # nested
            if level==0:
                # Ignore, but count the higher-nested () terms.
                # This is for dealing with top-level terms that are
                # enclosed in brackets (), taking signs into account.
                if expr[i] in ['+','-']: n2 += 1
        elif expr[i] in ['+','-']:               # end of an un-nested term
            if ncpt>0:                           # some chars in term
                term = expr[i1:i]
                append_term (rr, term, key, n2, i, nest, trace=trace)
            i1 = i+1                             # first char of new term
            ncpt = 0                             # term char counter
            n2 = 0
            key = 'pos'                          # additive term
            if expr[i]=='-': key = 'neg'         # subtractive term              
        ncpt += 1                                # increment term char counter

    # Some checks:
    if not nest==0:                             # bracket imbalance
        print '\n** find_terms() Error: bracket imbalance, nest =',nest
        print 'expr =',expr
        print '\n'
        return False
    if trace: print '   -> (',nest,'):',rr
    return rr

#...............................................................................

def append_term (rr, term, key, n2, i, nest, trace=False):
    """Helper function for .find_terms()"""
    if n2>0:                             # term contains +/-
        rr1 = find_terms(term, level=1, trace=False)
        # rr1 = dict(pos=[], neg=[])
        if key=='pos':
            rr['pos'].extend(rr1['pos']) # 
            rr['neg'].extend(rr1['neg']) # 
        else:
            rr['neg'].extend(rr1['pos']) # 
            rr['pos'].extend(rr1['neg']) # 
            if trace: print '-',i,nest,key,n2,' rr1 =',rr1
    else:
        term = deenclose(term, '()', trace=False)
        rr[key].append(term)
        if trace: print '-',i,nest,key,'term =',term
    return True



#----------------------------------------------------------------------------
# Split into top-level additive (+/-) factors:
#----------------------------------------------------------------------------

def find_factors (expr, level=0, trace=False):
    """Find the additive (*/^) factors of the given mathematical expression (string),
    i.e. the top-level subexpressions separated by plus and minus signs.
    Return a record with two lists: pos and neg."""

    # trace = True
    if trace: print '\n** find_factors(): ',expr

    rr = dict(mult=[],div=[])                    # initialise output record
    nest = 0
    i1 = 0
    ncpt = 0
    n2 = 0
    has_terms = False
    skip_char = False
    expr = deenclose(expr, '()', trace=False)    # remove enclosing brackets
    nchar = len(expr)
    key = 'mult'
    for i in range(len(expr)):
        last = (i==(nchar-1))                    # True if last char
        if last:
            factor = expr[i1:(i+1)]
            append_factor (rr, factor, key, n2, i, nest, trace=trace)
            if expr[i]==')': nest -= 1           # closing bracket
        elif expr[i]=='(':                       # opening bracket
            nest += 1
        elif expr[i]==')':                       # closing bracket
            nest -= 1
        elif nest>0:                             # nested
            if level==0:
                # Ignore, but count the higher-nested () factors.
                # This is for dealing with top-level factors that are
                # enclosed in brackets (), taking signs into account.
                if expr[i] in ['*','/']: n2 += 1
                n2 = 0                           # .... disable (causes errors!)....... <--
        elif expr[i] in ['+','-']:               # additive terms detected
            has_terms = True                     # do NOT factorize (see below)
            break                                # escape
        elif skip_char:                          # skip this char
            skip_char = False                    # reset switch (see below) 
        elif expr[i]=='*' and expr[i+1]=='*':    # '**'     
            skip_char = True                     # ignore this char and the next
        elif expr[i] in ['*','/']:               # end of an un-nested factor
            if ncpt>0:                           # some chars in factor
                factor = expr[i1:i]
                append_factor (rr, factor, key, n2, i, nest, trace=trace)
            i1 = i+1                             # first char of new factor
            ncpt = 0                             # factor char counter
            n2 = 0
            key = 'mult'                         # multiplicative factor
            if expr[i]=='/': key = 'div'         # divider              
        ncpt += 1                                # increment factor char counter

    # Some checks:
    if has_terms==True:
        if trace: print '--- additive terms found @nest==0: return expr as single factor'
        rr = dict(mult=[expr],div=[])        
    elif not nest==0:                   
        print '\n** find_factors() Error: bracket imbalance, nest =',nest
        print 'expr =',expr
        print '\n'
        return False

    # Finished:
    if trace: print '   -> (',nest,'):',rr
    return rr

#...............................................................................

def append_factor (rr, factor, key, n2, i, nest, trace=False):
    """Helper function for .find_factors()"""
    if n2>0:                             # factor contains +/-
        rr1 = find_factors(factor, level=1, trace=False)
        if key=='mult':
            rr['mult'].extend(rr1['mult']) # 
            rr['div'].extend(rr1['div'])  # 
        else:
            rr['div'].extend(rr1['mult']) # 
            rr['mult'].extend(rr1['div']) # 
            if trace: print '-',i,nest,key,n2,' rr1 =',rr1
    else:
        factor = deenclose(factor, '()', trace=False)
        rr[key].append(factor)
        if trace: print '-',i,nest,key,'factor =',factor
    return True



#-----------------------------------------------------------------------
# Find top-level binary operations (binops), e.g. pow(a,b)
#-----------------------------------------------------------------------

def find_binop (expr, trace=False):
    """Check whether the given expr string consists of a single unary
    operation, e.g. 'cos(arg)'. If so, return the arument and the operation."""

    funcname = '.find_binop()'
    if trace: print '\n** .find_binop(',expr,'):'

    rr = dict(binop=None, node=None, lhs=None, rhs=None)
    n = len(expr)

    # Make a list of binary operations recognised in Python:
    binops = ['pow','atan2','tocomplex','polar','posdiff',
              'gaussnoise',
              'min','max','fmod','remainder']

    # The corresponding MeqNode names:
    nodes = ['Pow','Atan2','Tocomplex','Polar','Posdiff',
             'Gaussnoise',
             'Min','Max','Fmod','Remainder']

    # Some bunops may be unops, depending on the nr of arguments.
    # These are recognised below.
    bunops = ['max','min']          

    # Find the binop, if any:
    for i in range(len(binops)):
        binop = binops[i]
        n1 = len(binop)+1
        if n1<=n:
            if (expr[:n1]==binop+'('):
                rr['binop'] = binop
                rr['node'] = nodes[i]
                break

    # Do some checks:
    if rr['binop']==None:
        if trace: print funcname,': not a binary operation:',expr
        if trace: print funcname,'->',rr
        return rr                           # OK, but escape

    elif not expr[n-1]==')':
        print funcname,'ERROR: last char of:',expr,' is not a closing bracket...!'
        rr['binop'] = None
        return rr

    # Get and check the argument string:
    nest = 0
    has_comma = False
    k1 = len(rr['binop'])
    for k in range(k1,n):
        if expr[k]=='(':
            nest += 1
        elif expr[k]==')':
            nest -= 1
        if nest==1:                                # top-level of argument string
            if expr[k]==',':                       # comma separating the arguments
                has_comma = True
                if k>(k1+1):                       # only if non-empty string
                    rr['lhs'] = expr[k1+1:k]       # left-hand side (1st argument)
                k1 = k
    if (n-1)>(k1+1):                               # only if non-empty string
        rr['rhs'] = expr[k1+1:n-1]                 # right-hand side (2nd argument)

    # Check the result:
    if rr['lhs']==None:
        if has_comma:
            print funcname,'ERROR: empty first argument in:',expr
        elif not rr['binop'] in bunops:            # some binops may be unops...
            print funcname,'ERROR: no second argument in:',expr
        elif trace:
            print funcname,'WARNING: no second argument in:',expr,': assume unop'
        rr['binop'] = None                         # invalid

    elif rr['rhs']==None:
        print funcname,'ERROR: empty second argument in:',expr
        rr['binop'] = None                         # invalid

    elif not nest==0:
        print funcname,'ERROR: bracket mismatch in:',expr
        rr['binop'] = None                         # invalid

    # Return the record rr:
    if trace: print funcname,'->',rr
    return rr


#-----------------------------------------------------------------------
# Find top-level unary operations (unops), e.g. cos()
#-----------------------------------------------------------------------

def find_unop (expr, trace=False):
    """Check whether the given expr string consists of a single unary
    operation, e.g. 'cos(arg)'. If so, return the arument and the operation."""

    funcname = '.find_unop()'
    if trace: print '\n** .find_unop(',expr,'):'

    rr = dict(unop=None, node=None, arg=None)
    n = len(expr)

    # Make a list of unary operations recognised in Python:
    unops = ['cos','sin','tan','log','log10','exp','sqrt','sqr',
             'abs','fabs','floor','ceil','arg','norm','real','imag','conj',
             'pow2','pow3','pow4','pow5','pow6','pow7','pow8','pow9',
             'min','max','mean','sum','product','nelements',
             'cosh','sinh','tanh','acos','asin','atan']

    # The corresponding MeqNode names:
    nodes = ['Cos','Sin','Tan','Log','Log10','Exp','Sqrt','Sqr',
             'Abs','Fabs','Floor','Ceil','Arg','Norm','Real','Imag','Conj',
             'Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8','Pow9',
             'Min','Max','Mean','Sum','Product','Nelements',
             'Cosh','Sinh','Tanh','Acos','Asin','Atan']

    # Some unops may be binops, depending on the nr of arguments.
    # These are recognised below.
    bunops = ['max','min']          

    # Find the unop, if any:
    for i in range(len(unops)):
        unop = unops[i]
        n1 = len(unop)+1
        if n1<=n:
            if (expr[:n1]==unop+'('):
                rr['unop'] = unop
                rr['node'] = nodes[i]
                break

    # Some checks:
    if rr['unop']==None:
        if trace: print funcname,': not an unary operation:',expr
        if trace: print funcname,'->',rr
        return rr                          # OK, but escape

    elif not expr[n-1]==')':
        print funcname,'ERROR: last char of:',expr,' is not a closing bracket...!'
        rr['unop'] = None
        return rr

    # Get and check the argument string:
    nest = 0
    is_binop = False
    k1 = len(rr['unop'])
    for k in range(k1,n):
        if expr[k]=='(':
            nest += 1
        elif expr[k]==')':
            nest -= 1
        elif nest==1:                           # check argument string
            if expr[k]==',':                    # has second argument
                is_binop = True                 # assume binop
    if (n-1)>(k1+1):                            # only if non-empty string
        rr['arg'] = expr[k1+1:n-1]              # argument string

    # Check the result:
    if not nest==0:
        print funcname,'ERROR: bracket mismatch in:',expr
        rr['unop'] = None                       # invalid
        
    elif rr['arg']==None:
        print funcname,'ERROR: empty argument in:',expr
        rr['unop'] = None                       # invalid
        
    elif is_binop:                              # 2nd argument detected
        if not rr['unop'] in bunops:        
            print funcname,'ERROR: illegal second argument in:',expr
        elif trace:
            print funcname,'WARNING: found second argument in:',expr,': assume binop'
        rr['unop'] = None                       # invalid

    # Return the record rr:
    if trace: print funcname,'->',rr
    return rr



    


#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: JEN_parse.py:\n'

    if 1:
        matchstr = re.compile(r'Jones')
        print matchstr.sub(r'xxx', 'abcJonesABS')

    if 0:
        expr = 'a + b*sin(c+d) - 6'
        expr = 'a + b*sin(c+d*sin(c)) - 6*(sin(5))'
        expr = 'a + b*sin(c+d*sin(c)) - 6*(sin(5/sin()))'
        # expr = 'sin(c+d)'
        rr = find_function (expr, func='sin', trace=True)

    if 0:
        for x in [3,3.4,12345678907777777777777,'a',3+7j]:
            tf = isinstance(x, NUMERIC_TYPES)
            print '- isinstance(',x,type(x),', NUMERIC_TYPES) ->',tf

    if 0:
        find_unop('cos(a+b)', trace=True)
        find_unop('sin(a+b) ', trace=True)
        find_unop('exp()', trace=True)
        find_unop('xxx()', trace=True)
        find_unop('max(a)', trace=True)
        find_unop('max(a,b)', trace=True)

    if 0:
        find_binop('atan(a,b)', trace=True)
        find_binop('atan2(a,b)', trace=True)
        find_binop('pow(a,b)', trace=True)
        find_binop('pow(a)', trace=True)
        find_binop('max(a)', trace=True)
        find_binop('max(a,b)', trace=True)
        find_binop('max(,b)', trace=True)
        find_binop('max(a,)', trace=True)

    if 0:
        find_terms('{r}*{b}', trace=True)
        find_terms('{r}+{BA}*[t]+{A[1,2]}-{xxx}', trace=True)
        find_terms('({r}+{BA}*[t]+{A[1,2]}-{xxx})', trace=True)
        find_terms('{r}+({BA}*[t]+{A[1,2]})-{xxx}', trace=True)
        find_terms('{r}-({BA}*[t]+{A[1,2]})-{xxx}', trace=True)
        find_terms('{r}-({BA}*[t]-{A[1,2]})-{xxx}', trace=True)
        find_terms('{r}+(-{BA}*[t]+{A[1,2]})-{xxx}', trace=True)
        find_terms('{r}-(-{BA}*[t]+{A[1,2]})-{xxx}', trace=True)
        find_terms('-{r}-(-{BA}*[t]+{A[1,2]})-{xxx}-5', trace=True)
        find_terms('(cos(-{BA}*[t]))', trace=True)
        find_terms('{r}-(cos(-{BA}*[t])+{A[1,2]})-{xxx}', trace=True)

    if 0:
        find_factors('{r}*{b}', trace=True)
        find_factors('{r}*{BA}*[t]*{A[1,2]}/{xxx}', trace=True)
        find_factors('({r}*{BA}*[t]*{A[1,2]}/{xxx})', trace=True)
        find_factors('{r}*({BA}*[t]*{A[1,2]})/{xxx}', trace=True)
        find_factors('{r}/({BA}*[t]*{A[1,2]})/{xxx}', trace=True)
        find_factors('{r}/({BA}*[t]/{A[1,2]})/{xxx}', trace=True)
        find_factors('{r}*(-{BA}*[t]*{A[1,2]})/{xxx}', trace=True)
        find_factors('{r}/(-{BA}*[t]*{A[1,2]})/{xxx}', trace=True)
        find_factors('-{r}/(-{BA}*[t]*{A[1,2]})/{xxx}/5', trace=True)
        find_factors('(cos(-{BA}*[t]))', trace=True)
        find_factors('{r}/(cos(-{BA}*[t])*{A[1,2]})/{xxx}', trace=True)

    if 0:
        deenclose('{aa_bb}', trace=True)
        deenclose('{aa}+{bb}', trace=True)
        deenclose('{{aa}+{bb}}', trace=True)

    if 0:
        find_enclosed('{A}+{BA}*[t]+{A}', brackets='{}', trace=True)
        find_enclosed('{A}+{BA}*[t]', brackets='[]', trace=True)

    if 0:
        expr = make_global('{A}+{BA}*[t]+{_A}', trace=True)
        expr = make_global('{A}+{BA}*[t]', trace=True)

    if 0:
        ss = find_enclosed('{A[0,1]}', brackets='[]', trace=True)
        ss = find_enclosed('A', brackets='[]', trace=True)
        ss = find_enclosed('A[5]', brackets='[]', trace=True)
        print ss,'->',ss[0].split(',')
        
    print '\n*******************\n** End of local test of: JEN_Expression.py:\n'




#============================================================================================
# Remarks:
#
#============================================================================================

    
