# MG_JEN_Joneset.py

# Short description:
#   Functions dealing with a set (joneset) of 2x2 station Jones matrices

# Keywords: ....

# and The MeqTree Foundation
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
# - 09 mar 2006: adopted TDL_ParmSet and TDL_LeafSet
# - 11 mar 2006: removed TDL_Parmset and TDL_Leafset
# - 30 mar 2006: implemented EJones_WSRT()
# - 24 apr 2006: recast ParmSet/LeafSet
# - 04 may 2006: implemented create_ParmSet()

# Copyright: The MeqTree Foundation 




#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *

# from Timba.Contrib.JEN.util import TDL_common
from Timba.Contrib.JEN.util import JEN_inarg
from Timba.Contrib.JEN.util import TDL_Joneset
from Timba.Contrib.JEN.util import TDL_ParmSet     
from Timba.Contrib.JEN.util import TDL_LeafSet                   # <--------- remove...     
from Timba.Contrib.JEN.util import TDL_radio_conventions

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
   # The following is a bit of a kludge (see MG_JEN_Cohset.Jones()):
   if True:
      JEN_inarg.define(pp, '@Jsequence', jones, hide=True,
                       help='list membership indication (used in JEN_inargGui)')
   else:
      # obsolete since the use of qualifiers...
      for name in ['@Jsequence','@Jsequence_simul','@Jsequence_KJones']:
         JEN_inarg.define(pp, name, jones, hide=True,
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
   sg_choice = []
   cond_choice = [None]
   sg_default = []
   cond_default = None
   sg_help = 'solvegroup: list of parmgroups, to be solved for:'
   cond_help = '(list of) extra condition equations:'

   # Make the choice and help, depending on Jsequence:
   sg_choice.extend([['GJones'],['Ggain'],['Gphase']])
   sg_help += '\n- [GJones]:  all GJones MeqParms'
   sg_help += '\n- [Ggain]:   GJones station gains (both pols)'
   sg_help += '\n- [Gphase]:  GJones station phases (both pols)'
   sg_choice.extend([['Gpol1'],['Gpol2']])
   sg_help += '\n- [Gpol1]:   All GJones MeqParms for pol1 (X or R)'
   sg_help += '\n- [Gpol2]:   All GJones MeqParms for pol2 (Y or L)'

   cond_choice.extend(['Gphase_X_sum=0.0','Gphase_Y_sum=0.0'])
   cond_choice.append(['Gphase_X_sum=0.0','Gphase_Y_sum=0.0'])
   cond_help += '\n- [...phase_sum=0.0]:   sum of phases = zero'
   cond_choice.append(['Gphase_X_first=0.0','Gphase_Y_first=0.0'])  
   cond_choice.append(['Gphase_X_last=0.0','Gphase_Y_last=0.0'])  
   cond_help += '\n- [...phase_first=0.0]: phase of first station = zero'
   cond_help += '\n- [...phase_last=0.0]:  phase of last station = zero'

   sg_choice.append(['JJones'])
   sg_choice.append(['JJones','stokesU'])
   sg_choice.append(['JJones','stokesQ'])
   sg_choice.append(['JJones','stokesV'])
   sg_choice.append(['stokesQU','JJones'])
   sg_choice.append(['stokesQUV','JJones'])
   sg_help += '\n- [JJones,stokesU]:     actually solves for U!'
   sg_help += '\n- [JJones,stokesQ]:     -> zero Q(?), but better freq sol(?)'
   sg_help += '\n- [JJones,stokesV]:     -> punit V(?)...'

   sg_choice.append(['GJones','stokesI'])
   sg_choice.append(['stokesI','shape'])
   sg_choice.extend([['stokesI'],['stokesIQU'],['stokesIQUV']])
   sg_choice.extend([['stokesIV'],['stokesQU'],['stokesQUV']])
   sg_help += '\n- [stokesI]:    stokes I (incl SI(f), if relevant)'
   sg_help += '\n- [shape]:      parameters of extended source(s)'
   sg_help += '\n- [stokesIQU]:  stokes I,Q,U (incl RM and SI(f))'
   sg_help += '\n- [stokesIQUV]: stokes I,Q,U,V (incl RM and SI(f))'

   sg_choice.append(['GJones','DJones'])
   sg_choice.extend([['DJones'],['Dang'],['Dell']])
   cond_choice.extend(['Dang_sum=0.0'])
   cond_help += '\n- [Dang_sum=0.0]:   sum of dipole pos.angle errors = zero'
   sg_choice.extend([['Dreal'],['Dimag']])
   # cond_choice.append(['Dimag_X_sum=0.0','Dimag_Y_sum=0.0'])
   # cond_choice.append(['Dreal_X_product=1.0','Dreal_Y_product=1.0'])

   sg_choice.append(['GJones','DJones','FJones'])
   sg_choice.extend([['FJones']])

   sg_choice.append(['EJones'])
   sg_choice.append(['Epointing'])

   sg_choice.append(['GJones','BJones'])
   sg_choice.extend([['BJones'],['Breal'],['Bimag']])
   sg_choice.extend([['Bpol1'],['Bpol2']])
   cond_choice.append(['Bimag_X_sum=0.0','Bimag_Y_sum=0.0'])
   cond_choice.append(['Breal_X_product=1.0','Breal_Y_product=1.0'])
   cond_help += '\n- [...imag_sum=0.0]:   sum of imag.parts = zero'
   cond_help += '\n- [...real_product=1.0]:   product of real.parts = unity'


   JEN_inarg.define(pp, 'solvegroup', sg_default, choice=sg_choice, help=sg_help)
   JEN_inarg.define(pp, 'condition', cond_default, choice=cond_choice, help=cond_help)
   return True






def station_pol1 (polrep='linear'):
   """Return the name (X or R) of the first station polarisation,
   depending on the polarisation representation."""
   if polrep=='circular': return 'R'
   return 'X'

def station_pol2 (polrep='linear'):
   """Return the name (X or R) of the first station polarisation,
   depending on the polarisation representation."""
   if polrep=='circular': return 'L'
   return 'Y'





#--------------------------------------------------------------------------------

def create_ParmSet(label='<label>', **pp):
    """Helper function to create a ParmSet object in an organised way."""
    ps = TDL_ParmSet.ParmSet(label=label)
    if pp.has_key('parmtable'): ps.parmtable(pp['parmtable'])
    # if pp.has_key('punit'): ps.quals(dict(q=pp['punit']))
    return ps


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

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()',
                            version='26apr2006', description=GJones.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              
    # ** Jones matrix elements:
    JEN_inarg.define(pp, 'Gpolar', tf=True, hide=True, 
                     help='obsolete, kept only for upward compatibility')

    pol1 = station_pol1(pp['polrep'])
    pol2 = station_pol2(pp['polrep'])

    # Input arguments for ParmSet parmgroups:
    ps = create_ParmSet(label=jones, **pp)
    inarg_Joneset_ParmSet(pp, slave=slave)
    a1 = ps.inarg_parmgroup (pp, 'Ggain_'+pol1, hide=simul,
                         tdeg=0, fdeg=0, subtile_size=1,
                         condeq_corrs='paral11', c00_default=1.0, 
                         color='red', style='diamond', size=10)
    a2 = ps.inarg_parmgroup (pp, 'Ggain_'+pol2, hide=simul, follows=a1,
                         condeq_corrs='paral22', c00_default=1.0,
                         color='blue', style='diamond', size=10)
    p1 = ps.inarg_parmgroup (pp, 'Gphase_'+pol1, hide=simul, follows=a1, fdeg=1,
                         condeq_corrs='paral11', c00_default=0.0,
                         color='magenta', style='diamond', size=10)
    p2 = ps.inarg_parmgroup (pp, 'Gphase_'+pol2, hide=simul, follows=a1,
                         condeq_corrs='paral22', c00_default=0.0,
                         color='cyan', style='diamond', size=10)
    if simul:                                          # simulation mode
       # Input arguments for simulation instructions:
       ps.LeafSet.inarg_simul (pp, a1, offset=1, time_scale_min=100)
       ps.LeafSet.inarg_simul (pp, a2, offset=1, time_scale_min=100)
       ps.LeafSet.inarg_simul (pp, p1, time_scale_min=10, fdeg=1)
       ps.LeafSet.inarg_simul (pp, p2, time_scale_min=10)

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False

    funcname = JEN_inarg.localscope(pp)
    label = JEN_inarg.qualifier(pp, prepend=jones)

    # Some preparations:
    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)

    # Create a Joneset object
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.ParmSet = ps                           # attach the ParmSet object
    js.ParmSet.quals(dict(q=pp['punit']))
    
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

    # Define solvegroup(s) from combinations of parmgroups:
    if simul:
       js.ParmSet.LeafSet.NodeSet.bookmark('GJones', [a1, p1, a2, p2])
    else:
       # NB: For the bookmark definition, see after stations.
       js.ParmSet.solvegroup('GJones', [a1, p1, a2, p2], bookpage=None)
       js.ParmSet.solvegroup('Gpol1', [a1, p1])
       js.ParmSet.solvegroup('Gpol2', [a2, p2])
       js.ParmSet.solvegroup('Ggain', [a1, a2])
       js.ParmSet.solvegroup('Gphase', [p1, p2])


    # Create the station jones matrices:
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)        
       qual = dict(s=skey)

       # Define MeqParm/MeqLeaf nodes, to be used below:
       ss = dict()
       for group in [a1,a2,p1,p2]:
          ss[group] = js.ParmSet.MeqParm (ns, group, qual=qual, simul=simul)

       # Make the 2x2 Jones matrix:
       if pp['Gpolar']:                  # Preferred (fewer nodes)
          stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
             ns[label+'_11'](s=skey, q=pp['punit']) << Meq.Polar(ss[a1], ss[p1]),
             0,0,
             ns[label+'_22'](s=skey, q=pp['punit']) << Meq.Polar(ss[a2], ss[p2])
             )
       else:
          cos1 = ns << ss[a1] * Meq.Cos(ss[p1])
          cos2 = ns << ss[a2] * Meq.Cos(ss[p2])
          sin1 = ns << ss[a1] * Meq.Sin(ss[p1])
          sin2 = ns << ss[a2] * Meq.Sin(ss[p2])
          stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
             ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(cos1, sin1),
             0,0,
             ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(cos2, sin2)
             )
       js.append(skey, stub)


    # Make nodes and bookmarks for some derived quantities (for display):
    # NB: This must be done AFTER the station nodes have been defined!
    if simul:
       bookpage = js.ParmSet.LeafSet.NodeSet.tlabel()+'_GJones'
       js.ParmSet.LeafSet.NodeSet.apply_binop(ns, [a1,p1], 'Polar', bookpage=bookpage)
       js.ParmSet.LeafSet.NodeSet.apply_binop(ns, [a2,p2], 'Polar', bookpage=bookpage)
    else:
       bookpage = js.ParmSet.NodeSet.tlabel()+'_GJones'
       js.ParmSet.NodeSet.apply_binop(ns, [a1,p1], 'Polar', bookpage=bookpage)
       js.ParmSet.NodeSet.apply_binop(ns, [a2,p2], 'Polar', bookpage=bookpage)

    # Finished:
    js.ParmSet.cleanup()
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


    # Input arguments for ParmSet parmgroups:
    ps = create_ParmSet(label=jones, **pp)
    inarg_Joneset_ParmSet(pp, slave=slave)
    RM = ps.inarg_parmgroup (pp, 'RM',
                             tdeg=0, fdeg=2, subtile_size=1,
                             condeq_corrs='cross', c00_default=0.0,
                             color='red', style='circle', size=10)
    if simul:                    
       # Input arguments for simulation instructions:
       ps.LeafSet.inarg_simul (pp, RM, time_scale_min=100)

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False

    funcname = JEN_inarg.localscope(pp)
    label = JEN_inarg.qualifier(pp, prepend=jones)

    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)
   
    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.ParmSet = ps                           # attach the ParmSet object
    js.ParmSet.quals(dict(q=pp['punit']))

    # MeqParm node_groups: add 'F' to default 'Parm':
    js.ParmSet.node_groups(label[0])
    
    # Define solvegroup(s) from combinations of parmgroups:
    if simul:
       js.ParmSet.LeafSet.NodeSet.bookmark('FJones', [RM])
    else:
       js.ParmSet.solvegroup('FJones', [RM])

    # Make a node for the Faraday rotation (same for all stations...)
    ss = dict()
    if simul:
       ss[RM] = js.ParmSet.LeafSet.MeqLeaf (ns, RM)
    else:
       ss[RM] = js.ParmSet.MeqParm(ns, RM)

    wvl2 = MG_JEN_twig.wavelength (ns, unop='Sqr')        # -> lambda squared
    farot = ns.farot(q=pp['punit']) << (ss[RM] * wvl2)       # Faraday rotation angle
  
    # The FJones matrix depends on the polarisation representation:
    if pp['polrep']=='circular':
       matname = 'FJones_phase_matrix'
       stub = MG_JEN_matrix.phase (ns, angle=farot, name=matname)
    else:
       matname = 'FJones_rotation_matrix'
       stub = MG_JEN_matrix.rotation (ns, angle=farot, name=matname)

    # Create the station jones matrices:
    # For the moment, assume that FJones is the same for all stations:
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)
       qual = dict(s=skey)
       js.append(skey, stub)

    # Finished:
    js.ParmSet.cleanup()
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
    pol1 = station_pol1()
    pol2 = station_pol2()

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005',
                            description=BJones.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              
    # ** Jones matrix elements:

    # Input arguments for ParmSet parmgroups:
    ps = create_ParmSet(label=jones, **pp)
    inarg_Joneset_ParmSet(pp, slave=slave)
    br1 = ps.inarg_parmgroup (pp, 'Breal_'+pol1,
                              tdeg=0, fdeg=5, subtile_size=None,
                              condeq_corrs='paral11', c00_default=1.0,
                              color='red', style='square', size=7)
    br2 = ps.inarg_parmgroup (pp, 'Breal_'+pol2, follows=br1,
                              condeq_corrs='paral22', c00_default=1.0,
                              color='blue', style='square', size=7)
    bi1 = ps.inarg_parmgroup (pp, 'Bimag_'+pol1, follows=br1,
                              condeq_corrs='paral11', c00_default=0.0,
                              color='magenta', style='square', size=7)
    bi2 = ps.inarg_parmgroup (pp, 'Bimag_'+pol2, follows=br1,
                              condeq_corrs='paral22', c00_default=0.0,
                              color='cyan', style='square', size=7)
    if simul:
       # Input arguments for simulation instructions:
       ps.LeafSet.inarg_simul (pp, br1, offset=1, time_scale_min=500)
       ps.LeafSet.inarg_simul (pp, br2, offset=1, time_scale_min=500)
       ps.LeafSet.inarg_simul (pp, bi1, time_scale_min=300)
       ps.LeafSet.inarg_simul (pp, bi2, time_scale_min=300)

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False

    funcname = JEN_inarg.localscope(pp)
    label = JEN_inarg.qualifier(pp, prepend=jones)

    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)

    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.ParmSet = ps                           # attach the ParmSet object
    js.ParmSet.quals(dict(q=pp['punit']))

    # Define potential extra condition equations:
    js.ParmSet.define_condeq(bi1, unop='Add', value=0.0)
    js.ParmSet.define_condeq(bi2, unop='Add', value=0.0)
    js.ParmSet.define_condeq(br1, unop='Multiply', value=1.0)
    js.ParmSet.define_condeq(br2, unop='Multiply', value=1.0)

    # MeqParm node_groups: add 'B' to default 'Parm':
    js.ParmSet.node_groups(label[0])

    # Define solvegroup(s) from combinations of parmgroups:
    if simul:
       js.ParmSet.LeafSet.NodeSet.bookmark('BJones', [br1, bi1, br2, bi2])
    else:
       js.ParmSet.solvegroup('BJones', [br1, bi1, br2, bi2], bookpage=True)
       js.ParmSet.solvegroup('Bpol1', [br1, bi1])
       js.ParmSet.solvegroup('Bpol2', [br2, bi2])
       js.ParmSet.solvegroup('Breal', [br1, br2])
       js.ParmSet.solvegroup('Bimag', [bi1, bi2])

    # Create the station jones matrices:
    for station in pp['stations']:
        skey = TDL_radio_conventions.station_key(station)      
        qual = dict(s=skey)

        # Define MeqParm/MeqLeaf nodes, to be used below:
        ss = dict()
        for group in [br1,br2,bi1,bi2]:
           if simul:
              ss[group] = js.ParmSet.LeafSet.MeqLeaf (ns, group, qual=qual)
           else:
              ss[group] = js.ParmSet.MeqParm (ns, group, qual=qual)

        # Make the 2x2 Jones matrix
        stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
            ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[br1], ss[bi1]),
            0,0,
            ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[br2], ss[bi2])
            )
        js.append(skey, stub)

    # Finished:
    js.ParmSet.cleanup()
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
    JEN_inarg.define(pp, 'diagonal_only', tf=False,  
                     help='if True, solve for diagonal (11,22) elements only')
    JEN_inarg.define(pp, 'all4_always', None, choice=[None, [14], [1], 'WSRT/WHAT'],  
                     help='stations for which all 4 elements will always be solved for')

    # Input arguments for ParmSet parmgroups:
    ps = create_ParmSet(label=jones, **pp)
    inarg_Joneset_ParmSet(pp, slave=slave)
    jr11 = ps.inarg_parmgroup (pp, 'Jreal_11',
                               tdeg=0, fdeg=0, subtile_size=None,
                               condeq_corrs='paral11', c00_default=1.0,
                               color='red', style='square', size=7)
    jr12 = ps.inarg_parmgroup (pp, 'Jreal_12', follows=jr11,
                               condeq_corrs='*', c00_default=0.0,
                               color='red', style='square', size=7)
    jr21 = ps.inarg_parmgroup (pp, 'Jreal_21', follows=jr11,
                               condeq_corrs='*', c00_default=0.0,
                               color='red', style='square', size=7)
    jr22 = ps.inarg_parmgroup (pp, 'Jreal_22', follows=jr11,
                               condeq_corrs='paral22', c00_default=1.0,
                               color='blue', style='square', size=7)
    ji11 = ps.inarg_parmgroup (pp, 'Jimag_11', follows=jr11,
                               condeq_corrs='paral11', c00_default=0.0,
                               color='magenta', style='square', size=7)
    ji12 = ps.inarg_parmgroup (pp, 'Jimag_12', follows=jr11,
                               condeq_corrs='*', c00_default=0.0,
                               color='magenta', style='square', size=7)
    ji21 = ps.inarg_parmgroup (pp, 'Jimag_21', follows=jr11,
                               condeq_corrs='*', c00_default=0.0,
                               color='magenta', style='square', size=7)
    ji22 = ps.inarg_parmgroup (pp, 'Jimag_22', follows=jr11,
                               condeq_corrs='paral22', c00_default=0.0,
                               color='cyan', style='square', size=7)
    if simul:               
       # Input arguments for simulation instructions:
       ps.LeafSet.inarg_simul (pp, jr11, offset=1, time_scale_min=500)
       ps.LeafSet.inarg_simul (pp, jr12, offset=1, scale=0.1, time_scale_min=500)
       ps.LeafSet.inarg_simul (pp, jr21, offset=1, scale=0.1, time_scale_min=500)
       ps.LeafSet.inarg_simul (pp, jr22, offset=1, time_scale_min=500)
       ps.LeafSet.inarg_simul (pp, ji11, scale=0.1, time_scale_min=300)
       ps.LeafSet.inarg_simul (pp, ji12, scale=0.1, time_scale_min=300)
       ps.LeafSet.inarg_simul (pp, ji21, scale=0.1, time_scale_min=300)
       ps.LeafSet.inarg_simul (pp, ji22, scale=0.1, time_scale_min=300)
       # ps.LeafSet.inarg_simul (pp, 'Dang', scale=0.01, time_scale_min=720)
       
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False

    funcname = JEN_inarg.localscope(pp)
    label = JEN_inarg.qualifier(pp, prepend=jones)

    adjust_for_telescope(pp, origin=funcname)

    # Special case (temporary kludge):
    if not pp['all4_always']:
       pp['all4_always'] = []
    if pp['all4_always']=='WSRT/WHAT':
       pp['all4_always'] = [14]
    if not isinstance(pp['all4_always'], (list,tuple)):
       pp['all4_always'] = [pp['all4_always']]

    pp['punit'] = get_punit(Sixpack, pp)

    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.ParmSet = ps                           # attach the ParmSet object
    js.ParmSet.quals(dict(q=pp['punit']))

    # Define potential extra condition equations:
    # js.ParmSet.define_condeq(ji11, unop='Add', value=0.0)
    # js.ParmSet.define_condeq(ji22, unop='Add', value=0.0)
    # js.ParmSet.define_condeq(jr11, unop='Multiply', value=1.0)
    # js.ParmSet.define_condeq(jr22, unop='Multiply', value=1.0)

    # MeqParm node_groups: add 'J' to default 'Parm':
    js.ParmSet.node_groups(label[0])

    # Define solvegroup(s) from combinations of parmgroups:
    if simul:
       if pp['diagonal_only'] and len(pp['all4_always'])==0:
          js.ParmSet.LeafSet.NodeSet.bookmark('JJones', [jr11, ji11, jr22, ji22])
       else:
          js.ParmSet.LeafSet.NodeSet.bookmark('Jreal', [jr11, jr12, jr21, jr22])
          js.ParmSet.LeafSet.NodeSet.bookmark('Jimag', [ji11, ji12, ji21, ji22])
    elif pp['diagonal_only'] and len(pp['all4_always'])==0:
       js.ParmSet.solvegroup('JJones', [jr11, ji11, jr22, ji22], bookpage=True)
       js.ParmSet.solvegroup('Jreal', [jr11, jr22])
       js.ParmSet.solvegroup('Jimag', [ji11, ji22])
    else:
       js.ParmSet.solvegroup('JJones', [jr11, ji11, jr12, ji12,
                                        jr21, ji21, jr22, ji22])
       js.ParmSet.solvegroup('Jreal', [jr11, jr12, jr21, jr22], bookpage=True)
       js.ParmSet.solvegroup('Jimag', [ji11, ji12, ji21, ji22], bookpage=True)


    # Make station Jones matrices:
    for station in pp['stations']:
        skey = TDL_radio_conventions.station_key(station)      
        qual = dict(s=skey)

        if pp['diagonal_only'] and not (station in pp['all4_always']):
           diagonal = True
           JJ = [jr11,jr22,ji11,ji22]
        else:
           diagonal = False
           JJ = [jr11,jr12,jr21,jr22,ji11,ji12,ji21,ji22]

        ss = dict()
        for group in JJ:
           if simul:
              ss[group] = js.ParmSet.LeafSet.MeqLeaf (ns, group, qual=qual)
           else:
              ss[group] = js.ParmSet.MeqParm (ns, group, qual=qual)

        # Make the 2x2 Jones matrix
        if diagonal:
           stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
              ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[jr11], ss[ji11]),
              0,0,
              ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[jr22], ss[ji22])
              )
        else:
           stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
              ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[jr11], ss[ji11]),
              ns[label+'_12'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[jr12], ss[ji12]),
              ns[label+'_21'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[jr21], ss[ji21]),
              ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[jr22], ss[ji22])
              )
        js.append(skey, stub)

    # Finished:
    js.ParmSet.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js





