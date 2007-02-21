# file: ../contrib/JEN/Grunt/WSRT_solve_cps.py

# Description:

# Assume a WSRT observation of a field with a dominant point source in
# the centre of the field (i.e. a calibrator observation).
# Solve for a (subset of) the M.E. parameters in a user-defined sequence of
# uv-plane WSRT Jones matrices (from module Grunting/WSRT_Jones.py).
# The source model is a user-defined point-source.

# History:
# - 17jan2007: creation

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
from Timba.Contrib.JEN.Grunt import solving22


#========================================================================
# meqbrowser user menu-items:
#========================================================================

# Run-time menu:
JEN_Meow_Utils.include_ms_options(has_input=True, has_output='CORRECTED_DATA',
                                  tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();


# Compile-time menu:
PointSource22.include_TDL_options('cps model')  

WSRT_Jones.include_TDL_options_uvp('instrum. model')
pg = WSRT_Jones.parmgroups_uvp()
TDLCompileOption('TDL_parmgog','parmgroups to be solved for', pg, more=str);

solving22.include_TDL_options()

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
    Meow.Context.set(array, observation)
    direction = Meow.LMDirection(ns, 'cps', l=0.0, m=0.0)

    # Make a user-defined point source model, derived from the Meow.PointSource class,
    # with some extra functionality for predefined sources and solving etc.
    ps = PointSource22.PointSource22 (ns, direction=direction)
    if TDL_display_PointSource22: ps.display(full=True)

    # Create a Visset22 object with predicted uv-data:
    pred = ps.Visset22(array, observation, name='pred', visu=True)

    # Corrupt the predicted data with a sequence of Jones matrices,
    # which contain the solvable parameters. uv-plane effects only.
    #   (Note that the user-defined TDLOption parameters are
    #    short-circuited between the functions in the WSRT_Jones module)
    jones = WSRT_Jones.Joneseq22_uvp(ns, stations=array.stations())
    pred.corrupt(jones, visu=True)

    # The measured uv-data are read from the Measurement Set via spigots:
    data = Visset22.Visset22(ns, label='data', array=array)
    data.make_spigots(visu=True)

    # Create a solver for a user-defined subset of parameters (parmgroup):
    # NB: The solver gets its requests from a ReqSeq that is automatically
    #     inserted into the main-stream by data.make_sinks() below.
    solving22.make_solver(lhs=data, rhs=pred, parmgroup=TDL_parmgog)

    # Correct the data for the estimated instrumental errors
    if True:
        data.correct(jones, visu=True)
        data.show_timetracks('corrected', separate=True)                 

    # Finished:
    if TDL_display_Visset22: data.display(full=True)
    data.make_sinks(vdm='vdm')        
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_WSRT_solve_cps (mqs,parent):
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
