# ../Timba/PyApps/test/WSRT_jones.py:  
#   Jones matrices for WSRT Central Point Source reduction


#=======================================================================================
# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
# Use: Settings.forest_state['field'] = ....

from numarray import *

from JEN_util_TDL import *
from JEN_util import *
# Better: put the JEN stuff in a sub-directory....
# from JEN.JEN_util_TDL import *
# from JEN.JEN_util import *


  
#=======================================================================================
# Initialise a standard 'jones_set' object, which contains information about
# a set of 2x2 jones matrices for all stations, for a single p-unit (source):
# This object (dict) is updated by, and passed between, various TDL functions 

def _init_joneset (name='<Jones>', origin='WSRT_jones:', input={},
                   stations=[0], punit='uvp',
                   jones={}, parm={}, solver={}, plot={},
                   trace=0):
  """initialise/check a standard _init_joneset object"""
  joneset = dict(name=name+'_'+punit, type='joneset', origin=origin,
                 stations=stations, punit=punit, input=input, 
                 jones=jones, parm=parm, solver=solver,
                 corrs={}, plot=plot)
  joneset['plot'].get('color',{})
  joneset['plot'].get('style',{})
  joneset['plot'].get('size',{})

  if joneset['input'].has_key('solvable'):
    if not joneset['input']['solvable']:
      joneset['parm'] = {}
      joneset['solver'] = {}
      
  if trace:
    JEN_display (joneset, 'joneset', joneset['name'])
  return joneset

# NB: There is something funny if I use jonest = record()
#     If jones is a dict, it is ignored (but parm is not!)
#     Perhaps record does not accept integer key names....?
#     NB: Only happens in my home TDL implementation (OMS)


#=======================================================================================


def WSRT_JJones (ns, jones=[], **pp):
  """makes a set of WSRT_JJones matrices by multiplying input jones matrices""";

  trace = pp.get('trace',0)
  jname = 'JJones'
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_JJones()');

  if len(jones) == 0:
    return JEN_history (joneset, error='no input jones matrices')
     
  # 
  for i in range(len(jones)):      
    # JEN_display (jones[i], jones[i]['name'])

    key = jones[i]['name']                               # e.g. 'GJones'
    joneset['input'][key] = jones[i]['input']

    if i == 0:                                           # first one
      joneset['parm'] = jones[i]['parm']
      joneset['solver'] = jones[i]['solver']
      # joneset['jseq'] = [jones[i]['jseq']]             # obsolete....?
      punit = jones[i]['punit']
      for key in jones[0]['jones'].keys():               # for all stations
        joneset['jones'][key] = [jones[i]['jones'][key]]

    elif jones[i]['punit'] != punit:                     # error
      err = 'different punits:'+punit+':'+str(jones[i]['punit'])
      return JEN_history (joneset, error=err)
            
    else:
      joneset['parm'].update(jones[i]['parm'])           # merge parms
      joneset['solver'].update(jones[i]['solver'])       # merge solvers
      # joneset['jseq'].append(jones[i]['jseq'])         # obsolete....?
      for key in jones[i]['jones'].keys():               # for all stations
        joneset['jones'][key].append(jones[i]['jones'][key]) # append to list


  # Multiply the accumulated (listed) jones matrices per station (key):
  for key in joneset['jones'].keys():
    jj = joneset['jones'][key]
    kwquals = jj[0].kwquals
    if len(jj) == 1:
      j0 = ns[jname](**kwquals) << Meq.Selector(*jj)
    else:
      j0 = ns[jname](**kwquals) << Meq.MatrixMultiply(*jj)
    joneset['jones'][key] = j0

  if trace:
    JEN_display (joneset, 'joneset', joneset['name'])
  return joneset
  


#=======================================================================================

