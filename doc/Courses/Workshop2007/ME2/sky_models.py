from Timba.TDL import *
import Meow
import math

DEG = math.pi/180.;
ARCMIN = DEG/60;

def imagesize ():
  """Returns current image size, based on grid size and step""";
  return grid_size*grid_step;

def point_source (ns,name,l,m):
  """shortcut for making a pointsource with a direction""";
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=1);

def cross_model (ns,basename,l0,m0,dl,dm,nsrc):
  """Returns sources arranged in a cross""";
  model = [];
  dy = 0;
  for dx in range(-nsrc,nsrc+1):
    name = "%s%+d%+d" % (basename,dx,dy);
    model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  dx = 0;
  for dy in range(-nsrc,nsrc+1):
    if dy:
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;
  
def star8_model (ns,basename,l0,m0,dl,dm,nsrc):
  """Returns sources arranged in an 8-armed star""";
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for n in range(1,nsrc+1):
    for dx in (-n,0,n):
      for dy in (-n,0,n):
        if dx or dy:
          name = "%s%+d%+d" % (basename,dx,dy);
          model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def grid_model (ns,basename,l0,m0,dl,dm,nsrc):
  """Returns sources arranged in a grid""";
  model = [ point_source(ns,basename+"+0+0",l0,m0) ];
  for dx in range(-nsrc,nsrc+1):
    for dy in range(-nsrc,nsrc+1):
      if dx or dy:
        name = "%s%+d%+d" % (basename,dx,dy);
        model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy));
  return model;

def make_model (ns,basename="S",l0=0,m0=0):
  """Creates and returns selected model""";
  return model_func(ns,basename,l0,m0,grid_step*ARCMIN,grid_step*ARCMIN,(grid_size-1)/2);


# model options
TDLCompileOption("model_func","Model type",[cross_model,grid_model,star8_model]);
TDLCompileOption("grid_size","Number of sources in each direction",[1,3,5,7],more=int);
TDLCompileOption("grid_step","Grid step, in arcmin",[.1,.5,1,2,5,10,15,20,30],more=float);


