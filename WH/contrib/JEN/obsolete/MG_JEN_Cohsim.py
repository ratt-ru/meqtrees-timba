# MG_JEN_Cohset.py

# Short description:
#   Functions dealing with Cohsets of simulated uv-data  

# Keywords: ....

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 15 dec 2005: creation, copied from MG_JEN_Cohset.py

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
# from Timba.Trees import TDL_Joneset
# from Timba.Trees import TDL_Sixpack

from Timba.Contrib.JEN import MG_JEN_Cohset
# from Timba.Contrib.JEN import MG_JEN_Joneset
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


#======================================================================================
# Make spigots and sinks (plus some common services)
#======================================================================================


def simul_spigots(ns=None, Cohset=None, **inarg):

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohsim::simul_spigots()', version='25dec2005')
    pp.setdefault('MS_corr_index', [0,1,2,3])
    pp.setdefault('visu', False)
    pp.setdefault('flag', False)
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Simulate MeqSpigots:
    # Cohset.spigots(ns, MS_corr_index=pp['MS_corr_index'])
    # spigots = Cohset.nodes()

    # Create the nodes expected by read_MS_auxinfo.py 
    MG_JEN_Cohset.MSauxinfo().create_nodes(ns)

    # Append the initial (spigot) Cohset to the forest state object:
    MG_JEN_forest_state.object(Cohset, funcname)

    # Optional: visualise the spigot (input) data:
    if pp['visu']:
	MG_JEN_Cohset.visualise (ns, Cohset)
	MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')
        
    # Optional: flag the spigot (input) data:
    if pp['flag']:
       MG_JEN_Cohset.insert_flagger (ns, Cohset, scope='spigots',
                       unop=['Real','Imag'], visu=False)
       if pp['visu']: MG_JEN_Cohset.visualise (ns, Cohset)

    # Return a list of spigot nodes:
    return spigots


#--------------------------------------------------------------------------


def simul_sinks(ns=None, Cohset=None, **inarg):

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohsim::simul_sinks()', version='25dec2005')
    pp.setdefault('visu_array_config', True)
    pp.setdefault('visu', False)
    pp.setdefault('flag', False)
    pp.setdefault('output_col', 'PREDICT')
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Change the scope (name) for visualisation etc:
    Cohset.scope('simul_sinks')

    # Optional: flag the sink (output) data:
    if pp['flag']:
       MG_JEN_Cohset.insert_flagger (ns, Cohset, scope='sinks',
                       unop=['Real','Imag'], visu=False)

    # Optional: visualise the sink (output) data:
    if pp['visu']:
       MG_JEN_Cohset.visualise (ns, Cohset)
       MG_JEN_Cohset.visualise (ns, Cohset, type='spectra')

    # Attach array visualisation nodes:
    start = []
    if pp['visu_array_config']:
       dcoll = MG_JEN_Cohset.MSauxinfo.dcoll(ns)
       for i in range(len(dcoll)):
          MG_JEN_forest_state.bookmark(dcoll[i], page='MSauxinfo_array_config')
       start.extend(dcoll)

    # Attach any collected hcoll/dcoll nodes:
    post = Cohset.coll(clear=True)               

    # Simulate MeqSinks
    # Cohset.sinks(ns, start=start, post=post, output_col=pp['output_col'])
    sinks = Cohset.nodes()
    
    # Append the final Cohset to the forest state object:
    MG_JEN_forest_state.object(Cohset, funcname)
    
    # Return a list of sink nodes:
    return sinks





#---------------------------------------------------------------------------------

