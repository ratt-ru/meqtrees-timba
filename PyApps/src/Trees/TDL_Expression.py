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
# Description:
#
#  -) Expression objects
#     -) e0 = Expression (label, "{A} + {ampl}*cos({phase}*[t])")
#     -) Variables in square brackets: [t],[time],[f],[fGHz],[l],[m],[RA],  etc
#     -) Parameters in curly brackets.
#     -) The expression is supplied to the Expression constructor
#     -) Extra information about parameters is supplied via a function:
#         -) e0.parm('A', 34)                         numeric, default value is 34
#         -) e0.parm('A', 34, constant=True)          numeric constant, value is 34
#         -) e0.parm('ampl', e1)                   another Expression object
#         -) e0.parm('phase', polc=[2,3])    Expression generated internally
#         -) e0.parm('A', f1)                          A Funklet object
#         -) e0.parm('A', node)                    A node (child of a MeqFunctional node)
#         -) e0.parm('A', image)                  A FITS image
#     -) The Expression object may yield a:
#         -) Funklet                                       with p0,p1,p2,... and x0,x1,...
#         -) MeqParm (init_funklet=Funklet)
#         -) MeqFunctional node               (parms AND vars are its children)      
#         -) MeqCompounder()                  needs extra children
#         -) ...
#     -) Easy to build up complex expressions (MIM, beamshape)
#     -) Should be very useful for LSM
#     -) Other functionality:
#         -) Plotting
#         -) Interactive coeff determination
#         -) Uncertainty (rms scatter) in default values (simulation)
#         -) Etc



#***************************************************************************************
# Preamble
#***************************************************************************************

