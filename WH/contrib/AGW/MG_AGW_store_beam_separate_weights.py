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
# and form a combined, weighted beam with phase-conjugate weighting.
# The weights are found by getting complex values at specified
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose.

# We then pretend that we are observing with an AzEl mounted telescope
# at the VLA site and calculate the change in phased-up beam
# shape as we track a specific off-boresight RA/DEC point over
# an 8 hr 'VLA' observation. The constant L,M (RA/DEC) position
# has to be translated into the L',M' frame of the Az/El mount.

# We then re-rotate the phased-up beam so that
# we see what the beam looks like in the frame of the sky.

# History:
# - 07 Mar 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils
from handle_beams import *
from make_multi_dim_request import *
from MG_AGW_setup_array_weights import *

import os


# to force caching put 100
#Settings.forest_state.cache_policy = 100

# get position of phase up point in L and M
TDLCompileMenu('L and M position of phased-up beam',
  TDLOption('l_beam','L position of beam (in units of FWHM)',[0,1,2,3],more=float),
  TDLOption('m_beam','M position of beam (in units of FWHM)',[0,1,2,3],more=float),
);

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_defocus','veidt_fpa_180', 'veidt_fpa_30'],more=str)

# Attempt to 'form' a Gaussian beam?
TDLCompileOption('do_fit','make gaussian fit',[True, False])

# define default desired half-intensity width of power pattern (HPBW)
# as we are fitting total intensity I pattern (here .021 rad = 74.8 arcmin)
beam_width = 0.021747 # beam FWHM
if do_fit:
  Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/pol_sky",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/IQUV_sky",viewer="Result Plotter",pos=(0,0))]),
    record(name='Fits',page=[
      record(udi="/node/solver_x",viewer="Result Plotter",pos=(0,0)),
      record(udi="/node/solver_y",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/condeq_x",viewer="Result Plotter",pos=(1,0)),
      record(udi="/node/condeq_y",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/sqrt_gauss",viewer="Result Plotter",pos=(2,0))])]);

# beam_width = 0.02098           # default: veidt fpa 180 width
# if fpa_directory.find('gauss_array_pats') >= 0:
#   if fpa_directory.find('gauss_array_pats_offset') >= 0:
#     print 'using gauss array pats offset width for fit'
#     beam_width = 0.02178
#   else:
#     print 'using gauss array pats width for fit'
#     beam_width = 0.02081
# if fpa_directory.find('veidt_fpa_180') >= 0:
#   print 'using veidt fpa 180 width for fit'
#   beam_width = 0.02098
# if fpa_directory.find('veidt_fpa_30') >= 0:
#   print 'using veidt fpa 30 width for fit'
#   beam_width = 0.02179

else:
  Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/pol_sky",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/IQUV_sky",viewer="Result Plotter",pos=(1,0))])])

if do_fit:
  mep_beam_weights = 'beam_weights_' + str(l_beam) + '_' + str(m_beam) + '.mep'
else:
  mep_beam_weights = 'beam_weights_' + str(l_beam) + '_' + str(m_beam) + '_conj.mep'


########################################################
def _define_forest(ns):  

  ns.fwhm << Meq.Constant(beam_width) # beam FWHM
  ns.width_factor << Meq.Constant(1.0)
  ns.width << ns.width_factor * ns.fwhm


  # values for l_beam and m_beam are obtained from the TDLCompileMenu
  ns.l_beam_c << ns.fwhm * l_beam
  ns.m_beam_c << ns.fwhm * m_beam

  ns.lm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);


# setup for fitting the phased up beam to a gaussian
  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

# constant for half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

# total intensity gaussian to which we want to optimize beams
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_beam_c) + Meq.Sqr(maxis - ns.m_beam_c)
  ns.gaussian << Meq.Exp((ns.lm_x_sq * ns.ln_16)/Meq.Sqr(ns.width));

# corresponding gaussian voltage response
  ns.sqrt_gauss << Meq.Sqrt(ns.gaussian)

# get beam data
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  # now determine weights for individual beams
  parms_req_mux, solver_x, solver_y = setup_separate_array_weights(ns, num_beams, mep_beam_weights, do_fit)

  ns.E << Meq.Matrix22(ns.norm_voltage_sum_xx, ns.norm_voltage_sum_xy,ns.norm_voltage_sum_yx, ns.norm_voltage_sum_yy)
  ns.Et << Meq.ConjTranspose(ns.E)

 # sky brightness
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

  # observe!
  ns.observed << Meq.MatrixMultiply(ns.E, ns.B0, ns.Et)
  ns.IpQ << Meq.Selector(ns.observed,index=0)  # XX = (I+Q)/2
  ns.ImQ << Meq.Selector(ns.observed,index=3)  # YY = (I-Q)/2
  ns.I << Meq.Add(ns.IpQ,ns.ImQ)                     # I = XX + YY
  ns.Q << Meq.Subtract(ns.IpQ,ns.ImQ)                # Q = XX - YY

  ns.UpV << Meq.Selector(ns.observed,index=1)  # XY = (U+iV)/2
  ns.UmV << Meq.Selector(ns.observed,index=2)  # YX = (U-iV)/2
  ns.U << Meq.Add(ns.UpV,ns.UmV)                     # U = XY + YX
  ns.iV << Meq.Subtract(ns.UpV,ns.UmV)               # iV = XY - YX  <----!!
  ns.V << ns.iV / 1j                                 # V = iV / i

  ns.I_real << Meq.Real(ns.I)
  ns.Q_real << Meq.Real(ns.Q)
  ns.U_real << Meq.Real(ns.U)
  ns.V_real << Meq.Real(ns.V)

  ns.IQUV_sky << Meq.Matrix22(ns.I_real,ns.Q_real,ns.U_real,ns.V_real)
  ns.Q_sqr << Meq.Sqr(ns.Q_real)
  ns.U_sqr << Meq.Sqr(ns.U_real)
  ns.pol_sky << Meq.Sqrt(ns.Q_sqr + ns.U_sqr)

  if do_fit:
    ns.req_seq<<Meq.ReqSeq(parms_req_mux, solver_x, solver_y, ns.IQUV_sky, ns.pol_sky)
  else:
    ns.req_seq<<Meq.ReqSeq(parms_req_mux, ns.IQUV_sky, ns.pol_sky)

  # If you want the aips++ imager to generate images in the sequence I,Q,U,V
  # make sure that the newsimulator setspwindow method uses
  # stokes='XX XY YX YY' and not stokes='RR RL LR LL'. If you
  # do the latter you will get the images rolled out in the
  # order I,U,V,Q!



########################################################################
def _test_forest(mqs,parent):

# delete any previous version if the mep file ...
  print 'trying to delete file ', mep_beam_weights
  try:
    command = "rm -rf "+ mep_beam_weights
    os.system(command)
    print 'issued OS command ', command
  except:   pass

  t0 = 0.0
  t1 = 1.5e70

  f0 = 800.0
  f1 = 1300.0

  m_range = [-0.15,0.15];
  l_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
  request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],l_range,m_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='req_seq',request=request),wait=False);
#####################################################################

if __name__=='__main__':
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
