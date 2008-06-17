"""
QuickRef module: QR_execution.py:

MeqTree execution issues (Request, Result etc)

This module may be called from the module QuickRef.py.
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

# file: ../JEN/demo/QR_execution.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 11 jun 2008: creation (from QR-template.py)
#
# Description:
#
# Remarks:
#
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

import QuickRefUtil as QRU
import EasyTwig as ET

# import math
# import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_execution topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),
               TDLOption('opt_input_twig',"input twig",
                         ET.twig_names(), more=str),
               TDLMenu("request",
                       toggle='opt_request'),

               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_execution')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************


def QR_execution (ns, path, rider):
   """
   A MeqTree is a non-circular graph, i.e. it consists of (software, C++) nodes,
   each of which has zero or more children. The tree is defined by means of the
   Tree Definition Language (TDL), which is just Python with a few extensions.
   A TDL script generates a list of instructions for the creation of C++ nodes,
   which do the real work. Python is not used in the actual execution, except by
   a user-defined class of nodes called PyNodes. The latter are usually not on
   the critical path, so they do not slow down the execution.

   A (sub)tree may be 'executed' by passing a request (object) to any node. This
   is usually, but not necessarily the root (bottom) node of the entire tree.
   Nodes that have children pass the request on, and calculate their result by
   'doing their thing' with their child results, according to their type (class).
   Leaf nodes (no children) have access to other information to produce their result.
   Thus, the request is passed all the way 'up the tree' to its leaves, and the
   results are passed 'downstream' from children to parent nodes. The process ends
   when the node that has been given the request has produced its result (object).

   A request specifies a 'domain', i.e. an N-dimensional array of points in some
   space. The default domain is a 2D rectangle in time-freq space, reflecting the
   fact that most Measurement Equations depend on time and frequency. A domain is
   subdivided into 'cells', not necessarily on a regular grid, not necessarily with
   uniform size, and not necessarily contiguous.

   A result contains at least one 'vellset', i.e. an array of values for the cells of
   the requested domain. Producing these values is the ultimate purpose of MeqTrees. 


   Multiple results (tensors).
   Perturbations.
   Caching.
   See ....
   
   """
   rr = QRU.on_entry(QR_execution, path, rider)
 
   twig = ET.twig(ns, opt_input_twig)

   cc = [twig]
   if opt_alltopics or opt_request:
      cc.append(request (ns, rr.path, rider, twig=twig))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=twig, viewer='Record Browser')



#********************************************************************************
# 2nd tier: Functions called from the top function above:
#********************************************************************************

def make_helpnodes (ns, path, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   rr = QRU.on_entry(make_helpnodes, path, rider)
   
   cc = []
   if opt_alltopics or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, name='EasyTwig_twig',
                             help=ET.twig.__doc__, trace=False))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#--------------------------------------------------------------------------------

def request (ns, path, rider, twig):
   """
   A request is an object, which contains a domain, subdivided in cells, for which values
   are required. A request also contains other information. It is passed 'up' a tree, from
   parent to children, until the leaf nodes (which have no children).

   The simplest way to generate a simple 2D (freq-time) request is:
   .      from Timba.Meq import meq
   .      domain = meq.domain(fmin,fmax,tmin,tmax)              <class 'Timba.dmi.MeqDomain'> 
   .      cells = meq.cells(domain, num_time=10, num_freq=21)   <class 'Timba.dmi.MeqCells'> 
   .      request_counter += 1
   .      rqid = meq.requestid(request_counter)
   .      request = meq.request(cells, rqid=rqid)               <class 'Timba.dmi.MeqRequest'>

   The request may be inspected (after execution) in the state record of any node (by clicking 
   on it in the browser), or by specifying 'show each request' in the Custom Settings of the
   TDL exec menu when executing the QuickRef module.
   
   The tree may now be executed (starting at the named node):
   .      result = mqs.meq('Node.Execute',record(name=<nodename>, request=request), wait=True)   

   NB: Changing the request identifier by incrementing the request_counter guarantees that the
   request will be interpreted by the nodes upstream as a new request, for which new values
   are required (i.e. the values in their caches will not do).
   An alternative way of generating a request is (... this needs some explanation! ...):
   .      request = meq.request(cells, rqtype='ev')

   See below for a more detailed discussion of generating domains and cells.
   """
   rr = QRU.on_entry(request, path, rider, twig)
   cc = [twig]
   cc.append(request_domain (ns, rr.path, rider, twig=twig))
   cc.append(request_cells (ns, rr.path, rider, twig=twig))
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=twig, viewer='Record Browser')



#********************************************************************************
#********************************************************************************
#********************************************************************************
# 3rd tier: Functions called from functions at the 2nd tier above
#********************************************************************************
#********************************************************************************


#================================================================================
# request_... 
#================================================================================

def request_domain (ns, path, rider, twig):
   """
   A domain object is ...

   The simplest way to generate a simple 2D (freq-time) domain is:
   .      from Timba.Meq import meq
   .      domain = meq.domain(fmin,fmax,tmin,tmax)              <class 'Timba.dmi.MeqDomain'> 

   A more general (N-dimensional) domain may be specified by:
   .      dd = record()                             
   .      dd.freq = (fmin,fmax)
   .      dd.time = (tmin,tmax)
   .      dd.L = (Lmin,Lmax)
   .      dd.M = (Mmin,Mmax)
   .      .. etc ..
   .      domain = meq.gen_domain(**dd)                         <class 'Timba.dmi.MeqDomain'> 

   The request domain may be inspected (after execution) in the state record of any node.
   Try this by executing different kinds of input nodes (twigs).
   """
   rr = QRU.on_entry(request_domain, path, rider)
   cc = [twig]
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=twig, viewer='Record Browser')

#--------------------------------------------------------------------------------------------

def request_cells (ns, path, rider, twig):
   """
   A cells object sub-divides a rectangular N-dim domain (envelope) into an N-dim array
   of cells. NB: Since the domain is an envelope, and cell coordinates represent the
   cell centres, the coordinates of the outer cells will be different from the domain
   boundaries. 
   
   The simplest way to generate a default 2D (freq-time) cells object is:
   .      from Timba.Meq import meq
   .      cells = meq.cells(domain, num_time=10, num_freq=21)   <class 'Timba.dmi.MeqCells'> 

   A more general (N-dimensional) cells may be specified by:
   .      nn = record()                             
   .      nn.num_freq = 100
   .      nn.num_L = 23
   .      nn.num_M = 3
   .      .. etc ..
   .      cells = meq.gen_cells(domain, **nn)                   <class 'Timba.dmi.MeqCells'> 

   In both cases, the domain object is generated in the way(s) discussed above.

   By default, domain cells are on a regular grid, uniform in size, and contiguous.
   However, in many cases, less regular cells may needed (e.g. with data that are sampled
   irregularly in time of freq). Such cells be specified in the following way:
   ... to be done ....
   (NB: do irregular cells carry a penalty in efficiency?)

   The cells details may be inspected (after execution) in the state record of any node.
   Try this by executing different kinds of input nodes (twigs).
   """
   rr = QRU.on_entry(request_cells, path, rider)
   cc = [twig]
   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      bookmark=twig, viewer='Record Browser')











#================================================================================
#================================================================================
#================================================================================
#================================================================================
# It is possible to define a standalone forest (i.e. not part of QuickRef.py) of
# this QR_module. Just load it into the browser, and compile/execute it.
#================================================================================

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider()                   # the rider is a CollatedHelpRecord object
   rootnodename = 'QR_execution'                 # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QRU.bundle (ns, path, rider,
              nodes=[QR_execution(ns, path, rider)],
              help=__doc__)

   # Finished:
   return True


#--------------------------------------------------------------------------------

# A 'universal TDLRuntimeMenu is defined in QuickRefUtil.py (QRU):

TDLRuntimeMenu(":")
TDLRuntimeMenu("QuickRef runtime options:", QRU)
TDLRuntimeMenu(":")

# For the TDLCompileMenu, see the top of this module


#--------------------------------------------------------------------------------
# Functions that execute the demo tree of this module with different requests.
# Many such functions are defined in QuickRefUtil.py (QRU).
# Make a selection that is suitable for this particular QR module.
#--------------------------------------------------------------------------------

def _tdl_job_execute_1D (mqs, parent):
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_2D (mqs, parent):
   return QRU._tdl_job_execute_2D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_3D (mqs, parent):
   return QRU._tdl_job_execute_3D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_4D (mqs, parent):
   return QRU._tdl_job_execute_4D (mqs, parent, rootnode='QR_execution')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QR_execution')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header='QR_execution')

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header='QR_execution')

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header='QR_execution')

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename='QR_execution')



#=====================================================================================
# Standalone test (without the browser):
#=====================================================================================

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_execution.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 1:
      QR_execution(ns, 'test', rider=rider)
      if 1:
         print rider.format()
            
   print '\n** End of standalone test of: QR_execution.py:\n' 

#=====================================================================================





