from Timba.dmi import *
from Timba.Meq import meq
from Timba import pynode
from Timba import utils
from Timba import mequtils

import re
import os
import os.path
import time
import motor_control
import pgm
import math

import numarray
Array = numarray

image_xaxis = "time";
image_yaxis = "freq";

_dbg = utils.verbosity(0,name='floptix');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

def acquire_imagename (file_rex,directory='.',timeout=5,sleep_time=1/7.5):
  """Returns filename for the latest image from the camera.
  Deletes previous images.
  'directory':  which directory to look in
  'file_rex":   str or regex specifying the filename pattern
  'timeout':    how long to wait before giving up (secs)
  'sleep':      how long to wait before looking for an image
  """;
  filelist = os.listdir(directory);
  if isinstance(file_rex,str):
    file_rex = re.compile(file_rex);
  # remove all files matching filename template
  nfiles = len(filelist);
  for f in filelist:
    if file_rex.match(f):
      os.unlink(os.path.join(directory,f));
      nfiles -= 1;
  _dprint(0,"deleted",len(filelist)-nfiles,"of",len(filelist),"files");
  # now wait for a new file to show up
  timeout = time.time() + timeout;
  while True:
    if time.time() > timeout:
      raise RuntimeError,"timeout acquiring image";
    # rescan directory, continue if no new files
    filelist = os.listdir(directory);
    if len(filelist) == nfiles:
      time.sleep(sleep_time);
      continue;
    # now look for another image file
    for f in filelist:
      if file_rex.match(f):
        # acquire this image
        _dprint(0,"acquired image",f);
	# wait for another to show up, to make sure this one is complete
	while len(os.listdir(directory)) == len(filelist):
	  if time.time() > timeout:
	    raise RuntimeError,"timeout acquiring image";
	  time.sleep(sleep_time);
	return os.path.join(directory,f)
    # no image found, try again
  # we should never get here
  pass;


def make_cells (nx,ny,xaxis,yaxis):
  """helper function to make an nx by ny cells with the given axes.
  """;
  # make value of same shape as cells
  dom = meq.gen_domain(**{xaxis:[0,nx] , yaxis:[0,ny]});
  return meq.gen_cells(dom,**{'num_'+xaxis : nx , 'num_'+yaxis : ny});

def make_symmetric_cells (nx,ny,xaxis,yaxis):
  """helper function to make an nx by ny cells with the given axes.
  """;
  # make value of same shape as cells
  dom = meq.gen_domain(**{xaxis:[-nx/2.,nx/2.] , yaxis:[-ny/2.,ny/2.]});
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


