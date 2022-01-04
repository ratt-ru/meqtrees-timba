#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.widgets import *
from Timba.Grid.Debug import *
import Timba.Grid.Cell
import Timba.Grid.Page
from Timba import *

import weakref
import re
import gc
import types

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

_reg_viewers = {};
_reg_viewers_byname = {};

# registers a viewer plug-in for the specified type
#
# a viewer plug-in must provide the following interface:
#

def registerViewer (tp,viewer,check_udi=lambda x:True,priority=0):
  """Registers a viewer for the specified type:
  The 'viewer' argument must be a class (or callable) providing the following 
  interface:
    viewer.viewer_name 
      # (optional static attribute) returns "official name" of this 
      # viewer class, for use in menus and such. If not defined, the classname 
      # (viewer.__name__) will be used instead. 
    viewer.is_viewable(data); 
      # (optional static method) checks if a specific data item (of the 
      # registered type) is viewable in this viewer or not. If not defined, 
      # True is assumed.
    viewer.uses_cells 
      # (optional static attribute) does this viewer uses the workspace at all?
      # True is assumed. (Should be False for viewers creating their own
      # windows).
    viewer.icon(); 
      # (optional static method) returns a QIcon for this viewer
    vo = viewer(gw,cellspec,dataitem,**opts); 
      # construct a viewer object. The gw argument is its parent 
      # GriddedWorkspace object from which the viewer may allocate cells and 
      # pages as needed. 
      # The cellspec argument should be passed to gw.allocate_cells() when 
      # allocating cell(s). This will contain information on how to allocate 
      # a cell (i.e., if an existing cell should be reused, or a new one 
      # allocated, etc.)
      # A dataitem (GridDataItem class) will be supplied at this 
      # time, although dataitem.data may be None if the object is not yet 
      # populated. 
      # **opts may be used to pass in optional keyword arguments on a 
      # per-viewer basis.
    vo.grid_page();
      # Return page on which viewer resides (a Grid.Page object), or None
      # if viewer is outside the grid.
    vo.set_data(dataitem,**opts);
      # sets/updates the content of the viewer. **opts may be used to pass 
      # in optional keyword arguments on a per-viewer basis.
    vo.add_data(dataitem,**opts); 
      # (optional method) adds another data object to the viewer. If 
      # multiple-object viewing is not supported, the viewer class should not
      # define this method. The method must return True if the object is
      # successfully added, or False if this cannot be done.
    vo.cleanup():
      # called when the viewer object is removed from the workspace
  The viewer object may also issue one Qt signal: PYSIGNAL("refresh()",(udi,)), 
  which requests a refresh of the data item given by the udi.
  Note that the GridCell interface already provides a refresh button which does 
  the same on behalf of the viewer.
  """;
  global _reg_viewers;
  global _reg_viewers_byname;
  name = getattr(viewer,'viewer_name',viewer.__name__);
  _dprint(1,"registering",name,"for type",tp);
  _reg_viewers.setdefault(tp,[]).append((priority,viewer,check_udi));
  _reg_viewers_byname[name] = viewer;

def isViewableWith (arg,viewer):
  if type(arg) is type:
    return True;
  try: checker = viewer.is_viewable;
  except AttributeError: return True; 
  if callable(checker):
    return checker(arg);
  return True;

def isViewable (arg,udi=None):
  global _reg_viewers;
  # arg may specify a type or a data object
  if type(arg) is type:
    datatype = arg;
  else:
    datatype = type(arg);
  for (tp,vlist) in _reg_viewers.items():
    # registered type must be a superclass of the supplied type;
    # registered dmi type must be either None or match the argument dmi type
    if issubclass(datatype,tp):
      for (pri,viewer,check_udi) in vlist:
        if isViewableWith(arg,viewer) and ( not udi or check_udi(udi) ):
          return True;
  return False;
  
def getViewerByName (name):
  global _reg_viewers_byname;
  return _reg_viewers_byname.get(name,None);

