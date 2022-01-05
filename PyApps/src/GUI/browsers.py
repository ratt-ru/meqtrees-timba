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
from Timba import utils
from Timba import dmi_repr
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import widgets
from Timba import Grid
from Timba.Meq import meqds

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL,ClickableTreeWidget
from Timba.GUI.widgets import DataDraggableTreeWidget

import sys
import time
import weakref

from Timba.pretty_print import PrettyPrinter

dmirepr = dmi_repr.dmi_repr();

_dbg = verbosity(0,name='browsers');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# helper class implementing a 'Precision' menu
class PrecisionPopupMenu (QMenu):
  def_range = list(range(0,12));
  num_formats = (('f','&Fixed-point'),('e','&Exponent'),('g','&Auto'));
  def __init__ (self,parent=None,precrange=None,prec=(None,'g')):
    self._currier = PersistentCurrier();
    QMenu.__init__(self,parent);
    # format title
    #tlab = QLabel("<i>Format:</i>",self);
    #tlab.setAlignment(Qt.AlignCenter);
    #tlab.setFrameShape(QFrame.ToolBarPanel);
    #tlab.setFrameShadow(QFrame.Sunken);
    #self.insertItem(tlab);
    self.addAction("Format").setSeparator(True);
    format_qag = QActionGroup(self);
    # number format settings
    self._format_qa = self._prec_qa = {};
    for fcode,name in self.num_formats:
      self._format_qa[fcode] = qa = QAction(name,format_qag);
      self.addAction(qa);
      qa.setCheckable(True);
      QObject.connect(qa,SIGNAL("triggered(bool)"),self._currier.curry(self.set_format,fcode));
    # precision title
    #tlab = QLabel("<i>Precision:</i>",self);
    #tlab.setAlignment(Qt.AlignCenter);
    #tlab.setFrameShape(QFrame.ToolBarPanel);
    #tlab.setFrameShadow(QFrame.Sunken);
    #self.insertItem(tlab);
    self.addAction("Precision").setSeparator(True);
    prec_qag = QActionGroup(self);
    # precision settings
    self._precrange = precrange or self.def_range;
    self._prec_qa[None] = qa = QAction("Default",prec_qag);
    self.addAction(qa);
    qa.setCheckable(True);
    QObject.connect(qa,SIGNAL("toggled(bool)"),self._currier.curry(self.set_prec,None));
    for p in self._precrange:
      self._prec_qa[p] = qa = QAction(str(p),prec_qag);
      self.addAction(qa);
      qa.setCheckable(True);
      QObject.connect(qa,SIGNAL("toggled(bool)"),self._currier.curry(self.set_prec,p));
    # set initial precision
    self.set(prec);
    
  def get (self):
    return self._prec;    
    
  def set (self,prec):
    self._prec = prec;
    for qa in self._prec_qa[prec[0]],self._format_qa[prec[1]]:
      if not qa.isChecked(): 
        qa.setChecked(True);
    self.emit(SIGNAL("setPrecision"),*self._prec);
    
  def set_prec (self,prec,set=True):
    if set:
      self.set((prec,self._prec[1]));
    
  def set_format (self,format,set=True):
    if set:
      self.set((self._prec[0],format));
      
      

