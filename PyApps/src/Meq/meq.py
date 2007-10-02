#!/usr/bin/python

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba import dmi
from Timba.dmi import *

from numarray import *
from Timba.Meq import meqds
from Timba import mequtils

domain_ndim = 2;
domain_axes = ( "time","freq" );

_funklet_type = dmi_type('MeqFunklet',record);
_composedpolc_type = dmi_type('MeqComposedPolc',_funklet_type);
_polc_type = dmi_type('MeqPolc',_funklet_type);
_polclog_type = dmi_type('MeqPolcLog',_polc_type);
_domain_type = dmi_type('MeqDomain',record);
_cells_type = dmi_type('MeqCells',record);
_request_type = dmi_type('MeqRequest',record);
_result_type = dmi_type('MeqResult',record);
_vells_type = dmi_type('MeqVells',array_class);
_vellset_type = dmi_type('MeqVellSet',record);

def node (classname,name,children=None,groups=None,**kwargs):
  "creates a node record";
  rec = record({'class':classname},name=name,**kwargs);
  if children:
    if not isinstance(children,(list,tuple)):
      children = (children,);
    self.children = children;
  if groups:
    self.node_groups = make_hiid_list(groups);
  return rec;
  
def array_double (*args,**kw):
  return array(typecode=arr_double,*args,**kw);

def array_complex (*args,**kw):
  return array(typecode=arr_dcomplex,*args,**kw);
  
def polc (coeff,shape=None,offset=None,scale=None,domain=None,
          weight=None,dbid=None,pert=1e-6,subclass=_polc_type):
  """creates a polc record""";
  rec = subclass();
  # process coeff argument -- if a list, then force into a 2D array
  if isinstance(coeff,(tuple,list)):
    if shape and len(shape)>2:
      raise ValueError,'coeff array must be one- or two-dimensional';
    #    if filter(lambda x:isinstance(x,complex),coeff):
    #      coeff = array_complex(coeff,shape=shape);
    #    else:
    coeff = array_double(coeff,shape=shape);
  if is_scalar(coeff):
    #    if not isinstance(coeff,complex):  # force float or complex
    coeff = float(coeff);
    rec.coeff = array(coeff);
  elif is_array(coeff):
    if len(coeff.getshape()) > 2:
      raise TypeError,'coeff array must be one- or two-dimensional';
##    if coeff.type() not in (arr_double,arr_dcomplex):
##      raise TypeError,'coeff array must be float (Float64) or dcomplex (Complex64)';
##    if not coeff.type() == arr_double:
##      raise TypeError,'coeff array must be float (Float64)';
    rec.coeff = array_double(coeff);
  else:
    raise TypeError,'illegal coeff argument';
  # process domain argument
  if domain is not None:
    if isinstance(domain,_domain_type):
      rec.domain = domain;
    else:
      raise TypeError,'domain argument must be a MeqDomain object';
  # other optional arguments
  if offset is not None:
    if isinstance(coeff,(tuple,list)):
      if shape and len(shape)>1:
        raise ValueError,'offset array must be one-dimensional';
      rec.offset  = array_double(offset,shape=shape);
    elif is_array(offset):
      if len(offset.getshape()) > 1:
        raise TypeError,'offset array must be one-dimensional';
      rec.offset = array_double(offset);
  if scale is not None:
    if isinstance(coeff,(tuple,list)):
      if shape and len(shape)>1:
        raise ValueError,'scale array must be one-dimensional';
      rec.scale  = array_double(scale,shape=shape);
    elif is_array(scale):
      if len(scale.getshape()) > 1:
        raise TypeError,'scale array must be one-dimensional';
      rec.scale = array_double(scale);

  if weight is not None:
    rec.weight = float(weight);
  if dbid is not None:
    rec.dbid = int(dbid);
  if pert is not None:
    rec.pert = float(pert);
  
  return rec;


def polclog (coeff,shape=None,offset=None,scale=None,domain=None,
             weight=None,dbid=None,pert=1e-6):
  """creates a polclog record""";
  return polc(coeff,shape,offset,scale,domain,
             weight,dbid,pert,subclass=_polclog_type);


def composedpolc(coeff=0.,shape=None,offset=None,scale=None,domain=None,
                 weight=None,dbid=None,funklet_list=[],pert=1e-6):
  """creates a polclog record""";
  rec = polc(coeff,shape,offset,scale,domain,
             weight,dbid,pert,subclass=_composedpolc_type);
  rec.funklet_list=dmilist(funklet_list);
  return rec;

