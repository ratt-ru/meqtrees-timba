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
        self._locked = False                      # if true, do not modify

        # For each parameter in self._expression, make an entry in self._item.
        # These entries may be modified with extra info by self.parm().
        self._item = dict()
        self._item_order = []
        self._find_items(self._expression)

        # Some placeholders:
        self._MeqNode = None
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

    def item_order (self):
        """Return the order of parameters in the input expression"""
        return self._item_order


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
        if self._locked:
            ss += '  (locked) '
        return ss

    #----------------------------------------------------------------

    def display(self, full=False):
        """Display a summary of this object"""
        print '\n** Summary of: '+self.oneliner()
        print '  * description: '+str(self._descr)
        print '  * expression: '+str(self._expression)
        print '  * items ('+str(len(self._item))+'):'
        self._adjust_item_order()
        for key in self.item_order():
            rr = self._item[key]
            print '    - '+str(key)+':  ('+str(rr['type'])+'):  '+str(rr['item']),
            if rr['type']=='var':
                print '  '+str(rr['var']),
            if rr.has_key('from'):
                print '  <- '+str(rr['from']),
            print
        if full:
            for key in self.item_order():
                print '    - '+str(key)+':  '+str(self._item[key])
        v = self._testeval()
        print '  * testexpr: '+str(self._testexpr)
        print '    - .testeval() ->  '+str(v)+'  ('+str(type(v))+')'
        print '  * expanded: '+str(self._expanded)
        for itemtype in ['MeqNode']:
            print '    - .has_itemtype('+str(itemtype)+') -> '+str(self.has_itemtype(itemtype))
        print '  * MeqNode = '+str(self._MeqNode)
        print '  * Funklet = '+str(self._Funklet)
        print '    - function = '+str(self._Funklet_function)
        print '  * Functional = '+str(self._Functional)
        print '    - function = '+str(self._Functional_function)
        print '  * Compounder = '+str(self._Compounder)
        print '    - common_axes = '+str(self._Compounder_common_axes)
        print '**\n'
        return True
        
    #-------------------------------------------------------------------------

    def _adjust_item_order(self):
        """Helper function to order the various items in categories"""
        order = []
        for it in ['subexpr','parm','MeqParm','MeqNode','var','numeric']:
            for key in self._item_order:
                if self._item[key]['type']==it: order.append(key)
        for key in self._item_order:
            if not key in order: order.append(key)
        self._item_order = order
        return True
        
    #============================================================================
    # Functions dealing with items, i.e. {parms} and [vars]:
    #============================================================================

    def _find_items (self, expr=None, trace=False):
        """Find the parameters (enclosed in {}) in the given expression string,
        and add them to self._item, avoiding duplication. By default, the parm
        items are of type 'parm', which will be turned into Funklets or MeqParms
        when necessary. They may be re-specified as something else by means of
        the function .parm().
        Also find the vars (enclosed in []) in the expression, and add them to
        self._item. These may be re-specified with the function .var()."""
        order = JEN_parse.find_enclosed(expr, brackets='{}')
        if not isinstance(order,(list,tuple)):
            s = '** order is not a list, but: '+str(type(order))
            raise TypeError,s
        for key1 in order:
            key = '{'+key1+'}'
            if not self._item.has_key(key):
                self._item[key] = dict(type='parm', item=None, index=[0],
                                       unit=None, default=2.0)
                self._item_order.append(key)
        self._find_vars(expr)       # Do the same for the vars [] in expr
        return True

    #-------------------------------------------------------------------------

    def _transfer_items (self, other=None, trace=False):
        """Transfer the items from the given (other) Expression object,
        and add them to self._item.
        - If a var item [] already exists, ignore the one from other.
        - If a parm item {} already exists, raise an error.
        """
        for key in other.item_order():
            if self._item.has_key(key):
                if key[0]=='{':
                    s = 'item {} already defined: '+str(key)
                    raise ValueError, s
            else:
                self._item[key] = other._item[key]
                self._item_order.append(key)
        # Finished: 
        return True

    #-------------------------------------------------------------------------

    def has_itemtype (self, itemtype='MeqNode', expr=None):
        """Helper function to test whether the given expr has any 'items' {}
        of the specified itemtype (default='MeqNode'). * is all types."""
        cc = []
        if expr==None: expr = self._expanded
        for key in self._item.keys():
            if key in expr:
                if itemtype=='*' or self._item[key]['type']==itemtype:
                    cc.append(key)
        if len(cc)==0: return False
        return cc

    #----------------------------------------------------------------------------

    def parm (self, key, item=None, arg=None, polc=None,
              redefine=False, unlock=False, **pp):
        """Define an existing {key} parameter as a numeric value, an expression,
        a MeqParm or another MeqNode, etc"""

        # First some checks:
        if self._locked and not unlock:
            s = '** Expression is locked: can no longer be modified'
            raise ValueError, s
        if not self._item.has_key(key):
            s = '** parameter key not recognised: '+str(key)
            raise ValueError, s
        rr = self._item[key]

        # Unless specified explicitly, only allow redefinition of the
        # 'undefined' items, i.e. the ones with the default type 'parm'
        if not redefine:
            if not rr['type']=='parm':
                s = '** duplicate definition of parameter: '+str(key)
                raise ValueError, s

        # Some types require extra arguments:
        if not isinstance(pp, dict): pp = dict()

        # OK, go ahead:
        if item==None:
            # Assume item-type=='parm' (i.e. undefined).
            # Just supply a new default/test value
            if not pp.has_key('default'):
                raise ValueError,'** parm needs default=value'
            rr['default'] = float(pp['default'])

        elif item=='MeqParm':
            if not pp.has_key('default'):
                if isinstance(arg, (int, long, float)):
                    pp['default'] = arg
                else:
                    raise ValueError,'** MeqParm needs a default value'
            rr['item'] = self.ns[key] << Meq.Parm(**pp)  # use Meow....
            rr['type'] = 'MeqNode'
            if isinstance(pp['default'], (int, long, float)):
                rr['default'] = float(pp['default'])

        elif isinstance(item, str):                      # assume sub-expr
            rr['item'] = item
            rr['type'] = 'subexpr'
            self._find_items(item)

        elif isinstance(item, (int, long, float, complex)):
            rr['item'] = item
            rr['type'] = 'numeric'

        elif is_node(item):
            rr['item'] = item
            rr['type'] = 'MeqNode'
            if item.classname=='MeqParm':
                rr['default'] = item.initrec()['init_funklet']['coeff']
            elif item.classname=='MeqConstant':          # ....?
                rr['value'] = item.initrec()['value']

        elif isinstance(item, Funklet):
            rr['item'] = item
            rr['type'] = 'Funklet'
            # qnode << Meq.Parm(funklet=funklet,       # new MXM 28 June 2006
            #                       node_groups=['Parm'])

        elif isinstance(item, Expression):
            expr = item._expand()                        # ....??
            rr['item'] = expr
            rr['type'] = 'subexpr'
            rr['from'] = 'Expression: '+str(item.name)
            self._transfer_items(item)

        else:
            s = '** parameter type not recognised: '+str(type(item))
            raise TypeError, s

        # Finished:
        return True


    #============================================================================
    # Functions dealing with variables []:
    #============================================================================

    def var (self, key, xn=None, axis=None, unit=None, nodeclass=None):
        """Specify fields of the var-record in the item definition record.
        This is used for non-standard varaibles, i.e. other than the ones
        (like [t],[f] etc) that are recognised in _find_vars()"""

        if not key in self._item:
            s ='** variable not recognised: '+str(key)
            raise ValueError, s
        elif key in ['[t]','[f]','[l]','[m]']:
            s ='** standard variable cannot be modified: '+str(key)
            raise ValueError, s                   # <-- ??
        
        # Only replace the specified fields:
        rr = self._item[key]
        if isinstance(nodeclass, str):
            rr['var']['nodeclass'] = nodeclass    # default: 'MeqGrid'
        if isinstance(xn, str):
            rr['var']['xn'] = xn                  # e.g. 'x2' or 'x7'
        if isinstance(axis, str):
            rr['var']['axis'] = axis              # e.g. 'x' or 'lat'
        if isinstance(unit, str):
            rr['unit'] = unit                     # e.g. 'rad'
        return True

    #----------------------------------------------------------------------------

    def _find_vars (self, expr=None):
        """Find the variables (enclosed in []) in the given expression string,
        and add them to self._item, avoiding duplication"""
        vv = JEN_parse.find_enclosed(expr, brackets='[]')
        for key in vv:
            key = '['+key+']'
            if not self._item.has_key(key):
                rr = dict(type='var', item=None, index=[0],
                          unit=None, default=10.0)
                var = dict(nodeclass='MeqGrid', xn='xn', axis=None)
                # Deal with some standard variables:
                if key=='[t]':                      # time
                    var['nodeclass'] = 'MeqTime' 
                    var['xn'] = 'x0'                # used in Funklet
                    var['axis'] = 'time'            # used in MeqKernel
                    rr['unit'] = 's'
                elif key=='[f]':                    # freq
                    var['nodeclass'] = 'MeqFreq'  
                    var['xn'] = 'x1'
                    var['axis'] = 'freq'            # used in MeqKernel
                    rr['unit'] = 'Hz'
                elif key=='[l]':                    # celestial l-coordinate
                    var['nodeclass'] = 'MeqGrid'   
                    var['axis'] = 'l'               # used in MeqKernel
                    var['xn'] = 'x2'                # .....!?
                    rr['unit'] = 'rad'
                elif key=='[m]':                    # celestial m-coordinate
                    var['nodeclass'] = 'MeqGrid'  
                    var['axis'] = 'm'               # used in MeqKernel
                    var['xn'] = 'x3'                # .....!?
                    rr['unit'] = 'rad'
                rr['var'] = var                     # attach the var definition record
                self._item[key] = rr                # attach the item definition record
                self._item_order.append(key)        # include the key
        # Finished
        return True

    #-------------------------------------------------------------------------------

    def _nodes2vars (self):
        """The reverse of _vars2nodes(). Just change the item-type of the
        items that represent variables [] from 'MeqNode' to 'var'."""
        for key in self.item_order():
            rr = self._item[key]                           # item definition record
            if rr.has_key('var'):                          # var definition record
                rr['type'] = 'var'                         # just change type to var
        return True

    #-------------------------------------------------------------------------------
    
    def _vars2nodes (self):
        """Change the item-type of the variables from 'var' to 'MeqNode',
        while creating MeqGrid nodes for them if necessary."""
        expr = self._expand()
        for key in self.item_order():
            rr = self._item[key]                           # item definition record
            if rr.has_key('var'):                          # var definition record
                if not rr['item']:                         # only if not yet defined
                    nodeclass = rr['var']['nodeclass']     # e.g. 'MeqTime'
                    axis = rr['var']['axis']               # e.g. 'freq', or 'm'
                    qnode = self.ns[key]
                    if nodeclass=='MeqTime':
                        qnode << Meq.Time()
                    elif nodeclass=='MeqFreq':
                        qnode << Meq.Freq()
                    elif nodeclass=='MeqGrid':
                        qnode << Meq.Grid(axis=axis)
                    else:
                        s = 'nodeclass not recognised:'+str(nodeclass)
                        raise TypeError,s
                    rr['item'] = qnode                     # attach the node
                # Just change the item type:
                rr['type'] = 'MeqNode'
        # Finished:
        self._locked = True                                # no more modifications
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
            for key in self.item_order():
                rr = self._item[key]
                if rr['type']==None:
                    s = '** expand(): parameter not yet defined: '+str(key)
                    raise ValueError, s  
                elif rr['type']=='subexpr':
                    if key in expr:
                        subexpr = '('+rr['item']+')'
                        expr = expr.replace(key, subexpr)
                        if trace:
                            print '**',count,': replace:',key,' with:',subexpr
                        repeat = True
                elif replace_numeric and rr['type']=='numeric':
                    expr = expr.replace(key, '('+str(rr['item'])+')')
            # Guard against an infinite loop:
            if count>10:
                print '\n** current expr =',expr
                s = '** expand(): maximum count exceeded '+str(count)
                raise ValueError, s
        # Finished:    
        self._expanded = expr
        self._locked = True                              # no more modifications
        return expr

    #---------------------------------------------------------------------------

    def _testeval(self, trace=False):
        """Test-evaluation of its expression, in which all the non-numeric
        parameters have been replaced with their test-values. This is primarily
        a syntax check (brackets etc), but it may have other uses too"""
        expr = self._expand(replace_numeric=True)
        for key in self.item_order():
            if key in expr:
                replace = '('+str(self._item[key]['default'])+')'
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
            self._vars2nodes()        
            function = deepcopy(self._expanded)
            children = []
            nodenames = []
            child_map = []                                      # for MeqFunctional
            k = -1
            for key in self.item_order():
                rr = self._item[key]                            # item definition record
                if rr['type'] in ['MeqNode','MeqParm']:
                    k += 1                                      # increment
                    xk = 'x'+str(k)                             # x0, x1, x2, ..
                    function = function.replace(key, xk)
                    nodename = rr['item'].name
                    if not nodename in nodenames:               # once only
                        nodenames.append(nodename)
                        children.append(rr['item'])
                    child_num = nodenames.index(nodename)       # 0-based(!)
                    qq = record(child_num=child_num,
                                index=rr['index'],              # usually: [0]
                                nodename=nodename)
                    child_map.append(qq)
            qnode << Meq.Functional(children=children,
                                    function=function,
                                    child_map=child_map)
        # Finsihed:
        self._locked = True                              # no more modifications
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
            for key in self.item_order():
                if key[0]=='[' and key in self._expanded:
                    print key,caxes
                    if not key in ['[t]','[f]']:
                        pass
                    # NB: str(hiid('m')) -> 'M'   ............!
                    #if not key in caxes:
                    #    s = '** missing cax:',key
                    #    raise ValueError, s
                
            qnode << Meq.Compounder(children=[extra_axes, node],
                                    common_axes=common_axes)
            self._Compounder = qnode
            self._Compounder_common_axes = str(common_axes)

        # Finished
        self._locked = True                              # no more modifications
        if show: display.subtree(qnode)
        return qnode

    #============================================================================

    def Funklet (self, plot=False):
        """Return the corresponding Funklet object. Make one if necessary."""

        # Avoid double work:
        if self._Funklet:
            return self._Funklet

        self._nodes2vars()        
        if self.has_itemtype ('MeqNode'):
            # If there are MeqNode children, the Expression should be turned into
            # a MeqFunctional node. It is not possible to make a Funklet.
            return False
        
        function = deepcopy(self._expanded)

        coeff = []
        k = -1
        for key in self.item_order():
            rr = self._item[key]
            if rr['type']=='parm':                     # ....!!
                # Replace the undefined parameters {} with pk = p0,p1,p2,...
                # and fill the coeff-list with their default values
                k += 1
                pk = 'p'+str(k)
                function = function.replace(key, pk)
                value = rr['default']         
                value = float(value)                   # required by Funklet...!?
                coeff.append(value)

            elif rr['type']=='var':
                # Replace the valiables [] with x0 (time), x1(freq) etc
                xn = rr['var']['xn']
                function = function.replace(key, xn) 


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

        if plot:
            # NB: The following plots WITHOUT execution!
            dom = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),l=(-0.1,0.1),m=(-0.1,0.1))
            cells = meq.gen_cells(domain=dom,num_time=4,num_freq=5, num_l=6, num_m=7)
            f0.plot(cells=cells)

        # Finished:
        self._locked = True                              # no more modifications
        self._Funklet = f0
        self._Funklet_function = function         
        return self._Funklet





    #===========================================================================
    # Turn the Expression into a node:
    #===========================================================================

    def MeqNode (self, show=False):
        """Make a single node/subtree from the Expression. In most cases,
        this will be a MeqParm, with the expression Funklet as init_funklet.
        But if the expression has at least one parameter that is a node,
        the result will be a MeqFunctional node."""

        self._nodes2vars()
        if not self.has_itemtype ('MeqNode'):
            qnode = self.ns['Expr_MeqParm']
            if not qnode.initialized():
                f0 = self.Funklet()
                if isinstance(f0, bool):
                    s = '** Funklet is '+str(type(f0))
                    raise TypeError,s
                funklet = f0.get_meqfunklet()
                print '\n** funklet =',funklet
                print dir(f0),'\n'
                if len(funklet['coeff'])==0:
                    s = '** coeff is empty'
                    raise ValueError,s
                qnode << Meq.Parm(init_funklet=funklet,       # new MXM 28 June 2006
                                  node_groups=['Parm'])
        else:
            qnode = self.ns['Expr_MeqNode']
            if not qnode.initialized():
                qnode = self.MeqFunctional()

        # Finished:
        self._MeqNode = qnode
        if show: display.subtree(qnode)
        self._locked = True                          # inhibit further modifications
        return qnode

    #--------------------------------------------------------------------------
    # MXM: 28 June 2006
    # Ok, ik heb een functie get_meqfunklet() toegevoegd, die kun je gebruiken om
    # het funklet_type object te krijgen, nodig als je het 'init_funklet' veld zelf
    # met de hand zet (zoals je nu doet in Expression). Als je Meq.Parm
    # aanroept met als eerste variable het Funklet object (of: funklet =  funklet,
    # ipv init_funklet=funklet), gaat het ook goed, de Meq.Parm functie roept dan
    # zelf get_meqfunklet() aan.
    # WEl lijkt het om vreemde import redenen niet te werken, dit komt omdat je
    # Timba.TDL niet direkt geimporteerd hebt, als je :
    #            from Timba.TDL import *
    # toevoegt werkt het.
    #--------------------------------------------------------------------------

    def _MeqParm_obsolete (self):
        """Helper function to make a MeqParm node by converting the (expanded)
        expression into a Funklet, and using that as init_funklet."""

        qnode = self.ns['Expr_MeqParm']
        if not qnode.initialized():
            f0 = self.Funklet()
            if isinstance(f0, bool):
                s = '** Funklet is '+str(type(f0))
                raise TypeError,s
            funklet = f0.get_meqfunklet()
            print '** funklet =',funklet
            print dir(f0)
            if len(funklet['coeff'])==0:
                s = '** coeff is empty'
                raise ValueError,s
            qnode << Meq.Parm(init_funklet=funklet,       # new MXM 28 June 2006
                              node_groups=['Parm'])
        # Finished
        self._locked = True                              # no more modifications
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
        for key in self._item_order:
            item = self._item[key]
            if isinstance(item, dict) and item.has_key('node'):
                classwise(item['node'], klasses=klasses, done=done)
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
    result = Expression(ns, 'p1', func,
                        descr='polc_Expression')
    result._expression_type = type

    # Define the Expression parms:
    for key in pp.keys():
        result.parm('{'+key+'}', pp[key], unit=uunit[key])

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




