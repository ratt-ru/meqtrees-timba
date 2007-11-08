# Setup for new simulation in MeqTree. What we need for this:
# LOFAR MS (check)
# LSM (check for testing, getting final version from Niruj)
# Simulator (this script)
# Ionospheric model (from GPS, Kolmogorov or TID)

# Setup of the script
# 1. define the global hardcoded variables
# 2. set the TDL Options and MeqMaker
# 3. read the MS into MeqTree: antenna locations, frequency, time
# 4. read the LSM into MeqTree: source locations, flux
# 5. calculate the Z-jones matrix (TEC values at the pierce points)
# 6. simulate (MeqTree request)
# 7. make images and/or movies (Glish)

# Default coordinate system is long-lat
# Ionosphere is a thin layer at 400km altitude
# Earth model for ITRF to LLH or ENU conversion is WGS84

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
import math
import Meow
from Meow import Context

# 3. Read the MS into MeqTree
# and set the corresponding Compile and Runtime options 
mssel = Context.mssel = Meow.MSUtils.MSselector(has_input=True, tile_sizes=None, flags=False,hanning=True)
TDLCompileOptions(*mssel.compile_options());
TDLRuntimeMenu("MS/data selection options",*mssel.runtime_options())

# Until here I have the following questions:
# - how are the compile and runtime options defined?
# - what does the * in the statement (*mssel.bladiebla) mean?

# 2.a Set the TDL Options
# We have already got some options for the MS, but we want options to define
# what we will do in this tree: simulate, solve, subtract). This needs to be set-up
# with care, since we cannot solve and simulate at the same time, and we can only
# subtract if we have solved.

# First set the global menu, then add submenus or single options
# This is what Oleg does, need to move that into my own stuf
TDLCompileMenu("What do we want to do",
               # This is a menu with two options
               TDLMenu("Solve",
                       TDLoption('do_solve',"Solve for ionospheric parameters", False),
                       TDLoption('do_subtract',"Subtract model from observed phases",False))
               # This is a single option
               TDLOption('do_sim',"Simulate", True))

# Questions on the TDL options
# - what does the open keyword do? (see calico-wsrt.py)
# - can we automatically toggle an option off if another is toggled on and vice versa?

# 2.b Call the MeqMaker
from Meow import MeqMaker
if do_solve:
    meqmaker = MeqMaker.MeqMaker(solvable=True)
else:
    meqmaker = MeqMaker.MeqMaker(solvable=False)


# 4. Read the LSM/GSM into the meqmaker
# these will show up in the menu automatically
# for testing purposes keep the central point-source option in here
import central_point_source
# also allow to read from a LSM file
import Meow.LSM
lsm = Meow.LSM.MeowLSM(include_options=False);
meqmaker.add_sky_models([central_point_source,lsm]);

# 5. Include the Z-jones matrix
# the routine solvable_ionosphere returns the actual matrix, or in this case scalar.
# It has the proper indices, the Z-jones has to be specified with station and source.
import solvable_ionosphere
# label = Z, used to generate the NodeStub name
# name = descriptive name
# module = list of modules that contain the compute_jones function
meqmaker.add_sky_jones('Z','ionosphere'.[solvable_ionosphere.Iono()]);

# insert all the TDL options that MeqMaker has generated
TDLCompileOptions(*meqmaker.compile_options())

# Now we can start building the tree....

def _define_forest (ns):
    # First define the context in which we are working:
    ANTENNAS = mssel.get_antenna_set();
    array = Meow.IfrArray(ns,ANTENNAS,mirror_uvw=False)
    observation = Meow.Observation(ns);
    Meow.Context.set(array,observation);
    stations = array.stations();
