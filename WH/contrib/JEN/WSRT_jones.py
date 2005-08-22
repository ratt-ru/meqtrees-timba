# ../Timba/WH/contrib/JEN/WSRT_jones.py:  
#   Jones matrices for WSRT Central Point Source reduction

print '\n',100*'*'
print '** WSRT_jones.py    h30jul/h08aug2005'

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

def WSRT_display_jones_subtree (joneset, full=1, trace=1):
  keys = joneset['jones'].keys()
  jones = joneset['jones'][keys[0]]
  txt = 'jones[0/'+str(len(keys))+'] of joneset: '+joneset['name']
  JEN_display_subtree(jones, txt, full=full)

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
      joneset['plot']['color'] = jones[i]['plot']['color']
      joneset['plot']['style'] = jones[i]['plot']['style']
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
      joneset['plot']['color'].update(jones[i]['plot']['color'])
      joneset['plot']['style'].update(jones[i]['plot']['style'])
      # joneset['jseq'].append(jones[i]['jseq'])         # obsolete....?
      for key in jones[i]['jones'].keys():               # for all stations
        joneset['jones'][key].append(jones[i]['jones'][key]) # append to list


  # Multiply the accumulated (listed) jones matrices per station (key):
  for key in joneset['jones'].keys():
    jj = joneset['jones'][key]
    kwquals = jj[0].kwquals
    quals = list(jj[0].quals)
    if len(jj) == 1:
      print '-',key,'  kwquals=',kwquals,'  quals=',quals
      j0 = ns[jname](**kwquals)(*quals) << Meq.Selector(*jj)
    else:
      for i in range(1,len(jj)):
        kwquals.update(jj[i].kwquals)
        quals.extend(list(jj[i].quals))
      print '-',key,'  kwquals=',kwquals,'  quals=',quals
      j0 = ns[jname](**kwquals)(*quals) << Meq.MatrixMultiply(*jj)
    joneset['jones'][key] = j0

  if trace:
    JEN_display (joneset, 'joneset', joneset['name'])

  JEN_forest_history ('WSRT_JJones()', level=2)
  return joneset
  


#=======================================================================================
# GJones: diagonal 2x2 matrix for complex gains per polarization
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
                                 polar='if True, use MeqPolar, otherwise MeqToComplex',
                                 stddev_ampl='scatter in default  funklet c00 values',
                                 stddev_phase='scatter in default  funklet c00 values'),
                      stations=[0], punit='uvp', solvable=1,
                      ampl=1, phase=0, polar=False,
                      stddev_ampl=0, stddev_phase=0)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  jname = 'GJones'
  aname = 'ampl'
  pname = 'phase'
  node_groups = ['Parm','G']

  # Create the various groups of parameters:
  parm = record(Xampl=[], Yampl=[], Xphase=[], Yphase=[])
  plot = record(color=record(Xampl='red', Yampl='blue', Xphase='magenta', Yphase='cyan'),
                style=record(Xampl='dot', Yampl='dot', Xphase='dot', Yphase='dot'))

  jones = {}
  ss = {}
  for station in pp.stations:
    ss['Xampl'] = (ns[aname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.ampl, stddev=pp.stddev_ampl),
                            node_groups=node_groups))
    ss['Yampl'] = (ns[aname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.ampl, stddev=pp.stddev_ampl),
                            node_groups=node_groups))
    ss['Xphase'] = (ns[pname]('X', s=station, q=pp.punit) <<
                    Meq.Parm(JEN_funklet(pp.phase, stddev=pp.stddev_phase),
                             node_groups=node_groups))
    ss['Yphase'] = (ns[pname]('Y', s=station, q=pp.punit) <<
                    Meq.Parm(JEN_funklet(pp.phase, stddev=pp.stddev_phase),
                             node_groups=node_groups))

    # The names of the MeqParm nodes are to be returned for a solver:
    [parm[key].append(ss[key].name) for key in ss.keys()]

    # Make the 2x2 Jones matrix
    if pp.polar:
      stub = ns[jname](s=station, q=pp.punit) << Meq.Matrix22 (
        ns[jname]('11', s=station, q=pp.punit) << Meq.Polar( ss['Xampl'], ss['Xphase']),
        0,0,
        ns[jname]('22', s=station, q=pp.punit) << Meq.Polar( ss['Yampl'], ss['Yphase'])
        )

    else:
      Xcos = ns.Xcos('X', s=station, q=pp.punit) << Meq.Cos(ss['Xphase']) * ss['Xampl']
      Ycos = ns.Ycos('Y', s=station, q=pp.punit) << Meq.Cos(ss['Yphase']) * ss['Yampl']
      Xsin = ns.Xsin('X', s=station, q=pp.punit) << Meq.Sin(ss['Xphase']) * ss['Xampl']
      Ysin = ns.Ysin('Y', s=station, q=pp.punit) << Meq.Sin(ss['Yphase']) * ss['Yampl']
      stub = ns[jname](s=station, q=pp.punit) << Meq.Matrix22 (
        ns[jname]('11', s=station, q=pp.punit) << Meq.ToComplex( Xcos, Xsin),
        0,0,
        ns[jname]('22', s=station, q=pp.punit) << Meq.ToComplex( Ycos, Ysin)
        )
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  paral = ['XX','YY']
  solver['GJones'] = record(solvable=['Xampl','Xphase','Yampl','Yphase'], corrs=paral)
  solver['GX'] = record(solvable=['Xampl','Xphase'], corrs=['XX'])
  solver['GY'] = record(solvable=['Yampl','Yphase'], corrs=['YY'])
  solver['Gampl'] = record(solvable=['Xampl','Yampl'], corrs=paral)
  solver['Gphase'] = record(solvable=['Xphase','Yphase'], corrs=paral)

  # Create the (standard) joneset object:
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_GJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot,
                          trace=pp.trace);

  JEN_forest_history ('WSRT_GJones()', level=2)
  return joneset



