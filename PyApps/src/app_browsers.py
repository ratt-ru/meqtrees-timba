#!/usr/bin/python

from qt import *
from qttable import *
from dmitypes import *
import sys
import time
import qt_threading
import app_pixmaps as pixmaps
import dmi_repr
import gridded_workspace 
import weakref

dmirepr = dmi_repr.dmi_repr();

# helper class implementing a 'Precision' menu
class PrecisionPopupMenu (QPopupMenu):
  def_range = range(0,16);
  def_prec  = 99;

  def __init__ (self,parent=None,precrange=None,prec=None):
    QPopupMenu.__init__(self,parent);
    self._precrange = precrange or self.def_range;
    self.insertItem('Default',self.def_prec);
    for p in self._precrange:
      self.insertItem(str(p),p);
    self._prec = prec;
    self.setItemChecked((prec is None and self.def_prec) or prec,True);
    QWidget.connect(self,SIGNAL("activated(int)"),self.set);
    
  def set (self,prec):
    if prec == self.def_prec:
      prec = None;
    self._prec = prec;
    self.setItemChecked(self.def_prec,prec is None);
    for p in self._precrange:
      self.setItemChecked(p,p==prec);
    self.emit(PYSIGNAL("setPrecision()"),(prec,));

  def get (self):
    return self._prec;    
  

class HierBrowser (object):
  # seqs/dicts with <= items than this are treated as "short"
  ShortSeq       = 5;
  # maximum number of sequence items to show in expanded view
  MaxExpSeq      = 20;
  # max number of dictionary items to show in expanded view
  MaxExpDict     = 100;
  
  class Item (QListViewItem):
    def __init__(self,parent,key,value,udi_key=None,udi=None,strfunc=None,
                 prec=None,name=None,desc=''):
