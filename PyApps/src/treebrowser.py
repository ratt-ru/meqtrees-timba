#!/usr/bin/python

from dmitypes import *
from qt import *
from app_proxy_gui import *
import app_pixmaps as pixmaps
import weakref
import sets
import re
import meqds
import meqserver_gui
from meqds import mqs

_dbg = verbosity(3,name='tb');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class AppState (object):
  Idle       = -hiid('idle').get(0);
  Stream     = -hiid('stream').get(0);
  Debug      = -hiid('debug').get(0);
  Execute    = -hiid('execute').get(0);

class TreeBrowser (QObject):

  class NodeItem (QListViewItem):
    def __init__(self,tb,node,name,parent,after):
      QListViewItem.__init__(self,parent,after,name);
      # fill basic listview stuff
      self.setText(tb._icol_class,str(node.classname));
      self.setText(tb._icol_index,str(node.nodeindex));
      self.setDragEnabled(True);
      if node.children:
        self.setExpandable(True);
      # internal state, etc.
      self.tb = weakref.ref(tb);  # self.tb() returns treebrowser
      self._node = weakref.proxy(node);
      self._expanded = False;
      self._udi  = meqds.node_udi(node);
      self._callbacks = [];
      # add ourselves to the item list for this node
      if not hasattr(node,'_tb_items'):
        node._tb_items = [];
      node._tb_items.append(weakref.ref(self));
      # subsribe to various events
      node.subscribe_status(self._update_status);
      node.subscribe_state(self._update_state);
      QObject.connect(node,PYSIGNAL("update_debug()"),self._update_debug);
      # default color group is None to use normal colors
      self._cg_name = self._color_group = None;
      # make sure pixmaps, etc. are updated
      self._update_status(node,node.control_status);
      
    def _update_state (self,node,state,event):
      """updates node item based on changes in state.""";
      # flash the publish pixmap briefly to indicate new state
      # self._publish_pixmap is the "normal" (None or publish) pixmap set by _update_status()
      # below; we set a timer event to revert to it
      self.setPixmap(self.tb()._icol_publish,pixmaps.publish_active.pm());
      QTimer.singleShot(500,self.xcurry(self.setPixmap,(self.tb()._icol_publish,self._publish_pixmap)));
      # update context menu
      if state is not None:
        try: menu = self._context_menu;
        except AttributeError: pass;
        else:
          for (act_id,act) in menu._actions.iteritems():
            if hasattr(act,'eval_state'):
              menu.setItemChecked(act_id,act.eval_state(state));
              
    def _update_debug (self,node):
      """updates node item based on its debugging status.""";
      try: stopped = min(node._stopped,1);
      except AttributeError: stopped = -1;
      self._color_group = self.tb().get_color_group(self._cg_name,stopped);
      
    def _update_status (self,node,old_status):
      """updates node item based on node status.""";
      tb = self.tb();
      control_status = node.control_status;
      # choose a colorgroup name for the item based on its status
      stopped = bool(control_status&meqds.CS_STOP_BREAKPOINT);
      result_status = control_status&meqds.CS_RES_MASK;
      if result_status == meqds.CS_RES_FAIL:
        self._cg_name = "fail";
      elif not control_status&meqds.CS_ACTIVE or \
           result_status in (meqds.CS_RES_WAIT,meqds.CS_RES_MISSING): 
        self._cg_name = "disabled";
      else:
        self._cg_name = None;
      # call update_debug to complete setting of color group (debug state
      # determines background)
      self._update_debug(node);
      # update status column
      self.setText(tb._icol_status,node.control_status_string);
      # update breakpoint status pixmaps
      if control_status&meqds.CS_BREAKPOINT:
        self.setPixmap(tb._icol_breakpoint,pixmaps.breakpoint.pm());
      elif control_status&meqds.CS_BREAKPOINT_SS:
        self.setPixmap(tb._icol_breakpoint,pixmaps.forward_to.pm());
      else:
        self.setPixmap(tb._icol_breakpoint,QPixmap());
      # update exec state pixmaps and rqid string
      es = meqds.CS_ES_state(control_status);
      self.setPixmap(tb._icol_execstate,es[4].pm());
      if node.request_id is None:
        self.setText(tb._icol_execstate,'');
      else:
        self.setText(tb._icol_execstate,str(node.request_id));
      # update enabled/disabled pixmap
      if control_status&meqds.CS_ACTIVE:
        self.setPixmap(tb._icol_disable,QPixmap());
      else:
        self.setPixmap(tb._icol_disable,pixmaps.cancel.pm());
      # update publish/state pixmap
      if control_status&meqds.CS_PUBLISHING:
        self._publish_pixmap = pixmaps.publish.pm();
      else:
        self._publish_pixmap = QPixmap();
      self.setPixmap(tb._icol_publish,self._publish_pixmap);
      # update breakpoints menu
      try: menu = self._debug_bp_menu;
      except AttributeError: pass;
      else:
        _dprint(3,'node',self._node.name,'breakpoint mask is',self._node.breakpoint);
        for (item,bp) in self._debug_bp_items:
          menu.setItemChecked(item,(self._node.breakpoint&bp)!=0);
      # update context menu
      try: menu = self._context_menu;
      except AttributeError: pass;
      else:
        for (act_id,act) in menu._actions.iteritems():
          if hasattr(act,'eval_status'):
            menu.setItemChecked(act_id,act.eval_status(node));
    
    def expand (self):
      if self._expanded:
        return;
      i1 = self;
      for (key,ni) in self._node.children:
        node = meqds.nodelist[ni];
        name = str(key) + ": " + node.name;
        i1 = self.__class__(self.tb(),node,name,self,i1);
      self._expanded = True;
      
    def xcurry (self,*args,**kwargs):
      cb = xcurry(*args,**kwargs);
      self._callbacks.append(cb);
      return cb;
    
    def debug_menu (self):
      try: menu = self._debug_menu;
      except AttributeError:
        node = self._node;
        menu = self._debug_menu = QPopupMenu();
        menu1 = self._debug_bp_menu = QPopupMenu();
        self._debug_bp_items = [];
        _dprint(3,'node',node.name,'breakpoint mask is',node.breakpoint);
        for st in meqds.CS_ES_statelist:
          title = ''.join(('at ',node.name,':',st[1]));
          bpmask = meqds.breakpoint_mask(st[0]);
          cb = self.xcurry(meqds.set_node_breakpoint,(node,bpmask),_argslice=slice(0));
          item = menu1.insertItem(st[4].iconset(),title,cb);
          menu1.setItemChecked(item,(node.breakpoint&bpmask)!=0);
          self._debug_bp_items.append((item,bpmask));
        menu1.insertItem(pixmaps.node_any.iconset(),''.join(("at ",node.name,':all')),self.xcurry(\
              meqds.set_node_breakpoint,(node,meqds.BP_ALL),_argslice=slice(0)));
        menu.insertItem(pixmaps.breakpoint.iconset(),"Set &breakpoint at",menu1);
        menu.insertItem(pixmaps.roadsign_nolimit.iconset(),"Clear &all breakpoints at "+node.name,self.xcurry(\
              meqds.clear_node_breakpoint,(node,meqds.BP_ALL),_argslice=slice(0)));
        menu.insertSeparator();
        menu.insertItem(pixmaps.forward_to.iconset(),"Continue &until "+node.name,self.xcurry(self.tb()._debug_until_node,(node,),_argslice=slice(0)));
