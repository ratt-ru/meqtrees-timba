# ../WH/contrib/JEN/JEN_visualise.py:  
#   Functions that deal with visualisation subtrees

print '\n',100*'*'
print '** JEN_TDL_visualise.py    h09/d15aug2005'

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
from copy import deepcopy

from JEN_forest_state import *

from JEN_util_TDL import *
from JEN_util import *
# Better: put the JEN stuff in a sub-directory....
# from JEN.JEN_util_TDL import *
# from JEN.JEN_util import *




#======================================================================================

def JEN_dcoll (ns, node=[], **pp):
  """visualises the given node(s) and return a dcoll dict"""

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'JEN_TDL_visualise::JEN_dcoll(ns, node, **pp)',
                      _help=dict(scope='scope (e.g. rawdata)',
                                 tag='plot tag (e.g. allcorrs)',
                                 title='plot title',
                                 insert='if node given, insert dconc node',
                                 xlabel='x-axis label',
                                 ylabel='y-axis label',
                                 color='plot color',
                                 style='plot style',
                                 size='plot size',
                                 type='plot type (realvsimag or spectra)',
                                 errorbars='if T, plot stddev as crosses around mean',
                                 bookmark='name of dcoll bookmark (False=none)',
                                 bookpage='name of bookpage to be used (False=none)'),
                      scope='<scope>', tag='<tag>',
                      title=False, insert=False,
                      type='realvsimag', errorbars=False,
                      bookmark=False, bookpage=False,
                      xlabel='<xlabel>', ylabel='<ylabel>',
                      color='red', style='dot', size=10)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Initialise the output dict:
  dcoll = dict(stripped=[], mean=[], stddev=[], input=pp, attrib=None,
               dcoll_mean=None, dcoll_stddev=None, dcoll=None)

  # Make sure that the input is a list:
  if not isinstance(node, (list, tuple)): node = [node]

  # Make the visualisation chains per node:
  for i in range(len(node)):
    stripped = ns << Meq.Stripper (node[i])
    dcoll['stripped'].append (stripped)
    if pp.type == 'realvsimag':
      dcoll['mean'].append (ns << Meq.Mean(stripped))
      if pp.errorbars:
        dcoll['stddev'].append (ns << Meq.StdDev(stripped))
        

  # Make dataCollection node(s):
  # Initialise the plot attribute record (changed below):
  scope_tag = 'dcoll_'+str(pp.scope)+'_'+str(pp.tag)
  if not isinstance(pp.title, str): pp.title = scope_tag
  attrib = record(plot=record(), tag=pp.tag)
  if pp.type == 'spectra':
    attrib['plot'] = record(type=pp.type, title=pp.title,
                            spectrum_color='hippo',
                            x_axis=pp.xlabel, y_axis=pp.ylabel)
    dcoll['dcoll'] = ns[scope_tag] << Meq.DataCollect(children=dcoll['stripped'],
                                                      top_label=hiid('visu'),
                                                      attrib=attrib)

  else:
    # Assume pp.type == 'realvsimag'
    attrib['plot'] = record(type=pp.type, title=pp.title,
                            color=pp.color, symbol='circle', symbol_size=pp.size,
                            mean_circle=1, mean_circle_color=pp.color,
                            mean_circle_style='DashLine', mean_arrow=1)
    
    
    if not pp.errorbars:
      # Indicate just the mean values of the child results:
      dcoll['dcoll'] = ns[scope_tag] << Meq.DataCollect(children=dcoll['mean'],
                                                        top_label=hiid('visu'),
                                                        attrib=attrib)
    else:
      # Indicate the stddev of the child results with 'error bars':

      # Make a separate dcoll for the means:
      attr = deepcopy(attrib)
      if not isinstance(attr.tag, list): attr.tag = [attr.tag]
      attr.tag.append('Mean')
      dc_mean = ns[scope_tag+'_mean'] << Meq.DataCollect(children=dcoll['mean'],
                                                         top_label=hiid('visu'),
                                                         attrib=attr)
      dcoll['dcoll_mean'] = dc_mean
      
      # Make a separate dcoll for the stddevs:
      attr = deepcopy(attrib)
      if not isinstance(attr.tag, list): attr.tag = [attr.tag]
      attr.tag.append('StdDev')
      dc_stddev = ns[scope_tag+'_stddev'] << Meq.DataCollect(children=dcoll['stddev'],
                                                             top_label=hiid('visu'),
                                                             attrib=attr)
      dcoll['dcoll_stddev'] = dc_stddev
      
      # Combine the mean and stddev dcolls:
      attr = deepcopy(attrib)
      attr.plot.stddev_circle=1
      attr.plot.stddev_circle_color=pp.color
      attr.plot.stddev_circle_style='DotLine'
      attr.plot.value_tag = 'Mean'
      attr.plot.error_tag = 'StdDev'
      dcoll['dcoll'] = ns[scope_tag] << Meq.DataCollect(children=[dc_mean, dc_stddev],
                                                        top_label=hiid('visu'),
                                                        attrib=attr)

  # Attach the attribute record to the output record, for later use:
  dcoll['attrib'] = attrib
  dcoll['tag'] = dcoll['attrib']['tag']            # used by JEN_dconc() below

  # Optionally, make a bookmark for the dconc node:
  if isinstance(pp.bookpage, str):
    bm = JEN_bookmark (dconc['dcoll'], page=pp.bookpage)
  elif isinstance(pp.bookmark, str):
    bm = JEN_bookmark (dconc['dcoll'], pp.bookmark)

  # Progress message:
  if pp.trace:
    JEN_display_subtree (dcoll['dcoll'], 'dcoll', full=1)
    JEN_display(dcoll, 'dcoll', 'after JEN_dcoll()')

  # If an insert-node is specified, make the dconc node a step-child of a
  # MeqSelector node just before it, to issue requests:
  if not isinstance(pp.insert, bool):
    output = ns[scope_tag+'_branch'] << Meq.Selector(insert, step_children=dcoll['dcoll'])
    return output

  return dcoll



