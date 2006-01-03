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
# GJones: diagonal 2x2 matrix for complex gains per polarization
#--------------------------------------------------------------------------------

def GJones (ns=None, **inarg):
    """defines diagonal GJones matrices for complex(Gampl,Gphase) parms""";

    jones = 'GJones'

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='15dec2005')
    pp.setdefault('punit', 'uvp')                  # source/patch for which this Joneset is valid
    pp.setdefault('stations', [0])                 # range of station names/numbers
    pp.setdefault('parmtable', None)               # name of the MeqParm table (AIPS++)
    # ** Jones matrix elements:
    pp.setdefault('polrep', 'linear')              # polarisation representation 
    pp.setdefault('Gpolar', False)                 # if True, use MeqPolar, otherwise MeqToComplex
    # ** Solving instructions:
    pp.setdefault('unsolvable', False)             # if True, do NOT store solvegroup/parmgroup info
    pp.setdefault('Gphase_constrain', True)        # if True, constrain 1st station phase
    pp.setdefault('fdeg_Gampl', 0)                 # degree of default freq polynomial         
    pp.setdefault('fdeg_Gphase', 0)                # degree of default freq polynomial          
    pp.setdefault('tdeg_Gampl', 0)                 # degree of default time polynomial         
    pp.setdefault('tdeg_Gphase', 0)                # degree of default time polynomial       
    pp.setdefault('tile_size_Gampl', 0)            # used in tiled solutions         
    pp.setdefault('tile_size_Gphase', 0)           # used in tiled solutions         
    # ** MeqParm default values:
    pp.setdefault('c00_Gampl', 0.3)                # default c00 funklet value
    pp.setdefault('c00_Gphase', 0.0)               # default c00 funklet value
    pp.setdefault('stddev_Gampl', 0.0)             # scatter in default c00 funklet values
    pp.setdefault('stddev_Gphase', 0.0)            # scatter in default c00 funklet values
    pp.setdefault('ft_coeff_scale', 0.0)           # scale of polc_ft non-c00 coeff
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)
    label = jones+JEN_inarg.qualifier(pp)

    # Some preparations:
    adjust_for_telescope(pp, origin=funcname)

    # Create a Joneset object
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
    
    # Register the parmgroups (in js.Parmset eventually):
    a1 = js.register('Gampl', ipol=1, color='red', style='diamond', size=10, corrs='paral1')
    a2 = js.register('Gampl', ipol=2, color='blue', style='diamond', size=10, corrs='paral2')
    p1 = js.register('Gphase', ipol=1, color='magenta', style='diamond', size=10, corrs='paral1')
    p2 = js.register('Gphase', ipol=2, color='cyan', style='diamond', size=10, corrs='paral2')

    # MeqParm node_groups: add 'G' to default 'Parm':
    js.Parmset.node_groups(label[0])

    # Define extra solvegroup(s) from combinations of parmgroups:
    js.Parmset.define_solvegroup('GJones', [a1, p1, a2, p2])
    js.Parmset.define_solvegroup('Gpol1', [a1, p1])
    js.Parmset.define_solvegroup('Gpol2', [a2, p2])
    js.Parmset.define_solvegroup('Gampl', [a1, a2])
    js.Parmset.define_solvegroup('Gphase', [p1, p2])
    
    first_station = True
    for station in pp['stations']:
       skey = TDL_radio_conventions.station_key(station)        
       # Define station MeqParms (in ss), and do some book-keeping:  
       js.Parmset.buffer(reset=True)

       for Gampl in [a1,a2]:
          default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gampl'], stddev=pp['stddev_Gampl'],
                                            fdeg=pp['fdeg_Gampl'], tdeg=pp['tdeg_Gampl'],
                                            scale=pp['ft_coeff_scale']) 
          js.Parmset.define_MeqParm (ns, Gampl, station=skey, default=default,
                                     tile_size=pp['tile_size_Gampl'])

       for Gphase in [p1,p2]:
          default = MG_JEN_funklet.polc_ft (c00=pp['c00_Gphase'], stddev=pp['stddev_Gphase'], 
                                            fdeg=pp['fdeg_Gphase'], tdeg=pp['tdeg_Gphase'],
                                            scale=pp['ft_coeff_scale']) 
          constrain = False
          if pp['Gphase_constrain']: 
             if first_station: constrain = True
          js.Parmset.define_MeqParm (ns, Gphase, station=skey, default=default,
                                     constrain=constrain,
                                     tile_size=pp['tile_size_Gphase'])

       ss = js.Parmset.buffer(update=True)
       first_station = False

       # Make the 2x2 Jones matrix:
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
    js.Parmset.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js