#        menu.insertSeparator();
#        self.tb()._ag_debug.addTo(menu);
      return menu;
      
    def context_menu (self):
      try: menu = self._context_menu;
      except AttributeError:
        # create menu on the fly when first called for this item
        node = self._node;
        menu = self._context_menu = QPopupMenu();
        # insert title
        menu.insertItem("%s: %s"%(node.name,node.classname));
        # insert viewer list submenus
        viewer_list = gridded_workspace.getViewerList(meqds.NodeClass(node.classname));
        if viewer_list: 
          menu.insertSeparator();
          # create display submenus
          menu1 = self._display_menu1 = QPopupMenu();
          menu2 = self._display_menu2 = QPopupMenu();
          menu.insertItem(pixmaps.view_split.iconset(),"State display with",menu1);
          menu.insertItem(pixmaps.view_right.iconset(),"New state display with",menu2);
          for v in viewer_list:
            # create entry for viewer
            name = getattr(v,'viewer_name',v.__name__);
            try: icon = v.icon();
            except AttributeError: icon = QIconSet();
            # add entry to both menus ("Display with" and "New display with")
            menu1.insertItem(icon,name,
              self.xcurry(self.tb().wtop().emit,(PYSIGNAL("view_node()"),(node,v)),_argslice=slice(0)));
            menu2.insertItem(icon,name,
              self.xcurry(self.tb().wtop().emit,(PYSIGNAL("view_node()"),(node,v,dict(newcell=True))),_argslice=slice(0)));
        # add node actions
        if self.tb().get_node_actions():
          menu._actions = {};
          menu.insertSeparator();
          for act in self.tb().get_node_actions():
            if act.applies_to(node):
              act_id = act.add_to_menu(self,menu);
              # add to action map
              menu._actions[act_id] = act;
        # add debugging
        menu.insertItem(pixmaps.breakpoint.iconset(),"Debug",self.debug_menu());
      # display menu if defined
      return menu;
      
    def paintCell (self,painter,cg,column,width,align):
      return QListViewItem.paintCell(self,painter,self._color_group or cg,column,width,align);

    def clear_children (parent):
      """Recursively cleans up all child items of the given parent, in
      preparation for deleting them. This is mainly done to remove cyclic
      references caused by the NodeItem._callbacks list.""";
      item = parent.firstChild();
      while item:
        try: delattr(item,'_callbacks');
        except: pass;
        if hasattr(item,'clear_children'):
          item.clear_children(item);
        item = item.nextSibling();
    clear_children = staticmethod(clear_children);
      
  def __init__ (self,parent):
    QObject.__init__(self);
    self._parent = weakref.proxy(parent);
    # ---------------------- construct GUI
    nl_vbox = self._wtop = QVBox(parent);
    #---------------------- node list view
    self._nlv = nlv = DataDraggableListView(nl_vbox);
    nlv.setShowSortIndicator(True);
    nlv.setRootIsDecorated(True);
    nlv.setTreeStepSize(12);
    # nlv.setSorting(-1);
    nlv.setResizeMode(QListView.NoColumn);
    nlv.setFocus();
    QObject.connect(nlv,SIGNAL('expanded(QListViewItem*)'),self._expand_node);
    QObject.connect(nlv,SIGNAL('mouseButtonClicked(int,QListViewItem*,const QPoint &,int)'),
                     self._node_clicked);
    QObject.connect(nlv,SIGNAL('contextMenuRequested(QListViewItem*,const QPoint &,int)'),
                     self._show_context_menu);
    QObject.connect(nlv,SIGNAL('currentChanged(QListViewItem*)'),self._set_recent_item);
    # map the get_data_item method
    nlv.get_data_item = self.get_data_item;
    #---------------------- setup color groups for items
    self._cg = {};
    # color group for stopped nodes
    stopcolor = { -1:None, 0:QColor("lightblue"), 1:QColor("lightblue2") };
    for stopped in stopcolor.keys():
      # color group for normal nodes
      self._cg[(None,stopped)] = self._new_colorgroup(stopcolor[stopped]);
      # color groups for nodes with missing data
      self._cg[("disabled",stopped)] = \
        self._new_colorgroup(stopcolor[stopped],QColor("grey50"));
      # color groups for failed nodes
      self._cg[("fail",stopped)] = \
        self._new_colorgroup(stopcolor[stopped],QColor("red"));
    # ---------------------- setup toolbars, QActions and menus
    # scan all modules for defined toolbar actions
    self._toolbar_actions = [];
    funcs = sets.Set();
    for (name,mod) in sys.modules.iteritems():
      _dprint(4,'looking for treebrowser actions in',name);
      try: 
        if callable(mod.define_treebrowser_toolbar_actions):
          _dprint(3,'tb action found in',name,'adding to set');
          funcs.add(mod.define_treebrowser_toolbar_actions);
      except AttributeError: pass;
    _dprint(1,len(funcs),'unique treebrowser action-definition methods found');
    for f in funcs:
      f(self);
    # build up toolbar
    self._toolbar = QToolBar("Tree operations",parent);
    tba = self._toolbar_actions;
    self._toolbar_actions = [];
    tba.sort();
    for (pri,action) in tba:
      if action is None:
        self._toolbar.addSeparator();
      else:
        self._toolbar_actions.append(action);
        action.addTo(self._toolbar);
        action.setEnabled(False);
    QObject.connect(self.wtop(),PYSIGNAL("entering()"),self._toolbar,SLOT("show()"));
    QObject.connect(self.wtop(),PYSIGNAL("leaving()"),self._toolbar,SLOT("hide()"));
    self._toolbar.hide();
    # ---------------------- other internal state
    self._recent_item = None;
    self._current_debug_stack = None;
    #----------------------- public state
    self.app_state = None;
    self.debug_level = 0;
    self.is_connected = self.is_loaded = self.is_running = self.is_stopped = False;
    
  def _reset_toolbar (self):
    self._set_debug_control(self.debug_level>0);
    _dprint(3,'reset_toolbars:',self.debug_level,self.is_connected,self.is_running,self.is_stopped);
    for act in self._toolbar_actions:
      try: act.setEnabled(act._is_enabled());
      except AttributeError: pass;

  def _set_debug_control (self,enable):
    """This updates the state of the debug control without sending
    out a message.""";
    self._setting_debug_control = True;
    self._qa_dbg_enable.setOn(enable);
    self._setting_debug_control = False;
    
  def _debug_enable_slot (self,enable):
    """Sends a debug enable/disable message.""";
    if enable:
      self._qa_dbg_enable.setAccel(Qt.CTRL+Qt.Key_F5);
      self._qa_dbg_enable.setText("Disable debugger and continue");
      self._qa_dbg_enable.setMenuText("&Disable debugger");
      if not getattr(self,'_setting_debug_control',False):
        mqs().meq('Debug.Set.Level',srecord(debug_level=2,get_forest_status=True),wait=False);
    else:
      if not getattr(self,'_setting_debug_control',False):
        # confirm disable if in debugger
        if self._current_debug_stack:
          if QMessageBox.warning(None,"Disabling Tree Debugger",\
               """This will disable the debugger and release the tree to ignore
               all breakpoints and run until it is finished or out of data. 
               Are you sure this is what you want?""",QMessageBox.Ok,\
               QMessageBox.Cancel|QMessageBox.Default|QMessageBox.Escape) \
             != QMessageBox.Ok:
            self._set_debug_control(True);
            return;
          mqs().meq('Debug.Set.Level',srecord(debug_level=0,get_forest_status=True),wait=False);
      # really disable
      self.clear_debug_stack();
      self._qa_dbg_enable.setAccel(Qt.Key_F5);
      self._qa_dbg_enable.setText("Enable debugger");
      self._qa_dbg_enable.setMenuText("Enable &Debugger");

  def get_color_group (self,which,is_stopped=-1):
    return self._cg[(which,is_stopped)][0];
    
  def _new_colorgroup (self,background=None,foreground=None):
    palette = QPalette(self._nlv.palette().copy());
    cg = palette.active();
    if background:
      cg.setColor(QColorGroup.Base,background);
    if foreground: 
      cg.setColor(QColorGroup.Text,foreground);
    return (cg,palette);
    
  # init empty set of node actions
  _node_actions = [];
  def add_node_action (action):
    """Registers a node action for the tree browser context menu.""";
    TreeBrowser._node_actions.append(action);
  add_node_action = staticmethod(add_node_action);
  
  def get_node_actions (self):
    return self._node_actions;

  def get_data_item (self,udi):
    (name,ni) = meqds.parse_node_udi(udi);
    if ni is None:
      if name is None:
        return None;
      if not len(name):
        raise ValueError,'bad udi (either name or nodeindex must be supplied): '+udi;
      node = meqds.nodelist[name];
    else:
      try: 
        node = meqds.nodelist[ni];
      except ValueError: # can't convert nodeindex to int: malformed udi
        raise ValueError,'bad udi (nodeindex must be numeric): '+udi;
    # create and return dataitem object
    return meqserver_gui.makeNodeDataItem(node);
 
  def wtop (self):
    return self._wtop;
    
  def clear (self):
    self.is_loaded = False;
    self._debug_node = self._current_debug_stack = None;
    self.NodeItem.clear_children(self._nlv);
    self._nlv.clear();
    self._reset_toolbar();
    
  def connected (self,conn,auto_request=True):
    self.emit(PYSIGNAL("connected()"),(conn,));
    self.is_connected = conn;
    if conn is True:
      self._reset_toolbar();
      if auto_request:
        self._request_nodelist();
    else:
      self.clear();

  def update_app_state (self,state):
    self.app_state = state;
    # enable pause control in running state 
    self.is_running = state in (AppState.Debug,AppState.Stream,AppState.Execute);
    self.is_stopped = state == AppState.Debug;
    self._reset_toolbar();
    
  def update_forest_status (self,fst):
    """Updates forest status: enables/disables debug QActions as appropriate,
    sets/clears highlighting of stopped nodes."""
    _dprint(2,"updating forest status");
    # this will hold the list of nodes currently in the debug stack
    debug_stack = sets.Set();
    self._debug_node = None;
    # make sure debug buttons are enabled/disabled as appropriate
    # also compiles a set of nodes in the debug-stack
    self.debug_level = fst.debug_level;
    # do other stuff if debug is enabled
    if fst.debug_level:
      _dprint(2,"debugging enabled");
      try: 
        self._nlv.setColumnWidthMode(self._icol_execstate,QListView.Maximum);
        self._nlv.setColumnWidthMode(self._icol_status,QListView.Maximum);
      except AttributeError: pass;
      self._set_debug_control(True);
      if meqds.nodelist and fst.debug_stack:
        for (n,frame) in enumerate(fst.debug_stack):
          try: node = meqds.nodelist[frame.nodeindex];
          except KeyError: continue;
          # top (most recently stopped) node gets special treatment
          if not n:
            self._debug_node = node;
          node._stopped = n;
          debug_stack.add(node);
          if hasattr(frame,'state'):
            node.update_state(frame.state);
          else:
            node.update_status(frame.control_status);
    else:
      _dprint(2,"debugging disabled");
      self._set_debug_control(False);
      try:
        self._nlv.setColumnWidthMode(self._icol_execstate,QListView.Manual);
        self._nlv.setColumnWidth(self._icol_execstate,0);
        self._nlv.setColumnWidthMode(self._icol_status,QListView.Manual);
        self._nlv.setColumnWidth(self._icol_status,0);
      except AttributeError: pass;
    # nodes in the debug-stack will have been highlighted by
    # update_state/status above. We now need to remove highlighting from
    # nodes no longer in the stack:
    if self._current_debug_stack:
      self.clear_debug_stack(self._current_debug_stack - debug_stack);
    # set current stack
    self._current_debug_stack = debug_stack;
    # make sure most recent node is open
    if self._debug_node:
      self.make_node_visible(self._debug_node);
    # reset toolbar as appropriate
    self._reset_toolbar();
        
  def clear_debug_stack (self,clearset=None):
    """Clears highlighting of stopped nodes. If a set is supplied, that 
    set is cleared, otherwise the current set is used""";
    if clearset is None:
      clearset = self._current_debug_stack;
      self._current_debug_stack = None;
    if clearset:
      for node in clearset:
        delattr(node,'_stopped');
        node.emit(PYSIGNAL("update_debug()"),(node,));
  
  def update_nodelist (self):
    # init columns if calling for the first time
    # (we don't do it in the constructor because the number of columns
    # depends on the available node actions)
    # init one column per registered action; first one is always node name
    if not self._nlv.columns(): 
      self._node_actions = TreeBrowser._node_actions;
      self._nlv.addColumn('node');
      self._icol_publish = self._nlv.columns();
      self._nlv.addColumn('',20);
      # add status, class and index columns
      self._icol_breakpoint = self._nlv.columns();
      self._nlv.addColumn('',20);
      self._icol_execstate = self._nlv.columns();
      self._nlv.addColumn('xs/rqid');
      self._icol_class = self._icol_disable = self._nlv.columns();
      self._nlv.addColumn('Class');
      self._icol_status = self._nlv.columns();
      self._nlv.addColumn('(status)');
      self._icol_index = self._nlv.columns();
      self._nlv.addColumn('idx',60);
    #      for icol in range(self._nlv.columns()):
    #        self._nlv.setColumnWidthMode(icol,QListView.Maximum);
    # clear view
    self.clear();
    self.is_loaded = True;
    self._reset_toolbar();
    # reset the nodelist view
    nodelist = meqds.nodelist;
    self._recent_item = None;
    all_item  = QListViewItem(self._nlv,"All Nodes (%d)"%len(nodelist));
    all_item._no_auto_open = True;
    all_item._iter_nodes = nodelist.iternodes();
    all_item.setExpandable(True);
    rootnodes = nodelist.rootnodes();
    rootitem  = self._nlv_rootitem = QListViewItem(self._nlv,all_item,"Root Nodes (%d)"%len(rootnodes));
    rootitem._iter_nodes = iter(rootnodes);
    rootitem.setExpandable(True);
    classes = nodelist.classes();
    cls_item  = item = QListViewItem(self._nlv,rootitem,"By Class (%d)"%len(classes));
    cls_item._no_auto_open = True;
    for (cls,nodes) in classes.iteritems():
      if len(nodes) == 1:
        item = self.NodeItem(self,nodes[0],nodes[0].name,cls_item,item);
      else:
        item = QListViewItem(cls_item,item,"(%d)"%len(nodes));
        item.setText(self._icol_class,cls);
        item.setExpandable(True);
        item._iter_nodes = iter(nodes);
      item._no_auto_open = True;
    
  def is_node_visible (self,node):
    for itemref in getattr(node,'_tb_items',[]):
      if itemref() and itemref().isVisible():
          return True;
    return False;
    
  def make_node_visible (self,node):
    # no node list -- do nothing
    if not meqds.nodelist:
      return;
    # Go over every available item and find one with the lowest "display cost".
    # Cost starts at 0 and is incremented for every level that needs to be opened
    # to make the item visible. Thus, already-visible items will have a cost of 0.
    (best_cost,best_item) = (100000,None);
    for itemref in getattr(node,'_tb_items',[]):
      item = itemref();
      if item is not None:
        cost = 0;
        parent = item.parent();
        while parent:
          if not parent.isOpen():
            cost += 1;
            # if we hit a closed parent tagged with this attr (this is for "All nodes" 
            # and "By class" items), set a cost of None and give up: this item is ineligible
            if getattr(parent,'_no_auto_open',False):
              cost = None;
              break;
          # if parent is a recent item, decrease cost -- we want this item to be preferred
          if parent is self._recent_item:
            _dprint(3,"parent",parent.text(0),"is recent, what a bonus");
            cost -= 100;
          parent = parent.parent();
        _dprint(3,"item cost is ",cost);
        # update best cost estimate
        if cost is not None and cost < best_cost:
          (best_cost,best_item) = (cost,item);
    # if no suitable item was found, try to expand the root tree
    if best_item: 
      _dprint(3,"have a preferred item, ensuring visibility");
    else: # no suitable item was found, try to expand the root tree
      _dprint(3,"no suitable items found, expanding tree to look for active item");
      best_item = self.expand_active_tree(active_ni=node.nodeindex);
    self._nlv.ensureItemVisible(best_item);
    
  def expand_active_tree (self,start=None,active_ni=None):
    """expands all items from start (the "Root nodes" menu, if start=None) that
    correspond to active (i.e. non-idle) nodes. If 'active' is specified and is a node, 
    returns the item corresponding to that node (if it finds it)."""
    if start is None:
      try: start = self._nlv_rootitem;
      except AttributeError: return;
    active_item = None;
    self._nlv.setOpen(start,True);
    # recursively expand all non-idle child nodes
    item = start.firstChild();
    while item:
      if isinstance(item,self.NodeItem):
        if item._node.nodeindex == active_ni and not active_item:   
          self._nlv.ensureItemVisible(item);
          active_item = item;
        if (item._node.control_status&meqds.CS_MASK_EXECSTATE) != meqds.CS_ES_IDLE:
          i1 = self.expand_active_tree(item,active_ni);
          active_item = active_item or i1;
      item = item.nextSibling();
    return active_item;
  
  # slot: called to show a context menu for a browser item
  def _show_context_menu (self,item,point,col):
    if isinstance(item,self.NodeItem):
      if col in (self._icol_status,self._icol_execstate,self._icol_breakpoint):
        menu = item.debug_menu();
      else:
        menu = item.context_menu();
      if menu is not None:
        menu.exec_loop(point);
      
  def _node_clicked (self,button,item,point,col):
    self._recent_item = item;
    if isinstance(item,self.NodeItem):
      if button == 1:
        self.wtop().emit(PYSIGNAL("view_node()"),(item._node,None));
        
  def _set_recent_item (self,item):
    self._recent_item = item;
  
  def _expand_node (self,item):
    self._recent_item = item;
    if isinstance(item,self.NodeItem):
      item.expand();
    else:
      # populate list when first opened, if an iterator is present as an attribute
      try: iter_nodes = item._iter_nodes;
      except: pass;
      else:
        i1 = item;
        for node in iter_nodes:
          i1 = self.NodeItem(self,node,node.name,item,i1);
        delattr(item,'_iter_nodes');
  # _expand_node = busyCursorMethod(_expand_node);
  
  def _request_nodelist (self):
    _dprint(1,"requesting node list");
    mqs().meq('Get.Node.List',meqds.NodeList.RequestRecord,wait=False);
    
  def _save_forest (self):
    try: dialog = _save_dialog;
    except AttributeError:
      dialog = self._save_dialog = QFileDialog(self._nlv,"save dialog",True);
      dialog.setMode(QFileDialog.AnyFile);
      dialog.setFilters("Forests (*.forest *.meqforest);;All files (*.*)");
      dialog.setViewMode(QFileDialog.Detail);
      dialog.setCaption("Save forest");
    if dialog.exec_loop() == QDialog.Accepted:
      fname = str(dialog.selectedFile());
      rec = srecord(file_name=fname,get_forest_status=True);
      mqs().meq('Save.Forest',rec,wait=False);

  def _load_forest (self):
    try: dialog = self._load_dialog;
    except AttributeError:
      dialog = self._load_dialog = QFileDialog(self._nlv,"load dialog",True);
      dialog.setMode(QFileDialog.ExistingFile);
      dialog.setFilters("Forests (*.forest *.meqforest);;All files (*.*)");
      dialog.setViewMode(QFileDialog.Detail);
      dialog.setCaption("Load forest");
    if dialog.exec_loop() == QDialog.Accepted:
      fname = str(dialog.selectedFile());
      rec = srecord(file_name=fname,get_forest_status=True);
      mqs().meq('Load.Forest',rec,wait=False);
      
  def _debug_single_step (self):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._reset_toolbar();
    mqs().meq('Debug.Single.Step',srecord(),wait=False);
  
  def _debug_next_node (self):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._reset_toolbar();
    mqs().meq('Debug.Next.Node',srecord(),wait=False);
    
  def _debug_until_node (self,node):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._reset_toolbar();
    mqs().meq('Debug.Until.Node',srecord(nodeindex=node.nodeindex),wait=False);
  
  def _debug_continue (self):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._reset_toolbar();
    mqs().meq('Debug.Continue',srecord(),wait=False);
    
  def _debug_pause (self):
    mqs().meq('Debug.Pause',srecord(),wait=False);

  def add_toolbar_action (self,action,callback=None,order=1000,menus=None):
    if callback:
      QObject.connect(action,SIGNAL("activated()"),callback);
    action._tb_menus = menus;
    self._toolbar_actions.append((order,action));
    
  def add_toolbar_separator (self,order=1000):
    self._toolbar_actions.append((order,None));

