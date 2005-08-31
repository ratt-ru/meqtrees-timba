script_name = 'MG_JEN_funklet.py'

# Short description:
#   Demo and helper functions for the family of funklets

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 


#================================================================================
# Import of Python modules:

from Timba.TDL import *
from Timba.Meq import meq

from random import *
from math import *
from numarray import *
# from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec as MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state as MG_JEN_forest_state




#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.
#================================================================================

def _define_forest (ns):

   # Generate a list (cc) of one or more node bundles (bb):
   cc = []

   # Demo of importable function: polc_ft()
   bb = []
   for i in range(3):
      polc = polc_ft(c00=i, nfreq=2, ntime=3, scale=1e-10, stddev=0.0)
      bb.append(ns.polc_ft(i) << Meq.Parm(polc))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'polc_ft()'))

   # Demo of importable function: polclog_SIF()
   bb = []
   bb.append(ns.polclog_SIF << Meq.Parm(polclog_SIF()))
   bb.append(ns.polclog_SIF(SI=0) << Meq.Parm(polclog_SIF(SI=0)))
   bb.append(ns.polclog_SIF(I0=10) << Meq.Parm(polclog_SIF(I0=10)))
   bb.append(ns.polclog_SIF(I0='e') << Meq.Parm(polclog_SIF(I0=e)))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'polclog_SIF()'))

   # Demo of importable function: polclog_StokesI()
   bb = []
   bb.append(polclog_StokesI(ns))
   bb.append(polclog_StokesI(ns, '10', I0=10))
   bb.append(polclog_StokesI(ns, '3c147'))
   bb.append(polclog_StokesI(ns, '3c295')) 
   bb.append(polclog_StokesI(ns, '3c48')) 
   bb.append(polclog_StokesI(ns, '3c268'))

   cc.append(MG_JEN_exec.bundle(ns, bb, 'polclog_StokesI()'))


   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------------
# Make a 'standard' freq-time polc with the following features:
# - nfreq and ntime give the polynomial degree in these dimensions
# - the constant coeff (c00) is specified explicitly
# - the other coeff are generated with an algorithm:
#   - first they are all set to the same value (=scale)
#   - then they are 'attenuated' (more for higher-order coeff)
#   - their sign is alternated between -1 and 1
# - If stddev>0, a 'proportional' random number is added to each coeff

def polc_ft (c00=1, nfreq=0, ntime=0, scale=1, mult=1/sqrt(10), stddev=0): 
 
   # If the input is a polc (funklet) already, just return it ......??
   if isinstance(c00, dmi_type('MeqFunklet')):
	return c00

   # Create a coeff array with the correct dimensions.
   # All coeff have the same value (=scale), see also below
   scale = float(scale)
   coeff = resize(array(scale), (nfreq+1,ntime+1))

   # Multiply each coeff with sign*mult**(i+j)
   # If mult<1, this makes the higher-order coeff smaller
   sign = 1.0
   for i in range(nfreq+1):
      for j in range(ntime+1):
         factor = mult**(i+j)                               # depends on polynomial degree                
         coeff[i,j] *= (sign*factor)                       # attenuate, and apply the sign
         if (i+j)==0: coeff[0,0] = c00                # override the constant coeff c00
         if stddev > 0:
            # Optional: Add some gaussian scatter to the coeff value
            # NB: If stddev=0, the coeff values are fully predictable!
            coeff[i,j] += gauss(0.0, stddev*factor)   # add 'proportional' scatter,    
         sign *=-1                                                 # negate the sign for the next coeff                                 

  # NB: Should we set the lower-right triangle coeff to zero?  

  # Make the polc:
   polc = meq.polc(coeff)
   return polc


# NB: The polcs generated with this function are given to MeqParms as default funklets.
#     This is their ONLY use....
#     However, the MeqParm default funklets are used if no other funklets are known.
#     When used, their domains are ignored: It is assumed that their coeff are valid
#     for the requested domain, which may be anything....
#     So: It  might be reasonable to demand that MeqParms default funklets are c00 only!?
#     However: If the requested domain is automatically scaled back to (0-1) (under what
#              conditions?), the polc_ft() should be tested with requested domain (0-1)
#     After all, it IS nice to be able to make a (t,f) variable MeqParm.......



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
   print oneliner(polclog, 'polclog_SIF')
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

def polclog_StokesI (ns, source=None, I0=1.0, SI=-0.7, f0=1e6): 
   if not isinstance(source, str):
	source = MG_JEN_forest_state.autoqual(source, 'MG_JEN_funklet_StokesI')

   polclog = polclog_predefined(source, I0=I0, SI=SI, f0=f0)
   SIF = ns.SIF(q=source) << Meq.Parm(polclog)
   node = ns.StokesI(q=source) << Meq.Pow(10.0, SIF)
   print '** polclog_StokesI(',source,') ->',node
   return node

