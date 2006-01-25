# MG_JEN_Sixpack.py

# Short description (see also the full description below):
#   A template for the generation of MeqGraft (MG) scripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 20 oct 2005: introduced Sixpack object
# - 20 jan 2006: introduced Parmset

# Copyright: The MeqTree Foundation

# Full description (try to be complete, and up-to-date!):


   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq

MG = record(script_name='MG_JEN_Sixpack.py', last_changed = 'h22sep2005')

from Timba import utils
# _dbg = utils.verbosity(0, name='tutorial')
# _dprint = _dbg.dprint                         # use: _dprint(2, "abc")
# _dprintf = _dbg.dprintf                       # use: _dprintf(2, "a = %d", a)
# run the script with: -dtutorial=3
# level 0 is always printed

from numarray import *
# from string import *
# from copy import deepcopy

# Scripts needed to run a MG_JEN script: 
from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state

# Other MG_JEN scripts (uncomment as necessary):
# NB: Also browse the list of other available scripts!

from Timba.Trees import TDL_Sixpack
from Timba.Trees import TDL_Parmset
from Timba.Trees import TDL_Leaf
from Timba.Trees import JEN_inarg

from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_matrix
# from Timba.Contrib.JEN import MG_JEN_twig




#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...
# See MG_JEN_forest_state.py

MG_JEN_forest_state.init(MG.script_name)






#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************

# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.


def _define_forest (ns):
   """Definition of a MeqForest for demonstration/testing/experimentation
   of the subject of this MG script, and its importable functions"""

   # Perform some common functions, and return an empty list (cc=[]):
   cc = MG_JEN_exec.on_entry (ns, MG)

   group = dict()
   group['basic'] = ['unpol','Qonly','Uonly','Vonly']
   group['combi'] = ['QU','QUV','QU2']
   group['test'] = ['RMtest','SItest']
   group['3c'] = ['3c147','3c48','3c286','3c295']

   # Sixpack['default'] = newstar_source (ns)
   # Sixpack['QUV_RM_SI'] = newstar_source (ns, name='QUV', RM=1, SI=-0.7)

   radec = []
   for key in group.keys():
      ss = []
      for predef in group[key]:
         Sixpack = newstar_source (ns, name=predef)
         bb = []
         bb.append(Sixpack.stokesI())
         bb.append(Sixpack.stokesQ())
         bb.append(Sixpack.stokesU())
         bb.append(Sixpack.stokesV())
         ss.append(MG_JEN_exec.bundle(ns, bb, predef))
         radec.append(Sixpack.ra())
         radec.append(Sixpack.dec())
      cc.append(MG_JEN_exec.bundle(ns, ss, key))
      MG_JEN_forest_state.bookfolder(key)
 
   # Collect the 'loose' RA,DEC root nodes to a single root node (more tidy):
   radec_root = ns.radec_root << Meq.Add (children=radec)


   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)
















#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************

#-----------------------------------------------------------------------------
# Standard input arguments (used e.g. by MG_JEN_Cohset.py)

def inarg_punit (pp, **kwargs):
    JEN_inarg.inarg_common(kwargs)
    choice = ['unpol','unpol2','unpol10','3c147',
              'RMtest','QUV','QU','SItest']
    JEN_inarg.define (pp, 'punit', 'unpol', choice=choice,
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      help='name of calibrator source/patch \n'+
                      '- unpol:   unpolarised, I=1Jy \n'+
                      '- unpol2:  idem, I=2Jy \n'+
                      '- unpol10: idem, I=10Jy \n'+
                      '- RMtest:  Rotation Measure \n'+
                      '- SItest:  Spectral Index \n'+
                      '- QUV:     non-zero Q,U,V \n'+
                      '- QU:      non-zero Q,U \n'+
                      '- 3c147:')
    return True

#------------------------------------------------------------------------------

