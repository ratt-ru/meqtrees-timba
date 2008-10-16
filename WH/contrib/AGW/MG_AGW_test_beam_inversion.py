#!/usr/bin/python

#
# Copyright (C) 2002-2007
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

# Short description:
# We read in a group of focal plane array beams, 
# and form a combined, weighted beam. The weights
# are found by getting complex values at a specified
# L,M location in the X  and Y (|| poln) beams and then
# taking the conjugate transpose. This is called phase 
# conjugate weighting.

# We use these weights as an initial starting guess for the
# weights to be used to obtain a nice Gaussian beam. These weights
# are given to the solver, which then proceeds to solve for
# the optimum weights. This script finds the 'best' gaussian
# beam at a single L,M. We store the weights for this beam in
# a 'mep' table.
# This script solves for gains of X and Y beams separately
#
# Finally the script inverts the beam to show the gain by which
# an observed field would need to be multiplied to get the proper sky
# signal

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils
from make_multi_dim_request import *
from handle_beams import *
from MG_AGW_setup_array_weights import *

import numpy
import os

# get position of phase up point in L and M
TDLCompileMenu('L and M position of phased-up beam',
  TDLOption('l_beam','L position of beam (in units of FWHM)',[0,1,2,3],more=float),
  TDLOption('m_beam','M position of beam (in units of FWHM)',[0,1,2,3],more=float),
);

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_noise','gauss_array_pats_sweep','gauss_array_pats_offset','veidt_fpa_180', 'veidt_fpa_30','veidt_fpa_180_low_res', 'veidt_fpa_180_low_res_noise','veidt_fpa_180_noise','veidt_fpa_30_sweep'],more=str)

# Attempt to 'form' a Gaussian beam?
TDLCompileOption('do_fit','make gaussian fit',[True, False])

