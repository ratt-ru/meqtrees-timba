# standard preamble
from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq
from numarray import *
from Timba.Contrib.MXM.MIM.GPS_MIM import read_gps
Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='test_pynode');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# This class is meant to illustrate the pynode interface. All pynodes
# need to be derived from the Timba.pynode.PyNode class.
class PyNodeSatPos (pynode.PyNode):

  # An __init__ method is not necessary at all. If you do define your 
  # own for some reason, make sure you call pynode.PyNode.__init__() 
  # as done below
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain');

  ## Next, we may need to keep track of the node state record. This includes
  ## initializing from this record when the node is first created. 
  ## There's three ways to do it:
  ## * The low-level way to do it is to define a set_state_impl() method
  ##   (see below).
  ## * An easier, high-level approach is to define an update_state() method.
  ## * Easiest way is to have no state at all. Does your pynode really
  ##   need "state"? If not, you can skip this entirely.
  
  ## update_state() is called when the node is first created and a full
  ## state record is available, but also when state changes, and only a
  ## partial state record is supplied. Instead of the state record, we 
  ## receive a clever object called "mystate" which encapsulates the
  ## state record with some additional semantics:
  def update_state (self,mystate):
    # mystate is a magic "state helper" object is used both to set up
    # initial/default state, and to update state on the fly later.
    
    # This does the following:
    #  - checks the incoming state record for field 'a'
    #  - if present, sets self.a = staterec.a
    #  - if not present but we're initializing the node, sets self.a = 3,
    #    and also sets staterec.a = 3 on the C++ side
    #  - if not present and not initializing, does nothing
    mystate('filename','sat');
    mystate('sat_nr',0);
    
  # Finally, we should define a get_result method. (We don't have to, but if
  # we don't, then what's the point of this node?) 
  # This is called with a list of child results (possibly empty, if we're a 
  # leaf node), and a request object
  def get_result (self,request,*children):
    if len(children):
      raise TypeError,"this is a leaf node, no children expected!";
    # make value of same shape as cells
    cells = request.cells;
    nr_time = meq.shape(cells)[0]; #only time dependend
    times = cells.grid.time;
    pos = read_gps.read_sat_pos(filename=self.filename,time = times,sat_nr=self.sat_nr);
    #flat = value.getflat();   # 'flat' reference to array data
    #for i in range(len(flat)): 
    #  flat[i] = pos[i][0][self.coord_index];
    res = meq.result(0,cells);
    vellsets =[];
    for i in range(3):
      value = meq.vells((nr_time,));
      value[:]=pos[:,0,i];
      vellsets.append(meq.vellset(value));
    res.vellsets=vellsets;
    #res.dims = [3,1];
    #    return meq.result(meq.vellset(value),cells);
    return res;



class PyNodeTec(pynode.PyNode):

  # An __init__ method is not necessary at all. If you do define your 
  # own for some reason, make sure you call pynode.PyNode.__init__() 
  # as done below
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    self.set_symdeps('domain');

  ## Next, we may need to keep track of the node state record. This includes
  ## initializing from this record when the node is first created. 
  ## There's three ways to do it:
  ## * The low-level way to do it is to define a set_state_impl() method
  ##   (see below).
  ## * An easier, high-level approach is to define an update_state() method.
  ## * Easiest way is to have no state at all. Does your pynode really
  ##   need "state"? If not, you can skip this entirely.
  
  ## update_state() is called when the node is first created and a full
  ## state record is available, but also when state changes, and only a
  ## partial state record is supplied. Instead of the state record, we 
  ## receive a clever object called "mystate" which encapsulates the
  ## state record with some additional semantics:
  def update_state (self,mystate):
    # mystate is a magic "state helper" object is used both to set up
    # initial/default state, and to update state on the fly later.
    
    # This does the following:
    #  - checks the incoming state record for field 'a'
    #  - if present, sets self.a = staterec.a
    #  - if not present but we're initializing the node, sets self.a = 3,
    #    and also sets staterec.a = 3 on the C++ side
    #  - if not present and not initializing, does nothing
    mystate('station','bgis');
    mystate('sat_nr',0);
    mystate('track_domain',[0,2880]); # validity domain
    
  # Finally, we should define a get_result method. (We don't have to, but if
  # we don't, then what's the point of this node?) 
  # This is called with a list of child results (possibly empty, if we're a 
  # leaf node), and a request object
  def get_result (self,request,*children):
    if len(children):
      raise TypeError,"this is a leaf node, no children expected!";
    # make value of same shape as cells
    cells = request.cells;
    nr_time = meq.shape(cells)[0]; #only time dependend
    times = cells.grid.time;

    flags = meq.flags((nr_time,));
    value = meq.vells((nr_time,));
    if times[0]/30>self.track_domain[1] or times[len(times)-1]/30 < self.track_domain[0]:
      # flag all and return
      tec = zeros((nr_time,));
      flag = ones((nr_time,));
      flags[:] = flag;
      value[:] = tec;
      vellset = meq.vellset(value);
      vellset.flags = flags;
      return meq.result(vellset,cells);
      
    init_flags = zeros((nr_time,));
    flags[:] = init_flags;
    tec = read_gps.read_tec(filename=self.station,time = times,sat_nr=self.sat_nr,flags = flags);
    #set flags :
    for itm,tm in enumerate(times):
      if tm/30 < self.track_domain[0] or tm/30 > self.track_domain[1]:
        
        flags[itm]=1;
    
        tec[itm]=0;
    #flat = value.getflat();   # 'flat' reference to array data
    #for i in range(len(flat)): 
    #  flat[i] = pos[i][0][self.coord_index];

    value[:]=tec;
    vellset = meq.vellset(value);
    vellset.flags = flags;
    return meq.result(vellset,cells);
