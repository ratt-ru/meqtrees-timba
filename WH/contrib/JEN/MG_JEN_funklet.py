script_name = 'MG_JEN_funklet.py'

# Short description:
#   Demo and helper functions for the family of funklets

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 24 aug 2005: creation

# Copyright: The MeqTree Foundation 


#================================================================================
# Import of Python modules:

from Timba import TDL
from Timba.TDL import dmi_type, Meq
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


#----------------------------------------------------------------------
# Make a polclog for a freq-dependent spectral index:


def polclog_SIF (SI=-0.7, I0=1.0):
   SIF = [log(I0)/log(10)]                        # Make 10log(), because Python log() is e-log
   # NB: what if I0 is polc???
   if not isinstance(SI, list): SI = [SI]
   SIF.extend(SI)                                     # NB: SIF[1] = classical S.I.
   SIF = array(SIF)
   SIF = reshape(SIF, (1,len(SIF)))
   polclog = meq.polclog(SIF)                 # NB: what is the default f0?? 1Hz!
   return polclog


#    if len(SI) == 1:
#       print type(ns)
#       parm['I0'] = (ns.I0(q=pp['name']) << Meq.Parm(pp['I0']))
#       parm['SI'] = (ns.SI(q=pp['name']) << Meq.Parm(pp['SI']))
#       freq = (ns.freq << Meq.Freq())
#       fratio = (ns.fratio(q=pp['name']) << (freq/pp['f0']))
#       fmult = (ns.fmult(q=pp['name']) << Meq.Pow(fratio, parm['SI']))
#       iquv[n6.I] = (ns[n6.I](q=pp['name']) << (parm['I0'] * fmult))




#----------------------------------------------------------------------
# Functions related to general funklets 
#----------------------------------------------------------------------

#----------------------------------------------------------------------
# Turn the given funklet into a one-liner string: 

def oneliner (funklet):
   s = str(funklet)
   return s

#----------------------------------------------------------------------
# Make sure that the input (funkin) is a funklet.
# Perturb the c00 coeff, if required

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
  # print 'run test_forest',script_name 
  # return MG_JEN_exec.meqforest (mqs, parent)
  # return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, f1=0, f2=1, t1=0, t2=1, trace=False) 
  return MG_JEN_exec.meqforest (mqs, parent, nfreq=20, ntime=19, domain='lofar')

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