#=======================================================================================
# BJones: diagonal 2x2 matrix for complex bandpass per polarization
#=======================================================================================

def WSRT_BJones (ns=0, **pp):
  """defines diagonal WSRT_BJones bandpass matrices""";

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_jones::WSRT_BJones(ns, **pp)',
                      _help=dict(stations='range of station names/numbers',
                                 punit='name of prediction-unit (source/patch)',
                                 real='default funklet value',
                                 imag='default funklet value',
                                 stddev_real='scatter in default  funklet c00 values',
                                 stddev_imag='scatter in default  funklet c00 values',
                                 solvable='if T, the parms are potentially solvable'),
                      stations=[0], punit='uvp', solvable=1,
                      real=1, imag=0,
                      stddev_real=0, stddev_imag=0)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  jname = 'BJones'
  aname = 'Breal'
  pname = 'Bimag'
  node_groups = ['Parm','B']

  # Create the various groups of parameters:
  parm = record(Xreal=[], Yreal=[], Ximag=[], Yimag=[])
  plot = record(color=record(Xreal='red', Yreal='blue', Ximag='magenta', Yimag='cyan'),
                style=record(Xreal='dot', Yreal='dot', Ximag='dot', Yimag='dot'))

  jones = {}
  ss = {}
  for station in pp.stations:
    ss['Xreal'] = (ns[aname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.real, stddev=pp.stddev_real),
                            node_groups=node_groups))              
    ss['Yreal'] = (ns[aname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.real, stddev=pp.stddev_real),
                            node_groups=node_groups))              
    ss['Ximag'] = (ns[pname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.imag, stddev=pp.stddev_imag),
                            node_groups=node_groups))              
    ss['Yimag'] = (ns[pname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.imag, stddev=pp.stddev_imag),
                            node_groups=node_groups))              
    
    # The names of the MeqParm nodes are to be returned for a solver:
    [parm[key].append(ss[key].name) for key in ss.keys()]

    # Make the 2x2 Jones matrix
    stub = ns[jname](s=station, q=pp.punit) << Meq.Matrix22 (
      ns[jname]('11', s=station, q=pp.punit) << Meq.ToComplex( ss['Xreal'], ss['Ximag']),
      0,0,
      ns[jname]('22', s=station, q=pp.punit) << Meq.ToComplex( ss['Yreal'], ss['Yimag'])
      )
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  paral = ['XX','YY']
  solver['BJones'] = record(solvable=['Xreal','Ximag','Yreal','Yimag'], corrs=paral)
  solver['BX'] = record(solvable=['Xreal','Ximag'], corrs=['XX'])
  solver['BY'] = record(solvable=['Yreal','Yimag'], corrs=['YY'])
  solver['Breal'] = record(solvable=['Xreal','Yreal'], corrs=paral)
  solver['Bimag'] = record(solvable=['Ximag','Yimag'], corrs=paral)

  # Create the (standard) joneset object:
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_BJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot,
                          trace=pp.trace);

  JEN_forest_history ('WSRT_BJones()', level=2)
  return joneset