def inarg_Sixpack_common (pp, **kwargs):
    """Some common JEN_inarg definitions for Joneset definition functions"""
    JEN_inarg.inarg_common(kwargs)
    JEN_inarg.define(pp, 'parmtable', None, slave=kwargs['slave'], trace=trace, 
                     help='name of the MeqParm table (AIPS++)')
    # ** Solving instructions:
    JEN_inarg.define(pp, 'unsolvable', tf=False, trace=trace, hide=True,
                     help='if True, do NOT store solvegroup/parmgroup info')
    return True


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
    pp['I0'] = 1.0
  elif (pp['name']=='unpol2'):
    pp['I0'] = 2.0
  elif (pp['name']=='unpol10'):
    pp['I0'] = 10.0
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


#---------------------------------------------------------------------
# Predefined polclog definitions of selected sources:
# From MG_JEN_funklet.py (for comparison)

def polclog_predefined (source='<source>', SI=-0.7, I0=1.0, f0=1e6, stokes='stokesI'):

   polclog = dict(stokesI=1.0, stokesQ=0.0, stokesU=0.0, stokesV=0.0)
   if source=='3c147':	
      polclog['stokesI'] = polclog_SIF (I0=10**1.766, SI=[0.447, -0.148], f0=1e6)
   elif source =='3c48':	
      polclog['stokesI'] = polclog_SIF (I0=10**2.345, SI=[0.071, -0.138], f0=1e6)
   elif source =='3c295':	
      polclog['stokesI'] = polclog_SIF (I0=10**1.485, SI=[0.759, -0.255], f0=1e6)
   elif source =='3c286':	
      polclog['stokesI'] = polclog_SIF (I0=10**1.48, SI=[0.292, -0.124], f0=1e6)
      polclog['stokesQ'] = polclog_SIF (I0=2.735732, SI=[-0.923091, 0.073638], f0=1e6)
      polclog['stokesU'] = polclog_SIF (I0=6.118902, SI=[-2.05799, 0.163173], f0=1e6)
      #    pp['I0'] = 10**1.48
      #    pp['SI'] = [0.292, -0.124]
      #    pp['Q'] = [2.735732, -0.923091, 0.073638]
      #    pp['U'] = [6.118902, -2.05799, 0.163173]
      
   else:
      # If source not recognised, use the other arguments:
      polclog['stokesI'] = polclog_SIF (SI=SI, I0=I0, f0=f0)

   print '** polclog_predefined(',source,stokes,') ->',polclog[stokes]
   return polclog[stokes]


#======================================================================
# Make a polclog for a freq-dependent spectral index:
#======================================================================

# regular polc (comparison): v(f,t) = c00 + c01.t + c10.f + c11.f.t + ....
#
# polclog:
#            I(f) = I0(c0 + c1.x + c2.x^2 + c3.x^3 + .....)
#            in which:  x = 10log(f/f0)
#
# if c2 and higher are zero:           
#            I(f) = 10^(c0 + c1.10log(f/f0)) = (10^c0) * (f/f0)^c1
#                 = I0 * (f/f0)^SI  (classical spectral index formula)
#            in which: c0 = 10log(I0)  and c1 is the classical S.I. (usually ~0.7)   
#
# so:        I(f) = 10^SIF
# NB: If polclog_SIF is to be used as multiplication factor for (Q,U,V),
#     use: fmult = ns.fmult() << Meq.Parm(polclog(SI, I0=1.0), i.e. SIF[0] = 0.0)



def polclog_SIF (I0=1.0, SI=-0.7, f0=1e6):
   SIF = [log(I0)/log(10)]                               # SIF[0] = 10log(I0). (Python log() is e-log)
   # NB: what if I0 is polc???
   if not isinstance(SI, list): SI = [SI]
   SIF.extend(SI)                                             # NB: SIF[1] = classical S.I.
   SIF = array(SIF)
   SIF = reshape(SIF, (1,len(SIF)))               # freq coeff only....
   polclog = meq.polclog(SIF)                        # NB: the default f0 = 1Hz!
   polclog.axis_list = record(freq=f0)                # the default is f0=1Hz
   # print oneliner(polclog, 'polclog_SIF')
   return polclog

