from Timba.TDL import *
import Meow
import math

DEG = math.pi/180.;
ARCMIN = DEG/60;

def imagesize ():
  """Returns current image size, based on grid size and step""";
  return grid_size*grid_step;

def point_source (ns,name,l,m,I=1):
  """shortcut for making a pointsource with a direction""";
  srcdir = Meow.LMDirection(ns,name,l,m);
  return Meow.PointSource(ns,name,srcdir,I=I);

def cross_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a cross""";
  model = [point_source(ns,basename+"+0+0",l0,m0,I)];
  dy = 0;
  for dx in range(-nsrc,nsrc+1):
    if dx:
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  dx = 0;
  for dy in range(-nsrc,nsrc+1):
    if dy:
      name = "%s%+d%+d" % (basename,dx,dy);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

def pentagon_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns 5 sources placed in a pentagon shape"""
  nsrc = 5
  I=15.0
  model = []
  name = "%s0" % (basename);
  model.append(point_source(ns,name,l0,m0+dm,I));
  dl1=dl*math.cos(18.0*DEG);
  dl4=-dl1;
  dm1=dm*math.sin(18.0*DEG);
  dm4=dm1;
  dl2=dl*math.cos(-54.0*DEG);
  dl3=-dl2;
  dm2=dm*math.sin(-54.0*DEG);
  dm3=dm2;
  name = "%s1" % (basename);
  model.append(point_source(ns,name,l0+dl1,m0+dm1,I));
  name = "%s2" % (basename);
  model.append(point_source(ns,name,l0+dl2,m0+dm2,I));
  name = "%s3" % (basename);
  model.append(point_source(ns,name,l0+dl3,m0+dm3,I));
  name = "%s4" % (basename);
  model.append(point_source(ns,name,l0+dl4,m0+dm4,I));
  return model;

def diagonal (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources in a diagonal line"""
  I=100.0
  model = [];
  model.append(point_source(ns,basename+"+0",l0,m0,I));
  for dx in range(-nsrc,nsrc+1):
    if dx:
      name = "%s%+d%+d" % (basename,dx,dx);
      model.append(point_source(ns,name,l0+dl*dx,m0+dm*dx,I));
  return model;

def single_off_center (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns a single source off-center"""
  name = "%s+0" % (basename)
  I=15.0
  nsrc=1;
  dy=0.5;
  model = [];
  model.append(point_source(ns,name,l0+dl*dy,m0+dm*dy,I));
  return model;

def double_off_center (ns,basename,l0,m0,dl,dm,nsrc,I):
  I=15.0
  nsrc=2;
  dy=0.5
  model= [];
  model.append(point_source(ns,basename+"+0",l0+dl*dy,m0+dm*dy,I));
  model.append(point_source(ns,basename+"+1",l0-dl*dy,m0-dm*dy,I));
  return model;
  

def mbar_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a line along the m axis""";
  model = [];
  model.append(point_source(ns,basename+"+0",l0,m0,I));
  for dy in range(-nsrc,nsrc+1):
    if dy:
      name = "%s%+d" % (basename,dy);
      model.append(point_source(ns,name,l0,m0+dm*dy,I));
  return model;

def lbar_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a line along the m axis""";
  model = [];
  model.append(point_source(ns,basename+"+0",l0,m0,I));
  for dx in range(-nsrc,nsrc+1):
    if dx:
      name = "%s%+d" % (basename,dx);
      model.append(point_source(ns,name,l0+dl*dx,m0,I));
  return model;
  
def star8_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in an 8-armed star""";
  model = [ point_source(ns,basename+"+0+0",l0,m0,I) ];
  for n in range(1,nsrc+1):
    for dx in (-n,0,n):
      for dy in (-n,0,n):
        if dx or dy:
          name = "%s%+d%+d" % (basename,dx,dy);
          model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

def grid_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a grid""";
  model = [ point_source(ns,basename+"+0+0",l0,m0,I) ];
  for dx in range(-nsrc,nsrc+1):
    for dy in range(-nsrc,nsrc+1):
      if dx or dy:
        name = "%s%+d%+d" % (basename,dx,dy);
        model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

def make_model (ns,basename="S",l0=0,m0=0,I=1):
  """Creates and returns selected model""";
  return model_func(ns,basename,l0,m0,grid_step*ARCMIN,grid_step*ARCMIN,(grid_size-1)/2,I);


# model options
TDLCompileOption("model_func","Model type",[diagonal,single_off_center,double_off_center,cross_model,grid_model,pentagon_model,lbar_model,mbar_model]);
TDLCompileOption("grid_size","Number of sources in each direction",[1,3,5,7],more=int,default=0);
TDLCompileOption("grid_step","Grid step, in arcmin",[1,5,10,30,60,120,240],more=float,default=4);


