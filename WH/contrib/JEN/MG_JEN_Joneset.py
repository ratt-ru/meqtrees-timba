script_name = 'MG_JEN_Joneset.py'
last_changed = 'h10sep2005'

# Short description:
#   Functions dealing with a set (joneset) of 2x2 station Jones matrices

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation
# - 31 aug 2005: added .visualise()
# - 05 sep 2005: adapted to Joneset object

# Copyright: The MeqTree Foundation 


#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from numarray import *
# from string import *
# from copy import deepcopy

from Timba.Trees import TDL_Joneset

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_matrix
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_twig
from Timba.Contrib.JEN import MG_JEN_dataCollect


#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

    # Make a sequence (jseq) of (jonesets of) 2x2 jones matrices:
   stations = range(0,3)
   scope = script_name
   jseq = TDL_Joneset.Joneseq(label='JJones', origin='MG_JEN_Joneset') 
   jseq.append(GJones (ns, stations=stations, scope=scope, stddev_ampl=0.1, stddev_phase=0.1)) 
   jseq.append(BJones (ns, stations=stations, scope=scope, stddev_real=0.1, stddev_imag=0.1))
   jseq.append(FJones (ns, stations=stations, scope=scope, RM=0.5))
   jseq.append(DJones_WSRT (ns, stations=stations, scope=scope, PZD=0.8, stddev_dang=0.1, stddev_dell=0.1))
   # jseq.append(DJones_WSRT (ns, stations=stations, scope=scope, coupled_XY_dang=False, coupled_XY_dell=False))
   jseq.display()

   # Visualise them individually:
   dconc = []
   for js in jseq:
     dc = visualise(ns, js)
     cc.append(dc['dcoll'])
     dconc.append(dc)

   # Matrix multiply to produce the resulting Jones joneset:
   js = jseq.make_Joneset(ns)
   dc = visualise(ns, js)
   cc.append(dc['dcoll'])
   dconc.append(dc)

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)




#================================================================================
# Optional: Importable function(s): To be imported into user scripts.
#================================================================================





#--------------------------------------------------------------------------------
# Adjust the input arguments (pp) for telescope (dangerous?):

def adjust_for_telescope(pp, origin='<origin>'):
   #------------------------
   return False # inhibited!
   #------------------------
   if not isinstance(pp, dict): return False
   pp = record(pp)

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

def GJones (ns=0, label='GJones', **pp):
  """defines diagonal GJones matrices for complex(ampl,phase) parms""";
  funcname = 'MG_JEN_Joneset::GJones()'

  # Input parameters:
  pp.setdefault('scope', '<scope>')    # scope of this Joneset
  pp.setdefault('stations', [0])       # range of station names/numbers
  pp.setdefault('punit', 'uvp')        # name of prediction-unit (source/patch)
  pp.setdefault('polrep', 'linear')    # polarisation representation
  pp.setdefault('solvable', True)      # if False, do not store parmgroup info
  pp.setdefault('ampl', 1.0)           # default funklet value
  pp.setdefault('phase', 0.0)          # default funklet value
  pp.setdefault('polar', False)        # if True, use MeqPolar, otherwise MeqToComplex
  pp.setdefault('stddev_ampl', 0)      # scatter in default funklet c00 values
  pp.setdefault('stddev_phase', 0)     # scatter in default funklet c00 values
  pp = record(pp)
  adjust_for_telescope(pp, origin=funcname)

  # Create a Joneset object
  js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

  # Register the parmgroups:
  a1 = js.register('Gampl', ipol=1, color='red', corrs='paral1')
  a2 = js.register('Gampl', ipol=2, color='blue', corrs='paral2')
  p1 = js.register('Gphase', ipol=1, color='magenta', corrs='paral1')
  p2 = js.register('Gphase', ipol=2, color='cyan', corrs='paral2')

  # MeqParm node_groups: add 'G' to default 'Parm':
  js.node_groups(label[0])

  # Define extra solvegroup(s) from combinations of parmgroups:
  js.define_solvegroup('GJones', [a1, p1, a2, p2])
  js.define_solvegroup('Gpol1', [a1, p1])
  js.define_solvegroup('Gpol2', [a2, p2])
  js.define_solvegroup('Gampl', [a1, a2])
  js.define_solvegroup('Gphase', [p1, p2])

  for station in pp.stations:
    skey = str(station)                 # station key, e.g. 's2'
    # Define station MeqParms (in ss), and do some book-keeping:  
    js.MeqParm(reset=True)

    default = MG_JEN_funklet.polc_ft (c00=pp.ampl, stddev=pp.stddev_ampl) 
    js.define_MeqParm(ns, a1, station=skey, default=default)

    default = MG_JEN_funklet.polc_ft (c00=pp.ampl, stddev=pp.stddev_ampl) 
    js.define_MeqParm(ns, a2, station=skey, default=default)

    default = MG_JEN_funklet.polc_ft (c00=pp.phase, stddev=pp.stddev_phase) 
    js.define_MeqParm(ns, p1, station=skey, default=default)

    default = MG_JEN_funklet.polc_ft (c00=pp.phase, stddev=pp.stddev_phase) 
    js.define_MeqParm(ns, p2, station=skey, default=default)

    ss = js.MeqParm(update=True)

    # Make the 2x2 Jones matrix:
    if pp.polar:
      stub = ns[label](s=skey, q=pp.punit) << Meq.Matrix22 (
        ns[label+'_11'](s=skey, q=pp.punit) << Meq.Polar( ss[a1], ss[p1]),
        0,0,
        ns[label+'_22'](s=skey, q=pp.punit) << Meq.Polar( ss[a2], ss[p2])
        )
    else:
      cos1 = ns << ss[a1] * Meq.Cos(ss[p1])
      cos2 = ns << ss[a2] * Meq.Cos(ss[p2])
      sin1 = ns << ss[a1] * Meq.Sin(ss[p1])
      sin2 = ns << ss[a2] * Meq.Sin(ss[p2])
      stub = ns[label](s=skey, q=pp.punit) << Meq.Matrix22 (
        ns[label+'_11'](s=skey, q=pp.punit) << Meq.ToComplex( cos1, sin1),
        0,0,
        ns[label+'_22'](s=skey, q=pp.punit) << Meq.ToComplex( cos2, sin2)
        )
    js.append(skey, stub)


  # Finished:
  js.cleanup()
  MG_JEN_forest_state.object(js, funcname)
  return js


