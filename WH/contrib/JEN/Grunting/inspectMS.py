# file: ../contrib/JEN/Grunt/inspectMS.py

#========================================================================

from Timba.TDL import *
from Timba.Meq import meq
# import math

import Meow
from Timba.Contrib.JEN.Grunting import JEN_Meow_Utils    # ..temporary..

# import Grunt
from Timba.Contrib.JEN.Grunt import Visset22


#========================================================================

# Run-time menu:
JEN_Meow_Utils.include_ms_options(has_input=True,tile_sizes=[30,48,96,20,10,5,2,1]);
JEN_Meow_Utils.include_imaging_options();
  
# Compile-time menu:
TDLCompileOption('num_stations',"Number of stations",[5,27,14,3,4,5,6,7,8,9,10], more=int);
TDLCompileOption('display_object',"Display the Visset22 object", [True,False]);
TDLCompileOption('cache_policy',"Node result caching policy",[100,0], more=int);




#========================================================================
#========================================================================

def _define_forest (ns):
    """Inspect the contents of the MS"""

    array = Meow.IfrArray(ns, range(1,num_stations+1))
    observation = Meow.Observation(ns)
    vis = Visset22.Visset22(ns, label='inspectMS', array=array)
    vis.make_spigots(visu=True)
    if True:
        # Does not start by itself....?
        vis.collector()
    if False:
        # AGW still has to repair a 'dims' bug
        vis.collector_separate()
    if display_object:
        vis.display(full=True)
    vis.make_sinks(vdm='vdm')
    return True





#========================================================================
#========================================================================

def _tdl_job_1_inspect_MS (mqs,parent):
    mqs.meq('Set.Forest.State', record(state=record(cache_policy=cache_policy)))
    req = JEN_Meow_Utils.create_io_request(inhibit_output=True);
    mqs.execute('vdm',req,wait=False);
    return True
                                     
  
def _tdl_job_2_make_image (mqs,parent):
    JEN_Meow_Utils.make_dirty_image(npix=256,cellsize='1arcsec',channels=[32,1,1]);
    return True



#========================================================================
#========================================================================


if __name__ == '__main__':
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();  
  
  print len(ns.AllNodes()),'nodes defined';
