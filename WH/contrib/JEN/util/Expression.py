# Expression.py
#
# Author: J.E.Noordam
# 
# Short description:
#   Contains a mathematical expression that can be turned into
#   a funklet, a MeqFunctional node, or a subtree.
#
# History:
#    - 29 apr 2007: creation, from TDL_Expression.py
#
# Remarks:
#
# Description:
#
#  -) Expression objects
#     -) e0 = Expression ("{A} + {ampl}*cos({phase}*[t])" [, label='<label>'])
#     -) Variables in square brackets[]: [t],[time],[f],[fGHz],[l],[m],[RA],  etc
#     -) Parameters in curly brackets{}.
#     -) The expression is supplied to the Expression constructor
#     -) Extra information about parameters is supplied via a function:
#         -) e0.parm('{A}', 34)                         numeric, default value is 34
#         -) e0.parm('{ampl}', e1)                      another Expression object
#         -) e0.parm('{phase}', polc=[2,3])             A polc-type Expression generated internally
#         -) e0.parm('{A}', f1)                         A Funklet object
#         -) e0.parm('{A}', node)                       A node (child of a MeqFunctional node)
#         -) e0.parm('{A}', image)                      A FITS image
#     -) The Expression object may be converted to:
#         -) a Funklet                                  with p0,p1,p2,... and x0,x1,...
#         -) a MeqParm node (init_funklet=Funklet)
#         -) a MeqFunctional node                       (parms AND vars are its children)      
#         -) a MeqCompounder node                       needs extra children
#         -) ...
#     -) Easy to build up complex expressions (MIM, beamshape)
#     -) Should be very useful for LSM




#***************************************************************************************
# Preamble
#***************************************************************************************

from Timba.Meq import meq
from Timba.TDL import *                         # needed for type Funklet....

import Meow

# from Timba.Contrib.JEN.Grunt import SimulParm
from Timba.Contrib.JEN.Grunt import display
# from Timba.Contrib.JEN.util import JEN_bookmarks

Settings.forest_state.cache_policy = 100

# import numarray                               # see numarray.rank()
from numarray import *
# import numarray.linear_algebra                # redefines numarray.rank....
# import random
# import pylab
from copy import deepcopy


from Timba.Contrib.MXM.TDL_Funklet import *   # needed for type Funklet.... 
# from Timba.Contrib.MXM import TDL_Funklet
# from Timba.Contrib.JEN.util import TDL_Leaf
from Timba.Contrib.JEN.util import JEN_parse


# Replacement for is_numeric(): if isinstance(x, NUMMERIC_TYPES):
NUMERIC_TYPES = (int, long, float, complex)


#***************************************************************************************
#***************************************************************************************

