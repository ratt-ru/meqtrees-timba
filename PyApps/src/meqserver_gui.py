#!/usr/bin/python

import meqserver
from app_proxy_gui import *
import app_pixmaps as pixmaps
import weakref

class NodeList (dict):
  NodeAttrs = ('name','class','children');
  class Node (object):
    def __init__ (self,ni):
      self.nodeindex = ni;
      self.name = None;
      self.classname = None;
      self.children = [];
      self.parents  = [];
      
  # initialize from a MEQ-produced nodelist
  def __init__ (self,meqnl):
    # check that all list fields are correct
    num = len(meqnl.nodeindex);
    for f in self.NodeAttrs:
      if f not in meqnl:
        raise ValueError,"bad nodelist record: missing "+f+" field";
      if len(meqnl[f]) != num:
        raise ValueError,"malformed nodelist record: len(%s)=%d, expected %d"%(f,len(meqnl[f]),num);
    # form sequence of iterators
    iter_name     = iter(meqnl.name);
    iter_class    = iter(meqnl['class']);
    iter_children = iter(meqnl.children);
    # iterate over all nodes in list
    for ni in meqnl.nodeindex:
      # insert node into list (or use old one: may have been inserted below)
      node = self.setdefault(ni,self.Node(ni));
      node.name      = iter_name.next();
      node.classname = iter_class.next();
      children  = iter_children.next();
      if isinstance(children,dict):
        node.children = tuple(children.iteritems());
      else:
        node.children = tuple(enumerate(children));
      # for all children, init node entry in list (if necessary), and
      # add ourselves to parent list
      for (i,ch_ni) in node.children:
        self.setdefault(ch_ni,self.Node(ch_ni)).parents.append(ni);
    # generate list of root nodes
    self._rootnodes = [];
    for (ni,node) in self.iteritems():
      if not node.parents:
        self._rootnodes.append(ni)
        
  # return list of root nodes
  def rootnodes (self):
    return self._rootnodes;

# return True if this is a valid NodeList
def is_valid_nodelist (nodelist):
  for f in ('nodeindex',) + NodeList.NodeAttrs:
    if f not in nodelist:
      return False;
  return True;
    

class TreeBrowser (object):
  def __init__ (self,parent,mqs):
    self._mqs = mqs;
    self._splitter = QSplitter(QSplitter.Horizontal,parent);
    self._nl_vbox = QVBox(self._splitter);
    self._nl_control = QWidget(self._nl_vbox);
    self._nl_control_lo = QHBoxLayout(self._nl_control);
    self._nl_control_lo.addStretch();
    # add refresh button
    self._nl_update = QPushButton(self._nl_control);
    self._nl_update.setIconSet(QIconSet(pixmaps.refresh.pm()));
    self._nl_control_lo.addWidget(self._nl_update);
    QObject.connect(self._nl_update,SIGNAL("clicked()"),self._request_nodelist);
    self._nlv = QListView(self._nl_vbox);
    self._nlv.addColumn('node');
    self._nlv.addColumn('class');
    self._nlv.addColumn('index');
    self._nlv.setRootIsDecorated(True);
    self._nlv.setTreeStepSize(12);
    # self._nlv.setSorting(-1);
    self._nlv.setResizeMode(QListView.NoColumn);
    for icol in range(4):
      self._nlv.setColumnWidthMode(icol,QListView.Maximum);
    self._nlv.setFocus();
    self._nlv.connect(self._nlv,SIGNAL('expanded(QListViewItem*)'),
                      self._expand_node);
    self.nodelist = None;
  
  def wtop (self):
    return self._splitter;
    
  def clear (self):
    self._nlv.clear();
  def connected (self,conn):
    self._nl_update.setDisabled(not conn);

  def _request_nodelist (self):
#    self._nl_update.setDisabled(True);
    self.nodelist = None;
    rec = srecord(dict.fromkeys(NodeList.NodeAttrs,True));
    rec.nodeindex = True;
    self._mqs.meq('Get.Node.List',rec,wait=False);
    
  def make_node_item (self,node,name,parent,after):
    item = QListViewItem(parent,after,name,' '+node.classname,' '+str(node.nodeindex));
    item._node = node;
    if node.children:
      item.setExpandable(True);
    return item;

  def update_nodelist (self,nodelist):
#    self._nl_update.setDisabled(False);
    if self.nodelist is None:
      # reset the nodelist view
      self._nlv.clear();
      all_item  = QListViewItem(self._nlv,"All Nodes");
      all_item._all_nodes = True;
      all_item.setExpandable(True);
      rootitem  = item = QListViewItem(self._nlv,all_item,"Root Nodes");
      rootitem._expanded = True;
      for ni in nodelist.rootnodes():
        node = nodelist[ni];
        item = self.make_node_item(node,node.name,rootitem,item);
      self._nlv.setOpen(rootitem,True);
      self.nodelist = nodelist;
    
  def _expand_node (self,item):
    # populate when first opened
    if not hasattr(item,'_expanded'):
      i1 = item;
      if hasattr(item,'_all_nodes'):
        for (ni,node) in self.nodelist.iteritems():
          i1 = self.make_node_item(node,node.name,item,i1);
      elif hasattr(item,'_node'):
        for (key,ni) in item._node.children:
          node = self.nodelist[ni];
          name = str(key) + ": " + node.name;
          i1 = self.make_node_item(node,name,item,i1);
        item._expanded = True;

class meqserver_gui (app_proxy_gui):

  def __init__(self,app,*args,**kwargs):
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    self.dprint(2,"meqserver-specifc init"); 
    
    # add Tree browser panel
    self.treebrowser = TreeBrowser(self,app);
    self.maintab.insertTab(self.treebrowser.wtop(),"MeqTrees",1);
    
    # add Result Log panel
    self.resultlog = Logger(self,"node result log",limit=100);
    self.maintab.insertTab(self.resultlog.wtop(),"Result Log",2);
    self.resultlog.wtop()._default_iconset = QIconSet();
    self.resultlog.wtop()._default_label   = "Result Log";
    self.resultlog.wtop()._newres_iconset  = QIconSet(pixmaps.check.pm());
    self.resultlog.wtop()._newres_label    = "New Results";
    self.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    # add handler for result log
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("hello",lambda x:x.treebrowser.clear() and x.treebrowser.connected(True));
    self._add_ce_handler("bye",lambda x:x.treebrowser.connected(False));
    
  def ce_NodeResult (self,ev,value):
    if self.resultlog.enabled:
      txt = '';
      name = ('name' in value and value.name) or '<unnamed>';
      cls  = ('class' in value and value['class']) or '?';
      rqid = 'request_id' in value and value.request_id;
      txt = ''.join((name,' <',cls,'>'));
      if rqid:
        txt = ''.join((txt,' rqid:',str(rqid)));
      self.resultlog.add(txt,value,Logger.Event);
      wtop = self.resultlog.wtop();
      if self.maintab.currentPage() is not wtop:
        self.maintab.changeTab(wtop,wtop._newres_iconset,wtop._newres_label);
        
  def ce_LoadNodeList (self,ev,nodelist):
    if is_valid_nodelist(nodelist):
      self.nodelist = NodeList(nodelist);
      self.dprintf(2,"loaded %d nodes into nodelist\n",len(self.nodelist));
      self.treebrowser.update_nodelist(self.nodelist);
    else:
      self.dprint(2,"got nodelist but it is not valid, ignoring");
  
      
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop():
      self._reset_maintab_label(tabwin);
  