#---------------------------------------------------------------------
# Make a fmult(q=source) node based on a polclog:
# This may be used to multiply StokesQ,U,V.....

def polclog_fmult (ns, source=None, SI=-0.7, f0=1e6):
   if not isinstance(source, str):
	source = MG_JEN_forest_state.autoqual(source, 'MG_JEN_funklet_fmult')
   polclog = polclog_predefined(source, I0=1.0, SI=SI, f0=f0)
   SIF = ns.SIF(q=source) << Meq.Parm(polclog)
   node = ns.mult(q=source) << Meq.Pow(10.0, SIF)
   # node = ns << Meq.Pow(10.0, SIF)               # <--- better?
   print '** polclog_fmult(',source,') ->',node
   return node
   
#---------------------------------------------------------------------
# Predefined polclog definitions of selected sources:

def polclog_predefined (source='<source>', SI=-0.7, I0=1.0, f0=1e6):

   if source=='3c147':	
      polclog = polclog_SIF (I0=10**1.766, SI=[0.447, -0.148], f0=1e6)
   elif source =='3c48':	
      polclog = polclog_SIF (I0=10**2.345, SI=[0.071, -0.138], f0=1e6)
   elif source =='3c295':	
      polclog = polclog_SIF (I0=10**1.485, SI=[0.759, -0.255], f0=1e6)
      
   elif source =='3c268':	
      polclog = polclog_SIF (I0=10**1.48, SI=[0.292, -0.124], f0=1e6)
      # Q_polclog = polclog_SIF (I0=2.735732, SI=[-0.923091, 0.073638], f0=1e6)
      # U_polclog = polclog_SIF (I0=6.118902, SI=[-2.05799, 0.163173], f0=1e6)
      #    pp['I0'] = 10**1.48
      #    pp['SI'] = [0.292, -0.124]
      #    pp['Q'] = [2.735732, -0.923091, 0.073638]
      #    pp['U'] = [6.118902, -2.05799, 0.163173]
      
   else:
      # If source not recognised, use the other arguments:
      polclog = polclog_SIF (SI=SI, I0=I0, f0=f0)

   print '** polclog_predefined(',source,') ->',polclog
   return polclog




#======================================================================
# Functions related to general funklets 
#======================================================================

#----------------------------------------------------------------------
# Turn the given funklet into a one-liner string: 

def oneliner (funklet, txt=None):
   s = str(funklet)
   if isinstance (txt, str): s = str(txt)+':'+s
   return s

#----------------------------------------------------------------------
# Make sure that the input (funkin) is a funklet.
# Perturb the c00 coeff, if required
# NB: Semi-obsolete (replace with polc_ft() above........

def funklet (funkin, mean=0, stddev=0):
    if isinstance(funkin, dmi_type('MeqFunklet')):
        funklet = deepcopy(funkin)
    elif isinstance(funkin,type(array(0))):
        funklet = meq.polc(deepcopy(funkin))
    else:
        funklet = meq.polc(deepcopy(funkin))

    if mean != 0 or stddev > 0:
        if (funklet['coeff'].rank==0):
            funklet['coeff'] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==1):
            funklet['coeff'][0] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==2):
            funklet['coeff'][0,0] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==3):
            funklet['coeff'][0,0,0] += gauss(mean, stddev)
        elif (funklet['coeff'].rank==4):
            funklet['coeff'][0,0,0,0] += gauss(mean, stddev)
        else:
            print '\n** JEN_funklet error: rank =',funklet['coeff'].rank

    return funklet






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
  # return MG_JEN_exec.meqforest (mqs, parent)
  # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False)
  return MG_JEN_exec.meqforest (mqs, parent, nfreq=200, f1=1e6, f2=2e8, t1=-10, t2=10) 
  # return MG_JEN_exec.meqforest (mqs, parent, domain='lofar')

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    if False:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n**',script_name,':\n'
       ns = TDL.NodeScope()

       if 0:
          # polc = polc_ft(c00=2, nfreq=2, ntime=3)
          print oneliner(polc_ft())
          print oneliner(polc_ft(c00=10, stddev=1))
          print oneliner(polc_ft(nfreq=0, ntime=1))
          print oneliner(polc_ft(nfreq=1, ntime=0))
          print oneliner(polc_ft(nfreq=1, ntime=1))
          print oneliner(polc_ft(nfreq=0, ntime=2))
          print oneliner(polc_ft(nfreq=2, ntime=3))
          print oneliner(polc_ft(nfreq=2, ntime=3, stddev=1))

       if 0:
          # polclog = polclog_SIF (SI=0, I0=1.0)
          print oneliner(polclog_SIF())
          print oneliner(polclog_SIF())
          print oneliner(polclog_SIF(0))
          print oneliner(polclog_SIF(I0=10))
          print oneliner(polclog_SIF(I0=e))

       # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
       print '\n** end of',script_name,'\n'

#********************************************************************************
#********************************************************************************





