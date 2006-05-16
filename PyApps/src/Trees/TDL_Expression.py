# TDL_Expression.py
#
# Author: J.E.Noordam
#
# Short description:
#   Contains a mathematical expression that can be turned into
#   a funklet, a MeqFunctional node, or a subtree.
#
# History:
#    - 10 may 2006: creation, from TDL_Functional.py (MXM)
#
# Remarks:
#


#***************************************************************************************
# Preamble
#***************************************************************************************

from Timba.Meq import meq
from numarray import *
from copy import deepcopy
from Timba.Contrib.MXM.TDL_Funklet import *


#***************************************************************************************
#***************************************************************************************

class Expression:
    def __init__(self, label='<label>', expression='-1.23456789', **pp):
        """Create the object with a mathematical expression (string)
        of the form:  {aa}*[t]+cos({b}*[f]).
        Variables are enclosed in square brackets: [t],[f],[m],...
        Parameters are enclosed in curly brackets: {aa}, {b}, ...
        Simple information about parameters (type, default value)
        may be supplied via keyword arguments pp. More detailed
        information may be supplied via the function .parm()."""

        self.__label = _unique_label(label)
        self.__expression = expression
        self.__pp = str(pp)

        # Get a list of parameter names, enclosed in curly brackets:
        self.__order = find_enclosed(self.__expression, brackets='{}')

        # For each parameter in self.__expression, make an entry in self.__parm.
        # These entries may be overwritten with extra info by self.parm().
        self.__parm = dict()
        self.__parmtype = dict(Expression=[], MeqNode=[], Funklet=[])
        for key in self.__order:
            self.parm(key, -1)

        # Limited parm info (type, default value) may also be specified
        # via the keyword arguments pp: e.g. pp['aa']= 4.5
        for key in pp.keys():
            self.parm(key, pp[key])

        # Get a list of variable names, enclosed in square brackets,
        # and create entries in self.__var:
        vv = find_enclosed(self.__expression, brackets='[]')
        self.__var = dict()
        for key in vv:
            self.var(key)

        # Initialise some derived quantities:
        self.__expanded = False
        self.__xexpr = None
        self.__xorder = []
        self.__xparm = dict()
        self.__xvar = dict()
        self.__test_result = None
        self.__eval_result = None
        self.__test_seval = None
        self.__eval_seval = None
        self.__Funklet = None
        self.__Funklet_function = None

        # Finished:
        return None

    #----------------------------------------------------------------------------
    # Some access functions:
    #----------------------------------------------------------------------------

    def label (self):
        """Return the (unique) label of this Expression object"""
        return self.__label

    def tlabel (self):
        """Return a concatenation of object type and label"""
        return str(type(self))+':'+self.__label

    def test_result (self):
        """Return the result of evaluation with the test-values."""
        return self.__test_result

    def order (self):
        """Return the order of parameters in the input expression"""
        return self.__order

    def xexpr (self):
        """Return the expanded expression"""
        self.expand()
        return self.__xexpr

    def xorder (self):
        """Return the order of parameters in the expanded expression"""
        self.expand()
        return self.__xorder

    def xparm (self, key=None):
        """Return the named (key) parameter in the expanded expression"""
        self.expand()
        if key==None: return self.__xparm
        if self.__xparm.has_key(key): return self.__xparm[key]
        return False

    def xvar (self, key=None):
        """Return the named (key) variable in the expanded expression"""
        self.expand()
        if key==None: return self.__xvar
        if self.__xvar.has_key(key): return self.__xvar[key]
        return False


    #----------------------------------------------------------------------------
    # Some display functions:
    #----------------------------------------------------------------------------

    def oneliner(self):
        """Return a one-line summary of the Expression"""
        ss = '** Expression ('+str(self.__label)+'):  '
        ss += str(self.__expression)
        return ss

    def display(self, txt=None, full=False):
        """Display a summary of the Expression"""
        self.expand()
        if txt==None: txt = self.label()
        print '\n** Display of: Expression (',txt,'):'
        indent = 2*' '
        print indent,'-',self.oneliner()
        print indent,'- input: ',str(self.__pp)
        
        print indent,'- its variables (',len(self.__var),'): '
        for key in self.__var.keys():
            print indent,'  -',key,':',self.__var[key]

        print indent,'- its parameters (',len(self.__parm),'):'
        for key in self.__order:
            p = self.__parm[key]
            if isinstance(p, Expression):
                print indent,'  -',key,':',p.oneliner()
                if full:
                    for key1 in p.xorder():
                        p1 = p.xparm(key1)
                        print indent,'    -',key1,':',p1
            elif isinstance(p, Funklet):
                print indent,'  -',key,':',type(p)
            elif isinstance(p, Timba.TDL.TDLimpl._NodeStub):
                print indent,'  -',key,':',p.name
            else:
                print indent,'  -',key,':',p

        print indent,'- parameter types:'
        for key in self.__parmtype.keys():    
            print indent,'  -',key,'(',str(len(self.__parmtype[key])),'): ',self.__parmtype[key]

        if self.__expanded:
            print indent,'- Expanded:  xexpr:  ',self.__xexpr
            if not full:
                print indent,'  - parameters:',self.__xparm.keys()
                print indent,'  - variables: ',self.__xvar.keys()
            else:
                for key in self.__xorder:
                    p = self.__xparm[key]
                    if isinstance(p, Expression):
                        print indent,'  -',key,':',p.oneliner()
                    elif isinstance(p, Funklet):
                        print indent,'  -',key,':',type(p)
                    elif isinstance(p, Timba.TDL.TDLimpl._NodeStub):
                        print indent,'  -',key,':',p.name
                    else:
                        print indent,'  -',key,':',p
                for key in self.__xvar.keys():
                    print indent,'  .',key,':',self.__xvar[key]
            print indent,'  - test_result: ',self.__test_result
            print indent,'  - eval_result: ',self.__eval_result
            if full:
                print indent,'  - test_seval: ',self.__test_seval
                print indent,'  - eval_seval: ',self.__eval_seval

        if self.__Funklet:
            print indent,'- Funklet:'
            print indent,'  - function =',str(self.__Funklet_function)
            print indent,'  - _function ->',str(self.__Funklet._function)
            print indent,'  - _coeff ->',str(self.__Funklet._coeff)
            # print dir(self.__Funklet)
            print indent,'- eval() ->',str(self.__Funklet.eval())
            
        print '**\n'



        
    #============================================================================
    # Manual definition of named parameters and variables:
    #============================================================================

    def parm (self, key=None, default=None, polc=None,
              help=None, scatter=0, test=None, trace=True):
        """Provide extra information for the named parameter (key).
        The default argument may either be a value, or an object of type
        Expression or Funklet, or a nodestub (child of MeqFunctional node).
        If polc=[ntime,nfreq] (one-relative), a polc Expression is generated,
        with the default value/list as a coeff-list."""

        # If no key specified, return the entire record:
        if key==None:
            return self.__parm

        if not key in self.__order:
            print '\n** .parm(',key,'): not recognised in:',self.__order,'\n'
            return False

        # Special case: make a polc Expression:
        if isinstance(polc, (list,tuple)):
            default = create_polc(shape=polc, coeff=default, label=None, trace=trace)

        # Update the specified self.__parm entry:
        if default==None:
            # No default specified, just return the existing entry:
            return self.__parm[key]

        # The parm may be another object, or a nodestub:
        elif isinstance(default, Expression):
            print '   default == Expression'
            self.__parm[key] = default
            self.__parmtype['Expression'].append(key)
        elif isinstance(default, Funklet):
            self.__parm[key] = default
            self.__parmtype['Funklet'].append(key)
        elif isinstance(default, Timba.TDL.TDLimpl._NodeStub):
            self.__parm[key] = default
            self.__parmtype['MeqNode'].append(key)

        else:
            # A numeric parm has a default value.
            # It also has other information:
            # - test: value to be used for testing.
            # - scatter: stddev to be used for simulaton.
            if test==None: test = default
            self.__parm[key] = dict(default=default, help=help,
                                    test=test, scatter=scatter)

        # Enforce a new expansion:
        self.__expanded = False

        # Always return the named (key) parm entry:
        return self.__parm[key]

    #----------------------------------------------------------------------------

    def var (self, key=None, default=1.0, test=None, trace=True):
        """Get/set the named variable (key).
        If the entry (key) does not exist yet, create it (if recognisable)"""

        # If no key specified, return the entire record:
        if key==None: return self.__var

        # If the entry exists already, just return it:
        if self.__var.has_key(key): return self.__var[key]

        # Create a new entry:
        if test==None: test = default            # test-value
        rr = dict(xn='xn', default=default, test=test, unit=None)

        # self.__var_def = {'x0':"time",'x1':"freq"}
        if key[0]=='t':                          # time
            rr['xn'] = 'x0'
            rr['unit'] = 's'
        if key[0]=='f':                          # freq, fGHz, fMHz
            rr['xn'] = 'x1'
            rr['unit'] = 'Hz'
        if key[0]=='l':
            rr['xn'] = 'x2'
            rr['unit'] = 'rad'
        if key[0]=='m':
            rr['xn'] = 'x3'
            rr['unit'] = 'rad'
        
        self.__var[key] = rr

        # Enforce a new expansion:
        self.__expanded = False

        # Finished:
        return self.__var[key]



    #============================================================================
    # Expansion of the hierarchical Expression into a flat one
    #============================================================================

    def expand (self, trace=False):
        """Expand the function-string by replacing the parameters that are Expressions
        by the relevant function-strings, while slightly renaming its parameter names."""

        if trace: print '\n** expand():',self.oneliner()
        if self.__expanded: return False                 # avoid duplication

        self.__xexpr = deepcopy(self.__expression)
        self.__xparm = dict()
        self.__xorder = []
        self.__xvar = deepcopy(self.__var)

        # Then replace the (expanded) Expression parameters:
        for key in self.__order:
            parm = self.__parm[key]

            if isinstance(parm, Expression):
                pexpr = '('+parm.xexpr()+')'
                if trace: print '-',key,pexpr
                for pkey in parm.xorder():
                    ckey = key+'_'+pkey
                    self.__xorder.append(ckey)
                    self.__xparm[ckey] = parm.xparm(pkey)
                    pexpr = pexpr.replace('{'+pkey+'}', '{'+ckey+'}')
                self.__xexpr = self.__xexpr.replace('{'+key+'}', pexpr)
                for vkey in parm.xvar().keys():
                    self.__xvar.setdefault(vkey, parm.xvar(vkey))

            # elif isinstance(parm, Funklet):

            # elif isinstance(parm, Timba.TDL.TDLimpl._NodeStub):

            else:
                self.__xorder.append(key)
                self.__xparm[key] = self.__parm[key]
                
        self.__expanded = True
        if trace: print '   ->',self.__xexpr
        self.__test_result = self.eval(test=True)
        self.__eval_result = self.eval()
        return True
    



    #============================================================================
    # The Expression can be converted into a Funklet:
    #============================================================================

    def Funklet (self, trace=False):
        """Return the corresponding Funklet object. Make one if necessary."""
        if not self.__Funklet:
            self.expand()
            expr = deepcopy(self.__xexpr)
            if trace: print '\n** Funklet(): ',expr
            # Replace the parameters {} with pk = p0,p1,p2,...
            # and fill the coeff-list with their default values
            coeff = []
            keys = self.__xparm.keys()
            for k in range(len(keys)):
                pk = 'p'+str(k)
                expr = expr.replace('{'+keys[k]+'}', pk)
                coeff.append(self.__xparm[keys[k]]['default'])
                if trace: print '-',k,keys[k],pk,expr,coeff
            # Replace the valiables [] with x0 (time), x1(freq) etc
            for key in self.__xvar.keys():
                xk = self.__xvar[key]['xn']
                expr = expr.replace('['+key+']', xk) 
                if trace: print '-',key,xk,expr
            # Make the Funklet:
            self.__Funklet = Funklet(funklet=record(function=expr, coeff=coeff))
            self.__Funklet_function = expr          # for display only
            # Alternative
            #   self.__Funklet = meq.polc(coeff=coeff, subclass=meq._funklet_type)
            #   self.__Funklet.function = expr
        return self.__Funklet

    #----------------------------------------------------------------------------

    def plot_Funklet(self, cells=None):
        """Make a plot of the Funklet"""
        self.Funklet()
        if not self.__Funklet: return
        return self.__Funklet.plot(cells=cells)

    #------------------------------------------------------------------------

    def MeqParm (self, ns, key=None, qual=None, children=None):
        """Make a MeqParm node from the Expression"""
        return node

    def MeqCompounder (self, ns, key=None, qual=None, children=None):
        """Make a MeqCompunder node from the Expression"""
        if compounder_children:
            # Special case: Make a MeqCompounder node with a ND funklet.
            # Used for interpolatable Jones matrices like EJones or MIM etc

            # The parm is the one to be used by the solver, but it cannot
            # be evaluated by itself...
            parm = ns[key](**quals)
            if not parm.initialized():
                parm << Meq.Parm(init_funklet=init_funklet)
                self.NodeSet.set_MeqNode(parm, group=leafgroup)
            
            # The Compounder has more qualifiers than the Parm.
            # E.g. EJones_X is per station, but the compounder and its
            # children (l,m) are for a specific source (q=3c84)
            group = leafgroup                            # e.g. 'EJones'
            if isinstance(qual2, dict):
                for qkey in qual2.keys():
                    s1 = str(qual2[qkey])
                    quals[qkey] = s1
                    group += '_'+s1                      # e.g. 'EJones_3c84'
            node = ns[key](**quals)
            if not node.initialized():
                cc = compounder_children
                if not isinstance(cc, (list, tuple)): cc = [cc]
                cc.append(parm)
                node << Meq.Compounder(children=cc, common_axes=common_axes)
                self.NodeSet.set_MeqNode(node, group=group)
                self.NodeSet.append_MeqNode_eval(parm.name, append=node)



    #============================================================================
    # Evaluating the (expanded) expression:
    #============================================================================

    def eval(self, trace=False, test=False, **pp):
        """Evaluate the (expanded) expression for the specified (pp) values of
        parameters {} and variables []. Use defaults if not specified.
        The specified parameters/variables may be multiple (lists),
        provided that all such lists have the same length.
        The evaluation will then return a list of the same length."""

        if trace: print '\n** eval():',pp

        # Make sure that an expanded expression exists:
        self.expand()

        # Use the default values in self.__xparm and self.__xvar,
        # unless other values have been specified via **pp.
        rr = dict()
        field = 'default'                        # normal mode
        if test: field = 'test'                  # .test() mode
        for key in self.__xparm.keys():
            pp.setdefault(key, self.__xparm[key][field])
            rr['{'+key+'}'] = pp[key]
        for key in self.__xvar.keys():
            pp.setdefault(key, self.__xvar[key][field])
            rr['['+key+']'] = pp[key]

        # Parameters/variables may be multiple:
        nmax = 1
        for key in rr.keys():
            if isinstance(rr[key], (list,tuple)):
                n = len(rr[key])
                if n>1:
                    if nmax>1 and not nmax==n:
                        print '** .eval() error:',key,n,nmax
                        return False            # error
                    nmax = n
            else:
                rr[key] = [rr[key]]

        # Evaluate the result element-by-element:
        result = []
        for i in range(nmax):
            qq = dict()
            for key in rr.keys():
                if len(rr[key])==1:
                    qq[key] = rr[key][0]
                else:
                    qq[key] = rr[key][i]
            result.append(self.eval1(qq, test=test, trace=trace))
        if len(result)==1: result = result[0]
        if trace: print '  -> result =',result
        return result


    #-----------------------------------------------------------------------

    def eval1 (self, pp, test=False, trace=False):
        """Helper function called by .eval()"""

        seval = deepcopy(self.__xexpr)
        if trace:
            print '.... eval1():',seval
            print pp

        # Replace parameters and variables with numeric values:
        for key in pp.keys():
            value = pp[key]
            if value<0:
                srep = '('+str(value)+')'
            else:
                srep = str(value)
            seval = seval.replace(key, srep)
            if trace:
                print '- substitute',key,'->',value,':   ',seval
            
        # Evaluate the seval string:
        try:
            if test:
                self.__test_seval = seval
            else:
                self.__eval_seval = seval
            result = eval(seval)                  # covers most things
        except:
            print sys.exc_info()
            return False                          # something wrong
        # Return the result
        if trace: print '  -> result =',result
        return result












