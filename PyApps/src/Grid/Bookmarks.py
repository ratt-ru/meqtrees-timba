#!/usr/bin/python

from Timba.dmi import *
from Timba.utils import *
from qt import *

class Bookmark (QObject):
  def __init__ (self,name,udi,viewer=None,parent):
    QObject.__init__(parent);
    self.rec = record(name=name,udi=udi);
    if viewer is not None:
      if not isinstance(viewer,str):
        viewer = getattr(viewer,'viewer_name',None);
        if viewer is None:
          viewer = getattr(viewer,'__name__');
      self.rec = viewer;
    self.viewer = viewer;
  def show(self):
    pass;

class Pagemark (QObject):
  iconset = pixmaps.bookmark_toolbar.iconset;
  def __init__ (self,name,page,parent):
    QObject.__init__(parent);
    self.rec = record(name=name,page=page);
  def show(self):
    pass;

class BookmarkFolder (QObject):
  iconset = pixmaps.bookmark_folder.iconset;
  def __init__ (self,name,parent,load=None):
    QObject.__init__(parent);
    self.name = name;
    self._bklist = [];
    self._menu = QPopupMenu(self);
    if load is not None:
      self.load(load);
    
  def load (self,bklist):
    """loads bookmarks from list""";
    self._bklist = [];
    self._menu.clear();
    for item in bklist:
      try: name = item.name;
      except AttributeError:
        _dprintf(2,"ignoring invalid bookmark item",item);
        continue;
      # add all items here too!
      # determine type
      if hasattr(item,'page'):  # page bookmark
        self.addItem(Pagemark(name,item.list,self));
      elif hasattr(item,'folder'): # folder
        self.addItem(BookmarkFolder(name,self,load=item.folder));
      elif hasattr(item,'udi'): # bookmark
        self.addItem(Bookmark(name,item.udi,getattr(item,'viewer',None),self));
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
    
  def addItem (self,item):
    """adds an item to the list and menu.""";
    self._bklist.append(item);
    if isinstance(item,BookmarkFolder):
      self._menu.insertItem(item.iconset(),item.name,item.getMenu());
    elif hasattr(item,iconset):
      self._menu.insertItem(item.iconset(),item.name,item.show);
    else:
      self._menu.insertItem(item.name,item.show);
    
  def add (self,name,udi,viewer=None):
    """adds bookmark to end of list, updates popup menu if present.""";
    self.addItem(Bookmark(name,udi,viewer,self));
      
  def addFolder (self,name):
    """adds bookmark folder to end of list, updates popup menu if present.""";
    self.addItem(BookmarkFolder(name,self));
  
  def addPage (self,name,page):
    """adds page bookmark to end of list, updates popup menu if present.""";
    self.addItem(Pagemark(name,page,self));
    
  def getMenu (self):
    """returns popup menu containing all items.""";
    return self._menu;
    