#--------------------------------------------------------------------------------
# FJones: 2x2 matrix for ionospheric Faraday rotation (NOT ion.phase!)
#--------------------------------------------------------------------------------

def FJones (ns=0, label='FJones', **pp):
  """defines diagonal FJones Faraday rotation matrices""";
  funcname = 'MG_JEN_Joneset::FJones()'

  # Input parameters:
  pp.setdefault('scope', '<scope>')    # scope of this Joneset
  pp.setdefault('stations', [0])       # range of station names/numbers
  pp.setdefault('punit', 'uvp')        # name of prediction-unit (source/patch)
  pp.setdefault('polrep', 'linear')    # polarisation representation
  pp.setdefault('solvable', True)      # if True, the parms are potentially solvable
  pp.setdefault('RM', 0.0)             # default funklet value
  pp = record(pp)
  adjust_for_telescope(pp, origin=funcname)

  # Create a Joneset object:
  js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

  # Register the parmgroups:
  RM = js.register('RM', color='black', corrs='cross')

  # MeqParm node_groups: add 'F' to default 'Parm':
  js.node_groups(label[0])

  # Define extra solvegroup(s) from combinations of parmgroups:
  js.define_solvegroup('FJones', [RM])

  # Make a node for the Faraday rotation (same for all stations...)
  js.MeqParm(reset=True)
  js.define_MeqParm(ns, RM, default=pp.RM)              # Rotation Measure
  ss = js.MeqParm(update=True)
  wvl2 = MG_JEN_twig.wavelength (ns, unop='Sqr')        # -> lambda squared
  farot = ns.farot(q=pp.punit) << (ss[RM] * wvl2)       # Faraday rotation angle
  
  # The FJones matrix depends on the polarisation representation:
  if pp.polrep=='circular':
     matname = 'FJones_phase_matrix'
     stub = MG_JEN_matrix.phase (ns, angle=farot, name=matname)
  else:
     matname = 'FJones_rotation_matrix'
     stub = MG_JEN_matrix.rotation (ns, angle=farot, name=matname)

  # For the moment, assume that FJones is the same for all stations:
  for station in pp.stations:
     skey = str(station)
     js.append(skey, stub)

  # Finished:
  js.cleanup()
  MG_JEN_forest_state.object(js, funcname)
  return js



#--------------------------------------------------------------------------------
# BJones: diagonal 2x2 matrix for complex bandpass per polarization
#--------------------------------------------------------------------------------