#=========================================================================================
# Concatenate the given dcolls (dicts, see above) into a dconc node
#=========================================================================================

def JEN_dconc (ns, dcoll, **pp):

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'JEN_TDL_visualise::JEN_dconc(ns, dcoll, **pp)',
                      _help=dict(scope='scope (e.g. rawdata)',
                                 tag='plot tag (e.g. allcorrs)',
                                 title='<dconc title>',
                                 xlabel='x-axis label',
                                 ylabel='y-axis label',
                                 insert='if node given, insert dconc node',
                                 bookmark='name of dcoll bookmark (False=none)',
                                 bookpage='name of bookpage to be used (False=none)'),
                      scope='<scope>', tag='<tag>',
                      title=False, insert=False,
                      bookmark=False, bookpage=False,
                      xlabel='<xlabel>', ylabel='<ylabel>'))
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Initialise the output dict:
  dconc = dict(input=pp, cc=[], attrib=None, dcoll=None)

  scope_tag = 'dconc_'+str(pp.scope)+'_'+str(pp.tag)
  if not isinstance(pp.title, str): pp.title = scope_tag

  attrib = record(plot=record(), tag=['dconc'])
  attrib.plot.title = pp.title

  # Collect the dcoll nodes in a list (cc):
  if not isinstance(dcoll, (list, tuple)): dcoll = [dcoll]
  for i in range(len(dcoll)):
    dconc['cc'].append(dcoll[i]['dcoll'])     # 
    attrib['tag'].append(dcoll[i]['tag'])     # concatenate the dcoll tags (unique?)
    
  # Make concatenations (dconc) node:
  dconc['dcoll'] = (ns[scope_tag] << Meq.DataCollect(children=dconc['cc'],
                                                     top_label=hiid('visu'),
                                                     attrib=attrib))

  # Optionally, make a bookmark for the dconc node:
  if isinstance(pp.bookpage, str):
    bm = JEN_bookmark (dconc['dcoll'], page=pp.bookpage)
  elif isinstance(pp.bookmark, str):
    bm = JEN_bookmark (dconc['dcoll'], pp.bookmark)


  # Progress message:
  if pp.trace:
    JEN_display_subtree (dconc['dcoll'], 'dconc', full=1)
    JEN_display(dcoll, 'dconc', 'after JEN_dconc('+scope_tag,')')
    
  # If an insert-node is specified, make the dconc node a step-child of a
  # MeqSelector node just before it, to issue requests:
  if not isinstance(pp.insert, bool):
    output = ns[scope_tag+'_branch'] << Meq.Selector(insert, step_children=dconc['dcoll'])
    return output

  return dconc


#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  ns = NodeScope()

  if 1:
    cc = []
    cc.append(ns.xxx(s1=0, s2=1) << -1)
    cc.append(ns.xxx(s1=0, s2=2) << -2)
    cc.append(ns.xxx(s1=1, s2=2) << -3)
    nsub = ns.Subscope('sub')
    JEN_dcoll (nsub, cc, errorbars=1, trace=1) 
    # JEN_dcoll (nsub, cc, type='spectra', errorbars=1, trace=1) 

  if 0:
    JEN_display_NodeScope(ns, 'test')

