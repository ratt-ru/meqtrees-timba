#/usr/bin/python

#
# Copyright (C) 2002-2008
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# This script does a simulation of the VLA beam squint at 20 cm wavelength
# and displays the resulting circular V instrumental polarization.

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meq
from Meow import Bookmarks,Utils

# The make_multi_dim_request function is just something used to incorporate 
# L, M into the request in addition to the standard time and frequency domains
from make_multi_dim_request import *

#setup bookmarks for display of results - the I total intensity response,
# the instrumental V response and the degree of polarization
Settings.forest_state = record(bookmarks=[
  record(name='Results',page=[
    record(udi="/node/I_real",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/V_real",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/Ins_pol",viewer="Result Plotter",pos=(1,0))])])

# to force caching put 100
Settings.forest_state.cache_policy = 100

# useful constant: 1 deg in radians
import math
DEG = math.pi/180.
ARCMIN = DEG/60;
ARCSEC = ARCMIN/60;

# Define desired VLA half-intensity width of power pattern (HPBW)
# Use ABridle approximate formula from
# http://www.cv.nrao.edu/vla/hhg2vla/node41.html#SECTION000115000000000000000
ghz = 1.4
fwhm  = (45/ghz) * ARCMIN

# VLA beam squint taken from Fomalont & Perley 
# (P108 of Synthesis Imaging in Radio Astronomy II)
# They give squint separation as fwhm * 0.05
# Assume squint offset along diagonal and centred at L,M = 0
# Then squint offset in L, M given by
squint = (fwhm * 0.05) *  0.5 * 0.707 

# The _define_forest section of a MeqTrees script sets up the nodes required
# for calculating squinty beams.
# The << operator essentially means an assignment.
########################################################
def _define_forest(ns):  

 # constant for gaussian half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

  # define desired half-intensity width of power pattern (HPBW)
  ns.width << Meq.Constant(fwhm) # beam FWHM

  # setup an L, M grid for calculating a gaussian beam 
  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

  # For this example we just approximate beam shapes by a gaussian
  # first specify L, M central location of R voltage pattern
  ns.l_beam_R << Meq.Constant(squint * -1.0)
  ns.m_beam_R << Meq.Constant(squint)
  ns.lm_x_sq_R << Meq.Sqr(laxis - ns.l_beam_R) + Meq.Sqr(maxis - ns.m_beam_R)
  # total intensity response for R
  ns.gaussian_R << Meq.Exp((ns.lm_x_sq_R * ns.ln_16)/Meq.Sqr(ns.width));
  # take sqrt to get voltage response for R
  ns.voltage_R << Meq.Sqrt(ns.gaussian_R)

  # specify L, M central location of L voltage pattern etc
  ns.l_beam_L << Meq.Constant(squint)
  ns.m_beam_L << Meq.Constant(squint * -1.0)
  ns.lm_x_sq_L << Meq.Sqr(laxis - ns.l_beam_L) + Meq.Sqr(maxis - ns.m_beam_L)
  ns.gaussian_L << Meq.Exp((ns.lm_x_sq_L * ns.ln_16)/Meq.Sqr(ns.width));
  ns.voltage_L << Meq.Sqrt(ns.gaussian_L)

  # create the E-Jones matrix for a VLA antenna; we assume no RL, LR leakage here
  ns.E << Meq.Matrix22(ns.voltage_R, 0.0, 0.0, ns.voltage_L)
  # compute the complex conjugate for second antenna of an interferometer pair
  ns.Et << Meq.ConjTranspose(ns.E)

  # sky brightness 2 x 2 coherency matrix for unpolarized sky
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

  # Then the primary beam power response for an interferometer pair
  # is just a sequence of 2 x 2 matrix multiplies (left to right):
  ns.observed << Meq.MatrixMultiply(ns.E, ns.B0, ns.Et) 

  # extract I,Q,U,V etc for circular polarization system
  ns.IpV << Meq.Selector(ns.observed,index=0)        # RR = (I+V)/2
  ns.ImV << Meq.Selector(ns.observed,index=3)        # LL = (I-V)/2
  ns.I << Meq.Add(ns.IpV,ns.ImV)                     # I = RR + LL
  ns.V << Meq.Subtract(ns.IpV,ns.ImV)                # V = RR - LL

  ns.QpU << Meq.Selector(ns.observed,index=1)        # RL = (Q+iU)/2
  ns.QmU << Meq.Selector(ns.observed,index=2)        # LR = (Q-iU)/2
  ns.Q << Meq.Add(ns.QpU,ns.QmU)                     # Q = RL + LR
  ns.iU << Meq.Subtract(ns.QpU,ns.QmU)               # iU = RL - LR <----!!
  ns.U << ns.iU / 1j                                 # U = iU / i 
                                                     # i -> j in python

  # join together into one node in order to make a single request
  ns.IQUV_complex << Meq.Composer(ns.I, ns.Q,ns.U, ns.V)

  # comvert to real; in this simple simulation this step was not really 
  # necessary as the voltage patterns were all real to begin with 
  ns.IQUV << Meq.Real(ns.IQUV_complex) 

  # note: instrumental Q and U are zero in the case of this simulation 
  # so they're ignored from here on
  ns.I_real << Meq.Selector(ns.IQUV,index=0)
  ns.V_real << Meq.Selector(ns.IQUV,index=3)
  ns.Ins_pol << ns.V_real / ns.I_real

# running the _test_forest section will cause the script in _define_forest to be
# executed
########################################################################
def _test_forest(mqs,parent):

# any old time and frequency range will do for this request
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 1.5

  # define L, M range (in radians) and number of cells in L and M
  lm_range = [-0.05,0.05];
  lm_num = 101;
  counter = 0
  # make a request for a domain that involves L and M as well as the standard 
  # time, frequency domain 
  request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])

  # Tell the Ins_pol node to execute the request. That node sends requests through
  # the whole tree so that everything gets processed
  mqs.meq('Node.Execute',record(name='Ins_pol',request=request),wait=True);
#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