def BJones (ns=0, label='BJones', **pp):
  """defines diagonal BJones bandpass matrices""";
  funcname = 'MG_JEN_Joneset::BJones()'

  # Input parameters:
  pp.setdefault('scope', '<scope>')    # scope of this Joneset
  pp.setdefault('stations', [0])       # range of station names/numbers
  pp.setdefault('punit', 'uvp')        # name of prediction-unit (source/patch)
  pp.setdefault('solvable', True)      # if True, the parms are potentially solvable
  pp.setdefault('polar', False)        # if True, use MeqPolar, otherwise MeqToComplex
  pp.setdefault('real', 1.0)           # default funklet value
  pp.setdefault('imag', 0.0)           # default funklet value
  pp.setdefault('stddev_real', 0)      # scatter in default funklet c00 values
  pp.setdefault('stddev_imag', 0)      # scatter in default funklet c00 values
  pp.setdefault('fdeg', 3)             # degree of default freq polynomial              # <---- !!
  pp.setdefault('tdeg', 0)             # degree of default time polynomial              # <---- !!
  pp = record(pp)
  adjust_for_telescope(pp, origin=funcname)

  # Create a Joneset object:
  js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)
  
  # Register the parmgroups:
  br1 = js.register('Breal', ipol=1, color='red', corrs='paral1')
  br2 = js.register('Breal', ipol=2, color='blue', corrs='paral2')
  bi1 = js.register('Bimag', ipol=1, color='magenta', corrs='paral1')
  bi2 = js.register('Bimag', ipol=2, color='cyan', corrs='paral2')

  # MeqParm node_groups: add 'B' to default 'Parm':
  js.node_groups(label[0])

  # Define extra solvegroup(s) from combinations of parmgroups:
  js.define_solvegroup('BJones', [br1, bi1, br2, bi2])
  js.define_solvegroup('Bpol1', [br1, bi1])
  js.define_solvegroup('Bpol2', [br2, bi2])
  js.define_solvegroup('Breal', [br1, br2])
  js.define_solvegroup('Bimag', [bi1, bi2])

  for station in pp.stations:
    skey = str(station)                 # station key, e.g. 's2'
    # Define station MeqParms (in ss), and do some book-keeping:  
    js.MeqParm(reset=True)

    # polc_ft (c00=1, fdeg=0, tdeg=0, scale=1, mult=1/sqrt(10), stddev=0) 

    default = MG_JEN_funklet.polc_ft (c00=pp.real, stddev=pp.stddev_real,
                                      fdeg=pp['fdeg'], tdeg=pp['tdeg']) 
    js.define_MeqParm(ns, br1, station=skey, default=default)

    default = MG_JEN_funklet.polc_ft (c00=pp.real, stddev=pp.stddev_real, 
                                      fdeg=pp['fdeg'], tdeg=pp['tdeg']) 
    js.define_MeqParm(ns, br2, station=skey, default=default)

    default = MG_JEN_funklet.polc_ft (c00=pp.imag, stddev=pp.stddev_imag, 
                                      fdeg=pp['fdeg'], tdeg=pp['tdeg']) 
    js.define_MeqParm(ns, bi1, station=skey, default=default)

    default = MG_JEN_funklet.polc_ft (c00=pp.imag, stddev=pp.stddev_imag, 
                                      fdeg=pp['fdeg'], tdeg=pp['tdeg']) 
    js.define_MeqParm(ns, bi2, station=skey, default=default)

    ss = js.MeqParm(update=True)

    # Make the 2x2 Jones matrix
    stub = ns[label](s=skey, q=pp.punit) << Meq.Matrix22 (
      ns[label+'_11'](s=skey, q=pp.punit) << Meq.ToComplex(ss[br1], ss[bi1]),
      0,0,
      ns[label+'_22'](s=skey, q=pp.punit) << Meq.ToComplex(ss[br2], ss[bi2])
      )
    js.append(skey, stub)

  # Finished:
  js.cleanup()
  MG_JEN_forest_state.object(js, funcname)
  return js





#--------------------------------------------------------------------------------
# DJones: 2x2 matrix for polarization leakage
#--------------------------------------------------------------------------------

