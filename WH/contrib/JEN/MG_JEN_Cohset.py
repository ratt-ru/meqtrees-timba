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
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::make_spigots()')
    pp.setdefault('MS_corr_index', [0,1,2,3])
    pp.setdefault('visu', False)
    pp.setdefault('flag', False)
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

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


def make_sinks(ns=None, Cohset=None, **inarg):

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::make_sinks()')
    pp.setdefault('visu_array_config', True)
    pp.setdefault('visu', False)
    pp.setdefault('flag', False)
    pp.setdefault('output_col', 'PREDICT')
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

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
    start = []
    if pp['visu_array_config']:
       global MSauxinfo
       dcoll = MSauxinfo.dcoll(ns)
       for i in range(len(dcoll)):
          MG_JEN_forest_state.bookmark(dcoll[i], page='MSauxinfo_array_config')
       start.extend(dcoll)

    # Attach any collected hcoll/dcoll nodes:
    post = Cohset.coll(clear=True)               

    # Make MeqSinks
    Cohset.sinks(ns, start=start, post=post, output_col=pp['output_col'])
    sinks = Cohset.nodes()
    
    # Append the final Cohset to the forest state object:
    MG_JEN_forest_state.object(Cohset, funcname)
    
    # Return a list of sink nodes:
    return sinks



#======================================================================================

def predict (ns=None, Sixpack=None, Joneset=None, **inarg):
    """Make a Cohset with predicted (optional: corrupted) uv-data for
    the source defined by Sixpack"""

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::predict()')
    pp.setdefault('scope', 'rawdata')
    pp.setdefault('ifrs', [(0,1)])
    pp.setdefault('polrep', 'linear')
    JEN_inarg.nest(pp, MG_JEN_Joneset.KJones(_getinarg=True))
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    if not Sixpack: Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')

    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:
    coh0 = Sixpack.coh22(ns, pp['polrep'])

    # Create a Cohset object for the 2x2 cohaerencies of the given ifrs:
    Cohset = TDL_Cohset.Cohset(label='predict', origin=funcname, **pp)

    # Put the same node (coh0) with 'nominal' (i.e. uncorrupted) visibilities
    # into all ifr-slots of the Cohset:
    Cohset.uniform(ns, coh0)

    # Optionally, multiply the Cohset with the KJones (DFT) Joneset
    if False:
       KJones = MG_JEN_Joneset.KJones (ns, Sixpack=Sixpack, _inarg=pp)
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
    MG_JEN_forest_state.object(Cohset, funcname)
    return Cohset



#--------------------------------------------------------------------------------------
# Make a JJones Joneset from the specified sequence (list) of jones matrices:

