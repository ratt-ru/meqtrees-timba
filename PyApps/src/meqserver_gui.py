#!/usr/bin/python

import meqserver
from app_proxy_gui import *
from dmitypes import *
import app_pixmaps as pixmaps
import weakref
import math
import sets
import re

# ---------------- TODO -----------------------------------------------------
# Bugs:
#   Tree browser not always enabled! (Hello message lost??)
#
# Minor fixes:
#   Disorderly thread error or SEGV on exit
#   Why can't we exit with CTRL+C?
#   + Enable drop on "show viewer" button
#
# Enhancements:
#   Enable views/drags/drops of sub-items (i.e. "nodestate:name/cache_result")
#   Enhanced 'verbosity' interface (look for option parsing modules?)
#   User-defined node groups in tree viewer
#   Right-button actions
#   + Viewer plugin interface
#   + Update contents of HierBrowser on-the-fly, without closing expanded
#     sub-items (good for, e.g., node state updates)
#   + When looking at node state, open something useful by default (i.e.,
#     cache_result/vellsets/0 or smth)
#   + drag-and-drop
# ---------------------------------------------------------------------------

class NodeList (object):
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
    self._nimap = {};
    self._namemap = {};
    self._classmap = {};
    # iterate over all nodes in list
    for ni in meqnl.nodeindex:
      # insert node into list (or use old one: may have been inserted below)
      node = self._nimap.setdefault(ni,self.Node(ni));
      node.name      = iter_name.next();
      node.classname = iter_class.next();
      children  = iter_children.next();
      if isinstance(children,dict):
        node.children = tuple(children.iteritems());
      else:
        node.children = tuple(enumerate(children));
      # for all children, init node entry in list (if necessary), and
      # add to parent list
      for (i,ch_ni) in node.children:
        self._nimap.setdefault(ch_ni,self.Node(ch_ni)).parents.append(ni);
      # add to name map
      self._namemap[node.name] = node;
      # add to class map
      self._classmap.setdefault(node.classname,[]).append(node);
    # compose list of root (i.e. parentless) nodes
    self._rootnodes = [ node for node in self._nimap.itervalues() if not node.parents ];
  __init__ = busyCursorMethod(__init__);
  # return list of root nodes
  def rootnodes (self):
    return self._rootnodes;
  # return map of classes
  def classes (self):
    return self._classmap;
  def iteritems (self):
    return self._nimap.iteritems();
  def iternodes (self):
    return self._nimap.itervalues();
  # mapping methods
  def __len__ (self):
    return len(self._nimap);
  # helper method: selects name or nodeindex map depending on key type
  def _map_ (self,key):
    if isinstance(key,str):  return self._namemap;
    elif isinstance(key,int):   return self._nimap;
    else:                       raise TypeError,"invalid node key "+key;
  def __getitem__ (self,key):
    return self._map_(key).__getitem__(key);
  def __contains__ (self,key):
    return self._map_(key).__contains__(key);
  def __setitem__ (self,key,node):
    if __debug__:
      if isinstance(key,string):  assert value.name == key;
      elif isinstance(key,int):   assert value.nodeindex == key;
      else:                       raise TypeError,"invalid node key "+key;
    self._nimap[node.nodeindex] = self._namemap[node.name] = node;
  def __iter__(self):
    return iter(self._nimap);
   

# return True if this is a valid meqNodeList (i.e. node list object from meq kernel)
def is_valid_meqnodelist (nodelist):
  for f in ('nodeindex',) + NodeList.NodeAttrs:
    if f not in nodelist:
      return False;
  return True;
 
def makeNodeUdi (node):
  return "/nodestate/%s#%d"%(node.name,node.nodeindex);
    