def WSRT_GJones (ns=0, **pp):
  """defines diagonal WSRT_GJones matrices for complex(ampl,phase) parms""";

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_jones::WSRT_GJones(ns, **pp)',
                      _help=dict(stations='range of station names/numbers',
                                 punit='name of prediction-unit (source/patch)',
                                 solvable='if T, the parms are potentially solvable',
                                 ampl='default funklet value',
                                 phase='default funklet value',
                                 stddev_ampl='scatter in default  funklet c00 values',
                                 stddev_phase='scatter in default  funklet c00 values'),
                      stations=[0], punit='uvp', solvable=1,
                      ampl=1, phase=0,
                      stddev_ampl=0.1, stddev_phase=0.1)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Convert to funklet, if necessary:
  # DANGEROUS: if pp.ampl is funklet, is is modified in JEN_funklet()
  #            and something goes wrong in any case: TEST!
  # pp.ampl = JEN_funklet (pp.ampl)
  # pp.phase = JEN_funklet (pp.phase)

  jname = 'GJones'
  aname = 'ampl'
  pname = 'phase'

  # Create the various groups of parameters:
  parm = record(Xampl=[], Yampl=[], Xphase=[], Yphase=[])
  plot = record(color=record(Xampl='red', Yampl='blue', Xphase='magenta', Yphase='cyan'),
                style=record(Xampl='dot', Yampl='dot', Xphase='dot', Yphase='dot'))

  jones = {}
  ss = {}
  for station in pp.stations:
    ss['Xampl'] = (ns[aname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.ampl, stddev=pp.stddev_ampl),
                            node_groups=hiid('Parm')))
    ss['Yampl'] = (ns[aname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.ampl, stddev=pp.stddev_ampl),
                            node_groups=hiid('Parm')))
    ss['Xphase'] = (ns[pname]('X', s=station, q=pp.punit) <<
                    Meq.Parm(JEN_funklet(pp.phase, stddev=pp.stddev_phase),
                             node_groups=hiid('Parm')))
    ss['Yphase'] = (ns[pname]('Y', s=station, q=pp.punit) <<
                    Meq.Parm(JEN_funklet(pp.phase, stddev=pp.stddev_phase),
                             node_groups=hiid('Parm')))

    # The names of the MeqParm nodes are to be returned for a solver:
    [parm[key].append(ss[key].name) for key in ss.keys()]

    # Make the 2x2 Jones matrix
    stub = ns[jname](s=station, q=pp.punit) << Meq.Matrix22 (
      ns[jname]('11', s=station, q=pp.punit) << Meq.Polar( ss['Xampl'], ss['Xphase']),
      0,0,
      ns[jname]('22', s=station, q=pp.punit) << Meq.Polar( ss['Yampl'], ss['Yphase'])
      )
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  solver['GJones'] = record(solvable=parm.keys(), corrs=['XX','YY'], icorr=[0,3])
  # solver['GJones'] = record(solvable=parm.keys(), corrs=['XX','XY','YX','YY'], icorr=[0,1,2,3])
  solver['GX'] = record(solvable=['Xampl','Xphase'], corrs=['XX'], icorr=[0])
  solver['GY'] = record(solvable=['Yampl','Yphase'], corrs=['YY'], icorr=[3])
  solver['Gampl'] = record(solvable=['Xampl','Yampl'], corrs=['XX','YY'], icorr=[0,3])
  solver['Gphase'] = record(solvable=['Xphase','Yphase'], corrs=['XX','YY'], icorr=[0,3])

  # Create the (standard) joneset object:
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_GJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot,
                          trace=pp.trace);

  return joneset


#=======================================================================================

