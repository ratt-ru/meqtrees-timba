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
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose.

# We use these weights as an initial starting guess for the
# weights to be used to obtain a nice Gaussian beam. These weights
# are given to the solver, which then proceeds to solve for
# the optimum weights. This script finds the 'best' gaussian
# beam at a single L,M. We store the weights for this beam in
# a 'mep' table.

# History:
# - 27 Feb 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils

from make_multi_dim_request import *
from handle_beams import *

from numarray import *
import os

# get position of phase up point in L and M
TDLCompileMenu('L and M position of phased-up beam',
  TDLOption('l_beam','L position of beam (in units of FWHM)',[0,1,2,3],more=float),
  TDLOption('m_beam','M position of beam (in units of FWHM)',[0,1,2,3],more=float),
);

# get position of source with respect to beam in L and M
TDLCompileMenu('L and M relative offset position of source',
  TDLOption('l_off_beam','relative L position of source (in units of FWHM)',[0,0.25,0.5,0.75],more=float),
  TDLOption('m_off_beam','relative M position of source (in units of FWHM)',[0,0.25,0.5,0.75],more=float),
);

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_defocus','veidt_fpa_180', 'veidt_fpa_30'],more=str)

# get number of GRASP beams to use in FPA simulation
#TDLCompileOption('num_beams','number of focal plane antennas',[30, 90])

# get number of GRASP beams to use in FPA simulation
TDLCompileOption('do_fit','make gaussian fit',[True, False])


#setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Results',page=[
    record(udi="/node/I_real",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/I_src",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/solver",viewer="Result Plotter",pos=(1,1)),
    record(udi="/node/gaussian",viewer="Result Plotter",pos=(2,0)),
    record(udi="/node/condeq",viewer="Result Plotter",pos=(2,1))])]);

# to force caching put 100
# Settings.forest_state.cache_policy = 100
Settings.forest_state.log_append = True

mep_beam_weights = 'beam_weights.mep'
# first, make sure that any previous version of the mep table is
# obliterated so nothing strange happens in succeeding steps
try:
  os.system("rm -fr "+ mep_beam_weights);
except:   pass

fwhm  = 0.021747 # beam FWHM                 

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
#                 node_groups='Parm', save_all=True,
                  table_name=mep_beam_weights)

########################################################
def _define_forest(ns):  

 # Define a field centre RA and DEC (in radians) which the boresight
  # will track - 
  ns.ra0 << Meq.Constant(0.030543262)  # RA = 0h07m
# ns.dec0 << Meq.Constant(0.5)         # DEC = 28d38m52.4s  (0.5 rad)
# ns.dec0 << Meq.Constant(1.0)         # 1.0 rad
  ns.dec0 << Meq.Constant(0.50032772)  # 28d40m
  # then create a MeqComposer containing the field centre RA and DEC as children
  ns.RADec0 <<Meq.Composer(ns.ra0, ns.dec0)

  # now define parallactic angle node
  ns.ParAngle << Meq.ParAngle(radec=ns.RADec0, observatory='VLA')

  # constant for half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

  # define desired half-intensity width of power pattern (HPBW)
  # as we are fitting total intensity I pattern (here .021 rad = 74.8 arcmin)
  ns.width_factor << Meq.Constant(1.0)
  ns.width << ns.width_factor * fwhm

  # values for l_beam and m_beam are obtained from the TDLCompileMenu
  ns.l_beam_c << fwhm * l_beam
  ns.m_beam_c << fwhm * m_beam

  ns.ll_mm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);
  # we should now be able to create an LMRaDec node with the field
  # centre RA and DEC and the L and M offsets as children.
  # This node gives as output the RA and DEC corresponding to the
  # specified L,M offset
  ns.RaDec_beam << Meq.LMRaDec(radec_0=ns.RADec0, lm=ns.ll_mm_beam)
