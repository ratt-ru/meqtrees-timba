script_name = 'MG_JEN_joneset.py'

# Short description:
#   Functions dealing with a set (joneset) of 2x2 station Jones matrices

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 31 aug 2005: added .visualise()

# Copyright: The MeqTree Foundation 


#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_matrix
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_visualise


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

    # Make a series of (jonesets of) 2x2 jones matrices:
   stations = range(0,3)
   ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
   JJ = []
   JJ.append(GJones (ns, stations=stations, stddev_ampl=0.5, stddev_phase=0.5)) 
   JJ.append(BJones (ns, stations=stations, stddev_real=0.3, stddev_imag=0.1))
   JJ.append(FJones (ns, stations=stations))
   JJ.append(DJones_WSRT (ns, stations=stations, stddev_dang=0.1, stddev_dell=0.1))
   # JJ.append(DJones_WSRT (ns, stations=stations, coupled_XY_dang=False, coupled_XY_dell=False))

   # Visualise them individually and collectively:
   dconc = []
   for i in range(len(JJ)):
     dc = visualise(ns, JJ[i])
     cc.append(dc)
     dconc.append(dc)

   # Matrix multiply to produce the resulting Jones joneset:
   Jones = JJones (ns, JJ)
   dc = visualise(ns, Jones)
   cc.append(dc)
   dconc.append(dc)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================



#--------------------------------------------------------------------------------
# Initialise a standard 'joneset' object, which contains information about
# a set of 2x2 jones matrices for all stations, for a single p-unit (source):
# This object (dict) is updated by, and passed between, various TDL functions 

def init (name='<Jones>', origin='MG_JEN_jones:', input={},
                   stations=[0], punit='uvp',
                   jones={}, parm={}, solver={}, plot={}):
  """initialise/check a standard joneset object"""
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
      
  return joneset


#--------------------------------------------------------------------------------
# Display the first jones matrix in the given joneset:

def display_jones_subtree (joneset, full=1):
  keys = joneset['jones'].keys()
  jones = joneset['jones'][keys[0]]
  txt = 'jones[0/'+str(len(keys))+'] of joneset: '+joneset['name']
  MG_JEN_exec.display_subtree(jones, txt, full=full)


#======================================================================================
# Visualie the contents of a joneset

def visualise(ns, joneset, **pp):
    """visualises the 2x2 jonse matrices in joneset"""

    # Input arguments:
    pp.setdefault('scope', 'simulated')     # identifying name of this visualiser
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('result', 'joneset')      # result of this routine (joneset or dcolls)
    pp = record(pp)

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    jname = joneset['name']                 # e.g. GJones
    visu_scope = 'visu_'+pp.scope+'_'+jname
  
    # Make dcolls per parm group:
    dcoll = []
    for key in joneset['parm'].keys():
       if len(joneset['parm'][key])>0:      # ignore if empty list
          dc = MG_JEN_visualise.dcoll (ns, joneset['parm'][key],
                                       scope=visu_scope, tag=key,
                                       type=pp.type, errorbars=pp.errorbars,
                                       color=joneset['plot']['color'][key],
                                       style=joneset['plot']['style'][key])
          dcoll.append(dc)

    # Make dcolls per matrix element:
    nodes = dict(m11=[], m12=[], m21=[], m22=[])
    mkeys = nodes.keys()
    for skey in joneset['jones'].keys():
       jones = joneset['jones'][skey]
       for i in range(len(mkeys)):
          mkey = mkeys[i]
          nsub = ns.Subscope(visu_scope+'_'+mkey, s=skey)
          selected = nsub.selector(i) << Meq.Selector (jones, index=i)
          nodes[mkey].append(selected)
       
    for mkey in nodes.keys():
       dc = MG_JEN_visualise.dcoll (ns, nodes[mkey],
                                    scope=visu_scope, tag=mkey,
                                    type=pp.type, errorbars=pp.errorbars)
       dcoll.append(dc)

 
    # Make concatenations of dcolls:
    sc = []
    dconc = MG_JEN_visualise.dconc(ns, dcoll, scope=visu_scope,
                                   bookpage=jname)
    MG_JEN_forest_state.history ('MG_JEN_joneset::visualise()')

    # Return node that needs a request:
    return dconc['dcoll']


#--------------------------------------------------------------------------------

