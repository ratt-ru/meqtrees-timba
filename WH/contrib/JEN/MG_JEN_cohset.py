script_name = 'MG_JEN_cohset.py'

# Short description:
#   Functions dealing with sets (all ifrs) of 2x2 cohaerency matrices 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 

#================================================================================
# How to use this template:
# - Copy it to a suitably named script file (e.g. MG_JEN_xyz.py)
# - Fill in the correct script_name at the top
# - Fill in the author and the short description
# - Replace the example importable function with specific ones
# - Make the specific _define_forest() function
# - Remove this 'how to' recipe

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_visualise
from Timba.Contrib.JEN import MG_JEN_flagger
from Timba.Contrib.JEN import MG_JEN_sixpack
from Timba.Contrib.JEN import MG_JEN_joneset



#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Make a set (joneset) of 2x2 jones matrices for all stations:
   nsim = ns.Subscope('_')
   stations = range(0,3)
   ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
   JJ = []
   JJ.append(MG_JEN_joneset.GJones (nsim, stations=stations, stddev_ampl=0.2, stddev_phase=0.2)) 
   # JJ.append(MG_JEN_joneset.BJones (nsim, stations=stations, stddev_real=0.3, stddev_imag=0.1))
   # JJ.append(MG_JEN_joneset.FJones (nsim, stations=stations))
   JJ.append(MG_JEN_joneset.DJones_WSRT (nsim, stations=stations, stddev_dang=0.01, stddev_dell=0.01))
   # JJ.append(MG_JEN_joneset.DJones_WSRT (nsim, stations=stations, coupled_XY_dang=False, coupled_XY_dell=False))
   joneset = MG_JEN_joneset.JJones (nsim, JJ)
   MG_JEN_exec.display_object(joneset, 'joneset', script_name)

   # Simulated source:
   source = 'unpol'
   # source = '3c147'
   # source = 'RMtest'
   # source = 'QUV'

   # Make a cohaerency set (cohset) of 2x2 matrices for all ifrs:
   nsim = ns.Subscope('_')
   cohset = predict (nsim, source=source, ifrs=ifrs, joneset=joneset)
   cohset = visualise (nsim, cohset, scope='simulated')
   
   # MG_JEN_exec.display_object(cohset, 'cohset', script_name)
   # cohset = addnoise (ns, cohset)
   # cohset = insert_flagger (ns, cohset, scope='residual', unop=['Real','Imag'], visu=True)
   # MG_JEN_exec.display_object(cohset, 'cohset', script_name)

   # Tie the trees for the different ifrs together in an artificial 'sink':
   cc.append(simul_sink(ns, cohset))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================





#=======================================================================================
# Initialise a standard 'jones_set' object, which contains information about
# a set of 2x2 jones matrices for all stations, for a single p-unit (source):
# This object (dict) is updated by, and passed between, various functions
# in this module (and other modules that use this cohset):

def init (name='<coh>', origin='WSRT_coh:', input={},
          ifrs=[], stations={}, polrep='linear',
          coh={}, punit='uvp'):
    """initialise/check a standard cohset object"""
    cohset = dict(name=name+'_'+punit, type='cohset',
                  origin=origin, punit=punit, polrep=polrep,
                  ifrs=ifrs, stations=stations, coh=coh,
                  parm={}, solver={},
                  input=input, dims=[2,2])

    # Polarisation representation
    if polrep == 'circular':
        cohset['corrs'] = ['RR', 'RL', 'LR', 'LL'] 
    else:
        cohset['corrs'] = ['XX', 'XY', 'YX', 'YY']
    
    # Plot information (see .visualise()):
    plot = record(color=record(XX='red', XY='magenta', YX='cyan', YY='blue'),
                  style=record(XX='dot', XY='dot', YX='dot', YY='dot'))
    for key in ['color','style']:
        plot[key]['RR'] = plot[key]['XX']
        plot[key]['RL'] = plot[key]['XY']
        plot[key]['LR'] = plot[key]['YX']
        plot[key]['LL'] = plot[key]['YY']
    cohset['plot'] = plot

    # Finished
    return cohset


#======================================================================================
# Make a deep copy of the given cohset, and rename it:

