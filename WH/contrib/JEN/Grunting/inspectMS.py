# file: ../contrib/JEN/Grunt/inspectMS.py

# Description:
# Inspect the data in a Measurement Set in various ways.
# The data is NOT written back.

# History:
# - 14jan2007: creation
# - 09jun2007: adapted to new TDLOptions

# Copyright: The MeqTree Foundation

#========================================================================
# Preamble:
#========================================================================

from Timba.TDL import *
from Timba.Meq import meq
# import math

import Meow
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..

# import Grunt
from Timba.Contrib.JEN.Grunt import Visset22


#========================================================================
# meqbrowser user menu-items:
#========================================================================

# Run-time menu:
JEN_Meow_Utils.include_ms_options(has_input=True, has_output=False,
                                  tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();
  
# Compile-time menu:
TDLCompileOption('TDL_num_stations',"Number of stations",[5,27,14,3,4,5,6,7,8,9,10], more=int);
TDLCompileMenu('Print extra information',
               TDLCompileOption('TDL_display_Visset22',"Display the Visset22 object", [True,False]),
               );
TDLCompileOption('TDL_cache_policy',"Node result caching policy",[100,0], more=int);




#========================================================================
# Tree definition:
#========================================================================

def _define_forest (ns):
    """Define the MeqTree forest."""

    array = Meow.IfrArray(ns, range(1,TDL_num_stations+1))
    observation = Meow.Observation(ns)
    Meow.Context.set(array, observation)

    data = Visset22.Visset22(ns, name='inspectMS', array=array)
    data.make_spigots(visu=True)

    data.visualize(visu='*', separate=True)
    data.bookpage(9)

    # Insert array configuration visualisation here.....?
    # Keep the relevant functions in this script?

    # closure phase

    # autocorrelations

    # select ifrs

    # simulate rain effects (grounf reflectivity)

    # redundancy tables (CS1, WSRT)

    # All kinds of differences (show_timetracks)

    # Finished:
    if TDL_display_Visset22: data.display(full=True)
    global vdm_nodename
    vdm_nodename = data.make_sinks(vdm='vdm')
    return True





#========================================================================
# Routines for the TDL execute menu:
#========================================================================

def _tdl_job_1_inspect_MS (mqs,parent):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=TDL_cache_policy)))
    req = JEN_Meow_Utils.create_io_request(override_output_column=None);
    mqs.execute(vdm_nodename, req, wait=False);
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
