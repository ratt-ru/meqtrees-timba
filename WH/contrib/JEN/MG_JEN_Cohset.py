# MG_JEN_Cohset.py

# Short description:
#   Functions dealing with sets (all ifrs) of 2x2 cohaerency matrices 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 05 sep 2005: adapted to Cohset/Joneset objects
# - 25 nov 2005: MS_corr_index argument to .make_spigots()
# - 05 dec 2005: included TDL_MSauxinfo services
# - 07 dec 2005: converted to JEN_inarg

# Copyright: The MeqTree Foundation 

#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *

from Timba.Trees import JEN_inarg
from Timba.Trees import TDL_Cohset
from Timba.Trees import TDL_Joneset
from Timba.Trees import TDL_MSauxinfo
# from Timba.Trees import TDL_Sixpack
from Timba.Contrib.JEN import MG_JEN_Joneset
from Timba.Contrib.JEN import MG_JEN_Sixpack

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_historyCollect
from Timba.Contrib.JEN import MG_JEN_flagger


#-------------------------------------------------------------------------
# MG control record (may be edited here)

MG = MG_JEN_exec.MG_init('MG_JEN_Cohset.py', last_changed = 'd07dec2005')



#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG.script_name)


#-------------------------------------------------------------------------
# The MSauxinfo object contains auxiliary MS info (nodes):
# It is used at various points in this module, e.g. make_sinks()

MSauxinfo = TDL_MSauxinfo.MSauxinfo(label=MG.script_name)
MSauxinfo.station_config_default()           # WSRT (15 stations), incl WHAT






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   # Make the Cohset ifrs (and the Joneset stations):
   ifrs = TDL_Cohset.stations2ifrs(range(0,5))
   stations = TDL_Cohset.ifrs2stations(ifrs)

   # Source/patch to be used for simulation/selfcal:
   punit = 'unpol'
   # punit = 'unpol2'
   # punit = '3c147'
   # punit = 'RMtest'
   # punit = 'QUV'
   # punit = 'QU'
   # punit =  'SItest'
   # Get the 6 punit subtrees:
   Sixpack = MG_JEN_Sixpack.newstar_source (ns, name=punit)

   # Make a Cohset for the specified ifrs, with simulated uv-data: 
   jones = ['G']
   # jones = ['D']
   # jones = ['G','D']
   jones  = ['B']  
   Cohset = simulate(ns, ifrs, Sixpack=Sixpack, jones=jones)
   visualise (ns, Cohset)
   visualise (ns, Cohset, type='spectra')

   if False:
       # Check by correcting with the corrupting JJones:
       global simulated_JJones                               # see .simulate()
       Cohset.correct(ns, simulated_JJones)
       visualise (ns, Cohset)
       visualise (ns, Cohset, type='spectra')

   if False:
       insert_flagger (ns, Cohset, scope='residual', unop=['Real','Imag'], visu=True)
       visualise (ns, Cohset)
       visualise (ns, Cohset, type='spectra')

   if False:
       # Insert a solver for a named group of MeqParms (e.g. 'GJones'):
       jones = ['G']
       # punit = 'QUV'
       punit = 'unpol10'
       Joneset = JJones(ns, stations, Sixpack=Sixpack, jones=jones)
       predicted = predict (ns, Sixpack=Sixpack, ifrs=ifrs, Joneset=Joneset)
       sgname = 'GJones'
       # sgname = 'DJones'
       # sgname = ['DJones', 'GJones']

       # Either correct the Cohset data, or subtract (or both?)
       if True:
           correct = Joneset
           subtract = None
       else:
           correct = None
           subtract = predicted

       insert_solver (ns, solvegroup=sgname, measured=Cohset, predicted=predicted, 
                      correct=correct, subtract=subtract, num_iter=10)
           
       visualise (ns, Cohset)
       visualise (ns, Cohset, type='spectra')
 
   if False:
       # Insert another solver for a different group of MeqParms (e.g. 'DJones'):
       # NB: Concatenating solvers this way causes problems...
       DJoneset = JJones(ns, stations, Sixpack=Sixpack, jones=['D'])
       Dpredicted = predict (ns, Sixpack=Sixpack, ifrs=ifrs, Joneset=DJoneset)
       insert_solver (ns, solvegroup='DJones', measured=Cohset, predicted=Dpredicted, 
                               correct = DJoneset, num_iter=10)
       visualise (ns, Cohset) 
       visualise (ns, Cohset, type='spectra')


   # Tie the trees for the different ifrs together in an artificial 'sink':
   cc.append(Cohset.simul_sink(ns))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)









