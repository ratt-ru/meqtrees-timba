#!/usr/bin/python

#
# Copyright (C) 2007
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
# and form a combined, weighted beam using the method of
# phase conjugation. The weights
# are found by getting complex values at specified
# L,M location in the X (|| poln) beams and then
# taking the conjugate transpose.

# The resulting weights are stored in a mep table for possible
# later use.

# History:
# - 27 Feb 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils

from numarray import *
import os

#setup a bookmark for display of results with a 'Collections Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='Results',page=[
    record(udi="/node/I_real",viewer="Result Plotter",pos=(0,0))])])

# to force caching put 100
Settings.forest_state.cache_policy = 100

mep_beam_weights = 'beam_weights.mep'
# first, make sure that any previous version of the mep table is
# obliterated so nothing strange happens in succeeding steps
try:
  os.system("rm -fr "+ mep_beam_weights);
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
#                 node_groups='Parm', save_all=True,
                  table_name=mep_beam_weights)

########################################################
def _define_forest(ns):  

  # define location for phase-up
# BEAM_LM = [(0.0,0.0)]                # xntd_0
# BEAM_LM = [(0.00543675,0.0)]         # xntd_0_a
# BEAM_LM = [(0.0108735,0.0)]          # xntd_1
# BEAM_LM = [(0.01631025,0.0)]         # xntd_1_a
# BEAM_LM = [(0.021747,0.0)]           # xntd_2
# BEAM_LM = [(0.02718375,0.0)]         
# BEAM_LM = [(0.032620,0.0)]           # xntd_3
  BEAM_LM = [(0.038057,0.0)]           # xntd_3_a
# BEAM_LM = [(0.043494,0.0)]           # xntd_4
# BEAM_LM = [(0.04893075,0.0)]           # xntd_4
# BEAM_LM = [(0.0543675,0.0)]           # xntd_4
# BEAM_LM = [(0.05980425,0.0)]           # xntd_4
# BEAM_LM = [(0.065241,0.0)]           # xntd_4
# BEAM_LM = [(0.065241,0.065241)]           # xntd_4
# BEAM_LM = [(0.0761145,0.0)]           # xntd_4
# BEAM_LM = [(0.0, 0.0108735)]         # xntd_m_1
# BEAM_LM = [(0.0, 0.021747)]          # xntd_m_2
# BEAM_LM = [(0.0, 0.032620)]          # xntd_m_3
# BEAM_LM = [(0.0, 0.043494)]          # xntd_m_4
# BEAM_LM = [(0.0, 0.04893075)]          # xntd_m_4
# BEAM_LM = [(-0.00543675,0.0)]         # xntd_0_a
# BEAM_LM = [(-0.0108735,0.0)]          # xntd_1
# BEAM_LM = [(-0.01631025,0.0)]         # xntd_1_a
# BEAM_LM = [(-0.021747,0.0)]           # xntd_2
# BEAM_LM = [(-0.02718375,0.0)]         
# BEAM_LM = [(-0.032620,0.0)]           # xntd_3
# BEAM_LM = [(-0.038057,0.0)]           # xntd_3_a
# BEAM_LM = [(-0.043494,0.0)]           # xntd_4
# BEAM_LM = [(-0.0543675,0.0)]           # xntd_4
# BEAM_LM = [(-0.065241,0.0)]           # xntd_4
# BEAM_LM = [(-0.0761145,0.0)]           # xntd_4
# BEAM_LM = [(0.043494,0.043494)]           # xntd_3_a
  l_beam,m_beam = BEAM_LM[0]
  ns.l_beam_c << Meq.Constant(l_beam) 
  ns.m_beam_c << Meq.Constant(m_beam)

  ns.lm_beam << Meq.Composer(ns.l_beam_c,ns.m_beam_c);

