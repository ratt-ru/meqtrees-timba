# MG_JEN_cps_GJones.py

# Short description:
#   General (universal?) GJones solution script
#   for a central point source (cps), i.e. a calibrator source

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 19 dec 2005: converted to JEN_inarg
# - 03 jan 2006: num_cells

# Copyright: The MeqTree Foundation 

#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble *********************************************
#********************************************************************************
#********************************************************************************

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
# from Timba.Meq import meq

from numarray import *

from Timba.Trees import JEN_inarg
from Timba.Trees import TDL_Cohset
from Timba.Trees import TDL_Joneset
# from Timba.Trees import TDL_Sixpack

from Timba.Contrib.JEN import MG_JEN_Cohset
from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_historyCollect
from Timba.Contrib.JEN import MG_JEN_flagger





#********************************************************************************
#********************************************************************************
#****************** PART II: Definition of importable functions *****************
#********************************************************************************
#********************************************************************************





#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************


#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

# punit = 'unpol'
# punit = 'unpol2'
# punit = '3c147'
# punit = 'RMtest'
# punit = 'QUV'
# punit = 'QU'
# punit =  'SItest'
# punit = 'unpol10'

MG = JEN_inarg.init('MG_JEN_cps_GJones',
                    last_changed = 'd19dec2005',
                    punit='unpol10',                   # name of calibrator source/patch
                    polrep='linear',                   # polarisation representation (linear/circular)
                    # polrep='circular',                 # polarisation representation (linear/circular)
                    stations=range(4),                 # specify the (subset of) stations to be used
                    redun=False,                       # if True, use redundant baseline calibration
                    master_reqseq=False,               # if True, use a master reqseq for solver(s)
                    chain_solvers=True,                # if True, chain the solver(s)
                    parmtable=None)                    # name of MeqParm table

# Derive a list of ifrs from MG['stations'] (used below):
MG['ifrs'] = TDL_Cohset.stations2ifrs(MG['stations'])



#----------------------------------------------------------------------------------------------------
# Specify arguments for data stream control:
#----------------------------------------------------------------------------------------------------

inarg = MG_JEN_exec.stream_control(_getdefaults=True)
JEN_inarg.modify(inarg,
                 tile_size=11,
                 _JEN_inarg_option=None)     
JEN_inarg.attach(MG, inarg)


inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
JEN_inarg.modify(inarg,
                 # MS_corr_index=[0,-1,-1,1],       # only XX/YY available
                 # MS_corr_index=[0,-1,-1,3],       # all available, use only XX/YY
                 MS_corr_index=[0,1,2,3],           # all corrs available, use all
                 # flag=False,                        # if True, flag the input data
                 visu=True,                         # if True, visualise the input data
                 _JEN_inarg_option=None)            # optional, not yet used 
JEN_inarg.attach(MG, inarg)
                 


inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
JEN_inarg.modify(inarg,
                 output_col='PREDICT',              # logical (tile) output column
                 visu_array_config=True,            # if True, visualise the array config (from MS)
                 # flag=False,                        # if True, flag the input data
                 visu=True,                         # if True, visualise the input data
                 _JEN_inarg_option=None)            # optional, not yet used 
JEN_inarg.attach(MG, inarg)
                 





#----------------------------------------------------------------------------------------------------
# Specify arguments for solver-related functions:
#----------------------------------------------------------------------------------------------------


# Specify the name qualifier for (the inarg records of) this 'predict and solve' group.
# NB: The same qualifier should be used when using the functions in _define_forest()
qual = None

# Specify the sequence of zero or more (corrupting) Jones matrices:
Jsequence = ['GJones'] 

# Specify a list of MeqParm solvegroup(s) to be solved for:
solvegroup = ['GJones']
# solvegroup = ['Gphase']

# Extra condition equations to be used:
condition = []
condition.append('Gphase_X_sum=0.0')
condition.append('Gphase_Y_sum=0.0')


inarg = MG_JEN_Cohset.JJones(_getdefaults=True, _qual=qual, expect=Jsequence) 
JEN_inarg.modify(inarg,
                 stations=MG['stations'],               # List of array stations
                 parmtable=MG['parmtable'],             # MeqParm table name
                 unsolvable=False,                      # If True, no solvegroup info is kept
                 polrep=MG['polrep'],                   # polarisation representation
                 Jsequence=Jsequence,                   # Sequence of corrupting Jones matrices 
                 _JEN_inarg_option=None)                # optional, not yet used 