#--------------------------------------------------------------------------------
# FJones: 2x2 matrix for ionospheric Faraday rotation (NOT ion.phase!)
#--------------------------------------------------------------------------------

def FJones (ns=0, **inarg):
   """defines diagonal FJones Faraday rotation matrices""";

   jones = 'FJones'

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005')
   pp.setdefault('punit', 'uvp')                  # source/patch for which this Joneset is valid
   pp.setdefault('stations', [0])                 # range of station names/numbers
   pp.setdefault('parmtable', None)               # name of the MeqParm table (AIPS++) 
   # ** Jones matrix elements:
   pp.setdefault('polrep', 'linear')              # polarisation representation
   # ** Solving instructions:
   pp.setdefault('unsolvable', False)             # if True, do NOT store solvegroup/parmgroup info
   pp.setdefault('tile_size_RM', 1)               # used in tiled solutions         
   pp.setdefault('fdeg_RM', 0)                    # degree of default freq polynomial          
   pp.setdefault('tdeg_RM', 0)                    # degree of default time polynomial         
   # ** MeqParm default values:
   pp.setdefault('c00_RM', 0.0)                   # default c00 funklet value
   pp.setdefault('ft_coeff_scale', 0.0)           # scale of polc_ft non-c00 coeff
   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   label = jones+JEN_inarg.qualifier(pp)
   
   adjust_for_telescope(pp, origin=funcname)
   
   # Create a Joneset object:
   js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

   # Register the parmgroups (in js.Parmset eventually):
   RM = js.register('RM', color='red', style='circle', size=10, corrs='cross')

   # MeqParm node_groups: add 'F' to default 'Parm':
   js.Parmset.node_groups(label[0])

   # Define extra solvegroup(s) from combinations of parmgroups:
   js.Parmset.define_solvegroup('FJones', [RM])

   # Make a node for the Faraday rotation (same for all stations...)
   js.Parmset.buffer(reset=True)
   js.Parmset.define_MeqParm(ns, RM, default=pp['c00_RM'])              # Rotation Measure
   ss = js.Parmset.buffer(update=True)
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
      js.append(skey, stub)

   # Finished:
   js.Parmset.cleanup()
   MG_JEN_forest_state.object(js, funcname)
   return js



#--------------------------------------------------------------------------------
# BJones: diagonal 2x2 matrix for complex bandpass per polarization
#--------------------------------------------------------------------------------

