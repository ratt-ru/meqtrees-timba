# MG_JEN_Joneset.py

# Short description:
#   Functions dealing with a set (joneset) of 2x2 station Jones matrices

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 31 aug 2005: added .visualise()
# - 05 sep 2005: adapted to Joneset object
# - 07 dec 2005: introduced define_MeqParm() argument 'constrain'
# - 10 dec 2005: make the functions inarg-compatible
# - 02 jan 2006: converted to TDL_Parmset.py
# - 07 dec 2005: removed define_MeqParm() argument 'constrain' again
# - 07 dec 2005: introduced Parmset.define_condeq()
# - 10 jan 2006: tile_size -> subtile_size
# - 10 jan 2006: pp.setdefault() -> JEN_inarg.define(pp)
# - 11 jan 2006: KJones with MSauxinfo
# - 20 jan 2006: new TDL_Parmset.py
# - 02 feb 2006: removed punit from the input arguments (use Sixpack)
# - 05 feb 2006: Introduced keyword 'uv_plane_effect'
# - 14 feb 2006: Implemented DJones
# - 24 feb 2006: DJones -> JJones
# - 25 feb 2006: included simul (Leafset etc)
# - 09 mar 2006: adopted TDL_ParmSet

# Copyright: The MeqTree Foundation 




#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *
# from Timba.Meq import meq

from numarray import *

from Timba.Trees import JEN_inarg
from Timba.Trees import TDL_Joneset
# from Timba.Trees import TDL_Parmset          # via TDL_Joneset.py
from Timba.Trees import TDL_Leafset     
from Timba.Trees import TDL_LeafSet     
from Timba.Trees import TDL_radio_conventions

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_matrix
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_dataCollect
from Timba.Contrib.JEN import MG_JEN_Sixpack












#********************************************************************************
#********************************************************************************
#******************** PART II: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


#--------------------------------------------------------------------------------
# Adjust the input arguments (pp) for telescope (dangerous?):

def adjust_for_telescope(pp, origin='<origin>'):
   #------------------------
   return False # inhibited!
   #------------------------
   if not isinstance(pp, dict): return False
   # pp = record(pp)

   if not pp.has_key('telescope'): pp['telescope'] = 'WSRT'

   if pp['telescope']=='WSRT':
      pp['polrep'] = 'linear'

   elif pp['telescope']=='VLA':
      pp['polrep'] = 'circular'

   elif pp['telescope']=='ATCA':
      pp['polrep'] = 'linear'

   elif pp['telescope']=='GMRT':
      pp['polrep'] = 'linear'

   elif pp['telescope']=='VLBI':
      pp['polrep'] = 'circular'

   else:
      return False
   return True
      




#--------------------------------------------------------------------------------
# Common input arguments (move to TDL_Joneset.py?)
#--------------------------------------------------------------------------------

def inarg_Joneset_common (pp, jones=None, **kwargs):
   """Some common JEN_inarg definitions for Joneset definition functions"""
   JEN_inarg.inarg_common(kwargs)
   inarg_stations(pp, **kwargs)
   inarg_polrep(pp, **kwargs)
   JEN_inarg.define(pp, '@Jsequence', jones, hide=True,
                    help='list membership indication (used in JEN_inargGui)')
   return True


def inarg_stations (pp, **kwargs):
   """Some common JEN_inarg definitions for Joneset definition functions"""
   JEN_inarg.inarg_common(kwargs)
   JEN_inarg.define (pp, 'stations', range(5),
                     slave=kwargs['slave'], hide=kwargs['hide'],
                     choice=[range(7),range(14),range(15),'range(5)'],
                     help='the (subset of) stations to be used')
   return True


def inarg_polrep (pp, **kwargs):
   """Some common JEN_inarg definitions for Joneset definition functions"""
   JEN_inarg.inarg_common(kwargs)
   JEN_inarg.define(pp, 'polrep', 'linear', choice=['linear','circular'],
                    slave=kwargs['slave'], hide=kwargs['hide'],
                    help='polarisation representation')
   return True


#------------------------------------------------------------------------------

def inarg_Joneset_Parmset (pp, **kwargs):
   """Semi-obsolete"""
   return inarg_Joneset_ParmSet (pp, **kwargs)

def inarg_Joneset_ParmSet (pp, **kwargs):
   """Some common JEN_inarg definitions for Joneset definition functions"""
   JEN_inarg.inarg_common(kwargs)
   JEN_inarg.define(pp, 'parmtable', None, slave=kwargs['slave'], trace=trace,
                    choice=[None,'test'],
                    help='name of the MeqParm table to be used')
   inarg_uvplane_effect(pp, **kwargs)
   # JEN_inarg.define(pp, 'ft_coeff_scale', 0.0, trace=trace, hide=True,
   #                 help='scale of polc_ft non-c00 coeff')
   return True

#------------------------------------------------------------------------------

def inarg_uvplane_effect (pp, **kwargs):
   JEN_inarg.inarg_common(kwargs)
   kwargs.setdefault('uvplane_effect', False)
   JEN_inarg.define (pp, 'uvplane_effect', kwargs['uvplane_effect'],
                     slave=kwargs['slave'], hide=kwargs['hide'],
                     help='if True, the Joneset reprsents uv-plane effects (q=uvp)')
   return True


#------------------------------------------------------------------------------

def inarg_solvegroup (pp, **kwargs):
   """To be used by functions that call Joneset functions"""
   kwargs.setdefault('Jsequence','*')        # not yet used (for customisation)
   s_choice = []
   cond_choice = [None]
   s_default = []
   cond_default = None
   s_help = 'group (list) of parmgroups, to be solved for:'
   cond_help = '(list of) extra condition equations:'

   # Make the choice and help, depending on Jsequence:
   s_choice.extend([['GJones'],['Ggain'],['Gphase']])
   s_help += '\n- [GJones]:  all GJones MeqParms'
   s_help += '\n- [Ggain]:   GJones station gains (both pols)'
   s_help += '\n- [Gphase]:  GJones station phases (both pols)'
   s_choice.extend([['Gpol1'],['Gpol2']])
   s_help += '\n- [Gpol1]:   All GJones MeqParms for pol1 (X or R)'
   s_help += '\n- [Gpol2]:   All GJones MeqParms for pol2 (Y or L)'

   cond_choice.extend(['Gphase_X_sum=0.0','Gphase_Y_sum=0.0'])
   cond_choice.append(['Gphase_X_sum=0.0','Gphase_Y_sum=0.0'])
   cond_help += '\n- [...phase_sum=0.0]:   sum of phases = zero'
   cond_choice.append(['Gphase_X_first=0.0','Gphase_Y_first=0.0'])  
   cond_choice.append(['Gphase_X_last=0.0','Gphase_Y_last=0.0'])  
   cond_help += '\n- [...phase_first=0.0]: phase of first station = zero'
   cond_help += '\n- [...phase_last=0.0]:  phase of last station = zero'

   s_choice.append(['JJones'])
   s_choice.append(['JJones','stokesU'])
   s_choice.append(['JJones','stokesQ'])
   s_choice.append(['JJones','stokesV'])
   s_choice.append(['stokesQU','JJones'])
   s_choice.append(['stokesQUV','JJones'])
   s_help += '\n- [JJones,stokesU]:     actually solves for U!'
   s_help += '\n- [JJones,stokesQ]:     -> zero Q(?), but better freq sol(?)'
   s_help += '\n- [JJones,stokesV]:     -> punit V(?)...'

   s_choice.append(['GJones','stokesI'])
   s_choice.extend([['stokesI'],['stokesIQU'],['stokesIQUV']])
   s_choice.extend([['stokesIV'],['stokesQU'],['stokesQUV']])
   s_help += '\n- [stokesI]:    stokes I (incl SI(f), if relevant)'
   s_help += '\n- [stokesIQU]:  stokes I,Q,U (incl RM and SI(f))'
   s_help += '\n- [stokesIQUV]: stokes I,Q,U,V (incl RM and SI(f))'

   s_choice.append(['GJones','DJones'])
   s_choice.extend([['DJones'],['Dang'],['Dell']])
   cond_choice.extend(['Dang_sum=0.0'])
   cond_help += '\n- [Dang_sum=0.0]:   sum of dipole pos.angle errors = zero'
   s_choice.extend([['Dreal'],['Dimag']])
   # cond_choice.append(['Dimag_X_sum=0.0','Dimag_Y_sum=0.0'])
   # cond_choice.append(['Dreal_X_product=1.0','Dreal_Y_product=1.0'])

   s_choice.append(['GJones','DJones','FJones'])
   s_choice.extend([['FJones']])

   s_choice.append(['GJones','BJones'])
   s_choice.extend([['BJones'],['Breal'],['Bimag']])
   s_choice.extend([['Bpol1'],['Bpol2']])
   cond_choice.append(['Bimag_X_sum=0.0','Bimag_Y_sum=0.0'])
   cond_choice.append(['Breal_X_product=1.0','Breal_Y_product=1.0'])
   cond_help += '\n- [...imag_sum=0.0]:   sum of imag.parts = zero'
   cond_help += '\n- [...real_product=1.0]:   product of real.parts = unity'


   JEN_inarg.define(pp, 'solvegroup', s_default, choice=s_choice, help=s_help)
   JEN_inarg.define(pp, 'condition', cond_default, choice=cond_choice, help=cond_help)
   return True