#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = []

    if 0:
        e0 = Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}')
        e0.parm('{a}', '[f]*{c}/{b}+{d}')
        e0.parm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
        e0.parm('{c}', 47)
        e0.parm('{d}', (ns << Meq.Parm(-56)))
        e0.parm('{f}', 'MeqParm', default=-56)
        e1 = 111
        if False:
            e1 = Expression(ns,'e1','{A}+{B}/[m]')
            e1.parm('{A}', 45)
            e1.parm('{B}', -45)
        e0.parm('{e}', e1)    
        e0.display()
    
        if 1:
            cc.append(e0.MeqNode())   
            e0.display()

        if 0:                       
            cc.append(e0.MeqFunctional(show=True))
            e0.display()


    #------------------------------------------------------------

    if 1:
        e4 = Expression(ns, 'e4', '[l]-[m]+{a}')
        e4.parm('{a}','MeqParm', default=9)
        e4.display()

        if 0:
            f0 = e4.Funklet(plot=True)
            print '** f0 =',f0

        if 1:
            LM = ns.LM << Meq.Composer(ns.L<<0.1, ns.M<<-0.2)
            node = e4.MeqCompounder(extra_axes=LM,
                                    common_axes=[hiid('l'),hiid('m')],
                                    show=True)
            cc.append(node)
            e4.display()

        if 0:
            cc.append(e4.MeqNode())   
            e4.display()


    ns.result << Meq.Composer(children=cc)
    return True

