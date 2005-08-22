# ../Timba/WH/contrib/JEN/WSRT_coh.py:  
#   Functions that deal with 2x2 WSRT coherency matrices

print '\n',100*'*'
print '** WSRT_coh.py    h30jul/h09/d16aug2005'

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
from copy import deepcopy

from JEN_forest_state import *
from JEN_TDL_flagging import *
from JEN_TDL_visualise import *

from JEN_util_TDL import *
from JEN_util import *
# Better: put the JEN stuff in a sub-directory....
# from JEN.JEN_util_TDL import *
# from JEN.JEN_util import *

# Temporary:
from JEN_lsm import *


#=======================================================================================
# Initialise a standard 'jones_set' object, which contains information about
# a set of 2x2 jones matrices for all stations, for a single p-unit (source):
# This object (dict) is updated by, and passed between, various TDL functions 

def _init_cohset (name='<coh>', origin='WSRT_coh:', input={},
                  ifrs=[], stations={}, polrep='linear',
                  coh={}, punit='uvp',
                  trace=0):
  """initialise/check a standard _init_cohset object"""
  cohset = dict(name=name+'_'+punit, type='cohset',
                origin=origin, punit=punit, polrep=polrep,
                ifrs=ifrs, stations=stations, coh=coh,
                parm={}, solver={},
                input=input)

  cohset['dims'] = [2,2]
  if polrep == 'circular':
    cohset['corrs'] = ['RR', 'RL', 'LR', 'LL'] 
  else:
    cohset['corrs'] = ['XX', 'XY', 'YX', 'YY']
    
  plot = record(color=record(XX='red', XY='magenta', YX='cyan', YY='blue'),
                style=record(XX='dot', XY='dot', YX='dot', YY='dot'))
  for key in ['color','style']:
    plot[key]['RR'] = plot[key]['XX']
    plot[key]['RL'] = plot[key]['XY']
    plot[key]['LR'] = plot[key]['YX']
    plot[key]['LL'] = plot[key]['YY']
  cohset['plot'] = plot

  if trace:
    JEN_display (cohset, 'cohset (init)', cohset['origin'])
  return cohset


#======================================================================================
# Make a deep copy of the given cohset, and rename it:

def coh_copy (cohset, note=0, trace=0):
  cohout = deepcopy(cohset)
  if not cohout.has_key('note'): cohout['note'] = []
  cohout['note'].append(note)
  return cohout
  

#======================================================================================
# Make a copy of the cohset with a named subset of the available corrs:

def coh_select_corrs (ns, cohset, corrs=0, trace=1): 
  cohout = coh_copy (cohset, 'coh_select_corrs('+str(corrs)+')')

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
 
  if trace:
    JEN_display (cohout, 'cohout', 'after coh_select_corrs()')
    
  return cohout

#======================================================================================
# Helper function:

def coh_display_first_subtree (cohset=0):
  key = cohset['coh'].keys()[0]
  coh = cohset['coh'][key]
  txt = 'coh[0/'+str(len(cohset['coh']))+']'
  txt = txt+': key='+str(key)
  JEN_display_subtree(coh, txt, full=1)
  return

#======================================================================================

def coh_spigots (ns=0, **pp):

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_spigots(ns, **pp)',
                      _help=dict(ifrs='list of ifrs (station pairs)'),
                      ifrs=[(0,1)])) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Make a record/dict of spigots that produce 2x2 coherency matrices:
  coh = {}
  for (st1,st2) in pp.ifrs:
    key = str(st1)+'_'+str(st2)
    coh[key] = ns.spigot(s1=st1,s2=st2) << Meq.Spigot(station_1_index=st1,
                                                      station_2_index=st2,
                                                      flag_bit=4,input_column='DATA') 
  
  # Create the cohset object:
  cohset = _init_cohset (name='spigots', origin='WSRT_coh::coh_spigots()', input=pp,
                         ifrs=pp.ifrs, coh=coh, trace=pp.trace)
  JEN_forest_history ('coh_spigots()')
  return cohset

#======================================================================================


