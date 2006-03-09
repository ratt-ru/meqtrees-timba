# MG_JEN_Sixpack.py

# Short description (see also the full description below):
#   A template for the generation of MeqGraft (MG) scripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 20 oct 2005: introduced Sixpack object
# - 20 jan 2006: introduced Parmset
# - 09 mar 2006: introduced new ParmSet as well 

# Copyright: The MeqTree Foundation

# Full description (try to be complete, and up-to-date!):


   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preamble *********************************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
from Timba.Meq import meq


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

from Timba.LSM.LSM import *
from Timba.LSM.LSM_GUI import *

from Timba.Trees import TDL_common
from Timba.Trees import TDL_Sixpack
from Timba.Trees import TDL_Parmset
from Timba.Trees import TDL_ParmSet
from Timba.Trees import TDL_Leaf
from Timba.Trees import JEN_inarg

from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_matrix
# from Timba.Contrib.JEN import MG_JEN_twig



















#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************

#-----------------------------------------------------------------------------
# Standard input arguments (used e.g. by MG_JEN_Cohset.py)

def inarg_punit (pp, **kwargs):
    """Definition of inarg input argument punit""" 
    JEN_inarg.inarg_common(kwargs)
    choice = ['unpol','unpol2','unpol10',
              'QUV','QU','Qonly','Uonly','Vonly',
              '3c147','3c286','3c48','3c295',
              'RMtest','SItest']
    JEN_inarg.define (pp, 'punit', 'unpol', choice=choice,
                      slave=kwargs['slave'], hide=kwargs['hide'],
                      callback=True,
                      help='name of calibrator source/patch \n'+
                      '- unpol:   unpolarised, I=1Jy \n'+
                      '- unpol2:  idem, I=2Jy \n'+
                      '- unpol10: idem, I=10Jy \n'+
                      '- RMtest:  Rotation Measure \n'+
                      '- SItest:  Spectral Index \n'+
                      '- QUV:     non-zero Q,U,V \n'+
                      '- QU:      non-zero Q,U \n'+
                      '- QU2:     stronger version of QU \n'+
                      '- Qonly:   non-zero Q \n'+
                      '- Uonly:   non-zero U \n'+
                      '- Vonly:   non-zero V \n'+
                      '- 3c286:   \n'+
                      '- 3c48:    \n'+
                      '- 3c295:   \n'+
                      '- 3c147:   \n'+
                      '')

    # Optional: Specify an LSM to get the Sixpack from:
    JEN_inarg.define (pp, 'from_LSM', None, browse='*.lsm', hide=False,
                      help='(file)name of a Local Sky Model to be used'+
                      '(instead of a predefined punit)')

    # Upward compatibility (temporary).
    # name has been changed into punit on friday 10 feb 2006....
    JEN_inarg.define (pp, 'name', None, hide=True)
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
    """Some sources are defined by their name (punit)"""
    # NB: It is assumed that none of their source parameters are explicitly specified!
    if (pp['punit']=='3c147'):
       predefined_reset(pp) 
       pp['I0'] = 10**1.766
       pp['SI'] = [0.447, -0.184]
    elif (pp['punit']=='3c48'):
       predefined_reset(pp) 
       pp['I0'] = 10**2.345
       pp['SI'] = [0.071, -0.138]
    elif (pp['punit']=='3c286'): 
       predefined_reset(pp) 
       pp['I0'] = 10**1.48
       pp['SI'] = [0.292, -0.124]
       pp['Q'] = [2.735732, -0.923091, 0.073638]         # <-----
       pp['U'] = [6.118902, -2.05799, 0.163173]          # <-----
    elif (pp['punit']=='3c295'):
       predefined_reset(pp) 
       pp['I0'] = 10**1.485
       pp['SI'] = [0.759, -0.255]
    elif (pp['punit']=='unpol'):
       predefined_reset(pp) 
       pp['I0'] = 1.0
    elif (pp['punit']=='unpol2'):
       predefined_reset(pp) 
       pp['I0'] = 2.0
    elif (pp['punit']=='unpol10'):
       predefined_reset(pp) 
       pp['I0'] = 10.0
    elif (pp['punit']=='Qonly'):
       predefined_reset(pp) 
       pp['Qpct'] = 10
    elif (pp['punit']=='Uonly'):
       predefined_reset(pp) 
       pp['Upct'] = -10
    elif (pp['punit']=='Vonly'):
       predefined_reset(pp) 
       pp['Vpct'] = 2                            
    elif (pp['punit']=='QU'):
       predefined_reset(pp) 
       pp['Qpct'] = 10
       pp['Upct'] = -10
    elif (pp['punit']=='QUV'):
       predefined_reset(pp) 
       pp['Qpct'] = 10
       pp['Upct'] = -10
       pp['Vpct'] = 2
    elif (pp['punit']=='QU2'):
       predefined_reset(pp) 
       pp['I0'] = 2.0
       pp['Qpct'] = 40
       pp['Upct'] = -30
    elif (pp['punit']=='RMtest'):
       predefined_reset(pp) 
       pp['RM'] = 1.0
       pp['Qpct'] = 10
       pp['Upct'] = -10
    elif (pp['punit']=='SItest'):
       predefined_reset(pp) 
       pp['SI'] = -0.7
    elif (pp['punit']=='I0polc'):
       predefined_reset(pp) 
       pp['I0'] = array([[2,-.3,.1],[.3,-.1,0.03]]),

    else:
       # If punit not recognised, pp is not changed at all:
       pass

    if trace: print '\n** predefined() -> pp =',TDL_common.unclutter_inarg(pp),'\n'
    return 

