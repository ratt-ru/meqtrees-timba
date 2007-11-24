from Timba.TDL import *
from Timba.Meq import meq
from Timba import pynode
import DigestifACM

import Meow
import math
import os
from Timba import mequtils

Settings.forest_state.cache_policy = 1;

TDLCompileOption("pointing_nsteps","Number of pointing steps along one radius",[15],more=int);
TDLCompileOption("pointing_dlm","Size of one pointing step, in arcmin",[2],more=float);
TDLCompileOption("table_name","Weights table",TDLDirSelect("*.mep",default="weights.mep"));
TDLCompileOption("acm_filename","Input ACM file",TDLFileSelect("*.bin"));

      
TDLCompileOption("out_filename","Output filename for sky image",
                  TDLFileSelect("*.fits",default="digestif-image.fits"));

  
ARCMIN = math.pi/(180*60);

class DigestifAxisKludger (pynode.PyNode):
  def modify_child_request (self,request):
    # Creates a new request which will be used to poll children.
    # Because Polc currently does not tile in l/m, we use time/freq for
    # the weight axes. So, what we need to do now is take the l/m grid
    # from the incoming request, and convert it to a time/freq grid
    # in the outgoing request
    c0 = self.cells = request.cells;
    try:
      domain = meq.gen_domain(time=c0.domain.l,freq=c0.domain.m);
      cells = meq.gen_cells(domain,num_time=len(c0.grid.l),
                                 num_freq=len(c0.grid.m));
      return meq.request(cells=cells);
    except:
      print "Error forming up modified request:";
      traceback.print_exc();
      print "Using original request";
      return None;
  
  def get_result (self,request,*children):
    res = children[0];
    # child result is time,freq
    # we need to reshape that to the incoming cells shape
    shape = meq.shape(self.cells); 
    val = meq.vells(shape,is_complex=True,value=res.vellsets[0].value);
    return meq.result(meq.vellset(val),cells=self.cells);

def _define_forest (ns,**kwargs):
  # read ACM file to establish number of elements
  acm = DigestifACM.DigestifACM(acm_filename);
  nel = acm.nel;
  acm = None;
  ELEMS = range(nel);
  mequtils.add_axis('l');
  mequtils.add_axis('m');
  # create nodes to represent the beam weights
  for p in ELEMS:
    # and a weight parameter
    wr = ns.weight(p,'r') << Meq.Parm(1,tags="beam weight solvable",
                                        tiling=record(time=1,freq=1),
                                        table_name=table_name,save_all=True,use_mep=True);
    wi = ns.weight(p,'i') << Meq.Parm(0,tags="beam weight solvable",
                                        tiling=record(time=1,freq=1),
                                        table_name=table_name,save_all=True,use_mep=True);
    ns.weight_tf(p) << Meq.ToComplex(wr,wi);
    ns.weight(p) << Meq.PyNode(ns.weight_tf(p),
                    class_name="DigestifAxisKludger",module_name=__file__);
  ns.weight << Meq.Composer(*[ns.weight(p) for p in ELEMS]);
    
  # acm node
  ns.acm << Meq.PyNode(class_name="DigestifAcmNode",module_name='DigestifACM',
                        file_name='acm.bin');
  # nodes to compute resulting image
  ns.image << Meq.MatrixMultiply(Meq.ConjTranspose(ns.weight),ns.acm,ns.weight);
  try: os.remove(out_filename); 
  except: pass;
  ns.image_real << Meq.Real(ns.image);
  ns.image_fits << Meq.FITSWriter(ns.image_real,filename=out_filename);
    
  # make some bookmarks
  Meow.Bookmarks.make_node_folder("Beam weights",
        [ns.weight(p) for p in ELEMS],nrow=2,ncol=2);
  Meow.Bookmarks.Page("ACM").add(ns.acm);
  Meow.Bookmarks.Page("Complex image").add(ns.image);
  Meow.Bookmarks.Page("Image").add(ns.image_real);

def compute_cells ():
  prad = (pointing_nsteps+.5)*pointing_dlm*ARCMIN;
  pn   = pointing_nsteps*2+1;
  domain = meq.gen_domain(l=[-prad,prad],m=[-prad,prad]);
  cells = meq.gen_cells(domain,num_l=pn,num_m=pn);
  return cells;
  

def _tdl_job_1_compute_image (mqs,parent,**kwargs):
  from Timba.Meq import meq
  cells = compute_cells();
  request = meq.request(cells,rqtype='ev');
  mqs.execute('image_fits',request);

 