def JJones(ns=None, **inarg):
    """Make a Joneset by creating and multiplying one ore more Jonesets"""
   
    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::JJones()')
    pp.setdefault('scope', 'predicted') 
    pp.setdefault('punit', 'uvp') 
    pp.setdefault('jones', ['G']) 
    pp.setdefault('stations', range(4)) 
    pp.setdefault('parmtable', None)
    # Include nested inarg records for various Jones matrix functions:
    JEN_inarg.nest(pp, MG_JEN_Joneset.GJones(_getinarg=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.FJones(_getinarg=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.BJones(_getinarg=True))
    JEN_inarg.nest(pp, MG_JEN_Joneset.DJones_WSRT(_getinarg=True))
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)
    
    # Create a sequence of Jonesets:
    jseq = TDL_Joneset.Joneseq()
    if not isinstance(pp['jones'], (list,tuple)): pp['jones'] = [pp['jones']]
    for jones in pp['jones']:
        if jones=='G':
            jseq.append(MG_JEN_Joneset.GJones (ns, _inarg=pp, Gscale=0))
        elif jones=='B':
            jseq.append(MG_JEN_Joneset.BJones (ns, _inarg=pp, Bscale=0))
        elif jones=='F':
            jseq.append(MG_JEN_Joneset.FJones (ns, _inarg=pp, Fscale=0)) 
        elif jones=='D':
            jseq.append(MG_JEN_Joneset.DJones_WSRT (ns, _inarg=pp, Dscale=0))
        else:
            print '** jones not recognised:',jones,'from:',pp['jones']
               
    # Matrix-multiply the collected jones matrices in jseq to a 2x2 Joneset:
    MG_JEN_forest_state.object(jseq, funcname)
    Joneset = jseq.make_Joneset(ns)
    MG_JEN_forest_state.object(Joneset, funcname)
    return Joneset
    










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


def insert_solver (ns=None, measured=None, predicted=None, Joneset=None, **inarg):
    """insert a solver for a specific subset (solvegroup) of MeqParms""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::insert_solver()')
    pp.setdefault('solvegroup', [])        # list of solvegroup(s) to be solved for
    pp.setdefault('num_iter', 20)          # max number of iterations
    pp.setdefault('num_cells', None)       # if defined, ModRes argument [ntime,nfreq]
    # pp.setdefault('num_cells', [1,5])      # if defined, ModRes argument [ntime,nfreq]
    pp.setdefault('epsilon', 1e-4)         # iteration control criterion
    pp.setdefault('debug_level', 10)       # solver debug_level
    pp.setdefault('visu', True)            # if True, include visualisation
    pp.setdefault('history', True)         # if True, include history collection of metrics 
    pp.setdefault('subtract',False)        # if True, subtract 'predicted' from 'measured' 
    pp.setdefault('correct',False)         # if True, correct 'measured' with 'Joneset'(inv) 
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # The solver name must correspond to one or more of the
    # predefined solvegroups of parms in the input Cohset(s).
    # These are collected from the Jonesets upstream.
    # The solver_name is just a concatenation of such solvegroup names:
    if isinstance(pp['solvegroup'], str): pp['solvegroup'] = [pp['solvegroup']]
    solver_name = pp['solvegroup'][0]
    for i in range(len(pp['solvegroup'])):
        if i>0: solver_name = solver_name+pp['solvegroup'][i]

    # Use copies of the input Cohsets:
    # - We need a Pohset copy, since it gets modified with condeq nodes.
    # - We need a Mohset copy, since the measured data may be corrected first.
    Pohset = predicted.copy(label='predicted('+str(pp['solvegroup'])+')')
    Pohset.label('solver_'+solver_name)
    Mohset = measured.copy(label='measured('+str(pp['solvegroup'])+')')
    Mohset.label('solver_'+solver_name)

    # Insert a ReSampler node as counterpart to the ModRes node below.
    # This node resamples the full-resolution (f,t) measured uv-data onto
    # the smaller number of cells of the request from the condeq.
    if pp['num_cells']:
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

    # Collect a list of names of solvable MeqParms for the solver:
    # NB: The measured side may also have solvable parameters:
    #     first use:  Pohset.update_from_Cohset(measured)
    corrs = Pohset.solvecorrs(pp['solvegroup'])
    solvable = Pohset.solveparms(pp['solvegroup'])

    # Temporary: show the first solvable MeqParm of each parmgroup on the allcorrs page:
    if pp['visu']:
        MG_JEN_forest_state.bookmark (ns[solvable[0]], page='allcorrs')
  
    # Make condeq nodes (use Pohset from here onwards):
    solver_condeqs = []
    Pohset.Condeq(ns, Mohset)
    Pohset.display('after defining condeqs')
    solver_condeqs = Pohset.cohs(corrs=corrs, ns=ns)  

    # Visualise the condeqs (at solver resoltion), if required:
    dcoll_condeq = []
    if pp['visu']:
       Pohset.scope('condeq_'+solver_name)
       dcoll_condeq = visualise (ns, Pohset, errorbars=True, graft=False)
       # NB: What about visualising MeqParms (solvegroups)?
       #     Possibly compared with their simulated values...
  
    # Obtain the current list of (full-resolution) hcoll/dcoll nodes, and clear: 
    coll_before = measured.coll(clear=True)

    # Make the solver node:
    punit = Pohset.punit()
    solver = ns.solver(solver_name, q=punit) << Meq.Solver(children=solver_condeqs,
                                                           solvable=solvable,
                                                           num_iter=pp['num_iter'],
                                                           epsilon=pp['epsilon'],
                                                           last_update=True,
                                                           save_funklets=True,
                                                           debug_level=pp['debug_level'])
    # Make a bookmark for the solver plot:
    MG_JEN_forest_state.bookmark (solver, name=('solver: '+solver_name),
                                  udi='cache/result', viewer='Result Plotter')
    if pp['visu']:
        MG_JEN_forest_state.bookmark (solver, page='allcorrs',
                                      udi='cache/result', viewer='Result Plotter')

    # Make historyCollect nodes for the solver metrics
    hcoll_nodes = []
    if pp['history'] and pp['visu']:
        # Make a tensor node of solver metrics/debug hcoll nodes:
        hc = MG_JEN_historyCollect.make_hcoll_solver_metrics (ns, solver, name=solver_name)
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
    solver_subtree = ns[subtree_name](q=punit) << Meq.ReqSeq(children=cc, result_index=0)


    # Insert a ModRes node to change (reduce) the number of request cells:
    # NB: This node must be BEFORE the hcoll/dcoll nodes, since these also
    #     require the low-resolution request, of course....
    if pp['num_cells']:
       num_cells = pp['num_cells']                # [ntime, nfreq]
       solver_subtree = ns.modres_solver(solver_name, q=punit) << Meq.ModRes(solver_subtree,
                                                                             num_cells=num_cells)

    #-------------------------------------------------------------

    if True:
       # Insert some post-solution operations (correct, subtract) on the uv-data.

       # Optional: subtract the predicted (corrupted) Cohset from the measured data:
       if pp['subtract']:
          measured.subtract(ns, predicted) 
          if pp['visu']: visualise (ns, measured, errorbars=True, graft=False)
        
       # Optional: Correct the measured data with the given Joneset.
       # Assume that this is the Joneset that has been used for predict,
       # and which has been affected by the solution for its MeqParms.
       if pp['correct'] and Joneset:
          measured.correct(ns, Joneset)   
          if pp['visu']: visualise (ns, measured, errorbars=True, graft=False)

       # NB: Correction should be inserted BEFORE the solver reqseq (see below),
       # because otherwise it messes up the correction of the insertion ifr
       # (one of the input Jones matrices is called before the solver....)

    #-------------------------------------------------------------

    # Attach any collected full-resolution hcoll/dcoll nodes:
    coll_after = measured.coll(clear=True)               
    if (len(coll_before)+len(coll_after))>0:
       cc = coll_before                          # hcoll/dcoll nodes BEFORE the solver
       if len(coll_before)>1:
          cc = [ns.coll_before(solver_name, q=punit) << Meq.Composer(children=coll_before)]
       cc.append(solver_subtree)                 # the solver subtree itself
       if len(coll_after)>1:
          coll_after = [ns.coll_after(solver_name, q=punit) << Meq.Composer(children=coll_after)]
       cc.extend(coll_after)                     # hcoll/dcoll nodes AFTER the solver
       solver_subtree = ns.solver_fullres(solver_name, q=punit) << Meq.ReqSeq(children=cc)

    # Graft the solver_subtree onto all measured ifr-streams via reqseqs:
    measured.graft(ns, solver_subtree, name='solver_'+solver_name)

    # Finished: do some book-keeping:
    Pohset.history(funcname+' -> '+Pohset.oneliner())
    MG_JEN_forest_state.object(Mohset, funcname)
    MG_JEN_forest_state.object(Pohset, funcname)
    MG_JEN_forest_state.history (funcname)
    return True
    


#======================================================================================
# Insert a flagger:
#======================================================================================


def insert_flagger (ns=None, Cohset=None, **inarg):
    """insert a flagger for the coherency matrices in Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::insert_flagger()')
    pp.setdefault('sigma', 5.0)              # flagged if exceeds sigma*stddev
    pp.setdefault('unop', 'Abs')             # unop used to make real data
    pp.setdefault('oper', 'GT')              # decision function (GT=Greater Than)
    pp.setdefault('flag_bit', 1)             # affected flag-bit
    pp.setdefault('merge', True)             # if True, merge the flags of 4 corrs
    pp.setdefault('visu', False)             # if True, visualise the result
    pp.setdefault('compare', False)          # ....
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
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
    MG_JEN_forest_state.object(Cohset, funcname)
    return True



#======================================================================================
# Cohset visualisation:
#======================================================================================

def visualise(ns=None, Cohset=None, **pp):
    """visualises the 2x2 coherency matrices in Cohset"""

    funcname = 'MG_JEN_Cohset.visualise(): '

    # Input arguments:
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('graft', False)           # if True, graft the visu-nodes on the Cohset
    pp['graft'] = False                              # disabled permanently....?

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    visu_scope = 'visu_'+Cohset.scope()

    # The dataCollect nodes are visible, and should show the punit:
    dcoll_scope = Cohset.scope()+'_'+Cohset.punit()
  
    # Make separate lists of nodes per (available) corr:
    nodes = {}
    for corr in Cohset.corrs():
        nodes[corr] = Cohset.cohs(corrs=corr, ns=ns, name='visu')

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
       if pp['type']=='spectra':
          # Since spectra plots are crowded, make separate plots for the 4 corrs.
          # key = corr
          dc = dcoll[key]
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=key)
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=dcoll_scope+'_spectra')
          MG_JEN_forest_state.bookmark (dc['dcoll'], page=Cohset.scope())

       elif pp['type']=='realvsimag':
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
  
    if pp['graft']:
        # Make the dcoll nodes children of a (synchronising) MeqReqSeq node
        # that is inserted into the coherency stream(s):
        Cohset.graft(ns, sc, name=visu_scope+'_'+pp['type']) 
        MG_JEN_forest_state.object(Cohset, funcname+'_'+visu_scope+'_'+pp['type'])
        # Return an empty list to be consistent with the alternative below
        return []

    else:
        # Return a list of dataCollect nodes that need requests:
        # Do NOT modify the input Cohset
        Cohset.history(funcname+' -> '+'dconc '+str(len(dconc)))
        cc = []
        for key in dconc.keys():
           cc.append(dconc[key]['dcoll'])
        Cohset.coll(cc)                              # collect in Cohset
        return cc