# compute corresponding 'apparent' L,M position of feed in AzEl
# system as function of parallactic angle
  ns.lm_prime_beam << Meq.LMN(ns.RADec0, ns.RaDec_beam, -1.0 * ns.ParAngle)
  ns.l_beam_cc << Meq.Selector(ns.lm_prime_beam, index=0)
  ns.m_beam_cc << Meq.Selector(ns.lm_prime_beam, index=1)
  ns.lm_beam << Meq.Composer(ns.l_beam_cc,ns.m_beam_cc);

  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

  # gaussian to which we want to optimize beams
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_beam_cc) + Meq.Sqr(maxis - ns.m_beam_cc)
  ns.gaussian << Meq.Exp((ns.lm_x_sq * ns.ln_16)/Meq.Sqr(ns.width));

  beam_solvables = []
  parm_solvers = []

  # read in beam data
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  BEAMS = range(0,num_beams)

  for k in BEAMS:
    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.image_im_yy(k),dep_mask = 0xff)
    ns.sample_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_y(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
    if do_fit:
      ns.beam_wt_re_y(k) << tpolc(0)
      ns.beam_wt_im_y(k) << tpolc(0)
      beam_solvables.append(ns.beam_wt_re_y(k))
      beam_solvables.append(ns.beam_wt_im_y(k))
    # we need to assign the weights we've extracted as initial guesses
    # to the Parm - can only be done by solving
      ns.condeq_wt_re_y(k) << Meq.Condeq(children=(ns.sample_wt_re_y(k), ns.beam_wt_re_y(k)))
      ns.condeq_wt_im_y(k) << Meq.Condeq(children=(ns.sample_wt_im_y(k), ns.beam_wt_im_y(k)))
      ns.solver_wt_re_y(k)<<Meq.Solver(ns.condeq_wt_re_y(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_re_y(k),save_funklets=True,last_update=True)
      ns.solver_wt_im_y(k)<<Meq.Solver(ns.condeq_wt_im_y(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_im_y(k),save_funklets=True,last_update=True)
      parm_solvers.append(ns.solver_wt_re_y(k))
      parm_solvers.append(ns.solver_wt_im_y(k))
      ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))
    else:
      ns.beam_weight_y(k) << Meq.ToComplex(ns.sample_wt_re_y(k), ns.sample_wt_im_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.image_re_yx(k), ns.image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.image_re_yy(k), ns.image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.image_im_xx(k),dep_mask = 0xff)
    ns.sample_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_x(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
    if do_fit:
      ns.beam_wt_re_x(k) << tpolc(0)
      ns.beam_wt_im_x(k) << tpolc(0)
      beam_solvables.append(ns.beam_wt_re_x(k))
      beam_solvables.append(ns.beam_wt_im_x(k))
      ns.condeq_wt_re_x(k) << Meq.Condeq(children=(ns.sample_wt_re_x(k), ns.beam_wt_re_x(k)))
      ns.condeq_wt_im_x(k) << Meq.Condeq(children=(ns.sample_wt_im_x(k), ns.beam_wt_im_x(k)))
      ns.solver_wt_re_x(k)<<Meq.Solver(ns.condeq_wt_re_x(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_re_x(k),save_funklets=True,last_update=True)
      ns.solver_wt_im_x(k)<<Meq.Solver(ns.condeq_wt_im_x(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_im_x(k),save_funklets=True,last_update=True)
      parm_solvers.append(ns.solver_wt_re_x(k))
      parm_solvers.append(ns.solver_wt_im_x(k))

      ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))
    else:
      ns.beam_weight_x(k) << Meq.ToComplex(ns.sample_wt_re_x(k), ns.sample_wt_im_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.image_re_xy(k), ns.image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.image_re_xx(k), ns.image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  # solver to 'copy' resampled beam locations to parms as
  # first guess
  if do_fit:
    ns.parms_req_mux<<Meq.ReqMux(children=parm_solvers)

 # sum things up
  ns.wt_sum_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.wt_sum_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  ns.voltage_sum_xx_norm << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS]) / ns.wt_sum_x
  ns.voltage_sum_xy_norm << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS]) / ns.wt_sum_x
  ns.voltage_sum_yx_norm << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS]) / ns.wt_sum_y
  ns.voltage_sum_yy_norm << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS]) / ns.wt_sum_y

  ns.E << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_yx_norm,ns.voltage_sum_xy_norm, ns.voltage_sum_yy_norm)
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

  # extract I,Q,U,V etc
  ns.I_select << Meq.Real(ns.I)
  ns.I_max << Meq.Max(ns.I_select)


  if do_fit:
    ns.I_parm_max << tpolc(0,1.0)
    ns.I_real  << ns.I_select / ns.I_parm_max
    beam_solvables.append(ns.I_parm_max)
    ns.condeq_I_max << Meq.Condeq(children=(ns.I_parm_max, ns.I_max))
    ns.solver_I_max <<Meq.Solver(ns.condeq_I_max,num_iter=50,epsilon=1e-4,solvable=ns.I_parm_max,save_funklets=True,last_update=True)
  else:
    ns.I_real  << ns.I_select / ns.I_max

  ns.resampler_I << Meq.Resampler(ns.I_real)
  if do_fit:
    ns.condeq<<Meq.Condeq(children=(ns.resampler_I, ns.gaussian))
    ns.solver<<Meq.Solver(ns.condeq,num_iter=15,mt_polling=False,epsilon=1e-4,solvable=beam_solvables,save_funklets=True,last_update=True,debug_level=10)

  # we have beam so get observed source flux

  l = fwhm * (l_beam + l_off_beam)
  m = fwhm * (m_beam + m_off_beam)
  n = math.sqrt(1-l*l-m*m);
  ns.lmn_minus1_src << Meq.Composer(l,m,n-1);
  # get intrinsic RA, DEC of sources
  ns.lm_src << Meq.Composer(l,m);
  ns.RaDec_src << Meq.LMRaDec(radec_0=ns.RADec0, lm=ns.lm_src)
  # and the projected brightness...