#=======================================================================================
#=======================================================================================
#=======================================================================================
# Standalone helper functions
#=======================================================================================

#-------------------------------------------------------------------------------
# Functions dealing with (unique) labels:
#-------------------------------------------------------------------------------

_labels = {}

def _unique_label (label, trace=False):
    """Counter service (use to automatically generate unique node names)"""
    global _labels
    if not _labels.has_key(label):                # label has not been used yet
        _labels.setdefault(label, 1)              # create an entry
        return label                              # return label unchanged
    # Duplicate label: 
    _labels[label] += 1                           # increment the counter
    return label+'<'+str(_labels[label])+'>'      # modify the label 


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
    keyin = key
    if not isinstance(key, str): return key
    bopen = str(brackets[0])
    bclose = str(brackets[1])
    if key[0]==bopen:
        key = key[1:]
        n = len(key)-1
        if key[n]==bclose:
            key = key[:n]
    if trace: print '** deenclose(',keyin,') ->',key
    return key

#----------------------------------------------------------------------------

def find_enclosed (ss, brackets='{}', trace=False):
    """Return a list of substrings that are enclosed in the specified brackets.
    e.g. ss='{A}+{B}*{A}' would produce ['{A}','{B}']"""
    if trace: print '\n** find_enclosed(',brackets,'): ',ss
    b1 = brackets[0]                            # opening bracket
    b2 = brackets[1]                            # closing bracket
    cc = []
    level = 0
    for i in range(len(ss)):
        if ss[i]==b1:
            if not level==0:
                return False
            else:
                level += 1
                i1 = i
        elif ss[i]==b2:
            if not level==1:
                return False
            else:
                level -= 1
                substring = ss[i1:(i+1)]
                substring = deenclose(substring, brackets)
                if not substring in cc:
                    cc.append(substring)
                    if trace: print '-',i,level,cc
    # Some checks:
    if not level==0:
        return False
    if trace: print '   -> (',len(cc),level,'):',cc
    return cc


