# standard preamble
#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
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
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba import mequtils

import pyfits
import PIL.Image
import re
import math
import os
import Meow
import Meow.Utils

import floptix

Settings.forest_state.cache_policy = 1;

_dbg = utils.verbosity(0,name='flopcal');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

TDLCompileOption('static_filename',"Static filename (enables static mode for testing)",[None,'test.pgm'],more=str);
TDLCompileOption('filename_pattern',"Image filename pattern",["live.*pgm","test.pgm"],more=str);
TDLCompileOption('directory_name',"Directory name",["/home/floptix","."],more=str);
TDLCompileOption('scaling_factor',"Rescale image",[.25,.5,1],more=float);
TDLCompileOption('masking_radius',"Radius of box around sources",[20],more=int);
TDLCompileOption('moments_order',"Max moment order",[2]);
TDLCompileOption('moments_image_threshold',"Image threshold for moment calculation",[0,.1,.25,.5],more=float);
background_order = 2;
TDLCompileOption('background_order',"Polc order for background fit",[2,3],more=int);

def read_lsm (filename):
  """Reads catalog file produced by sextractor, returns a list
  of (id,x,y) tuples""";
  sources = [];
  for line in open(filename).readlines():
    _dprint(0,"catalog line",line);
    if not line.startswith('#'):
      fields = re.split('[^\d.eE+-]+',line);
      _dprint(0,"catalog fields",len(fields),fields);
      src = fields[1];
      x,y = float(fields[6]),float(fields[5]);
      sources.append((src,x,y));
  return sources;


def _define_forest (ns,**kwargs):
  os.system("rm -fr lsm.mep");
  global filename_pattern;
  global directory_name;
  _dprint(0,filename_pattern,directory_name,static_filename);
  # run source finding on current image
  if static_filename is not None:
    fname = filename_pattern = static_filename;
    directory_name = ".";
  else:
    fname = floptix.acquire_imagename(filename_pattern,directory=directory_name);
  _dprint(0,"running source finding on",fname);
  if scaling_factor == 1:
    os.system("pnmtofits %s >%s.fits"%(fname,fname))
  else:
    os.system("pnmscale %f %s | pnmtofits >%s.fits"%(scaling_factor,fname,fname))
  # get image shape
  global image_nx;
  global image_ny;
  image_nx,image_ny = pyfits.open("%s.fits"%fname)[0].data.shape;
  os.system("rm -f %s.fits"%fname);
  _dprint(0,"scaled image size is",image_nx,image_ny);


  # now make the tree
  ns.img << Meq.PyNode(class_name="floptix.PyCameraImage",
                       directory_name=directory_name,
                       file_name=filename_pattern,
                       static_mode=(static_filename is not None),
                       rescale=scaling_factor,
                       perturbation=1,pert_scale=1,max_pert=5,
                       node_groups=['Parm'],
                       radius=masking_radius
                     );

  sbk = Meow.Bookmarks.Page("Solvers");
  
  # make a branch to solve for background
  ns.backgr << \
    Meq.Parm(0,shape=[background_order+1,background_order+1],table_name='lsm.mep',tags="background");
  bk = Meow.Bookmarks.Page("Background fit");
  ns.ce_bg << Meq.Condeq(ns.img,ns.backgr);
  ns.img1 << Meq.Subtract(ns.img,ns.backgr,cache_policy=100);
  ns.solver_bg << Meq.Solver(ns.ce_bg,num_iter=20,epsilon=1e-4,
                  last_update=True,save_funklets=True,
                  solvable=[ns.backgr]);
  bk.add(ns.img);
  bk.add(ns.backgr);
  bk.add(ns.ce_bg);
  bk.add(ns.img1);
  sbk.add(ns.solver_bg);
  ns.reqseq_bg << Meq.ReqSeq(ns.solver_bg,ns.img1);
  
  # now make trees to compute the moments
  # read LSM file
  sources = read_lsm('test.cat');
  bk = Meow.Bookmarks.Page("Image and moments");
#  bk.add(ns.img1);
  # construct nodes to extract sources and compute moments
  for src,x,y in sources:
    mom = ns.moments(src) << Meq.PyNode(class_name="floptix.PyMoments",
                          origin_0=[x,y],
                          radius=masking_radius,
                          order=moments_order,
                          image_threshold=moments_image_threshold,
                          children=[ns.img1]
                       );
    bk.add(mom);
    # first moment is image, next two moments are center of gravity, 
    # so make a selector to extract subsequent ones
    m2 = ns.mom2(src) << Meq.Selector(mom,index=range(3,moments_order+2),multi=True);
    # this is the "target" moments that we try to fit
    m0 = ns.mom0 << Meq.Composer(*([0]*(moments_order-1)));
    # create condeq
    ns.ce_mom(src) << Meq.Condeq(m2,m0);
  # make node to acquire all moments
  ns.all_moments << Meq.Composer(*[ns.moments(src) for src,x,y in sources]);
  
  # now make branch to solve for actuators
  bk = Meow.Bookmarks.Page("Optical calibration");
  solvable = [ ns.img ];
  ns.solver_cal << Meq.Solver(children=[ns.ce_mom(src) for src,x,y in sources],
         num_iter=20,
	 epsilon=1e-4,
	 lm_factor=1e-4,
	 last_update=True,
	 solvable=solvable);
  bk.add(ns.mom2(sources[0][0]));
  bk.add(ns.solver_cal);
  sbk.add(ns.solver_cal);
  
def _tdl_job_1_run_source_extraction (mqs,parent,**kwargs):
  global filename_pattern;
  global directory_name;
  # run source finding on current image
  if static_filename is not None:
    filename = static_filename;
    directory_name = '.';
  else:
    filename = floptix.acquire_imagename(filename_pattern,directory=directory_name);
  _dprint(0,"running source finding on",filename);
  if scaling_factor == 1:
    os.system("pnmdepth 32000 %s | pnmtofits >tmp.fits"%(filename,))
  else:
    os.system("pnmscale %f %s | pnmdepth 32000 | pnmtofits >tmp.fits"%(scaling_factor,filename))
  os.system("sextractor tmp.fits");
  
def _tdl_job_2_solve_for_background (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq_bg',request);

def _tdl_job_4_calibrate_optics (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
#  mqs.execute('solver_bg',request);
  mqs.execute('solver_cal',request);

def _tdl_job_5_acquire_image_and_moments (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('all_moments',request);