def DJones_WSRT (ns=0, label='DJones_WSRT', **pp):
  """defines 2x2 DJones_WSRT (polarisation leakage) matrices""";
  funcname = 'MG_JEN_Joneset::DJones_WSRT()'

  # Input parameters:
  pp.setdefault('scope', '<scope>')       # scope of this Joneset
  pp.setdefault('stations', [0])          # range of station names/numbers
  pp.setdefault('punit', 'uvp')           # name of prediction-unit (source/patch)
  pp.setdefault('solvable', True)         # if True, the parms are potentially solvable
  pp.setdefault('coupled_XY_dang', True)  # if True, Xdang = Ydang per station
  pp.setdefault('coupled_XY_dell', True)  # if True, Xdell = -Ydell per station
  pp.setdefault('dang', 0.0)              # default funklet value
  pp.setdefault('dell', 0.0)              # default funklet value
  pp.setdefault('PZD', 0.0)               # default funklet value
  pp.setdefault('stddev_dang', 0)         # scatter in default funklet c00 values
  pp.setdefault('stddev_dell', 0)         # scatter in default funklet c00 values
  pp = record(pp)
  adjust_for_telescope(pp, origin=funcname)

  # Create a Joneset object:
  js = TDL_Joneset.Joneset(label=label, origin=funcname, **pp)

  # Register the parmgroups:
  dang = js.register('dang', color='green', corrs='cross')
  dell = js.register('dell', color='magenta', corrs='cross')
  dang1 = js.register('dang', ipol=1, color='green', corrs='cross')
  dang2 = js.register('dang', ipol=2, color='black', corrs='cross')
  dell1 = js.register('dell', ipol=1, color='magenta', corrs='cross')
  dell2 = js.register('dell', ipol=2, color='yellow', corrs='cross')
  pzd = js.register('PZD', color='black', corrs='cross')

  # MeqParm node_groups: add 'D' to default 'Parm':
  js.node_groups(label[0])

  # Define extra solvegroup(s) from combinations of parmgroups:
  if pp.coupled_XY_dang and pp.coupled_XY_dell:
    js.define_solvegroup('DJones', [dang, dell, pzd])
  elif pp.coupled_XY_dang:
    js.define_solvegroup('DJones', [dang, dell1, dell2, pzd])
    js.define_solvegroup('dell', [dell1, dell2, pzd])
  elif pp.coupled_XY_dell:
    js.define_solvegroup('DJones', [dang1, dang2, dell, pzd])
    js.define_solvegroup('dang', [dang1, dang2, pzd])
  else:
    js.define_solvegroup('DJones', [dang1, dang2, dell1, dell2, pzd])
    js.define_solvegroup('dang', [dang1, dang2, pzd])
    js.define_solvegroup('dell', [dell1, dell2, pzd])

  # The X/Y Phase-Zero-Difference (PZD) is shared by all stations:
  js.MeqParm(reset=True)
  js.define_MeqParm(ns, pzd, default=pp.PZD)
  ss = js.MeqParm(update=True)
  matname = 'DJones_PZD_matrix'
  pmat = MG_JEN_matrix.phase (ns, angle=ss[pzd], name=matname)


  # Make the jones matrices per station:
  jones = {}
  ss = {}
  for station in pp.stations:
    skey = str(station)                 # station key, e.g. 's2'
    # Define station MeqParms (in ss), and do some book-keeping:  
    js.MeqParm(reset=True)
    qual = None

    # Dipole angle errors may be coupled (dang(X)=dang(Y)) or not:
    matname = 'DJones_dang_matrix'
    if pp.coupled_XY_dang:
       default = MG_JEN_funklet.polc_ft (c00=pp.dang, stddev=pp.stddev_dang) 
       js.define_MeqParm(ns, dang, station=skey, default=default)
       ss = js.MeqParm(update=True, reset=True)
       rmat = MG_JEN_matrix.rotation (ns, angle=ss[dang], qual=qual, name=matname)
    else: 
       default = MG_JEN_funklet.polc_ft (c00=pp.dang, stddev=pp.stddev_dang) 
       js.define_MeqParm(ns, dang1, station=skey, default=default)
       default = MG_JEN_funklet.polc_ft (c00=pp.dang, stddev=pp.stddev_dang) 
       js.define_MeqParm(ns, dang2, station=skey, default=default)
       ss = js.MeqParm(update=True, reset=True)
       rmat = MG_JEN_matrix.rotation (ns, angle=[ss[dang1],ss[dang2]], qual=qual, name=matname)


    # Dipole ellipticities may be coupled (dell(X)=-dell(Y)) or not:
    matname = 'DJones_dell_matrix'
    if pp.coupled_XY_dell:
       default = MG_JEN_funklet.polc_ft (c00=pp.dell, stddev=pp.stddev_dell) 
       js.define_MeqParm(ns, dell, station=skey, default=default)
       ss = js.MeqParm(update=True, reset=True)
       emat = MG_JEN_matrix.ellipticity (ns, angle=ss[dell], qual=qual, name=matname)
    else:
       default = MG_JEN_funklet.polc_ft (c00=pp.dell, stddev=pp.stddev_dell) 
       js.define_MeqParm(ns, dell1, station=skey, default=default)
       default = MG_JEN_funklet.polc_ft (c00=pp.dell, stddev=pp.stddev_dell) 
       js.define_MeqParm(ns, dell2, station=skey, default=default)
       ss = js.MeqParm(update=True, reset=True)
       emat = MG_JEN_matrix.ellipticity (ns, angle=[ss[dell1],ss[dell2]], qual=qual, name=matname)

    # Make the 2x2 Jones matrix by multiplying the sub-matrices:
    stub = ns[label](s=skey, q=pp.punit) << Meq.MatrixMultiply (rmat, emat, pmat)
    js.append(skey, stub)

  # Finished:
  js.cleanup()
  MG_JEN_forest_state.object(js, funcname)
  return js