class Expression (Meow.Parameterization):

    def __init__(self, ns, name, expr,
                 descr=None, unit=None,
                 quals=[], kwquals={}):
        """Create the object with a mathematical expression (string)
        of the form:  {aa}*[t]+cos({b}*[f]).
        Variables are enclosed in square brackets: [t],[f],[m],...
        Parameters are enclosed in curly brackets: {aa}, {b}, ...
        Simple information about parameters (type, default value)
        may be supplied via keyword arguments pp. More detailed
        information may be supplied via the function .parm()."""

        Meow.Parameterization.__init__(self, ns, str(name),
                                       quals=quals, kwquals=kwquals)

        self._descr = descr                       # optional description
        self._unit = unit                         # unit of the result
        self._expression = deepcopy(expr)         # never modified
        self._expanded = deepcopy(expr)           # working version

        # For each parameter in self._expression, make an entry in self._parm.
        # These entries may be modified with extra info by self.parm().
        self._parm = dict()
        self._parm_order = []
        self._has_MeqNodes = False
        self._parmtype = dict()
        self._find_parms(self._expression)

        # For each variable in self._expression, make an entry in self._var.
        self._var = dict()
        self._find_vars(self._expression)

        # Some placeholders:
        self._done_vars2nodes = False
        self._done_parms2nodes = False
        self._MeqNode = None
        self._MeqParm = None
        self._Funklet = None
        self._Funklet_function = None
        self._Functional = None
        self._Functional_function = None
        self._Compounder = None
        self._Compounder_common_axes = None
        self._testexpr = None

        # Finished:
        return None


    #----------------------------------------------------------------------------
    # Some access functions:
    #----------------------------------------------------------------------------

    def unit (self):
        """Return the (string) unit of the result of the Expression object"""
        if not isinstance(self._unit, str): return ''
        return self._unit

    def descr (self):
        """Return the brief description of this Expression object"""
        return str(self._descr)

    def expression (self):
        """Return its (mathematical) expression."""
        return self._expression

    def parm_order (self):
        """Return the order of parameters in the input expression"""
        return self._parm_order

    def parmtype (self, parmtype=None, key=None):
        """Helper function to read/update self._parmtype"""
        if parmtype==None:
            return self._parmtype
        elif key==None:
            return self._parmtype[parmtype]
        else:
            self._parmtype.setdefault(parmtype,[])
            if not key in self._parmtype[parmtype]:
                self._parmtype[parmtype].append(key)
        return True



    #----------------------------------------------------------------------------
    # Some display functions:
    #----------------------------------------------------------------------------

    def oneliner(self, full=True):
        """Return a one-line summary of the Expression"""
        ss = '** Expression ('+str(self.name)+'):  '
        if self._unit: ss += '('+str(self._unit)+') '
        if self._descr:
            ss += str(self._descr)
        elif full:
            s1 = str(self._expression)
            if len(s1)>50: s1 = s1[:50]+' ...' 
            ss += s1
        return ss

    #----------------------------------------------------------------

    def display(self, full=False):
        """Display a summary of this object"""
        print '\n** Summary of: '+self.oneliner()
        print '  * description: '+str(self._descr)
        print '  * expression: '+str(self._expression)
        print '  * parameters ('+str(len(self._parm))+', has_MeqNodes='+str(self._has_MeqNodes)+'):'
        for key in self.parm_order():
            rr = self._parm[key]
            print '    - '+str(key)+':  ('+str(rr['type'])+'):  '+str(rr['parm']),
            if rr.has_key('from'):
                print '  <- '+str(rr['from'])
            elif rr.has_key('default'):
                print '  default='+str(rr['default'])
            else:
                print
        if full:
            for key in self.parm_order():
                print '    - '+str(key)+':  '+str(self._parm[key])
        if False:
            print '  * parmtypes ('+str(len(self.parmtype()))+'):'
            for key in self._parmtype.keys():
                print '    - '+str(key)+':  '+str(self.parmtype(key))
        print '  * variables ('+str(len(self._var))+'):'
        for key in self._var.keys():
            print '    - '+str(key)+':  '+str(self._var[key])
        v = self._testeval()
        print '  * testexpr: '+str(self._testexpr)
        print '    - testeval() ->  '+str(v)+'  ('+str(type(v))+')'
        print '  * expanded: '+str(self._expanded)
        print '  * done_vars2nodes  = '+str(self._done_vars2nodes)
        print '  * done_parms2nodes = '+str(self._done_parms2nodes)
        print '  * (single) MeqNode = '+str(self._MeqNode)
        print '  * (single) MeqParm = '+str(self._MeqParm)
        print '  * Funklet = '+str(self._Funklet)
        print '    - function = '+str(self._Funklet_function)
        print '  * Functional = '+str(self._Functional)
        print '    - function = '+str(self._Functional_function)
        print '  * Compounder = '+str(self._Compounder)
        print '    - common_axes = '+str(self._Compounder_common_axes)
        print '**\n'
        return True
        
        
        
    #============================================================================
    # Definition of parameters {xxx} etc:
    #============================================================================

    def _find_parms (self, expr=None, trace=False):
        """Find the parameters (enclosed in {}) in the given expression string,
        and add them to self._parm, avoiding duplication"""
        order = JEN_parse.find_enclosed(expr, brackets='{}')
        if not isinstance(order,(list,tuple)):
            s = '** order is not a list, but: '+str(type(order))
            raise TypeError,s
        for key in order:
            self._create_undefined_parm ('{'+key+'}')
        # Finished: 
        return True

    def _create_undefined_parm (self, key):
        """Create a new (but undefined) parm"""
        if self._parm.has_key(key):
            pass
        else:
            rr = dict(type=None, index=None, parm=None, testval=2.0)
            self._parm[key] = rr
            self._parm_order.append(key)
        return True

    def _transfer_parms (self, other=None, trace=False):
        """Transfer the parms from the given (other) Expression object,
        and add them to self._parm."""
        for key in other.parm_order():
            if self._parm.has_key(key):
                s = '\n** transfer_parms(): already defined: '+str(key)
                raise ValueError, s
            else:
                self._parm[key] = other._parm[key]
                self._parm_order.append(key)
            self.parmtype (other._parm[key]['type'], key)
        # Finished: 
        return True

    #----------------------------------------------------------------------------

    def parm (self, key, parm, redefine=False, **pp):
        """Define an existing {key} parameter as a numeric value, an expression,
        a MeqParm or another MeqNode, etc"""

        # First some checks:
        if not self._parm.has_key(key):
            s = '** parameter key not recognised: '+str(key)
            raise ValueError, s
        rr = self._parm[key]
        if not redefine:
            if not rr['type']==None:
                s = '** duplicate definition of parameter: '+str(key)
                raise ValueError, s
        if not isinstance(pp, dict): pp = dict()

        # OK, go ahead:
        if parm=='MeqParm':
            rr['parm'] = self.ns[key] << Meq.Parm(**pp)  # use Meow....
            rr['type'] = 'MeqParm'
            rr['default'] = pp['default']
            rr['testval'] = pp['default']
        elif isinstance(parm, str):                      # assume sub-expr
            rr['parm'] = parm
            rr['type'] = 'subexpr'
            self._find_parms(parm)
            self._find_vars(parm)
        elif isinstance(parm, (int, long, float, complex)):
            rr['parm'] = parm
            rr['type'] = 'numeric'
        elif is_node(parm):
            rr['parm'] = parm
            if parm.classname=='MeqParm':
                rr['type'] = 'MeqParm'
                default = parm.initrec()['init_funklet']['coeff']
                rr['default'] = default
            elif parm.classname=='MeqConstant':          # ....?
                rr['type'] = 'MeqNode'
                value = parm.initrec()['value']
                rr['value'] = value
            else:
                rr['type'] = 'MeqNode'
        elif isinstance(parm, Funklet):
            rr['parm'] = parm
            rr['type'] = 'Funklet'
        elif isinstance(parm, Expression):
            expr = parm._expand()                        # ....??
            rr['parm'] = expr
            rr['type'] = 'subexpr'
            rr['from'] = 'Expression: '+str(parm.name)
            self._transfer_parms(parm)
            self._find_vars(expr)
        else:
            s = '** parameter type not recognised: '+str(type(parm))
            raise TypeError, s

        # Finishing touches:
        # Keep track of the different types of parameters:
        self.parmtype (rr['type'], key)

        # Transfer optional parameters from input pp to rr:
        for key in ['testval']:
            if pp.has_key(key):
                rr[key] = pp[key]
        return True

    #---------------------------------------------------------------------------

    def _parms2nodes (self):
        """Convert parameter(s) in self._expression to node(s).
        E.g. {xx} is converted into a MeqParm node, etc"""

        # Do this only once:
        if self._done_parms2nodes:
            return True                                  # done already
        self._done_parms2nodes = True

        # Turn the vars [] into parms {} first:
        self._vars2nodes()
        
        for key in self._parm.keys():
            rr = self._parm[key]
            pname = key
            qnode = self.ns[pname]
            funklet = None
            if rr['type']=='Funklet':
                funklet = rr['parm']                     # used below......?
            elif rr['type']=='subexpr':
                pass                                     # should not occur
            elif rr['type']=='MeqNode':
                pass                                     # already a node
            elif rr['type']=='MeqParm':
                pass                                     # already a node
            elif rr['type']=='numeric':
                pass                                     # part of expanded expr
                # qnode << Meq.Constant(rr['parm'])
                # self.parm(key, qnode, redefine=True)      
            else:                                        # assume numeric
                s = '** parmtype not recognised: '+str(rr['type'])
                raise TypeError,s

            if funklet:
                qnode << Meq.Parm(funklet=funklet,       # new MXM 28 June 2006
                                  node_groups=['Parm'])
                self.parm(key, qnode, redefine=True)             

        # Finished
        return True

    #============================================================================
    # Definition of variables [t] etc:
    #============================================================================

    def _find_vars (self, expr=None, trace=False):
        """Find the variables (enclosed in []) in the given expression string,
        and add them to self._var, avoiding duplication"""
        vv = JEN_parse.find_enclosed(expr, brackets='[]')
        for key in vv:
            key = '['+key+']'
            if not self._var.has_key(key):
                rr = dict(type=None, node=None,
                          xn='xn', axis=key[1],
                          unit=None, testval=10.0)
                # Deal with some standard variables:
                if key[1]=='t':                    # time
                    rr['type'] = 'MeqTime'         # used in Functional
                    rr['xn'] = 'x0'                # used in Funklet
                    rr['axis'] = 'time'            # used in MeqKernel
                    rr['unit'] = 's'
                elif key[1]=='f':                  # freq, fGHz, fMHz
                    rr['type'] = 'MeqFreq'  
                    rr['xn'] = 'x1'
                    rr['axis'] = 'freq'            # used in MeqKernel
                    rr['unit'] = 'Hz'
                elif key[1]=='l':
                    rr['type'] = 'MeqGridL'        # .....!?
                    rr['xn'] = 'x2'                # .....!?
                    rr['unit'] = 'rad'
                elif key[1]=='m':
                    rr['type'] = 'MeqGridM'        # .....!?
                    rr['xn'] = 'x3'                # .....!?
                    rr['unit'] = 'rad'
                else:
                    s ='** variable not recognised: '+str(key)
                    ValueError,s
                self._var[key] = rr
        # Finished
        return True

    #----------------------------------------------------------------------------

    def _vars2nodes (self):
        """Convert the variable(s) in self._expression to node(s).
        E.g. [t] is converted into a MeqTime node, etc.
        This is only done when needed"""

        # Do this only once:
        if self._done_vars2nodes:
            return True                                # done already
        self._done_vars2nodes = True

        expr = self._expand()
        for key in self._var.keys():
            rr = self._var[key]                        # var definition record
            vtype = rr['type']                         # e.g. 'MeqTime'
            pkey = '{'+vtype+'}'
            if pkey in self._parm_order:
                s = '\n** var is already a parm: '+str(pkey)
                raise ValueError,s
            qnode = self.ns[pkey]
            if not qnode.initialized():                # ....?
                if vtype=='MeqTime':
                    qnode << Meq.Time()
                elif vtype=='MeqFreq':
                    qnode << Meq.Freq()
                elif vtype=='MeqGridL':
                    qnode << Meq.Grid(axis='l')
                elif vtype=='MeqGridM':
                    qnode << Meq.Grid(axis='m')
                else:
                    s = '\n** var2node(): not recognised:'+str(vtype)
                    raise TypeError,s
            # Define a MeqNode parm with qnode
            expr = expr.replace(key, pkey)             # e.g. replace [t] with {MeqTime}
            self._create_undefined_parm (pkey)         
            self.parm (pkey, qnode, testval=rr['testval'])

        # Finished:
        self._expanded = expr
        return True


    #================================================================================
    # Expansion and evaluation:
    #================================================================================

    def _expand (self, replace_numeric=True, trace=False):
        """Expand its expression by replacing the sub-expressions.
        If replace_numeric==True, also replace the numeric ones (for eval())."""
        expr = deepcopy(self._expression)
        repeat = True
        count = 0
        while repeat:
            count += 1
            repeat = False
            for key in self.parm_order():
                rr = self._parm[key]
                if rr['type']==None:
                    s = '** expand(): parameter not yet defined: '+str(key)
                    raise ValueError, s  
                elif rr['type']=='subexpr':
                    if key in expr:
                        subexpr = '('+rr['parm']+')'
                        expr = expr.replace(key, subexpr)
                        if trace:
                            print '**',count,': replace:',key,' with:',subexpr
                        repeat = True
                elif replace_numeric and rr['type']=='numeric':
                    expr = expr.replace(key, '('+str(rr['parm'])+')')
            # Guard against an infinite loop:
            if count>10:
                print '\n** current expr =',expr
                s = '** expand(): maximum count exceeded '+str(count)
                raise ValueError, s
        # Finished:    
        self._expanded = expr
        self._done_parms2nodes = False
        self._done_vars2nodes = False
        return expr

    #---------------------------------------------------------------------------

    def _testeval(self, trace=False):
        """Test-evaluation of its expression, in which all the non-numeric
        parameters have been replaced with their test-values. This is primarily
        a syntax check (brackets etc), but it may have other uses too"""
        expr = self._expand(replace_numeric=True)
        for key in self.parm_order():
            if key in expr:
                replace = '('+str(self._parm[key]['testval'])+')'
                expr = expr.replace(key, replace)
                if trace:
                    print '** replace:',key,' with:',replace,' ->',expr
        for key in self._var.keys():
            if key in expr:
                replace = '('+str(self._var[key]['testval'])+')'
                expr = expr.replace(key, replace)
                if trace:
                    print '** replace:',key,' with:',replace,' ->',expr
        # Finished:
        self._testexpr = expr
        v = eval(expr)
        return v
                                    

    #============================================================================
    # The Expression can be converted into various other objects:
    #============================================================================

    def MeqFunctional (self, show=False):
        """Turn the expression into a MeqFunctional node,
        i.e. an expression of its children."""

        qnode = self.ns['Functional']
        if not qnode.initialized():
            self._parms2nodes()              # calls ._expand() and ._vars2nodes()
            function = deepcopy(self._expanded)
            children = []
            nodenames = []
            child_map = []                                      # for MeqFunctional
            k = -1
            for key in self.parm_order():
                rr = self._parm[key]                            # parm definition record
                if rr['type'] in ['MeqNode','MeqParm']:
                    k += 1                                      # increment
                    xk = 'x'+str(k)                             # x0, x1, x2, ..
                    function = function.replace(key, xk)
                    nodename = rr['parm'].name
                    if not nodename in nodenames:               # once only
                        nodenames.append(nodename)
                        children.append(rr['parm'])
                    child_num = nodenames.index(nodename)       # 0-based(!)
                    qq = record(child_num=child_num, index=rr['index'],
                                nodename=nodename)
                    child_map.append(qq)
            qnode << Meq.Functional(children=children,
                                    function=function,
                                    child_map=child_map)
        # Finsihed:
        self._Functional_function = function
        self._Functional = qnode
        if show: display.subtree(qnode)
        return qnode


    #--------------------------------------------------------------------------

    def MeqCompounder (self, extra_axes=None, common_axes=None, show=False):
        """Make a MeqCompounder node from the Expression. The extra_axes argument
        should be a MeqComposer that bundles the extra (coordinate) children,
        described by the common_axes argument (e.g. [hiid('l'),hiid('m')]."""                   

        qnode = self.ns['MeqCompounder']
        if not qnode.initialized():

            # Make a single node from the Expression:
            node = self.MeqNode()

            # Check whether there are extra axes defined for all variables
            # in the expression other than [t] and [f]:
            caxes = []
            for cax in common_axes:
                caxes.append('['+str(cax)+']')
            for key in self._var.keys():
                print key,caxes
                if not key in ['[t]','[f]']:
                    pass
                    #if not key in caxes:
                    #    s = '** missing cax:',key
                    #    raise ValueError, s
                
            qnode << Meq.Compounder(children=[extra_axes, node],
                                    common_axes=common_axes)
            self._Compounder = qnode
            self._Compounder_common_axes = str(common_axes)

        # Finished
        if show: display.subtree(qnode)
        return qnode


    #============================================================================

    def Funklet (self):
        """Return the corresponding Funklet object. Make one if necessary."""

        # Avoid double work:
        if self._Funklet:
            return self._Funklet

        if self._has_MeqNodes:
            # If there are MeqNode children, the Expression should be turned into
            # a MeqFunctional node. It is not possible to make a Funklet.
            return False
        
        function = deepcopy(self._expanded)

        # Replace the parameters {} with pk = p0,p1,p2,...
        # and fill the coeff-list with their default values
        coeff = []
        k = -1
        for key in self.parm_order():
            rr = self._parm[key]
            if rr['type'] in ['MeqParm']:
                k += 1
                pk = 'p'+str(k)
                function = function.replace(key, pk)
                value = rr['default']
                value = float(value)                   # required by Funklet...!?
                coeff.append(value)
                print '- parm',k,key,pk,coeff

        # Replace the valiables [] with x0 (time), x1(freq) etc
        for key in self._var.keys():
            xk = self._var[key]['xn']
            function = function.replace(key, xk) 
            print '- var',key,xk

        # Make the Funklet, and attach it:
        # if self._expression_type=='MeqPolc':         # see polc_Expression()
        # elif self._expression_type=='MeqPolcLog':    # see polc_Expression()
        # else:
        #-----------------------------------------------------
        if True:
            # type: isinstance(f0, Funklet) -> True
            f0 = Funklet(funklet=record(function=function, coeff=coeff),
                         name=self.name)
        else:
            # Alternative: type(meq.polc(0)) 
            f0 = meq.polc(coeff=coeff, subclass=meq._funklet_type)
            f0.function = function
        #-----------------------------------------------------

        # Finished:
        self._Funklet = f0
        self._Funklet_function = function         
        return self._Funklet





    #--------------------------------------------------------------------------

    def MeqParm (self, show=False):
        """Make a MeqParm node by converting the (expanded) expression into
        a Funklet, and using that as init_funklet."""
        qnode = self.ns['MeqParm']
        if not qnode.initialized():
            funklet = self.Funklet()
            if isinstance(funklet, bool):
                s = '** funklet is '+str(type(funklet))
                raise TypeError,s
            qnode << Meq.Parm(funklet=funklet,       # new MXM 28 June 2006
                              node_groups=['Parm'])
        # Finished
        self._MeqParm = qnode
        if show: display.subtree(qnode)
        return qnode

    # MXM: 28 June 2006
    # Ok, ik heb een functie get_meqfunklet() toegevoegd, die kun je gebruiken om
    # het funklet_type object te krijgen, nodig als je het 'init_funklet' veld zelf
    # met de hand zet (zoals je nu doet in Expression). Als je Meq.Parm
    # aanroept met als eerste variable het Funklet object (of: funklet =  funklet,
    # ipv init_funklet=funklet), gaat het ook goed, de Meq.Parm functie roept dan
    # zelf get_meqfunket() aan.
    # WEl lijkt het om vreemde import redenen niet te werken, dit komt omdat je
    # Timba.TDL niet direkt geimporteerd hebt, als je :
    #            from Timba.TDL import *
    # toevoegt werkt het.

    #---------------------------------------------------------------------------

    def MeqNode (self, show=False):
        """Make a single node/subtree from the Expression. In most cases,
        this will be a MeqParm, with the expression Funklet as init_funklet.
        But if the expression has at least one parameter that is a node,
        the result will be a MeqFunctional node."""

        qnode = self.ns['MeqNode']
        if not qnode.initialized():
            if not self._has_MeqNodes:        
                qnode = self.MeqParm(show=show)
            else:
                qnode = self.MeqFunctional(show=show)
            self._MeqNode = qnode
        if show:
            display.subtree(qnode)
        return qnode



    #===========================================================================
    # Functions dealing with the available MeqParms (for solving etc)
    #===========================================================================

    def MeqParms (self, ns=None, group='all', trace=False):
        """Access to the (groups of) MeqParm nodes associated with this Expression"""
        if not self._MeqParms:
            # Avoid duplication
            self._MeqParms = self.expanded().find_MeqParms()
        if ns and len(self._MeqParms['all'])==0:
            # If there are no MeqParm nodes, turn the Expression into one: 
            self._MeqParms['all'] = [self.MeqParm(ns)]
        if self._MeqParms.has_key(group):
            if trace: print '\n** .MeqParms(',group,'): ->',self._MeqParms[group],'\n'
            return self._MeqParms[group]
        else:
            print '\n** .MeqParms(',group,'): group not found in:',self._MeqParms.keys(),'\n'
        return False


    def find_MeqParms (self, trace=False):
        """Find the available MeqParm node names in the Expression"""
        self._MeqParms = dict(all=[])
        klasses = dict()
        done = []
        for key in self._parm_order:
            parm = self._parm[key]
            if isinstance(parm, dict) and parm.has_key('node'):
                classwise(parm['node'], klasses=klasses, done=done)
        if klasses.has_key('MeqParm'):
            self._MeqParms['all'].extend(klasses['MeqParm'])
        return self._MeqParms