def coh_sink (ns, cohset, **pp):
  """attaches the coherency matrices to MeqSink nodes""" 

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_sink(ns, cohset, **pp)',
                      _help=dict(output_col='name of MS output column (NONE means inhibited)'),
                      output_col='RESIDUALS')) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

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
    if trace: print sink, pp.output_col
  if trace:
    JEN_display_subtree(MeqSink, full=1, recurse=1)

  JEN_forest_history ('coh_sink()')
  return sink


#======================================================================================


#======================================================================================

def coh_predict (ns=0, source='unpol', corrupt=0, **pp):

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_predict(ns, **pp)',
                      _help=dict(ifrs='list of ifrs (station pairs)'),
                      ifrs=[(0,1)])) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Get the 6 source subtrees:
  sixpack = lsm_NEWSTAR_source (ns, name=source, trace=0)

  # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:
  coh0 = coh_linear (ns, sixpack, name='nominal', trace=0)

  # Make a record/dict of identical coherency matrices for all ifrs:
  coh = {}
  stations = {}
  for (st1,st2) in pp.ifrs:
    key = str(st1)+'_'+str(st2)
    stations[key] = (st1,st2)
    coh[key] = ns.nominal(s1=st1, s2=st2) << Meq.Selector(coh0)

  # Create the cohset object:
  cohset = _init_cohset (name='predict', origin='WSRT_coh::coh_predict()', input=pp,
                         ifrs=pp.ifrs, stations=stations, coh=coh, 
                         trace=pp.trace)

  # Visualise the coherencies:
  # cohset = coh_visualise (ns, cohset, scope='nominal', errorbars=False)

  # Corrupt with the given jones matrices:
  if not isinstance(corrupt, int):
    cohset = coh_corrupt (ns, cohset, joneset=corrupt, trace=pp.trace)

  JEN_forest_history ('coh_predict()')
  return cohset
    
#======================================================================================
# Convert an (LSM) sixpack into visibilities for linearly polarised receptors:
  
def coh_linear (ns, sixpack, name='nominal', trace=0):
  # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:

  if isinstance(sixpack, str):
    sixpack = lsm_NEWSTAR_source (ns, name=sixpack, trace=0)
  n6 = lsm_sixnames()
  iquv = sixpack['iquv']
  source = sixpack['name']

  name = name+'_XYYX'
  coh = ns[name](q=source) << Meq.Matrix22(
    (ns['XX'](q=source) << iquv[n6.I] + iquv[n6.Q]),
    (ns['XY'](q=source) << Meq.ToComplex( iquv[n6.U], iquv[n6.V])),
    (ns['YX'](q=source) << Meq.Conj( ns['XY'](q=source) )),
    (ns['YY'](q=source) << iquv[n6.I] - iquv[n6.Q])
    ) * 0.5
  if trace: JEN_display_subtree(coh, txt='WSRT_coh::coh_linear()', full=1)
  return coh

#--------------------------------------------------------------------------------------
# Convert an (LSM) sixpack into visibilities for circularly polarised receptors:

def coh_circular (ns, sixpack, name='nominal', trace=0):
  # Make a 2x2 coherency matrix (coh0) by multiplication with the Stokes matrix:

  if isinstance(sixpack, str):
    sixpack = lsm_NEWSTAR_source (ns, name=sixpack, trace=0)
  n6 = lsm_sixnames()
  iquv = sixpack['iquv']
  source = sixpack['name']

  name = name+'_RLLR'
  coh = ns[name](q=source) << Meq.Matrix22(
    (ns['RR'](q=source) << iquv[n6.I] + iquv[n6.V]),
    (ns['RL'](q=source) << Meq.ToComplex( iquv[n6.Q], iquv[n6.U])),
    (ns['LR'](q=source) << Meq.Conj( ns['RL'](q=source) )),
    (ns['LL'](q=source) << iquv[n6.I] - iquv[n6.V])
    ) * 0.5
  if trace: JEN_display_subtree(coh, txt='WSRT_coh::coh_circular()', full=1)
  return coh


#======================================================================================


