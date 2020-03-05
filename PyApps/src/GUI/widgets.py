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

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

from Timba.utils import verbosity

_dbg = verbosity(0,name='widgets');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# ====== DataDroppableWidget ===================================================
# A metaclass implementing a data-droppable widget.
# Use, e.g., DataDroppableWidget(QToolButton) to create a class that
# subclasses QToolButton, handles data-drop events, and emits an
# itemDropped() signal.
#
def DataDroppableWidget (parent_class):
  class widgetclass (parent_class):
    def __init__ (self,*args):
      parent_class.__init__(self,*args);
      self.setAcceptDrops(True);
      self._accept_drops_from_children = False;
    def setAcceptDropsFromChildren(self,value):
      self._accept_drops_from_children = value;
      
    @staticmethod 
    def get_drag_key (event):
      key = None;
      data = event.mimeData();
      if data.hasText():
        key = data.text();
        _dprint(3,"mimeData text is",key);
      elif data.hasUrls():
        key = " ".join([str(url.toString()) for url in data.urls()]);
        _dprint(3,"mimeData URLs are",key);
      return key;
    # Drag objects must be text or URL drags originating from another widget (i.e., 
    # within the same app). The source widget must implement a 
    # get_drag_item(key) method and a get_drag_item_type(key) method,
    # where 'key' is a string containing the text of the drag.
    # The method can return any object, or None for none, it is up to the
    # subclass to deal with this.
    def dragEnterEvent (self,ev):
      key = None;
      try: 
        wsrc = ev.source();
        key = self.get_drag_key(ev);
        # refuse event if source widget does not define get_drag_item(), or drag is not a string
        try: 
          if not callable(wsrc.get_drag_item) or not key:
            _dprint(3,'invalid drag or drag source');
            return;
        except AttributeError: return;
        _dprint(3,'got drag key',key);
        # if source widget is a child of ours, we may refuse the drop
        if not self._accept_drops_from_children:
          ws = wsrc;
          while ws:
            if ws is self:
              _dprint(3,'refusing drop from child widget');
              return;
            ws = ws.parent();
        # check if we accept this item
        if hasattr(self,'accept_drop_item'):
          item = wsrc.get_drag_item(key);
          _dprint(3,'drag item is',item);
          if item is not None and self.accept_drop_item(item):
            _dprint(3,'accepted');
            ev.accept();
        elif hasattr(self,'accept_drop_item_type'):
          itemtype = wsrc.get_drag_item_type(key);
          _dprint(3,'drag item type is',itemtype);
          if itemtype is not None and self.accept_drop_item_type(itemtype):
            _dprint(3,'accepted');
            ev.accept();
        else:
          _dprint(3,'no accept_() methods defined, accepting by default');
          ev.accept();
      except AttributeError: 
        _dprint(3,'attribute error somewhere, rejecting drag');
        ev.ignore();
        pass;
    # The text drag is decoded into a text key, an item is fetched from the 
    # source using get_drag_item(key), and process_drop_item is called
    def dropEvent (self,ev):
      key = self.get_drag_key(ev);
      if key:
        try: dragfunc = ev.source().get_drag_item;
        except AttributeError: return;
        item = dragfunc(str(key));
        if item is not None:
          self.process_drop_item(item,ev);
          ev.accept();
        
#     def accept_drop_item (self,item):
#       """Provide this function to selectively accept drops based on item
#       itself. Return False to reject item.""";
#       return True;
#       
#     def accept_drop_item_type (self,itemtype):
#       """Provide this function to selectively accept drops based on item
#       type. Only called if accept_drop_item() is not defined. This is 
#       usually more efficient than defining accept_drop_item() itself. 
#       If neither accept_xxx() method is defined, True is assumed.
#       Return False if item type is not supported.""";
#       return True;
      
    def process_drop_item (self,item,event):
      """This function is called when a drop occurs.
      Default action is to emit an itemDropped() signal.""";
      self.emit(SIGNAL("itemDropped"),item,event);
      
  return widgetclass;


# ====== DataDraggableTreeWidget =================================================
# A QListView implementing the dragObject() function as follows:
#   if the selected item has a _udi attribute, returns a text drag containing 
#   the udi.
def DataDraggableTreeWidget (parent_class):
  class widgetclass (parent_class):
    def __init__ (self,*args):
      parent_class.__init__(self,*args);
      self.setDragEnabled(True);
      
    def mimeData (self,items):
      urls = [];
      for item in items:
        udi = getattr(item,'_udi',None);
        if udi:
          urls.append(QUrl(udi));
      mimedata = QMimeData();
      mimedata.setUrls(urls);
      return mimedata;
      
  return widgetclass;