class PyPgmImage (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    mystate('file_name','test.pgm');
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
    mystate('rescale',1.);
                          
  def get_result (self,request,*children):
    # read PGM image
    img = pgm.Image(file(self.file_name).read()).pixels;
    img.byteswap();
    # make cells and value, construct array
    nx,ny = img.shape;
    cells = make_cells(nx,ny,self.xaxis,self.yaxis);
    value = meq.vells(shape=meq.shape(cells),value=img.flat);
    return meq.result(meq.vellset(value),cells);

    
class PyCameraImage (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution','iteration');
    motor_control.init();
    
  def update_state (self,mystate):
    # static mode, for debugging: reaquires the same image over and over
    mystate('static_mode',False);
    # filename pattern
    mystate('file_name','test.pgm*');
    self._file_re = re.compile(self.file_name);
    # directory to look in
    mystate('directory_name','.');
    # time to sleep before looking for another image, in seconds
    mystate('sleep_time',.1);
    # give up if no new images show up within this time period
    mystate('timeout',10);
    # image parameters
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
    mequtils.add_axis(self.xaxis);
    mequtils.add_axis(self.yaxis);
    mystate('rescale',1.);
    # average N frames together
    mystate('average',1);
    # actuators
    self._positions = {};
    mystate('actuators',motor_control.ALL_MOTORS);
    for act in self.actuators:
      self._positions[act] = 0;
    mystate('solvable',False);
    if self.solvable:
      self.set_symdeps('domain','resolution','iteration');
    else:
      self.set_symdeps('domain','resolution');
    # perturbation step
    mystate('perturbation',1);
    # perturbation rescaling
    mystate('pert_scale',1e-6);
    # max perturbation
    mystate('max_pert',3);
    # delay to let the system settle before taking a measurement, in secs
    mystate('settle_time',.1);
    # name and nodeindex
    mystate('name','');
    mystate('nodeindex',0);
    
  def _spid (self,act):
    return (self.nodeindex<<8)+int(act);
    
  def _acquire_image (self,log_filename=None):
    """acquires latest image from camera. Returns a tuple of cells and vells""";
    for nframe in range(self.average):
      if self.static_mode:
        filename = self.file_name;
      else:
        filename = acquire_imagename(self._file_re,directory=self.directory_name,
                        timeout=self.timeout,sleep_time=self.sleep_time);
        if log_filename:
          os.rename(filename,log_filename);
          filename = log_filename;
      # read image
      img = pgm.Image(file(filename).read()).pixels;
      img.byteswap();
      if self.average > 1:
        if nframe:
          sumimage = sumimage + img;
        else:
          sumimage = img.astype(Array.Int32);
    # if averaging is in effect, use average image
    if self.average > 1:
      sumimage = sumimage/self.average;
#    img.transpose();
    nx,ny = img.shape;
    if self.rescale != 1:
      nx = int(round(nx*self.rescale));
      ny = int(round(ny*self.rescale));
      img = img.resize((nx,ny)); # ,PIL.Image.ANTIALIAS);
    # note that getdata() returns elements in the wrong sequence, so we
    # have to swap the x and y axes around
    cells = make_cells(ny,nx,self.xaxis,self.yaxis);
    vells = meq.vells(shape=meq.shape(cells),value=img.flat);
    return cells,vells;

  def discover_spids (self,request,*children):
    # start with empty result
    res = meq.result(); 
    # add spid map if solvable
    if self.solvable:
      spidmap = record();
      for act in self.actuators:
        spidmap[hiid(self._spid(act))] = record(name=self.name+":"+str(act),nodeindex=self.nodeindex);
      res.spid_map = spidmap;
    return res;
      
  def process_command (self,command,args,rqid,verbosity):
    _dprint(0,"received command",command,args);
    if command == "Update_Parm":
      updates = [ round(u/self.pert_scale) for u in args.incr_update ];
      _dprint(0,"incremental updates are",updates);
      updates = [ max(min(u,self.max_pert),-self.max_pert) for u in updates ];
      _dprint(0,"applying values",updates);
      for ia,act in enumerate(self.actuators):
        upd = updates[ia];
        self._positions[act] += upd;
        if upd > 0:
          motor_control.move(act,1,upd);    
        elif upd < 0:
          motor_control.move(act,0,-upd);   
      _dprint(0,"new motor positions:",self._positions);
    return 0;
                       
  def get_result (self,request,*children):
    try:
      # read main image
      time.sleep(self.settle_time);
      cells,value = self._acquire_image();
      vellset = meq.vellset(value);
      # if solvable, perturb each actuator
      if self.solvable:
        vellset.spid_index = spid_index = [];
        vellset.perturbations = perturbations = [];
        vellset.perturbed_value = perturbed_value = [];
        for act in self.actuators:
          motor_control.move(act,1,self.perturbation);  # move motor forward
          time.sleep(self.settle_time);
          cells,vells = self._acquire_image();
          motor_control.move(act,0,self.perturbation);  # move motor back
          spid_index.append(self._spid(act));
          perturbations.append(float(self.perturbation*self.pert_scale));
          perturbed_value.append(vells);
      return meq.result(vellset,cells);
    except:
      traceback.print_exc();
      raise;
      

class PyCroppedCameraImages (PyCameraImage):
  """This node acquires camera images, but cuts out boxes around the sources. The source
  coordinates are expected to be given by a set of 2-vector child results."""
  def update_state (self,mystate):
    # size of boxes to be cropped
    mystate('radius',10);
    return PyCameraImage.update_state(self,mystate);
    
  def _acquire_image (self):
    """acquires latest image from camera. Returns a tuple of cells and vells""";
    if self.static_mode:
      filename = self.file_name;
    else:
      filename = acquire_imagename(self._file_re,directory=self.directory_name,
                      timeout=self.timeout,sleep_time=self.sleep_time);
    # read image
    img = pgm.Image(file(filename).read()).pixels;
    img.byteswap();
    nx,ny = img.shape;
    if self.rescale != 1:
      nx = int(round(nx*self.rescale));
      ny = int(round(ny*self.rescale));
      img = img.resize((nx,ny)); 
    boxsize = self.radius*2+1;
    cells = make_symmetric_cells(boxsize,boxsize,self.xaxis,self.yaxis);
    shape = meq.shape(cells);
    vells_list = [];
    # now cut out boxes and paste them into the vells
    # note that the x axis (0) is time and y (1) is frequency, we want to stack
    # source images along the first axis
    px0 = 0;  # current x offset at which cropped image will be pasted in
    for sx,sy in self._sources:
      vells = meq.vells(shape=shape);
      flags = None;
      xc = round(sx);
      yc = round(sy);
      x0 = xc - self.radius;
      x1 = xc + self.radius + 1;
      y0 = yc - self.radius;
      y1 = yc + self.radius + 1;
      # cropped image [x0:x1,y0:y1] will be pasted at [px0:px1,py0:py1] in output vells
      px0 = 0;
      px1 = boxsize;
      py0 = 0;
      py1 = boxsize;
      # handle boxes that overlap image edges
      if x0 < 0:
        px1 = -x0;      # adjust start of pasting region
        flags = flags or meq.flagvells(shape=shape);
        flags[0:px0,:] = 1 # set flags to mask values "beyond" the edge
        x0 = 0;
      if y0 < 0:
        py0 = -y0;         # adjust start of pasting region
        flags = flags or meq.flagvells(shape=shape);
        flags[:,0:py0] = 1 # set flags to mask values "beyond" the edge
        y0 = 0;
      if x1 > nx:
        px1 -= (x1-nx);
        flags = flags or meq.flagvells(shape=shape);
        flags[px1:boxsize,:] = 1;
        x1 = nx;
      if y1 > ny:
        py1 -= (y1-ny);
        flags = flags or meq.flagvells(shape=shape);
        flags[:,py1:boxsize] = 1;
        y1 = ny;
      # now paste in image
      vells[px0:px1,py0:py1] = img[x0:x1,y0:y1];
      vells_list.append((vells,flags));
    return cells,vells_list;

  def get_result (self,request,*children):
    try:
      # get x/y values from children
      self._sources = [];
      for res in children:
        self._sources.append((float(res.vellsets[0].value),float(res.vellsets[1].value)));
      # read main image
      time.sleep(self.settle_time);
      cells,vells_list = self._acquire_image();
      # put each cropped image into a vellset
      result = meq.result(cells=cells);
      result.vellsets = [];
      for vells,flags in vells_list:
        vellset = meq.vellset(vells);
        if flags is not None:
          vellset.flags = flags;
        result.vellsets.append(vellset);
      # if solvable, perturb each actuator and acquire perturbed image
      if self.solvable:
        # setup list of spids in each vellset
        spid_index = [];
        perturbations = [];
        for vellset in result.vellsets:
          vellset.spid_index = spid_index;
          vellset.perturbations = perturbations;
          vellset.perturbed_value = [];
        # now loop over actuators
        for act in self.actuators:
          motor_control.move(act,1,self.perturbation);  # move motor forward
          time.sleep(self.settle_time);
          cells,vells_list = self._acquire_image();
          motor_control.move(act,0,self.perturbation);  # move motor back
          spid_index.append(self._spid(act));
          perturbations.append(float(self.perturbation*self.pert_scale));
          for (vells,flags),vellset in zip(vells_list,result.vellsets):
            vellset.perturbed_value.append(vells);
      return result;
    except:
      traceback.print_exc();
      raise;
      

class PyMoments (pynode.PyNode):
  def update_state (self,mystate):
    mystate("origin_0",(0,0));
    self.origin = self.origin_0;
    mystate("detection_radius",20);
    self._boxsize = self.detection_radius*2+1;
    mystate("psf_radius",10);
    mystate("order",2);
    mystate("isq_moment",True);
    print "isq_moment:",self.isq_moment;
    mystate("image_threshold",.25);
    mystate('xaxis',image_xaxis);
    mystate('yaxis',image_yaxis);
    mequtils.add_axis(self.xaxis);
    mequtils.add_axis(self.yaxis);
    self._log = [];
    
  def compute_moments (self,img0,recenter=False):
    # reshape image to two significant axes
    nx,ny = [ n for n in img0.shape if n != 1 ][0:2];
    img0 = Array.reshape(img0,(nx,ny));
    # if recenter mode is on (which it is for the first vells), then we
    # do two passes: find the center of gravity first, then recenter 
    if recenter:
      npass = 2;
    else:
      npass = 1;
    for ipass in range(0,npass):
      logrec = record(npass=ipass,origin=self.origin);
      self._log.append(logrec);
      # extract box around origin
      xc,yc = self.origin;
      xc,yc = int(round(xc)),int(round(yc));
      x0 = max(xc-self.detection_radius,0);
      x1 = min(xc+self.detection_radius+1,img0.shape[0]);
      y0 = max(yc-self.detection_radius,0);
      y1 = min(yc+self.detection_radius+1,img0.shape[1]);
      # check for degeneracy
      if x0>=x1 or y0>=y1:
        print "box coords",x0,x1,y0,y1;
        raise ValueError,"Illegal source coordinates: %d,%d"%(xc,yc);
      img = img0[x0:x1,y0:y1];
      nx,ny = img.shape;
      nel = nx*ny;
      if not ipass:
        img_sum0 = img.sum();
      # threshold the image 
      print "image min/max",img.min(),img.max();
      # if recentering during a first pass, use a bigger threshold
      if not ipass and npass > 1:
        thr = (img.min()+img.max())/2.;
      else:
        thr = img.min()*(1-self.image_threshold) + img.max()*self.image_threshold;
#      thr = img.min();
      img = Array.clip(img,thr,img.max()) - thr;
      # renormalize image
      img_sum = float(img.sum());
      img = img/img_sum;
      logrec.img = img.copy();
      # if recentering, recompute coordinate arrays
      if recenter:
        self._xi = Array.fromfunction(lambda i,j:i,(nx,ny));
        self._yi = Array.fromfunction(lambda i,j:j,(nx,ny));
        self._xisum = self._xi.sum();
        self._yisum = self._yi.sum();
        self.set_state('$xi',self._xi);
        self.set_state('$yi',self._yi);
      # get center of gravity
      gx = (img*self._xi).sum();
      gy = (img*self._yi).sum();
      # recenter if necessary
      if recenter:
        self.origin = x0+gx,y0+gy;
        self.set_state('origin',self.origin);
        logrec.new_origin = self.origin;
    # recompute coordinates w.r.t. center
    x = self._xi - gx;
    y = self._yi - gy;
    logrec = record();
    self._log.append(logrec);
    # mask points outside of PSF radius
    img = Array.where(x*x+y*y <= (self.psf_radius**2),img,0);
    # set initial moments array
    moments = [img] + list(self.origin);
    # compute central moments
    # 2nd order moment
    img1 = img*(x*x+y*y);
    logrec.mom_2 = img1;
    mom2 = img1.sum();
    moments.append(img1.sum());
    sigma = math.sqrt(mom2);
    # normalized 3rd order moment (skewness)
    img1 = img*(x**3+y**3);
    logrec.mom_3 = img1;
    moments.append(img1.sum()/(sigma**3));
    # normalized 4th order moment 
    img1 = img*(x**4+y**4);
    logrec.mom_4 = img1;
    moments.append(img1.sum()/(sigma**4));
    # 2nd-order difference moments
    img1 = img*(x**2-y**2);
    logrec.mom_dxy = img1;
    moments.append(img1.sum()/(sigma**2));
    # rotate by 45 degrees
    cos45 = math.sqrt(2.);
    x1 = x*cos45-y*cos45;
    y1 = x*cos45+y*cos45;
    img1 = img*(x1**2-y1**2);
    logrec.mom_dxy1 = img1;
    moments.append(img1.sum()/(sigma**2));
    # add sum(I)
    moments.append(img_sum0);
    # add sum(I^2) 
    if self.isq_moment:
      img1 = img*img;
      moments.append(nel/img1.sum());
      logrec.sq_img = img1;
    self.set_state('$op_log',self._log);
    print moments[1:];
    return moments;
    
  def get_result (self,request,*children):
    try:
      if len(children) != 1:
        raise TypeError,"only one child expected";
      vs0 = children[0].vellsets[0];
      spid_index = vs0.get('spid_index',None);
      perturbations = vs0.get('perturbations',None);
      perturbed_value = vs0.get('perturbed_value',[]);
      # compute centers and moments for main image
      moments = self.compute_moments(vs0.value,recenter=True);
      # returns a list; with #0 and #1 being x/y coordinates, and the rest being central moments
      cells = make_symmetric_cells(self._boxsize,self._boxsize,self.xaxis,self.yaxis);
      cells_shape = meq.shape(cells);
      result = meq.result(cells=cells);
      result.vellsets = [];
      for mom in moments:
        if isinstance(mom,array_class):
          vells = meq.vells(shape=cells_shape,value=mom);
        else:
          vells = meq.vells(shape=[1],value=mom);
        vs = meq.vellset(vells);
        if spid_index: 
          vs.spid_index = spid_index;
        if perturbations:
          vs.perturbations = perturbations;
          vs.perturbed_value = [];
        result.vellsets.append(vs);
      # now fill in moments for each perturbed value...
      for pval in perturbed_value:
        moments = self.compute_moments(pval);
        for i,mom in enumerate(moments):
          if isinstance(mom,array_class):
            vells = meq.vells(shape=cells_shape,value=mom);
          else:
            vells = meq.vells(shape=[1],value=mom);
          result.vellsets[i].perturbed_value.append(vells);
      return result;
    except:
      traceback.print_exc();
      raise;
      
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
    for chres in children:
      x,y = float(chres.vellsets[0].value),float(chres.vellsets[1].value);
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