class HierBrowser (object):
  # seqs/dicts with <= items than this are treated as "short"
  ShortSeq       = 5;
  # maximum number of sequence items to show in expanded view
  MaxExpSeq      = 1000;
  # max number of dictionary items to show in expanded view
  MaxExpDict     = 5000;
  # maximum width of value field, in characters
  MaxWidth       = 400;
  
  class Item (QTreeWidgetItem):
    def __init__(self,parent,key,value,udi_key=None,udi=None,
                 parent_udi=None,strfunc=None,
                 prec=(None,'g'),name=None,caption=None,desc=''):
      (key,value) = (str(key),str(value));
      # insert item at end of parent's content list (if any)
      if parent:
        parent_content = getattr(parent,'_content_list',None);
        if parent_content:
          QTreeWidgetItem.__init__(self,parent,parent_content[-1]);
          parent_content.append(self);
        else:
          QTreeWidgetItem.__init__(self,parent);
          if parent:
            parent._content_list = [self];
      else:
        QTreeWidgetItem.__init__(self);
      # get maxwidth
      maxwidth = getattr(self.treeWidget(),'_maxwidth',HierBrowser.MaxWidth);
      # set flags
      self.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled);
      # set text
      self.setText(0,str(key));
      self.setText(1,'');
      strvalue = str(value);
      self.setToolTip(2,"<P>"+strvalue+"</P>");
      if len(strvalue) > maxwidth:
        strvalue = strvalue[:maxwidth-2] + "...";
      self.setText(2,strvalue);
      # set viewable and content attributes
      self._viewable  = False;
      self._content   = None;
      # set the refresh function and precision, if specified
      self._strfunc   = strfunc;
      self._prec      = prec;
      self._prec_menu = None;
      # is udi directly specified?
      if udi:
        self._udi = udi;
        self._udi_key = udi_key or udi;
      else:
        # else generate udi key if none is specified
        if udi_key is id:
          udi_key = "%-X" % (id(self),);
        elif udi_key is None:
          udi_key = key;
        self._udi_key = udi_key;
        # setup udi of self, if parent self has a udi of its own
        # add ourselves to content map and propagate the map
        parent_udi = parent_udi or ( parent and parent._udi );
        if parent_udi:
          self._udi = '/'.join((parent_udi,udi_key));
        else:
          self._udi = None;
      # add to content map, if we have a UDI
      if self._udi and parent:
        self.treeWidget()._content_map[self._udi] = self;
      # set name and/or description
      self._name     = name;
      self._desc     = desc;
      self._caption  = caption;
      # other state
      self._curries  = [];
      
    def set_udi (self,udi):
      self.treeWidget()._content_map[udi] = self;
      self._udi = udi;
      
    # caches content in an item: marks as expandable, ensures content is a dict
    # if viewable is None, decides if content is viewable based on its type
    # else, must be True or False to specify viewability explicitly
    def cache_content(self,content,viewable=None,viewopts={},make_data=None):
      # if already have content, remove it (and remove all children)
      try: delattr(self,'_content');
      except: pass;
      try: delattr(self,'_content_list');
      except: pass;
      self.takeChildren();
      ### only available in Qt4.4
      ## self.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator);
      # make dummy child item to ensure that child indicatro is shown
      dum = QTreeWidgetItem(self);
      # convert all content to dict
      if isinstance(content,(dict,list,tuple,array_class)):
        self._content = content;
      elif isinstance(content,message):
        self._content = {};
        for k in [x for x in dir(content) if not x.startswith('_')]:
          attr = getattr(content,k);
          if not callable(attr):
            self._content[k] = attr;
      else:
        self._content = {"":content};
      # set the viewable property
      self.set_viewable(content,viewable,viewopts);
      # set the make_data property
      self._make_data = make_data;
      
    def set_viewable (self,content,viewable=None,viewopts={}):
      # set the viewable property
      if not self._udi:
        viewable = False;
      elif viewable is None:
        viewable = Grid.Services.isViewable(content);
      self._viewable = viewable;
      if viewable:
        self._viewopts = viewopts;
        self.setIcon(1,pixmaps.viewmag_plus.icon());
        self.setFlags(self.flags()|Qt.ItemIsDragEnabled);
        
    # helper static method to expand content into Items record 
    # note that we make this a static method because 'item' may in fact be
    # a parent QListView, the expansion interface is the same
    def expand_content(item,content):
      # content_list attribute is initialized upon expansion
      if hasattr(item,'_content_list'):
        return;
      # remove children of item, if any
      if hasattr(item,'takeChildren'):
        item.takeChildren();
      item._content_list = [];
      # Setup content_iter as an iterator that returns (label,value)
      # pairs, depending on content type.
      # Apply limits here
      if isinstance(content,dict):
        n = len(content) - HierBrowser.MaxExpDict;
        if n > 0:
          keys = list(content.keys())[:HierBrowser.MaxExpDict];
          content_iter = [(k,content[k]) for k in keys];
          content_iter.append(('...','...(%d items skipped)...'%n));
        else:
          content_iter = iter(content.items());
      elif isinstance(content,(list,tuple,array_class)):
        n = len(content) - HierBrowser.MaxExpSeq;
        if n > 0:
          content_iter = list(enumerate(content[:HierBrowser.MaxExpSeq-2]));
          content_iter.append(('...','...(%d items skipped)...'%(n+1)));
          content_iter.append((len(content)-1,content[-1]));
        else:
          content_iter = enumerate(content);
      else:
        content_iter = (("",content),);
      for (key,value) in content_iter:
        # simplest case: do we have an inlined to-string converter?
        # then the value is represented by a single item
        # use curry() to create a refresh-function
        (itemstr,inlined) = dmirepr.inline_str(value);
        if itemstr is not None:
          i0 = HierBrowser.Item(None,key,itemstr,prec=item._prec,parent_udi=item._udi,
                  strfunc=curry(dmirepr.inline_str,value));
          i0._content = value;
          i0.set_viewable(value);
          item._content_list.append(i0);
          continue;
        # else get string representation, insert item with it
        (itemstr,inlined) = dmirepr.expanded_repr_str(value,False);
        i0 = HierBrowser.Item(None,str(key),itemstr,prec=item._prec,
                  parent_udi=item._udi,
                  strfunc=curry(dmirepr.expanded_repr_str,value,False));
        item._content_list.append(i0);
        # cache value for expansion, if not inlined
        if isinstance(value,(list,tuple)):
          if len(value) > 1 or not inlined:
            i0.cache_content(value);
        elif isinstance(value,array_class):
          if value.size > 1 or not inlined:
            i0.cache_content(value);
        # dicts and messages always cached for expansion
        elif isinstance(value,(dict,message)):
          i0.cache_content(value);
      if hasattr(item,'addChildren'):
        item.addChildren(item._content_list);
      else:
        item.addTopLevelItems(item._content_list);
    expand_content = staticmethod(expand_content);

    # expands item content into subitems (wrapper around expand_content)
    def expand_self (self):
      self.expand_content(self,self._content);

    def make_data_item (self,viewer=None,viewopts={}):
      make_data = getattr(self,'_make_data',None);
      if callable(make_data):
        return make_data(viewer=None,viewopts={});
      # return item only if viewable, has udi and contents
      if self._content is not None and self._udi and self._viewable: 
        vo = getattr(self,'_viewopts',{});
        vo.update(viewopts);
        name = self._name;
        desc = self._desc;
        if not (name or desc):
          desc = self._udi;
        # a refresh function may be defined in the list view
        refresh = getattr(self.treeWidget(),'_refresh_func',None);
        # make item and return
        if not self._name and not self._caption:
          (name,caption) = meqds.make_udi_caption(self._udi);
        else:
          (name,caption) = (self._name or self._caption,self._caption or self._name);
        return Grid.DataItem(self._udi,name=name,caption=caption,
                             data=self._content,viewer=viewer,viewopts=vo,
                             refresh=refresh);
      return None;

    def get_precision (self):
      return self._prec;
      
    # changes display precision of item
    def set_precision (self,prec,set_menu=True,recursive=True):
      self._prec = prec;
      if callable(self._strfunc):
        (txt,inlined) = self._strfunc(prec=self._prec);
        self.setText(2,txt);
      # set menu checkmark, if any
      if set_menu and self._prec_menu:
        self._prec_menu.set(prec);
      # recursively apply to children
      if recursive:
        for i in range(self.childCount()):
          self.child(i).set_precision(prec);
    
    def _set_prec_frommenu (self,prec,format):
      self.set_precision((prec,format),set_menu=False);
 
    # curries and adds to local list
    # This is useful for creating on-the-fly callbacks
    # (since most Qt callbacks are held via weakref, they're deleted immediately
    # unless strongly referenced elsewhere)
    def curry (self,*args,**kw):
      c = curry(*args,**kw);
      self._curries.append(c);
      return c;  
      
    def xcurry (self,*args,**kw):
      c = xcurry(*args,**kw);
      self._curries.append(c);
      return c;  
      
    # dum argument needed to use as callback from popup menu
    def copy_to_clipboard (self,dum=None):
      # text = str(self.text(0))+": "+str(self.text(2));
      text = str(self.text(2));
      QApplication.clipboard().setText(text);
      QApplication.clipboard().setText(text,QClipboard.Selection);

    def get_context_menu (self):
      try: menu = self._context_menu;
      except AttributeError:
        # create menu on the fly when first called for this item
        viewer_list = self._content is not None and self._viewable and \
                   Grid.Services.getViewerList(self._content,self._udi);
        # create menu
        menu = self._context_menu = QMenu(self.treeWidget());
        menu._callbacks = [];
        menu.addAction(self._desc or self._name or str(self.text(0))).setSeparator(True);
        # insert Copy item
        copy_qa = menu.addAction(pixmaps.editcopy.icon(),'&Copy to clipboard',
                                 self.copy_to_clipboard,Qt.CTRL+Qt.Key_Insert);
        # create "Precision" submenu
        if self._strfunc:
          self._prec_menu = PrecisionPopupMenu(menu,prec=self._prec);
          qa = menu.addMenu(self._prec_menu);
          qa.setText('Number format');
          qa.setIcon(pixmaps.precplus.icon());
          QWidget.connect(self._prec_menu,PYSIGNAL("setPrecision()"),self._set_prec_frommenu);
        # create "display with" entries
        if viewer_list: 
          # create display submenus
          menu1 = self._display_menu1 = menu.addMenu(pixmaps.viewmag.icon(),"Display with");
          menu2 = self._display_menu2 = menu.addMenu(pixmaps.viewmag_plus.icon(),"New display with");
          for v in viewer_list:
            # create entry for viewer
            name = getattr(v,'viewer_name',v.__name__);
            try: icon = v.icon();
            except AttributeError: icon = QIcon();
            # add entry to both menus ("Display with" and "New display with")
            menu1.addAction(icon,name, \
              self.xcurry(self.emit_display_signal,viewer=v,_argslice=slice(0)));
            menu2.addAction(icon,name, \
              self.xcurry(self.emit_display_signal,viewer=v,newcell=True,_argslice=slice(0)));
      # set the precision submenu to the right setting
      return menu;
      
    # if item is displayable, creates a dataitem from it and
    # emits a displayDataItem(dataitem,cellspec) signal
    def emit_display_signal (self,viewer=None,**kwargs):
      _dprint(2,"emitting displayDataItem() signal");
      dataitem = self.make_data_item(viewer=viewer);
      if dataitem:
        self.treeWidget().emit(SIGNAL("displayDataItem"),dataitem,kwargs);

  # init for HierBrowser
  def __init__(self,parent,name,name1='',udi_root=None,caption=None,prec=(None,'g'),maxwidth=None):
    self._tw = DataDraggableTreeWidget(ClickableTreeWidget)(parent);
    self._tw.setHeaderLabels([name1,'',name]);
    self._tw.setRootIsDecorated(True);
    self._tw.setSortingEnabled(False);
    self._tw.header().setResizeMode(0,QHeaderView.ResizeToContents);
    self._tw.header().setResizeMode(1,QHeaderView.ResizeToContents);
    self._tw.header().setResizeMode(2,QHeaderView.ResizeToContents);
    self._tw.header().setStretchLastSection(False);
    self._tw.header().setResizeMode(QHeaderView.ResizeToContents);

    self._tw.header().hide();
    setattr(self._tw,'_maxwidth',maxwidth or HierBrowser.MaxWidth);
    # self._tw.header().setResizeMode(QHeaderView.Fixed);
