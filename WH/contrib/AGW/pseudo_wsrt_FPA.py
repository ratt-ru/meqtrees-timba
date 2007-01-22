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

# determine the E_Jones for beams calculated for antenna with
# struts
# History:
# - 17 Jan 2007: creation:

#=======================================================================
# Import of Python / TDL modules:

# Get TDL and Meq for the Kernel
from Timba.TDL import * 
from Timba.Meq import meqds
from Timba.Meq import meq
from Meow import Bookmarks,Utils

import os

Settings.forest_state = record(bookmarks=[
  record(name='E Jones',page=Bookmarks.PlotPage(
      ["E"],
  )),
])
# to force caching put 100
Settings.forest_state.cache_policy = 100


########################################################
def _define_forest(ns):  

# read in beam images
  home_dir = os.environ['LOFAR_AGW']
  # read in beam data

  infile_name_re_yx = home_dir + '/veidt_stuff/yx_real.fits'
  infile_name_im_yx = home_dir + '/veidt_stuff/yx_imag.fits'
  infile_name_re_yy = home_dir + '/veidt_stuff/yy_real.fits'
  infile_name_im_yy = home_dir + '/veidt_stuff/yy_imag.fits' 
  ns.image_re_yx << Meq.FITSImage(filename=infile_name_re_yx,cutoff=1.0,mode=2)
  ns.image_im_yx << Meq.FITSImage(filename=infile_name_im_yx,cutoff=1.0,mode=2)
  ns.image_re_yy << Meq.FITSImage(filename=infile_name_re_yy,cutoff=1.0,mode=2)
  ns.image_im_yy << Meq.FITSImage(filename=infile_name_im_yy,cutoff=1.0,mode=2)
  ns.beam_yx << Meq.ToComplex(ns.image_re_yx, ns.image_im_yx)
  ns.beam_yy << Meq.ToComplex(ns.image_re_yy, ns.image_im_yy)

  infile_name_re_xx = home_dir + '/veidt_stuff/xx_real.fits'
  infile_name_im_xx = home_dir + '/veidt_stuff/xx_imag.fits'
  infile_name_re_xy = home_dir + '/veidt_stuff/xy_real.fits'
  infile_name_im_xy = home_dir + '/veidt_stuff/xy_imag.fits'
  ns.image_re_xx << Meq.FITSImage(filename=infile_name_re_xx,cutoff=1.0,mode=2)
  ns.image_im_xx << Meq.FITSImage(filename=infile_name_im_xx,cutoff=1.0,mode=2)
  ns.image_re_xy << Meq.FITSImage(filename=infile_name_re_xy,cutoff=1.0,mode=2)
  ns.image_im_xy << Meq.FITSImage(filename=infile_name_im_xy,cutoff=1.0,mode=2)
  ns.beam_xx << Meq.ToComplex(ns.image_re_xx, ns.image_im_xx)
  ns.beam_xy << Meq.ToComplex(ns.image_re_xy, ns.image_im_xy)

  # I think the following order is correct!
  ns.E << Meq.Matrix22(ns.beam_xx, ns.beam_xy,ns.beam_yx, ns.beam_yy)
  ns.fits <<Meq.FITSWriter(ns.E, filename= '!test.fits')
########################################################################
def _test_forest(mqs,parent):

# any large time range will do
  t0 = 0.0;
  t1 = 1.5e70

  f0 = 0.5
  f1 = 1.5

  lm_range = [-0.04,0.04];
  lm_num = 50;
# define request
  request = make_request(counter=1, dom_range = [[f0,f1],[t0,t1],lm_range,lm_range], nr_cells = [1,1,lm_num,lm_num])
# execute request
  mqs.meq('Node.Execute',record(name='fits',request=request),wait=True);

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
  
