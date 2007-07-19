#!/usr/bin/env python

# file ../contrib/JEN/peeling/pylab_peeling.py

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

from Timba.Contrib.JEN.util import JEN_pylab
import pylab

#-------------------------------------------------------------------------------

def contam_mosaic(**ctrl):
    funcname = JEN_pylab.on_entry(ctrl, 'contam_mosaic')
    contam_error(subplot=321)
    contam_error(subplot=322)
    return JEN_pylab.on_exit(ctrl, mosaic=True)


#-------------------------------------------------------------------------------

def contam_error(**ctrl):
    """Plot the parm errors and final residuals caused by peeling contamination"""
    funcname = JEN_pylab.on_entry(ctrl, 'contam_error',
                                  save=True, savefile='contam_error',
                                  xlabel='peeling source index',
                                  ylabel='log(parm error) or log(final resdidual)(+)',
                                  title='Errors caused by peeling contamination')
    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 1     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 5               # nr on antennas in array
    flux_factor = 1.0      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([0.06, 0.002, 0.0002]), resid=0.06, color='red')

    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 2     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 5               # nr on antennas in array
    flux_factor = 1.0      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([0.004, 1e-5, 0.0001]), resid=0.05, color='red')

    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 3     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 5               # nr on antennas in array
    flux_factor = 1.0      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([1e-18, 1e-18, 1e-18]), resid=1e-18, color='green')

    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 1     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 5               # nr on antennas in array
    flux_factor = 0.5      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([0.02, 0.002, 6e-5]), resid=0.02, color='red')

    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 2     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 5               # nr on antennas in array
    flux_factor = 0.5      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([0.001, 5e-8, 5e-8]), resid=0.001, color='red')

    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 2     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 27               # nr on antennas in array
    flux_factor = 0.5      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([0.003, 5e-7, 5e-7]), resid=0.003, color='red')

    #------------
    # Experiment:
    tile_size = 10         # nr of time-slots in a tile
    predict_window = 1     # nr of sources in predict-window
    grid_spacing = 10      # arcmin
    nant = 27               # nr on antennas in array
    flux_factor = 0.5      # factor by which successive sources are fainter
    ctrl = contam_error1(ctrl, perr=pylab.array([0.01, 0.005, 2e-6]), resid=0.01, color='red')


    #---------------------------------------------
    # Acceptability level:
    JEN_pylab.plot_line(ctrl, xx=[0,2], yy=[-3.0,-3.0], style='--', color='black')
    return JEN_pylab.on_exit(ctrl)

#---------------------------------------------

def contam_error1(ctrl, perr, resid, color='red'):
    nps = len(perr)
    xx = pylab.arange(nps)
    perr = pylab.log(perr)/pylab.log(10.0)
    resid = pylab.log(resid)/pylab.log(10.0)
    logmin = -8.5
    resid = max(resid,logmin)
    for i in range(len(perr)):
        perr[i] = max(perr[i],logmin)
    JEN_pylab.plot_marker(ctrl, xx, perr, style='o', color=color)
    JEN_pylab.plot_line(ctrl, xx, perr, style='--', color=color)
    JEN_pylab.plot_marker(ctrl, xx[len(xx)-1], resid, style='+', size=16, color=color)
    return ctrl


#-------------------------------------------------------------------------------
# Test functions:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print '\n*******************\n** Local test of: pylab_peeling.py:\n'
    # from numarray import *
    # from numarray.linear_algebra import *
    # from Timba.Trees import TDL_display
    # from Timba.Trees import JEN_record

    if 1:
        contam_error()
    
    if 0:
        JEN_pylab.ctrl_display(ctrl, 'final')


#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------