#--------------------------------------------------------------------

def predefined_reset(pp):
    """Reset some of the pp fields to a known state.
    This is used for all recognised punits in predefined()"""
    pp.setdefault('I0', 1.0) 
    pp.setdefault('Qpct', None) 
    pp.setdefault('Upct', None) 
    pp.setdefault('Vpct', None) 
    pp.setdefault('RM', None) 
    pp.setdefault('SI', None) 
    return True


#--------------------------------------------------------------------

def predefined_inarg (punit='unpol'):
    """Make a predefined inarg for a specific punit (source)"""
    pp = dict(punit=punit)
    predefined (pp)
    print 'predefined(pp) ->',pp
    inarg = newstar_source(_getdefaults=True)
    JEN_inarg.modify(inarg, **pp)
    return inarg

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
#       parm['I0'] = (ns.I0(q=pp['punit']) << Meq.Parm(pp['I0']))
#       parm['SI'] = (ns.SI(q=pp['punit']) << Meq.Parm(pp['SI']))
#       freq = (ns.freq << Meq.Freq())
#       fratio = (ns.fratio(q=pp['punit']) << (freq/pp['f0']))
#       fmult = (ns.fmult(q=pp['punit']) << Meq.Pow(fratio, parm['SI']))
#       iquv[n6.I] = (ns[n6.I](q=pp['punit']) << (parm['I0'] * fmult))


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


