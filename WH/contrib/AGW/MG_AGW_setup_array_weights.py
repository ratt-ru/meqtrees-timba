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
# utility functions for handling FPA beams

# Get TDL and Meq for the Kernel
from Timba.TDL import *
from Timba.Meq import meqds
from Timba.Meq import meq
from numarray import *

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (mep_beam_weights,tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
#                 node_groups='Parm', save_all=True,
                  table_name=mep_beam_weights)

def setup_separate_array_weights(ns, num_beams, mep_beam_weights, do_fit=False):

  # now determine weights for individual beams
  BEAMS = range(0,num_beams)
  solver_x = None
  solver_y = None
  for k in BEAMS:
    # it would be wonderful if a) the rationale for dep_masks was given and
    # b) why on earth are we using hex values - very un-user friendly!

    # first set up Y beam stuff
    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.image_im_yy(k),dep_mask = 0xff)
    
    # obtain the real and imaginary values of the beam in the direction where
    # we want to phase up the beam. Note that we multiply the imaginary value
    # by -1 in order to use the phase conjugate as the weight for this
    # beam
    ns.sample_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_y(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])

    # I want to solve for these parameters
    ns.beam_wt_re_y(k) << tpolc(mep_beam_weights,0)
    ns.beam_wt_im_y(k) << tpolc(mep_beam_weights,0)

    # we need to assign the weights we've extracted as initial guesses
    # to the Parm - can only be done by solving according to Oleg
    ns.condeq_wt_re_y(k) << Meq.Condeq(children=(ns.sample_wt_re_y(k), ns.beam_wt_re_y(k)))
    ns.condeq_wt_im_y(k) << Meq.Condeq(children=(ns.sample_wt_im_y(k), ns.beam_wt_im_y(k)))
    ns.solver_wt_re_y(k)<<Meq.Solver(ns.condeq_wt_re_y(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_re_y(k),save_funklets=True,last_update=True)
    ns.solver_wt_im_y(k)<<Meq.Solver(ns.condeq_wt_im_y(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_im_y(k),save_funklets=True,last_update=True)
    
    # now form the complex weights for the beam and multiply the beam by its weight
    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.image_re_yx(k), ns.image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.image_re_yy(k), ns.image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

    # Now set up X beam stuff
    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.image_im_xx(k),dep_mask = 0xff)
    ns.sample_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_x(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])

    # I want to solve for these parameters
    ns.beam_wt_re_x(k) << tpolc(mep_beam_weights,0)
    ns.beam_wt_im_x(k) << tpolc(mep_beam_weights,0)
    ns.condeq_wt_re_x(k) << Meq.Condeq(children=(ns.sample_wt_re_x(k), ns.beam_wt_re_x(k)))
    ns.condeq_wt_im_x(k) << Meq.Condeq(children=(ns.sample_wt_im_x(k), ns.beam_wt_im_x(k)))
    ns.solver_wt_re_x(k)<<Meq.Solver(ns.condeq_wt_re_x(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_re_x(k),save_funklets=True,last_update=True)
    ns.solver_wt_im_x(k)<<Meq.Solver(ns.condeq_wt_im_x(k),num_iter=50,epsilon=1e-4,solvable=ns.beam_wt_im_x(k),save_funklets=True,last_update=True)

    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.image_re_xy(k), ns.image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.image_re_xx(k), ns.image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  # create lists of solvable parameters
  parm_solvers = []
  beam_solvables_x = []
  beam_solvables_y = []
  for k in BEAMS:
    parm_solvers.append(ns.solver_wt_re_x(k))
    parm_solvers.append(ns.solver_wt_im_x(k))
    beam_solvables_x.append(ns.beam_wt_re_x(k))
    beam_solvables_x.append(ns.beam_wt_im_x(k))
  for k in BEAMS:
    parm_solvers.append(ns.solver_wt_re_y(k))
    parm_solvers.append(ns.solver_wt_im_y(k))
    beam_solvables_y.append(ns.beam_wt_re_y(k))
    beam_solvables_y.append(ns.beam_wt_im_y(k))

  # sum up the weights
  ns.wt_sum_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.wt_sum_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  # sum beams up and normalize by the summed weights
  ns.voltage_sum_xx_norm << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS]) / ns.wt_sum_x
  ns.voltage_sum_xy_norm << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS]) / ns.wt_sum_x
  ns.voltage_sum_yx_norm << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS]) / ns.wt_sum_y
  ns.voltage_sum_yy_norm << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS]) / ns.wt_sum_y

  # normalize beam to amplitude peak response
  ns.voltage_sum_xx_r << Meq.Real(ns.voltage_sum_xx_norm)
  ns.voltage_sum_xx_i << Meq.Imag(ns.voltage_sum_xx_norm)
  ns.voltage_sum_yy_r << Meq.Real(ns.voltage_sum_yy_norm)
  ns.voltage_sum_yy_i << Meq.Imag(ns.voltage_sum_yy_norm)
  ns.im_sq_x << ns.voltage_sum_xx_r * ns.voltage_sum_xx_r + ns.voltage_sum_xx_i * ns.voltage_sum_xx_i 
  ns.im_x <<Meq.Sqrt(ns.im_sq_x)
