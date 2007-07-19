# standard preamble
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

from Timba.TDL import *
from Timba import pynode
from Timba import dmi
from Timba import utils
from Timba.Meq import meq

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
  # This is called with a request object, and a list of child results 
  # (possibly empty, if we're a leaf node)
  def get_result (self,request,*children):
    _dprint(0,"get_result: request is ",dmi.dmi_typename(request),request);
    for i,ch in enumerate(children):
      _dprint(0,"child",i,":",dmi.dmi_typename(ch),ch);
    return None;

import random

# This shows a rather more functional PyNode.
# PyRandom can be configured to return random values using any
# of the functions in the Python random module.

class PyRandom (pynode.PyNode):
  def __init__ (self,*args):
    pynode.PyNode.__init__(self,*args);
    # this tells the caching system what our result depends on
    self.set_symdeps('domain','resolution');
    
  def update_state (self,mystate):
    # setup distribution type and arguments
    got_args = mystate('distribution_args',[0.,1.]);
    if mystate('distribution_type','uniform') or got_args:
      # treat 'distribution_type' as a function name, and look for such
      # a function in the standard random module.
      gen = getattr(random,self.distribution_type,None);
      if not callable(gen):
        raise ValueError,"unknown distribution type '"+self.distribution_type+"'";
      self._generator = gen;
      # now check distribution arguments
      # single argument converts to single-element tuple
      if isinstance(self.distribution_args,(int,float,complex)):
        self.distribution_args = (self.distribution_args,);
      # use the inspect module to look at the selected function,
      # and make sure that the given number of arguments matches the function
      narg = len(inspect.getargspec(self._generator)[0]);
      if inspect.ismethod(self._generator):
        narg -= 1;
      if len(self.distribution_args) != narg:
        raise TypeError,"random.%s: %d arguments expected, distribution_args contains %d"% \
                          (self.distribution_type,narg,len(self.distribution_args));
                          
  def get_result (self,request,*children):
    if len(children):
      raise TypeError,"this is a leaf node, no children expected!";
    # make value of same shape as cells
    cells = request.cells;
    shape = meq.shape(cells);
    print "cells shape is",shape;
    value = meq.vells(shape);
    # fill in random numbers with the given distribution
    flat = value.getflat();   # 'flat' reference to array data
    for i in range(len(flat)):
      flat[i] = self._generator(*self.distribution_args);
    return meq.result(meq.vellset(value),cells);
    
# class PyRFI (pynode.PyNode):
#   def evaluate (self,request,childres):
#     # pick random timeslot for RFI
#     value = childres[0];
#     itime = random.randint(value.shape[0]);
#     value[itime] = 999;
#     return value;
#     

def _define_forest (ns,**kwargs):
  ns.a << Meq.Time;
  ns.b << Meq.Freq;
  ns.c << Meq.Add(ns.a,ns.b,
    ns.ran1 << Meq.PyNode(class_name="PyRandom",module_name=__file__,
                          distribution_type='gauss',distribution_args=(6.,1.)) , \
    ns.ran2 << Meq.PyNode(class_name="PyRandom",module_name=__file__,
                          distribution_type='lognormvariate',distribution_args=(6.,1.)) , \
    ns.ran3 << Meq.PyNode(class_name="PyRandom",module_name=__file__,
                          distribution_type='gammavariate',distribution_args=(6.,1.)));

  # ns.rfi <<  Meq.PyFunctionNode(class_name="PyRFI",module_name=__file__);
  ns.pynode << Meq.PyNode(Meq.Sin(ns.b),class_name="PyDemoNode",module_name=__file__);
  

def _test_forest (mqs,parent,**kwargs):
  from Timba.Meq import meq
  # run tests on the forest
  cells = meq.cells(meq.domain(0,1,0,1),num_freq=20,num_time=10);
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