from Timba.Meq import meq
from numarray import *
from copy import deepcopy
from Timba.Trees.TDL_Leaf import *
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
        self.__input_expression = expression        
        self.__pp = str(pp)

        # Get a list of parameter names, enclosed in curly brackets:
        self.__order = find_enclosed(self.__expression, brackets='{}')

        # For each parameter in self.__expression, make an entry in self.__parm.
        # These entries may be overwritten with extra info by self.parm().
        self.__parm = dict()
        self.__child = dict()
        self.__child_order = []
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
        self.__xchild = dict()
        self.__xchild_order = []

        self.__Funklet = None
        self.__Funklet_function = None

        self.__test_result = None
        self.__eval_result = None
        self.__test_seval = None
        self.__eval_seval = None

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
        print indent,'- input_expression: ',str(self.__input_expression)
        print indent,'- input: ',str(self.__pp)
        print indent,'-',self.oneliner()
        
        print indent,'- its variables (',len(self.__var),'): '
        for key in self.__var.keys():
            print indent,'  -',key,':',self.__var[key]

        print indent,'- its parameters (',len(self.__parm),'):'
        for key in self.__order:
            p = self.__parm[key]
            if isinstance(p, Expression):
                print indent,'  -',key,':',p.oneliner()
            elif isinstance(p, Funklet):
                print indent,'  -',key,': (Funklet):',p._function
            elif p.has_key('index'):
                print indent,'  -',key,': (MeqNode):',p
            else:
                print indent,'  -',key,':',p

        print indent,'- parameter types:'
        for key in self.__parmtype.keys():    
            print indent,'  -',key,'(',str(len(self.__parmtype[key])),'): ',self.__parmtype[key]

        print indent,'- MeqFunctional children: ',self.__child_order
        if full:
            for key in self.__child_order:
                node = self.__child[key]
                print indent,'  -',key,':',node.name,' (',node.classname,')'

        if self.__expanded:
            print indent,'- Expanded:  xexpr:  ',self.__xexpr
            if not full:
                print indent,'  - parameters:',self.__xparm.keys()
                print indent,'  - variables: ',self.__xvar.keys()
                print indent,'  - MeqFunctional children: ',self.__xchild_order
            else:
                for key in self.__xorder:
                    p = self.__xparm[key]
                    if isinstance(p, Expression):
                        print indent,'  -',key,':',p.oneliner()
                    elif isinstance(p, Funklet):
                        print indent,'  -',key,': (Funklet):',p._function
                    elif p.has_key('index'):
                        print indent,'  -',key,': (MeqNode):',p
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

    def parm (self, key=None, default=None, constant=False, polc=None,
              help=None, scatter=0, testval=None, trace=True):
        """Provide extra information for the named parameter (key).
        The default argument may either be a value, or an object of type
        Expression or Funklet, or a nodestub (child of MeqFunctional node).
        If polc=[ntime,nfreq] (one-relative), a polc Expression is generated,
        with the default value/list as a coeff-list."""

        # If no key specified, return the entire record:
        if key==None:
            return self.__parm

        # Search the key for indices (in square brackets)
        # If found, change the key in expression and order.
        keyin = key
        child_name = key                          #
        index = [0]
        ii = find_enclosed(key, brackets='[]')    # e.g. A[0,1]
        if len(ii)>0:                             # found
            ss = ii[0].split(',')                 # -> ['0','1']
            child_name = key.split('[')[0]        # A
            key = child_name+'_'
            for s in ss: key += s                 # -> A_01
            index = []
            for s in ss: index.append(eval(s))    # -> [0,1]
            print keyin,key,child_name,index
            # Replace keyin with key in self.__expression
            print 'was:',self.__expression
            self.__expression = self.__expression.replace('{'+keyin+'}','{'+key+'}')
            print 'new:',self.__expression
            if keyin in self.__order:
                # Replace keyin with key in self.__order
                print 'was:',self.__order
                for i in range(len(self.__order)):
                    if self.__order[i]==keyin:
                        self.__order[i] = key
                print 'new:',self.__order


        if not key in self.__order:
            print '\n** .parm(',key,'): not recognised in:',self.__order,'\n'
            return False

        # Special case: make a polc Expression:
        if isinstance(polc, (list,tuple)):
            default = polc_Expression(shape=polc, coeff=default, label=None, trace=trace)

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
            # For the moment, assume that the node is a scalar
            # In the future, accept parameters {A[1,2]} in the input expression.
            # These are converted to self__parm key A_12, while index
            self.__child[child_name] = default
            self.__child_order.append(child_name)
            self.__parmtype['MeqNode'].append(key)
            self.__parm[key] = dict(child_name=child_name, index=index,
                                    testval=3, default=3)

        else:
            # A numeric parm has a default value.
            # It also has other information:
            # - testval: value to be used for testing.
            # - scatter: stddev to be used for simulaton.
            if testval==None: testval = default
            self.__parm[key] = dict(default=default, help=help,
                                    constant=constant,
                                    testval=testval, scatter=scatter)

        # Enforce a new expansion:
        self.__expanded = False

        # Always return the named (key) parm entry:
        return self.__parm[key]

    #----------------------------------------------------------------------------

    def var (self, key=None, default=1.0, testval=None, trace=True):
        """Get/set the named variable (key).
        If the entry (key) does not exist yet, create it (if recognisable)"""

        # If no key specified, return the entire record:
        if key==None: return self.__var

        # If the entry exists already, just return it:
        if self.__var.has_key(key): return self.__var[key]

        # Create a new entry:
        if testval==None: testval = (default+0.1)*1.1
        rr = dict(xn='xn', node=None, default=default, testval=testval, unit=None)

        # self.__var_def = {'x0':"time",'x1':"freq"}
        if key[0]=='t':                          # time
            rr['node'] = 'MeqTime'
            rr['xn'] = 'x0'
            rr['unit'] = 's'
        if key[0]=='f':                          # freq, fGHz, fMHz
            rr['node'] = 'MeqFreq'
            rr['xn'] = 'x1'
            rr['unit'] = 'Hz'
        if key[0]=='l':
            rr['node'] = 'MeqL'                  # .....!!
            rr['xn'] = 'x2'
            rr['unit'] = 'rad'
        if key[0]=='m':
            rr['node'] = 'MeqM'                  # .....!!
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

            if isinstance(parm, Funklet):
                parm = Funklet2Expression(parm, key)

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

            # elif isinstance(parm, Timba.TDL.TDLimpl._NodeStub):
              # do nothing (just copy, see below)

            else:
                # Just copy:
                self.__xorder.append(key)
                self.__xparm[key] = self.__parm[key]
                
        self.__expanded = True
        if trace: print '   ->',self.__xexpr
        self.__test_result = self.eval(test=True)
        self.__eval_result = self.eval()
        return True
    





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
        if test: field = 'testval'               # .test() mode
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



    #============================================================================
    # The Expression can be converted into a Funklet:
    #============================================================================

    def Funklet (self, trace=False):
        """Return the corresponding Funklet object. Make one if necessary."""

        if len(self.__parmtype['MeqNode'])>0:
            print '\n** .Funklet(): Expression has node child(ren)!\n'
            return False
        
        if not self.__expanded or not self.__Funklet:
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
            if trace:
                print '\n** Funklet(): expr =',expr
                print dir(self.__Funklet)
                print 'F._name:',self.__Funklet._name
                print 'F._nx:',self.__Funklet._nx
                print 'F._function:',self.__Funklet._function
                print 'F._coeff:',self.__Funklet._coeff
                print '\n'
        return self.__Funklet


    #============================================================================
    # Plotting the (expanded) expression:
    #============================================================================

    def plot_Funklet(self, cells=None):
        """Make a plot of the (Funklet of) the expanded expression."""
        self.Funklet()
        if not self.__Funklet: return
        return self.__Funklet.plot(cells=cells)



    #===========================================================================
    # Functions that require a nodescope (ns)
    #===========================================================================

    def var2node (self, ns, trace=False):
        """Convert the variable(s) in self.__expression to node(s).
        E.g. [t] is converted into a MeqTree node, etc"""
        uniqual = _counter ('var2node', increment=-1)
        for key in self.__var.keys():
            rr = self.__var[key]                        # var definition record
            pkey = rr['node']                           # var key, e.g. 't'
            name = 'Expr_'+self.label()+'_'+pkey
            node = _unique_node (ns, name, qual=None, trace=trace)
            if not node.initialized():
                if pkey=='MeqTime':
                    node << Meq.Time()
                elif pkey=='MeqFreq':
                    node << Meq.Freq()
                elif pkey=='MeqL':
                    node = TDL_Leaf.MeqL(ns)
                elif pkey=='MeqM':
                    node = TDL_Leaf.MeqM(ns)
                else:
                    print '\n** var2node(): not recognised:',pkey,'\n'
                    return False                        # problem, escape
            self.__expression = self.__expression.replace('['+key+']','{'+pkey+'}')
            if not pkey in self.__order:
                self.__order.append(pkey)
                self.parm(pkey, node)                   # define a new parm
        self.__var = dict()                             # no more vars in expression
        if trace: self.display('.var2node()', full=True)
        return True

    #---------------------------------------------------------------------------

    def parm2node (self, ns, trace=False):
        """Convert parameter(s) in self.__expression to node(s).
        E.g. {t} is converted into a MeqParm node, etc"""
        uniqual = _counter ('parm2node', increment=-1)
        for key in self.__parm.keys():
            parm = self.__parm[key]
            name = 'Expr_'+self.label()+'_'+key
            node = _unique_node (ns, name, qual=None, trace=trace)
            funklet = None
            if key in self.__parmtype['Expression']:
                funklet = parm.Funklet()
            elif key in self.__parmtype['Funklet']:
                funklet = parm
            elif key in self.__parmtype['MeqNode']:
                pass                                    # already a node
            else:                                       # assume numeric
                node << Meq.Parm(parm['default'])
                self.parm(key, node)                    # redefine the parm
            if funklet:
                node << Meq.Parm(init_funklet=funklet)
                self.parm(key, node)                    # redefine the parm
        self.__parmtype['Expression'] = []              # no more Expression parms
        self.__parmtype['Funklet'] = []                 # no more Funklet parms
        if trace: self.display('.parm2node()', full=True)
        return True

    #--------------------------------------------------------------------------

    def MeqParm (self, ns, name=None, qual=None, trace=False):
        """Make a MeqParm node,  with the expression Funklet as init_funklet."""
        funklet = self.Funklet()
        if not name: name = 'Expr_'+self.label()+'_MeqParm'
        node = _unique_node (ns, name, qual=qual, trace=trace)
        node << Meq.Parm(init_funklet=funklet)
        # if trace: print dir(node)
        return node

    #--------------------------------------------------------------------------

    def MeqCompounder (self, ns, name=None, qual=None, 
                       extra_axes=None, common_axes=None, trace=False):
        """Make a MeqCompunder node from the Expression. The extra_axes argument
        should be a MeqComposer that bundles the extra (coordinate) children,
        described by the common_axes argument (e.g. [hiid('l'),hiid('m')]."""                   

        # Make a MeqParm node from the Expression:
        parm = self.MeqParm(ns, name=name, qual=None, trace=trace)

        # Check whether there are extra axes defined for all variables
        # in the expression other than [t] and [f]:
        caxes = []
        for cax in common_axes: caxes.append(str(cax))
        print 'caxes =',caxes
        for key in self.__var.keys():
            if not key in ['t','f']:
                if not key in caxes:
                    print '\n** .MeqCompouder(',name,qual,'): missing cax:',key,'\n'
                
        # NB: The specified qualifier (qual) is used for the MeqCompounder,
        # but NOT for the MeqParm. The reason is that the Compounder has more
        # qualifiers than the Parm. E.g. EJones_X is per station, but the
        # compounder and its children (l,m) are for a specific source (q=3c84)
        if not name: name = 'Expr_'+self.label()+'_MeqCompounder'
        node = _unique_node (ns, name, qual=qual, trace=trace)
        node << Meq.Compounder(children=[extra_axes,parm], common_axes=common_axes)
        return node

    #---------------------------------------------------------------------------

    def MeqNode (self, ns, trace=False):
        """Make a single node/subtree from the Expression. In most cases,
        this will be a MeqParm, with the expression Funklet as init_funklet.
        But if the expression has at least one parameter that is a node,
        the result will be a MeqFunctional node."""
        if len(self.__parmtype['MeqNode'])>0:
            node = self.MeqFunctional(ns, trace=trace)
        else:
            node = self.MeqParm(ns, trace=trace)
        return node

    #---------------------------------------------------------------------------

    def MeqFunctional (self, ns, name=None, qual=None, trace=False):
        """Make a MeqFunctional node from the Expression, by replacing all its
        parameters and variables with nodes (MeqParm, MeqTime, MeqFreq, etc)."""
        self.parm2node (ns, trace=trace)                # convert parms to nodes
        self.var2node (ns, trace=trace)                 # convert vars to nodes
        uniqual = _counter ('MeqFunctional', increment=-1)
        function = deepcopy(self.__expression)
        children = []
        child_map = []                                  # for MeqFunctional
        k = -1
        for key in self.__parm.keys():
            k += 1                                      # increment
            xk = 'x'+str(k)                             # x0, x1, x2, ..
            function = function.replace('{'+key+'}',xk)
            parm = self.__parm[key]                     # parm definition record
            child_name = parm['child_name']
            if not child_name in children:
                children.append(child_name)
            child_num = 1+children.index(child_name)
            rr = record(child_num=child_num, index=parm['index'],
                        child_name=child_name)
            if trace: print '-',key,xk,rr
            child_map.append(rr)
        # Replace child-names with actual children:
        for i in range(len(children)):
            children[i] = self.__child[children[i]]
        if not name: name = 'Expr_'+self.label()+'_MeqFunctional'
        node = _unique_node (ns, name, qual=qual, trace=trace)
        node << Meq.Functional(children=children, child_map=child_map)
        return node









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
    """Helper function to generate a unique object label."""
    global _labels
    if not _labels.has_key(label):                # label has not been used yet
        _labels.setdefault(label, 1)              # create an entry
        return label                              # return label unchanged
    # Duplicate label: 
    _labels[label] += 1                           # increment the counter
    return label+'<'+str(_labels[label])+'>'      # modify the label 

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