#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************

#--------------------------------------------------------------------------------
# Produce a Cohset for the specified ifrs, with simulated uv-data: 

def simulate(ns, ifrs, Sixpack, **pp):
   funcname = 'MG_JEN_Cohset.simulate(): '

   pp.setdefault('jones', [])

   pp.setdefault('stddev_Gampl', 0.1) 
   pp.setdefault('stddev_Gphase', 0.1) 
   pp.setdefault('fdeg_Gampl', 1) 
   pp.setdefault('fdeg_Gphase', 1) 
   pp.setdefault('tdeg_Gampl', 0) 
   pp.setdefault('tdeg_Gphase', 0) 

   pp.setdefault('stddev_Breal', 0.1) 
   pp.setdefault('stddev_Bimag', 0.1) 
   pp.setdefault('fdeg_Breal', 3) 
   pp.setdefault('fdeg_Bimag', 3) 
   pp.setdefault('tdeg_Breal', 0) 
   pp.setdefault('tdeg_Bimag', 0) 

   pp.setdefault('stddev_dang', 0.01) 
   pp.setdefault('stddev_dell', 0.01) 
   pp.setdefault('fdeg_dang', 1) 
   pp.setdefault('fdeg_dell', 1) 
   pp.setdefault('tdeg_dang', 0) 
   pp.setdefault('tdeg_dell', 0) 

   pp.setdefault('RM', 0.1) 
   pp.setdefault('PZD', 0.2)
   pp.setdefault('stddev_noise', 0.0)
   pp = record(pp)

   # Recommended ways to mark nodes that contains simulated data: 
   scope = 'simulated'           # mark the Cohset/Jonesets (visualisation)
   nsim = ns.Subscope('_')       # prepend all simulation nodes with _:: 

   # Optional: corrupt the uvdata with simulated jones matrices: 
   if not isinstance(pp.jones, (list,tuple)): pp.jones = [pp.jones]
   if len(pp.jones)>0:
       stations = TDL_Cohset.ifrs2stations(ifrs) 
       jseq = TDL_Joneset.Joneseq()
       for jones in pp.jones:
           if jones=='G':
               jseq.append(MG_JEN_Joneset.GJones (nsim, scope=scope, stations=stations, Sixpack=Sixpack, 
                                                  solvable=False,
                                                  fdeg_Gampl=pp.fdeg_Gampl, fdeg_Gphase=pp.fdeg_Gphase,
                                                  tdeg_Gampl=pp.tdeg_Gampl, tdeg_Gphase=pp.tdeg_Gphase,
                                                  stddev_Gampl=pp.stddev_Gampl, stddev_Gphase=pp.stddev_Gphase))
           elif jones=='B':
               jseq.append(MG_JEN_Joneset.BJones (nsim, scope=scope, stations=stations, Sixpack=Sixpack, 
                                                  solvable=False,
                                                  fdeg_Breal=pp.fdeg_Breal, fdeg_Bimag=pp.fdeg_Bimag,
                                                  tdeg_Breal=pp.tdeg_Breal, tdeg_Bimag=pp.tdeg_Bimag,
                                                  stddev_Breal=pp.stddev_Breal, stddev_Bimag=pp.stddev_Bimag))
           elif jones=='F':
               jseq.append(MG_JEN_Joneset.FJones (nsim, scope=scope, stations=stations, Sixpack=Sixpack, 
                                                  solvable=False, RM=pp.RM))
           elif jones=='D':
               jseq.append(MG_JEN_Joneset.DJones_WSRT (nsim, scope=scope, stations=stations, Sixpack=Sixpack, 
                                                       solvable=False, PZD=pp.PZD,
                                                       fdeg_dang=pp.fdeg_dang, fdeg_dell=pp.fdeg_dell,
                                                       tdeg_dang=pp.tdeg_dang, tdeg_dell=pp.tdeg_dell,
                                                       stddev_dang=pp.stddev_dang, stddev_dell=pp.stddev_dang))
           elif jones=='K':
               # NB: Note that we are NOT using nodescope nsim here, because the array coordinate
               #     nodes (for uvw) have predefined names). This probably means that we cannot
               #     solve for station positions until we have addressed this problem....
               #     In any case, KJones does not produce any solvegroups....
               jseq.append(MG_JEN_Joneset.KJones (ns, scope=scope, stations=stations, Sixpack=Sixpack)) 

           else:
               print '** jones not recognised:',jones,'from:',pp.jones
               
       # Matrix-multiply the collected jones matrices in jseq to a 2x2 Joneset:
       global simulated_JJones
       simulated_JJones = jseq.make_Joneset(nsim)
       MG_JEN_forest_state.object(jseq, funcname)
       MG_JEN_forest_state.object(simulated_JJones, funcname)

   # Make the Cohset with simulated/corrupted uvdata:
   Cohset = predict (nsim, scope=scope, Sixpack=Sixpack, ifrs=ifrs, Joneset=simulated_JJones)

   # Add some gaussian noise to the data
   # (NB: More advanced noise may be added to the Cohset after this function)
   if (pp.stddev_noise>0): addnoise (ns, Cohset, stddev=pp.stddev_noise)

   MG_JEN_forest_state.object(Cohset, funcname)
   return Cohset

