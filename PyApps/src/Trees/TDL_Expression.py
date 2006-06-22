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
#    - 01 jun 2006: expansion into a separate Expression
#    - 05 jun 2006: regularized node parm
#    - 06 jun 2006: introduced 'global' {_xx} parameters
#    - 07 jun 2006: implement .MeqParms()
#
# Remarks:
#
# Description:
#
#  -) Expression objects
#     -) e0 = Expression ("{A} + {ampl}*cos({phase}*[t])" [, label='<label>'])
#     -) Variables in square brackets: [t],[time],[f],[fGHz],[l],[m],[RA],  etc
#     -) Parameters in curly brackets.
#     -) The expression is supplied to the Expression constructor
#     -) Extra information about parameters is supplied via a function:
#         -) e0.parm('A', 34)                         numeric, default value is 34
#         -) e0.parm('A', 34, constant=True)          numeric constant, value is 34
#         -) e0.parm('ampl', e1)                      another Expression object
#         -) e0.parm('phase', polc=[2,3])             A polc-type Expression generated internally
#         -) e0.parm('A', f1)                         A Funklet object
#         -) e0.parm('A', node)                       A node (child of a MeqFunctional node)
#         -) e0.parm('A', image)                      A FITS image
#     -) The Expression object may be converted to:
#         -) a Funklet                                  with p0,p1,p2,... and x0,x1,...
#         -) a MeqParm node (init_funklet=Funklet)
#         -) a MeqFunctional node                     (parms AND vars are its children)      
#         -) a MeqCompounder node                     needs extra children
#         -) ...
#     -) Easy to build up complex expressions (MIM, beamshape)
#     -) Internally, there is a self.__expression, which does not change, and an
#        expanded version self.__xexpr. In the latter, parameters that are Expressions,
#        Funklets, MeqNodes etc are replaced with sub-expressions. The self.__xexpr is
#        the basis for translation into a Funklet, evaluation, etc.
#     -) Should be very useful for LSM
#     -) Plotting: Each parameter and variable has an internal testval (scalar) and testvec
#                  vector. These will be used for plotting, unless otherwise specified.
#                  The testval/testvec may be specified explicitly with .parm() and .var().
#         -) .plot()               Plots the Expression for its internal parameter test-values,
#                                  and against the internal testvec of one of its variables.
#         -) .plot(A=True)         Multiple plots for the internal testvec of parm {A} 
#         -) .plot(A=True, B=True) The same , but it uses the longest A/B testvec as x-axis
#         -) .plot(f=True)         Enforce the use of the freq variable as the x-axis
#     -) Fitting: If the Expression is a has multiple additive terms, each with a single
#                 numeric parameter, it is possible to solve for the parameter values
#                 to fit a given number of values vv(f,t,l,m). The result is plotted.
#     -) Other functionality:
#         -) Uncertainty (rms stddev) in default values (simulation)
#         -) Etc

"""Qualifier service:

  Some of the Expression methods generate MeqTree nodes. Such methods always need
  a node-scope (ns). If no name or qualifier (qual) is specified, an automatic node
  name is generates, which will also be unique. It is also possible, with a separate
  method, to specify overall qualifiers that will be used for for all nodes that are
  subsequently generated for that object:
     .quals(*args, **kwargs)
  Any extra qualifiers specified in a method call will be added to these overall
  qualifiers. The overall qualifiers can be removed with .quals().

  For convenience, some extra features are added to the qualifier service. When
  modifying the .quals(), the following things happen:
    -) .quals() is called for  
    -) All existing nodes are removed.
    -) The default values are modified where stddev>0
  
  """


#***************************************************************************************
# Preamble
#***************************************************************************************

from numarray import *
from numarray.linear_algebra import *
from random import *
# from pylab import *                       # gives problems...
from copy import deepcopy
from Timba.Trees import TDL_Leaf
from Timba.Meq import meq
from Timba.Contrib.MXM.TDL_Funklet import *


# Replacement for is_numeric(): if isinstance(x, NUMMERIC_TYPES):
NUMERIC_TYPES = (int, long, float, complex)


#***************************************************************************************
#***************************************************************************************