#==========================================================================
# Some functions related to simulation:
# (i.s.o. make_spigots and make_sinks)
#==========================================================================




#--------------------------------------------------------------------------------
# Produce a Cohset for the specified ifrs, with simulated uv-data: 

def simulate(ns=None, ifrs=None, Sixpack=None, **inarg):
   """Make a Cohset with simulated uv-data"""

   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::simulate()')
   pp.setdefault('jones', [])
   pp.setdefault('stddev_noise', 0.0)
   if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)

   # Recommended ways to mark nodes that contains simulated data: 
   scope = 'simulated'           # mark the Cohset/Jonesets (visualisation)
   nsim = ns.Subscope('_')       # prepend all simulation nodes with _:: 

   if not Sixpack: Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit='uvp')

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



#---------------------------------------------------------------------------------

def addnoise (ns=None, Cohset=None, **inarg):
    """Add gaussian noise to the coherency matrices in Cohset""" 

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Cohset::addnoise()')
    pp.setdefault('stddev', 1.0)                      # stddev of the noise
    pp.setdefault('unop', 'Exp')                      # Unary operation on the noise
    if JEN_inarg.getinarg(pp): return JEN_inarg.pp2inarg(pp)
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






#==========================================================================
# Some convenience functions:
#==========================================================================

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






