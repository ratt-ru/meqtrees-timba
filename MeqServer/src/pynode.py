#!/usr/bin/python
# PyNode: base class for nodes implemented in Python

from Timba import dmi
from Timba import utils

_dbg = utils.verbosity(0,name='pynode');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class PyNode (object):
  """Base class for implementing PyNodes. This class runs on the
  kernel side. Provides interface to the C++ node object, plus various
  helpful methods.
  """;
  def __init__ (self,name,node_baton):
    import meqserver_interface
    _dprintf(2,"created PyNode '%s'");
    self.name = name;
    self._baton = node_baton;
    if hasattr(self,'update_state'):
      self.set_state_impl = self._state_handler; 
    
  class StateHelper (object):
    def __init__ (self,pynode,staterec,initializing):
      self.pynode,self.staterec,self.initializing = pynode,staterec,initializing;
      self.newstate = dmi.record();
    
    def __call__ (self,field,default_value=None):
      if field in self.staterec:
        setattr(pynode,field,self.staterec[field]);
        return True;
      elif self.initializing:
        if default_value is not None:
          self.newstate[field] = default_value;
          setattr(self.pynode,field,default_value);
          return True;
        elif hasattr(self.pynode,field):
          self.newstate[field] = getattr(self.pynode,field);
          return False;
        else:
          raise ValueError,"state field '"+field+"' not initialized and no default value provided";
      else:          
        return False;
        
    def set (self,field,value):
      pynode.field = self.newstate[field] = value;
      
  def _state_handler (self,staterec,initializing):
    helper = self.StateHelper(self,staterec,initializing);
    self.update_state(helper);
    return helper.newstate;
    
  def get_state (self,field):
    """Returns the given field of the node's state record."""
    return meqserver_interface.get_node_state_field(self._baton,str(field));
    
  def set_state (self,field,value):
    """Sets the given field of the node's state record."""
    return meqserver_interface.set_node_state_field(self._baton,str(field),value);
    
  def get_forest_state (field):
    """Returns the given field of the forest state record."""
    return meqserver_interface.get_forest_state_field(str(field));
    
  get_forest_state = staticmethod(get_forest_state);
  

class PyVerboseNode (PyNode):
  """A PyNode class used for testing: this simply prints the arguments
  every time set_state_impl or get_result is called""";
  
  def set_state_impl (self,staterec,initializing):
    _dprint(0,"set_state_impl:",staterec);
    _dprint(0,"set_state_impl: initializing=",initializing);
    
  def get_result (self,children,request):
    _dprint(0,"get_result: request is ",request);
    _dprint(0,"get_result: children are ",children);
    return None;
  