#--------------------------------------------------------------------------------------
# Make a JJones Joneset from the specified sequence (list) of jones matrices:

def JJones(ns, stations, Sixpack, **pp):
    funcname = 'MG_JEN_Cohset.JJones(): '

    pp.setdefault('jones', []) 
    pp.setdefault('scope', 'predicted') 

    pp.setdefault('parmtable', None)

    pp.setdefault('fdeg_Gampl', 1) 
    pp.setdefault('fdeg_Gphase', 1) 
    pp.setdefault('tdeg_Gampl', 0) 
    pp.setdefault('tdeg_Gphase', 0) 
    
    pp.setdefault('fdeg_Breal', 3) 
    pp.setdefault('fdeg_Bimag', 3) 
    pp.setdefault('tdeg_Breal', 0) 
    pp.setdefault('tdeg_Bimag', 0) 
    
    pp.setdefault('fdeg_dang', 1) 
    pp.setdefault('fdeg_dell', 1) 
    pp.setdefault('tdeg_dang', 0) 
    pp.setdefault('tdeg_dell', 0) 

    pp.setdefault('RM', 0.1) 
    pp.setdefault('PZD', 0.1)
    pp = record(pp)

    # Temporary (until None-bug is solved)
    if not pp.has_key('parmtable'): pp.parmtable = None

    jseq = TDL_Joneset.Joneseq()
    if not isinstance(pp.jones, (list,tuple)): pp.jones = [pp.jones]
    for jones in pp.jones:
        if jones=='G':
            jseq.append(MG_JEN_Joneset.GJones (ns, stations=stations, Sixpack=Sixpack, Gscale=0, **pp))
        elif jones=='B':
            jseq.append(MG_JEN_Joneset.BJones (ns, stations=stations, Sixpack=Sixpack, Bscale=0, **pp))
        elif jones=='F':
            jseq.append(MG_JEN_Joneset.FJones (ns, stations=stations, Sixpack=Sixpack, Fscale=0, **pp)) 
        elif jones=='K':
            jseq.append(MG_JEN_Joneset.KJones (ns, stations=stations, Sixpack=Sixpack, Fscale=0, **pp)) 
        elif jones=='D':
            jseq.append(MG_JEN_Joneset.DJones_WSRT (ns, stations=stations, Sixpack=Sixpack, Dscale=0, **pp))
        else:
            print '** jones not recognised:',jones,'from:',pp.jones
               
    # Matrix-multiply the collected jones matrices in jseq to a 2x2 Joneset:
    MG_JEN_forest_state.object(jseq, funcname)
    Joneset = jseq.make_Joneset(ns)
    MG_JEN_forest_state.object(Joneset, funcname)
    return Joneset
    


#======================================================================================

def addnoise (ns, Cohset, **pp):
    """add gaussian noise to the coherency matrices in Cohset""" 

    funcname = 'MG_JEN_Cohset.addnoise(): '

    # Input arguments:
    pp.setdefault('stddev', 1.0)          #
    pp.setdefault('unop', 'Exp')          #
    pp = record(pp)

    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        nsub = ns.Subscope('addnoise', s1=s12[0], s2=s12[1])
        noise = MG_JEN_twig.gaussnoise (nsub, dims=Cohset.dims(),
                                        stddev=pp.stddev, unop=pp.unop)
        coh = ns.noisy(s1=s12[0], s2=s12[1]) << Meq.Add(Cohset[key], noise)
        Cohset[key] = coh

    # Finished:
    s = funcname
    s = s+', stddev='+str(pp.stddev)
    s = s+', unop='+str(pp.unop)
    Cohset.history(s)
    MG_JEN_forest_state.history (funcname)
    return True



