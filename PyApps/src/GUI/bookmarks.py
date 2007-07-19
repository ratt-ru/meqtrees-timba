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

from Timba.dmi import *
from Timba.utils import *
from qt import *
from Timba import Grid
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import meqgui

_dbg = verbosity(0,name='bookmarks');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class Bookmark (QObject):
  def __init__ (self,name,udi,parent,viewer=None):
    QObject.__init__(self,parent);
    QObject.connect(self,PYSIGNAL("updated()"),parent,PYSIGNAL("updated()"));
    self.name = name;
    self.rec = record(name=name,udi=udi);
    # resolve viewer to actual viewer class (or None if none specified),
    # and rec.viewer to viewer name; set iconset based on viewer
    if viewer is None:
      self.iconset = QIconSet;
      self.enabled = True;
      self.viewer  = None;
    else:
      if isinstance(viewer,str):
        self.rec.viewer = viewer;
        self.viewer = Grid.Services.getViewerByName(viewer);
      elif callable(viewer):
        self.rec.viewer = getattr(viewer,'viewer_name',viewer.__name__);
        self.viewer = viewer;
      else:
        raise TypeError,"illegal viewer argument "+str(viewer);
      if self.viewer is not None:
        self.iconset = getattr(self.viewer,'icon',QIconSet);
        self.enabled = True;
      else:
        self.iconset = QIconSet;
        self.enabled = False;
  def show(self,**kws):
    self.parent().emit(PYSIGNAL("showBookmark()"),(self.rec.udi,self.rec.viewer));

class Pagemark (QObject):
  iconset = pixmaps.bookmark_toolbar.iconset;
  enabled = True;
  def __init__ (self,name,page,parent):
    QObject.__init__(self,parent);
    QObject.connect(self,PYSIGNAL("updated()"),parent,PYSIGNAL("updated()"));
    self.name = name;
    self.page = page;
    self.rec = record(name=name,page=page);
  def show (self,**kws):
    self.parent().emit(PYSIGNAL("showPagemark()"),(self,));

class BookmarkFolder (QObject):
  iconset = pixmaps.bookmark_folder.iconset;
  enabled = True;
  def __init__ (self,name,parent,menu=None,load=None,gui_parent=None):
    QObject.__init__(self,parent);
    self.name = name;
    self._gui_parent = gui_parent;
    self._bklist = [];
    self._menu = menu or QPopupMenu(gui_parent or parent);
    self._initial_menu_size = self._menu.count();
    if load is not None:
      self.load(load);
    QObject.connect(self,PYSIGNAL("showBookmark()"),self.parent(),PYSIGNAL("showBookmark()"));
    QObject.connect(self,PYSIGNAL("showPagemark()"),self.parent(),PYSIGNAL("showPagemark()"));
    
  def load (self,bklist):
    """loads bookmarks from list""";
    self._bklist = [];
    if self._initial_menu_size:
      while self._menu.count() > self._initial_menu_size:
        self._menu.removeItemAt(self._initial_menu_size);
    else:
      self._menu.clear();
    for item in bklist:
      try: name = item.name;
      except AttributeError:
        _dprintf(2,"ignoring invalid bookmark item",item);
        continue;
      # add all items here too!
      # determine type
      if hasattr(item,'page'):  # page bookmark
        self.addItem(Pagemark(name,item.page,self),quiet=True);
      elif hasattr(item,'folder'): # folder
        self.addItem(BookmarkFolder(name,self,load=item.folder,gui_parent=self._gui_parent),quiet=True);
      elif hasattr(item,'udi'): # bookmark
        self.addItem(Bookmark(name,item.udi,self,viewer=getattr(item,'viewer',None)),quiet=True);
      else:
        _dprintf(2,"ignoring invalid bookmark item",item);
    
  def getList (self):
    """returns bookmarks as a list""";
    outlist = [];
    for item in self._bklist:
      if isinstance(item,BookmarkFolder):
        outlist.append(record(name=item.name,folder=item.getList()));
      elif isinstance(item,Bookmark):
        outlist.append(item.rec);
      elif isinstance(item,Pagemark):
        outlist.append(item.rec);
    return outlist;
    
  def addItem (self,item,quiet=False):
    """adds an item to the list and menu.""";
    self._bklist.append(item);
    if isinstance(item,BookmarkFolder):
      iid = self._menu.insertItem(item.iconset(),item.name,item.getMenu());
    elif isinstance(item,Pagemark):
      iid = self._menu.insertItem(item.iconset(),item.name,item.show);
    else:
      iid = self._menu.insertItem(item.iconset(),item.name,item.show);
    if not item.enabled:
      self._menu.setItemEnabled(iid,False);
    if not quiet:
      self.emit(PYSIGNAL("updated()"),());
    return item;
    
  def add (self,name,udi,viewer=None):
    """adds bookmark to end of list, updates popup menu if present.""";
    return self.addItem(Bookmark(name,udi,self,viewer=viewer));
      
  def addFolder (self,name):
    """adds bookmark folder to end of list, updates popup menu if present.""";
    return self.addItem(BookmarkFolder(name,self));
  
  def addPage (self,name,page):
    """adds page bookmark to end of list, updates popup menu if present.""";
    return self.addItem(Pagemark(name,page,self));
    
  def getMenu (self):
    """returns popup menu containing all items.""";
    return self._menu;
    
  def generatePageName (self):
    """convenience function to generate a default name for a new pagemark.""";
    # use list comprehension to count the number of pagemarks
    count = len([item for item in self._bklist if isinstance(item,Pagemark)]);
    return "Page " + str(count+1);
    
    
    