def BJones (ns=0, **inarg):
    """defines diagonal BJones bandpass matrices""";

    jones = 'BJones'

    # Input arguments:
    pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005')
    pp.setdefault('punit', 'uvp')                  # source/patch for which this Joneset is valid
    pp.setdefault('stations', [0])                 # range of station names/numbers
    # ** Jones matrix elements:
    pp.setdefault('polrep', 'linear')              # polarisation representation
    # ** Solving instructions:
    pp.setdefault('unsolvable', False)             # if True, do NOT store solvegroup/parmgroup info
    pp.setdefault('parmtable', None)               # name of the MeqParm table (AIPS++)
    pp.setdefault('Breal_constrain', False)        # if True, constrain 1st station phase
    pp.setdefault('Bimag_constrain', True)         # if True, constrain 1st station phase
    pp.setdefault('fdeg_Breal', 3)                 # degree of default freq polynomial           
    pp.setdefault('fdeg_Bimag', 3)                 # degree of default freq polynomial           
    pp.setdefault('tdeg_Breal', 0)                 # degree of default time polynomial           
    pp.setdefault('tdeg_Bimag', 0)                 # degree of default time polynomial          
    pp.setdefault('tile_size_Breal', 0)            # used in tiled solutions         
    pp.setdefault('tile_size_Bimag', 0)            # used in tiled solutions         
    # ** MeqParm default values: 
    pp.setdefault('c00_Breal', 1.0)                # default c00 funklet value
    pp.setdefault('c00_Bimag', 0.0)                # default c00 funklet value
    pp.setdefault('stddev_Breal', 0)               # scatter in default c00 funklet values
    pp.setdefault('stddev_Bimag', 0)               # scatter in default c00 funklet values
    pp.setdefault('ft_coeff_scale', 0.0)           # scale of polc_ft non-c00 coeff
    if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
    if not JEN_inarg.is_OK(pp): return False
    funcname = JEN_inarg.localscope(pp)
    label = jones+JEN_inarg.qualifier(pp)

    adjust_for_telescope(pp, origin=funcname)

    # Create a Joneset object:
    js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
  
    # Register the parmgroups (in js.Parmset eventually):
    br1 = js.register('Breal', ipol=1, color='red', style='square', size=7, corrs='paral1')
    br2 = js.register('Breal', ipol=2, color='blue', style='square', size=7, corrs='paral2')
    bi1 = js.register('Bimag', ipol=1, color='magenta', style='square', size=7, corrs='paral1')
    bi2 = js.register('Bimag', ipol=2, color='cyan', style='square', size=7, corrs='paral2')

    # MeqParm node_groups: add 'B' to default 'Parm':
    js.Parmset.node_groups(label[0])

    # Define extra solvegroup(s) from combinations of parmgroups:
    js.Parmset.define_solvegroup('BJones', [br1, bi1, br2, bi2])
    js.Parmset.define_solvegroup('Bpol1', [br1, bi1])
    js.Parmset.define_solvegroup('Bpol2', [br2, bi2])
    js.Parmset.define_solvegroup('Breal', [br1, br2])
    js.Parmset.define_solvegroup('Bimag', [bi1, bi2])

    first_station = True
    for station in pp['stations']:
        skey = TDL_radio_conventions.station_key(station)      
        # Define station MeqParms (in ss), and do some book-keeping:  
        js.Parmset.buffer(reset=True)

        # Example: polc_ft (c00=1, fdeg=0, tdeg=0, scale=1, mult=1/sqrt(10), stddev=0) 

        for Breal in [br1,br2]:
            default = MG_JEN_funklet.polc_ft (c00=pp['c00_Breal'], stddev=pp['stddev_Breal'], 
                                              fdeg=pp['fdeg_Breal'], tdeg=pp['tdeg_Breal'], 
                                              scale=pp['ft_coeff_scale']) 
            constrain = False
            if pp['Breal_constrain']: 
                if first_station: constrain = True
            js.Parmset.define_MeqParm (ns, Breal, station=skey, default=default,
                               constrain=constrain,
                               tile_size=pp['tile_size_Breal'])

        for Bimag in [bi1,bi2]:
            default = MG_JEN_funklet.polc_ft (c00=pp['c00_Bimag'], stddev=pp['stddev_Bimag'], 
                                              fdeg=pp['fdeg_Bimag'], tdeg=pp['tdeg_Bimag'], 
                                              scale=pp['ft_coeff_scale']) 
            constrain = False
            if pp['Bimag_constrain']: 
                if first_station: constrain = True
            js.Parmset.define_MeqParm (ns, Bimag, station=skey, default=default,
                               constrain=constrain,
                               tile_size=pp['tile_size_Bimag'])

        ss = js.Parmset.buffer(update=True)
        first_station = False

        # Make the 2x2 Jones matrix
        stub = ns[label](s=skey, q=pp['punit']) << Meq.Matrix22 (
            ns[label+'_11'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[br1], ss[bi1]),
            0,0,
            ns[label+'_22'](s=skey, q=pp['punit']) << Meq.ToComplex(ss[br2], ss[bi2])
            )
        js.append(skey, stub)

    # Finished:
    js.Parmset.cleanup()
    MG_JEN_forest_state.object(js, funcname)
    return js





#--------------------------------------------------------------------------------
# DJones: 2x2 matrix for polarization leakage
#--------------------------------------------------------------------------------