#--------------------------------------------------------------------------------
# DJones_WSRT: 2x2 matrix for WSRT polarization leakage
#--------------------------------------------------------------------------------

def DJones_WSRT (ns=0, Sixpack=None, slave=False, simul=False, **inarg):
    """defines 2x2 DJones_WSRT (polarisation leakage) matrices""";

    jones = 'DJones_WSRT'
    pol1 = station_pol1()
    pol2 = station_pol2()

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005',
                            description=DJones_WSRT.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              

    # ** Jones matrix elements:
    JEN_inarg.define(pp, 'coupled_XY_Dang', tf=True,  
                     help='if True, XDang = YDang per station')
    JEN_inarg.define(pp, 'coupled_XY_Dell', tf=True,  
                     help='if True, XDell = -YDell per station')

    # Input arguments for ParmSet parmgroups:
    ps = create_ParmSet(label=jones, **pp)
    inarg_Joneset_ParmSet(pp, slave=slave)
    Dang = ps.inarg_parmgroup (pp, 'Dang',
                               tdeg=0, fdeg=0, subtile_size=None,
                               condeq_corrs='cross', c00_default=0.0,
                               color='green', style='triangle', size=7)
    Dell = ps.inarg_parmgroup (pp, 'Dell', follows=Dang,
                               condeq_corrs='cross', c00_default=0.0,
                               color='magenta', style='triangle', size=7)
    Dang1 = ps.inarg_parmgroup (pp, 'Dang_'+pol1, follows=Dang,
                                condeq_corrs='cross', c00_default=0.0,
                                color='green', style='triangle', size=7)
    Dang2 = ps.inarg_parmgroup (pp, 'Dang_'+pol2, follows=Dang,
                                condeq_corrs='cross', c00_default=0.0,
                                color='black', style='triangle', size=7)
    Dell1 = ps.inarg_parmgroup (pp, 'Dell_'+pol1, follows=Dang,
                                condeq_corrs='cross', c00_default=0.0,
                                color='magenta', style='triangle', size=7)
    Dell2 = ps.inarg_parmgroup (pp, 'Dell_'+pol2, follows=Dang,
                                condeq_corrs='cross', c00_default=0.0,
                                color='yellow', style='triangle', size=7)
    pzd = ps.inarg_parmgroup (pp, 'PZD',
                              tdeg=0, fdeg=0, subtile_size=None,
                              condeq_corrs='cross', c00_default=0.0,
                              color='blue', style='circle', size=10)
    if simul:
       # Input arguments for simulation instructions:
       ps.LeafSet.inarg_simul (pp, Dang, scale=0.01, time_scale_min=720)
       ps.LeafSet.inarg_simul (pp, Dell, scale=0.01, time_scale_min=720)
       ps.LeafSet.inarg_simul (pp, Dang1, scale=0.01, time_scale_min=720)
       ps.LeafSet.inarg_simul (pp, Dang2, scale=0.01, time_scale_min=720)
       ps.LeafSet.inarg_simul (pp, Dell1, scale=0.01, time_scale_min=720)
       ps.LeafSet.inarg_simul (pp, Dell2, scale=0.01, time_scale_min=720)
       ps.LeafSet.inarg_simul (pp, pzd, time_scale_min=300)

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False

    funcname = JEN_inarg.localscope(pp)
    label = JEN_inarg.qualifier(pp, prepend=jones)

    adjust_for_telescope(pp, origin=funcname)
    pp['punit'] = get_punit(Sixpack, pp)
    
    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.ParmSet = ps                           # attach the ParmSet object
    js.ParmSet.quals(dict(q=pp['punit']))
    
    # Define potential extra condition equations:
    js.ParmSet.define_condeq(Dang, unop='Add', value=0.0)
    js.ParmSet.define_condeq(Dang1, unop='Add', value=0.0)
    js.ParmSet.define_condeq(Dang2, unop='Add', value=0.0)
    
    # MeqParm node_groups: add 'D' to default 'Parm':
    js.ParmSet.node_groups(label[0])

    # Define solvegroup(s) from combinations of parmgroups:
    if simul:
       if pp['coupled_XY_Dang'] and pp['coupled_XY_Dell']:
          js.ParmSet.LeafSet.NodeSet.bookmark('DJones', [Dang, Dell, pzd])
       elif pp['coupled_XY_Dang']:
          js.ParmSet.LeafSet.NodeSet.bookmark('DJones', [Dang, Dell1, Dell2, pzd])
       elif pp['coupled_XY_Dell']:
          js.ParmSet.LeafSet.NodeSet.bookmark('DJones', [Dang1, Dang2, Dell, pzd])
       else:
          js.ParmSet.LeafSet.NodeSet.bookmark('DJones', [Dang1, Dang2, Dell1, Dell2, pzd])
    elif pp['coupled_XY_Dang'] and pp['coupled_XY_Dell']:
       js.ParmSet.solvegroup('DJones', [Dang, Dell, pzd], bookpage=True)
    elif pp['coupled_XY_Dang']:
       js.ParmSet.solvegroup('DJones', [Dang, Dell1, Dell2, pzd], bookpage=True)
       js.ParmSet.solvegroup('Dell', [Dell1, Dell2, pzd])
    elif pp['coupled_XY_Dell']:
       js.ParmSet.solvegroup('DJones', [Dang1, Dang2, Dell, pzd], bookpage=True)
       js.ParmSet.solvegroup('Dang', [Dang1, Dang2, pzd])
    else:
       js.ParmSet.solvegroup('DJones', [Dang1, Dang2, Dell1, Dell2, pzd], bookpage=True)
       js.ParmSet.solvegroup('Dang', [Dang1, Dang2, pzd])
       js.ParmSet.solvegroup('Dell', [Dell1, Dell2, pzd])

    # The X/Y Phase-Zero-Difference (PZD) is shared by all stations:
    ss = dict()
    if simul:
       ss[pzd] = js.ParmSet.LeafSet.MeqLeaf (ns, pzd)
    else:
       ss[pzd] = js.ParmSet.MeqParm(ns, pzd)
    matname = 'DJones_PZD_matrix'
    pmat = MG_JEN_matrix.phase (ns, angle=ss[pzd], name=matname)


    # Make the jones matrices per station:
    jones = {}
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)  
       qual = dict(s=skey)

       # Dipole angle errors (Dang) may be coupled (Dang(X)=Dang(Y)) or not:
       matname = 'DJones_Dang_matrix'
       if pp['coupled_XY_Dang']:
          if simul:
             ss[Dang] = js.ParmSet.LeafSet.MeqLeaf (ns, Dang, qual=qual)
          else:
             ss[Dang] = js.ParmSet.MeqParm (ns, Dang, qual=qual)
          rmat = MG_JEN_matrix.rotation (ns, angle=ss[Dang],
                                         qual=None, name=matname)

       else: 
          for Dang in [Dang1,Dang2]:
             if simul:
                ss[Dang] = js.ParmSet.LeafSet.MeqLeaf (ns, Dang, qual=qual)
             else:
                ss[Dang] = js.ParmSet.MeqParm (ns, Dang, qual=qual)
          rmat = MG_JEN_matrix.rotation (ns, angle=[ss[Dang1],ss[Dang2]],
                                         qual=None, name=matname)

       # Dipole ellipticities (Dell) may be coupled (Dell(X)=-Dell(Y)) or not:
       matname = 'DJones_Dell_matrix'
       if pp['coupled_XY_Dell']:
          if simul:
             ss[Dell] = js.ParmSet.LeafSet.MeqLeaf (ns, Dell, qual=qual)
          else:
             ss[Dell] = js.ParmSet.MeqParm (ns, Dell, qual=qual)
          emat = MG_JEN_matrix.ellipticity (ns, angle=ss[Dell],
                                            qual=None, name=matname)

       else:
          for Dell in [Dell1,Dell2]:
             if simul:
                ss[Dell] = js.ParmSet.LeafSet.MeqLeaf (ns, Dell, qual=qual)
             else:
                ss[Dell] = js.ParmSet.MeqParm (ns, Dell, qual=qual)
          emat = MG_JEN_matrix.ellipticity (ns, angle=[ss[Dell1],ss[Dell2]],
                                            qual=None, name=matname)

       # Make the 2x2 Jones matrix by multiplying the sub-matrices:
       stub = ns[label](s=skey, q=pp['punit']) << Meq.MatrixMultiply (rmat, emat, pmat)
       js.append(skey, stub)

    # Finished:
    js.ParmSet.cleanup()
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
    label = JEN_inarg.qualifier(pp, prepend=jones)
    
    adjust_for_telescope(pp, origin=funcname)

    # Note the difference with other Jones matrices:
    if not Sixpack:
       Sixpack = punit2Sixpack(ns, punit='uvp')
    pp['punit'] = get_punit(Sixpack)

    # Create a Joneset object
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    # js.ParmSet = ps                           # attach the ParmSet object
    js.ParmSet.quals(dict(q=pp['punit']))

    # Calculate punit (l,m,n) from input Sixpack:
    radec = Sixpack.radec(ns)
    radec0 = MSauxinfo.radec0()
    lmn    = ns['lmn'](q=pp['punit']) << Meq.LMN(radec_0=radec0, radec=radec)
    ncoord = ns['ncoord'](q=pp['punit']) << Meq.Selector(lmn, index=2)
    lmn1   = ns['lmn_minus1'](q=pp['punit']) << Meq.Paster(lmn, ncoord-1, index=2)
    sqrtn  = ns << Meq.Sqrt(ncoord)
   
    # The 2x2 KJones matrix is diagonal, with identical elements (Kmel) 
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)
       qual = dict(s=skey)
       uvw = MSauxinfo.node_station_uvw(skey, ns=ns)
       Kmel = ns['dft'](s=skey, q=pp['punit']) << Meq.VisPhaseShift(lmn=lmn1, uvw=uvw)/sqrtn
       stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (Kmel,0,0,Kmel)
       js.append(skey, stub)

    # Finished:
    js.ParmSet.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js






