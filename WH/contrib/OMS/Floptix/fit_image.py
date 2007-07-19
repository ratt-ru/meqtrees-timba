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

import Meow

import floptix

Settings.forest_state.cache_policy = 1;

_dbg = utils.verbosity(0,name='fit_image');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

TDLCompileOption('init_filename',"Image filename",['t2.fits','t2.pgm']);
TDLCompileOption('scaling_factor',"Rescale image",[.25,.5,1],more=float);

TDLCompileOption('background_order',"Polc order for background fit",[None,1,2,3,4],more=int);
TDLCompileOption('add_support',"Add per-source support term",False);
TDLCompileOption('lsm_file',"Source catalog file",[None,'test.cat']);


def make_lsm (ns,filename,support=False):    
  """Creates an LSM tree from a catalog file""";
#   add_background_offset = background_order is None;
#   sources = [];
#   # for every source, create a flux,x,y 3-pack
#   for line in open(filename).readlines():
#     if not line.startswith('#'):
#       fields = re.split('[\d.-]',line);
#       src = fields[1];
#       sources.append(src);
#       x,y = float(fields[5]),float(fields[6]);
#       lsmpack = ns.lsm_pack(src) << Meq.Composer(
#         ns.flux(src) << Meq.Parm(0,tags="lsm flux"),
#         ns.x(src) << Meq.Parm(x,tags="lsm pos"),
#         ns.y(src) << Meq.Parm(y,tags="lsm pos"));
#       sources.append(lsmpack);
#   ns.fwhm << Meq.Parm(10,tags="lsm fwhm");    
#   
#   # make a Python LSM node to create image with sources
#   ns.lsm_image << Meq.PyTensorFuncNode(
#       class_name="PyLsmMaker",module_name=__file__,
#       add_background_offset=add_background_offset,
#       ns.fwhm,*sources
#       );
  # create xy coordinate node
  ns.xy << Meq.Composer(
    ns.x << Meq.Grid(axis=floptix.image_xaxis),
    ns.y << Meq.Grid(axis=floptix.image_yaxis)
  );
  ns.sigma << Meq.Parm(1,tags="lsm sigma");
  ns.sigsq_2 << 2*Meq.Sqr(ns.sigma);
  ns.vec11 << Meq.Composer(1,1,dims=[1,2]); # (1,1) row vector: (1,1)*(x,y)^t = x+y
  xy_nodes = [];
  source_nodes = [];
  # now loop over sources
  for line in open(filename).readlines():
    _dprint(0,"catalog line",line);
    if not line.startswith('#'):
      fields = re.split('[^\d.-]+',line);
      _dprint(0,"catalog fields",len(fields),fields);
      src = fields[1];
      x,y = float(fields[6])*scaling_factor,float(fields[5])*scaling_factor;
      ns.flux(src) << Meq.Parm(0,tags="lsm flux")
      ns.xy0(src) << Meq.Composer(
        ns.x0(src) << Meq.Parm(x,tags="lsm pos"),
        ns.y0(src) << Meq.Parm(y,tags="lsm pos")
      );
      xy_nodes.append(ns.xy0(src));
      # create gaussian at x0,y0
      xy2 = ns.dxy2(src) << Meq.Sqr(ns.xy - ns.xy0(src));
      xy2sum = ns.xy2sum(src) << Meq.MatrixMultiply(ns.vec11,xy2);
      out = ns.gauss(src) << ns.flux(src)*Meq.Exp(-xy2sum/ns.sigsq_2)/(math.pi*ns.sigsq_2);
      if support:
        supp = ns.supp(src) << Meq.Parm(0,tags="lsm supp");
        out = ns.gauss_supp(src) << out + supp;
      source_nodes.append(out);
      
  # sum things up 
  ns.lsm0 << Meq.Add(mt_polling=True,*source_nodes);
  
  # add node to flag everything except sources
  ns.lsm_mask << Meq.PyNode(class_name="floptix.PyMakeLsmMask",
                            radius=10,*xy_nodes);
            
  ns.lsm << Meq.MergeFlags(ns.lsm0,ns.lsm_mask);
  
  return ns.lsm;



def _define_forest (ns,**kwargs):
  if init_filename.endswith('.fits'):
    ns.img << Meq.PyNode(class_name="floptix.PyFitsImage",
                         file_name=init_filename);
  else:
    ns.img << Meq.PyNode(class_name="floptix.PyPILImage",
                         file_name=init_filename,
                         rescale=scaling_factor);

  if lsm_file is not None:
    make_lsm(ns,lsm_file,support=add_support);
    
  solvers = [];
  image_node = ns.img;
  
  if background_order is not None:  
    bk1 = Meow.Bookmarks.Page("Background");
    bk1.add(ns.img);

    ns.background << Meq.Parm(0.,shape=[background_order,background_order],tags="background"); # table_name="t2.fits.mep");

    ns.ce_bg << Meq.Condeq(ns.img,Meq.MergeFlags(ns.background,ns.lsm_mask));
    image_node = ns.flat_img << ns.img - ns.background;
    ns.solver_bg << Meq.Solver(ns.ce_bg,num_iter=20,epsilon=1e-4,last_update=True,save_funklets=True,solvable=[ns.background]);
    bk1.add(ns.ce_bg);
    bk1.add(ns.flat_img);
    bk1.add(ns.solver_bg);
    
    solvers.append(ns.solver_bg);

  if lsm_file is None:
    ns.root << Meq.ReqSeq(ns.solver_bg,ns.flat_img,result_index=1);
  else:
    bk2 = Meow.Bookmarks.Page("LSM");
    ns.ce_lsm << Meq.Condeq(image_node,ns.lsm);
    ns.residual << image_node - ns.lsm0;   # use unmasked lsm here
    ns.solver_lsm << Meq.Solver(ns.ce_lsm,num_iter=20,epsilon=1e-4,last_update=True,solvable=ns.lsm.search(tags="lsm"));
    bk2.add(image_node);
    bk2.add(ns.ce_lsm);
    bk2.add(ns.residual);
    bk2.add(ns.solver_lsm);
    
    solvers.append(ns.solver_lsm);

  ns.root << Meq.ReqSeq(*(solvers+[ns.residual]));
  
  

def _test_forest (mqs,parent,**kwargs):
  # figure out our image format
  if init_filename.endswith('.fits'):
    nx,ny = pyfits.open(init_filename)[0].data.shape;
  else:
    print init_filename;
    img = PIL.Image.open(init_filename); 
    nx,ny = img.size;
    img = None;
    nx = int(round(nx*scaling_factor));
    ny = int(round(ny*scaling_factor));
  # run tests on the forest
  cells = floptix.make_cells(ny,nx,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('root',request);