def DJones_WSRT (ns=0, **inarg):
   """defines 2x2 DJones_WSRT (polarisation leakage) matrices""";

   jones = 'DJones_WSRT'

   # Input arguments:
   pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='16dec2005')
   pp.setdefault('punit', 'uvp')                     # source/patch for which this Joneset is valid
   pp.setdefault('stations', [0])                    # range of station names/numbers
   # ** Jones matrix elements:
   pp.setdefault('polrep', 'linear')                 # polarisation representation
   # ** Solving instructions:
   pp.setdefault('unsolvable', False)                # if True, do NOT store solvegroup/parmgroup info
   pp.setdefault('parmtable', None)                  # name of the MeqParm table (AIPS++)
   pp.setdefault('coupled_XY_dang', True)            # if True, Xdang = Ydang per station
   pp.setdefault('coupled_XY_dell', True)            # if True, Xdell = -Ydell per station
   pp.setdefault('fdeg_dang', 0)                     # degree of default freq polynomial
   pp.setdefault('fdeg_dell', 0)                     # degree of default freq polynomial
   pp.setdefault('tdeg_dang', 0)                     # degree of default time polynomial
   pp.setdefault('tdeg_dell', 0)                     # degree of default time polynomial
   pp.setdefault('tile_size_dang', 0)                # used in tiled solutions         
   pp.setdefault('tile_size_dell', 0)                # used in tiled solutions         
   # ** MeqParm default values:
   pp.setdefault('c00_dang', 0.0)                    # default c00 funklet value
   pp.setdefault('c00_dell', 0.0)                    # default c00 funklet value
   pp.setdefault('c00_PZD', 0.0)                     # default c00 funklet value
   pp.setdefault('stddev_dang', 0)                   # scatter in default c00 funklet values
   pp.setdefault('stddev_dell', 0)                   # scatter in default c00 funklet values
   pp.setdefault('ft_coeff_scale', 0.0)              # scale of polc_ft non-c00 coeff
   if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
   if not JEN_inarg.is_OK(pp): return False
   funcname = JEN_inarg.localscope(pp)
   label = jones+JEN_inarg.qualifier(pp)

   adjust_for_telescope(pp, origin=funcname)

   # Create a Joneset object:
   js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

   # Register the parmgroups (in js.Parmset eventually):
   dang = js.register('dang', color='green', style='triangle', size=7, corrs='cross')
   dell = js.register('dell', color='magenta', style='triangle', size=7, corrs='cross')
   dang1 = js.register('dang', ipol=1, color='green', style='triangle', size=7, corrs='cross')
   dang2 = js.register('dang', ipol=2, color='black', style='triangle', size=7, corrs='cross')
   dell1 = js.register('dell', ipol=1, color='magenta', style='triangle', size=7, corrs='cross')
   dell2 = js.register('dell', ipol=2, color='yellow', style='triangle', size=7, corrs='cross')
   pzd = js.register('PZD', color='blue', style='circle', size=10, corrs='cross')

   # MeqParm node_groups: add 'D' to default 'Parm':
   js.Parmset.node_groups(label[0])

   # Define extra solvegroup(s) from combinations of parmgroups:
   if pp['coupled_XY_dang'] and pp['coupled_XY_dell']:
      js.Parmset.define_solvegroup('DJones', [dang, dell, pzd])
   elif pp['coupled_XY_dang']:
      js.Parmset.define_solvegroup('DJones', [dang, dell1, dell2, pzd])
      js.Parmset.define_solvegroup('dell', [dell1, dell2, pzd])
   elif pp['coupled_XY_dell']:
      js.Parmset.define_solvegroup('DJones', [dang1, dang2, dell, pzd])
      js.Parmset.define_solvegroup('dang', [dang1, dang2, pzd])
   else:
      js.Parmset.define_solvegroup('DJones', [dang1, dang2, dell1, dell2, pzd])
      js.Parmset.define_solvegroup('dang', [dang1, dang2, pzd])
      js.Parmset.define_solvegroup('dell', [dell1, dell2, pzd])

   # The X/Y Phase-Zero-Difference (PZD) is shared by all stations:
   js.Parmset.buffer(reset=True)
   js.Parmset.define_MeqParm(ns, pzd, default=pp['c00_PZD'])
   ss = js.Parmset.buffer(update=True)
   matname = 'DJones_PZD_matrix'
   pmat = MG_JEN_matrix.phase (ns, angle=ss[pzd], name=matname)


   # Make the jones matrices per station:
   jones = {}
   ss = {}
   for station in pp['stations']:
      skey = TDL_radio_conventions.station_key(station)  
      # Define station MeqParms (in ss), and do some book-keeping:  
      js.Parmset.buffer(reset=True)
      qual = None


      # Dipole angle errors may be coupled (dang(X)=dang(Y)) or not:
      matname = 'DJones_dang_matrix'
      if pp['coupled_XY_dang']:
         default = MG_JEN_funklet.polc_ft (c00=pp['c00_dang'], stddev=pp['stddev_dang'],
                                           scale=pp['ft_coeff_scale'],
                                           fdeg=pp['fdeg_dang'], tdeg=pp['tdeg_dang']) 
         js.Parmset.define_MeqParm (ns, dang, station=skey, default=default,
                                    tile_size=pp['tile_size_dang'])
         ss = js.Parmset.buffer(update=True, reset=True)
         rmat = MG_JEN_matrix.rotation (ns, angle=ss[dang], qual=qual, name=matname)
      else: 
         for dang in [dang1,dang2]:
            default = MG_JEN_funklet.polc_ft (c00=pp['c00_dang'], stddev=pp['stddev_dang'],
                                              scale=pp['ft_coeff_scale'],
                                              fdeg=pp['fdeg_dang'], tdeg=pp['tdeg_dang']) 
            js.Parmset.define_MeqParm (ns, dang, station=skey, default=default,
                                       tile_size=pp['tile_size_dang'])
         ss = js.Parmset.buffer(update=True, reset=True)
         rmat = MG_JEN_matrix.rotation (ns, angle=[ss[dang1],ss[dang2]], qual=qual, name=matname)


      # Dipole ellipticities may be coupled (dell(X)=-dell(Y)) or not:
      matname = 'DJones_dell_matrix'
      if pp['coupled_XY_dell']:
         default = MG_JEN_funklet.polc_ft (c00=pp['c00_dell'], stddev=pp['stddev_dell'],
                                           scale=pp['ft_coeff_scale'],
                                           fdeg=pp['fdeg_dell'], tdeg=pp['tdeg_dell']) 
         js.Parmset.define_MeqParm (ns, dell, station=skey, default=default,
                                    tile_size=pp['tile_size_dell'])
         ss = js.Parmset.buffer(update=True, reset=True)
         emat = MG_JEN_matrix.ellipticity (ns, angle=ss[dell], qual=qual, name=matname)
      else:
         for dell in [dell1,dell2]:
            default = MG_JEN_funklet.polc_ft (c00=pp['c00_dell'], stddev=pp['stddev_dell'],
                                              scale=pp['ft_coeff_scale'], 
                                              fdeg=pp['fdeg_dell'], tdeg=pp['tdeg_dell']) 
            js.Parmset.define_MeqParm (ns, dell, station=skey, default=default,
                                       tile_size=pp['tile_size_dell'])
         ss = js.Parmset.buffer(update=True, reset=True)
         emat = MG_JEN_matrix.ellipticity (ns, angle=[ss[dell1],ss[dell2]], qual=qual, name=matname)

      # Make the 2x2 Jones matrix by multiplying the sub-matrices:
      stub = ns[label](s=skey, q=pp['punit']) << Meq.MatrixMultiply (rmat, emat, pmat)
      js.append(skey, stub)

   # Finished:
   js.Parmset.cleanup()
   MG_JEN_forest_state.object(js, funcname)
   return js



