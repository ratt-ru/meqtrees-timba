"""
QuickRef module: QR_MeqNodes.py
Gives an overview over all available MeqNodes.
Click on the top bookmark ('help_on__how_to_use_this_module')
"""

# file: ../JEN/QuickRef/QR_MeqNodes.py:
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
#   - 05 sep 2008: implemented 'coordinates'
#
# Description:
#
# Remarks:
#
# Problem nodes:
#
#   MeqNElements           multiple children give error
#   (Axis reduction nodes do not work on multiple children...?)
#   MeqMod                 crashes the browser/server
#   MeqRandomNoise         crashes the browser/server
#
#   MeqPaster              does not paste
#   MeqSelector            index=[1,2] not supported
#
#   MeqResampler           server crashes when changing mode 1 -> 2
#                          FitsImage()
#
#   MeqRaDec               crashes the meqserver...!            
#   MeqObjectRADec         Measures cannot find the planetary data table DE200
#
#   MeqFITSWriter/Reader   Something goes wrong in the writing and reading of the
#                          coordinates (time,freq, etc). See FITS_RW() below.
#
# Workaround exists:
#
#   MeqMatrix22            use of children=[...] gives error
#   MeqConjugateTranspose  use of children=[...] gives error
#
# Misc:
#
#   MeqAzEl                Meq.AzEl(radec,..) and (radec=radec,..) give the same result
#                          (the 2nd form is confusing, and should be discouraged,
#                           and NOT used in the wiki example!). Review the interface
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

from Timba.Contrib.JEN.pylab import PyNodePlot as PNP

import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************

WNB_observatories = 'ALMA ARECIBO ATCA BIMA CLRO DRAO DWL GB GBT GMRT IRAM PDB IRAM_PDB JCMT MOPRA MOST NRAO12M NRAO_GBT PKS VLA VLBA WSRT'.split(' ')

WNB_ssobjs = 'SUN MOON MERCURIUS VENUS MARS JUPITER SATURNUS URANUS NEPTUNUS PLUTO'.split(' ')


oo = TDLCompileMenu("QR_MeqNodes topics:",
                    # TDLOption_user_level,               # ... needs some thought ...
                    # TDLOption('opt_allcats',"all",True),
                    TDLOption('opt_alltopics',"override: include all topics",True),
                    TDLMenu("Unary math (unops) nodes (one child)",
                            TDLOption('opt_unops_twig',"input twig (child node)",
                                      ET.twig_names(), more=str),
                            toggle='opt_unops'),
                    TDLMenu("Binary math (binops) nodes (two children)",
                            TDLOption('opt_binops_lhs',"lhs twig (child node)",
                                      ET.twig_names(), more=str),
                            TDLOption('opt_binops_rhs',"rhs twig (child node)",
                                      ET.twig_names(), more=str),
                            toggle='opt_binops'),
                    TDLMenu("Multimath: one or more children",
                            TDLOption('opt_multimath_twig1',"1st twig (child node)",
                                      ET.twig_names(), more=str),
                            TDLOption('opt_multimath_twig2',"2nd twig (child node)",
                                 ET.twig_names(include=[None]), more=str),
                            TDLOption('opt_multimath_twig3',"3rd twig (child node)",
                                      ET.twig_names(include=[None]), more=str),
                            toggle='opt_multimath'),
                    TDLMenu("Leaf nodes (no children)",
                            toggle='opt_leaves'),
                    TDLMenu("Interaction with FITS files",
                            TDLMenu("write/read results to/from FITS file",
                            toggle='opt_FITS_RW'),
                            TDLMenu("FITSImage (mode=1)",
                                    TDLOption('opt_FITSImage_cutoff',"0.0<cutoff level<1.0",
                                              [1.0,0.9,0.5,0.1,0.0], more=float),
                                    toggle='opt_FITSImage'),
                            TDLMenu("FITSImage (mode=2)",
                                    TDLOption('opt_FITSImage_cutoff_mode2',"0.0<cutoff level<1.0",
                                              [1.0,0.9,0.5,0.1,0.0], more=float),
                                    TDLOption('opt_FITSImage_resampler_mode',"ReSampler mode",
                                              [1,2], more=int),
                                    toggle='opt_FITSImage_mode2'),
                            toggle='opt_FITS'),
                    TDLMenu("Tensor nodes (multiple vellsets)",
                            TDLOption('opt_tensor_manipulation',"Tensor manipulation",False),
                            TDLOption('opt_tensor_matrix',"Matrix operations",False),
                            TDLOption('opt_tensor_matrix22',"Operations on 2x2 matrices",False),
                            toggle='opt_tensor'),
                    TDLOption('opt_axisreduction',"axisreduction",False),
                    TDLMenu("resampling",
                            TDLOption('opt_resampling_MeqModRes_twig',
                                      "input twig (child node) of MeqModRes",
                                      ET.twig_names(first='f+t'), more=str),
                            TDLOption('opt_resampling_MeqModRes_num_freq',
                                      "nr of freq cells for MeqModRes num_cells [nt,nf]",
                                      [4,1,2,3,5,6,10,20,50], more=int),
                            TDLOption('opt_resampling_MeqModRes_num_time',
                                      "nr of time cells for MeqModRes num_cells [nt,nf]",
                                      [4,1,2,3,5,6,10,20,50], more=int),
                            TDLOption('opt_resampling_MeqResampler_mode',"mode for MeqResampler",
                                      [1,2]),
                            toggle='opt_resampling'),
                    TDLMenu("compounder",
                            TDLOption('opt_compounder_simple',"simple",False),
                            TDLOption('opt_compounder_advanced',"advanced",False),
                            toggle='opt_compounder'),
                    TDLMenu("flagging",
                            TDLOption('opt_flagging_twig',"input twig (child node)",
                                      ET.twig_names('noise', first='noise_3'), more=str),
                            TDLOption('opt_flagging_nsigma',"nsigma (times stddev)",
                                      [5.0,1.0,2.0,3.0,4.0,7.0,9.0], more=str),
                            toggle='opt_flagging'),
                    TDLOption('opt_solving',"solving",False),
                    TDLMenu("spigot2sink (MS)",
                            TDLOption('opt_s2s_nstat',"nr of stations in array",
                                      [5,3,4,5,6,7,8,9,10,14], more=int),
                            TDLOption('opt_s2s_pynodePlot',"make 4-corrs plot",False),
                            toggle='opt_s2s'),
                    TDLMenu("visualization",
                            TDLOption('opt_visualization_inspector_twig',"input twig (child node)",
                                      ET.twig_names(first='t'), more=str),
                            toggle='opt_visualization'),
                    TDLMenu("coordinates",
                            TDLOption('opt_coordinates_RA',"input Right Ascension (rad)",
                                      [0.0,1.0,-1.0,math.pi/2,math.pi,math.pi*1.5], more=float),
                            TDLOption('opt_coordinates_DEC',"input Declination (rad)",
                                      [1.0,0.0,-1.0,math.pi/2], more=float),
                            TDLOption('opt_coordinates_ssobj',"(override) RA,DEC from Solar System object",
                                      WNB_ssobjs+[None], more=str),
                            TDLMenu("Earth-related",
                                    TDLOption('opt_coordinates_observatory',"Observatory",
                                              WNB_observatories, more=str),
                                    toggle='opt_coord_azel'),
                            TDLMenu("image-related",
                                    TDLOption('opt_coordinates_RA0',"RA of phase centre (rad)",
                                              [0.0,1.0,-1.0,math.pi/2,math.pi,math.pi*1.5], more=float),
                                    TDLOption('opt_coordinates_DEC0',"DEC of phase centre (rad)",
                                              [1.0,0.0,-1.0,math.pi/2], more=float),
                                    toggle='opt_coord_lmn'),
                            toggle='opt_coordinates'),
                    # TDLOption('opt_transforms',"transforms",False),
                    TDLOption('opt_flowcontrol',"flowcontrol",False),
                    
                    TDLMenu("help",
                            TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                            toggle='opt_helpnodes'),

                    toggle='opt_QR_MeqNodes')

# Assign the menu to an attribute, for outside visibility:
itsTDLCompileMenu = oo

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
   if override or opt_binops:
      cc.append(binops (ns, rider))
   if override or opt_multimath:
      cc.append(multimath (ns, rider))
   if override or opt_leaves:             
      cc.append(leaves (ns, rider))
   if override or opt_FITS:
      cc.append(FITS (ns, rider))
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
   if override or opt_s2s:
      cc.append(spigot2sink (ns, rider))
   if override or opt_visualization:
      cc.append(visualization (ns, rider))
   if override or opt_flowcontrol:
      cc.append(flowcontrol (ns, rider))
   if override or opt_coordinates:
      cc.append(coordinates (ns, rider))

   if override or opt_helpnodes:
      cc.append(make_helpnodes (ns, rider))

   return QRU.on_exit (ns, rider, cc, mode='group')



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


