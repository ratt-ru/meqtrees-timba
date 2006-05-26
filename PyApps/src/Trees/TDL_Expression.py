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
#     -) e0 = Expression ("{A} + {ampl}*cos({phase}*[t])" [, label='<label>'])
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
from pylab import *
from copy import deepcopy
from Timba.Trees.TDL_Leaf import *
from Timba.Meq import meq
from Timba.Contrib.MXM.TDL_Funklet import *


#***************************************************************************************
#***************************************************************************************

class Expression:
    def __init__(self, expression='-1.23456789', label='<label>', **pp):
        """Create the object with a mathematical expression (string)
        of the form:  {aa}*[t]+cos({b}*[f]).
        Variables are enclosed in square brackets: [t],[f],[m],...
        Parameters are enclosed in curly brackets: {aa}, {b}, ...
        Simple information about parameters (type, default value)
        may be supplied via keyword arguments pp. More detailed
        information may be supplied via the function .parm()."""

        self.__label = _unique_label(label)
        self.__expression = expression
        self.__numeric_value = None  
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

        # The expression may be purely numeric:
        self.numeric_value()

        # Initialise derived quantities:
        self._reset()

        # Finished:
        return None


    #----------------------------------------------------------------------------

    def numeric_value(self, trace=True):
        """The expression may be purely numeric (None if not)"""
        self.__numeric_value = None
        if len(self.__parm)==0 and len(self.__var)==0:
            try:
                v = eval(self.__expression)
            except:
                return self.__numeric_value
            self.__numeric_value = v
        if trace: print '\n**',self.__expression,': numeric_value =',self.__numeric_value,'\n'
        return self.__numeric_value


    #----------------------------------------------------------------------------

    def _reset (self, nominal=True):
        """Reset the object to its original state."""
        self.__quals = dict()
        self.__plotrec = None
        self.__expanded = False
        self.__Functional = None
        self.__MeqParm = None
        self.__Funklet = None
        self.__Funklet_function = None
        self.__test_result = None
        self.__eval_result = None
        self.__test_seval = None
        self.__eval_seval = None
        for key in self.__parm.keys():
            rr = self.__parm[key]
            if isinstance(rr, Expression):
                rr._reset(nominal=nominal)
            elif isinstance(rr, Funklet):
                pass
            elif rr.has_key('index'):
                pass
            elif nominal:
                rr['default'] = rr['nominal']
            elif rr['stddev']>0:
                rr['default'] = gauss(rr['nominal'], rr['stddev'])
            else:
                rr['default'] = rr['nominal']
        return True
    

    #----------------------------------------------------------------------------
    # Some access functions:
    #----------------------------------------------------------------------------

    def label (self):
        """Return the (unique) label of this Expression object"""
        return self.__label

    def tlabel (self):
        """Return a concatenation of object type and label"""
        return 'Expression: '+self.__label
        # return str(type(self))+':'+self.__label

    def test_result (self):
        """Return the result of evaluation with the test-values."""
        return self.__test_result

    def order (self):
        """Return the order of parameters in the input expression"""
        return self.__order

    def expression (self):
        """Return the (mathematical) expression"""
        return self.__expression

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
        if self.__quals: ss += '(quals='+str(self.__quals)+') '
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
        print indent,'- default node qualifiers: ',str(self.__quals)
        print indent,'- numeric value: ',str(self.__numeric_value)
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
            print indent,'  - _type ->',str(self.__Funklet._type)
            # print dir(self.__Funklet)
            print indent,'- eval() ->',str(self.__Funklet.eval())
            
        print '**\n'



        
    #============================================================================
    # Manual definition of named parameters and variables:
    #============================================================================

    def parm (self, key=None, default=None, constant=False, polc=None,
              help=None, stddev=0, testval=None, trace=True):
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
            # - nominal: nominal default value (i.e. without stddev)
            # - stddev: stddev to be used for simulaton.
            if testval==None: testval = default
            self.__parm[key] = dict(default=default, constant=constant,
                                    help=help, testval=testval,
                                    nominal=default, stddev=stddev)

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
        rr = dict(xn='xn', node=None, default=default,
                  testval=testval, unit=None, plotrange=range(10))

        # self.__var_def = {'x0':"time",'x1':"freq"}
        if key[0]=='t':                          # time
            rr['node'] = 'MeqTime'
            rr['xn'] = 'x0'
            rr['unit'] = 's'
        if key[0]=='f':                          # freq, fGHz, fMHz
            rr['node'] = 'MeqFreq'
            rr['xn'] = 'x1'
            rr['unit'] = 'Hz'
            rr['plotrange'] = dict(min=1.2e8, max=1.5e8, nr=13)
        if key[0]=='l':
            rr['node'] = 'MeqL'                  # .....!!
            rr['xn'] = 'x2'
            rr['unit'] = 'rad'
            fwhm_rad = 0.1                       # ~ 5 deg    
            rr['plotrange'] = dict(min=-fwhm_rad, max=fwhm_rad, nr=13)
        if key[0]=='m':
            rr['node'] = 'MeqM'                  # .....!!
            rr['xn'] = 'x3'
            rr['unit'] = 'rad'
            fwhm_rad = 0.1                       # ~ 5 deg    
            rr['plotrange'] = dict(min=-fwhm_rad, max=fwhm_rad, nr=13)
        
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
        self.__xchild_order = []
        self.__xvar = deepcopy(self.__var)

        # Then replace the (expanded) Expression parameters:
        for key in self.__order:
            parm = self.__parm[key]

            if isinstance(parm, Funklet):
                # Convert a Funklet to an Expression first
                parm = Funklet2Expression(parm, key)

            if isinstance(parm, Expression):
                # Merge the parm (expanded) expr with its own:
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

            else:
                # Otherwise, just copy (numeric or node):
                self.__xorder.append(key)
                self.__xparm[key] = self.__parm[key]
                
        # Finished, do some bookkeeping:
        self.__expanded = True
        if trace: print '   ->',self.__xexpr
        self.__test_result = self.eval(_test=True)
        self.__eval_result = self.eval()
        return True
    



    #============================================================================
    # Fit the Expression (e.g. a polc) to a set of given points.
    #============================================================================

    def fit (self, vv, **pp):
        """Adjust the Expression default parameters to make them fit the
        values of the specified points v(f,t,l,m)"""

        trace = True
        if trace: print '\n** fit(',type(vv),len(vv),'):'

        # The function values at the specified points:
        nvv = len(vv)
        vv = array(vv)
        if trace: print '- vv =',type(vv),' nvv =',nvv

        # Check whether there are values for all relevant variables:
        self.expand()
        CCC = dict()
        for key in self.__xvar.keys():
            if not pp.has_key(key):
                print 'need values for variable:',key
                return False
            elif len(pp[key])==1:
                pass                            # OK...?
            elif not len(pp[key])==nvv:
                print 'length mismatch for variable:',key,':',nvv,len(pp[key])
                return False
            else:                               # OK
                CCC[key] = array(pp[key])
                if trace: print '- CCC[',key,'] =',CCC[key]
            

        # Assume a linear expression, with one (multiplicative) parameter
        # per term. The latter are the unknowns to be solved:
        terms = find_terms(self.__xexpr)
        unks = []
        coeff = dict()
        for term in terms['pos']:                         # 'neg' too!
            unknown = find_enclosed(term,'{}')
            if trace: print '\n- term:',term,'->',unknown
            if len(unknown)>1:
                print 'more than one unknown in term:',term
                return False
            unk = unknown[0]                              # string
            unks.append(unk)                              # list of unkowns

            # Calculate the coeff of the unkowns in the condition equations:
            # First replace the unkowns with 1.0
            term = term.replace('{'+unk+'}', '1.0')
            # Then replace the variables [f],[t],etc with CCC['f'],CCC['t'] etc:
            for vkey in CCC.keys():
                term = term.replace('['+vkey+']', 'CCC[\''+vkey+'\']')
                if trace: print '  --',vkey,':',term
            # Evaluate the term for the given values of CCC['t'] etc
            try:
                coeff[unk] = eval(term)
            except:
                print 'problem'
                return False
            if not isinstance(coeff[unk], type(array(0))):     # scalar
                coeff[unk] = coeff[unk]*ones(nvv)              # make array
            if trace: print ' coeff[',unk,'] =',coeff[unk]
        nuk = len(unks)                                    # nr of unknowns    
        if trace: print '\n unknowns:',nuk,':',unks

        # Now make the (rectangular) condition matrix, and solve for the unknowns:
        aa = zeros([nvv,nuk])                              # matrix
        for i in range(nvv):
            for j in range(nuk):
                unk = unks[j]
                aa[i,j] = coeff[unk][i]
        # bb = generalized_inverse(aa)
        # bb = solve_linear_equations(aa,vv)          # aa must be square
        bb = linear_least_squares(aa,vv)
        if trace: print bb
        sol = bb[0]                                   # solution vector
        ## sol = bb[3]                                   # solution vector..?
        # Replace the default values of the Expression parameters:
        self._reset()
        for j in range(nuk):
            rr = self.__parm[unks[j]]
            rr['nominal'] = sol[j]
            rr['default'] = sol[j]
            rr['testval'] = sol[j]                    # for plotting
            rr['stddev'] = 0.0
        if trace:
            self.display('fit')
            cc = plot(CCC['t'],vv,'o')
            self.plot(t=CCC['t'])
            
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

    def varange (self, rr, key=None, trace=False):
        """Helper function to translate rr into a vector of variable values,
        for evaluation and/or plotting"""
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
            self.expand()
            vv = self.varange(self.__xvar[key]['plotrange'])
        else:                                       # error message?
            vv = array(range(10))                   # some safe default
        if trace: print '\n** .varange(',rr,key,')\n   ->',vv,'\n'
        return vv

    #-----------------------------------------------------------------------

    def plot (self, _plot='linear', **pp):
        """Plot the Expression for the specified parameter/variable value(s).
        See also self.eval()."""

        # Make sure that there is at least one variable vector:
        self.expand()
        xvkeys = self.__xvar.keys()
        if len(pp)==0:
            if 'l' in xvkeys:
                pp['l'] = self.varange(True, 'l')
            elif 'm' in xvkeys:
                pp['m'] = self.varange(True, 'm')
            elif 't' in xvkeys:
                pp['t'] = self.varange(True, 't')
            elif 'f' in xvkeys:
                pp['f'] = self.varange(True, 'f')

        # Evaluate the (expanded) expression (produces self.__plotrec):        
        self.eval(_test=True, **pp)

        # Use the plot-record generated by .eval() to make the plot:
        rr = self.plotrec (trace=trace)
        xlabel(rr['xlabel'])
        ylabel(rr['ylabel'])
        title(rr['title'])
        legend(rr['legend'])
        if True:
            # Display the expression, term for term:
            terms = find_terms(rr['expr'])
            y = 0.8
            figtext(0.14,y,'Expression, term by term:')
            for term in terms['pos']:
                y -= 0.04
                figtext(0.15,y,'+'+term, color='blue')
            for term in terms['neg']:
                y -= 0.04
                figtext(0.15,y,'-'+term, color='red')
        # Plot the data:
        for i in range(len(rr['yy'])):
            yy = rr['yy'][i]
            if _plot=='loglog':
                cc = loglog(rr['xx'], yy)         # log x, log y
                cc = loglog(rr['xx'], yy, 'o', color=cc[0].get_color()) 
            elif _plot=='semilogx':
                cc = semilogx(rr['xx'], yy)       # linear y, log x
                cc = semilogx(rr['xx'], yy, '+', color=cc[0].get_color()) 
            elif _plot=='semilogy':
                cc = semilogy(rr['xx'], yy)       # linear x, log y
                cc = semilogy(rr['xx'], yy, '+', color=cc[0].get_color()) 
            else:
                cc = plot(rr['xx'], yy)           # default: both linear
                cc = plot(rr['xx'], yy, '+', color=cc[0].get_color())     
            print '-',i,'cc=',cc
            # print dir(cc[0])
            if len(rr['annot'])>0:
                color = cc[0].get_color()
                text(rr['xannot'], yy[0], rr['annot'][i], color=color)

        # Optimise the plotting-range:
        dx = 0.05*abs(rr['xmax']-rr['xmin'])
        dy = 0.05*abs(rr['ymax']-rr['ymin'])

        if _plot=='loglog':
            axis([rr['xmin'], rr['xmax']+dx, rr['ymin'], rr['ymax']+dy])
        elif _plot=='semilogx':
            axis([rr['xmin'], rr['xmax']+dx, rr['ymin']-dy, rr['ymax']+dy])
        elif _plot=='semilogy':
            axis([rr['xmin']-dx, rr['xmax']+dx, rr['ymin'], rr['ymax']+dy])
        else:
            axis([rr['xmin']-dx, rr['xmax']+dx, rr['ymin']-dy, rr['ymax']+dy])

        # Finished: show the plot:
        show()
        return rr

    #============================================================================
    # Evaluating the (expanded) expression:
    #============================================================================

    def eval (self, _test=False, **pp):
        """Evaluate the (expanded) expression for the specified (pp) values of
        parameters {} and variables []. Use defaults if not specified.
        If _test==True, the parm/val testvals are used, otherwise their defaults.
        Two of the specified parameters/variables may be multiple (list,tuple,array).
        The longest multiple is the 'variable', and the result is in the form of
        array(s) of this length. The shortest multiple (if any) is the 'parameter',
        i.e. there will be as many result arrays as parameter values."""

        trace = True
        if trace: print '\n** eval(_test=',_test,'):',pp

        # Make sure that an expanded expression exists:
        self.expand()

        # Use the default values in self.__xparm and self.__xvar,
        # unless other values have been specified via **pp.
        rr = dict()
        field = 'default'                        # normal mode
        if _test: field = 'testval'               # .test() mode
        for key in self.__xparm.keys():
            value = self.__xparm[key][field]
            if pp.has_key(key): value = pp[key]
            rr['{'+key+'}'] = value
        for key in self.__xvar.keys():
            value = self.__xvar[key][field]
            if pp.has_key(key): value = self.varange(pp[key], key=key)
            rr['['+key+']'] = value

        # Parameters/variables may be multiple:
        nmax = 0
        variable = rr.keys()[0]                   # key of the variable multiple
        parameter = None                          # key of the parameter multiple
        for key in rr.keys():
            n = 1
            if isinstance(rr[key], (list,tuple)):
                rr[key] = array(rr[key])          # make array
            if isinstance(rr[key], (type(array(0)))):
                n = len(rr[key])
                if n>nmax:
                    if nmax>1: parameter = variable
                    variable = key
                    nmax = n
                elif n>1:
                    parameter = key
            if trace: print '-',key,n,nmax,parameter,variable
        if trace: print 'parameter=',parameter,' variable=',variable,'(',nmax,')'

        # The results are collected in a plot-record (plotrec):
        plotrec = dict(yy=[], xx=rr[variable], test=_test,
                       xmin=-10, xmax=10, ymin=1e20, ymax=-1e20,
                       expr=self.__expression,
                       annot=[], xannot=0.0,
                       xlabel=variable,
                       ylabel='value',
                       parameter=parameter, pp=None,
                       title=self.tlabel(), legend=[])
        vkey = deenclose(variable,'[]')
        if vkey in self.__xvar.keys():
            plotrec['xlabel'] += '   ('+str(self.__xvar[vkey]['unit'])+')'
        if isinstance(plotrec['xx'], type(array(0))):
            plotrec['xannot'] = plotrec['xx'][0]
            plotrec['xmin'] = min(plotrec['xx'])
            plotrec['xmax'] = max(plotrec['xx'])
        # if trace: print 'plotrec =',plotrec

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
                else:
                    qq[key] = rr[key]
                    if first and not key==variable:
                        plotrec['legend'].append(key+'='+str(rr[key]))
                if trace: print '  -- qq[',key,']:',type(qq[key]),'=',qq[key]
            if trace and parameter:
                print '-',i,'/',n,': qq[',parameter,']=',qq[parameter]
            r1 = self.evalone(qq, _test=_test, trace=trace)
            plotrec['yy'].append(r1)
            plotrec['ymin'] = min(plotrec['ymin'],min(r1))
            plotrec['ymax'] = max(plotrec['ymax'],max(r1))
            if parameter:
                plotrec['annot'].append(parameter+'='+str(qq[parameter]))
            first = False

        # The plot-record is stored internally (see self.plot())
        self.plotrec (new=plotrec, trace=trace)

        # The return value depends on the shape:
        if len(plotrec['yy'])==1:
            return plotrec['yy'][0]               # just an array
        return plotrec['yy']                      # a list of arrays

    #-----------------------------------------------------------------------

    def evalone (self, pp, _test=False, trace=False):
        """Helper function called by self.eval()"""

        seval = deepcopy(self.__xexpr)
        if trace:
            print '\n .... evalone():',seval
            print '     ',pp

        # Replace parameters and variables with parameter names CCC[i]:
        CCC = []
        keys = pp.keys()
        for i in range(len(keys)):
            key = keys[i]
            CCC.append(pp[key])
            seval = seval.replace(key, 'CCC['+str(i)+']')
            if trace:
                print '- substitute',key,'-> ',seval
        if trace:
            print '  -> seval =',seval
            print '  -> CCC =',CCC

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

        if len(self.__parmtype['MeqNode'])>0:
            print '\n** .Funklet(): Expression has node child(ren)!\n'
            return False
        
        if not self.__expanded or not self.__Funklet:
            nv = self.numeric_value(trace=True)     # decide on treatment...
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
                print 'F._type:',self.__Funklet._type
                print '\n'
        return self.__Funklet



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
            node = self._unique_node (ns, name, qual=None, trace=trace)
            funklet = None
            if key in self.__parmtype['Expression']:
                funklet = parm.Funklet()
            elif key in self.__parmtype['Funklet']:
                funklet = parm
            elif key in self.__parmtype['MeqNode']:
                pass                                    # already a node
            elif parm['constant']==True:
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
        e1 = Expression(substring, label)
        for key in e1.__parm.keys():
            e1.__parm[key] = self.__parm[key]
            if trace: print '- copy parm[',key,']:',e1.__parm[key]
        for key in e1.__var.keys():
            e1.__var[key] = self.__var[key]
            if trace: print '- copy var[',key,']:',e1.__var[key]
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
        """Make a MeqParm node,  with the expression Funklet as init_funklet."""
        if not self.__MeqParm: 
            funklet = self.Funklet()
            if not name: name = 'Expr_'+self.label()+'_MeqParm'
            self.__MeqParm = self._unique_node (ns, name, qual=qual, trace=trace)
            self.__MeqParm << Meq.Parm(init_funklet=funklet)
            # if trace: print dir(self.__MeqParm)
        return self.__MeqParm

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
        caxstring = ''
        for cax in common_axes:
            caxes.append(str(cax))
            caxstring += str(cax)
        # print 'caxes =',caxes
        for key in self.__var.keys():
            if not key in ['t','f']:
                if not key in caxes:
                    print '\n** .MeqCompouder(',name,qual,'): missing cax:',key,'\n'
                
        # NB: The specified qualifier (qual) is used for the MeqCompounder,
        # but NOT for the MeqParm. The reason is that the Compounder has more
        # qualifiers than the Parm. E.g. EJones_X is per station, but the
        # compounder and its children (l,m) are for a specific source (q=3c84)
        if not name:
            # name = 'Expr_'+self.label()+'_'+caxstring+'_MeqCompounder'
            name = 'Expr_'+self.label()+'_'+caxstring
        node = self._unique_node (ns, name, qual=qual, trace=trace)
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
        if not self.__Functional:
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
            self.__Functional = self._unique_node (ns, name, qual=qual, trace=trace)
            self.__Functional << Meq.Functional(children=children, child_map=child_map)
        return self.__Functional




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
        print '\n** Error: bracket imbalance, nest =',nest,'\n'
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
    e0 = Expression(expr, 'Funklet_'+label)

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
    result = Expression(func, label, **pp)
    # insert help..
    if trace:
        result.display()
    return result


 