def getViewerList (arg,udi=None):
  global _reg_viewers;
  if arg is None:
    return [];
  # arg may specify a type or a data object
  if type(arg) is type:
    datatype = arg;
  else:
    datatype = type(arg);
  viewer_pri = {};
  # resolve data type (argument may be object or type)
  _dprint(3,udi,type(arg),'looking for viewers for',datatype);
  for (tp,vlist) in _reg_viewers.items():
    # find viewers for this class
    _dprint(3,udi,datatype,'subclass of',tp,issubclass(datatype,tp));
    if issubclass(datatype,tp):
      for (pri,v,checker) in vlist:
        _dprint(3,udi,'isViewableWith(arg,v)',v,isViewableWith(arg,v),checker(udi));
        if type(arg) is type or isViewableWith(arg,v): # if specified as object, check viewability
          # check udi if specified
          if udi is None or checker(udi):
            _dprint(3,udi,type(arg),'viewer',v,'priority',pri);
            viewer_pri[v] = min(pri,viewer_pri.get(v,999999));
  # return list sorted by priority
  vlist = list(viewer_pri.keys());
  from past.builtins import cmp
  from functools import cmp_to_key
  vlist.sort(key=cmp_to_key(lambda a,b,dd=viewer_pri:cmp(dd[a],dd[b])));
  return vlist;

class Floater (QMainWindow):
  """implements a floating window""";
  def __init__ (self,parent):
    QMainWindow.__init__(self,parent,Qt.Dialog);
    self.setWindowIcon(pixmaps.float_window.icon());
#  def hideEvent (self,ev):
#    _dprint(0,'hideEvent',ev);
#    self.emit(SIGNAL("hidden"));
  def closeEvent (self,ev):
    _dprint(2,'closeEvent',ev);
    self.emit(SIGNAL("closed"));
    QMainWindow.closeEvent(self,ev);
    
#    self.hide();
#    ev.ignore();
    
_dataitems = {};
_current_gw = None;
    
def setDefaultWorkspace (gw):
  global _current_gw;
  _current_gw = gw;
  
def getCurrentWorkspace ():
  return _current_gw;
  
def addDataItem (item,gw=None,show_gw=True,viewer=None,position=None,avoid_pos=None,newcell=False,newpage=False):
  """Adds a data cell with a viewer the given item.
       viewer:    if not None, must a be a viewer plugin class, or name. 
                  Overrides the viewer specified by the item.
       gw:        if not None, specifies a non-default gridded workspace to
                  display the item on.
       position:  if not None, must be a tuple specifying a cell to allocate, 
                  as (gridpage,x,y)
       avoid_pos: if not None, must be a tuple specifying a cell to AVOID
                  allocating, as (gridpage,x,y). 
       newpage:   if True, creates a new page with the data cell
       newcell:   if True, uses an empty cell (changing layouts as needed)
                  rather than reusing an existing unpinned panel. If False,
                  reuses a panel if possible.
       Note that the position, newpage and newcell argument are rolled up into
       a "cell specification" dict, and passed to the viewer object as the 
       cellspec argument. The cellspec is then passed as keyword arguments
       (via **cellspec) to Workspace.allocate_cells() when the viewer goes 
       to allocate cells for itself.
     Return value is either the item object itself if added, or if the
     same item (i.e. same udi/viewer) is already displayed, then the old
     item object is returned, or None on error.
  """;
  _dprint(2,item.udi,item.viewer);
  global _dataitems,_current_gw;
  # if position is specified, select workspace from page
  gw = None;
  if position is not None and isinstance(position[0],Timba.Grid.Page):
    gw = position[0].gw();
  item._gridded_workspace = gw = gw or _current_gw;
  if isinstance(viewer,str):
    vc = getViewerByName(viewer,None);
    if vc:
      viewer = vc;
    else:
      raise TypeError("unknown viewer type "+viewer);
  else:  
    viewer = viewer or item.viewer;
  if not viewer:
    if not item.viewer_list:
      raise TypeError("no viewers registered and none explicitly specified");
    viewer = self.viewer_list[0];
  # Are we already displaying this item? (if not, init with empty list)
  itemlist = _dataitems.setdefault(item.udi,[]);
  # see if we can get away with not adding a viewer at all, because
  # the item is already displayed on the current page with the same viewer,
  # and we're not requested to put it into a new cell or a specific cell
  if itemlist and not (position or newcell or newpage):
    _dprint(2,'item already displayed, checking for suitable viewers');
    _dprint(2,'current page',_current_gw.current_page());
    for item0 in itemlist:
      _dprint(2,'item page',item0.viewer_obj.grid_page());
      if item0.viewer == viewer and item0.viewer_obj.grid_page() is _current_gw.current_page():
        _dprint(2,'found visible viewer');
        # in this case, highlight the data item, ask for a refresh, and
        # let the viewers take care of the rest
        highlightDataItem(item0);
        if item.data is not None:
          item0.update(item.data);
        else:
          item0.refresh();
        if show_gw:
          gw.show();
        return item0;
  # ok, we got to here so we have to create a viewer
  vopts = {};
  vopts.update(item.viewopts.get(None,{}));
  for (vclass,vo) in item.viewopts.items():
    if vclass and issubclass(viewer,vclass):
      vopts.update(vo);
  cellspec = { 'position':position,'avoid_pos':avoid_pos,'newcell':newcell,'newpage':newpage };
  try:
    item.viewer_obj = viewer(gw,dataitem=item,cellspec=cellspec,**vopts);
  except:
    (et,ev,etb) = sys.exc_info();
    _dprint(0,'error creating plugin',viewer.__name__);
    traceback.print_exc();
    errstr = '<qt><center><big>Error creating a plug-in of class <b>%s</b> for item <tt>%s</tt>.</big></center>'%(viewer.__name__,item.udi);
    errstr += '<p><tt>%s</tt>: %s'% \
        (getattr(ev,'_classname',ev.__class__.__name__),getattr(ev,'__doc__',''));
    if hasattr(ev,'args'):
      errstr += '</p><p>("'+' '.join(ev.args)+'")</p>';
    errstr += '</p></qt>';
    QMessageBox.warning(None,'Error initializing plug-in',errstr,QMessageBox.Ok,QMessageBox.NoButton);
    return None;
  # add to list
  itemlist.append(item);
  # highlight it
  highlightDataItem(item);
  # ask for a refresh of the item
  item.refresh();
  # show the workspace
  if show_gw:
    gw.show();
  return item;