#======================================================================================
# Make spigots and sinks (plus some common services)
#======================================================================================

# inarg = MG_JEN_Cohset.make_spigots(getinarg=True)
# JEN_inarg.modify(inarg,
#                 # MS_corr_index=[0,-1,-1,1],       # only XX/YY available
#                 # MS_corr_index=[0,-1,-1,3],       # all available, use only XX/YY
#                 MS_corr_index=[0,1,2,3],           # all corrs available, use all
#                 flag=False,                        # if True, flag the input data
#                 visu=False)                        # if True, visualise the input data
# JEN_inarg.attach(inarg, MG)
                 

def make_spigots(ns=None, Cohset=None, **inarg):

    # Input arguments:
    pp = JEN_inarg.extract(inarg, 'MG_JEN_Cohset.make_spigots()')
    pp.setdefault('MS_corr_index', [0,1,2,3])
    pp.setdefault('visu', False)
    pp.setdefault('flag', False)
    if pp.has_key('getinarg'): return JEN_inarg.noexec(pp)
    funcname = JEN_inarg.funcname(pp)
    if not JEN_inarg.check(pp): return False

    # Make MeqSinks
    Cohset.spigots(ns, MS_corr_index=pp['MS_corr_index'])
    spigots = Cohset.nodes()

    # Create the nodes expected by read_MS_auxinfo.py 
    global MSauxinfo
    MSauxinfo.create_nodes(ns)

    # Append the initial (spigot) Cohset to the forest state object:
    MG_JEN_forest_state.object(Cohset, funcname)

    # Optional: visualise the spigot (input) data:
    if pp['visu']:
	visualise (ns, Cohset)
	visualise (ns, Cohset, type='spectra')
        
    # Optional: flag the spigot (input) data:
    if pp['flag']:
       insert_flagger (ns, Cohset, scope='spigots',
                       unop=['Real','Imag'], visu=False)
       if pp['visu']: visualise (ns, Cohset)

    # Return a list of spigot nodes:
    return spigots


#--------------------------------------------------------------------------

# inarg = MG_JEN_Cohset.make_sinks(getinarg=True)
# JEN_inarg.modify(inarg,
#                 output_col='PREDICT'               # logical (tile) output column
#                 visu_array_config=False,           # if True, visualise the array config
#                 flag=False,                        # if True, flag the input data
#                 visu=False)                        # if True, visualise the input data
# JEN_inarg.attach(inarg, MG)
                 

def make_sinks(ns, Cohset, **inarg):

    # Input arguments:
    pp = JEN_inarg.extract(inarg, 'MG_JEN_Cohset.make_sinks()')
    pp.setdefault('visu_array_config', True)
    pp.setdefault('visu', False)
    pp.setdefault('flag', False)
    pp.setdefault('output_col', 'PREDICT')
    if pp.has_key('getinarg'): return JEN_inarg.noexec(pp)
    funcname = JEN_inarg.funcname(pp)
    if not JEN_inarg.check(pp): return False

    # Change the scope (name) for visualisation etc:
    Cohset.scope('sinks')

    # Optional: flag the sink (output) data:
    if pp['flag']:
       insert_flagger (ns, Cohset, scope='sinks',
                       unop=['Real','Imag'], visu=False)

    # Optional: visualise the sink (output) data:
    if pp['visu']:
       visualise (ns, Cohset)
       visualise (ns, Cohset, type='spectra')

    # Attach array visualisation nodes:
    bb = []
    if pp['visu_array_config']:
       global MSauxinfo
       dcoll = MSauxinfo.dcoll(ns)
       for i in range(len(dcoll)):
          MG_JEN_forest_state.bookmark(dcoll[i], page='MSauxinfo_array_config')
       bb.extend(dcoll)

    # Make MeqSinks
    Cohset.sinks(ns, start=bb, output_col=pp['output_col'])
    sinks = Cohset.nodes()
    
    # Append the final Cohset to the forest state object:
    MG_JEN_forest_state.object(Cohset, funcname)
    
    # Return a list of sink nodes:
    return sinks



#======================================================================================

