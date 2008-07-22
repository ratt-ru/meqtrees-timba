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

from Timba.Contrib.JEN.pylab import PyNodeNamedGroups as PNNG
from Timba.Contrib.JEN.pylab import PyNodePlot as PNP

# from Timba.Contrib.JEN.Expression import Expression

import math
import random
import numpy


#******************************************************************************** 
# TDLCompileMenu (included in QuickRef menu):
#********************************************************************************


TDLCompileMenu("QR_ionos topics:",
               TDLOption('opt_alltopics',"override: include all topics",True),

               TDLMenu("thinlayer",
                       TDLOption('opt_thinlayer_alltopics',
                                 "override: include all thinlayer sub-topics",False),
                       TDLOption('opt_thinlayer_altitude',"altitude (km)",
                                 [300,350,400,500,200], more=float),
                       TDLOption('opt_thinlayer_Earth_radius',"Earth radius (km)",
                                 [6370,1e3,1e4,1e9], more=float),
                       TDLOption('opt_thinlayer_TEC0',"vertical TEC (TECU)",
                                 [1.0,2.0,5.0,10.0,100.0,0.0], more=float),
                       TDLOption('opt_thinlayer_wvl',"observing wavelength (m)",
                                 [1.0,2.0,4.0,10.0,20.0,0.33,0.21], more=float),
                       TDLOption('opt_thinlayer_bmax',"max baseline (km)",
                                 [1000,100,30,10,3,1.0], more=float),

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
               
               TDLMenu("GPS",
                       TDLMenu("TEC",
                               toggle='opt_GPS_TEC'),
                       TDLMenu("triplefreq",
                               toggle='opt_GPS_triplefreq'),
                       toggle='opt_GPS'),
               
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

   if override or opt_thinlayer:
      cc.append(thinlayer (ns, rr.path, rider))

   if override or opt_GPS:
      cc.append(GPS (ns, rr.path, rider))

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
   It is fully characterized by two parameters: its altitude h (usually at a few
   hundred km) and its vertical TEC (TECU), which is independent of Earth position (x,y).
   The TEC from a given viewing position (x,y,z) is determined by the slant-angle of the
   line-of-sight, i.e. the angle at which it intersects the thin layer. This leads to a
   z-factor (>=1.0) with which TEC0 must be multiplied:   TEC(z) = z-factor * TEC0         

   For a flat Earth, z-factor = sec(z), in which z is the zenith angle, and sec(z)=1/cos(z).

   For a curved Earth surface (R=6370 km), z-factor = sec(asin(sin(z)*(R/(R+h)))).

   The flat Earth formula gives a reasonable approximation for z<1 rad. The curved Earth
   formula has the obvious advantage that the z-factor towards the horizon (z=pi/2) is
   about 3.0 (for h=300 km), rather than infinite.
   """
   rr = QRU.on_entry(thinlayer, path, rider)
   cc = []
   override = opt_thinlayer_alltopics

   if override or opt_thinlayer_TEC:
      cc.append(thinlayer_TEC (ns, rr.path, rider))
   if override or opt_thinlayer_MIM:
      cc.append(thinlayer_MIM (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)


#================================================================================

def thinlayer_TEC (ns, path, rider):
   """
   This topic shows a few (PyNodePlot) plots that fully describe the effects of a thin layer.
   The user may experiment a little by varying the various parameters (h, TEC0, wvl, bmax).
   """
   rr = QRU.on_entry(thinlayer_TEC, path, rider)
   cc = []
   viewer = []

   h = float(opt_thinlayer_altitude)
   R = float(opt_thinlayer_Earth_radius)
   TEC0 = float(opt_thinlayer_TEC0)
   wvl = float(opt_thinlayer_wvl)
   bmax = float(opt_thinlayer_bmax)

   zmax = numpy.pi/2
   dz = zmax/30
   zz = numpy.arange(dz,dz+zmax,dz).tolist()
   zfz = []
   for z in zz:
      zfz.append(zfactor_thin_layer (l=z, h=h, R=R, trace=False))

   dx = bmax/20
   xx = numpy.arange(dx,dx+bmax,dx).tolist()
   ll = [0,0.5,1.0,1.5]
   pdiff = numpy.zeros([len(ll),len(xx)])
   derr = numpy.zeros([len(ll),len(xx)])
   zfx = numpy.zeros([len(ll),len(xx)])
   psf = numpy.zeros([len(ll),len(xx)])
   rad2arcmin = 60.0*180.0/math.pi
   derrmax = 0.0
   for j,l in enumerate(ll):
      for i,x in enumerate(xx):
         zfx[j,i] = zfactor_thin_layer (x=x, l=l, h=h, R=R, trace=False)
         pdiff[j,i] = -25*wvl*TEC0*(zfx[j,i]-zfx[j,0])
         opd = -4*wvl*wvl*TEC0*(zfx[j,i]-zfx[j,0])       # pathlength diff (m)
         if not x==0.0:
            x_m = x*1000.0                               # x in meters
            derr[j,i] = math.atan(opd/x_m)*rad2arcmin    # direction error
            derrmax = max(derrmax,derr[j,i])
            psf[j,i] = (wvl/x_m)*rad2arcmin              # resolution (width of psf) 

   # Make the groupspecs record for all plots:
   gs = record(zz=zz, xx=xx, zfz=zfz)
   gs['psf'] = psf[0].tolist()
   for j,l in enumerate(ll):
      gs['zfx'+str(j)] = zfx[j].tolist()
      gs['pdiff'+str(j)] = pdiff[j].tolist()
      gs['derr'+str(j)] = derr[j].tolist()

   # The legend for wavelength-independent plots:
   legend = ['thin layer altitude ='+str(h)+' km',
             'Earth radius = '+str(R)+' km',
             'Vertical TEC: TEC0 = '+str(TEC0)+' TECU']

   if True:
      psg = [record(y='{zfz}', x='{zz}', color='red',
                    marker=None, linestyle='-')]
      ps = record(graphics=psg, legend=legend,
                  title='z-factor as a function of zdir',
                  xlabel='zenith angle (rad)',
                  ylabel='z-factor')
      cc.append(PNP.pynode_Plot(ns, groupspecs=gs, plotspecs=ps))

   if True:
      psg = []
      for j,l in enumerate(ll):
         psg.append(record(y='{zfx'+str(j)+'}', x='{xx}', color='magenta',
                           marker=None, linestyle='-',
                           label='z='+str(l)+' rad'))
      ps = record(graphics=psg, legend=legend,
                  title='z-factor as a function of xpos',
                  xlabel='baseline length (km)',
                  ylabel='z-factor')
      cc.append(PNP.pynode_Plot(ns, groupspecs=gs, plotspecs=ps))


   # Append wavelength-dependent legend(s):
   legend.append('wavelength = '+str(wvl)+ 'm')

   if True:
      psg = []
      for j,l in enumerate(ll):
         psg.append(record(y='{pdiff'+str(j)+'}', x='{xx}', color='blue',
                           marker=None, linestyle='-',
                           label='z='+str(l)+' rad'))
      ps = record(graphics=psg, legend=legend,
                  title='ionospheric phase-diff',
                  xlabel='baseline length (km)',
                  ylabel='phase-diff (rad)')
      cc.append(PNP.pynode_Plot(ns, groupspecs=gs, plotspecs=ps))

   if True:
      psg = []
      for j,l in enumerate(ll):
         psg.append(record(y='{derr'+str(j)+'}', x='{xx}', color='red',
                           marker=None, linestyle='-',
                           label='z='+str(l)+' rad'))
      psg.append(record(y='{psf}', x='{xx}', color='blue',
                        marker=None, linestyle='--',
                        ignore='{psf}>'+str(derrmax),
                        legend='PSF width (resolution)'))
      ps = record(graphics=psg, legend=legend,
                  title='baseline-dependent "refraction"',
                  xlabel='baseline length (km)',
                  ylabel='direction err (arcmin)')
      cc.append(PNP.pynode_Plot(ns, groupspecs=gs, plotspecs=ps))


   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help,
                      viewer='Pylab Plotter')




#================================================================================

def thinlayer_MIM (ns, path, rider):
   """
   """
   rr = QRU.on_entry(thinlayer_MIM, path, rider)
   cc = []

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)



#================================================================================
# GPS:
#================================================================================

def GPS (ns, path, rider):
   """
   The simplest ionospheric model is a thin, uniform layer at a constant altitude.
   """
   rr = QRU.on_entry(GPS, path, rider)
   cc = []
   override = opt_GPS_alltopics

   if override or opt_GPS_TEC:
      cc.append(GPS_TEC (ns, rr.path, rider))
   if override or opt_GPS_triplefreq:
      cc.append(GPS_triplefreq (ns, rr.path, rider))

   return QRU.bundle (ns, rr.path, rider, nodes=cc, help=rr.help)











#********************************************************************************
#********************************************************************************
#********************************************************************************
# Helper functions
#********************************************************************************

def zfactor_thin_layer (x=0, y=0, z=0, l=0, m=0, t=0,
                        h=300, R=6370.0, trace=False):
   """
   Return the z-factor for a uniform thin layer at altitude h (km),
   for a given position (x,y,z) km, in a given direction (l,m) rad
   w.r.t. the zenith at the origin (x=0,y=0,z=0) on the Earth surface.
   The z-factor is the factor with which the excess path length L0
   (and thus the TEC0) for the zenith have to be multiplied. 
   """
   zlocal = local_zenith_angle (x=x, y=y, z=z, l=l, m=m, R=R, trace=trace)
   zfactor = 1.0/math.cos(math.asin(math.sin(zlocal)*R/(R+h)))
   if trace:
      print '** zfactor_thin_layer(h=',h,'km',R,') ->',zfactor 
   return zfactor

#-------------------------------------------------------------------------------

def local_zenith_angle (x=0,y=0,z=0,l=0,m=0, R=6370.0, trace=False):
   """
   Calculates the (geometric) zenith angle (rad) at position (x,y,z)
   of a source that would have direction (l,m) rad w.r.t. the zenith
   at the origin (x=0,y=0,z=0) on the Earth surface (R=6370km).
   """
   z1 = l - math.atan(float(x)/(R+z))
   z2 = m - math.atan(float(y)/(R+z))
   zang = math.hypot(z1,z2)          # equiv:  zang = math.sqrt(z1*z1 + z2*z2)
   if trace:
      s = '\n** local_zenith_angle (x='+str(x)+', y='+str(y)+', z='+str(z)
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
      local_zenith_angle(trace=True)
      local_zenith_angle(l=1, trace=True)
      local_zenith_angle(l=1, m=1, trace=True)
      local_zenith_angle(x=100, trace=True)
      local_zenith_angle(x=100, l=0.1, trace=True)
      local_zenith_angle(x=100, m=0.1, trace=True)
      local_zenith_angle(x=100, y=100, trace=True)
      local_zenith_angle(y=100, trace=True)
      local_zenith_angle(y=100, z=100, trace=True)

   if 1:
      zfactor_thin_layer(trace=True)
      for L in [0,0.01,0.1,0.2,0.5,1]:
         zfactor_thin_layer(l=L, trace=True)
      for x in [0,1,10,100,1000]:
         zfactor_thin_layer(x=x, trace=True)
            
   print '\n** End of standalone test of: QR_ionos.py:\n' 

#=====================================================================================