def removeDataItem (item):
  global _dataitems;
  global _highlighted_item;
  itemlist = _dataitems.get(item.udi,[]);
  _dprint(2,item.udi,len(itemlist),'instances');
  # remove from highlight list
  if item is _highlighted_item:
    _highlighted_item = None;
    _current_gw.wtop().emit(SIGNAL("itemSelected"),None,);
  # remove from item list
  for i in range(len(itemlist)):
    if itemlist[i] is item:
      _dprint(2,'removing instance',i);
      del itemlist[i];
      item.cleanup();
      return;
  _dprint(2,'no matching items found');
  
_highlighted_item = None;
  
def highlightDataItem (item):
  global _highlighted_item;
  _dprint(2,item.udi);
  # remove highlights from previous cells, if any
  if _highlighted_item:
    if item is _highlighted_item:
      _dprint(3,'already highlighted');
      return;
    else:
      _dprint(3,'de-highlighting previous',_highlighted_item.udi);
      _highlighted_item.highlight(False);
  _dprint(3,'highlighting',item.udi);
  _highlighted_item = item;  
  item.highlight(True);
  _current_gw.wtop().emit(SIGNAL("itemSelected"),item,);
  
def getHighlightedItem ():
  return _highlighted_item;

# updates a data item, if it is known
def updateDataItem (udi,data):
  global _dataitems;
  _dprint(3,udi);
  _dprint(2,_dataitems);
  # scan current data items to see which need updating
  for (u,itemlist) in _dataitems.items():
    if u == udi or u.startswith(udi+'/'):
      _dprint(3,len(itemlist),'items for',u);
      update = True;
      data1 = data;  # data1 may get modified below
      subudi = u[len(udi):];
      if subudi:   # a sub-udi, so we must process it by indexing into the data
        # split into keys and process one by one (first one is empty string)
        for key in subudi.split("/")[1:]:
          try: data1 = data1[key];
          except (TypeError,KeyError): # try to convert key to integer instead
            try: data1 = data1[int(key)];
            except: 
              update = False;
              break;
      # update for all items in list
      if update:
        for item in itemlist:
          _dprint(3,'updating',item);
          item.update(data1);