def predict (ns=0, Sixpack=None, Joneset=None, **pp):
    funcname = 'MG_JEN_Cohset.predict(): '

    # Input arguments:
    pp.setdefault('scope', 'rawdata')
    pp.setdefault('ifrs', [(0,1)])
    pp.setdefault('polrep', 'linear')
    pp = record(pp)

    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:
    coh0 = Sixpack.coh22(ns, pp['polrep'])

    # Create a Cohset object for the 2x2 cohaerencies of the given ifrs:
    Cohset = TDL_Cohset.Cohset(label='predict', origin=funcname, **pp)

    # Put the same node (coh0) with 'nominal' (i.e. uncorrupted) visibilities
    # into all ifr-slots of the Cohset:
    Cohset.uniform(ns, coh0)

    # Optionally, corrupt the Cohset visibilities with the instrumental effects
    # in the given Joneset of 2x2 station jones matrices:
    if not Joneset==None:
       Cohset.corrupt (ns, Joneset=Joneset)
       Cohset.display('.predict(): after corruption')

    # Finished:
    MG_JEN_forest_state.object(Sixpack, funcname)
    Cohset.history(funcname+' using '+Sixpack.oneliner())
    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    MG_JEN_forest_state.object(Cohset, funcname)
    return Cohset






#======================================================================================
# Insert a flagger:
#======================================================================================

def insert_flagger (ns, Cohset, **pp):
    """insert a flagger for the coherency matrices in Cohset""" 

    funcname = 'MG_JEN_Cohset.insert_flagger(): '

    # Input arguments:
    pp.setdefault('sigma', 5.0)              # flagged if exceeds sigma*stddev
    pp.setdefault('unop', 'Abs')             # unop used to make real data
    pp.setdefault('oper', 'GT')              # decision function (GT=Greater Than)
    pp.setdefault('flag_bit', 1)             # affected flag-bit
    pp.setdefault('merge', True)             # if True, merge the flags of 4 corrs
    pp.setdefault('visu', False)             # if True, visualise the result
    pp.setdefault('compare', False)          # ....
    pp = record(pp)

    # Insert flaggers for all ifrs:
    flagger_scope = 'flag_'+Cohset.scope()
    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        nsub = ns.Subscope(flagger_scope, s1=s12[0], s2=s12[1])
        coh = MG_JEN_flagger.flagger (nsub, Cohset[key],
                                      sigma=pp.sigma, unop=pp.unop, oper=pp.oper,
                                      flag_bit=pp.flag_bit, merge=pp.merge)
        Cohset[key] = coh

    # Visualise the result, if required:
    if pp.visu:
        visu_scope = 'flagged_'+Cohset.scope()
        visualise (ns, Cohset, scope=visu_scope, type='spectra')

    Cohset.scope('flagged')
    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    MG_JEN_forest_state.object(Cohset, funcname)
    return True



#======================================================================================
# Insert a solver for the specified solvegroup(s):
#======================================================================================

# - The 'measured' Cohset is assumed to be the main data stream.
# - The 'predicted' Cohset contains corrupted model visibilities.
# - The (optional) 'correct' Joneset contains the instrumental model
#   that is affected by this solver. If supplied, the measured data
#   will be corrected with the estimated values BEFORE the reqseq graft.
# - The (optional) 'subtract' Cohset contains predicted visibilities
#   e.g. for a particular source/patch. If supplied, they will be
#   subtracted from the measured data BEFORE the reqseq graft.
# - The (optional) 'compare' Joneset contains the simulated instrumental
#   values. If supplied they will be subtracted from the estimated values
#   when visualised. 


