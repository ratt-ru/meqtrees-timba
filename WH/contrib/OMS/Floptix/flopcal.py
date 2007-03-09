# standard preamble
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

import floptix

Settings.forest_state.cache_policy = 1;

_dbg = utils.verbosity(0,name='fit_image');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

TDLCompileOption('filename_pattern',"Image filename pattern",["test.pgm-.*","test.pgm"],more=str);
TDLCompileOption('directory_name',"Directory name",["."],more=str);
TDLCompileOption('scaling_factor',"Rescale image",[.25,.5,1],more=float);
TDLCompileOption('ideal_fwhm',"Ideal FWHM",[3],more=float);
TDLCompileOption('masking_radius',"Radius of box around sources",[20],more=int);
TDLCompileOption('static_mode',"Static mode for testing",False);

def read_lsm (filename):
  """Reads catalog file produced by sextractor, returns a list
  of (id,x,y) tuples""";
  sources = [];
  for line in open(filename).readlines():
    _dprint(0,"catalog line",line);
    if not line.startswith('#'):
      fields = re.split('[^\d.-]+',line);
      _dprint(0,"catalog fields",len(fields),fields);
      src = fields[1];
      x,y = float(fields[6]),float(fields[5]);
      sources.append((src,x,y));
  return sources;

def make_lsm (ns,sources,support=False):    
  """Creates an LSM tree from a catalog file""";
  # create xy coordinate node
  ns.xy << Meq.Composer(
    ns.x << Meq.Grid(axis=floptix.image_xaxis),
    ns.y << Meq.Grid(axis=floptix.image_yaxis)
  );
  # make two sets of sources: with a solvable fwhm, and
  # with a static fwhm
  ns.fwhm('fit') << Meq.Parm(1,tags="lsm fwhm");
  ns.fwhm('ideal') << Meq.Parm(ideal_fwhm);
  for tp in ('fit','ideal'):
    ns.sigma(tp) << ns.fwhm(tp)/2.3548; 
    ns.sigsq_2(tp) << 2*Meq.Sqr(ns.sigma(tp));
  #  now make the other nodes
  ns.vec11 << Meq.Composer(1,1,dims=[1,2]); # (1,1) row vector: (1,1)*(x,y)^t = x+y
  xy_nodes = [];
  source_nodes = [];
  # now loop over sources
  for src,x,y in sources:
    ns.flux(src) << Meq.Parm(0,tags="lsm flux")
    ns.xy0(src) << Meq.Composer(
      ns.x0(src) << Meq.Parm(x,tags="lsm pos"),
      ns.y0(src) << Meq.Parm(y,tags="lsm pos")
    );
    xy_nodes.append(ns.xy0(src));
    # create support
    if support:
      supp = ns.supp(src) << Meq.Parm(0,tags="lsm supp");
    # create gaussian at x0,y0
    xy2 = ns.dxy2(src) << Meq.Sqr(ns.xy - ns.xy0(src));
    xy2sum = ns.xy2sum(src) << Meq.MatrixMultiply(ns.vec11,xy2);
    for tp in ('fit','ideal'):
      gaussian = ns.flux(src)*Meq.Exp(-xy2sum/ns.sigsq_2(tp))/(math.pi*ns.sigsq_2(tp));
      if support:
        ns.img(src,tp) << gaussian + supp;
      else:
        ns.img(src,tp) << gaussian;
      
  # sum things up for the two types of lsm
  for tp in ('fit','ideal'):
    ns.lsm(tp) << Meq.Add(mt_polling=True,*[ns.img(src,tp) for src,x,y in sources]);
  
  # add node to flag everything except sources
  ns.lsm('mask') << Meq.PyNode(class_name="floptix.PyMakeLsmMask",
                               radius=masking_radius,*xy_nodes);

  return ns.lsm('fit'),ns.lsm('ideal'),ns.lsm('mask');            

def _define_forest (ns,**kwargs):
  # run source finding on current image
  if static_mode:
    filename = filename_pattern;
  else:
    filename = floptix.acquire_imagename(filename_pattern,directory=directory_name);
  _dprint(0,"running source finding on",filename);
  if scaling_factor == 1:
    os.system("pnmtofits %s >%s.fits"%(filename,filename))
  else:
    os.system("pnmscale %f %s | pnmtofits >%s.fits"%(scaling_factor,filename,filename))
  os.system("sextractor %s.fits"%filename);
  # get image shape
  global image_nx;
  global image_ny;
  image_nx,image_ny = pyfits.open("%s.fits"%filename)[0].data.shape;
  os.system("rm -f %s.fits"%filename);
  _dprint(0,"scaled image size is",image_nx,image_ny);

  # now make the tree
  ns.img << Meq.PyNode(class_name="floptix.PyCameraImage",
                       directory_name=directory_name,
                       file_name=filename_pattern,
                       static_mode=static_mode,
                       rescale=scaling_factor,
                       node_groups=['Parm'],
                       tags="actuators"
                       );
  # make LSM
  sources = read_lsm('test.cat');
  lsm_fit,lsm_ideal,lsm_mask = make_lsm(ns,sources,support=True);
  
  # apply mask to incoming image
  masked_image = ns.masked_img << Meq.MergeFlags(ns.img,lsm_mask);
  
  # make branch to solve for LSM sources
  bk = Meow.Bookmarks.Page("LSM fit");
  ns.ce_lsm << Meq.Condeq(masked_image,lsm_fit);
  ns.residual_lsm << ns.img - lsm_fit;
  ns.solver_lsm << Meq.Solver(ns.ce_lsm,num_iter=20,epsilon=1e-4,last_update=True,solvable=lsm_fit.search(tags="lsm"));
  bk.add(masked_image);
  bk.add(ns.ce_lsm);
  bk.add(ns.residual_lsm);
  bk.add(ns.solver_lsm);
  ns.reqseq_lsm << Meq.ReqSeq(ns.solver_lsm,ns.residual_lsm);
  
  # make branch to solve for LSM sources
  bk = Meow.Bookmarks.Page("Optical calibration");
  ns.ce_cal << Meq.Condeq(masked_image,lsm_ideal);
  ns.residual_cal << ns.img - lsm_ideal;
  ns.solver_cal << Meq.Solver(ns.ce_cal,num_iter=20,epsilon=1e-4,last_update=True,solvable=masked_image.search(tags="actuators"));
  bk.add(masked_image);
  bk.add(ns.ce_cal);
  bk.add(ns.residual_cal);
  bk.add(ns.solver_cal);
  ns.reqseq_cal << Meq.ReqSeq(ns.solver_cal,ns.residual_cal);
  

def _tdl_job_1_solve_for_LSM (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq_lsm',request);

def _tdl_job_2_calibrate_optics (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq_cal',request);