def copy (cohset, note=0):
    cohout = deepcopy(cohset)
    if not cohout.has_key('note'): cohout['note'] = []
    cohout['note'].append(note)
    return cohout
  

#======================================================================================
# Make a copy of the cohset with a named subset of the available corrs:

def select_corrs (ns, cohset, corrs=0): 
    cohout = copy (cohset, 'select_corrs('+str(corrs)+')')

    icorr = []
    cohout['corrs'] = [] 
    for corr in corrs:
        if cohset['corrs'].__contains__(corr):
            icorr.append(cohset['corrs'].index(corr))
            cohout['corrs'].append(corr)
        else:
            print 'corr not recognised:',corr

    for key in ['color','style']:
        cohout['plot'][key] = record()
        for corr in cohout['corrs']:
            cohout['plot'][key][corr] = cohset['plot'][key][corr]

    # Select the relevant corrs from the coherency tensors:
    for key in cohout['coh'].keys():
        s12 = cohout['stations'][key]
        s1 = s12[0]
        s2 = s12[1]
        multi = (len(icorr)>1)
        cohout['coh'][key] = (ns << Meq.Selector(cohout['coh'][key],
                                                 index=icorr, multi=multi))

    # Adjust the coherence shape, if necessary:  
    if len(icorr)<4: cohout['dims'] = [len(icorr)]            #...shape...??
 
    return cohout

#======================================================================================
# Helper function:

def display_first_subtree (cohset=0):
    key = cohset['coh'].keys()[0]
    coh = cohset['coh'][key]
    txt = 'coh[0/'+str(len(cohset['coh']))+']'
    txt = txt+': key='+str(key)
    MG_JEN_exec.display_subtree(coh, txt, full=1)
    return

#======================================================================================

def spigots (ns=0, **pp):

    # Input arguments:
    pp.setdefault('ifrs', [(0,1)])        # list of ifrs (station pairs)
    pp = record(pp)

    # Make a record/dict of spigots that produce 2x2 coherency matrices:
    coh = {}
    for (st1,st2) in pp.ifrs:
        key = str(st1)+'_'+str(st2)
        coh[key] = ns.spigot(s1=st1,s2=st2) << Meq.Spigot(station_1_index=st1,
                                                          station_2_index=st2,
                                                          flag_bit=4,input_column='DATA') 
    # Create the cohset object:
    cohset = init (name='spigots', origin='WSRT_coh::spigots()',
                   input=pp, ifrs=pp.ifrs, coh=coh)

    MG_JEN_forest_state.history ('MG_JEN_cohset::spigots()')
    return cohset

#======================================================================================


def sink (ns, cohset, **pp):
    """attaches the coherency matrices to MeqSink nodes""" 

    # Input arguments:
    pp.setdefault('output_col', 'RESIDUALS')        # name of MS output column (NONE means inhibited)
    pp = record(pp)

    # Duplicate for all 4 children:
    oc = pp.output_col
    pp.output_col = [oc,oc,oc,oc] 

    for key in cohset['coh'].keys():
        s12 = cohset['stations'][key]
        s1 = s12[0]
        s2 = s12[1]
        sink = ns.MeqSink(s1=s1, s2=s2) << Meq.Sink(cohset['coh'][key], station_1_index=st1,
                                                    station_2_index=st2, corr_index=[0,1,2,3],
                                                    output_col=pp.output_col)

    MG_JEN_forest_state.history ('MG_JEN_cohset::sink()')
    return sink



#======================================================================================

def predict (ns=0, source='unpol', joneset=None, **pp):

    # Input arguments:
    pp.setdefault('ifrs', [(0,1)])        # list of ifrs (station pairs)
    pp = record(pp)

    # Get the 6 source subtrees:
    sixpack = MG_JEN_sixpack.newstar_source (ns, name=source)

    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:
    coh0 = linear (ns, sixpack, name='nominal')

    # Make a record/dict of identical coherency matrices for all ifrs:
    coh = {}
    stations = {}
    for (st1,st2) in pp.ifrs:
        key = str(st1)+'_'+str(st2)
        stations[key] = (st1,st2)
        coh[key] = ns.nominal(s1=st1, s2=st2) << Meq.Selector(coh0)

    # Create the cohset object:
    cohset = init (name='predict', origin='WSRT_coh::predict()', input=pp,
                   ifrs=pp.ifrs, stations=stations, coh=coh) 

    # Visualise the coherencies:
    # cohset = visualise (ns, cohset, scope='nominal', errorbars=False)

    # Corrupt with the given set of jones matrices:
    if not joneset==None:
        cohset = corrupt (ns, cohset, joneset=joneset)

    MG_JEN_forest_state.history ('MG_JEN_cohset::predict()')
    return cohset
    