def insert_solver (ns, measured, predicted, correct=None, subtract=None, compare=None, **pp):
    """insert a named solver""" 

    funcname = 'MG_JEN_Cohset.solver(): '

    # Input arguments:
    # pp.setdefault('num_cells', [1,5])      # if defined, ModRes argument [ntime,nfreq]
    pp.setdefault('num_cells', None)      # if defined, ModRes argument [ntime,nfreq]
    pp.setdefault('solvegroup', [])        # list of solvegroup(s) to be solved for
    pp.setdefault('num_iter', 20)          # max number of iterations
    pp.setdefault('epsilon', 1e-4)         # iteration control criterion
    pp.setdefault('debug_level', 10)       # solver debug_level
    pp.setdefault('visu', True)            # if True, include visualisation
    pp.setdefault('history', True)         # if True, include history collection of metrics 
    pp = record(pp)

    # The solver name must correspond to one or more of the
    # predefined solvegroups of parms in the input Cohset(s).
    # These are collected from the Jonesets upstream.
    # The solver_name is just a concatenation of such solvegroup names:
    if isinstance(pp.solvegroup, str): pp.solvegroup = [pp.solvegroup]
    solver_name = pp.solvegroup[0]
    for i in range(len(pp.solvegroup)):
        if i>0: solver_name = solver_name+pp.solvegroup[i]

    # Use copies of the input Cohsets:
    # - We need a Pohset copy, since it gets modified with condeq nodes.
    # - We need a Mohset copy, since the measured data may be corrected first.
    Pohset = predicted.copy(label='predicted('+str(pp.solvegroup)+')')
    Pohset.label('solver_'+solver_name)
    Mohset = measured.copy(label='measured('+str(pp.solvegroup)+')')
    Mohset.label('solver_'+solver_name)

    # Insert a ReSampler node as counterpart to the ModRes node below.
    # This node resamples the full-resolution (f,t) measured uv-data onto
    # the smaller number of cells of the request from the condeq.
    if pp.num_cells:
        Mohset.ReSampler(ns, flag_mask=3, flag_bit=4, flag_density=0.1)

    # From here on, only the Pohset copy will be modified,
    # until it contains the MeqCondeq nodes for the solver.
    # It will be attached to the state_forest, for later inspection.
    Pohset.history(funcname+' input: '+str(pp))
    Pohset.history(funcname+' measured: '+measured.oneliner())
    Pohset.history(funcname+' predicted: '+predicted.oneliner())

    # For redundancy calibration, we need station positions:
    if False:
        # Get a record with the names of MS interface nodes
        # Supply a nodescope (ns) in case it does not exist yet
        rr = MG_JEN_forest_state.MS_interface_nodes(ns)
        # Since
        # Use rr.redun.pairs to get ifr keys to select ifrs from Mohset

    # Collect a list of names of solvable MeParms for the solver:
    # The measured side may also have solvable parameters:
    # Pohset.update_from_Cohset(measured)
    corrs = []
    solvable = []
    for sgname in pp.solvegroup:
        if not Pohset.solvegroup().has_key(sgname):
            print '\n** solvegroup name not recognised:',sgname
            print '     choose from:',Pohset.solvegroup().keys()
            print
            return
        solvegroup = Pohset.solvegroup()[sgname]
        corrs.extend(Pohset.condeq_corrs()[sgname])
        for key in solvegroup:
            pgnames = Pohset.parmgroup()[key]     # list of parmgroup node-names
            solvable.extend(pgnames)              # list of solvable node-names
            # Temporary: show the first solvable MeqParm of each parmgroup on the allcorrs page:
            if pp.visu:
                MG_JEN_forest_state.bookmark (ns[pgnames[0]], page='allcorrs')


    # Make new Cohset objects with the relevant corrs only:
    # Pohset.selcorr(ns, corrs)
    # Mohset.selcorr(ns, corrs)
  
    # Make condeq nodes (use Pohset from here onwards):
    cc = []
    punit = predicted.punit()
    for key in Pohset.keys():
        if not measured.has_key(key):
            print '\n** key not recognised in measured Cohset:',key
            return

        # Poh/Moh are coherency nodes (tensors), with only the specified 1-4 corrs:
        Poh = Pohset.coh (key, corrs=corrs, ns=ns, name='predicted')
        Moh = Mohset.coh (key, corrs=corrs, ns=ns, name='measured')
        
        s12 = Pohset.stations()[key]
        condeq = ns.condeq(solver_name)(s1=s12[0],s2=s12[1], q=punit) << Meq.Condeq(Moh, Poh)
        Pohset[key] = condeq
        cc.append(condeq)
    Pohset.display('after defining condeqs')


    # Visualise the condeqs, if required:
    dcoll_condeq = []
    if pp.visu:
       Pohset.scope('condeq_'+solver_name)
       dcoll_condeq = visualise (ns, Pohset, errorbars=True, graft=False)
       # NB: What about visualising MeqParms (solvegroups)?
       #     Possibly compared with their simulated values...
  
    # Make the solver node:
    solver = ns.solver(solver_name, q=punit) << Meq.Solver(children=cc,
                                                           solvable=solvable,
                                                           num_iter=pp.num_iter,
                                                           epsilon=pp.epsilon,
                                                           last_update=True,
                                                           save_funklets=True,
                                                           debug_level=pp.debug_level)
    # Make a bookmark for the solver plot:
    MG_JEN_forest_state.bookmark (solver, name=('solver: '+solver_name),
                                  udi='cache/result', viewer='Result Plotter')
    if pp.visu:
        MG_JEN_forest_state.bookmark (solver, page='allcorrs',
                                      udi='cache/result', viewer='Result Plotter')

    # Make historyCollect nodes for the solver metrics
    hcoll_nodes = []
    if pp.history and pp.visu:
        # Make a tensor node of solver metrics/debug hcoll nodes:
        hc = MG_JEN_historyCollect.make_hcoll_solver_metrics (ns, solver, name=solver_name)
        hcoll_nodes.append(hc)

    # Make a solver subtree with the solver and its associated hcoll/dcoll nodes:
    # This is necessary in order to give them all the same resampled request (see below)
    subtree_name = 'solver_subtree_'+solver_name        # used in reqseq name
    cc = [solver]                              # start a list of reqseq children (solver is first)
    cc.extend(hcoll_nodes)                     # extend with historyCollect nodes
    cc.extend(dcoll_condeq)                       # extend the list with the condeq dataCollect node(s) 
    solver_subtree = ns[subtree_name](q=punit) << Meq.ReqSeq(children=cc, result_index=0)


    # Insert a ModRes node to change (reduce) the number of request cells:
    # NB: This node must be BEFORE the hcoll/dcoll nodes, since these also
    #     require the low-resolution request, of course....
    if pp.num_cells:
        num_cells = pp['num_cells']                            # [ntime, nfreq]
        solver_subtree = ns.modres_solver(solver_name, q=punit) << Meq.ModRes(solver_subtree,
                                                                              num_cells=num_cells)

    # Optional: subtract the given Cohset from the measured (corrected?) data:
    # NB: The interaction between correct and subtract requires a little thought...
    # NB: Use predicted for subtract/correct...? (ONLY if not resampling....)
    if subtract:
	measured.subtract(ns, subtract)        # assume that 'subtract' is a Cohset
        
    # Add to the Pohset history (why not to measured?):
    Pohset.history(funcname+' -> '+Pohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    MG_JEN_forest_state.object(Pohset, funcname)

    # Optional: Correct the measured data with the given Joneset (correct).
    # This is the Joneset that has been affected by the solver.
    # NB: This correction should be inserted BEFORE the solver reqseq (see below),
    #         because otherwise it messes up the correction of the insertion ifr
    #         (one of the input Jones matrices is called before the solver....)
    if correct:
	measured.correct(ns, correct)          # assume that 'correct' is a Joneset


    # Graft the solver subtree onto all measured ifr-streams via reqseqs:
    measured.graft(ns, solver_subtree, name='solver_'+solver_name)
    MG_JEN_forest_state.object(measured, funcname)

    # Finished
    return True
    




#======================================================================================

def visualise(ns, Cohset, **pp):
    """visualises the 2x2 coherency matrices in Cohset"""

    funcname = 'MG_JEN_Cohset.visualise(): '
    uniqual = MG_JEN_forest_state.uniqual('MG_JEN_Cohset::visualise()')

    # Input arguments:
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('graft', True)            # if True, graft the visu-nodes on the Cohset
    pp = record(pp)

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    visu_scope = 'visu_'+Cohset.scope()

    # The dataCollect nodes are visible, and should show the punit:
    dcoll_scope = Cohset.scope()+'_'+Cohset.punit()
  
    # Make separate lists of nodes per (available) corr:
    nodes = {}
    for corr in Cohset.corrs():
        nodes[corr] = []
        for key in Cohset.keys():
           node = Cohset.coh(key, corrs=corr, ns=ns, name='visu')
           nodes[corr].append(node)

    # Make dcolls per (available) corr, and collect groups of corrs:
    dcoll = dict()
    for corr in Cohset.corrs():
        dc = MG_JEN_dataCollect.dcoll (ns, nodes[corr], 
	                               scope=dcoll_scope, tag=corr,
                                       type=pp.type, errorbars=pp.errorbars,
                                       color=Cohset.plot_color()[corr],
                                       style=Cohset.plot_style()[corr],
                                       size=Cohset.plot_size()[corr],
                                       pen=Cohset.plot_pen()[corr])
        if pp.type=='spectra':
           dcoll[corr] = dc
        elif pp.type=='realvsimag':
           key = 'allcorrs'
           dcoll.setdefault(key,[])
           dcoll[key].append(dc)
           if corr in ['XY','YX','RL','LR']:
              key = 'crosscorr'
              dcoll.setdefault(key,[])
              dcoll[key].append(dc)
           if True and corr in ['XX','YY','RR','LL']:
              key = 'paralcorr'
              dcoll.setdefault(key,[])
              dcoll[key].append(dc)

    # Make the final dcolls:
    dconc = dict()
    sc = []
    for key in dcoll.keys():
       bookpage = None
       if pp.type=='spectra':
          # Since spectra plots are crowded, make separate plots for the 4 corrs.
          # key = corr
          dc = dcoll[key]
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=key)
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=dcoll_scope+'_spectra')
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=Cohset.scope())

       elif pp.type=='realvsimag':
          # For realvsimag plots it is better to plot multiple corrs in the same plot.
          # key = allcorrs, [paralcorr], [crosscorr]
          dc = MG_JEN_dataCollect.dconc(ns, dcoll[key], 
                                        scope=dcoll_scope,
                                        tag=key, bookpage=key)
          # MG_JEN_forest_state.bookmark (dc['dcoll'], page=dcoll_scope)
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=Cohset.scope())

       dconc[key] = dc                               # atach to output record
       sc.append (dc['dcoll'])                       # step-child for graft below
      

    MG_JEN_forest_state.history (funcname)
  
    if pp.graft:
        # Make the dcoll nodes children of a (synchronising) MeqReqSeq node
        # that is inserted into the coherency stream(s):
        Cohset.graft(ns, sc, name=visu_scope+'_'+pp.type) 
        MG_JEN_forest_state.object(Cohset, funcname+'_'+visu_scope+'_'+pp.type)
        # Return an empty list to be consistent with the alternative below
        return []

    else:
        # Return a list of dataCollect nodes that need requests:
        # Do NOT modify the input Cohset
        Cohset.history(funcname+' -> '+'dconc '+str(len(dconc)))
        cc = []
        for key in dconc.keys(): cc.append(dconc[key]['dcoll'])
        return cc