# don't really need to use the following for a point source
  ns.B << ns.B0 / n;

# create L,M offset of source with respect to 'phased' beam centre
# compute corresponding 'apparent' L,M position of feed in AzEl
# system as function of parallactic angle

  ns.lm_prime_src << Meq.LMN(ns.RADec0, ns.RaDec_src, -1.0 * ns.ParAngle)
  ns.l_prime_src <<  Meq.Selector(ns.lm_prime_src, index=0)
  ns.m_prime_src << Meq.Selector(ns.lm_prime_src, index=1)
  ns.lm_offset_src << Meq.Composer(ns.l_prime_src, ns.m_prime_src)
 
  # now compute the E-Jones voltage gains
  ns.I_src <<Meq.Compounder(children=[ns.lm_offset_src,ns.resampler_I],common_axes=[hiid('l'),hiid('m')],log_policy=100)

  if do_fit:
    ns.req_seq<<Meq.ReqSeq(ns.parms_req_mux, ns.solver_I_max, ns.solver, ns.I_src)
  else:
    ns.req_seq<<Meq.ReqSeq(ns.I_src)

########################################################################
def _test_forest(mqs,parent,wait=False):

# The time ranges, field centre etc are set to co-incide with those
# specified for setting up the UV track locations.

# time: (4485011701.19, 4485040501.19)
# time: [array Float64: 480] mean: 4485026101.19, min: 4485011731.19, max: 4485040471.19

  t0 = 4485011701.19                 # starting time corresponds to that in 
                                     # the ska_sim_mars.g simulation

  delta_t = 60                      # 15 sec integration steps
  t1 = t0
  t0 = t0 - delta_t 

  f0 = 0.5
  f1 = 5000.0e6

  lm_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
  for i in range(480):
      t0 = t0 + delta_t    
      t1 = t1 + delta_t 
#     mqs.clearcache('I_src',recursive=True,wait=wait,sync=True)
      request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
      counter = counter + 1
# execute request
      mqs.meq('Node.Execute',record(name='req_seq',request=request),wait=wait);
########################################################################

if __name__=='__main__':
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

 else:
# Timba.TDL._dbg.set_verbose(5);
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