#=======================================================================================

def create_polc(shape=[1,1], coeff=None, label=None, trace=False):
    """Create an Expression object for a polc with the given shape.
    Parameters can be initialized by specifying a list of coeff.
    The coeff will be assumed 0 for all those missing in the list."""

    if trace:
        print '\n** create_polc(',shape,coeff,label,'):'
    if coeff==None: coeff = []
    if not isinstance(coeff, (list,tuple)): coeff = [coeff]
    if len(shape)==1: shape.append(1)
    if shape[0]==0: shape[0] = 1
    if shape[1]==0: shape[1] = 1
    if label==None: label = 'polc'+str(shape[0])+str(shape[1])
    func = ""
    k = -1
    pp = dict()
    help = dict()
    first = True
    for i in range(shape[1]):
        for j in range(shape[0]):
            k += 1
            pk = 'c'+str(j)+str(i)                   # e.g. c01
            pp[pk] = 0.0
            if len(coeff)>k: pp[pk] = coeff[k]
            help[pk] = label+'_'+str(j)+str(i)
            if not first: func += '+'
            func += '{'+pk+'}'                       # {c01}
            for i2 in range(j): func += '*[t]'
            for i1 in range(i): func += '*[f]'
            first = False
            if trace: print '-',i,j,k,pk,':',func
    result = Expression(label, func, **pp)
    # insert help..
    if trace:
        result.display()
    return result



