script_name = 'MG_JEN_sixpack.py'

# Short description:
#   Generation of some LSM point-source sixpacks, for simulation 

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 28 aug 2005: creation

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
from Timba.Contrib.JEN import MG_JEN_twig


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

  # Make a dict of named sixpacks for various sources:  
   sixpack = {}
   sixpack['default'] = newstar_source (ns)
   sixpack['unpol'] = newstar_source (ns, name='unpol')
   sixpack['3c147'] = newstar_source (ns, name='3c147')
   sixpack['3c286'] = newstar_source (ns, name='3c286')                          # <------ !!
   sixpack['QUV'] = newstar_source (ns, name='QUV')
   nsub = ns.Subscope('sub') 
   sixpack['QUV_RM_SI'] = newstar_source (nsub, name='QUV', RM=1, SI=-0.7)
 
  # Make 'bundles' of the 4 (I,Q,U,V) flux subtrees in each sixpack:
   for skey in sixpack.keys():
      bb = []
      for key in sixpack[skey]['iquv'].keys():
         bb.append(sixpack[skey]['iquv'][key])
      cc.append(MG_JEN_exec.bundle(ns, bb, skey))

   # Collect the 'loose' RA,DEC root nodes to a single root node (more tidy):
   radec = [] 
   for skey in sixpack.keys():
      for key in sixpack[skey]['radec'].keys():
         radec.append(sixpack[skey]['radec'][key])
   radec_root = ns.radec_root << Meq.Add (children=radec)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)









#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================


#=======================================================================================
# Initialise a standard 'sixpack' object, which contains the 6 nodes that
# represent the manifestations of a source/patch in the image.
# This object (dict) is updated by, and passed between, various TDL functions 

def init (name='cps', origin='MG_JEN_newstar::', input={},
          iquv={}, radec={}, simul=0, trace=0):
   """initialise/check a standard sixpack object"""
   sixpack = dict(name=name, type='lsm_sixpack', origin=origin, 
                  iquv=iquv, radec=radec, input=input, simul=simul)
   # n6 = lsm_sixnames()
   # if trace: JEN_display (sixpack, 'sixpack', sixpack['name'])
   return sixpack


# Centrally define the 6 standard names:

def sixnames ():
  return record(I='StokesI', Q='StokesQ', U='StokesU', V='StokesV', R='RA', D='Dec') 




#---------------------------------------------------------------------------------------
# Make sixpack of subtrees for sources with 'NEWSTAR' parametrization:

