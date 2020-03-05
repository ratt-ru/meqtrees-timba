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

__all__ = [ "Cell","CellBlock","Page","Workspace","Services" ];

from Timba.Grid import Services

from .Services import Floater,addDataItem,removeDataItem,updateDataItem
from Timba.Grid.Cell import Cell
from Timba.Grid.CellBlock import CellBlock
from Timba.Grid.Page import Page
from Timba.Grid.Workspace import Workspace

from Timba.Grid.Debug import *

from Timba.Meq import meqds


class Error (RuntimeError):
  """Grid widget manipulation error""";
  _classname = "Grid.Error";

# ====== Grid.DataItem ==========================================================
# represents a per-cell data item 
class DataItem (object):
  """Represents a DataItem that is displayed in by the workspace (though not necessarily
  in a cell, or in a single GridCell.) This is meant to be constructed by data sources, 
  and passed to the workspace for displaying. Besides everything passed into the constructor,
  the dataitem also has the following attributes:
    refresh_func: the refresh function.
    viewer:     viewer class for this item (selected automatically if not specified)
    viewer_obj: instance of viewer object, once this item is displayed 
  """;
  def __init__ (self,udi,name=None,caption=None,desc=None,data=None,datatype=None,
                refresh=None,viewer=None,viewopts={}):
    """the constructor initializes standard attributes:
    udi:      the Uniform Data ID (e.g. "nodestate/<nodename>")
    name:     the name of the data item (plain text, e.g., the node name)
    caption:  caption (Qt RichText tags allowed)
    desc:     detailed description (e.g. for popup hints, etc.)
    data:     content, None if not yet initialized
    datatype: if data=None, may be used to specify which data type it will be
    refresh:  refresh function. (If not None, then the GridCell will have a 
              'refresh' button calling this function when pressed)
    viewer:   If None, a viewer will be selected from among the registered
              viewers for the data type/udi. Otherwise, provide a callable 
              viewer plug-in, or a name. See registerViewer() for details.
    viewopts: dict of dicts of viewer options (passed in as keyword arguments
              to the viewer constructor).
              viewopts[None]   applies to all viewers,
              viewopts[class]  applies to a specific class (overrides [None])
    """;
    # copy-constructor form?
    if isinstance(udi,DataItem):
      for attr in ("udi","name","caption","desc","data","refresh_func",
                   "viewer","viewopts","viewer_list"):
        setattr(self,attr,getattr(udi,attr));
    else: # else new item
      if refresh and not callable(refresh):
        raise ValueError('refresh argument must be a callable');
      self.udi      = udi;
      self.name     = name or udi;
      self.caption  = caption or udi;
      self.desc     = desc or self.name;
      self.data     = data;
      if viewopts is None:
        viewopts = {};
      self.viewopts = viewopts;
      self.refresh_func = refresh;
      # build list of compatible viewers
      self.viewer_list = Services.getViewerList(datatype or data,udi=udi);
      # if viewer specified by string, try to look it up
      if isinstance(viewer,str):
        vc = Services.getViewerByName(viewer);
        if vc:
          viewer = vc;
        else:
          raise TypeError("unknown viewer type "+viewer);
      # if viewer not specified, try to select from list
      if viewer is None:
        if not self.viewer_list:
          raise TypeError("no viewers registered and none specified");
        viewer = self.viewer_list[0];
      else:
        if not callable(viewer):
          raise TypeError('viewer argument must be a callable');
        # prepend to list
        if viewer not in self.viewer_list:
          self.viewer_list.insert(0,viewer);
      self.viewer = viewer;
      self.viewer_name = getattr(viewer,'viewer_name',viewer.__name__);
    # init other internal state
    self.viewer_obj = None;
  def __del__ (self):
    self.cleanup();
  def cleanup (self):
    _dprint(2,self.udi);
    try: self.viewer_obj.cleanup();
    except: pass;
    self.viewer_obj = None;
  def refresh (self):
    self.refresh_func and self.refresh_func();
  def is_mutable (self):
    return self.refresh_func is not None;
  def update (self,data):
    self.data = data;
    if self.viewer_obj:
      _dprint(3,'updating',self.viewer_obj,'with item',self);
      self.viewer_obj.set_data(self); 
  def highlight (self,color=True):
    if self.viewer_obj:
      self.viewer_obj.highlight(color);
  # returns True if the specified viewer class is already displaying this item
  def is_viewed_by (self,viewer):
    for v in self.viewers:
      if v is viewer or v.__class__ == viewer:
        return True;
    return False;