# ns.im_x_max <<Meq.Max(ns.im_x)

  ns.im_sq_y << ns.voltage_sum_yy_r * ns.voltage_sum_yy_r + ns.voltage_sum_yy_i * ns.voltage_sum_yy_i 
  ns.im_y <<Meq.Sqrt(ns.im_sq_y)
# ns.im_y_max <<Meq.Max(ns.im_y)

  # find peak values
  ns.resampler_im_x << Meq.Resampler(ns.im_x,dep_mask = 0xff)
  ns.im_x_max << Meq.Compounder(children=[ns.lm_beam,ns.resampler_im_x],common_axes=[hiid('l'),hiid('m')])
  ns.im_x_max_fit << tpolc(mep_beam_weights,0,1.0)
  ns.condeq_im_x_max << Meq.Condeq(children=(ns.im_x_max_fit, ns.im_x_max))
  ns.solver_im_x_max <<Meq.Solver(ns.condeq_im_x_max,num_iter=50,epsilon=1e-4,solvable=ns.im_x_max_fit,save_funklets=True,last_update=True)
  parm_solvers.append(ns.solver_im_x_max)
# beam_solvables_x.append(ns.im_x_max_fit)

  ns.resampler_im_y << Meq.Resampler(ns.im_y,dep_mask = 0xff)
  ns.im_y_max << Meq.Compounder(children=[ns.lm_beam,ns.resampler_im_y],common_axes=[hiid('l'),hiid('m')])
  ns.im_y_max_fit << tpolc(mep_beam_weights,0,1.0)
  ns.condeq_im_y_max << Meq.Condeq(children=(ns.im_y_max_fit, ns.im_y_max))
  ns.solver_im_y_max <<Meq.Solver(ns.condeq_im_y_max,num_iter=50,epsilon=1e-4,solvable=ns.im_y_max_fit,save_funklets=True,last_update=True)
  parm_solvers.append(ns.solver_im_y_max)
# beam_solvables_y.append(ns.im_y_max_fit)

  # node that is called to process all initial parameter solvers in parallel
  parms_req_mux = ns.parms_req_mux<<Meq.ReqMux(children=parm_solvers)

  # now set up equations to solve for X and Y weights so that difference
  # between above x and y beams and voltage gaussian is minimized
  if do_fit:
    ns.im_x_norm_max << Meq.Max(ns.im_x)
    ns.im_x_norm << ns.im_x / ns.im_x_norm_max
    ns.resampler_x <<Meq.Resampler(ns.im_x_norm)
    ns.condeq_x << Meq.Condeq(children=(ns.resampler_x, ns.sqrt_gauss))
    solver_x = ns.solver_x <<Meq.Solver(ns.condeq_x,num_iter=20,epsilon=5e-4,solvable=beam_solvables_x,save_funklets=True,last_update=True)

    ns.im_y_norm_max << Meq.Max(ns.im_y)
    ns.im_y_norm << ns.im_y / ns.im_y_norm_max
    ns.resampler_y <<Meq.Resampler(ns.im_y_norm)
    ns.condeq_y << Meq.Condeq(children=(ns.resampler_y, ns.sqrt_gauss))
    solver_y = ns.solver_y <<Meq.Solver(ns.condeq_y,num_iter=20,epsilon=5e-4,solvable=beam_solvables_y,save_funklets=True,last_update=True)
    ns.norm_voltage_sum_xx << ns.voltage_sum_xx_norm / ns.im_x_norm_max
    ns.norm_voltage_sum_xy << ns.voltage_sum_xy_norm / ns.im_x_norm_max
    ns.norm_voltage_sum_yy << ns.voltage_sum_yy_norm / ns.im_y_norm_max
    ns.norm_voltage_sum_yx << ns.voltage_sum_yx_norm / ns.im_y_norm_max
  else:
    ns.norm_voltage_sum_xx << ns.voltage_sum_xx_norm / ns.im_x_max_fit
    ns.norm_voltage_sum_xy << ns.voltage_sum_xy_norm / ns.im_x_max_fit
    ns.norm_voltage_sum_yy << ns.voltage_sum_yy_norm / ns.im_y_max_fit
    ns.norm_voltage_sum_yx << ns.voltage_sum_yx_norm / ns.im_y_max_fit

  return (parms_req_mux, solver_x, solver_y)