def define_treebrowser_toolbar_actions (tb):
  _dprint(1,'defining standard treebrowser actions');
  parent = tb.wtop();
  # Refresh
  refresh = QAction("Refresh",pixmaps.refresh.iconset(),"Refresh node list",Qt.Key_F2,parent);
  refresh._is_enabled = lambda tb=tb: tb.is_connected;
  tb.add_toolbar_action(refresh,tb._request_nodelist,10);
  tb.add_toolbar_separator(20);
  # Save and load
  load = QAction("Load",pixmaps.file_open.iconset(),"Load forest",Qt.Key_L+Qt.ALT,parent);
  save = QAction("Save",pixmaps.file_save.iconset(),"Save forest",Qt.Key_S+Qt.ALT,parent);
  load._is_enabled = save._is_enabled = lambda tb=tb: tb.is_connected and tb.app_state == AppState.Idle;
  tb.add_toolbar_action(load,tb._load_forest,30);
  tb.add_toolbar_action(save,tb._save_forest,40);
  tb.add_toolbar_separator(50);
  # Enable debugger
  dbg_enable = tb._qa_dbg_enable = QAction("Enable debugger",pixmaps.eject.iconset(),"Enable &Debugger",Qt.Key_F5,parent,"",True);
  QObject.connect(dbg_enable,SIGNAL("toggled(bool)"),tb._debug_enable_slot);
  QObject.connect(tb,PYSIGNAL("debug_enabled()"),dbg_enable.setOn);
  dbg_enable._is_enabled = lambda tb=tb: tb.is_connected;
  tb.add_toolbar_action(dbg_enable,None,60);
  # Pause
  pause = QAction("Pause",pixmaps.pause.iconset(),"&Pause",Qt.Key_F6,parent);
  dbg_enable.is_enabled = lambda tb=tb: tb.is_connected and tb.debug_level>0 and \
                                        tb.is_running and not tb.is_stopped;
  tb.add_toolbar_action(pause,tb._debug_pause,70);
  tb.add_toolbar_separator(80);
  # Debug action group
  ag_debug = QActionGroup(parent);
  dbgcont  = QAction("Continue",pixmaps.right_2triangles.iconset(),"&Continue",Qt.Key_F6+Qt.SHIFT,parent);      
  QObject.connect(dbgcont,SIGNAL("activated()"),tb._debug_continue);
  dbgstep  = QAction("Step",pixmaps.down_triangle.iconset(),"&Step",Qt.Key_F7,parent);      
  QObject.connect(dbgstep,SIGNAL("activated()"),tb._debug_single_step);
  dbgnext  = QAction("Step to next node",pixmaps.down_2triangles.iconset(),"Step to &next node",Qt.Key_F8,parent);      
  QObject.connect(dbgnext,SIGNAL("activated()"),tb._debug_next_node);
  ag_debug._is_enabled = lambda tb=tb: tb.is_connected and tb.debug_level>0 and \
                                       tb.is_loaded and tb.is_stopped;
  ag_debug.add(dbgcont);
  ag_debug.add(dbgstep);
  ag_debug.add(dbgnext);
  tb.add_toolbar_action(ag_debug,None,90);
  
