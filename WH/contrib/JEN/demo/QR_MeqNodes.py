"""
QuickRef module: QR_MeqNodes.py
Gives an overview over all available MeqNodes.
It may be called from the module QuickRef.py.
But it may also be used stand-alone.
-- Load the TDL script into the meqbrowser.
-- Using TDL Options, select categories to be included,
.    and customize parameters and input children.
-- Compile: The tree will appear in the left panel.
.    (NB: the state record of each node has a quickref_help field)
-- Use the bookmarks to select one or more views.
-- Use TDL Exec to execute the tree: The views will come alive.
-- Use TDL Exec to show or print or save the hierarchical help
.    for the selected categories.
"""

# file: ../JEN/demo/QR_MeqNodes.py:
#
# Author: J.E.Noordam
#
# Short description:
#   Functions that make subtrees that demonstrate MeqNodes
#   Called from QuickRef.py
#
# History:
#   - 25 may 2008: creation (from QuickRef.py)
#   - 30 may 2008: local testing tree/routine
#   - 06 jun 2008: selectable input twigs
#   - 07 jun 2008: added twig() etc
#   - 07 jun 2008: added 4D (L,M)
#   - 07 jun 2008: import EasyTwig as ET
#   - 09 jun 2008: implemented hhelp
#
# Description:
#
# Remarks:
#
# Problem nodes:
#
#   MeqNElements()           multiple children give error
#   (Axis reduction nodes do not work on multiple children...?)
#   MeqMod()                 crashes the browser/server
#   MeqRandomNoise()         crashes the browser/server
#
#   MeqPaster()              does not paste
#   MeqSelector()            index=[1,2] not supported          
#
# Workaround exists:
#
#   MeqMatrix22()            use of children=[...] gives error
#   MeqConjugateTranspose()  use of children=[...] gives error
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