#--------------------------------------------------------------------------------
# KJones: diagonal 2x2 matrix for DFT Fourier kernel
# This function requires a Sixpack as input!
#--------------------------------------------------------------------------------

def KJones (ns=0, Sixpack=None, **inarg):
  """defines diagonal KJones matrices for DFT Fourier kernel""";

  jones = 'KJones'

  # Input arguments:
  pp = JEN_inarg.inarg2pp(inarg, 'MG_JEN_Joneset::'+jones+'()', version='12dec2005')
  pp.setdefault('stations', [0])       # range of station names/numbers
  # ** Solving instructions:
  pp.setdefault('unsolvable', True)                # if True, do NOT store solvegroup/parmgroup info
  # ** MeqParm default values:
  if JEN_inarg.getdefaults(pp): return JEN_inarg.pp2inarg(pp)
  if not JEN_inarg.is_OK(pp): return False
  funcname = JEN_inarg.localscope(pp)
  label = jones+JEN_inarg.qualifier(pp)


  adjust_for_telescope(pp, origin=funcname)

  if not Sixpack: Sixpack = punit2Sixpack(ns, punit='uvp')
  punit = Sixpack.label()

  # Create a Joneset object
  js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

  # Get a record with the names of MS interface nodes
  # Supply a nodescope (ns) in case it does not exist yet
  rr = MG_JEN_forest_state.MS_interface_nodes(ns)

  # Calculate punit (l,m,n) from input Sixpack:
  radec = Sixpack.radec()
  lmn   = ns.lmn  (q=punit) << Meq.LMN(radec_0=ns[rr.radec0], radec=radec)
  n     = ns.n    (q=punit) << Meq.Selector(lmn, index=2)
  lmn1  = ns.lmn_minus1(q=punit) << Meq.Paster(lmn, n-1, index=2)
  sqrtn = ns << Meq.Sqrt(n)

  # The 2x2 KJones matrix is diagonal, with identical elements (Kmel) 
  for station in pp['stations']:
    skey = TDL_radio_conventions.station_key(station)
    Kmel = ns.dft(s=skey, q=punit) << Meq.VisPhaseShift(lmn=lmn1,
                                                        uvw=ns[rr.uvw[skey]])/sqrtn
    stub = ns[label](s=skey, q=punit) << Meq.Matrix22 (Kmel,0,0,Kmel)
    js.append(skey, stub)


  # Finished:
  js.Parmset.cleanup()
  MG_JEN_forest_state.object(js, funcname)
  return js



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
# Initialise a Joneseq object
def Joneseq(label='JJones', origin='MG_JEN_Joneset'):
    jseq = TDL_Joneset.Joneseq(label=label, origin=origin)
    return jseq;

