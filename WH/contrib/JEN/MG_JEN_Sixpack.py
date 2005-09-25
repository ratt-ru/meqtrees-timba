# MG_JEN_Sixpack.py

# Short description (see also the full description below):
#   A template for the generation of MeqGraft (MG) scripts

# Keywords: ....

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation

# Full description (try to be complete, and up-to-date!):


   





#********************************************************************************
#********************************************************************************
#**************** PART II: Preample and initialisation **************************
#********************************************************************************
#********************************************************************************

from Timba.TDL import *

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

from Timba.Contrib.JEN import MG_JEN_funklet
from Timba.Contrib.JEN import MG_JEN_matrix
from Timba.Contrib.JEN import MG_JEN_twig




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








#---------------------------------------------------------------------------------------
# Make Sixpack of subtrees for sources with 'NEWSTAR' parametrization:

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
   # pp = record(pp)
  
   # Adjust parameters pp for some special cases:
   predefined (pp)  
   
   # Make the Sixpack of 6 standard subtree root-nodes: 
   n6 = record(I='stokesI', Q='stokesQ', U='stokesU', V='stokesV', R='ra', D='dec') 
   zero = ns.zero << Meq.Constant(0)
   
   iquv = {}
   parm = {}
   fmult = 1.0
   if pp['SI'] is None:
      parm['I0'] = ns.I0(q=pp['name']) << Meq.Parm(pp['I0'])
      iquv[n6.I] = parm['I0']
   else:
      iquv[n6.I] = MG_JEN_funklet.polclog_flux(ns, source=pp['name'],
                                               I0=pp['I0'], SI=pp['SI'], stokes='stokesI')
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
         # iquv['Q'] = MG_JEN_funklet.polclog_flux(ns, source=pp['name'], stokes='stokesQ')
         # iquv['U'] = MG_JEN_funklet.polclog_flux(ns, source=pp['name'], stokes='stokesU')
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
      wvl2 = MG_JEN_twig.wavelength (ns, qual=None, unop='Sqr')
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

   # Finished: Make the Sixpack and return it
   Sixpack = TDL_Sixpack.Sixpack(label=pp['name'],
                                 stokesI=iquv[n6.I], 
                                 stokesQ=iquv[n6.Q], 
                                 stokesU=iquv[n6.U], 
                                 stokesV=iquv[n6.V], 
                                 ra=radec[n6.R], 
                                 dec=radec[n6.D])
   MG_JEN_forest_state.object(Sixpack)
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
      # Sixpack = newstar_source (ns)
      # Sixpack = newstar_source (ns, name='3c147')
      Sixpack = newstar_source (ns, name='3c286')                    # <------ !!
      # Sixpack = newstar_source (ns, name='QUV', RM=1, SI=-0.7)
      Sixpack.display()
      Sixpack.nodescope(ns)
      MG_JEN_exec.display_subtree (Sixpack.stokesI(), 'stokesI()', full=1)
      MG_JEN_exec.display_subtree (Sixpack.sixpack(), 'sixpack()', full=1)
      MG_JEN_exec.display_subtree (Sixpack.iquv(), 'iquv()', full=1)
      MG_JEN_exec.display_subtree (Sixpack.radec(), 'radec()', full=1)

   print '\n** End of local test of:',MG.script_name,'\n*******************\n'
       
#********************************************************************************
#********************************************************************************




