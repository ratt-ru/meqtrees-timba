# ../Timba/WH/contrib/JEN/JEN_lsm.py:  
#   Temporary JEN version of Local Sky Model (LSM) object 

print '\n',100*'*'
print '** JEN_lsm.py    h30jul/h08aug2005'

# standard preamble
from Timba.TDL import *
from Timba.Meq import meq
from numarray import *

from JEN_util_TDL import *
from JEN_util import *
# Better: put the JEN stuff in a sub-directory....
# from JEN.JEN_util_TDL import *
# from JEN.JEN_util import *

  
#=======================================================================================


#=======================================================================================
# Initialise a standard 'sixpack' object, which contains the 6 nodes that
# represent the manifestations of a source/patch in the image.
# This object (dict) is updated by, and passed between, various TDL functions 

def lsm_init_sixpack (name='cps', origin='JEN_lsm::', input={},
                      iquv={}, radec={}, simul=0, trace=0):
  """initialise/check a standard _init_sixpack object"""
  sixpack = dict(name=name, type='sixpack', origin=origin, 
                 iquv=iquv, radec=radec, input=input, simul=simul)
  # n6 = lsm_sixnames()
  if trace: JEN_display (sixpack, 'sixpack', sixpack['name'])
  return sixpack


# Centrally define the 6 standard names:

def lsm_sixnames ():
  return record(I='StokesI', Q='StokesQ', U='StokesU', V='StokesV',
                R='RA', D='Dec') 

#=======================================================================================
# Make source subtrees with NEWSTAR parametrization:

