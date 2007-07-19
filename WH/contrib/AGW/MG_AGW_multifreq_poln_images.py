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

# determine the observed instrumental polarization pattern for
# an interferometer observing with GRASP-designed beams as a function
# of frequency

# History:
# 14-Feb-2007 created
#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq

# setup a bookmark for display of results with a 'Results Plotter'
Settings.forest_state = record(bookmarks=[
  record(name='I Q U V',page=[
    record(udi="/node/IQUV",viewer="Result Plotter",pos=(2,0)),
    record(udi="/node/I",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/Q",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/U",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/V",viewer="Result Plotter",pos=(1,1))]),
  record(name='norm',page=[
    record(udi="/node/im_x_max",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/im_y_max",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/im_x",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/im_y",viewer="Result Plotter",pos=(1,1))]),
  record(name='normalized beams',page=[
    record(udi="/node/beam_xx",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/beam_xy",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/beam_yx",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/beam_yy",viewer="Result Plotter",pos=(1,1))]),
  record(name='raw beams',page=[
    record(udi="/node/image_re_xx",viewer="Result Plotter",pos=(0,0)),
    record(udi="/node/image_im_xx",viewer="Result Plotter",pos=(0,1)),
    record(udi="/node/image_re_xy",viewer="Result Plotter",pos=(1,0)),
    record(udi="/node/image_im_xy",viewer="Result Plotter",pos=(1,1)),
    record(udi="/node/image_re_yx",viewer="Result Plotter",pos=(2,0)),
    record(udi="/node/image_im_yx",viewer="Result Plotter",pos=(2,1)),
    record(udi="/node/image_re_yy",viewer="Result Plotter",pos=(3,0)),
    record(udi="/node/image_im_yy",viewer="Result Plotter",pos=(3,1))]),
  ]);

# to force caching put 100
Settings.forest_state.cache_policy = 100

########################################################
def _define_forest(ns):  

# read in beam images

  home_dir = '/home/twillis/Timba/WH/contrib/AGW'
  # read in beam data
  fits_num = 2

  infile_name_re_yx = home_dir + '/veidt_multifreq/yx_' + str(fits_num) + '_Re_x.fits'
  infile_name_im_yx = home_dir + '/veidt_multifreq/yx_' + str(fits_num) + '_Im_x.fits'
  infile_name_re_yy = home_dir + '/veidt_multifreq/yy_' + str(fits_num) + '_Re_y.fits'
  infile_name_im_yy = home_dir + '/veidt_multifreq/yy_' + str(fits_num) + '_Im_y.fits'
  ns.image_re_yx << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
  ns.image_im_yx << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
  ns.image_re_yy << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
  ns.image_im_yy << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)

  # normalize beam to peak response
  ns.im_sq_y << ns.image_re_yy * ns.image_re_yy + ns.image_im_yy * ns.image_im_yy +\
                ns.image_re_yx * ns.image_re_yx + ns.image_im_yx * ns.image_im_yx
  ns.im_y << Meq.Sqrt(ns.im_sq_y)
  ns.im_y_max << Meq.Max(ns.im_y,reduction_axes=["L", "M"])

  ns.beam_yx << Meq.ToComplex(ns.image_re_yx, ns.image_im_yx) / ns.im_y_max
  ns.beam_yy << Meq.ToComplex(ns.image_re_yy, ns.image_im_yy) / ns.im_y_max

  infile_name_re_xx = home_dir + '/veidt_multifreq/xx_' + str(fits_num) + '_Re_x.fits'
  infile_name_im_xx = home_dir + '/veidt_multifreq/xx_' + str(fits_num) + '_Im_x.fits'
  infile_name_re_xy = home_dir + '/veidt_multifreq/xy_' + str(fits_num) + '_Re_y.fits'
  infile_name_im_xy = home_dir + '/veidt_multifreq/xy_' + str(fits_num) + '_Im_y.fits'
  ns.image_re_xx << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
  ns.image_im_xx << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)
  ns.image_re_xy << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
  ns.image_im_xy << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)


  ns.im_sq_x << ns.image_re_xx * ns.image_re_xx + ns.image_im_xx * ns.image_im_xx +\
                ns.image_re_xy * ns.image_re_xy + ns.image_im_xy * ns.image_im_xy
  ns.im_x << Meq.Sqrt(ns.im_sq_x)
  ns.im_x_max << Meq.Max(ns.im_x,reduction_axes=["L", "M"])

  ns.beam_xx << Meq.ToComplex(ns.image_re_xx, ns.image_im_xx) / ns.im_x_max
  ns.beam_xy << Meq.ToComplex(ns.image_re_xy, ns.image_im_xy) / ns.im_x_max

  # Create E-Jones from beam data
  # I think the following order is correct!
  ns.E << Meq.Matrix22(ns.beam_xx, ns.beam_yx,ns.beam_xy, ns.beam_yy)
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
  ns.IQUV << Meq.Real(ns.IQUV_complex)
  ns.Ins_pol << ns.IQUV / ns.I

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

  f0 = 700000000.0
  f1 = 1400000000.0


  lm_range = [-0.04,0.04];
  lm_num = 50;
# define request
  request = make_request(counter=1, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='Ins_pol',request=request),wait=True);


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
  