# read in beam images
  num_beams = 90
  BEAMS = range(0,num_beams)
  home_dir = os.environ['HOME']
  # read in beam data
  beam_solvables = []
  parm_solvers = []
  for k in BEAMS:
  # read in beam data - y dipole
    infile_name_re_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+num_beams) + '_Re_x.fits'
    infile_name_im_yx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+num_beams) +'_Im_x.fits'
    infile_name_re_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+num_beams) +'_Re_y.fits'
    infile_name_im_yy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k+num_beams) +'_Im_y.fits' 
    ns.image_re_yx(k) << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
    ns.image_im_yx(k) << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
    ns.image_re_yy(k) << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
    ns.image_im_yy(k) << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)

  # normalize
    ns.y_im_sq(k) << ns.image_re_yy(k) * ns.image_re_yy(k) + ns.image_im_yy(k) * ns.image_im_yy(k) +\
                  ns.image_re_yx(k) * ns.image_re_yx(k) + ns.image_im_yx(k) * ns.image_im_yx(k)
    ns.y_im(k) <<Meq.Sqrt(ns.y_im_sq(k))
    ns.y_im_max(k) <<Meq.Max(ns.y_im(k))
    ns.norm_image_re_yy(k) << ns.image_re_yy(k) / ns.y_im_max(k)
    ns.norm_image_im_yy(k) << ns.image_im_yy(k) / ns.y_im_max(k)
    ns.norm_image_re_yx(k) << ns.image_re_yx(k) / ns.y_im_max(k)
    ns.norm_image_im_yx(k) << ns.image_im_yx(k) / ns.y_im_max(k)

    ns.resampler_image_re_yy(k) << Meq.Resampler(ns.norm_image_re_yy(k),dep_mask = 0xff)
    ns.resampler_image_im_yy(k) << Meq.Resampler(ns.norm_image_im_yy(k),dep_mask = 0xff)
    ns.sample_wt_re_y(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_yy(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_y(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_yy(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
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

    ns.beam_yx(k) << Meq.ToComplex(ns.norm_image_re_yx(k), ns.norm_image_im_yx(k)) 
    ns.beam_yy(k) << Meq.ToComplex(ns.norm_image_re_yy(k), ns.norm_image_im_yy(k))
    ns.wt_beam_yx(k) << ns.beam_yx(k) * ns.beam_weight_y(k)
    ns.wt_beam_yy(k) << ns.beam_yy(k) * ns.beam_weight_y(k)

  # read in beam data - x dipole
    infile_name_re_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) + '_Re_x.fits'
    infile_name_im_xx = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) +'_Im_x.fits'
    infile_name_re_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) +'_Re_y.fits'
    infile_name_im_xy = home_dir + '/Timba/WH/contrib/AGW/veidt_fpa_180/fpa_pat_' + str(k) +'_Im_y.fits' 
    ns.image_re_xy(k) << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
    ns.image_im_xy(k) << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)
    ns.image_re_xx(k) << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
    ns.image_im_xx(k) << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)
  # normalize
    ns.x_im_sq(k) << ns.image_re_xx(k) * ns.image_re_xx(k) + ns.image_im_xx(k) * ns.image_im_xx(k) +\
                  ns.image_re_xy(k) * ns.image_re_xy(k) + ns.image_im_xy(k) * ns.image_im_xy(k)
    ns.x_im(k) <<Meq.Sqrt(ns.x_im_sq(k))
    ns.x_im_max(k) <<Meq.Max(ns.x_im(k))
    ns.norm_image_re_xx(k) << ns.image_re_xx(k) / ns.x_im_max(k)
    ns.norm_image_im_xx(k) << ns.image_im_xx(k) / ns.x_im_max(k)
    ns.norm_image_re_xy(k) << ns.image_re_xy(k) / ns.x_im_max(k)
    ns.norm_image_im_xy(k) << ns.image_im_xy(k) / ns.x_im_max(k)


    ns.resampler_image_re_xx(k) << Meq.Resampler(ns.norm_image_re_xx(k),dep_mask = 0xff)
    ns.resampler_image_im_xx(k) << Meq.Resampler(ns.norm_image_im_xx(k),dep_mask = 0xff)
    ns.sample_wt_re_x(k) << Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_re_xx(k)],common_axes=[hiid('l'),hiid('m')])
    ns.sample_wt_im_x(k) << -1.0 * Meq.Compounder(children=[ns.lm_beam,ns.resampler_image_im_xx(k)],common_axes=[hiid('l'),hiid('m')])
    # I want to solve for these parameters
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

    ns.beam_xy(k) << Meq.ToComplex(ns.norm_image_re_xy(k), ns.norm_image_im_xy(k)) 
    ns.beam_xx(k) << Meq.ToComplex(ns.norm_image_re_xx(k), ns.norm_image_im_xx(k))
    ns.wt_beam_xy(k) << ns.beam_xy(k) * ns.beam_weight_x(k)
    ns.wt_beam_xx(k) << ns.beam_xx(k) * ns.beam_weight_x(k)

  # solver to 'copy' resampled beam locations to parms as
  # first guess
  ns.parms_req_mux<<Meq.ReqMux(children=parm_solvers)

  # sum the weights
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
  ns.I_select << Meq.Real(ns.I)
  ns.I_max << Meq.Max(ns.I_select)
  ns.I_real  << ns.I_select / ns.I_max
  ns.I_parm_max << tpolc(0)
  ns.condeq_I_max << Meq.Condeq(children=(ns.I_parm_max, ns.I_max))
  ns.solver_I_max <<Meq.Solver(ns.condeq_I_max,num_iter=50,epsilon=1e-4,solvable=ns.I_parm_max,save_funklets=True,last_update=True)

  ns.req_seq<<Meq.ReqSeq(ns.parms_req_mux, ns.solver_I_max, ns.I_real)

