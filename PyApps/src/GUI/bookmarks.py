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

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

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
    # and rec.viewer to viewer name; set icon based on viewer
    if viewer is None:
      self.icon = QIcon;
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
        raise TypeError("illegal viewer argument "+str(viewer));
      if self.viewer is not None:
        self.icon = getattr(self.viewer,'icon',QIcon);
        self.enabled = True;
      else:
        self.icon = QIcon;
        self.enabled = False;
  def show(self,**kws):
    self.parent().emit(SIGNAL("showBookmark"),self.rec.udi,self.rec.viewer);

class Pagemark (QObject):
  icon = pixmaps.bookmark_toolbar.icon;
  enabled = True;
  def __init__ (self,name,page,parent):
    QObject.__init__(self,parent);
    QObject.connect(self,PYSIGNAL("updated()"),parent,PYSIGNAL("updated()"));
    self.name = name;
    self.page = page;
    self.rec = record(name=name,page=page);
  def show (self,**kws):
    self.parent().emit(SIGNAL("showPagemark"),self,);

class BookmarkFolder (QObject):
  icon = pixmaps.bookmark_folder.icon;
  enabled = True;
  def __init__ (self,name,parent,menu=None,load=None,gui_parent=None):
    """Creates a folder of bookmarks, and the associated menu.
    If 'menu' is not None, bookmarks will be added to the supplied menu, else a new one will be created.
    If load is set to a list (of bookmarks records), folder will be loaded.
    'parent' is parent object. 'gui_parent' is parent object for menus (or else 'parent' will be used.)
    """;
    QObject.__init__(self,parent);
    self.name = name;
    self._gui_parent = gui_parent;
    self._bklist = [];
    self._qas = [];
    if menu:
      self._menu = menu;
      self._have_initial_menu = True;
    else:
      self._menu = QMenu(str(name),gui_parent or parent);
      self._menu.setIcon(self.icon());
      self._have_initial_menu = False;
    if load is not None:
      self.load(load);
    QObject.connect(self,PYSIGNAL("showBookmark()"),self.parent(),PYSIGNAL("showBookmark()"));
    QObject.connect(self,PYSIGNAL("showPagemark()"),self.parent(),PYSIGNAL("showPagemark()"));
    
  def load (self,bklist):
    """loads bookmarks from list""";
    self._bklist = [];
    if self._have_initial_menu:
      for qa in self._qas:
        self._menu.removeAction(qa);
    else:
      self._menu.clear();
    self._qas = [];
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
      qa = self._menu.addMenu(item.getMenu());
    elif isinstance(item,Pagemark) or isinstance(item,Bookmark):
      qa = self._menu.addAction(item.icon(),str(item.name),item.show);
    if not item.enabled:
      qa.setEnabled(False);
    self._qas.append(qa);
    if not quiet:
      self.emit(SIGNAL("updated"));
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
    
