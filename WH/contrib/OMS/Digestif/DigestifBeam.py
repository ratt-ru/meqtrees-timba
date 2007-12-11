from Timba.TDL import *
from Timba import pynode
from Timba.Meq import meq
from Timba import mequtils
import struct
import math
import pyfits
import cPickle
from Meow import Context

_dbg = utils.verbosity(0,name='digestif');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

ARCMIN = math.pi/(180*60);

class Gridding (object):
  """Encapsulates information about the 4D gridding used to compute pointings and beam grids""";
  def __init__ (self,np,dp,ng,dg):
    self.pointing_nsteps = np;
    self.pointing_dlm = dp;
    self.grid_nsteps = ng;
    self.grid_dlm = dg;

  def compute_cells (self,rows=None):
    grad = (self.grid_nsteps+.5)*self.grid_dlm*ARCMIN;
    gn   = self.grid_nsteps*2+1;
    prad = (self.pointing_nsteps+.5)*self.pointing_dlm*ARCMIN;
    pn   = self.pointing_nsteps*2+1;
    if rows is None:
      domain = meq.gen_domain(time=[-prad,prad],freq=[-prad,prad],l=[-grad,grad],m=[-grad,grad]);
      cells = meq.gen_cells(domain,num_time=pn,num_freq=pn,num_l=gn,num_m=gn);
    else:
      cells = [];
      for i0 in range(-self.pointing_nsteps,self.pointing_nsteps+1,rows):
        i1 = min(self.pointing_nsteps,i0+rows-1);
        t0 = (i0-0.5)*self.pointing_dlm*ARCMIN;
        t1 = (i1+0.5)*self.pointing_dlm*ARCMIN;
        domain = meq.gen_domain(time=[t0,t1],freq=[-prad,prad],l=[-grad,grad],m=[-grad,grad]);
        cells.append(meq.gen_cells(domain,num_time=(i1-i0+1),num_freq=pn,num_l=gn,num_m=gn));
    return cells;


class AxisFlipper (pynode.PyNode):
  """An AxisFlipper node remaps axes. Given an incoming request,
  it creates a new cells with out_axis_[12] copied from in_axis_[12], and
  passes that on to its child. It then modifies the child result
  my mapping out_axis back to in_axis.
  Note that the child request will only have the two out_axis in it. Also,
  no transposition of the result is done, so the in/out axis pairs
  must be in the same order w.r.t. each other in the axis map.
  """;
  def update_state (self,mystate):
    mystate('in_axis_1');
    mystate('in_axis_2');
    mystate('out_axis_1');
    mystate('out_axis_2');
    mequtils.add_axis(self.in_axis_1);
    mequtils.add_axis(self.in_axis_2);
    mequtils.add_axis(self.out_axis_1);
    mequtils.add_axis(self.out_axis_2);

  def modify_child_request (self,request):
    c0 = self.cells = request.cells;
    try:
      domain = meq.gen_domain(**{
        self.out_axis_1:c0.domain[self.in_axis_1],
        self.out_axis_2:c0.domain[self.in_axis_2]});
      self._shape = (len(c0.grid[self.in_axis_1]),len(c0.grid[self.in_axis_2]));
      cells = meq.gen_cells(domain,**{
        'num_'+self.out_axis_1:self._shape[0],
        'num_'+self.out_axis_2:self._shape[1]});
      return meq.request(cells=cells,rqid=request.request_id);
    except:
      print "Error forming up modified request:";
      traceback.print_exc();
      print "Using original request";
      return None;

  def get_result (self,request,*children):
    result = children[0];
    # restore original cells
    result.cells = self.cells;
    # change the shape of the vells to conform to original cells
    ax1 = mequtils.get_axis_number(self.in_axis_1);
    ax2 = mequtils.get_axis_number(self.in_axis_2);
    newshape = [1]*(max(ax1,ax2)+1);
    newshape[ax1] = self._shape[0];
    newshape[ax2] = self._shape[1];
    for vs in result.vellsets:
      vs.shape = newshape;
      vs.value.shape = newshape;
      if hasattr(vs,'perturbed_value'):
        for pval in vs.perturbed_value:
          pval.shape = newshape;
    return result;

class DigestifBeamWriterNode (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);

  def update_state (self,mystate):
    mystate('file_name','digestif.beam');
    mystate('pointing_axis','time');
    mequtils.add_axis(self.pointing_axis);
    mystate('grid_axis','l');
    mequtils.add_axis(self.grid_axis);

  def get_result (self,request,*children):
    # compute
    ff = file(self.file_name,'w');
    result = children[0];
    # compute number of pointings, grid points, and steps
    np = (len(result.cells.grid[self.pointing_axis])-1)/2;
    ng = (len(result.cells.grid[self.grid_axis])-1)/2;
    dp = result.cells.cell_size[self.pointing_axis][0]/ARCMIN;
    dg = result.cells.cell_size[self.grid_axis][0]/ARCMIN;
    # dump stuff to file
    cPickle.dump((np,dp,ng,dg),ff);
    cPickle.dump(result.vellsets[0].value,ff);
    return result;