def coh_simul_sink (ns, cohset, trace=0):
  """makes a common root node for all entries in cohset""" 
  cc = []
  for key in cohset['coh'].keys():
    cc.append(cohset['coh'][key])
    print key, cohset['coh'][key]
  sink = ns.simul_sink << Meq.Add(children=cc)

  if trace:
    JEN_display_subtree(sink, full=1, recurse=1)

  JEN_forest_history ('coh_simul_sink()')
  return sink


#======================================================================================

def coh_addnoise (ns, cohset, stddev=0, unop='Exp', trace=0):
  """add gaussian noise to the coherency matrices in cohset""" 
  cohout = coh_copy (cohset, 'coh_addnoise('+str(stddev)+')')

  for key in cohset['coh'].keys():
    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]
    nsub = ns.Subscope('coh_addnoise', s1=s1, s2=s2)
    noise = JEN_gaussnoise (nsub, dims=cohset['dims'],
                            stddev=stddev, unop=unop)
    coh = ns.noisy(s1=s1, s2=s2) << Meq.Add(cohset['coh'][key], noise)
    cohout['coh'][key] = coh

  if trace:
    coh_display_first_subtree (cohout)
    JEN_display(cohout,'cohout', 'after coh_addnoise()')

  JEN_forest_history ('coh_addnoise()')
  return cohout

#======================================================================================

def coh_insert_flagger (ns, cohset, scope='rawdata', sigma=5.0, unop='Abs',
                        oper='GT', flag_bit=1, merge=True,
                        visu=False, compare=False, trace=0):
  
  """flag the coherency matrices in cohset""" 
  cohout = coh_copy (cohset, 'coh_insert_flagger('+str(scope)+')')

  # Insert flaggers for all ifrs:
  flagger_scope = 'flag_'+scope
  for key in cohset['coh'].keys():
    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]
    nsub = ns.Subscope(flagger_scope, s1=s1, s2=s2)
    coh = JEN_flagger (nsub, cohset['coh'][key],
                       sigma=sigma, unop=unop, oper=oper,
                       flag_bit=flag_bit, merge=merge)
    cohout['coh'][key] = coh

  # Visualise the result, if required:
  if visu:
    visu_scope = 'flagged_'+scope
    cohout = coh_visualise (ns, cohout, scope=visu_scope, type='spectra', trace=1)

  if trace:
    coh_display_first_subtree (cohout)
    JEN_display(cohout,'cohout', 'after coh_insert_flagger()')

  JEN_forest_history ('coh_insert_flagger()')
  return cohout

#======================================================================================

def coh_corrupt (ns, cohset, joneset, trace=0):
  """corrupts a list of 2x2 coherency matrices with the corresponding 2x2 jones matrices""" 
  cohout = coh_copy (cohset, 'coh_corrupt()')

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

  if trace:
    coh_display_first_subtree (cohout)
    JEN_display(cohout,'cohout', 'after coh_corrupt()')

  JEN_forest_history ('coh_corrupt()')
  return cohout


#======================================================================================

def coh_correct (ns, cohset, joneset, trace=0):
  """corrects a list of 2x2 coherency matrices with the corresponding 2x2 jones matrices""" 
  cohout = coh_copy (cohset, 'coh_correct()')

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

  if trace:
    coh_display_first_subtree (cohout)
    JEN_display(cohout,'cohout', 'after coh_correct()')

  JEN_forest_history ('coh_correct()')
  return cohout


#======================================================================================
# Insert a named solver 
#======================================================================================