#==========================================================================
# Some convenience functions:
#==========================================================================

#--------------------------------------------------------------------------
# Display the subtree of the first ifr in the Cohset

def display_first_subtree (Cohset=0, recurse=3):
    key = Cohset.keys()[0]
    txt = 'coh[0/'+str(Cohset.len())+']'
    txt = txt+': key='+str(key)
    MG_JEN_exec.display_subtree(Cohset[key], txt, full=1, recurse=recurse)
    return


# Make a Sixpack from a punit string

def punit2Sixpack(ns, punit='uvp'):
    Sixpack = MG_JEN_Sixpack.newstar_source (ns, name=punit)
    return Sixpack











#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************


#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

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



#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    print '\n*******************\n** Local test of:',MG.script_name,':\n'

    # This is the default:
    if 1:
        MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=3)

    # This is the place for some specific tests during development.
    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG.script_name, ifrs=ifrs)

    if 0:   
        cs.display('initial')
       
    if 0:
        cs.spigots (ns)
           
    if 0:
        # coh = predict ()
        punit = 'unpol'
        # punit = '3c147'
        # punit = 'RMtest'
        Sixpack = punit2Sixpack(ns, punit)
        jseq = TDL_Joneset.Joneseq()
        jseq.append(MG_JEN_Joneset.GJones (ns, stations=stations))
        js = jseq.make_Joneset(ns)
        cs = predict (ns, Sixpack=Sixpack, ifrs=ifrs, Joneset=js)
        visualise (ns, cs)
        addnoise (ns, cs)
        insert_flagger (ns, cs, scope='residual', unop=['Real','Imag'], visu=True)

    if 1:
        punit = 'unpol'
        # punit = '3c147'
        # punit = 'RMtest'
        Sixpack = punit2Sixpack(ns, punit)
        Joneset = MG_JEN_Joneset.GJones (nsim, stations=stations, solvable=1)
        measured = predict (nsim, Sixpack=Sixpack, ifrs=ifrs, Joneset=Joneset)
        # measured.select(ns, corrs=['XX','YY'])
        
        Joneset = MG_JEN_Joneset.DJones_WSRT (ns, stations=stations)
        predicted = predict (ns, Sixpack=Sixpack, ifrs=ifrs, Joneset=Joneset)
        cs = predicted
        
        sgname = 'DJones'
        # sgname = ['DJones', 'GJones']
        insert_solver (ns, solvegroup=sgname, measured=measured, predicted=predicted) 
           
    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG.script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




