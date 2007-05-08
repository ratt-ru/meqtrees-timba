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
#         -) e0.modparm('{A}', 34)                         numeric, default value is 34
#         -) e0.modparm('{ampl}', e1)                      another Expression object
#         -) e0.modparm('{phase}', polc=[2,3])             A polc-type Expression generated internally
#         -) e0.modparm('{A}', f1)                         A Funklet object
#         -) e0.modparm('{A}', node)                       A node (child of a MeqFunctional node)
#         -) e0.modparm('{A}', image)                      A FITS image
#     -) The Expression object may be converted to:
#         -) a FunkletParm                                  with p0,p1,p2,... and x0,x1,...
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
from Timba.Contrib.JEN.util import JEN_bookmarks

Settings.forest_state.cache_policy = 100

# import numarray                               # see numarray.rank()
from numarray import *
from math import *
# import numarray.linear_algebra                # redefines numarray.rank....
import random
# import pylab
from copy import deepcopy
import re


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
                 quals=[], kwquals={}, **pp):
        """Create the object with a mathematical expression (string)
        of the form:  {aa}*[t]+cos({b}*[f]).
        Variables are enclosed in square brackets: [t],[f],[m],...
        Parameters are enclosed in curly brackets: {aa}, {b}, ...
        Simple information about parameters (type, default value)
        may be supplied via keyword arguments pp. More detailed
        information may be supplied via the function .modparm()."""

        Meow.Parameterization.__init__(self, ns, str(name),
                                       quals=quals, kwquals=kwquals)

        self._descr = descr                       # optional description
        self._unit = unit                         # unit of the result
        self._exprin = deepcopy(expr)             # never modified
        self._expression = deepcopy(expr)         # may be modified: {a=10~0.1} -> {a}
        self._expanded = deepcopy(expr)           # working version
        self._locked = False                      # if true, do not modify
        self._last_solvable_tags = None           # used by .solvable()

        # Default values for the variable-modification constants:
        self._var_modifier = dict(t0=0.0, f0=1.0)

        # Default values for the Meow.Parms defined in .find_items()
        self._parm_default = dict(value=2.0, stddev=0.0,
                                  tags=['MeqFunctional'],
                                  tiling=None, time_deg=0, freq_deg=0)  # **kw

        if not isinstance(pp, dict): pp = dict()
        for key in self._parm_default.keys():
            if pp.has_key(key):
               self._parm_default[key] = pp[key] 

        # For each parameter in self._expression, make an entry in self._item.
        # These entries may be modified with extra info by self.modparm().
        self._item = dict()
        self._item_order = []
        self._expression = self._find_items(self._expression)

        # Some placeholders:
        self._MeqNode = None
        self._FunckDiff = None
        self._FunkletParm = None
        self._Funklet = None
        self._Funklet_funktion = None
        self._MeqFunctional = None
        self._MeqFunctional_function = None
        self._MeqFunctional_childmap = []
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

    def display(self, txt=None, full=False):
        """Display a summary of this object"""
        print '\n** Summary of: '+self.oneliner(),
        if txt: print '  (*** '+str(txt)+' ***)',
        print
        print '  * description: '+str(self._descr)
        print '  * expression: '+str(self._expression)
        if not self._exprin==self._expression:
            print '    - exprin: '+str(self._exprin)
        #..........................................................
        print '  * items ('+str(len(self._item))+'):'
        self._adjust_item_order()
        for key in self.item_order():
            rr = self._item[key]
            print '    - '+str(key)+':  ('+str(rr['type'])+'):  '+str(rr['item']),
            if rr['type']=='parm':
                s1 = '  default='+str(rr['default'])
                if rr['stddev']>0: s1 += '  stddev='+str(rr['stddev'])
                print s1,
            if rr['type']=='var':
                print '  '+str(rr['var']),
            if rr.has_key('unit') and rr['unit']:
                print '  unit='+str(rr['unit']),
            if rr.has_key('from'):
                print '  <- '+str(rr['from']),
            print
        if full:
            for key in self.item_order():
                print '    - '+str(key)+':  '+str(self._item[key])
        #..........................................................
        print '  * parm_default: '+str(self._parm_default)
        print '  * var_modier: '+str(self._var_modifier)
        #..........................................................
        print '  * last_solvable_tags: '+str(self._last_solvable_tags)
        cc = self.solvable()
        ncc = len(cc)
        print '    - .solvable(): -> '+str(ncc)
        if full or ncc<5:
            for k,c in enumerate(cc):
                print '    - '+str(k)+': '+str(c)
        else:
            print '    - '+str(0)+': '+str(cc[0])
            print '         ...'
            print '    - '+str(ncc-1)+': '+str(cc[ncc-1])
        #..........................................................
        v = self._testeval()
        print '  * testexpr: '+str(self._testexpr)
        print '    - .testeval() ->  '+str(v)+'  ('+str(type(v))+')'
        #..........................................................

        nmax = 100
        if len(self._expanded)>nmax: print
        print '  * expanded: '+str(self._expanded)
        if len(self._expanded)>nmax: print

        if full:
            for itemtype in ['node']:
                print '    - .has_itemtype('+str(itemtype)+') -> '+str(self.has_itemtype(itemtype))
        if self._MeqNode:
            print '  * MeqNode = '+str(self._MeqNode)
        if self._FunckDiff:
            print '  * FunckDiff = '+str(self._FunckDiff)
        if self._FunkletParm or self._Funklet:
            print '  * FunkletParm = '+str(self._FunkletParm)
            print '  * Funklet = '+str(self._Funklet)
            print '    - funktion = '+str(self._Funklet_funktion)
        if self._MeqFunctional:
            print '  * MeqFunctional = '+str(self._MeqFunctional)
            print '    - function = '+str(self._MeqFunctional_function)
            cc = self._MeqFunctional_childmap
            ncc = len(cc)
            if full or ncc<5:
                for k,c in enumerate(cc):
                    print '    - '+str(k)+': '+str(c)
            else:
                print '    - '+str(0)+': '+str(cc[0])
                print '         ...'
                print '    - '+str(ncc-1)+': '+str(cc[ncc-1])
                
        if self._Compounder:
            print '  * Compounder = '+str(self._Compounder)
            print '    - common_axes = '+str(self._Compounder_common_axes)
        print '**\n'
        return True
        
    #-------------------------------------------------------------------------

    def _adjust_item_order(self):
        """Helper function to order the various items in categories"""
        order = []
        for it in ['subexpr','parm','node','var','numeric']:
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
        the function .modparm().
        Also find the vars (enclosed in []) in the expression, and add them to
        self._item. These may be re-specified with the function .modvar()."""

        order = JEN_parse.find_enclosed(expr, brackets='{}', enclose=False)
        if not isinstance(order,(list,tuple)):
            s = '** order is not a list, but: '+str(type(order))
            raise TypeError,s

        pp = self._parm_default
        tags = pp['tags']
        if not isinstance(tags,(list,tuple)):
            tags = [tags]
        if not 'MeqFunctional' in tags:
            tags.append('MeqFunctional')
        
        for unenc in order:                   # still unenclosed, e.g. 'a'
            default = pp['value']
            stddev = pp['stddev']

            # The key may contain optional information about the
            # default value and the stddev: e.g. {a=10~0.5}
            kk = unenc.split('=')
            key = '{'+kk[0]+'}'               # enclose: -> {a}
            expr = expr.replace('{'+unenc+'}', key)
            if len(kk)>1:                     # default value specified
                vv = kk[1].split('~')
                default = float(vv[0])        # default = 10.0
                if len(vv)>1:                 # stddev (~) specified
                    stddev = float(vv[1])     # stddev = 0.5

            # If stddev specified, perturb the default value:
            if stddev>0.0:
                default = random.gauss(default, stddev)

            # Create the new item (if it does not exist already!)
            if not self._item.has_key(key):
                self._item[key] = dict(type='parm', item=None,
                                       index=[0], unit=None,
                                       default=default, stddev=stddev)
                parmdef = Meow.Parm(value=default, tags=tags,
                                    tiling=pp['tiling'],
                                    time_deg=pp['time_deg'],
                                    freq_deg=pp['freq_deg'])           # **kw
                self._add_parm(key, parmdef, solvable=True) 
                self._item_order.append(key)

        # Do someting similar for the vars [] in expr
        return self._find_vars(expr)

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

    def has_itemtype (self, itemtype='node', expr=None):
        """Helper function to test whether the given expr has any 'items' {}
        of the specified itemtype (default='node'). * is all types."""
        cc = []
        if expr==None: expr = self._expanded
        for key in self._item.keys():
            if key in expr:
                if itemtype=='*' or self._item[key]['type']==itemtype:
                    cc.append(key)
        if len(cc)==0: return False
        return cc

    #----------------------------------------------------------------------------

    def modparm (self, key, item=None, arg=None,
                 polc=None,
                 redefine=False, unlock=False, **pp):
        """Modify the definition of an existing {key} parameter as:
        - a numeric value
        - an Expression
        """

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
        ## self._parm_default = dict(tiling=None, time_deg=0, freq_deg=0)  # **kw

        # OK, go ahead:
        if item==None:
            # Just supply a new (numeric!) default value
            # Assume item-type=='parm' (i.e. undefined).......
            if not pp.has_key('default'):
                raise ValueError,'** parm needs default=value'
            rr['default'] = float(pp['default'])

        elif isinstance(item, str):                      # assume sub-expr
            rr['type'] = 'subexpr'
            rr['item'] = self._find_items(item)          # item(expr) may be modified!

        elif isinstance(item, (int, long, float, complex)):
            rr['item'] = item
            rr['type'] = 'numeric'

        elif is_node(item):
            rr['item'] = item
            rr['type'] = 'node'
            if item.classname=='MeqParm':
                rr['default'] = item.initrec()['init_funklet']['coeff']
            elif item.classname=='MeqConstant':          # ....?
                rr['value'] = item.initrec()['value']

        elif isinstance(item, Expression):
            expr = item._expand()                        # ....??
            rr['item'] = expr
            rr['type'] = 'subexpr'
            rr['from'] = 'Expression: '+str(item.name)
            self._transfer_items(item)

        else:
            s = '** parameter type not recognised: '+str(type(item))
            raise TypeError, s

        # Some input parameters:
        for key in ['unit']:
            if pp.has_key(key):
                rr[key] = pp[key]

        # Finished:
        return True


    #============================================================================
    # Functions dealing with variables []:
    #============================================================================

    def modvar (self, key, xn=None, axis=None, unit=None, nodeclass=None):
        """Modify the definition of the variable item [key]."""

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
            rr['var']['funktion'] = xn            # e.g. 'x2' or 'x7'
        if isinstance(axis, str):
            rr['var']['axis'] = axis              # e.g. 'x' or 'lat'
        if isinstance(unit, str):
            rr['unit'] = unit                     # e.g. 'rad'
        return True

    #----------------------------------------------------------------------------

    def _find_vars (self, expr=None):
        """Find the variables (enclosed in []) in the given expression string,
        and add them to self._item, avoiding duplication"""
        vv = JEN_parse.find_enclosed(expr, brackets='[]', enclose=False)
        for key in vv:
            kk = key.split('^')                     # e.g. t^4
            key = '['+key+']'
            key0 = '['+kk[0]+']'                    # e.g. [t]
            
            if not self._item.has_key(key):
                rr = dict(type='var', item=None, index=[0],
                          unit=None, default=10.0)
                var = dict(nodeclass='MeqGrid', key0=key0,
                           axis=None, funktion=None)

                
                # Deal with some standard variables:
                if key=='[t]' or key=='[dt]':                
                    var['nodeclass'] = 'MeqTime' 
                    var['funktion'] = 'x0'          # used in Funklet
                    var['axis'] = 'time'    
                    rr['unit'] = 's'
                    if key=='[dt]':                 # relative time (t-t0)
                        t0 = self._var_modifier['t0']     
                        var['subtract'] = t0
                        var['funktion'] = '(x0-'+str(t0)+')'
                elif key=='[f]' or key=='[ff]':              
                    var['nodeclass'] = 'MeqFreq'  
                    var['funktion'] = 'x1'          # used in Funklet
                    var['axis'] = 'freq'    
                    rr['unit'] = 'Hz'
                    if key=='[ff]':                 # normalized freq (f/f0)
                        f0 = self._var_modifier['f0']     
                        var['divide'] = f0
                        var['funktion'] = '(x1/'+str(f0)+')'
                elif key=='[l]':                    # celestial l-coordinate
                    var['nodeclass'] = 'MeqGrid'   
                    var['funktion'] = 'x2'          # used in Funklet
                    var['axis'] = 'l'      
                    rr['unit'] = 'rad'
                elif key=='[m]':                    # celestial m-coordinate
                    var['nodeclass'] = 'MeqGrid'  
                    var['funktion'] = 'x3'          # used in Funklet
                    var['axis'] = 'm'        
                    rr['unit'] = 'rad'

                # Variables can be functions of the basic one
                elif len(kk)>1:                     # e.g. [t^4]
                    var['nodeclass'] = 'MeqPow'     # for MeqFunctional
                    var['power'] = int(kk[1])
                    rr['unit'] = str(self._item[key0]['unit'])+'^'+kk[1]
                    funktion = self._item[key0]['var']['funktion']       # e.g. [t]
                    funktion = '('+str(funktion)+'**'+kk[1]+')'          # e.g. ([t]**4)
                    var['funktion'] = funktion      # used in Funklet

                rr['var'] = var                     # attach the var definition record
                self._item[key] = rr                # attach the item definition record
                self._item_order.append(key)        # include the key
        # Finished
        return expr

    #-------------------------------------------------------------------------------

    def _nodes2vars (self):
        """The reverse of _vars2nodes(). Just change the item-type of the
        items that represent variables [] from 'node' to 'var'."""
        for key in self.item_order():
            rr = self._item[key]                           # item definition record
            if rr.has_key('var'):                          # var definition record
                rr['type'] = 'var'                         # just change type to var
        return True

    #-------------------------------------------------------------------------------
    
    def _vars2nodes (self):
        """Change the item-type of the variables from 'var' to 'node',
        while creating MeqGrid nodes for them if necessary."""
        expr = self._expand()
        for key in self.item_order():
            rr = self._item[key]                           # item definition record
            if rr.has_key('var'):                          # var definition record
                if not rr['item']:                         # only if not yet defined
                    var = rr['var']
                    nodeclass = var['nodeclass']           # e.g. 'MeqTime'
                    key0 = var['key0']                     # e.g. [t]
                    axis = var['axis']                     # e.g. 'freq', or 'm'
                    qnode = self.ns[key]
                    if nodeclass=='MeqTime':
                        if var.has_key('subtract') and var['subtract']:
                            tnode = self.ns['[t]'] << Meq.Time()
                            qnode << Meq.Subtract(tnode,var['subtract'])
                        else:
                            qnode << Meq.Time()
                    elif nodeclass=='MeqFreq':
                        if var.has_key('divide') and var['divide']:
                            fnode = self.ns['[f]'] << Meq.Freq()
                            qnode << Meq.Divide(fnode,var['divide'])
                        else:
                            qnode << Meq.Freq()
                    elif nodeclass=='MeqGrid':
                        qnode << Meq.Grid(axis=axis)
                    elif nodeclass=='MeqPow':
                        node = self._item[key0]['item']    # e.g. MeqTime
                        power = var['power']               # e.g. 2
                        qnode << Meq.Pow(node,power)   

                    else:
                        s = 'nodeclass not recognised:'+str(nodeclass)
                        raise TypeError,s

                    rr['item'] = qnode                     # attach the node
                # Just change the item type:
                rr['type'] = 'node'
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
                                    

    #===========================================================================
    # Turn the Expression into a single node/subtree:
    #===========================================================================

    def MeqNode (self, show=False):
        """Make a single node/subtree from the Expression. In most cases,
        this will be a FunkletParm, i.e. a MeqParm with the expression Funklet
        as init_funklet. But if the expression has at least one parameter that
        is an actual node, the result will be a MeqFunctional node."""

        self._nodes2vars()
        if self.has_itemtype ('node'):
            # As soon as some parm items are nodes, it is no longer
            # possible to turn the Expression into a Funklet. So if
            # the latter is required, it should be done BEFORE the
            # function .MeqFunctional() is called....
            # In any case, return a Functional here:
            qnode = self.MeqFunctional()

        elif self.has_itemtype ('parm'):
            qnode = self.FunkletParm()

        elif self.has_itemtype ('var'):
            # Special case: only variables [] in the expression.
            # Since a Funklet requires at least one 'parm', make
            # a MeqFunctional after turning the vars into MeqGrid nodes.
            qnode = self.MeqFunctional()

        else:
            s = 'cannot make a MeqNode...'
            raise ValueError,s

        # Finished:
        self._MeqNode = qnode
        self._locked = True                      # inhibit further modifications
        if show: display.subtree(qnode)
        return qnode

    
    #--------------------------------------------------------------------

    def FunckDiff (self, show=False):
        """Make s subtree for the difference between the FunkletParm
        and the MeqFunctional"""
        qnode = self.ns['FunckDiff']
        if not qnode.initialized():
            c1 = self.FunkletParm()              # this one FIRST!
            c2 = self.MeqFunctional()
            qnode << Meq.Subtract(c1,c2)
        self._FunckDiff = qnode
        if show: display.subtree(qnode)
        return qnode

    #=====================================================================

    def solvable (self, tags='last', trace=False):
        """Return a list of solvable MeqParm nodes. If tags='last',
        it will use the tags of the MeqParm(s) that were generated
        in the last operation (e.g. MeqNode() or MeqFunctional()."""

        tagsin = deepcopy(tags)

        # See above:
        if tags=='last':
            tags = self._last_solvable_tags     # NB: ==None initially

        # It is possible to limit the search to a subtree:
        subtree = None
        if tags=='MeqFunctional':
            subtree = self._MeqFunctional
        elif tags=='FunkletParm':
            subtree = self._FunkletParm
            
        ss = self.ns.Search(class_name='MeqParm', tags=tags,
                            subtree=subtree,
                            return_names=False)
        if trace:
            print '\n** solvable(',tagsin,tags,' subtree='+str(subtree),'):',type(ss)
            if isinstance(ss,(list,tuple)):
                for s in ss: print '-',str(s)
            print
        return ss



    #============================================================================
    # Turn the Expression into a MeqFunctional node:
    #============================================================================

    def MeqFunctional (self, show=False):
        """Turn the expression into a MeqFunctional node,
        i.e. an expression of its children."""

        self._vars2nodes()        
        qnode = self.ns['Expr_MeqFunctional']
        if not qnode.initialized():
            function = deepcopy(self._expanded)
            children = []
            nodenames = []
            child_map = []            
            k = -1
            for key in self.item_order():
                if key in self._expanded:                           # extra check...
                    rr = self._item[key]                            # item definition record
                    if rr['type']=='parm':                          # undefined item
                        rr['type'] = 'node'                         # turn into MeqParm node
                        rr['item'] = self._parm(key)                # Meow (Parameterization)

                    if rr['type']=='node':
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
            function = self._adjust_functions(function)              # deal with log(..) etc
            qnode << Meq.Functional(children=children,
                                    testval=self._testeval(),
                                    function=function,
                                    child_map=child_map)
            self._MeqFunctional = qnode
            self._MeqFunctional_childmap = child_map
            self._MeqFunctional_function = function

        # Finished:
        self._last_solvable_tags = 'MeqFunctional'          # used by .solvable()
        self._locked = True                                 # no more modifications
        if show: display.subtree(qnode)
        return qnode


    #============================================================================

    def _adjust_functions (self, expr, trace=True):
        """Helper function to replace functions like sinh(...) in the given expr
        with versions that can not be evaluated in a Funklet expression."""

        ff = JEN_parse.find_function (expr, func='log', trace=False)
        # ff is a list of dict(substring='sin(..)', arg='..')
        for rr in ff:
            old = rr['substring']
            # new = '('+old+'/log(10))'
            new = '('+old+'/log('+str(e)+'))'
            if trace: print '** replace:',old,'  with:',new
            expr = expr.replace(old, new)

        return expr

    #============================================================================
    # Turn the Expression into a MeqParm with an init Funklet
    #============================================================================

    def FunkletParm (self, show=False):
        """Make a single MeqParm with the Funklet made from the Expression."""

        self._nodes2vars()
        if self.has_itemtype ('node'):
            # As soon as some parm items are nodes, it is no longer
            # possible to turn the Expression into a Funklet. So if
            # the latter is required, it should be done BEFORE the
            # function .MeqFunctional() is called....
            s = '** not possible to make a FunkletParm (has node-items)'
            raise ValueError, s

        elif not self.has_itemtype ('parm'):
            s = '** not possible to make a FunkletParm (no parm-items)'
            raise ValueError,s

            
        qnode = self.ns['Expr_FunkletParm']
        if not qnode.initialized():
            f0 = self.Funklet()
            if isinstance(f0, bool):
                s = '** Funklet is '+str(type(f0))
                raise TypeError,s
            funklet = f0.get_meqfunklet()
            # print '\n** funklet =',funklet
            # print dir(f0),'\n'
            if len(funklet['coeff'])==0:
                s = '** coeff is empty'
                raise ValueError,s
            qnode << Meq.Parm(init_funklet=funklet,       # new MXM 28 June 2006
                              testval=self._testeval(),
                              tags=['FunkletParm'],
                              node_groups=['Parm'])

        # Finished:
        self._FunkletParm = qnode
        self._last_solvable_tags = 'FunkletParm'          # used by .solvable()
        self._locked = True                               # inhibit further modifications
        if show: display.subtree(qnode)
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


    def Funklet (self, plot=False):
        """Return the Funklet object corresponding to this Expression.
        Make one if necessary."""

        # Avoid double work:
        if self._Funklet:
            return self._Funklet

        self._nodes2vars()        
        if self.has_itemtype ('node'):
            # If there are MeqNode children, the Expression should be turned into
            # a MeqFunctional node. It is not possible to make a Funklet.
            return False
        
        funktion = deepcopy(self._expanded)
        coeff = []
        k = -1
        for key in self.item_order():
            rr = self._item[key]
            if rr['type']=='parm':                     # ....!!
                # Replace the undefined parameters {} with pk = p0,p1,p2,...
                # and fill the coeff-list with their default values
                k += 1
                pk = 'p'+str(k)
                funktion = funktion.replace(key, pk)
                value = rr['default']         
                value = float(value)                   # required by Funklet...!?
                coeff.append(value)

            elif rr['type']=='var':
                # Replace the valiables [] with x0 (time), x1(freq) etc
                funktion = funktion.replace(key, rr['var']['funktion'])
                # print '- replace:',key,'by:',funktion,'\n  ->',funktion

        funktion = self._adjust_functions(funktion)    # deal with log(..) etc

        # Make the Funklet, and attach it:
        # if self._expression_type=='MeqPolc':         # see polc_Expression()
        # elif self._expression_type=='MeqPolcLog':    # see polc_Expression()
        # else:
        #-----------------------------------------------------
        if True:
            # type: isinstance(f0, Funklet) -> True
            f0 = Funklet(funklet=record(function=funktion, coeff=coeff),
                         name=self.name)
        else:
            # Alternative: type(meq.polc(0)) 
            f0 = meq.polc(coeff=coeff, subclass=meq._funklet_type)
            f0.function = funktion
        #-----------------------------------------------------

        if plot:
            # NB: The following plots WITHOUT execution!
            dom = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),l=(-0.1,0.1),m=(-0.1,0.1))
            cells = meq.gen_cells(domain=dom,num_time=4,num_freq=5, num_l=6, num_m=7)
            f0.plot(cells=cells)

        # Finished:
        self._locked = True                              # no more modifications
        self._Funklet = f0
        self._Funklet_funktion = funktion         
        return self._Funklet







    #==========================================================================
    # Special case: Compounder
    #==========================================================================


    def MeqCompounder (self, extra_axes=None, common_axes=None,
                       use='MeqFunctional', show=False):
        """Make a MeqCompounder node from the Expression. The extra_axes argument
        should be a MeqComposer that bundles the extra (coordinate) children,
        described by the common_axes argument (e.g. [hiid('l'),hiid('m')]."""                   

        qnode = self.ns['MeqCompounder']
        if not qnode.initialized():

            # Find the variable axes other than 'time' and 'freq':
            caxes = []
            for key in self.item_order():
                if self._item[key].has_key('var'):
                    var = self._item[key]['var']
                    # print '***',key,':',var
                    if var.has_key('axis') and var['axis']:
                        if var['axis'] in ['freq','time']:
                            pass
                        else:
                            caxes.append(var['axis'])
            if len(caxes)==1:
                # For some reason, there should be 2 common_axes....??!
                if caxes[0]=='m': caxes.append('l')
                if caxes[0]=='l': caxes.append('m')

            if extra_axes==None:
                # Kludge for convenient testing of the Compounder.
                #    NB:   str(hiid('m')) -> 'M'   ............!
                print '** caxes =',caxes
                cc = []
                common_axes = []
                for k,axis in enumerate(caxes):
                    common_axes.append(hiid(axis))
                    if (k%2)==0:        # alternate between MeqFreq and MeqTime
                        cc.append(self.ns['extra_axis_'+axis] << Meq.Time())
                    else:
                        cc.append(self.ns['extra_axis_'+axis] << Meq.Freq())
                if len(cc)<2:
                    raise ValueError,'** too few common axes for MeqCompounder() ...'
                extra_axes = self.ns['extra_axes'] << Meq.Composer(children=cc)
                print '** common_axes=',common_axes,str(extra_axes)
                

            # Make/get a node/subtree from the Expression:
            if use=='MeqFunctional':
                node = self.MeqFunctional()
            else:
                node = self.MeqNode()

            # OK, make the compounder:
            qnode << Meq.Compounder(children=[extra_axes, node],
                                    common_axes=common_axes)
            self._Compounder = qnode
            self._Compounder_common_axes = str(common_axes)

        # Finished
        self._locked = True                              # no more modifications
        if show: display.subtree(qnode)
        return qnode





#===============================================================
# Test routine (with meqbrowser):
#===============================================================

def _define_forest(ns):

    cc = [ns.dummy<<45]

    if 0:
        e0 = Expression(ns, 'e0', '{a}+{b}*[t]-{e}**{f}')
        e0.modparm('{a}', '[f]*{c}/{b}+{d}')
        e0.modparm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
        e0.modparm('{c}', 47)
        e0.modparm('{d}', (ns << Meq.Parm(-56)))
        e1 = 111
        if False:
            e1 = Expression(ns,'e1','{A}+{B}/[m]')
            e1.modparm('{A}', 45)
            e1.modparm('{B}', -45)
        e0.modparm('{e}', e1)    
        e0.display()
    
        if 1:
            cc.append(e0.MeqNode())   
            e0.display()

        if 0:                       
            cc.append(e0.MeqFunctional(show=True))
            e0.display()


    #------------------------------------------------------------

    if 0:
        # e4 = Expression(ns, 'e4', '[l]-[m]+{a}+[long]')
        e4 = Expression(ns, 'e4', '[l]-[m]')
        # e4 = Expression(ns, 'e4', '[l]-[m]+{a}')
        # e4.modvar('[long]', xn='x6', axis='long')
        e4.display()

        if 0:
            f0 = e4.Funklet(plot=True)
            print '** f0 =',f0

        if 1:
            # LM = ns.LM << Meq.Composer(ns.L<<0.1, ns.M<<-0.2)
            LM = ns.LM << Meq.Composer(ns.L<<Meq.Freq(), ns.M<<Meq.Time())
            node = e4.MeqCompounder(extra_axes=LM,
                                    common_axes=[hiid('l'),hiid('m')],        # Time, Freq, L, M, 4, 5, 6, 7
                                    # common_axes=[hiid('lat'),hiid('long')],     # Time, Freq, $lat, long, L, M, 6, 7
                                    # common_axes=[hiid('q'),hiid('m')],        # Time, Freq, q, M, L, 5, 6, 7
                                    # common_axes=[hiid('m')],                  # kernel crash
                                    show=True)
            cc.append(node)
            e4.display()

        if 0:
            cc.append(e4.MeqNode())   
            e4.display()


    if 0:
        e5 = Expression(ns, 'e5', '[long]-[$lat]+{p}')
        e5.modvar('[long]', xn='x2', axis='long')
        e5.modvar('[$lat]', xn='x3', axis='$lat')
        e5.display()
        if 1:
            cc.append(e5.MeqNode())   
            e5.display()

    if 1:
        expr = '{a0}'
        for k in range(1,15):
            expr += ' + {a'+str(k)+'}'
        e9 = Expression(ns, 'e9', expr, value=0.0)

        # The following are OK with FunkletParm or MeqFunctional: 
        # e9.modparm('{a0}', 'pi')                  
        # e9.modparm('{a1}','sin(2)+cos(3)')             
        # e9.modparm('{a2}','exp(-2)+sqrt(4)')       
        # e9.modparm('{a3}','(5**2)')                       
        # e9.modparm('{a4}','abs(-2)+ceil(3.5)+floor(3.7)')

        # Works with MeqFunctional, but NOT with Funklet(!!?)
        # e9.modparm('{a5}','asin(0.5)+acos(-0.5)+atan(4)+atan2(2,3)')     # math

        # The following work neither with FunkletParm as with MeqFunctional
        ## e9.modparm('{a6}','arcsin(0.5)+arccos(-0.5)+arctan(4)')        # numarray
        ## e9.modparm('{a7}','sinh(2)+cosh(-2)+tanh(4)')
        ## e9.modparm('{a8}','complex(5,3)')
        ## e9.modparm('{a9}','tan(4)')                         # <--!!
        ## e9.modparm('{a10}','pow(-2,3)')             
        ## e9.modparm('{a11}','e')

        # The following gives different results in Python (testeval) and the node.
        # Python log(x)=elog(x) while Funklet (AIPS++ functional) assumes 10log(x)
        # The latter can be turned into the former: elog(x) = 10log(x)/10log(e)
        # NB: OK now, since log(x) is replaced with (log(x)/log(e)) in Funklet funktion,
        #     but not in the Python expression. This then gives the same result.
        e9.modparm('{a12}','log(10)')         # funklet/functional=1.0,  python=2.3 
        cc.append(ns.log10 << Meq.Log(10))    # =2.3 So: replace in funklet expr 

        e9.display()
        # c = e9.FunkletParm()       
        c = e9.MeqFunctional()
        cc.append(c)
        JEN_bookmarks.create(c, 'eval')


    ns.result << Meq.Composer(children=cc)
    return True



#---------------------------------------------------------------

def _tdl_job_2D_tf (mqs, parent):
    """Execute the forest with a 2D request (freq,time), starting at the named node"""
    domain = meq.domain(1.0e8,1.1e8,0,2000)                            # (f1,f2,t1,t2)
    cells = meq.cells(domain, num_freq=10, num_time=11)
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
       
def _tdl_job_4D_tf_lat_long (mqs, parent):
    """Execute the forest with a 4D request (freq,time,$lat,long).
    NB: This does NOT work on a Compounder node!"""
    domain = meq.gen_domain(time=(0.0,1.0),freq=(100e6,110e6),
                            lat=(-0.1,0.1),long=(-0.1,0.1))
    cells = meq.gen_cells(domain=domain, num_time=4, num_freq=5,
                          num_lat=6, num_long=7)
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
        e0.modparm('{b}', (ns << Meq.Add(ns<<13,ns<<89)))
        e1 = 111.111
        if True:
            e0.modparm('{a}', '[f]*{c}/{b}+{d}')
            e0.modparm('{c}', 47)
            e1 = Expression(ns,'e1','{A}+{B}/[m]')
            e1.modparm('{A}', 45)
            e1.modparm('{B}', -45)
        e0.modparm('{e}', e1)
        # e0.modparm('{d}', (ns << Meq.Parm(-56)))
        e0.display()

        if 0:
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
        e2.modparm('{a}', '[f]*{c}/{b}+{d}')
        e2.modparm('{b}', 447)
        e2.modparm('{c}', 47)
        e2.modparm('{d}', (ns << Meq.Parm(-56)))
        e2.display()
        if 0:
            e2.MeqNode()
            e2.display()
        if 0:
            e2.FunkletParm()
            e2.display()
        if 0:
            e2.MeqCompounder(show=True)
            e2.display()

    if 0:
        e4 = Expression(ns, 'e4', '[l]-[m]+{p}')
        # e4 = Expression(ns, 'e4', '[l]-[m]')
        # e4.modvar('[m]', xn='x10', axis='mcoord')
        e4.display()
        if 0:
            e4.MeqNode(show=True)
            e4.display()
        if 0:
            e4.MeqFunctional(show=True)
            e4.display()
        if 1:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e4.MeqCompounder(extra_axes=LM,
                                    # common_axes=[hiid('l'),hiid('m')],
                                    common_axes=[hiid('m')],
                                    show=True)
            e4.display()

    if 0:
        e5 = Expression(ns, 'e5', '[long]-[$lat]+{p}')
        e5.modvar('[long]', xn='x2', axis='long')
        e5.modvar('[$lat]', xn='x3', axis='$lat')
        e5.display()
        if 0:
            e5.MeqNode(show=True)
            e5.display()
        if 0:
            e5.MeqFunctional(show=True)
            e5.display()
        if 0:
            L = ns.L << 0.1
            M = ns.M << -0.2
            LM = ns.LM << Meq.Composer(L,M)
            node = e5.MeqCompounder(extra_axes=LM,
                                    # common_axes=[hiid('l'),hiid('m')],
                                    common_axes=[hiid('m')],
                                    show=True)
            e5.display()

    if 1:
        e8 = Expression(ns,'e8','{a}+{b=12}+{c=4~0.5}')
        e8.display()

    if 0:
        expr = '{a0}'
        for k in range(1,9):
            expr += ' + {a'+str(k)+'}'
        print expr
        e9 = Expression(ns, 'e9', expr, value=0.0)
        e9.modparm('{a0}', 'pi+e')
        e9.modparm('{a1}','sin(2)+cos(3)+tan(4)')
        # e9.modparm('{a2}','arcsin(0.5)+arccos(-0.5)+arctan(4)')        # numarray
        e9.modparm('{a2}','asin(0.5)+acos(-0.5)+atan(4)+atan2(2,3)')     # math
        e9.modparm('{a3}','sinh(2)+cosh(-2)+tanh(4)')
        e9.modparm('{a4}','log(2)+exp(-2)+sqrt(4)')
        e9.modparm('{a5}','pow(-2,3)+(5**2)')
        e9.modparm('{a6}','abs(-2)+ceil(3.5)+floor(3.7)')
        e9.modparm('{a7}','complex(5,3)')
        e9.display()
        if True:
            import numarray
            print '\n** numarray:',dir(numarray)
            import math
            print '\n** math:',dir(math)

    print '\n*******************\n** End of local test of: Expression.py:\n'




#============================================================================================

    