#    if len(SI) == 1:
#       print type(ns)
#       parm['I0'] = (ns.I0(q=pp['name']) << Meq.Parm(pp['I0']))
#       parm['SI'] = (ns.SI(q=pp['name']) << Meq.Parm(pp['SI']))
#       freq = (ns.freq << Meq.Freq())
#       fratio = (ns.fratio(q=pp['name']) << (freq/pp['f0']))
#       fmult = (ns.fmult(q=pp['name']) << Meq.Pow(fratio, parm['SI']))
#       iquv[n6.I] = (ns[n6.I](q=pp['name']) << (parm['I0'] * fmult))


#---------------------------------------------------------------------
# Make a StokesI(q=source) node based on a polclog:

def polclog_flux (ns, source=None, I0=1.0, SI=-0.7, f0=1e6, stokes='stokesI'):
   # print
   source = MG_JEN_forest_state.autoqual('MG_JEN_funklet_flux', qual=source)

   polclog = polclog_predefined(source, I0=I0, SI=SI, f0=f0, stokes=stokes)
   SIF = ns['SIF_'+stokes](q=source) << Meq.Parm(polclog)
   node = ns[stokes](q=source) << Meq.Pow(10.0, SIF)
   # print '** polclog_flux(',source,') ->',SIF,'->',node
   return node

#---------------------------------------------------------------------
# Make a fmult(q=source) node based on a polclog:
# This may be used to multiply StokesQ,U,V.....

def polclog_fmult (ns, source=None, SI=-0.7, f0=1e6):
   source = MG_JEN_forest_state.autoqual('MG_JEN_funklet_fmult', qual=source)
      
   polclog = polclog_predefined(source, I0=1.0, SI=SI, f0=f0, stokes='stokesI')
   SIF = ns.SIF(q=source) << Meq.Parm(polclog)
   node = ns.mult(q=source) << Meq.Pow(10.0, SIF)
   # node = ns << Meq.Pow(10.0, SIF)               # <--- better?
   # print '** polclog_fmult(',source,') ->',SIF,'->',node
   return node
   






#=======================================================================================
#=======================================================================================
#=======================================================================================
# Make Sixpack of subtrees for sources with 'NEWSTAR' parametrization:
#=======================================================================================


