script_name = 'MG_JEN_Cohset.py'

# Short description:
#   Functions dealing with sets (all ifrs) of 2x2 cohaerency matrices 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 05 sep 2005: adapted to Cohset/Joneset objects

# Copyright: The MeqTree Foundation 

#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Trees import TDL_Cohset
from Timba.Trees import TDL_Joneset
from Timba.Contrib.JEN import MG_JEN_Joneset

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_visualise
from Timba.Contrib.JEN import MG_JEN_flagger
from Timba.Contrib.JEN import MG_JEN_sixpack



#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   stations = range(0,3)
   ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];

   # Make a Cohset with predicted data:
   nsim = ns.Subscope('_')
   punit = 'unpol'
   # punit = '3c147'
   # punit = 'RMtest'
   # source = 'QUV'
   source = 'QU'
   jseq = TDL_Joneset.Joneseq()
   # jseq.append(MG_JEN_Joneset.GJones (nsim, stations=stations, stddev_ampl=0.1, stddev_phase=0.1))
   # jseq.append(MG_JEN_Joneset.BJones (nsim, stations=stations, stddev_real=0.1, stddev_imag=0.1))
   # jseq.append(MG_JEN_Joneset.FJones (nsim, stations=stations, RM=0.0))
   jseq.append(MG_JEN_Joneset.DJones_WSRT (nsim, stations=stations, PZD=0.0, stddev_dang=0.0, stddev_dell=0.0))
   dconc = MG_JEN_Joneset.visualise_Joneseq(ns, jseq)
   cc.append(dconc['dcoll'])
   js = jseq.make_Joneset(nsim)
   Cohset = predict (nsim, punit=punit, ifrs=ifrs, Joneset=js)

   visualise (ns, Cohset, scope='simulated')
   # addnoise (ns, Cohset)
   # insert_flagger (ns, Cohset, scope='residual', unop=['Real','Imag'], visu=True)

   # Tie the trees for the different ifrs together in an artificial 'sink':
   cc.append(Cohset.simul_sink(ns))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)






#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================


    
#======================================================================================
# Convert an (LSM) sixpack into visibilities for linearly polarised receptors:
  
def sixpack2linear (ns, sixpack, name='nominal'):
    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:

    funcname = 'MG_JEN_Cohset.sixpack2linear(): '

    if isinstance(sixpack, str):
        sixpack = MG_JEN_sixpack.newstar_source (ns, name=sixpack)
    n6 = MG_JEN_sixpack.sixnames()
    iquv = sixpack['iquv']
    punit = sixpack['name']
    name = name+'_XYYX'
    coh0 = ns[name](q=punit) << Meq.Matrix22(
        (ns['XX'](q=punit) << iquv[n6.I] + iquv[n6.Q]),
        (ns['XY'](q=punit) << Meq.ToComplex( iquv[n6.U], iquv[n6.V])),
        (ns['YX'](q=punit) << Meq.Conj( ns['XY'](q=punit) )),
        (ns['YY'](q=punit) << iquv[n6.I] - iquv[n6.Q])
        ) * 0.5
    return coh0

#--------------------------------------------------------------------------------------
# Convert an (LSM) sixpack into visibilities for circularly polarised receptors:

def sixpack2circular (ns, sixpack, name='nominal'):
    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:

    funcname = 'MG_JEN_Cohset.sixpack2circular(): '

    if isinstance(sixpack, str):
        sixpack = MG_JEN_sixpack.newstar_source (ns, name=sixpack)
    n6 = MG_JEN_sixpack.sixnames()
    iquv = sixpack['iquv']
    punit = sixpack['name']
    name = name+'_RLLR'
    coh0 = ns[name](q=punit) << Meq.Matrix22(
        (ns['RR'](q=punit) << iquv[n6.I] + iquv[n6.V]),
        (ns['RL'](q=punit) << Meq.ToComplex( iquv[n6.Q], iquv[n6.U])),
        (ns['LR'](q=punit) << Meq.Conj( ns['RL'](q=punit) )),
        (ns['LL'](q=punit) << iquv[n6.I] - iquv[n6.V])
        ) * 0.5
    return coh0



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
    MG_JEN_forest_state.history ('MG_JEN_Cohset::addnoise()')
    return True









#======================================================================================