#setup a bookmark for display of results with some 'Result' Plotters
beam_width = 0.02081           # default: gauss array pats width
if do_fit:
  Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/IQUV_complex",viewer="Result Plotter",pos=(1,0)),
      record(udi="/node/inv_real",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/IQUV",viewer="Result Plotter",pos=(0,0))]),
    record(name='Fits',page=[
      record(udi="/node/solver_x",viewer="Result Plotter",pos=(0,0)),
      record(udi="/node/solver_y",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/condeq_x",viewer="Result Plotter",pos=(1,0)),
      record(udi="/node/condeq_y",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/sqrt_gauss",viewer="Result Plotter",pos=(2,0))])]);
 
  # define taget total intensity half power width
  beam_width = 0.02098           # default: veidt fpa 180 width
  if fpa_directory.find('gauss_array_pats') >= 0:
    if fpa_directory.find('gauss_array_pats_offset') >= 0:
      print 'using gauss array pats offset width for fit'
      beam_width = 0.02178
    else:
      print 'using gauss array pats width for fit'
      beam_width = 0.02081
  if fpa_directory.find('veidt_fpa_180') >= 0:
    print 'using veidt fpa 180 width for fit'
    beam_width = 0.02098
  if fpa_directory.find('veidt_fpa_30') >= 0:
    print 'using veidt fpa 30 width for fit'
    beam_width = 0.02179

else:
  Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/IQUV_complex",viewer="Result Plotter",pos=(1,0)),
      record(udi="/node/inv_real",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/IQUV",viewer="Result Plotter",pos=(0,0))])])

# to force caching put 100
Settings.forest_state.cache_policy = 100

if do_fit:
  mep_beam_weights = 'beam_weights_' + str(l_beam) + '_' + str(m_beam) + '.mep'
else:
  mep_beam_weights = 'beam_weights_' + str(l_beam) + '_' + str(m_beam) + '_conj.mep'

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(numpy.zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
#                 node_groups='Parm', save_all=True,
                  table_name=mep_beam_weights)

########################################################
def _define_forest(ns):  
# first, make sure that any previous version of the mep table is

  # constant for half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

  ns.fwhm << Meq.Constant(beam_width) # beam FWHM                 
   
  ns.width_factor << Meq.Constant(1.0)
  ns.width << ns.width_factor * ns.fwhm

  # L, M values for l_beam and m_beam are obtained from the TDLCompileMenu
  ns.l_beam_c << ns.fwhm * l_beam
  ns.m_beam_c << ns.fwhm * m_beam

  ns.lm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);

  # setup for fitting the phased up beam to a gaussian
  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

  # total intensity gaussian to which we want to optimize beams
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_beam_c) + Meq.Sqr(maxis - ns.m_beam_c)
  ns.gaussian << Meq.Exp((ns.lm_x_sq * ns.ln_16)/Meq.Sqr(ns.width));

  # corresponding gaussian voltage response
  ns.sqrt_gauss << Meq.Sqrt(ns.gaussian)

  # load up individual beams of focal plane array 
  num_beams = read_in_FPA_beams(ns,fpa_directory)

 # now determine weights for individual beams
  parms_req_mux, solver_x, solver_y = setup_separate_array_weights(ns, num_beams, mep_beam_weights, do_fit)

  ns.E << Meq.Matrix22(ns.norm_voltage_sum_xx, ns.norm_voltage_sum_xy,ns.norm_voltage_sum_yx, ns.norm_voltage_sum_yy)
  ns.Et << Meq.ConjTranspose(ns.E)

  # sky brightness
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

  # observe!
  ns.observed << Meq.MatrixMultiply(ns.E, ns.B0, ns.Et)

  # extract I,Q,U,V etc
  ns.IpQ << Meq.Selector(ns.observed,index=0)        # XX = (I+Q)/2
  ns.ImQ << Meq.Selector(ns.observed,index=3)        # YY = (I-Q)/2
  ns.I << Meq.Add(ns.IpQ,ns.ImQ)                     # I = XX + YY
  ns.Q << Meq.Subtract(ns.IpQ,ns.ImQ)                # Q = XX - YY

  ns.UpV << Meq.Selector(ns.observed,index=1)        # XY = (U+iV)/2
  ns.UmV << Meq.Selector(ns.observed,index=2)        # YX = (U-iV)/2
  ns.U << Meq.Add(ns.UpV,ns.UmV)                     # U = XY + YX
  ns.iV << Meq.Subtract(ns.UpV,ns.UmV)               # iV = XY - YX  <----!!
  ns.V << ns.iV / 1j                                 # V = iV / i
                                                     # (note: i => j in Python)

  ns.IQUV_complex << Meq.Composer(ns.I, ns.Q,ns.U, ns.V)
  ns.IQUV << Meq.Real(ns.IQUV_complex)
  ns.obs_norm = ns.observed * 2
  ns.inv << Meq.MatrixInvert22(ns.obs_norm)
  ns.inv_real << Meq.Real(ns.inv)
  if do_fit:
    ns.req_seq<<Meq.ReqSeq(parms_req_mux, solver_x, solver_y, ns.IQUV, ns.inv_real)
  else:
    ns.req_seq<<Meq.ReqSeq(parms_req_mux, ns.IQUV, ns.inv_real)

  # want the aips++ imager to generate images in the sequence I,Q,U,V
  # make sure that the newsimulator setspwindow method uses
  # stokes='XX XY YX YY' and not stokes='RR RL LR LL'. If you
  # do the latter you will get the images rolled out in the
  # order I,U,V,Q!

########################################################################
def _test_forest(mqs,parent,wait=False):

# obliterate any previous table so nothing strange happens in succeeding steps
  try:
    command = "rm -rf "+ mep_beam_weights
    print 'issuing OS command ', command
    os.system(command)
  except:   pass

# any large time and frequency range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 750.0e6
  f1 = 1550.0e6

  lm_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
# request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [8,1,lm_num,lm_num])
  request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])

# execute request
  mqs.meq('Node.Execute',record(name='req_seq',request=request),wait);
########################################################################

if __name__ == '__main__':
 # run in batch mode?
 if '-run' in sys.argv:
   from Timba.Apps import meqserver
   from Timba.TDL import Compile

   # this starts a kernel.
   mqs = meqserver.default_mqs(wait_init=10);

   # This compiles a script as a TDL module. Any errors will be thrown as
   # an exception, so this always returns successfully. We pass in
   # __file__ so as to compile ourselves.
   (mod,ns,msg) = Compile.compile_file(mqs,__file__);

   # this runs the _test_forest job.
   mod._test_forest(mqs,None,wait=True);
   print 'finished'
   sys.exit()
 else:
# Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())

