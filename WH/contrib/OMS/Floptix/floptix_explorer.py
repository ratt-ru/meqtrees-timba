# standard preamble
from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from Timba import mequtils
from Timba import pynode
import Meow

import re
import os
import os.path
import time
import motor_control
import pgm
import floptix
import pyfits

import numarray
Array = numarray

_dbg = utils.verbosity(0,name='floptix_explorer');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class PyImage_ExploreAroundCenter (floptix.PyCameraImage):
  def update_state (self,mystate):
    floptix.PyCameraImage.update_state(self,mystate);
    mystate("actuator",1);
    mystate("max_extension",10);
    
  def get_result (self,request,*children):
    try:
      # read main image
      time.sleep(self.settle_time);
      cells,value = self._acquire_image("image.00.pgm");
      result = meq.result(meq.vellset(value),cells);
      # perturb actuator in positive direction
      for i in range(self.max_extension):
        motor_control.move(self.actuator,1,1);  
        time.sleep(self.settle_time);
        cells,vells = self._acquire_image("image.+%d.pgm"%(i+1));
        result.vellsets.append(meq.vellset(vells));
      # return to 0
      motor_control.move(self.actuator,0,self.max_extension);
      # perturb actuator in negative direction
      for i in range(self.max_extension):
        motor_control.move(self.actuator,0,1);  
        time.sleep(self.settle_time);
        cells,vells = self._acquire_image("image.-%d.pgm"%(i+1));
        result.vellsets.insert(0,meq.vellset(vells));
      # return to 0
      motor_control.move(self.actuator,1,self.max_extension);
      return result;
    except:
      traceback.print_exc();
      raise;

class PyImage_ExploreImageStability (floptix.PyCameraImage):
  def update_state (self,mystate):
    floptix.PyCameraImage.update_state(self,mystate);
    mystate("num_images",10);
    
  def get_result (self,request,*children):
    try:
      # read main image
      time.sleep(self.settle_time);
      cells,value = self._acquire_image("image.00.pgm");
      result = meq.result(meq.vellset(value),cells);
      # take extra images
      for i in range(self.num_images-1):
        cells,vells = self._acquire_image("image.+%d.pgm"%(i+1));
        result.vellsets.append(meq.vellset(vells));
      return result;
    except:
      traceback.print_exc();
      raise;


class PyExploreMoments (floptix.PyMoments):
  """Computes moments for every vellset in result.
  Returns NxNmom tensor""";
  def get_result (self,request,*children):
    try:
      if len(children) != 1:
        raise TypeError,"only one child expected";
      vss = children[0].vellsets;
      # returns a list; with #0 and #1 being x/y coordinates, and the rest being central moments
      cells = floptix.make_symmetric_cells(self._boxsize,self._boxsize,self.xaxis,self.yaxis);
      cells_shape = meq.shape(cells);
      result = meq.result(cells=cells);
      result.vellsets = [];
      # do some tricks with origin -- we only have a good estimate for the central
      # (unperturbed) image, so save it
      nvs = len(children[0].vellsets);
      nvs0 = int(nvs/2);
      # compute centers and moments for main image, and forward perturbations
      for i in range(nvs0,nvs):
        recenter = ( i == nvs0 );
        moments = self.compute_moments(vss[i].value,recenter=True);
        if recenter:
          origin = self.origin;
        vs1 = [];
        for mom in moments:
          if isinstance(mom,array_class):
            vells = meq.vells(shape=cells_shape,value=mom);
          else:
            vells = meq.vells(shape=[1],value=mom);
          vs1.append(meq.vellset(vells));
        result.vellsets += vs1;
      # reset origin
      self.origin = origin;
      self.set_state('origin',self.origin);
      # compute reverse perturbations
      for i in range(nvs0-1,-1,-1):
        moments = self.compute_moments(vss[i].value,recenter=True);
        vs1 = [];
        for mom in moments:
          if isinstance(mom,array_class):
            vells = meq.vells(shape=cells_shape,value=mom);
          else:
            vells = meq.vells(shape=[1],value=mom);
          vs1.append(meq.vellset(vells));
        result.vellsets[0:0] = vs1;
      nvs0 = len(children[0].vellsets);
      nvs1 = len(result.vellsets);
      result.dims = [nvs0,int(nvs1/nvs0)]; 
      print result.dims;
      return result;
    except:
      traceback.print_exc();
      raise;


