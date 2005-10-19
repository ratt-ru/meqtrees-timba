# MG_JEN_Antenna.py

# Short description:
#   Functions for simulating (LOFAR) station beams

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 16 oct 2005: creation

# Copyright: The MeqTree Foundation

# Full description:






#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Contrib.MXM import MG_MXM_functional

from Timba.Trees import TDL_Antenna
from Timba.Trees import TDL_Dipole
# from Timba.Contrib.MXM import MG_MXM_functional
# from Timba.Contrib.SBY import MG_SBY_dipole_beam


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_Antenna.py',
                         last_changed='h17oct2005',
                         trace=False)             # If True, produce progress messages  

MG.parm = record(height=0.25, # dipole height from ground plane, in wavelengths
                              # note that this varies with freq. in order to 
                              # model this variation, use the t,f polynomial
                              # given below
                 ntime=5,     # no. of grid points in time [0,1]
                 nfreq=5,     # no. of grid points in frequency [0,1]
                 nphi=40,     # no. of grid points in azimuth [0,2*pi]
                 ntheta=40,   # no. of grid points in declination [0,pi/2]
                              # measured from the zenith
                 debug_level=10)    # debug level

# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG)






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""
   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   if True:
      # add Azimuth and Elevation axes as the 3rd and 4th axes
      MG_MXM_functional._add_axes_to_forest_state(['A','E']);
      # create the dummy node (needed for the funklet)
      ns.dummy<<Meq.Parm([[0,1],[1,0]],node_groups='Parm');



   # Various antennas:
   
   obj = TDL_Antenna.Antenna()
   if True:
      # Make a bookmark for the sky temperature:
      node = obj.subtree_Tsky(ns)
      cc.append(node)
      MG_JEN_forest_state.bookmark(node, page='sensit')
   _experiment(ns, obj, cc)
   
   dip1 = TDL_Dipole.Dipole(polarisation='X')
   dip2 = TDL_Dipole.Dipole(polarisation='Y')
   dip3 = TDL_Dipole.Dipole(polarisation='Z')

   _experiment(ns, dip1, cc, sensit=True, beam=True)
   _experiment(ns, dip2, cc, sensit=True, beam=True)

   obj = TDL_Antenna.Feed(dip1, dip2)
   _experiment(ns, obj, cc)

   obj = TDL_Antenna.TriDipole(dip1, dip2, dip3)
   _experiment(ns, obj, cc)

   obj = TDL_Antenna.Array()
   obj.testarr()
   _experiment(ns, obj, cc)
   
   obj = TDL_Antenna.Station()
   _experiment(ns, obj, cc)


  # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc, make_bookmark=False)



#----------------------------------------------------------------------------
def _experiment(ns, obj, cc=[], dcoll=True, sensit=False, beam=False):

    if dcoll:
        node = obj.dcoll_xy(ns)
        cc.append(node)
        MG_JEN_forest_state.bookmark(node, page='dcoll_xy')

    if sensit:
        node = obj.subtree_sensit(ns)
        cc.append(node)
        MG_JEN_forest_state.bookmark(node, page='sensit')

    if beam:
        node = obj.subtree_beam(ns, height=MG.parm['height'])
        cc.append(node)
        MG_JEN_forest_state.bookmark(node, page='beam')

    return True



#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


   






#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
    """Execute the forest with a default domain"""
    return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')
    # return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')
    # return MG_JEN_exec.meqforest (mqs, parent)

def _tdl_job_4D_request (mqs,parent):
   """ evaluate beam pattern for the upper hemisphere
   for this create a grid in azimuth(phi) [0,2*pi], pi/2-elevation(theta) [0,pi/2]
   """;
   # run dummy first, to make python know about the extra axes (some magic)
   MG_MXM_functional._dummy(mqs, parent);

   time_range = [0.,1.]
   freq_range = [0.,1.]
   freq_range = [100e6,200e6]                # 100-200 MHz
   az_range = [0.,math.pi*2.0]
   el_range = [0.,math.pi/2.0]
   dom_range = [time_range, freq_range, az_range, el_range]
   nr_cells = [MG.parm['ntime'],MG.parm['nfreq'],MG.parm['nphi'],MG.parm['ntheta']]
   request = MG_MXM_functional._make_request(Ndim=4, dom_range=dom_range,
                                             nr_cells=nr_cells)

   return MG_JEN_exec.meqforest (mqs, parent, request=request)



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 1:
      rr = station_config(ns)
      MG_JEN_exec.display_object (rr, 'rr', 'station_config', full=True)
      
      

   if 0:
       MG_JEN_exec.display_object (MG, 'MG', MG.script_name)
       # MG_JEN_exec.display_subtree (rr, MG.script_name, full=1)
   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




