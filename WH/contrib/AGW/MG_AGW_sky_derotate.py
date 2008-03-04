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

import os

Settings.forest_state = record(bookmarks=[
  record(name='I rot',page=Bookmarks.PlotPage(
#     ["resampler_I"], ["IQUV_rot"],["IQUV"],
      ["IQUV"],
  )),
])

# to force caching put 100
#Settings.forest_state.cache_policy = 100

# get position of phase up point in L and M
TDLCompileMenu('L and M position of phased-up beam',
  TDLOption('l_beam','L position of beam (in units of FWHM)',[0,1,2,3],more=float),
  TDLOption('m_beam','M position of beam (in units of FWHM)',[0,1,2,3],more=float),
);

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_defocus','veidt_fpa_180', 'veidt_fpa_30'],more=str)

########################################################
def _define_forest(ns):  

  # station position for 'pseudo' VLA telescope for 
  # aips++ MVDirection object (ITRF units are metres)
  X_pos = -1597262.96
  Y_pos = -5043205.54
  Z_pos = 3554901.34
  ns.x_pos << Meq.Parm(X_pos,node_groups='Parm')
  ns.y_pos << Meq.Parm(Y_pos,node_groups='Parm')
  ns.z_pos << Meq.Parm(Z_pos,node_groups='Parm')
  #create a  MeqComposer containing X_pos, Y_pos, Z_pos children
  ns.XYZ <<Meq.Composer(ns.x_pos, ns.y_pos, ns.z_pos)

  # now define a field centre RA and DEC (in radians) which the boresight
  # will track - we arbitrarily choose Ra = 0, Dec = 28.6 deg (0.5 rad)
  ns.ra0 << Meq.Constant(0.0)
  ns.dec0 << Meq.Constant(0.5)
# then create a MeqComposer containing the field centre RA and DEC as children
  ns.RADec0 <<Meq.Composer(ns.ra0, ns.dec0)
 
  # we should now be able to create an ParAngle node with X,Y,Z station positions
  ns.ParAngle << Meq.ParAngle(radec=ns.RADec0, xyz=ns.XYZ)
# freeze beam position over 'tile' interval by getting the mean over interval
  pa = ns.ParAngle_mean << Meq.Mean(ns.ParAngle)
# pa = ns.ParAngle << Meq.Constant(0.05)

  # define desired half-intensity width of power pattern (HPBW)
  # as we are fitting total intensity I pattern (here .021 rad = 74.8 arcmin)
  ns.fwhm << Meq.Constant(0.021747) # beam FWHM

  # values for l_beam and m_beam are obtained from the TDLCompileMenu
  ns.l_beam_c << ns.fwhm * l_beam
  ns.m_beam_c << ns.fwhm * m_beam

  ns.ll_mm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);
  # we should now be able to create an LMRaDec node with the field
  # centre RA and DEC and the L and M offsets as children.
  # This node gives as output the RA and DEC corresponding to the
  # specified L,M offset
  ns.RaDec_beam << Meq.LMRaDec(radec_0=ns.RADec0, lm=ns.ll_mm_beam)

# compute corresponding 'apparent' L,M position of feed in AzEl
# system as function of parallactic angle
  ns.lm_prime_beam << Meq.LMN(ns.RADec0, ns.RaDec_beam, -1.0 * ns.ParAngle)
  ns.l_prime_beam << Meq.Selector(ns.lm_prime_beam, index=0)
  ns.m_prime_beam << Meq.Selector(ns.lm_prime_beam, index=1)
  ns.lm_beam << Meq.Composer(ns.l_prime_beam,ns.m_prime_beam);