#********************************************************************************
# Topics and their subtopics:
#********************************************************************************

#================================================================================
# spigot2sink_... 
#================================================================================

def spigot2sink (ns, rider):
   """
   The MeqSpigot reads data from an AIPS++/Casa Measurement Set (MS, uv-data).
   It is twinned with the MeqSink, which (optionally) writes uv-data back into the MS,
   and generates a sequence of requests with suitable time-freq domains (snippets).
   See also <A href='http://www.astron.nl/meqwiki/StreamControl'>StreamControl()</A>.
   
   <li> <A href='http://www.astron.nl/meqwiki/StreamControl'>Meq.Spigot()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/StreamControl'>Meq.Sink()</A>
   <li> <A href='http://www.astron.nl/meqwiki/StreamControl'>Meq.VisDataMux()</A> 

   In the various low-threshold 'frameworks' (see modules QR_Meow and QR_Calico),
   the interaction with the MS will be hidden to the user. A full treatment of
   all the details and possibilities is given in the module QR_MS. Here, we show
   the simplest possible case: Spigot/Sink pairs are created for a small subset
   of ifrs, and the results are displayed in various ways. Use the <b>execute MS</b>
   option in the runtime menu to read a sequence of timeslots from a smallish MS,
   which is a short WSRT observation of 3c286 @ 21cm.

   <tip>
   Use the pynodePlot option to make a plot of the 4 corrs of all ifrs in a single
   real-vs-imag plot. Note that the XX(=I+Q) are larger than the YY(=I-Q), due to
   the ~10% linear polarisation. The XY(=U+iV) and YX(=U-iV) show the same. 
   </tip>

   The MeqSink nodes are the children of a single VisDataMux node,
   which is the root node that is executed by <b>execute MS</b>.  The
   request contains the MS name and any other instructions for reading
   the MS. The VisDataMux then generates a sequence of snippet
   (timeslot) requests to its children (the MeqSinks).
   """

   stub = QRU.on_entry(ns, rider, spigot2sink, stubname='s2s')
   nstat = QRU.getopt(globals(), 'opt_s2s_nstat', rider)
   pynodePlot = QRU.getopt(globals(), 'opt_s2s_pynodePlot', rider)
   # msname = '3C286-10705290.MS'
   nstat = 5
   cc = []
   crosscorrs = []
   sinks = []
   for p in range(nstat-1):
      for q in range(p,nstat):
         node = stub('Spigot')(p)(q) << Meq.Spigot(station_1_index=p,
                                                   input_column='DATA',
                                                   # corr_index=[0,1,2,3],
                                                   # flag_bit=4,
                                                   # input_column=input_col)
                                                   station_2_index=q)
         if not p==q:
            crosscorrs.append(node)                # subset for pynode
         if p==0:
            cc.append(node)                        # subset to be published
         node = stub('Sink')(p,q) << Meq.Sink(node,
                                              # output_col=output_col,
                                              # corr_index=self._MS_corr_index,
                                              station_1_index=p,
                                              station_2_index=q)
         sinks.append(node)

   post = None
   if pynodePlot:
      qhelp = None
      document = True
      cc.append(PNP.pynode_Plot(ns, crosscorrs, 'VIS22'))
      # cc.append(PNP.pynode_Plot(ns, crosscorrs, 'VIS22_IQUV'))
      post = cc[-1]
            
   # The single VisDataMux node is the actual interface node.
   # The name 'VisDataMux' is expected by tdl_job_execute_MS()
   if post:
      vdm = ns['VisDataMux'] << Meq.VisDataMux(post=post, *sinks)
   else:
      vdm = ns['VisDataMux'] << Meq.VisDataMux(*sinks)
   return QRU.on_exit (ns, rider, cc)



#================================================================================
# coordinates_... 
#================================================================================

def coordinates (ns, rider):
   """
   Nodes that to (mostly astronomical) coordinate transforms.
   """
   stub = QRU.on_entry(ns, rider, coordinates)
   cc = []
   override = opt_alltopics

   # Get the radec (RA,DEC) node here, and pass it down:
   ssobj = QRU.getopt(globals(), 'opt_coordinates_ssobj', rider)
   ra = QRU.getopt(globals(), 'opt_coordinates_RA', rider)
   dec = QRU.getopt(globals(), 'opt_coordinates_DEC', rider)
   if False and ssobj:                                           # temporarily disabled
      # Measures cannot find the planetary data table DE200
      radec = stub('radec') << Meq.ObjectRADec(obj_name=ssobj)
   else:
      RA = stub('RA') << ra
      DEC = stub('DEC') << dec
      radec = stub('radec') << Meq.Composer(RA,DEC)

   if override or opt_coord_azel:
      cc.append(coord_azel (ns, rider, radec=radec))
   if override or opt_coord_lmn:
      cc.append(coord_lmn (ns, rider, radec=radec))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def coord_azel (ns, rider, radec=None):
   """
   Coordinate transform nodes that involve Earth-related coordinates like
   Azimuth, Elevation, Latitude, Longitude, Local Sidereal Time (LST) etc.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.AzEl(radec, observatory='WSRT')</A> -> azel (rad)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Parangle(radec, observatory='WSRT')</A> -> rad
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.LST(observatory='ATCA')</A> -> hrs(?)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.LongLat(observatory='VLA')</A> -> longlat (rad)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.RaDec(azel, observatory='WSRT')</A> -> radec
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ObjectRADec(obj_name='JUPITER')</A> -> radec

   The nodes that accept observatory=name(string) will also accept xyz=xyz(tensor node),
   giving ITRF Earth position coordinates. In this case, the radec argument must be specified explicitly(!)

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.AzEl(radec=radec, xyz=xyz)</A> -> azel (rad)

   These nodes use the AIPS++/Casa Measures module, written by Wim Brouw.
   They use the time values of the request domain (assuming MJD).
   See also: <A href='http://www.astron.nl/meqwiki/AllNodes'>meqwiki/MeqAllNodes</A>
   
   <tip>
   The Meq.AzEl nodes are tensor nodes, i.e. their results have two vellsets (RA amd DEC).
   The same is true for radec, azel, longlat etc.
   You may toggle between multiple vellsets of a node with the right-click menu.
   </tip>

   <tip>
   The (ITRF) Earth coordinates in this example are those of a VLA antenna.
   Compare the Az/El results with those of the VLA observatory.
   </tip>
   """

   stub = QRU.on_entry(ns, rider, coord_azel)
   cc = []

   cc.append(radec)
   
   obs = QRU.getopt(globals(), 'opt_coordinates_observatory', rider)

   cc.append(stub('AzEl')('observatory') << Meq.AzEl(radec, observatory=obs))
   if False:
      # Crashes the server...!
      cc.append(stub('RaDec')('observatory') << Meq.RaDec (cc[-1], observatory=obs))
   cc.append(stub('ParAngle')('observatory') << Meq.ParAngle(radec, observatory=obs))
   cc.append(stub('LST')('observatory') << Meq.LST(observatory=obs))

   # Use the Earth coordinates of a VLA antenna:
   x = stub('x') << -1597262.96
   y = stub('y') << -5043205.54
   z = stub('z') << 3554901.34
   xyz = stub('xyz')('VLA antenna') << Meq.Composer(x,y,z)
   cc.append(xyz)

   cc.append(stub('AzEl')('xyz') << Meq.AzEl(radec=radec, xyz=xyz))
   cc.append(stub('ParAngle')('xyz') << Meq.ParAngle(radec=radec, xyz=xyz))
   cc.append(stub('LongLat')('xyz') << Meq.LongLat(xyz=xyz))
   
   return QRU.on_exit (ns, rider, cc, show_recurse=True)


#--------------------------------------------------------------------------------

def coord_lmn (ns, rider, radec=None):
   """
   Coordinate transform nodes related to relative sky coordinates (l,m,n).

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.LMN(radec0, radec)</A> -> lmn
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.LMRaDec(radec_0=radec0, lm=lm)</A> -> radec
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ObjectRADec(obj_name='JUPITER')</A> -> radec

   They use the AIPS++/Casa Measures module, written by Wim Brouw.
   See also: <A href='http://www.astron.nl/meqwiki/MeqAllNodes'>meqwiki/MeqAllNodes</A>

   <tip>
   Compare the input (RA,DEC) with the one produced by MeqLMRaDec after converting
   back and forth. Note that they are the same, except for an 2pi 'ambiguity'.
   </tip>
   """

   stub = QRU.on_entry(ns, rider, coord_lmn)
   cc = []

   cc.append(radec)

   ra0 = QRU.getopt(globals(), 'opt_coordinates_RA0', rider)
   dec0 = QRU.getopt(globals(), 'opt_coordinates_DEC0', rider)
   radec0 = stub('radec0') << Meq.Composer(ra0,dec0)
   cc.append(radec0)
   
   cc.append(stub('LMN') << Meq.LMN(radec0, radec))
   L = stub('L') << Meq.Selector(cc[-1], index=0)
   M = stub('M') << Meq.Selector(cc[-1], index=1)
   lm = stub('LM') << Meq.Composer(L,M)
   cc.append(lm)
   cc.append(stub('LMRaDec') << Meq.LMRaDec(radec_0=radec0, lm=lm))

   qhelp = 'Difference between the input radec, and after converting to (l,m) and back'
   cc.append(stub('diff') << Meq.Subtract(cc[-1], radec, qhelp=qhelp))
   
   return QRU.on_exit (ns, rider, cc, show_recurse=True)