#      print args;
      # insert item at end of parent's content list (if any)
      parent_content = getattr(parent,'_content_list',None);
      if parent_content:
        QListViewItem.__init__(self,parent,parent_content[-1],str(key),'',str(value));
        parent_content.append(self);
      else:
        QListViewItem.__init__(self,parent,str(key),'',str(value));
        parent._content_list = [self];
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
          udi_key = str(id(self));
        elif udi_key is None:
          udi_key = key;
        self._udi_key = udi_key;
        # setup udi of self, if parent self has a udi of its own
        # add ourselves to content map and propagate the map
        if parent._udi:
          self._udi = '/'.join((parent._udi,udi_key));
        else:
          self._udi = None;
      # add to content map, if we have a UDI
      if self._udi:
        self.listView()._content_map[self._udi] = self;
      # set name and/or description
      self._name     = name or self._udi or str(key);
      self._desc     = desc;
      # other state
      self._curries  = [];
      
    def set_udi (self,udi):
      self.listView()._content_map[udi] = self;
      self._udi = udi;
      
    # caches content in an item: marks as expandable, ensures content is a dict
    # if viewable is None, decides if content is viewable based on its type
    # else, must be True or False to specify viewability explicitly
    def cache_content(self,content,viewable=None,viewopts={},make_data=None):
      self.setExpandable(True);
      # if already have content, remove it (remove all children)
      try: delattr(self,'_content');
      except: pass;
      try: delattr(self,'_content_list');
      except: pass;
      i1 = self.firstChild(); 
      while i1:
        inext = i1.nextSibling();
        self.takeItem(i1);
        i1 = inext;
      # convert all content to dict
      if isinstance(content,(dict,list,tuple,array_class)):
        self._content = content;
      elif isinstance(content,message):
        self._content = {};
        for k in filter(lambda x:not x.startswith('_'),dir(content)):
          attr = getattr(content,k);
          if not callable(attr):
            self._content[k] = attr;
      else:
        self._content = {"":content};
      # set the viewable property
      if not self._udi:
        viewable = False;
      elif viewable is None:
        viewable = gridded_workspace.isViewable(content);
      self._viewable = viewable;
      if viewable:
        self._viewopts = viewopts;
        self.setPixmap(1,pixmaps.magnify.pm());
        self.setDragEnabled(True);
      # set the make_data property
      self._make_data = make_data;
        
    # helper static method to expand content into Items record 
    # note that we make this a static method because 'item' may in fact be
    # a parent QListView
    def expand_content(item,content):
      # content_list attribute is initialized upon expansion
      if hasattr(item,'_content_list'):
        return;
      item._content_list = [];
      # Setup content_iter as an iterator that returns (label,value)
      # pairs, depending on content type.
      # Apply limits here
      if isinstance(content,dict):
        n = len(content) - HierBrowser.MaxExpDict;
        if n > 0:
          keys = content.keys()[:HierBrowser.MaxExpDict];
          content_iter = map(lambda k:(k,content[k]),keys);
          content_iter.append(('...','...(%d items skipped)...'%n));
        else:
          content_iter = content.iteritems();
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
          i0 = HierBrowser.Item(item,key,itemstr,strfunc=\
                  curry(dmirepr.inline_str,value));
          item._content_list.append(i0);
          continue;
        # else get string representation, insert item with it
        (itemstr,inlined) = dmirepr.expanded_repr_str(value,False);
        i0 = HierBrowser.Item(item,str(key),itemstr,strfunc=\
                  curry(dmirepr.expanded_repr_str,value,False));
        item._content_list.append(i0);
        # cache value for expansion, if not inlined
        if isinstance(value,(list,tuple,array_class)):
          if not inlined:
            i0.cache_content(value);
        # dicts and messages always cached for expansion
        elif isinstance(value,(dict,message)):
          i0.cache_content(value);
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
        refresh = getattr(self.listView(),'_refresh_func',None);
        # make item and return
        return gridded_workspace.GridDataItem(self._udi,name,desc,
                  data=self._content,viewer=viewer,viewopts=vo,
                  refresh=refresh);
      return None;

    def get_precision (self):
      return self._prec;
      
    prec_range = range(0,16);
    prec_default = 99;
      
    # changes display precision of item
    def set_precision (self,prec,set_menu=True):
      print 'set_precision',prec;
      self._prec = prec;
      if callable(self._strfunc):
        (txt,inlined) = self._strfunc(prec=prec);
        self.setText(2,txt);
      # set menu checkmark, if any
      if set_menu and self._prec_menu:
        self._prec_menu.set(prec);
    
    def _set_prec_frommenu (self,prec):
      self.set_precision(prec,set_menu=False);
 
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

    def get_context_menu (self):
      try: menu = self._context_menu;
      except AttributeError:
        # create menu on the fly when first called for this item
        viewer_list = self._content is not None and self._viewable and \
                   gridded_workspace.getViewerList(self._content);
        # no menu for this item if not viewable or refreshable
        if not ( self._strfunc or viewer_list ):
          self._context_menu = None;
          return None;
        # create menu
        menu = self._context_menu = QPopupMenu();
        menu._callbacks = [];
        menu.insertItem(' '.join((self._name,self._desc)));
        menu.insertSeparator();
        # create "Precision" submenu
        if self._strfunc:
          self._prec_menu = PrecisionPopupMenu(prec=self._prec);
          menu.insertItem(pixmaps.precplus.iconset(),'Precision',self._prec_menu);
          QWidget.connect(self._prec_menu,PYSIGNAL("setPrecision()"),
                          self._set_prec_frommenu);
        # create "display with" entries
        if viewer_list: 
          # create display submenus
          menu1 = self._display_menu1 = QPopupMenu();
          menu2 = self._display_menu2 = QPopupMenu();
          menu.insertItem(pixmaps.view_split.iconset(),"Display with",menu1);
          menu.insertItem(pixmaps.view_right.iconset(),"New display with",menu2);
          for v in viewer_list:
            # create entry for viewer
            name = getattr(v,'viewer_name',v.__name__);
            try: icon = v.icon();
            except AttributeError: icon = QIconSet();
            # add entry to both menus ("Display with" and "New display with")
            menu1.insertItem(icon,name, \
              self.xcurry(self.emit_display_signal,viewer=v,_argslice=slice(0)));
            menu2.insertItem(icon,name, \
              self.xcurry(self.emit_display_signal,viewer=v,newcell=True,_argslice=slice(0)));
      # set the precision submenu to the right setting
      return menu;
      
    # if item is displayable, creates a dataitem from it and
    # emits a displayDataItem(dataitem,(),kwargs) signal
    def emit_display_signal (self,viewer=None,**kwargs):
      dataitem = self.make_data_item(viewer=viewer);
      if dataitem:
        self.listView().emit(PYSIGNAL("displayDataItem()"),(dataitem,(),kwargs));

  # init for HierBrowser
  def __init__(self,parent,name,name1='',udi_root=None):
    self._lv = gridded_workspace.DataDraggableListView(parent);
    self._lv.addColumn(name1);
    self._lv.addColumn('');
    self._lv.addColumn(name);
    self._lv.setRootIsDecorated(True);
    self._lv.setSorting(-1);
    self._lv.setResizeMode(QListView.NoColumn);
#    for col in (0,1,2):
#      self._lv.setColumnWidthMode(col,QListView.Maximum);
    self._lv.setFocus();
    self._lv.connect(self._lv,SIGNAL('expanded(QListViewItem*)'),
                     self._expand_item_content);
    self._lv.connect(self._lv,SIGNAL('mouseButtonClicked(int,QListViewItem*,const QPoint &,int)'),
                     self._process_item_click);
    self._lv.connect(self._lv,SIGNAL('contextMenuRequested(QListViewItem*,const QPoint &,int)'),
                     self._show_context_menu);
