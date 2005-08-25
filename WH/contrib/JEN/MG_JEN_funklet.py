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

 
   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

#----------------------------------------------------------------------
# Make a 'standard' freq-time polc 

def ft_polc (nfreq=2, ntime=3, c00=1): 
   v = array([[c00,.3,.1],[.3,.1,0.03]])
   polc = meq.polc(v)
   return polc

#----------------------------------------------------------------------
    
   # v = array([[0,.3,.1],[.3,.1,0.03]])
   # stddev = 1
   # mean = complex(-1,-2)
   # vreal = funklet(v, mean=mean.real, stddev=stddev)
   # vimag = funklet(v, mean=mean.imag, stddev=stddev)
   # real = ns[name](qual)(i,'real') << Meq.Parm (vreal, node_groups='Parm')
   # imag = ns[name](qual)(i,'imag') << Meq.Parm (vimag, node_groups='Parm')
   # cc.append(ns[name](qual)(i) << Meq.ToComplex (real, imag))

#----------------------------------------------------------------------
   # mean = 2
   # dflt = funklet(v, mean=mean, stddev=stddev)
   # cc.append(ns[name](qual)(i) << Meq.Parm (dflt, node_groups='Parm'))


#----------------------------------------------------------------------
# Make sure that the funklet is a funklet.
# Perturb the c00 coeff, if required

# array([[1,.3,.1],[.3,.1,0.03]])

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
   return MG_JEN_exec.meqforest (mqs, parent)

#-------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
    if True:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n**',script_name,':\n'
       # ns = NodeScope()
       # ............
       # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
       print '\n** end of',script_name,'\n'

#********************************************************************************
#********************************************************************************