#========================================================================
# Test routine:
#========================================================================

if __name__ == '__main__':
    print '\n*******************\n** Local test of: JEN_Expression.py:\n'
    # from numarray import *
    # from Timba.Trees import TDL_display
    # from Timba.Trees import TDL_Joneset
    # from Timba.Contrib.JEN import MG_JEN_funklet
    # from Timba.Trees import JEN_record
    # ns = NodeScope()

    if 0:
        e0 = Expression()
        # e0.display()
        if 0:
            print '** dir(ps) ->',dir(ps)
            print '** e0.__doc__ ->',e0.__doc__
            print '** e0.__str__() ->',e0.__str__()
            print '** e0.__module__ ->',e0.__module__
            print

    #-------------------------------------------------------------------

    if 0:
        e1 = Expression('e1', '{A}*cos({B}*[f])')
        e1.parm('A', -5, help='help for A')
        e1.parm('B', 10, test=4, help='help for B')
        # e1.display()
        # e1.eval(trace=True, f=range(5))
        # e1.Funklet(trace=True)
        e1.display()

    if 0:
        e2 = Expression('e2', '{r}+{BA}*[t]+{A}')
        # e2.parm ('BA', default=e1, help='help')
        e2.parm ('A', default=11, polc=[2,5], help='help')
        # e2.expand()
        e2.eval(trace=True, f=range(5))

    if 0:
        e2.Funklet(trace=True)
        e2.display(full=True)

    if 1:
        e2 = Expression('e2', '{peak}*exp(-{ldep}-{mdep})')
        e2.parm ('peak', default=1.0, polc=[2,1], help='peak voltage beam')
        e3 = Expression('e3', '(([l]-{l0})/{lwidth})**2')
        e3.parm ('l0', default=0.0)
        e3.parm ('lwidth', default=1.0, help='beam-width in l-direction')
        e2.parm ('ldep', default=e3)
        e4 = Expression('e4', '(([m]-{m0})/{mwidth})**2')
        e4.parm ('m0', default=0.0)
        e4.parm ('mwidth', default=1.0, help='beam-width in m-direction')
        e2.parm ('mdep', default=e4)
        e2.display(full=True)

    if 0:
        # Display the final result:
        e1.display('final result', full=True)


    #--------------------------------------------------------------------------
    # Tests of standalone helper functions:
    #--------------------------------------------------------------------------

    if 0:
        deenclose('{aa_bb}', trace=True)

    if 0:
        find_enclosed('{A}+{BA}*[t]+{A}', brackets='{}', trace=True)
        find_enclosed('{A}+{BA}*[t]', brackets='[]', trace=True)
        
    if 0:
        fp = create_polc([2,1], 56, trace=True)
        print fp.order()
        # fp.parm(fp.order()[1], 34)
        fp2 = create_polc([1,2], 56, trace=True)
        fp.parm(fp.order()[1], fp2)
        fp.display()

    if 0:
        fp = create_polc([0,0], 56, trace=True)
        fp = create_polc([1,1], 56, trace=True)
        fp = create_polc([2,2], 56, trace=True)
        fp = create_polc([1,2], 56, trace=True)
        fp = create_polc([2,1], 56, trace=True)
        fp = create_polc([3,2], 56, trace=True)
        fp = create_polc([2,3], 56, trace=True)

    print '\n*******************\n** End of local test of: JEN_Expression.py:\n'




#============================================================================================

    