def coh_solver (ns, measured, predicted, **pp):
  """create a named solver""" 

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_solver(ns, **pp)',
                      _help=dict(name='name of the solver (e.g. GJones)',
                                 measured='cohset of measured vis',
                                 predicted='cohset of predicted vis',
                                 num_iter='number of iterations',
                                 debug_level='debug_level'),
                      name='GJones', result='cohset',
                      num_iter=10, debug_level=10)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # The solver name must correspond to one or more of the
  # predefined groups of parms in the input cohsets.
  # The latter are defined in the joneset's.
  # The solver name (sname) is just a concatenation of such group names:
  if isinstance(pp.name, str): pp.name = [pp.name]
  sname = pp.name[0]
  for i in range(len(pp.name)):
    if i>0: sname = sname+pp.name[i]

  # Use a copy of the predicted cohset for the output cohset: 
  cohset = coh_copy (predicted, 'coh_solver('+str(pp.name)+')')
  cohset['name'] = 'solver_'+sname
  cohset['origin'] = 'WSRT_coh::coh_solver()'
  cohset['input'] = pp

  # Merge the parm/solver info from BOTH input cohsets:
  # (the measured side may also have solvable parameters)
  JEN_display(measured['solver'], txt='coh_solver(): measured[solver]')
  JEN_display(cohset['solver'], txt='cohset[solver]: before update')
  cohset['parm'].update(measured['parm'])
  cohset['solver'].update(measured['solver'])
  # cohset['plot']['color'].update(measured['plot']['color'])
  # cohset['plot']['style'].update(measured['plot']['style'])
  JEN_display(cohset['solver'], txt='cohset[solver]: after update')

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
  cohset['solver_solvable'] = solvable          # for display only

  # Make new objects with the relevant corrs only:
  cohset = coh_select_corrs (ns, cohset, corrs=corrs)
  sel_measured = coh_select_corrs (ns, measured, corrs=corrs)
  sel_predicted = coh_select_corrs (ns, predicted, corrs=corrs)
  
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
  dconc_condeq = coh_visualise (ns, cohset, scope='condeq',
                                errorbars=True, result='dconc')
  
  # Make the solver node:
  solver = ns.solver(sname, q=punit) << Meq.Solver(children=cc,
                                                   solvable=solvable,
                                                   num_iter=pp.num_iter,
                                                   debug_level=pp.debug_level)

  # Make a bookmark for the solver plot:
  JEN_bookmark (solver, name=('solver: '+sname),
                udi='cache/result', viewer='Result Plotter',
                page=0, save=1, clear=0, trace=0)

  # Finished:
  if pp.trace:
    JEN_display_subtree(solver, full=1)
    JEN_display(cohset,'cohset', 'after coh_solver()')

  JEN_forest_history ('coh_solver()')

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