#    self._lv.connect(self._lv,SIGNAL('doubleClicked(QListViewItem*)'),
#                     self.display_item);
    # connect the get_data_item method for drag-and-drop
    self._lv.get_data_item = self.get_data_item;
    # this serves as a list of active items.
    # Populated in Item constructor, and also used by apply_limit, etc.
    self._lv._content_list = [];
    # enable UDIs, if udi root is not none
    self.set_udi_root(udi_root);
    # for debugging purposes
    QWidget.connect(self._lv,SIGNAL("clicked(QListViewItem*)"),self._print_item);
    
  def set_refresh_func (self,refresh):
    self._lv._refresh_func = refresh;
    
  def set_udi_root (self,udi_root):
    self._udi_root = udi_root;
    if udi_root is not None:
      if not udi_root.startswith('/'):
        udi_root = "/" + udi_root;
      self._lv._udi = udi_root;
      # map of UDIs to items
      self._lv._content_map = weakref.WeakValueDictionary();
    else:
      self._lv._udi = None;
    
  def _print_item (self,item):
    if item is not None:
      print 'item:',item.text(0),item.text(2);
      for attr in ('_udi','_udi_key','_viewable','_name','_desc'):
        if hasattr(item,attr):
          print ' ',attr+':',getattr(item,attr);
      try: 
        lencont = len(item.listView()._content_map);
        print '  _content_map: ',lencont,' items';
      except AttributeError: pass;
    
  def get_data_item (self,udi):
    item = self._lv._content_map.get(udi,None);
    return item and item.make_data_item();
    
  def wlistview (self):
    return self._lv;
  def wtop (self):
    return self._lv;
  def clear (self):
    self._lv.clear();
    for attr in ('_content','_content_list'):
      try: delattr(self._lv,attr);
      except: pass;

  # limits browser to last 'limit' items
  def apply_limit (self,limit):
    try: items = self._lv._content_list;
    except AttributeError: 
      return
    if limit>0 and len(items) > limit:
      for i in items[:len(items)-limit]:
        self._lv.takeItem(i);
      del items[:len(items)-limit];

  # called when an item is expanded                    
  def _expand_item_content (self,item):
    item.expand_self();

  # slot: called when one of the items is clicked
  def _process_item_click (self,button,item,point,col):
    if button == 1 and col == 1:
      item.emit_display_signal();
      
  # slot: called to show a context menu for an item
  def _show_context_menu (self,item,point,col):
    menu = item.get_context_menu();
    if menu is not None:
      menu.exec_loop(point);

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
      item = parent.firstChild();
      while item is not None:
        if item is current:
          current_key = item._udi_key;
        if item.isOpen():
          openitems[item._udi_key] = _get_open_items_impl(item,current);
        item = item.nextSibling();
      if openitems or current_key:
        return (openitems,current_key);
      return None;
    return _get_open_items_impl(self._lv,self._lv.currentItem());
    
  def set_open_items (self,openspec):
    """sets currently open and selected items according to tree returned
    by a previous get_open_items() call.""";
    # recursive helper function implementing tree traversal
    def _set_open_items_impl (parent,openspec):
      if openspec is None:
        return;
      (openitems,current_key) = openspec;
      item = parent.firstChild();
      while item is not None:
        if item._udi_key == current_key:
          self._lv.setCurrentItem(item);
        # if item is open, expand it and go in recursively
        if item._udi_key in openitems:
          self._lv.setOpen(item,True);
          _set_open_items_impl(item,openitems[item._udi_key]);
        item = item.nextSibling();
    # call recursive helper on listview
    _set_open_items_impl(self._lv,openspec);
    
  def change_item_content (self,item,content,keepopen=True,**kwargs):
    """changes content of an item. If keepopen=True and item was open,
    attempts to preserve open structure""";
    openitems = None;
    if item.isOpen():
      openitems = (keepopen and self.get_open_items()) or None;
      item.setOpen(False);
    print openitems;
    item.cache_content(content,**kwargs);
    if openitems:
      self.set_open_items(openitems);
    
class BrowserPlugin (object):
  _icon = pixmaps.magnify;  # default icon
  def icon (_class):
    return _class._icon.iconset();
  icon = classmethod(icon);
  
  def viewer_name (_class):
    return getattr(_class,'_name',_class.__name__);
  viewer_name = classmethod(viewer_name);
    
