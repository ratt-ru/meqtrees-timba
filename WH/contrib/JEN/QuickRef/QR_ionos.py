"""
QuickRef module: QR_ionos.py:

Topics in ionospheric simulation/calibration

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

# file: ../JEN/demo/QR_ionos.py:
#
# Author: J.E.Noordam
#
# Short description:
#
# History:
#   - 13 jul 2008: creation (from QR-template.py)
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

from Timba.Contrib.JEN.QuickRef import QuickRefUtil as QRU
from Timba.Contrib.JEN.QuickRef import EasyTwig as ET
from Timba.Contrib.JEN.QuickRef import EasyNode as EN


import math
import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_ionos topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),

               TDLMenu("thinlayer",
                       TDLMenu("TEC",
                               toggle='opt_thinlayer_TEC'),
                       TDLMenu("MIM",
                               toggle='opt_thinlayer_MIM'),
                       toggle='opt_thinlayer'),

               TDLMenu("multilayer",
                       toggle='opt_multilayer'),
               
               TDLMenu("parabolic",
                       toggle='opt_parabolic'),

               TDLMenu("TID",
                       toggle='opt_TID'),
               
               TDLMenu("help",
                       TDLOption('opt_helpnode_twig',"help on EasyTwig.twig()", False),
                       toggle='opt_helpnodes'),

               toggle='opt_QR_ionos')



#********************************************************************************
# Top-level function, called from QuickRef.py:
#********************************************************************************

header = 'QR_ionos'                    # used in exec functions at the bottom

def QR_ionos (ns, path, rider):
   """
   """
   rr = QRU.on_entry(QR_ionos, path, rider)
   cc = []
   override = opt_alltopics
   global header

   # Edit this part:
   if override or opt_thinlayer:
      cc.append(thinlayer (ns, rr.path, rider))

   if opt_helpnodes:
      cc.append(make_helpnodes (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#********************************************************************************

def make_helpnodes (ns, path, rider):
   """
   It is possible to define nodes that have no other function than to carry
   a help-text. The latter may be consulted in the quickref_help field in the
   state record of this node (a bookmark is generated automatically). It is
   also added to the subset of documentation that is accumulated by the rider.
   """
   rr = QRU.on_entry(make_helpnodes, path, rider)
   
   override = opt_alltopics
   cc = []
   zz = numpy.arange(0,math.pi,math.pi/20)     # does NOT include math.pi itself

   if override or opt_helpnode_twig:
      cc.append(QRU.helpnode (ns, rr.path, rider, func=ET.twig))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)



#================================================================================
# thinlayer:
#================================================================================

def thinlayer (ns, path, rider):
   """
   The simplest ionospheric model is a thin, uniform layer at a constant altitude.
   """
   rr = QRU.on_entry(thinlayer, path, rider)
   cc = []
   override = opt_alltopics

   if override or opt_thinlayer_TEC:
      cc.append(thinlayer_TEC (ns, rr.path, rider))
   if override or opt_thinlayer_MIM:
      cc.append(thinlayer_MIM (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#================================================================================

def thinlayer_TEC (ns, path, rider):
   """
   """
   rr = QRU.on_entry(thinlayer_TEC, path, rider)
   cc = []

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)




#================================================================================

def thinlayer_MIM (ns, path, rider):
   """
   """
   rr = QRU.on_entry(thinlayer_MIM, path, rider)
   cc = []

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)












#********************************************************************************
#********************************************************************************
#********************************************************************************
# Helper functions
#********************************************************************************

def TEC_thin_layer (x=0, y=0, z=0, l=0, m=0, t=0,
                    TEC0=1.0, h=300, trace=False):
   """
   Return the TEC(x,y,z,l,m,t) for a thin layer at altitude h[=300] (km),
   for the given vertical TEC[=1.0] value (TECU)
   """
   zeff = zenith_angle_thin_layer(x=x, y=y, z=z, l=l, m=m, trace=trace)
   TEC = TEC0/math.cos(zeff)
   if trace:
      print '** TEC_thin_layer(TEC0=',TEC0,'TECU, h=',h,'km) ->',TEC 
   return TEC

#-------------------------------------------------------------------------------

def zenith_angle_thin_layer (x=0,y=0,z=0,l=0,m=0, h=300, trace=False):
   """
   Calculate the 'effective' zenith angle (x,y,z,l,m)
   for a thin layer at h[=300] km
   """
   R = 6370.0                        # Earth Radius (km)
   zang = zenith_angle (x=x, y=y, z=z, l=l, m=m, trace=False)
   zeff = math.asin(math.sin(zang)*R/(R+h))
   if trace:
      s = '** zenith_angle_thin_layer(x='+str(x)+', y='+str(y)+', z='+str(z)
      s += ', l='+str(l)+', m='+str(m)+', h='+str(h)+'km)'
      print s,'-> ',zeff,' rad (dz=',zeff-zang,1./math.cos(zeff),')'
   return zeff

#-------------------------------------------------------------------------------

def zeff_thin_layer (z, h=300, trace=False):
   """
   Calculate the 'effective' zenith angle from the nominal one,
   for a thin layer at h[=300] km
   """
   R = 6370.0                        # Earth Radius (km)
   zeff = math.asin(math.sin(z)*R/(R+h))
   if trace:
      print '** zeff_thin_layer(',z,', h=',h,'km) -> ',zeff,' rad (dz=',zeff-z,1./math.cos(zeff),')'
   return zeff

#-------------------------------------------------------------------------------

def zenith_angle (x=0,y=0,z=0,l=0,m=0, trace=False):
   """
   Calculates the zenith angle (rad) from (x,y,z,l,m).
   """
   R = 6700.0                        # Earth Radius (km)
   z1 = l - math.atan(float(x)/(R+z))
   z2 = m - math.atan(float(y)/(R+z))
   zang = math.hypot(z1,z2)          # equiv:  zang = math.sqrt(z1*z1 + z2*z2)
   if trace:
      s = '** zenith_angle (x='+str(x)+', y='+str(y)+', z='+str(z)
      s += ', l='+str(l)+', m='+str(m)+')'
      print s,' -> ',zang,' rad   (z1=',z1,', z2=',z2,')'
   return zang






#********************************************************************************
#********************************************************************************
# Standalone forest (i.e. not part of QuickRef.py) of this QR_module.
# Just load it into the browser, and compile/execute it.
#********************************************************************************
#********************************************************************************

def _define_forest (ns, **kwargs):
   """Define a standalone forest for standalone use of this QR module"""

   global rider                                 # global because it is used in tdl_jobs
   rider = QRU.create_rider()                   # the rider is a CollatedHelpRecord object
   rootnodename = 'QR_ionos'                    # The name of the node to be executed...
   path = rootnodename                          # Root of the path-string
   QRU.bundle (ns, path, rider,
               nodes=[QR_ionos(ns, path, rider)],
               help=__doc__)

   # Finished:
   QRU.ET.EN.bundle_orphans(ns)
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

def _tdl_job_execute_1D_f (mqs, parent):
   return QRU._tdl_job_execute_1D (mqs, parent, rootnode='QR_ionos')

def _tdl_job_execute_2D_ft (mqs, parent):
   return QRU._tdl_job_execute_ft (mqs, parent, rootnode='QR_ionos')

def _tdl_job_execute_6D_tLMXYZ (mqs, parent):
   return QRU._tdl_job_execute_tLMXYZ (mqs, parent, rootnode='QR_ionos')

def _tdl_job_execute_sequence (mqs, parent):
   return QRU._tdl_job_execute_sequence (mqs, parent, rootnode='QR_ionos')

#--------------------------------------------------------------------------------
# Some functions to dispose of the specified subset of the documentation:
#--------------------------------------------------------------------------------

def _tdl_job_m (mqs, parent):
   """Dummy tdl job that acts as separator in the TDL exec menu.""" 
   return QRU._tdl_job_m (mqs, parent)

def _tdl_job_print_doc (mqs, parent):
   """Print the specified subset of the help doc on the screen"""
   return QRU._tdl_job_print_doc (mqs, parent, rider, header=header)

def _tdl_job_print_hardcopy (mqs, parent):
   """Print a hardcopy of the specified subset of the help doc on the printer.
   NB: The printer may be customized with the runtime options."""
   return QRU._tdl_job_print_hardcopy (mqs, parent, rider, header=header)

def _tdl_job_show_doc (mqs, parent):
   """Show the specified subset of the help doc in a popup"""
   return QRU._tdl_job_show_doc (mqs, parent, rider, header=header)

def _tdl_job_save_doc (mqs, parent):
   """Save the specified subset of the help doc in a file"""
   return QRU._tdl_job_save_doc (mqs, parent, rider, filename=header)




#********************************************************************************
#********************************************************************************
# Standalone test (without the browser):
#********************************************************************************
#********************************************************************************

if __name__ == '__main__':

   print '\n** Start of standalone test of: QR_ionos.py:\n' 

   ns = NodeScope()

   rider = QRU.create_rider()             # CollatedHelpRecord object
   if 0:
      QR_ionos(ns, 'test', rider=rider)
      if 1:
         print rider.format()

   if 0:
      zenith_angle(trace=True)
      zenith_angle(l=1, trace=True)
      zenith_angle(l=1, m=1, trace=True)
      zenith_angle(x=100, trace=True)
      zenith_angle(x=100, l=0.1, trace=True)
      zenith_angle(x=100, m=0.1, trace=True)
      zenith_angle(x=100, y=100, trace=True)
      zenith_angle(y=100, trace=True)
      zenith_angle(y=100, z=100, trace=True)

   if 0:
      zenith_angle_thin_layer(trace=True)
      zenith_angle_thin_layer(l=1, trace=True)
      zenith_angle_thin_layer(l=math.pi/2, trace=True)

   if 1:
      TEC_thin_layer(trace=True)
      TEC_thin_layer(l=1, trace=True)
            
   print '\n** End of standalone test of: QR_ionos.py:\n' 

#=====================================================================================