def newstar_source (ns=0, predefine=False, **inarg):
   """Make a Sixpack (I,Q,U,V,Ra,Dec) for a source with NEWSTAR parametrisation"""

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Sixpack::newstar_source()', version='10feb2006',
                           description=newstar_source.__doc__)
   inarg_punit (pp)
   inarg_Sixpack_common(pp)            # solvable, parmtable etc
   JEN_inarg.define(pp, 'I0', 1.0, choice=[1.0, 10.0],  
                    help='Stokes I: Total intensity @ f=f0 (usually 1 MHz)')
   JEN_inarg.define(pp, 'Qpct', None, choice=[None, 0.1, -0.05, 0.01],  
                    help='Stokes Q (percentage of I)')
   JEN_inarg.define(pp, 'Upct', None, choice=[None, -0.1, 0.05, -0.01],  
                    help='Stokes U (percentage of I)')
   JEN_inarg.define(pp, 'Vpct', None, choice=[None, 0.01, -0.005, 0.001],  
                    help='Stokes V (percentage of I)')
   JEN_inarg.define(pp, 'RM', None, choice=[1.0,3.0,10.0,-10.0,60.0],  
                    help='Intrinsic Rotation Measure (rad/m2)')
   help = """Spectral Index (generalised)
   A scalar represents the classical SI: I(f)=I0*(f/f0)^SI
   A vector represents a freq-dependent SI (....)"""
   JEN_inarg.define(pp, 'SI', None,
                    choice=[None,-0.7,[0.447, -0.184]],
                    help=help)
   JEN_inarg.define(pp, 'f0', 1e6, choice=[1e6], hide=True,
                    help='reference freq (Hz): I=I0 @ f=f0')
   # NB: (4.357,1.092) are the coordinates of 3c343...
   JEN_inarg.define(pp, 'RA', 4.357, choice=[0.0,0.5,1.0,4.357],  
                    help='Right Ascension (rad, J2000)')
   JEN_inarg.define(pp, 'Dec', 1.092, choice=[0.5,1.0,1.0920],  
                    help='Declination (rad, J2000)')
   JEN_inarg.define(pp, 'fsr_trace', tf=True, hide=True,   
                    help='If True, attach to forest state record')

   # Non-point sources:
   JEN_inarg.define(pp, 'shape', 'point', hide=True,
                    choice=['point','ell.gauss'],  
                    help='source shape')
   JEN_inarg.define(pp, 'major', 0.0, choice=[1.0,10.0,100.0], hide=True,
                    help='major axis (arcsec)')
   JEN_inarg.define(pp, 'minor', 0.0, choice=[0.5,5.0,50.0], hide=True, 
                    help='minor axis (arcsec)')
   JEN_inarg.define(pp, 'pa', 0.0, choice=[0.0,1.0,-0.5], hide=True,  
                    help='position angle (rad)')

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)

   # Upward compatibility (temporary)
   JEN_inarg.obsolete (pp, old='name', new='punit')

   # Hidden option: If a LSM (file) is specified, return the Sixpack
   # that represents the brightest object:
   if pp['from_LSM']:
       print '\n**',funcname,': from_LSM =',pp['from_LSM']
       lsm = LSM()
       lsm.load(pp['from_LSM'],ns)
       plist = lsm.queryLSM(count=1)
       print '\n** plist =',type(plist),len(plist)
       punit = plist[0]                     # take the first (the brightest)
       Sixpack = punit.getSP()              # better: get_Sixpack()
       Sixpack.display(funcname)
       return Sixpack
  
   # Adjust parameters pp for some special cases:
   # NB: Normally disabled, to allow customisation via inargGui....
   #     But may be invoked for testing (see below)
   if predefine:
       predefined (pp, trace=True)  

   # Make the Sixpack and get its Parmset object:
   punit = pp['punit']
   Sixpack = TDL_Sixpack.Sixpack(label=punit, **pp)
   # Sixpack.display()
   pset = Sixpack.Parmset              # old (to be removed eventually)
   ParmSet = Sixpack.ParmSet           # new
   
   if True:
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
       # NB A solvegroup is automatically creates for each parmgroup (e.g. stokesI)
       pset.solvegroup('stokesIQUV', [sI,sQ,sU,sV])
       pset.solvegroup('stokesIQU', [sI,sQ,sU])
       pset.solvegroup('stokesIV', [sI,sV])
       pset.solvegroup('stokesQU', [sQ,sU])
       pset.solvegroup('stokesQUV', [sQ,sU,sV])

   # Register the parmgroups:
   sI = ParmSet.parmgroup('stokesI', color='red', style='diamond', size=10,
                       rider=dict(condeq_corrs='corrI'))
   sQ = ParmSet.parmgroup('stokesQ', color='blue', style='diamond', size=10,
                       rider=dict(condeq_corrs='corrQ'))
   sU = ParmSet.parmgroup('stokesU', color='magenta', style='diamond', size=10, 
                       rider=dict(condeq_corrs='corrU'))
   sV = ParmSet.parmgroup('stokesV', color='cyan', style='diamond', size=10, 
                       rider=dict(condeq_corrs='corrV'))
   pg_radec = ParmSet.parmgroup('radec', color='black', style='circle', size=10, 
                       rider=dict(condeq_corrs='corrI'))                       # <----- ?
   
   # MeqParm node_groups: add 'S' to default 'Parm':
   ParmSet.node_groups('S')
   
   # Define extra solvegroup(s) from combinations of parmgroups:
   # NB A solvegroup is automatically creates for each parmgroup (e.g. stokesI)
   ParmSet.solvegroup('stokesIQUV', [sI,sQ,sU,sV])
   ParmSet.solvegroup('stokesIQU', [sI,sQ,sU])
   ParmSet.solvegroup('stokesIV', [sI,sV])
   ParmSet.solvegroup('stokesQU', [sQ,sU])
   ParmSet.solvegroup('stokesQUV', [sQ,sU,sV])

   # Make the Sixpack of 6 standard subtree root-nodes: 
   n6 = record(I='stokesI', Q='stokesQ', U='stokesU', V='stokesV', R='ra', D='dec') 
   # zero = ns.zero << Meq.Constant(0)
   
   iquv = {}
   parm = {}
   fmult = 1.0
   if pp['SI']==None:
      parm['I0'] = pset.define_MeqParm (ns, 'I0', parmgroup=sI, default=pp['I0'])
      parm['I0'] = ParmSet.MeqParm (ns, 'I0', parmgroup=sI, default=pp['I0'])
      iquv[n6.I] = parm['I0']
      fmult = iquv[n6.I]               
   else:
      polclog = polclog_SIF (SI=pp['SI'], I0=pp['I0'], f0=pp['f0'])
      print 'polclog =',polclog
      parm['SIF'] = pset.define_MeqParm (ns, 'SIF_stokesI', parmgroup=sI,
                                         init_funklet=polclog)
      parm['SIF'] = ParmSet.MeqParm (ns, 'SIF_stokesI', parmgroup=sI,
                                     init_funklet=polclog)
      iquv[n6.I] = ns['stokesI'](q=punit) << Meq.Pow(10.0, parm['SIF'])
      # fmult = ...??

   # Create Stokes V by converting Vpct and correcting for SI if necessary
   if pp['Vpct']==None:
       # iquv[n6.V] = zero
       iquv[n6.V] = ns[n6.V](q=punit) << Meq.Parm(0.0)
   else:
      parm['Vpct'] = pset.define_MeqParm (ns, 'Vpct', parmgroup=sV, default=pp['Vpct'])
      parm['Vpct'] = ParmSet.MeqParm (ns, 'Vpct', parmgroup=sV, default=pp['Vpct'])
      if isinstance(fmult, float):
         iquv[n6.V] = ns[n6.V](q=punit) << (parm['Vpct']*(fmult/100))
      else:
         iquv[n6.V] = ns[n6.V](q=punit) << (parm['Vpct']*fmult/100)
    
      
   if pp['RM']==None:
      # Without Rotation Measure:
      # Create Stokes Q by converting Qpct and correcting for SI if necessary
      if pp['Qpct']==None:
          # iquv[n6.Q] = zero
          iquv[n6.Q] = ns[n6.Q](q=punit) << Meq.Parm(0.0)
      else:
         parm['Qpct'] = pset.define_MeqParm (ns, 'Qpct', parmgroup=sQ, default=pp['Qpct'])
         parm['Qpct'] = ParmSet.MeqParm (ns, 'Qpct', parmgroup=sQ, default=pp['Qpct'])
         if isinstance(fmult, float):
            iquv[n6.Q] = ns[n6.Q](q=punit) << (parm['Qpct']*(fmult/100))
         else:
            iquv[n6.Q] = ns[n6.Q](q=punit) << (parm['Qpct']*fmult/100)

      # Create Stokes U by converting Upct and correcting for SI if necessary
      if pp['Upct']==None:
          # iquv[n6.U] = zero
          iquv[n6.U] = ns[n6.U](q=punit) << Meq.Parm(0.0)
      else:
         parm['Upct'] = pset.define_MeqParm (ns, 'Upct', parmgroup=sU, default=pp['Upct'])
         parm['Upct'] = ParmSet.MeqParm (ns, 'Upct', parmgroup=sU, default=pp['Upct'])
         if isinstance(fmult, float):
            iquv[n6.U] = ns[n6.U](q=punit) << (parm['Upct']*(fmult/100))
         else:
            iquv[n6.U] = ns[n6.U](q=punit) << (parm['Upct']*fmult/100)
    
   else:
      # With Rotation Measure: 
      # Create an intermediate QU = [Q,U]
      if pp['Qpct']==None:
          pp['Qpct'] = 0.0
      if pp['Upct']==None:
          pp['Upct'] = 0.0
      if False:
         pass
         # NB: Some sources have polclogs for their absolute polarised flux (e.g. 3c286):
         # iquv['Q'] = MG_JEN_funklet.polclog_flux(ns, source=punit, stokes='stokesQ')
         # iquv['U'] = MG_JEN_funklet.polclog_flux(ns, source=punit, stokes='stokesU')
         # if not == 0.0, then ....
      parm['Qpct'] = pset.define_MeqParm (ns, 'Qpct', parmgroup=sQ, default=pp['Qpct'])
      parm['Upct'] = pset.define_MeqParm (ns, 'Upct', parmgroup=sU, default=pp['Upct'])
      parm['Qpct'] = ParmSet.MeqParm (ns, 'Qpct', parmgroup=sQ, default=pp['Qpct'])
      parm['Upct'] = ParmSet.MeqParm (ns, 'Upct', parmgroup=sU, default=pp['Upct'])
      if isinstance(fmult, float):
         Q = ns['Q'](q=punit) << (parm['Qpct']*(fmult/100))
         U = ns['U'](q=punit) << (parm['Upct']*(fmult/100))
      else:
         Q = ns['Q'](q=punit) << (parm['Qpct']*fmult/100)
         U = ns['U'](q=punit) << (parm['Upct']*fmult/100)
      QU = ns['QU'](q=punit) << Meq.Composer(children=[Q,U])  

      # Rotate QU by the RM matrix -> QURM
      parm['RM'] = pset.define_MeqParm (ns, 'RM', parmgroup=sQ, default=pp['RM'])  
      parm['RM'] = ParmSet.MeqParm (ns, 'RM', parmgroup=sQ, default=pp['RM'])  
      wvl2 = TDL_Leaf.MeqWavelength (ns, unop='Sqr')       
      farot = ns.farot(q=punit) << (parm['RM']*wvl2)
      rotmat = MG_JEN_matrix.rotation (ns, angle=farot)
      QURM = ns['QURM'](q=punit) << Meq.MatrixMultiply(rotmat, QU)  

      # Unpack QURM into separate StokesQ and StokesU subtrees:
      iquv[n6.Q] = ns[n6.Q](q=punit) <<  Meq.Selector(QURM, index=0)
      iquv[n6.U] = ns[n6.U](q=punit) <<  Meq.Selector(QURM, index=1)


   # Source coordinates (RA, DEC)
   radec = {}
   radec[n6.R] = pset.define_MeqParm (ns, n6.R, qual=dict(q=punit),
                                      parmgroup=pg_radec, default=pp['RA'])  
   radec[n6.D] = pset.define_MeqParm (ns, n6.D, qual=dict(q=punit),
                                      parmgroup=pg_radec, default=pp['Dec'])  
   radec[n6.R] = ParmSet.MeqParm (ns, n6.R, qual=dict(q=punit),
                                  parmgroup=pg_radec, default=pp['RA'])  
   radec[n6.D] = ParmSet.MeqParm (ns, n6.D, qual=dict(q=punit),
                                  parmgroup=pg_radec, default=pp['Dec'])  

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