#================================================================================
# transforms_... 
#================================================================================

def transforms (ns, rider):
   """
   MeqUVBrick
   MeqUVInterpol
   MeqVisPhaseShift
   
   """
   stub = QRU.on_entry(ns, rider, transforms)
   cc = []
   # cc.append(transforms_coord (ns, rider))
   # cc.append(transforms_FFT (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#================================================================================
# flowcontrol_... 
#================================================================================

def flowcontrol (ns, rider):
   """
   Nodes that control the issuing of requests to children:
   """
   stub = QRU.on_entry(ns, rider, flowcontrol)
   cc = []
   cc.append(flowcontrol_reqseq (ns, rider))
   # cc.append(flowcontrol_reqmux (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------


def flowcontrol_reqseq (ns, rider):
   """
   Nodes that control the issuing of requests to children:
   
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ReqSeq()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ReqMux()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sink()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.VisDataMux</A> 

   The MeqReqSeq (Request Sequencer) node issues its request to its children one
   by one (rather than simultaneously, as other nodes do), in the order of the child list.
   When finished, it passes on the result of only one of the children, which may be
   specified by means of the keyword 'result_index' (default=0, i.e. the first child).
   """
   stub = QRU.on_entry(ns, rider, flowcontrol_reqseq)
   cc = []

   children = []
   for i in range(5):
      children.append(ns << (-5*i))
   cc.append(stub('children') << Meq.Composer(*children))

   cc.append(stub('ReqSeq') << Meq.ReqSeq(*children))
   for rindex in [0,1]:
      cc.append(stub('ReqSeq')(rindex) << Meq.ReqSeq(children=children,
                                                     result_index=rindex))
   return QRU.on_exit (ns, rider, cc, node_help=True)


#--------------------------------------------------------------------------------


#================================================================================
# visualization_... 
#================================================================================

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

def visualization_inspector (ns, rider):
   """
   An 'inspector' is a MeqComposer node. Its default viewer (invoked when
   clicking on it in the browser tree) is the Collections Plotter, which
   plots time-tracks of its children in a single plot. If the keyword
   argument 'plot_label' is given a list of strings, these are used as
   labels in the plot.
   <li> The plotter takes the average over all the non-time axes over the domain.
   (this is equivalent to axisreduction with reduction_axis=all-except-time)
   Exercise: Play with different input twigs, and different domain axes.
   <li> When the result is complex, one may toggle betweem ampl,phase,real,imag. 
   <li> When a sequence is executed, the tim-slots are plotted sequentially.
   NB: this can be confusing, since the time-axis is really a sequence-axis...
   Exercise: Execute a sequence with different fractional time-steps.
   (a time-step of 1.0 steps by the domain size, so the time is continuous)
   <li> When the tree is excuted again, the new result is plotted after what is there
   already. The plot can be cleared via its right-clicking menu.
   On the whole, the Inspector is very useful, but it has its limitation.
   For more control, check out the PyNodePlots.
   """
   stub = QRU.on_entry(ns, rider, visualization_inspector)
   
   tname = QRU.getopt(globals(), 'opt_visualization_inspector_twig', rider)
   twig = ET.twig(ns, tname)
   cc = []
   plot_label = []
   children = []
   nc = 7
   for i in range(nc):
      label = 'sin('+str(i)+'*'+tname+')'
      plot_label.append(label)
      node = stub(label) << Meq.Sin(Meq.Multiply(i,twig))
      children.append(node)
      if i in [0,nc/2,nc-1]:   # display only a subset of the children
         cc.append(node)

   cc.append(stub('inspector') << Meq.Composer(children=children,
                                               plot_label=plot_label,
                                               qviewer='Collections Plotter'))
   return QRU.on_exit (ns, rider, cc, node_help=True, show_bookmarks=True)


#================================================================================
# solving_... 
#================================================================================

def solving (ns, rider):
   """
   The purpose of MeqTrees is not only to allow the implementation of an arbitrary
   Measurement Equation, but also to solve for (arbitrary subsets of) its parameters.
   This is treated in detail in a separate module (QR_solving). For completeness,
   we show a single simple example here.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Parm()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Condeq()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Solver()</A> 

   """
   stub = QRU.on_entry(ns, rider, solving)
   cc = []
   cc.append(solving_ab (ns, rider))    
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def solving_ab (ns, rider):
   """
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Parm()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Condeq()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Solver()</A> 

   Demonstration of solving for two unknown parameters (a,b),
   using two linear equations (each represented by a Condeq node):
   <li> condeq 0:  a + b = p (=10)
   <li> condeq 1:  a - b = q (=2)

   The result should be (check this):
   <li> a = (p+q)/2 = (10+2)/2 = 6
   <li> b = (p-q)/2 = (10-2)/2 = 4
   
   The Condeq Results are the solution residuals, which should be small.

   Note that the solvable MeqParms are found by a search of the nodescope
   for nodes with tags 'solvable'. 
   """
   stub = QRU.on_entry(ns, rider, solving_ab)
   cc = []

   a = stub('a') << Meq.Parm(0, tags='solvable')
   b = stub('b') << Meq.Parm(0, tags='solvable')

   qhelp ="""The parameter values after solving. Check that they now have the
   correct values for satisfying the two equations."""
   cc.append(stub('solved_parameters_a_b') << Meq.Composer(a,b, qhelp=qhelp))

   p = stub('p') << Meq.Constant(10)
   q = stub('q') << Meq.Constant(2)

   qhelp = """The right-hand sides of the condeq equations. Check that p=10, and q=2"""
   cc.append(stub('driving_values_p_q') << Meq.Composer(p,q, qhelp=qhelp))

   condeqs = []
   sum_ab = stub('a+b') << Meq.Add(a,b) 
   qhelp ='This condeq represents equation: a + b = p (lhs=rhs)'
   condeqs.append(stub('a+b=p') << Meq.Condeq(sum_ab, p, qhelp=qhelp))
   cc.append(condeqs[-1])

   diff_ab = stub('a-b') << Meq.Subtract(a,b)
   qhelp ='This condeq represents equation: a - b = q (lhs=rhs)'
   condeqs.append(stub('a-b=q') << Meq.Condeq(diff_ab, q, qhelp=qhelp))
   cc.append(condeqs[-1])

   solver = stub('solver') << Meq.Solver(children=condeqs,
                                         solvable=stub.search(tags='solvable'),
                                         qviewer=[True,'Record Browser'])

   # The solver should be executed first (otherwise the displayed parameter values are
   # not the final ones). So it must be the first child of the bundle:
   cc.insert(0, solver)

   return QRU.on_exit (ns, rider, cc, node_help=True,
                       show_recurse=solver,
                       parentclass='ReqSeq', result_index=0)



#================================================================================
# flagging_... 
#================================================================================

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
  
def flagging_simple (ns, rider):
   """
   Demonstration of simple flagging.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ZeroFlagger()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.MergeFlags()</A> 

   A zero-criterion (zerocrit) is calculated
   by a little subtree. This calculates the abs(diff) from the mean of the
   input, and then subtracts 'nsigma' times its stddev.


   The ZeroFlagger(oper=GE) flags all domain cells whose zcrit value is >= 0.
   Other behaviour can be specified with oper=LE or GT or LT.
   The MergeFlags node merges the new flags with the original flags of the input.
   """
   stub = QRU.on_entry(ns, rider, flagging_simple)
   cc = []

   cc.append(stub('input') << Meq.Exp(ET.twig(ns, QRU.getopt(globals(), 'opt_flagging_twig',rider))))
   cc.append(stub('mean') << Meq.Mean(cc[0]))
   cc.append(stub('stddev') << Meq.StdDev(cc[0]))
   stddev = cc[-1]
   dev = stub('dev') << Meq.Subtract(cc[0],cc[1])

   qhelp = """The absolute deviation (per cell) from the mean over the domain."""
   cc.append(stub('absdev') << Meq.Abs(dev, qhelp=qhelp))
   absdev = cc[-1]
   
   nsigma = QRU.getopt(globals(), 'opt_flagging_nsigma',rider)
   cc.append(stub('abscrit') << Meq.Multiply(nsigma,stddev))

   qhelp ="""The zero-criterion is the absolute deviation from the mean,
   minus nsigma (="""+str(nsigma)+""")* the stddev w.r.t. the mean.
   This will be GE zero for those cells whose value deviates more
   than nsigma*stddev from the mean over the domain."""
   cc.append(stub('zerocrit') << Meq.Subtract(absdev, cc[-1], qhelp=qhelp))

   cc.append(stub('flag') << Meq.ZeroFlagger(cc[-1], oper='GE'))
   cc.append(stub('merge') << Meq.MergeFlags(cc[0], cc[-1]))

   return QRU.on_exit (ns, rider, cc, node_help=True)