#=======================================================================================
# FJones: 2x2 matrix for ionospheric Faraday rotation (NOT ion.phase!)
#=======================================================================================

def WSRT_FJones (ns=0, **pp):
  """defines diagonal WSRT_FJones Faraday rotation matrices""";

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_jones::WSRT_FJones(ns, **pp)',
                      _help=dict(stations='range of station names/numbers',
                                 punit='name of prediction-unit (source/patch)',
                                 RM='default funklet value',
                                 solvable='if T, the parms are potentially solvable'),
                      stations=[0], punit='uvp', RM=0, 
                      solvable=1)) 
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  jname = 'FJones'
  node_groups = ['Parm','F']

  # Create the various groups of parameters:
  parm = record(RM=[])
  plot = record(color=record(RM='red'),
                style=record(RM='dot'))

  # Make the lambda-squared node for RM -> farot conversion: 
  wvl2 = JEN_wavelength (ns, unop='Sqr', trace=0)

  RM = (ns.RM(q=pp.punit) << Meq.Parm(JEN_funklet(pp.RM),
                                      node_groups=node_groups))
  parm['RM'] = [RM.name]
  farot = (ns.farot(q=pp.punit) << (RM * wvl2))

  matname = 'FJones_rotation_matrix' 
  stub = JEN_rotation_matrix (ns, angle=farot, name=matname, trace=0)

  jones = {}
  for station in pp.stations:
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  cross = ['XY','YX']
  solver['FJones'] = record(solvable=['RM'], corrs=cross)

  # Create the (standard) joneset object:
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_FJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot,
                          trace=pp.trace);

  JEN_forest_history ('WSRT_FJones()', level=2)
  return joneset



#=======================================================================================
# DJones: 2x2 matrix for polarization leakage
#=======================================================================================

