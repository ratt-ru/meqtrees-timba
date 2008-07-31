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
#   - 09 jun 2008: implemented make_helpnodes
#   - 30 jul 2008: removed QRU.MeqNode() etc
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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN


# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_MeqNodes topics:",
               # TDLOption_user_level,               # ... needs some thought ...
               # TDLOption('opt_allcats',"all",True),
               TDLOption('opt_alltopics',"override: include all topics",True),
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
               TDLOption('opt_axisreduction',"axisreduction",False),
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
               TDLOption('opt_solving',"solving",False),
               TDLMenu("visualization",
                       TDLOption('opt_visualization_inspector_twig',"input twig (child node)",
                                 ET.twig_names(first='t'), more=str),
                       toggle='opt_visualization'),
               TDLOption('opt_transforms',"transforms",False),
               TDLOption('opt_flowcontrol',"flowcontrol",False),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_MeqNodes')



#********************************************************************************
# Top function, called from QuickRef.py:
#********************************************************************************

header = 'QR_MeqNodes'

def QR_MeqNodes (ns, rider):
   """
   Available standard nodes: ns[name] << Meq.XYZ(*children,**kwargs).
   """
   stub = QRU.on_entry(ns, rider, QR_MeqNodes)
   cc = []
   override = opt_alltopics
   global header
   
   if override or opt_unops:
      cc.append(unops (ns, rider))
   if override or opt_binops_math:
      cc.append(binops_math (ns, rider))
   if override or opt_multi_math:
      cc.append(multi_math (ns, rider))
   if override or opt_leaves:             
      cc.append(leaves (ns, rider))
   if override or opt_tensor:
      cc.append(tensor (ns, rider))
   if override or opt_axisreduction:
      cc.append(axisreduction (ns, rider))
   if override or opt_resampling:
      cc.append(resampling (ns, rider))
   if override or opt_compounder:
      cc.append(compounder (ns, rider))
   if override or opt_flagging:
      cc.append(flagging (ns, rider))
   if override or opt_solving:
      cc.append(solving (ns, rider))
   if override or opt_visualization:
      cc.append(visualization (ns, rider))
   if override or opt_flowcontrol:
      cc.append(flowcontrol (ns, rider))
   if override or opt_transforms:
      cc.append(transforms (ns, rider))

   if override or opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, rider):
   """
   helpnodes...
   """
   stub = QRU.on_entry(ns, rider, make_helpnodes)
   
   cc = []
   if opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rider, func=ET.twig))

   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def unops (ns, rider):
   """
   Unary math operations on one child, which may be a 'tensor node' (i.e. multiple
   vellsets in its Result). An illegal operation (e.g. sqrt(-1)) produces a NaN
   (Not A Number) for that cell, which is then carried all the way downstream
   (i.e. from child to parent, towards the root of the tree). It does NOT produce
   a FAIL. See also ....

   The best way to visualize the operation of unary nodes is to use an MeqFreq (f)
   or MeqTime (t) as input twig (node), and to execute with a 1-dim domain. Since
   these variables increase linearly over the domain, this produces simple plots
   of the function value vs its argument. 
   """
   stub = QRU.on_entry(ns, rider, unops)
   twig = ET.twig (ns, opt_unops_twig)
   cc = [] 
   cc.append(unops_elementary (ns, rider, twig))
   cc.append(unops_goniometric (ns, rider, twig))
   cc.append(unops_hyperbolic (ns, rider, twig))
   cc.append(unops_power (ns, rider, twig))
   cc.append(unops_misc (ns, rider, twig))
   cc.append(unops_complex (ns, rider, twig))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def leaves (ns, rider):
   """
   Leaf nodes have no children. They often (but not always) have access to
   some external source of information (like a file) to satisfy a request. 
   """
   stub = QRU.on_entry(ns, rider, leaves)
   cc = []
   cc.append(leaves_constant (ns, rider))
   cc.append(leaves_parm (ns, rider))
   cc.append(leaves_grids (ns, rider))
   cc.append(leaves_noise (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def tensor (ns, rider):
   """
   Many node classes can handle Results with multiple vellsets.
   They are somewhat clumsily (and wrongly) called 'tensor nodes'.
   The advantages of multiple vellsets are:
   - the trees are more compact, so easier to define and read
   - efficiency: execution can be optimized internally
   - they allow special nodes that do matrix/tensor operations
   - etc, etc
   """
   stub = QRU.on_entry(ns, rider, tensor)
   cc = []
   cc.append(tensor_manipulation (ns, rider))
   cc.append(tensor_matrix (ns, rider))
   cc.append(tensor_matrix22 (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def axisreduction (ns, rider):
   """
   Axisreduction nodes reduce the values of all domain cells to a smaller
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
   stub = QRU.on_entry(ns, rider, axisreduction)
   cc = []
   cc.append(axisreduction_single (ns, rider))
   cc.append(axisreduction_multiple (ns, rider))
   cc.append(axisreduction_axes (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def resampling (ns, rider):
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
   stub = QRU.on_entry(ns, rider, resampling)
   twig = ET.twig (ns, opt_resampling_MeqModRes_twig)
   num_cells = [opt_resampling_MeqModRes_num_time,
                opt_resampling_MeqModRes_num_freq]
   mode = opt_resampling_MeqResampler_mode
   cc = []
   cc.append(resampling_experiment (ns, rider,
                                    twig, num_cells, mode))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def compounder (ns, rider):
   """
   The MeqCompounder node interpolates ....
   The extra_axes argument
   should be a MeqComposer that bundles the extra (coordinate) children,
   described by the common_axes argument (e.g. [hiid('L'),hiid('M')].                  
   """
   stub = QRU.on_entry(ns, rider, compounder)
   cc = []
   cc.append(compounder_simple (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def flowcontrol (ns, rider):
   """
   MeqReqSeq
   MeqReqMux
   MeqSink
   MeqVisDataMux
   """
   stub = QRU.on_entry(ns, rider, flowcontrol)
   cc = []
   cc.append(flowcontrol_reqseq (ns, rider))
   # cc.append(flowcontrol_reqmux (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def flagging (ns, rider):
   """
   MeqZeroFlagger
   MeqMergeFlags
   """
   stub = QRU.on_entry(ns, rider, flagging)
   cc = []
   cc.append(flagging_simple (ns, rider))
   # cc.append(flagging_merge (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def solving (ns, rider):
   """
   The purpose of MeqTrees is not only to allow the implementation of an arbitrary
   Measurement Equation, but also to solve for (arbitrary subsets of) its parameters.
   This is treated in detail in a separate module (QR_solving). For completeness,
   we show a single simple example here.
   """
   stub = QRU.on_entry(ns, rider, solving)
   cc = []
   cc.append(solving_ab (ns, rider))    
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def visualization (ns, rider):
   """
   MeqComposer (inpector)
   MeqParmFiddler
   MeqDataCollect (?)
   MeqDataConcat (?)
   MeqHistoryCollect (?)
   point to pyNodes...
   """
   stub = QRU.on_entry(ns, rider, visualization)
   cc = []
   cc.append(visualization_inspector(ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def transforms (ns, rider):
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
   stub = QRU.on_entry(ns, rider, transforms)
   cc = []
   # cc.append(transforms_coord (ns, rider))
   # cc.append(transforms_FFT (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')





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

def transforms_astro (ns, rider):
   """
   Astronomical coordinate transform nodes...
   """
   stub = QRU.on_entry(ns, rider, transforms_astro)
   cc = []
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

#================================================================================
# flowcontrol_... 
#================================================================================

def flowcontrol_reqseq (ns, rider):
   """
   The MeqReqSeq (Request Sequencer) node issues its request to its children one
   by one (rather than simultaneously, as other nodes do), in order of the child list.
   When finished, it passes on the result of only one of the children, which may be
   specified by means of the keyword 'result_index' (default=0, i.e. the first child).
   """
   stub = QRU.on_entry(ns, rider, flowcontrol_reqseq)
   rindex = 1
   cc = []
   for i in range(5):
      cc.append(ns << (-5*i))
   node = QRU.MeqNode(ns, rider, meqclass='ReqSeq',
                     name='ReqSeq(*cc, result_index='+str(rindex)+')',
                     children=cc, help=help, result_index=rindex)
   CC = EN.unique_stub(ns,'cc') << Meq.Composer(*cc)
   return QRU.on_exit (ns, rider, [node,CC])


#--------------------------------------------------------------------------------


#================================================================================
# visualization_... 
#================================================================================

def visualization_inspector (ns, rider):
   """
   An 'inspector' is a MeqComposer node. Its default viewer (invoked when
   clicking on it in the browser tree) is the Collections Plotter, which
   plots time-tracks of its children in a single plot. If the keyword
   argument 'plot_label' is given a list of strings, these are used as
   labels in the plot.
   - The plotter takes the average over all the non-time axes over the domain.
   .   (this is equivalent to axisreduction with reduction_axis=all-except-time)
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
   stub = QRU.on_entry(ns, rider, visualization_inspector)
   
   tname = opt_visualization_inspector_twig
   twig = ET.twig(ns, tname)
   cc = []
   plot_label = []
   for i in range(10):
      label = 'sin('+str(i)+'*'+tname+')'
      plot_label.append(label)
      cc.append(ns[label] << Meq.Sin(Meq.Multiply(i,twig)))
   node = QRU.MeqNode(ns, rider,
                      meqclass='Composer', name='inspector',
                      children=cc, help=help, plot_label=plot_label)
   return QRU.on_exit (ns, rider, [node],
                      viewer='Collections Plotter')


#================================================================================
# solving_... 
#================================================================================

def solving_ab (ns, rider):
   """
   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (one condeq child each):
   - condeq 0:  a + b = p (=10)
   - condeq 1:  a - b = q (=2)
   The result should be: a = (p+q)/2 (=6), and b = (p-q)/2 (=4)
   Condeq Results are the solution residuals, which should be small.
   """
   stub = QRU.on_entry(ns, rider, solving_ab)
   a = EN.unique_stub(ns, 'a') << Meq.Parm(0)
   b = EN.unique_stub(ns, 'b') << Meq.Parm(0)
   p = EN.unique_stub(ns, 'p') << Meq.Constant(10)
   q = EN.unique_stub(ns, 'q') << Meq.Constant(2)
   sum_ab = ns << Meq.Add(a,b) 
   diff_ab = ns << Meq.Subtract(a,b)
   drivers = EN.unique_stub(ns, 'driving_values_p_q') << Meq.Composer(p,q)
   parmset = EN.unique_stub(ns, 'solved_parameters_a_b') << Meq.Composer(a,b)

   condeqs = []
   condeqs.append(QRU.MeqNode (ns, rider, meqclass='Condeq',name='Condeq(a+b,p)',
                               help='Represents equation: a + b = p (=10)',
                               children=[sum_ab, p]))
   condeqs.append(QRU.MeqNode (ns, rider, meqclass='Condeq',name='Condeq(a-b,q)',
                               help='Represents equation: a - b = q (=2)',
                               children=[diff_ab, q]))

   solver = QRU.MeqNode (ns, rider, meqclass='Solver',
                         name='Solver(*condeqs, solvable=[a,b])',
                         help='Solver', show_recurse=True,
                         children=condeqs,
                         solvable=[a,b])  
   residuals = QRU.MeqNode (ns, rider, meqclass='Add', name='residuals',
                            help='The sum of the (abs) condeq residuals',
                            children=condeqs, unop='Abs')
   cc = [solver,residuals,drivers,parmset]
   return QRU.on_exit (ns, rider, cc,
                      parentclass='ReqSeq', result_index=0)



#================================================================================
# flagging_... 
#================================================================================

  
def flagging_simple (ns, rider):
   """
   Demonstration of simple flagging. A zero-criterion (zcrit) is calculated
   by a little subtree. This calculates the abs(diff) from the mean of the
   input, and then subtracts 'nsigma' times its stddev.
   The ZeroFlagger(oper=GE) flags all domain cells whose zcrit value is >= 0.
   Other behaviour can be specified with oper=LE or GT or LT.
   The MergeFlags node merges the new flags with the original flags of the input.
   """
   stub = QRU.on_entry(ns, rider, flagging_simple)

   twig = EN.unique_stub(ns,'twig') << Meq.Exp(ET.twig(ns, opt_flagging_twig))
   mean =  ns << Meq.Mean(twig)
   stddev =  ns << Meq.Stddev(twig)
   diff = ns << Meq.Subtract(twig,mean)
   absdiff = ns << Meq.Abs(diff)
   nsigma = opt_flagging_nsigma
   zcritname = 'zero_crit(nsigma='+str(nsigma)+')'
   zcrit = EN.unique_stub(ns, zcritname) << Meq.Subtract(absdiff,nsigma*stddev)
   zflag = QRU.MeqNode (ns, rider, meqclass='ZeroFlagger',
                        name='ZeroFlagger(zcrit, oper=GE)',
                        help='oper=GE: Flag all cells for which zcrit>=0.0.',
                        children=[zcrit], oper='GE')
   mflag = QRU.MeqNode (ns, rider, meqclass='MergeFlags',
                        name='MergeFlags(twig,zflag)',
                        help='Merge new flags with existing flags',
                        children=[twig, zflag])
   cc = [twig, mean, stddev, zcrit, zflag, mflag]
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

#================================================================================
# compounder_... 
#================================================================================

  
def compounder_simple (ns, rider):
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
   stub = QRU.on_entry(ns, rider, compounder_simple)

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
   cs = EN.unique_stub(ns,'Compounders') << Meq.Composer(*cc)
   return QRU.on_exit (ns, rider, nodes=[cs,cc[1],twig_LM,twig_ft])

# make_helpnode=True, ....??


#--------------------------------------------------------------------------------

#================================================================================
# resampling_... 
#================================================================================


def resampling_experiment (ns, rider,
                           twig=None, num_cells=[2,3], mode=1):
   """
   The experiment shows the difference between the twig, and after
   a sequence of ModRes and Resample. Obviously, the differences are
   smaller when the twig is smoother and/or when num_cells is larger.
   You may experiment with different twigs, MeqModRes num_cells or
   MeqResampler mode, by modifying the TDLOptions and recompiling and
   re-executing.
   """
   stub = QRU.on_entry(ns, rider, resampling_experiment)

   original = EN.unique_stub(ns, 'original') << Meq.Identity(twig)
   modres = QRU.MeqNode (ns, rider, meqclass='ModRes',
                         name='ModRes(original, num_cells=[nt,nf])',
                         help='changes the resolution of the REQUEST',
                         children=[twig], num_cells=num_cells)
   resampled = QRU.MeqNode (ns, rider, meqclass='Resampler',
                            name='Resampler(modres, mode='+str(mode)+')',
                            help='resamples the domain according to the twig request',
                            children=[modres], mode=mode)
   diff = EN.unique_stub(ns, 'diff(resampled,original)') << Meq.Subtract(resampled,original)
   # bookmark=[original, modres, resampled, diff])
   return QRU.on_exit (ns, rider, [diff])




#================================================================================
# axisreduction_... 
#================================================================================

def axisreduction_single (ns, rider):
   """
   Demonstration of basic axisreduction, on one child, with a single vellset.
   The reduction is done along all available axes (the default), producing a
   single-number Result.
   """
   stub = QRU.on_entry(ns, rider, axisreduction_single)

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
      cc.append(QRU.MeqNode (ns, rider,
                             meqclass=q, name=q+'('+str(twig.name)+')',
                             help=help[q], children=[twig]))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def axisreduction_multiple (ns, rider):
   """
   Demonstration of more advanced axis reduction, with Results that may contain
   multiple vellsets.
   NB: Axisreduction nodes ONLY work with a single child.
   The reduction is done along all available axes (the default), producing a
   single-number Result.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   stub = QRU.on_entry(ns, rider, axisreduction_multiple)

   democlass = 'Sum'
   help = record(f=democlass+' over the cells of a single vellset, of its single child',
                 range_5=democlass+' over the cells of multiple vellsets, from a tensor child')
   cc = []
   for twig_name in help.keys():
      twig = ET.twig(ns, twig_name)
      cc.append(twig)
      cc.append(QRU.MeqNode (ns, rider, meqclass=democlass,
                             name=democlass+'('+str(twig.name)+')',
                             help=help[twig_name], children=[twig]))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def axisreduction_axes (ns, rider):
   """
   Demonstration of more advanced axisreduction, along a subset of the available axes.
   If one or more reduction_axes are specified, the reduction is only
   along the specified axes (e.g. reduction_axes=['time'] reduces only
   the time-axis to length 1. The default is all available axes, of course. 
   The Result of a reduction node will be expanded when needed to fit a
   domain of the original size, in which multiple cells have the same value.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   stub = QRU.on_entry(ns, rider, axisreduction_axes)

   democlass = 'Sum'
   help = democlass+' over the cells of '
   twig_name = 'ft'
   twig = ET.twig(ns, twig_name)
   ntwig = ns << Meq.NElements(twig)
   cc = [twig,ntwig]
   cc.append(QRU.MeqNode (ns, rider, meqclass=democlass,
                          name=democlass+'('+str(twig.name)+')',
                          help=help+'no reduction_axes specified, assume all',
                          children=[twig]))
   cc.append(QRU.MeqNode (ns, rider, meqclass=democlass,
                          name=democlass+'('+str(twig.name)+', reduction_axes=[time])',
                          help=help+'the time-axis is reduced to length 1.',
                          children=[twig], reduction_axes=['time']))
   cc.append(QRU.MeqNode (ns, rider, meqclass=democlass,
                          name=democlass+'('+str(twig.name)+', reduction_axes=[freq])',
                          help=help+'the freq-axis is reduced to length 1.',
                          children=[twig], reduction_axes=['freq']))
   cc.append(QRU.MeqNode (ns, rider, meqclass=democlass,
                          name=democlass+'('+str(twig.name)+', reduction_axes=[freq,time])',
                          help=help+'both the freq and time axes are reduced.',
                          children=[twig], reduction_axes=['freq','time']))
   return QRU.on_exit (ns, rider, cc)




#================================================================================
# tensor_... 
#================================================================================


def tensor_manipulation (ns, rider):
   """
   Manipulation of 'tensor' nodes, i.e. nodes with multiple vellsets.
   """
   stub = QRU.on_entry(ns, rider, tensor_manipulation)
   c0 = ET.twig(ns,'f', nodename='c0')
   c1 = ET.twig(ns,'t', nodename='c1')
   c2 = ET.twig(ns,'ft', nodename='c2')
   cc = [c0,c1,c2]
   tensor = QRU.MeqNode (ns, rider, meqclass='Composer', name='Composer(c0,c1,c2)',
                         help="""Combine the vellsets in the Results of its children
                         into a Result with multiple vellsets in the new node.""",
                         children=[c0,c1,c2])
   cc.append(tensor)
   for index in [0,1,2]:
      cc.append(QRU.MeqNode (ns, rider, meqclass='Selector',
                             name='Selector(child, index='+str(index)+')',
                             help="""Select the specified (index) vellset in its child
                             for a new node with a single vellset in its Result""",
                             children=[tensor], index=index))
   if False:
      # Problem: Gives an error (list indix not supported?)
      cc.append(QRU.MeqNode (ns, rider, meqclass='Selector', name='Selector(child, index=[0,2])',
                             help="""Select the specified (index) vellsets in its child
                             for a new node with this subset of vellsets in its Result""",
                             children=[tensor], index=[0,2]))
   if True:
      # Problem: Does not work... (nr of vells stays the same). But index is the correct keyword...
      c1 = ET.twig(ns,'prod_f2t2')
      cc.append(QRU.MeqNode (ns, rider, meqclass='Paster', name='Paster(c0, c1, index=1)',
                             help="""Make a new node, in which the vellset from the
                             second child (c1) is pasted at the specified (index) position
                             among the vellsets of its first child (c0)""",
                             children=[tensor,c1], index=1))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def tensor_matrix (ns, rider):
   """
   Nodes with multiple vellsets can be treated as matrices.
   There are some specialised nodes that do matrix operations.
   NB: For the moment, only 2x2 matrices can be inverted, since
   this was easiest to program by hand (see MatrixInvert22).
   A more general inversion node will be implemted later.
   """
   stub = QRU.on_entry(ns, rider, tensor_matrix)
   cc = []
   cc.append(QRU.MeqNode (ns, rider, meqclass='Composer',
                          name='Composer(1,2,3,4,5,6, dims=[2,3])',
                          help="""Make a tensor node with a 2x3 array of vellsets.
                          This can be treated as a 2x3 matrix. Note the use of
                          constants as children, for easier inspection and verification.""",
                          children=range(6),dims=[2,3]))
   cc.append(QRU.MeqNode (ns, rider, meqclass='Transpose', name='Transpose(m0)',
                          help="""Make the 3x2 transpose of the given 2x3 matrix.""",
                          children=[cc[0]]))
   cc.append(QRU.MeqNode (ns, rider, meqclass='MatrixMultiply', name='MatrixMultiply(m0,m1)',
                          help="""Multply the original 2x3 matrix with its 3x2 transpose.
                          This produces a 2x2 matrix.""",
                          children=[cc[0],cc[1]]))
   cc.append(QRU.MeqNode (ns, rider, meqclass='MatrixMultiply', name='MatrixMultiply(m1,m0)',
                          help="""Multiply the 3x2 transpose with the original 2x3 matrix.
                          This produces a 3x3 matrix.""",
                          children=[cc[1],cc[0]]))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def tensor_matrix22 (ns, rider):
   """
   Because the 2x2 cohaerency matrix and the 2x2 Jones matrix play an important
   role in the radio-astronomical Measurement Equation (M.E.), there are a few
   specialized nodes that deal with 2x2 matrices.
   """
   stub = QRU.on_entry(ns, rider, tensor_matrix22)
   children = [ET.twig(ns,'cx_ft'),0,0,ET.twig(ns,'cx_tf')]
   cc = []
   cc.append(QRU.MeqNode (ns, rider, meqclass='Matrix22',
                          name='Matrix22(cxft,0,0,cxtf)',
                          help="""Make a complex 2x2 diagonal matrix.""",
                          children=children))
   cc.append(QRU.MeqNode (ns, rider, meqclass='MatrixInvert22',
                          name='MatrixInvert22(m0)',
                          help="""Invert the given 2x2 matrix (m0), cell-by-cell""",
                          children=[cc[0]]))
   cc.append(QRU.MeqNode (ns, rider, meqclass='MatrixMultiply',
                          name='MatrixMultiply(m0,m0inv)',
                          help="""Multply the matrix (m0) with its inverse (m0inv).
                          The result should be a unit matrix (cell-by-cell).""",
                          children=[cc[0],cc[1]]))
   cc.append(QRU.MeqNode (ns, rider, meqclass='ConjTranspose',
                          name='ConjTranspose(m0)',
                          help="""Conjugate Transpose the given matrix (m0)""",
                          children=[cc[0]]))
   return QRU.on_exit (ns, rider, cc)



#================================================================================
# leaves_...
#================================================================================

def leaves_constant (ns, rider):
   """
   A Constant node may represent a real or a complex constant.
   It can also be a tensor node, i.e. containing an N-dimensional array of vellsets.
   There are various ways to define one.
   """
   stub = QRU.on_entry(ns, rider, leaves_constant)
   cc = []
   if False:
      # The QRU.MeqNode(..., node=node) gives an error: no such field: order
      # NB: We could add quickref_help to the node here, and provide a QRU function
      #     that attaches the same help to the rider, with the proper path etc... 
      help = 'Constant node created with: '
      cc.append(QRU.MeqNode (ns, rider, node=(ns << 2.5),
                             help=help+'ns << 2.5'))
      cc.append(QRU.MeqNode (ns, rider, node=(ns.xxxx << 2.4),
                             help=help+'ns.xxxx << 2.4'))

   cc.append(QRU.MeqNode (ns, rider, meqclass='Constant', name='Constant(real)',
                          help=None, value=1.2))
   cc.append(QRU.MeqNode (ns, rider, meqclass='Constant', name='Constant(complex)',
                          help=None, value=complex(1,2)))

   vv = [1.5, -2.5, 3.5, -467]
   cc.append(QRU.MeqNode (ns, rider, meqclass='Constant',
                          name='Constant([r,r,r,r])',
                          help='produces a tensor node', value=vv))
   cc.append(QRU.MeqNode (ns, rider, meqclass='Constant',
                          name='Constant([r,r,r,r], shape=[2,2])',
                          help='produces a tensor node', value=vv, shape=[2,2]))

   vv[2] = complex(3,5)
   help = """A vector that contains one or more complex numbers
   produces a tensor node with all complex values"""
   cc.append(QRU.MeqNode (ns, rider, meqclass='Constant',
                          name='Constant([r,r,cx,r])',
                          help=help, value=vv))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def leaves_parm (ns, rider):
   """
   MeqParm nodes represent M.E. parameters, which may be solved for.
   """
   stub = QRU.on_entry(ns, rider, leaves_parm)
   cc = []
   help = ''
   cc.append(QRU.MeqNode (ns, rider, meqclass='Parm',
                          help=help, default=2.5))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def leaves_noise (ns, rider):
   """
   Noise nodes generate noisy cell values. The arguments are passed as
   keyword arguments in the node constructor (or as children?)
   """
   stub = QRU.on_entry(ns, rider, leaves_noise)
   cc = []
   help = 'Gaussian noise with given stddev (and zero mean)'
   cc.append(QRU.MeqNode (ns, rider, meqclass='GaussNoise',
                          name='GaussNoise(stddev=2)',
                          help=help,
                          stddev=2.0))
   help = 'Gaussian noise with given stddev and mean'
   # NB: mean does not work...
   cc.append(QRU.MeqNode (ns, rider, meqclass='GaussNoise',
                          name='GaussNoise(stddev=2,mean=-10)',
                          help=help,
                          mean=-10.0, stddev=2.0))
   if False:
      # Problem: The server crashes on this one...!
      help = 'Random noise between lower and upper bounds'
      cc.append(QRU.MeqNode (ns, rider, meqclass='RandomNoise',
                             name='RandomNoise(-2,4)',
                             help=help,
                             lower=-2.0, upper=4.0))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def leaves_grids (ns, rider):
   """
   Grid nodes fill in the cells of the requested domain with the
   values of the specified axis (time, freq, L, M, X, Y, Z, etc).
   They are created by:  ns[nodename] << Meq.Grid(axis='M')

   The two default axes (time and freq) also have dedicated Grid nodes,
   called MeqTime and MeqFreq, e.g.:  ns[nodename] << Meq.Freq()

   NB: Check also the Forest State record. Note that its axis_map and
   its axis_list have default axes [time,freq,L,M], but that extra
   axes are added to them as soon as MeqGrid node with a new axis
   (name) has been defined.   
   """
   stub = QRU.on_entry(ns, rider, leaves_grids)
   cc = []
   for q in ['Freq','Time']:
      cc.append(QRU.MeqNode (ns, rider, meqclass=q,
                             name=q+'()', help=None)) 
   for q in ['time','L','M','X','Y','Z']:
      cc.append(QRU.MeqNode (ns, rider, meqclass='Grid',
                             name='Grid(axis='+q+')', help=None, axis=q))
   cc.append(ns.ft << Meq.Add(cc[2],cc[3]))
   cc.append(ns.LM << Meq.Add(cc[4],cc[5]))
   cc.append(ns.ftLM << Meq.Add(cc[2],cc[3],cc[4],cc[5]))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def leaves_spigot (ns, rider):
   """
   The MeqSpigot reads data from an AIPS++/Casa Measurement Set (uv-data).
   It is twinned with the MeqSink, which writes uv-data back into the MS,
   and generates a sequence of requests with suitable time-freq domains
   (snippets). See also....
   MeqVisDataMux:
   MeqFITSSpigot:
   """
   stub = QRU.on_entry(ns, rider, leaves_spigot)
   cc = []
   help = ''
   cc.append(QRU.MeqNode (ns, rider, meqclass='Spigot',
                          name='Spigot()', help=help))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def leaves_FITS (ns, rider):
   """
   There are various nodes to read images from FITS files.
   MeqFITSReader:
   MeqFITSImage:
   MeqFITSSpigot:
   """
   stub = QRU.on_entry(ns, rider, leaves_FITS)
   cc = []
   help = ''
   cc.append(QRU.MeqNode (ns, rider, meqclass='FITSReader',
                          help=help))
   return QRU.on_exit (ns, rider, cc)




#================================================================================
# unops_... (Unary operations)
#================================================================================


def unops_elementary (ns, rider, twig=None):
   """
   Elementary unary math operations.
   """
   stub = QRU.on_entry(ns, rider, unops_elementary)
   cc = [twig]
   help = record(Negate='-c', Invert='1/c', Exp='exp(c)', Sqrt='square root',
                 Log='e-log (for 10-log, divide by Log(10))')
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      # NB: explain log...
      cc.append(QRU.MeqNode (ns, rider, meqclass=q,
                             name=q+'('+str(twig.name)+')',
                             help=help[q], children=[twig]))
   return QRU.on_exit (ns, rider, cc)

#-----------------------------------------#--------------------------------------------------------------------------------

def unops_goniometric (ns, rider, twig=None):
   """
   (Tri-)Goniometric functions (Sin, Cos, Tan) turn an angle (rad) into a fraction.
   Their inverses (Asin, Acos, Atan) turn a fraction into an angle (rad).
   The abs inputs of Asin and Acos must be smaller than one, of course. 
   
   Applying first the function and then its inverse should yield the original
   input (which it does NOT in case of Acos(Cos(x))....)
   """
   stub = QRU.on_entry(ns, rider, unops_goniometric)
   cc = []
   for q in ['Sin','Cos','Tan','Asin','Acos','Atan']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
   cc.append('Applying a function to its inverse should yield unity')
   cc.append(stub('AsinSin') << Meq.Asin(cc[0]))
   cc.append(stub('AcosCos') << Meq.Acos(cc[1]))
   cc.append(stub('AtanTan') << Meq.Atan(cc[2]))
   return QRU.on_exit (ns, rider, cc,
                       help='** Extra topic help **',
                       show_recurse=True)

#--------------------------------------------------------------------------------

def unops_hyperbolic (ns, rider, twig=None):
   """
   Hyperbolic functions.
   """
   stub = QRU.on_entry(ns, rider, unops_hyperbolic)
   cc = [twig]
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(QRU.MeqNode (ns, rider,
                             meqclass=q, name=q+'('+str(twig.name)+')',
                             help=None, children=[twig]))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def unops_complex (ns, rider, twig=None):
   """
   Complex unary math operations on a (usually) complex child.
   """
   stub = QRU.on_entry(ns, rider, unops_complex)
   twig = ET.twig(ns,'cx_ft')                # override input twig...
   cc = [twig]
   help = record(Abs='', Norm='like Abs', Arg='-> rad', Real='', Imag='',
                 Conj='complex conjugate: a+bj -> a-bj',
                 Exp='exp(a+bj) = exp(a)*exp(bj), i.e. cos with increasing ampl',
                 Log='e-log (ln)')
   for q in ['Abs','Norm','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(QRU.MeqNode (ns, rider,
                             meqclass=q, name=q+'('+str(twig.name)+')',
                             help=help[q], children=[twig]))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def unops_power (ns, rider, twig=None):
   """
   Nodes that take some power of its child.
   """
   stub = QRU.on_entry(ns, rider, unops_power)
   cc = [twig]
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(QRU.MeqNode (ns, rider,
                             meqclass=q, name=q+'('+str(twig.name)+')',
                             children=[twig]))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def unops_misc (ns, rider, twig=None):
   """
   Miscellaneous unary math operations.
   """
   stub = QRU.on_entry(ns, rider, unops_misc)
   cc = [twig]
   help = record(Abs='Take the absolute value.',
                 Ceil='Round upwards to integers.',
                 Floor='Round downwards to integers.',
                 Stripper="""Remove all derivatives (if any) from the result.
                 This saves space and can be used to control solving.""",
                 Identity='Make a copy node with a different name.'
                 )
   for q in ['Abs','Ceil','Floor','Stripper','Identity']:
      cc.append(QRU.MeqNode (ns, rider, meqclass=q,
                             name=q+'('+str(twig.name)+')',
                             help=help[q], children=[twig]))
   return QRU.on_exit (ns, rider, cc)


#================================================================================
# binops_math
#================================================================================

def binops_math (ns, rider):
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
   stub = QRU.on_entry(ns, rider, binops_math)
   lhs = ET.twig(ns, opt_binops_math_lhs)         # left-hand side (child)
   rhs = ET.twig(ns, opt_binops_math_rhs)         # right-hand side (child)
   cc = []
   help = record(Subtract='lhs-rhs', Divide='lhs/rhs', Pow='lhs^rhs',
                 Mod='lhs%rhs',
                 ToComplex='(real, imag)', Polar='(amplitude, phase)')
   # Problem: MeqMod() crashes the meqserver.... Needs integer children??
   # for q in ['Subtract','Divide','Pow','ToComplex','Polar','Mod']:
   for q in ['Subtract','Divide','Pow','ToComplex','Polar']:
      cc.append(QRU.MeqNode (ns, rider, meqclass=q,
                             name=q+'('+str(lhs.name)+','+str(rhs.name)+')',
                             help=help[q], children=[lhs,rhs]))
   return QRU.on_exit (ns, rider, cc)


#================================================================================
# multi_math
#================================================================================

def multi_math (ns, rider):
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
   stub = QRU.on_entry(ns, rider, multi_math)

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
      cc.append(QRU.MeqNode (ns, rider, meqclass=q,
                             name=q+'('+sname+')', help=help[q],
                             children=twigs))

   # Then the weighted ones:
   help = record(WSum="""Weighted sum: w[0]*c0 + w[1]*c1 + w[2]*c2 + ...
                 The weights vector (weights) is a vector of DOUBLES (!)""",
                 WMean="""Weighted mean, the same as WSum, but divides by
                 the sum of the weights (w[0]+w[1]+w[2]+....)""")
   sw = str(weights).replace('.0','').replace('.',',')
   for q in ['WSum','WMean']:
      # print '\n** ',q,': weigths =',weights,'\n'
      cc.append(QRU.MeqNode (ns, rider, meqclass=q,
                             name=q+'('+sname+',weights='+sw+')',
                             help=help[q],
                             weights=weights, children=twigs))

   # Attach the input twigs to the bundle, for inspection.
   # NB: If attached at the start, WMean and WSum refuse to plot....?
   cc.extend(twigs)
   return QRU.on_exit (ns, rider, cc)












#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Local testing forest:
#================================================================================

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QRU)
TDLRuntimeMenu(":")

# For TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------

def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   global rootnodename
   rootnodename = 'QuickRef'                    # The name of the node to be executed...
   global rider                                 # used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # CollatedHelpRecord object
   QRU.on_exit (ns, rider,
               nodes=[QR_MeqNodes(ns, rider)])

   # Finished:
   return True
   


#--------------------------------------------------------------------------------

def _tdl_job_execute_1D_f (mqs, parent):
   return QRU._tdl_job_execute_f (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_1D_t (mqs, parent):
   return QRU._tdl_job_execute_t (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_4D_ftLM (mqs, parent):
   return QRU._tdl_job_execute_ftLM (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode=rootnodename)

def _tdl_job_m (mqs, parent):
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   return QRU._tdl_job_print_doc (mqs, parent, rider, header=header)

def _tdl_job_print_hardcopy (mqs, parent):
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header=header)

def _tdl_job_show_doc (mqs, parent):
   return QRU._tdl_job_show_doc (mqs, parent, rider, header=header)

def _tdl_job_save_doc (mqs, parent):
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename=header)



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_MeqNodes.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_MeqNodes(ns, 'test', rider)
      if 1:
         print rider.format()

   print '\n** End of standalone test of: QR_MeqNodes.py:\n' 

#=====================================================================================