#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

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
                    punit='unpol10',                   # name of calibrator source
                    polrep='linear',                   # polarisation representation (linear/circular)
                    stations=range(4),                 # specify the (subset of) stations to be used
                    parmtable=None)                    # name of MeqParm table

# Derive a list of ifrs from MG['stations'] (used below):
MG['ifrs'] = TDL_Cohset.stations2ifrs(MG['stations'])


#========
if True:                                               # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.make_spigots(_getinarg=True)   # get a record with default input arguments
   inarg = make_spigots(_getinarg=True)                 # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # MS_corr_index=[0,-1,-1,1],       # only XX/YY available
                    # MS_corr_index=[0,-1,-1,3],       # all available, use only XX/YY
                    # MS_corr_index=[0,1,2,3],           # all corrs available, use all
                    # flag=False,                        # if True, flag the input data
                    visu=True,                         # if True, visualise the input data
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 

#========
if True:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.make_sinks(_getinarg=True)     # get a record with default input arguments 
   inarg = make_sinks(_getinarg=True)                   # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    output_col='PREDICT',              # logical (tile) output column
                    visu_array_config=True,            # if True, visualise the array config
                    # flag=False,                        # if True, flag the input data
                    visu=True,                         # if True, visualise the input data
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 

#========
if True:
   MG['stream_control'] = dict(ms_name='D1.MS',
                               data_column_name='DATA',
                               tile_size=10,                   # input tile-size
                               channel_start_index=10,
                               channel_end_index=50,           # -10 should indicate 10 from the end (OMS...)
                               # output_col='RESIDUALS')
                               predict_column='CORRECTED_DATA')


#========
if False:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.insert_flagger(_getinarg=True) # get a record with default input arguments
   inarg = insert_flagger(_getinarg=True)               # local (MG_JEN_Cohset.py) version 
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
# Solving:
#----------------------------------------------------------------------------------------------------

#========
if True:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.predict(_getinarg=True)        # get a record with default input arguments
   inarg = predict(_getinarg=True)                      # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    scope='rawdata',                   # Cohset scope
                    ifrs=MG['ifrs'],                   # list if Cohset ifrs 
                    polrep=MG['polrep'],               # polarisation representation
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


