# file: ../contrib/JEN/Grunt/WSRT_simul_cps.py

# Description:

# Simulation of WSRT data for testing purposes. A user-defined central
# point source (cps) may be corrupted with a user-defined sequence of
# WSRT Jones matrices (from module Grunting/WSRT_Jones.py).
# Optionally, gaussian noise may be added to the corrupted uv-data.

# History:
# - 14jan2007: creation

# Copyright: The MeqTree Foundation

#========================================================================
# Preamble:
#========================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..
from Timba.Contrib.JEN.Grunting import WSRT_Jones

from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import PointSource22


#========================================================================
# meqbrowser user menu-items:
#========================================================================

# Run-time menu:
JEN_Meow_Utils.include_ms_options(has_input=False, has_output='MODEL_DATA',
                                  tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();


# Compile-time menu:
# PointSource22.include_TDL_options('Central Point Source (cps)')    # ....!? 
menuname = 'Central Point Source (cps)'
predefined = ['unpol','Q','U','V','QU','QUV','UV','QV']
# predefined.extend(['3c147','3c286'])
predefined.append(None)
TDLCompileMenu(menuname,
               TDLOption('TDL_source_name','source name (overridden by predefined)', ['PS22'], more=str),
               TDLOption('TDL_predefined','predefined source',predefined),
               TDLOption('TDL_StokesI','Stokes I (Jy)',[1.0, 2.0, 10.0], more=float),
               TDLOption('TDL_StokesQ','Stokes Q (Jy)',[None, 0.0, 0.1], more=float),
               TDLOption('TDL_StokesU','Stokes U (Jy)',[None, 0.0, -0.1], more=float),
               TDLOption('TDL_StokesV','Stokes V (Jy)',[None, 0.0, 0.02], more=float),
               TDLOption('TDL_spi','Spectral Index (I=I0*(f/f0)**(-spi)',[0.0, 1.0], more=float),
               TDLOption('TDL_freq0','Reference freq (MHz) for Spectral Index',[None, 1.0], more=float),
               TDLOption('TDL_RM','Intrinsic Rotation Measure (rad/m2)',[None, 0.0, 1.0], more=float),
               );

WSRT_Jones.include_TDL_options('corruption')

TDLCompileOption('TDL_stddev_noise','Add gaussian noise: stddev (Jy)',[0.0, 0.0001, 0.001, 0.01,0.1,1.0], more=float);
TDLCompileOption('TDL_num_stations','Number of stations',[5,14], more=int);
TDLCompileMenu('Print extra information',
               TDLCompileOption('TDL_display_PointSource22','Display PointSource22 object', [False, True]),
               TDLCompileOption('TDL_display_Visset22','Display Visset22 object', [False, True]),
               );
TDLCompileOption('TDL_cache_policy','Node result caching policy',[100,0], more=int);




#========================================================================
# Tree definition:
#========================================================================

def _define_forest (ns):
    """Define the MeqTree forest"""

    array = Meow.IfrArray(ns, range(1,TDL_num_stations+1))
    observation = Meow.Observation(ns)
    direction = Meow.LMDirection(ns, TDL_source_name, l=0.0, m=0.0)

    # Make a user-defined point source, derived from the Meow.PointSource class,
    # with some extra functionality for predefined sources and solving etc.
    ps = PointSource22.PointSource22 (ns, name=TDL_source_name,
                                      predefined=TDL_predefined,
                                      I=TDL_StokesI, Q=TDL_StokesQ,
                                      U=TDL_StokesU, V=TDL_StokesV,
                                      spi=TDL_spi, freq0=TDL_freq0, RM=TDL_RM,
                                      direction=direction)
    if TDL_display_PointSource22: ps.display(full=True)

    # Create a Visset22 object, with nominal source coherencies:
    vis = ps.Visset22(array, observation, name='simul', visu=True)

    # Corrupt the data with a sequence of Jones matrices:
    #   (Note that the user-defined TDLOption parameters are
    #    short-circuited between the functions in the WSRT_Jones module)
    jones = WSRT_Jones.Joneseq22(ns, stations=array.stations(),
                                 simulate=True)
    vis.corrupt(jones, visu=True)

    # Add gaussian noise, if required:
    vis.addGaussianNoise(stddev=TDL_stddev_noise, visu=True)

    # Finished:
    vis.show_timetracks(separate=True)                 
    if TDL_display_Visset22: vis.display(full=True)
    vis.make_sinks(vdm='vdm')        
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_WSRT_simul_cps (mqs,parent):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    # req = JEN_Meow_Utils.create_io_request(override_output_column='MODEL_DATA');
    req = JEN_Meow_Utils.create_io_request();
    mqs.execute('vdm',req,wait=False);
    return True
                                     
  
def _tdl_job_2_make_image (mqs,parent):
    JEN_Meow_Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);
    return True



#========================================================================
# Test routine (without the meqbrowser):
#========================================================================

if __name__ == '__main__':
    ns = NodeScope();
    _define_forest(ns);
    # resolves nodes
    ns.Resolve();  
    print len(ns.AllNodes()),'nodes defined';