def lsm_NEWSTAR_source (ns=0, **pp):
  # Deal with input parameters (pp):
  pp = dict(JEN_pp (pp, 'JEN_lsm.lsm_NEWSTAR_source(ns, **pp)',
  # pp = record(JEN_pp (pp, 'JEN_lsm.lsm_NEWSTAR_source(ns, **pp)',
                      _help=dict(name='source name',
                                 I0='StokesI0 (Jy)',
                                 Qpct='StokesQpct',
                                 Upct='StokesUpct',
                                 Vpct='StokesVpct',
                                 RM='Rotation Measure (rad/m2)',
                                 SI='Spectral Index (generalised)',
                                 f0='SI reference frequency (Hz)',
                                 shape='source shape (e.g. point or elliptic_gaussian)',
                                 major='major axis (rad), elliptic gaussian',
                                 minor='minor axis (rad), elliptic gaussian',
                                 pa='position angle (rad), elliptic gaussian',
                                 RA='Right Ascension (rad, J2000)',
                                 Dec='Declination (rad, J2000)'),
                      name='cps',
                      I0=1.0, Qpct=None, Upct=None, Vpct=None,
                      RM=None, SI=None, f0=1e6,
                      shape='point', major=0.0, minor=0.0, pa=0.0,
                      RA=0.0, Dec=1.0))
  if isinstance(ns, int): return JEN_pp_noexec(pp, trace=pp['trace'])
  # print 'pp (after JEN_pp()):',pp

  # Adjust parameters pp for some special cases:
  lsm_NEWSTAR_calibrators (pp, trace=pp['trace'])  

  # Make the sixpack of 6 standard subtree root-nodes: 
  n6 = lsm_sixnames()
  zero = (ns.zero << Meq.Constant(0))

  iquv = {}
  parm = {}
  fmult = 1.0
  if pp['SI'] is None:
    parm['I0'] = (ns.I0(q=pp['name']) << Meq.Parm(pp['I0']))
    iquv[n6.I] = parm['I0']
  else:
    # For the moment, we use only the first term of the SI
    # until I have the PolcLog figured out again
    print 'pp[SI] =',pp['SI'],type(pp['SI'])
    print 'len(pp[SI]) =',len(pp['SI'])
    if not isinstance(pp['SI'], list): pp['SI'] = [pp['SI']]
    # pp['SI'] =  pp['SI'][0]
    if not isinstance(pp['SI'], list): pp['SI'] = [pp['SI']]
    print 'pp[SI] =',pp['SI'],type(pp['SI'])
    print 'len(pp[SI]) =',len(pp['SI'])
    if len(pp['SI']) == 1:
      print type(ns)
      parm['I0'] = (ns.I0(q=pp['name']) << Meq.Parm(pp['I0']))
      parm['SI'] = (ns.SI(q=pp['name']) << Meq.Parm(pp['SI']))
      freq = (ns.freq << Meq.Freq())
      fratio = (ns.fratio(q=pp['name']) << (freq/pp['f0']))
      fmult = (ns.fmult(q=pp['name']) << Meq.Pow(fratio, parm['SI']))
      iquv[n6.I] = (ns[n6.I](q=pp['name']) << (parm['I0'] * fmult))
    else:
      SIF = [log(pp['I0'])]                           # what if I0 is polc???
      SIF.extend(pp['SI'])
      # NB: SIF[1] = classical S.I.
      SIF = array(SIF)
      SIF = reshape(SIF, (1,len(SIF)))
      polc = meq.polclog(SIF) 
      # polc.funklet_type = 'MeqPolcLog'
      parm['SIF'] = (ns.SIF(q=pp['name']) << Meq.Parm(polc))
      iquv[n6.I] = (ns[n6.I](q=pp['name']) << Meq.Selector(parm['SIF']))
      # NB: fmult = 1.0, so Q,U,V are NOT corrected for SI....
      #     possible solution: make fmult from SIF with SIF[0] = 10

  # Create Stokes V by converting Vpct and correcting for SI if necessary
  iquv[n6.V] = zero
  if pp['Vpct'] is not None:
    parm['Vpct'] = (ns.Vpct(q=pp['name']) << Meq.Parm(pp['Vpct']))
    if isinstance(fmult, float):
      iquv[n6.V] = (ns[n6.V](q=pp['name']) << (parm['Vpct']*(fmult/100)))
    else:
      iquv[n6.V] = (ns[n6.V](q=pp['name']) << (parm['Vpct']*fmult/100))
    
      
  if pp['RM'] is None:
    # Without Rotation Measure:
    # Create Stokes Q by converting Qpct and correcting for SI if necessary
    iquv[n6.Q] = zero
    if pp['Qpct'] is not None:
      parm['Qpct'] = (ns.Qpct(q=pp['name']) << Meq.Parm(pp['Qpct']))
      if isinstance(fmult, float):
        iquv[n6.Q] = (ns[n6.Q](q=pp['name']) << (parm['Qpct']*(fmult/100)))
      else:
        iquv[n6.Q] = (ns[n6.Q](q=pp['name']) << (parm['Qpct']*fmult/100))

    # Create Stokes U by converting Upct and correcting for SI if necessary
    iquv[n6.U] = zero
    if pp['Upct'] is not None:
      parm['Upct'] = (ns.Upct(q=pp['name']) << Meq.Parm(pp['Upct']))
      if isinstance(fmult, float):
        iquv[n6.U] = (ns[n6.U](q=pp['name']) << (parm['Upct']*(fmult/100)))
      else:
        iquv[n6.U] = (ns[n6.U](q=pp['name']) << (parm['Upct']*fmult/100))
    
  else:
    # With Rotation Measure: 
    # Create an intermediate QU = [Q,U]
    if pp['Qpct'] is None: pp['Qpct'] = 0.0
    if pp['Upct'] is None: pp['Upct'] = 0.0
    parm['Qpct'] = (ns.Qpct(q=pp['name']) << Meq.Parm(pp['Qpct']))
    parm['Upct'] = (ns.Upct(q=pp['name']) << Meq.Parm(pp['Upct']))
    if isinstance(fmult, float):
      Q = (ns['Q'](q=pp['name']) << (parm['Qpct']*(fmult/100)))
      U = (ns['U'](q=pp['name']) << (parm['Upct']*(fmult/100)))
    else:
      Q = (ns['Q'](q=pp['name']) << (parm['Qpct']*fmult/100))
      U = (ns['U'](q=pp['name']) << (parm['Upct']*fmult/100))
    QU = (ns['QU'](q=pp['name']) << Meq.Composer(children=[Q,U]))  

    # Rotate QU by the RM matrix -> QURM
    parm['RM'] = (ns.RM(q=pp['name']) << Meq.Parm(pp['RM']))
    wvl2 = JEN_wavelength (ns, unop='Sqr', trace=0)
    farot = ns.farot(q=pp['name']) << (parm['RM']*wvl2)
    rotmat = JEN_rotation_matrix (ns, angle=farot, trace=0)
    QURM = (ns['QURM'](q=pp['name']) << Meq.MatrixMultiply(rotmat, QU))  
    if trace:
      JEN_display_subtree(QURM, 'QURM', full=1)

    # Unpack QURM into separate StokesQ and StokesU subtrees:
    iquv[n6.Q] = (ns[n6.Q](q=pp['name']) <<  Meq.Selector(QURM, index=0))
    iquv[n6.U] = (ns[n6.U](q=pp['name']) <<  Meq.Selector(QURM, index=1))



  # Source coordinates (RA, DEC)
  radec = {}
  radec[n6.R] = (ns[n6.R](q=pp['name']) << Meq.Parm(pp['RA']))
  radec[n6.D] = (ns[n6.D](q=pp['name']) << Meq.Parm(pp['Dec']))

  if trace:
    for key in iquv.keys():
      JEN_display_subtree(iquv[key], key, full=1)

  sixpack = lsm_init_sixpack (name=pp['name'], iquv=iquv, radec=radec, trace=pp['trace'])

  return sixpack