##def polclog (coeff,shape=None,offset=None,scale=None,domain=None,
##             weight=None,dbid=None,subclass=_polclog_type):
##  """creates a polc record""";
##  rec = subclass();
##  # process coeff argument -- if a list, then force into a 2D array
##  if isinstance(coeff,(tuple,list)):
##    if shape and len(shape)>2:
##      raise ValueError,'coeff array must be one- or two-dimensional';
##    if filter(lambda x:isinstance(x,complex),coeff):
##      coeff = array_complex(coeff,shape=shape);
##    else:
##      coeff = array_double(coeff,shape=shape);
##  if is_scalar(coeff):
##    if not isinstance(coeff,complex):  # force float or complex
##      coeff = float(coeff);
##    rec.coeff = array(coeff);
##  elif is_array(coeff):
##    if len(coeff.getshape()) > 2:
##      raise TypeError,'coeff array must be one- or two-dimensional';
##    if coeff.type() not in (arr_double,arr_dcomplex):
##      raise TypeError,'coeff array must be float (Float64) or dcomplex (Complex64)';
##    rec.coeff = coeff;
##  else:
##    raise TypeError,'illegal coeff argument';
##  # process domain argument
##  if domain is not None:
##    if isinstance(domain,_domain_type):
##      rec.domain = domain;
##    else:
##      raise TypeError,'domain argument must be a MeqDomain object';
##  # other optional arguments
##  if offset is not None:
##    rec.offset = offset;
##  if scale is not None:
##    rec.scale = scale;
##  if weight is not None:
##    rec.weight = weight;
##  if dbid is not None:
##    rec.dbid = dbid;
##  return rec;

def make_polc (p):
  if isinstance(p,_polc_type):
    return p;
  elif is_scalar(p) or is_array(p):
    return polc(p);
  else:
    raise TypeError,'cannot convert %s to a meq.polc'%type(p);

def parm (name,default=None,polcs=None,*args,**kwargs):
  rec = node('MeqParm',name,*args,**kwargs);
  # default must be a polc
  if default is not None:
#    rec.default = make_polc(default);
    rec.init_funklet = make_polc(default);
  # polcs must be a list of polcs, or a single polc
  if polcs is not None:
    if isinstance(polcs,(list,tuple)):
      rec.polcs = map(make_polc,polcs);
    else:
      rec.polcs = ( make_polc(polcs), );
  return rec;

def domain (startfreq,endfreq,starttime,endtime):
  """Creates a time/frequency domain""";
  return _domain_type(freq=map(float,(startfreq,endfreq)),
                time=map(float,(starttime,endtime)));

def gen_domain (**kw):
  """Creates a generalized domain. Axes should be specified as, e.g.,
  freq=(f0,f1),time=(t0,t1),l=(l0,l1), etc.
  """;
  dom = _domain_type();
  for kw,value in kw.iteritems():
    if not isinstance(value,(list,tuple)) or len(value)!=2:
      raise TypeError,kw+": list or tuple of (min,max) expected";
    dom[kw] = map(float,value);
  return dom;

_make_domain = domain;
  
# helper function to resolve a meq.cells grid for one axis
# returns (grid,cellsize,segs) tuple
def _resolve_grid (axisname,dom,num,grid,cellsize):
  # first, figure out grid
  # (a) grid specified explicitly
  if grid is not None and len(grid):
    if grid.rank != 1:
      raise TypeError,'%s_grid must be a vector'%axisname;
    if num is not None and num != len(grid):
      raise ValueError,'both num_%s and %s_grid specified but do not match'%(axisname,axisname);
    num = len(grid);
    # figure out segments
    if num<3:  # <=2 points: always regular
      segs = record(start_index=0,end_index=num-1);
    else:      # >2 grid points: check for regularity
      segs = record(start_index=[0],end_index=[1]);
      cur_step = grid[1]-grid[0];
      for i in range(2,num-1):
        dx = grid[i] - grid[i-1];
        if cur_step is not None and dx != cur_step: # start new segment if new step
          cur_step = None;
          segs.start_index.append(i);
          segs.end_index.append(i);
        else: # else extend current segment
          cur_step = dx;
          segs.end_index[-1] = i;  # update end of current segment
  # (b) num is specified
  elif num is not None:
    if num <= 0:
      raise ValueError,'illegal num_%s value'%axisname;
    if dom is None:
      raise ValueError,'domain must be specified to use num_%s'%axisname;
    step = (dom[1]-dom[0])/num;
    grid = dom[0] + (numarray.arange(num)+0.5)*step;
    # set cell size if not specified
    if cellsize is None or not len(cellsize):
      cellsize = numarray.zeros([num],arr_double) + step;
    segs = record(start_index=0,end_index=num-1);
  else:
    raise ValueError,'either num_%s or %s_grid must be specified'%(axisname,axisname);
  # resolve cell size if not specified
  # use distance to nearest grid point as the cell size
  if cellsize is None or not len(cellsize):
    cellsize = numarray.zeros([num],arr_double);
    x = array([ 2*grid[0]-grid[1]] + grid.getflat() + [2*grid[-1]-grid[-2]]);
    d1 = grid - x[:-2];
    d2 = x[2:] - grid;
    for i in range(num):
      cellsize[i] = min(d1[i],d2[i]);
  elif len(cellsize) == 1:
    cellsize = numarray.zeros([num],arr_double) + cellsize[0];
  elif len(cellsize) != num:
    raise ValueError,'length of %s_cell_size does not conform to grid shape'%axisname;
  return (grid,cellsize,segs);
  
  