def newstar_source (ns=0, **pp):

   # Deal with input parameters (pp):
   pp.setdefault('name', 'cps')        # source name
   pp.setdefault('I0', 1.0)            # StokesI0 (Jy)
   pp.setdefault('Qpct', None)         # StokesQpct
   pp.setdefault('Upct', None)         # StokesUpct
   pp.setdefault('Vpct', None)         # StokesVpct
   pp.setdefault('RM', None)           # Rotation Measure (rad/m2)
   pp.setdefault('SI', None)           # Spectral Index (generalised)
   pp.setdefault('f0', 1e6)            # SI reference frequency (Hz)
   pp.setdefault('shape', 'point')     # source shape (e.g. point or elliptic_gaussian)
   pp.setdefault('major', 0.0)         # major axis (rad), elliptic gaussian
   pp.setdefault('minor', 0.0)         # minor axis (rad), elliptic gaussian
   pp.setdefault('pa', 0.0)            # position angle (rad), elliptic gaussian
   pp.setdefault('RA', 0.0)            # Right Ascension (rad, J2000)
   pp.setdefault('Dec', 1.0)           # Declination (rad, J2000)
   pp = record(pp)
  
   # Adjust parameters pp for some special cases:
   predefined (pp)  
   
   # Make the sixpack of 6 standard subtree root-nodes: 
   n6 = sixnames()
   zero = ns.zero << Meq.Constant(0)
   
   iquv = {}
   parm = {}
   fmult = 1.0
   if pp['SI'] is None:
      parm['I0'] = ns.I0(q=pp['name']) << Meq.Parm(pp['I0'])
      iquv[n6.I] = parm['I0']
   else:
      iquv[n6.I] = MG_JEN_funklet.polclog_flux(ns, source=pp['name'], I0=pp['I0'], SI=pp['SI'], stokes='I')
      # fmult = ...??

   # Create Stokes V by converting Vpct and correcting for SI if necessary
   iquv[n6.V] = zero
   if pp['Vpct'] is not None:
      parm['Vpct'] = ns.Vpct(q=pp['name']) << Meq.Parm(pp['Vpct'])
      if isinstance(fmult, float):
         iquv[n6.V] = ns[n6.V](q=pp['name']) << (parm['Vpct']*(fmult/100))
      else:
         iquv[n6.V] = ns[n6.V](q=pp['name']) << (parm['Vpct']*fmult/100)
    
      
   if pp['RM'] is None:
      # Without Rotation Measure:
      # Create Stokes Q by converting Qpct and correcting for SI if necessary
      iquv[n6.Q] = zero
      if pp['Qpct'] is not None:
         parm['Qpct'] = ns.Qpct(q=pp['name']) << Meq.Parm(pp['Qpct'])
         if isinstance(fmult, float):
            iquv[n6.Q] = ns[n6.Q](q=pp['name']) << (parm['Qpct']*(fmult/100))
         else:
            iquv[n6.Q] = ns[n6.Q](q=pp['name']) << (parm['Qpct']*fmult/100)

      # Create Stokes U by converting Upct and correcting for SI if necessary
      iquv[n6.U] = zero
      if pp['Upct'] is not None:
         parm['Upct'] = ns.Upct(q=pp['name']) << Meq.Parm(pp['Upct'])
         if isinstance(fmult, float):
            iquv[n6.U] = ns[n6.U](q=pp['name']) << (parm['Upct']*(fmult/100))
         else:
            iquv[n6.U] = ns[n6.U](q=pp['name']) << (parm['Upct']*fmult/100)
    
   else:
      # With Rotation Measure: 
      # Create an intermediate QU = [Q,U]
      if pp['Qpct'] is None: pp['Qpct'] = 0.0
      if pp['Upct'] is None: pp['Upct'] = 0.0
      if 0:
         pass
         # NB: Some sources have polclogs for their absolute polarised flux (e.g. 3c286):
         # iquv['Q'] = MG_JEN_funklet.polclog_flux(ns, source=pp['name'], stokes='Q')
         # iquv['U'] = MG_JEN_funklet.polclog_flux(ns, source=pp['name'], stokes='U')
         # if not == 0.0, then ....
      parm['Qpct'] = ns.Qpct(q=pp['name']) << Meq.Parm(pp['Qpct'])
      parm['Upct'] = ns.Upct(q=pp['name']) << Meq.Parm(pp['Upct'])
      if isinstance(fmult, float):
         Q = ns['Q'](q=pp['name']) << (parm['Qpct']*(fmult/100))
         U = ns['U'](q=pp['name']) << (parm['Upct']*(fmult/100))
      else:
         Q = ns['Q'](q=pp['name']) << (parm['Qpct']*fmult/100)
         U = ns['U'](q=pp['name']) << (parm['Upct']*fmult/100)
      QU = ns['QU'](q=pp['name']) << Meq.Composer(children=[Q,U])  

      # Rotate QU by the RM matrix -> QURM
      parm['RM'] = ns.RM(q=pp['name']) << Meq.Parm(pp['RM'])
      wvl2 = MG_JEN_twig.wavelength (ns, qual='auto', unop='Sqr')
      farot = ns.farot(q=pp['name']) << (parm['RM']*wvl2)
      rotmat = MG_JEN_matrix.rotation (ns, angle=farot)
      QURM = ns['QURM'](q=pp['name']) << Meq.MatrixMultiply(rotmat, QU)  

      # Unpack QURM into separate StokesQ and StokesU subtrees:
      iquv[n6.Q] = ns[n6.Q](q=pp['name']) <<  Meq.Selector(QURM, index=0)
      iquv[n6.U] = ns[n6.U](q=pp['name']) <<  Meq.Selector(QURM, index=1)


   # Source coordinates (RA, DEC)
   radec = {}
   radec[n6.R] = ns[n6.R](q=pp['name']) << Meq.Parm(pp['RA'])
   radec[n6.D] = ns[n6.D](q=pp['name']) << Meq.Parm(pp['Dec'])

   # Finished: Make the sixpack and return it
   sixpack = init (name=pp['name'], iquv=iquv, radec=radec)
   return sixpack





#----------------------------------------------------------------------
# Some sources are predefined: Modify parameters pp accordingly.

def predefined (pp, trace=0):  

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
   print '\n**',script_name,':\n'
   
   # This is the default:
   MG_JEN_exec.without_meqserver(script_name)

   # This is the place for some specific tests during development.
   ns = NodeScope()
   if 1:
      # sixpack = newstar_source (ns)
      # sixpack = newstar_source (ns, name='3c147')
      sixpack = newstar_source (ns, name='3c286')                    # <------ !!
      # sixpack = newstar_source (ns, name='QUV', RM=1, SI=-0.7)
      for key in sixpack['iquv'].keys():
         MG_JEN_exec.display_subtree (sixpack['iquv'][key], 'key', full=1)

   print '\n** end of',script_name,'\n'

#********************************************************************************
#********************************************************************************