#----------------------------------------------------------------------
# Some sources are predefined: Modify parameters pp accordingly.

def lsm_NEWSTAR_calibrators (pp, trace=0):  

  # Some sources are defined by their name:
  # NB: It is assumed that none of their source parameters are explicitly specified!
  if (pp['name']=='3c147'):
    pp['I0'] = 10**1.766
    pp['SI'] = [0.447, -0.184]
  elif (pp['name']=='3c48'):
    pp['I0'] = 10**2.345
    pp['SI'] = [0.071, -0.138]
  elif (pp['name']=='3c286'): 
    pp['I0'] = 10**1.48
    pp['SI'] = [0.292, -0.124]
    pp['Q'] = [2.735732, -0.923091, 0.073638]
    pp['U'] = [6.118902, -2.05799, 0.163173]
  elif (pp['name']=='3c295'):
    pp['I0'] = 10**1.485
    pp['SI'] = [0.759, -0.255]
  elif (pp['name']=='unpol'):
    pp['I0'] = pp['I0']
  elif (pp['name']=='Qonly'):
    pp['Qpct'] = 10
  elif (pp['name']=='Uonly'):
    pp['Upct'] = -10
  elif (pp['name']=='Vonly'):
    pp['Vpct'] = 2                            
  elif (pp['name']=='QU'):
    pp['Qpct'] = 10
    pp['Upct'] = -10
  elif (pp['name']=='QUV'):
    pp['Qpct'] = 10
    pp['Upct'] = -10
    pp['Vpct'] = 2
  elif (pp['name']=='QU2'):
    pp['I0'] = 2.0
    pp['Qpct'] = 40
    pp['Upct'] = -30
  elif (pp['name']=='RMtest'):
    pp['RM'] = 1.0
    pp['Qpct'] = 10
    pp['Upct'] = -10
  elif (pp['name']=='SItest'):
    pp['SI'] = -0.7
  elif (pp['name']=='I0polc'):
    pp['I0'] = array([[2,-.3,.1],[.3,-.1,0.03]]),

  # if trace: print 'pp =',pp
  return 




#=======================================================================================
# Test function:
#=======================================================================================

if __name__ == '__main__':
  ns = NodeScope()
  nsub = ns.Subscope('_')
  print 

  if 0:
    lsm_init_sixpack (name='cps', origin='JEN_lsm:', input={},
                      iquv={}, radec={}, simul=0, trace=1)

  if 1:
    n6 = lsm_sixnames()
    name = 'unpol'
    name = 'QU2'
    name = '3c147'
    name = 'RMtest'
    # NB: subscope can only be used when cumulative (simul!)
    nsub = ns.Subscope('LSM', q=name)
    lsm_NEWSTAR_source (nsub, name=name, trace=1)

  if 0:
    # print dir(meq)
    print dir(meq.polc)
    print meq.polc.func_defaults
    print meq.polc.func_doc
    print meq.polc.func_code
    
  if 0:
    lsm_NEWSTAR_source (nsub, name='3c147', trace=1)

  if 0:
    c = [0]
    print c, shape(c)
    c.append(3)
    print c, shape(c)
    aa = [2,3,4]
    [c.append(aa[i]) for i in range(len(aa))]
    # c.append([4,5])
    # reshape(c, (4,))
    print c, shape(c)

  if 0:
    polc = [12.,13]
    polc = array(polc)
    print polc, type(polc),polc.shape
    polc = reshape(polc, (1,2))
    print '(after reshape):',polc, type(polc),polc.shape
    polc = meq.polc(polc)
    print polc, type(polc)
    node = ns.yyy << Meq.Parm(polc)
    print node, node.name, node.classname, node.initrec()

  print