# #-- meq.cells() -------------------------------------------------------------
# # Creates a Meq::Cells
# # Two forms of constructor are available:
# #   meq.cells(domain,num_freq,num_time) creates regularly-spaced cells over
# #         the given domain
# #   meq.cells(freq_grid=[...],time_grid=[...]) creates cells with an explicitly
# #         specified grid
# # The forms may be combined, e.g.:
# #   meq.cells(domain,num_freq,time_grid=[...]) creates cells with regular freq
# #         sampling, and an explicitly specified time grid
# # The optional freq_cell_size and time_cell_size arguments may be given to 
# # specify cell sizes (default is full tiling). Use either a scalar for 
# # uniform cell size, or a vector of the same length as the grid.
#
def cells(domain=None,num_freq=None,num_time=None,
          freq_grid=[],time_grid=[],
          freq_cell_size=[],time_cell_size=[]):
  # decompose domain into axis ranges
  if domain is not None:
    if not isinstance(domain,_domain_type):
      raise TypeError,'domain: must be a MeqDomain object';
    df = domain.freq;
    dt = domain.time;
  else:
    df = None;
    dt = None;
  # convert everything to double arrays (possibly empty)
  freq_grid = asarray(freq_grid,arr_double);
  time_grid = asarray(time_grid,arr_double);
  freq_cell_size = asarray(freq_cell_size,arr_double);
  time_cell_size = asarray(time_cell_size,arr_double);
  # resolve grids
  (freq_grid,freq_cell_size,fs) = _resolve_grid(
        'freq',df,num_freq,freq_grid,freq_cell_size);
  (time_grid,time_cell_size,ts) = _resolve_grid(
        'time',dt,num_time,time_grid,time_cell_size);
  # create record
  rec = _cells_type(domain    = _make_domain(df[0],df[1],dt[0],dt[1]),
                 grid      = record(freq=freq_grid,time=time_grid),
                 cell_size = record(freq=freq_cell_size,time=time_cell_size),
                 segments  = record(freq=fs,time=ts));
  return rec;

def gen_cells (domain,**kw):
  """Creates a generalized cells. First create a generalized domain
  with gen_domain(), then pass it here, along with a number of num_axis
  keywords specifying the number of points along each axis (default 1).
  """;
  if not isinstance(domain,_domain_type):
    raise TypeError,'domain: must be a MeqDomain object';
  grid = record();
  cell_size = record();
  segments = record();
  for axis,dom in domain.iteritems():
    nc = kw.get('num_'+str(axis),1);
    grid[axis],cell_size[axis],segments[axis] = \
        _resolve_grid(axis,dom,nc,[],[]);
  return _cells_type(domain=domain,grid=grid,cell_size=cell_size,segments=segments);
  

def shape (arg0=None,*args,**kw):
  """Returns a shape object -- basically just a tuple of dimensions. Can
  be used as follows:
    meq.shape(cells)      shape corresponding to Cells
    meq.shape(vells)      shape of Vells array
    meq.shape(vellset)    shape of VellSet
    meq.shape(nfreq,ntime,...)       [nfreq,ntime,...] shape
    meq.shape(freq=nf,time=nt,...)   [nfreq,ntime,...] shape
  """;
  if isinstance(arg0,_cells_type):
    return shape(**dict([(axis,int(isinstance(grid,float)) or len(grid)) for axis,grid in arg0.grid.iteritems()]));
  elif isinstance(arg0,dmi.array_class):
    return arg0.getshape();
  else:
    # form up shape from arguments
    if isinstance(arg0,(int,long)):
      shp = [arg0] + list(args);
    else:
      shp = list(args);
    # now go over keywords
    for axis,extent in kw.iteritems():
      iaxis = mequtils.get_axis_number(axis);
      if iaxis >= len(shp):
        shp += [1]*(iaxis-len(shp)+1);
      shp[iaxis] = extent;
    return shp;
  