#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
# GJones: diagonal 2x2 matrix for complex gains per polarization
#--------------------------------------------------------------------------------

def GJones (ns=None, Sixpack=None, slave=False, simul=False, **inarg):
    """Defines diagonal 2x2 Jones matrices that represent complex gain:
    Gjones(station,source) matrix elements:
    - G_11 = Ggain_X*exp(iGphase_X)
    - G_12 = 0
    - G_21 = 0
    - G_22 = Ggain_Y*exp(iGphase_Y)
    For circular polarisation, R and L are used rather than X and Y
    """

    jones = 'GJones'
    # print '\n**',jones,' simul =',simul,'\n'
    # JEN_inarg.display(inarg, jones)

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='15dec2005',
                            description=GJones.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              
    # ** Jones matrix elements:
    JEN_inarg.define(pp, 'Gpolar', tf=False,  
                     help='if True, use MeqPolar, otherwise MeqToComplex')
    
    if simul:                              # simulation mode
       # ls = TDL_Leafset.Leafset()
       ls = TDL_LeafSet.LeafSet()
       ls.inarg(pp)

    else:                                  # normal mode
       inarg_Joneset_ParmSet(pp, slave=slave)              
       # ** Solving instructions:
       JEN_inarg.define(pp, 'tdeg_Ggain', 0, choice=[0,1,2,3],  
                        help='degree of time polynomial')
       JEN_inarg.define(pp, 'tdeg_Gphase', '@tdeg_Ggain',
                        choice=[0,1,2,3,'@tdeg_Ggain'],  
                        help='degree of time polynomial')
       JEN_inarg.define(pp, 'fdeg_Ggain', 0, choice=[0,1,2,3],  
                        help='degree of freq polynomial')
       JEN_inarg.define(pp, 'fdeg_Gphase', '@fdeg_Ggain',
                        choice=[0,1,2,3,'@fdeg_Ggain'],  
                        help='degree of freq polynomial')
       JEN_inarg.define(pp, 'subtile_size_Ggain', 1,
                        choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                        help='sub-tile size (None=entire tile)')
       JEN_inarg.define(pp, 'subtile_size_Gphase', '@subtile_size_Ggain',  
                        choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                        help='sub-tile size (None=entire tile)')
       # ** MeqParm default values:
       JEN_inarg.define(pp, 'c00_Ggain', 1.0, choice=[0.9, 0.1], hide=True,  
                        help='default c00 funklet value')
       JEN_inarg.define(pp, 'c00_Gphase', 0.0, choice=[0.1], hide=True,  
                        help='default c00 funklet value')
       JEN_inarg.define(pp, 'stddev_Ggain', 0.0, choice=[0.1], hide=True,   # obsolete?
                        help='scatter in default c00 funklet values')
       JEN_inarg.define(pp, 'stddev_Gphase', 0.0, choice=[0.1], hide=True,  # obsolete?  
                        help='scatter in default c00 funklet values')
    
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)

    # JEN_inarg.display(inarg, funcname)

    label = jones+JEN_inarg.qualifier(pp)

    # Some preparations:
    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)

    # Create a Joneset object
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.display('inside GJones')
    
    # Register the parmgroups:
    a1 = js.parmgroup('Ggain', ipol=1, corrs='paral11', c00_default=1.0,
                      c00_scale=1.0, timescale_min=20, fdeg=0,
                      color='red', style='diamond', size=10, **pp)
    a2 = js.parmgroup('Ggain', ipol=2, corrs='paral22', c00_default=1.0,
                      c00_scale=1.0, timescale_min=20, fdeg=0,
                      color='blue', style='diamond', size=10, **pp)
    p1 = js.parmgroup('Gphase', ipol=1, corrs='paral11', c00_default=0.0,
                      c00_scale=1.0, timescale_min=10, fdeg=0,
                      color='magenta', style='diamond', size=10, **pp)
    p2 = js.parmgroup('Gphase', ipol=2, corrs='paral22', c00_default=0.0,
                      c00_scale=1.0, timescale_min=10, fdeg=0,
                      color='cyan', style='diamond', size=10, **pp)

    if False:
       # Define potential extra condition equations:
       js.Parmset.define_condeq(p1, unop='Add', value=0.0)
       js.Parmset.define_condeq(p1, select='first', value=0.0)
       js.Parmset.define_condeq(p1, select='last', value=0.0)
       
       js.Parmset.define_condeq(p2, unop='Add', value=0.0)
       js.Parmset.define_condeq(p2, select='first', value=0.0)
       js.Parmset.define_condeq(p2, select='last', value=0.0)
       
       js.Parmset.define_condeq(a1, unop='Multiply', value=1.0)
       js.Parmset.define_condeq(a1, select='first', value=1.0)
       js.Parmset.define_condeq(a1, select='last', value=1.0)
       
       js.Parmset.define_condeq(a2, unop='Multiply', value=1.0)
       js.Parmset.define_condeq(a2, select='first', value=1.0)
       js.Parmset.define_condeq(a2, select='last', value=1.0)
       
       # MeqParm node_groups: add 'G' to default 'Parm':
       js.Parmset.node_groups(label[0])
       
       # Define extra solvegroup(s) from combinations of parmgroups:
       js.Parmset.solvegroup('GJones', [a1, p1, a2, p2])
       js.Parmset.solvegroup('Gpol1', [a1, p1])
       js.Parmset.solvegroup('Gpol2', [a2, p2])
       js.Parmset.solvegroup('Ggain', [a1, a2])
       js.Parmset.solvegroup('Gphase', [p1, p2])
       
    
    # Define potential extra condition equations:
    js.ParmSet.define_condeq(p1, unop='Add', value=0.0)
    js.ParmSet.define_condeq(p1, select='first', value=0.0)
    js.ParmSet.define_condeq(p1, select='last', value=0.0)

    js.ParmSet.define_condeq(p2, unop='Add', value=0.0)
    js.ParmSet.define_condeq(p2, select='first', value=0.0)
    js.ParmSet.define_condeq(p2, select='last', value=0.0)

    js.ParmSet.define_condeq(a1, unop='Multiply', value=1.0)
    js.ParmSet.define_condeq(a1, select='first', value=1.0)
    js.ParmSet.define_condeq(a1, select='last', value=1.0)

    js.ParmSet.define_condeq(a2, unop='Multiply', value=1.0)
    js.ParmSet.define_condeq(a2, select='first', value=1.0)
    js.ParmSet.define_condeq(a2, select='last', value=1.0)

    # MeqParm node_groups: add 'G' to default 'Parm':
    js.ParmSet.node_groups(label[0])

    # Define extra solvegroup(s) from combinations of parmgroups:
    js.ParmSet.solvegroup('GJones', [a1, p1, a2, p2])
    js.ParmSet.solvegroup('Gpol1', [a1, p1])
    js.ParmSet.solvegroup('Gpol2', [a2, p2])
    js.ParmSet.solvegroup('Ggain', [a1, a2])
    js.ParmSet.solvegroup('Gphase', [p1, p2])

    js.bookpage('GJones', [a1, p1, a2, p2])
    
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)        
       qual = dict(s=skey)

       for Ggain in [a1,a2]:
          if simul:
             # js.Leafset.define_MeqLeaf (ns, Ggain, qual=qual, **pp)
             js.LeafSet.MeqLeaf (ns, Ggain, qual=qual, **pp)
          else:
             # default = MG_JEN_funklet.polc_ft (c00=pp['c00_Ggain'], stddev=pp['stddev_Ggain'],
             #                                  fdeg=pp['fdeg_Ggain'], tdeg=pp['tdeg_Ggain'],
             #                                  scale=pp['ft_coeff_scale']) 
             js.ParmSet.MeqParm (ns, Ggain, qual=qual,
                                 tfdeg=[pp['tdeg_Ggain'],pp['fdeg_Ggain']],
                                 subtile_size=pp['subtile_size_Ggain'])
             # js.Parmset.define_MeqParm (ns, Ggain, qual=qual,
             #                           tfdeg=[pp['tdeg_Ggain'],pp['fdeg_Ggain']],
             #                           subtile_size=pp['subtile_size_Ggain'])

       for Gphase in [p1,p2]:
          if simul:
             # js.Leafset.define_MeqLeaf (ns, Gphase, qual=qual, **pp)
             js.LeafSet.MeqLeaf (ns, Gphase, qual=qual, **pp)
          else:
             # default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gphase'], stddev=pp['stddev_Gphase'], 
             #                                  fdeg=pp['fdeg_Gphase'], tdeg=pp['tdeg_Gphase'],
             #                                  scale=pp['ft_coeff_scale']) 
             js.ParmSet.MeqParm (ns, Gphase, qual=qual,
                                 tfdeg=[pp['tdeg_Gphase'],pp['fdeg_Gphase']],
                                 subtile_size=pp['subtile_size_Gphase'])
             # js.Parmset.define_MeqParm (ns, Gphase, qual=qual,
             #                           tfdeg=[pp['tdeg_Gphase'],pp['fdeg_Gphase']],
             #                           subtile_size=pp['subtile_size_Gphase'])


       # Make the 2x2 Jones matrix:
       ss = js.buffer()
       if pp['Gpolar']:
          stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
             ns[label+'_11'](s=skey, q=pp['punit']) << Meq.Polar( ss[a1], ss[p1]),
             0,0,
             ns[label+'_22'](s=skey, q=pp['punit']) << Meq.Polar( ss[a2], ss[p2])
             )
       else:
          cos1 = ns << ss[a1] * Meq.Cos(ss[p1])
          cos2 = ns << ss[a2] * Meq.Cos(ss[p2])
          sin1 = ns << ss[a1] * Meq.Sin(ss[p1])
          sin2 = ns << ss[a2] * Meq.Sin(ss[p2])
          stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
             ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex( cos1, sin1),
             0,0,
             ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex( cos2, sin2)
             )
       js.append(skey, stub)

    # Finished:
    js.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js