#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
# EJones_WSRT: diagonal 2x2 matrix for WSRT voltage beams
#--------------------------------------------------------------------------------

def EJones_WSRT (ns=0, Sixpack=None, MSauxinfo=None, simul=False, slave=False, **inarg):
    """defines EJones (voltage beamshape) matrices for WSRT (l,m interpolatable)
    Ejones(station,source) matrix elements:
    - E_11 = Egain_X*exp(iEphase_X)
    - E_12 = 0
    - E_21 = 0
    - E_22 = Egain_Y*exp(iEphase_Y)
    For circular polarisation, R and L are used rather than X and Y
    """

    jones = 'EJones_WSRT'
    pol1 = station_pol1()
    pol2 = station_pol2()
 
    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='15dec2005',
                            description=EJones_WSRT.__doc__)
    inarg_Joneset_common(pp, jones=jones, slave=slave)              

    # Input arguments for ParmSet parmgroups:
    ps = create_ParmSet(label=jones, **pp)
    inarg_Joneset_ParmSet(pp, slave=slave)
    b1 = ps.inarg_parmgroup (pp, 'EJones_'+pol1,
                             tdeg=0, fdeg=0, subtile_size=1,
                             descr='Station X voltage beam shape (l,m,t,f)',
                             condeq_corrs='paral', c00_default=1.0,
                             color='red', style='diamond', size=10)
    b2 = ps.inarg_parmgroup (pp, 'EJones_'+pol2, follows=b1,
                             descr='Station Y voltage beam shape (l,m,t,f)',
                             condeq_corrs='paral', c00_default=1.0,
                             color='blue', style='diamond', size=10)
    if simul:
       # Input arguments for simulation instructions:
       ps.LeafSet.inarg_simul (pp, b1, offset=1, time_scale_min=1000)
       ps.LeafSet.inarg_simul (pp, b2, offset=1, time_scale_min=1000)

    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False

    funcname = JEN_inarg.localscope(pp)
    label = JEN_inarg.qualifier(pp, prepend=jones)

    # Some preparations:
    adjust_for_telescope(pp, origin=funcname)

    if not Sixpack:
       Sixpack = punit2Sixpack(ns, punit='uvp')
    pp['punit'] = get_punit(Sixpack)
       
    # Create a Joneset object
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    js.ParmSet = ps                           # attach the ParmSet object
    ## js.ParmSet.quals(dict(q=pp['punit']))
        
    # MeqParm node_groups: add 'E' to default 'Parm':
    js.ParmSet.node_groups(label[0])
    
    # Define solvegroup(s) from combinations of parmgroups:
    if simul:
       # js.ParmSet.LeafSet.NodeSet.bookmark('EJones', [b1,b2,dl,dm])
       js.ParmSet.LeafSet.NodeSet.bookmark('EJones', [b1,b2])
       # js.ParmSet.LeafSet.NodeSet.bookmark('Epointing', [dl,dm])
    else:
       # NB: For the bookmark definition, see after stations.
       js.ParmSet.solvegroup('EJones', [b1,b2], bookpage=None)
       # js.ParmSet.solvegroup('Epointing', [dl,dm], bookpage=None)


    # Calculate punit (l,m) from input Sixpack:
    radec = Sixpack.radec(ns)
    radec0 = MSauxinfo.radec0()
    lmn    = ns['lmn'](q=pp['punit']) << Meq.LMN(radec_0=radec0, radec=radec)
    lm = ns['lm'](q=pp['punit']) << Meq.Selector(lmn, index=[0,1], multi=True)
    cax = [hiid('l'),hiid('m')]                           # <---- necessary?
    qual_punit = dict(q=pp['punit'])

    # The two voltage beams are slightly elongated in the L or M direction:
    X_beam = WSRT_voltage_beam_funklet(a_rad=0.01, b_rad=0.011)
    Y_beam = WSRT_voltage_beam_funklet(a_rad=0.011, b_rad=0.01)

    # Create the station jones matrices:
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)        
       qual = dict(s=skey)

       # Create MeqParm/MeqLeaf nodes, to be used below (using ss):
       ss = dict()
       if False:
          if simul:
             ss[dl] = js.ParmSet.LeafSet.MeqLeaf (ns, dl, qual=qual)
             ss[dm] = js.ParmSet.LeafSet.MeqLeaf (ns, dm, qual=qual)
          else:
             ss[dl] = js.ParmSet.MeqParm (ns, dl, qual=qual)
             ss[dm] = js.ParmSet.MeqParm (ns, dm, qual=qual)

       # Create MeqParm/MeqLeaf nodes with 4D (l,m,f,t) beam funklets:
       lmtot = lm
       if False:
          # Temporarily disabled, until Sarod has implemented solving for (l,m) branch:
          dlm = ns['pointing_error'](s=skey, q=pp['punit']) << Meq.Composer(ss[dl],ss[dm])
          lmtot = ns['lm'](s=skey, q=pp['punit']) << Meq.Add(lm,dlm)

       if simul:
          ss[b1] = js.ParmSet.LeafSet.MeqLeaf (ns, b1, qual=qual, init_funklet=X_beam,
                                       qual2=qual_punit,
                                       compounder_children=lmtot, common_axes=cax)
          ss[b2] = js.ParmSet.LeafSet.MeqLeaf (ns, b2, qual=qual, init_funklet=Y_beam,
                                       qual2=qual_punit,
                                       compounder_children=lmtot, common_axes=cax)
       else:
          ss[b1] = js.ParmSet.MeqParm (ns, b1, qual=qual, init_funklet=X_beam,
                                       qual2=qual_punit,
                                       compounder_children=lmtot, common_axes=cax)
          ss[b2] = js.ParmSet.MeqParm (ns, b2, qual=qual, init_funklet=Y_beam,
                                       qual2=qual_punit,
                                       compounder_children=lmtot, common_axes=cax)

       # Make the 2x2 Jones matrix:
       stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22(ss[b1],0,0,ss[b2])
       js.append(skey, stub)


    # Make nodes and bookmarks for some derived quantities (for display):
    # NB: This must be done AFTER the station nodes have been defined!
    if True:
       pass
    elif simul:
       bookpage = js.ParmSet.LeafSet.NodeSet.tlabel()+'_EJones'
       js.ParmSet.LeafSet.NodeSet.apply_binop(ns, [b1,b2], 'Polar', bookpage=bookpage)
       # js.ParmSet.LeafSet.NodeSet.apply_binop(ns, [dl,dm], 'Polar', bookpage=bookpage)
    else:
       bookpage = js.ParmSet.NodeSet.tlabel()+'_EJones'
       js.ParmSet.NodeSet.apply_binop(ns, [b1,b2], 'Polar', bookpage=bookpage)
       # js.ParmSet.NodeSet.apply_binop(ns, [dl,dm], 'Polar', bookpage=bookpage)

    # Finished:
    js.ParmSet.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js


