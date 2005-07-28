# ../Timba/PyApps/test/WSRT_coh.py:  
#   Functions that deal with 2x2 coherency matrices


# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
from copy import deepcopy

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
    JEN_display (cohset, 'cohset', cohset['name'])
  return cohset


#======================================================================================
# Make a copy of the cohset with a subset of the 

def coh_select (cohset, corrs=0, icorr=0, trace=1): 
  cohout = cohset.copy()
  # cohout = deepcopy(cohset)


  if trace:
    JEN_display (cohout, 'cohout', cohout['name'])
    
  return cohout

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

  # Corrupt with the given jones matrices:
  if not isinstance(corrupt, int):
    cohset = coh_corrupt (ns, cohset, joneset=corrupt, trace=pp.trace)

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
  return sink


#======================================================================================


def coh_corrupt (ns, cohset, joneset, trace=0):
  """corrupts a list of 2x2 coherency matrices with the corresponding 2x2 jones matrices""" 
  cohout = cohset.copy()
  # cohout = deepcopy(cohset)

  bname = 'corrupted'
  for key in cohset['coh'].keys():
    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]
    coh = ns[bname](s1=s1, s2=s2) << Meq.MatrixMultiply(
      joneset['jones'][s1],
      cohset['coh'][key],
      (ns << Meq.ConjTranspose(joneset['jones'][s2]))
      )
    cohout['coh'][key] = coh

  # Transfer the parm/solver info fron joneset to cohset:
  cohout['parm'].update(joneset['parm'])
  cohout['solver'].update(joneset['solver'])

  if trace:
    JEN_display_subtree(coh, full=1)
    JEN_display(cohout,'cohout', 'after coh_corrupt()')
  return cohout


#======================================================================================

def coh_correct (ns, cohset, joneset, trace=0):
  """corrects a list of 2x2 coherency matrices with the corresponding 2x2 jones matrices""" 
  # cohout = cohset.copy()
  cohout = deepcopy(cohset)

  bname = 'corrected'
  for key in cohset['coh'].keys():
    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1] 
    coh = ns[bname](s1=s1,s2=s2) << Meq.MatrixMultiply(
      Meq.MatrixInvert22(joneset['jones'][s1]),
      cohset['coh'][key],
      (ns << Meq.MatrixInvert22(ns << Meq.ConjTranspose(joneset['jones'][s2])))
      )
    cohout['coh'][key] = coh

  # Transfer the parm/solver info fron joneset to cohset:
  cohout['parm'].update(joneset['parm'])
  cohout['solver'].update(joneset['solver'])

  if trace:
    JEN_display_subtree(coh, full=1)
    JEN_display(cohout,'cohout', 'after coh_correct()')
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

  # Use a copy of the predicted cohset for the output cohset: 
  cohset = predicted.copy()
  # cohset = deepcopy(predicted)
  cohset['name'] = 'solver_'+pp.name
  cohset['origin'] = 'WSRT_coh::coh_solver()'
  cohset['input'] = pp

  # Merge the parm/solver info from BOTH input cohsets:
  # (the measured side may also have solvable parameters)
  cohset['parm'].update(measured['parm'])
  cohset['solver'].update(measured['solver'])

  # Collect the solvable parms for the named solver(s):
  if not cohset['solver'].has_key(pp.name):
    print '\n** solver name not recognised:',pp.name
    print '     choose from:',cohset['solver'].keys()
    print
    return
  ss = cohset['solver'][pp.name]
  corrs = ss['corrs']
  icorr = ss['icorr']
  solvable = []
  for key in ss['solvable']:
    solvable.extend(cohset['parm'][key])
  
  # Make condeq nodes
  cc = []
  punit = predicted['punit']
  for key in cohset['coh'].keys():
    if not measured['coh'].has_key(key):
      print '\n** key not recognised:',key
      return

    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]

    meas = measured['coh'][key]
    pred = predicted['coh'][key]
    # if len(icorr) < 4:
    if 0:
      multi = (len(icorr)>1)
      meas = (ns << Meq.Selector(meas, index=icorr, multi=multi))
      pred = (ns << Meq.Selector(pred, index=icorr, multi=multi))

    condeq = ns.condeq(s1=s1,s2=s2,q=punit) << Meq.Condeq(meas, pred)
    cohset['coh'][key] = condeq
    cc.append(condeq)

  # Visualize the condeqs:
  dconc_condeq = coh_visualize (ns, cohset, scope='condeq', result='dconc')
  
  # Make the solver node:
  solver = ns.solver(pp.name, q=punit) << Meq.Solver(children=cc,
                                                     solvable=solvable,
                                                     num_iter=pp.num_iter,
                                                     debug_level=pp.debug_level)

  # Make a bookmark for the solver plot:
  JEN_bookmark (solver, name=('solver: '+pp.name),
                udi='cache/result', viewer='Result Plotter',
                page=0, save=1, clear=0, trace=0)

  # Finished:
  if pp.trace:
    JEN_display_subtree(solver, full=1)
    JEN_display(cohset,'cohset', 'after coh_solver()')

  # Return the specified result:
  if pp.result == 'cohset':
    key = measured['coh'].keys()[0]
    cc = [solver,  dconc_condeq['allcorrs'], measured['coh'][key]]      # coh should be LAST!
    sname = 'solver_'+pp.name
    measured['coh'][key] = ns.reqseq(sname, q=punit) << Meq.ReqSeq(children=cc,
                                                                   result_index=len(cc)-1)
    return cohset
  else:
    # Return the reqseq that needs requests:
    reqseq = ns.reqseq(pp.name, q=punit) << Meq.ReqSeq(solver,
                                                       result_index=0)
    return reqseq
    