import QuickRefUtil as QR
import EasyTwig as ET

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_MeqNodes categories:",
               # TDLOption_user_level,               # ... needs some thought ...
               TDLOption('opt_allcats',"all",True),
               TDLMenu("Unary nodes (one child)",
                       TDLOption('opt_unops_twig',"input twig (child node)",
                                 ET.twig_names(), more=str),
                       toggle='opt_unops'),
               TDLMenu("Binary math nodes (two children)",
                       TDLOption('opt_binops_math_lhs',"lhs twig (child node)",
                                 ET.twig_names(), more=str),
                       TDLOption('opt_binops_math_rhs',"rhs twig (child node)",
                                 ET.twig_names(), more=str),
                       toggle='opt_binops_math'),
               TDLMenu("Math on an arbitrary nr of children",
                       TDLOption('opt_multi_math_twig1',"1st twig (child node)",
                                 ET.twig_names(), more=str),
                       TDLOption('opt_multi_math_twig2',"2nd twig (child node)",
                                 ET.twig_names(include=[None]), more=str),
                       TDLOption('opt_multi_math_twig3',"3rd twig (child node)",
                                 ET.twig_names(include=[None]), more=str),
                       toggle='opt_multi_math'),
               TDLOption('opt_leaves',"Leaf nodes (no children)",False),
               TDLOption('opt_tensor',"Tensor nodes (multiple vellsets)",False),
               TDLOption('opt_axis_reduction',"axis_reduction",False),
               TDLMenu("resampling",
                       TDLOption('opt_resampling_MeqModRes_twig',
                                 "input twig (child node) of MeqModRes",
                                 ET.twig_names(), more=str),
                       TDLOption('opt_resampling_MeqModRes_num_freq',
                                 "nr of freq cells for MeqModRes num_cells [nt,nf]",
                                 [4,1,2,3,5,6,10,20,50], more=int),
                       TDLOption('opt_resampling_MeqModRes_num_time',
                                 "nr of time cells for MeqModRes num_cells [nt,nf]",
                                 [4,1,2,3,5,6,10,20,50], more=int),
                       TDLOption('opt_resampling_MeqResampler_mode',"mode for MeqResampler",
                                 [1,2]),
                       toggle='opt_resampling'),
               TDLOption('opt_compounder',"compounder",False),
               TDLMenu("flagging",
                       TDLOption('opt_flagging_twig',"input twig (child node)",
                                 ET.twig_names('noise', first='noise_3'), more=str),
                       TDLOption('opt_flagging_nsigma',"nsigma (times stddev)",
                                 [5.0,1.0,2.0,3.0,4.0,7.0,9.0], more=str),
                       toggle='opt_flagging'),
               TDLMenu("solving",
                       TDLOption('opt_solving_twig',"input twig (lhs of condeq)",
                                 ET.twig_names(['gaussian'],first='gaussian_ft'),
                                 more=str),
                       TDLOption('opt_solving_tiling_time',"size (time-cells) of solving subtile",
                                 [None,1,2,3,4,5,10], more=int),
                       TDLOption('opt_solving_tiling_freq',"size (freq-cells) of solving subtile",
                                 [None,1,2,3,4,5,10], more=int),
                       TDLOption('opt_solving_mepfile',"name of mep table file",
                                 [None,'QR_MeqNodes'], more=str),
                       TDLMenu("solving_polyparm",
                               TDLOption('opt_solving_polyparm_poly',"polynomial to be fitted (rhs)",
                                         ET.twig_names(['polyparm']), more=str),
                               toggle='opt_solving_polyparm'),
                       TDLMenu("solving_Expression",
                               TDLOption('opt_solving_Expression_expr',"Expression to be fitted (rhs)",
                                         ET.twig_names(['Expression']), more=str),
                               toggle='opt_solving_Expression'),
                       TDLMenu("solving_onepolc",
                               TDLOption('opt_solving_onepolc_tdeg',"time deg of MeqParm polc",
                                         range(6), more=int),
                               TDLOption('opt_solving_onepolc_fdeg',"freq deg of MeqParm polc",
                                         range(6), more=int),
                               toggle='opt_solving_onepolc'),
                       toggle='opt_solving'),
               TDLMenu("visualization",
                       TDLOption('opt_visualization_inspector_twig',"input twig (child node)",
                                 ET.twig_names(first='t'), more=str),
                       toggle='opt_visualization'),
               TDLOption('opt_transforms',"transforms",False),
               TDLOption('opt_flowcontrol',"flowcontrol",False),

               TDLMenu("help",
                       TDLOption('opt_hhelp_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_MeqNodes')



#********************************************************************************
# Top function, called from QuickRef.py:
#********************************************************************************


def MeqNodes (ns, path, rider=None):
   """
   Available standard nodes: ns[name] << Meq.XYZ(*children,**kwargs).
   """
   rr = QR.on_entry(MeqNodes, path, rider)
   cc = []
   if opt_allcats or opt_unops:
      cc.append(unops (ns, rr.path, rider))
   if opt_allcats or opt_binops_math:
      cc.append(binops_math (ns, rr.path, rider))
   if opt_allcats or opt_multi_math:
      cc.append(multi_math (ns, rr.path, rider))
   if opt_allcats or opt_leaves:
      cc.append(leaves (ns, rr.path, rider))
   if opt_allcats or opt_tensor:
      cc.append(tensor (ns, rr.path, rider))
   if opt_allcats or opt_axis_reduction:
      cc.append(axis_reduction (ns, rr.path, rider))
   if opt_allcats or opt_resampling:
      cc.append(resampling (ns, rr.path, rider))
   if opt_allcats or opt_compounder:
      cc.append(compounder (ns, rr.path, rider))
   if opt_allcats or opt_flagging:
      cc.append(flagging (ns, rr.path, rider))
   if opt_allcats or opt_solving:
      cc.append(solving (ns, rr.path, rider))
   if opt_allcats or opt_visualization:
      cc.append(visualization (ns, rr.path, rider))
   if opt_allcats or opt_flowcontrol:
      cc.append(flowcontrol (ns, rr.path, rider))
   if opt_allcats or opt_transforms:
      cc.append(transforms (ns, rr.path, rider))

   if opt_helpnodes:
      cc.append(helpnodes (ns, rr.path, rider))

   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def helpnodes (ns, path, rider=None):
   """
   helpnodes...
   """
   rr = QR.on_entry(helpnodes, path, rider)
   
   print '\n**',path,type(rider)
   cc = []
   if opt_hhelp_twig:
      cc.append(QR.helpnode (ns, rr.path,
                             # name='EasyTwig.twig(ns,name)',
                             name='EasyTwig_twig',
                             help=ET.twig.__doc__, rider=rider, trace=False))
      print '**',path,'cc[0]:',str(cc[0]),type(rider),'\n'

   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def unops (ns, path, rider=None):
   """
   Unary math operations on one child, which may be a "tensor node" (multiple
   vellsets in its Result). An illegal operation (e.g. sqrt(-1)) produces a NaN
   (Not A Number) for that cell, which is then carried all the way downstream
   (i.e. from child to parent, towards the root of the tree). It does NOT produce
   a FAIL. See also ....
   """
   rr = QR.on_entry(unops, path, rider)
   twig = ET.twig (ns, opt_unops_twig)
   cc = [] 
   cc.append(unops_elementary (ns, rr.path, rider, twig))
   cc.append(unops_goniometric (ns, rr.path, rider, twig))
   cc.append(unops_hyperbolic (ns, rr.path, rider, twig))
   cc.append(unops_power (ns, rr.path, rider, twig))
   cc.append(unops_misc (ns, rr.path, rider, twig))
   cc.append(unops_complex (ns, rr.path, rider, twig))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def leaves (ns, path, rider=None):
   """
   Leaf nodes have no children. They often (but not always) have access to
   some external source of information (like a file) to satisfy a request. 
   """
   rr = QR.on_entry(leaves, path, rider)
   cc = []
   cc.append(leaves_constant (ns, rr.path, rider=rider))
   cc.append(leaves_parm (ns, rr.path, rider=rider))
   cc.append(leaves_grids (ns, rr.path, rider=rider))
   cc.append(leaves_noise (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def tensor (ns, path, rider=None):
   """
   Many node classes can handle Results with multiple vellsets.
   They are somewhat clumsily (and wrongly) called 'tensor nodes'.
   The advantages of multiple vellsets are:
   - the trees are more compact, so easier to define and read
   - efficiency: execution can be optimized internally
   - they allow special nodes that do matrix/tensor operations
   - etc, etc
   """
   rr = QR.on_entry(tensor, path, rider)
   cc = []
   cc.append(tensor_manipulation (ns, rr.path, rider=rider))
   cc.append(tensor_matrix (ns, rr.path, rider=rider))
   cc.append(tensor_matrix22 (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def axis_reduction (ns, path, rider=None):
   """
   Axis_reduction nodes reduce the values of all domain cells to a smaller
   number of values (e.g. their mean). They operate on all the vellsets
   in the Result(s) of their child(ren?).
   NB: It is not clear (to me, in this stage) what happens if some cells
   are flagged....!?
   If one or more reduction_axes are specified, the reduction is only
   along the specified axes (e.g. reduction_axes=['time'] reduces only
   the time-axis to length 1. The default is all available axes, of course. 
   The Result of a reduction node will be expanded when needed to fit a
   domain of the original size, in which multiple cells have the same value.
   """
   rr = QR.on_entry(axis_reduction, path, rider)
   cc = []
   cc.append(axis_reduction_single (ns, rr.path, rider=rider))
   cc.append(axis_reduction_multiple (ns, rr.path, rider=rider))
   cc.append(axis_reduction_axes (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def resampling (ns, path, rider=None):
   """
   The number of cells in the domain may be changed locally:
   ...
   - The MeqModRes(child, num_cells=[2,3]) node changes the number
   of cells in the domain of the REQUEST that it issues to its child.
   Thus, the entire subtree below the child is evaluated with this
   resolution. 
   - The MeqResample(child, mode=1) resamples the domain of the Result
   it gets from its child, to match the resolution of the Request that
   it received itself. (So it does nothing if the domains already match,
   i.e. if there is no MeqModRes upstream).
   - The MeqResample(child, mode=2) resamples in a different way...
   .....
   This feature has been developed (by Sarod) for 'peeling': If the
   phase-centre is shifted to the position of the peeling source, its
   visibility function will be smooth over the domain, so it is not
   necessary to predict it at the full time/freq resolution of the data.
   Since the number of cells may be 100 less, this can save a lot of
   processing.
   There may also be other applications of these nodes....
   """
   rr = QR.on_entry(resampling, path, rider)
   twig = ET.twig (ns, opt_resampling_MeqModRes_twig)
   num_cells = [opt_resampling_MeqModRes_num_time,
                opt_resampling_MeqModRes_num_freq]
   mode = opt_resampling_MeqResampler_mode
   cc = []
   cc.append(resampling_experiment (ns, rr.path, rider, twig, num_cells, mode))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def compounder (ns, path, rider=None):
   """
   The MeqCompounder node interpolates ....
   The extra_axes argument
   should be a MeqComposer that bundles the extra (coordinate) children,
   described by the common_axes argument (e.g. [hiid('L'),hiid('M')].                  
   """
   rr = QR.on_entry(compounder, path, rider)
   cc = []
   cc.append(compounder_simple (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def flowcontrol (ns, path, rider=None):
   """
   MeqReqSeq
   MeqReqMux
   MeqSink
   MeqVisDataMux
   """
   rr = QR.on_entry(flowcontrol, path, rider)
   cc = []
   cc.append(flowcontrol_reqseq (ns, rr.path, rider=rider))
   # cc.append(flowcontrol_reqmux (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def flagging (ns, path, rider=None):
   """
   MeqZeroFlagger
   MeqMergeFlags
   """
   rr = QR.on_entry(flagging, path, rider)
   cc = []
   cc.append(flagging_simple (ns, rr.path, rider=rider))
   # cc.append(flagging_merge (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def solving (ns, path, rider=None):
   """
   MeqSolver
   MeqCondeq
   MeqStripper (?)
   """
   rr = QR.on_entry(solving, path, rider)
   cc = []
   cc.append(solving_ab (ns, rr.path, rider=rider))           # simplest, do always
   if opt_solving_polyparm:
      cc.append(solving_polyparm (ns, rr.path, rider=rider))
   if opt_solving_Expression:
      cc.append(solving_Expression (ns, rr.path, rider=rider))
   if opt_solving_onepolc:
      cc.append(solving_onepolc (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def visualization (ns, path, rider=None):
   """
   MeqComposer (inpector)
   MeqParmFiddler
   MeqDataCollect (?)
   MeqDataConcat (?)
   MeqHistoryCollect (?)
   point to pyNodes...
   """
   rr = QR.on_entry(visualization, path, rider)
   cc = []
   cc.append(visualization_inspector(ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def transforms (ns, path, rider=None):
   """
   MeqUVBrick
   MeqUVInterpol
   MeqVisPhaseShift
   MeqCoordTransform
   MeqAzEl
   MeqLST
   MeqLMN
   MeqLMRaDec
   MeqObjectRADec (A?)
   MeqParAngle
   MeqRaDec
   MeqUVW
   
   """
   rr = QR.on_entry(transforms, path, rider)
   cc = []
   # cc.append(transforms_coord (ns, rr.path, rider=rider))
   # cc.append(transforms_FFT (ns, rr.path, rider=rider))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)





#********************************************************************************
#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************

#================================================================================
# transforms_... 
#================================================================================

def transforms_astro (ns, path, rider=None):
   """
   Astronomical coordinate transform nodes...
   """
   rr = QR.on_entry(transforms_astro, path, rider)
   cc = []
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

#================================================================================
# flowcontrol_... 
#================================================================================

def flowcontrol_reqseq (ns, path, rider=None):
   """
   The MeqReqSeq (Request Sequencer) node issues its request to its children one
   by one (rather than simultaneously, as other nodes do), in order of the child list.
   When finished, it passes on the result of only one of the children, which may be
   specified by means of the keyword 'result_index' (default=0, i.e. the first child).
   """
   rr = QR.on_entry(flowcontrol_reqseq, path, rider)
   rindex = 1
   cc = []
   for i in range(5):
      cc.append(ns << (-5*i))
   node = QR.MeqNode(ns, rr.path, meqclass='ReqSeq',
                     name='ReqSeq(*cc, result_index='+str(rindex)+')',
                     children=cc, help=help, result_index=rindex)
   CC = ET.unique_stub(ns,'cc') << Meq.Composer(*cc)
   return QR.bundle (ns, rr.path, nodes=[node,CC], help=rr.help, rider=rider)


#--------------------------------------------------------------------------------


#================================================================================
# visualization_... 
#================================================================================

def visualization_inspector (ns, path, rider=None):
   """
   An 'inspector' is a MeqComposer node. Its default viewer (invoked when
   clicking on it in the browser tree) is the Collections Plotter, which
   plots time-tracks of its children in a single plot. If the keyword
   argument 'plot_label' is given a list of strings, these are used as
   labels in the plot.
   - The plotter takes the average over all the non-time axes over the domain.
   .   (this is equivalent to axis_reduction with reduction_axis=all-except-time)
   .   Exercise: Play with different input twigs, and different domain axes.
   - When the result is complex, one may toggle betweem ampl,phase,real,imag. 
   - When a sequence is executed, the tim-slots are plotted sequentially.
   .   NB: this can be confusing, since the time-axis is really a sequence-axis...
   .   Exercise: Execute a sequence with different fractional time-steps.
   .   (a time-step of 1.0 steps by the domain size, so the time is continuous)
   - When the tree is excuted again, the new result is plotted after what is there
   .   already. The plot can be cleared via its right-clicking menu.
   On the whole, the Inspector is very useful, but it has its limitation.
   For more control, check out the PyNodePlots.
   """
   rr = QR.on_entry(visualization_inspector, path, rider)
   
   tname = opt_visualization_inspector_twig
   twig = ET.twig(ns, tname)
   cc = []
   plot_label = []
   for i in range(10):
      label = 'sin('+str(i)+'*'+tname+')'
      plot_label.append(label)
      cc.append(ns[label] << Meq.Sin(Meq.Multiply(i,twig)))
   node = QR.MeqNode(ns, rr.path, meqclass='Composer', name='inspector',
                     children=cc, help=help, plot_label=plot_label)
   return QR.bundle (ns, rr.path, nodes=[node], help=rr.help, rider=rider,
                     viewer='Collections Plotter')


#================================================================================
# solving_... 
#================================================================================

def solving_ab (ns, path, rider=None):
   """
   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (one condeq child each):
   - condeq 0:  a + b = p (=10)
   - condeq 1:  a - b = q (=2)
   The result should be: a = (p+q)/2 (=6), and b = (p-q)/2 (=4)
   Condeq Results are the solution residuals, which should be small.
   """
   rr = QR.on_entry(solving_ab, path, rider)
   a = ET.unique_stub(ns, 'a') << Meq.Parm(0)
   b = ET.unique_stub(ns, 'b') << Meq.Parm(0)
   p = ET.unique_stub(ns, 'p') << Meq.Constant(10)
   q = ET.unique_stub(ns, 'q') << Meq.Constant(2)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   drivers = ET.unique_stub(ns, 'driving_values_p_q') << Meq.Composer(p,q)
   parmset = ET.unique_stub(ns, 'solved_parameters_a_b') << Meq.Composer(a,b)

   condeqs = []
   condeqs.append(QR.MeqNode (ns, rr.path, meqclass='Condeq',name='Condeq(a+b,p)',
                              help='Represents equation: a + b = p (=10)',
                              rider=rider, children=[sum_ab, p]))
   condeqs.append(QR.MeqNode (ns, rr.path, meqclass='Condeq',name='Condeq(a-b,q)',
                              help='Represents equation: a - b = q (=2)',
                              rider=rider, children=[diff_ab, q]))

   solver = QR.MeqNode (ns, rr.path, meqclass='Solver',
                        name='Solver(*condeqs, solvable=[a,b])',
                        help='Solver', rider=rider, children=condeqs,
                        solvable=[a,b])  
   residuals = QR.MeqNode (ns, rr.path, meqclass='Add', name='residuals',
                           help='The sum of the (abs) condeq residuals',
                           rider=rider, children=condeqs, unop='Abs')
   cc = [solver,residuals,drivers,parmset]
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def solving_polyparm (ns, path, rider=None):
   """
   Demonstration of solving for the coefficients of a freq-time polynomial.
   It is fitted to the specified twig (e.g. a 2D gaussian).
   A separate equation is generated for each cell of the Request domain.

   The number of cells should be greater than the number of unknowns.
   In this case, this is the number of MeqParms, which have polcs with only
   a single coefficient (c00). NB: Try solving for freq-time polcs....)

   If the input (twig) function does not vary much over the domain, there
   is not enough information to solve for higher-order polynomial coeff.
   In this case, the solution will 'lose rank', which is indicated in the
   solver plot: the black line on the right leaves the right edge. 
   """
   rr = QR.on_entry(solving_polyparm, path, rider)
   twig = ET.twig(ns, opt_solving_twig)                       # move to solving()?
   poly = ET.twig(ns, opt_solving_polyparm_poly)
   parms = ET.find_parms(poly, trace=False)
   parmset = ET.unique_stub(ns,'solved_parms') << Meq.Composer(*parms)
   condeq = ns << Meq.Condeq(poly, twig)
   solver = QR.MeqNode (ns, rr.path, meqclass='Solver',
                        name='Solver(condeq, solvable=parms)',
                        help='Solver', rider=rider,
                        children=[condeq], solvable=parms)  
   cc = [solver,condeq,poly,twig,parmset]
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def solving_Expression (ns, path, rider=None):
   """
   """
   rr = QR.on_entry(solving_Expression, path, rider)
   lhs = ET.twig(ns, opt_solving_twig)              
   print '** expr =',opt_solving_Expression_expr
   rhs = ET.twig(ns, opt_solving_Expression_expr)
   print '** rhs =',str(rhs)
   parms = ET.find_parms(rhs, trace=True)
   if len(parms)==0:
      s = '** the Expression: '+opt_solving_Expression_expr
      s += '\n  should have at least one {parm}...'
      raise ValueError,s
   elif len(parms)==1:
      parmset = parms[0]
   else:
      parmset = ET.unique_stub(ns,'solved_parms') << Meq.Composer(*parms)
   condeq = ns << Meq.Condeq(lhs,rhs)
   solver = QR.MeqNode (ns, rr.path, meqclass='Solver',
                        name='Solver(condeq, solvable=parms)',
                        help='Solver', rider=rider,
                        children=[condeq], solvable=parms)  
   cc = [solver,condeq,lhs,rhs,parmset]
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider,
                     parentclass='ReqSeq', result_index=0)

#--------------------------------------------------------------------------------

def solving_onepolc (ns, path, rider=None):
   """
   Solving for the coeff of the polc of a single MeqParm.
   The single MeqCondeq child of the MeqSolver has two children:
   - The left-hand side (lhs) is the input twig node (e.g. a gaussian_ft)
   - The right-hand side (rhs) is a MeqParm:
   .      rhs = ns['MeqParm'] << Meq.Parm(meq.polc(coeff=numpy.zeros([tdeg+1,fdeg+1])))
   """
   rr = QR.on_entry(solving_onepolc, path, rider)
   lhs = ET.twig(ns, opt_solving_twig)
   tiling = record(freq=opt_solving_tiling_freq,
                   time=opt_solving_tiling_time)
   fdeg = opt_solving_onepolc_fdeg
   tdeg = opt_solving_onepolc_tdeg
   mepfile = opt_solving_mepfile
   pname = 'MeqParm(shape=[1+'+str(tdeg)+',1+'+str(fdeg)+'])'
   help = 'help'
   rhs = ET.unique_stub(ns,pname) << Meq.Parm(0.0,
                                              tags=['tag1','tag2'],
                                              shape=[tdeg+1,fdeg+1],
                                              tiling=tiling,
                                              table_name=mepfile,
                                              use_previous=True,
                                              quickref_help='...help...',
                                              node_groups='Parm')
   condeq = ns << Meq.Condeq(lhs,rhs)
   solver = QR.MeqNode (ns, rr.path, meqclass='Solver',
                        name='Solver(condeq, solvable=MeqParm)',
                        help='Solver', rider=rider,
                        children=[condeq],
                        niter=10,
                        solvable=rhs)  
   cc = [solver,condeq,lhs,rhs]
   QR.helpnode(ns, path, rider=rider, node=rhs)
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider,
                     parentclass='ReqSeq', result_index=0)


#--------------------------------------------------------------------------------


#================================================================================
# flagging_... 
#================================================================================

  
def flagging_simple (ns, path, rider=None):
   """
   Demonstration of simple flagging. A zero-criterion (zcrit) is calculated
   by a little subtree. This calculates the abs(diff) from the mean of the
   input, and then subtracts 'nsigma' times its stddev.
   The ZeroFlagger(oper=GE) flags all domain cells whose zcrit value is >= 0.
   Other behaviour can be specified with oper=LE or GT or LT.
   The MergeFlags node merges the new flags with the original flags of the input.
   """
   rr = QR.on_entry(flagging_simple, path, rider)

   twig = ET.unique_stub(ns,'twig') << Meq.Exp(ET.twig(ns, opt_flagging_twig))
   mean =  ns << Meq.Mean(twig)
   stddev =  ns << Meq.Stddev(twig)
   diff = ns << Meq.Subtract(twig,mean)
   absdiff = ns << Meq.Abs(diff)
   nsigma = opt_flagging_nsigma
   zcritname = 'zcrit(nsigma='+str(nsigma)+')'
   zcrit = ET.unique_stub(ns, zcritname) << Meq.Subtract(absdiff,nsigma*stddev)
   zflag = QR.MeqNode (ns, rr.path, meqclass='ZeroFlagger',
                       name='ZeroFlagger(zcrit, oper=GE)',
                       help='oper=GE: Flag all cells for which zcrit>=0.0.',
                       rider=rider, children=[zcrit], oper='GE')
   mflag = QR.MeqNode (ns, rr.path, meqclass='MergeFlags',
                       name='MergeFlags(twig,zflag)',
                       help='Merge new flags with existing flags',
                       rider=rider, children=[twig, zflag])
   cc = [twig, mean, stddev, zcrit, zflag, mflag]
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

#================================================================================
# compounder_... 
#================================================================================

  
def compounder_simple (ns, path, rider=None):
   """
   Demonstration of a 'grid' of compounders, which sample a grid of points (L,M)
   of a 2D gaussian input twig (subtree): 'gaussian_LM' -> exp(-(L**2+M**2)).
   Execute with a 2D (f,t) domain.
   The result of each compounder is a constant, with values that decrease with
   the distance to the origin. Expected values are:
   v(0,0) = 1.00000
   v(1,1) = 0.13533
   v(2,2) = 0.00335
   v(0,1) = v(1,0) = 0.36788
   v(0,2) = v(2,0) = 0.01831
   v(2,1) = v(1,2) = 0.00673
   A similar 2D gaussian (in f,t) is shown for comparison.
   NB: Try executing with a 4D domain....
   """
   rr = QR.on_entry(compounder_simple, path, rider)

   twig_LM = ET.twig(ns,'gaussian_LM')
   twig_ft = ET.twig(ns,'gaussian_ft')
   common_axes = [hiid('L'),hiid('M')]
   help = 'Compounder(LM,twigLM,common_axes='+str(common_axes)+')'
   cc = []
   for L in [0,1,2]:
      for M in [0,1,2]:
         LM = [(ns << L), (ns << M)]
         extra_axes = ns['extra_axes'](L=L)(M=M) << Meq.Composer(*LM)
         c = ns.Compounder(L=L)(M=M) << Meq.Compounder(extra_axes, twig_LM,
                                                       help=help,
                                                       common_axes=common_axes)
         cc.append(c)
   cs = ET.unique_stub(ns,'Compounders') << Meq.Composer(*cc)
   return QR.bundle (ns, rr.path, nodes=[cs,cc[1],twig_LM,twig_ft],
                     make_helpnode=True,
                     help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

#================================================================================
# resampling_... 
#================================================================================


def resampling_experiment (ns, path, rider,
                           twig=None, num_cells=[2,3], mode=1):
   """
   The experiment shows the difference between the twig, and after
   a sequence of ModRes and Resample. Obviously, the differences are
   smaller when the twig is smoother and/or when num_cells is larger.
   You may experiment with different twigs, MeqModRes num_cells or
   MeqResampler mode, by modifying the TDLOptions and recompiling and
   re-executing.
   """
   rr = QR.on_entry(resampling_experiment, path, rider)

   original = ET.unique_stub(ns, 'original') << Meq.Identity(twig)
   modres = QR.MeqNode (ns, rr.path, meqclass='ModRes',
                        name='ModRes(original, num_cells=[nt,nf])',
                        help='changes the resolution of the REQUEST',
                        rider=rider, children=[twig], num_cells=num_cells)
   resampled = QR.MeqNode (ns, rr.path, meqclass='Resampler',
                           name='Resampler(modres, mode='+str(mode)+')',
                           help='resamples the domain according to the twig request',
                           rider=rider, children=[modres], mode=mode)
   diff = ET.unique_stub(ns, 'diff(resampled,original)') << Meq.Subtract(resampled,original)
   return QR.bundle (ns, rr.path, nodes=[diff], help=rr.help, rider=rider,
                     bookmark=[original, modres, resampled, diff])




#================================================================================
# axis_reduction_... 
#================================================================================

def axis_reduction_single (ns, path, rider=None):
   """
   Demonstration of basic axis_reduction, on one child, with a single vellset.
   The reduction is done along all available axes (the default), producing a
   single-number Result.
   """
   rr = QR.on_entry(axis_reduction_single, path, rider)

   twig_name = 'f'
   twig = ET.twig(ns, twig_name)
   cc = [twig]
   help = record(NElements='nr of cells',
                 Sum='sum of cell values', Mean='mean of cell values',
                 Product='product of cell values',
                 Min='min cell value', Max='max  cell value',
                 StdDev='stddev of cell values',
                 Rms='same as StdDev (obsolete?)')
   for q in ['Nelements','Sum','Mean','Product','StdDev','Rms', 'Min','Max']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=help[q], rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def axis_reduction_multiple (ns, path, rider=None):
   """
   Demonstration of more advanced axis reduction, with Results that may contain
   multiple vellsets.
   NB: Axis_reduction nodes ONLY work with a single child.
   The reduction is done along all available axes (the default), producing a
   single-number Result.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   rr = QR.on_entry(axis_reduction_multiple, path, rider)

   democlass = 'Sum'
   help = record(f=democlass+' over the cells of a single vellset, of its single child',
                 range_5=democlass+' over the cells of multiple vellsets, from a tensor child')
   cc = []
   for twig_name in help.keys():
      twig = ET.twig(ns, twig_name)
      cc.append(twig)
      cc.append(QR.MeqNode (ns, rr.path, meqclass=democlass, name=democlass+'('+str(twig.name)+')',
                            help=help[twig_name], rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def axis_reduction_axes (ns, path, rider=None):
   """
   Demonstration of more advanced axis_reduction, along a subset of the available axes.
   If one or more reduction_axes are specified, the reduction is only
   along the specified axes (e.g. reduction_axes=['time'] reduces only
   the time-axis to length 1. The default is all available axes, of course. 
   The Result of a reduction node will be expanded when needed to fit a
   domain of the original size, in which multiple cells have the same value.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   rr = QR.on_entry(axis_reduction_axes, path, rider)

   democlass = 'Sum'
   help = democlass+' over the cells of '
   twig_name = 'ft'
   twig = ET.twig(ns, twig_name)
   ntwig = ns << Meq.NElements(twig)
   cc = [twig,ntwig]
   cc.append(QR.MeqNode (ns, rr.path, meqclass=democlass,
                         name=democlass+'('+str(twig.name)+')',
                         help=help+'no reduction_axes specified, assume all',
                         rider=rider, children=[twig]))
   cc.append(QR.MeqNode (ns, rr.path, meqclass=democlass,
                         name=democlass+'('+str(twig.name)+', reduction_axes=[time])',
                         help=help+'the time-axis is reduced to length 1.',
                         rider=rider, children=[twig], reduction_axes=['time']))
   cc.append(QR.MeqNode (ns, rr.path, meqclass=democlass,
                         name=democlass+'('+str(twig.name)+', reduction_axes=[freq])',
                         help=help+'the freq-axis is reduced to length 1.',
                         rider=rider, children=[twig], reduction_axes=['freq']))
   cc.append(QR.MeqNode (ns, rr.path, meqclass=democlass,
                         name=democlass+'('+str(twig.name)+', reduction_axes=[freq,time])',
                         help=help+'both the freq and time axes are reduced.',
                         rider=rider, children=[twig], reduction_axes=['freq','time']))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)




#================================================================================
# tensor_... 
#================================================================================


def tensor_manipulation (ns, path, rider=None):
   """
   Manipulation of 'tensor' nodes, i.e. nodes with multiple vellsets.
   """
   rr = QR.on_entry(tensor_manipulation, path, rider)
   cc = []
   children = [ET.twig(ns,'f'), ET.twig(ns,'t'), ET.twig(ns,'ft')]
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Composer', name='Composer(c0,c1,c2)',
                         help="""Combine the vellsets in the Results of its children
                         into a Result with multiple vellsets in the new node.""",
                         rider=rider, children=children))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Selector', name='Selector(child, index=1)',
                         help="""Select the specified (index) vellset in its child
                         for a new node with a single vellset in its Result""",
                         rider=rider, children=[cc[0]], index=1))
   if True:
      # Problem: Gives an error (list indix not supported?)
      cc.append(QR.MeqNode (ns, rr.path, meqclass='Selector', name='Selector(child, index=[0,2])',
                            help="""Select the specified (index) vellsets in its child
                            for a new node with this subset of vellsets in its Result""",
                            rider=rider, children=[cc[0]], index=[0,2]))
   if True:
      # Problem: Does not work... (nr of vells stays the same). But index is the correct keyword...
      c1 = ET.twig(ns,'prod_f2t2')
      cc.append(QR.MeqNode (ns, rr.path, meqclass='Paster', name='Paster(c0, c1, index=1)',
                            help="""Make a new node, in which the vellset from the
                            second child (c1) is pasted at the specified (index) position
                            among the vellsets of its first child (c0)""",
                            rider=rider, children=[cc[0],c1], index=1))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def tensor_matrix (ns, path, rider=None):
   """
   Nodes with multiple vellsets can be treated as matrices.
   There are some specialised nodes that do matrix operations.
   NB: For the moment, only 2x2 matrices can be inverted, since
   this was easiest to program by hand (see MatrixInvert22).
   A more general inversion node will be implemted later.
   """
   rr = QR.on_entry(tensor_matrix, path, rider)
   cc = []
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Composer',
                         name='Composer(1,2,3,4,5,6, dims=[2,3])',
                         help="""Make a tensor node with a 2x3 array of vellsets.
                         This can be treated as a 2x3 matrix. Note the use of
                         constants as children, for easier inspection and verification.""",
                         rider=rider, children=range(6),dims=[2,3]))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Transpose', name='Transpose(m0)',
                         help="""Make the 3x2 transpose of the given 2x3 matrix.""",
                         rider=rider, children=[cc[0]]))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='MatrixMultiply', name='MatrixMultiply(m0,m1)',
                         help="""Multply the original 2x3 matrix with its 3x2 transpose.
                         This produces a 2x2 matrix.""",
                         rider=rider, children=[cc[0],cc[1]]))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='MatrixMultiply', name='MatrixMultiply(m1,m0)',
                         help="""Multply the 3x2 transpose with the original 2x3 matrix.
                         This produces a 3x3 matrix.""",
                         rider=rider, children=[cc[1],cc[0]]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def tensor_matrix22 (ns, path, rider=None):
   """
   Because the 2x2 cohaerency matrix and the 2x2 Jones matrix play an important
   role in the radio-astronomical Measurement Equation (M.E.), there are a few
   specialized nodes that deal with 2x2 matrices.
   """
   rr = QR.on_entry(tensor_matrix22, path, rider)
   children = [ET.twig(ns,'cx_ft'),0,0,ET.twig(ns,'cx_tf')]
   cc = []
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Matrix22', name='Matrix22(cxft,0,0,cxtf)',
                         help="""Make a complex 2x2 diagonal matrix.""",
                         rider=rider, children=children))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='MatrixInvert22', name='MatrixInvert22(m0)',
                         help="""Invert the given 2x2 matrix (m0), cell-by-cell""",
                         rider=rider, children=[cc[0]]))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='MatrixMultiply', name='MatrixMultiply(m0,m0inv)',
                         help="""Multply the matrix (m0) with its inverse (m0inv).
                         The result should be a unit matrix (cell-by-cell).""",
                         rider=rider, children=[cc[0],cc[1]]))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='ConjTranspose', name='ConjTranspose(m0)',
                         help="""Conjugate Transpose the given matrix (m0)""",
                         rider=rider, children=[cc[0]]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)



