

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
# - 09 dec 2005: introduced Cohset.Condeq(), .coh()
# - 20 dec 2005: separate solver_subtree()
# - 29 dec 2005: redundancy calibration
# - 01 jan 2006: implement chain and master solver schemes
# - 03 jan 2006: resampling: move argument num_cells to insert_solver
# - 11 jan 2006: make function MSauxinfo()
# - 14 jan 2006: referenced values prepended with @/@@

# Copyright: The MeqTree Foundation 

#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble *********************************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *

from Timba.Trees import JEN_inarg
from Timba.Trees import JEN_inargGui
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


try:
    from qt import *
    # from qt import QApplication,QCursor,Qt,QObject
except:
    pass;


#********************************************************************************
#********************************************************************************
#****************** PART II: Definition of importable functions *****************
#********************************************************************************
#********************************************************************************


#======================================================================================
# Make spigots and sinks (plus some common services)
#======================================================================================


def make_spigots(ns=None, Cohset=None, **inarg):

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::make_spigots()', version='25dec2005')
    JEN_inarg.define (pp, 'MS_corr_index', [0,1,2,3],
                      choice=[[0,-1,-1,1],[0,-1,-1,3],'@@'],
                      help='correlations to be used: \n'+
                      '- [0,1,2,3]:   all corrs available, use all \n'+
                      '- [0,-1,-1,1]: only XX/YY (or RR/LL) available \n'+
                      '- [0,-1,-1,3]: all available, but use only XX/YY or RR/LL')
    JEN_inarg.define (pp, 'visu', tf=False,
                      help='if True, visualise the input uv-data')
    JEN_inarg.define (pp, 'flag', tf=False,
                      help='if True, insert a flagger for the input uv-data')
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make MeqSinks
    Cohset.spigots(ns, MS_corr_index=pp['MS_corr_index'])
    spigots = Cohset.cohs()

    # Create the nodes expected by read_MS_auxinfo.py 
    MSauxinfo().create_nodes(ns)

    # Append the initial (spigot) Cohset to the forest state object:
    # MG_JEN_forest_state.object(Cohset, funcname)

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



def make_sinks(ns=None, Cohset=None, **inarg):

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::make_sinks()', version='25dec2005')
    JEN_inarg.define (pp, 'output_col', 'PREDICT',
                      choice=['PREDICT','RESIDUALS','CORRECTED_DATA'],
                      help='name of the logical (tile) output column')
    JEN_inarg.define (pp, 'visu_array_config', tf=True,
                      help='if True, visualise the array config (from MS)')
    JEN_inarg.define (pp, 'visu', tf=False,
                      help='if True, visualise the output uv-data')
    JEN_inarg.define (pp, 'flag', tf=False,
                      help='if True, insert a flagger for the output uv-data')
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Change the scope (name) for visualisation etc:
    Cohset.scope('sinks')

    # Insert a master reqseq for solvers, if required:
    solvers = Cohset.rider('master_reqseq')
    if len(solvers)>0:
        Cohset.graft(ns, solvers, name='master_reqseq')

    # Insert the end of the solver chain, if required:
    solver = Cohset.rider('chain_solvers')
    if len(solver)>0:
        Cohset.graft(ns, solver[0], name='chain_solvers')

    # Optional: flag the sink (output) data:
    if pp['flag']:
       insert_flagger (ns, Cohset, scope='sinks',
                       unop=['Real','Imag'], visu=False)

    # Optional: visualise the sink (output) data:
    # But only if there are no dcoll/hcoll nodes to be inserted
    # (assume that the latter visualise the current status...?)
    ncoll = len(Cohset.rider('dcoll'))               
    ncoll += len(Cohset.rider('hcoll'))               
    if pp['visu'] and ncoll==0:
       visualise (ns, Cohset)
       visualise (ns, Cohset, type='spectra')

    # Attach array visualisation nodes:
    start = []
    if pp['visu_array_config']:
       dcoll = MSauxinfo().dcoll(ns)
       for i in range(len(dcoll)):
          MG_JEN_forest_state.bookmark(dcoll[i], page='MSauxinfo_array_config')
       start.extend(dcoll)

    # Attach any collected hcoll/dcoll nodes:
    post = Cohset.rider('dcoll', clear=True)               
    post.extend(Cohset.rider('hcoll', clear=True))               

    # Make MeqSinks
    Cohset.sinks(ns, start=start, post=post, output_col=pp['output_col'])
    sinks = Cohset.cohs()
    
    # Append the final Cohset to the forest state object:
    MG_JEN_forest_state.object(Cohset, funcname)
    MG_JEN_forest_state.object(Cohset.Parmset, funcname)
    
    # Return a list of sink nodes:
    return sinks



#======================================================================================

def predict (ns=None, Sixpack=None, Joneset=None, **inarg):
    """Make a Cohset with predicted (optional: corrupted) uv-data for
    the source defined by Sixpack"""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::predict()', version='25dec2005')
    JEN_inarg.define (pp, 'ifrs', [(0,1)], choice=['@@'], hide=True,
                      help='list of ifrs (tuples) for the Cohset')
    pp.setdefault('polrep', 'linear')
    JEN_inarg.nest(pp, MG_JEN_Joneset.KJones(_getdefaults=True))
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make sure that there is a valid source/patch Sixpack:
    if not Sixpack: Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')
    punit = Sixpack.label()

    # Create a Cohset object for the 2x2 cohaerencies of the given ifrs:
    Cohset = TDL_Cohset.Cohset(label='predict', origin=funcname, **pp)

    # Make a 'nominal' 2x2 coherency matrix (coh0) for the source/patch
    # by multiplication its (I,Q,U,V) with the Stokes matrix:
    nominal = Sixpack.coh22(ns, pp['polrep'])

    # Put the same 'nominal' (i.e. uncorrupted) visibilities into all
    # ifr-slots of the Cohset:
    Cohset.uniform(ns, nominal)

    # Optionally, multiply the Cohset with the KJones (DFT) Joneset
    if False:
       KJones = MG_JEN_Joneset.KJones (ns, Sixpack=Sixpack,
                                       MSauxinfo=MSauxinfo(),
                                       _inarg=pp)
       Cohset.corrupt (ns, Joneset=KJones)

    # Optionally, corrupt the Cohset visibilities with the instrumental effects
    # in the given Joneset of 2x2 station jones matrices:
    if Joneset:
       Cohset.corrupt (ns, Joneset=Joneset)
       # Cohset.display('.predict(): after corruption')

    # Finished:
    MG_JEN_forest_state.object(Sixpack, funcname)
    Cohset.history(funcname+' using '+Sixpack.oneliner())
    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    # MG_JEN_forest_state.object(Cohset, funcname)
    return Cohset



