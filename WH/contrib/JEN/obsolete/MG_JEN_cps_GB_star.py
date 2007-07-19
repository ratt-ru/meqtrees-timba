# MG_JEN_cps_GB_star.py

# Short description:
#   Script for sequential (star-config) G-B solution
#   for a central point source (cps), i.e. a calibrator source

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 19 dec 2005: converted to JEN_inarg
# - 03 jan 2006: num_cells

# Copyright: The MeqTree Foundation

# Detailed description:
#   The uv-data are first solved for GJones (phase/gain),
#     with a time resolution of 1 time-slot (1-2 minutes)
#   Then they are then solved for BJones (bandpass),
#     with a slower time resolution of, say, 1 hour.
#   The result is uv-data that is corrected for uv-plane effects,
#     i.e. phase, gain and bandpass for the brightest (cps) source.
#   Optionally, the central source may be subtracted...
#
# Remarks:
# - The difference with MG_JEN_cps_GBJones is that the two solvers
#   are attached to the same reqseq, in a star-configuration
#   This avoids one solver being the child of another....

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

MG = JEN_inarg.init('MG_JEN_cps_GB_star',
                    last_changed = 'd02jan2006',
                    punit='unpol',                     # name of calibrator source/patch
                    polrep='linear',                   # polarisation representation (linear/circular)
                    # polrep='circular',                 # polarisation representation (linear/circular)
                    stations=range(4),                 # specify the (subset of) stations to be used
                    insert_solver_GBJones=True,        # if True, insert GBJones solver
                    solver_subtree_GJones=True,        # if True, include GJones solver
                    solver_subtree_BJones=True,        # if True, include BJones solver
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
                 # ms_name='A963.MS',
                 # selection_string='TIME_CENTROID<4615466159.46',
                 tile_size=10,
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
# Specify arguments for functions related to the G and BJones solvers:
#----------------------------------------------------------------------------------------------------

if MG['insert_solver_GBJones']:

    qual = None
    
    # Specify the sequence of zero or more (corrupting) Jones matrices:
    Jsequence = ['GJones','BJones'] 
    
    inarg = MG_JEN_Cohset.JJones(_getdefaults=True, _qual=qual, expect=Jsequence) 
    JEN_inarg.modify(inarg,
                     stations=MG['stations'],               # List of array stations
                     parmtable=MG['parmtable'],             # MeqParm table name
                     polrep=MG['polrep'],                   # polarisation representation
                     Jsequence=Jsequence,                   # Sequence of corrupting Jones matrices 
                     _JEN_inarg_option=None)                # optional, not yet used 
    if 'GJones' in Jsequence: 
        JEN_inarg.modify(inarg,
                         fdeg_Ggain=0,                      # degree of default freq polynomial         
                         fdeg_Gphase='fdeg_Ggain',          # degree of default freq polynomial          
                         tdeg_Ggain=0,                      # degree of default time polynomial         
                         tdeg_Gphase='tdeg_Ggain',          # degree of default time polynomial       
                         subtile_size_Ggain=1,                 # used in tiled solutions         
                         subtile_size_Gphase='subtile_size_Ggain', # used in tiled solutions         
                         _JEN_inarg_option=None)            # optional, not yet used 
    if 'BJones' in Jsequence: 
        JEN_inarg.modify(inarg,
                         fdeg_Breal=5,                      # degree of default freq polynomial        
                         fdeg_Bimag='fdeg_Breal',           # degree of default freq polynomial          
                         tdeg_Breal=1,                      # degree of default time polynomial         
                         tdeg_Bimag='tdeg_Breal',           # degree of default time polynomial    
                         subtile_size_Breal=0,                 # used in tiled solutions         
                         subtile_size_Bimag='subtile_size_Breal', # used in tiled solutions         
                         _JEN_inarg_option=None)            # optional, not yet used 
    JEN_inarg.attach(MG, inarg)


    inarg = MG_JEN_Cohset.predict(_getdefaults=True, _qual=qual)  
    JEN_inarg.modify(inarg,
                     ifrs=MG['ifrs'],                       # list of Cohset ifrs 
                     polrep=MG['polrep'],                   # polarisation representation
                     _JEN_inarg_option=None)                # optional, not yet used 
    JEN_inarg.attach(MG, inarg)


    # Make qualified .solver_subtree() inargs, and remember their qual-strings:
    solver_subtree_qual = []                                 # input for .insert_solver()
    ss_inarg = dict()

    # Make the .solver_subtree() inarg for the BJones solution (if required)
    if MG['solver_subtree_GJones']:
        qual = 'GJones'
        # Extra condition equations to be used:
        condition = []
        condition.append('Gphase_X_sum=0.0')
        condition.append('Gphase_Y_sum=0.0')
        solver_subtree_qual.append(qual)
        ss_inarg[qual] = MG_JEN_Cohset.solver_subtree(_getdefaults=True, _qual=qual) 
        JEN_inarg.modify(ss_inarg[qual],
                         # solvegroup=['GJones'],             # list of solvegroup(s) to be solved for
                         solvegroup=['Gphase'],             # list of solvegroup(s) to be solved for
                         # condition=[],                      # list of names of extra condition equations
                         condition=condition,               # list of names of extra condition equations
                         rmin=200,                          # if specified, only use baselines>=rmin 
                         # rmax=None,                         # if specified, only use baselines<=rmax
                         # num_iter=20,                       # max number of iterations
                         # epsilon=1e-4,                      # iteration control criterion
                         # debug_level=10,                    # solver debug_level
                         visu=True,                         # if True, include visualisation
                         history=True,                      # if True, include history collection of metrics 
                         _JEN_inarg_option=None)            # optional, not yet used 
         

    # Make the .solver_subtree() inarg for the BJones solution (if required)
    if MG['solver_subtree_BJones']:
        qual = 'BJones'
        # Extra condition equations to be used:
        condition = []
        condition.append('Bimag_X_sum=0.0')
        condition.append('Bimag_Y_sum=0.0')
        solver_subtree_qual.append(qual)
        ss_inarg[qual] = MG_JEN_Cohset.solver_subtree(_getdefaults=True, _qual=qual) 
        JEN_inarg.modify(ss_inarg[qual],
                         solvegroup=['BJones'],             # list of solvegroup(s) to be solved for
                         # condition=[],                      # list of names of extra condition equations
                         condition=condition,               # list of names of extra condition equations
                         rmin=200,                          # if specified, only use baselines>=rmin 
                         # rmax=None,                         # if specified, only use baselines<=rmax
                         # num_iter=20,                       # max number of iterations
                         # epsilon=1e-4,                      # iteration control criterion
                         # debug_level=10,                    # solver debug_level
                         visu=True,                         # if True, include visualisation
                         history=True,                      # if True, include history collection of metrics 
                         _JEN_inarg_option=None)            # optional, not yet used 


    # Make the inarg for the .insert_solver()
    inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, _qual=None) 
    JEN_inarg.modify(inarg,
                     solver_subtree=solver_subtree_qual,     # list of .solver_subtree() inarg qualifiers
                     visu=True,                              # if True, include visualisation
                     subtract=True,                          # if True, subtract 'predicted' from uv-data 
                     correct=True,                           # if True, correct the uv-data with 'predicted.Joneset()'
                     # num_cells=None,                       # if defined, ModRes argument [ntime,nfreq]
                     _JEN_inarg_option=None)                 # optional, not yet used 
    # Attach the .solver_subtree() inargs AFTER modification:
    localscope = JEN_inarg.localscope(inarg)
    for qual in solver_subtree_qual:
        JEN_inarg.attach(inarg[localscope], ss_inarg[qual])
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

    # Model of the calibrator source:
    Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=MG['punit'])

    if MG['insert_solver_GBJones']:
        # Insert the (fast) GJones solver (and correct the uv-data):
        Joneset =  MG_JEN_Cohset.JJones(ns, Sixpack=Sixpack, _inarg=MG)
        predicted =  MG_JEN_Cohset.predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)
        MG_JEN_Cohset.insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG)

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