#======================================================================================
# Joneset/Joneseq visualisation:
#======================================================================================


#======================================================================================
# Visualise the contents of the given Joneseq object:

def visualise_Joneseq (ns, Joneseq, **pp):
    """visualises the contents of the given Joneseq"""

    dconc = []
    for js in Joneseq:
      dc = visualise(ns, js, **pp)
      print '****',js.label(),dc
      dconc.append(dc)
    js = Joneseq.make_Joneset(ns)
    dc = visualise(ns, js, **pp)
    print '****',dc
    dconc.append(dc)
    # return True

    # Make a concatenation of the various dcolls:
    dconc = MG_JEN_dataCollect.dconc (ns, dconc, scope=Joneset.scope(),
                                      bookpage='Joneseq')

    # Return a dcoll record (dataCollect node = dcond['dcoll'])
    return dconc



#======================================================================================
# Visualise the contents of the given Joneset object:

def visualise(ns, Joneset, **pp):
    """visualises the contents of the given Joneset"""

    # Input arguments:
    pp.setdefault('type', 'realvsimag')     # plot type (realvsimag or spectra)
    pp.setdefault('errorbars', False)       # if True, plot stddev as crosses around mean
    pp.setdefault('result', 'Joneset')      # result of this routine (Joneset or dcolls)
    pp = record(pp)

    # Use a sub-scope where node-names are prepended with name
    # and may have other qualifiers: nsub = ns.subscope(name, '[qual_list]')
    label = Joneset.label()                 # e.g. GJones
    visu_scope = 'visu_'+Joneset.scope()+'_'+label
  
    # Make dcolls per parm group:
    dcoll = []
    for key in Joneset.parmgroup().keys():
       pgk = Joneset.parmgroup()[key]        # list of MeqParm node names
       if len(pgk)>0:  # ignore if empty 
          dc = MG_JEN_dataCollect.dcoll (ns, pgk, scope=visu_scope, tag=key,
                                         type=pp.type, errorbars=pp.errorbars,
                                         color=Joneset.plot_color()[key],
                                         style=Joneset.plot_style()[key])
          dcoll.append(dc)


    # Make dcolls per matrix element:
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
       style = 'cross'
       if key=='m12' or key=='m21':
           size = 7
           color = 'gray'
       dc = MG_JEN_dataCollect.dcoll (ns, nodes[key],
                                    scope=visu_scope, tag=key,
                                    type=pp.type,
                                    color=color, style=style, size=size,
                                    errorbars=pp.errorbars)
       dcoll.append(dc)

 
    # Make a concatenation of the various dcolls:
    dconc = MG_JEN_dataCollect.dconc (ns, dcoll, scope=visu_scope, bookpage=label)
    
    # Return a dcoll record (dataCollect node = dcond['dcoll'])
    return dconc


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




#==========================================================================
# Some convenience functions:
#==========================================================================


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
  if 0:
      MG_JEN_exec.without_meqserver(script_name, callback=_define_forest)

  ns = NodeScope()
  stations = range(0,3)
  scope = script_name
  ifrs  = [ (s1,s2) for s1 in stations for s2 in stations if s1<s2 ];

  if 0:
    # js = GJones (ns, stations=stations, scope=scope, solvable=True, polrep='circular', polar=True)
    js = BJones (ns, stations=stations, scope=scope, solvable=True, polrep='circular')
    # js = FJones (ns, stations=stations, scope=scope, solvable=True, polrep='circular')
    # js = FJones (ns, stations=stations, scope=scope, solvable=True, polrep='linear')
    # js = DJones_WSRT (ns, stations=stations, sscope=scope, olvable=True, coupled_XY_dang=False, coupled_XY_dell=True)
    js.display()     
    display_first_subtree (js, full=1)

  if 1:
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


  print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




