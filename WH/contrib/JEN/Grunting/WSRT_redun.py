# file: ../contrib/JEN/Grunting/WSRT_redun.py

# Description:

# Solve, by comparing redundant spacings, for a (subset of) the
# M.E. parameters in a user-defined sequence of uv-plane WSRT
# Jones matrices (from module Grunting/WSRT_Jones.py).
# No source model is needed.

# History:
# - 20feb2007: creation (from WSRT_solve_cps.py)

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
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..
from Timba.Contrib.JEN.Grunting import WSRT_Jones

from Timba.Contrib.JEN.Grunt import Visset22
from Timba.Contrib.JEN.Grunt import RedunVisset22
from Timba.Contrib.JEN.Grunt import PointSource22
from Timba.Contrib.JEN.Grunt import solving22
from Timba.Contrib.JEN.Grunt import Condexet22


#========================================================================
# meqbrowser user menu-items:
#========================================================================

# Run-time menu:

JEN_Meow_Utils.include_ms_options(has_input=True, has_output='CORRECTED_DATA',
                                  tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();


# Compile-time menu:

TDLCompileOption('TDL_simul_input','Simulated input data',[False,True]);
PointSource22.include_TDL_options('input cps model')  

WSRT_Jones.include_TDL_options_uvp('instrum. model')

pg = WSRT_Jones.parmgroups_uvp()
TDLCompileOption('TDL_parmgog','parmgroups to be solved for', pg, more=str);

TDLCompileOption('TDL_redun_mode','Redundancy mode',['rhs','lhs']);

solving22.include_TDL_options()

TDLCompileOption('TDL_num_stations','Number of stations',[5,14], more=int);
TDLCompileMenu('Print extra information',
               # TDLCompileOption('TDL_display_PointSource22','Display PointSource22 object', [False, True]),
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
    Meow.Context.set(array, observation)

    if TDL_simul_input:
        # Make a user-defined point source model, derived from the Meow.PointSource class,
        # with some extra functionality for predefined sources and solving etc.
        direction = Meow.LMDirection(ns, 'cps', l=0.0, m=0.0)
        ps = PointSource22.PointSource22 (ns, direction=direction)
        # if TDL_display_PointSource22: ps.display(full=True)
        # Create a Visset22 object with simulated uv-data:
        data = ps.Visset22(array, observation, name='data', visu=True)
        # The default controls for the various parameters in WSRT_Jones
        # may be overridden by specifying a field in the following way:
        override = dict(example=dict(tfdeg=[2,3], subtile_size=1),
                        Gphase=dict(Psec=1000),
                        GJones=dict(),
                        JJones=dict(),
                        DJones=dict())
        jones = WSRT_Jones.Joneseq22_uvp(ns, stations=array.stations(),
                                         simulate=True,
                                         override=override)
        print jones._pgm.tabulate()
        data.corrupt(jones, visu='*')
    else:
        # The measured uv-data are read from the Measurement Set via spigots:
        data = Visset22.Visset22(ns, label='data', array=array)
        data.make_spigots(visu='*')

    # Correct(!) the measured data with a sequence of Jones matrices,
    # which contain the solvable parameters. uv-plane effects only.
    #   (Note that the user-defined TDLOption parameters are
    #    short-circuited between the functions in the WSRT_Jones module)
    # The default controls for the various parameters in WSRT_Jones
    # may be overridden by specifying a field in the following way:
    override = dict(example=dict(tfdeg=[2,3], subtile_size=1),
                    Gphase=dict(tfdeg=[7,8], subtile_freq=2),
                    GJones=dict(tfdeg=[2,2]),
                    JJones=dict(),
                    DJones=dict())
    jones = WSRT_Jones.Joneseq22_uvp(ns, stations=array.stations(),
                                     override=override)

    # Make the right-hand side (rhs), if required:
    rhs = None
    redun = None
    if TDL_redun_mode=='rhs':
        # Corrupt a (rhs) RedunVisset22 object:
        rr = RedunVisset22.make_WSRT_redun_groups (ifrs=array.ifrs(), sep9A=36,
                                                   # rhs='constant', select='all')
                                                   rhs='diagonal', select='all')
        rhs = RedunVisset22.RedunVisset22(ns, label='rhs', array=array,
                                          redun=rr, polar=True)
        rhs.corrupt(jones, visu=False)
    else:
        # TDL_redun_mode=='lhs' (use redun dict to make pairs from lhs)
        # Correct(!) the measured data with a sequence of Jones matrices,
        # NB: Note the unusual pgm_merge==True, to make sure that the parmgroup
        #     manager from the data visset is passed on (this is not the
        #     case for a normal solve, where the pgm from the predicted
        #     visset is used (...)
        # NB: Visu==False because this shows the situation before solving,
        #     due to caching. So use visu==True on make_sinks() below.
        data.correct(jones, pgm_merge=True, visu=False)
        redun = Condexet22.make_WSRT_redun_pairs (ifrs=array.ifrs(), sep9A=36,
                                                  select='all')
        

    # Create a solver for a user-defined subset of parameters (parmgroup):
    # NB: The solver gets its requests from a ReqSeq that is automatically
    #     inserted into the main-stream by data.make_sinks() below.
    solving22.make_solver(lhs=data, rhs=rhs, redun=redun, parmgroup=TDL_parmgog)    # .... '*' ...?

    # Correct the data for the estimated instrumental errors
    if rhs:
        data.correct(jones, visu=False)

    # Finished:
    if TDL_display_Visset22: data.display(full=True)
    data.make_sinks(vdm='vdm', visu='*')        
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_WSRT_redun (mqs,parent):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    req = JEN_Meow_Utils.create_io_request(override_output_column='CORRECTED_DATA');
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