def _vells (shape,typecode,value=None):
  """Creates a Meq::Vells of the given shape.""";
  if value is None:
    arr = array(typecode=typecode,shape=shape);
  else:
    arr = array(value,typecode=typecode,shape=shape);
  return dmi_coerce(arr,_vells_type);
  
def vells (shape,is_complex=False,value=None):
  """Creates a Meq::Vells of the given shape.""";
  if is_complex:
    return _vells(shape,arr_dcomplex,value);
  else:
    return _vells(shape,arr_double,value);
   
def complex_vells (shape,value=None):
  return _vells(shape,arr_dcomplex,value); 

def sca_vells (value):
  if isinstance(value,complex):
    return _vells((1,),arr_dcomplex,value);
  else:
    return _vells((1,),arr_double,value);

def flagvells (shape,value=None):
  return _vells(shape,arr_int32,value); 
  
def vellset (mainval,**kw):
  """Creates a VellSet from the given main value""";
  return _vellset_type(value=mainval,**kw);
  
def result (vellset=None,cells=None):
  """Creates a Result from the given VellSet and Cells""";
  kw = record();
  if vellset is not None:
    kw.vellsets = [ vellset ];
  if cells is not None:
    kw.cells = cells;
  return _result_type(**kw);
  

# # #-- meq.result() -------------------------------------------------------------
# # # Creates a Meq::Result, data should be numarray, matching the cells grid?? 
# def result (cells=None,data=None,rqid=hiid(0)):
#   # decompose domain into axis ranges
#   if cells is not None:
#     if not isinstance(cells,_cells_type):
#       raise TypeError,'cells argument must be a MeqCells object';
#   else:
#     raise ValueError,'cells should be specified';
# 
#   if data is None:
#     raise ValueError,'data should be specified';
# 
#   # create record
#   
#   rec = _result_type(cells = cells,
#                  vellsets      = [record(shape=data.shape,value=data)],
#                  result_code = 0,
#                  request_id = rqid);
# 
#   #result assumes axis_map in domain needed for result_plotter
# 
#   dom  =  cells.domain;
#   forest_state=meqds.get_forest_state();
#   axis_map=forest_state.axis_map;
#   axis_list = [];
# 
#   for i in range(len(axis_map)):
#     if axis_map[i].has_key('id') and axis_map[i]['id']:
#       axis_list.append(str(axis_map[i]['id']).lower());
#   dom['axis_map'] = axis_list;
# 
#   rec.cells.domain = dom;
#   return rec;
# 
#   

_meqdataset_id = 0;

def requestid (domain_id=0,dataset_id=0,rqtype='ev'):
  return hiid(rqtype,0,0,0,domain_id,dataset_id);

def request (cells=None,rqtype=None,dataset_id=None,rqid=None,eval_mode=None):
  # if cells is specified, default rqtype becomes 'ev'
  if rqtype is None:
    if cells is not None:
      rqtype='ev';
    else:
      rqtype='0';
  # use eval_mode to override rqtype, if supplied
  if eval_mode is not None:
    print "*** WARNING: the eval_mode argument to meq.request() is now deprecated.";
    print "*** Please replace it with rqtype='ev', 'e1' or 'e2'";
    print "*** for eval_mode 0, 1 or 2.";
    if eval_mode == 0:    rqtype='ev';
    elif eval_mode == 1:  rqtype='e1';
    elif eval_mode == 2:  rqtype='e2';
  # generate rqid if not supplied
  if rqid is None:
    if dataset_id is None:
      global _meqdataset_id;
      dataset_id = _meqdataset_id;
      _meqdataset_id += 1;
    rqid = requestid(dataset_id=dataset_id,rqtype=rqtype);
  elif len(rqid) >= 6:
    _meqdataset_id = rqid[5];
  else:
    _meqdataset_id = 0;
  print 'rqid',rqid;
  rec = _request_type(request_id=make_hiid(rqid));
  if cells is not None:
    if not isinstance(cells,_cells_type):
      raise TypeError,'cells argument must me a MeqCells object';
    rec.cells = cells;
  return rec;
  