#--------------------------------------------------------------------------------
# Display the first jones matrix in the given joneset:

def display_first_subtree (joneset, full=1):
  keys = joneset.keys()
  jones = joneset[keys[0]]
  txt = 'jones[0/'+str(len(keys))+'] of joneset: '+joneset.label()
  MG_JEN_exec.display_subtree(jones, txt, full=full)


# Make a Sixpack from a punit string

def punit2Sixpack(ns, punit='uvp'):
  Sixpack = MG_JEN_Sixpack.newstar_source (ns, name=punit)
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


#========
if True:                                                # ... Copied from MG_JEN_Joneset.py ...
    # inarg = MG_JEN_Joneset.GJones(_getdefaults=True)      
    inarg = GJones(_getdefaults=True)                    # local (MG_JEN_Joneset.py) version 
    JEN_inarg.modify(inarg,
                     punit=MG['punit'],                 # source/patch name
                     stations=MG['stations'],           # range of station names/numbers
                     parmtable=MG['parmtable'],         # name of the MeqParm table (AIPS++)
                     
                     # ** Jones matrix elements:
                     polrep=MG['polrep'],               # polarisation representation
                     # Gpolar=False,                      # if True, use MeqPolar, otherwise MeqToComplex
                     
                     # ** Solving instructions:
                     unsolvable=False,                  # if True, do not store parmgroup info
                     Gphase_constrain=True,             # if True, constrain 1st station phase
                     fdeg_Gampl=5,                      # degree of default freq polynomial         
                     fdeg_Gphase='fdeg_Gampl',          # degree of default freq polynomial          
                     tdeg_Gampl=0,                      # degree of default time polynomial         
                     tdeg_Gphase='tdeg_Gampl',          # degree of default time polynomial       
                     tile_size_Gampl=0,                 # used in tiled solutions         
                     tile_size_Gphase='tile_size_Gampl', # used in tiled solutions         
                     
                     # ** MeqParm default values:
                     c00_Gampl=0.3,                     # default c00 funklet value
                     c00_Gphase=0.0,                    # default c00 funklet value
                     stddev_Gampl=0.1,                  # scatter in default c00 funklet values
                     stddev_Gphase=0.1,                 # scatter in default c00 funklet values
                     # ft_coeff_scale=0.0,                # scale of polc_ft non-c00 coeff
                     
                     _JEN_inarg_option=None)            # optional, not yet used 
    JEN_inarg.attach(MG, inarg)
    
    
    