#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=1, num_time=100)
    request = meq.request(cells, rqtype='ev')
    result = mqs.meq('Node.Execute',record(name='result', request=request))
    return result
       

def _tdl_job_4D_tflm (mqs, parent):
    """Execute the forest with a 4D request (freq,time,l,m).
    NB: This does NOT work on a Compounder node!"""
    domain = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),l=(-0.1,0.1),m=(-0.1,0.1))
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

 
    #--------------------------------------------------------------------------
    # Tests of standalone helper functions:
    #--------------------------------------------------------------------------

        
    if 0:
        fp = polc_Expression([2,1], 56, trace=True)
        fp.display()
        if 1:
            fp.Funklet()
            fp.display()


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

    if 1:
        e0 = Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}')
        if False:
            e0.parm('{a}', '[f]*{c}/{b}+{d}')
            e0.parm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
            e0.parm('{c}', 47)
            e1 = 111.111
            if True:
                e1 = Expression(ns,'e1','{A}+{B}/[m]')
                e1.parm('{A}', 45)
                e1.parm('{B}', -45)
            e0.parm('{e}', e1)
            e0.parm('{d}', (ns << Meq.Parm(-56)))
            e0.parm('{f}', 'MeqParm', default=-56)
        e0.display()

        if 1:
            e0.MeqNode()
            e0.display()
        if 0:
            e0._vars2nodes()
            e0.display()
        if 0:
            e0._nodes2vars()
            e0.display()
        if 0:
            e0.MeqFunctional(show=True)
            e0.display()

    if 0:
        # e2 = Expression(ns, 'e2', '{a}*[t]-{a}**{f}+[m]+[Xat]')
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
        if 0:
            e2.Funklet()
            e2.display()
        if 0:
            e2.MeqCompounder(show=True)
            e2.display()

    if 0:
        e4 = Expression(ns, 'e4', '[l]-[m]+{p}')
        e4.parm('{p}', 'MeqParm', default=-56)
        # e4.var('[m]', xn='x10', axis='mcoord')
        e4.display()
        if 0:
            e4.MeqNode(show=True)
            e4.display()
        if 0:
            e4.MeqFunctional(show=True)
            e4.display()
        if 0:
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

    