#--------------------------------------------------------------------------------
# FJones: 2x2 matrix for ionospheric Faraday rotation (NOT ion.phase!)
#--------------------------------------------------------------------------------

def FJones (ns=0, Sixpack=None, slave=False, simul=False, **inarg):
   """defines diagonal FJones Faraday rotation matrices""";

   jones = 'FJones'

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005',
                            description=FJones.__doc__)
   inarg_Joneset_common(pp, jones=jones, slave=slave)              

   if simul:                              # simulation mode
      ls = TDL_Leafset.Leafset()
      ls.inarg(pp, mean_period_s=500, stddev_period_s=50,
               mean_tampl=0.2, stddev_tampl=0.02)
      
   else:                                  # normal mode
      inarg_Joneset_Parmset(pp, slave=slave)              
      # ** Solving instructions:
      JEN_inarg.define(pp, 'tdeg_RM', 0, choice=[0,1,2,3],  
                       help='degree of time polynomial')
      JEN_inarg.define(pp, 'fdeg_RM', 2, choice=[0,1,2,3],  
                       help='degree of freq polynomial')
      JEN_inarg.define(pp, 'subtile_size_RM', 1,  
                       choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                       help='sub-tile size (None=entire tile)')
      # ** MeqParm default values:
      JEN_inarg.define(pp, 'c00_RM', 0.0, choice=[0.1], hide=True,  
                       help='default c00 funklet value')
       
   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   label = jones+JEN_inarg.qualifier(pp)
   
   adjust_for_telescope(pp, origin=funcname)
   pp['punit'] = get_punit(Sixpack, pp)
   
   # Create a Joneset object:
   js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

   # Register the parmgroups (in js.Parmset eventually):
   RM = js.parmgroup('RM', corrs='cross', default=0.0,
                     color='red', style='circle', size=10, **pp)

   # MeqParm node_groups: add 'F' to default 'Parm':
   js.Parmset.node_groups(label[0])

   # Define extra solvegroup(s) from combinations of parmgroups:
   js.Parmset.solvegroup('FJones', [RM])

   # Make a node for the Faraday rotation (same for all stations...)
   if simul:
      js.Leafset.define_MeqLeaf (ns, RM, **pp)
   else:
      js.Parmset.define_MeqParm(ns, RM, tfdeg=[pp['tdeg_RM'],pp['fdeg_RM']])

   ss = js.buffer()
   wvl2 = MG_JEN_twig.wavelength (ns, unop='Sqr')        # -> lambda squared
   farot = ns.farot(q=pp['punit']) << (ss[RM] * wvl2)       # Faraday rotation angle
  
   # The FJones matrix depends on the polarisation representation:
   if pp['polrep']=='circular':
      matname = 'FJones_phase_matrix'
      stub = MG_JEN_matrix.phase (ns, angle=farot, name=matname)
   else:
      matname = 'FJones_rotation_matrix'
      stub = MG_JEN_matrix.rotation (ns, angle=farot, name=matname)

   # For the moment, assume that FJones is the same for all stations:
   for station in pp['stations']:
      skey = TDL_radio_conventions.station_key(station)
      qual = dict(s=skey)
      js.append(skey, stub)

   # Finished:
   js.cleanup()
   MG_JEN_forest_state.object(js, funcname)
   return js



