from Timba.TDL import *
import Meow
import math

DEG = math.pi/180.;
ARCMIN = DEG/60;

def estimate_image_size (**kw):
  """Returns current image size, based on grid size and step""";
  return grid_size*grid_step;

def point_source (ns,name,l,m,I=1):
  """shortcut for making a pointsource with a direction. Returns None for sources out of the "sky"
  (l^2+m^2>1)""";
  l = math.sin(l);
  m = math.sin(m);
  if l*l + m*m <= 1:
    srcdir = Meow.LMDirection(ns,name,l,m);
    return Meow.PointSource(ns,name,srcdir,I=I);
  else:
    return None;

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

def circ_grid_model (ns,basename,l0,m0,dl,dm,nsrc,I):
  """Returns sources arranged in a circular grid""";
  # start with a cross model
  model = cross_model(ns,basename,l0,m0,dl,dm,nsrc,I);
  # fill in diagonals
  dl /= math.sqrt(2);
  dm /= math.sqrt(2);
  for n in range(1,nsrc+1):
    for dx in (-n,0,n):
      for dy in (-n,0,n):
        if dx and dy:
          name = "%s%+d%+d" % (basename,dx,dy);
          model.append(point_source(ns,name,l0+dl*dx,m0+dm*dy,I));
  return model;

# NB: use lm0=1e-20 to avoid our nasty bug when there's only a single source
# at the phase centre
def source_list (ns,basename="S",l0=0,m0=0):
  """Creates and returns selected model""";
  if grid_size == 1 and not l0 and not m0:
    l0 = m0 = 1e-20;
  sources = model_func(ns,basename,l0,m0,
                       grid_step*ARCMIN,grid_step*ARCMIN,
                       (grid_size-1)/2,source_flux);
  return filter(lambda x:x,sources);

# model options
model_option = TDLCompileOption("model_func","Sky model type",
      [cross_model,grid_model,circ_grid_model,star8_model,lbar_model,mbar_model]);

TDLCompileOption("grid_size","Number of sources in each direction",
      [1,3,5,7],more=int);
TDLCompileOption("grid_step","Grid step, in arcmin",
      [.1,.5,1,2,5,10,15,20,30],more=float);
TDLCompileOption("source_flux","Source flux, Jy",
      [1e-6,1e-3,1],more=float);

