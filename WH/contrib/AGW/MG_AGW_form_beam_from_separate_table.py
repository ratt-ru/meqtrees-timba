#i/usr/bin/python

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
# Reads in FPA beam weights from a aips++ table and phases up the FPA

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
from MG_AGW_read_separate_table_weights import *

from numarray import *
import os

#setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Results',page=[
    record(udi="/node/I_real",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/Ins_pol",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/Q_real",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/U_real",viewer="Result Plotter",pos=(1,1))])])
# to force caching put 100
Settings.forest_state.cache_policy = 100

# get directory with GRASP focal plane array beams
TDLCompileOption('fpa_directory','directory with focal plane array files',['gauss_array_pats','gauss_array_pats_defocus','veidt_fpa_180', 'veidt_fpa_30','veidt_fpa_180_noise'],more=str)

# get position of phase up point in L and M
TDLCompileMenu('L and M position of phased-up beam',
  TDLOption('l_beam','L position of beam (in units of FWHM)',[0,1,2,3],more=float),
  TDLOption('m_beam','M position of beam (in units of FWHM)',[0,1,2,3],more=float),
);

# Attempt to 'form' a Gaussian beam?
TDLCompileOption('use_gauss','Use Gaussian weights from table?',[False,True])

########################################################
def _define_forest(ns):  

#read in weights for system
  I_parm_max_x,I_parm_max_y,weight_re,weight_im = read_separate_table_weights(l_beam, m_beam, use_gauss)

# read in beam images
# number of beams is 30 or 90
  num_beams = read_in_FPA_beams(ns,fpa_directory)
  BEAMS = range(0,num_beams)

# get complex weights for beams
  for k in BEAMS:
    ns.beam_wt_re_x(k) << Meq.Constant(weight_re['beam_wt_re_x:'+ str(k)])
    ns.beam_wt_im_x(k) << Meq.Constant(weight_im['beam_wt_im_x:'+ str(k)])
    ns.beam_weight_x(k) << Meq.ToComplex(ns.beam_wt_re_x(k), ns.beam_wt_im_x(k))

  for k in BEAMS:
    ns.beam_wt_re_y(k) << Meq.Constant(weight_re['beam_wt_re_y:'+ str(k)])
    ns.beam_wt_im_y(k) << Meq.Constant(weight_im['beam_wt_im_y:'+ str(k)])
    ns.beam_weight_y(k) << Meq.ToComplex(ns.beam_wt_re_y(k), ns.beam_wt_im_y(k))

# form a beam
  for k in BEAMS:
    ns.beam_xy(k) << Meq.ToComplex(ns.image_re_xy(k), ns.image_im_xy(k))
    ns.beam_xx(k) << Meq.ToComplex(ns.image_re_xx(k), ns.image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

    ns.beam_yx(k) << Meq.ToComplex(ns.image_re_yx(k), ns.image_im_yx(k))
    ns.beam_yy(k) << Meq.ToComplex(ns.image_re_yy(k), ns.image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

  # sum up the weights
  ns.wt_sum_x << Meq.Add(*[ns.beam_weight_x(k) for k in BEAMS])
  ns.wt_sum_y << Meq.Add(*[ns.beam_weight_y(k) for k in BEAMS])

  # sum beams up and normalize by the summed weights
  ns.voltage_sum_xx_norm << Meq.Add(*[ns.wt_beam_xx(k) for k in BEAMS]) / (ns.wt_sum_x * I_parm_max_x) 
  ns.voltage_sum_xy_norm << Meq.Add(*[ns.wt_beam_xy(k) for k in BEAMS]) / (ns.wt_sum_x * I_parm_max_x) 
  ns.voltage_sum_yx_norm << Meq.Add(*[ns.wt_beam_yx(k) for k in BEAMS]) / (ns.wt_sum_y * I_parm_max_y)
  ns.voltage_sum_yy_norm << Meq.Add(*[ns.wt_beam_yy(k) for k in BEAMS]) / (ns.wt_sum_y * I_parm_max_y)

  ns.E << Meq.Matrix22(ns.voltage_sum_xx_norm, ns.voltage_sum_xy_norm, ns.voltage_sum_yx_norm, ns.voltage_sum_yy_norm)
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

  # join together into one node in order to make a single request
  ns.IQUV_complex << Meq.Composer(ns.I, ns.Q,ns.U, ns.V)

  # comvert to real and normalize
  ns.IQUV << Meq.Real(ns.IQUV_complex) 

  ns.I_real << Meq.Selector(ns.IQUV,index=0)
  ns.Q_real << Meq.Selector(ns.IQUV,index=1)
  ns.U_real << Meq.Selector(ns.IQUV,index=2)
  ns.V_real << Meq.Selector(ns.IQUV,index=3)
  ns.pol_sq << ns.Q_real * ns.Q_real + ns.U_real * ns.U_real + ns.V_real * ns.V_real
  ns.Ins_pol << Meq.Sqrt(ns.pol_sq) / ns.I_real
  ns.fits <<Meq.FITSWriter(ns.I_real, filename= '!beam.fits')
  ns.req_seq << Meq.ReqSeq(ns.Ins_pol, ns.fits)

# Note: we are observing with linearly-polarized dipoles. If we
  # want the aips++ imager to generate images in the sequence I,Q,U,V
  # make sure that the newsimulator setspwindow method uses
  # stokes='XX XY YX YY' and not stokes='RR RL LR LL'. If you
  # do the latter you will get the images rolled out in the
  # order I,U,V,Q!

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
  mqs.meq('Node.Execute',record(name='req_seq',request=request),wait=True);
#####################################################################

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
