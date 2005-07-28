# ../Timba/PyApps/test/WSRT_coh.py:  
#   Functions that deal with 2x2 coherency matrices


# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from numarray import *

from JEN_util_TDL import *
from JEN_util import *
# Better: put the JEN stuff in a sub-directory....
# from JEN.JEN_util_TDL import *
# from JEN.JEN_util import *




#======================================================================================

def JEN_visualise (ns, node=[], **pp):
  """visualises the 2x2 coherency matrices in cohset"""

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_coh.coh_visualize(ns, cohset, **pp)',
                      _help=dict(scope='identifying name of this visualizer',
                                 title='plot title',
                                 xlabel='x-axis label',
                                 ylabel='y-axis label',
                                 tag='plot tag',
                                 color='plot color',
                                 style='plot style',
                                 size='plot size',
                                 type='plot type (realvsimag or spectra)',
                                 errorbars='if T, plot stddev as crosses around mean',
                                 bookmark='name of dcoll bookmark (0=none)',
                                 bookpage='name of bookpage to be used (0=none)'),
                      scope='<scope>', type='realvsimag', errorbars=0,
                      tag='<tag>', title='<title>',
                      bookmark=0, bookpage=0,
                      xlabel='<xlabel>', ylabel='<ylabel>',
                      color='red', style='dot', size=10)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Use a sub-scope where node-names are prepended with name
  # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
  nsub = ns.Subscope(pp.scope)
  scopename = pp.scope+':: '

  # Make sure that the input is a list:
  if not isinstance(node, (list, tuple)): node = [node]

  # Make the visualisation chains per node:
  mean = []
  stddev = []
  for i in range(len(node)):
      stripped = (nsub.stripper(corr, s1=s1, s2=s2) << Meq.Stripper (node[i]))
      mean.append(nsub << Meq.Mean (stripped))
      if pp.errorbars:
        stddev.append(nsub << Meq.StdDev (stripped))
      if pp.trace:
        print stripped,len(mean),len(stddev)
        

  # Make dataCollection node(s):

  # Initialise the plot attribute record (changed below):
  attrib = record(plot=record(), tag=pp.tag)
  if pp.type == 'spectra':
    attrib['plot'] = record(type=pp.type, title=pp.title,
                            spectrum_color='hippo', x_axis=pp.xlabel, y_axis=pp.ylabel)
  else:
    attrib['plot'] = record(type=pp.type, title=pp.title,
                            color=pp.color, symbol='circle', symbol_size=pp.size,
                            mean_circle=1, mean_circle_color=pp.color, mean_circle_style='DashLine',
                            stddev_circle=1, stddev_circle_color=pp.color, stddev_circle_style='DotLine',
                            mean_arrow=1)
    
  attr = record(attrib.copy())  
  attr.tag.append('Mean')
  dc_mean = (nsub.dcoll_mean << Meq.DataCollect(children=mean,
                                                top_label=hiid('visu'),
                                                attrib=attr))
  if pp.errorbars:
    attr = record(attrib[corr].copy())  
    attr.tag.append('StdDev')
    dc_stddev = (nsub.dcoll_stddev << Meq.DataCollect(children=stddev,
                                                      top_label=hiid('visu'),
                                                      attrib=attr))
    attr = record(attrib[corr].copy())  
    attr.plot.value_tag = 'Mean'
    attr.plot.error_tag = 'StdDev'
    dcoll = (nsub.dcoll << Meq.DataCollect(children=[dc_mean, dc_stddev],
                                           top_label=hiid('visu'),
                                           attrib=attr))
  else:
    attr = record(attrib[corr].copy())  
    dcoll = (nsub.dcoll << Meq.DataCollect(children=[dc_mean],
                                           top_label=hiid('visu'),
                                           attrib=attr))

  # Make bookmark pages from the dconc nodes:
  if isinstance(pp.bookmark, str):
    bm = JEN_bookmark (dcoll, pp.bookmark, page=pp.bookpage, save=0)
      
  if pp.trace:
    print
    print dc_mean,dc_stddev,dcoll
    print attrib

  return dcoll



#=========================================================================================

def JEN_dconc(dcoll=[], trace=0):


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
    bms.append(bm)
  # if pp.scope=='rawdata': JEN_bookpage(bm, 'allcorrs')

  if pp.trace:
    print
    # JEN_display(attrib, 'attrib')
    # JEN_display_subtree(dconc['allcorrs'], full=1, recurse=7)
    # JEN_display_subtree(dconc['cross'], full=1, recurse=7)
    # JEN_display_subtree(dconc['paral'], full=1, recurse=7)
    
    
  # Finally, make the dcoll nodes step-children of a MeqSelector
  # node that is inserted before one of the coherency nodes:
  key = cohset['coh'].keys()[0]
  # if pp.trace: JEN_display_subtree(cohset['coh'][key], full=1, recurse=3)
  sc = [dconc['allcorrs'].name, dconc['cross'].name, dconc['paral'].name]
  cohset['coh'][key] = nsub.dconc('(branch)') << Meq.Selector(children=[cohset['coh'][key]],
                                                              step_children=sc)
  # if pp.trace: JEN_display_subtree(cohset['coh'][key], full=1, recurse=1000)

  return cohset


#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  from WSRT_jones import *

  if 0:
    JEN_display_NodeScope(ns, 'test')

