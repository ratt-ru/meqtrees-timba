# file: ../contrib/JEN/WSRT/WSRT_simul_cps.py

# Description:

# Simulation of WSRT data for testing purposes. A user-defined central
# point source (cps) may be corrupted with a user-defined sequence of
# WSRT Jones matrices (from module Grunting/WSRT_Jones.py).
# Optionally, gaussian noise may be added to the corrupted uv-data.

# History:
# - 14jan2007: creation
# - 16jun2007: adaptation to new TDLOptions

# Copyright: The MeqTree Foundation

#========================================================================
# Preamble:
#========================================================================

from Timba.TDL import *
from Timba.Meq import meq

import Meow
# from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..

from Timba.Contrib.JEN.WSRT import WSRT_Joneseq

from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import PointSource22


#========================================================================
# meqbrowser user menu-items:
#========================================================================


# MS options first
TDLCompileOption('TDL_num_stations','Number of stations',[5,14], more=int);
mssel = Meow.MSUtils.MSSelector(has_input=False,tile_sizes=[8,1,2,3,5,16,32,64,96]);
#                                   tile_sizes=[30,48,96,20,10,5,2,1]);

# MS compile-time options
TDLCompileOptions(*mssel.compile_options());

# MS run-time options
TDLRuntimeOptions(*mssel.runtime_options());
## also possible:
# TDLRuntimeMenu("MS selection options",open=True,*mssel.runtime_options());


# Compile-time menu:
PointSource22.include_TDL_options('cps model')  

TDLCompileMenu('Corrupting Jones matrices', WSRT_Joneseq)

TDLCompileOption('TDL_stddev_noise','Add gaussian noise: stddev (Jy)',
                 [0.0, 0.0001, 0.001, 0.01,0.1,1.0], more=float);
TDLCompileMenu('Print extra information',
               TDLCompileOption('TDL_display_PointSource22',
                                'Display PointSource22 object', [False, True]),
               TDLCompileOption('TDL_display_Visset22',
                                'Display Visset22 object', [False, True]),
               );
TDLCompileOption('TDL_cache_policy','Node result caching policy',[100,0], more=int);



#========================================================================
# Tree definition:
#========================================================================

def _define_forest (ns):
    """Define the MeqTree forest"""

    ANTENNAS = mssel.get_antenna_set(range(1,TDL_num_stations+1));
    array = Meow.IfrArray(ns, ANTENNAS)
    observation = Meow.Observation(ns)
    Meow.Context.set(array, observation)
    center = Meow.LMApproxDirection(ns, 'cps', l=0.0, m=0.0)

    # note how we set default image size from our current sky model
    imsel = mssel.imaging_selector(npix=512,arcmin=10);
    ## imsel = mssel.imaging_selector(npix=512,arcmin=sky_models.imagesize());
    TDLRuntimeMenu("Imaging options",*imsel.option_list());
  
    # Make a user-defined point source, derived from the Meow.PointSource class,
    # with some extra functionality for predefined sources and solving etc.
    ps = PointSource22.PointSource22 (ns, direction=center)
    if TDL_display_PointSource22: ps.display(full=True)

    # Create a Visset22 object, with nominal source coherencies:
    vis = ps.Visset22(array, observation, name='vissimmul', visu=True)

    if False:
        # An experiment in shifting the phase-centre:
        dl = 0.01            # 0.5 degrees: breaks down
        dl = 0.001           # 0.05 deg: still ok
        # dl = 0.00001
        dm = dl
        single = Meow.LMApproxDirection(ns, 'single', l=dl, m=dm)
        mirror = single.mirror()
        again = Meow.LMApproxDirection(ns, 'again', l=dl, m=dm)
        double = Meow.LMApproxDirection(ns, 'double', l=2*dl, m=2*dm)
        triple = Meow.LMApproxDirection(ns, 'triple', l=3*dl, m=3*dm)
        vis.shift_phase_centre(single, visu=True)
        vis.shift_phase_centre(mirror, visu=True)
        # vis.shift_phase_centre(again, visu=True)
        # vis.shift_phase_centre(double, visu=True)
        # vis.shift_phase_centre(triple, visu=True)
        vis.restore_phase_centre(visu=True, last=False)


    if True:
        # Corrupt the data with a sequence of Jones matrices:
        jones = WSRT_Joneseq.Joneseq22_uvp(ns, stations=array.stations(),
                                           # override=dict(GJones=dict(Psec=500)),
                                           simulate=True)
        jones.visualize('*')
        jones.p_plot_rvsi()
        jones.display(full=True)
        # jones.p_bundle()
        # jones.bundle()
        vis.corrupt(jones, visu=False)

    # Add gaussian noise, if required:
    if True:
        vis.addGaussianNoise(stddev=TDL_stddev_noise, visu='*')

    # Finished:
    vis.visualize(visu='timetracks')                 
    if TDL_display_Visset22: vis.display(full=True)
    global vdm_nodename
    vdm_nodename = vis.make_sinks(vdm='vdm')
    vis.history().display(full=True)
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_WSRT_simul_cps (mqs,parent):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    # req = JEN_Meow_Utils.create_io_request(override_output_column='MODEL_DATA');
    req = JEN_Meow_Utils.create_io_request();
    mqs.execute(vdm_nodename, req, wait=False);
    return True
                                     
def _tdl_job_1_simulate_MS (mqs,parent,wait=False):
    mqs.execute(vdm_nodename, mssel.create_io_request(), wait=wait);
  
  
# def _tdl_job_2_make_image (mqs,parent):
#    JEN_Meow_Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);
#    return True


#========================================================================
# Test routine (without the meqbrowser):
#========================================================================

if __name__ == '__main__':
    ns = NodeScope();
    _define_forest(ns);
    # resolves nodes
    ns.Resolve();  
    print len(ns.AllNodes()),'nodes defined';