class DigestifBeamReaderNode (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);

  def update_state (self,mystate):
    mystate('file_name','digestif.beam');

  def get_result (self,request,*children):
    ff = file(self.file_name);
    header = cPickle.load(ff);
    cells = Gridding(*header).compute_cells();
    value = cPickle.load(ff);
    return meq.result(meq.vellset(value),cells=cells);

def read_beam_gridding (filename):
  """Reads header of a Digestif beam file. Returned value is a Gridding."""
  _dprint(0,"reading beam file",filename);
  ff = file(filename);
  header = cPickle.load(ff);
  _dprint(0,"  ",header[0],"pointings, step ",header[1],"'");
  _dprint(0,"  ",header[2],"grid points, step ",header[3],"'");
  return Gridding(*header);

class DigestifBeamReader (object):
  """This class reads a binary file containing a Digestif beam.
  """;
  def __init__ (self,filename):
    ff = file(self.file_name);
    # read header
    header  = cPickle.load(ff);
    self.cells = Gridding(*header).compute_cells();
    self.beamdata = cPickle.load(ff);
    self.npl = self.npm = np;
    self.ngl = self.ngm = ng;

  def get_beam_pattern (self,il,im,center=True):
    """Returns beam pattern for pointing #il,im. If center=True,
    il,im refer to the center pointing""";
    if center:
      il0 = (self.npl-1)/2;
      im0 = (self.npm-1)/2;
    else:
      il0 = im0 = 0;
    return self.beamdata[im0+il,il0+im,:,:];

class DigestifBeamNode (pynode.PyNode):
  """Node to read a Digestif beam file and extract a single pointing""";
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    mequtils.add_axis('l');
    mequtils.add_axis('m');

  def update_state (self,mystate):
    mystate('file_name','digestif.beam');
    mystate('nl',0);
    mystate('nm',0);

  def get_result (self,request,*children):
    beamreader = DigestifBeamReader(self.file_name);
    # get the beam pattern
    beam = beamreader.get_beam_pattern(self.nl,self.nm);
    cells = beamreader.cells;
    # reshape into an l/m vells
    print meq.shape(cells);
    print beam.shape;
    beam = meq.vells(meq.shape(cells),is_complex=True,value=beam);
    return meq.result(meq.vellset(beam),cells=beamreader.cells);

# list of options for Jones module
_options = [
  TDLOption("beam_filename","Filename for beam pattern",
                  TDLFileSelect("*.beam",default="digestif.beam",exist=True)),
  TDLOption("beam_nl","Number of pointing in l",[0],more=int),
  TDLOption("beam_nm","Number of pointing in m",[0],more=int)
];
def compile_options ():
  return _options;

## this is to use this as a Jones module
def compute_jones (Jones,sources,stations=None,pointing_offsets=None,**kw):
  """Computes beam gain for a list of sources.
  The output node, will be qualified with either a source only, or a source/station pair
  """;
  stations = stations or Context.array.stations();
  ns = Jones.Subscope();
  # create node to read beam pattern
  ns.beam << Meq.PyNode(class_name="DigestifBeamNode",module_name=__file__,
                       file_name=beam_filename,nl=beam_nl,nm=beam_nm);
  # are pointing errors configured? then we have different beam Jones
  # per source, per station
  if pointing_offsets:
    # create nodes to compute actual pointing per source, per antenna
    for p in Context.array.stations():
      for src in sources:
        lm = ns.lm(src.direction,p) << src.direction.lm() + pointing_offsets(p);
        Jones(src,p) << Meq.Compounder(lm,ns.beam,dep_mask=255);
  # no pointing errors, single Jones per source
  else:
    for src in sources:
      Jones(src) << Meq.Compounder(src.direction.lm(),ns.beam,dep_mask=255);
      for p in Context.array.stations():
        Jones(src,p) << Meq.Identity(Jones(src));
  return Jones;


## this is for testing purposes
def _define_forest (ns,**kwargs):
  ns.beam << Meq.PyNode(class_name="DigestifBeamNode",module_name=__file__,
                       file_name=beam_filename,nl=beam_nl,nm=beam_nm,
                       cache_policy=100);

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=10);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('beam',request);

## for command-line testing
if __name__ == '__main__':
  beam = DigestifBeamReader('digestif-beam.fits');
  print "number of pointings:",beam.npl,beam.npm;
  print "pointing offsets:",beam.pl,beam.pm;
  print "beam cells:",beam.cells;
  print "beam for central pointing:",beam.get_beam_pattern(0,0).shape;
  print "beam array shape:",beam.beamdata.shape;