#--------------------------------------------------------------------------------
# BJones: diagonal 2x2 matrix for complex bandpass per polarization
#--------------------------------------------------------------------------------

def BJones (ns=0, Sixpack=None, slave=False, simul=False, **inarg):
    """Defines diagonal 2x2 Jones matrices that represent the IF bandpass:
    Bjones(station,source) matrix elements:
    - B_11 = (Breal_X,Bimag_X)
    - B_12 = 0
    - B_21 = 0
    - B_22 = (Breal_Y,Bimag_Y)
    For circular polarisation, R and L are used rather than X and Y
    NB: The main differences with Gjones are:
      - the higher-order (~5) freq-polynomial
      - solving for real/imag rather than gain/phase 
    """

    jones = 'BJones'

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005',
                            description=BJones.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              
    # ** Jones matrix elements:

    if simul:                              # simulation mode
       ls = TDL_Leafset.Leafset()
       ls.inarg(pp, mean_period_s=5000, stddev_period_s=100,
                mean_tampl=0.2, stddev_tampl=0.02)

    else:                                  # normal mode
       inarg_Joneset_Parmset(pp, slave=slave)              
       # ** Solving instructions:
       JEN_inarg.define(pp, 'tdeg_Breal', 0, choice=[0,1,2,3],  
                        help='degree of time polynomial')
       JEN_inarg.define(pp, 'tdeg_Bimag', '@tdeg_Breal',
                        choice=[0,1,2,3,'@tdeg_Breal'],  
                        help='degree of time polynomial')
       JEN_inarg.define(pp, 'fdeg_Breal', 5, choice=[3,4,5,6],  
                        help='degree of freq polynomial')
       JEN_inarg.define(pp, 'fdeg_Bimag', '@fdeg_Breal',
                        choice=[3,4,5,6,'@fdeg_Breal'],  
                        help='degree of freq polynomial')
       JEN_inarg.define(pp, 'subtile_size_Breal', None,
                        choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                        help='sub-tile size (None=entire tile)')
       JEN_inarg.define(pp, 'subtile_size_Bimag', '@subtile_size_Breal',  
                        choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                        help='sub-tile size (None=entire tile)')
       # ** MeqParm default values: 
       JEN_inarg.define(pp, 'c00_Breal', 1.0, choice=[0.9, 0.1], hide=True,  
                        help='default c00 funklet value')
       JEN_inarg.define(pp, 'c00_Bimag', 0.0, choice=[0.1], hide=True,  
                        help='default c00 funklet value')
       JEN_inarg.define(pp, 'stddev_Breal', 0.0, choice=[0.1], hide=True,   # obsolete?
                        help='scatter in default c00 funklet values')
       JEN_inarg.define(pp, 'stddev_Bimag', 0.0, choice=[0.1], hide=True,  # obsolete?  
                        help='scatter in default c00 funklet values')
       
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)
    label = jones+JEN_inarg.qualifier(pp)

    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)

    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

    # Register the parmgroups (in js.Parmset eventually):
    br1 = js.parmgroup('Breal', ipol=1, corrs='paral11', default=1.0,
                       color='red', style='square', size=7, **pp)
    br2 = js.parmgroup('Breal', ipol=2, corrs='paral22', default=1.0,
                       color='blue', style='square', size=7, **pp)
    bi1 = js.parmgroup('Bimag', ipol=1, corrs='paral11', default=0.0,
                       color='magenta', style='square', size=7, **pp)
    bi2 = js.parmgroup('Bimag', ipol=2, corrs='paral22', default=0.0,
                       color='cyan', style='square', size=7, **pp)

    # Define potential extra condition equations:
    js.Parmset.define_condeq(bi1, unop='Add', value=0.0)
    js.Parmset.define_condeq(bi2, unop='Add', value=0.0)
    js.Parmset.define_condeq(br1, unop='Multiply', value=1.0)
    js.Parmset.define_condeq(br2, unop='Multiply', value=1.0)

    # MeqParm node_groups: add 'B' to default 'Parm':
    js.Parmset.node_groups(label[0])

    # Define extra solvegroup(s) from combinations of parmgroups:
    js.Parmset.solvegroup('BJones', [br1, bi1, br2, bi2])
    js.Parmset.solvegroup('Bpol1', [br1, bi1])
    js.Parmset.solvegroup('Bpol2', [br2, bi2])
    js.Parmset.solvegroup('Breal', [br1, br2])
    js.Parmset.solvegroup('Bimag', [bi1, bi2])

    for station in pp['stations']:
        skey = TDL_radio_conventions.station_key(station)      
        qual = dict(s=skey)

        for Breal in [br1,br2]:
           if simul:
              js.Leafset.define_MeqLeaf (ns, Breal, qual=qual, **pp)
           else:
              js.Parmset.define_MeqParm (ns, Breal, qual=qual,
                                         tfdeg=[pp['tdeg_Breal'],pp['fdeg_Breal']],
                                         subtile_size=pp['subtile_size_Breal'])

        for Bimag in [bi1,bi2]:
           if simul:
              js.Leafset.define_MeqLeaf (ns, Bimag, qual=qual, **pp)
           else:
              js.Parmset.define_MeqParm (ns, Bimag, qual=qual,
                                         tfdeg=[pp['tdeg_Bimag'],pp['fdeg_Bimag']],
                                         subtile_size=pp['subtile_size_Bimag'])


        # Make the 2x2 Jones matrix
        ss = js.buffer()
        stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
            ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[br1], ss[bi1]),
            0,0,
            ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[br2], ss[bi2])
            )
        js.append(skey, stub)

    # Finished:
    js.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js



#--------------------------------------------------------------------------------
# JJones: diagonal 2x2 matrix for full polarization:
#--------------------------------------------------------------------------------