class NodeAction (object):
  """NodeAction is a class describing a node-associated action.""";
  # these class attributes are meant to be redefined by subclasses
  text = 'unknown action';
  iconset = None;
  nodeclass = None;  # None means all nodes; else assign meqds.NodeClass('class');
  def applies_to_all (self):
    return self.nodeclass is None;
  def applies_to (self,node):
    return self.applies_to_all() or issubclass(meqds.NodeClass(node.nodeclass),self.nodeclass);
  def add_to_menu (self,item,menu):
    cb = item.xcurry(self.activate,(item._node,),_argslice=slice(0));
    if self.iconset:
      iid = menu.insertItem(self.iconset(),self.text,cb);
    else:
      iid = menu.insertItem(self.text,cb);
    if hasattr(self,'eval_status'):
      menu.setItemChecked(iid,self.eval_status(item._node));
    return iid;
  ### if eval_status() defined in a sub-class, then the menu entry for this node action will be 
  ### "checkable", with the "checked" status determined by calling this method with the node's
  ### control status whenever that is updated.
  ## def eval_status (self,node):
  ##   return False;
  ### if eval_state() defined in a sub-class, then the menu entry for this node action will be 
  ### "checkable", with the "checked" status determined by calling this method with the node's
  ### state record whenever that is updated.
  ## def eval_state (self,state):
  ##   return False;
  # activate is called whenever this action is selected from the context menu
  def activate (self,node):
    """this method is called whenever this action is selected from the context menu""";
    raise "activate() not defined in NodeAction of type "+str(type(self));
    
class NTA_NodeDisable (NodeAction):
  text = "Disable";
  iconset = pixmaps.cancel.iconset;
  def activate (self,node):
    cs = node.control_status ^ meqds.CS_ACTIVE;
    meqds.set_node_state(node,control_status=cs);
  def eval_status (self,node):
    return not node.is_active();

class NTA_NodePublish (NodeAction):
  text = "Publish";
  iconset = pixmaps.publish.iconset;
  def activate (self,node):
    cmd = srecord(nodeindex=node.nodeindex,get_state=True,enable=not node.is_publishing());
    mqs().meq('Node.Publish.Results',cmd,wait=False);
  def eval_status (self,node):
    return node.is_publishing();

TreeBrowser.add_node_action(NTA_NodeDisable());
TreeBrowser.add_node_action(NTA_NodePublish());



