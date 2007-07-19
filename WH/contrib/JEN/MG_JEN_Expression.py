# MG_JEN_Expression.py

# Short description:
#   Demo and helper functions TDL_Expressions

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 jun 2006: creation
# - 07 aug 2006: updated .subTree() comparison

# Copyright: The MeqTree Foundation 


#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

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

MG = record(script_name='MG_JEN_Expression.py', last_changed = 'h22jun2006')

from random import *
from math import *
from numarray import *
from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.MXM import TDL_Funklet

from Timba.Contrib.JEN.util import JEN_bookmarks
from Timba.Contrib.JEN.util import TDL_Expression
from Timba.Contrib.JEN.util import TDL_display


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG['script_name'])






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   if False:
      # Experiment: a*cos(t/T) used in M.E. parameter simulation:
      cosvar = costime (ampl=1.0, period=0.1, phase=0.1, plot=False, trace=False) 
      cc.append(cosvar.MeqNode(ns))

   if True:
      # Experiment: Compare Funklet and subTree versions:
      if True:
         # NB: Does not work, because contains operator '**'
         Q = WSRT_voltage_Xbeam_gaussian (ell=0.1)
      else:
         # expr = '12+{a}-{b}'
         # expr = '12+{a}*[f]-{b}*[t]'
         # expr = '12+{a}*[f]-{b}'
         # expr = '{a}*sin({b}+{c}*cos({d}*[t]))-[f]*[f]'
         # expr = 'pow({d},[t])'                 # NB: pow() is unkown in Python.... 
         # expr = 'log({a})'                     # NB: difference: 10/e
         expr = 'sqrt({a})'                      # OK
         expr = 'cos({a})'                       # OK ...? Why not tan()?
         expr = 'abs({c})'                       # OK
         expr = 'tan({a})'                     # NB: tan() is unkown in Python.... 
         expr = '{a}*sin({b}+{c}*cos({d}*[t]))/[f]'
         Q = TDL_Expression.Expression(expr, label='Q')   # create expression
         Q.parm('a',2)                         # modify the default value of parm {a}
         Q.parm('b',100)                       # modify the default value of parm {b}

      if False:
         node = Q.subTree(ns, diff=True) 
         cc.append(node)
         JEN_bookmarks.create(node, recurse=1, page=None)
      else:
         node = Q.subTree(ns, solve=True) 
         cc.append(node)
         JEN_bookmarks.create(node, recurse=2, page=None)

      if False:
         # Optional: Plot the Funklet derived from Expression Q: 
         # NB: This plots after tree generation, i.e. WITHOUT execution!
         funk = Q.Funklet()
         dom = meq.gen_domain(time=(0,1),freq=(1,100))
         cells = meq.gen_cells(domain=dom,num_time=10,num_freq=10)
         funk.plot(cells=cells)
      

   if False:
      # Experiment: WSRT gaussian voltage beam(s):

      # NB: The following plots WITHOUT execution!
      dom = meq.gen_domain(time=(0,1),freq=(100e6,110e6),l=(-0.1,0.1),m=(-0.1,0.1))
      cells = meq.gen_cells(domain=dom,num_time=1,num_freq=5, num_l=11, num_m=11)

      Xbeam = WSRT_voltage_Xbeam_gaussian (ell=0.1)
      # Xbeam.Funklet().plot(cells=cells)
      Xbeam.Funklet(plot=True, newpage=True)

      if True:
         Ybeam = WSRT_voltage_Ybeam_gaussian (ell=0.1)
         Ybeam.Funklet().plot(cells=cells)
         if True:
            Qbeam = TDL_Expression.Expression('{Xbeam}-{Ybeam}', label='Qbeam')
            Qbeam.parm('Xbeam', Xbeam)
            Qbeam.parm('Ybeam', Ybeam)
            Qbeam.expanded().display(full=True)
            Qbeam.Funklet().plot(cells=cells, newpage=True)

      for L in array(range(5))*0.04:
         cc.append(make_LMCompounder (ns, Xbeam, l=L, m=0, q='3c123'))
      cc.append(make_Functional (ns, Xbeam, q='3c123'))

   if False:
      # Experiment: Solve for Xbeam=Ybeam
      Xbeam = WSRT_voltage_Xbeam_gaussian (ell=0.1)
      Ybeam = WSRT_voltage_Ybeam_gaussian (ell=0.1)
      condeq = []
      ng2 = 1
      dgrid = 0.04
      for L in array(range(-ng2,ng2+1))*dgrid:
         for M in array(range(-ng2,ng2+1))*dgrid:
            cX = make_LMCompounder (ns, Xbeam, l=L, m=M, q='3c123')
            cY = make_LMCompounder (ns, Ybeam, l=L, m=M, q='3c123')
            condeq.append(ns.condeq(l=L,m=M) << Meq.Condeq(cX,cY))
      solvable = Xbeam.MeqParms(ns, trace=True)
      solver = ns.solver << Meq.Solver(children=condeq,
                                       num_iter=5,
                                       solvable=solvable)
      cc.append(solver)


   # Example
   ### cc.append(MG_JEN_exec.bundle(ns, bb, 'polclog_flux_3c286()'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