#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------


def classwise (node, klasses=dict(), done=[], level=0, trace=False):
   """Recursively collect the nodes of the given subtree, divided in classes """

   # trace = True

   # Keep track of the processed nodes (to avoid duplication):
   if node.name in done: return True
   done.append(node.name)

   # Append the nodename to its (klass) group:
   klass = node.classname
   klasses.setdefault(klass, [])
   klasses[klass].append(node.name)
   if trace:
       print (level*'.')+klass+' '+node.name+' '+str(len(klasses[klass]))

   # Recursive:
   if True:
       for i in range(len(node.stepchildren)):
           stepchild = node.stepchildren[i][1]
           classwise (stepchild, klasses=klasses, done=done, level=level+1, trace=trace)
   for i in range(len(node.children)):
      child = node.children[i][1]
      classwise (child, klasses=klasses, done=done, level=level+1, trace=trace)

   # Finished:
   if level==0:
       if trace:
           print '\n** classwise():'
           for klass in klasses.keys():
               print '-',klass,':',klasses[klass]
           print
       return klasses
   return True



#=======================================================================================
#=======================================================================================
#=======================================================================================
# Standalone helper functions
#=======================================================================================

#-------------------------------------------------------------------------------
# Functions dealing with (unique) labels etc:
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



#=======================================================================================