#---------------------------------------------------------------------------------

def WSRT_voltage_beam_funklet(a_rad=0.1, b_rad=0.1, trace=False):
   """Creation of a compiled 4D funklet for the WSRT voltage beam.
       EJones (L,M) = cos((L/a)^2+(M/b)^2)^3    (L,M,a,b in rad)
   in which the parameters a and b are polcs(freq,time)""" 

   # Polynomials in (t,f) for function coeff a and b:
   t = 'x0'
   f = 'x1'
   if True:
      a_poly = 'p0'
      b_poly = 'p1'
      coeff = [a_rad,b_rad]               # [p0,p1]
   elif False:
      a_poly = 'p0+p1*'+f
      b_poly = 'p2+p3*'+f
      coeff = [a_rad,0,b_rad,0]       # [p0,p1,p2,p3]
   else:
      a_poly = 'p0+p1*'+t+'+p2*'+f
      b_poly = 'p3+p4*'+t+'+p5*'+f
      coeff = [a_rad,0,0,b_rad,0,0]       # [p0,p1,p2,p3,p4,p5]
   
   L ='x2'                                # L axis
   M ='x3'                                # M axis
   # beamshape = '(cos((('+L+')/('+a_poly+'))^2+(('+M+')/('+b_poly+'))^2))^3'
   beamshape = 'exp(-(('+L+')/('+a_poly+'))^2-(('+M+')/('+b_poly+'))^2)'
   # beamshape = 'exp(-((x2)/('+a_poly+'))^2-((x3)/('+b_poly+'))^2)'
   # beamshape = '(cos(((x2)/('+a_poly+'))^2+((x3)/('+b_poly+'))^2))^3'

   funklet = meq.polc(coeff=coeff, subclass=meq._funklet_type)
   funklet.function = beamshape

   if trace:
      print '- t=',t,' f=',f,' L=',L,' M=',M,'   coeff =',coeff
      print '- a_poly =',a_poly,'  b_poly =',b_poly
      print '->',funklet
   return funklet