#======================================================================================
# Convert an (LSM) sixpack into visibilities for linearly polarised receptors:
  
def linear (ns, sixpack, name='nominal'):
    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:

    if isinstance(sixpack, str):
        sixpack = MG_JEN_sixpack.newstar_source (ns, name=sixpack)
    n6 = MG_JEN_sixpack.sixnames()
    iquv = sixpack['iquv']
    source = sixpack['name']
    name = name+'_XYYX'
    coh = ns[name](q=source) << Meq.Matrix22(
        (ns['XX'](q=source) << iquv[n6.I] + iquv[n6.Q]),
        (ns['XY'](q=source) << Meq.ToComplex( iquv[n6.U], iquv[n6.V])),
        (ns['YX'](q=source) << Meq.Conj( ns['XY'](q=source) )),
        (ns['YY'](q=source) << iquv[n6.I] - iquv[n6.Q])
        ) * 0.5
    return coh

#--------------------------------------------------------------------------------------
# Convert an (LSM) sixpack into visibilities for circularly polarised receptors:

def circular (ns, sixpack, name='nominal'):
    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:

    if isinstance(sixpack, str):
        sixpack = MG_JEN_sixpack.newstar_source (ns, name=sixpack)
    n6 = MG_JEN_sixpack.sixnames()
    iquv = sixpack['iquv']
    source = sixpack['name']
    name = name+'_RLLR'
    coh = ns[name](q=source) << Meq.Matrix22(
        (ns['RR'](q=source) << iquv[n6.I] + iquv[n6.V]),
        (ns['RL'](q=source) << Meq.ToComplex( iquv[n6.Q], iquv[n6.U])),
        (ns['LR'](q=source) << Meq.Conj( ns['RL'](q=source) )),
        (ns['LL'](q=source) << iquv[n6.I] - iquv[n6.V])
        ) * 0.5
    return coh


#======================================================================================


def simul_sink (ns, cohset):
    """makes a common root node for all entries in cohset""" 
    cc = []
    for key in cohset['coh'].keys():
        cc.append(cohset['coh'][key])
        print key, cohset['coh'][key]
    sink = ns.simul_sink << Meq.Add(children=cc)

    MG_JEN_forest_state.history ('MG_JEN_cohset::simul_sink()')
    return sink


#======================================================================================

def addnoise (ns, cohset, **pp):
    """add gaussian noise to the coherency matrices in cohset""" 

    # Input arguments:
    pp.setdefault('stddev', 0)        #
    pp.setdefault('unop', 'Exp')        #
    pp = record(pp)

    cohout = copy (cohset, 'addnoise('+str(pp.stddev)+')')
    for key in cohset['coh'].keys():
        s12 = cohset['stations'][key]
        s1 = s12[0]
        s2 = s12[1]
        nsub = ns.Subscope('addnoise', s1=s1, s2=s2)
        noise = MG_JEN_twig.gaussnoise (nsub, dims=cohset['dims'],
                                        stddev=pp.stddev, unop=pp.unop)
        coh = ns.noisy(s1=s1, s2=s2) << Meq.Add(cohset['coh'][key], noise)
        cohout['coh'][key] = coh

    MG_JEN_forest_state.history ('MG_JEN_cohset::addnoise()')
    return cohout


#======================================================================================