def coh_visualise(ns, cohset, **pp):
  """visualises the 2x2 coherency matrices in cohset"""

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_visualise(ns, cohset, **pp)',
                      _help=dict(scope='identifying name of this visualiser',
                                 type='plot type (realvsimag or spectra)',
                                 errorbars='if True, plot stddev as crosses around mean',
                                 result='result of this routine (cohset or dcolls)'),
                      scope='uvdata', type='realvsimag', errorbars=0, result='cohset')) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

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
    dc = JEN_dcoll (ns, nodes[corr], scope=pp.scope, tag=corr,
                    type=pp.type,
                    errorbars=pp.errorbars,
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
    dc = JEN_dconc(ns, dcoll[key], scope=pp.scope, tag=key,
                   bookpage=key, trace=pp.trace)
    dconc[key] = dc
    sc.append (dc['dcoll'])

  JEN_forest_history ('coh_visualise()')
  
  # Return the specified result:
  if pp.result == 'cohset':
    # Make the dcoll nodes step-children of a MeqSelector
    # node that is inserted before one of the coherency nodes:
    key = cohset['coh'].keys()[0]
    cohset['coh'][key] = ns[visu_scope] << Meq.Selector(cohset['coh'][key],
                                                        stepchildren=sc)
    if pp.trace:
      JEN_display_NodeStub(cohset['coh'][key])
      JEN_display_subtree(cohset['coh'][key], 'inserted', full=1, recurse=3)
    return cohset

  else:
    # Return a dict of named dconc nodes that need requests:
    return dconc











#======================================================================================

def coh_visualise_old (ns, cohset, **pp):
  """visualises the 2x2 coherency matrices in cohset"""

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_visualise_old(ns, cohset, **pp)',
                      _help=dict(scope='identifying name of this visualiser',
                                 type='plot type (realvsimag or spectra)',
                                 errorbars='if T, plot stddev as crosses around mean',
                                 result='result of this routine (cohset or dcolls)'),
                      scope='uvdata', type='realvsimag', errorbars=0, result='cohset')) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Use a sub-scope where node-names are prepended with name
  # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
  visu_scope = 'visu_'+pp.scope
  
  # Make the visualisation chains per ifr/corr:
  corrs = cohset['corrs']
  mean = {}
  stddev = {}
  stripped = {}
  for corr in corrs:
    stripped[corr] = []
    mean[corr] = []
    stddev[corr] = []

  for key in cohset['coh'].keys():
    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]
    coh = cohset['coh'][key]
    for icorr in range(len(corrs)):
      corr = cohset['corrs'][icorr]
      nsub = ns.Subscope(visu_scope+'_'+corr, s1=s1, s2=s2)
      selected = nsub.selector(icorr) << Meq.Selector (coh, index=icorr)
      strp = nsub.stripper << Meq.Stripper (selected)
      stripped[corr].append(strp)
      if pp.type == 'realvsimag':
        mean[corr].append(nsub.mean << Meq.Mean (strp))
        if pp.errorbars:
          stddev[corr].append(nsub.stddev << Meq.StdDev (strp))
        

  # Make dcolls per corr:
  nsub = ns.Subscope(visu_scope)
  dcoll = {}
  attrib = {}
  dc_mean = {}
  dc_stddev = {}
  # Initialise the plot attribute record (changed below):
  attrib[corr] = record(plot=record(), tag=['dcoll',corr])

  if pp.type == 'spectra':
    for corr in corrs:
      attrib[corr]['plot'] = record(type=pp.type, title=visu_scope+':: '+corr,
                                    spectrum_color='hippo', x_axis='freq', y_axis='<y_axis>')
      attr = record(deepcopy(attrib[corr]))  
      dcoll[corr] = nsub.dcoll(corr) << Meq.DataCollect(children=stripped[corr],
                                                        top_label=hiid('visu'),
                                                        attrib=attr)

  else:
    # Assume pp.type == 'realvsimag'
    for corr in corrs:
      color = cohset['plot']['color'][corr]
      attrib[corr]['plot'] = record(type=pp.type, title=visu_scope+':: '+corr,
                                    color=color, symbol='circle', symbol_size=10,
                                    mean_circle=1, mean_circle_color=color, mean_circle_style='DashLine',
                                    stddev_circle=1, stddev_circle_color=color, stddev_circle_style='DotLine',
                                    mean_arrow=1)
      attr = record(deepcopy(attrib[corr]))  
      attr.tag.append('Mean')
      dc_mean[corr] = nsub.dcoll_mean(corr) << Meq.DataCollect(children=mean[corr],
                                                               top_label=hiid('visu'),
                                                               attrib=attr)
      if pp.errorbars:
        attr = record(deepcopy(attrib[corr]))  
        attr.tag.append('StdDev')
        dc_stddev[corr] = nsub.dcoll_stddev(corr) << Meq.DataCollect(children=stddev[corr],
                                                                     top_label=hiid('visu'),
                                                                     attrib=attr)
        attr = record(deepcopy(attrib[corr]))  
        attr.plot.value_tag = 'Mean'
        attr.plot.error_tag = 'StdDev'
        dcoll[corr] = nsub.dcoll(corr) << Meq.DataCollect(children=[dc_mean[corr],
                                                                    dc_stddev[corr]],
                                                          top_label=hiid('visu'),
                                                          attrib=attr)
      else:
        attr = record(deepcopy(attrib[corr]))  
        dcoll[corr] = nsub.dcoll(corr) << Meq.DataCollect(children=[dc_mean[corr]],
                                                          top_label=hiid('visu'),
                                                          attrib=attr)

      
  # Make concatenations (dconc) for groups of dcoll nodes:
  dconc = {}
  attrib['allcorrs'] = record(plot=record(), tag=['dcoll','allcorrs'])
  attrib['allcorrs'].plot.title = visu_scope+':: '+str(cohset['corrs'])
  cc = []
  for corr in dcoll.keys():
    cc.append(dcoll[corr])
  dconc['allcorrs'] = nsub.dconc_allcorrs << Meq.DataCollect(children=cc,
                                                             top_label=hiid('visu'),
                                                             attrib=attrib['allcorrs'])
  
  if (dcoll.has_key('XY') and dcoll.has_key('YX')):
    attrib['cross'] = record(plot=record(), tag=['dcoll','cross'])
    attrib['cross'].plot.title = visu_scope+':: '+' XY YX'
    dconc['cross'] = nsub.dconc_cross << Meq.DataCollect(children=[dcoll['XY'], dcoll['YX']],
                                                         top_label=hiid('visu'),
                                                         attrib=attrib['cross'])

  if (dcoll.has_key('XX') and dcoll.has_key('YY')):
    attrib['paral'] = record(plot=record(), tag=['dcoll','paral'])
    attrib['paral'].plot.title = visu_scope+':: '+' XX YY'
    dconc['paral'] = nsub.dconc_paral << Meq.DataCollect(children=[dcoll['XX'], dcoll['YY']],
                                                         top_label=hiid('visu'),
                                                         attrib=attrib['paral'])

  # Make bookmark pages from the dconc nodes:
  bms = []
  for key in dconc.keys():
    bm = JEN_bookmark (dconc[key], page=key, save=0)

  if pp.trace:
    print
    # JEN_display(attrib, 'attrib')
    # JEN_display_subtree(dconc['allcorrs'], full=1, recurse=7)
    # JEN_display_subtree(dconc['cross'], full=1, recurse=7)
    # JEN_display_subtree(dconc['paral'], full=1, recurse=7)
    

  # Return the specified result:
  if pp.result == 'cohset':
    # Make the dcoll nodes step-children of a MeqSelector
    # node that is inserted before one of the coherency nodes:
    sc = [dconc['allcorrs'].name, dconc['cross'].name, dconc['paral'].name]
    key = cohset['coh'].keys()[0]
    cohset['coh'][key] = ns[visu_scope] << Meq.Selector(children=[cohset['coh'][key]],
                                                        step_children=sc)
    return cohset
  else:
    # Return a dict of named dconc nodes that need requests:
    return dconc