#------------------------------------------------------------------------------------

def make_bundle(ns, Sixpack, radec=None):
   """Make a bundle of the I,Q,U,V nodes of the given Sixpack"""
   bb = []
   bb.append(Sixpack.stokesI())
   bb.append(Sixpack.stokesQ())
   bb.append(Sixpack.stokesU())
   bb.append(Sixpack.stokesV())
   if radec: collect_radec(radec, Sixpack)
   return ns[Sixpack.label()] << Meq.Composer(children=bb)


def make_bookmark(ns, Sixpack, radec=None):
   """Make a bookmark of the I,Q,U,V nodes of the given Sixpack"""
   bb = []
   bb.append(Sixpack.stokesI())
   bb.append(Sixpack.stokesQ())
   bb.append(Sixpack.stokesU())
   bb.append(Sixpack.stokesV())
   if radec: collect_radec(radec, Sixpack)
   return MG_JEN_exec.bundle(ns, bb, Sixpack.label())


def collect_radec(radec=[], Sixpack=None, ns=None):
   """Tie RA,Dec nodes to a single radec_root node (to avoid browser clutter)"""
   if Sixpack:
      radec.append(Sixpack.ra())
      radec.append(Sixpack.dec())
   if ns:
      ns._radec_root << Meq.Add (children=radec)
   return True