def insert_flagger (ns, cohset, **pp):
    """insert a flagger for the coherency matrices in cohset""" 

    # Input arguments:
    pp.setdefault('scope', 'rawdata')        # part of tag/name
    pp.setdefault('sigma', 5.0)              # flagged if exceeds sigma*stddev
    pp.setdefault('unop', 'Abs')             # unop used to make real data
    pp.setdefault('oper', 'GT')              # decision function (GT=Greater Than)
    pp.setdefault('flag_bit', 1)             # affected flag-bit
    pp.setdefault('merge', True)             # if True, merge the flags of 4 corrs
    pp.setdefault('visu', False)             # if True, visualise the result
    pp.setdefault('compare', False)          # ....
    pp = record(pp)

    cohout = copy (cohset, 'insert_flagger('+str(pp.scope)+')')

    # Insert flaggers for all ifrs:
    flagger_scope = 'flag_'+pp.scope
    for key in cohset['coh'].keys():
        s12 = cohset['stations'][key]
        s1 = s12[0]
        s2 = s12[1]
        nsub = ns.Subscope(flagger_scope, s1=s1, s2=s2)
        # coh = MG.JEN_flagger.flagger (nsub, cohset['coh'][key],
        #                               sigma=pp.sigma, unop=pp.unop, oper=pp.oper,
        #                               flag_bit=pp.flag_bit, merge=pp.merge)
        cohout['coh'][key] = coh

    # Visualise the result, if required:
    if pp.visu:
        visu_scope = 'flagged_'+pp.scope
        cohout = visualise (ns, cohout, scope=visu_scope, type='spectra')

    MG_JEN_forest_state.history ('MG_JEN_cohset::insert_flagger()')
    return cohout

#======================================================================================

def corrupt (ns, cohset, joneset):
    """corrupts a list of 2x2 coherency matrices with the corresponding 2x2 jones matrices""" 
    cohout = copy (cohset, 'corrupt()')
    
    for key in cohset['coh'].keys():
        s12 = cohset['stations'][key]
        s1 = s12[0]
        s2 = s12[1]
        coh = ns.corrupted(s1=s1, s2=s2) << Meq.MatrixMultiply(
            joneset['jones'][s1],
            cohset['coh'][key],
            (ns << Meq.ConjTranspose(joneset['jones'][s2]))
            )
        cohout['coh'][key] = coh

    # Transfer the parm/solver info from joneset to cohset:
    cohout['parm'].update(joneset['parm'])
    cohout['solver'].update(joneset['solver'])
    cohout['plot']['color'].update(joneset['plot']['color'])
    cohout['plot']['style'].update(joneset['plot']['style'])

    MG_JEN_forest_state.history ('MG_JEN_cohset::corrupt()')
    return cohout


#======================================================================================

def correct (ns, cohset, joneset):
    """corrects a list of 2x2 coherency matrices with the corresponding 2x2 jones matrices""" 
    cohout = copy (cohset, 'correct()')

    for key in cohset['coh'].keys():
        s12 = cohset['stations'][key]
        s1 = s12[0]
        s2 = s12[1] 
        coh = ns.corrected(s1=s1,s2=s2) << Meq.MatrixMultiply(
            Meq.MatrixInvert22(joneset['jones'][s1]),
            cohset['coh'][key],
            (ns << Meq.MatrixInvert22(ns << Meq.ConjTranspose(joneset['jones'][s2])))
            )
        cohout['coh'][key] = coh

    # Transfer the parm/solver info from joneset to cohset:
    cohout['parm'].update(joneset['parm'])
    cohout['solver'].update(joneset['solver'])
    cohout['plot']['color'].update(joneset['plot']['color'])
    cohout['plot']['style'].update(joneset['plot']['style'])

    MG_JEN_forest_state.history ('MG_JEN_cohset::correct()')
    return cohout


#======================================================================================
# Insert a named solver 
#======================================================================================