def JJones (ns=0, Sixpack=None, slave=False, simul=False, **inarg):
    """Defines diagonal 2x2 Jones matrices for full polarisation:
    Jjones(station,source) matrix elements:
    - J_11 = (Jreal_11,Jimag_11)
    - J_12 = (Jreal_12,Jimag_12)
    - J_21 = (Jreal_21,Jimag_21)
    - J_22 = (Jreal_22,Jimag_22)
    For circular polarisation, R and L are used rather than X and Y
    """

    jones = 'JJones'

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='14feb2006',
                            description=JJones.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              
    # ** Jones matrix elements:

    if simul:                              # simulation mode
       ls = TDL_Leafset.Leafset()
       ls.inarg(pp, mean_period_s=500, stddev_period_s=50,
                mean_tampl=0.2, stddev_tampl=0.02)

    else:                                  # normal mode
       inarg_Joneset_Parmset(pp, slave=slave)              
       # ** Solving instructions:
       JEN_inarg.define(pp, 'tdeg_Jreal', 0, choice=[0,1,2,3],  
                        help='degree of time polynomial')
       JEN_inarg.define(pp, 'tdeg_Jimag', '@tdeg_Jreal',
                        choice=[0,1,2,3,'@tdeg_Jreal'],  
                        help='degree of time polynomial')
       JEN_inarg.define(pp, 'fdeg_Jreal', 0, choice=[0,1,2,3],  
                        help='degree of freq polynomial')
       JEN_inarg.define(pp, 'fdeg_Jimag', '@fdeg_Jreal',
                        choice=[0,1,2,3,'@fdeg_Jreal'],  
                        help='degree of freq polynomial')
       JEN_inarg.define(pp, 'subtile_size_Jreal', None,
                        choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                        help='sub-tile size (None=entire tile)')
       JEN_inarg.define(pp, 'subtile_size_Jimag', '@subtile_size_Jreal',  
                        choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                        help='sub-tile size (None=entire tile)')
       # ** MeqParm default values: 
       JEN_inarg.define(pp, 'c00_Jreal', 1.0, choice=[0.9, 0.1], hide=True,  
                        help='default c00 funklet value')
       JEN_inarg.define(pp, 'c00_Jimag', 0.0, choice=[0.1], hide=True,  
                        help='default c00 funklet value')
       JEN_inarg.define(pp, 'stddev_Jreal', 0.0, choice=[0.1], hide=True,   # obsolete?
                        help='scatter in default c00 funklet values')
       JEN_inarg.define(pp, 'stddev_Jimag', 0.0, choice=[0.1], hide=True,  # obsolete?  
                        help='scatter in default c00 funklet values')
       
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)
    label = jones+JEN_inarg.qualifier(pp)

    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)

    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

    # Register the parmgroups (in js.Parmset eventually):
    dr11 = js.parmgroup('Jreal_11', corrs='paral11', default=1.0,
                        color='red', style='square', size=7, **pp)
    dr12 = js.parmgroup('Jreal_12', corrs='cross12', default=0.0,
                        color='red', style='square', size=7, **pp)
    dr21 = js.parmgroup('Jreal_21', corrs='cross21', default=0.0,
                        color='red', style='square', size=7, **pp)
    dr22 = js.parmgroup('Jreal_22', corrs='paral22', default=1.0,
                        color='blue', style='square', size=7, **pp)
    di11 = js.parmgroup('Jimag_11', corrs='paral11', default=0.0,
                        color='magenta', style='square', size=7, **pp)
    di12 = js.parmgroup('Jimag_12', corrs='cross12', default=0.0,
                        color='magenta', style='square', size=7, **pp)
    di21 = js.parmgroup('Jimag_21', corrs='cross21', default=0.0,
                        color='magenta', style='square', size=7, **pp)
    di22 = js.parmgroup('Jimag_22', corrs='paral22', default=0.0,
                        color='cyan', style='square', size=7, **pp)

    # Define potential extra condition equations:
    # js.Parmset.define_condeq(di11, unop='Add', value=0.0)
    # js.Parmset.define_condeq(di22, unop='Add', value=0.0)
    # js.Parmset.define_condeq(dr11, unop='Multiply', value=1.0)
    # js.Parmset.define_condeq(dr22, unop='Multiply', value=1.0)

    # MeqParm node_groups: add 'J' to default 'Parm':
    js.Parmset.node_groups(label[0])

    # Define extra solvegroup(s) from combinations of parmgroups:
    js.Parmset.solvegroup('JJones', [dr11, di11, dr12, di12,
                                            dr21, di21, dr22, di22])
    js.Parmset.solvegroup('Jreal', [dr11, dr12, dr21, dr22])
    js.Parmset.solvegroup('Jimag', [di11, di12, di21, di22])

    for station in pp['stations']:
        skey = TDL_radio_conventions.station_key(station)      
        qual = dict(s=skey)

        for Jreal in [dr11,dr12,dr21,dr22]:
           if simul:
              js.Leafset.define_MeqLeaf (ns, Jreal, qual=qual, **pp)
           else:
              js.Parmset.define_MeqParm (ns, Jreal, qual=qual,
                                         tfdeg=[pp['tdeg_Jreal'],pp['fdeg_Jreal']],
                                         subtile_size=pp['subtile_size_Jreal'])

        for Jimag in [di11,di12,di21,di22]:
           if simul:
              js.Leafset.define_MeqLeaf (ns, Jimag, qual=qual, **pp)
           else:
              js.Parmset.define_MeqParm (ns, Jimag, qual=qual,
                                         tfdeg=[pp['tdeg_Jimag'],pp['fdeg_Jimag']],
                                         subtile_size=pp['subtile_size_Jimag'])
              

        # Make the 2x2 Jones matrix
        ss = js.buffer()
        stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
            ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[dr11], ss[di11]),
            ns[label+'_12'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[dr12], ss[di12]),
            ns[label+'_21'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[dr21], ss[di21]),
            ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[dr22], ss[di22])
            )
        js.append(skey, stub)

    # Finished:
    js.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js





#--------------------------------------------------------------------------------
# DJones_WSRT: 2x2 matrix for WSRT polarization leakage
#--------------------------------------------------------------------------------