#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

def description ():
    """MG_JEN_Sixpack.py makes source Sixpacks"""
    return True


#----------------------------------------------------------------------------------------------------
# Intialise the MG control record with some overall arguments 
#----------------------------------------------------------------------------------------------------

MG = JEN_inarg.init('MG_JEN_Sixpack', description=description.__doc__)
JEN_inarg.define (MG, 'last_changed', 'd12feb2006', editable=False)


#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...
# See MG_JEN_forest_state.py

MG_JEN_forest_state.init(MG)








#********************************************************************************
#********************************************************************************
#**************** PART III: Required test/demo function *************************
#********************************************************************************
#********************************************************************************


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
   # Sixpack['QUV_RM_SI'] = newstar_source (ns, punit='QUV', RM=1, SI=-0.7)

   radec = []
   for key in group.keys():
      ss = []
      for predef in group[key]:
         Sixpack = newstar_source (ns, predefine=True, punit=predef)
         ss.append(make_bookmark(ns, Sixpack))
         collect_radec(radec, Sixpack)
      cc.append(MG_JEN_exec.bundle(ns, ss, key))
      MG_JEN_forest_state.bookfolder(key)
      # JEN_bookmarks.bookfolder(key)
 
   # Make the radec_root node:
   collect_radec(radec, ns=ns)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)







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