def solver (ns, measured, predicted, **pp):
    """create a named solver""" 

    # Input arguments:
    pp.setdefault('name', 'GJones')        # name of the solver (e.g. GJones)
    pp.setdefault('num_iter', 10)          # number of iterations
    pp.setdefault('debug_level', 10)       # solver debug_level
    pp.setdefault('result', 'cohset')      # solver debug_level
    pp = record(pp)

    # The solver name must correspond to one or more of the
    # predefined groups of parms in the input cohsets.
    # The latter are defined in the joneset's.
    # The solver name (sname) is just a concatenation of such group names:
    if isinstance(pp.name, str): pp.name = [pp.name]
    sname = pp.name[0]
    for i in range(len(pp.name)):
        if i>0: sname = sname+pp.name[i]

    # Use a copy of the predicted cohset for the output cohset: 
    cohset = copy (predicted, 'solver('+str(pp.name)+')')
    cohset['name'] = 'solver_'+sname
    cohset['origin'] = 'WSRT_coh::solver()'
    cohset['input'] = pp

    # Merge the parm/solver info from BOTH input cohsets:
    # (the measured side may also have solvable parameters)
    # JEN_display(measured['solver'], txt='solver(): measured[solver]')
    # JEN_display(cohset['solver'], txt='cohset[solver]: before update')
    cohset['parm'].update(measured['parm'])
    cohset['solver'].update(measured['solver'])
    # cohset['plot']['color'].update(measured['plot']['color'])
    # cohset['plot']['style'].update(measured['plot']['style'])
    # JEN_display(cohset['solver'], txt='cohset[solver]: after update')

    # Collect the solvable parms for the named solver(s):
    corrs = []
    solvable = []
    for gname in pp.name:
        if not cohset['solver'].has_key(gname):
            print '\n** solver name not recognised:',gname
            print '     choose from:',cohset['solver'].keys()
            print
            return
        ss = cohset['solver'][gname]
        corrs.extend(ss['corrs'])
        for key in ss['solvable']:
            solvable.extend(cohset['parm'][key])
    cohset['solver_solvable'] = solvable                   # for display only

    # Make new objects with the relevant corrs only:
    cohset = select_corrs (ns, cohset, corrs=corrs)
    sel_measured = select_corrs (ns, measured, corrs=corrs)
    sel_predicted = select_corrs (ns, predicted, corrs=corrs)
  
    # Make condeq nodes
    cc = []
    punit = sel_predicted['punit']
    for key in cohset['coh'].keys():
        if not sel_measured['coh'].has_key(key):
            print '\n** key not recognised:',key
            return

    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]

    condeq = ns.condeq(s1=s1,s2=s2,q=punit) << Meq.Condeq(
        sel_measured['coh'][key], sel_predicted['coh'][key])
    cohset['coh'][key] = condeq
    cc.append(condeq)

    # Visualise the condeqs:
    dconc_condeq = visualise (ns, cohset, scope='condeq',
                              errorbars=True, result='dconc')
  
    # Make the solver node:
    solver = ns.solver(sname, q=punit) << Meq.Solver(children=cc,
                                                     solvable=solvable,
                                                     num_iter=pp.num_iter,
                                                     debug_level=pp.debug_level)

    # Make a bookmark for the solver plot:
    MG_JEN_forest_state.bookmark (solver, name=('solver: '+sname),
                                  udi='cache/result', viewer='Result Plotter',
                                  page=0, save=1, clear=0)

    MG_JEN_forest_state.history ('MG_JEN_cohset::solver()')

    # Return the specified result:
    if pp.result == 'cohset':
        key = measured['coh'].keys()[0]
        cc = [solver,  dconc_condeq['allcorrs']['dcoll'], measured['coh'][key]]      # coh should be LAST!
        sname = 'solver_'+sname
        measured['coh'][key] = ns.reqseq(sname, q=punit) << Meq.ReqSeq(children=cc,
                                                                       result_index=len(cc)-1)
        return cohset

    else:
        # Return the reqseq that needs requests:
        reqseq = ns.reqseq(sname, q=punit) << Meq.ReqSeq(solver, result_index=0)
        return reqseq
    




#======================================================================================