# get beam data
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  BEAMS = range(0,num_beams)
  for k in BEAMS:
    # it would be wonderful if a) the rationale for dep_masks was given and
    # b) why on earth are we using hex values - very un-user friendly!
    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.image_im_yy(k),dep_mask = 0xff)
    
    # obtain the real and imaginary values of the beam in the direction where
    # we want to phase up the beam. Note that we multiply the imaginary value
    # by -1 in order to eventually use the phase conjugate as the weight for this
    # beam
    ns.beam_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_wt_im_y(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])

    # now form the weights for the beam and multiply the beam by its weight
    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.image_re_yx(k), ns.image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.image_re_yy(k), ns.image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.image_im_xx(k),dep_mask = 0xff)
    ns.beam_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_wt_im_x(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])

    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.image_re_xy(k), ns.image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.image_re_xx(k), ns.image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  # sum up the weights
  ns.wt_sum_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.wt_sum_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  # sum beams up and normalize by the summed weights
  ns.voltage_sum_xx_norm << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS]) / ns.wt_sum_x
  ns.voltage_sum_xy_norm << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS]) / ns.wt_sum_x
  ns.voltage_sum_yx_norm << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS]) / ns.wt_sum_y
  ns.voltage_sum_yy_norm << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS]) / ns.wt_sum_y

  # attempt to de-rotate the I image
  ns.l << Meq.Grid(axis=2);     # returns l(l) = l
  ns.m << Meq.Grid(axis=3);     # returns m(m) = m
  ns.lm_pre_rot << Meq.Composer(ns.l,ns.m)    # returns an lm 2-vector

  ns.P << Meq.Matrix22(Meq.Cos(pa),-Meq.Sin(pa),Meq.Sin(pa),Meq.Cos(pa)) 
  ns.rot_lm << Meq.MatrixMultiply(ns.P,ns.lm_pre_rot);    # rotated lm
  ns.l_rot << Meq.Selector(ns.rot_lm,index=0)
  ns.m_rot << Meq.Selector(ns.rot_lm,index=1)
  ns.lm_rot << Meq.Composer(Meq.Grid(axis=0),Meq.Grid(axis=1),ns.l_rot,ns.m_rot)

  ns.resampler_xx_real << Meq.Resampler(Meq.Real(ns.voltage_sum_xx_norm),dep_mask = 0xff)
  ns.xx_real << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xx_real],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_xx_imag << Meq.Resampler(Meq.Imag(ns.voltage_sum_xx_norm),dep_mask = 0xff)
  ns.xx_imag << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xx_imag],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_xy_real << Meq.Resampler(Meq.Real(ns.voltage_sum_xy_norm),dep_mask = 0xff)
  ns.xy_real << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xy_real],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_xy_imag << Meq.Resampler(Meq.Imag(ns.voltage_sum_xy_norm),dep_mask = 0xff)
  ns.xy_imag << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xy_imag],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yx_real << Meq.Resampler(Meq.Real(ns.voltage_sum_yx_norm),dep_mask = 0xff)
  ns.yx_real << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yx_real],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yx_imag << Meq.Resampler(Meq.Imag(ns.voltage_sum_yx_norm),dep_mask = 0xff)
  ns.yx_imag << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yx_imag],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yy_real << Meq.Resampler(Meq.Real(ns.voltage_sum_yy_norm),dep_mask = 0xff)
  ns.yy_real << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yy_real],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yy_imag << Meq.Resampler(Meq.Imag(ns.voltage_sum_yy_norm),dep_mask = 0xff)
  ns.yy_imag << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yy_imag],common_axes=[hiid('l'),hiid('m')])

  ns.xx << Meq.ToComplex(ns.xx_real, ns.xx_imag)
  ns.xy << Meq.ToComplex(ns.xy_real, ns.xy_imag)
  ns.yx << Meq.ToComplex(ns.yx_real, ns.yx_imag)
  ns.yy << Meq.ToComplex(ns.yy_real, ns.yy_imag)
  ns.E << Meq.Matrix22(ns.xx, ns.xy, ns.yx, ns.yy)
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

  # the resampler seems to only work on 1 VellSet so we have to
  # do each polarization separately.
  ns.I_real_un_norm << Meq.Real(ns.I)
  ns.norm << Meq.Max(ns.I_real_un_norm)
  ns.I_real << ns.I_real_un_norm / ns.norm
  ns.Q_real << Meq.Real(ns.Q) / ns.norm
  ns.U_real << Meq.Real(ns.U) / ns.norm
  ns.V_real << Meq.Real(ns.V) / ns.norm

  # join together into one node in order to make a single request
  ns.IQUV << Meq.Composer(log_policy=100, children=[ns.I_real, ns.Q_real,ns.U_real, ns.V_real])

########################################################################
def _test_forest(mqs,parent):

# any large time range will do: we observe the changes in the beam
# pattern in timesteps of 3600s, or 1 hr
  delta_t = 900.0
  # t0 = -1200.0 + 0.5 * delta_t
  # Approx start of 2001
  t0 = 4485011731.14 - delta_t       
  t1 = t0 + delta_t

  f0 = 800.0
  f1 = 1300.0

  m_range = [-0.15,0.15];
  l_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
# for i in range(16):
  for i in range(32):
      t0 = t0 + delta_t
      t1 = t0 + delta_t
      mqs.clearcache('IQUV',recursive=True)
      request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],l_range,m_range], nr_cells = [1,1,lm_num,lm_num])
      counter = counter + 1
# execute request
      mqs.meq('Node.Execute',record(name='IQUV',request=request),wait=False);
#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