class Expression:
    def __init__(self, expression='-1.23456789',
                 label='<label>', descr=None, unit=None, **pp):
        """Create the object with a mathematical expression (string)
        of the form:  {aa}*[t]+cos({b}*[f]).
        Variables are enclosed in square brackets: [t],[f],[m],...
        Parameters are enclosed in curly brackets: {aa}, {b}, ...
        Simple information about parameters (type, default value)
        may be supplied via keyword arguments pp. More detailed
        information may be supplied via the function .parm()."""

        self.__label = _unique_label(label)
        self.__ident = int(100000*random())        # unique identifier
        self.__descr = descr
        self.__unit = unit                         # unit of the result
        self.__expression = expression
        self.__numeric_value = None  
        self.__input_expression = expression        
        self.__pp = str(pp)

        # For each parameter in self.__expression, make an entry in self.__parm.
        # These entries may be modified with extra info by self.parm().
        # First extract a list of parameter names, enclosed in curly brackets:
        self.__parm_order = find_enclosed(self.__expression, brackets='{}')
        self.__parm = dict()
        self.__parmtype = dict(Expression=[], MeqNode=[], Funklet=[])
        for key in self.__parm_order:
            self._create_parm(key)

        # Optional: Limited parm info (type, default value) may also be specified
        # via the constructor keyword arguments pp: e.g. aa=4.5 for parm {aa}.
        for key in pp.keys():
            self.parm(key, default=pp[key])

        # For each variable in self.__expression, make an entry in self.__var.
        # First extract a list of variable names, enclosed in square brackets:
        vv = find_enclosed(self.__expression, brackets='[]')
        self.__var = dict()
        for key in vv:
            self._create_var(key)

        # The expression may be purely numeric:
        self.numeric_value()

        # Initialise derived quantities:
        self._reset()

        # Finished:
        return None


    #----------------------------------------------------------------------------

    def numeric_value(self, trace=False):
        """The expression may be purely numeric (None if not)"""
        self.__numeric_value = None
        if len(self.__parm)==0 and len(self.__var)==0:
            try:
                v = eval(self.__expression)
            except:
                return None
            self.__numeric_value = v
        if trace: print '\n**',self.__expression,': numeric_value =',self.__numeric_value,'\n'
        return self.__numeric_value


    #----------------------------------------------------------------------------

    def _reset (self, nominal=True, recurse=True):
        """Reset the object to its original state."""
        self.__quals = dict()
        self.__plotrec = None
        self.__expanded = False
        self.__MeqNode = None
        self.__MeqFunctional = None
        self.__MeqParm = None
        self.__MeqParms = None
        self.__MeqConstant = None
        self.__Funklet = None
        self.__Funklet_function = None
        self.__test_result = None
        self.__eval_result = None
        self.__test_seval = None
        self.__eval_seval = None
        for key in self.__parm.keys():
            rr = self.__parm[key]
            if isinstance(rr, Expression):
                if recurse: rr._reset(nominal=nominal)
            elif isinstance(rr, Funklet):
                pass
            elif rr.has_key('nodename'):
                pass
            elif nominal:
                rr['default'] = rr['nominal']
            elif rr['stddev']>0:
                # See .quals(). Note that stddev is given a a fraction (e.g. 0.1)
                # of the 'scale' of the parameter value. This allows specification
                # of the scatter in general terms.
                rr['default'] = gauss(rr['nominal'], rr['stddev']*rr['scale'])
            else:
                rr['default'] = rr['nominal']
        return True
    
    #----------------------------------------------------------------------------

    def copy(self, label=None, descr=None, quals=None):
        """Return a (re-labelled) 'deep' copy of this object""" 
        new = deepcopy(self)                                       # copy() is not enough...
        if label==None: label = '('+self.label()+')'               # Enclose old label in ()
        new.__label = label                                        # re-label (always)
        if descr==None: descr = '('+self.descr()+')'               # Enclose old descr in ()
        new.__descr = descr                                        # 
        if not quals==None: new.quals(quals)                       # ....??                                
        return new


    #----------------------------------------------------------------------------
    # Some access functions:
    #----------------------------------------------------------------------------

    def label (self):
        """Return the (unique) label of this Expression object"""
        return self.__label

    def unit (self):
        """Return the (string) unit of the result of the Expression object"""
        if not isinstance(self.__unit, str): return ''
        return self.__unit

    def descr (self):
        """Return the brief description of this Expression object"""
        return str(self.__descr)

    def tlabel (self):
        """Return a concatenation of object type and label"""
        return 'Expression: '+self.__label
        # return str(type(self).__class__)+':'+self.__label

    def test_result (self):
        """Return the result of evaluation with the test-values."""
        return self.__test_result

    def parm_order (self):
        """Return the order of parameters in the input expression"""
        return self.__parm_order

    def expression (self):
        """Return the (mathematical) expression"""
        return self.__expression



    #----------------------------------------------------------------------------
    # Some display functions:
    #----------------------------------------------------------------------------

    def oneliner(self, full=True):
        """Return a one-line summary of the Expression"""
        # ss = '** Expression ('+str(self.__label)+'):  '
        ss = '** '+self.tlabel()+':  '
        if self.__quals: ss += '(quals='+str(self.__quals)+') '
        if self.__unit: ss += '('+str(self.__unit)+') '
        if self.__descr:
            ss += str(self.__descr)
        elif full:
            s1 = str(self.__expression)
            if len(s1)>50: s1 = s1[:50]+' ...' 
            ss += s1
        return ss

    #----------------------------------------------------------------

    def display(self, txt=None, full=False):
        """Display a summary of the Expression"""
        if txt==None: txt = self.label()
        print '\n** Display of: Expression (',txt,'):',str(self.__ident)
        indent = 2*' '
        if full:
            print indent,'- Input_expression: ',str(self.__input_expression)
            print indent,'- Input: ',str(self.__pp)
        print indent,'- Default node qualifiers: ',str(self.__quals)
        print indent,'- Purely numeric value: ',str(self.__numeric_value)
        print indent,'-',self.oneliner()

        print indent,'- Its expression (term-by-term):'
        ss = self.format_expr(header=False)
        for term in ss['terms']:
            print indent,'  ',term
        
        print indent,'- Its variables (',len(self.__var),'): '
        for key in self.__var.keys():
            print indent,'  -',key,':',self.__var[key]

        print indent,'- Its parameters (',len(self.__parm),'):'
        for key in self.__parm_order:
            p = self.__parm[key]
            if isinstance(p, Expression):
                expr = p.expression()
                if len(expr)>80: expr = expr[0:80]+' ...'
                print indent,'  -',key,':',p.oneliner(),expr
            elif isinstance(p, Funklet):
                print indent,'  -',key,': (Funklet):',p._function
            elif p.has_key('nodename'):
                print indent,'  -',key,': (MeqNode):',p
            else:
                print indent,'  -',key,':',p

        print indent,'- Parameter types:'
        for key in self.__parmtype.keys():    
            print indent,'  -',key,'(',str(len(self.__parmtype[key])),'): ',self.__parmtype[key]

        if not isinstance(self.__expanded, Expression):
            print indent,'- Expanded:  ',self.__expanded
        else:
            print indent,'- Expanded:  ',self.__expanded.oneliner()
            n = len(self.__expanded.parm_order())
            print indent,'  - xparms (',str(n),'):  ',self.__expanded.parm_order()
            print indent,'  - xvars:  ',self.__expanded.__var.keys()
            if full:
                print indent,'  - xexpr:  ',self.__expanded.expression()
            
        print indent,'- Evaluation:'
        # print indent,'  - test_result: ',self.__test_result
        print indent,'  - eval_result: ',self.__eval_result
        if full:
            # print indent,'  - test_seval: ',self.__test_seval
            print indent,'  - eval_seval: ',self.__eval_seval

        if not self.__Funklet:
            print indent,'- Derived Funklet:',str(self.__Funklet)
        else:
            print indent,'- Derived Funklet:'
            print indent,'  - function =',str(self.__Funklet_function)
            print indent,'  - F._function ->',str(self.__Funklet._function)
            if full:
                print indent,'  - F._coeff ->',str(self.__Funklet._coeff)
                s1 = str(self.__Funklet._type)
                if len(s1)>20: s1 = s1[:20]+' ....?'
                print indent,'  - F._type ->',s1
                # print dir(self.__Funklet)
                print indent,'  - F.eval() ->',str(self.__Funklet.eval())

        self.find_MeqParms()
        if not isinstance(self.__MeqParms, dict):
            print indent,'- Available (groups of) MeqParms: None'
        else:
            print indent,'- Available (groups of) MeqParms:'
            for key in self.__MeqParms.keys():
                gg = self.__MeqParms[key]
                print indent,'  -',key,'(',len(gg),'): ',gg

        if full:    
            print indent,'- Created MeqNodes:'
            print indent,'  - MeqNode:',self.__MeqParm
            print indent,'  - MeqParm:',self.__MeqParm
            print indent,'  - MeqFunctional:',self.__MeqFunctional
            print indent,'  - MeqConstant:',self.__MeqConstant
        print '**\n'



        
    #============================================================================
    # Definition of parameters {xxx} etc:
    #============================================================================

    def _create_parm (self, key=None, trace=False):
        """Create a parameter definition in self.__parm.
        This function is ONLY called from the constructor."""

        if trace:
            print level*'..','** .create_parm(',key,'): ',self.tlabel()

        # Search the key for indices (in square brackets)
        # If found, change the key in expression and parm_order.
        keyin = key
        index = [0]
        ii = find_enclosed(key, brackets='[]')    # e.g. A[0,1]
        if len(ii)>0:                             # found
            ss = ii[0].split(',')                 # -> ['0','1']
            key = key.split('[')[0]               # key -> A
            key += '_'                            # key -> A_
            for s in ss:
                key += s                          # key -> A_01
            index = []
            for s in ss:
                index.append(eval(s))             # -> [0,1]

            # Replace keyin with key in self.__expression:
            self.__expression = self.__expression.replace('{'+keyin+'}','{'+key+'}')
            if keyin in self.__parm_order:
                # Replace keyin with key in self.__parm_order:
                for i in range(len(self.__parm_order)):
                    if self.__parm_order[i]==keyin:
                        self.__parm_order[i] = key

        # Create a place-holder, assuming a numeric parm:
        self.__parm[key] = self._create_numeric_parm(default=-1, index=index, key=key)
        return self.__parm[key]


    #----------------------------------------------------------------------------

    def parm (self, key=None, default=None,
              constant=None, polc=None,
              ntest=None, testinc=None,
              stddev=None, scale=None,
              unit=None, ident=None, help=None, group=None,
              recurse=True, level=0, trace=False):
        """Modify the definition of the named parameter (key).
        The default argument may either be a value, or an object of type
        Expression or Funklet, or a nodestub (child of MeqFunctional node).
        If polc=[ntime,nfreq] (one-relative), a polc Expression is generated,
        with the default value/list as a coeff-list."""

        # trace = True
        if trace:
            print '\n',level*'..','** .parm(',key,type(default),'): ',self.tlabel()

        # If no key specified, return the entire record:
        if key==None:
            return self.__parm

        # Modify existing parms only:
        if key in self.__parm_order:

            # Special case: make a polc Expression:
            if isinstance(polc, (list,tuple)):
                default = polc_Expression(shape=polc, coeff=default,
                                          label=None, unit=unit, trace=trace)

            # First deal with a new default, if specified:
            if not default==None:
                if isinstance(default, Expression):
                    self.__parm[key] = default
                    if not key in self.__parmtype['Expression']:
                        self.__parmtype['Expression'].append(key)

                elif isinstance(default, Funklet):
                        self.__parm[key] = default
                        if not key in self.__parmtype['Funklet']:
                            self.__parmtype['Funklet'].append(key)

                elif isinstance(default, Timba.TDL.TDLimpl._NodeStub):
                    if not key in self.__parmtype['MeqNode']:
                        self.__parmtype['MeqNode'].append(key)
                    index = [0]
                    if self.__parm[key].has_key('index'):
                        index = self.__parm[key]['index']          # see _create_parm()
                    self.__parm[key] = dict(node=default, nodename=default.name,
                                            classname=default.classname, index=index,
                                            default=3.0, ntest=0)
                    default = None   # kludge for _update_definition_record() below... 

                elif isinstance(default, dict):
                    # Assume a self.__parm dict, which is recursively passed down from
                    # a 'parent' expression (see recursion below):
                    self.__parm[key] = default

                else:
                    # Assume that the specified default is numeric:
                    rr = self.__parm[key]                            # convenience
                    if not isinstance(rr, dict) or rr.has_key('node'):
                        # The parm (key) was NOT numeric: create a new one
                        # (otherwise, the existing parm gets updated below)
                        self.__parm[key] = self._create_numeric_parm(default, key=key)

            # Then update the various parm types, as required:
            if isinstance(self.__parm[key], dict):
                self._update_definition_record (self.__parm[key], default=default,
                                                ident=ident, unit=unit,
                                                testinc=testinc, ntest=ntest,
                                                scale=scale, stddev=stddev,
                                                key=key, trace=False)

        # Optional: update parameters in its Expression parameters recursively:
        recurse_result = False
        if key[0]=='_': recurse = True                 # Always recurse global parm
        if recurse:              
            for key1 in self.__parm.keys():
                p1 = self.__parm[key1]
                if isinstance(p1, Expression):
                    if key in self.__parm_order:
                        # key is parm in this Expression: copy its definition
                        r1 = p1.parm(key, self.__parm[key]) 
                    else:
                        # key is NOT a parm in this Expression: use arguments
                        r1 = p1.parm(key, default, group=group,
                                     constant=constant, polc=polc,
                                     ntest=ntest, testinc=testinc,
                                     recurse=recurse, level=level+1,
                                     help=help, stddev=stddev,
                                     unit=unit, ident=ident, trace=trace)
                    if r1: recurse_result = r1

        # Finishing touches:
        self.__expanded = False                       # Enforce a new expansion 
        if key in self.__parm_order:
            return self.__parm[key]                   # updated parm definition
        elif recurse_result:
            return recurse_result                     # updated parm definition
        return False


    #----------------------------------------------------------------------------

    def _create_numeric_parm (self, default=-1, index=[0], key=None, trace=False):
        # A numeric parm has a default value, which is used for MeqParm.
        # It also has other information:
        # - testval: value to be used for testing.
        # - testvec: value to be used for plotting.
        # - nominal: nominal default value (i.e. without stddev)
        # - stddev: stddev to be used (with scale) for calculating a new default
        #     value by adding a random value to the nominal default value. This
        #     is done each time the internal node qualifier is changed.
        #     See ._reset(), which is called from .quals(), for more details.
        # - if constant==True, the parameter is a constant with value default.
        ident = int(1000000*random())             # unique parm identifier
        rr = dict(default=default, nominal=default, index=index,
                  ident=ident, group=None, unit=None,
                  constant=False, scale=1.0, stddev=0.0,
                  ntest=None, testinc=None, testval=None, testvec=None,
                  help=None)
        # If default specified (and non-zero), modify the scale:
        self._update_definition_record (rr, default, ntest=1, testinc=1.0,
                                        key=key, trace=False)
        return rr

    #------------------------------------------------------------------------------

    def _update_definition_record (self, rr, default=None,
                                   unit=None, ident=None, group=None,
                                   testinc=None, ntest=None,
                                   scale=None, stddev=None,
                                   key=None, trace=False):
        """Helper function to update the 'numeric' fields of a parameter
        or variable definition record. See self.parm() and self.var()"""
        # trace = True
        rr.setdefault('testvec', None)
        update_testval = False
        rr.setdefault('unit', None)
        if unit: rr['unit'] = unit                         # new unit specified
        if ident: rr['ident'] = ident                      # new ident specified
        if not default==None:
            rr['default'] = default                        # new default specified
            rr['nominal'] = default                        # new default specified
            if not default==0: rr['scale'] = abs(default)
            update_testval = True
        if scale: rr['scale'] = scale                      # new scale specified
        if rr.has_key('scale'):
            if rr['scale']<=0: rr['scale'] = 1.0
        if not stddev==None: rr['stddev'] = stddev         # new stddev specified
        if testinc:
            rr['testinc'] = testinc                        # new test incr specified
            update_testval = True
        if not ntest==None:
            rr['ntest'] = ntest                            # new ntest specified
            update_testval = True
        if rr['testvec']==None: update_testval = True
        if update_testval:
            rr.setdefault('ntest', 0)
            rr.setdefault('testinc', 1.0)
            rr['testval'] = rr['default'] + rr['testinc']  # non-zero, positive
            rr['testvec'] = dict(min=rr['default']-rr['testinc']*rr['ntest'],
                                 max=rr['default']+rr['testinc']*rr['ntest'],
                                 nr=(1+rr['ntest']*2))
        if trace: print '** _update_definition_record(',key,default,'): ->\n   ',rr
        return True

    #============================================================================
    # Definition of variables [t],[f] etc:
    #============================================================================

    def _create_var (self, key=None, trace=False):
        """Create the definition of a variable [v] in self.__var.
        This function is ONLY called from the constructor."""

        ident = int(1000000*random())             # unique var identifier
        rr = dict(xn='xn', default=0.0, unit=None, node=None,
                  testval=None, testvec=None, ident=ident)

        # Deal with some standard variables:
        if key[0]=='t':                    # time
            rr['node'] = 'MeqTime'         # used in Functional
            rr['xn'] = 'x0'                # used in Funklet
            rr['unit'] = 's'
            default = 1e9                  # 'current' MJD (s)
            testinc = 10.0                 # 10 s
        elif key[0]=='f':                  # freq, fGHz, fMHz
            rr['node'] = 'MeqFreq'
            rr['xn'] = 'x1'
            rr['unit'] = 'Hz'
            default = 150e6                # 150 MHz
            testinc = 1e6                  # 1 MHz
        elif key[0]=='l':
            rr['node'] = 'MeqL'            # .....!?
            rr['xn'] = 'x2'                # .....!?
            rr['unit'] = 'rad'
            default = 0.0                  # phase centre
            testinc = 0.01                 # 0.57 deg
        elif key[0]=='m':
            rr['node'] = 'MeqM'            # .....!?
            rr['xn'] = 'x3'                # .....!?
            rr['unit'] = 'rad'
            default = 0.0                  # phase centre
            testinc = 0.01                 # 0.57 deg
        else:
            default = 0.0                  # phase centre
            testinc = 0.01                 # 0.57 deg

        # Create the entry in self.__var:
        self.__var[key] = rr
        # Use the modification function to initialize it:
        return self.var(key, default=default, ntest=10, testinc=testinc)

    #----------------------------------------------------------------------------

    def var (self, key=None, default=None, testinc=None, ntest=None,
             unit=None, ident=None, recurse=True, level=0, trace=False):
        """Modify/get the named (key) variable definition record."""

        # If no key specified, return the entire record:
        if key==None: return self.__var

        # Only update existing var definitions:
        if self.__var.has_key(key):
            self._update_definition_record (self.__var[key],
                                            default=default, ident=ident, unit=unit,
                                            testinc=testinc, ntest=ntest,
                                            key=key, trace=False)

        # Optional: update vars in any Expression parameters recursively:
        recurse_result = False
        if recurse:              
            for key1 in self.__parm.keys():
                p1 = self.__parm[key1]
                if isinstance(p1, Expression):
                    r1 = p1.var(key, default, unit=unit, ident=ident, 
                                ntest=ntest, testinc=testinc,
                                recurse=recurse, level=level+1,
                                trace=trace)
                    if r1: recurse_result = r1

        # Finishing touches:
        self.__expanded = False                       # Enforce a new expansion 
        if key in self.__var.keys():
            return self.__var[key]
        elif recurse_result:
            return recurse_result                     # updated var definition
        return False



    #============================================================================
    # Make a new Expression object, in which the hierarchical self.__expression
    # is expanded into a flat one. Keep this object internally.
    #============================================================================

    def expand (self, reset=False, unique=False, trace=False):
        """If necessary, expand the hierarchical self.__expression into a flat one.
        This is done by replacing the parameters that are Expressions by the relevant
        function-strings, while slightly renaming its parameter names. Similar actions
        are taken for other types of parameters, like Funklets and MeqNodes.
        If expansion makes a difference, the expanded expression and its parms/vars
        are used to make a new Expression object, and attached to self.__expanded.
        Otherwise, self.__expanded = True. See also self.expanded()."""

        if trace: print '\n** expand(reset=',reset,unique,'):',self.oneliner()
        if reset: self._reset()
        if unique: self._reset(recurse=False)                      # enforce new expansion
        if self.__expanded: return self.expanded()                 # avoid duplication

        xexpr = deepcopy(self.__expression)
        xparm = dict()
        xorder = []
        xvar = deepcopy(self.__var)
        different = False

        # Then replace the (expanded) Expression parameters:
        for key in self.__parm_order:
            parm = deepcopy(self.__parm[key])

            if isinstance(parm, Funklet):
                # Convert a Funklet to an Expression first
                different = True
                parm = Funklet2Expression(parm, key)

            if isinstance(parm, Expression):
                # Merge the (expanded) parm expr with its own:
                parm = parm.expanded()
                different = True
                pexpr = '('+parm.expression()+')'
                if trace: print '-',key,pexpr
                for pkey in parm.parm_order():
                    if pkey[0]=='_':                    # global parm {_xx}
                        ckey = pkey
                        if unique: ckey = key+pkey      # make unique (non-global) anyway
                    else:                               # normal parm {xx}
                        ckey = key+'_'+pkey
                    xorder.append(ckey)
                    pd = parm.parm(pkey)
                    xparm[ckey] = pd
                    pexpr = pexpr.replace('{'+pkey+'}', '{'+ckey+'}')
                xexpr = xexpr.replace('{'+key+'}', pexpr)
                for vkey in parm.var().keys():
                    xvar.setdefault(vkey, parm.var(vkey))

            elif parm.has_key('nodename'):              # parm is a MeqNode
                # different = True
                xorder.append(key)
                xparm[key] = self.__parm[key]

            else:
                # Otherwise, just copy (assume numeric):
                xorder.append(key)
                xparm[key] = self.__parm[key]
        if trace: print '   ->',xexpr
                
        # Dispose of the result:
        if not different:
            # If expansion does not change anything, just indicate
            # that the current object is expanded already:
            self.__expanded = True
            self.__test_result = self.eval(_test=True)
            self.__eval_result = self.eval()

        else:
            # Make the Expression object for the expanded version:
            e0 = Expression(xexpr, label='expanded_'+self.label(),
                            descr=self.__descr)
            e0.__expanded = True
            e0.__quals = self.__quals
            # Transfer the parameters:
            e0.__parm_order = xorder
            for key in xorder:
                parm = xparm[key]
                e0.__parm[key] = parm
                if isinstance(parm, Expression):
                    e0.__parmtype['Expression'].append(key)
                elif isinstance(parm, Funklet):
                    e0.__parmtype['Funklet'].append(key)
                elif parm.has_key('nodename'):
                    e0.__parmtype['MeqNode'].append(key)
            # Transfer the variables:
            for key in xvar.keys():
                e0.__var[key] = xvar[key]
            # Attach the expanded Expression to itself:
            self.__expanded = e0
            self.__test_result = e0.eval(_test=True)
            self.__eval_result = e0.eval()
            # e0.weedout(trace=True)                       # ......?
            if trace: e0.display('expanded', full=True)

        # Finished:
        return self.__expanded

    #----------------------------------------------------------------------------

    def weedout (self, trace=False):
        """Remove any duplicates of the same parm from self.__parm"""
        # NB: Should the Expression be expanded?
        for key1 in self.__parm_order:
            parm1 = self.__parm[key1]
            identical = [key1]
            for key2 in self.__parm_order:
                parm2 = self.__parm[key2]
                s1 = '- compare parm:',key1,key2,':'
                if not key1==key2 and self.is_identical_parm(parm1, parm2):
                    identical.append(key2)
                    print s1,identical
                elif trace:
                    print s1
                if key1=='Uterm_u' and key2=='Vterm_u':
                    print key1,':',parm1
                    print key2,':',parm2
            if len(identical)>1:
                if trace: print '- identical:',identical
        return True

    #............................................................................

    def is_identical_parm (self, parm1, parm2, trace=False):
        """Decide whether the two given parms are identical"""
        s1 = '.is_identical_parm(): '
        if isinstance(parm1, Expression):
            if not isinstance(parm2, Expression): return False
            if not parm1.__ident==parm2.__ident: return False
            s1 += parm1.oneliner()+str(parm1.__ident)
        elif isinstance(parm1, Funklet):
            if not isinstance(parm2, Funklet): return False
            s1 += 'Funklet '
            return False
        elif not isinstance(parm1, dict) or not isinstance(parm2, dict):
            return False
        elif not parm1.has_key('ident') or not parm2.has_key('ident'):
            return False
        elif not parm1['ident']==parm2['ident']:
            return False
        else:
            s1 += str(parm1['ident'])+'=='+str(parm2['ident'])
        if trace: print s1+' -> True'
        return True

    #----------------------------------------------------------------------------

    def expanded (self, reset=False, expand=True, unique=False, trace=False):
        """Return the expanded version of the Expression"""
        # trace = True
        if trace: print '\n** .expanded(reset=',reset,expand,'): (',self.oneliner(),')'
        if reset: self._reset()
        if unique:
            if trace: print '   expand(unique=True)'
            self.expand(unique=True)
            return self.expanded(trace=trace)
        elif isinstance(self.__expanded, Expression): # Expression 
            if trace: print '   return expanded version:',self.__expanded.oneliner()
        elif self.__expanded:                       # True: object already expanded 
            if trace: print '   not expandable: return self:',type(self)
            return self
        else:                                       # False: not yet expanded
            if trace: print '   expand()'
            self.expand()                           # expand if requested
            return self.expanded(trace=trace)
            # if expand: self.expand()              # expand if requested
        if trace: print '   -> self.__expanded =',self.__expanded,'(',self.oneliner(),')'
        return self.__expanded 
        

    #============================================================================
    # Fit the Expression (e.g. a polc) to a set of given points.
    #============================================================================

    def fit (self, **pp):
        """Adjust the Expression default parameters to make them fit the
        values of the specified points v(f,t,l,m)"""

        # trace = True
        
        # The function values at the specified points:
        if not pp.has_key('vv'): pp['vv'] = array(range(10))
        vv = array(pp['vv'])
        nvv = len(vv)
        if trace: print '\n** fit(',type(vv),len(vv),'):'

        self._reset()

        # Check whether there are values for all relevant variables:
        Z = dict()
        plotvar = None
        for key in self.__var.keys():
            if not pp.has_key(key):
                print 'need values for variable:',key
                return False
            elif len(pp[key])==1:
                pass                                      # OK...?
            elif not len(pp[key])==nvv:
                print 'length mismatch for variable:',key,':',nvv,len(pp[key])
                return False
            else:                                         # OK
                Z[key] = array(pp[key])
                plotvar = key                             # see below 
                self.__var[key]['testvec'] = Z[key]
                self.__var[key]['testval'] = Z[key][2]
                self.__var[key]['default'] = Z[key][0]
                if trace: print '- Z[',key,'] =',Z[key]

        # Assume a linear expression, with one (multiplicative) parameter
        # per term. The latter are the unknowns to be solved:
        terms = find_terms(self.__expression)
        unks = []
        coeff = dict()
        for term in terms['pos']:                         # 'neg' too!
            unknown = find_enclosed(term,'{}')
            if trace: print '\n- term:',term,'->',unknown
            if len(unknown)>1:
                print 'more than one unknown in term:',term
                return False
            unk = unknown[0]                               # string
            unks.append(unk)                               # list of unkowns

            # Calculate the coeff of the unkowns in the condition equations:
            # First replace the unkowns with 1.0
            term = term.replace('{'+unk+'}', '1.0')
            # Then replace the variables [f],[t],etc with Z['f'],Z['t'] etc:
            for vkey in Z.keys():
                term = term.replace('['+vkey+']', 'Z[\''+vkey+'\']')
                if trace: print '  --',vkey,':',term
            # Evaluate the term for the given values of Z['t'] etc
            try:
                coeff[unk] = eval(term)
            except:
                print 'problem'
                return False
            if not isinstance(coeff[unk], type(array(0))): # scalar
                coeff[unk] = coeff[unk]*ones(nvv)          # make array
            if trace: print ' coeff[',unk,'] =',coeff[unk]
        nuk = len(unks)                                    # nr of unknowns    
        if trace: print '\n unknowns:',nuk,':',unks

        # Now make the (rectangular) condition matrix, and solve for the unknowns:
        aa = zeros([nvv,nuk])                              # matrix
        for i in range(nvv):
            for j in range(nuk):
                aa[i,j] = coeff[unks[j]][i]
        bb = linear_least_squares(aa,vv)
        if trace: print bb
        solvec = bb[0]                                     # solution vector

        # Replace the default values of the Expression parameters:
        self._reset()
        for j in range(nuk):
            rr = self.__parm[unks[j]]
            rr['nominal'] = solvec[j]
            rr['default'] = solvec[j]
            rr['testval'] = solvec[j]                      # for plotting
            rr['stddev'] = 0.0
        if trace:
            self.display('fit')
            cc = plot(Z[plotvar],vv,'o')
            rr = dict()
            rr[plotvar] = True
            self.plot(**rr)
        return True


    #============================================================================
    # Plotting the (expanded) expression:
    #============================================================================

    def plotrec (self, new=None, trace=False):
        """Return the internal plot-record (see .eval())"""
        if new:
            self.__plotrec = new
        if trace:
            rr = self.__plotrec                   # convenience
            if not isinstance(rr, dict):
                print '\n** self.__plotrec:',rr,'\n'
            else:
                print '\n** self.__plotrec:'
                for key in rr.keys():
                    if key=='yy':
                        print '...',key,':'
                        for yy in rr[key]:
                            print '.......',yy
                    else:
                        print '...',key,':',rr[key]
                print ''
        return self.__plotrec

    #-----------------------------------------------------------------------

    def plot_Funklet(self, cells=None):
        """Make a plot of the (Funklet of) the expanded expression."""
        self.Funklet()
        if not self.__Funklet: return
        return self.__Funklet.plot(cells=cells)

    #-----------------------------------------------------------------------

    def plotall (self, **pp):
        """Plot the Expression in various subplots, in each of which a
        different parameter is varied. The x-axis variable (f,t,..) is
        automatic, but may be specified explicitly (e.g. t=True)."""

        # Find the nr of rows and columns of the figure: 
        keys = self.parm_order() 
        n = len(keys)                               # nr of parameters/subplots
        ncol = int(ceil(sqrt(n)))
        nrow = int(ceil(float(n)/ncol))

        # Make the plots:
        k = -1
        for row in range(1,nrow+1):
            for col in range(1,ncol+1):
                k += 1
                if k<n:
                    key = keys[k]
                    sp = nrow*100 + ncol*10 + k+1
                    rr = dict()
                    rr[key] = True
                    self.plot (_plot='linear', _test=True, _cells=None,
                               _legend=False,
                               _figure=1, _subplot=sp, _show=False, **rr)
        # Show the result:
        show()
        return True

    #-----------------------------------------------------------------------

    def format_expr (self, header=True):
        """Format the (unexpanded) expression in a list of one-line strings"""
        rr = dict(terms=[], parms=[])
        terms = find_terms(self.__expression, trace=False)

        if header:
            rr['terms'].append('Descr:   '+str(self.__descr))
            rr['terms'].append('Expression (unexpanded), term by term:')
        for term in terms['pos']:
            rr['terms'].append(' + '+term)
        for term in terms['neg']:
            rr['terms'].append(' - '+term)

        if header:
            rr['parms'].append('Its parameters (top-level only):')
        for key in self.__parm_order:
            parm = self.__parm[key]
            s1 = ' {'+key+'}:  '
            if isinstance(parm, Expression):
                rr['parms'].append(s1+'(Expr: '+parm.label()+'): '+parm.expression())
            elif isinstance(parm, Funklet):
                rr['parms'].append(s1+'(Funklet: '+parm._type+') '+parm._function)
            elif parm.has_key('nodename'):
                rr['parms'].append(s1+'MeqNode: '+parm['classname']+' '+parm['nodename'])
        return rr

    #-----------------------------------------------------------------------

    def plot (self, _plot='linear', _title=None, _test=False, _cells=None,
              _figure=None, _subplot=None, _legend=True, _show=True, **pp):
        """Plot the Expression for the specified parameter/variable value(s).
        See also self.eval()."""

        # if isinstance(_cells, meq._cells_type):
        # See MXM TDL_Funklet.py
        # if isinstance(_cells, dict):
        #     grid = _cells.grid                   # ......not yet used......

        # Work on the expanded version:
        ex = self.expanded()

        # Evaluate the (expanded) expression (produces ex.__plotrec):        
        ex.eval(_test=_test, **pp)

        # Use the plot-record generated by .eval() to make the plot:
        rr = ex.plotrec (trace=True)

        # Optional: select a particular figure (window) or subplot:
        if _figure:                                # numeric? 1,2,3,...
            figure(_figure)
        if _subplot:                               # e.g. 211,212,...?
            subplot(_subplot)
        mosaic = not _show              

        # Labels:
        xlabel(rr['xlabel'])
        ylabel(rr['ylabel'])
        if isinstance(_title, str): rr['title'] = _title
        title(rr['title'])
        if _legend: legend(rr['legend'])

        # Display the (unexpanded) expression (but not if mosaic):
        if not mosaic:
            ss = self.format_expr()
            y = 0.90
            for key in ['terms','parms']:
                y -= 0.02
                for i in range(len(ss[key])):
                    y -= 0.04
                    figtext(0.14,y,ss[key][i], color='gray')

        # Plot the data:
        # NB: Plotting rather stupidly fails with scalars....!?
        xx = rr['xx']
        scalar = False
        if not isinstance(xx, type(array(0))):
            scalar = True
            xx = array([xx,xx])
        elif len(xx)==1:
            scalar = True
            xx = array([xx[0],xx[0]])
            
        for i in range(len(rr['yy'])):
            yy = rr['yy'][i]
            if scalar: yy = array([yy[0],yy[0]])
            if _plot=='loglog':
                cc = loglog(xx, yy)                               # log x, log y
                cc = loglog(xx, yy, 'o', color=cc[0].get_color()) 
                xlabel('log('+rr['xlabel']+')')
                ylabel('log('+rr['ylabel']+')')
            elif _plot=='semilogx':
                cc = semilogx(xx, yy)                             # linear y, log x
                cc = semilogx(xx, yy, '+', color=cc[0].get_color()) 
                xlabel('log('+rr['xlabel']+')')
            elif _plot=='semilogy':
                cc = semilogy(xx, yy)                             # linear x, log y
                cc = semilogy(xx, yy, '+', color=cc[0].get_color()) 
                ylabel('log('+rr['ylabel']+')')
            else:
                cc = plot(xx, yy)                                 # default: both linear
                cc = plot(xx, yy, '+', color=cc[0].get_color())     
            if len(rr['annot'])>0:
                color = cc[0].get_color()
                text(rr['xannot'], yy[0], rr['annot'][i], color=color)

        if True:
            # Fill the plot-window, but leave a small margin:
            dx = 0.05*abs(rr['xmax']-rr['xmin'])                  # x-margin
            dy = 0.05*abs(rr['ymax']-rr['ymin'])                  # y-margin
            if dx==0.0: dx = 1.0
            if dy==0.0: dy = 1.0
            if _plot=='loglog':
                axis([rr['xmin'], rr['xmax']+dx, rr['ymin'], rr['ymax']+dy])
            elif _plot=='semilogx':
                axis([rr['xmin'], rr['xmax']+dx, rr['ymin']-dy, rr['ymax']+dy])
            elif _plot=='semilogy':
                axis([rr['xmin']-dx, rr['xmax']+dx, rr['ymin'], rr['ymax']+dy])
            else:
                axis([rr['xmin']-dx, rr['xmax']+dx, rr['ymin']-dy, rr['ymax']+dy])

        # Finished: show the plot (if required):
        if _show: show()
        return rr

    #---------------------------------------------------------------------------

    def compare(self, other, _plot=True, _legend=False, **pp):
        """Compare the Expression with another one (by subtraction)"""
        diff = Expression('{self}-{other}', unit=self.__unit,
                          label=self.label()+'.compare()',
                          descr='{'+self.label()+'}-{'+other.label()+'}')
        # Compare expanded versions, in which 'global' parameters {_x}
        # are ignored in favour of unique ones {self_x} and {other_x}.
        # Otherwise, the global parameters in self/other may clash...
        diff.parm('self', self.expanded(unique=True))
        diff.parm('other', other.expanded(unique=True))
        if _plot: diff.plot(_title=diff.descr(), _legend=_legend, **pp)
        return True

    #============================================================================
    # Evaluating the (expanded) expression:
    #============================================================================

    def evalarr (self, rr, key=None, trace=False):
        """Helper function to translate the given rr into a array of
        (one or more) values, for evaluation and/or plotting"""
        if isinstance(rr, (list,tuple)):            #
            vv = array(rr)                          # make into array
        elif isinstance(rr, type(array(0))):        # already an array
            vv = rr                                 # just copy
        elif isinstance(rr, dict):                  # assume fields min,max,span,nr
            rr.setdefault('nr',10)         
            rr.setdefault('min',1)          
            rr.setdefault('max',11)
            n = max(2,ceil(rr['nr']))               # safe nr of points
            factor = (rr['max']-rr['min'])/float(n-1) # scale-factor
            vv = rr['min'] + factor*array(range(n))
        elif isinstance(rr, bool):                  # use default plot-range
            if key in self.__var.keys():
                vv = self.evalarr(self.__var[key]['testvec'])
            elif key in self.__parm.keys():
                vv = self.evalarr(self.__parm[key]['testvec'])
            else:
                vv = array(range(2,9))              # some safe default
        elif isinstance(rr, NUMERIC_TYPES):         # NB: AFTER bool!
            vv = array(rr)                          # array of one
        else:                                       # error message?
            vv = array(range(1,12))                 # some safe default
        if trace: print '\n** evalarr(',rr,key,')\n   ->',vv,'\n'
        return vv

    #----------------------------------------------------------------------------

    def eval (self, _test=False, **pp):
        """Evaluate the (expanded) expression for the specified (pp) values of
        parameters {} and variables []. Use defaults if not specified.
        If _test==True, the parm/val testvals are used, otherwise their defaults.
        Two of the specified parameters/variables may be multiple (list,tuple,array).
        The longest multiple is the 'variable', and the result is in the form of
        array(s) of this length. The shortest multiple (if any) is the 'parameter',
        i.e. there will be as many result arrays as parameter values."""

        trace = False
        # trace = True
        if trace: print '\n** eval(_test=',_test,'):',pp

        # Special case: the Expression is purely numeric:
        nv = self.numeric_value()
        if not nv==None:
            self.__plotrec = None
            return array([nv])

        # Use the (scalar) default values in self.__parm,
        # unless other values have been specified via **pp.
        # If multiple values have been specified, use this parm as
        # 'parameter' for multiple plots. If two are multiple, use
        # the longest one as 'variable' (x-axis):
        variable = None
        parameter = None            
        nmult = 0
        rr = dict()
        unit = dict()                             # used in plot-legend
        field = 'default'                         # normal mode
        if _test: field = 'testval'               # test-mode
        for key in self.__parm.keys():            # all parameters
            if pp.has_key(key):                   # specified by name(key)
                value = self.evalarr(pp[key], key=key)
            else:
                value = self.evalarr(self.__parm[key][field])
            pkey = '{'+key+'}'
            unit[pkey] = self.__parm[key]['unit']
            # If multiple, the parm is used as 'parameter', or even 'variable'
            if rank(value)>0:                     # rank-0 array (scalar) has no length...!?
                if nmult==0:                 
                    nmult = 1                     # the first multiple one
                    parameter = pkey              #   use as 'parameter'
                    nmax = len(value)
                elif nmult==1:
                    nmult = 2                     # the second multiple one
                    if len(value)>nmax:           # if longer than 'parameter'
                        variable = pkey           #   use as x-axis
                    else:                         # if equal or shorter
                        parameter = pkey          #   use as 'parameter'
                        variable = parameter      #   use the first on as x-axis
                else:                             # too many multiple ones
                    value = array(value[0])       # make scalar
            rr[pkey] = value                      # use below
            if trace: print '-',key,pkey,'  parameter =',parameter,'  variable =',variable
                
        
        # Use the (scalar) default values in self.__var,
        # unless other values have been specified via **pp.
        for key in self.__var.keys():             # all variables
            if pp.has_key(key):                   # specified by name(key)
                value = self.evalarr(pp[key], key=key)
            else:
                value = self.evalarr(self.__var[key][field])
            vkey = '['+key+']'
            unit[vkey] = self.__var[key]['unit']
            # If multiple, the var is used as 'variable', if none specified yet:
            if rank(value)>0:            
                if not variable:                  # no variable specified yet
                    variable = vkey               # use var as 'variable'
                elif not parameter:               # no parameter specified yet
                    parameter = vkey              # use var as 'parameter'
                else:                             # too many multiple ones
                    value = array(value[0])       # make scalar
            rr[vkey] = value           
            if trace:
                print '-',key,vkey,'  variable =',variable,'  parameter =',parameter

        # A variable is always needed. If still None, use one of the available
        # variables (if any):
        if not variable:
            for key in ['l','m','t','f']:         # the earlier ones have precedence...
                vkey = '['+key+']'
                if not variable and key in self.__var.keys():
                    variable = vkey 
                    rr[variable] = self.evalarr(True, key)
                    unit[variable] = self.__var[key]['unit']
                if trace:
                    print '-',key,vkey,'  variable =',variable

            # Last resort: use the first key in rr
            if not variable:
                variable = rr.keys()[0]
                if trace: print '-  variable =',variable

        if trace:
            for key in rr.keys():
                print '- rr[',key,']:',rank(rr[key]),unit[key]

        #..............................................................
        # Initialise a plot-record (plotrec):
        plotrec = dict(yy=[], xx=rr[variable], test=_test,
                       xmin=-10, xmax=10, ymin=1e20, ymax=-1e20,
                       expr=self.__expression,
                       annot=[], xannot=0.0,
                       xlabel=variable,
                       ylabel=self.__label,
                       parameter=parameter, pp=None,
                       # title=self.tlabel(),
                       # title='',
                       title='Expression: '+str(self.__ident),
                       legend=[])
        if unit.has_key(variable) and unit[variable]:
                plotrec['xlabel'] += '   ('+str(unit[variable])+')'
        if not isinstance(plotrec['ylabel'], str):
            plotrec['ylabel'] = 'value'
        plotrec['ylabel'] = plotrec['ylabel'].replace('expanded_','')
        if isinstance(self.__unit, str):
            plotrec['ylabel'] += '  ('+self.__unit+')'
        if isinstance(plotrec['xx'], type(array(0))):
            plotrec['xannot'] = plotrec['xx'][0]
            plotrec['xmin'] = min(plotrec['xx'])
            plotrec['xmax'] = max(plotrec['xx'])
        else:                                    # assume scalar
            plotrec['xmin'] = plotrec['xx']
            plotrec['xmax'] = plotrec['xx']

        # Evaluate the expression for successive values of the parameter:
        # First check whether an eval/plot 'parameter' has been specified:
        n = 1
        if isinstance(parameter,str):
            n = len(rr[parameter])
            plotrec['pp'] = rr[parameter]
        first = True
        for i in range(n):
            qq = dict()
            for key in rr.keys():
                if key==parameter:
                    qq[key] = rr[key][i]
                elif key==variable:
                    qq[key] = rr[key]
                else:
                    qq[key] = rr[key]                # array of rank 0 (scalar)
                    if first:
                        if not any(rr[key]==0):      # show in legend only if non-zero
                            legend = key+'='+self.format_val(qq[key])
                            if unit[key]: legend += '  ('+unit[key]+')'
                            plotrec['legend'].append(legend)
                if trace: print '  -- qq[',key,']:',type(qq[key]),'=',qq[key]
            if trace and parameter:
                print '-',i,'/',n,': qq[',parameter,']=',qq[parameter]
            r1 = self.evalone(qq, _test=_test, trace=trace)
            plotrec['yy'].append(r1)
            plotrec['ymin'] = min(plotrec['ymin'],min(r1))
            plotrec['ymax'] = max(plotrec['ymax'],max(r1))
            if parameter:
                # annot = parameter+'='+str(qq[parameter])
                annot = parameter+'='+self.format_val(qq[parameter])
                if unit[parameter]: annot += '  ('+unit[parameter]+')'
                plotrec['annot'].append(annot)
            first = False

        # The plot-record is stored internally (see self.plot())
        self.plotrec (new=plotrec, trace=trace)

        # The return value depends on the shape:
        if len(plotrec['yy'])==1:
            return plotrec['yy'][0]               # just an array
        return plotrec['yy']                      # a list of arrays

    #-----------------------------------------------------------------------

    def format_val (self, v):
        """Helper function to format a numerical value, for annotation.
        NB: This is mainly to correct a strange bug in str(v)...."""
        s = str(v)
        n = len(s)
        if len(s)>2:
            if s[1]=='.': s = s[0:5]              # e.g.  0.1000000000001
            if s[2]=='.': s = s[0:6]              # e.g. -0.3000000000001
        return s

    #-----------------------------------------------------------------------

    def evalone (self, pp, _test=False, trace=False):
        """Helper function called by self.eval()"""

        seval = deepcopy(self.__expression)
        if trace:
            print '\n .... evalone():',seval
            print '     ',pp

        # Replace parameters and variables with parameter names Z[i]:
        Z = []
        keys = pp.keys()
        for i in range(len(keys)):
            key = keys[i]
            Z.append(pp[key])
            substring = 'Z['+str(i)+']'
            seval = seval.replace(key, substring)
            if trace:
                print '- substitute',key,' with: ',substring
        if trace:
            print '  -> seval =',seval
            print '  -> Z =',Z

        # Evaluate the seval string:
        try:
            if _test:
                self.__test_seval = seval
            else:
                self.__eval_seval = seval
            result = eval(seval)                  # covers most things
        except:
            print '\n** ERROR in eval(',seval,')\n'
            print sys.exc_info()
            return False                          # something wrong
        if _test:
            self.__test_result = result
        else:
            self.__eval_result = result

        # Return the (numeric) result:
        if not isinstance(result,type(array(0))):
            result = array([result])
        if trace: print '  -> evalone() ->',type(result),'=',result,'\n'
        return result



    #============================================================================
    # The Expression can be converted into a Funklet:
    #============================================================================

    def Funklet (self, trace=False):
        """Return the corresponding Funklet object. Make one if necessary."""

        if trace: print '\n** .Funklet():',self.oneliner()

        # Work on the expanded version:
        ex = self.expanded()

        # Avoid double work:
        if self.__Funklet:  return self.__Funklet
        
        if len(ex.__parmtype['MeqNode'])>0:
            # If there are MeqNode children, the Expression should be turned into
            # a MeqFunctional node. It is not possible to make a Funklet.
            print '\n** .Funklet(): Expression has MeqNode child(ren)!\n'
            return False
        
        nv = ex.numeric_value(trace=False)
        if not nv==None:
            # Special case: the Expression is purely numeric
            coeff = [nv]
            expr = 'p0'

        else:           
            expr = deepcopy(ex.expression())
            # Replace the parameters {} with pk = p0,p1,p2,...
            # and fill the coeff-list with their default values
            coeff = []
            keys = ex.__parm.keys()
            for k in range(len(keys)):
                pk = 'p'+str(k)
                expr = expr.replace('{'+keys[k]+'}', pk)
                coeff.append(ex.__parm[keys[k]]['default'])
                if trace: print '- parm',k,keys[k],pk,coeff
            # Replace the valiables [] with x0 (time), x1(freq) etc
            for key in ex.__var.keys():
                xk = ex.__var[key]['xn']
                expr = expr.replace('['+key+']', xk) 
                if trace: print '- var',key,xk

        # Make the Funklet, and attach it:
        f0 = Funklet(funklet=record(function=expr, coeff=coeff))
        # Alternative
        #   f0 = meq.polc(coeff=coeff, subclass=meq._funklet_type)
        #   f0.function = expr
        ex.__Funklet = f0
        self.__Funklet = f0
        ex.__Funklet_function = expr            # for display only
        self.__Funklet_function = expr          # for display only

        # Finished:
        if trace:
            print '   Funklet()  -> expr =',expr
            print dir(f0)
            print ''
        return self.__Funklet

    #===========================================================================
    # Functions dealing with the available MeqParms (for solving etc)
    #===========================================================================

    def MeqParms (self, group='all', trace=False):
        """Access to the (groups of) MeqParm nodes associated with this Expression"""
        if not self.__MeqParms:
            self.__MeqParms = self.expanded().find_MeqParms()
        if self.__MeqParms.has_key(group):
            return self.__MeqParms[group]
        return False


    def find_MeqParms (self, trace=False):
        """Find the available MeqParm node names in the Expression"""
        self.__MeqParms = dict(all=[])
        klasses = dict()
        done = []
        for key in self.__parm_order:
            parm = self.__parm[key]
            if isinstance(parm, dict) and parm.has_key('node'):
                classwise(parm['node'], klasses=klasses, done=done)
        if klasses.has_key('MeqParm'):
            self.__MeqParms['all'].extend(klasses['MeqParm'])
        return self.__MeqParms

    #===========================================================================
    # Functions that require a nodescope (ns)
    #===========================================================================

    def var2node (self, ns, trace=False):
        """Convert the variable(s) in self.__expression to node(s).
        E.g. [t] is converted into a MeqTree node, etc"""
        for key in self.__var.keys():
            rr = self.__var[key]                        # var definition record
            pkey = rr['node']                           # var key, e.g. 't'
            name = 'Expr_'+self.label()+'_'+pkey
            node = self._unique_node (ns, name, qual=None, trace=trace)
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
            if not pkey in self.__parm_order:
                self.__parm_order.append(pkey)
                self._create_parm(pkey)                 # create a new parm
                self.parm(pkey, node)                   # re-define the new parm
        self.__var = dict()                             # no more vars in expression
        if trace: self.display('.var2node()', full=True)
        return True

    #---------------------------------------------------------------------------

    def parm2node (self, ns, trace=False):
        """Convert parameter(s) in self.__expression to node(s).
        E.g. {xx} is converted into a MeqParm node, etc"""
        for key in self.__parm.keys():
            parm = self.__parm[key]
            name = 'Expr_'+self.label()+'_'+key
            node = self._unique_node (ns, name, qual=None, trace=trace)
            funklet = None
            if key in self.__parmtype['Expression']:
                funklet = parm.Funklet()
            elif key in self.__parmtype['Funklet']:
                funklet = parm
            elif key in self.__parmtype['MeqNode']:
                pass                                    # already a node
            elif parm.has_key('constant') and parm['constant']==True:
                # NB: The alternative is to modify self.__expression so that
                #     it contains an explicit number, rather than a node.
                # This is OK too, since only a MeqParm can be solved for....
                node << Meq.Constant(parm['default'])
                self.parm(key, node)                    # redefine the parm
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

    def subExpression (self, substring, label='substring', trace=False):
        """Convert the specified substring of self.__expression
        into a separate Expression object, including its parm/var info."""
        if trace:
            print '\n** .subExpression(',substring,'):'
        index = self.__expression.rfind(substring)
        if index<0:
            print '\n** .subExpression(',substring,'): not found in:',self.__expression,'\n'
            return False
        e1 = Expression(substring, label, descr='from: '+self.descr())
        for key in e1.__parm.keys():
            e1.__parm[key] = self.__parm[key]
            if trace: print '- copy parm[',key,']:',e1.__parm[key]
        for key in e1.__var.keys():
            e1.__var[key] = self.__var[key]
            if trace: print '- copy var[',key,']:',e1.__var[key]
        e1.__quals = self.__quals
        if trace:
            e1.display('subExpression()', full=True)
        return e1

    #--------------------------------------------------------------------------

    def subTree (self, ns, trace=False):
        """Make a subtree of separate nodes"""
        if trace:
            print '\n** .subTree():',self.tlabel()

        # Split self.__expression into additive terms:
        rr = find_terms(self.__expression, trace=trace)
        cc = dict(pos=[], neg=[])
        for key in cc.keys():                           # 'pos','neg'
            for i in range(len(rr[key])):
                subex = self.subExpression(rr[key][i], label=key+'_term_'+str(i))
                if trace: print subex.oneliner()
                cc[key].append(subex.MeqNode(ns))

        # Make separate subtrees for the positive and negative terms:
        for key in cc.keys():                           # 'pos','neg'
            if len(cc[key])==0:                         # no nodes
                cc[key] = None
            elif len(cc[key])==1:                       # one node: keep it
                cc[key] = cc[key][0]
            else:                                       # more than one: MeqAdd
                cc[key] = ns << Meq.Add(children=cc[key])

        # Subtract the negative from the positive:
        if cc['pos']==None:
            node = cc['neg']
        elif cc['neg']==None:
            node = cc['pos']
        else:
            node = ns << Meq.Subtract(cc['pos'],cc['neg'])
        # Return the root node of the resulting subtree:
        return node


    #--------------------------------------------------------------------------

    def MeqParm (self, ns, name=None, qual=None, trace=False):
        """Make a MeqParm node by converting the (expanded) expression into
        a Funklet, and using that as init_funklet."""
        if not self.__MeqParm:                          # avoid duplication
            funklet = self.Funklet()
            if isinstance(funklet, bool): return False
            if not name: name = 'Expr_'+self.label()+'_MeqParm'
            self.__MeqParm = self._unique_node (ns, name, qual=qual, trace=trace)
            self.__MeqParm << Meq.Parm(init_funklet=funklet)
        return self.__MeqParm

    #---------------------------------------------------------------------------

    def MeqNode (self, ns, name=None, qual=None, expand=True, trace=False):
        """Make a single node/subtree from the Expression. In most cases,
        this will be a MeqParm, with the expression Funklet as init_funklet.
        But if the expression has at least one parameter that is a node,
        the result will be a MeqFunctional node."""
        nv = self.numeric_value()
        if not nv==None:
            # Special case: the Expression is purely numeric
            if not self.__MeqConstant:
                if not name: name = 'Expr_'+self.label()+'_MeqConstant'
                self.__MeqConstant = self._unique_node (ns, name, qual=qual, trace=trace)
                self.__MeqConstant  << Meq.Constant(nv)
            node = self.__MeqConstant
        elif len(self.__parmtype['MeqNode'])>0:
            node = self.MeqFunctional(ns, name=name, qual=qual,
                                      expand=expand, trace=trace)
        else:
            node = self.MeqParm(ns, name=name, qual=qual, trace=trace)
        self.__MeqNode = node
        return node

    #---------------------------------------------------------------------------

    def MeqFunctional (self, ns, name=None, qual=None, expand=True, trace=False):
        """Make a MeqFunctional node from the Expression, by replacing all its
        parameters and variables with nodes (MeqParm, MeqTime, MeqFreq, etc).
        If expand==True (default), the Functional is made from the expanded
        expression. Note that, if expand==False, the object itself is modified!!"""
        if self.__MeqFunctional: return self.__MeqFunctional    # avoid duplication
        if expand:
            ex = self.expanded(expand=True, trace=trace)
            f0 = ex.make_MeqFunctional (ns, name=name, qual=qual, trace=trace)
        else:
            f0 = self.make_MeqFunctional (ns, name=name, qual=qual, trace=trace)
        self.__MeqFunctional = f0
        return self.__MeqFunctional

    #..........................................................................
        
    def make_MeqFunctional (self, ns, name=None, qual=None, trace=False):
        """Helper function that does the work for .MeqFunctional()"""
        if trace: print '\n** MeqFunctional(',name,qual,'):'
        self.parm2node (ns, trace=trace)                # convert parms to nodes
        self.var2node (ns, trace=trace)                 # convert vars to nodes
        function = deepcopy(self.__expression)
        children = []
        nodenames = []
        child_map = []                                  # for MeqFunctional
        k = -1
        for key in self.__parm.keys():
            k += 1                                      # increment
            xk = 'x'+str(k)                             # x0, x1, x2, ..
            function = function.replace('{'+key+'}',xk)
            parm = self.__parm[key]                     # parm definition record
            nodename = parm['nodename']
            if not nodename in nodenames:               # once only
                nodenames.append(nodename)
                children.append(parm['node'])
            child_num = 1 + nodenames.index(nodename)
            rr = record(child_num=child_num, index=parm['index'],
                        nodename=parm['nodename'])
            if trace: print '-',key,xk,rr
            child_map.append(rr)
        if not name: name = 'Expr_'+self.label()+'_MeqFunctional'
        self.__MeqFunctional = self._unique_node (ns, name, qual=qual, trace=trace)
        self.__MeqFunctional << Meq.Functional(children=children,
                                               function=function,
                                               child_map=child_map)
        self.__expanded = True
        return self.__MeqFunctional


    #--------------------------------------------------------------------------

    def MeqCompounder (self, ns, name=None, qual=None, 
                       extra_axes=None, common_axes=None, trace=False):
        """Make a MeqCompunder node from the Expression. The extra_axes argument
        should be a MeqComposer that bundles the extra (coordinate) children,
        described by the common_axes argument (e.g. [hiid('l'),hiid('m')]."""                   

        # Make a MeqParm node from the Expression:
        parm = self.MeqParm(ns, name=name, qual=None, trace=trace)
        ### if isinstance(funklet, parm): return False

        # Check whether there are extra axes defined for all variables
        # in the expression other than [t] and [f]:
        caxes = []
        caxstring = ''
        for cax in common_axes:
            caxes.append(str(cax))
            caxstring += str(cax)
        for key in self.__var.keys():
            if not key in ['t','f']:
                if not key in caxes:
                    print '\n** .MeqCompouder(',name,qual,'): missing cax:',key,'\n'
                
        # NB: The specified qualifier (qual) is used for the MeqCompounder,
        # but NOT for the MeqParm. The reason is that the Compounder has more
        # qualifiers than the Parm. E.g. EJones_X is per station, but the
        # compounder and its children (l,m) are for a specific source (q=3c84)
        if not name: name = 'Expr_'+self.label()+'_'+caxstring
        node = self._unique_node (ns, name, qual=qual, trace=trace)
        node << Meq.Compounder(children=[extra_axes,parm], common_axes=common_axes)
        return node


    #================================================================================
    # Node-names:
    #================================================================================

    def quals(self, *args, **kwargs):
        """Get/set the overall MeqNode node-name qualifier(s)"""

        # Reset the object (if nominal, reset parm defaults to nominal, else stddev):
        nominal = True
        if len(kwargs)>0: nominal=False
        # if len(args)>0: nominal=False
        self._reset (nominal=nominal)              # BEFORE modifying self.__quals

        # Modify self.__quals (always!):
        for key in kwargs.keys():
            self.__quals[key] = kwargs[key]        # 
        # Always return the current self.__quals
        # print '\n** .quals():   args =',args,'  kwargs =',kwargs,'  ->',self.__quals
        return self.__quals


    #--------------------------------------------------------------------------

    def _unique_node (self, ns, name, qual=None, trace=False):
        """Helper function to generate a unique node-name.
        It first tries one with the internal and the specified qualifiers.
        If that exists already, it add a unique qualifier (uniqual)."""

        trace = False
        
        # Combine any specified qualifiers (qual) with any internal ones:
        quals = deepcopy(self.__quals)
        qualin = deepcopy(qual)
        if isinstance(qual, dict):
            for key in qual.keys():
                quals[key] = qualin[key]
            qualin = None
        if len(quals)==0: quals = None
        
        # First try without uniqual:
        if isinstance(quals, dict):
            if qualin:
                node = ns[name](**quals)(qualin)
            else:
                node = ns[name](**quals)
        elif qualin:
            node = ns[name](qualin)
        else:
            node = ns[name]

        # If the node exists already, make a unique one:
        if node.initialized():
            # Add an extra qualifier to make the nodename unique:
            uniqual = _counter (name, increment=-1)
            if isinstance(quals, dict):
                if qualin:
                    node = ns[name](**quals)(qualin)(uniqual)
                else:
                    node = ns[name](**quals)(uniqual)
            elif qualin:
                node = ns[name](qualin)(uniqual)
            else:
                node = ns[name](uniqual)
                
        if trace: print '\n** ._unique_node(',name,qual,') ->',node
        return node


