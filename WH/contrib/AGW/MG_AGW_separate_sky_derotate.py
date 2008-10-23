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

#setup a bookmark for display of results with some 'Result' Plotters
if do_fit:
  Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/IQUV_azel_frame",viewer="Result Plotter",pos=(2,0)),
      record(udi="/node/azel_frame",viewer="Result Plotter",pos=(0,0)),
      record(udi="/node/sky_frame",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/pol_sky",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/IQUV_sky",viewer="Result Plotter",pos=(1,0))]),
    record(name='Fits',page=[
      record(udi="/node/solver_x",viewer="Result Plotter",pos=(0,0)),
      record(udi="/node/solver_y",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/condeq_x",viewer="Result Plotter",pos=(1,0)),
      record(udi="/node/condeq_y",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/sqrt_gauss",viewer="Result Plotter",pos=(2,0))])]);
else:
  Settings.forest_state = record(bookmarks=[
    record(name='Results',page=[
      record(udi="/node/IQUV_azel_frame",viewer="Result Plotter",pos=(2,0)),
      record(udi="/node/azel_frame",viewer="Result Plotter",pos=(0,0)),
      record(udi="/node/sky_frame",viewer="Result Plotter",pos=(0,1)),
      record(udi="/node/pol_sky",viewer="Result Plotter",pos=(1,1)),
      record(udi="/node/IQUV_sky",viewer="Result Plotter",pos=(1,0))])])

mep_beam_weights = 'beam_weights_rotate_' + str(l_beam) + '_' + str(m_beam) + '.mep'


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
# ns.ParAngle << Meq.ParAngle(radec=ns.RADec0, xyz=ns.XYZ)
# freeze beam position over 'tile' interval by getting the mean over interval
# pa = ns.ParAngle_mean << Meq.Mean(ns.ParAngle)
  pa = ns.ParAngle << Meq.Constant(0.001)
  cospa = ns << Meq.Cos(pa);
  sinpa = ns << Meq.Sin(pa);
  ns.pa_rotate << Meq.Matrix22(cospa,-sinpa,sinpa,cospa)
  ns.pa_rotate_t << Meq.ConjTranspose(ns.pa_rotate)
  ns.pa_inv << Meq.Matrix22(cospa,sinpa,-sinpa,cospa);
  ns.pa_inv_t << Meq.ConjTranspose(ns.pa_inv);

  # define desired half-intensity width of power pattern (HPBW)
  # as we are fitting total intensity I pattern (here .021 rad = 74.8 arcmin)
  ns.fwhm << Meq.Constant(0.021747) # beam FWHM
  ns.width_factor << Meq.Constant(1.0)
  ns.width << ns.width_factor * ns.fwhm


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
  ns.lm_prime_beam << Meq.LMN(ns.RADec0, ns.RaDec_beam, pa)
  ns.l_prime_beam << Meq.Selector(ns.lm_prime_beam, index=0)
  ns.m_prime_beam << Meq.Selector(ns.lm_prime_beam, index=1)
  ns.lm_beam << Meq.Composer(ns.l_prime_beam,ns.m_prime_beam);


# setup for fitting the phased up beam to a gaussian
  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);

# constant for half-intensity determination
  ns.ln_16 << Meq.Constant(-2.7725887)

# total intensity gaussian to which we want to optimize beams
  ns.lm_x_sq << Meq.Sqr(laxis - ns.l_prime_beam) + Meq.Sqr(maxis - ns.m_prime_beam)
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
  # note - in the case of a sky with no Q,U,V as is the case above, the 
  # pa_rotate operations below are really not needed
  ns.azel_frame << Meq.MatrixMultiply(ns.E, ns.pa_rotate,ns.B0, ns.pa_rotate_t,ns.Et)
  # extract the 'equivalent' of I,Q,U,V etc at this parallactic angle
  # note that dipoles are not oriented N/S on the sky so these are not
  # the proper values - they are just used to check the solution results
  ns.IpQ_azel_frame << Meq.Selector(ns.azel_frame,index=0)  # XX = (I+Q)/2
  ns.ImQ_azel_frame << Meq.Selector(ns.azel_frame,index=3)  # YY = (I-Q)/2
  ns.I_azel_frame << Meq.Add(ns.IpQ_azel_frame,ns.ImQ_azel_frame) # I = XX + YY
  ns.Q_azel_frame << Meq.Subtract(ns.IpQ_azel_frame,ns.ImQ_azel_frame) # Q = XX - YY

  ns.UpV_azel_frame << Meq.Selector(ns.azel_frame,index=1)  # XY = (U+iV)/2
  ns.UmV_azel_frame << Meq.Selector(ns.azel_frame,index=2)  # YX = (U-iV)/2
  ns.U_azel_frame << Meq.Add(ns.UpV_azel_frame,ns.UmV_azel_frame) # U = XY + YX
  ns.iV_azel_frame << Meq.Subtract(ns.UpV_azel_frame,ns.UmV_azel_frame) # iV = XY - YX  <----!!
  ns.V_azel_frame << ns.iV_azel_frame / 1j                         # V = iV / i

  ns.I_real_azel_frame << Meq.Real(ns.I_azel_frame)
  ns.Q_real_azel_frame << Meq.Real(ns.Q_azel_frame)
  ns.U_real_azel_frame << Meq.Real(ns.U_azel_frame)
  ns.V_real_azel_frame << Meq.Real(ns.V_azel_frame)
  ns.IQUV_azel_frame << Meq.Matrix22(ns.I_real_azel_frame,ns.Q_real_azel_frame,ns.U_real_azel_frame,ns.V_real_azel_frame)

# now attempt to de-rotate the image observed on the az-el grid
  ns.l << Meq.Grid(axis=2);     # returns l(l) = l
  ns.m << Meq.Grid(axis=3);     # returns m(m) = m
  ns.lm_pre_rot << Meq.Composer(ns.l,ns.m)    # returns an lm 2-vector

# compute the l,m locations on the sky that correspond to the l,m locations
# on the az-el grid. Since the sky and Azel grids align at a parallactic angle 
# of zero, rotating the az-el grid by the parallactic angle does this
  ns.rot_lm << Meq.MatrixMultiply(ns.pa_rotate,ns.lm_pre_rot);    # rotated lm
  ns.l_rot << Meq.Selector(ns.rot_lm,index=0)
  ns.m_rot << Meq.Selector(ns.rot_lm,index=1)
  ns.lm_rot << Meq.Composer(Meq.Grid(axis=0),Meq.Grid(axis=1),ns.l_rot,ns.m_rot)


  # extract real and imaginary components of the voltage responses
  ns.xx << Meq.Selector(ns.azel_frame,index=0)  # XX = (I+Q)/2
  ns.xy << Meq.Selector(ns.azel_frame,index=1)  # YY = (I-Q)/2
  ns.yx << Meq.Selector(ns.azel_frame,index=2)  # XY = (U+iV)/2
  ns.yy << Meq.Selector(ns.azel_frame,index=3)  # YX = (U-iV)/2
  ns.xx_r << Meq.Real(ns.xx)
  ns.xy_r << Meq.Real(ns.xy)
  ns.yx_r << Meq.Real(ns.yx)
  ns.yy_r << Meq.Real(ns.yy)
  ns.xx_i << Meq.Imag(ns.xx)
  ns.xy_i << Meq.Imag(ns.xy)
  ns.yx_i << Meq.Imag(ns.yx)
  ns.yy_i << Meq.Imag(ns.yy)
                           
  ns.resampler_xx_r << Meq.Resampler(ns.xx_r,dep_mask = 0xff)
  ns.xx_orig_r << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xx_r],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_xy_r << Meq.Resampler(ns.xy_r,dep_mask = 0xff)
  ns.xy_orig_r << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xy_r],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yx_r << Meq.Resampler(ns.yx_r,dep_mask = 0xff)
  ns.yx_orig_r << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yx_r],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yy_r << Meq.Resampler(ns.yy_r,dep_mask = 0xff)
  ns.yy_orig_r << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yy_r],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_xx_i << Meq.Resampler(ns.xx_i,dep_mask = 0xff)
  ns.xx_orig_i << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xx_i],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_xy_i << Meq.Resampler(ns.xy_i,dep_mask = 0xff)
  ns.xy_orig_i << Meq.Compounder(children=[ns.lm_rot,ns.resampler_xy_i],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yx_i << Meq.Resampler(ns.yx_i,dep_mask = 0xff)
  ns.yx_orig_i << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yx_i],common_axes=[hiid('l'),hiid('m')])
  ns.resampler_yy_i << Meq.Resampler(ns.yy_i,dep_mask = 0xff)
  ns.yy_orig_i << Meq.Compounder(children=[ns.lm_rot,ns.resampler_yy_i],common_axes=[hiid('l'),hiid('m')])
  ns.vis_orig << Meq.Matrix22(Meq.ToComplex(ns.xx_orig_r,ns.xx_orig_i),Meq.ToComplex(ns.xy_orig_r,ns.xy_orig_i),Meq.ToComplex(ns.yx_orig_r,ns.yx_orig_i),Meq.ToComplex(ns.yy_orig_r,ns.yy_orig_i))
 # the above signals are in the right place on the sky, but the dipoles
 # are oriented in the Az-El frame, so we must invert back to the sky
 # stokes reference frame
  ns.sky_frame << Meq.MatrixMultiply(ns.pa_inv,ns.vis_orig,ns.pa_inv_t)

 # extract I,Q,U,V etc
  ns.IpQ << Meq.Selector(ns.sky_frame,index=0)  # XX = (I+Q)/2
  ns.ImQ << Meq.Selector(ns.sky_frame,index=3)  # YY = (I-Q)/2
  ns.I << Meq.Add(ns.IpQ,ns.ImQ)                     # I = XX + YY
  ns.Q << Meq.Subtract(ns.IpQ,ns.ImQ)                # Q = XX - YY

  ns.UpV << Meq.Selector(ns.sky_frame,index=1)  # XY = (U+iV)/2
  ns.UmV << Meq.Selector(ns.sky_frame,index=2)  # YX = (U-iV)/2
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
    ns.req_seq<<Meq.ReqSeq(parms_req_mux, solver_x, solver_y, ns.IQUV_azel_frame, ns.IQUV_sky, ns.pol_sky)
  else:
    ns.req_seq<<Meq.ReqSeq(parms_req_mux, ns.IQUV_azel_frame, ns.IQUV_sky, ns.pol_sky)

########################################################################
def _test_forest(mqs,parent):

# delete any previous version if the mep file ...
  print 'trying to delete file ', mep_beam_weights
  try:
    command = "rm -rf "+ mep_beam_weights
    os.system(command)
    print 'issued OS command ', command
  except:   pass

# any large time range will do: we observe the changes in the beam
# pattern in timesteps of 3600s, or 1 hr
  delta_t = 900.0 * 16
# delta_t = 3600.0
  # t0 = -1200.0 + 0.5 * delta_t
  # Approx start of 2007
  t0 = 4674314227.58 - 1.5 * delta_t       
  t1 = t0 + delta_t

  f0 = 800.0
  f1 = 1300.0

  m_range = [-0.15,0.15];
  l_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
# for i in range(16):
# for i in range(8):
# for i in range(32):
  for i in range(1):
      t0 = t0 + delta_t
      t1 = t1 + delta_t
      mqs.clearcache('IQUV_sky',recursive=True)
      request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],l_range,m_range], nr_cells = [1,1,lm_num,lm_num])
      counter = counter + 1
# execute request
      mqs.meq('Node.Execute',record(name='req_seq',request=request),wait=False);
#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