def DJones_WSRT (ns=0, Sixpack=None, slave=False, simul=False, **inarg):
   """defines 2x2 DJones_WSRT (polarisation leakage) matrices""";

   jones = 'DJones_WSRT'

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005',
                            description=DJones_WSRT.__doc__)
   inarg_Joneset_common(pp, jones=jones, slave=slave)              

   # ** Jones matrix elements:
   JEN_inarg.define(pp, 'coupled_XY_Dang', tf=True,  
                    help='if True, XDang = YDang per station')
   JEN_inarg.define(pp, 'coupled_XY_Dell', tf=True,  
                    help='if True, XDell = -YDell per station')

   if simul:                              # simulation mode
      ls = TDL_Leafset.Leafset()
      ls.inarg(pp, mean_period_s=3000, stddev_period_s=100,
               mean_tampl=0.002, stddev_tampl=0.0002)

   else:                                  # normal mode
      inarg_Joneset_Parmset(pp, slave=slave)              
      # ** Solving instructions:
      JEN_inarg.define(pp, 'tdeg_Dang', 0, choice=[0,1,2,3],  
                       help='degree of time polynomial')
      JEN_inarg.define(pp, 'tdeg_Dell', '@tdeg_Dang',
                       choice=[0,1,2,3,'@tdeg_Dang'],  
                       help='degree of time polynomial')
      JEN_inarg.define(pp, 'fdeg_Dang', 0, choice=[0,1,2,3],  
                       help='degree of freq polynomial')
      JEN_inarg.define(pp, 'fdeg_Dell', '@fdeg_Dang',
                       choice=[0,1,2,3,'@fdeg_Dang'],  
                       help='degree of freq polynomial')
      JEN_inarg.define(pp, 'subtile_size_Dang', None,
                       choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                       help='sub-tile size (None=entire tile)')
      JEN_inarg.define(pp, 'subtile_size_Dell', '@subtile_size_Dang',  
                       choice=[None, 1, 2, 5, 10, 20, 50, 100, 200, 500],  
                       help='sub-tile size (None=entire tile)')
      # ** MeqParm default values:
      JEN_inarg.define(pp, 'c00_Dang', 0.0, choice=[0.1], hide=True,  
                       help='default c00 funklet value')
      JEN_inarg.define(pp, 'c00_Dell', 0.0, choice=[0.1], hide=True,  
                       help='default c00 funklet value')
      JEN_inarg.define(pp, 'c00_PZD', 0.0, choice=[0.1], hide=True,  
                       help='default c00 funklet value')
      JEN_inarg.define(pp, 'stddev_Dang', 0.0, choice=[0.1], hide=True,   # obsolete?
                       help='scatter in default c00 funklet values')
      JEN_inarg.define(pp, 'stddev_Dell', 0.0, choice=[0.1], hide=True,  # obsolete?  
                       help='scatter in default c00 funklet values')
      
   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   label = jones+JEN_inarg.qualifier(pp)

   adjust_for_telescope(pp, origin=funcname)
   pp['punit'] = get_punit(Sixpack, pp)

   # Create a Joneset object:
   js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

   # Register the parmgroups (in js.Parmset eventually):
   Dang = js.parmgroup('Dang', corrs='cross', default=0.0,
                       color='green', style='triangle', size=7, **pp)
   Dell = js.parmgroup('Dell', corrs='cross', default=0.0,
                       color='magenta', style='triangle', size=7, **pp)
   Dang1 = js.parmgroup('Dang', ipol=1, corrs='cross', default=0.0,
                        color='green', style='triangle', size=7, **pp)
   Dang2 = js.parmgroup('Dang', ipol=2, corrs='cross', default=0.0,
                        color='black', style='triangle', size=7, **pp)
   Dell1 = js.parmgroup('Dell', ipol=1, corrs='cross', default=0.0,
                        color='magenta', style='triangle', size=7, **pp)
   Dell2 = js.parmgroup('Dell', ipol=2, corrs='cross', default=0.0,
                        color='yellow', style='triangle', size=7, **pp)
   pzd = js.parmgroup('PZD', corrs='cross', default=0.0,
                      color='blue', style='circle', size=10, **pp)

   # Define potential extra condition equations:
   js.Parmset.define_condeq(Dang, unop='Add', value=0.0)
   js.Parmset.define_condeq(Dang1, unop='Add', value=0.0)
   js.Parmset.define_condeq(Dang2, unop='Add', value=0.0)

   # MeqParm node_groups: add 'D' to default 'Parm':
   js.Parmset.node_groups(label[0])

   # Define extra solvegroup(s) from combinations of parmgroups:
   if pp['coupled_XY_Dang'] and pp['coupled_XY_Dell']:
      js.Parmset.solvegroup('DJones', [Dang, Dell, pzd])
   elif pp['coupled_XY_Dang']:
      js.Parmset.solvegroup('DJones', [Dang, Dell1, Dell2, pzd])
      js.Parmset.solvegroup('Dell', [Dell1, Dell2, pzd])
   elif pp['coupled_XY_Dell']:
      js.Parmset.solvegroup('DJones', [Dang1, Dang2, Dell, pzd])
      js.Parmset.solvegroup('Dang', [Dang1, Dang2, pzd])
   else:
      js.Parmset.solvegroup('DJones', [Dang1, Dang2, Dell1, Dell2, pzd])
      js.Parmset.solvegroup('Dang', [Dang1, Dang2, pzd])
      js.Parmset.solvegroup('Dell', [Dell1, Dell2, pzd])

   # The X/Y Phase-Zero-Difference (PZD) is shared by all stations:
   if simul:
      js.Leafset.define_MeqLeaf (ns, pzd, **pp)
   else:
      js.Parmset.define_MeqParm(ns, pzd)
      
   ss = js.buffer()
   matname = 'DJones_PZD_matrix'
   pmat = MG_JEN_matrix.phase (ns, angle=ss[pzd], name=matname)


   # Make the jones matrices per station:
   jones = {}
   ss = {}
   for station in pp['stations']:
      skey = TDL_radio_conventions.station_key(station)  
      qual = dict(s=skey)

      # Dipole angle errors (Dang) may be coupled (Dang(X)=Dang(Y)) or not:
      matname = 'DJones_Dang_matrix'
      if pp['coupled_XY_Dang']:
         if simul:
            js.Leafset.define_MeqLeaf (ns, Dang, qual=qual, **pp)
         else:
            js.Parmset.define_MeqParm (ns, Dang, qual=qual,
                                       tfdeg=[pp['tdeg_Dang'],pp['fdeg_Dang']],
                                       subtile_size=pp['subtile_size_Dang'])
         ss = js.buffer()
         rmat = MG_JEN_matrix.rotation (ns, angle=ss[Dang], qual=None, name=matname)

      else: 
         for Dang in [Dang1,Dang2]:
            if simul:
               js.Leafset.define_MeqLeaf (ns, Dang, qual=qual, **pp)
            else:
               js.Parmset.define_MeqParm (ns, Dang, qual=qual,
                                          tfdeg=[pp['tdeg_Dang'],pp['fdeg_Dang']],
                                          subtile_size=pp['subtile_size_Dang'])
         ss = js.buffer()
         rmat = MG_JEN_matrix.rotation (ns, angle=[ss[Dang1],ss[Dang2]], qual=None, name=matname)


      # Dipole ellipticities (Dell) may be coupled (Dell(X)=-Dell(Y)) or not:
      matname = 'DJones_Dell_matrix'
      if pp['coupled_XY_Dell']:
         if simul:
            js.Leafset.define_MeqLeaf (ns, Dell, qual=qual, **pp)
         else:
            js.Parmset.define_MeqParm (ns, Dell, qual=qual,
                                       tfdeg=[pp['tdeg_Dell'],pp['fdeg_Dell']],
                                       subtile_size=pp['subtile_size_Dell'])
         ss = js.buffer()
         emat = MG_JEN_matrix.ellipticity (ns, angle=ss[Dell], qual=None, name=matname)

      else:
         for Dell in [Dell1,Dell2]:
            if simul:
               js.Leafset.define_MeqLeaf (ns, Dell, qual=qual, **pp)
            else:
               js.Parmset.define_MeqParm (ns, Dell, qual=qual,
                                          tfdeg=[pp['tdeg_Dell'],pp['fdeg_Dell']],
                                          subtile_size=pp['subtile_size_Dell'])
         ss = js.buffer()
         emat = MG_JEN_matrix.ellipticity (ns, angle=[ss[Dell1],ss[Dell2]], qual=None, name=matname)

      # Make the 2x2 Jones matrix by multiplying the sub-matrices:
      stub = ns[label](s=skey, q=pp['punit']) << Meq.MatrixMultiply (rmat, emat, pmat)
      js.append(skey, stub)

   # Finished:
   js.cleanup()
   MG_JEN_forest_state.object(js, funcname)
   return js



#--------------------------------------------------------------------------------
# KJones: diagonal 2x2 matrix for DFT Fourier kernel
# This function requires a Sixpack as input!
# And also an MSauxinfo object (see TDL_MSauxinfo.py and MG_JEN_Cohset.py)
#--------------------------------------------------------------------------------