#--------------------------------------------------------------------------------------
# Make a JJones Joneset from the specified sequence of Jones matrices:

def JJones(ns=None, Sixpack=None, **inarg):
    """Make a Joneset by creating and multiplying one ore more Jonesets"""
   
    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::JJones()', version='25dec2005')
    # Arguments that should common to all Jonesets in the sequence
    # (they are set recursively by JEN_inarg.modify())
    pp.setdefault('stations',[0])                   # list of stations
    pp.setdefault('polrep', 'linear')               # polarisation representation
    pp.setdefault('unsolvable', False)              # if True, do NOT store solvegroup info
    pp.setdefault('parmtable', None)                # MeqParm table name
    pp.setdefault('Jsequence', ['GJones'])          # sequence of Jones matrices
    pp.setdefault('expect', '*')                    # list of expected Jones matrices 

    # Include default inarg records for various Jones matrix definition functions:
    # (This includes a mechanism to exclude the unneeded ones, to avoid clutter)
    available = ['GJones','FJones','BJones','DJones_WSRT']
    if pp['expect']=='*':
        pp['expect'] = available                    # all the available ones
    if not isinstance(pp['expect'], (list, tuple)): pp['expect'] = [pp['expect']]
    if 'GJones' in pp['expect']:
        JEN_inarg.nest(pp, MG_JEN_Joneset.GJones(_getdefaults=True))
    if 'FJones' in pp['expect']:
        JEN_inarg.nest(pp, MG_JEN_Joneset.FJones(_getdefaults=True))
    if 'BJones' in pp['expect']:
        JEN_inarg.nest(pp, MG_JEN_Joneset.BJones(_getdefaults=True))
    if 'DJones_WSRT' in pp['expect']:
        JEN_inarg.nest(pp, MG_JEN_Joneset.DJones_WSRT(_getdefaults=True))

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make sure that there is a valid source/patch Sixpack:
    # NB: This is just for the punit-name!
    if not Sixpack: Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')
    punit = Sixpack.label()
    
    # Create a sequence of Jonesets for the specified punit:
    jseq = TDL_Joneset.Joneseq()
    if not isinstance(pp['Jsequence'], (list,tuple)): pp['Jsequence'] = [pp['Jsequence']]
    for jones in pp['Jsequence']:
        if jones=='GJones':
            jseq.append(MG_JEN_Joneset.GJones (ns, _inarg=pp, punit=punit))
        elif jones=='BJones':
            jseq.append(MG_JEN_Joneset.BJones (ns, _inarg=pp, punit=punit))
        elif jones=='FJones':
            jseq.append(MG_JEN_Joneset.FJones (ns, _inarg=pp, punit=punit)) 
        elif jones=='DJones_WSRT':
            jseq.append(MG_JEN_Joneset.DJones_WSRT (ns, _inarg=pp, punit=punit))
        else:
            print '** jones not recognised:',jones,'from:',pp['Jsequence']
               
    # Matrix-multiply the collected jones matrices in jseq to a 2x2 Joneset:
    # MG_JEN_forest_state.object(jseq, funcname)
    Joneset = jseq.make_Joneset(ns)
    # MG_JEN_forest_state.object(Joneset, funcname)
    return Joneset
    










#======================================================================================
# Insert a solver:
#======================================================================================

# - The 'measured' Cohset is assumed to be the main data stream.
# - The 'predicted' Cohset contains corrupted model visibilities,
#   and the Joneset with which it has been corrupted (if any).

