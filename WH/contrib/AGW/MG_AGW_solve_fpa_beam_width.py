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

# script_name = 'MG_AGW_multi_beams.py'

# Short description:
# We read in a group of focal plane array beams, 
# and form a combined, weighted beam. The weights
# are found by getting complex values at specified
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose.

# We then fit a gaussian to the phased up beam at boresight to
# get the FWHM

# History:
# - 07 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils
from numarray import *
from make_multi_dim_request import *
from handle_beams import *

import os

Settings.forest_state = record(bookmarks=[
  record(name='fit',page=Bookmarks.PlotPage(
      ["I"], ["condeq"], ["width"],
  )),
])
# to force caching put 100
Settings.forest_state.cache_policy = 100

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_offset','gauss_array_pats_defocus','veidt_fpa_180', 'veidt_fpa_30'],more=str)

mep_beam_parms = 'beam_widths.mep'

try:
  os.system("rm -fr "+ mep_beam_parms);
except:   pass

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

def tpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
                  constrain = [-0.15,0.15],
                  table_name = mep_beam_parms)

def wpolc (tdeg,c00=0.0):
  return Meq.Parm(create_polc(degree_f=0,degree_t=tdeg,c00=c00),
                  node_groups='Parm',
                  constrain = [1.0e-5,1.0],
                  table_name = mep_beam_parms)


########################################################
def _define_forest(ns):  

  BEAM_LM = [(0.0,0.0)]      # location where we phase beams up
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam_c << Meq.Constant(l_beam) 
  ns.m_beam_c << Meq.Constant(m_beam)
  ns.lm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);

  ns.ln_16 << Meq.Constant(-2.7725887)

  ns.width << wpolc(tdeg=0,c00=0.01)
  ns.l << tpolc(tdeg=0,c00=0.0)
  ns.m << tpolc(tdeg=0,c00=0.0)
  
 
 # number of beams is 30 or 90
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  BEAMS = range(0,num_beams)

  for k in BEAMS:

    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.image_im_yy(k),dep_mask = 0xff)
    ns.beam_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_wt_im_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])

    ns.beam_wt_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

    # take transpose for phase conjugate weighting
    ns.beam_weight_y(k) << Meq.ConjTranspose(ns.beam_wt_y(k))

    ns.beam_yx(k) << Meq.ToComplex(ns.image_re_yx(k), ns.image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.image_re_yy(k), ns.image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.image_im_xx(k),dep_mask = 0xff)
    ns.beam_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.beam_wt_im_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])

    ns.beam_wt_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

    # take transpose for phase conjugate weighting
    ns.beam_weight_x(k) << Meq.ConjTranspose(ns.beam_wt_x(k))

    ns.beam_xy(k) << Meq.ToComplex(ns.image_re_xy(k), ns.image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.image_re_xx(k), ns.image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  ns.voltage_sum_xx << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS])
  ns.voltage_sum_xy << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS])
  ns.voltage_sum_yx << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS])
  ns.voltage_sum_yy << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS])

  # normalize beam to peak response
  ns.voltage_sum_xx_r << Meq.Real(ns.voltage_sum_xx)
  ns.voltage_sum_xx_i << Meq.Imag(ns.voltage_sum_xx)
  ns.voltage_sum_xy_r << Meq.Real(ns.voltage_sum_xy)
  ns.voltage_sum_xy_i << Meq.Imag(ns.voltage_sum_xy)
  ns.im_sq_x << ns.voltage_sum_xx_r * ns.voltage_sum_xx_r + ns.voltage_sum_xx_i * ns.voltage_sum_xx_i 
  ns.im_x <<Meq.Sqrt(ns.im_sq_x)
  ns.im_x_max <<Meq.Max(ns.im_x)
  ns.voltage_sum_xx_norm << ns.voltage_sum_xx / ns.im_x_max
  ns.voltage_sum_xy_norm << ns.voltage_sum_xy / ns.im_x_max

  ns.voltage_sum_yy_r << Meq.Real(ns.voltage_sum_yy)
  ns.voltage_sum_yy_i << Meq.Imag(ns.voltage_sum_yy)
  ns.voltage_sum_yx_r << Meq.Real(ns.voltage_sum_yx)
  ns.voltage_sum_yx_i << Meq.Imag(ns.voltage_sum_yx)
  ns.im_sq_y << ns.voltage_sum_yy_r * ns.voltage_sum_yy_r + ns.voltage_sum_yy_i * ns.voltage_sum_yy_i 
  ns.im_y <<Meq.Sqrt(ns.im_sq_y)
  ns.im_y_max <<Meq.Max(ns.im_y)
  ns.voltage_sum_yy_norm << ns.voltage_sum_yy / ns.im_y_max
  ns.voltage_sum_yx_norm << ns.voltage_sum_yx / ns.im_y_max

  ns.E << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_xy_norm,ns.voltage_sum_yx_norm, ns.voltage_sum_yy_norm)
  ns.Et << Meq.ConjTranspose(ns.E)

 # sky brightness
  ns.B0 << 0.5 * Meq.Matrix22(1.0, 0.0, 0.0, 1.0)

  # observe!
  ns.observed << Meq.MatrixMultiply(ns.E, ns.B0, ns.Et)

  # extract I,Q,U,V etc
  ns.IpQ << Meq.Selector(ns.observed,index=0)        # XX = I+Q
  ns.ImQ << Meq.Selector(ns.observed,index=3)        # YY = I-Q
  ns.I_complex << Meq.Add(ns.IpQ,ns.ImQ)             # I = XX + YY
  ns.I << Meq.Real(ns.I_complex)


  laxis = ns.laxis << Meq.Grid(axis=2);
  maxis = ns.maxis << Meq.Grid(axis=3);
  ns.lm_sq << Meq.Sqr(laxis - ns.l) + Meq.Sqr(maxis - ns.m)
  ns.gaussian << Meq.Exp((ns.lm_sq * ns.ln_16)/Meq.Sqr(ns.width));

  ns.resampler_I << Meq.Resampler(ns.I)
  ns.condeq<<Meq.Condeq(children=(ns.resampler_I, ns.gaussian))
  ns.solver<<Meq.Solver(ns.condeq,num_iter=50,epsilon=1e-4,solvable=[ns.l,ns.m,ns.width],save_funklets=True,last_update=True)

########################################################################
def _test_forest(mqs,parent):

# any large time range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 1.5

  lm_range = [-0.15,0.15];
  lm_num = 101;
  counter = 0
  request = make_multi_dim_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='solver',request=request),wait=False);

#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