########################################################################
def _test_forest(mqs,parent):

# any large time range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 5000.0e6

  lm_range = [-0.15,0.15];
  lm_num = 50;
  counter = 0
  request = make_request(counter=counter, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='req_seq',request=request),wait=False);

#####################################################################
def make_request(counter=0,Ndim=4,dom_range=[0.,1.],nr_cells=5):

    """make multidimensional request, dom_range should have length 2 or be a list of
    ranges with length Ndim, nr_cells should be scalar or list of scalars with length Ndim"""
    forest_state=meqds.get_forest_state();
    axis_map=forest_state.axis_map;
    
    range0 = [];
    if is_scalar(dom_range[0]):
        for i in range(Ndim):		
            range0.append(dom_range);
    else:
        range0=dom_range;
    nr_c=[];
    if is_scalar(nr_cells):
        for i in range(Ndim):		
            nr_c.append(nr_cells);
    else:
        nr_c =nr_cells;
    dom = meq.domain(range0[0][0],range0[0][1],range0[1][0],range0[1][1]); #f0,f1,t0,t1
    cells = meq.cells(dom,num_freq=nr_c[0],num_time=nr_c[1]);
    
    # workaround to get domain with more axes running 

    for dim in range(2,Ndim):
        id = axis_map[dim].id;
        if id:
            dom[id] = [float(range0[dim][0]),float(range0[dim][1])];
            step_size=float(range0[dim][1]-range0[dim][0])/nr_c[dim];
            startgrid=0.5*step_size+range0[dim][0];
            grid = [];
            cell_size=[];
        for i in range(nr_c[dim]):
            grid.append(i*step_size+startgrid);
            cell_size.append(step_size);
            cells.cell_size[id]=array(cell_size);
            cells.grid[id]=array(grid);
            cells.segments[id]=record(start_index=0,end_index=nr_c[dim]-1);

    cells.domain=dom;
    rqid = meq.requestid(domain_id=counter)
    request = meq.request(cells,rqtype='ev',rqid=rqid);
    return request;

if __name__=='__main__':
  ns=NodeScope()
  _define_forest(ns)
  ns.Resolve()
  print "Added %d nodes" % len(ns.AllNodes())
  