#----------------------------------------------------------------------------------

def classwise (node, klasses=dict(), done=[], level=0, trace=False):
   """Recursively collect the nodes of the given subtree, divided in classes """

   # Keep track of the processed nodes (to avoid duplication):
   if node.name in done: return True
   done.append(node.name)

   # Append the nodename to its (klass) group:
   klass = node.classname
   klasses.setdefault(klass, [])
   klasses[klass].append(node.name)

   # Recursive:
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

def find_enclosed (expr, brackets='{}', trace=False):
    """Return a list of substrings that are enclosed in the specified brackets.
    e.g. expr='{A}+{B}*{A}' would produce ['A','B']"""
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
                    cc.append(substring)
                    if trace: print '-',i,level,cc
    # Some checks:
    if not level==0:
        return False
    if trace: print '   -> (',len(cc),level,'):',cc
    return cc

#----------------------------------------------------------------------------

def find_terms (expr, level=0, trace=False):
    """Find the additive terms of the given mathematical expression (string),
    i.e. the subexpressions separated by plus and minus signs.
    Return a record with two lists: pos and neg."""

    # trace = True
    if trace: print '\n** find_terms(): ',expr

    rr = dict(pos=[],neg=[])                     # initialise output record
    if level>5:
        print '\n** max level exceeded:',level,expr,'->',rr
        return rr

    nest = 0
    i1 = 0
    ncpt = 0
    n2 = 0
    expr = deenclose(expr, '()', trace=False)
    nchar = len(expr)
    key = 'pos'
    for i in range(len(expr)):
        last = (i==(nchar-1))                    # True if last char
        # if trace: print nest,nest*'..',i,ncpt,n2,last,':',expr[i]
        if last:
            term = expr[i1:(i+1)]
            append_term (rr, term, key, n2, i, nest,
                         level=level, trace=trace)
            if expr[i]==')': nest -= 1           # closing bracket
        elif expr[i]=='(':                       # opening bracket
            nest += 1
        elif expr[i]==')':                       # closing bracket
            nest -= 1
        elif nest>0:                             # nested
            if level==0:
                if expr[i] in ['+','-']: n2 += 1 # ignore, but count the higher-nest +/-
        elif expr[i] in ['+','-']:               # end of a term
            if ncpt>0:                           # some chars in term
                term = expr[i1:i]
                append_term (rr, term, key, n2, i, nest,
                             level=level, trace=trace)
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