def newstar_source (ns=0, **pp):
   """Make a Sixpack for a source with NEWSTAR parametrisation"""

   # Deal with input parameters (pp):
   pp.setdefault('name', 'cps')        # source name
   inarg_Sixpack_common(pp)            # solvable, parmtable etc
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
   pp.setdefault('fsr_trace', True)    # if True, attach to forest state record
  
   # Adjust parameters pp for some special cases:
   predefined (pp)  

   # Make the Sixpack and get its Parmset object:
   punit = pp['name']
   Sixpack = TDL_Sixpack.Sixpack(label=punit, **pp)
   # Sixpack.display()
   pset = Sixpack.Parmset 
   
   # Register the parmgroups:
   sI = pset.parmgroup('stokesI', color='red', style='diamond', size=10,
                       rider=dict(condeq_corrs='corrI'))
   sQ = pset.parmgroup('stokesQ', color='blue', style='diamond', size=10,
                       rider=dict(condeq_corrs='corrQ'))
   sU = pset.parmgroup('stokesU', color='magenta', style='diamond', size=10, 
                       rider=dict(condeq_corrs='corrU'))
   sV = pset.parmgroup('stokesV', color='cyan', style='diamond', size=10, 
                       rider=dict(condeq_corrs='corrV'))
   pg_radec = pset.parmgroup('radec', color='black', style='circle', size=10, 
                       rider=dict(condeq_corrs='corrI'))                       # <----- ?
   
   # MeqParm node_groups: add 'S' to default 'Parm':
   pset.node_groups('S')
   
   # Define extra solvegroup(s) from combinations of parmgroups:
   pset.define_solvegroup('stokesIQUV', [sI,sQ,sU,sV])
   pset.define_solvegroup('stokesIQU', [sI,sQ,sU])
   pset.define_solvegroup('stokesQU', [sQ,sU])

   # Make the Sixpack of 6 standard subtree root-nodes: 
   n6 = record(I='stokesI', Q='stokesQ', U='stokesU', V='stokesV', R='ra', D='dec') 
   zero = ns.zero << Meq.Constant(0)
   
   iquv = {}
   parm = {}
   fmult = 1.0
   if pp['SI'] is None:
      parm['I0'] = pset.define_MeqParm (ns, 'I0', parmgroup=sI, default=pp['I0'])
      iquv[n6.I] = parm['I0']
   else:
      polclog = polclog_SIF (SI=pp['SI'], I0=pp['I0'], f0=pp['f0'])
      parm['SIF'] = pset.define_MeqParm (ns, 'SIF_stokesI', parmgroup=sI, default=polclog)
      iquv[n6.I] = ns['stokesI'](q=punit) << Meq.Pow(10.0, parm['SIF'])
      # fmult = ...??

   # Create Stokes V by converting Vpct and correcting for SI if necessary
   iquv[n6.V] = zero
   if pp['Vpct'] is not None:
      parm['Vpct'] = pset.define_MeqParm (ns, 'Vpct', parmgroup=sV, default=pp['Vpct'])
      if isinstance(fmult, float):
         iquv[n6.V] = ns[n6.V](q=punit) << (parm['Vpct']*(fmult/100))
      else:
         iquv[n6.V] = ns[n6.V](q=punit) << (parm['Vpct']*fmult/100)
    
      
   if pp['RM'] is None:
      # Without Rotation Measure:
      # Create Stokes Q by converting Qpct and correcting for SI if necessary
      iquv[n6.Q] = zero
      if pp['Qpct'] is not None:
         parm['Qpct'] = pset.define_MeqParm (ns, 'Qpct', parmgroup=sQ, default=pp['Qpct'])
         if isinstance(fmult, float):
            iquv[n6.Q] = ns[n6.Q](q=punit) << (parm['Qpct']*(fmult/100))
         else:
            iquv[n6.Q] = ns[n6.Q](q=punit) << (parm['Qpct']*fmult/100)

      # Create Stokes U by converting Upct and correcting for SI if necessary
      iquv[n6.U] = zero
      if pp['Upct'] is not None:
         parm['Upct'] = pset.define_MeqParm (ns, 'Upct', parmgroup=sU, default=pp['Upct'])
         if isinstance(fmult, float):
            iquv[n6.U] = ns[n6.U](q=punit) << (parm['Upct']*(fmult/100))
         else:
            iquv[n6.U] = ns[n6.U](q=punit) << (parm['Upct']*fmult/100)
    
   else:
      # With Rotation Measure: 
      # Create an intermediate QU = [Q,U]
      if pp['Qpct'] is None: pp['Qpct'] = 0.0
      if pp['Upct'] is None: pp['Upct'] = 0.0
      if 0:
         pass
         # NB: Some sources have polclogs for their absolute polarised flux (e.g. 3c286):
         # iquv['Q'] = MG_JEN_funklet.polclog_flux(ns, source=punit, stokes='stokesQ')
         # iquv['U'] = MG_JEN_funklet.polclog_flux(ns, source=punit, stokes='stokesU')
         # if not == 0.0, then ....
      parm['Qpct'] = pset.define_MeqParm (ns, 'Qpct', parmgroup=sQ, default=pp['Qpct'])
      parm['Upct'] = pset.define_MeqParm (ns, 'Upct', parmgroup=sU, default=pp['Upct'])
      if isinstance(fmult, float):
         Q = ns['Q'](q=punit) << (parm['Qpct']*(fmult/100))
         U = ns['U'](q=punit) << (parm['Upct']*(fmult/100))
      else:
         Q = ns['Q'](q=punit) << (parm['Qpct']*fmult/100)
         U = ns['U'](q=punit) << (parm['Upct']*fmult/100)
      QU = ns['QU'](q=punit) << Meq.Composer(children=[Q,U])  

      # Rotate QU by the RM matrix -> QURM
      parm['RM'] = pset.define_MeqParm (ns, 'RM', parmgroup=sQ, default=pp['RM'])  
      wvl2 = TDL_Leaf.MeqWavelength (ns, unop='Sqr')       
      farot = ns.farot(q=punit) << (parm['RM']*wvl2)
      rotmat = MG_JEN_matrix.rotation (ns, angle=farot)
      QURM = ns['QURM'](q=punit) << Meq.MatrixMultiply(rotmat, QU)  

      # Unpack QURM into separate StokesQ and StokesU subtrees:
      iquv[n6.Q] = ns[n6.Q](q=punit) <<  Meq.Selector(QURM, index=0)
      iquv[n6.U] = ns[n6.U](q=punit) <<  Meq.Selector(QURM, index=1)


   # Source coordinates (RA, DEC)
   radec = {}
   radec[n6.R] = pset.define_MeqParm (ns, n6.R, parmgroup=pg_radec, default=pp['RA'])  
   radec[n6.D] = pset.define_MeqParm (ns, n6.D, parmgroup=pg_radec, default=pp['Dec'])  

   # Finished: Fill the Sixpack and return it:
   Sixpack.stokesI(iquv[n6.I])
   Sixpack.stokesQ(iquv[n6.Q])
   Sixpack.stokesU(iquv[n6.U])
   Sixpack.stokesV(iquv[n6.V])
   # Sixpack.radec([iquv[n6.R],iquv[n6.D]])
   Sixpack.ra(radec[n6.R])
   Sixpack.dec(radec[n6.D])

   # Sixpack.display()
   # if pp['fsr_trace']:
   #   MG_JEN_forest_state.object(Sixpack)
   return Sixpack