def visualise(ns, cohset, **pp):
    """visualises the 2x2 coherency matrices in cohset"""

    # Input arguments:
    pp.setdefault('scope', 'uvdata')        # identifying name of this visualiser
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('result', 'cohset')       # result of this routine (cohset or dcolls)
    pp = record(pp)

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    visu_scope = 'visu_'+pp.scope
  
    # Make separate lists of nodes (all ifrs) per corr:
    corrs = cohset['corrs']
    nodes = {}
    for corr in corrs:
        nodes[corr] = []

    for key in cohset['coh'].keys():
        s12 = cohset['stations'][key]
        s1 = s12[0]
        s2 = s12[1]
        coh = cohset['coh'][key]
        for icorr in range(len(corrs)):
            corr = cohset['corrs'][icorr]
            nsub = ns.Subscope(visu_scope+'_'+corr, s1=s1, s2=s2)
            selected = nsub.selector(icorr) << Meq.Selector (coh, index=icorr)
            nodes[corr].append(selected)

    # Make dcolls per corr:
    dcoll = dict(allcorrs=[])
    for corr in corrs:
        dc = MG_JEN_visualise.dcoll (ns, nodes[corr], scope=pp.scope, tag=corr,
                                     type=pp.type, errorbars=pp.errorbars,
                                     color=cohset['plot']['color'][corr],
                                     style=cohset['plot']['style'][corr])
        dcoll['allcorrs'].append(dc)
        if corr in ['XY','YX','RL','LR']:
            key = 'cross'
            if not dcoll.has_key(key): dcoll[key] = []
            dcoll[key].append(dc)
        if corr in ['XX','YY','RR','LL']:
            key = 'paral'
            if not dcoll.has_key(key): dcoll[key] = []
            dcoll[key].append(dc)

    # Make concatenations of dcolls:
    dconc = {}
    sc = []
    for key in dcoll.keys():
        dc = MG_JEN_visualise.dconc(ns, dcoll[key], scope=pp.scope, tag=key,
                                    bookpage=key)
        dconc[key] = dc
        sc.append (dc['dcoll'])

    MG_JEN_forest_state.history ('MG_JEN_cohset::visualise()')
  
    # Return the specified result:
    if pp.result == 'cohset':
        # Make the dcoll nodes step-children of a MeqSelector
        # node that is inserted before one of the coherency nodes:
        key = cohset['coh'].keys()[0]
        cohset['coh'][key] = ns[visu_scope] << Meq.Selector(cohset['coh'][key],
                                                            stepchildren=sc)
        return cohset

    else:
        # Return a dict of named dconc nodes that need requests:
        return dconc

















#********************************************************************************
# Initialisation and testing routines
# NB: this section should always be at the end of the script
#********************************************************************************

#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)

#-------------------------------------------------------------------------
# Meqforest execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.
# If not explicitly supplied, a default request will be used.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    if False:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n*******************\n** Local test of:',script_name,':\n'
       ns = NodeScope()
       nsim = ns.Subscope('_')
       stations = range(0,3)
       ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
       
       if 0:
           # spigots ()
           coh = spigots (ns, ifrs=ifrs)
           print coh
           
       if 0:
           # coh = predict ()
           source = 'unpol'
           # source = '3c147'
           # source = 'RMtest'
           joneset = 0
           joneset = MG_JEN_joneset.GJones (ns, stations=stations)
           cohset = predict (ns, source=source, ifrs=ifrs, joneset=joneset)
           rr = visualise (ns, cohset)
           # MG_JEN_exec.display_object(rr, 'rr', script_name)
           
           cohset = addnoise (ns, cohset)
           # cohset = insert_flagger (ns, cohset, scope='residual', unop=['Real','Imag'], visu=True)
           MG_JEN_exec.display_object(cohset, 'cohset', script_name)

           # sel = select_corrs (ns, cohset, corrs=['XX','YY'])

       if 0:
           source = 'unpol'
           # source = '3c147'
           # source = 'RMtest'
           joneset = MG_JEN_joneset.GJones (nsim, stations=stations, solvable=1)
           measured = predict (nsim, source=source, ifrs=ifrs, joneset=joneset)
           select_corrs (ns, measured, corrs=['XX','YY'])
           
           # joneset = MG_JEN_joneset.WSRT_DJones (ns, stations=stations)
           # predicted = predict (ns, source=source, ifrs=ifrs, joneset=joneset)
           
           # sname = 'DJones'
           # sname = ['DJones', 'GJones']
           # solver (ns, name=sname, measured=measured, predicted=predicted) 
           
       if 0:
           # sixpack = lsm_NEWSTAR_source (ns, name='QUV')
           sixpack = 'unpol'
           print circular (ns, sixpack)
           print linear (ns, sixpack)
           
       # ............
       # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
       print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