def append_term (rr, term, key, n2, i, nest,
                 level=0, trace=False):
    """Helper function for .find_terms"""
    if n2>0:                         # term contains +/-
        rr1 = find_terms(term, level=level+1, trace=False)
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
        # Replace all C[i][j] in the Funklet expression with {<label>_ij}
        coeff = Funklet._coeff                     # 2D, e.g. [[2,3],[0,2]] 
        for i in range(len(coeff)):
            for j in range(len(coeff[i])):
                pname = label+'_'+str(i)+str(j)
                expr = expr.replace('C['+str(i)+']['+str(j)+']', '{'+pname+'}')
    else:                                          # Any other 'functional' Funklet:
        # Replace all C[i] in the Funklet expression with {<label>_i} 
        coeff = array(Funklet._coeff).flat         # flatten first....?
        for i in range(len(coeff)):
            pname = label+'_'+str(i)
            expr = expr.replace('C['+str(i)+']', '{'+pname+'}')

    # Replace all x[n] in the Funklet expression to [t],[f] etc
    expr = expr.replace('x[0]','[t]')
    expr = expr.replace('x[1]','[f]')
    expr = expr.replace('x[2]','[l]')              # .........?
    expr = expr.replace('x[3]','[m]')              # .........?

    # Make the Expression object:
    e0 = Expression(expr, 'Funklet_'+label, descr='from: '+self.descr())

    # Transfer the coeff default values: 
    if Funklet._type in ['MeqPolc','MeqPolcLog']:
        for i in range(len(coeff)):
            for j in range(len(coeff[i])):
                pname = label+'_'+str(i)+str(j)
                e0.parm(pname, coeff[i][j])
    else:
        for i in range(len(coeff)):
            pname = label+'_'+str(i)
            e0.parm(pname, coeff[i])

    # Finished: return the Expression object:
    if trace: e0.display('Funklet2Expression()', full=True)
    return e0