#========
if True:                                                # ... Copied from MG_JEN_Joneset.py ...
    # inarg = MG_JEN_Joneset.BJones(_getdefaults=True)  
    inarg = BJones(_getdefaults=True)                    # local (MG_JEN_Joneset.py) version 
    JEN_inarg.modify(inarg,
                     punit=MG['punit'],                 # source/patch name
                     stations=MG['stations'],           # range of station names/numbers
                     parmtable=MG['parmtable'],         # name of the MeqParm table (AIPS++)
                     
                     # ** Jones matrix elements:
                     polrep=MG['polrep'],               # polarisation representation
                     
                     # ** Solving instructions:
                     unsolvable=False,                  # if True, do not store parmgroup info
                     Breal_constrain=False,             # if True, constrain 1st station phase
                     Bimag_constrain=True,              # if True, constrain 1st station phase
                     fdeg_Breal=3,                      # degree of default freq polynomial        
                     fdeg_Bimag='fdeg_Breal',           # degree of default freq polynomial          
                     tdeg_Breal=0,                      # degree of default time polynomial         
                     tdeg_Bimag='tdeg_Breal',           # degree of default time polynomial    
                     tile_size_Breal=0,                 # used in tiled solutions         
                     tile_size_Bimag='tile_size_Breal', # used in tiled solutions         
                     
                     # ** MeqParm default values:
                     c00_Breal=1.0,                         # default c00 funklet value
                     c00_Bimag=0.0,                         # default c00 funklet value
                     stddev_Breal=0.1,                    # scatter in default c00 funklet values
                     stddev_Bimag=0.1,                    # scatter in default c00 funklet values
                     ft_coeff_scale=1.0,                  # scale of polc_ft non-c00 coeff
                     
                     _JEN_inarg_option=None)            # optional, not yet used 
    JEN_inarg.attach(MG, inarg)
    
    

#========
if True:                                                # ... Copied from MG_JEN_Joneset.py ...
    # inarg = MG_JEN_Joneset.FJones(_getdefaults=True)   
    inarg = FJones(_getdefaults=True)                    # local (MG_JEN_Joneset.py) version 
    JEN_inarg.modify(inarg,
                     punit=MG['punit'],                 # source/patch name
                     stations=MG['stations'],           # range of station names/numbers
                     parmtable=MG['parmtable'],         # name of the MeqParm table (AIPS++)
                     
                     # ** Jones matrix elements:
                     polrep=MG['polrep'],               # polarisation representation
                     
                     # ** Solving instructions:
                     unsolvable=False,                  # if True, do not store parmgroup info
                     tile_size_RM=1,                    # used in tiled solutions         
                     fdeg_RM=0,                         # degree of default freq polynomial          
                     tdeg_RM=0,                         # degree of default time polynomial         

                     # ** MeqParm default values:
                     c00_RM=0.5,                        # default c00 funklet value
                     ft_coeff_scale=0.0,                # scale of polc_ft non-c00 coeff
                     
                     _JEN_inarg_option=None)            # optional, not yet used 
    JEN_inarg.attach(MG, inarg)
    
    
