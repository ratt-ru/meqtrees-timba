"""
ParmClump.py: A Clump of MeqParms, e.g. Ggain:0...D
"""

# file: ../JEN/Clump/ParmClump.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 07 nov 2008: creation (from templateClump.py)
#   - 06 dec 2008: implemented class PFunctionalClump
#   - 06 dec 2008: implemented ParmClump simulation mode 
#
# Description:
#
# Remarks:
#
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

from Timba.TDL import *
from Timba.Meq import meq

from Timba.Contrib.JEN.Clump import Clump
from Timba.Contrib.JEN.Expression import Expression

import math                 # support math.cos() etc
# from math import *          # support cos() etc
# import numpy                # support numpy.cos() etc



#********************************************************************************
#********************************************************************************

class ParmClump(Clump.LeafClump):
   """
   Contains a group of (usually similar) MeqParm nodes.
   This class has a number of methods to facilitate the
   specification of how its MeqParms should be solved for.
   """

   def __init__(self, clump=None, default=0.0,
                constraint=None,
                nodelist=None,
                simulate=False,
                **kwargs):
      """
      Derived from class LeafClump. There are two modes:
      - If a nodelist is given, use those, assuming that they
      are MeqParms (..). See class PListClump below.
      - Else a clump should be given. A group of MeqParm nodes
      is generated for each of its tree qualifiers (treequals), 
      and with the specified (kwargs) MeqParm arguments.
      If simulate=True, use MeqFunctionals i.s.o. MeqParms
      """

      # The default value is used as default for the MeqParm, but also
      # to generate context-sensitive simulation expressions.
      self._default = default

      # If simulate=True, the ParmClump object is in simulation mode.
      # This has (fully transparent) repercussions throughout
      self._simulate = simulate
      if self._simulate:
         pass

      else:
         # The following are used in the Meq.Parm() constructor:
         # See .initexec() below
         mpp = dict()
         mpp['use_previous'] = kwargs.get('use_previous', True) 
         mpp['table_name'] = kwargs.get('table_name', None) 
         self._MeqParm_parms = mpp

         # Constraints may be specified. They are used to generate constraint
         # equations in the form of condeq nodes. See self.constrain()
         self._constraint = constraint

      Clump.LeafClump.__init__(self, clump=clump, nodelist=nodelist, **kwargs)
      return None


   #==========================================================================
   #==========================================================================

   def initexec (self, **kwargs):
      """Fill the ParmClump object with suitable MeqParm nodes.
      Re-implemented version of the function in the baseclass (LeafClump).
      """
      help = 'definition of a set of similar MeqParms: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)

      if self._simulate:
         self.add_option('simexpr', self.simexpr_choice(),
                         help='python string')

      # Execute always (always=True) , to ensure that the leaf Clump has nodes!
      if self.execute_body(always=True):           

         if self._simulate:                  # simulation mode (MeqFunctionals)
            # NB: simexpr is a python expression with [t] or [f] etc
            simexpr = self.getopt('simexpr')
            stub = self.unique_nodestub('simul')
            for i,qual in enumerate(self.nodequals()):
               # Generate a new Expression for each qual. They may be varied
               # by means of the inbuilt random generator, e.g. {2~0.1}
               Ename = self.name()+'_'+str(qual)
               E = Expression.Expression(self.ns(), Ename, simexpr)
               self[i] = E.MeqFunctional(qnode=stub(qual), show=False)

         else:                                # normal mode (MeqParms)
            mpp = self._MeqParm_parms
            default = self._default

            stub = self.unique_nodestub()
            for i,qual in enumerate(self.nodequals()):
               qd = 'dflt='+str(default)
               self[i] = stub(qual)(qd) << Meq.Parm(default, **mpp)

            # A ParmClump object is itself the only entry in its list of ParmClumps:
            self.ParmClumps(append=self)

         # Mandatory counterpart of self.execute_body()
         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl)


   #----------------------------------------------------------------------------

   def simexpr_choice (self):
      """Helper function to make a standard choice of simulation expressions,
      using self._default as a context-sensitive guide.
      """
      v = self._default                       # the MeqParm default value
      zero = (v==0)
      dv = float(v)/10.0                      # variation in value
      sv = str(v)+' + '
      if zero:
         dv = 0.1
         sv = ''
      sdv = str(dv)
      T = 100                                 # typical period (s)
      dT = float(T)/20.0                      # variation in period
      sTdT = '{'+str(T)+'~'+str(dT)+'}'

      cc = []
      cc.append('{'+str(v)+'~'+sdv+'}')
      cc.append(sv+sdv+'*cos([t]/'+sTdT+')')
      cc.append(sv+sdv+'*sin([t]/'+sTdT+')')
      cc.append(sv+'abs('+sdv+'*sin([t]/'+sTdT+'))')
      cc.append('[f]+[t]')
      return cc


   #============================================================================
   #============================================================================

   def solspec (self, **kwargs):
      """
      A menu for the specification of the solving parameters for its MeqParms.
      It returns a list of solvable parms, to be given to a MeqSolver.
      This routine called by the solver object(!), not the ParmClump constructor.
      This means that the menu-options are also settable in the solver!!
      If self._simulate (simulation mode), just return [].
      """
      solvable = []                               # return a list of solvable MeqParm names
      if self._simulate:                         # in simulation mode
         return solvable                          # do nothing
      
      help = 'specify solving parameters for the MeqParms of: '+self.oneliner()
      prompt = 'solve for: '+self.name()
      ctrl = self.on_entry(self.solspec, prompt=prompt, help=help, **kwargs)

      self.add_option('fdeg', range(6),
                      help='freq deg of polc')

      self.add_option('tdeg', range(6),
                      help='time deg of polc')

      self.add_option('nfreq_subtile', [None,1,2,3,4,5,10], more=int,
                      # hide=True,
                      help="size (freq-cells) of solving subtile")

      self.add_option('ntime_subtile', [None,1,2,3,4,5,10], more=int,
                      # hide=True,
                      help="size (time-cells) of solving subtile")

      always = kwargs.get('always',False)         # see e.g. SolverUnit.py
      if self.execute_body(always=always):           

         tdeg = self.getopt('tdeg')
         fdeg = self.getopt('fdeg')
         nt = self.getopt('ntime_subtile')
         nf = self.getopt('nfreq_subtile')
         tiling = record(freq=nf, time=nt)

         for i,qual in enumerate(self.nodequals()):
            rr = self[i].initrec()
            rr.shape = [tdeg+1,fdeg+1] 
            rr.tiling = tiling,
            solvable.append(self[i])

         self.end_of_body(ctrl)

      # Mandatory counterpart of self.on_entry()
      return self.on_exit(ctrl, result=solvable)


   #================================================================

   def constrain (self, condeqs=[], trace=False):
      """If any constraints have been specified, add the resulting
      MeqCondeq nodes to the given list (condeqs). Return the list.
      If self._simulate (simulation mode), just return the input condeqs.
      """

      if self._simulate:                   # in simulation mode
         return condeqs                     # do nothing

      cs = self._constraint                 # convenience
      if not isinstance(cs, dict):
         cs = dict()

      if not isinstance(condeqs,list):
         condeqs = []

      if cs.has_key('sum'):
         value = cs['sum']
         stub = self.unique_nodestub('constraint','sum')
         lhs = stub('lhs=sum') << Meq.Add(*self.get_nodelist())
         rhs = stub(rhs=value) << Meq.Constant(value)
         node = stub(value) << Meq.Condeq(lhs,rhs)
         condeqs.append(node)
         self.history('constraint: sum='+str(value)+' -> '+str(node))

      if cs.has_key('prod'):
         value = cs['prod']
         stub = self.unique_nodestub('constraint','prod')
         lhs = stub('lhs=prod') << Meq.Multiply(*self.get_nodelist())
         rhs = stub(rhs=value) << Meq.Constant(value)
         node = stub(value) << Meq.Condeq(lhs,rhs)
         condeqs.append(node)
         self.history('constraint: prod='+str(value)+' -> '+str(node))

      # Always return the (possibly updated) list of condeqs
      return condeqs
   