#========
if True:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.JJones(_getinarg=True)        # get a record with default input arguments
   inarg = JJones(_getinarg=True)                       # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    stations=MG['stations'], 
                    # scope='predicted', 
                    parmtable=MG['parmtable'],
                    # jones=['G'],                       # Succession of Jones matrices 
                    # jones=['D'],                       # Succession of Jones matrices 
                    jones=['G','D'],                   # Succession of Jones matrices 
                    # Insert Joneset paramters here
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


#========
if True:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.insert_solver(_getinarg=True)  # get a record with default input arguments
   inarg = insert_solver(_getinarg=True)                # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # num_cells=None,                    # if defined, ModRes argument [ntime,nfreq]
                    # solvegroup=['GJones'],             # list of solvegroup(s) to be solved for
                    # solvegroup=['DJones'],             # list of solvegroup(s) to be solved for
                    solvegroup=['GJones','DJones'],    # list of solvegroup(s) to be solved for
                    # num_iter=20,                       # max number of iterations
                    # epsilon=1e-4,                      # iteration control criterion
                    # debug_level=10,                    # solver debug_level
                    visu=True,                         # if True, include visualisation
                    subtract=True,                    # if True, subtract 'predicted' from uv-data 
                    correct=False,                      # if True, correct the uv-data with 'Joneset'
                    history=True,                      # if True, include history collection of metrics 
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)
                 


#----------------------------------------------------------------------------------------------------
# Simulation: 
#----------------------------------------------------------------------------------------------------

#========
if False:                                               # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.simulate(_getinarg=True)       # get a record with default input arguments
   inarg = simulate(_getinarg=True)                     # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    #..............
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)


#========
if False:                                              # ... Copied from MG_JEN_Cohset.py ...
   # inarg = MG_JEN_Cohset.addnoise(_getinarg=True)       # get a record with default input arguments
   inarg = addnoise(_getinarg=True)                     # local (MG_JEN_Cohset.py) version 
   JEN_inarg.modify(inarg,
                    # stddev=1.0,                        # stddev of the noise
                    # unop='Exp',                        # Unary operation on the noise
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, inarg)



#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(MG['script_name'])


#-------------------------------------------------------------------------
# The MSauxinfo object contains auxiliary MS info (nodes):
# It is used at various points in this module, e.g. make_sinks()

MSauxinfo = TDL_MSauxinfo.MSauxinfo(label=MG['script_name'])
MSauxinfo.station_config_default()           # WSRT (15 stations), incl WHAT





#********************************************************************************
#********************************************************************************
#***************** PART IV: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


def _define_forest (ns):

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   if True:
      # Make MeqSpigot nodes that read the MS:
      Cohset = TDL_Cohset.Cohset(label=MG['script_name'],
                                 polrep=MG['polrep'],
                                 ifrs=MG['ifrs'])
                                 # stations=MG['stations'])
      make_spigots(ns, Cohset, _inarg=MG)


   if False:
      insert_flagger (ns, Cohset, scope='residual', unop=['Real','Imag'], visu=True)
      visualise (ns, Cohset)
      visualise (ns, Cohset, type='spectra')


   if True:
      # Make predicted uv-data for the given source:
      # Source/patch to be used for simulation/selfcal:
      Sixpack = MG_JEN_Joneset.punit2Sixpack(ns, punit=MG['punit'])
      Joneset = JJones(ns, Sixpack=Sixpack, _inarg=MG)
      predicted = predict (ns, Sixpack=Sixpack, Joneset=Joneset, _inarg=MG)

   if True:
      # Insert a solver for a named group of MeqParms (e.g. 'GJones'):
      insert_solver (ns, measured=Cohset, predicted=predicted,
                     Joneset=Joneset, _inarg=MG)
      visualise (ns, Cohset)
      visualise (ns, Cohset, type='spectra')
 
   if False:
      # Tie the trees for the simulated ifrs together in an artificial 'sink':
      cc.append(Cohset.simul_sink(ns))

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

    if 1:
       punit = 'unpol'
       # punit = '3c147'
       # punit = 'RMtest'
       Sixpack = punit2Sixpack(ns, punit)

    if 1:
       inarg = JJones(_getinarg=True)
       JJones(ns, Sixpack, _inarg=inarg, stations=stations)
           
    if 0:
       jseq = TDL_Joneset.Joneseq()
       jseq.append(MG_JEN_Joneset.GJones (ns, stations=stations))
       js = jseq.make_Joneset(ns)
       cs = predict (ns, Sixpack=Sixpack, ifrs=ifrs, Joneset=js)
       visualise (ns, cs)
       addnoise (ns, cs)
       insert_flagger (ns, cs, scope='residual', unop=['Real','Imag'], visu=True)

    if 0:
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
    print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




