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

import Meow

Settings.forest_state.cache_policy = 1;

_dbg = utils.verbosity(0,name='fit_image');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

TDLCompileOption('init_filename',"Image filename",['t2.fits','t2.pgm']);
TDLCompileOption('scaling_factor',"Rescale image",[.25,.5,1],more=float);

image_xaxis = "time";
image_yaxis = "freq";

TDLCompileOption('background_order',"Polc order for background fit",[None,1,2,3,4],more=int);
TDLCompileOption('add_bias',"Add bias term to each source",False);
TDLCompileOption('lsm_file',"Source catalog file",[None,'test.cat']);
TDLCompileOption('lsm_rescale',"Rescale LSM coordinates by",[1,.25],more=float);

def make_cells (nx,ny,xaxis,yaxis):
  """helper function to make an nx by ny cells with the given axes.
  """;
  # make value of same shape as cells
  dom = meq.gen_domain(**{xaxis:[0,nx] , yaxis:[0,ny]});
  return meq.gen_cells(dom,**{'num_'+xaxis : nx , 'num_'+yaxis : ny});
  

class PyFitsImage (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    mystate('file_name','test.fits');
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
                          
  def get_result (self,request,*children):
    # read fits image
    img = pyfits.open(self.file_name)[0].data;
    nx,ny = img.shape;
    _dprint(1,"read FITS image of size ",nx,ny);
    # make cells and value
    cells = make_cells(nx,ny,self.xaxis,self.yaxis);
    value = meq.vells(shape=meq.shape(cells),value=img);
    return meq.result(meq.vellset(value),cells);

class PyPngImage (pynode.PyNode):
  import PIL.Image
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    mystate('file_name','test.png');
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
    mystate('rescale',scaling_factor);
                          
  def get_result (self,request,*children):
    # read PNG image
    img = PIL.Image.open(self.file_name);
    # apply shrink factor, if needed
    if self.rescale != 1.:
      nx,ny = img.size;
      img = img.resize((int(round(nx*self.rescale)),int(round(ny*self.rescale))),PIL.Image.ANTIALIAS);
    # make cells and value, construct array
    nx,ny = img.size;
    cells = make_cells(nx,ny,self.xaxis,self.yaxis);
    value = meq.vells(shape=meq.shape(cells),value=img.getdata());
    return meq.result(meq.vellset(value),cells);


class PyMakeLsmMask (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    mystate('radius',10);
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
    

  def get_result (self,request,*children):
    nx = len(request.cells.grid[self.xaxis]);
    ny = len(request.cells.grid[self.yaxis]);
    # make array to flag everything
    flags = meq.flagvells(shape=(nx,ny));
    flags += 1;
    
    # go over all sources and make a hole in the mask for each
    for res in children:
      x,y = float(res.vellsets[0].value),float(res.vellsets[1].value);
      print "source at ",x,y;
      x0 = max(int(x-self.radius),0);
      x1 = min(int(x+self.radius+1),nx);
      y0 = max(int(y-self.radius),0);
      y1 = min(int(y+self.radius+1),ny);
      flags[x0:x1,y0:y1] = 0;
      
    # reshape flags to proper dimensions
    flagshape = meq.shape(**{self.xaxis:nx,self.yaxis:ny});
    flags.setshape(flagshape);
    vellset = meq.vellset(meq.vells(shape=[1]),flags=flags);
    return meq.result(vellset,request.cells);


class PyLsmMaker (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    mystate('add_background_offset',True);
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
    
  def compute_result_cells (self,request,*children):
    # figure out nx,ny size
    nx = len(self.cells.grid[self.xaxis]);
    ny = len(self.cells.grid[self.yaxis]);
    # make a full output shape (including degenerate axes)
    self._full_shape = make_cells(nx,ny,self.xaxis,self.yaxis);
    # image shape is just 2D
    self._img_shape = (nx,ny);
    return request.cells;
    
  def get_result_dims (self,*dims):
    # verify child dims
    if len(dims)<1:
      raise ValueError,"at least one child expected";
    if len(dims[0]):
      raise ValueError,"child 0 cannot return a tensor";
    for d in dims[1:]:
      if len(d) != 1 or d[0] != 3:
        raise ValueError,"children 1+ must return 3-vectors";
    # result is always scalar
    return [];
                          
  def evaluate_tensors (self,args):
    # args[0] is FWHM
    fwhm = int(args[0][0]);
    # make empty image

def make_lsm (ns,filename,bias=False):    
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
    ns.x << Meq.Grid(axis=image_xaxis),
    ns.y << Meq.Grid(axis=image_yaxis)
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
      if bias:
        b = ns.bias(src) << Meq.Parm(0,tags="lsm bias");
        out = ns.gauss_bias(src) << out + b;
      source_nodes.append(out);
      
  # sum things up 
  ns.lsm0 << Meq.Add(mt_polling=True,*source_nodes);
  
  # add node to flag everything except sources
  ns.lsm_mask << Meq.PyNode(class_name="PyMakeLsmMask",module_name=__file__,
                            radius=10,*xy_nodes);
            
  ns.lsm << Meq.MergeFlags(ns.lsm0,ns.lsm_mask);
  
  return ns.lsm;


def _define_forest (ns,**kwargs):
  ns.img << Meq.PyNode(class_name="PyFitsImage",module_name=__file__,
                       file_name="t2.fits");

  if lsm_file is not None:
    make_lsm(ns,lsm_file,bias=add_bias);
    
  bk1 = Meow.Bookmarks.Page("Background");
  bk1.add(ns.img);

  ns.background << Meq.Parm(0.,shape=[background_order,background_order],tags="background",table_name="t2.fits.mep");
  
  ns.ce_bg << Meq.Condeq(ns.img,Meq.MergeFlags(ns.background,ns.lsm_mask));
  ns.flat_img << ns.img - ns.background;
  ns.solver_bg << Meq.Solver(ns.ce_bg,num_iter=20,epsilon=1e-4,last_update=True,save_funklets=True,solvable=[ns.background]);
  bk1.add(ns.ce_bg);
  bk1.add(ns.flat_img);
  bk1.add(ns.solver_bg);
  
  if lsm_file is None:
    ns.root << Meq.ReqSeq(ns.solver_bg,ns.flat_img,result_index=1);
  else:
    bk2 = Meow.Bookmarks.Page("LSM");
    ns.ce_lsm << Meq.Condeq(ns.flat_img,ns.lsm);
    ns.residual << ns.flat_img - ns.lsm0;   # use unmasked lsm here
    ns.solver_lsm << Meq.Solver(ns.ce_lsm,num_iter=20,epsilon=1e-4,last_update=True,solvable=ns.lsm.search(tags="lsm"));
    bk2.add(ns.flat_img);
    bk2.add(ns.ce_lsm);
    bk2.add(ns.residual);
    bk2.add(ns.solver_lsm);

    ns.root << Meq.ReqSeq(ns.solver_bg,ns.solver_lsm,ns.residual,result_index=2);
  
  

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # figure out our image format
  if init_filename.endswith('.fits'):
    nx,ny = pyfits.open(init_filename)[0].data.shape;
  else:
    nx,ny = PIL.Image.open(init_filename).size;
    nx = int(round(nx*scaling_factor));
    ny = int(round(ny*scaling_factor));
  # run tests on the forest
  cells = make_cells(nx,ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('root',request);