#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class PListClump:
#********************************************************************************

class PListClump(Clump.LeafClump):
   """
   This is a LeafClump that is created with a list of nodes (nodelist), which are
   serached for MeqParm nodes upstream. The latter are put into a ParmClump.
   """

   def __init__(self, nodelist=None, **kwargs):
      """
      NB: The kwargs are passed on to its ParmClump. They may include
      ParmClump specs like 'tdeg' and 'nfreq_subtile' etc.
      They may also contain things like ns and TCM.
      """
      
      Clump.LeafClump.__init__(self, nodelist=nodelist, **kwargs)

      # Search the nodes (subtrees) for MeqParms:
      parms = self.search_nodescope(class_name='MeqParm')
      if len(parms)==0:
         self.ERROR('no MeqParms found')
         
      # Make a new ParmClump with the MeqParms
      if kwargs.has_key('name'):
         kwargs['name'] = '{'+str(kwargs['name'])+'}'
      else:
         kwargs['name'] = '{upstream}'
      pc = ParmClump(nodelist=parms, **kwargs)
      self.ParmClumps(append=pc)

      return None



#********************************************************************************
#********************************************************************************
#********************************************************************************
# Derived class PFunctionalClump:
#********************************************************************************

class PFunctionalClump(Clump.LeafClump):
   """
   This is a LeafClump that is created with a python math expression which contains
   parameters {p..} and variables [..]. The parameters are put into a ParmClump.
   The expression is evaluated for all the treequals in the input clump, using
   variables that are supplied as named lists of values of the correct length
   via the dict varvals (e.g. varvals=dict(x=[144,288, ...]))
   The resulting MeqFunctional nodes are the nodes of this PFunctionalClump.
   """

   def __init__(self, expr=None, varvals=None, **kwargs):
      """
      """
      self._simulate = kwargs.get('simulate',False)        # If True, simulate the MeqParms
      self._expr = expr                                    # python math expression
      self._varvals = varvals                              # dict with list(s) of variable values
      if not isinstance(self._varvals,dict):
         self._varvals = dict()
      nv = self.check_varvals()
      kwargs['treequals'] = range(nv)                      # placeholder
      Clump.LeafClump.__init__(self, **kwargs)
      return None



   #-------------------------------------------------------------------------
   # Re-implementation of its initexec function (called from Clump.__init__())
   #-------------------------------------------------------------------------

   def initexec (self, **kwargs):
      """
      Evaluate the given expression for the given lists of variable values,
      and make MeqFunctional nodes for this Clump.
      The parameters in the expressions are put into a ParmClump.
      Called from .__init__()
      """

      kwargs['fixture'] = True              # this clump is always selected

      help = 'make ... nodes for: '+self.oneliner()
      ctrl = self.on_entry(self.initexec, help=help, **kwargs)

      # Execute always (always=True), to ensure that the LeafClump has nodes:
      if self.execute_body(always=True):

         pp = self.make_ParmClump(**kwargs)

         # Make clump nodes by evaluating the expression
         stub = self.unique_nodestub()
         vv = self._varvals                     # convenience
         for i,qual in enumerate(self.nodequals()):

            # Replace all variables [..] with values:
            expr = self._expr
            stub1 = stub                        # nodename contains varvals
            for vname in vv.keys():
               sval = str(vv[vname][i])
               svname = '['+vname+']'
               expr = expr.replace(svname, sval)
               stub1 = stub1(vname+'='+sval)    # varval is qualifier in nodename

            # Make the Expression, and replace parms {..} with MeqParm nodes:
            E = Expression.Expression(self.ns(), 'E'+str(qual), expr)
            for pname in pp.keys():
               E.modparm('{'+pname+'}',pp[pname])

            # Make the MeqFunctional node and put it in the Clump:
            self[i] = E.MeqFunctional(qnode=stub1, show=False)
         self.end_of_body(ctrl)
         
      return self.on_exit(ctrl)



   #---------------------------------------------------------------------------
   #---------------------------------------------------------------------------

   def make_ParmClump (self, **kwargs):
      """Helper function to make a ParmClump object with the parameters in self._expr.
      """
      trace = False
      # trace = True
      
      pnames = self.extract_bracketed (self._expr, bb='{}', enclose=False)
      if len(pnames)==0:
         self.ERROR('no parms {..} in expression')

      kwargs.setdefault('name','MeqFunctionalParms')
      kwargs['treequals'] = pnames
      pc = ParmClump(**kwargs)
      if not self._simulate:
         self.ParmClumps(append=pc)
      if trace:
         pc.show('make_ParmClump()')

      # Return the dict of 'MeqParm' nodes
      pp = dict()
      for i,pname in enumerate(pnames):
         pp[pname] = pc[i]
      return pp

   #---------------------------------------------------------------------------

   def check_varvals(self):
      """Helper function to make sure that self._varvals contains lists of values
      (of the same length) for each variable [..] in self._expr.
      Expand any scalars into lists of the correct length.
      Return the length (used in .__init__()) 
      """
      trace = False
      # trace = True
      vnames = self.extract_bracketed (self._expr, bb='[]', enclose=False)

      nv = None                                        # determined below                                       
      for vname in vnames:
         if not self._varvals.has_key(vname):
            self.ERROR('no values for variable: '+str(vname))
         vv = self._varvals[vname]
         if isinstance(vv, (int,float,complex)):
            pass                                       # scalar, expanded below
         elif nv==None:                                # length not yet determined
            nv = len(vv)                               # length of the value list(s)
         elif not len(vv)==nv:
            self.ERROR('length mismatch for variable: '+str(vname)+': '+str(len(vv))+'!='+str(nv))

      if nv==None:
         self.ERROR('at least one of the value lists should be a list')

      # Expand any numerical values into lists of length nv:
      # Do this AFTER the value of nv has been determined above.
      for vname in vnames:
         vv = self._varvals[vname]
         if isinstance(vv, (int,float,complex)):
            self._varvals[vname] = nv*[vv]
         if trace:
            print '--',vname,'=',self._varvals[vname]

      # Return the length of the value list(s):
      return nv