#---------------------------------------------------------------------------------

def dummy_zero_funklet(trace=False):
   """Creation of a compiled 4D funklet that represents zero."""

   funklet = meq.polc(coeff=[0.0], subclass=meq._funklet_type)
   funklet.function = 'p0'

   if trace:
      print '->',funklet
   return funklet










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
        parmgroup = Joneset.ParmSet.parmgroup().keys()  # default: all parmgroups
    for key in Joneset.ParmSet.parmgroup_keys():
        if parmgroup.__contains__(key):                 # only if parmgroup specified 
            pgk = Joneset.ParmSet.parmgroup()[key]      # list of MeqParm node names
            if len(pgk)>0:                              # ignore if empty 
                dc = MG_JEN_dataCollect.dcoll (ns, pgk, scope=visu_scope, tag=key,
                                               type=pp['type'], errorbars=pp['errorbars'],
                                               color=Joneset.ParmSet.plot_color()[key],
                                               style=Joneset.ParmSet.plot_style()[key])
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

def _counter (key, increment=0, reset=False, trace=False):
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
  nsim = ns.Subscope('_')
  stations = range(0,3)
  ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];
  scope = MG['script_name']

  if 1:
     from Timba.Contrib.JEN.util import TDL_MSauxinfo
     MSauxinfo = TDL_MSauxinfo.MSauxinfo(label='MG_JEN_Cohset')
     MSauxinfo.station_config_default()           # WSRT (15 stations), incl WHAT
     MSauxinfo.create_nodes(ns)

  if 0:
     if 1:
        js = EJones_WSRT (ns, MSauxinfo=MSauxinfo, stations=stations, simul=False)
     if 0:
        js = KJones (ns, MSauxinfo=MSauxinfo, stations=stations)
     js.display()     
     display_first_subtree (js, full=True)


  if 0:
     simul = False
     inarg = FJones (_getdefaults=True, simul=simul)
     # inarg = GJones (_getdefaults=True, simul=simul)
     # inarg = BJones (_getdefaults=True, simul=simul)
     # inarg = JJones (_getdefaults=True, simul=simul)
     # inarg = EJones (_getdefaults=True, simul=simul)
     # inarg = KJones (_getdefaults=True, simul=simul)
     # inarg = DJones_WSRT (_getdefaults=True, simul=simul)
     from Timba.Contrib.JEN.util import JEN_inargGui
     igui = JEN_inargGui.ArgBrowser()
     igui.input(inarg)
     igui.launch()

  if 1:
     simul = False
     # simul = True
     jseq = Joneseq()
     jseq.append(GJones (ns, scope=scope, stations=stations, simul=simul))
     # jseq.append(BJones (ns, scope=scope, stations=stations, simul=simul))
     # jseq.append(FJones (ns, scope=scope, stations=stations, simul=simul))
     # jseq.append(JJones (ns, scope=scope, stations=stations, simul=simul))
     # jseq.append(DJones_WSRT (ns, scope=scope, stations=stations, simul=simul))
     # jseq.append(KJones (ns, MSauxinfo=MSauxinfo, stations=stations, simul=simul))
     # jseq.append(EJones_WSRT (ns, MSauxinfo=MSauxinfo, stations=stations, simul=simul))
     jseq.display()
     js = jseq.make_Joneset(ns)
     # js.display()     
     display_first_subtree (js, full=1)

  if 0:
     if True:
        js = GJones (nsim, stations=stations, simul=True)
     else:
        js = GJones (ns, stations=stations)
     full = True
     # js.display(full=full)     
     js.ParmSet.display(full=full)     
     # display_first_subtree (js, full=True)

  if 0:
     simul = True
     inarg = GJones (_getdefaults=True, stations=stations, simul=simul)
     js = GJones (ns, _inarg=inarg, simul=simul)
     full = True
     # js.display(full=full)     
     js.ParmSet.display(full=full)     
     # js.ParmSet.LeafSet.display(full=full)     
     # display_first_subtree (js, full=True)

  if 0:
     WSRT_voltage_beam_funklet(a_rad=0.1, b_rad=0.1, trace=True)
     dummy_zero_funklet(trace=True)

  if 0:
     js = JJones (ns, stations=stations, simul=True,
                  diagonal_only=True, all4_always=[14])

  if 0:
     js = GJones (ns, stations=stations)
     dconc = visualise(ns, js)
     MG_JEN_exec.display_object (dconc, 'dconc')
     MG_JEN_exec.display_subtree (dconc, 'dconc', full=1)

  if 0:
     full = True
     # js.display(full=full)     
     js.ParmSet.display(full=full)     
     # js.ParmSet.LeafSet.display(full=full)     
     # display_first_subtree (js, full=True)

  if 0:
     MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
     # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
  print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




