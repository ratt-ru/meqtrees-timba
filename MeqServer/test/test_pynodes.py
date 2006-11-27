# standard preamble
from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils

import inspect

Settings.forest_state.cache_policy = 100;

_dbg = utils.verbosity(0,name='test_pynode');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# This class is meant to illustrate the pynode interface. All pynodes
# need to be derived from the Timba.pynode.PyNode class.
class PyDemoNode (pynode.PyNode):

  # An __init__ method is not necessary at all. If you do define your 
  # own for some reason, make sure you call pynode.PyNode.__init__() 
  # as done below
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    self.some_field = 1;
    self.another_field = 2;

  ## Next, we need to keep track of the node state record. This includes
  ## initializing from this record when the node is first created.
  ## There's two ways to do it:
  ## * The low-level way to do it is to define a set_state_impl() method
  ##   (see below).
  ## * An easier, high-level approach is to define an update_state() method.
  
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
    mystate('a',3);
    _dprint(0,"a=",self.a);
    
    # You can also use it with only one argument, without providing a 
    # default value. In this case self.field has to be initialized already.
    # The statement below does the following:
    #  - checks the incoming state record for field 'some_field'
    #  - if present, sets self.some_field = staterec.some_field
    #  - if not present but we're initializing the node, checks if 
    #    self.some_field already exists (in this case we set it up in
    #    __init__):
    #     - if yes, sets staterec.some_field = self.some_field on the C++ side
    #     - if not, raises an exception 
    #  - if staterec.some_field is not present and we're not initializing, 
    #    does nothing
    mystate('some_field');
    _dprint(0,"some_field=",self.some_field);
    
    # finally, you can check the return value of mystate() to see if
    # the state field has actually changed. This returns True if:
    #  - self.b was set from incoming state
    #  - self.b was initialized with a default value
    if mystate('b',4):
      _dprint(0,"b initialized or changed:",self.b);
     
    # and in this form, it only returns True if self.another_field
    # was set from incoming state:
    if mystate('another_field'):
      _dprint(0,"another_field changed:",self.another_field);

  ## set_state_impl() is an alternative, nuts'n'bolts style interface.
  ## If defined, this method will be called when the node is initialized
  ## (with a complete state record and initializing=True), or any time
  ## the node's state is changed (with a partial state record and 
  ## initializing=False). The method should be defined like this:
  #     def set_state_impl (self,staterec,initializing):
  ## and its return value should be either false, or else a record
  ## of stuff to be copied back into the node state record. 
  ## This whole initializing-or-not rigamarole is hard to keep track of,
  ## so I really recommend using update_state() instead.


  # Finally, we should define a get_result method. (We don't have to, but if
  # we don't, then what's the point of this node?) 
  # This is called with a list of child results (possibly empty, if we're a 
  # leaf node), and a request object
  def get_result (self,children,request):
    _dprint(0,"get_result: request is ",dmi.dmi_typename(request),request);
    for i,ch in enumerate(children):
      _dprint(0,"child",i,":",dmi.dmi_typename(ch),ch);
    return None;


class PyRandom (pynode.PyNode):
  import random

  def update_state (self,mystate):
    # setup distribution type and arguments
    if mystate('distribution_type','uniform') or mystate('distribution_args',[0.,1.]):
      gen = getattr(random,self.distribution_type,None);
      if not callable(gen):
        raise ValueError,"unknown distribution type '"+self.distribution_type+"'";
      self._generator = gen;
      # single argument converts to single-element tuple
      if isinstance(self.distribution_args,(int,float,complex)):
        self.distribution_args = (self.distribution_args,);
      # check number of arguments to the specified Python method
      narg = len(inspect.getargspec(self._generator)[0]);
      if inspect.ismethod(self._generator):
        narg -= 1;
      if len(self.distribution_args) != narg:
        raise TypeError,"random.%s: %d arguments expected, distribution_args contains %d"% \
                          (self.distribution_type,narg,len(self.distribution_args));
                          
  def get_result (self,children,request):
    _dprint(0,"get_result: request is ",request);
    _dprint(0,"get_result: children are ",children);
    return None;
  


def _define_forest (ns,**kwargs):
  ns.a << Meq.Time;
  ns.b << Meq.Freq;
  ns.c << ns.a+ns.b;
  ns.pynode << Meq.PyNode(ns.c,Meq.Sin(ns.b),class_name="PyDemoNode",module_name=__file__);
  

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=6,num_time=4);
  request = meq.request(cells,rqtype='ev');
  mqs.execute('pynode',request);

# this is the testing branch, executed when the script is run directly
# via 'python script.py'

if __name__ == '__main__':
#  from Timba.Meq import meqds 
  Timba.TDL._dbg.set_verbose(5);
  ns = NodeScope();
  _define_forest(ns);
  # resolves nodes
  ns.Resolve();