def costime (ampl=1.0, period=100, phase=0.1, plot=False, trace=True): 
   # Cosine time variation (multiplicative) of an M.E. parameter:
   cosvar = TDL_Expression.Expression('{ampl}*cos(2*pi*[t]/{T}+{phi})', label='cosvar',
                                      descr='cos(t) variation of an M.E. parameter')
   cosvar.parm('ampl', ampl, polc=[2,3], unit='unit', help='amplitude(f,t) of the variation') 
   cosvar.parm('T', period, unit='s', help='period (s) of the variation') 
   cosvar.parm('phi', phase, unit='rad', help='phase (f,t) of the cosine') 
   if trace: cosvar.expanded().display(full=True)
   if plot: cosvar.plot()
   return cosvar


#===========================================================================

def WSRT_voltage_Xbeam_gaussian (ell=0.1, plot=False, trace=False):
   """Xpol version of WSRT_voltage_beam_gaussian"""
   return WSRT_voltage_beam_gaussian (pol='X', ell=ell,
                                      plot=plot, trace=trace)

def WSRT_voltage_Ybeam_gaussian (ell=0.1, plot=False, trace=False):
   """Ypol version of WSRT_voltage_beam_gaussian"""
   return WSRT_voltage_beam_gaussian (pol='Y', ell=-ell,
                                      plot=plot, trace=trace)


def WSRT_voltage_beam_gaussian (pol='X', ell=0.1, plot=False, trace=False):
   """ Make an Expression object for a WSRT telescope voltage beam (gaussian)"""
   vbeam = TDL_Expression.Expression('{peak}*exp(-{Lterm}-{Mterm})', label='gauss'+pol+'beam',
                                     descr='WSRT '+pol+' voltage beam (gaussian)', unit=None)
   # vbeam.parm ('peak', default=[1.0,0.1], polc=[2,1], unit='Jy', help='peak voltage beam')
   vbeam.parm ('peak', default=2.1, polc=[3,1], unit='Jy', help='peak voltage beam')
   # vbeam.parm ('peak', default=[1.0,0.001], polc=[1,2], unit='Jy', help='peak voltage beam')
   # vbeam.parm ('peak', default=[[1.0,0.002,-0.003],[0.1,-0.2,0.3]], polc=[3,2], unit='Jy', help='peak voltage beam')
   # vbeam.parm ('peak', default=2.3, unit='Jy', help='peak voltage beam')
   Lterm = TDL_Expression.Expression('(([l]-{L0})*{_D}*(1+{_ell})/{lambda})**2', label='Lterm')
   Lterm.parm ('L0', default=0.0, unit='rad', help='pointing error in L-direction')
   vbeam.parm ('Lterm', default=Lterm)
   Mterm = TDL_Expression.Expression('(([m]-{M0})*{_D}*(1-{_ell})/{lambda})**2', label='Mterm')
   Mterm.parm ('M0', default=0.0, unit='rad', help='pointing error in M-direction')
   vbeam.parm ('Mterm', default=Mterm)
   vbeam.parm ('_D', default=25.0, unit='m', help='WSRT telescope diameter')
   vbeam.parm ('lambda', default=TDL_Expression.Expression('3e8/[f]', label='lambda',
                                                           descr='observing wavelength'), unit='m')
   vbeam.parm ('_ell', default=ell, help='Voltage beam elongation factor (1+ell)')

   # Finished:
   if trace: vbeam.expanded().display(full=True)
   if plot: vbeam.plot()
   return vbeam

#---------------------------------------------------------------------------------

def make_LMCompounder (ns, beam, l=0.1, m=0.05, q='3c123', trace=False):
   """Make a (l,m) MeqCompounder node of the given beam Expression""" 
   L = ns.L(l=l) << l
   M = ns.M(m=m) << m
   LM = ns.LM(l=l, m=m) << Meq.Composer(L,M)
   node = beam.MeqCompounder(ns, qual=dict(q=q, l=l, m=m),
                             extra_axes=LM,
                             common_axes=[hiid('l'),hiid('m')],
                             trace=True)
   if trace:
      TDL_display.subtree(node, 'MeqCompounder', full=True, recurse=5)
   return node

#---------------------------------------------------------------------------------

def make_Functional (ns, beam, q='3c123', trace=False):
   """Make a MeqFunctional node of the given beam Expression""" 
   node = beam.MeqFunctional(ns, qual=dict(q=q), trace=trace)
   if trace:
      TDL_display.subtree(node, 'MeqFunctional', full=True, recurse=5)
   return node




#********************************************************************************
# Testing routines
# NB: this section should always be at the end of the script
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

def _test_forest (mqs, parent):
  return MG_JEN_exec.meqforest (mqs, parent)
  # return MG_JEN_exec.meqforest (mqs, parent, ntime=1)
  # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=100e6, f2=150e6, t1=0, t2=1, trace=False)
  # return MG_JEN_exec.meqforest (mqs, parent, nfreq=200, f1=1e6, f2=2e8, t1=-10, t2=10) 
  # return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    print '\n**',MG['script_name'],':\n'

    if 0:
        MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest)

    ns = NodeScope()

    if 0:
       Xbeam = WSRT_voltage_Xbeam_gaussian (ell=0.1, plot=False, trace=True)

    if 1:
       cosvar = costime (ampl=1.0, period=100, phase=0.1, plot=True, trace=True)
       node = cosvar.MeqNode(ns)
       TDL_display.subtree(node, 'MeqNode', full=True, recurse=5)

    print '\n** end of',MG['script_name'],'\n'

#********************************************************************************
#********************************************************************************