#======================================================================================

def coh_visualize (ns, cohset, **pp):
  """visualises the 2x2 coherency matrices in cohset"""

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh::coh_visualize(ns, cohset, **pp)',
                      _help=dict(scope='identifying name of this visualizer',
                                 type='plot type (realvsimag or spectra)',
                                 errorbars='if T, plot stddev as crosses around mean',
                                 result='result of this routine (cohset or dcolls)'),
                      scope='uvdata', type='realvsimag', errorbars=0, result='cohset')) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Use a sub-scope where node-names are prepended with name
  # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
  nsub = ns.Subscope(pp.scope)
  scopename = pp.scope+':: '

  # Make the visualisation chains per corr:
  mean = {}
  stddev = {}
  for icorr in range(4):
    corr = cohset['corrs'][icorr]
    mean[corr] = []
    stddev[corr] = []

  for key in cohset['coh'].keys():
    s12 = cohset['stations'][key]
    s1 = s12[0]
    s2 = s12[1]
    coh = cohset['coh'][key]
    for icorr in range(4):
      corr = cohset['corrs'][icorr]
      selected = (nsub.selector(corr, s1=s1, s2=s2) << Meq.Selector (coh, index=icorr))
      stripped = (nsub.stripper(corr, s1=s1, s2=s2) << Meq.Stripper (selected))
      mean[corr].append(nsub.mean(corr, s1=s1, s2=s2) << Meq.Mean (stripped))
      if pp.errorbars:
        stddev[corr].append(nsub.stddev(corr, s1=s1, s2=s2) << Meq.StdDev (stripped))
      if pp.trace:
        print icorr,corr,selected,stripped,len(mean[corr]),len(stddev[corr])
        

  # Make dcolls per corr:
  dcoll = {}
  attrib = {}
  dc_mean = {}
  dc_stddev = {}
  for icorr in range(4):
    corr = cohset['corrs'][icorr]

    # Initialise the plot attribute record (changed below):
    attrib[corr] = record(plot=record(), tag=['dcoll',corr])
    if pp.type == 'spectra':
      attrib[corr]['plot'] = record(type=pp.type, title=scopename+corr,
                                    spectrum_color='hippo', x_axis='freq', y_axis='<y_axis>')
    else:
      color = cohset['plot']['color'][corr]
      attrib[corr]['plot'] = record(type=pp.type, title=scopename+corr,
                                    color=color, symbol='circle', symbol_size=10,
                                    mean_circle=1, mean_circle_color=color, mean_circle_style='DashLine',
                                    stddev_circle=1, stddev_circle_color=color, stddev_circle_style='DotLine',
                                    mean_arrow=1)

    attr = record(deepcopy(attrib[corr]))  
    attr.tag.append('Mean')
    dc_mean[corr] = (nsub.dcoll_mean(corr) << Meq.DataCollect(children=mean[corr],
                                                              top_label=hiid('visu'),
                                                              attrib=attr))
    if pp.errorbars:
      attr = record(deepcopy(attrib[corr]))  
      attr.tag.append('StdDev')
      dc_stddev[corr] = (nsub.dcoll_stddev(corr) << Meq.DataCollect(children=stddev[corr],
                                                                    top_label=hiid('visu'),
                                                                    attrib=attr))
      attr = record(deepcopy(attrib[corr]))  
      attr.plot.value_tag = 'Mean'
      attr.plot.error_tag = 'StdDev'
      dcoll[corr] = (nsub.dcoll(corr) << Meq.DataCollect(children=[dc_mean[corr],
                                                                   dc_stddev[corr]],
                                                         top_label=hiid('visu'),
                                                         attrib=attr))
    else:
      attr = record(deepcopy(attrib[corr]))  
      dcoll[corr] = (nsub.dcoll(corr) << Meq.DataCollect(children=[dc_mean[corr]],
                                                         top_label=hiid('visu'),
                                                         attrib=attr))

      
    if pp.trace:
      print
      print icorr,corr,dc_mean,dc_stddev,dcoll[corr]
      print attrib[corr]


  # Make concatenations (dconc) for groups of dcoll nodes:
  dconc = {}
  attrib['allcorrs'] = record(plot=record(), tag=['dcoll','allcorrs'])
  attrib['allcorrs'].plot.title = scopename+str(cohset['corrs'])
  cc = [dcoll['XX'], dcoll['XY'], dcoll['YX'], dcoll['YY']]
  dconc['allcorrs'] = (nsub.dconc_allcorrs << Meq.DataCollect(children=cc,
                                                              top_label=hiid('visu'),
                                                              attrib=attrib['allcorrs']))
  
  attrib['cross'] = record(plot=record(), tag=['dcoll','cross'])
  attrib['cross'].plot.title = scopename+str(cohset['corrs'][1:2])
  dconc['cross'] = (nsub.dconc_cross << Meq.DataCollect(children=[dcoll['XY'], dcoll['YX']],
                                                        top_label=hiid('visu'),
                                                        attrib=attrib['cross']))

  attrib['paral'] = record(plot=record(), tag=['dcoll','paral'])
  attrib['paral'].plot.title = scopename+str([cohset['corrs'][0], cohset['corrs'][3]])
  dconc['paral'] = (nsub.dconc_paral << Meq.DataCollect(children=[dcoll['XX'], dcoll['YY']],
                                                        top_label=hiid('visu'),
                                                        attrib=attrib['paral']))

  # Make bookmark pages from the dconc nodes:
  bms = []
  for key in dconc.keys():
    bm = JEN_bookmark (dconc[key], page=key, save=0)
    # bms.append(bm)

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
    cohset['coh'][key] = nsub.dconc('(branch)') << Meq.Selector(children=[cohset['coh'][key]],
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

  if 0:
    # coh = coh_predict (trace=1)
    source = 'unpol'
    source = '3c147'
    source = 'RMtest'
    corrupt = 0
    corrupt = WSRT_GJones (ns, stations=stations, trace=1)
    cohset = coh_predict (ns, source=source, ifrs=ifrs, corrupt=corrupt, trace=1)
    # coh_visualize (ns, cohset, trace=1)
    # coh_predict_sink (ns, coh, trace=1)

  if 1:
    source = 'unpol'
    # source = '3c147'
    # source = 'RMtest'
    corrupt = WSRT_GJones (nsim, stations=stations, solvable=0, trace=1)
    measured = coh_predict (nsim, source=source, ifrs=ifrs, corrupt=corrupt, trace=1)

    corrupt = WSRT_DJones (ns, stations=stations, trace=1)
    predicted = coh_predict (ns, source=source, ifrs=ifrs, corrupt=corrupt, trace=1)

    coh_solver (ns, name='DJones', measured=measured, predicted=predicted, trace=1) 

  if 0:
    # sixpack = lsm_NEWSTAR_source (ns, name='QUV', trace=1)
    sixpack = 'unpol'
    print coh_circular (ns, sixpack, trace=1)
    print coh_linear (ns, sixpack, trace=1)

  if 0:
    JEN_display_NodeScope(ns, 'test')

