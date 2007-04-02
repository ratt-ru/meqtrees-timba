from Timba.dmi import *
from Timba.Meq import meq
from Timba import pynode
from Timba import utils

import re
import os
import os.path
import time
import motor_control
import pgm

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
    mystate('rescale',1.);
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
    mystate('settle_time',.5);
    # name and nodeindex
    mystate('name','');
    mystate('nodeindex',0);
    
  def _spid (self,act):
    return (self.nodeindex<<8)+int(act);
    
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