def WSRT_DJones (ns=0, **pp):
  """defines 2x2 WSRT_DJones matrices for complex(dang,dell) parms""";

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_jones::WSRT_DJones(ns, **pp)',
                      _help=dict(stations='range of station names/numbers',
                                 punit='name of prediction-unit (source/patch)',
                                 solvable='if T, the parms are potentially solvable',
                                 dang='default funklet value',
                                 dell='default funklet value',
                                 stddev_dang='scatter in default  funklet c00 values',
                                 stddev_dell='scatter in default  funklet c00 values'),
                      stations=[0], punit='uvp', solvable=1,
                      dang=0, dell=0,
                      stddev_dang=0.01, stddev_dell=0.01))
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Convert to funklet, if necessary:
  # pp.dang = JEN_funklet (pp.dang)
  # pp.dell = JEN_funklet (pp.dell)

  # Node names:
  jname = 'DJones'
  aname = 'dang'
  pname = 'dell'

  # Create the various groups of parameters:
  parm = record(Xdang=[], Ydang=[], Xdell=[], Ydell=[])
  plot = record()
  plot.color = record(Xdang='green', Ydang='black', Xdell='magenta', Ydell='yellow')
  plot.style = record(Xdang='dot', Ydang='dot', Xdell='dot', Ydell='dot')

  jones = {}
  ss = {}
  for station in pp.stations:
    ss['Xdang'] = (ns[aname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dang, stddev=pp.stddev_dang),
                            node_groups=hiid('Parm')))
    ss['Ydang'] = (ns[aname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dang, stddev=pp.stddev_dang),
                            node_groups=hiid('Parm')))
    ss['Xdell'] = (ns[pname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dell, stddev=pp.stddev_dell),
                            node_groups=hiid('Parm')))
    ss['Ydell'] = (ns[pname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dell, stddev=pp.stddev_dell),
                            node_groups=hiid('Parm')))

    # The names of the MeqParm nodes are to be returned for a solver:
    [parm[key].append(ss[key].name) for key in ss.keys()]

    # Make the 2x2 Jones matrix
    stub = ns[jname](s=station, q=pp.punit) << Meq.Matrix22 (
      ns[jname]('11', s=station, q=pp.punit) << Meq.Polar( ss['Xdang'], ss['Xdell']),
      0,0,
      ns[jname]('22', s=station, q=pp.punit) << Meq.Polar( ss['Ydang'], ss['Ydell'])
      )
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  solver['DJones'] = record(solvable=parm.keys(), corrs=['XY','YX'], icorr=[1,2])
  solver['Ddang'] = record(solvable=['Xdang','Ydang'], corrs=['XY','YX'], icorr=[1,2])
  solver['Ddell'] = record(solvable=['Xdell','Ydell'], corrs=['XY','YX'], icorr=[1,2])

  # Create the (standard) joneset object:
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_DJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot,
                          trace=pp.trace);
  return joneset

















#===============================================================================
# Test function:
#===============================================================================

if __name__ == '__main__':
  print 
  ns = NodeScope()
  nsim = ns.Subscope('_')

  if 0:
    pp = dict(a=1,b=2)
    pp = record(pp)
    print pp,pp.a,pp.b

    pp = dict(trace=1)
    pp = record(pp)
    print pp,pp.trace

    pp = dict()
    pp['x'] = pp.get('x',56)
    print pp
    pp = record(pp)
    pp.y = pp.get('y',6)
    print pp

  if 0:
    print '\n** ',ns.test('a','b') << Meq.Parm
    test_name = ns.test('a','b').name
    print '\n** ns.test.name = ',test_name
    print '\n** ns[',test_name,'] = ',ns[test_name]
    node = ns.test(s1='a', s2='b', q='3c48', p=34) 
    JEN_display_NodeStub(node)
    node2 = ns.test2(rr='rr', **node.kwquals)
    JEN_display_NodeStub(node2)

  if 1:
    stations = range(0,3)
    ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
    JJ = []
    JJ.append(WSRT_GJones (nsim, stations=stations, solvable=1, trace=1))
    # JJ.append(WSRT_DJones (nsim, stations=stations, solvable=0, trace=1))
    # WSRT_DJones (trace=1)
    # WSRT_GJones ()
    # Jones = JJ[0]
    # Jones = WSRT_JJones (nsim, JJ, trace=1)

  if 0:
    JEN_display_NodeScope(ns, 'test')