# def _tdl_job_default (mqs, parent):
#    return MG_JEN_exec.meqforest (mqs, parent)

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
   print '\n*******************\n** Local test of:',MG['script_name'],':\n'
   from Timba.Trees import JEN_inargGui

   # Generic test:
   if 0:
       MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest, recurse=3)

   # Various specific tests:
   ns = NodeScope()
   Sixpack = None

   if 1:
      punit = '3c286'
      punit = '3c147'
      punit = 'RMtest'
      punit = 'unpol'
      punit = 'SItest'
      unsolvable = False
      # unsolvable = True
      parmtable = None
      # parmtable = '<lsm-parmtable>'
      Sixpack = newstar_source (ns, predefine=True,
                                punit=punit, 
                                unsolvable=unsolvable,
                                parmtable=parmtable)
      # Sixpack = newstar_source (ns)
      # Sixpack = newstar_source (ns, punit='QUV', RM=1, SI=-0.7)
      Sixpack.display()
      Sixpack.Parmset.display()
      Sixpack.ParmSet.display()

   if 0:
      inarg = predefined_inarg(punit='QU')
      igui = JEN_inargGui.ArgBrowser()
      igui.input(inarg)
      igui.launch()

   if 0:
      inarg = newstar_source(_getdefaults=True)
      JEN_inarg.modify(inarg,
                       RA0=(ns.RA0 << 1.2),
                       Dec0=(ns.Dec0 << 1.3),
                       dRA=9.5,
                       dDec=-11.7)
      Sixpack = newstar_source(ns, _inarg=inarg)
      Sixpack.display()

   if 0:
      Sixpack.nodescope(ns)
      MG_JEN_exec.display_subtree (Sixpack.radec(), 'radec()', full=1)

   if 0:
      Sixpack.nodescope(ns)
      MG_JEN_exec.display_subtree (Sixpack.stokesI(), 'stokesI()', full=1)
      MG_JEN_exec.display_subtree (Sixpack.sixpack(), 'sixpack()', full=1)
      MG_JEN_exec.display_subtree (Sixpack.iquv(), 'iquv()', full=1)


   print '\n** End of local test of:',MG['script_name'],'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