def KJones (ns=0, Sixpack=None, MSauxinfo=None, simul=False, slave=False, **inarg):
   """defines diagonal KJones matrices for DFT Fourier kernel""";

   jones = 'KJones'
   
   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='12dec2005',
                            description=KJones.__doc__)
   inarg_Joneset_common(pp, jones=jones, slave=slave)              

   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False

   funcname = JEN_inarg.localscope(pp)
   label = jones+JEN_inarg.qualifier(pp)
   
   adjust_for_telescope(pp, origin=funcname)

   # Note the difference with other Jones matrices:
   if not Sixpack:
      Sixpack = punit2Sixpack(ns, punit='uvp')
   pp['punit'] = get_punit(Sixpack)

   # Create a Joneset object
   js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

   # Calculate punit (l,m,n) from input Sixpack:
   radec = Sixpack.radec(ns)
   radec0 = MSauxinfo.radec0()
   lmn    = ns.lmn(q=pp['punit']) << Meq.LMN(radec_0=radec0, radec=radec)
   ncoord = ns.ncoord(q=pp['punit']) << Meq.Selector(lmn, index=2)
   lmn1   = ns.lmn_minus1(q=pp['punit']) << Meq.Paster(lmn, ncoord-1, index=2)
   sqrtn  = ns << Meq.Sqrt(ncoord)

   if False:
      # Sixpack.display(full=True)
      print '\n KJones:'
      print '- radec  =',radec
      print '- radec0 =',radec0
      print '- lmn    =',lmn
      print '- lmn1   =',lmn1
      print '- ncoord =',ncoord
      print '- sqrtn  =',sqrtn
      print
   
   # The 2x2 KJones matrix is diagonal, with identical elements (Kmel) 
   for station in pp['stations']:
      skey = TDL_radio_conventions.station_key(station)
      qual = dict(s=skey)
      uvw = MSauxinfo.node_station_uvw(skey, ns=ns)
      Kmel = ns.dft(s=skey, q=pp['punit']) << Meq.VisPhaseShift(lmn=lmn1, uvw=uvw)/sqrtn
      stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (Kmel,0,0,Kmel)
      js.append(skey, stub)


   # Finished:
   js.cleanup()
   MG_JEN_forest_state.object(js, funcname)
   return js

















#======================================================================================
#======================================================================================
#======================================================================================
# Joneset/Joneseq visualisation:
#======================================================================================



#======================================================================================
# Visualise the contents (parmgroups) of the given Joneset object:
# If a 'compare' Joneset is given, subtract its MeqParms from the corresponding
# MeqParms (parmgroups) 

def visualise(ns, Joneset, parmgroup=False, compare=None, **pp):
    """visualises the contents of the given Joneset"""

    # Input arguments:
    pp.setdefault('type', 'realvsimag')         # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)           # if True, plot stddev as crosses around mean
    pp.setdefault('show_mxel', True)            # if True, show Joneset matrix elements too  
    pp.setdefault('result', 'dcoll')            # result of this routine ([dcoll] or dconc)
    # pp = record(pp)

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    label = 'Joneset:'+str(Joneset.label())     # e.g. Joneset:GJones
    # visu_scope = 'visu_'+Joneset.scope()+'_'+label
    visu_scope = 'visu_'+label
  
    # Make dcolls per (specified) parm group:
    dcoll = []                                          # list of dcoll records
    if not isinstance(parmgroup, str):                  # no parmgroup specified
        parmgroup = Joneset.Parmset.parmgroup().keys()  # default: all parmgroups
    for key in Joneset.Parmset.parmgroup().keys():
        if parmgroup.__contains__(key):                 # only if parmgroup specified 
            pgk = Joneset.Parmset.parmgroup()[key]      # list of MeqParm node names
            if len(pgk)>0:                              # ignore if empty 
                dc = MG_JEN_dataCollect.dcoll (ns, pgk, scope=visu_scope, tag=key,
                                               type=pp['type'], errorbars=pp['errorbars'],
                                               color=Joneset.Parmset.plot_color()[key],
                                               style=Joneset.Parmset.plot_style()[key])
                dcoll.append(dc)


    # Optional: Also make dcolls per matrix element:
    if pp['show_mxel']:
        melname = ['m11', 'm12', 'm21', 'm22']
        nodes = dict(m11=[], m12=[], m21=[], m22=[])
        for key in Joneset.keys():
            jk = Joneset[key]                        # 2x2 jones matrix node (key=station)
            for i in range(len(melname)):
                nsub = ns.Subscope(visu_scope+'_'+melname[i], s=key)
                selected = nsub.selector(i) << Meq.Selector (jk, index=i)
                nodes[melname[i]].append(selected)    # nodes per matrix element (e.g. m22)
       
        for key in nodes.keys():
            size = 10
            color = 'darkGray'
            style = 'cross'                          # symbol: +
            if key=='m12' or key=='m21':             # cross corrs
                style = 'xcross'                     # symbol: x
                size = 7
                color = 'gray'
            dc = MG_JEN_dataCollect.dcoll (ns, nodes[key],
                                           scope=visu_scope, tag=key,
                                           type=pp['type'],
                                           color=color, style=style, size=size,
                                           errorbars=pp['errorbars'])
            dcoll.append(dc)

    # Make a concatenation of the various dcolls:
    dconc = MG_JEN_dataCollect.dconc (ns, dcoll, scope=visu_scope, bookpage=label)

    if pp['result']=='dconc':
       # Return a dconc record (dataCollect node = dconc['dcoll'])
       return dconc

    else:
       # Default: Return a LIST(!) of one dataCollect node:
       # (This is consistent with MG_JEN_Cohset.visualise()...)
       return [dconc['dcoll']]
    

#---------------------------------------------------------------------------------
# AGW:
#	if (type=='color') {
#           ss := 'black';
#	    ss := [ss,"red blue darkGreen magenta"];
#	    ss := [ss,"darkGray darkMagenta darkRed darkYellow"];
#	    ss := [ss,"darkBlue darkCyan gray"];
#	    ss := [ss,"yellow lightGray cyan green"];
#	    # ss := [ss,"none white"];
#	} else if (type=='spectrum_color') {
#	    ss := "hippo grayscale brentjens";
#	} else if (type=='symbol') {
#	    ss := "circle rectangle square ellipse";
#	    ss := [ss, "xcross cross triangle diamond"];
#	    # ss := [ss,"none"];
#	} else if (type=='line_style') {
#	    ss := "dots lines steps stick";
#	    ss := [ss, "SolidLine DashLine DotLine DashDotLine DashDotDotLine"];
#	    ss := [ss, "solidline dashline dotline dashdotline dashdotdotline"];
#	    # ss := [ss,"none"];





#======================================================================================
# Visualise the contents of the given Joneseq object:

def visualise_Joneseq (ns, Joneseq, **pp):
    """visualises the contents of the given Joneseq"""

    pp.setdefault('result', 'dconc')
    pp['result'] = 'dconc'

    dconc = []
    for js in Joneseq:
      dc = visualise(ns, js, **pp)
      # print '****',js.label(),dc
      dconc.append(dc)
    js = Joneseq.make_Joneset(ns)
    dc = visualise(ns, js, **pp)  
    # print '****',dc
    dconc.append(dc)
    # return True

    # Make a concatenation of the various dcolls:
    dconc = MG_JEN_dataCollect.dconc (ns, dconc, scope=Joneset.scope(),
                                      bookpage='Joneseq')

    # Return a dcoll record (dataCollect node = dconc['dcoll'])
    return dconc





#==========================================================================
# Some convenience functions:
#==========================================================================

# Counter service (use to automatically generate unique node names)

_counters = {}

def _counter (key, increment=0, reset=False, trace=True):
    global _counters
    _counters.setdefault(key, 0)
    if reset: _counters[key] = 0
    _counters[key] += increment
    if trace: print '** MG_JEN_Joneset: _counters(',key,') =',_counters[key]
    return _counters[key]


#--------------------------------------------------------------------------

def Joneseq(label='JJones', origin='MG_JEN_Joneset'):
   """Initialise a Joneseq (Joneset sequence) object"""
   jseq = TDL_Joneset.Joneseq(label=label, origin=origin)
   return jseq

#--------------------------------------------------------------------------------

def display_first_subtree (joneset, full=1):
   """Display the first jones matrix in the given joneset"""
   keys = joneset.keys()
   jones = joneset[keys[0]]
   txt = 'jones[0/'+str(len(keys))+'] of joneset: '+joneset.label()
   MG_JEN_exec.display_subtree(jones, txt, full=full)
   return True

