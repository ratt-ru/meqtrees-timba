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

from Timba.Contrib.JEN import MG_JEN_exec as MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state as MG_JEN_forest_state

# from Timba.Contrib.JEN import MG_JEN_util as MG_JEN_util
from Timba.Contrib.JEN import MG_JEN_math as MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_funklet as MG_JEN_funklet


#================================================================================
# Required functions:
#================================================================================


#--------------------------------------------------------------------------------
# Tree definition routine (may be executed from the browser):
# To be used as example, for experimentation, and automatic testing.

def _define_forest (ns):

   # Generate a list (cc) of one or more root nodes:
   cc = []

   # Test/demo of importable function: .freqtime()
   bb = []
   bb.append(freqtime (ns))
   bb.append(freqtime (ns, combine='ToComplex')) 
   bb.append(freqtime (ns, combine='Add', unop=['Cos','Sin']))  
   cc.append(MG_JEN_exec.bundle(ns, bb, 'freqtime'))

   # Test/demo of importable function: .wavelength()
   bb = []
   bb.append(wavelength (ns))
   bb.append(wavelength (ns, unop='Sqr'))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'wavelength'))

   # Test/demo of importable function: .gaussnoise()
   dims = [1]
   dims = [2,2]
   bb = []
   bb.append(gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims)) 
   bb.append(gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims, unop='Exp'))
   bb.append(gaussnoise (ns, stddev=1, mean=0, complex=True, dims=dims, unop=['Exp','Exp']))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'gaussnoise'))

   # Test/demo of importable function: .cloud()
   bb = cloud (ns, n=3, name='pnt', qual='auto', stddev=1, mean=complex(0))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'cloud'))

   # Finished: 
   return MG_JEN_exec.on_exit (ns, cc)



#--------------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

MG_JEN_forest_state.init(script_name)


#--------------------------------------------------------------------------------
# Tree execution routine (may be called from the browser):
# The 'mqs' argument is a meqserver proxy object.

def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)


#--------------------------------------------------------------------------------
# Test routine to check the tree for consistency in the absence of a server

if __name__ == '__main__':
   MG_JEN_exec.without_meqserver(script_name)









#================================================================================
# Importable function(s): The essence of a MeqGraft (MG) script.
# To be imported into user scripts. 
#================================================================================

#-------------------------------------------------------------------------------
# Make a node that varies with freq and time

def freqtime (ns, qual='auto', combine='Add', unop=False):
    """Make an input node that varies with freq and time:"""
 
    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_twig_freqtime')

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

def wavelength (ns, qual='auto', unop=0):

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_twig_wavelength')

    clight = 2.997925e8
    freq = ns.freq << Meq.Freq()
    wvl = ns.wavelength(qual) << (2.997925e8/freq)
    if isinstance(unop, str):
        wvl = (ns << getattr(Meq,unop)(wvl))
    return wvl


#-------------------------------------------------------------------------------
# Make a node with gaussian noise

def gaussnoise (ns, qual='auto', stddev=1, mean=0, complex=False, dims=[1], unop=False):
    """makes gaussian noise"""

    # If necessary, make an automatic qualifier:
    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_twig_gaussnoise')

    # Determine the nr (nel) of tensor elements:
    if not isinstance(dims, (list, tuple)): dims = [dims]
    nel = sum(dims)
    # print 'nel =',nel

    # NB: What about making/giving stddev as a MeqParm...?

    # The various tensor elements have different noise, of course:
    # NB: Is this strictly necessary? A single GaussNoise node would
    #     be requested separately by each tensor element, and produce
    #     a separate set of values (would it, for the same request..........?)
    #     So a single GaussNoise would be sufficient (for all ifrs!)
    #     provided they would have the same stddev
    cc = []
    for i in range(nel):
	if complex:
		real = ns.real(qual)(i) << Meq.GaussNoise(stddev=stddev)
		imag = ns.imag(qual)(i) << Meq.GaussNoise(stddev=stddev)
		cc.append (ns.gaussnoise(qual)(i) << Meq.ToComplex(children=[real, imag]))
	else:
		cc.append (ns.gaussnoise(qual)(i) << Meq.GaussNoise(stddev=stddev))

    # Make into a tensor node, if necessary:
    output = cc[0]
    if nel>1: 
	output = ns.gaussnoise(qual) << Meq.Composer(children=cc, dims=dims)

    # Optional: Add the specified mean:
    if abs(mean)>0:
	if not complex and isinstance(mean, complex): mean = mean.real
	output = output + mean

    # Optional: Apply zero or more unary operations on the output (e.g Exp):
    output = MG_JEN_math.unop (ns, unop, output) 

    return output


#----------------------------------------------------------------------
# Make a 'cloud' of points (cc) scattered (stddev) around a mean

def cloud (ns, n=3, name='pnt', qual='auto', stddev=1, mean=complex(0)):

    qual = MG_JEN_forest_state.autoqual(qual, 'MG_JEN_twig_cloud')

    cc = []
    v = array([[0,.3,.1],[.3,.1,0.03]])
    if isinstance(mean, complex):
        for i in range(n):
            vreal = MG_JEN_funklet.funklet(v, mean=mean.real, stddev=stddev)
            vimag = MG_JEN_funklet.funklet(v, mean=mean.imag, stddev=stddev)
            real = ns[name](qual)(i,'real') << Meq.Parm (vreal, node_groups='Parm')
            imag = ns[name](qual)(i,'imag') << Meq.Parm (vimag, node_groups='Parm')
            cc.append(ns[name](qual)(i) << Meq.ToComplex (real, imag))
    else:
        for i in range(n):
            dflt = MG_JEN_funklet.funklet(v, mean=mean, stddev=stddev)
            cc.append(ns[name](qual)(i) << Meq.Parm (dflt, node_groups='Parm'))
        
    return cc



#********************************************************************************