#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  from WSRT_jones import *
  ns = NodeScope()
  nsim = ns.Subscope('_')
  stations = range(0,3)
  ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];

  if 0:
    # coh_spigots (trace=1)
    coh = coh_spigots (ns, ifrs=ifrs, trace=1)

  if 1:
    # coh = coh_predict (trace=1)
    source = 'unpol'
    # source = '3c147'
    # source = 'RMtest'
    corrupt = 0
    # corrupt = WSRT_GJones (ns, stations=stations, trace=1)
    cohset = coh_predict (ns, source=source, ifrs=ifrs, corrupt=corrupt, trace=1)
    # coh_visualise_old (ns, cohset, trace=1)
    coh_visualise (ns, cohset, trace=1)

    # cohset = coh_addnoise (ns, cohset, trace=1)
    # cohset = coh_insert_flagger (ns, cohset, scope='residual',
    #                              unop=['Real','Imag'], visu=True, trace=1)

    # coh_predict_sink (ns, coh, trace=1)

    # sel = coh_select_corrs (ns, cohset, corrs=['XX','YY'], trace=1)

  if 0:
    source = 'unpol'
    # source = '3c147'
    # source = 'RMtest'
    corrupt = WSRT_GJones (nsim, stations=stations, solvable=1, trace=1)
    measured = coh_predict (nsim, source=source, ifrs=ifrs, corrupt=corrupt, trace=1)
    coh_select_corrs (ns, measured, corrs=['XX','YY'], trace=1)

    # corrupt = WSRT_DJones (ns, stations=stations, trace=1)
    # predicted = coh_predict (ns, source=source, ifrs=ifrs, corrupt=corrupt, trace=1)
      
    # sname = 'DJones'
    # sname = ['DJones', 'GJones']
    # coh_solver (ns, name=sname, measured=measured, predicted=predicted, trace=1) 

  if 0:
    # sixpack = lsm_NEWSTAR_source (ns, name='QUV', trace=1)
    sixpack = 'unpol'
    print coh_circular (ns, sixpack, trace=1)
    print coh_linear (ns, sixpack, trace=1)

  if 0:
    JEN_display_NodeScope(ns, 'test')

  if 1:
    JEN_forest_history(show=True)