#--------------------------------------------------------------------------------

def get_punit(Sixpack=None, pp=dict()):
    """Get a valid predict-unit (punit) name"""
    punit = 'uvp'                               # default: uv-plane effect
    if Sixpack:                                 # Sixpack supplied
       punit = Sixpack.label()                  # get punit from there
    if pp.has_key('uvplane_effect'):            # 
       if pp['uvplane_effect']:                 # valid for the entire field
          punit = 'uvp'                         # override
    return punit


#--------------------------------------------------------------------------------

def punit2Sixpack(ns, punit='uvp'):
   """Make a Sixpack from a punit string"""
   Sixpack = MG_JEN_Sixpack.newstar_source (ns, punit=punit)
   return Sixpack






#********************************************************************************
#********************************************************************************
#************* PART III: MG control record (may be edited here)******************
#********************************************************************************
#********************************************************************************

script_name = 'MG_JEN_Joneset'

MG = JEN_inarg.init(script_name,
                    last_changed = 'h11dec2005',
                    stations=range(4),            # range of station names/numbers 
                    punit='3C84',                  # prediction-unit (source/patch)
                    parmtable=None,               # name of the MeqParm table (AIPS++)
                    polrep='linear',              # polarisation representation
                    scope=script_name)            # scope of Joneset


# inarg = MG_JEN_Joneset.GJones(_getdefaults=True, slave=True)      
inarg = GJones(_getdefaults=True, slave=True)       # local (MG_JEN_Joneset.py) version 
JEN_inarg.attach(MG, inarg)
    
# inarg = MG_JEN_Joneset.BJones(_getdefaults=True, slave=True)  
inarg = BJones(_getdefaults=True, slave=True)       # local (MG_JEN_Joneset.py) version 
JEN_inarg.attach(MG, inarg)
    
# inarg = MG_JEN_Joneset.JJones(_getdefaults=True, slave=True)  
inarg = JJones(_getdefaults=True, slave=True)       # local (MG_JEN_Joneset.py) version 
JEN_inarg.attach(MG, inarg)
    
# inarg = MG_JEN_Joneset.FJones(_getdefaults=True, slave=True)   
inarg = FJones(_getdefaults=True, slave=True)       # local (MG_JEN_Joneset.py) version 
JEN_inarg.attach(MG, inarg)
    
# inarg = MG_JEN_Joneset.DJones_WSRT(_getdefaults=True, slave=True)  
inarg = DJones_WSRT(_getdefaults=True, slave=True)  # local (MG_JEN_Joneset.py) version 
JEN_inarg.attach(MG, inarg)
if True:
   # Make a (modified) clone of the DJones_WRT inarg specified above: 
   clone = JEN_inarg.clone(inarg, _qual='independent') # the qualifier changes its identifcation        
   JEN_inarg.modify(clone,
                    coupled_XY_Dang=False,             # if True, XDang = YDang per station
                    coupled_XY_Dell=False,             # if True, XDell = -YDell per station
                    _JEN_inarg_option=None)            # optional, not yet used 
   JEN_inarg.attach(MG, clone)
            

#------------------------------------------------------------------------------

# inarg = MG_JEN_Joneset.KJones(_getdefaults=True, slave=True)     
inarg = KJones(_getdefaults=True, slave=True)       # local (MG_JEN_Joneset.py) version 
JEN_inarg.attach(MG, inarg)
            




#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

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

   # Make a sequence (jseq) of (jonesets of) 2x2 jones matrices:
   jseq = TDL_Joneset.Joneseq(label='Jones', origin='MG_JEN_Joneset')
   
   jseq.append(GJones (ns, _inarg=MG))
   jseq.append(BJones (ns, _inarg=MG))
   jseq.append(FJones (ns, _inarg=MG))
   jseq.append(JJones (ns, _inarg=MG))
   jseq.append(DJones_WSRT (ns, _inarg=MG))
   jseq.append(DJones_WSRT (ns, _inarg=MG, _qual='independent'))

   # jseq.append(KJones (ns, _inarg=MG))    # <--- special case (Sixpack? MSauxinfo?) 

   jseq.display()

   # Visualise them individually:
   for js in jseq:
     cc.extend(visualise(ns, js))

   # Matrix multiply to produce the resulting Jones joneset:
   js = jseq.make_Joneset(ns)
   cc.extend(visualise(ns, js))

   # Visualise separately per parmgroup:
   for pg in js.parmgroup().keys():
       cc.extend(visualise(ns, js, parmgroup=pg))

   # MG_JEN_exec.display_object(cc, 'cc', txt=MG['script_name'])

   # Finished: 
   return MG_JEN_exec.on_exit (ns, MG, cc)









#********************************************************************************
#********************************************************************************
#*******************  PART V: Forest execution routine(s) ***********************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)



#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routine(s) ***********************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
  print '\n*******************\n** Local test of:',MG['script_name'],':\n'

  # This is the default:
  if 0:
      MG_JEN_exec.without_meqserver(MG['script_name'], callback=_define_forest)

  ns = NodeScope()
  stations = range(0,3)
  ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
  scope = MG['script_name']

  if 0:
     from Timba.Trees import TDL_MSauxinfo
     MSauxinfo = TDL_MSauxinfo.MSauxinfo(label='MG_JEN_Cohset')
     MSauxinfo.station_config_default()           # WSRT (15 stations), incl WHAT
     MSauxinfo.create_nodes(ns)
     # Sixpack = punit2Sixpack(ns, punit='uvp')
     inarg = KJones (_getdefaults=True)
     JEN_inarg.modify(inarg, stations=stations)
     js = KJones (ns, MSauxinfo=MSauxinfo,_inarg=inarg)
     js.display()     
     display_first_subtree (js, full=True)

  if 0:
     # inarg = FJones (_getdefaults=True)
     inarg = GJones (_getdefaults=True, simul=True)
     # inarg = BJones (_getdefaults=True)
     # inarg = DJones_WSRT (_getdefaults=True)
     from Timba.Trees import JEN_inargGui
     igui = JEN_inargGui.ArgBrowser()
     igui.input(inarg)
     igui.launch()

  if 0:
     simul = False
     # simul = True
     jseq = Joneseq()
     jseq.append(GJones (ns, scope=scope, stations=stations, simul=simul))
     jseq.append(BJones (ns, scope=scope, stations=stations, simul=simul))
     jseq.append(FJones (ns, scope=scope, stations=stations, simul=simul))
     jseq.append(DJones_WSRT (ns, scope=scope, stations=stations, simul=simul))
     jseq.append(JJones (ns, scope=scope, stations=stations, simul=simul))
     jseq.display()
     js = jseq.make_Joneset(ns)
     js.display()     
     display_first_subtree (js, full=1)

  if 1:
     simul = True
     js = GJones (ns, stations=stations, simul=simul)
     full = True
     js.display(full=full)     
     # js.Parmset.display(full=full)     
     js.ParmSet.display(full=full)     
     js.LeafSet.display(full=True)     
     # display_first_subtree (js, full=True)

  if 0:
     js = GJones (ns, stations=stations)
     dconc = visualise(ns, js)
     MG_JEN_exec.display_object (dconc, 'dconc')
     MG_JEN_exec.display_subtree (dconc, 'dconc', full=1)


  if 0:
     MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
     # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
  print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