class TreeBrowser (object):
  def __init__ (self,parent):
    self._parent = weakref.proxy(parent);
    # construct GUI
    nl_vbox = self._wtop = QVBox(parent);
    nl_control = QWidget(nl_vbox);
    nl_control_lo = QHBoxLayout(nl_control);
    # add refresh button
    self._nl_update = nl_update = QToolButton(nl_control);
    nl_update.setIconSet(QIconSet(pixmaps.refresh.pm()));
    nl_update.setAutoRaise(True);
    nl_update.setDisabled(True);
    QToolTip.add(nl_update,"refresh the node list");
    #    nl_update.setMinimumWidth(30);
    #    nl_update.setMaximumWidth(30);
    nl_control_lo.addWidget(nl_update);
    nl_label = QLabel("Tree Browser",nl_control);
    nl_control_lo.addWidget(nl_label);
    nl_control_lo.addStretch();
    QObject.connect(nl_update,SIGNAL("clicked()"),self._request_nodelist);
    # node list
    self._nlv = nlv = DataDraggableListView(nl_vbox);
    nlv.addColumn('node');
    nlv.addColumn('class');
    nlv.addColumn('index');
    nlv.setRootIsDecorated(True);
    nlv.setTreeStepSize(12);
    # nlv.setSorting(-1);
    nlv.setResizeMode(QListView.NoColumn);
    for icol in range(4):
      nlv.setColumnWidthMode(icol,QListView.Maximum);
    nlv.setFocus();
    nlv.connect(nlv,SIGNAL('expanded(QListViewItem*)'),self._expand_node);
    nlv.connect(nlv,SIGNAL('clicked(QListViewItem*)'),self._node_clicked);
    # map the get_data_item method
    nlv.get_data_item = self.get_data_item;
    
    self.nodelist = None;
    self._wait_nodestate = {};

  patt_Udi_NodeState = re.compile("^/nodestate/([^#/]*)(#[0-9]+)?$");
  def get_data_item (self,udi):
    match = self.patt_Udi_NodeState.match(udi);
    if match is None:
      return None;
    (name,ni) = match.groups();
    if ni is None:
      if not len(name):
        raise ValueError,'bad udi (either name or nodeindex must be supplied): '+udi;
      node = self.nodelist[name];
    else:
      try: 
        node = self.nodelist[int(ni[1:])];
      except ValueError: # can't convert nodeindex to int: malformed udi
        raise ValueError,'bad udi (nodeindex must be numeric): '+udi;
    # create and return dataitem object
    return self._parent.make_node_data_item(node);
 
  def wtop (self):
    return self._wtop;
    
  def clear (self):
    self._nlv.clear();
    
  def connected (self,conn):
    self._nl_update.setDisabled(not conn);

  def _request_nodelist (self):
#    self._nl_update.setDisabled(True);
    self.nodelist = None;
    rec = srecord(dict.fromkeys(NodeList.NodeAttrs,True));
    rec.nodeindex = True;
    self._parent.mqs.meq('Get.Node.List',rec,wait=False);
    
  def make_node_item (self,node,name,parent,after):
    item = QListViewItem(parent,after,name,' '+str(node.classname),' '+str(node.nodeindex));
    item.setDragEnabled(True);
    item._node = weakref.proxy(node);
    item._expanded = False;
    item._udi  = makeNodeUdi(node);
    if node.children:
      item.setExpandable(True);
    return item;

  def update_nodelist (self,nodelist):
#    self._nl_update.setDisabled(False);
    if self.nodelist is None:
      # reset the nodelist view
      self._nlv.clear();
      all_item  = QListViewItem(self._nlv,"All Nodes (%d)"%len(nodelist));
      all_item._iter_nodes = nodelist.iternodes();
      all_item.setExpandable(True);
      rootnodes = nodelist.rootnodes();
      rootitem  = QListViewItem(self._nlv,all_item,"Root Nodes (%d)"%len(rootnodes));
      rootitem._iter_nodes = iter(rootnodes);
      rootitem.setExpandable(True);
      classes = nodelist.classes();
      cls_item  = item = QListViewItem(self._nlv,rootitem,"By Class (%d)"%len(classes));
      for (cls,nodes) in classes.iteritems():
        item = QListViewItem(cls_item,item,"(%d)"%len(nodes),cls,"");
        item.setExpandable(True);
        item._iter_nodes = iter(nodes);
      self.nodelist = nodelist;
      
  def _node_clicked (self,item):
    if hasattr(item,'_node'):
      self.wtop().emit(PYSIGNAL("node_clicked()"),(item._node,));
  
  def _expand_node (self,item):
    i1 = item;
    # populate list when first opened, if an iterator is present as an attribute
    try: iter_nodes = item._iter_nodes;
    except: pass;
    else:
      for node in iter_nodes:
        i1 = self.make_node_item(node,node.name,item,i1);
      delattr(item,'_iter_nodes');
    # populate node children when first opened
    try: node = item._node;
    except: pass;
    else:
      if not item._expanded:
        for (key,ni) in item._node.children:
          node = self.nodelist[ni];
          name = str(key) + ": " + node.name;
          i1 = self.make_node_item(node,name,item,i1);
        item._expanded = True;
  _expand_node = busyCursorMethod(_expand_node);