if 'GJones' in Jsequence: 
    JEN_inarg.modify(inarg,
                     # MeqParm solving instructions:
                     fdeg_Ggain=0,                      # degree of default freq polynomial         
                     fdeg_Gphase='fdeg_Ggain',          # degree of default freq polynomial          
                     tdeg_Ggain=0,                      # degree of default time polynomial         
                     tdeg_Gphase='tdeg_Ggain',          # degree of default time polynomial       
                     subtile_size_Ggain=0,                 # used in tiled solutions         
                     subtile_size_Gphase='subtile_size_Ggain', # used in tiled solutions         
                     # ** MeqParm default values:
                     c00_Ggain=2.0,                     # default c00 funklet value
                     c00_Gphase=0.5,                    # default c00 funklet value
                     stddev_Ggain=0.0,                  # scatter in default c00 funklet values
                     stddev_Gphase=0.0,                 # scatter in default c00 funklet values
                     # ft_coeff_scale=0.0,                # scale of polc_ft non-c00 coeff
                     _JEN_inarg_option=None)            # optional, not yet used 
JEN_inarg.attach(MG, inarg)




inarg = MG_JEN_Cohset.predict(_getdefaults=True, _qual=qual)  
JEN_inarg.modify(inarg,
                 ifrs=MG['ifrs'],                       # list of Cohset ifrs 
                 polrep=MG['polrep'],                   # polarisation representation
                 _JEN_inarg_option=None)                # optional, not yet used 
JEN_inarg.attach(MG, inarg)


inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, _qual=qual) 
JEN_inarg.modify(inarg,
                 subtract=False,                    # if True, subtract 'predicted' from uv-data 
                 correct=True,                      # if True, correct the uv-data with 'predicted.Joneset()'
                 visu=True,                         # if True, include visualisation
                 # num_cells=None,                    # if defined, ModRes argument [ntime,nfreq]
                 # ** Arguments for .solver_subtree()
                 solvegroup=solvegroup,             # list of solvegroup(s) to be solved for
                 # condition=[],                      # list of names of extra condition equations
                 condition=condition,               # list of names of extra condition equations
                 # num_iter=20,                       # max number of iterations
                 # epsilon=1e-4,                      # iteration control criterion
                 # debug_level=10,                    # solver debug_level
                 history=True,                      # if True, include history collection of metrics 
                 _JEN_inarg_option=None)            # optional, not yet used 
JEN_inarg.attach(MG, inarg)
                 









#====================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG['script_name'])








#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns):

    # Perform some common functions, and return an empty list (cc=[]):
    cc = MG_JEN_exec.on_entry (ns, MG)

    # Make MeqSpigot nodes that read the MS:
    Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                               polrep=MG['polrep'],
                               ifrs=MG['ifrs'])
    MG_JEN_Cohset.make_spigots(ns, Cohset, _inarg=MG)

    # Make a Cohset with predicted (corrupted) uv-data:
    qual = None
    Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=MG['punit'])
    Joneset =  MG_JEN_Cohset.JJones(ns, Sixpack=Sixpack, _inarg=MG, _qual=qual)
    predicted =  MG_JEN_Cohset.predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG, _qual=qual)
    
    # Insert the solver:
    MG_JEN_Cohset.insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG, _qual=qual)

    # Make MeqSink nodes that write the MS:
    sinks =  MG_JEN_Cohset.make_sinks(ns, Cohset, _inarg=MG)
    cc.extend(sinks)

    # Finished: 
    return MG_JEN_exec.on_exit (ns, MG, cc)




#********************************************************************************
#********************************************************************************
#*******************  PART V: Forest execution routine(s) ***********************
#********************************************************************************
#********************************************************************************



def _test_forest (mqs, parent):
   
   # Timba.TDL.Settings.forest_state is a standard TDL name. 
   # This is a record passed to Set.Forest.State. 
   Settings.forest_state.cache_policy = 100;
   
   # Make sure our solver root node is not cleaned up
   Settings.orphans_are_roots = True;

   # Start the sequence of requests issued by MeqSink:
   # MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG['stream_control'])
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG)
   return True






#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routine(s) ***********************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG['script_name'],':\n'

    # This is the default:
    if 1:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

    # This is the place for some specific tests during development.
    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG['script_name'], ifrs=ifrs)


    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