#========
if True:                                                # ... Copied from MG_JEN_Joneset.py ...
    # inarg = MG_JEN_Joneset.DJones_WSRT(_getdefaults=True)  
    inarg = DJones_WSRT(_getdefaults=True)               # local (MG_JEN_Joneset.py) version 
    JEN_inarg.modify(inarg,
                     punit=MG['punit'],                 # source/patch name
                     stations=MG['stations'],           # range of station names/numbers
                     parmtable=MG['parmtable'],         # name of the MeqParm table (AIPS++)
                     
                     # ** Jones matrix elements:
                     polrep=MG['polrep'],               # polarisation representation
                     coupled_XY_dang=True,              # if True, Xdang = Ydang per station
                     coupled_XY_dell=True,              # if True, Xdell = -Ydell per station
                     
                     # ** Solving instructions:
                     unsolvable=False,                  # if True, do not store parmgroup info
                     fdeg_dang=1,                       # degree of default freq polynomial
                     fdeg_dell='fdeg_dang',             # degree of default freq polynomial
                     tdeg_dang=0,                       # degree of default time polynomial
                     tdeg_dell='tdeg_dang',             # degree of default time polynomial
                     tile_size_dang=0,                  # used in tiled solutions         
                     tile_size_dell='tile_size_dang',   # used in tiled solutions         
                     
                     # ** MeqParm default values:
                     c00_dang=0.0,                      # default c00 funklet value
                     c00_dell=0.0,                      # default c00 funklet value
                     c00_PZD=0.8,                       # default c00 funklet value
                     stddev_dang=0.1,                   # scatter in default c00 funklet values
                     stddev_dell=0.1,                   # scatter in default c00 funklet values
                     ft_coeff_scale=1.0,                # scale of polc_ft non-c00 coeff
                     
                     _JEN_inarg_option=None)            # optional, not yet used 
    JEN_inarg.attach(MG, inarg)
   
    #========
    if True:
        # Make a (modified) clone of the DJones_WRT inarg specified above: 
        clone = JEN_inarg.clone(inarg, _qual='independent') # the qualifier changes its identifcation        
        JEN_inarg.modify(clone,
                         coupled_XY_dang=False,             # if True, Xdang = Ydang per station
                         coupled_XY_dell=False,             # if True, Xdell = -Ydell per station
                         _JEN_inarg_option=None)            # optional, not yet used 
        JEN_inarg.attach(MG, clone)
            

#------------------------------------------------------------------------------

#========
if True:                                              # ... Copied from MG_JEN_Joneset.py ...
    # inarg = MG_JEN_Joneset.KJones(_getdefaults=True)     
    inarg = KJones(_getdefaults=True)                    # local (MG_JEN_Joneset.py) version 
    JEN_inarg.modify(inarg,
                     stations=MG['stations'],           # range of station names/numbers
                     _JEN_inarg_option=None)            # optional, not yet used 
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
   jseq = TDL_Joneset.Joneseq(label='JJones', origin='MG_JEN_Joneset')
   
   jseq.append(GJones (ns, _inarg=MG))
   jseq.append(BJones (ns, _inarg=MG))
   jseq.append(FJones (ns, _inarg=MG))
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
    Sixpack = punit2Sixpack(ns, punit='uvp')
    js = KJones (ns, stations=stations, scope=scope, Sixpack=Sixpack)
    js.display()     
    display_first_subtree (js, full=1)

  if 0:
    # jseq = TDL_Joneset.Joneseq(origin='MG_JEN_Joneset')
    jseq = Joneseq()
    jseq.append(GJones (ns, scope=scope, stations=stations))
    jseq.append(BJones (ns, scope=scope, stations=stations))
    jseq.append(FJones (ns, scope=scope, stations=stations))
    # jseq.append(DJones_WSRT (ns, stations=stations))
    jseq.display()
    js = jseq.make_Joneset(ns)
    js.display()     
    display_first_subtree (js, full=1)

  if 0:
    js = GJones (ns, stations=stations)
    dconc = visualise(ns, js)
    MG_JEN_exec.display_object (dconc, 'dconc')
    MG_JEN_exec.display_subtree (dconc, 'dconc', full=1)


  if 1:
    MG_JEN_exec.display_object (MG, 'MG', MG['script_name'])
    # MG_JEN_exec.display_subtree (rr, MG['script_name'], full=1)
  print '\n** End of local test of:',MG['script_name'],'\n*******************\n'

#********************************************************************************
#********************************************************************************