def insert_solver(ns=None, measured=None, predicted=None, **inarg):
    """insert one or more solver subtrees in the data stream""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::insert_solver()', version='25dec2005')
    JEN_inarg.define(pp, 'solver_subtree', None, hide=True,
                     help='solver subtree qualifier(s)')
    JEN_inarg.define(pp, 'num_cells', None,
                     choice=[None, [2,2],[2,5]],
                     help='ModRes argument [ntime, nfreq]')
    JEN_inarg.define(pp, 'redun', tf=False,
                     help='if True, use redundant baseline calibration')
    inarg_solver_config (pp)
    JEN_inarg.define(pp, 'visu', tf=True,
                     help='if True, include full visualisation')
    JEN_inarg.define(pp, 'subtract', tf=False,
                     help='if True, subtract predicted from measured')
    JEN_inarg.define(pp, 'correct', tf=False,
                     help='if True, correct measured with predicted.Joneset')
    # Include (nest) the inarg record of a subroutine called below:
    JEN_inarg.nest(pp, solver_subtree(_getdefaults=True))
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make a unique qualifier:
    uniqual = _counter('.insert_solver()', increment=-1)
    punit = predicted.punit()

    # We need a Mohset copy, since it will be modified with condeqs etc
    Mohset = measured.copy(label='measured')
    Mohset.history(funcname+' input: '+str(pp))
    Mohset.history(funcname+' measured: '+measured.oneliner())
    Mohset.history(funcname+' predicted: '+predicted.oneliner())

    # Optional: Insert a ReSampler node as counterpart to the ModRes node below.
    # This node resamples the full-resolution (f,t) measured uv-data onto
    # the smaller number of cells of the request from the condeq.
    if pp['num_cells']:
        Mohset.ReSampler(ns, flag_mask=3, flag_bit=4, flag_density=0.1)

    # Make condeq nodes in Mohset:
    if pp['redun']:                              # redundant-spacing calibration
        Mohset.correct(ns, predicted.Joneset())  # correct BOTH sides of the condeq                 
        Mohset.Condeq_redun(ns)                  # special version of .Condeq()                        
        pp['subtract'] = False                   # .....??
    else:                                        # normal: measured-predicted
        Mohset.Condeq(ns, predicted)        
    Mohset.scope('condeq_'+punit)
    Mohset.history(funcname+' -> '+Mohset.oneliner())

    # Make a list of one or more MeqSolver subtree(s):
    # Assume that pp contains the relevant (qual) inarg record(s).
    # NB: Note that pp['num_cells'] overrides solver_subtree() default.
    if pp['solver_subtree']:
        if not isinstance(pp['solver_subtree'], (tuple, list)):
            pp['solver_subtree']= [pp['solver_subtree']]
        solver_subtrees = []
        for qual in pp['solver_subtree']:
            sst = solver_subtree(ns, Mohset, _inarg=pp, _qual=qual,
                                 num_cells=pp['num_cells'])
            solver_subtrees.append(sst)
    else:
        sst = solver_subtree(ns, Mohset, _inarg=pp, num_cells=pp['num_cells'])
        solver_subtrees = [sst]

    # Obtain the current list of (full-resolution) hcoll/dcoll nodes, and clear: 
    # NB: These are the ones that get a request BEFORE the solver(s)
    coll_before = []
    coll_before.extend(measured.rider('hcoll', clear=True))
    coll_before.extend(measured.rider('dcoll', clear=True))

    # Optional: subtract the predicted (corrupted) Cohset from the measured data:
    # NB: This should be done BEFORE correct, since predicted contains corrupted values
    if pp['subtract']:
        measured.subtract(ns, predicted) 
        if pp['visu']: visualise (ns, measured, errorbars=True, graft=False)
        
    # Optional: Correct the measured data with the given Joneset.
    # NB: This should be done AFTER subtract, for the same reason as stated above
    # NB: Correction should be inserted BEFORE the solver reqseq (see below),
    # because otherwise it messes up the correction of the insertion ifr
    # (one of the input Jones matrices is called before the solver....)
    if pp['correct']:
        # The 'predicted' Cohset has kept the Joneset with which it has been
        # corrupted, and which has been affected by the solution for its MeqParms.
        Joneset = predicted.Joneset() 
        if Joneset:                                  # if Joneset available
            measured.correct(ns, Joneset)            # correct 
            if pp['visu']: visualise (ns, measured, errorbars=True, graft=False)

    # Obtain the current list of (full-resolution) hcoll/dcoll nodes, and clear: 
    # NB: These are the ones that get a request AFTER the solver(s)
    coll_after = []
    coll_after.extend(measured.rider('dcoll', clear=True))
    coll_after.extend(measured.rider('hcoll', clear=True))

    # Make the 'full-resolution' reqseq with solver_subtree(s) and dcoll/hcoll nodes:
    cc = coll_before                                 # hcoll/dcoll nodes BEFORE the solver
    if len(coll_before)>1:
        cc = [ns.coll_before_solver(uniqual)(q=punit) << Meq.Composer(children=coll_before)]
        # cc = [ns.coll_before_solver(uniqual)(q=punit) << Meq.ReqMux(children=coll_before)]
        # NB: ReqMux gives error message: nmandatory<=nchildren...?
    cc.extend(solver_subtrees)                       # the solver subtree(s) 
    if len(coll_after)>1:
        coll_after = [ns.coll_after_solver(uniqual)(q=punit) << Meq.Composer(children=coll_after)]
    cc.extend(coll_after)                            # hcoll/dcoll nodes AFTER the solver
    fullres = ns.solver_fullres(uniqual)(q=punit) << Meq.ReqSeq(children=cc)

    # Attach the solver subtree (fullres) to something:
    if pp['master_reqseq']:
        # Collect all solvers for a master reqseq before the sinks
        # (See .make_sinks())
        measured.rider('master_reqseq', append=fullres)
    elif pp['chain_solvers']:
        # Chain the solvers, parallel to the main data-stream:
        measured.chain_solvers(ns, fullres) 
    else:
        # Graft the fullres onto all measured ifr-streams via reqseqs:
        # NB: Since the reqseqs have to wait for the solver to finish,
        #     this synchronises the ifr-streams
        measured.graft(ns, fullres, name='insert_solver')

    # Finished: do some book-keeping:
    MG_JEN_forest_state.object(Mohset, funcname)
    MG_JEN_forest_state.object(Mohset.Parmset, funcname)
    MG_JEN_forest_state.object(predicted, funcname)
    MG_JEN_forest_state.object(predicted.Parmset, funcname)
    MG_JEN_forest_state.history (funcname)
    Mohset.cleanup(ns)                
    return True
    

#-----------------------------------------------------------------------------
# A solver subtree

def solver_subtree (ns=None, Cohset=None, **inarg):
    """Make a solver-subtree for the given Condeq Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::solver_subtree()', version='20dec2005')
    pp.setdefault('solvegroup', [])        # list of solvegroup(s) to be solved for
    pp.setdefault('rmin', None)            # if specified, only use baselines>=rmin 
    pp.setdefault('rmax', None)            # if specified, only use baselines<=rmax
    pp.setdefault('condition', [])         # List of zero or more condition keys
    pp.setdefault('num_iter', 20)          # max number of iterations
    pp.setdefault('num_cells', None)       # if defined, ModRes argument [ntime,nfreq]
    pp.setdefault('epsilon', 1e-4)         # iteration control criterion
    pp.setdefault('debug_level', 10)       # solver debug_level
    pp.setdefault('visu', True)            # if True, include visualisation
    pp.setdefault('history', True)         # if True, include history collection of metrics 
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Make a unique qualifier:
    uniqual = _counter('.solver_subtree()', increment=-1)

    # The solver name must correspond to one or more of the
    # predefined solvegroups of parms in the input Cohset.
    # These are collected from the Jonesets upstream.
    # The solver_name is just a concatenation of such solvegroup names:
    if isinstance(pp['solvegroup'], str): pp['solvegroup'] = [pp['solvegroup']]
    solver_name = pp['solvegroup'][0]
    for i in range(len(pp['solvegroup'])):
        if i>0: solver_name = solver_name+pp['solvegroup'][i]

    # Get a list of names of solvable MeqParms for the solver:
    corrs = Cohset.Parmset.sg_rider(pp['solvegroup'], key='condeq_corrs')
    solvable = Cohset.Parmset.solveparm_names(pp['solvegroup'])

    dcoll_parm = []
    hcoll_parm = []
    if pp['visu']:
        if len(solvable)<10:
            # If not too many, show all solvable MeqParms
            for s1 in solvable:
                MG_JEN_forest_state.bookmark (ns[s1], page='solvable')
                hcoll = MG_JEN_historyCollect.insert_hcoll(ns, s1, page='hcoll_solvable', graft=False)
                hcoll_parm.append(hcoll)
        else:
            # Show the first MeqParm in each parmgroup:
            ss1 = Cohset.Parmset.solveparm_names(pp['solvegroup'], select='first')
            for s1 in ss1:
                MG_JEN_forest_state.bookmark (ns[s1], page='solvable')
                hcoll = MG_JEN_historyCollect.insert_hcoll(ns, s1, page='hcoll_solvable', graft=False)
                hcoll_parm.append(hcoll)
        # The following shows more than just the solvable parms....
        if Cohset.Joneset():                                  # if Joneset available
            dcoll_parm.extend(MG_JEN_Joneset.visualise (ns, Cohset.Joneset(),
                                                        errorbars=True, show_mxel=True))


    # Extract a list of condeq nodes for the specified corrs and baseline lengths:
    Cohset.select(rmin=pp['rmin'], rmax=pp['rmax'])
    solver_condeqs = Cohset.cohs(corrs=corrs, ns=ns)

    # Make extra condeq nodes to condition the solution, if required: 
    extra_condeqs = []
    if pp['condition']==None: pp['condition'] = []
    if not isinstance(pp['condition'], (list, tuple)): pp['condition'] = [pp['condition']]
    Cohset.Parmset.display('extra_condeqs', full=True)
    for key in pp['condition']:
        if isinstance(key, str):
            condeq = Cohset.Parmset.make_condeq(ns, key)
            if not isinstance(condeq, bool): extra_condeqs.append(condeq)
    solver_condeqs.extend(extra_condeqs)

    # Visualise the condeqs (at solver resolution), if required:
    dcoll_condeq = []
    if False and pp['visu']:
       dcoll_condeq = visualise (ns, Cohset, errorbars=True, graft=False, extra=extra_condeqs)
  
    # Make the MeqSolver node itself:
    punit = Cohset.punit()
    solver = ns.solver(solver_name, q=punit) << Meq.Solver(children=solver_condeqs,
                                                           solvable=solvable,
                                                           num_iter=pp['num_iter'],
                                                           epsilon=pp['epsilon'],
                                                           last_update=True,
                                                           save_funklets=True,
                                                           debug_level=pp['debug_level'])
    # Make a bookmark for the solver plot:
    page_name = 'solver: '+solver_name
    MG_JEN_forest_state.bookmark (solver, page=page_name,
                                  udi='cache/result', viewer='Result Plotter')
    MG_JEN_forest_state.bookmark (solver, page=page_name, viewer='ParmFiddler')
    if pp['visu']:
        # Optional: also show the solver on the allcorrs page:
        MG_JEN_forest_state.bookmark (solver, page='allcorrs',
                                      udi='cache/result', viewer='Result Plotter')

    # Make historyCollect nodes for the solver metrics
    hcoll_nodes = []
    if pp['history'] and pp['visu']:
        # Make a tensor node of solver metrics/debug hcoll nodes:
        hc = MG_JEN_historyCollect.make_hcoll_solver_metrics (ns, solver,
                                                              firstonly=True,
                                                              name=solver_name)
        hcoll_nodes.append(hc)


    # Make a solver subtree with the solver and its associated hcoll/dcoll nodes:
    # The latter are at solver resolution, which may be lower (resampling)
    # This is necessary in order to give them all the same resampled request (see below)
    subtree_name = 'solver_subtree_'+solver_name  # used in reqseq name
    cc = [solver]                                 # start a list of reqseq children (solver is first)
    if len(hcoll_nodes)>0:                        # append historyCollect nodes
       cc.append(ns.hcoll_solver(solver_name, q=punit) << Meq.Composer(children=hcoll_nodes))
    if len(dcoll_condeq)>0:                       # append dataCollect nodes
       cc.append(ns.dcoll_condeq(solver_name, q=punit) << Meq.Composer(children=dcoll_condeq))
    if len(dcoll_parm)>0:                         # append MeqParm dataCollect nodes
       cc.append(ns.dcoll_parm(solver_name, q=punit) << Meq.Composer(children=dcoll_parm))
    if len(hcoll_parm)>0:                         # append MeqParm historyCollect nodes
       cc.append(ns.hcoll_parm(solver_name, q=punit) << Meq.Composer(children=hcoll_parm))
    root = ns[subtree_name](q=punit) << Meq.ReqSeq(children=cc, result_index=0)


    # Insert a ModRes node to change (reduce) the number of request cells:
    # NB: This node must be BEFORE the hcoll/dcoll nodes, since these also
    #     require the low-resolution request, of course....
    if pp['num_cells']:
       num_cells = pp['num_cells']                # [ntime, nfreq]
       root = ns.modres_solver(solver_name, q=punit) << Meq.ModRes(root, num_cells=num_cells)


    # Finished: do some book-keeping:
    # MG_JEN_forest_state.object(Cohset, funcname)
    MG_JEN_forest_state.history (funcname)
    return root
    