#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************

# The function with the standard name _test_forest(), and any function
# with name _tdl_job_xyz(m), will show up under the 'jobs' button in
# the browser, and can be executed from there.  The 'mqs' argument is
# a meqserver proxy object.

# In the default function, the forest is executed once:
# If not explicitly supplied, a default request will be used:

def _tdl_job_default (mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent)

def _test_forest (mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent)



# The following call shows the default settings explicity:
# NB: It is also possible to give an explicit request, cells or domain
#     In addition, qualifying keywords will be used when sensible

def _tdl_job_custom(mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False) 

# There are some predefined domains:

def _tdl_job_lofar(mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')   # (100-110 MHz)

def _tdl_job_21cm(mqs, parent):
    return MG_JEN_exec.meqforest (mqs, parent, domain='21cm')    # (1350-1420 MHz)

# Execute the forest for a sequence of requests:

def _tdl_job_sequence(mqs, parent):
    for x in range(10):
        MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19,
                               f1=x, f2=x+1, t1=x, t2=x+1,
                               save=False, trace=False)
    MG_JEN_exec.save_meqforest(mqs) 
    return True






#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************

# These test routines do not require the meqbrowser, or even the meqserver.
# Just run them by enabling the required one (if 1:), and invoking python:
#      > python MG_JEN_Sixpack.py

if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()

   if 1:
      name = '3c286'
      name = '3c147'
      name = 'SItest'
      name = 'RMtest'
      unsolvable = False
      unsolvable = True
      parmtable = None
      parmtable = '<lsm-parmtable>'
      Sixpack = newstar_source (ns, name=name,
                                unsolvable=unsolvable,
                                parmtable=parmtable)
      # Sixpack = newstar_source (ns)
      # Sixpack = newstar_source (ns, name='QUV', RM=1, SI=-0.7)
      Sixpack.display()
      Sixpack.Parmset.display()
      if 0:
         Sixpack.nodescope(ns)
         MG_JEN_exec.display_subtree (Sixpack.stokesI(), 'stokesI()', full=1)
         MG_JEN_exec.display_subtree (Sixpack.sixpack(), 'sixpack()', full=1)
         MG_JEN_exec.display_subtree (Sixpack.iquv(), 'iquv()', full=1)
         MG_JEN_exec.display_subtree (Sixpack.radec(), 'radec()', full=1)

   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