def JJones (ns, jonesets=[], **pp):
  """makes a set of JJones matrices by multiplying input jones matrices""";

  jname = 'JJones'
  joneset = init(jname, origin='MG_JEN_jones::JJones()');

  if len(jonesets) == 0:
     return MG_JEN_forest_state.error ('MG_JEN_joneset::JJones()')
     
  # 
  for i in range(len(jonesets)):      
    jsin = jonesets[i]                                # convenience
    # JEN_display (jsin, jsin['name'])
    key = jsin['name']                                # e.g. 'GJones'
    print '- JJones:',i,key
    joneset['input'][key] = jsin['input']
     
    if i == 0:                                        # first one
      joneset['parm'] = jsin['parm']
      joneset['solver'] = jsin['solver']
      joneset['plot']['color'] = jsin['plot']['color']
      joneset['plot']['style'] = jsin['plot']['style']
      # joneset['jseq'] = [jsin['jseq']]             # obsolete....?
      punit = jsin['punit']
      for key in jonesets[0]['jones'].keys():        # for all stations
        joneset['jones'][key] = [jsin['jones'][key]]

    elif jsin['punit'] != punit:                     # **ERROR**
      err = 'different punits:'+punit+':'+str(jsin['punit'])
      return JEN_history (joneset, error=err)
            
    else:
      joneset['parm'].update(jsin['parm'])           # merge parms
      joneset['solver'].update(jsin['solver'])       # merge solvers
      joneset['plot']['color'].update(jsin['plot']['color'])
      joneset['plot']['style'].update(jsin['plot']['style'])
      # joneset['jseq'].append(jsin['jseq'])         # obsolete....?
      for key in jsin['jones'].keys():               # for all stations
        joneset['jones'][key].append(jsin['jones'][key]) # append to list


  # Multiply the accumulated (listed) jones matrices per station (key):
  for key in joneset['jones'].keys():
    jj = joneset['jones'][key]
    kwquals = jj[0].kwquals
    quals = list(jj[0].quals)
    if len(jj) == 1:
      j0 = ns[jname](**kwquals)(*quals) << Meq.Selector(*jj)
    else:
      for i in range(1,len(jj)):
        kwquals.update(jj[i].kwquals)
        quals.extend(list(jj[i].quals))
      j0 = ns[jname](**kwquals)(*quals) << Meq.MatrixMultiply(*jj)
    joneset['jones'][key] = j0

  # Finished:
  MG_JEN_forest_state.history ('MG_JEN_joneset::JJones()', level=2)
  return joneset
  


#--------------------------------------------------------------------------------
# GJones: diagonal 2x2 matrix for complex gains per polarization