#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: JEN_Expression.py:\n'
    from numarray import *
    # from numarray.linear_algebra import *
    # from pylab import *
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
        e0.varange(range(5), trace=True)
        e0.varange(dict(min=23,max=24,nr=12), trace=True)
        e0.varange(dict(min=23,max=24), trace=True)
        e0.varange(True, key='t', trace=True)

    #-------------------------------------------------------------------

    if 1:
        f0 = Funklet()
        f0.setCoeff([[1,0,4],[2,3,4]])       # [t]*[f]*[f] highest order
        # f0.setCoeff([[1,0],[2,3]]) 
        # f0.setCoeff([1,0,2,3])               # [t] only !!
        # f0.setCoeff([[1,0,2,3]])           # [f] only 
        # f0.setCoeff([[1],[0],[2],[3]])     # [t] only            
        # f0.setCoeff([[1,9],[0,9],[2,9],[3,8]])                
        f0.init_function()
        print dir(f0)
        print f0._function
        print f0._coeff
        print f0._type
        e0 = Funklet2Expression(f0, 'A', trace=True)
        e0.fit(vv=range(10), f=range(10), t=range(10))
 
    if 0:
        f0 = Funklet()
        f0.setCoeff([[1,0,2,3]])             # [f] only 
        # f0.setCoeff([1,0,2,3])               # [t] only !!
        f0.setCoeff([[1,0],[2,3]]) 
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
        e1 = Expression('{A}*cos({B}*[f])+{C}+({neq}+67)', label='e1')
        e1.parm('A', -5, constant=True, stddev=0.1)
        e1.parm('B', 10, testval=4, help='help for B')
        # e1.parm('C', f0, help='help for C')
        e1.quals(a=5,b=6)
        e1.display()

        if 0:
            e1.display(e1.quals(a=-1,b=17))
            e1.display(e1.quals(a=5,b=6))
            e1.display(e1.quals())

        if 0:
            ff = array(range(-10,15))/10.0
            # e1.eval(f=ff, A=range(2))
            # e1.plot(f=ff, A=range(4))
            e1.plot()

        if 0:
            e2 = e1.subExpression('cos({B}*[f])', trace=True)

        if 0:
            node = e1.subTree (ns, trace=True)
            TDL_display.subtree(node, 'subTree', full=True, recurse=10)
            
        if 0:
            f1 = e1.Funklet(trace=True)
            e1.display()
            # Funklet2Expression(f1, 'A', trace=True)

        if 0:
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
        e2 = Expression('{r}+{BA}*[t]+{A[1,2]}-{xxx}', label='e2')
        e2.parm ('BA', default=e1, help='help')
        e2.parm ('r', default=11, polc=[4,5], help='help')
        node = ns << 10
        # e2.parm ('A[1,2]', default=node, help='help')
        # e2.parm ('xxx', default=node, help='help')
        e2.display(full=True)
        # e2.expand()
        # e2.eval(f=range(5))
        # e2.parm2node(ns, trace=True)
        # e2.var2node(ns, trace=True)

        if 1:
            e2.plot()

        if 0:
            e2.Funklet(trace=True)
            e2.display(full=True)

        if 0:
            node = e2.MeqFunctional(ns, trace=True)
            TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)

        if 0:
            node = e2.MeqNode(ns, trace=True)
            TDL_display.subtree(node, 'MeqNode', full=True, recurse=5)

    #-----------------------------------------------------------------------------

    if 0:
        # Voltage beam (gaussian):
        gaussian = Expression('{peak}*exp(-{ldep}-{mdep})', label='gauss')
        gaussian.parm ('peak', default=1.0, polc=[2,1], help='peak voltage beam')
        lterm = Expression('(([l]-{l0})/{lwidth})**2', label='lterm')
        lterm.parm ('l0', default=0.0)
        lterm.parm ('lwidth', default=1.0, help='beam-width in l-direction')
        gaussian.parm ('ldep', default=lterm)
        mterm = Expression('(([m]-{m0})/{mwidth})**2', label='mterm')
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
# - Funklets cannot handle purely numeric expressions (e.g. '67')
#
# - Fitting
#
# - Plotting
#
# - Evaluation
#
# - subtrees



#============================================================================================

    
