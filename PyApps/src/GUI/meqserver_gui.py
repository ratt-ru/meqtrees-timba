#!/usr/bin/python

from Timba.dmi import *
from Timba.GUI.app_proxy_gui import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba.GUI.browsers import *
from Timba.GUI.treebrowser import *
from Timba import Grid

import weakref
import math
import sets
import re

_dbg = verbosity(0,name='meqgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# global symbol: meqserver object; initialized when a meqserver_gui
# is constructed
mqs = None;

# ---------------- TODO -----------------------------------------------------
# As of 14/12/2004, this list has been moved into the Bugzilla database
# http://lofar9.astron.nl/bugzilla/
# ---------------------------------------------------------------------------

class NodeBrowser(HierBrowser,GriddedPlugin):
  _icon = pixmaps.treeviewoblique;
  viewer_name = "Node Browser";
  
  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    HierBrowser.__init__(self,self.wparent(),"value","field",
        udi_root=(dataitem and dataitem.udi));
    self.set_cell_content(self.wtop(),dataitem.caption,icon=self.icon());
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

  StatePixmaps = { None: pixmaps.stop, \
    AppState.Idle: pixmaps.grey_cross,
    AppState.Stream: pixmaps.spigot,
    AppState.Debug: pixmaps.breakpoint };

  def __init__(self,app,*args,**kwargs):
    meqds.set_meqserver(app);
    global mqs;
    self.mqs = mqs = app;
    self.mqs.track_results(False);
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    # add handlers for result log
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("app.result.node.get.state",self.ce_NodeState);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("hello",self.ce_mqs_Hello);
    self._add_ce_handler("bye",self.ce_mqs_Bye);
    self._add_ce_handler("app.update.status.num.tiles",self.ce_UpdateAppStatus);
    
  def populate (self,main_parent=None,*args,**kwargs):
    # init icons
    pixmaps.load_icons('treebrowser');
    # populate GUI
    app_proxy_gui.populate(self,main_parent=main_parent,*args,**kwargs);
    self.setIcon(pixmaps.trees48x48.pm());
    self.set_verbose(self.get_verbose());
    _dprint(2,"meqserver-specifc init"); 
    # add Tree browser panel
    self.treebrowser = TreeBrowser(self);
    self.maintab.insertTab(self.treebrowser.wtop(),"Trees",1);
    self.connect(self.treebrowser.wtop(),PYSIGNAL("view_node()"),self._view_node);
    self.connect(self.treebrowser.wtop(),PYSIGNAL("view_forest_state()"),self._view_forest_state);
    
    # add Result Log panel
    self.resultlog = Logger(self,"node snapshot log",limit=1000,
          udi_root='snapshot');
    self.maintab.insertTab(self.resultlog.wtop(),"Snapshots",2);
    self.resultlog.wtop()._default_iconset = QIconSet();
    self.resultlog.wtop()._default_label   = "Snapshots";
    self.resultlog.wtop()._newres_iconset  = pixmaps.check.iconset();
    self.resultlog.wtop()._newres_label    = "Snapshots";
    self.resultlog.wtop()._newresults      = False;
    QObject.connect(self.resultlog.wlistview(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    
    # excluse ubiquotous events from the event logger
    self.eventlog.set_mask('!node.status.*;'+self.eventlog.get_mask());
    
    # subscribe to updates of forest state
    meqds.subscribe_forest_state(self._update_forest_state);

  def _checkStateUpdate (self,ev,value):
    try: 
      state = value.node_state;
      name  = state.name;
    except AttributeError: 
      return None;
    _dprint(5,'got state for node ',name);
    self.update_node_state(state,ev);
    return True;
    
  _prefix_NodeStatus = hiid('node.status');
  # override handleAppEvent to catch node state updates, whichever event they
  # may be in
  def handleAppEvent (self,ev,value):
    # check for node status
    if ev.startswith(self._prefix_NodeStatus):
      (ni,status,rqid) = (ev.get(2),ev.get(3),ev[4:]);
      _dprint(5,'got status for node',ni,':',status,rqid);
      try: node = meqds.nodelist[ni];
      except KeyError: pass;
      else: node.update_status(status,rqid);
    if isinstance(value,record):
      # check if message includes update of node state
      self._checkStateUpdate(ev,value);
      # check if message includes update of forest status
      fstatus = getattr(value,'forest_status',None);
      fstate  = getattr(value,'forest_state',None);
      if fstatus is not None:
        self.treebrowser.update_forest_status(fstatus);
      # update forest state, if supplied. Merge in the forest status if
      # we also have it
      if fstate is not None:
        if fstatus is not None:
          fstate.update(fstatus);
        meqds.update_forest_state(fstate);
      # no forest state supplied but a status is: merge it in
      elif fstatus is not None:
        meqds.update_forest_state(fstatus,True);
    # call top-level handler
    app_proxy_gui.handleAppEvent(self,ev,value);
    
  def ce_mqs_Hello (self,ev,value):
    self.treebrowser.clear();
    self.treebrowser.connected(True);  
    self.resultlog.clear();
    wtop = self.resultlog.wtop();
    self.maintab.changeTab(wtop,wtop._default_iconset,wtop._default_label);
    meqds.request_forest_state();
    
  def ce_mqs_Bye (self,ev,value):
    self.treebrowser.connected(False);  
    
  def ce_NodeState (self,ev,value):
    if hasattr(value,'name'):
      _dprint(5,'got state for node ',value.name);
      self.update_node_state(value,ev);
      
  def ce_NodeResult (self,ev,value):
    self.update_node_state(value,ev);
    if self.resultlog.enabled:
      txt = '';
      name = getattr(value,'name','') or '<unnamed>';
      cls  = getattr(value,'class','') or '?';
      rqid = str(getattr(value,'request_id',None)) or None;
      txt = ''.join((name,' <',cls.lower(),'>'));
      desc = 'snapshot for %s (%s)' % (name,cls);
      caption = '<B>%s</B> s/shot' % (name,);
      if rqid:
        txt = ''.join((txt,' rqid:',rqid));
        desc = desc + '; rqid: ' + rqid;
        caption = caption + ( ' <small>(rqid: %s)</small>' % (rqid,) );
      udi = meqds.snapshot_udi(value);
      self.resultlog.add(txt,content=value,category=Logger.Event,
        udi=udi,name=name,desc=desc,caption=caption,viewopts=_defaultResultViewopts);
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
    # re-update forest status, if available
    try: fst = meqnl.forest_status;
    except AttributeError: pass;
    else: self.treebrowser.update_forest_status(fst);
    
  def ce_UpdateAppStatus (self,ev,status):
    try: nt = status.num_tiles;
    except AttributeError: pass;
    else:
      if self.app.state == AppState.Stream:
        state = self.app.statestr.lower();
        self.status_label.setText(' %s (%d) ' % (state,nt) ); 
        
  def update_node_state (self,node,event=None):
    meqds.reclassify_nodestate(node);
    meqds.add_node_snapshot(node,event);
    udi = meqds.node_udi(node);
    Grid.updateDataItem(udi,node);
    
  def _view_node (self,node,viewer=None,kws={}):
    _dprint(2,"node clicked, adding item");
    node = meqds.nodeobject(node);
    Grid.addDataItem(makeNodeDataItem(node,viewer),**kws);
    self.show_gridded_workspace();
    
  def _view_forest_state (self,viewer=None,**kws):
    _dprint(2,"adding viewer for forest state");
    item = Grid.DataItem('/forest',name='Forest state',caption='<b>Forest state</b>',
                          desc='State of forest',data=meqds.get_forest_state(),
                          refresh=meqds.request_forest_state,viewer=viewer);
    Grid.addDataItem(item,**kws);
    self.show_gridded_workspace();
    
  def _update_forest_state (self,fst):
    Grid.updateDataItem('/forest',fst);
    
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop() and tabwin._newresults:
      self._reset_maintab_label(tabwin);
    tabwin._newresults = False;

  def _update_app_state (self):
    app_proxy_gui._update_app_state(self);
    if self.app.state == AppState.Stream:
      self.ce_UpdateAppStatus(None,self.app.status);
    self.treebrowser.update_app_state(self.app.state);

# register NodeBrowser at low priority for now (still experimental),
# but eventually we'll make it the default viewer
Grid.Services.registerViewer(meqds.NodeClass(),NodeBrowser,priority=30);

_default_state_open =  ({'cache_result':({'vellsets':({'0':None},None)},None), \
                        'request':None },None);

_defaultResultViewopts = { \
  RecordBrowser: { 'default_open': _default_state_open }, \
  };

_defaultNodeViewopts = { \
  RecordBrowser: { 'default_open': _default_state_open },
  NodeBrowser:   { 'default_open': ({'state':_default_state_open},None) } 
};

def makeNodeDataItem (node,viewer=None,viewopts={}):
  """creates a GridDataItem for a node""";
  udi = meqds.node_udi(node);
  nodeclass = meqds.NodeClass(node);
  vo = viewopts.copy();
  vo.update(_defaultNodeViewopts);
  namestr = node.name or '#'+str(node.nodeindex);
  name = "%s (%s)" % (namestr,node.classname);
  caption = "<b>%s</b> <small><i>(%s)</i></small>" % (namestr,node.classname);
  desc = "State record of node %s#%d (class %s)" % (node.name,node.nodeindex,node.classname);
  # curry is used to create a call for refreshing its state
  return Grid.DataItem(udi,name=name,caption=caption,desc=desc,
            datatype=nodeclass,
            refresh=curry(meqds.request_node_state,node.nodeindex),
            viewer=viewer,viewopts=vo);
            

# register reloadables
reloadableModule(__name__);
# reloadableModule('meqds');

