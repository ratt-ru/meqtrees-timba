#!/usr/bin/env python

# file ../contrib/JEN/peeling/pylab_peeling.py

from Timba.Contrib.JEN.util import JEN_pylab
import pylab

#-------------------------------------------------------------------------------

def contam_error(**ctrl):
    """Plot the parm errors and final residuals caused by peeling contamination"""
    funcname = JEN_pylab.on_entry(ctrl, 'contam_error',
                                  # savefile='transients_sine_plot',
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