#    for col in (0,1,2):
#      self._tw.setColumnWidthMode(col,QListView.Maximum);
#    self._tw.setFocus();
    QObject.connect(self._tw,SIGNAL('itemExpanded(QTreeWidgetItem*)'),
                     self._expand_item_content);
    QObject.connect(self._tw,PYSIGNAL('mouseButtonClicked()'),self._process_item_click);
    QObject.connect(self._tw,PYSIGNAL('itemContextMenuRequested()'),self._show_context_menu);
#    self._tw.connect(self._tw,SIGNAL('doubleClicked(QListViewItem*)'),
#                     self.display_item);
    # connect the get_drag_item method for drag-and-drop
    self._tw.get_drag_item = self.get_drag_item;
    self._tw.get_drag_item_type = self.get_drag_item_type;
    # enable UDIs, if udi root is not none
    self.set_udi_root(udi_root);
    # initialize precision
    self._tw._prec = prec;
    # for debugging purposes
    QObject.connect(self._tw,SIGNAL("itemClicked(QTreeWidgetItem*)"),self._print_item);
    
  def get_precision (self):
    return self._tw._prec;

  # changes display precision of view
  def set_precision (self,prec,recursive=True):
    self._tw._prec = prec;
    if recursive:
      for i in range(self._tw.topLevelItemCount()):
        self._tw.topLevelItem(i).set_precision(prec);
    
  def set_refresh_func (self,refresh):
    self._tw._refresh_func = refresh;
    
  def set_udi_root (self,udi_root):
    self._udi_root = udi_root;
    if udi_root is not None:
      if not udi_root.startswith('/'):
        udi_root = "/" + udi_root;
      self._tw._udi = udi_root;
      # map of UDIs to items
      self._tw._content_map = weakref.WeakValueDictionary();
    else:
      self._tw._udi = None;
    
  def _print_item (self,item,*dum):
    if item is not None:
      _dprint(4,'item:',item.text(0),item.text(2));
      for attr in ('_udi','_udi_key','_viewable','_name','_desc'):
        if hasattr(item,attr):
          _dprint(4,' ',attr+':',getattr(item,attr));
      try: 
        lencont = len(item.treeWidget()._content_map);
        _dprint(4,'  _content_map: ',lencont,' items');
      except AttributeError: pass;
    
  def get_drag_item (self,key):
    item = self._tw._content_map.get(key,None);
    return item and item.make_data_item();

  def get_drag_item_type (self,key):
    return key in self._tw._content_map and Timba.Grid.DataItem;
    
  def treeWidget (self):
    return self._tw;
  
  def wtop (self):
    return self._tw;
  
  def clear (self):
    self._tw.clear();
    for attr in ('_content',):
      try: delattr(self._tw,attr);
      except: pass;
    self.wtop().emit(SIGNAL("cleared"));
      
  # limits browser to last 'limit' items
  def apply_limit (self,limit):
    num_items = self._tw.topLevelItemCount();
    if num_items > limit:
      # remove N items from the beginning of the QTreeWidget
      items = [ self._tw.takeTopLevelItem(0) for i in range(num_items-limit) ];
      # add them to a dummy widget, which will then be destroyed -- this ensures the items get destoryed as well
      dum = QTreeWidget();
      dum.insertTopLevelItems(0,items);
      dum = None;

  # called when an item is expanded                    
  def _expand_item_content (self,item):
    item.expand_self();

  # slot: called when one of the items is clicked
  def _process_item_click (self,button,item,pos,col):
    if col == 1:
      if button == Qt.LeftButton:
        item.emit_display_signal();
      elif button == Qt.MidButton:
        item.emit_display_signal(newcell=True);
      
  # slot: called to show a context menu for an item
  def _show_context_menu (self,item,pos,col):
    menu = item and item.get_context_menu();
    if menu is not None:
      menu.exec_(self._tw.mapToGlobal(pos));

  def get_open_items (self):
    """gets tree of currently open and selected items. Returns tuple of
    (dict,<str|None>), describing the state of top-level items. The dict keys
    are udi_keys of expanded items; the dict values are similar tuples
    describing the state of each sub-level. The second element of the tuple is
    the key of the currently selected item, or None if no items are selected at
    this level; normally, at most one entry in the entire tree has a selected
    item. A None value in place of a tuple indicates no open and no selected
    items.""";
    # recursive helper function implementing tree traversal
    def _get_open_items_impl (parent,current):
      openitems = {};
      current_key = None;
      for i in range(parent.childCount()):
        item = parent.child(i);
        if item is current:
          current_key = item._udi_key;
        if item.isExpanded():
          openitems[item._udi_key] = _get_open_items_impl(item,current);
      if openitems or current_key:
        return (openitems,current_key);
      return None;
    return _get_open_items_impl(self._tw.invisibleRootItem(),self._tw.currentItem());
    
  def set_open_items (self,openspec):
    """sets currently open and selected items according to tree returned
    by a previous get_open_items() call.""";
    # recursive helper function implementing tree traversal
    def _set_open_items_impl (parent,openspec):
      select = None;
      if openspec is None:
        return None;
      (openitems,current_key) = openspec;
      for i in range(parent.childCount()):
        item = parent.child(i);
        if item._udi_key == current_key:
          select = item;
        # if item is open, expand it and go in recursively
        if item._udi_key in openitems:
          item.setExpanded(True);
          select = select or _set_open_items_impl(item,openitems[item._udi_key]);
      return select;
    # call recursive helper on listview, select returned item
    select = _set_open_items_impl(self._tw.invisibleRootItem(),openspec);
    if select:
      self._tw.setCurrentItem(select);
      self._tw.scrollToItem(select);
    
  def set_content (self,content):
    # expand first level of record
    self.clear();
    # call Item.expand_content() with our listview as the first argument,
    # since that method is universal for both Items an ListViews
    HierBrowser.Item.expand_content(self._tw,content);
    
  def change_item_content (self,item,content,keepopen=True,**kwargs):
    """changes content of an item. If keepopen=True and item was open,
    attempts to preserve open structure and selected items""";
    openitems = None;
    if item.isExpanded():
      openitems = (keepopen and self.get_open_items()) or None;
      item.setExpanded(False);
    item.cache_content(content,**kwargs);
    if openitems:
      self.set_open_items(openitems);
      
      
      
      
    
