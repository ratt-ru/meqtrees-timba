# standard preamble
from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq

import pyfits
import re
import Meow

Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='fit_image');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

init_filename = 't2.fits';

TDLCompileOption('background_order',"Polc order for background fit",[1,2,3,4],more=int);
TDLCompileOption('lsm_file',"Source catalog file",[None,'test.cat']);

def make_cells (nx,ny,xaxis,yaxis):
  """helper function to make an nx by ny cells with the given axes.
  """;
  # make value of same shape as cells
  kw = {};
  kw[xaxis] = [0,nx];
  kw[yaxis] = [0,ny];
  dom = meq.gen_domain(**kw);
  kw = {};
  kw['num_'+xaxis] = nx;
  kw['num_'+yaxis] = ny;
  return meq.gen_cells(dom,**kw);
  

class PyFitsImage (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    mystate('file_name','test.fits');
    mystate('xaxis','time');
    mystate('yaxis','freq');
                          
  def get_result (self,children,request):
    # read fits image
    img = pyfits.open(self.file_name)[0].data;
    nx,ny = img.shape;
    _dprint(1,"read FITS image of size ",nx,ny);
    # make cells and value
    cells = make_cells(nx,ny,self.xaxis,self.yaxis);
    value = meq.vells(shape=meq.shape(cells),value=img);
    return meq.result(meq.vellset(value),cells);

def make_lsm (ns,filename):    
  """Creates an LSM tree from a catalog file""";
  sources = [];
  for line in open(filename).readlines():
    if not line.startswith('#'):
      fields = re.split('[\d.-]',line);
      src = fields[1];
      sources.append(src);
      x,y = float(fields[5]),float(fields[6]);
      ns.flux(src) << Meq.Parm(0,tags="lsm flux");
      ns.xy(src) << Meq.Composer(
        ns.x(src) << Meq.Parm(x,tags="lsm pos"),
        ns.y(src) << Meq.Parm(y,tags="lsm pos"));
      
  # compose all source coordinates into a tensor
  ns.lsm_pack << Meq.Composer(dims=[],*sources);
  
  # make a Python LSM node to
  


def _define_forest (ns,**kwargs):
  ns.img << Meq.PyNode(class_name="PyFitsImage",module_name=__file__,
                       file_name="t2.fits");
                       
  ns.background << Meq.Parm(0.,shape=[background_order,background_order]);
  
  ns.residual << ns.img - ns.background; 
  ns.ce << Meq.Condeq(ns.img,ns.background);
  ns.solver << Meq.Solver(ns.ce,num_iter=20,epsilon=1e-4,last_update=True,solvable=[ns.background]);
  ns.reqseq << Meq.ReqSeq(ns.solver,ns.residual,result_index=1);
                       
  Meow.Bookmarks.Page("Image").add(ns.img).add(ns.solver).add(ns.residual);
  

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # figure out our image format
  nx,ny = pyfits.open(init_filename)[0].data.shape;
  # run tests on the forest
  cells = make_cells(nx,ny,'time','freq');
  request = meq.request(cells,rqtype='ev');
  mqs.execute('reqseq',request);