class RecordBrowser(HierBrowser,BrowserPlugin):
  _icon = pixmaps.view_tree;
  viewer_name = "Record Browser";
  def is_viewable (data):
    return len(data) > 0;
  is_viewable = staticmethod(is_viewable);

  def __init__(self,parent,dataitem=None,default_open=None,**opts):
    HierBrowser.__init__(self,parent,"value","field",
        udi_root=(dataitem and dataitem.udi));
    self._rec = None;
    self._default_open = default_open;
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);
  
  def set_data (self,dataitem,default_open=None,**opts):
    # save currenty open tree, if nothing is open, try to use default
    openitems = self.get_open_items() or default_open or self._default_open;
    # clear everything and reset data as new
    self.clear();
    self.set_udi_root(dataitem.udi);
    self._rec = dataitem.data;
    self.set_refresh_func(dataitem.refresh_func);
    # expand first level of record
    HierBrowser.Item.expand_content(self._lv,self._rec);
    # apply saved open tree
    self.set_open_items(openitems);
    
class ArrayBrowser(BrowserPlugin):
  _icon = pixmaps.matrix;
  viewer_name = "Array Browser";
  def is_viewable (data):
    try: return 1 <= data.rank <=2;
    except: return False;
  is_viewable = staticmethod(is_viewable);
  
  class ArrayTable(QTable):
    def __init__(self,parent,**args):
      QTable.__init__(self,parent,*args);
      self.setSelectionMode(QTable.NoSelection);
      self._arr = None;
      self._prec = None;
    # changes content
    def set_array (self,arr):
      if not 1<=arr.rank<=2:
        raise TypeError,"illegal array dimensionality";
      self._arr = arr;
      self._rank = arr.rank;
      self.setNumRows(arr.shape[0]);
      if self._rank == 1:   
        self.setNumCols(1);
      else:
        self.setNumCols(arr.shape[1]);
      self.repaint_cells();
    # changes precision
    def set_precision (self,prec):
      print 'table set prec',prec;
      self._prec = prec;
      self.repaint_cells();
      
    def repaint_cells (self):
      for col in range(self.columnAt(0),self.columnAt(self.width())+1):
        for row in range(self.rowAt(0),self.rowAt(self.height())+1):
          self.updateCell(row,col);
      
    # redefine paintCell method to paint on-the-fly
    def paintCell(self,painter,row,col,cr,selected):
      (txt,inline) = dmirepr.inline_str(self._arr[(row,col)[:self._rank]],prec=self._prec);
      if txt is None:
        txt = '';
      cg = QApplication.palette().active();
#      if selected:
#        qp.setPen(cg.highlightedText());
#        qp.setBackgroundColor(cg.highlight());
#      else:
#        qp.setPen(cg.text());
#        qp.setBackgroundColor(cg.background());
      rect = QRect(0,0,cr.width(),cr.height());
      if selected:
        painter.fillRect(rect,QBrush(cg.highlight()));
        painter.setPen(cg.highlightedText());
      else:
        painter.fillRect(rect,QBrush(cg.base()));
        painter.setPen(cg.text());
      painter.drawText(0,0,cr.width(),cr.height(),Qt.AlignLeft,txt);
      
    def resizeData(self,len):
      pass;
    
  def __init__(self,parent,dataitem=None,context_menu=None,**opts):
#    HierBrowser.__init__(self,parent,"value","field",
#        udi_root=(dataitem and dataitem.udi));
    self._arr = None;
    self._tbl = self.ArrayTable(parent);
    if dataitem and dataitem.data is not None:
      self.set_data(dataitem);
    if context_menu is not None:
      context_menu.insertSeparator();
      menu = PrecisionPopupMenu(parent);
      context_menu.insertItem(pixmaps.precplus.iconset(),'Precision',menu);
      QWidget.connect(menu,PYSIGNAL("setPrecision()"),\
                      self._tbl.set_precision);
      
  def wtop (self):
    return self._tbl;
  
  def set_data (self,dataitem,**opts):
    # save currenty open tree
#    if self._arr:
#      openitems = self.get_open_items();
#    else: # no data, use default open tree if specified
#      openitems = default_open or self._default_open;
    # clear everything and reset data as new
    self._tbl.set_array(dataitem.data);
    # apply saved open tree
#    self.set_open_items(openitems);
    

class ResultBrowser(RecordBrowser,BrowserPlugin):
  _icon = pixmaps.areas3d;
  viewer_name = "Result Browser";

# register the RecordBrowser as a viewer for the appropriate types
for tp in (dict,list,tuple,array_class):
  gridded_workspace.registerViewer(tp,RecordBrowser);
gridded_workspace.registerViewer(dict,ResultBrowser,dmitype='meqresult',priority=-10);
gridded_workspace.registerViewer(array_class,ArrayBrowser,priority=-5);

# import the array plotter plug-in
try:
  __import__('array_plotter',globals(),locals(),[]);
except ImportError,what:
  print 'error importing array_plotter module:',what;
  print 'Array Plotter will not be available.';