def Funklet2Expression (Funklet, label='C', trace=False):
    """Create an Expression object from the given Funklet object"""
    if trace:
        print '\n** Funklet2Expression():'
        print Funklet._coeff,Funklet._type, Funklet._name
        print Funklet._function
        print Funklet._coeff

    # Get the essential information from the Funklet
    expr = deepcopy(Funklet._function)             
    if Funklet._type in ['MeqPolc','MeqPolcLog']:
        coeff = Funklet._coeff                     # 2D, e.g. [[2,3],[0,2]] 
    else:                                          # Any other 'functional' Funklet:
        coeff = array(Funklet._coeff).flat         # flatten first....?
    if numarray.rank(coeff)==1:
        # Replace all C[i] in the Funklet expression with {<label>_i} 
        for i in range(len(coeff)):
            pname = label+'_'+str(i)
            expr = expr.replace('C['+str(i)+']', '{'+pname+'}')
    elif numarray.rank(coeff)==2:
        # Replace all C[i][j] in the Funklet expression with {<label>_ij}
        for i in range(len(coeff)):
            for j in range(len(coeff[i])):
                pname = label+'_'+str(i)+str(j)
                expr = expr.replace('C['+str(i)+']['+str(j)+']', '{'+pname+'}')
    else:
        pass                                       # error?

    # Replace all x[n] in the Funklet expression to [t],[f] etc
    expr = expr.replace('x[0]','[t]')
    expr = expr.replace('x[1]','[f]')
    expr = expr.replace('x[2]','[l]')              # .........?
    expr = expr.replace('x[3]','[m]')              # .........?

    # Make the Expression object:
    e0 = Expression(expr, 'Funklet_'+label, descr='from: ')

    # Transfer the coeff default values: 
    if numarray.rank(coeff)==1:
        for i in range(len(coeff)):
            pname = label+'_'+str(i)
            e0.parm(pname, coeff[i])
    elif numarray.rank(coeff)==2:
        for i in range(len(coeff)):
            for j in range(len(coeff[i])):
                pname = label+'_'+str(i)+str(j)
                e0.parm(pname, coeff[i][j])

    # Finished: return the Expression object:
    if trace: e0.display('Funklet2Expression()', full=True)
    return e0