#=======================================================================================


def polc_Expression(shape=[1,1], coeff=None, label=None, unit=None,
                    ignore_triangle=True,
                    type='MeqPolc', f0=1e6, t0=1.0,
                    fit=None, plot=False, trace=False):
    """Create an Expression object for a polc with the given shape (and type).
    Parameters can be initialized by specifying a list of coeff.
    The coeff will be assumed 0 for all those missing in the list.
    Optionally, the polc coeff may be determined by fitting to a given
    set of polc function values vv(t,f): fit=dict(vv=, tt=, ff=)."""

    if trace:
        print '\n** polc_Expression(',shape,coeff,label,type,'):'
        if fit: print '       fit =',fit
    if coeff==None: coeff = []
    if not isinstance(coeff, (list,tuple)): coeff = [coeff]
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
                pp[pk] = 0.0
                testinc[pk] = sign*(10**(-i-j))          # test-increment 
                if len(coeff)>k:
                    pp[pk] = coeff[k]
                help[pk] = label+'_'+str(j)+str(i)
                if not first: func += '+'
                func += '{'+pk+'}'                       # {c01}
                for i2 in range(j): func += '*'+tvar     # e.g:  *[t]
                for i1 in range(i): func += '*'+fvar     # e.g:  *[f]
                first = False
                if trace: print '-',i,j,' (',i+j,ijmax,') ',k,pk,':',func
    result = Expression(func, label, descr='polc_Expression', **pp)
    if True:
        # Modify the parm definitions:
        for key in pp.keys():
            result.parm(key, testinc=testinc[key])

    # Define the Expression parameters, if necessary:
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

    # Assign unit strings:
    # NB: The default value has to be repeated here!
    sunit = ''
    if isinstance(unit, str):
        sunit = unit
        result.parm('c00', pp['c00'], unit=sunit)
    if pp.has_key('c01'): result.parm('c01', pp['c01'], unit=sunit+'/Hz')
    if pp.has_key('c02'): result.parm('c02', pp['c02'], unit=sunit+'/Hz/Hz')
    if pp.has_key('c11'): result.parm('c11', pp['c11'], unit=sunit+'/s/Hz')
    if pp.has_key('c10'): result.parm('c10', pp['c10'], unit=sunit+'/s')
    if pp.has_key('c20'): result.parm('c20', pp['c20'], unit=sunit+'/s/s')

    # Optionally, fit the new polc to a given set of values(f,t):
    if isinstance(fit, dict):
        result.fit(**fit)

    # insert help......?

    # Finished:
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
        pp.__delitem__('_legend')

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
    print '\n*******************\n** Local test of: JEN_Expression.py:\n'
    from numarray import *
    # from numarray.linear_algebra import *
    from Timba.Trees import TDL_display
    from pylab import *              
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

    if 0:
        e0 = Expression()
        e0.quals()
        e0.quals(4,6,'7')
        e0.quals(a=1, b=2)
        e0._unique_node(ns, 'xxx', trace=True)
        e0._unique_node(ns, 'xxx', qual=dict(c=5), trace=True)
        node = e0._unique_node(ns, 'xxx', qual=5, trace=True)
        node << 0.9
        node = e0._unique_node(ns, 'xxx', qual=5, trace=True)

    if 0:
        e0 = Expression('3*[t]')
        # e0.display()
        e0.evalarr(range(5), trace=True)
        e0.evalarr(dict(min=23,max=24,nr=12), trace=True)
        e0.evalarr(dict(min=23,max=24), trace=True)
        # e0.evalarr(True, key='t', trace=True)

    #-------------------------------------------------------------------

    if 0:
        f0 = Funklet()
        # f0.setCoeff([[1,0,4],[2,3,4]])       # [t]*[f]*[f] highest order
        # f0.setCoeff([[1,0],[2,3]]) 
        f0.setCoeff([1,0,2,3])               # [t] only !!
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
        e1 = Expression('{A}*cos({B}*[f])-{C}+({neq}-67)', label='e1')
        e1.parm('A', -5, constant=True, stddev=0.1)
        # e1.parm('B', 10, help='help for B')
        # e1.parm('C', f0, help='help for C')
        # e1.quals(a=5,b=6)
        e1.display('initial', full=True)

        if 0:
            e1.expand()
            e1.display('after .expand', full=True)
            e1.expanded().display('.expanded()', full=True)

        if 0:
            e1.display(e1.quals(a=-1,b=17))
            e1.display(e1.quals(a=5,b=6))
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

        if 1:
            node = e1.subTree (ns, trace=True)
            e1.display()
            TDL_display.subtree(node, 'subTree', full=True, recurse=10)
            
        if 0:
            f1 = e1.Funklet(trace=True)
            e1.display()
            # e2 = Funklet2Expression(f1, 'A', trace=True)
            # e2.plot()

        if 0:
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

    if 1:
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
        Xbeam.parm ('_D', default=25.0, unit='m', help='WSRT telescope diameter')
        Xbeam.parm ('lambda', default=Expression('3e8/[f]', label='lambda',
                                                 descr='observing wavelength'), unit='m')
        Xbeam.parm ('_ell', default=0.1, help='Voltage beam elongation factor (1+ell)')
        # Xbeam.display(full=True)
        Xbeam.expanded().display(full=True)
        # Xbeam.plot()

        if 1:
            Ybeam = Xbeam.copy(label='gaussYbeam', descr='WSRT Y voltage beam (gaussian)')
            Ybeam.parm ('_ell', default=-0.1, help='Voltage beam elongation factor (1+ell)')
            # Ybeam.plot(l=True, m=True)
            # Explot(Xbeam, Ybeam, _legend=True, l=True, m=True)
            Xbeam.compare(Ybeam, l=True, m=True)
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

        qqual = dict(q='3c56')
        major = ns.major_axis(**qqual) << Meq.Parm(0.1)
        minor = ns.minor_axis(**qqual) << Meq.Parm(0.01)
        pa = ns.posangle(**qqual) << Meq.Parm(-0.1)
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
        for x in [3,3.4,12345678907777777777777,'a',3+7j]:
            tf = isinstance(x, NUMERIC_TYPES)
            print '- isinstance(',x,type(x),', NUMERIC_TYPES) ->',tf

    if 0:
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
        deenclose('{aa_bb}', trace=True)
        deenclose('{aa}+{bb}', trace=True)
        deenclose('{{aa}+{bb}}', trace=True)

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

    print '\n*******************\n** End of local test of: JEN_Expression.py:\n'




#============================================================================================
# Remarks:
#
# - MXM cannot interprete pk for k>9. Use C[k] (and X[n]) instead?
#
# - Funklets cannot handle purely numeric expressions (e.g. '67')
#
# - Fitting
#
# - subtrees


#============================================================================================

    