#======================================================================================
# Insert a flagger:
#======================================================================================


def insert_flagger (ns=None, Cohset=None, **inarg):
    """insert a flagger for the coherency matrices in Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::insert_flagger()', version='25dec2005')
    pp.setdefault('sigma', 5.0)              # flagged if exceeds sigma*stddev
    pp.setdefault('unop', 'Abs')             # unop used to make real data
    pp.setdefault('oper', 'GT')              # decision function (GT=Greater Than)
    pp.setdefault('flag_bit', 1)             # affected flag-bit
    pp.setdefault('merge', True)             # if True, merge the flags of 4 corrs
    pp.setdefault('visu', False)             # if True, visualise the result
    pp.setdefault('compare', False)          # ....
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # Insert flaggers for all ifrs:
    flagger_scope = 'flag_'+Cohset.scope()
    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        nsub = ns.Subscope(flagger_scope, s1=s12[0], s2=s12[1])
        coh = MG_JEN_flagger.flagger (nsub, Cohset[key],
                                      sigma=pp['sigma'], unop=pp['unop'], oper=pp['oper'],
                                      flag_bit=pp['flag_bit'], merge=pp['merge'])
        Cohset[key] = coh

    # Visualise the result, if required:
    if pp['visu']:
        visu_scope = 'flagged_'+Cohset.scope()
        visualise (ns, Cohset, scope=visu_scope, type='spectra')

    Cohset.scope('flagged')
    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history (funcname)
    # MG_JEN_forest_state.object(Cohset, funcname)
    return True



#======================================================================================
# Cohset visualisation:
#======================================================================================

def visualise(ns=None, Cohset=None, extra=None, **pp):
    """visualises the 2x2 coherency matrices in Cohset"""

    funcname = 'MG_JEN_Cohset.visualise(): '

    # Input arguments:
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('graft', False)           # if True, graft the visu-nodes on the Cohset
    pp.setdefault('paralcorr', False)       # if True, also make plots for parallel corrs only  
    pp.setdefault('crosscorr', False)       # if True, also make plots for cross corrs only  
    pp['graft'] = False                     # disabled permanently....?

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    visu_scope = 'visu_'+Cohset.scope()

    # The dataCollect nodes are visible, and should show the punit:
    dcoll_scope = Cohset.scope()+'_'+Cohset.punit()
  
    # Make separate lists of nodes per (available) corr:
    nodes = {}
    for corr in Cohset.corrs():
        nodes[corr] = Cohset.cohs(corrs=corr, ns=ns, name='visu')
        if extra:
            # Special case (kludge): include some extra nodes
            if not isinstance(extra, (list,tuple)): extra = [extra]
            nodes[corr].extend(extra)

    # Make dcolls per (available) corr, and collect groups of corrs:
    dcoll = dict()
    for corr in Cohset.corrs():
        dc = MG_JEN_dataCollect.dcoll (ns, nodes[corr], 
	                               scope=dcoll_scope, tag=corr,
                                       type=pp['type'], errorbars=pp['errorbars'],
                                       color=Cohset.plot_color()[corr],
                                       style=Cohset.plot_style()[corr],
                                       size=Cohset.plot_size()[corr],
                                       pen=Cohset.plot_pen()[corr])
        if pp['type']=='spectra':
            dcoll[corr] = dc
        elif pp['type']=='realvsimag':
            key = 'allcorrs'
            dcoll.setdefault(key,[])
            dcoll[key].append(dc)
            if pp['crosscorr'] and corr in ['XY','YX','RL','LR']:
                key = 'crosscorr'
                dcoll.setdefault(key,[])
                dcoll[key].append(dc)
            if pp['paralcorr'] and corr in ['XX','YY','RR','LL']:
                key = 'paralcorr'
                dcoll.setdefault(key,[])
                dcoll[key].append(dc)

    # Make the final dcolls:
    dconc = dict()
    sc = []
    for key in dcoll.keys():
       bookpage = None
       if pp['type']=='spectra':
          # Since spectra plots are crowded, make separate plots for the 4 corrs.
          dc = dcoll[key]                                         # key = corr
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=key)
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=dcoll_scope+'_spectra')
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=Cohset.scope())

       elif pp['type']=='realvsimag':
          # For realvsimag plots it is better to plot multiple corrs in the same plot.
          # NB: key = allcorrs, [paralcorr], [crosscorr]
          dc = MG_JEN_dataCollect.dconc(ns, dcoll[key], 
                                        scope=dcoll_scope,
                                        tag=key, bookpage=key)
          # MG_JEN_forest_state.bookmark (dc['dcoll'], page=dcoll_scope)
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=Cohset.scope())

       dconc[key] = dc                               # atach to output record
       sc.append (dc['dcoll'])                       # step-child for graft below
      

    MG_JEN_forest_state.history (funcname)
  
    if pp['graft']:
        # Make the dcoll nodes children of a (synchronising) MeqReqSeq node
        # that is inserted into the coherency stream(s):
        Cohset.graft(ns, sc, name=visu_scope+'_'+pp['type']) 
        # MG_JEN_forest_state.object(Cohset, funcname+'_'+visu_scope+'_'+pp['type'])
        # Return an empty list to be consistent with the alternative below
        return []

    else:
        # Return a list of dataCollect nodes that need requests:
        Cohset.history(funcname+' -> '+'dconc '+str(len(dconc)))
        cc = []
        for key in dconc.keys():
           cc.append(dconc[key]['dcoll'])
        Cohset.rider('dcoll', append=cc)                # collect in Cohset
        return cc








#==========================================================================
# Some convenience functions:
#==========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace:
        print '** MG_JEN_Cohset: _counters(',key,') =',_counters[key]
    return _counters[key]



#--------------------------------------------------------------------------
# Display the subtree of the first ifr in the Cohset

def display_first_subtree (Cohset=None, recurse=3):
    key = Cohset.keys()[0]
    txt = 'coh[0/'+str(Cohset.len())+']'
    txt = txt+': key='+str(key)
    MG_JEN_exec.display_subtree(Cohset[key], txt, full=1, recurse=recurse)
    return


# Make a Sixpack from a punit string

def punit2Sixpack(ns, punit='uvp'):
    Sixpack = MG_JEN_Sixpack.newstar_source (ns, name=punit)
    return Sixpack





#----------------------------------------------------------------------------------------------------
# inarg_functons (definition of groups of input arguments):
#----------------------------------------------------------------------------------------------------


def inarg_polrep (rr, **pp):
    pp.setdefault('master', False)          # If True, it is the master value
    pp.setdefault('polrep', 'linear')        
    if not pp['master']: pp['polrep'] = '@@polrep'
    JEN_inarg.define (rr, 'polrep', pp['polrep'],
                      choice=['linear','circular','@@polrep'],
                      help='polarisation representation')
    return True


def inarg_punit (rr, **pp):
    pp.setdefault('master', False)          # If True, it is the master value
    pp.setdefault('punit', 'unpol')        
    if not pp['master']: pp['punit'] = '@@punit'
    choice = ['unpol','unpol2','unpol10','3c147',
              'RMtest','QUV','QU','SItest','@@punit']
    JEN_inarg.define (rr, 'punit', pp['punit'], choice=choice,
                      help='name of calibrator source/patch \n'+
                      '- unpol:   unpolarised, I=1Jy \n'+
                      '- unpol2:  idem, I=2Jy \n'+
                      '- unpol10: idem, I=10Jy \n'+
                      '- RMtest:  Rotation Measure \n'+
                      '- SItest:  Spectral Index \n'+
                      '- QUV:     non-zero Q,U,V \n'+
                      '- QU:      non-zero Q,U \n'+
                      '- 3c147:')
    return True


def inarg_parmtable (rr, **pp):
    pp.setdefault('master', False)          # If True, it is the master value
    pp.setdefault('parmtable', None)        
    if not pp['master']: pp['parmtable'] = '@@parmtable'
    JEN_inarg.define (rr, 'parmtable', pp['parmtable'],
                      help='name of MeqParm table to be used')
    return True


def inarg_stations (rr, **pp):
    pp.setdefault('master', False)          # If True, it is the master value
    pp.setdefault('stations', range(4))        
    pp.setdefault('ifrs', (0,1))        
    if not pp['master']: pp['stations'] = '@@stations'
    JEN_inarg.define (rr, 'stations', pp['stations'],
                      choice=[range(7),range(14),range(15),'@@stations'],
                      help='the (subset of) stations to be used')
    # Derive a list of ifrs from rr['stations'] (assumed to exist):
    JEN_inarg.define (rr, 'ifrs', TDL_Cohset.stations2ifrs(rr['stations']), hide=True,
                      help='list if ifrs (derived from stations)')
    return True


def inarg_redun (rr, **pp):
    pp.setdefault('master', False)          # If True, it is the master value
    pp.setdefault('redun', False)        
    if not pp['master']: pp['redun'] = '@@redun'
    JEN_inarg.define (rr, 'redun', tf=pp['redun'], 
                      help='if True, redundant spacing calibration')
    return True



def inarg_solver_config (rr, **pp):
    pp.setdefault('master', False)          # If True, it is the master value
    pp.setdefault('chain_solvers', True)        
    pp.setdefault('master_reqseq', False)        
    if not pp['master']:
        pp['chain_solvers'] = '@@chain_solvers'
        pp['master_reqseq'] = '@@master_reqseq'
    JEN_inarg.define (rr, 'chain_solvers', tf=pp['chain_solvers'], hide=True,
                      help='if True, chain the solvers (recommended)')
    JEN_inarg.define (rr, 'master_reqseq', tf=pp['master_reqseq'], hide=True,
                      help='if True, use a master reqseq for solver(s)')
    return True




#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************level,(level*'.'),
#********************************************************************************

#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_Cohset')

# Define some overall arguments:
# Local (MG_JEN_Cohset.py) version:
JEN_inarg.define (MG, 'last_changed', 'd11jan2006', editable=False)
inarg_stations(MG, master=True)
inarg_parmtable(MG, master=True)
inarg_polrep(MG, master=True)
inarg_punit(MG, master=True)
inarg_solver_config (MG, master=True)
inarg_redun(MG, master=True)

# Copied from MG_JEN_Cohset.py:
# JEN_inarg.define (MG, 'last_changed', 'd11jan2006', editable=False)
# MG_JEN_Cohset.inarg_stations(MG, master=True)
# MG_JEN_Cohset.inarg_parmtable(MG, master=True)
# MG_JEN_Cohset.inarg_polrep(MG, master=True)
# MG_JEN_Cohset.inarg_punit(MG, master=True)
# MG_JEN_Cohset.inarg_solver_config (MG, master=True)
# MG_JEN_Cohset.inarg_redun(MG, master=True)
    

#----------------------------------------------------------------------------------------------------
# Interaction with the MS: spigots, sinks and stream control
#----------------------------------------------------------------------------------------------------

#=======
if True:                                               # ... Copied from MG_JEN_Cohset.py ...
   MG['stream_control'] = dict()
   MG_JEN_exec.inarg_stream_control(MG['stream_control'])
   JEN_inarg.modify(MG['stream_control'],
                    tile_size=10,
                    _JEN_inarg_option=None)            # optional, not yet used 


   # inarg = MG_JEN_Cohset.make_spigots(_getdefaults=True)  
   inarg = make_spigots(_getdefaults=True)              # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # MS_corr_index=[0,-1,-1,1],       # only XX/YY available
                    # MS_corr_index=[0,-1,-1,3],       # all available, use only XX/YY
                    MS_corr_index=[0,1,2,3],           # all corrs available, use all
                    # flag=False,                        # if True, flag the input data
                    visu=True,                         # if True, visualise the input data
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 


   # inarg = MG_JEN_Cohset.make_sinks(_getdefaults=True)   
   inarg = make_sinks(_getdefaults=True)                # local (MG_JEN_Cohset.py) version 
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

if False:                                                # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.insert_flagger(_getdefaults=True) 
   inarg = insert_flagger(_getdefaults=True)              # local (MG_JEN_Cohset.py) version 
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
if True:                                                   # ... Copied from MG_JEN_Cohset.py ...

   # Specify the name qualifier for (the inarg records of) this 'predict and solve' group.
   # NB: The same qualifier should be used when using the functions in _define_forest()
   qual = None
   qual = 'qual1'

   # Specify the sequence of zero or more (corrupting) Jones matrices:
   Jsequence = ['GJones'] 
   # Jsequence = ['BJones'] 
   # Jsequence = ['FJones'] 
   # Jsequence =['DJones_WSRT']             
   # Jsequence = ['GJones','DJones_WSRT']
   
   # Specify a list of MeqParm solvegroup(s) to be solved for:
   solvegroup = ['GJones']
   # solvegroup = ['DJones']
   # solvegroup = ['GJones','DJones']

   # Extra condition equations to be used:
   condition = []
   condition.append('Gphase_X_sum=0.0')
   condition.append('Gphase_Y_sum=0.0')
   # condition.append('Gphase_X_first=0.0')
   # condition.append('Gphase_Y_last=0.0')
   # condition.append('Bimag_X_sum=0.0')
   # condition.append('Bimag_Y_sum=0.0')
   # condition = []


   # inarg = MG_JEN_Cohset.JJones(_getdefaults=True, _qual=qual, expect=Jsequence) 
   inarg = JJones(_getdefaults=True, _qual=qual, expect=Jsequence)  
   JEN_inarg.modify(inarg,
                    # stations=MG['stations'],               # List of array stations
                    # parmtable=MG['parmtable'],             # MeqParm table name
                    stations='@@stations',               # List of array stations
                    parmtable='@@parmtable',             # MeqParm table name
                    unsolvable=False,                      # If True, no solvegroup info is kept
                    # polrep=MG['polrep'],                   # polarisation representation
                    polrep='@@polrep',                   # polarisation representation
                    Jsequence=Jsequence,                   # Sequence of corrupting Jones matrices 
                    _JEN_inarg_option=None)                # optional, not yet used 

   # Insert non-default Jones matrix arguments here: 
   #    (This is easiest by copying lines from MG_JEN_Joneset.py)
   if 'GJones' in Jsequence: 
       JEN_inarg.modify(inarg,
                        fdeg_Gampl=3,                      # degree of default freq polynomial         
                        fdeg_Gphase='@fdeg_Gampl',          # degree of default freq polynomial          
                        tdeg_Gampl=1,                      # degree of default time polynomial         
                        tdeg_Gphase='@tdeg_Gampl',          # degree of default time polynomial       
                        subtile_size_Gampl=0,                 # used in tiled solutions         
                        subtile_size_Gphase='subtile_size_Gampl', # used in tiled solutions         
                        _JEN_inarg_option=None)            # optional, not yet used 
   if 'DJones_WSRT' in Jsequence: 
       JEN_inarg.modify(inarg,
                        fdeg_dang=1,                       # degree of default freq polynomial
                        fdeg_dell='@fdeg_dang',             # degree of default freq polynomial
                        tdeg_dang=1,                       # degree of default time polynomial
                        tdeg_dell='@tdeg_dang',             # degree of default time polynomial
                        subtile_size_dang=0,                  # used in tiled solutions         
                        subtile_size_dell='subtile_size_dang',   # used in tiled solutions         
                        _JEN_inarg_option=None)            # optional, not yet used 
   if 'BJones' in Jsequence: 
       JEN_inarg.modify(inarg,
                        fdeg_Breal=3,                      # degree of default freq polynomial        
                        fdeg_Bimag='@fdeg_Breal',           # degree of default freq polynomial          
                        tdeg_Breal=0,                      # degree of default time polynomial         
                        tdeg_Bimag='@tdeg_Breal',           # degree of default time polynomial    
                        subtile_size_Breal=0,                 # used in tiled solutions         
                        subtile_size_Bimag='subtile_size_Breal', # used in tiled solutions         
                        _JEN_inarg_option=None)            # optional, not yet used 
   if 'FJones' in Jsequence: 
       JEN_inarg.modify(inarg,
                        fdeg_RM=0,                         # degree of default freq polynomial          
                        tdeg_RM=0,                         # degree of default time polynomial         
                        subtile_size_RM=1,                    # used in tiled solutions         
                        _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


   # inarg = MG_JEN_Cohset.predict(_getdefaults=True, _qual=qual)  
   inarg = predict(_getdefaults=True, _qual=qual)             # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # ifrs=MG['ifrs'],                       # list of Cohset ifrs 
                    # polrep=MG['polrep'],                   # polarisation representation
                    ifrs='@@ifrs',                       # list of Cohset ifrs 
                    polrep='@@polrep',                   # polarisation representation
                    _JEN_inarg_option=None)                # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


   #========
   if True:                                                # ... Copied from MG_JEN_Cohset.py ...
       # inarg = MG_JEN_Cohset.insert_solver(_getdefaults=True, _qual=qual) 
       inarg = insert_solver(_getdefaults=True, _qual=qual)   # local (MG_JEN_Cohset.py) version 
       JEN_inarg.modify(inarg,
                        # master_reqseq=MG['master_reqseq'], # if True, use a master reqseq for solver(s)
                        # chain_solvers=MG['chain_solvers'], # if True, chain the solver(s)
                        master_reqseq='@@master_reqseq', # if True, use a master reqseq for solver(s)
                        chain_solvers='@@chain_solvers', # if True, chain the solver(s)
                        redun=True,                        # if True, use redundant baseline calibration
                        # redun=MG['redun'],                 # if True, use redundant baseline calibration
                        # redun='@@redun',                 # if True, use redundant baseline calibration
                        subtract=False,                    # if True, subtract 'predicted' from uv-data 
                        correct=True,                      # if True, correct the uv-data with 'predicted.Joneset()'
                        visu=True,                         # if True, include visualisation
                        # num_cells=None,                    # if defined, ModRes argument [ntime,nfreq]
                        # num_cells=[2,5],                   # ModRes argument [ntime,nfreq]
                        # ** Arguments for .solver_subtree()
                        solvegroup=solvegroup,             # list of solvegroup(s) to be solved for
                        # condition=[],                      # list of names of extra condition equations
                        condition=condition,               # list of names of extra condition equations
                        # rmin=200,                         # if specified, only use baselines>=rmin 
                        # rmax=None,                         # if specified, only use baselines<=rmax
                        num_iter=10,                       # max number of iterations
                        # epsilon=1e-4,                      # iteration control criterion
                        # debug_level=10,                    # solver debug_level
                        history=True,                      # if True, include history collection of metrics 
                        _JEN_inarg_option=None)            # optional, not yet used 
       JEN_inarg.attach(MG, inarg)
                 


#---------------------------------------------------------------
# Launch the inarg Gui (should be done from the browser):
if False:
    igui = JEN_inargGui.ArgBrowser()
    igui.input(MG, name=MG['script_name'], set_open=False)
    igui.launch()






#====================================================================================
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG['script_name'])


#====================================================================================
# The MSauxinfo object contains auxiliary MS info (nodes):
# It is used at various points in this module, e.g. make_sinks()

def MSauxinfo(create=False):
    global msauxinfo
    if create:
        msauxinfo = TDL_MSauxinfo.MSauxinfo(label='MG_JEN_Cohset')
        msauxinfo.station_config_default()           # WSRT (15 stations), incl WHAT
    return msauxinfo
MSauxinfo(create=True)



#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _tdl_predefine (mqs, parent, **kwargs):
    """_tdl_predefine() is a standard TDL name. When a forest script is
    loaded by, e.g., the browser, this method is called prior to
    defining the forest. The method can do anything: run a GUI, read
    config files, etc.
    Parameters:
      mqs:    a meqserver object.
      parent: parent widget (if running in a GUI), or None if no GUI
      kwargs: extra arguments (may be used by assay scripts, etc.)
    If this function returns a dict, this dict is passed as the kwargs
    of _define_forest(). 
    Errors should be indicated by throwing an exception.
    """

    print '\n** inside _tdl_predefine() **\n'
    res = True
    if parent:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        try:
            igui = JEN_inargGui.ArgBrowser(parent)
            igui.input(MG, name=MG['script_name'], set_open=False)
            res = igui.exec_loop()
            print '** _tdl_predefine(): res =',type(res),'=',res,'\n'
            if res is None:
                raise RuntimeError("Cancelled by user");
        finally:
            QApplication.restoreOverrideCursor()
    return res




#**************************************************************************

def _define_forest (ns, **kwargs):
    # print '** _define_forest(): kwargs =',kwargs
    # if len(kwargs)==0: return False

    # The MG may be passed in from _tdl_predefine():
    # In that case, override the global MG record.
    if len(kwargs)>1: MG = kwargs

    # Perform some common functions, and return an empty list (cc=[]):
    cc = MG_JEN_exec.on_entry (ns, MG)

    if True:
        # Make MeqSpigot nodes that read the MS:
        Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                                   polrep=MG['polrep'],
                                   ifrs=MG['ifrs'])
        make_spigots(ns, Cohset, _inarg=MG)


    if False:
        # Optional: insert a flagger to the raw data: 
        insert_flagger (ns, Cohset, **MG)
        visualise (ns, Cohset)
        visualise (ns, Cohset, type='spectra')

    if True:
        # Optional: Insert a solver:
        qual = 'qual1'
        Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=MG['punit'])
        Joneset = JJones(ns, Sixpack=Sixpack, _inarg=MG, _qual=qual)
        predicted = predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG, _qual=qual)
        if True:
            # Insert a solver for a named group of MeqParms (e.g. 'GJones'):
            insert_solver (ns, measured=Cohset, predicted=predicted, _inarg=MG, _qual=qual)

    if True:
        # Make MeqSink nodes that write the MS:
        sinks = make_sinks(ns, Cohset, _inarg=MG)
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
   MG_JEN_exec.spigot2sink(mqs, parent, ctrl=MG['stream_control'])
   return True


def _tdl_job_noMS (mqs, parent):
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
    if 0:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

    # This is the place for some specific tests during development.
    ns = NodeScope()
    nsim = ns.Subscope('_')
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    cs = TDL_Cohset.Cohset(label='test', scops=MG['script_name'], ifrs=ifrs)

    if 1:
        igui = JEN_inargGui.ArgBrowser()
        igui.input(MG, name=MG['script_name'], set_open=False)
        igui.launch()
       
    if 0:   
       cs.display('initial')
       
    if 0:
       cs.spigots (ns)

    if 0:
       punit = 'unpol'
       # punit = '3c147'
       # punit = 'RMtest'
       Sixpack = punit2Sixpack(ns, punit)

           
    if 0:
        display_first_subtree(cs)
        cs.display('final result')

    # ............
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