def predict (ns=0, Joneset=None, **pp):
    funcname = 'MG_JEN_Cohset.predict(): '

    # Input arguments:
    pp.setdefault('ifrs', [(0,1)])
    pp.setdefault('punit', 'unpol')
    pp.setdefault('polrep', 'linear')
    pp = record(pp)

    # Get the 6 punit subtrees:
    sixpack = MG_JEN_sixpack.newstar_source (ns, name=pp['punit'])

    # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:
    if pp['polrep']=='circular':
       coh0 = sixpack2circular (ns, sixpack, name='nominal')
    else:
       coh0 = sixpack2linear (ns, sixpack, name='nominal')

    Cohset = TDL_Cohset.Cohset(label='predict', origin=funcname, **pp)
    Cohset.nominal(ns, coh0)
    Cohset.display('.predict(): nominal')

    # NB: The Sixpack object will have .oneliner() and .display():
    for key in sixpack['iquv'].keys():
       Cohset.history('sixpack: '+key+': '+str(sixpack['iquv'][key]))
    for key in sixpack['radec'].keys():
       Cohset.history('sixpack: '+key+': '+str(sixpack['radec'][key]))

    # Corrupt with the given set of jones matrices:
    if not Joneset==None:
       Cohset.corrupt (ns, Joneset=Joneset)
       Cohset.display('.predict(): after corruption')

    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history ('MG_JEN_Cohset::predict()')
    return Cohset






#======================================================================================
# Insert a flagger:
#======================================================================================

def insert_flagger (ns, Cohset, **pp):
    """insert a flagger for the coherency matrices in Cohset""" 

    funcname = 'MG_JEN_Cohset.insert_flagger(): '

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

    # Insert flaggers for all ifrs:
    flagger_scope = 'flag_'+pp.scope
    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        nsub = ns.Subscope(flagger_scope, s1=s12[0], s2=s12[1])
        coh = MG_JEN_flagger.flagger (nsub, Cohset[key],
                                      sigma=pp.sigma, unop=pp.unop, oper=pp.oper,
                                      flag_bit=pp.flag_bit, merge=pp.merge)
        Cohset[key] = coh

    # Visualise the result, if required:
    if pp.visu:
        visu_scope = 'flagged_'+pp.scope
        visualise (ns, Cohset, scope=visu_scope, type='spectra')

    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history ('MG_JEN_Cohset::insert_flagger()')
    return True



#======================================================================================
# Insert a named solver 
#======================================================================================

def solver (ns, measured, predicted, **pp):
    """create a named solver""" 

    funcname = 'MG_JEN_Cohset.solver(): '

    # Input arguments:
    pp.setdefault('name', 'GJones')        # name of the solver (e.g. GJones)
    pp.setdefault('num_iter', 10)          # number of iterations
    pp.setdefault('debug_level', 10)       # solver debug_level
    pp.setdefault('graft', True)           # if True, graft the solver on the Cohset stream
    pp = record(pp)

    # The solver name must correspond to one or more of the
    # predefined groups of parms in the input Cohsets.
    # The latter are defined in the Joneset's.
    # The solver name (sname) is just a concatenation of such group names:
    if isinstance(pp.name, str): pp.name = [pp.name]
    sname = pp.name[0]
    for i in range(len(pp.name)):
        if i>0: sname = sname+pp.name[i]

    # Use a copy of the predicted Cohset for the output Cohset: 
    Cohset = predicted.copy(label='solver('+str(pp.name)+')')
    Cohset.label('solver_'+sname)

    # Merge the parm/solver info from BOTH input Cohsets:
    # (the measured side may also have solvable parameters)
    Cohset.update_from_Cohset(measured)

    # Collect the solvable parms for the named solver(s):
    corrs = []
    solvable = []
    for gname in pp.name:
        if not Cohset.solvegroup().has_key(gname):
            print '\n** solvegroup name not recognised:',gname
            print '     choose from:',Cohset.solvegroup().keys()
            print
            return
        sg = Cohset.solvegroup()[gname]
        corrs.extend(Cohset.condeq_corrs()[gname])
        for key in sg: solvable.extend(Cohset.parmgroup()[key])

    # Make new objects with the relevant corrs only:
    Cohset.select(ns, corrs)
  
    # Make condeq nodes
    cc = []
    punit = predicted.punit()
    for key in Cohset.keys():
        if not measured.has_key(key):
            print '\n** key not recognised in measured Cohset:',key
            return
        s12 = Cohset.stations()[key]
        condeq = ns.condeq(s1=s12[0],s2=s12[1],q=punit) << Meq.Condeq(measured[key], predicted[key])
        Cohset[key] = condeq
        cc.append(condeq)
    Cohset.display('after defining condeqs')

    # Visualise the condeqs:
    dconc_condeq = visualise (ns, Cohset, scope='condeq', errorbars=True, graft=False)
  
    # Make the solver node:
    solver = ns.solver(sname, q=punit) << Meq.Solver(children=cc,
                                                     solvable=solvable,
                                                     num_iter=pp.num_iter,
                                                     debug_level=pp.debug_level)

    # Make a bookmark for the solver plot:
    MG_JEN_forest_state.bookmark (solver, name=('solver: '+sname),
                                  udi='cache/result', viewer='Result Plotter',
                                  page=0, save=1, clear=0)

    Cohset.history(funcname+' -> '+Cohset.oneliner())
    MG_JEN_forest_state.history ('MG_JEN_Cohset::solver()')

    if pp.graft:
        # Graft the solver subtree on the stream of the measured Cohset
        key = measured.keys()[0]
        cc = [solver,  dconc_condeq['allcorrs']['dcoll'], measured[key]]      # coh should be LAST!
        sname = 'solver_'+sname
        measured[key] = ns.reqseq(sname, q=punit) << Meq.ReqSeq(children=cc,
                                                                result_index=len(cc)-1)
        return Cohset                  # not really needed....

    else:
        # Return the reqseq that needs requests:
        reqseq = ns.reqseq(sname, q=punit) << Meq.ReqSeq(solver, result_index=0)
        return reqseq
    




