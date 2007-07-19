# MG_JEN_twig.py

# Short description:
#   Various convenience subtrees (twigs) for simulated input 

# and The MeqTree Foundation
# Author: Jan Noordam (JEN), Dwingeloo

# History:
# - 22 aug 2005: creation

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

from random import *
from numarray import *
from string import *
from copy import deepcopy

from Timba.Contrib.JEN import MG_JEN_exec
from Timba.Contrib.JEN import MG_JEN_forest_state
from Timba.Contrib.JEN import MG_JEN_math
from Timba.Contrib.JEN import MG_JEN_funklet

from Timba.Contrib.MXM import MG_MXM_functional

from Timba.Contrib.JEN.util import TDL_Leaf


#-------------------------------------------------------------------------
# Script control record (may be edited here):

MG = MG_JEN_exec.MG_init('MG_JEN_twig.py',
                         last_changed='h19oct2005',
                         trace=False)             # If True, produce progress messages  

MG.parm = record(height=0.25, # dipole height from ground plane, in wavelengths
                              # note that this varies with freq. in order to 
                              # model this variation, use the t,f polynomial
                              # given below
                 ntime=5,     # no. of grid points in time [0,1]
                 nfreq=5,     # no. of grid points in frequency [0,1]
                 nphi=40,     # no. of grid points in azimuth [0,2*pi]
                 ntheta=40,   # no. of grid points in declination [0,pi/2]
                              # measured from the zenith
                 debug_level=10)    # debug level

# Check the MG record, and replace any referenced values
MG = MG_JEN_exec.MG_check(MG)



#-------------------------------------------------------------------------
# The forest state record will be included automatically in the tree.
# Just assign fields to: Settings.forest_state[key] = ...

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

   if True:
       # add Azimuth and Elevation axes as the 3rd and 4th axes
       MG_MXM_functional._add_axes_to_forest_state(['A','E'])
       # create the dummy node (needed for the funklet)
       dummy = ns.dummy << Meq.Parm([[0,1],[1,0]],node_groups='Parm')

   # Test/demo of leaves in TDL_Leaf.py
   bb = []
   bb.append(TDL_Leaf.MeqFreq(ns))
   bb.append(TDL_Leaf.MeqWavelength(ns))
   bb.append(TDL_Leaf.MeqTime(ns))
   bb.append(TDL_Leaf.MeqFreqTime(ns))
   bb.append(TDL_Leaf.MeqTimeFreq(ns))
   bb.append(TDL_Leaf.MeqFreqTimeComplex(ns))
   bb.append(TDL_Leaf.MeqTimeFreqComplex(ns))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'TDL_Leaf_Freq_Time'))

   # Test/demo of leaves in TDL_Leaf.py
   bb = []
   for combine in ['Add','Subtract','Multiply','Divide']:
      bb.append(TDL_Leaf.MeqFreqTime(ns, combine=combine))
      bb.append(TDL_Leaf.MeqTimeFreq(ns, combine=combine))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'TDL_Leaf_FreqTime'))

   # Test/demo of leaves in TDL_Leaf.py
   bb = []
   bb.append(TDL_Leaf.MeqAzimuth(ns))
   bb.append(TDL_Leaf.MeqElevation(ns))
   bb.append(TDL_Leaf.MeqAzimuth(ns, ref=0.5))
   bb.append(TDL_Leaf.MeqElevation(ns, ref=1))
   cc.append(MG_JEN_exec.bundle(ns, bb, 'TDL_Leaf_AzEl'))

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
   return MG_JEN_exec.on_exit (ns, MG, cc)










#********************************************************************************
#********************************************************************************
#******************** PART IV: Optional: Importable functions *******************
#********************************************************************************
#********************************************************************************


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


# Make a ring of equidistant clouds on the unit circle in the complex plane: 

def clouds_ring (ns, nc=5, nppc=10, name='pnt', qual=None, stddev=0.2):
   cc = []
   for i in range(n):
      angle = 2*pi*(float(i)/n)
      mean = complex(cos(angle),sin(angle))
      print i,n,(float(i)/n),':',angle,'->',mean
      cc.append(cloud (ns, n=nppc, name=name+str(i), qual=None, stddev=stddev, mean=mean))

   return cc





#********************************************************************************
#********************************************************************************
#*****************  PART V: Forest execution routines ***************************
#********************************************************************************
#********************************************************************************


def _test_forest (mqs, parent):
   return MG_JEN_exec.meqforest (mqs, parent)

def _tdl_job_4D_request (mqs,parent):
   """ evaluate beam pattern for the upper hemisphere
   for this create a grid in azimuth(phi) [0,2*pi], pi/2-elevation(theta) [0,pi/2]
   """;
   # run dummy first, to make python know about the extra axes (some magic)
   MG_MXM_functional._dummy(mqs, parent);

   time_range = [0.,1.]
   freq_range = [0.,1.]
   az_range = [0.,math.pi*2.0]
   el_range = [0.,math.pi/2.0]
   dom_range = [freq_range, time_range, az_range, el_range]
   nr_cells = [MG.parm['ntime'],MG.parm['nfreq'],MG.parm['nphi'],MG.parm['ntheta']]
   request = MG_MXM_functional._make_request(Ndim=4, dom_range=dom_range,
                                             nr_cells=nr_cells)

   return MG_JEN_exec.meqforest (mqs, parent, request=request)




#********************************************************************************
#********************************************************************************
#******************** PART VI: Standalone test routines *************************
#********************************************************************************
#********************************************************************************


if __name__ == '__main__':
   print '\n*******************\n** Local test of:',MG.script_name,':\n'
   if 1:
        MG_JEN_exec.without_meqserver(MG.script_name, callback=_define_forest)

   if 1:
       ns = NodeScope()
       freqtime (ns, qual=None, combine='Add', unop=False)

   # ............
   # MG_JEN_display_object (rr, 'rr', MG.script_name)
   # MG_JEN_exec.display_subtree (rr, 'rr', full=1)

   print '\n** End of local test of:',MG.script_name,'\n*******************\n'

#********************************************************************************
#********************************************************************************




