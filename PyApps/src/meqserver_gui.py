#!/usr/bin/python

import meqserver
from app_proxy_gui import *
from dmitypes import *
import app_pixmaps as pixmaps
import weakref
import math
import sets
import re
import meqds
import app_browsers 
from app_browsers import *
from treebrowser import TreeBrowser

_dbg = verbosity(3,name='meqgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# global symbol: meqserver object; initialized when a meqserver_gui
# is constructed
mqs = None;

# ---------------- TODO -----------------------------------------------------
# Bugs:
#   Tree browser not always enabled! (Hello message lost??)
#   + In dmi_repr, array stats do not always use the right func
#   + Numarray indexing order is different! fixed converter
#   + Refresh of tree view with an empty forest list throws exception
#
# Minor fixes:
#   Create viewers as children of some widget (maybe a stack, again?) that
#     can be thrown out on exception together with any unclean children.
#   Do not compare result records, only state updates (and only if too recent)
#   Improve result labels, name them snapshots
#   Disorderly thread error or SEGV on exit
#   Why can't we exit with CTRL+C?
#   + Disallow drag-and-drop from a viewer onto the same cell
#   + Fix comparison of records and snapshots in Node Browser
#   + Enable drop on "show viewer" button
#
# Enhancements:
#   When first switching to the Trees panel, and have connection, and no nodelist
#     is loaded, request one
#   When getting node list, include debug status if we have one. Perhaps expand
#     the get node list into a full status call?
#   If all nodes are de-published, notify the browser somehow   
#   Context menu for Tree Browser
#   Option to specify udi directly in HierBrowser
#   Drop of a dataitem can create a cell with multiple items (think,
#       e.g., several 1D plots), if the viewer object supports it.
#   User-defined node groups in tree viewer
#   + Enhanced 'verbosity' interface (look for option parsing modules?)
#   + Right-button actions
#   + Enable views/drags/drops of sub-items (i.e. "nodestate:name/cache_result")
#   + Viewer plugin interface
#   + Update contents of HierBrowser on-the-fly, without closing expanded
#     sub-items (good for, e.g., node state updates)
#   + When looking at node state, open something useful by default (i.e.,
#     cache_result/vellsets/0 or smth)
#   + drag-and-drop
# ---------------------------------------------------------------------------

class NodeBrowser(HierBrowser,BrowserPlugin):
  _icon = pixmaps.treeviewoblique;
  viewer_name = "Node Browser";
  
  def __init__(self,parent,dataitem=None,default_open=None,**opts):
    HierBrowser.__init__(self,parent,"value","field",
        udi_root=(dataitem and dataitem.udi));
    # parse the udi
    (name,ni) = meqds.parse_node_udi(dataitem.udi);
    if ni is None:
      node = meqds.nodelist[name or dataitem.data.name];
    else:
      node = meqds.nodelist[ni];
    self._default_open = default_open;
    self._state = None;
    # at this point, _node is a very basic node record: all it has is a list
    # of children nodeindices, to which we'll dispatch update requests
    # construct basic view items
    lv = self.wlistview();
    self.set_udi_root(dataitem.udi);
    # Node state
    self._item_state = HierBrowser.Item(lv,'Current state','',udi=dataitem.udi,udi_key='state');
    # Node children
    # note that dataitem.data may be a node state or a node stub record,
    # depending on whether it is already available to us, so just to make sure
    # we always go back to meqds for the children list
    if len(node.children):
      childroot = HierBrowser.Item(lv,'Children (%d)'%len(node.children),'',udi_key='child');
      self._child_items = {};
      for (cid,child) in node.children: 
        # this registers out callback for whenever a child's state is sent over
        meqds.subscribe_node_state(child,self.set_child_state);
        # this initiates a state request for the child
        meqds.request_node_state(child);
        # create a listview item for that child
        self._child_items[child] = HierBrowser.Item(childroot,str(cid),'#'+str(child));
    else:
      self._child_items = None;
    # State snapshots
    meqds.subscribe_node_state(ni,self.set_own_state);
    sslist = meqds.get_node_snapshots(ni);
    self._item_snapshots = HierBrowser.Item(lv,'','',udi_key='snapshot');
    self._last_snapshot = None;
    nss = 0;
    for (stateref,event,timestamp) in sslist:
      st = stateref();
      if st is not None:
        item = HierBrowser.Item(self._item_snapshots, \
                time.strftime('%H:%M:%S',time.localtime(timestamp)),\
                str(event),udi_key=str(nss));
        item.cache_content(st);
        nss += 1;
    self._item_snapshots.setText(0,'Snapshots (%d)'%nss);
    # If we already have a full state record, go use it
    # Note that this will not always be the case; in the general case,
    # the node state will arrive later (perhaps even in between child
    # states)
    if dataitem.data is not None:
      self.set_data(dataitem);
    lv.setCurrentItem(None);

  # our own state is added to snapshots here (and to the main view
  # in set_data below)
  def set_own_state (self,state,event):
    if state is self._last_snapshot or getattr(state,'__nochange',False):
      return;
    # add snapshot
    nss = self._item_snapshots.childCount();
    item = HierBrowser.Item(self._item_snapshots, \
           time.strftime('%H:%M:%S'),str(event),udi_key=str(nss));
    item.cache_content(state);
    self._last_snapshot = state;
    # change label on snapshots item
    self._item_snapshots.setText(0,'Snapshots (%d)'%(nss+1));
      
  # this callback is registered for all child node state updates
  def set_child_state (self,node,event):
    _dprint(3,'Got state for child',node.name,node.field_names());
    _dprint(3,'Event is',event);
    if not self._child_items:
      raise RuntimeError,'no children expected for this node';
    item = self._child_items.get(node.nodeindex,None);
    if not item:
      raise ValueError,'this is not our child';
    # store node name in item
    item.setText(2,"%s (%s)"%(node.name,node['class'].lower()));
    item.set_udi(meqds.node_udi(node));
    self.change_item_content(item,node,\
      make_data=curry(makeNodeDataItem,node));
    
  def set_data (self,dataitem,default_open=None,**opts):
    # open items (use default first time round)
    openitems = default_open or self._default_open;
    if self._state is not None:
      # do nothing if state has already been marked as unchanged
      if getattr(dataitem.data,'__nochange',False):
        return;
      # if something is already open, use that
      openitems = self.get_open_items() or openitems;
    # at this point, dataitem.data is a valid node state record
    _dprint(3,'Got state for node',dataitem.data.name,dataitem.data.field_names());
    self.change_item_content(self._item_state,dataitem.data,viewable=False);
    # apply saved open tree
    self.set_open_items(openitems);
    self._state = dataitem.data;


class meqserver_gui (app_proxy_gui):
  def __init__(self,app,*args,**kwargs):
    meqds.set_meqserver(app);
    global mqs;
    self.mqs = mqs = app;
    self.mqs.track_results(False);
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    # add handlers for result log
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("debug.stop",self.ce_DebugStop);
    self._add_ce_handler("app.result.node.get.state",self.ce_NodeState);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("hello",self.ce_mqs_Hello);
    self._add_ce_handler("bye",self.ce_mqs_Bye);
    
  def populate (self,main_parent=None,*args,**kwargs):
    app_proxy_gui.populate(self,main_parent=main_parent,*args,**kwargs);
    self.set_verbose(self.get_verbose());
    _dprint(2,"meqserver-specifc init"); 
    # add Tree browser panel
    self.treebrowser = TreeBrowser(self);
    self.maintab.insertTab(self.treebrowser.wtop(),"Trees",1);
    self.connect(self.treebrowser.wtop(),PYSIGNAL("view_node()"),self._view_node);
    
    # add Result Log panel
    self.resultlog = Logger(self,"node result log",limit=1000,
          udi_root='noderes');
    self.maintab.insertTab(self.resultlog.wtop(),"Results",2);
    self.resultlog.wtop()._default_iconset = QIconSet();
    self.resultlog.wtop()._default_label   = "Results";
    self.resultlog.wtop()._newres_iconset  = pixmaps.check.iconset();
    self.resultlog.wtop()._newres_label    = "Results";
    self.resultlog.wtop()._newresults      = False;
    QWidget.connect(self.resultlog.wlistview(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QWidget.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    
    # excluse ubiquotous events from the event logger
    self.eventlog.add_exclusion('node.status');


  def _checkStateUpdate (self,ev,value):
    try: 
      state = value.node_state;
      name  = state.name;
    except AttributeError: 
      return None;
    _dprint(5,'got state for node ',name);
    self.update_node_state(state,ev);
    return True;
    
  def _checkStatusUpdate (self,ev,value):
    if not meqds.nodelist:   # ignore if no nodelist yet
      return False;
    try: 
      status = value.control_status;
      ni     = value.nodeindex;
    except AttributeError: return None;
    if not isinstance(status,int) or not isinstance(ni,int):
      return False;
    _dprint(5,'got control status for node ',ni);
    meqds.nodelist[ni].update_status(status,getattr(value,'request_id',None));
    return True;
    
  # override handleAppEvent to catch node state updates, whichever event they
  # may be in
  def handleAppEvent (self,ev,value):
    # update node state or status
    # note that a state update implies a status update, hence the or
    if isinstance(value,record):
      self._checkStateUpdate(ev,value) or self._checkStatusUpdate(ev,value);
      try: 
        self.treebrowser.debug_set_active_node(value.debug_status.nodeindex,value.node_state);
      except AttributeError: pass;
    # call top-level handler
    app_proxy_gui.handleAppEvent(self,ev,value);
    
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
      _dprint(5,'got state for node ',value.name);
      self.update_node_state(value,ev);
      
  def ce_DebugStop (self,ev,value):
    self.treebrowser.debug_set_active_node(value.nodeindex,value.node_state);
  
  def ce_NodeResult (self,ev,value):
    self.update_node_state(value,ev);
    if self.resultlog.enabled:
      txt = '';
      name = ('name' in value and value.name) or '<unnamed>';
      cls  = ('class' in value and value['class']) or '?';
      rqid = 'request_id' in value and str(value.request_id);
      txt = ''.join((name,' <',cls.lower(),'>'));
      desc = 'result';
      if rqid:
        txt = ''.join((txt,' rqid:',rqid));
        desc = desc + ':' + rqid;
      self.resultlog.add(txt,content=value,category=Logger.Event, 
        name=name,desc=desc,viewopts=_defaultResultViewopts);
      wtop = self.resultlog.wtop();
      if self.maintab.currentPage() is not wtop and not wtop._newresults:
        self.maintab.changeTab(wtop,wtop._newres_iconset,wtop._newres_label);
        wtop._newresults = True;
        
  def ce_LoadNodeList (self,ev,meqnl):
    if not meqds.nodelist.is_valid_meqnodelist(meqnl):
      _dprint(2,"got nodelist but it is not valid, ignoring");
      return;
    meqds.nodelist.load(meqnl);
    _dprintf(2,"loaded %d nodes into nodelist\n",len(meqds.nodelist));
    self.treebrowser.update_nodelist();
      
  def update_node_state (self,node,event=None):
    meqds.reclassify_nodestate(node);
    meqds.add_node_snapshot(node,event);
    udi = meqds.node_udi(node);
    self.gw.update_data_item(udi,node);
    
  def _view_node (self,node,viewer=None,kws={}):
    _dprint(2,"node clicked, adding item");
    self.gw.add_data_item(makeNodeDataItem(node,viewer),**kws);
    self.show_gridded_workspace();
    
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop() and tabwin._newresults:
      self._reset_maintab_label(tabwin);
    tabwin._newresults = False;

def makeNodeDataItem (node,viewer=None,viewopts={}):
  """creates a GridDataItem for a node""";
  udi = meqds.node_udi(node);
  nodeclass = meqds.NodeClass(node);
  vo = viewopts.copy();
  vo.update(_defaultNodeViewopts);
  # curry is used to create a call for refreshing its state
  return GridDataItem(udi,(node.name or '#'+str(node.nodeindex)),
            desc=nodeclass.__name__,data=None,datatype=nodeclass,
            refresh=curry(meqds.request_node_state,node),
            viewer=viewer,viewopts=vo);



_default_state_open =  ({'cache_result':({'vellsets':None},None), \
                        'request':None },None);

_defaultNodeViewopts = { \
  RecordBrowser: { 'default_open': _default_state_open },
  NodeBrowser:   { 'default_open': ({'state':_default_state_open},None) } };

_defaultResultViewopts = { \
  RecordBrowser: { 'default_open': _default_state_open }, \
  };


gridded_workspace.registerViewer(meqds.NodeClass(),NodeBrowser,priority=10);

# register reloadables
reloadableModule(__name__);
# reloadableModule('meqds');