class meqserver_gui (app_proxy_gui):
  def __init__(self,app,*args,**kwargs):
    self.mqs = app;
    self.mqs.track_results(False);
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    # add handlers for result log
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("app.result.node.get.state",self.ce_NodeState);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("hello",self.ce_mqs_Hello);
    self._add_ce_handler("bye",self.ce_mqs_Bye);
    
    self._wait_nodestate = {};
    
  def populate (self,main_parent=None,*args,**kwargs):
    app_proxy_gui.populate(self,main_parent=main_parent,*args,**kwargs);
    dbg.set_verbose(self.get_verbose());
    self.dprint(2,"meqserver-specifc init"); 
    # add workspace
    
    # add Tree browser panel
    self.treebrowser = TreeBrowser(self);
    self.maintab.insertTab(self.treebrowser.wtop(),"Trees",1);
    self.connect(self.treebrowser.wtop(),PYSIGNAL("node_clicked()"),self._node_clicked);
    
    # add Result Log panel
    self.resultlog = Logger(self,"node result log",limit=1000,
          click=self._process_logger_item_click,udi_root='noderes');
    self.maintab.insertTab(self.resultlog.wtop(),"Results",2);
    self.resultlog.wtop()._default_iconset = QIconSet();
    self.resultlog.wtop()._default_label   = "Results";
    self.resultlog.wtop()._newres_iconset  = QIconSet(pixmaps.check.pm());
    self.resultlog.wtop()._newres_label    = "Results";
    self.resultlog.wtop()._newresults      = False;
    self.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    
  def ce_mqs_Hello (self,ev,value):
    self.treebrowser.clear();
    self.treebrowser.connected(True);  
    self.resultlog.clear();
    wtop = self.resultlog.wtop();
    self.maintab.changeTab(wtop,wtop._default_iconset,wtop._default_label);
    
  def ce_mqs_Bye (self,ev,value):
    app_proxy_gui.ce_Hello(self,ev,value);
    self.treebrowser.connected(False);  
    
  def ce_NodeState (self,ev,value):
    if hasattr(value,'name'):
      self.dprint(5,'got state for node ',value.name);
      self.update_node_state(value);
  
  defaultResultViewopts = { \
    'default_open': ({'cache_result':({'vellsets':None},None)},None)  \
  };
  def ce_NodeResult (self,ev,value):
    self.update_node_state(value);
    if self.resultlog.enabled:
      txt = '';
      name = ('name' in value and value.name) or '<unnamed>';
      cls  = ('class' in value and value['class']) or '?';
      rqid = 'request_id' in value and str(value.request_id);
      txt = ''.join((name,' <',cls,'>'));
      desc = 'result';
      if rqid:
        txt = ''.join((txt,' rqid:',rqid));
        desc = desc + ':' + rqid;
      self.resultlog.add(txt,content=value,category=Logger.Event, 
        name=name,desc=desc,viewopts=self.defaultResultViewopts);
      wtop = self.resultlog.wtop();
      if self.maintab.currentPage() is not wtop and not wtop._newresults:
        self.maintab.changeTab(wtop,wtop._newres_iconset,wtop._newres_label);
        wtop._newresults = True;
        
  def ce_LoadNodeList (self,ev,nodelist):
    try:
      self.nodelist = NodeList(nodelist);
    except ValueError:
      self.dprint(2,"got nodelist but it is not valid, ignoring");
      return;
    self.dprintf(2,"loaded %d nodes into nodelist\n",len(self.nodelist));
    self.treebrowser.update_nodelist(self.nodelist);
      
  def update_node_state (self,node):
    udi = makeNodeUdi(node);
    self.gw.update_data_item(udi,node);
    
  defaultNodeViewopts = { \
    'default_open': ({'cache_result':({'vellsets':None},None), \
                      'request':None \
                     },None)  \
  };
  def make_node_data_item (self,node):
    """creates a GridDataItem for a node""";
    # create and return dataitem object
    reqrec = srecord(nodeindex=node.nodeindex);  # record used to request state
    udi = makeNodeUdi(node);
    # curry is used to create a Node.Get.State call for refreshing its state
    return GridDataItem(udi,(node.name or '#'+str(node.nodeindex)),
              desc='node state',datatype=srecord,
              refresh=curry(self.mqs.meq,'Node.Get.State',reqrec,wait=False),
              viewopts=self.defaultNodeViewopts);
    

  def _node_clicked (self,node):
    self.dprint(2,"node clicked, adding item");
    self.gw.add_data_item(self.make_node_data_item(node));
    self.show_gridded_workspace();
    
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop() and tabwin._newresults:
      self._reset_maintab_label(tabwin);
    tabwin._newresults = False;