#================================================================================
# leaves_...
#================================================================================

def leaves_constant (ns, path, rider=None):
   """
   A constant may be complex, or a tensor. There are various ways to define one.
   """
   rr = QR.on_entry(leaves_constant, path, rider)
   cc = []
   help = 'Constant node created with: '
   cc.append(QR.MeqNode (ns, rr.path, node=(ns << 2.5),
                         help=help+'ns << 2.5'))
   cc.append(QR.MeqNode (ns, rr.path, node=(ns.xxxx << 2.4),
                         help=help+'ns.xxxx << 2.4'))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Constant', name='Constant(real)',
                         help='', value=1.2))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Constant', name='Constant(complex)',
                         help='', value=complex(1,2)))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Constant', name='Constant(vector)',
                         help='produces a "tensor node"', value=range(4)))
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Constant', name='Constant(vector, shape=[2,2])',
                         help='produces a "tensor node"', value=range(4), shape=[2,2]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def leaves_parm (ns, path, rider=None):
   """
   MeqParm nodes represent M.E. parameters, which may be solved for.
   """
   rr = QR.on_entry(leaves_parm, path, rider)
   cc = []
   help = ''
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Parm',
                         help=help, default=2.5))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def leaves_noise (ns, path, rider=None):
   """
   Noise nodes generate noisy cell values. The arguments are passed as
   keyword arguments in the node constructor (or as children?)
   """
   rr = QR.on_entry(leaves_noise, path, rider)
   cc = []
   help = 'Gaussian noise with given stddev (and zero mean)'
   cc.append(QR.MeqNode (ns, rr.path, meqclass='GaussNoise',
                         name='GaussNoise(stddev=2)',
                         help=help, rider=rider,
                         stddev=2.0))
   help = 'Gaussian noise with given stddev and mean'
   # NB: mean does not work...
   cc.append(QR.MeqNode (ns, rr.path, meqclass='GaussNoise',
                         name='GaussNoise(stddev=2,mean=-10)',
                         help=help, rider=rider,
                         mean=-10.0, stddev=2.0))
   if False:
      # Problem: The server crashes on this one...!
      help = 'Random noise between lower and upper bounds'
      cc.append(QR.MeqNode (ns, rr.path, meqclass='RandomNoise',
                            name='RandomNoise(-2,4)',
                            help=help, rider=rider,
                            lower=-2.0, upper=4.0))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def leaves_grids (ns, path, rider=None):
   """
   Grid nodes fill in the cells of the requested domain with the
   values of the specified axis (time, freq, l, m, etc).
   See also the state forest....
   The two default axes (time and freq) have dedicated Grid nodes,
   called MeqTime and MeqFreq.
   """
   rr = QR.on_entry(leaves_grids, path, rider)
   cc = []
   help = ''
   for q in ['Freq','Time']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'()',
                            help=help, rider=rider)) 
   for q in ['freq','time','L','M']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass='Grid',name='Grid(axis='+q+')',
                            help=help, rider=rider, axis=q))
   cc.append(ns.ft << Meq.Add(cc[2],cc[3]))
   cc.append(ns.LM << Meq.Add(cc[4],cc[5]))
   cc.append(ns.ftLM << Meq.Add(cc[2],cc[3],cc[4],cc[5]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#--------------------------------------------------------------------------------

def leaves_spigot (ns, path, rider=None):
   """
   The MeqSpigot reads data from an AIPS++/Casa Measurement Set (uv-data).
   It is twinned with the MeqSink, which writes uv-data back into the MS,
   and generates a sequence of requests with suitable time-freq domains
   (snippets). See also....
   MeqVisDataMux:
   MeqFITSSpigot:
   """
   rr = QR.on_entry(leaves_spigot, path, rider)
   cc = []
   help = ''
   cc.append(QR.MeqNode (ns, rr.path, meqclass='Spigot', name='Spigot()',
                         help=help))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def leaves_FITS (ns, path, rider=None):
   """
   There are various nodes to read images from FITS files.
   MeqFITSReader:
   MeqFITSImage:
   MeqFITSSpigot:
   """
   rr = QR.on_entry(leaves_FITS, path, rider)
   cc = []
   help = ''
   cc.append(QR.MeqNode (ns, rr.path, meqclass='FITSReader',
                         help=help))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)




#================================================================================
# unops_... (Unary operations)
#================================================================================


def unops_elementary (ns, path, rider=None, twig=None):
   """
   Elementary unary math operations.
   """
   rr = QR.on_entry(unops_elementary, path, rider)
   cc = [twig]
   help = record(Negate='-c', Invert='1/c', Exp='exp(c)', Sqrt='square root',
                 Log='e-log (for 10-log, divide by Log(10))')
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      # NB: explain log...
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=help[q], rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def unops_goniometric (ns, path, rider=None, twig=None):
   """
   Goniometric functions turn an angle (rad) into a fraction.
   """
   rr = QR.on_entry(unops_goniometric, path, rider)
   cc = [twig]
   help = record(Sin='(rad)', Cos='(rad)', Tan='(rad)',
                 Asin='abs('+str(twig.name)+')<1', Acos='abs('+str(twig.name)+')<1', Atan='')
   for q in ['Sin','Cos','Tan','Asin','Acos','Atan']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=help[q], rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def unops_hyperbolic (ns, path, rider=None, twig=None):
   """
   Hyperbolic functions convert a fraction into an angle (rad).
   """
   rr = QR.on_entry(unops_hyperbolic, path, rider)
   cc = [twig]
   help = ''
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=help, rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def unops_complex (ns, path, rider=None, twig=None):
   """
   Complex unary math operations on a (usually) complex child.
   """
   rr = QR.on_entry(unops_complex, path, rider)
   twig = ET.twig(ns,'cx_ft')                # override input twig...
   cc = [twig]
   help = record(Abs='', Norm='like Abs', Arg='-> rad', Real='', Imag='',
                 Conj='complex conjugate: a+bj -> a-bj',
                 Exp='exp(a+bj) = exp(a)*exp(bj), i.e. cos with increasing ampl',
                 Log='e-log (ln)')
   for q in ['Abs','Norm','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=help[q], rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def unops_power (ns, path, rider=None, twig=None):
   """
   Nodes that take some power of its child.
   """
   rr = QR.on_entry(unops_power, path, rider)
   cc = [twig]
   help = ' of its single child'
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=q+help, rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)

#--------------------------------------------------------------------------------

def unops_misc (ns, path, rider=None, twig=None):
   """
   Miscellaneous unary math operations.
   """
   rr = QR.on_entry(unops_misc, path, rider)
   cc = [twig]
   help = record(Abs='Take the absolute value.',
                 Ceil='Round upwards to integers.',
                 Floor='Round downwards to integers.',
                 Stripper="""Remove all derivatives (if any) from the result.
                 This saves space and can be used to control solving.""",
                 Identity='Make a copy node with a different name.'
                 )
   for q in ['Abs','Ceil','Floor','Stripper','Identity']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+str(twig.name)+')',
                            help=help[q], rider=rider, children=[twig]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#================================================================================
# binops_math
#================================================================================

def binops_math (ns, path, rider=None):
   """
   Binary math operations (two children).
   The operation is performed cell-by-cell.
   The input children may be selected, for experimentation.
   - If the first child (left-hand-side, lhs) has a result with multiple vellsets
   .    ('tensor-node'), there are two possibilities: If the second child (rhs) is a
   .    'scalar node', its single vellset is applied to all the vellsets of lhs.
   - Otherwise, the Result of rhs must have the same number of vellsets as lhs,
   .    and the operation is performed between corresponding vellsets.
   The final Result always has the same shape (number of vellsets) as lhs.
   """
   rr = QR.on_entry(binops_math, path, rider)
   lhs = ET.twig(ns, opt_binops_math_lhs)         # left-hand side (child)
   rhs = ET.twig(ns, opt_binops_math_rhs)         # right-hand side (child)
   cc = []
   help = record(Subtract='lhs-rhs', Divide='lhs/rhs', Pow='lhs^rhs',
                 Mod='lhs%rhs',
                 ToComplex='(real, imag)', Polar='(amplitude, phase)')
   # Problem: MeqMod() crashes the meqserver.... Needs integer children??
   # for q in ['Subtract','Divide','Pow','ToComplex','Polar','Mod']:
   for q in ['Subtract','Divide','Pow','ToComplex','Polar']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q,
                            name=q+'('+str(lhs.name)+','+str(rhs.name)+')',
                            help=help[q], rider=rider, children=[lhs,rhs]))
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)