def GJones (ns=0, **pp):
  """defines diagonal GJones matrices for complex(ampl,phase) parms""";

  # Input parameters:
  pp.setdefault('stations', [0])       # range of station names/numbers
  pp.setdefault('punit', 'uvp')        # name of prediction-unit (source/patch)
  pp.setdefault('solvable', True)      # if True, the parms are potentially solvable
  pp.setdefault('ampl', 1.0)           # default funklet value
  pp.setdefault('phase', 0.0)          # default funklet value
  pp.setdefault('polar', False)        # if True, use MeqPolar, otherwise MeqToComplex
  pp.setdefault('stddev_ampl', 0)      # scatter in default funklet c00 values
  pp.setdefault('stddev_phase', 0)     # scatter in default funklet c00 values
  pp = record(pp)

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
                   Meq.Parm(MG_JEN_funklet.funklet(pp.ampl, stddev=pp.stddev_ampl),
                            node_groups=node_groups))
    ss['Yampl'] = (ns[aname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(MG_JEN_funklet.funklet(pp.ampl, stddev=pp.stddev_ampl),
                            node_groups=node_groups))
    ss['Xphase'] = (ns[pname]('X', s=station, q=pp.punit) <<
                    Meq.Parm(MG_JEN_funklet.funklet(pp.phase, stddev=pp.stddev_phase),
                             node_groups=node_groups))
    ss['Yphase'] = (ns[pname]('Y', s=station, q=pp.punit) <<
                    Meq.Parm(MG_JEN_funklet.funklet(pp.phase, stddev=pp.stddev_phase),
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
  joneset = init(jname, origin='MG_JEN_joneset::GJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot)

  # Finished:
  MG_JEN_forest_state.history ('MG_JEN_joneset::GJones()', level=2)
  return joneset



#--------------------------------------------------------------------------------
# BJones: diagonal 2x2 matrix for complex bandpass per polarization

def BJones (ns=0, **pp):
  """defines diagonal BJones bandpass matrices""";

  # Input parameters:
  pp.setdefault('stations', [0])       # range of station names/numbers
  pp.setdefault('punit', 'uvp')        # name of prediction-unit (source/patch)
  pp.setdefault('solvable', True)      # if True, the parms are potentially solvable
  pp.setdefault('real', 1.0)           # default funklet value
  pp.setdefault('imag', 0.0)           # default funklet value
  pp.setdefault('polar', False)        # if True, use MeqPolar, otherwise MeqToComplex
  pp.setdefault('stddev_real', 0)      # scatter in default funklet c00 values
  pp.setdefault('stddev_imag', 0)      # scatter in default funklet c00 values
  pp = record(pp)

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
                   Meq.Parm(MG_JEN_funklet.funklet(pp.real, stddev=pp.stddev_real),
                            node_groups=node_groups))              
    ss['Yreal'] = (ns[aname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(MG_JEN_funklet.funklet(pp.real, stddev=pp.stddev_real),
                            node_groups=node_groups))              
    ss['Ximag'] = (ns[pname]('X', s=station, q=pp.punit) <<
                   Meq.Parm(MG_JEN_funklet.funklet(pp.imag, stddev=pp.stddev_imag),
                            node_groups=node_groups))              
    ss['Yimag'] = (ns[pname]('Y', s=station, q=pp.punit) <<
                   Meq.Parm(MG_JEN_funklet.funklet(pp.imag, stddev=pp.stddev_imag),
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
  joneset = init(jname, origin='MG_JEN_joneset::BJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot)

  # Finished:
  MG_JEN_forest_state.history ('MG_JEN_joneset::BJones()', level=2)
  return joneset


#--------------------------------------------------------------------------------
# FJones: 2x2 matrix for ionospheric Faraday rotation (NOT ion.phase!)

def FJones (ns=0, **pp):
  """defines diagonal FJones Faraday rotation matrices""";

  # Input parameters:
  pp.setdefault('stations', [0])       # range of station names/numbers
  pp.setdefault('punit', 'uvp')        # name of prediction-unit (source/patch)
  pp.setdefault('solvable', True)      # if True, the parms are potentially solvable
  pp.setdefault('RM', 0.0)             # default funklet value
  pp = record(pp)

  jname = 'FJones'
  node_groups = ['Parm','F']

  # Create the various groups of parameters:
  parm = record(RM=[])
  plot = record(color=record(RM='red'),
                style=record(RM='dot'))

  # Make the lambda-squared node for RM -> farot conversion: 
  wvl2 = MG_JEN_twig.wavelength (ns, unop='Sqr')

  RM = (ns.RM(q=pp.punit) << Meq.Parm(MG_JEN_funklet.funklet(pp.RM),
                                      node_groups=node_groups))
  parm['RM'] = [RM.name]
  farot = (ns.farot(q=pp.punit) << (RM * wvl2))

  matname = 'FJones_rotation_matrix' 
  stub = MG_JEN_matrix.rotation (ns, angle=farot, name=matname)

  jones = {}
  for station in pp.stations:
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  cross = ['XY','YX']
  solver['FJones'] = record(solvable=['RM'], corrs=cross)

  # Create the (standard) joneset object:
  joneset = init(jname, origin='MG_JEN_joneset::FJones()', input=pp,
                          stations=pp.stations, punit=pp.punit,
                          jones=jones, parm=parm, solver=solver, plot=plot)

  # Finished:
  MG_JEN_forest_state.history ('MG_JEN_joneset::FJones()', level=2)
  return joneset



#--------------------------------------------------------------------------------
# DJones: 2x2 matrix for polarization leakage

def DJones_WSRT (ns=0, **pp):
  """defines 2x2 DJones_WSRT (polarisation leakage) matrices""";

  # Input parameters:
  pp.setdefault('stations', [0])                  # range of station names/numbers
  pp.setdefault('punit', 'uvp')                    # name of prediction-unit (source/patch)
  pp.setdefault('solvable', True)                # if True, the parms are potentially solvable
  pp.setdefault('coupled_XY_dang', True)  # if True, Xdang = Ydang per station
  pp.setdefault('coupled_XY_dell', True)  # if True, Xdell = -Ydell per station
  pp.setdefault('dang', 0.0)                          # default funklet value
  pp.setdefault('dell', 0.0)                          # default funklet value
  pp.setdefault('PZD', 0.0)                            # default funklet value
  pp.setdefault('stddev_dang', 0)               # scatter in default funklet c00 values
  pp.setdefault('stddev_dell', 0)               # scatter in default funklet c00 values
  pp = record(pp)

  # Node names:
  jname = 'DJones_WSRT'
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
  ss = (ns[pzd](q=pp.punit) << Meq.Parm(MG_JEN_funklet.funklet(pp.PZD), node_groups=node_groups))
  parm[pzd].append(ss.name)
  matname = 'DJones_PZD_matrix'
  pmat = MG_JEN_matrix.phase (ns, angle=ss, name=matname)

  # Make the jones matrices per station:
  jones = {}
  ss = {}
  for station in pp.stations:

    # Dipole angle errors may be coupled (dang(X)=dang(Y)) or not:
    matname = 'DJones_dang_matrix'
    if pp.coupled_XY_dang:
       ss['dang'] = (ns[dang](s=station, q=pp.punit) <<
                     Meq.Parm(MG_JEN_funklet.funklet(pp.dang, stddev=pp.stddev_dang),
                              node_groups=node_groups))
       rmat = MG_JEN_matrix.rotation (ns, angle=ss['dang'], name=matname)
    else: 
       ss['Xdang'] = (ns[dang]('X', s=station, q=pp.punit) <<
                      Meq.Parm(MG_JEN_funklet.funklet(pp.dang, stddev=pp.stddev_dang),
                               node_groups=node_groups))
       ss['Ydang'] = (ns[dang]('Y', s=station, q=pp.punit) <<
                      Meq.Parm(MG_JEN_funklet.funklet(pp.dang, stddev=pp.stddev_dang),
                               node_groups=node_groups))
       rmat = MG_JEN_matrix.rotation (ns, angle=[ss['Xdang'],ss['Ydang']], name=matname)


    # Dipole ellipticities may be coupled (dell(X)=-dell(Y)) or not:
    matname = 'DJones_dell_matrix'
    if pp.coupled_XY_dell:
       ss['dell'] = (ns[dell](s=station, q=pp.punit) <<
                     Meq.Parm(MG_JEN_funklet.funklet(pp.dell, stddev=pp.stddev_dell),
                              node_groups=node_groups))
       emat = MG_JEN_matrix.ellipticity (ns, angle=ss['dell'], name=matname)
    else:
       ss['Xdell'] = (ns[dell]('X', s=station, q=pp.punit) <<
                      Meq.Parm(MG_JEN_funklet.funklet(pp.dell, stddev=pp.stddev_dell),
                               node_groups=node_groups))
       ss['Ydell'] = (ns[dell]('Y', s=station, q=pp.punit) <<
                      Meq.Parm(MG_JEN_funklet.funklet(pp.dell, stddev=pp.stddev_dell),
                               node_groups=node_groups))
       emat = MG_JEN_matrix.ellipticity (ns, angle=[ss['Xdell'],ss['Ydell']], name=matname)


    # The names of the MeqParm nodes are to be returned for a solver:
    [parm[key].append(ss[key].name) for key in ss.keys()]

    # Make the 2x2 Jones matrix by multiplying the sub-matrices:
    stub = ns[jname](s=station, q=pp.punit) << Meq.MatrixMultiply (rmat, emat, pmat)
    jones[station] = stub

  # Make named groups of solvable parms for various (named) solvers:
  solver = {}
  cross = ['XY','YX']
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
  else:
    solver['DJones'] = record(solvable=['Xdang','Ydang','Xdell','Ydell'], corrs=cross)
    solver['Ddang'] = record(solvable=['Xdang','Ydang'], corrs=cross)
    solver['Ddell'] = record(solvable=['Xdell','Ydell'], corrs=cross)

  # Create the (standard) joneset object:
  joneset = init(jname, origin='MG_JEN_joneset::DJones_WSRT()', input=pp,
                 stations=pp.stations, punit=pp.punit,
                 jones=jones, parm=parm, solver=solver, plot=plot)

  # Finished:
  MG_JEN_forest_state.history ('MG_JEN_joneset::DJones_WSRT()', level=2)
  return joneset

















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
  print '\n*******************\n** Local test of:',script_name,':\n'

  # This is the default:
  # MG_JEN_exec.without_meqserver(script_name)

  # This is the place for some specific tests during development.
  ns = NodeScope()
  stations = range(0,3)
  ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
  JJ = []

  if 1:
    JJ.append(GJones (ns, stations=stations))
    # JJ.append(DJones_WSRT (ns, stations=stations))
    # MG_JEN_exec.display_object (JJ[0], 'joneset')
    print 'JJ =',len(JJ),'\n',JJ
    Jones = JJones (ns, JJ)
    MG_JEN_exec.display_object (Jones, 'Jones')

  if 0:
    JJ.append(GJones (ns, stations=stations))
    dconc = visualise(ns, JJ[0])
    MG_JEN_exec.display_object (dconc, 'dconc')
    MG_JEN_exec.display_subtree (dconc, 'dconc', full=1)

  if 0:
    JJ.append(GJones (ns, stations=stations))
    JJ.append(FJones (ns, stations=stations))
    JJ.append(BJones (ns, stations=stations))
    # JJ.append(DJones_WSRT (ns, stations=stations, coupled_XY_dang=False, coupled_XY_dell=False))
    JJ.append(DJones_WSRT (ns, stations=stations))
    # DJones_WSRT()
    # GJones()
    # Jones = JJ[0]
    # display_jones_subtree (JJ[0])
    Jones = JJones (ns, JJ)
    display_jones_subtree (Jones)
    # MG_JEN_exec.display_subtree (rr, 'rr', full=1)


  print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