#=======================================================================================


def polc_Expression(shape=[1,1], coeff=None, label=None, unit=None,
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
        print '\n** polc_Expression(',shape,coeff,label,type,'):'
        if fit: print '       fit =',fit
    if coeff==None: coeff = []
    if not isinstance(coeff, (list,tuple)): coeff = [coeff]
    coeff = array(coeff).flat
    if len(shape)==1: shape.append(1)
    if shape[0]==0: shape[0] = 1
    if shape[1]==0: shape[1] = 1
    if label==None: label = 'polc'+str(shape[0])+str(shape[1])

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
                help[pk] = label+'_'+str(j)+str(i)
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
    result = Expression(func, label, descr='polc_Expression')
    result._expression_type = type

    # Define the Expression parms:
    for key in pp.keys():
        result.parm(key, pp[key], testinc=testinc[key], unit=uunit[key], stddev=stddev)

    # Define the Expression 'variable' parms, if necessary:
    if type=='MeqPolcLog':
        if fdep:
            logf = Expression('log([f]/{f0})', label='fvar')
            logf.parm('f0', f0)
            logf.var('f', 1.e8, testinc=0.5*1e7)  
            result.parm('logf', logf)
        if tdep:
            logf = Expression('log([t]/{t0})', label='tvar')
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


 
#=======================================================================================

def Explot (*ee, **pp):
    """Plot the list of Expressions (ee) in a mosaic of subplots"""

    # Find the nr of rows and columns of the mosaic: 
    n = len(ee)                                 # nr of Expressions/subplots
    ncol = int(ceil(sqrt(n)))
    nrow = int(ceil(float(n)/ncol))

    _legend = False
    if pp.has_key('_legend'):
        _legend = pp['_legend']
        pp._delitem__('_legend')

    # Make the plots:
    k = -1
    for row in range(1,nrow+1):
        for col in range(1,ncol+1):
            k += 1
            if k<n:
                sp = nrow*100 + ncol*10 + k+1
                ee[k].plot (_plot='linear', _test=False, _cells=None,
                            _legend=_legend,
                            _figure=1, _subplot=sp, _show=False, **pp)
    # Show the result:
    show()
    return True




#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: Expression.py:\n'
    # from numarray import *
    # from numarray.linear_algebra import *
    # from Timba.Contrib.JEN.util import TDL_display
    # import pylab
    # from Timba.Contrib.JEN.util import TDL_Joneset
    # from Timba.Contrib.JEN import MG_JEN_funklet
    # from Timba.Contrib.JEN.util import JEN_record
    ns = NodeScope()



    #-------------------------------------------------------------------

    if 0:
        f0 = Funklet()
        # f0.setCoeff([[1,0,4],[2,3,4]])       # [t]*[f]*[f] highest order
        # f0.setCoeff([[1,0],[2,3]]) 
        f0.setCoeff([1.0,0.,2.,3.])               # [t] only !!
        # f0.setCoeff([[1,0,2,3]])           # [f] only 
        # f0.setCoeff([[1],[0],[2],[3]])     # [t] only            
        # f0.setCoeff([[1,9],[0,9],[2,9],[3,8]])                
        f0.init_function()
        print dir(f0)
        print f0._function
        print f0._coeff
        print f0._type
        e0 = Funklet2Expression(f0, 'A', trace=True)
        vv = array(range(10))
        vv = 14+0.123*(vv**2)-7.8*(vv**3)
        e0.fit(vv=vv, t=range(10))
 
    if 0:
        f0 = Funklet()
        f0.setCoeff([[1,0,2,3]])             # [f] only 
        # f0.setCoeff([1,0,2,3])               # [t] only !!
        # f0.setCoeff([[1,0],[2,3]]) 
        f0._type = 'MeqPolcLog' 
        f0.init_function()
        print dir(f0)
        print f0._function
        print f0._coeff
        print f0._type
        e0 = Funklet2Expression(f0, 'A', trace=True)
        e0.plot('semilogy', f=dict(min=1e8,max=1e9), t=range(1,5))

    #---------------------------------------------------------

    if 0:
        # Special case: A purely numeric Expression
        num = Expression('67', label='num')
        num.display()
        funklet = num.Funklet(trace=True)
        v = funklet.eval()
        print 'funklet.eval() ->',v
 
    #---------------------------------------------------------

    if 0:
        expr = '{A}*{B}*[f]'
        expr = '{A}*{B}/[f]'
        expr = '{A}/[f]'
        expr = '{A}'
        expr = '2.5/{A}'
        expr = '{A}*({B}+{C})*[f]'
        expr = '{A}+{B}*{C}-[f]'
        expr = '{A}+{B}*({C}-{D})-[f]'
        expr = '{A}+{B}*({C}*{B}-{A})'
        expr = '{A}+{B}*(-{C}*{B}-{A})'
        expr = '{A}+{B}*(-{C}*{B}+{A})'
        expr = 'cos({A}+{B}+sin({C}*exp({A}+{C})))'
        expr = '{a}*sin({b}+{c}*cos({d}*[t]))-[f]'
        expr = '{A}+pow({B},{C})'
        e3 = Expression(expr, label='e3')
        e3.display('initial', full=True)
        node = e3.subTree (ns, trace=True)
        TDL_display.subtree(node, 'subTree', full=True, recurse=10)



    #---------------------------------------------------------
 
    if 0:
        e1 = Expression('{A}*cos({B}*[f])-{C}+({neq}-67)+[l]+[m]', label='e1')
        print 'before A'
        e1.parm('A', -5, constant=True, stddev=0.1)
        print 'after A'
        # e1.parm('B', (ns.B << Meq.Add(ns.aa<<4, ns.bb<<7)))      # node variable
        e1.parm('B', (ns.B('ext')(8) << Meq.Parm(34)))                   # node variable
        # e1.parm('B', 10, help='help for B')
        # e1.parm('C', f0, help='help for C')
        e1.quals([5,6])
        e1.display('initial', full=True)

        if 0:
            e1.expand()
            e1.display('after .expand', full=True)
            e1.expanded().display('.expanded()', full=True)

        if 0:
            e1.display(e1.quals([1,17]))
            e1.display(e1.quals([5,6]))
            e1.display(e1.quals())

        if 0:
            ff = array(range(-10,15))/10.0
            # e1.eval(f=ff, A=range(2))
            e1.plot(f=ff, A=range(4))
            # e1.plot(f=True, A=True, B=True)
            # e1.plot(f=True)

        if 0:
            e1.plotall(t=True)

        if 0:
            e2 = e1.subExpression('cos({B}*[f])', trace=True)
            e2.expand()
            e2.display('after expand()')

        if 0:
            node = e1.subTree (ns, trace=True)
            TDL_display.subtree(node, 'subTree', full=True, recurse=10)
            
        if 0:
            f1 = e1.Funklet(trace=True)
            e1.display()
            # e2 = Funklet2Expression(f1, 'A', trace=True)
            # e2.plot()

        if 1:
            node = e1.MeqFunctional (ns, expand=True, trace=True)
            e1.display('MeqFunctional', full=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)

        if 0:
            node = e1.MeqParm (ns, trace=True)
            e1.display('MeqParm', full=True)
            TDL_display.subtree(node, 'MeqParm', full=True, recurse=5)

        if 0:
            node = e1.MeqNode (ns, trace=True)
            e1.display('MeqNode', full=True)
            TDL_display.subtree(node, 'MeqNode', full=True, recurse=5)

        if 0:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e1.MeqCompounder(ns, qual=dict(q='3c84'), extra_axes=LM,
                                    common_axes=[hiid('l'),hiid('m')], trace=True)
            e1.display('MeqCompounder', full=True)
            TDL_display.subtree(node, 'MeqCompounder', full=True, recurse=5)
            # print 'hiid(m) =',hiid('m'),type(hiid('m')),'  str() ->',str(hiid('m')),type(str(hiid('m')))

    #.........................................................................

    if 0:
        e2 = Expression('{r}+{BA}*[t]+{A[1,2]}-{xxx}', label='e2')
        e2.parm ('BA', default=e1, help='help')
        e2.parm ('r', default=11, polc=[4,5], help='help')
        if 1:
            node = ns << 10
            # e2.parm ('A[1,2]', default=node, help='help')
            e2.parm ('xxx', default=node, help='help')
        e2.display(full=True)
        # e2.eval(f=range(5))
        # e2.parm2node(ns, trace=True)
        # e2.var2node(ns, trace=True)

        if 0:
            e2.expand()
            e2.display('after .expand()', full=True)

        if 0:
            e2.plot()

        if 0:
            e2.Funklet(trace=True)
            e2.display(full=True)

        if 1:
            node = e2.MeqFunctional(ns, expand=True, trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)

        if 0:
            node = e2.MeqNode(ns, expand=False, trace=True)
            TDL_display.subtree(node, 'MeqNode', full=True, recurse=5)
            e2.display(full=True)

    #-----------------------------------------------------------------------------

    if 0:
        # Cosine time variation (multiplicative) of an M.E. parameter:
        cosvar = Expression('{ampl}*cos(2*pi*[t]/{T}+{phi})', label='cosvar',
                            descr='cos(t) variation of an M.E. parameter')
        cosvar.parm('ampl', 1.0, polc=[2,3], unit='unit', help='amplitude(f,t) of the variation') 
        cosvar.parm('T', 100, unit='s', help='period (s) of the variation') 
        cosvar.parm('phi', 0.1, unit='rad', help='phase (f,t) of the cosine') 
        cosvar.display(full=True)
        cosvar.expanded().display(full=True)
        cosvar.plot()
        # cosvar.plotall()
        # cosvar.plot(_test=True, phi=True)
        # cosvar.plot(t=True, phi=True, ampl_c00=3.45)
        # cosvar.plot(_test=True, ampl_c01=True, ampl_c00=True)
        # Explot(cosvar,cosvar,cosvar,cosvar,cosvar)

    if 0:
        def func(a=5, b=7):
            print 'func(a=',a,', b=',b,')'
        func()
        pp = dict(a=-4)
        func(**pp)


    if 0:
        # WSRT telescope voltage beams (gaussian) with external MeqParms:
        Xbeam = Expression('{peak}*exp(-{Lterm}-{Mterm})', label='gaussXbeam',
                           descr='WSRT X voltage beam (gaussian)', unit='kg')
        Xbeam.parm ('peak', default=1.0, polc=[2,1], unit='Jy', help='peak voltage beam')

        Lterm = Expression('(([l]-{L0})*{_D}*(1+{_ell})/{lambda})**2', label='Lterm')
        Lterm.parm ('L0', default=0.0, unit='rad', help='pointing error in L-direction')
        Xbeam.parm ('Lterm', default=Lterm)

        Mterm = Expression('(([m]-{M0})*{_D}*(1-{_ell})/{lambda})**2', label='Mterm')
        # Mterm.parm ('M0', default=0.0, unit='rad', help='pointing error in M-direction')
        # Mterm.parm ('M0', default=(ns.M0_external << Meq.Constant(12.9)))

        Xbeam.parm ('Mterm', default=Mterm)
        Xbeam.parm ('_D', default=25.0, unit='m', help='WSRT telescope diameter', constant=True, origin='test')
        Xbeam.parm ('lambda', default=Expression('3e8/[f]', label='lambda',
                                                 descr='observing wavelength'), unit='m')
        Xbeam.parm ('_ell', default=0.1, help='Voltage beam elongation factor (1+ell)', origin='test')

        Xbeam.parm ('M0', default=0.0, unit='rad', help='pointing error in M-direction')
        # Xbeam.parm ('M0', default=(ns.M0_external << Meq.Constant(12.9)))

        # Xbeam.display(full=True)
        # Xbeam.display(full=False)
        # Xbeam.expanded().display(full=True)
        Xbeam.expanded().display(full=False)
        # Xbeam.plot()

        if 1:
            Xbeam.quals(6)
            node = Xbeam.MeqFunctional(ns, qual=dict(q='3c84'), trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)


        


    if 0:
        # WSRT telescope voltage beams (gaussian):
        Xbeam = Expression('{peak}*exp(-{Lterm}-{Mterm})', label='gaussXbeam',
                           descr='WSRT X voltage beam (gaussian)', unit='kg')
        Xbeam.parm ('peak', default=1.0, polc=[2,1], unit='Jy', help='peak voltage beam')
        Lterm = Expression('(([l]-{L0})*{_D}*(1+{_ell})/{lambda})**2', label='Lterm')
        Lterm.parm ('L0', default=0.0, unit='rad', help='pointing error in L-direction')
        Xbeam.parm ('Lterm', default=Lterm)
        Mterm = Expression('(([m]-{M0})*{_D}*(1-{_ell})/{lambda})**2', label='Mterm')
        Mterm.parm ('M0', default=0.0, unit='rad', help='pointing error in M-direction')
        Xbeam.parm ('Mterm', default=Mterm)
        Xbeam.parm ('_D', default=25.0, unit='m', help='WSRT telescope diameter', origin='test')
        Xbeam.parm ('lambda', default=Expression('3e8/[f]', label='lambda',
                                                 descr='observing wavelength'), unit='m')
        Xbeam.parm ('_ell', default=0.1, help='Voltage beam elongation factor (1+ell)', origin='test')
        # Xbeam.display(full=True)
        # Xbeam.display(full=False)
        # Xbeam.expanded().display(full=True)
        Xbeam.expanded().display(full=False)
        # Xbeam.plot()

        if 0:
            Xbeam.expanded().make_cells(t=dict(nr=2),l=dict(nr=5),m=dict(nr=3))
            Xbeam.expanded().Funklet(plot=True)

        if 1:
            Ybeam = Xbeam.copy(label='gaussYbeam', descr='WSRT Y voltage beam (gaussian)')
            Ybeam.parm ('_ell', default=-0.1, help='Voltage beam elongation factor (1+ell)')
            Ybeam.expanded().display(full=False)
            # Ybeam.plot(l=True, m=True)
            # Explot(Xbeam, Ybeam, _legend=True, l=True, m=True)
            # Xbeam.compare(Ybeam, l=True, m=True)
            diff = Expression('{Xbeam}-{Ybeam}', label='diff')
            diff.parm('Xbeam', Xbeam)
            diff.parm('Ybeam', Ybeam)
            diff.expanded().display()

        if 0:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = Xbeam.MeqCompounder(ns, qual=dict(q='3c84'), extra_axes=LM,
                                       common_axes=[hiid('l'),hiid('m')], trace=True)
            TDL_display.subtree(node, 'MeqCompounder', full=True, recurse=5)

        if 0:
            node = Xbeam.MeqFunctional(ns, qual=dict(q='3c84'), trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)
            

    if 0:
        # MXM: Bandpass function:
        mxm = Expression('{a}*([f]**{b})+{c}', label='MXM',
                         descr='MXM bandpass function')
        mxm.parm('a', 2.3, polc=[2,1], help='a')
        # mxm.parm('b', 1.1, polc=[2,1], help='b')
        mxm.parm('b', 1.1, help='b')
        mxm.parm('c', -4.5, polc=[4,3], unit='kg/m', help='c')
        mxm.var('t', 100)
        mxm.var('f', 200, testinc=13)
        mxm.expanded().display('expanded mxm', full=True)
        mxm.display('mxm', full=True)
        # mxm.plot(_test=True)
        mxm.plot(f=dict(min=100, max=200), b=dict(min=1, max=2, nr=5))
        
    if 0:
        # Elliptic gaussian source:
        attuv = Expression('exp(-({Uterm}**2)-({Vterm}**2))', label='attuv',
                           descr='elliptic gaussian source attenuation factor(u,v)')
        # Uterm = Expression('exp(-{Uterm}-{Vterm})', label='Uterm')
        urot = Expression('{_major_axis}*({_u}*{cospa}-{_v}*{sinpa})', label='urot')
        vrot = Expression('{_minor_axis}*({_u}*{sinpa}+{_v}*{cospa})', label='vrot')

        attuv.parm('Uterm', urot)
        attuv.parm('Vterm', vrot)

        uvquals = dict(s1=3,s2=5)
        ucoord = ns.ucoord(**uvquals) << 1
        vcoord = ns.vcoord(**uvquals) << 1
        attuv.parm('_u', ucoord, unit='wvl', help='u-coordinate')
        attuv.parm('_v', vcoord, unit='wvl', help='v-coordinate')

        qqual = ['3c56']
        major = ns.major_axis(*qqual) << Meq.Parm(0.1)
        minor = ns.minor_axis(*qqual) << Meq.Parm(0.01)
        pa = ns.posangle(*qqual) << Meq.Parm(-0.1)
        cospa = Expression('cos({_posangle})', label='cospa')
        sinpa = Expression('sin({_posangle})', label='sinpa')

        attuv.parm('cospa', cospa, recurse=True, help='cos(posangle)')
        attuv.parm('sinpa', sinpa, recurse=True, help='sin(posangle)')
        group = 'source_shape'
        attuv.parm('_posangle', pa, unit='rad', group=group, help='source position angle (rad)')
        attuv.parm('_major_axis', major, unit='rad', group=group, help='source major axis (rad)')
        attuv.parm('_minor_axis', minor, unit='rad', group=group, help='source minor axis (rad)')

        if 1:
            node = attuv.MeqFunctional(ns, qual=dict(q='3c84'), trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)
            klasses = classwise(node, trace=True)

        attuv.display('attuv', full=True)
        attuv.expanded().display('expanded attuv', full=True)
        attuv.plot()

    #--------------------------------------------------------------------------
    # Tests of standalone helper functions:
    #--------------------------------------------------------------------------

        
    if 0:
        fp = polc_Expression([2,1], 56, trace=True)
        print fp.parm_order()
        if False:
            fp.parm(fp.parm_order()[1], 34)
            fp.display(full=True)
        fp2 = polc_Expression([1,2], 56, trace=True)
        fp.parm(fp.parm_order()[1], fp2)
        fp.expand()
        fp.display(full=True)

    if 0:
        vv = array(range(10))
        vv = 12 - vv + 3*(vv**2) - 14.5*(vv**4)
        if True:
            fit = dict(vv=vv, t=range(10))
            fp = polc_Expression([6,1], fit=fit, trace=True)
        else:
            fit = dict(vv=vv, f=range(10))
            fp = polc_Expression([1,5], fit=fit, trace=True)
        fp.display()

    if 0:
        fp = polc_Expression([1,4], [1,0,0,2], type='MeqPolcLog', trace=True, plot=True)
        # fp.plot(f=dict(min=1e7, max=1e9, nr=100))

    if 0:
        fp = polc_Expression([1,3], [10**1.766,0.447, -0.148],
                             type='MeqPolcLog', label='3c147',
                             trace=True, plot=False)
        fp.plot(f=dict(min=1e7, max=1e9, nr=100))

    if 0:
        fp = polc_Expression([0,0], 56, trace=True)
        fp = polc_Expression([1,1], 56, trace=True)
        fp = polc_Expression([2,2], 56, trace=True)
        fp = polc_Expression([1,2], 56, trace=True)
        fp = polc_Expression([2,1], 56, trace=True)
        fp = polc_Expression([3,2], 56, trace=True)
        fp = polc_Expression([2,3], 56, trace=True)


    #===============================================================================

    if 0:
        e0 = Expression(ns, 'e0')
        e0.display()
        if 0:
            print '** dir(e0) ->',dir(e0)
            print '** e0.__doc__ ->',e0.__doc__
            print '** e0.__str__() ->',e0.__str__()
            print '** e0.__module__ ->',e0.__module__
            print

    if 0:
        # e1 = Expression(ns,'e1','{A}+{B')
        # e1 = Expression(ns,'e1','45')
        e1 = Expression(ns,'e1','xx')
        e1.display()

    if 0:
        e0 = Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}')
        e0.parm('{a}', '[f]*{c}/{b}+{d}')
        e0.parm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
        e0.parm('{c}', 47)
        e0.parm('{d}', (ns << Meq.Parm(-56)))
        e0.parm('{f}', 'MeqParm', default=-56)
        if True:
            e1 = Expression(ns,'e1','{A}+{B}/[m]')
            e1.parm('{A}', 45)
            e1.parm('{B}', -45)
            e0.parm('{e}', e1)
        e0.display()
        if 1:
            e0.MeqNode()
            e0.display()
        if 0:
            e0.MeqParm()
            e0.display()
        if 0:
            e0._vars2nodes()
            e0.display()
        if 0:
            e0._parms2nodes()
            e0.display()
        if 0:
            e0.MeqFunctional(show=True)
            e0.display()

    if 0:
        e2 = Expression(ns, 'e2', '{a}*[t]-{a}**{f}')
        e2.parm('{a}', '[f]*{c}/{b}+{d}')
        e2.parm('{b}', 447)
        e2.parm('{c}', 47)
        e2.parm('{d}', (ns << Meq.Parm(-56)))
        e2.parm('{f}', 'MeqParm', default=-56)
        e2.display()
        if 0:
            e2.MeqNode()
            e2.display()
        if 1:
            e2.MeqParm()
            e2.display()
        if 0:
            e2.Funklet()
            e2.display()
        if 0:
            e2.MeqCompounder(show=True)
            e2.display()

    if 1:
        e4 = Expression(ns, 'e4', '[l]-[m]')
        e4.display()
        if 1:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e4.MeqCompounder(extra_axes=LM,
                                    common_axes=[hiid('l'),hiid('m')],
                                    show=True)
            e4.display()


    print '\n*******************\n** End of local test of: Expression.py:\n'




#============================================================================================
# Remarks:
#
# - MXM cannot interprete pk for k>9. Use C[k] (and X[n]) instead?
#
# - Funklets cannot handle purely numeric expressions (e.g. '67')
#
# - after Funklet.setCoeff(..), call .init_function()
#   NB: Convert coeff to float automatically...!
#
# - 


#============================================================================================

    