#================================================================================
# multi_math
#================================================================================

def multi_math (ns, path, rider=None):
   """
   Math operations on an arbitrary number (one or more) of children.
   The operation is performed cell-by-cell.
   The number and type of children may be selected, for experimentation.
   - If the number of children is two, the same rules apply as for binary
   .    operations (see binops_math).
   - If the number of children is greater than two, the Results of all children
   .    must have the same shape (i.e. the same number of vellsets in their Results).
   - If the number of of children is one, its Result is just passed on.
   """
   rr = QR.on_entry(multi_math, path, rider)

   # Make the child-related vectors (ignore the ones with opt=None):
   twigs = [ET.twig(ns,opt_multi_math_twig1)]
   sname = twigs[0].name
   weights = [1.0]
   if opt_multi_math_twig2:
      twigs.append(ET.twig(ns,opt_multi_math_twig2))
      sname += ','+twigs[len(twigs)-1].name
      weights.append(2.0)
   if opt_multi_math_twig3:
      twigs.append(ET.twig(ns,opt_multi_math_twig3))
      sname += ','+twigs[len(twigs)-1].name
      weights.append(3.0)
   cc = []

   # First the simple ones:
   help = record(Add='c0+c1+c2+...',
                 Multiply='c0*c1*c2*...')
   for q in ['Add','Multiply']:
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q, name=q+'('+sname+')',
                            help=help[q], rider=rider,
                            children=twigs))

   # Then the weighted ones:
   help = record(WSum="""Weighted sum: w[0]*c0 + w[1]*c1 + w[2]*c2 + ...
                 The weights vector (weights) is a vector of DOUBLES (!)""",
                 WMean="""Weighted mean, the same as WSum, but divides by
                 the sum of the weights (w[0]+w[1]+w[2]+....)""")
   sw = str(weights).replace('.0','').replace('.',',')
   for q in ['WSum','WMean']:
      # print '\n** ',q,': weigths =',weights,'\n'
      cc.append(QR.MeqNode (ns, rr.path, meqclass=q,
                            name=q+'('+sname+',weights='+sw+')',
                            help=help[q], rider=rider,
                            weights=weights, children=twigs))

   # Attach the input twigs to the bundle, for inspection.
   # NB: If attached at the start, WMean and WSum refuse to plot....?
   cc.extend(twigs)
   return QR.bundle (ns, rr.path, nodes=cc, help=rr.help, rider=rider)












