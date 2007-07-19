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

import Meow
# from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..

from Timba.Contrib.JEN.WSRT import WSRT_Joneseq

from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import PointSource22


#========================================================================
# meqbrowser user menu-items:
#========================================================================


# MS options first
mssel = Meow.MSUtils.MSSelector(has_input=False,tile_sizes=[8,1,2,3,5,16,32,64,96]);

# MS compile-time options
TDLCompileOptions(*mssel.compile_options());

# MS run-time options
TDLRuntimeOptions(*mssel.runtime_options());
## also possible:
# TDLRuntimeMenu("MS selection options",open=True,*mssel.runtime_options());


# Compile-time menu:
PointSource22.include_TDL_options('cps model')  


# WSRT_Joneseq.make_solv_option_menu()
TDLCompileMenu('Corrupting Jones matrices', WSRT_Joneseq)
               # toggle='TDL_Jones_matrices')

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

    ANTENNAS = mssel.get_antenna_set();
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
    if TDL_display_PointSource22:
        ps.display(full=True)

    # Create a Visset22 object, with nominal source coherencies:
    vis = ps.Visset22(array, observation, name='simvis', visu=True)

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


    # Optional: Corrupt the uv-data with a sequence of Jones matrices:
    jones = WSRT_Joneseq.Joneseq22_uvp(ns, stations=array.stations(),
                                       # override=dict(GJones=dict(Psec=500)),
                                       simulate=True)
    if jones:
        jones.visualize('*')
        jones.p_plot_rvsi()
        jones.display(full=True)
        jones.p_bundle()
        jones.bundle()
        vis.corrupt(jones, visu='*')
    # Test (temporary)
    # WSRT_Joneseq.get_solvable_parmgroups(trace=True)

    # Optional: Add gaussian noise, if required:
    if TDL_stddev_noise>0.0:
        vis.addGaussianNoise(stddev=TDL_stddev_noise, visu='*')

    # Finished:
    if TDL_display_Visset22:
        vis.display(full=True)
    global vdm_nodename
    vdm_nodename = vis.make_sinks(vdm='vdm', visu=False)
    vis.history().display(full=True)
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

                                     
def _tdl_job_1_simulate_MS (mqs, parent, wait=False):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    mqs.execute(vdm_nodename, mssel.create_io_request(), wait=wait);
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