def WSRT_DJones (ns=0, **pp):
  """defines 2x2 WSRT_DJones (polarisation leakage) matrices""";

  # Deal with input parameters (pp):
  pp = record(JEN_pp (pp, 'WSRT_jones::WSRT_DJones(ns, **pp)',
                      _help=dict(stations='range of station names/numbers',
                                 punit='name of prediction-unit (source/patch)',
                                 solvable='if T, the parms are potentially solvable',
                                 coupled_XY_dang='if T, Xdang = Ydang per station',
                                 coupled_XY_dell='if T, Xdell = -Ydell per station',
                                 dang='MeqParm default funklet value',
                                 dell='MeqParm default funklet value',
                                 PZD='MeqParm default funklet value',
                                 stddev_dang='scatter in default  funklet c00 values',
                                 stddev_dell='scatter in default  funklet c00 values'),
                      stations=[0], punit='uvp', solvable=1,
                      coupled_XY_dang=True, coupled_XY_dell=True,
                      dang=0, dell=0, PZD=0,
                      stddev_dang=0, stddev_dell=0))
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp.trace)

  # Node names:
  jname = 'DJones'
  dang = 'dang'
  dell = 'dell'
  pzd = 'PZD'
  node_groups = ['Parm','D']

  # Create the various groups of parameters:
  parm = record(dang=[], Xdang=[], Ydang=[], dell=[], Xdell=[], Ydell=[], PZD=[])
  plot = record()
  plot.color = record(dang='green', Xdang='green', Ydang='black',
                      dell='magenta', Xdell='magenta', Ydell='yellow', PZD='red')
  plot.style = record(dang='dot', Xdang='dot', Ydang='dot',
                      dell='dot', Xdell='dot', Ydell='dot', PZD='dot')

  # The X/Y Phase-Zero-Difference (PZD) is shared by all stations:
  ss = (ns[pzd](q=pp.punit) << Meq.Parm(JEN_funklet(pp.PZD), node_groups=node_groups))
  parm[pzd].append(ss.name)
  matname = 'DJones_PZD_matrix'
  pmat = JEN_phase_matrix (ns, angle=ss, name=matname, trace=0)

  # Make the jones matrices per station:
  jones = {}
  ss = {}
  for station in pp.stations:

    ss['dang'] = (ns[dang](s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dang, stddev=pp.stddev_dang),
                            node_groups=node_groups))
    ss['Xdang'] = (ns[dang]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dang, stddev=pp.stddev_dang),
                            node_groups=node_groups))
    ss['Ydang'] = (ns[dang]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dang, stddev=pp.stddev_dang),
                            node_groups=node_groups))

    ss['dell'] = (ns[dell](s=station, q=pp.punit) <<
                  Meq.Parm(JEN_funklet(pp.dell, stddev=pp.stddev_dell),
                           node_groups=node_groups))
    ss['Xdell'] = (ns[dell]('X', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dell, stddev=pp.stddev_dell),
                            node_groups=node_groups))
    ss['Ydell'] = (ns[dell]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(JEN_funklet(pp.dell, stddev=pp.stddev_dell),
                            node_groups=node_groups))

    # The names of the MeqParm nodes are to be returned for a solver:
    [parm[key].append(ss[key].name) for key in ss.keys()]

    # Dipole angle errors may be coupled (dang(X)=dang(Y)) or not:
    matname = 'DJones_dang_matrix'
    if pp.coupled_XY_dang:
      rmat = JEN_rotation_matrix (ns, angle=ss['dang'], name=matname, trace=0)
    else: 
      rmat = JEN_rotation_matrix (ns, angle=[ss['Xdang'],ss['Ydang']], name=matname, trace=0)

    # Dipole ellipticities may be coupled (dell(X)=-dell(Y)) or not:
    matname = 'DJones_dell_matrix'
    if pp.coupled_XY_dell:
      emat = JEN_ellipticity_matrix (ns, angle=ss['dell'], name=matname, trace=0)
    else:
      emat = JEN_ellipticity_matrix (ns, angle=[ss['Xdell'],ss['Ydell']], name=matname, trace=0)

    # Make the 2x2 Jones matrix by multiplying the sub-matrices:
    stub = ns[jname](s=station, q=pp.punit) << Meq.MatrixMultiply (rmat, emat, pmat)
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  cross = ['XY','YX']
  solver['DJones'] = record(solvable=['Xdang','Ydang','Xdell','Ydell'], corrs=cross)
  solver['Ddang'] = record(solvable=['Xdang','Ydang'], corrs=cross)
  solver['Ddell'] = record(solvable=['Xdell','Ydell'], corrs=cross)
  if pp.coupled_XY_dang and pp.coupled_XY_dell:
    solver['DJones'] = record(solvable=['dang','dell'], corrs=cross)
    solver['Ddang'] = record(solvable=['dang'], corrs=cross)
    solver['Ddell'] = record(solvable=['dell'], corrs=cross)
  elif pp.coupled_XY_dang:
    solver['DJones'] = record(solvable=['dang','Xdell','Ydell'], corrs=cross)
    solver['Ddang'] = record(solvable=['dang'], corrs=cross)
  elif pp.coupled_XY_dell:
    solver['DJones'] = record(solvable=['Xdang','Ydang','dell'], corrs=cross)
    solver['Ddell'] = record(solvable=['dell'], corrs=cross)

  # Create the (standard) joneset object:
  joneset = _init_joneset(jname, origin='WSRT_jones::WSRT_DJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot,
                          trace=pp.trace);

  JEN_forest_history ('WSRT_DJones()', level=2)
  return joneset






#======================================================================================













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
    JJ.append(WSRT_GJones (ns, stations=stations, trace=1))
    JJ.append(WSRT_FJones (ns, stations=stations, trace=1))
    JJ.append(WSRT_BJones (ns, stations=stations, trace=1))
    # JJ.append(WSRT_DJones (ns, stations=stations, coupled_XY_dang=False, coupled_XY_dell=False, trace=1))
    JJ.append(WSRT_DJones (ns, stations=stations, trace=1))
    WSRT_display_jones_subtree (JJ[0])
    # WSRT_DJones (trace=1)
    # WSRT_GJones ()
    Jones = JJ[0]
    Jones = WSRT_JJones (ns, JJ, trace=1)

  if 0:
    JEN_display_NodeScope(ns, 'test')

  if 1:
    JEN_forest_history(show=True)
