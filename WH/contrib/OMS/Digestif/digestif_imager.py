from Timba.TDL import *
from Timba.Meq import meq
from Timba import pynode
import DigestifACM
import DigestifBeam
import pyfits

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

DEG = math.pi/180;  
ARCMIN = DEG/60;

class WriteSkyImage (pynode.PyNode):
  """PyNode to transpose and write out the result as a sky image.
  """;
  def update_state (self,mystate):
    mystate('file_name','sky.fits');
    mystate('start_channel',0);
    mystate('end_channel',-1);
    
  def get_result (self,request,*children):
    result = children[0];
    # convert to 32 bits
    img = result.vellsets[0].value.astype('Float32');
    # cut off the time axis
    img.shape = img.shape[1:];
    # take channel subset
    if self.end_channel<0:
      img = img[self.start_channel:,:,:];
    else:
      img = img[self.start_channel:(self.end_channel+1),:,:];
    print img.min(),img.max();
    hdu = pyfits.PrimaryHDU(img);
    # add axis info
    hdr = hdu.header;
    hdr.update('CTYPE1','RA---NCP');
    hdr.update('CRPIX1',1);
    hdr.update('CRVAL1',result.cells.grid.l[0]*DEG);
    hdr.update('CDELT1',result.cells.cell_size.l[0]*DEG);
    hdr.update('CUNIT1','deg     ');
    hdr.update('CTYPE2','DEC--NCP');
    hdr.update('CRPIX2',1);
    hdr.update('CRVAL2',result.cells.grid.m[0]*DEG);
    hdr.update('CDELT2',result.cells.cell_size.m[0]*DEG);
    hdr.update('CUNIT2','deg     ');
    hdr.update('CTYPE3','FREQ-OBS');
    hdr.update('CRPIX3',1);
    hdr.update('CRVAL3',result.cells.grid.freq[self.start_channel]);
    hdr.update('CDELT3',result.cells.cell_size.freq[self.start_channel]);
    hdr.update('CUNIT3','HZ      ');
    hdulist = pyfits.HDUList([hdu]);
    hdulist.writeto(self.file_name,clobber=True);
    return result;



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
  ns.weight_tf << Meq.Composer(*[ns.weight_tf(p) for p in ELEMS]);
  ns.weight << Meq.PyNode(ns.weight_tf,
                    class_name="AxisFlipper",
                    module_name='DigestifBeam',
                    in_axis_1='l',in_axis_2='m',
                    out_axis_1='time',out_axis_2='freq');
    
  # acm node
  ns.acm << Meq.PyNode(class_name="DigestifAcmNode",module_name='DigestifACM',
                        file_name='acm.bin');
  # nodes to compute resulting image
  ns.image << Meq.MatrixMultiply(Meq.ConjTranspose(ns.weight),ns.acm,ns.weight);
  try: os.remove(out_filename); 
  except: pass;
  ns.image_real << Meq.Real(ns.image);
  ns.image_fits << Meq.PyNode(ns.image_real,class_name="WriteSkyImage",module_name=__file__,
                        file_name='digestif-sky.fits',
                        start_channel=0,end_channel=-1);
    
  # make some bookmarks
  Meow.Bookmarks.make_node_folder("Beam weights",
        [ns.weight_tf(p) for p in ELEMS],nrow=2,ncol=2);
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

 