class GriddedPlugin (Grid.CellBlock):
  def __init__ (self,*args,**kw):
    Grid.CellBlock.__init__(self,*args,**kw);
  
  def icon (_class):
    """icon() should return a QIcon""";
    return _class._icon.icon();
  icon = classmethod(icon);
  
  # redefine this 
  viewer_name = "?";
  # and this
  _icon = pixmaps.viewmag;  # default icon
  
  
  
  
  
class TextBrowser(GriddedPlugin):
  _icon = pixmaps.text_left;
  viewer_name = "Text Browser";
  
  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    self._wtext = QTextBrowser(self.wparent());
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    if dataitem.data is not None:
      self.set_data(dataitem);
      
  def wtop (self):
    return self._wtext;
      
  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    self._wtext.setText(dataitem.data);
    
    
    
    
    
class RecordBrowser(HierBrowser,GriddedPlugin):
  _icon = pixmaps.view_tree;
  viewer_name = "Record Browser";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    HierBrowser.__init__(self,self.wparent(),"value","field",
        udi_root=dataitem.udi);
    # adjust columns when font changes
    QObject.connect(self.wtop(),PYSIGNAL("fontChanged()"),self._resize_sections);
    
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    self._rec = None;
    self._default_open = default_open;
    if dataitem.data is not None:
      self.set_data(dataitem);
    # add number format menu
    context_menu = self.cell_menu();
    if context_menu is not None:
      context_menu.addSeparator();
      _dprint(3,self.get_precision());
      menu = PrecisionPopupMenu(context_menu,prec=self.get_precision());
      qa = context_menu.addMenu(menu);
      qa.setIcon(pixmaps.precplus.icon());
      qa.setText('Number format');
      QWidget.connect(menu,PYSIGNAL("setPrecision()"),self._set_prec_from_menu);
    
  def _resize_sections (self):
    for section in (0,1):
      self.wtop().header().setResizeMode(section,QHeaderView.ResizeToContents);
  
  def _set_prec_from_menu (self,prec,format):
    self.set_precision((prec,format));
  
  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    # save currently open tree
    if self._rec is not None:
      openitems = self.get_open_items();
    else: # no data, use default open tree if specified
      openitems = default_open or self._default_open;
    # clear everything and reset data as new
    self.clear();
    self.set_udi_root(dataitem.udi);
    self._rec = dataitem.data;
    self._pprint = PrettyPrinter(width=78,stream=sys.stderr);
    self.set_refresh_func(dataitem.refresh_func);
    # expand first level of record
    self.set_content(self._rec);
    # apply saved open tree
    self.set_open_items(openitems);
    # enable & highlight the cell
    self.enable();
    self.flash_refresh();

# register the RecordBrowser as a viewer (pri=20) for the appropriate types
for tp in (dict,list,tuple,array_class):
  Grid.Services.registerViewer(tp,RecordBrowser,priority=20);

Grid.Services.registerViewer(str,TextBrowser,priority=20);

