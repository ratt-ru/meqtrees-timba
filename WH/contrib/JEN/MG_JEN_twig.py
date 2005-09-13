script_name = 'MG_JEN_twig.py'

# Short description:
#   Various input subtrees (twigs)  

# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

# Copyright: The MeqTree Foundation 


# Import Python modules:
from Timba.TDL import *
from Timba.Meq import meq

from random import *
from numarray import *
from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_funklet




#================================================================================
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):
   MG_JEN_exec.on_entry (ns, script_name)

   # Generate a list (cc) of one or more root nodes:
   cc = []

   # Test/demo of importable function: .freqtime()
   bb = []
   bb.append(freqtime (ns))
   bb.append(freqtime (ns, combine='ToComplex')) 
   bb.append(freqtime (ns, combine='Add', unop=['Cos','Sin']))  
   cc.append(MG_JEN_exec.bundle(ns, bb, '.freqtime()'))

   # Test/demo of importable function: .wavelength()
   bb = []
   bb.append(wavelength (ns))
   bb.append(wavelength (ns, unop='Sqr'))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.wavelength()'))

   # Test/demo of importable function: .gaussnoise()
   dims = [1]
   dims = [2,2]
   bb = []
   bb.append(gaussnoise (ns)) 
   bb.append(gaussnoise (ns, stddev=1, mean=-1, dims=dims)) 
   bb.append(gaussnoise (ns, stddev=1, mean=complex(0), dims=dims)) 
   bb.append(gaussnoise (ns, stddev=1, mean=complex(0), dims=dims, unop='Exp'))
   bb.append(gaussnoise (ns, stddev=1, mean=complex(0), dims=dims, unop=['Exp','Exp']))
   cc.append(MG_JEN_exec.bundle(ns, bb, '.gaussnoise()'))

   # Test/demo of importable function: .cloud()
   bb = cloud (ns, n=3, name='pnt', stddev=1, mean=complex(0))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'cloud'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, script_name, cc)





#================================================================================
# Optional: Importable function(s): To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------
# Make a node that varies with freq and time

def freqtime (ns, qual=None, combine='Add', unop=False):
    """Make an input node that varies with freq and time:"""
 
    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_twig_freqtime', qual=qual)

    # Make the basic freq-time nodes:
    freq = ns.time(qual) << Meq.Freq()
    time = ns.freq(qual) << Meq.Time()

    # Combine them (e.g. e.g. adding):
    output = ns.freqtime(qual) << getattr(Meq,combine)(children=[freq, time])

    # Optional: Apply zero or more unary operations on the output:
    output = MG_JEN_math.unop (ns, unop, output) 

    # Finished:
    return output

#----------------------------------------------------------------------
# Calculate unop(wavelength):

def wavelength (ns, qual=None, unop=0):

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_twig_wavelength', qual=qual)

    clight = 2.997925e8
    freq = ns.freq << Meq.Freq()
    wvl = ns.wavelength(qual) << (2.997925e8/freq)
    if isinstance(unop, str):
        wvl = (ns << getattr(Meq,unop)(wvl))
    return wvl


#-------------------------------------------------------------------------------
# Make a node with gaussian noise
#   NB: complex if mean is complex

def gaussnoise (ns, qual=None, stddev=1, mean=0, dims=[1], unop=False):
    """makes gaussian noise"""

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual('MG_JEN_twig_gaussnoise', qual=qual)

    # Determine the nr (nel) of tensor elements:
    if not isinstance(dims, (list, tuple)): dims = [dims]
    nel = sum(dims)
    print dims,'nel=',nel

    # NB: What about making/giving stddev as a MeqParm...?

    # The various tensor elements have different noise, of course:
    # NB: Is this strictly necessary? A single GaussNoise node would
    #     be requested separately by each tensor element, and produce
    #     a separate set of values (would it, for the same request..........?)
    #     So a single GaussNoise would be sufficient (for all ifrs!)
    #     provided they would have the same stddev

    output = []
    for i in range(nel):
 	if isinstance(mean, complex):
		real = ns.real(qual)(i) << Meq.GaussNoise(stddev=stddev)
		imag = ns.imag(qual)(i) << Meq.GaussNoise(stddev=stddev)
		output.append (ns.gaussnoise(qual)(i) << Meq.ToComplex(children=[real, imag]))
	else:
		output.append (ns.gaussnoise(qual)(i) << Meq.GaussNoise(stddev=stddev))
 
    # Make into a tensor node, if necessary:
    if nel>1: 
	output = ns.gaussnoise(qual) << Meq.Composer(children=output, dims=dims)
    else:
	output = output[0]

    # Optional: Add the specified mean:
    if abs(mean)>0: output = ns << output + mean

    # Optional: Apply zero or more unary operations on the output (e.g Exp):
    output = MG_JEN_math.unop (ns, unop, output) 

    return output


#----------------------------------------------------------------------
# Make a 'cloud' of points (cc) scattered (stddev) around a mean

def cloud (ns, n=3, name='pnt', qual=None, stddev=1, mean=complex(0)):

    qual = MG_JEN_forest_state.autoqual('MG_JEN_twig_cloud', qual=qual)

    cc = []
    v = array([[0,.3,.1],[.3,.1,0.03]])
    if isinstance(mean, complex):
        for i in range(n):
            vreal = MG_JEN_funklet.polc_ft(c00=mean.real, fdeg=3, tdeg=2, stddev=stddev)
            vimag = MG_JEN_funklet.polc_ft(c00=mean.imag, fdeg=3, tdeg=2, stddev=stddev)
            real = ns[name](qual)(i,'real') << Meq.Parm (vreal, node_groups='Parm')
            imag = ns[name](qual)(i,'imag') << Meq.Parm (vimag, node_groups='Parm')
            cc.append(ns[name](qual)(i) << Meq.ToComplex (real, imag))
    else:
        for i in range(n):
            dflt = MG_JEN_funklet.polc_ft(c00=mean, fdeg=3, tdeg=2, stddev=stddev)
            cc.append(ns[name](qual)(i) << Meq.Parm (dflt, node_groups='Parm'))
        
    return cc



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
    if False:
        # This is the default:
        MG_JEN_exec.without_meqserver(script_name)

    else:
       # This is the place for some specific tests during development.
       print '\n*******************\n** Local test of:',script_name,':\n'
       ns = NodeScope()
       freqtime (ns, qual=None, combine='Add', unop=False)
       # ............
       # MG_JEN_display_object (rr, 'rr', script_name)
       # MG_JEN_exec.display_subtree (rr, 'rr', full=1)
       print '\n** End of local test of:',script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