#-----------------------------------------------------------------------------

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
    """Counter service (use to automatically generate unique node names)"""
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** Expression: _counters(',key,') =',_counters[key]
    return _counters[key]



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
    e.g. ss='{A}+{B}*{A}' would produce ['A','B']"""
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

def Funklet2Expression (Funklet, label='C', trace=False):
    """Create an Expression object from the given Funklet object"""
    if trace:
        print '\n** Funklet2Expression():'
        print Funklet._name
        print Funklet._function
        print Funklet._coeff
        print Funklet._nx,Funklet.getNX(),range(0,Funklet._nx)

    # Get the essential information from the Funklet
    expr = deepcopy(Funklet._function)             
    coeff = array(Funklet._coeff).flat             # flatten first
    if trace:
        print 'expr =',expr
        print 'coeff =',coeff,range(len(coeff))

    # Replace all C[n] in the Funklet expression to {<label>_n} 
    for i in range(len(coeff)):
        expr = expr.replace('C['+str(i)+']','{'+label+'_'+str(i)+'}')

    # Replace all x[n] in the Funklet expression to [t],[f] etc
    expr = expr.replace('x[0]','[t]')
    expr = expr.replace('x[1]','[f]')
    expr = expr.replace('x[2]','[l]')              # .........?
    expr = expr.replace('x[3]','[m]')              # .........?

    # Temporary workaround (until Funklet repaired):
    expr = expr.replace('[0]','')          
    expr = expr.replace('[1]','')          
    expr = expr.replace('[2]','')          
    expr = expr.replace('[3]','')          

    # Make the Expression object:
    e0 = Expression('Funklet_'+label, expr)

    # The Funklet coeff values are parameter default values: 
    for i in range(len(coeff)):
        e0.parm(label+'_'+str(i), coeff[i])
    
    # Finished: return the Expression object:
    if trace: e0.display('Funklet2Expression()', full=True)
    return e0



#=======================================================================================

def polc_Expression(shape=[1,1], coeff=None, label=None, trace=False):
    """Create an Expression object for a polc with the given shape.
    Parameters can be initialized by specifying a list of coeff.
    The coeff will be assumed 0 for all those missing in the list."""

    if trace:
        print '\n** polc_Expression(',shape,coeff,label,'):'
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
    from Timba.Trees import TDL_display
    # from Timba.Trees import TDL_Joneset
    # from Timba.Contrib.JEN import MG_JEN_funklet
    # from Timba.Trees import JEN_record
    ns = NodeScope()

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

    if 1:
        f0 = Funklet()
        # f0.setCoeff([[1,0],[2,3]])            # causes Funklet problems (see bug #...)
        f0.setCoeff([1,0,2,3])                  # OK
        f0.init_function()
        print f0._function
        print f0._coeff
        Funklet2Expression(f0, 'A', trace=True)
 
    if 1:
        e1 = Expression('e1', '{A}*cos({B}*[f])+{C}')
        e1.parm('A', -5, constant=True, scatter=0.1)
        e1.parm('B', 10, testval=4, help='help for B')
        e1.parm('C', f0, help='help for C')
        e1.display()

        if 0:
            e1.eval(trace=True, f=range(5))
            e1.display()

        if 0:
            f1 = e1.Funklet(trace=True)
            e1.display()
            Funklet2Expression(f1, 'A', trace=True)

        if 1:
            node = e1.MeqFunctional(ns, trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)

        if 0:
            node = e1.MeqParm(ns, trace=True)
            TDL_display.subtree(node, 'MeqParm', full=True, recurse=5)

        if 0:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e1.MeqCompounder(ns, qual=dict(q='3c84'), extra_axes=LM,
                                    common_axes=[hiid('l'),hiid('m')], trace=True)
            TDL_display.subtree(node, 'MeqCompounder', full=True, recurse=5)
            print 'hiid(m) =',hiid('m'),type(hiid('m')),'  str() ->',str(hiid('m')),type(str(hiid('m')))

    #.........................................................................

    if 0:
        e2 = Expression('e2', '{r}+{BA}*[t]+{A[1,2]}-{xxx}')
        e2.parm ('BA', default=e1, help='help')
        e2.parm ('r', default=11, polc=[4,5], help='help')
        node = ns << 10
        # e2.parm ('A[1,2]', default=node, help='help')
        # e2.parm ('xxx', default=node, help='help')
        e2.display(full=True)
        # e2.expand()
        # e2.eval(trace=True, f=range(5))
        # e2.parm2node(ns, trace=True)
        # e2.var2node(ns, trace=True)

    if 0:
        e2.Funklet(trace=True)
        e2.display(full=True)

    if 0:
        node = e2.MeqFunctional(ns, trace=True)
        TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)

    if 0:
        node = e2.MeqNode(ns, trace=True)
        TDL_display.subtree(node, 'MeqNode', full=True, recurse=5)

    if 0:
        # Voltage beam (gaussian):
        gaussian = Expression('gauss', '{peak}*exp(-{ldep}-{mdep})')
        gaussian.parm ('peak', default=1.0, polc=[2,1], help='peak voltage beam')
        lterm = Expression('lterm', '(([l]-{l0})/{lwidth})**2')
        lterm.parm ('l0', default=0.0)
        lterm.parm ('lwidth', default=1.0, help='beam-width in l-direction')
        gaussian.parm ('ldep', default=lterm)
        mterm = Expression('mterm', '(([m]-{m0})/{mwidth})**2')
        mterm.parm ('m0', default=0.0)
        mterm.parm ('mwidth', default=1.0, help='beam-width in m-direction')
        gaussian.parm ('mdep', default=mterm)
        if 1:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = gaussian.MeqCompounder(ns, qual=dict(q='3c84'), extra_axes=LM,
                                          common_axes=[hiid('l'),hiid('m')], trace=True)
            TDL_display.subtree(node, 'MeqCompounder', full=True, recurse=5)
        if 1:
            node = gaussian.MeqFunctional(ns, qual=dict(q='3c84'), trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)
        gaussian.display(full=True)
            



    #--------------------------------------------------------------------------
    # Tests of standalone helper functions:
    #--------------------------------------------------------------------------

    if 0:
        node = _unique_node (ns, 'name', qual=None, trace=True)
        node << 0
        node = _unique_node (ns, 'name', qual=12, trace=True)
        node = _unique_node (ns, 'name', qual=dict(s=3,b=4), trace=True)
        node = _unique_node (ns, 'name', qual=None, trace=True)

    if 0:
        deenclose('{aa_bb}', trace=True)

    if 0:
        find_enclosed('{A}+{BA}*[t]+{A}', brackets='{}', trace=True)
        find_enclosed('{A}+{BA}*[t]', brackets='[]', trace=True)

    if 0:
        ss = find_enclosed('{A[0,1]}', brackets='[]', trace=True)
        ss = find_enclosed('A', brackets='[]', trace=True)
        ss = find_enclosed('A[5]', brackets='[]', trace=True)
        print ss,'->',ss[0].split(',')
        
    if 0:
        fp = polc_Expression([2,1], 56, trace=True)
        print fp.order()
        # fp.parm(fp.order()[1], 34)
        fp2 = polc_Expression([1,2], 56, trace=True)
        fp.parm(fp.order()[1], fp2)
        fp.display()

    if 0:
        fp = polc_Expression([0,0], 56, trace=True)
        fp = polc_Expression([1,1], 56, trace=True)
        fp = polc_Expression([2,2], 56, trace=True)
        fp = polc_Expression([1,2], 56, trace=True)
        fp = polc_Expression([2,1], 56, trace=True)
        fp = polc_Expression([3,2], 56, trace=True)
        fp = polc_Expression([2,3], 56, trace=True)

    print '\n*******************\n** End of local test of: JEN_Expression.py:\n'




#============================================================================================
# Remarks:
#
# - MXM cannot interprete pk for k>9. Use C[k] (and X[n]) instead?
#
# - order of MeqFunctional children...


#============================================================================================

    