class PyFlattenTensor (pynode.PyNode):
  """flattens the first tensor dimension by turning it into the "time" axis""";
  def get_result (self,request,*children):
    try:
      if len(children) != 1:
        raise TypeError,"only one child expected";
      res0 = children[0];
      dims = getattr(res0,'dims',[len(res0.vellsets)]);
      if len(res0.dims) not in (1,2):
        raise TypeError,"a rank-1 or -2 tensor is expected";
      ntimes = res0.dims[0];
      if len(res0.dims) > 1:
        nsecond = res0.dims[1];
      else:
        nsecond = 1;
      # loop over second axis
      vellsets = [];
      for i in range(nsecond):
        # make a shape based on shape of first value, with ntimes along time axis
        value = res0.vellsets[i].value;
        if isinstance(value,array_class):
          shape = list(value.shape);
          shape[0] = ntimes;
          is_array = True;
        else:
          shape = (ntimes,);
          is_array = False;
        outval = meq.vells(shape=shape);
        # now copy over values
        for it in range(ntimes):
          if is_array:
            outval[it] = res0.vellsets[it*nsecond+i].value[0];
          else:
            outval[it] = res0.vellsets[it*nsecond+i].value;
        # put into output list
        vellsets.append(meq.vellset(outval));
      # now form up corresponding cells
      dt = ntimes/2.0;
      dt0 = (ntimes-1)/2;
      cells = res0.cells;
      cells.domain.time = Array.array([-dt,dt]);
      cells.grid.time = Array.array(range(-dt0,dt0+1)) - 0.0;
      cells.cell_size.time = Array.array([1.]*ntimes);
      cells.segments.time = record(start_index=0,end_index=ntimes-1);
      result = meq.result(cells=cells);
      result.vellsets = vellsets;
      return result;
    except:
      traceback.print_exc();
      raise;


TDLCompileOption('static_filename',"Static filename (enables static mode for testing)",[None,'test.pgm'],more=str);
TDLCompileOption('filename_pattern',"Image filename pattern",["live.*pgm","test.pgm"],more=str);
TDLCompileOption('directory_name',"Directory name",["/home/oms/live","."],more=str);
TDLCompileOption('average_frames',"Average N frames together",[1,2,5,10],more=int);
TDLCompileOption('scaling_factor',"Rescale image",[.25,.5,1],more=float);
TDLCompileOption('masking_radius',"Radius of box around sources",[20,40,60],more=int);
TDLCompileOption('psf_radius',"Radius of PSF",[10,15,20,30],more=int);
TDLCompileOption('moments_order',"Max moment order",[2]);
TDLCompileOption('moments_image_threshold',"Image threshold for moment calculation",[0,.1,.25,.5],more=float);
TDLCompileOption('test_actuator',"Actuator to test",motor_control.ALL_MOTORS);
TDLCompileOption('max_extension',"Max actuator extension",[5,10,20],more=int);

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
  # run source finding on current image
  global directory_name;
  print directory_name;
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
  
  # get image shape
  global image_nx;
  global image_ny;
  image_nx,image_ny = pyfits.open("tmp.fits")[0].data.shape;
  _dprint(0,"scaled image size is",image_nx,image_ny);

  # now make the tree
  ns.img('center') << Meq.PyNode(class_name="PyImage_ExploreAroundCenter",module_name=__file__,
                       directory_name=directory_name,
                       file_name=filename_pattern,
                       static_mode=(static_filename is not None),
                       xaxis="x",yaxis="y",
                       settle_time=.1,
                       rescale=scaling_factor,
                       average=average_frames,
                       actuator=test_actuator,
                       max_extension=max_extension,
                       detection_radius=masking_radius
                     );
  ns.img('stability') << Meq.PyNode(class_name="PyImage_ExploreImageStability",module_name=__file__,
                       directory_name=directory_name,
                       file_name=filename_pattern,
                       static_mode=(static_filename is not None),
                       xaxis="x",yaxis="y",
                       settle_time=.1,
                       rescale=scaling_factor,
                       average=average_frames,
                       num_images=max_extension*2+1,
                       detection_radius=masking_radius
                     );
                     
  sources = read_lsm('test.cat');
  if len(sources) > 10:
    raise ValueError,"too many sources found, edit 'default.sex' and try again";
  for tp in 'center','stability':
    for src,x,y in sources:
      mom = ns.moments(tp,src) << Meq.PyNode(class_name="PyExploreMoments",module_name=__file__,
                            origin_0=[x,y],
                            detection_radius=masking_radius,
                            psf_radius=psf_radius,
                            order=moments_order,
                            image_threshold=moments_image_threshold,
                            isq_moment=True,
                            xaxis='x',yaxis='y',
                            cache_policy=100,
                            children=[ns.img(tp)]
                        );
      ns.flat(tp,src) << Meq.PyNode(ns.moments(tp,src),class_name="PyFlattenTensor",module_name=__file__);
    # make node to acquire all moments
    ns.all_moments(tp) << Meq.Composer(dims=[0],cache_policy=100,*[ns.flat(tp,src) for src,x,y in sources]);
    ns.root(tp) << Meq.Composer(ns.all_moments(tp));
  
    bk = Meow.Bookmarks.Page("Moments "+tp);
    bk.add(ns.all_moments(tp));
  
    bk = Meow.Bookmarks.Page("Images "+tp);
    bk.add(ns.img(tp));

def _tdl_job_1_run_actuator_around_center (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'x','y');
  request = meq.request(cells);
  mqs.execute('root:center',request);

def _tdl_job_2_check_image_stability (mqs,parent,**kwargs):
  # run tests on the forest
  cells = floptix.make_cells(image_nx,image_ny,'x','y');
  request = meq.request(cells);
  mqs.execute('root:stability',request);