def addnoise (ns=None, Cohset=None, **inarg):
    """Add gaussian noise to the coherency matrices in Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::addnoise()', version='25dec2005')
    pp.setdefault('stddev', 1.0)                      # stddev of the noise
    pp.setdefault('unop', 'Exp')                      # Unary operation on the noise
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        nsub = ns.Subscope('addnoise', s1=s12[0], s2=s12[1])
        noise = MG_JEN_twig.gaussnoise (nsub, dims=Cohset.dims(),
                                        stddev=pp['stddev'], unop=pp['unop'])
        coh = ns.noisy(s1=s12[0], s2=s12[1]) << Meq.Add(Cohset[key], noise)
        Cohset[key] = coh

    # Finished:
    s = funcname
    s = s+', stddev='+str(pp['stddev'])
    s = s+', unop='+str(pp['unop'])
    Cohset.history(s)
    MG_JEN_forest_state.history (funcname)
    return True




#--------------------------------------------------------------------------------
# Produce a Cohset for the specified ifrs, with simulated uv-data: 

def simulate(ns=None, ifrs=None, Sixpack=None, **inarg):
   """Make a Cohset with simulated uv-data"""

   # Input arguments: 
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::simulate()', version='25dec2005')
   pp.setdefault('jones', [])
   pp.setdefault('stddev_noise', 0.0)
   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)

   if not Sixpack: Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')

   # Recommended ways to mark nodes that contains simulated data: 
   scope = 'simulated'           # mark the Cohset/Jonesets (visualisation)
   nsim = ns.Subscope('_')       # prepend all simulation nodes with _:: 

   # Optional: corrupt the uvdata with simulated jones matrices: 
   if not isinstance(pp['jones'], (list,tuple)): pp['jones'] = [pp['jones']]
   if len(pp['jones'])>0:
       stations = TDL_Cohset.ifrs2stations(ifrs) 
       jseq = TDL_Joneset.Joneseq()
       for jones in pp['jones']:
           if jones=='G':
              jseq.append(MG_JEN_Joneset.GJones (nsim, _inarg=pp))
           elif jones=='B':
              jseq.append(MG_JEN_Joneset.BJones (nsim, _inarg=pp))
           elif jones=='F':
              jseq.append(MG_JEN_Joneset.FJones (nsim, _inarg=pp))
           elif jones=='D':
              jseq.append(MG_JEN_Joneset.DJones_WSRT (nsim, _inarg=pp))
           elif jones=='K':
              # NB: Note that we are NOT using nodescope nsim here, because the array coordinate
              #     nodes (for uvw) have predefined names). This probably means that we cannot
              #     solve for station positions until we have addressed this problem....
              #     In any case, KJones does not produce any solvegroups....
              jseq.append(MG_JEN_Joneset.KJones (ns, Sixpack=Sixpack, _inarg=pp)) 

           else:
              print '** jones not recognised:',jones,'from:',pp['jones']
               
       # Matrix-multiply the collected jones matrices in jseq to a 2x2 Joneset:
       global simulated_JJones
       simulated_JJones = jseq.make_Joneset(nsim)
       MG_JEN_forest_state.object(jseq, funcname)
       MG_JEN_forest_state.object(simulated_JJones, funcname)

   # Make the Cohset with simulated/corrupted uvdata:
   Cohset = predict (nsim, Sixpack=Sixpack, Joneset=simulated_JJones)

   # Add some gaussian noise to the data
   # (NB: More advanced noise may be added to the Cohset after this function)
   if (pp['stddev_noise']>0): addnoise (ns, Cohset, stddev=pp['stddev_noise'])

   MG_JEN_forest_state.object(Cohset, funcname)
   return Cohset











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

MG = JEN_inarg.init('MG_JEN_Cohset',
                    last_changed = 'd13dec2005',
                    punit='unpol10',                   # name of calibrator source/patch
                    polrep='linear',                   # polarisation representation (linear/circular)
                    stations=range(4),                 # specify the (subset of) stations to be used
                    parmtable=None)                    # name of MeqParm table

# Derive a list of ifrs from MG['stations'] (used below):
MG['ifrs'] = TDL_Cohset.stations2ifrs(MG['stations'])


#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

#=======
if True:                                               # ... Copied from MG_JEN_Cohset.py ...
   MG['stream_control'] = dict(ms_name='D1.MS',
                               data_column_name='DATA',
                               tile_size=10,                   # input tile-size
                               channel_start_index=10,
                               channel_end_index=50,           # -10 should indicate 10 from the end (OMS...)
                               # output_col='RESIDUALS')
                               predict_column='CORRECTED_DATA')

   # inarg = MG_JEN_Cohsim.simul_spigots(_getdefaults=True) 
   inarg = simul_spigots(_getdefaults=True)             # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # MS_corr_index=[0,-1,-1,1],       # only XX/YY available
                    # MS_corr_index=[0,-1,-1,3],       # all available, use only XX/YY
                    MS_corr_index=[0,1,2,3],           # all corrs available, use all
                    # flag=False,                        # if True, flag the input data
                    visu=True,                         # if True, visualise the input data
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 

   # inarg = MG_JEN_Cohsim.simul_sinks(_getdefaults=True)    
   inarg = simul_sinks(_getdefaults=True)               # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    output_col='PREDICT',              # logical (tile) output column
                    visu_array_config=True,            # if True, visualise the array config (from MS)
                    # flag=False,                        # if True, flag the input data
                    visu=True,                         # if True, visualise the input data
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 



#----------------------------------------------------------------------------------------------------
# Operations on the raw uv-data:
#----------------------------------------------------------------------------------------------------

if False:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.insert_flagger(_getdefaults=True)
   inarg = insert_flagger(_getdefaults=True)            # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # sigma=5.0,                         # flagged if exceeds sigma*stddev
                    # unop='Abs',                        # unop used to make real data
                    # oper='GT',                         # decision function (GT=Greater Than)
                    # flag_bit=1,                        # affected flag-bit
                    # merge=True,                        # if True, merge the flags of 4 corrs
                    # compare=False,                     # ....
                    # visu=False,                        # if True, visualise the result
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
   


#----------------------------------------------------------------------------------------------------
# Insert a solver:
#----------------------------------------------------------------------------------------------------

#========
if True:                                               # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.JJones(_getdefaults=True)     
   inarg = JJones(_getdefaults=True)                    # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    stations=MG['stations'], 
                    parmtable=MG['parmtable'],
                    solvable=True,
                    polrep=MG['polrep'],               # polarisation representation
                    # sequence=['GJones'],                       # Succession of Jones matrices 
                    # sequence=['DJones_WSRT'],                       # Succession of Jones matrices 
                    sequence=['GJones','DJones_WSRT'],                   # Succession of Jones matrices 

                    # Insert non-default Jones matrix arguments here: 
                    #    (This is easiest by copying lines from MG_JEN_Joneset.py)
                    # NB: The arguments are used only if the corresponding Jones matrices
                    #     are specified with the 'sequence' argument. Otherwise they are ignored.
                    # GJones ..................................................
                    Gphase_constrain=True,             # if True, constrain 1st station phase
                    fdeg_Ggain=5,                      # degree of default freq polynomial         
                    fdeg_Gphase='fdeg_Ggain',          # degree of default freq polynomial          
                    tdeg_Ggain=0,                      # degree of default time polynomial         
                    tdeg_Gphase='tdeg_Ggain',          # degree of default time polynomial       
                    tile_size_Ggain=0,                 # used in tiled solutions         
                    tile_size_Gphase='tile_size_Ggain', # used in tiled solutions         
                    # DJones_WSRT ..................................................
                    fdeg_dang=1,                       # degree of default freq polynomial
                    fdeg_dell='fdeg_dang',             # degree of default freq polynomial
                    tdeg_dang=0,                       # degree of default time polynomial
                    tdeg_dell='tdeg_dang',             # degree of default time polynomial
                    tile_size_dang=0,                  # used in tiled solutions         
                    tile_size_dell='tile_size_dang',   # used in tiled solutions         
                    # BJones ..................................................
                    Breal_constrain=False,             # if True, constrain 1st station phase
                    Bimag_constrain=True,              # if True, constrain 1st station phase
                    fdeg_Breal=3,                      # degree of default freq polynomial        
                    fdeg_Bimag='fdeg_Breal',           # degree of default freq polynomial          
                    tdeg_Breal=0,                      # degree of default time polynomial         
                    tdeg_Bimag='tdeg_Breal',           # degree of default time polynomial    
                    tile_size_Breal=0,                 # used in tiled solutions         
                    tile_size_Bimag='tile_size_Breal', # used in tiled solutions         
                    # FJones .................................................. 
                    fdeg_RM=0,                         # degree of default freq polynomial          
                    tdeg_RM=0,                         # degree of default time polynomial         
                    tile_size_RM=1,                    # used in tiled solutions         
                    #..................................................
                    
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


   # inarg = MG_JEN_Cohset.predict(_getdefaults=True)  
   inarg = predict(_getdefaults=True)                   # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    ifrs=MG['ifrs'],                   # list of Cohset ifrs 
                    polrep=MG['polrep'],               # polarisation representation
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


   #========
   if True:                                                # ... Copied from MG_JEN_Cohset.py ...
       # inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True) 
       inarg = insert_solver(_getdefaults=True)             # local (MG_JEN_Cohset.py) version 
       JEN_inarg.modify(inarg,
                        # solvegroup=['GJones'],             # list of solvegroup(s) to be solved for
                        # solvegroup=['DJones'],             # list of solvegroup(s) to be solved for
                        solvegroup=['GJones','DJones'],    # list of solvegroup(s) to be solved for
                        # num_cells=None,                    # if defined, ModRes argument [ntime,nfreq]
                        # num_iter=20,                       # max number of iterations
                        # epsilon=1e-4,                      # iteration control criterion
                        # debug_level=10,                    # solver debug_level
                        visu=True,                         # if True, include visualisation
                        history=True,                      # if True, include history collection of metrics 
                        subtract=False,                    # if True, subtract 'predicted' from uv-data 
                        correct=True,                      # if True, correct the uv-data with 'predicted.Joneset()'
                        _JEN_inarg_option=None)            # optional, not yet used 
       JEN_inarg.attach(MG, inarg)
                 





#----------------------------------------------------------------------------------------------------
# Simulation (no MS): 
#----------------------------------------------------------------------------------------------------

#========
if False:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.simulate(_getdefaults=True)   
   inarg = simulate(_getdefaults=True)                  # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    #..............
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


#========
if False:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.addnoise(_getdefaults=True) 
   inarg = addnoise(_getdefaults=True)                  # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # stddev=1.0,                        # stddev of the noise
                    # unop='Exp',                        # Unary operation on the noise
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

   if True:
      # Make simulated  uv-data for the given source:
      Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=MG['punit'])
      Joneset = JJones(ns, Sixpack=Sixpack, _inarg=MG)
      Cohset = predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)

   if False:
       addnoise(ns, Cohset, **MG)

   if False:
      insert_flagger (ns, Cohset, scope='residual', unop=['Real','Imag'], visu=True)
      visualise (ns, Cohset)
      visualise (ns, Cohset, type='spectra')


   if False:
      # Make predicted uv-data for the given source:
      punit = MG['punit']
      # punit = ... other punit ....
      Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=punit)
      Joneset = JJones(ns, Sixpack=Sixpack, _inarg=MG)
      predicted = predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)
      if False:
          # Insert a solver for a named group of MeqParms (e.g. 'GJones'):
          insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG)
          visualise (ns, Cohset)
          visualise (ns, Cohset, type='spectra')
 
   if True:
      # Tie the trees for the simulated ifrs together in an artificial 'sink':
      cc.append(Cohset.simul_sink(ns))


   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)




#********************************************************************************
#********************************************************************************
#*******************  PART V: Forest execution routine(s) ***********************
#********************************************************************************
#********************************************************************************



def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)


# Execute the forest for a sequence of requests:

def _tdl_job_sequence(mqs, parent):
    for x in range(10):
        MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                               f1=x, f2=x+1, t1=x, t2=x+1,
                               save=False, trace=False, wait=False)
    MG_JEN_exec.save_meqforest(mqs) 
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

    if 0:   
       cs.display('initial')
       
    if 0:
       cs.spigots (ns)


    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