#********************************************************************************
#********************************************************************************
# Function called from _define_forest() in ClumpExec.py
#********************************************************************************
#********************************************************************************

def do_define_forest (ns, TCM):
   """
   Testing function for the class(es) in this module.
   It is called by ClumpExec.py
   """
   submenu = TCM.start_of_submenu(do_define_forest,
                                  prompt=__file__.split('/')[-1],
                                  help=__file__)
   TCM.add_option('test_class',['ParmClump',
                                'PListClump',
                                'PFunctionalClump'],
                                prompt='class to be tested:')

   TCM.add_option('simulate',False)

   clump = None
   if TCM.submenu_is_selected():
      test_class = TCM.getopt('test_class', submenu)
      simulate = TCM.getopt('simulate', submenu)

      if test_class=='PListClump':
         cc = []
         for i in range(4):
            node = ns.ddd(i) << Meq.Parm(i)
            cc.append(node)
         clump = PListClump(cc, name='polyparm',
                            ns=ns, TCM=TCM, trace=True)

      elif test_class=='PFunctionalClump':
         expr = '{p0}+{p1}'
         expr = '7+{p0}+{p1}-9'
         expr = '{p0}+{p1}*[x]+[y]'
         simexpr = '[t]*{1~0.1}+[f]*{2~0.1}'
         clump = PFunctionalClump(expr=expr,
                                  varvals=dict(x=range(5), y=range(5)),
                                  simulate=simulate,
                                  # simexpr=simexpr,                   # override default
                                  ns=ns, TCM=TCM, trace=True)

      else:
         simexpr = '[t]*{1~0.1}+[f]*{2~0.1}'
         clump = ParmClump(name='GgainY', default=2.3,
                           ns=ns, TCM=TCM,
                           treequals=range(10)+list('ABCD'),         # WSRT
                           tdeg=4, fdeg=[4,5],                       # override
                           simulate=simulate,
                           simexpr=simexpr,                          # override default
                           # simexpr=[simexpr],                        # replace all
                           select=True)

      solvable = clump.get_solvable(trace=True)
      clump.visualize()

   # The LAST statement:
   TCM.end_of_submenu()
   return clump