#======================================================================================

def visualise(ns, Cohset, **pp):
    """visualises the 2x2 coherency matrices in Cohset"""

    funcname = 'MG_JEN_Cohset.visualise(): '

    # Input arguments:
    pp.setdefault('scope', 'uvdata')        # identifying name of this visualiser
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('graft', True)            # if True, graft the visu-nodes on the Cohset
    pp = record(pp)

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    visu_scope = 'visu_'+pp.scope
  
    # Make separate lists of nodes per corr:
    corrs = Cohset.corrs()
    nodes = {}
    for corr in corrs:
        nodes[corr] = []

    for key in Cohset.keys():
        s12 = Cohset.stations()[key]
        coh = Cohset[key]
        for icorr in range(len(corrs)):
            corr = corrs[icorr]
            nsub = ns.Subscope(visu_scope+'_'+corr, s1=s12[0], s2=s12[1])
            selected = nsub.selector(icorr) << Meq.Selector (coh, index=icorr)
            nodes[corr].append(selected)

    # Make dcolls per corr:
    dcoll = dict(allcorrs=[])
    for corr in corrs:
        dc = MG_JEN_visualise.dcoll (ns, nodes[corr], scope=pp.scope, tag=corr,
                                     type=pp.type, errorbars=pp.errorbars,
                                     color=Cohset.plot_color()[corr],
                                     style=Cohset.plot_style()[corr])
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

    MG_JEN_forest_state.history (funcname)
  
    if pp.graft:
        # Make the dcoll nodes step-children of a MeqSelector
        # node that is inserted before one of the coherency nodes:
        Cohset.graft(ns, sc, stepchild=True)
        return True

    else:
        # Return a dict of named dconc nodes that need requests:
        # Do NOT modify the input Cohset
        Cohset.history(funcname+' -> '+'dconc '+str(len(dconc)))
        return dconc




#======================================================================================
# Helper function:

def display_first_subtree (Cohset=0, recurse=3):
    key = Cohset.keys()[0]
    txt = 'coh[0/'+str(Cohset.len())+']'
    txt = txt+': key='+str(key)
    MG_JEN_exec.display_subtree(Cohset[key], txt, full=1, recurse=recurse)
    return














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
       cs = TDL_Cohset.Cohset(label='test', ifrs=ifrs)
       cs.display('initial')
       
       if 0:
           cs.spigots (ns)
           
       if 0:
           # coh = predict ()
           punit = 'unpol'
           # punit = '3c147'
           # punit = 'RMtest'
           jseq = TDL_Joneset.Joneseq()
           jseq.append(MG_JEN_Joneset.GJones (ns, stations=stations))
           js = jseq.make_Joneset(ns)
           cs = predict (ns, punit=punit, ifrs=ifrs, Joneset=js)
           visualise (ns, cs)
           addnoise (ns, cs)
           insert_flagger (ns, cs, scope='residual', unop=['Real','Imag'], visu=True)

       if 1:
           punit = 'unpol'
           # punit = '3c147'
           # punit = 'RMtest'
           Joneset = MG_JEN_Joneset.GJones (nsim, stations=stations, solvable=1)
           measured = predict (nsim, punit=punit, ifrs=ifrs, Joneset=Joneset)
           # measured.select(ns, corrs=['XX','YY'])
           
           Joneset = MG_JEN_Joneset.DJones_WSRT (ns, stations=stations)
           predicted = predict (ns, punit=punit, ifrs=ifrs, Joneset=Joneset)
           cs = predicted
           
           sname = 'DJones'
           # sname = ['DJones', 'GJones']
           cs = solver (ns, name=sname, measured=measured, predicted=predicted) 
           
       if 0:
           # sixpack = lsm_NEWSTAR_source (ns, name='QUV')
           sixpack = 'unpol'
           print sixpack2circular (ns, sixpack)
           print sixpack2linear (ns, sixpack)

       if 1:
           display_first_subtree(cs)
           cs.display('final result')

       # ............
       # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
       print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




