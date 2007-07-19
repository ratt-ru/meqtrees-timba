#!/usr/bin/python
# PyNode: base class for nodes implemented in Python

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
from Timba import utils
try:
  import meqserver_interface
except:
  pass;

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
        setattr(self.pynode,field,self.staterec[field]);
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
    
  def set_symdeps (self,*symdeps):
    """Sets the given field of the node's state record."""
    symdeps = map(str,symdeps);
    return meqserver_interface.set_node_active_symdeps(self._baton,symdeps);
    
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
    
  def get_result (self,request,*children):
    _dprint(0,"get_result: request is ",request);
    _dprint(0,"get_result: children are ",children);
    return None;
  