#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n****************************************************'
   print '** Start of standalone test of: ParmClump.py:'
   print '****************************************************\n' 

   ns = NodeScope()
   TCM = None
   if 0:
      TCM = Clump.TOM.TDLOptionManager()
      print TCM.oneliner()

   if 0:
      c1 = None
      if 1:
         c1 = Clump.LeafClump(treequals=range(5))
         c1.show('input clump (c1)')
      # clump = ParmClump(c1, trace=True)
      clump = ParmClump(c1,
                        tdeg=[2,3], nfreq_subtile=2,
                        constraint=dict(sum=-1, prod=3),
                        trace=True)

   if 1:
      # c1 = Clump.LeafClump(treequals=range(5))
      expr = '{p0}+{p1}'
      expr = '7+{p0}+{p1}-9'
      expr = '{p0}+{p1}*[x]+[y]'
      clump = PFunctionalClump(expr=expr,
                               varvals=dict(x=4, y=range(5)),
                               simulate=False,
                               trace=True)

   if 0:
      cc = []
      for i in range(4):
         node = ns.ddd(i) << Meq.Parm(i)
         cc.append(node)
      cc[1] = ns << Meq.Cos(cc[1])
      clump = PListClump(cc, ns=ns, name='polyparm',
                         tdeg=[6,7],
                         trace=True)
      clump.ParmClumps()[0].show()


   if 0:
      tqs = range(10) + list('ABCD')
      clump = ParmClump(treequals=tqs,
                        name='GgainX',
                        default=1.0,
                        simulate=True,
                        tdeg=4, fdeg=[4,5],                       # override
                        # ns=ns, TCM=TCM,
                        trace=True)

   #--------------------------------------------------------
   
   if 1:
      clump.show('creation', full=True)

   if 0:
      clump1 = ParmClump(clump, name='other')
      clump1.show('clump1')

   if 0:
      pc = clump.ParmClumps()[0]
      solvable = pc.solspec()
      print '-> solvable:'
      for i,node in enumerate(solvable):
         print '-',i,':',str(node),'\n    ',node.initrec()
      print
      clump.show('after solspec()')
      pc.show('after solspec()')

   if 0:
      pc = clump.ParmClumps()[0]
      pc.constrain()
      pc.show('after constrain()')

   if 0:
      clump.compose()

   if 0:
      clump.show('final', full=True)

   
      
   print '\n** End of standalone test of: ParmClump.py:\n' 

#=====================================================================================





