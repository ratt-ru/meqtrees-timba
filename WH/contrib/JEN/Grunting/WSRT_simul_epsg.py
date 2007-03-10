# file: ../contrib/JEN/Grunt/WSRT_simul_epsg.py

# Description:

# Simulation of WSRT data for testing purposes. A user-defined group
# of equal point sources (epsg) may be corrupted with a user-defined
# sequence of WSRT Jones matrices (from module Grunting/WSRT_Jones.py).
# Optionally, gaussian noise may be added to the corrupted uv-data.

# History:
# - 10mar2007: creation

# Copyright: The MeqTree Foundation

#========================================================================
# Preamble:
#========================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..
from Timba.Contrib.JEN.Grunting import WSRT_Jones

from Timba.Contrib.JEN.Grunt import PointSourceGroup22


#========================================================================
# meqbrowser user menu-items:
#========================================================================

# Run-time menu:
JEN_Meow_Utils.include_ms_options(has_input=False, has_output='MODEL_DATA',
                                  tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();


# Compile-time menu:
# PointSource22.include_TDL_options('epsg model')  
PointSourceGroup22.include_EqualPointSourceGrid_TDL_options('epsg')

WSRT_Jones.include_TDL_options_uvp('corruption')

TDLCompileOption('TDL_stddev_noise','Add gaussian noise: stddev (Jy)',
                 [0.0, 0.0001, 0.001, 0.01,0.1,1.0], more=float);
TDLCompileOption('TDL_num_stations','Number of stations',[5,14], more=int);
TDLCompileMenu('Print extra information',
               TDLCompileOption('TDL_display_EqualPointSourceGrid22',
                                'Display EqualPointSourceGrid22 object', [False, True]),
               TDLCompileOption('TDL_display_Visset22',
                                'Display Visset22 object', [False, True]),
               );
TDLCompileOption('TDL_cache_policy','Node result caching policy',[100,0], more=int);




#========================================================================
# Tree definition:
#========================================================================

def _define_forest (ns):
    """Define the MeqTree forest"""

    array = Meow.IfrArray(ns, range(1,TDL_num_stations+1))
    observation = Meow.Observation(ns)
    Meow.Context.set(array, observation)

    # Make a user-defined pattern of equal (user-defined) point sources:
    epsg = PointSourceGroup22.EqualPointSourceGrid22 (ns)
    if TDL_display_EqualPointSourceGrid22: epsg.display(full=True)

    # Create a Visset22 object, with nominal source coherencies:
    vis = epsg.Visset22(name='simul', visu=True)

    if False:
        # Corrupt the data with a sequence of Jones matrices:
        #   (Note that the user-defined TDLOption parameters are
        #    short-circuited between the functions in the WSRT_Jones module)
        jones = WSRT_Jones.Joneseq22_uvp(ns, stations=array.stations(),
                                         override=dict(GJones=dict(Psec=500)),
                                         simulate=True)
        vis.corrupt(jones, visu=False)

    # Add gaussian noise, if required:
    vis.addGaussianNoise(stddev=TDL_stddev_noise, visu='*')

    # Finished:
    vis.show_timetracks(separate=True)                 
    if TDL_display_Visset22: vis.display(full=True)
    vis.make_sinks(vdm='vdm')        
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_WSRT_simul_epsg (mqs,parent):
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