#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Local testing forest:
#================================================================================

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QR)
TDLRuntimeMenu(":")

# For TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   global rider                                 # used in tdl_jobs
   rider = QR.create_rider()                    # CollatedHelpRecord object
   rootnodename = 'QR_MeqNodes'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QR.bundle (ns, path,
              nodes=[MeqNodes(ns, path, rider)],
              help=__doc__,
              rider=rider)

   # Finished:
   return True
   


#--------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent):
   return QR._tdl_job_execute_1D (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_execute_2D (mqs, parent):
   return QR._tdl_job_execute_2D (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_execute_3D (mqs, parent):
   return QR._tdl_job_execute_3D (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_execute_4D (mqs, parent):
   return QR._tdl_job_execute_4D (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_execute_sequence (mqs, parent):
   return QR._tdl_job_execute_sequence (mqs, parent, rootnode='QR_MeqNodes')

def _tdl_job_m (mqs, parent):
   return QR._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   return QR._tdl_job_print_doc (mqs, parent, rider, header='QR_MeqNodes')

def _tdl_job_print_hardcopy (mqs, parent):
   return QR._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_MeqNodes')

def _tdl_job_show_doc (mqs, parent):
   return QR._tdl_job_show_doc (mqs, parent, rider, header='QR_MeqNodes')

def _tdl_job_save_doc (mqs, parent):
   return QR._tdl_job_save_doc (mqs, parent, rider, filename='QR_MeqNodes')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_MeqNodes.py:\n' 

   ns = NodeScope()

   rider = QR.create_rider()             # CollatedHelpRecord object
   if 1:
      MeqNodes(ns, 'test', rider=rider)
      if 1:
         rider.show('testing')

   if 0:
      subject = 'unops'
      subject = 'binops'
      subject = 'leaves'
      subject = 'leaves.constant'
      # subject = 'axis_reduction'
      # subject = 'resampling'
      # subject = 'flagging'
      # subject = 'solving'
      # subject = 'visualization'
      # subject = 'transforms'
      # subject = 'flowcontrol'
      path = 'test.MeqNodes.'+subject
      rr = rider.subrec(path, trace=True)
      rider.show('subrec',rr, full=False)
            
   print '\n** End of standalone test of: QR_MeqNodes.py:\n' 

#=====================================================================================