#--------------------------------------------------------------------------------

#================================================================================
# compounder_... 
#================================================================================

def compounder (ns, rider):
   """
   The compounder implements an implicit function.
   The first child should give the grid points and the second child should give the higher
   dimensional function. 
   
   <li> <A href='http://www.astron.nl/meqwiki/MeqCompounder'>Meq.Compounder(common_axes=.., node=..)</A> 

   The extra_axes argument should be a MeqComposer that bundles the extra (coordinate) children,
   described by the common_axes argument (e.g. [hiid('L'),hiid('M')].                  
   """
   stub = QRU.on_entry(ns, rider, compounder)
   cc = []
   override = opt_alltopics
   if override or opt_compounder_simple:
      cc.append(compounder_simple (ns, rider))
   if override or opt_compounder_advanced:
      cc.append(compounder_advanced (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------
  
def compounder_simple (ns, rider):
   """

   <li> <A href='http://www.astron.nl/meqwiki/MeqCompounder'>Meq.Compounder(common_axes=.., node=..)</A> 

   Demonstration of a 'grid' of compounders, which sample a grid of points (L,M)
   of a 2D gaussian input twig (subtree): 'gaussian_LM' -> exp(-(L**2+M**2)).
   Execute with a 2D (f,t) domain.
   The result of each compounder is a constant, with values that decrease with
   the distance to the origin.

   Expected values v(L,M) are (compare with the plot):
   <li> v(0,0) = 1.0
   <li> v(1,1) = 0.1353
   <li> v(2,2) = 0.0036
   <li> v(0,1) = v(1,0) = 0.3678
   <li> v(0,2) = v(2,0) = 0.0183
   <li> v(2,1) = v(1,2) = 0.0067

   <remark>
   Try executing with a 4D domain....
   </remark>
   """
   stub = QRU.on_entry(ns, rider, compounder_simple)

   twigspec = 'gaussian_LM'
   twig_LM = ET.twig(ns,twigspec)
   common_axes = [hiid('L'),hiid('M')]
   LL = []
   ll = []
   for L in [0,1,2]:
      ll.append(L)
      LL.append(stub(L=L) << L)
   MM = []
   mm = []
   for M in [0,1,2]:
      mm.append(M)
      MM.append(stub(M=M) << M)
   xx = []
   yy = []
   zz = []
   for i,L in enumerate(LL):
      for j,M in enumerate(MM):
         xx.append(L)
         yy.append(M)
         extra_axes = stub('extra_axes')(i)(j) << Meq.Composer(L,M)
         qhelp = 'This compounder samples the function at point (L,M)=('+str(ll[i])+','+str(mm[j])+').'
         zz.append(stub('compounder')(i)(j) << Meq.Compounder(extra_axes, twig_LM,
                                                              qhelp=qhelp,
                                                              qviewer=[True, 'Record Browser'],
                                                              common_axes=common_axes))

   # Bundle the compounders, to provide them with a request: 
   cs = stub('compounders') << Meq.Composer(children=zz, qbookmark=False)
   
   qhelp = """The points represent the values of the LM-function
   at the compounder sample points (L,M)"""
   pynode = PNP.pynode_Plot(ns, xx+yy+zz, 'XXYYZZ',
                            title='results of grid (L,M) of compounders',
                            qhelp=qhelp,
                            zlabel='z ='+twigspec,
                            xlabel='L', ylabel='M') 

   return QRU.on_exit (ns, rider,
                       nodes=[cs,zz[1],pynode,twig_LM],
                       node_help=True)

#--------------------------------------------------------------------------------
  
def compounder_advanced (ns, rider):
   """

   <li> <A href='http://www.astron.nl/meqwiki/MeqCompounder'>Meq.Compounder(common_axes=.., node=..)</A> 

   Explore the behaviour of the compounder if the function is not
   sampled at a point (L,M) but over a sampling-domain of finite
   size. This is done by using MeqGrid nodes rather than MeqConstant
   nodes for the 'extra_axes' L and M.

   <remark>
   The conclusion is that executing for different LM-domains
   does not seem to make any difference, so obviously the finite size
   of the domain is not used: the LM-function is just sampled at a
   single point (L,M), which may be the centre point of the domain, or
   its average L,M coordinates. Is this the behaviour we want...?
   </remark>
   """
   stub = QRU.on_entry(ns, rider, compounder_advanced)

   twigspec = 'gaussian_LM'
   twig_LM = ET.twig(ns,twigspec)
   common_axes = [hiid('L'),hiid('M')]
   zz = []

   l = 0
   m = 1
   L = ns << l
   M = ns << m
   extra_axes = stub('extra_axes')(l)(m) << Meq.Composer(L,M)
   qhelp = 'This compounder samples the function at point (L,M)=('+str(l)+','+str(m)+').'
   zz.append(stub('compounder')(l)(m) << Meq.Compounder(extra_axes, twig_LM,
                                                        qhelp=qhelp,
                                                        common_axes=common_axes))
   axes = 'GridLM'
   L = ET.twig(ns,'L')
   M = ET.twig(ns,'M')
   extra_axes = stub('extra_axes')(axes) << Meq.Composer(L,M)
   qhelp = 'This compounder samples the function at MeqGrids L and M.'
   zz.append(stub('compounder')(axes) << Meq.Compounder(extra_axes, twig_LM,
                                                            qhelp=qhelp,
                                                            common_axes=common_axes))
   axes = 'GridL'
   m = 1
   L = ET.twig(ns,'L')
   M = ns << m
   extra_axes = stub('extra_axes')(axes)(m) << Meq.Composer(L,M)
   qhelp = 'This compounder samples the function at MeqGridL and M='+str(m)+'.'
   zz.append(stub('compounder')(axes)(m) << Meq.Compounder(extra_axes, twig_LM,
                                                           qhelp=qhelp,
                                                           common_axes=common_axes))

   axes = 'GridM'
   l = 1
   M = ET.twig(ns,'M')
   L = ns << l
   extra_axes = stub('extra_axes')(l)(axes) << Meq.Composer(L,M)
   qhelp = 'This compounder samples the function at MeqGridM and L='+str(l)+'.'
   zz.append(stub('compounder')(l)(axes) << Meq.Compounder(extra_axes, twig_LM,
                                                           qhelp=qhelp,
                                                           common_axes=common_axes))

   # Bundle the compounders, to provide them with a request: 
   cs = stub('compounders') << Meq.Composer(children=zz, qbookmark=False)
   
   return QRU.on_exit (ns, rider,
                       nodes=[cs,zz[0],zz[1],zz[2],zz[3],twig_LM],
                       node_help=True)


#--------------------------------------------------------------------------------

#================================================================================
# resampling_... 
#================================================================================

def resampling (ns, rider):
   """
   The number of cells in the domain may be changed locally:

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ModRes(c, num_cells=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Resampler(c, mode=1)</A> 
   
   ...
   <li> The MeqModRes(child, num_cells=[2,3]) node changes the number
   of cells in the domain of the REQUEST that it issues to its child.
   Thus, the entire subtree below the child is evaluated with this
   resolution. 
   <li> The MeqResample(child, mode=1) resamples the domain of the Result
   it gets from its child, to match the resolution of the Request that
   it received itself. (So it does nothing if the domains already match,
   i.e. if there is no MeqModRes upstream).
   <li> The MeqResample(child, mode=2) resamples in a different way...
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
   cc = []

   twig = ET.twig (ns, QRU.getopt(globals(), 'opt_resampling_MeqModRes_twig',rider))
   num_cells = [QRU.getopt(globals(), 'opt_resampling_MeqModRes_num_time',rider),
                QRU.getopt(globals(), 'opt_resampling_MeqModRes_num_freq',rider)]
   mode = QRU.getopt(globals(), 'opt_resampling_MeqResampler_mode',rider)
   cc.append(resampling_experiment (ns, rider, twig=twig,
                                    num_cells=num_cells, mode=mode))

   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def resampling_experiment (ns, rider, twig=None,
                           num_cells=[2,3], mode=1):
   """
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ModRes(c, num_cells=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Resampler(c, mode=..)</A> 

   The experiment shows the difference between the twig, and after
   a sequence of ModRes and Resample. Obviously, the differences are
   smaller when the twig is smoother and/or when num_cells is larger.
   You may experiment with different twigs, MeqModRes num_cells or
   MeqResampler mode, by modifying the TDLOptions and recompiling and
   re-executing.
   """
   stub = QRU.on_entry(ns, rider, resampling_experiment, stubname='resexp')
   cc = [twig]

   qhelp = """This copy of the input is needed for display, since the
   resolution of the request changes."""
   cc.append(stub('original') << Meq.Identity(twig, qhelp=qhelp))

   cc.append(stub('ModRes')(num_cells) << Meq.ModRes(twig, num_cells=num_cells))
   cc.append(stub('Resampler')(mode=mode) << Meq.Resampler(cc[-1], mode=mode))
   cc.insert(0, stub('diff') << Meq.Subtract(cc[-1],cc[1]))
   return QRU.on_exit (ns, rider, cc, parentclass='ReqSeq',
                       node_help=True, show_recurse=True)




#================================================================================
# axisreduction_... 
#================================================================================

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

def axisreduction_single (ns, rider):
   """
   Demonstration of basic axisreduction, on one child (c), with a single vellset.
   The reduction is done along all available axes (the default), producing a
   single-number Result.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Nelements(c)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sum(c)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Mean</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Product</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.StdDev(c)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Rms(c)</A> (same as StdDev) 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Min(c)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Max(c)</A> 

   """
   stub = QRU.on_entry(ns, rider, axisreduction_single)
   twig_name = 'f'
   twig = ET.twig(ns, twig_name)
   cc = [twig]
   # NB: Left out: 'Rms', which is the same as 'StdDev'...
   for q in ['Nelements','Sum','Mean','Product','StdDev','Min','Max']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def axisreduction_multiple (ns, rider):
   """
   Demonstration of more advanced axis reduction, with Results that may contain
   multiple vellsets.
   <remark>
   NB: Axisreduction nodes ONLY work with a single child.
   </remark>
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
      qhelp = help[twig_name]
      cc.append(stub(democlass)(twig_name) << getattr(Meq,democlass)(twig, qhelp=qhelp))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def axisreduction_axes (ns, rider):
   """
   Demonstration of more advanced axisreduction, along a subset of the available axes.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sum(c, reduction_axes=..)</A> 

   If one or more reduction_axes are specified, the reduction is only
   along the specified axes (e.g. reduction_axes=['time'] reduces only
   the time-axis to length 1. The default is all available axes, of course. 
   The Result of a reduction node will be expanded when needed to fit a
   domain of the original size, in which multiple cells have the same value.
   This demonstration uses only one of the relevant MeqNodes (MeqSum).
   """
   stub = QRU.on_entry(ns, rider, axisreduction_axes)

   twig_name = 'ft'
   twig = ET.twig(ns, twig_name)
   ntwig = stub('nelem') << Meq.NElements(twig)
   cc = [twig,ntwig]

   democlass = 'Sum'
   help = democlass+' over the cells of '

   qhelp =help+'no reduction_axes specified, assume all'
   cc.append(stub('all_axes') << getattr(Meq,democlass)(twig, qhelp=qhelp))

   qhelp = help+'the time-axis is reduced to length 1.'
   cc.append(stub('time_axis') << getattr(Meq,democlass)(twig, qhelp=qhelp,
                                                         reduction_axes=['time']))
   qhelp = help+'the freq-axis is reduced to length 1.'
   cc.append(stub('freq_axis') << getattr(Meq,democlass)(twig, qhelp=qhelp,
                                                         reduction_axes=['freq']))
   qhelp = help+'both the freq and time axes are reduced.'
   cc.append(stub('timefreq') << getattr(Meq,democlass)(twig, qhelp=qhelp,
                                                        reduction_axes=['freq','time']))
   return QRU.on_exit (ns, rider, cc)




#================================================================================
# tensor_... 
#================================================================================

def tensor (ns, rider):
   """
   Many node classes can handle Results with multiple vellsets.
   They are somewhat clumsily (and wrongly) called 'tensor nodes'.
   The advantages of multiple vellsets are:
   <li> the trees are more compact, so easier to define and read
   <li> efficiency: execution can be optimized internally
   <li> they allow special nodes that do matrix/tensor operations
   <li> etc, etc
   """
   stub = QRU.on_entry(ns, rider, tensor)
   cc = []
   override = opt_alltopics
   if override or opt_tensor_manipulation:
      cc.append(tensor_manipulation (ns, rider)) 
   if override or opt_tensor_matrix:
      cc.append(tensor_matrix (ns, rider))
   if override or opt_tensor_matrix22:
      cc.append(tensor_matrix22 (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')


#--------------------------------------------------------------------------------

def tensor_manipulation (ns, rider):
   """
   Manipulation of 'tensor' nodes, i.e. nodes with multiple vellsets.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Composer(*cc)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Selector(c, index=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Paster(children=[c0,c1], index=..)</A> 

   """
   stub = QRU.on_entry(ns, rider, tensor_manipulation)
   cc = []

   c0 = ET.twig(ns,'f', nodename='c0')
   c1 = ET.twig(ns,'t', nodename='c1')
   c2 = ET.twig(ns,'ft', nodename='c2')
   elements = [c0,c1,c2]

   qhelp = """Make a tensor node by combining the vellsets in the
   Results of its children into a Result with multiple vellsets
   in the new node."""
   cc.append(stub('tensor') << Meq.Composer(children=elements, qhelp=qhelp))

   for index in [0,1,2]:
      qhelp = """Select the specified (index) vellset in its child
      for a new node with a single vellset in its Result"""
      cc.append(stub('Selector')(index) << Meq.Selector(cc[0], index=index,
                                                        qhelp=qhelp))

   if False:
      # Problem: Gives an error (list indix not supported?)
      index = [0,2]
      qhelp = """Select the specified (index) vellsets in its child
      for a new node with this subset of vellsets in its Result"""
      cc.append(stub('Selector')(index) << Meq.Selector(cc[0], index=index,
                                                        qhelp=qhelp))

   if True:
      # Problem: Does not work... (nr of vells stays the same). But index is the correct keyword...
      c1 = ET.twig(ns,'prod_f2t2')
      index = 1
      qhelp = """Make a new node, in which the vellset from the
      second child (c1) is pasted at the specified (index) position
      among the vellsets of its first child (c0)"""
      cc.append(stub('Paster')(index) << Meq.Paster(children=[cc[0],c1],
                                                    index=index, qhelp=qhelp))

   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def tensor_matrix (ns, rider):
   """
   Nodes with multiple vellsets can be treated as matrices.
   There are some specialised nodes that do matrix operations.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.MatrixMultiply(*mm)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Transpose(m)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ConjTranspose(m)</A> 
   
   <remark>
   For the moment, only 2x2 matrices can be inverted, since
   this was easiest to program by hand (see MatrixInvert22).
   A more general inversion node will be implemted later.
   </remark>
   """
   stub = QRU.on_entry(ns, rider, tensor_matrix)
   cc = []

   qhelp = """Make a tensor node with a 2x3 array of vellsets.
   This can be treated as a 2x3 matrix. Note the use of
   constants as children, for easier inspection and verification."""
   cc.append(stub('2x3') << Meq.Composer(children=range(6),
                                         dims=[2,3], qhelp=qhelp))

   qhelp = """Make the 3x2 transpose of the given 2x3 matrix."""
   cc.append(stub('3x2') << Meq.Transpose(cc[0], qhelp=qhelp)) 

   qhelp = """Multply the original 2x3 matrix with its 3x2 transpose.
   This produces a 2x2 matrix."""
   cc.append(stub('2x2') << Meq.MatrixMultiply(cc[0],cc[1], qhelp=qhelp))

   qhelp = """Multiply the 3x2 transpose with the original 2x3 matrix.
   This produces a 3x3 matrix."""
   cc.append(stub('3x3') << Meq.MatrixMultiply(cc[1],cc[0], qhelp=qhelp))
   
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def tensor_matrix22 (ns, rider):
   """
   Because the 2x2 cohaerency matrix and the 2x2 Jones matrix play an important
   role in the radio-astronomical Measurement Equation (M.E.), there are a few
   specialized nodes that deal with 2x2 matrices.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Matrix22(m0,m1,m2,m3)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.MatrixInvert22(m)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ConjTranspose(m)</A> 

   """
   stub = QRU.on_entry(ns, rider, tensor_matrix22)
   elements = [ET.twig(ns,'cx_ft'),0,0,ET.twig(ns,'cx_tf')]
   cc = []

   qhelp = """Make a complex 2x2 diagonal matrix."""
   # NB: Matrix22(children=elements) gives an error.... 
   # cc.append(stub('m22') << Meq.Matrix22(*elements))          # takes 4 arguments ....!
   cc.append(stub('m22') << Meq.Composer(children=elements,
                                         dims=[2,2], qhelp=qhelp))

   qhelp = """Invert the given 2x2 matrix, cell-by-cell"""
   cc.append(stub('inv22') << Meq.MatrixInvert22(cc[0], qhelp=qhelp))

   qhelp = """Multply the matrix with its inverse.
   The result should be a unit matrix (cell-by-cell)."""
   cc.append(stub('m22xinv22') << Meq.MatrixMultiply(cc[0],cc[1],
                                                     qhelp=qhelp))

   qhelp = """Conjugate Transpose the given matrix"""
   cc.append(stub('hermitian') << Meq.ConjTranspose(cc[0], qhelp=qhelp))

   return QRU.on_exit (ns, rider, cc)



#================================================================================
# leaves_...
#================================================================================


def leaves (ns, rider):
   """
   Leaf nodes have no children. They often (but not always) have access to
   some external source of information (like a file) to satisfy a request. 
   """
   stub = QRU.on_entry(ns, rider, leaves)
   cc = []
   override = opt_alltopics
   
   cc.append(leaves_constant (ns, rider))
   cc.append(leaves_parm (ns, rider))
   cc.append(leaves_gridsFTLM (ns, rider))
   cc.append(leaves_gridsXYZetc (ns, rider))
   cc.append(leaves_noise (ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def leaves_constant (ns, rider):
   """
   A Constant node may represent a real or a complex constant.
   It can also be a tensor node, i.e. containing an N-dimensional array of vellsets.
   There are various ways to define one.

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Constant(value(s))</A> 

   """
   stub = QRU.on_entry(ns, rider, leaves_constant)
   cc = []
   
   v = 0.5
   cc.append(ns << v)
   cc[-1].initrec().qhelp = 'syntax: node = ns << '+str(v)

   v += 1
   cc.append(ns.NoDeNaMe << v)
   cc[-1].initrec().qhelp = 'syntax: node = ns.NoDeNaMe << '+str(v)

   v += 1
   cc.append(stub('real') << v)
   cc[-1].initrec().qhelp = """syntax: node = stub('real') << """+str(v)+""", in which:
   stub = """+str(stub)+""" is an uninitialised 'node-stub'"""

   v = complex(1,2)
   cc.append(stub('complex') << v)
   cc[-1].initrec().qhelp = "syntax: node = stub('complex') << "+str(v)

   v = [1.5, -2.5, 3.5, -467]
   cc.append(stub('tensor4') << Meq.Constant(v))
   cc[-1].initrec().qhelp = "syntax: node = stub('tensor4') << Meq.Constant("+str(v)+")"

   cc.append(stub('tensor22') << Meq.Constant(v, dims=[2,2]))
   cc[-1].initrec().qhelp = "syntax: node = stub('tensor22') << Meq.Constant("+str(v)+", dims=[2,2])"

   v[2] = complex(3,5)
   cc.append(stub('mixed') << Meq.Constant(v))
   cc[-1].initrec().qhelp = "syntax: node = stub('mixed') << Meq.Constant("+str(v)+")"

   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def leaves_parm (ns, rider):
   """
   MeqParm nodes represent M.E. parameters, which may be solved for.
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Parm(default)</A> 

   """
   stub = QRU.on_entry(ns, rider, leaves_parm)
   cc = []
   cc.append(stub('basic') << Meq.Parm(2.5))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

def leaves_noise (ns, rider):
   """
   Noise nodes generate noisy cell values. The arguments are passed as
   keyword arguments in the node constructor (or as children?)

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.GaussNoise(stddev=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.RandomNoise(lower=.., upper=..)</A> 

   """
   stub = QRU.on_entry(ns, rider, leaves_noise)
   cc = []
   cc.append(stub('stddev') << Meq.GaussNoise(stddev=2.0))

   # NB: Mean does not work...
   cc.append(stub('mean') << Meq.GaussNoise(mean=-10.0, stddev=2.0))

   if False:
      # NB: The server crashes on this one
      cc.append(stub('random') << Meq.RandomNoise(lower=-2.0, upper=4.0))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def leaves_gridsFTLM (ns, rider):
   """
   Grid nodes fill in the cells of the requested domain with the
   values of the specified axis (time, freq, L, M, X, Y, Z, etc).
   They are created by:  ns[nodename] << Meq.Grid(axis='M')

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Freq()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Time()</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Grid(axis='M')</A> 

   The two default axes (time and freq) also have dedicated Grid nodes,
   called MeqTime and MeqFreq, e.g.:  ns[nodename] << Meq.Freq()

   <tip>
   Check also the Forest State record. Note that its axis_map and
   its axis_list have default axes [time,freq,L,M], but that extra
   axes are added to them as soon as MeqGrid node with a new axis
   (name) has been defined.   
   </tip>

   <tip>
   Try a 3D or 4D request domain (e.g. '3D_ftLM'), and see that the Result Plotter
   sprouts a few extra knobs to allow you to plot various cross-sections of the ND array.
   </tip>
   """
   stub = QRU.on_entry(ns, rider, leaves_gridsFTLM)
   cc = []

   for q in ['Freq','Time']:
      cc.append(stub(q) << getattr(Meq,q)())

   for axis in ['L','M']:
      cc.append(stub(axis) << Meq.Grid(axis=axis))

   cc.append(stub('f+t') << Meq.Add(cc[0],cc[1]))
   cc.append(stub('L+M') << Meq.Add(cc[2],cc[3]))
   cc.append(stub('f+t+L+M') << Meq.Add(cc[0],cc[1],cc[2],cc[3]))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def leaves_gridsXYZetc (ns, rider):
   """
   Grid nodes fill in the cells of the requested domain with the
   values of the specified axis (time, freq, L, M, X, Y, Z, etc).
   They are created by:  ns[nodename] << Meq.Grid(axis='M')

   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Grid(axis='M')</A> 

   The two default axes (time and freq) also have dedicated Grid nodes,
   called MeqTime and MeqFreq, e.g.:  ns[nodename] << Meq.Freq()

   NB: Check also the Forest State record. Note that its axis_map and
   its axis_list have default axes [time,freq,L,M], but that extra
   axes are added to them as soon as MeqGrid node with a new axis
   (name) has been defined.

   <warning>
   At this moment (aug 2008), the system only accepts 5D request domains.
   So, request domains including X or Z will cause problems.
   (Y is the 5th in the axis-map, after time, freq, L, M (see forest state record)
   </warning>
   """
   stub = QRU.on_entry(ns, rider, leaves_gridsXYZetc)
   cc = []
   for axis in ['X','Y','Z']:
      cc.append(stub(axis) << Meq.Grid(axis=axis))
   cc.append(stub('X+Y+Z') << Meq.Add(cc[0],cc[1],cc[2]))
   cc.append(stub('f+t+Y') << Meq.Add(ET.twig(ns,'t'), ET.twig(ns,'f'), cc[1]))
   return QRU.on_exit (ns, rider, cc)


#--------------------------------------------------------------------------------

#================================================================================
# unops_... (Unary operations)
#================================================================================

def FITS (ns, rider):
   """
   There are various nodes to interact with FITS files.

   <li> <A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSReader(filename=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSWriter(filename=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSImage(filename=.., cutoff=.., mode=..)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSSpigot(filename=..)</A> 

   """
   stub = QRU.on_entry(ns, rider, FITS)
   cc = [] 
   override = opt_alltopics
   if override or opt_FITS_RW:
      cc.append(FITS_RW(ns, rider))
   if override or opt_FITSImage:
      cc.append(FITSImage(ns, rider))
   if override or opt_FITSImage_mode2:
      cc.append(FITSImage_mode2(ns, rider))
   return QRU.on_exit (ns, rider, cc, mode='group')

#----------------------------------------------------------------------------------------------

def FITS_RW (ns, rider):
   """
   The first(!) VellSet of a MeqNode Result may be written to a named
   FITS file. Its Cells is also written. 
   
   <li><A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSWriter(filename=..)</A>
   <li><A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSReadr(filename=..)</A>

   In the following, we first write the vellset in the result of a MeqNode to the
   file 'FITS_RW.fits'. We then read it again, and compare the input and output.

   <error>
   Something goes wrong in the writing and reading of the coordinates (time,freq, etc).
   In the MeqFitsReader node state, the result cells has a (slightly) different
   grid than the cells of the input request.
   Predictably, the difference between input and output results in an error.
   </error>

   <tip>
   Experiment with request domains with different dimensions (e.g. L,M),
   and different nrs of cells.
   </tip>
   """
   stub = QRU.on_entry(ns, rider, FITS_RW)
   cc = []
   cc.append(ET.twig(ns, 'f+t+L+M'))
   # filename = '!FITS_RW.fits'            # The exclamation mark is to allow rewrite....
   filename = 'FITS_RW.fits'  
   cc.append(stub('FITSWriter') << Meq.FITSWriter(cc[-1], filename=filename))
   cc.append(stub('FITSReader') << Meq.FITSReader(filename=filename,
                                                  qviewer=[True,'Record Browser']))
   qhelp = 'Make the result cells equal to the request cells'
   if True: 
      # Diff still gives an error...
      cc.append(stub('ReSampler')(mode=1) << Meq.Resampler(cc[-1], mode=1, qhelp=qhelp))
   else:
      # Diff is OK, but has a constant offset....
      cc.append(stub('ReSampler')(mode=2) << Meq.Resampler(cc[-1], mode=2, qhelp=qhelp))
   qhelp = 'Make sure that the writer node is executed before the reader node.'
   reqseq = stub('ReqSeq') << Meq.ReqSeq(cc[-2],cc[-1], result_index=1, qhelp=qhelp)
   qhelp = 'The difference between the input (twig) and the result read from FITS:' 
   cc.append(stub('diff') << Meq.Subtract(reqseq,cc[0], qhelp=qhelp))
   return QRU.on_exit (ns, rider, cc)



#----------------------------------------------------------------------------------------------

def FITSImage (ns, rider):
   """
   The <A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSImage(filename=.., cutoff=..)</A>
   node is used to read in a sky image in terms of fluxes (IQUV) and the phase center RA,DEC.
   (NB: If your image does not contain all 4 Stokes planes, you can add a degenerate axes.
   See the meqwiki via the above link).
   This node was developed for use with the MeqUVBrick, but can also be used (with some care)
   for other purposes. See also FITSImage_mode2().

   The 'cutoff' is the cutoff flux (value between 0 and 1), used to minimise the size of the image.
   (This is important for the UVBrick operation).
   For example, a cutoff of 0.2 will imply that only the rectangular area containing the 20% 
   pixels with highest flux (including the peak) will be selected.  

   <li>If <b>mode=1</b>: The result is a 'sixpack', i.e. it contains 6
   vellsets with elements RA,DEC,I,Q,U,V. In this demonstration, it
   has been split into 6 nodes, using MeqSelector.

   <remark>
   Note how the (l,m) coordinate ranges, and the number of (l,m)
   pixels of the results are affected by the cutoff value.  What about
   the nr of cells?
   </remark>

   <warning>
   The domain (nr of dimensions and nr of cells) of the
   result of MeqFITSImage is determined by the FITS image, NOT by the
   request (check this in its state record). If not handles correctly,
   this will cause problems downstream.
   </warning>

   """
   stub = QRU.on_entry(ns, rider, FITSImage, stubname='FITSImage')
   cc = []
   filename = 'Sun.fits'
   cutoff = QRU.getopt(globals(),'opt_FITSImage_cutoff',rider)
   qhelp = 'Default (assume mode=1)'
   sixpack = stub('sixpack') << Meq.FITSImage(filename=filename,
                                              qhelp=qhelp,
                                              qviewer=[True,'Record Browser'],
                                              cutoff=cutoff)
   cc.append(sixpack)
   cc.append(sixpack('RA') << Meq.Selector(sixpack, index=0))
   cc.append(sixpack('DEC') << Meq.Selector(sixpack, index=1))
   cc.append(sixpack('StokesI') << Meq.Selector(sixpack, index=2))
   cc.append(sixpack('StokesQ') << Meq.Selector(sixpack, index=3))
   cc.append(sixpack('StokesU') << Meq.Selector(sixpack, index=4))
   cc.append(sixpack('StokesV') << Meq.Selector(sixpack, index=5))
   return QRU.on_exit (ns, rider, cc)


#----------------------------------------------------------------------------------------------

def FITSImage_mode2 (ns, rider):
   """
   The <A href='http://www.astron.nl/meqwiki/MeqImage'>Meq.FITSImage(filename=.., cutoff=.., mode=2)</A>
   node is used to read in a sky image in terms of fluxes (IQUV) and the phase center RA,DEC.
   This node was developed for use with the MeqUVBrick (mode=1), but can also be used (with some care)
   for other purposes. See also FITS_MeqImage().

   The 'cutoff' is the cutoff flux (value between 0 and 1), used to reduce the size of the image.
   For example, a cutoff of 0.2 will imply that only the rectangular area containing 20% of the total
   pixels with highest flux (including the peak) will be selected.  

   <li>If <b>mode=2</b>: the result has a single vellset (StokesI). 

   <remark>
   Note how the (l,m) coordinate ranges, and the number of (l,m)
   pixels of the results are affected by the cutoff value.  What about
   the nr of cells?
   </remark>

   <warning>
   The domain (nr of dimensions and nr of cells) of the
   result of MeqFITSImage is determined by the FITS image, NOT by the
   request (check this in its state record). If not handles correctly,
   this will cause problems downstream.
   </warning>

   """
   stub = QRU.on_entry(ns, rider, FITSImage_mode2, stubname='FITSIm(2)')
   cc = []
   filename = 'Sun.fits'

   cutoff = QRU.getopt(globals(),'opt_FITSImage_cutoff_mode2',rider)
   mode = QRU.getopt(globals(),'opt_FITSImage_resampler_mode',rider)
   
   cc.append(stub('StokesI')('mode=2') << Meq.FITSImage(filename=filename,
                                                        qviewer=[True,'Record Browser'],
                                                        cutoff=cutoff, mode=2))
   qhelp = 'Resample the result to the request domain/cells'
   cc.append(stub('Resampler') << Meq.Resampler(cc[-1], mode=mode,
                                                qviewer=[True,'Record Browser'],
                                                qhelp=qhelp))
   
   # Make sure that the Resampler is executed last:
   return QRU.on_exit (ns, rider, cc, parentclass='ReqSeq')




#================================================================================
# unops_... (Unary operations)
#================================================================================


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
   twig = ET.twig (ns, QRU.getopt(globals(), 'opt_unops_twig',rider),
                   help='single child for unary math nodes', 
                   nodename='unops_child')
   cc = [] 
   cc.append(unops_elementary (ns, rider, twig))
   cc.append(unops_goniometric (ns, rider, twig))
   cc.append(unops_invgoniometric (ns, rider, twig))
   cc.append(unops_hyperbolic (ns, rider, twig))
   cc.append(unops_power (ns, rider, twig))
   cc.append(unops_misc (ns, rider, twig))
   cc.append(unops_complex (ns, rider, twig))
   return QRU.on_exit (ns, rider, cc, mode='group')

#--------------------------------------------------------------------------------

def unops_elementary (ns, rider, twig=None):
   """
   Elementary unary math operations (on c, a single child node):
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Negate(c)</A> -> (-c)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Invert(c)</A> -> (1/c)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Exp(c)</A> 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Log(c)</A> -> (e-log) 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sqrt(c)</A> 
   """
   stub = QRU.on_entry(ns, rider, unops_elementary)
   cc = [twig]
   for q in ['Negate','Invert','Exp','Log','Sqrt']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
   # NB: add 10log subtree...
   return QRU.on_exit (ns, rider, cc)

#-----------------------------------------#--------------------------------------------------------------------------------

def unops_goniometric (ns, rider, twig=None):
   """
   (Tri-)Goniometric functions turn an angle (c, rad) into a fraction:
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sin(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Cos(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Tan(c)</A>
   """
   stub = QRU.on_entry(ns, rider, unops_goniometric)
   cc = [twig]

   for q in ['Sin','Cos','Tan']:
      cc.append(stub(q+'(c)') << getattr(Meq,q)(twig))

   s2 = stub('s2') << Meq.Sqr(cc[1])
   c2 = stub('c2') << Meq.Sqr(cc[2])
   qhelp = 'Cos(c)**2 + Sin(c)**2 = 1'
   cc.append(stub('(sin**2+cos**2)') << Meq.Add(s2,c2, qhelp=qhelp))

   return QRU.on_exit (ns, rider, cc)

#-----------------------------------------#--------------------------------------------------------------------------------

def unops_invgoniometric (ns, rider, twig=None):
   """
   The inverses (tri-)Goniometric functions turn a fraction (c) into
   an angle (rad). The abs inputs of Asin and Acos must be smaller than one, of course. 
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Asin(c)</A> -> rad
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Acos(c)</A> -> rad
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Atan(c)</A> -> rad

   <tip>
   Applying first the function and then its inverse should yield the original input.
   </tip>
   """
   stub = QRU.on_entry(ns, rider, unops_invgoniometric)
   cc = [twig]

   for q in ['Asin','Acos','Atan']:
      cc.append(stub(q+'(c)') << getattr(Meq,q)(twig))

   qhelp = 'Applying a function to its inverse should yield the input'
   sin = stub('Sin(c)') << Meq.Sin(twig)
   cos = stub('Cos(c)') << Meq.Cos(twig)
   tan = stub('Tan(c)') << Meq.Tan(twig)
   asinsin = stub('Asin(Sin(c))') << Meq.Asin(sin)
   acoscos = stub('Acos(Cos(c))') << Meq.Acos(cos)
   atantan = stub('Atan(Tan(c))') << Meq.Atan(tan)
   cc.append(stub('Asin(Sin(c))-c') << Meq.Subtract(children=[asinsin,twig], qhelp=qhelp))
   cc.append(stub('Acos(Cos(c))-c') << Meq.Subtract(children=[acoscos,twig], qhelp=qhelp))
   cc.append(stub('Atan(Tan(c))-c') << Meq.Subtract(children=[atantan,twig], qhelp=qhelp))


   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def unops_hyperbolic (ns, rider, twig=None):
   """
   Hyperbolic functions:
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sinh(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Cosh(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Tanh(c)</A>

   Note the demonstration: Cosh(x)**2 - Sinh(x)**2 = 1 
   """
   stub = QRU.on_entry(ns, rider, unops_hyperbolic)
   cc = [twig]
   for q in ['Sinh','Cosh','Tanh']:
      cc.append(stub(q+'(c)') << getattr(Meq,q)(twig))
      
   sh2 = stub('sinh**2') << Meq.Sqr(cc[1])
   ch2 = stub('cosh**2') << Meq.Sqr(cc[2])
   qhelp = 'Demonstrates: Cosh(c)**2 - Sinh(c)**2 = 1'
   cc.append(stub('(cosh**2-sinh**2)') << Meq.Subtract(ch2,sh2, qhelp=qhelp))

   return QRU.on_exit (ns, rider, cc, node_help=True)

#--------------------------------------------------------------------------------

def unops_complex (ns, rider, twig=None):
   """
   Complex unary math operations on a (usually) complex child (c):
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Abs(c)</A> -> real
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Norm(c)</A> -> same as Abs
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Arg(c)</A> -> real (rad)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Real(c)</A> -> real
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Imag(c)</A> -> real
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Conj(c)</A> conj(a+jb) -> a-jb
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Exp(c)</A>
   exp(a+jb) -> exp(a)*exp(jb) = exp(a)*(cos(b)+jsin(b))
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Log(c)</A>
   ln(r*exp(js)) -> ln(r) + j(s + 2kpi) (k = integer)  

   Most math node take complex children, of course, or produce complex results. 
   """
   stub = QRU.on_entry(ns, rider, unops_complex)
   twig = ET.twig(ns,'cx_ft')                # override input twig...
   cc = [twig]
   for q in ['Abs','Arg','Real','Imag','Conj','Exp','Log']:
      cc.append(stub(q+'(c)') << getattr(Meq,q)(twig))
   return QRU.on_exit (ns, rider, cc)

#--------------------------------------------------------------------------------

def unops_power (ns, rider, twig=None):
   """
   Nodes that take some power of its child (c):
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Sqr(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow2(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow3(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow4(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow5(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow6(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow7(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow8(c)</A>
   """
   stub = QRU.on_entry(ns, rider, unops_power)
   cc = [twig]
   for q in ['Sqr','Pow2','Pow3','Pow4','Pow5','Pow6','Pow7','Pow8']:
      cc.append(stub(q) << getattr(Meq,q)(twig))
   return QRU.on_exit (ns, rider, cc, bookmark_bundle_help=False)

#--------------------------------------------------------------------------------

def unops_misc (ns, rider, twig=None):
   """
   Miscellaneous unary math operations.
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Ceil(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Floor(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Identity(c)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Stripper(c)</A>
   """
   stub = QRU.on_entry(ns, rider, unops_misc)
   cc = [twig]
   for q in ['Ceil','Floor','Identity']:
      cc.append(stub(q+'(c)') << getattr(Meq,q)(twig, qbookmark=True))

   cc.append(stub('Stripper(c)') << Meq.Stripper(twig, qviewer=[True, 'Record Browser']))

   return QRU.on_exit (ns, rider, cc, node_help=True)



#================================================================================
# binops
#================================================================================

def binops (ns, rider):
   """
   Binary math operations (two children, e.g. lhs,rhs).
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Subtract(lhs,rhs)</A> -> (lhs-rhs)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Divide(lhs,rhs)</A> -> (lhs/rhs)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Pow(lhs,rhs)</A> -> (lhs**rhs)
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.ToComplex(real,imag)</A> -> complex
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Polar(ampl,phase)</A> -> complex

   The operations are performed cell-by-cell.
   The following rules apply:
   <li> If the first child (left-hand-side, lhs) has a result with multiple vellsets
   ('tensor-node'), there are two possibilities: If the second child (rhs) is a
   'scalar node', its single vellset is applied to all the vellsets of lhs.
   <li> Otherwise, the Result of rhs must have the same number of vellsets as lhs,
   and the operation is performed between corresponding vellsets.
   <li> The final Result always has the same shape (number of vellsets) as lhs.

   The input children may be selected here, for experimentation.
   """
   stub = QRU.on_entry(ns, rider, binops, stubname='binops')
   lhs = ET.twig(ns, QRU.getopt(globals(), 'opt_binops_lhs',rider), nodename='lhs') 
   rhs = ET.twig(ns, QRU.getopt(globals(), 'opt_binops_rhs',rider), nodename='rhs') 
   cc = [lhs,rhs]
   for q in ['Subtract','Divide','Pow']:
      cc.append(stub(q+'(lhs,rhs)') << getattr(Meq,q)(lhs,rhs))
   cc.append(stub('ToComplex(r,i)') << Meq.ToComplex(lhs,rhs))
   cc.append(stub('Polar(a,p)') << Meq.Polar(lhs,rhs))
   # Problem: MeqMod() crashes the meqserver.... Needs integer children??
   return QRU.on_exit (ns, rider, cc, node_help=True)



#================================================================================
# multimath
#================================================================================

def multimath (ns, rider):
   """
   Math operations on an arbitrary number (one or more) of children (*cc).
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Add(*cc)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.Multiply(*cc)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.WSum(children=cc, weights=ww)</A>
   <li> <A href='http://www.astron.nl/meqwiki/AllNodes'>Meq.WMean(children=cc, weights=ww)</A>

   The operation is performed cell-by-cell.
   The following rules apply:
   <li> If the number of children is two, the same rules apply as for binary
   operations (see binops).
   <li> If the number of children is greater than two, the Results of all children
   must have the same shape (i.e. the same number of vellsets in their Results).
   <li> If the number of of children is one, its Result is just passed on.

   The number and type of children may be selected here, for experimentation.
   """
   stub = QRU.on_entry(ns, rider, multimath, stubname='multimath')
   cc = []

   # Make the child-related vectors (ignore the ones with opt=None):
   twigs = [ET.twig(ns,QRU.getopt(globals(), 'opt_multimath_twig1',rider))]
   weights = [1.0]
   if opt_multimath_twig2:
      twigs.append(ET.twig(ns,QRU.getopt(globals(), 'opt_multimath_twig2',rider)))
      weights.append(2.0)
   if opt_multimath_twig3:
      twigs.append(ET.twig(ns,QRU.getopt(globals(), 'opt_multimath_twig3',rider)))
      weights.append(3.0)

   # Attach the input twigs to the bundle, for inspection.
   cc.extend(twigs)

   # First the simple ones:
   for q in ['Add','Multiply']:
      cc.append(stub(q) << getattr(Meq,q)(*twigs))

   # Then the weighted ones:
   for q in ['WSum','WMean']:
      cc.append(stub(q) << getattr(Meq,q)(children=twigs,
                                          weights=weights, qhelp=True))

   return QRU.on_exit (ns, rider, cc)











#================================================================================
#================================================================================
#================================================================================
#================================================================================
# Standalone forest:
#================================================================================


def _define_forest (ns, **kwargs):
   """Definition of a 'forest' of one or more trees"""

   TDLRuntimeMenu(":")
   itsTDLRuntimeMenu = TDLRuntimeMenu("QR_MeqNodes runtime options:", QRU)
   TDLRuntimeMenu(":")

   global rootnodename
   rootnodename = 'QR_MeqNodes'                 # The name of the node to be executed...
   global rider                                 # used in tdl_jobs
   rider = QRU.create_rider(rootnodename)       # CollatedHelpRecord object

   # Make a 'how-to' help-node for the top bookmark:
   QRU.how_to_use_this_module (ns, rider, name='QR_MeqNodes',
                               topic='Overview of all available MeqNodes')

   # Execute the top-level function, and dispose of the resulting tree:
   QRU.on_exit (ns, rider,
                nodes=[QR_MeqNodes(ns, rider)],
                mode='group', finished=True)

   # Finished:
   return True
   


#--------------------------------------------------------------------------------

def _tdl_job_execute (mqs, parent):
   """Execute the tree, starting at the specified rootnode,
   with the ND request-domain (axes) specified in the
   TDLRuntimeOptions (see QuickRefUtils.py)"""
   return QRU._tdl_job_execute (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_sequence (mqs, parent):
   """Execute a sequence of requests""" 
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode=rootnodename)

def _tdl_job_execute_MS (mqs, parent):
   """Execute a Measurement Set (MS)""" 
   return QRU._tdl_job_execute_MS (mqs, parent, vdm_node='VisDataMux')

#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_hardcopy (mqs, parent):
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header=header)

def _tdl_job_save_doc_to_QuickRef_html (mqs, parent):
   return QRU.save_to_QuickRef_html (rider, filename=None)

def _tdl_job_show_doc (mqs, parent):
   return QRU._tdl_job_show_doc (mqs, parent, rider, header=header)


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





