#!/usr/bin/python

from qt import *
from dmitypes import *
import sys
import time
import qt_threading
import app_pixmaps as pixmaps
import dmi_repr
import gridded_workspace 

dmirepr = dmi_repr.dmi_repr();

class HierBrowser (object):
  # seqs/dicts with <= items than this are treated as "short"
  ShortSeq       = 5;
  # maximum number of sequence items to show in expanded view
  MaxExpSeq      = 20;
  # max number of dictionary items to show in expanded view
  MaxExpDict     = 100;
  
  class BrowserItem (QListViewItem):
    def __init__(self,*args):
#      print args;
      QListViewItem.__init__(self,*args);

    def _subitem (self,*args):
      return HierBrowser.subitem(self,*args);
      
    # caches content in an item: marks as expandable, ensures content is a dict
    def cache_content(self,content,viewable=False):
      self.setExpandable(True);
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
      self._viewable = viewable;
      if viewable:
        self.setPixmap(1,pixmaps.magnify.pm());
        
    # expands item content into subitems
    def expand_self (self):
      HierBrowser.expand_content(self,self._content);

  # init for HierBrowser
  def __init__(self,parent,name,name1=''):
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
    self.items = [];

    # expands item content into subitems
    def expand_self (self):
      HierBrowser.expand_content(self,self._content);
    
  def subitem (parent,key,value):
    if hasattr(parent,'_content_list') and parent._content_list:
      return HierBrowser.BrowserItem(parent,parent._content_list[-1],str(key),'',str(value));
    else:
      return HierBrowser.BrowserItem(parent,str(key),'',str(value));
  subitem = staticmethod(subitem);
    
  # helper static method to expand content into BrowserItems record 
  def expand_content(item,content):
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
      (itemstr,inlined) = dmirepr.inline_str(value);
      if itemstr is not None:
        item._content_list.append( HierBrowser.subitem(item,key,itemstr) );
        continue;
      # else get string representation, insert item with it
      (itemstr,inlined) = dmirepr.expanded_repr_str(value,False);
      i0 = HierBrowser.subitem(item,str(key),itemstr);
      item._content_list.append(i0);
      # cache value for expansion, if not inlined
      if isinstance(value,(list,tuple,dict,array_class)):
        if not inlined:
          i0.cache_content(value);
      elif isinstance(value,message):
        i0.cache_content(value);
      item._content_list.append(i0);
  expand_content = staticmethod(expand_content);
  
  def wlistview (self):
    return self._lv;
  def wtop (self):
    return self._lv;
  def clear (self):
    self._lv.clear();
    self.items = [];
    for attr in ('_content','_content_list'):
      if hasattr(self._lv,attr):
        delattr(self._lv,attr);
  # inserts a new item into the browser
  def new_item (self,key,value):
    if self.items:
      item = self.BrowserItem(self._lv,self.items[-1],str(key),'',str(value));
    else:
      item = self.BrowserItem(self._lv,str(key),'',str(value));
    self.items.append(item);
    self._lv.ensureItemVisible(item);
    return item;
  # limits browser to last 'limit' items
  def apply_limit (self,limit):
    if limit>0 and len(self.items) > limit:
      for i in self.items[:len(self.items)-limit]:
        self._lv.takeItem(i);
      del self.items[:len(self.items)-limit];
  # called when an item is expanded                    
  def _expand_item_content (self,item):
    item.expand_self();
    
class RecordBrowser(HierBrowser):
  def __init__(self,parent,rec=None,udi=None):
    HierBrowser.__init__(self,parent,"value","field");
    if rec is not None:
      self.set_record(rec);
  def set_record (self,rec):
    self.clear();
    self._rec = rec;
    # expand first level of record
    self.expand_content(self._lv,self._rec);
  set_data = set_record;
    
    
