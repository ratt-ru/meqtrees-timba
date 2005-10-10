#!/usr/bin/python

import Timba
from Timba.dmi import *
from Timba.GUI.app_proxy_gui import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI import meqgui

from qt import *
import weakref
import sets
import re
import copy
import math

_dbg = verbosity(0,name='tb');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class AppState (object):
  Idle       = -hiid('idle').get(0);
  Stream     = -hiid('stream').get(0);
  Debug      = -hiid('debug').get(0);
  Execute    = -hiid('execute').get(0);
  
class StickyListViewItem (QListViewItem):
  """This is a QListViewItem that ignores sorting, 'sticking' to one
  place in the listview.
  Each such item is created with a 'key' argument that determines its 
  placement in the listview, regardless of sort column or order. Items 
  with keys>0 are placed after regular items, items with keys<0 are 
  placed before regular items.
  """;
  def __init__(self,*args,**kw):
    QListViewItem.__init__(self,*args);
    self._key = kw.get('key',1);
  def compare (self,other,col,ascending):
    try: val = cmp(self._key,other._key);
    except AttributeError:  # other item not keyed
      val = self._key;
    if ascending:
      return val;
    return -val;

class TreeBrowser (QObject):

  class NodeItem (QListViewItem):
    def __init__(self,tb,node,name,parent,after,stepchild=False):
      QListViewItem.__init__(self,parent,after,name);
      _dprint(3,"creating TreeBrowser.NodeItem",name);
      # fill basic listview stuff
      self.setText(tb.icolumn("class"),str(node.classname));
      self.setText(tb.icolumn("index"),str(node.nodeindex));
      self.setDragEnabled(True);
      if node.children or node.step_children:
        self.setExpandable(True);
      # external state
      self.tb = weakref_proxy(tb);      # self.tb returns treebrowser
      self.node = weakref_proxy(node);  # self.node returns meqds node
      # internal state, etc.
      self._expanded = False;
      self._udi  = meqds.node_udi(node);
      self._callbacks = [];
      self._menu_actions = [];
      self._stepchild = stepchild;
      self._cg_name = self._color_group = None;
      # add ourselves to the item list for this node
      if not hasattr(node,'_tb_items'):
        node._tb_items = [];
      node._tb_items.append(weakref.ref(self));
      # subsribe to various events
      node.subscribe_status(self._update_status);
      node.subscribe_state(self._update_state);
      QObject.connect(node,PYSIGNAL("update_debug()"),self._update_debug);
      # default color group is None to use normal colors
      # make sure pixmaps, etc. are updated
      self._update_status(node,node.control_status);
      # add click handlers
      self._item_event_handler = {};
      # left-click: view
      self._item_event_handler[('click',1)] = xcurry(self._add_node_viewer);
      # middle-click: new view
      self._item_event_handler[('click',4)] = xcurry(self._add_node_viewer,newcell=True);
      self._item_event_handler['menu'] = self._show_context_menu;
      
    def __del__ (self):
      self.cleanup();
    
    def cleanup (self):
      self._callbacks = self._item_event_handler = None;
      # try: 
      #  node = self.node;
      #  node._tb_items = None; # NB: kludge
      #  node.unsubscribe_status(self._update_status);
      #  node.unsubscribe_state(self._update_state);
      
    def _show_context_menu (self,point,col):
      if col in (self.tb.icolumn("execstate"),self.tb.icolumn("breakpoint")):
        menu = self.debug_menu();
      else:
        menu = self.context_menu();
      if menu is not None:
        menu.exec_loop(point);
      
    def _add_node_viewer (self,viewer=None,**kws):
      Grid.addDataItem(meqgui.makeNodeDataItem(self.node,viewer),show_gw=True,**kws);
      
    def _update_state (self,node,state,event):
      """updates node item based on changes in state.""";
      # flash the publish pixmap briefly to indicate new state
      # self._publish_pixmap is the "normal" (None or publish) pixmap set by _update_status()
      # below; we set a timer event to revert to it
      self.setPixmap(self.tb.icolumn("publish"),pixmaps.publish_active.pm());
      QTimer.singleShot(500,self.xcurry(self.setPixmap,(self.tb.icolumn("publish"),self._publish_pixmap)));
              
    def _update_debug (self,node):
      """updates node item based on its debugging status.""";
      try: stopped = min(node._stopped,1);
      except AttributeError: stopped = -1;
      self._color_group = self.tb.get_color_group(self._cg_name,stopped);
      
    def _update_status (self,node,old_status):
      """updates node item based on node status.""";
      tb = self.tb;
      control_status = node.control_status;
      # choose a colorgroup name for the item based on its status
      stopped = bool(control_status&meqds.CS_STOP_BREAKPOINT);
      result_status = control_status&meqds.CS_RES_MASK;
      if result_status == meqds.CS_RES_FAIL:
        self._cg_name = "fail";
      elif not control_status&meqds.CS_ACTIVE or \
           result_status in (meqds.CS_RES_WAIT,meqds.CS_RES_MISSING): 
        self._cg_name = "disabled";
      elif self._stepchild:
        self._cg_name = "stepchild";
      else:
        self._cg_name = None;
      # call update_debug to complete setting of color group (debug state
      # determines background)
      self._update_debug(node);
      ## # update status column
      ## self.setText(tb.icolumn("status"),node.control_status_string);
      # update breakpoint status pixmaps
      if control_status&meqds.CS_BREAKPOINT:
        self.setPixmap(tb.icolumn("breakpoint"),pixmaps.breakpoint.pm());
      elif control_status&meqds.CS_BREAKPOINT_SS:
        self.setPixmap(tb.icolumn("breakpoint"),pixmaps.forward_to.pm());
      else:
        self.setPixmap(tb.icolumn("breakpoint"),QPixmap());
      # update exec state pixmaps and rqid string
      es = meqds.CS_ES_state(control_status);
      self.setPixmap(tb.icolumn("execstate"),es[4].pm());
      if node.request_id is None:
        self.setText(tb.icolumn("execstate"),'');
      else:
        self.setText(tb.icolumn("execstate"),str(node.request_id));
      # update result status pixmap
      icol = tb.icolumn("result");
      if result_status == meqds.CS_RES_NONE:
        self.setPixmap(icol,QPixmap());
      elif result_status == meqds.CS_RES_OK:
        if control_status&meqds.CS_RETCACHE:
          if control_status&meqds.CS_CACHED:
            self.setPixmap(icol,pixmaps.blue_round_reload_return.pm());
          else:
            self.setPixmap(icol,pixmaps.green_return.pm());
        else:
          if control_status&meqds.CS_CACHED:
            self.setPixmap(icol,pixmaps.blue_round_reload.pm());
          else:
            self.setPixmap(icol,pixmaps.green_return.pm());
      elif result_status == meqds.CS_RES_WAIT:
        self.setPixmap(icol,pixmaps.blue_round_clock.pm());
      elif result_status == meqds.CS_RES_EMPTY:
        if control_status&meqds.CS_RETCACHE:
          self.setPixmap(icol,pixmaps.blue_round_empty_return.pm());
        else:
          self.setPixmap(icol,pixmaps.blue_round_empty.pm());
      elif result_status == meqds.CS_RES_MISSING:
        self.setPixmap(icol,pixmaps.grey_round_cross.pm());
      elif result_status == meqds.CS_RES_FAIL:
        self.setPixmap(icol,pixmaps.red_round_cross.pm());
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
      self.setPixmap(tb.icolumn("publish"),self._publish_pixmap);
      # update breakpoints menu
      try: menu = self._debug_bp_menu;
      except AttributeError: pass;
      else:
        _dprint(3,'node',self.node.name,'breakpoint mask is',self.node.breakpoint);
        for (item,bp) in self._debug_bp_items:
          menu.setItemChecked(item,(self.node.breakpoint&bp)!=0);
    
    def expand (self):
      if self._expanded:
        return;
      i1 = self;
      # format string for enumerating children -- need to use sufficient digits
      chform = '%%0%dd: %%s' % (math.floor(math.log10(len(self.node.children)))+1,);
      # generate items for each child
      for (key,ni) in self.node.children:
        if ni > 0:
          node = meqds.nodelist[ni];
          name = self.node.child_label_format() % (key,node.name);
          i1 = self.__class__(self.tb,node,name,self,i1);
        else:  # missing child, generate dummy item with <none> in it
          name = self.node.child_label_format() % (key,'<none>');
          i1 = QListViewItem(self,i1,name);
      for ni in self.node.step_children:
        node = meqds.nodelist[ni];
        name = "(" + node.name +")";
        i1 = self.__class__(self.tb,node,name,self,i1,stepchild=True);
      self._expanded = True;
      
    def xcurry (self,*args,**kwargs):
      cb = xcurry(*args,**kwargs);
      self._callbacks.append(cb);
      return cb;
      
    def _fill_menu (self,menu,which,separator=False):
      """adds node-related actions defined in the TreeBrowser to the
      specified menu."""
      acts = self.tb.get_action_list(which);
      acts.sort(); # sorts by priority
      for (pri,action) in acts:
        if action is None:                # add separator
          separator = True;
        elif isinstance(action,QAction):  # add regular action 
          if separator:
            menu.insertSeparator();
            separator = False;
          action.addTo(menu);
        elif issubclass(action,NodeAction):            # assume NodeAction
          if action.applies_to_node(self.node):
            # instantiate action, add to menu if successful
            try:
              na = action(self,menu,separator=separator);
            except:
              _dprint(1,'error adding action to node menu:',sys.exc_info());
            else:
              self._menu_actions.append(na);
              separator = False;
        else:
          raise TypeError,'unknown action type '+type(action);
    
    def debug_menu (self):
      try: menu = self._debug_menu;
      except AttributeError:
        node = self.node;
        menu = self._debug_menu = QPopupMenu();
        menu1 = self._debug_bp_menu = QPopupMenu();
        self._debug_bp_items = [];
        _dprint(3,'node',node.name,'breakpoint mask is',node.breakpoint);
        for st in meqds.CS_ES_statelist:
          title = ''.join(('at ',node.name,':',st[1]));
          bpmask = meqds.breakpoint_mask(st[0]);
          cb = self.xcurry(meqds.set_node_breakpoint,(node.nodeindex,bpmask),_argslice=slice(0));
          item = menu1.insertItem(st[4].iconset(),title,cb);
          menu1.setItemChecked(item,(node.breakpoint&bpmask)!=0);
          self._debug_bp_items.append((item,bpmask));
        menu1.insertItem(pixmaps.node_any.iconset(),''.join(("at ",node.name,':all')),self.xcurry(\
              meqds.set_node_breakpoint,(node.nodeindex,meqds.BP_ALL),_argslice=slice(0)));
        menu.insertItem(pixmaps.breakpoint.iconset(),"Set &breakpoint at",menu1);
        menu.insertItem(pixmaps.roadsign_nolimit.iconset(),"Clear &all breakpoints at "+node.name,self.xcurry(\
              meqds.clear_node_breakpoint,(node.nodeindex,meqds.BP_ALL),_argslice=slice(0)));
        self._fill_menu(menu,"debug",separator=True);
      return menu;
      
    def context_menu (self):
      try: menu = self._context_menu;
      except AttributeError:
        # create menu on the fly when first called for this item
        node = self.node;
        menu = self._context_menu = QPopupMenu();
        # insert title
        menu.insertItem("%s: %s"%(node.name,node.classname));
        # menu.insertItem(pixmaps.info_blue_round.iconset(),"Show icon reference...",self.tb.show_icon_reference);
        # insert viewer list submenus
        viewer_list = Grid.Services.getViewerList(meqds.NodeClass(node.classname));
        if viewer_list: 
          menu.insertSeparator();
          # create display submenus
          menu1 = self._display_menu1 = QPopupMenu();
          menu2 = self._display_menu2 = QPopupMenu();
          menu.insertItem(pixmaps.viewmag.iconset(),"Display with",menu1);
          menu.insertItem(pixmaps.viewmag_plus.iconset(),"New display with",menu2);
          for v in viewer_list:
            # create entry for viewer
            name = getattr(v,'viewer_name',v.__name__);
            try: icon = v.icon();
            except AttributeError: icon = QIconSet();
            # add entry to both menus ("Display with" and "New display with")
            menu1.insertItem(icon,name,
              self.xcurry(self._add_node_viewer,viewer=v));
            menu2.insertItem(icon,name,
              self.xcurry(self._add_node_viewer,viewer=v,newcell=True));
        # add node actions
        self._fill_menu(menu,"node",separator=True);
        # add debugging menu
        menu.insertItem(pixmaps.breakpoint.iconset(),"Debug",self.debug_menu());
      # refresh all node actions
      map(lambda a:a.update(menu,self.node),self._menu_actions);
      return menu;
      
    def paintCell (self,painter,cg,column,width,align):
      return QListViewItem.paintCell(self,painter,self._color_group or cg,column,width,align);

    def clear_children (parent):
      """Recursively cleans up all child items of the given parent, in
      preparation for deleting them. This is mainly done to remove cyclic
      references caused by the NodeItem._callbacks list.""";
      item = parent.firstChild();
      while item:
        _dprint(2,item.text(0),item);
        try: item.cleanup();
        except AttributeError: pass;
        TreeBrowser.NodeItem.clear_children(item);
        item = item.nextSibling();
    clear_children = staticmethod(clear_children);
    
  ######################################################################################################
  # start of TreeBrowser implementation    
  ######################################################################################################
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
                     self._item_clicked);
    QObject.connect(nlv,SIGNAL('contextMenuRequested(QListViewItem*,const QPoint &,int)'),
                     self._show_context_menu);
    QObject.connect(nlv,SIGNAL('currentChanged(QListViewItem*)'),self._set_recent_item);
    # map the get_drag_item methods
    nlv.get_drag_item = self.get_drag_item;
    nlv.get_drag_item_type = self.get_drag_item_type;
    #---------------------- setup color groups for items
    self._cg = {};
    # color group for stopped nodes
    stopcolor = { -1:None, 0:QColor("lightblue"), 1:QColor("lightblue2") };
    for stopped in stopcolor.keys():
      # color group for normal nodes
      self._cg[(None,stopped)] = self._new_colorgroup(stopcolor[stopped]);
      # color groups for stepchildren
      self._cg[("stepchild",stopped)] = \
        self._new_colorgroup(stopcolor[stopped],QColor("grey40"));
      # color groups for nodes with missing data
      self._cg[("disabled",stopped)] = \
        self._new_colorgroup(stopcolor[stopped],QColor("grey50"));
      # color groups for failed nodes
      self._cg[("fail",stopped)] = \
        self._new_colorgroup(stopcolor[stopped],QColor("red"));
    # ---------------------- setup toolbars, QActions, menus, etc.
    # scan all modules for define_treebrowser_actions method, and call them all
    self._actions = {};
    funcs = sets.Set();
    for (name,mod) in sys.modules.iteritems():
      _dprint(4,'looking for treebrowser actions in',name);
      try: 
        if callable(mod.define_treebrowser_actions):
          _dprint(3,'tb action found in',name,'adding to set');
          funcs.add(mod.define_treebrowser_actions);
      except AttributeError: pass;
    _dprint(1,len(funcs),'unique treebrowser action-definition methods found');
    for f in funcs:
      f(self);
    # --- now, build up toolbar from defined actions
    mainwin = parent;
    while mainwin and not isinstance(mainwin,QMainWindow):
      mainwin = mainwin.parent();
    self._toolbar = QToolBar(mainwin,"Trees");
    self._toolbar_actions = [];
    tba = self.get_action_list("toolbar");
    tba.sort();
    prev_sep = True; # flag: previous entry is a separator, true at top
    for (pri,action) in tba:
      if action is None:
        if not have_sep: 
          self._toolbar.addSeparator();
          have_sep = True;
      elif action == "stretch":
        stretch = QWidget(self._toolbar);
        self._toolbar.setStretchableWidget(stretch);
      elif isinstance(action,QAction):
        self._toolbar_actions.append(action);
        action.addTo(self._toolbar);
        action.setEnabled(False);
        have_sep = False;

    # ---------------------- other internal state
    self._column_map = {};
    self._recent_item = None;
    self._current_debug_stack = None;
    self._callbacks = [];
    #----------------------- public state
    self.app_state = None;
    self.debug_level = 0;
    self.is_connected = self.is_loaded = self.is_running = self.is_stopped = False;
    
  def update_nodelist (self):
    # init columns if calling for the first time
    # (we don't do it in the constructor because the number of columns
    # depends on the available node actions)
    # init one column per registered action; first one is always node name
    if not self._nlv.columns(): 
      self.add_column("node");
      self.add_column("publish",'',24,iconset=pixmaps.publish.iconset());
      self.add_column("breakpoint",'',24,iconset=pixmaps.breakpoint.iconset());
      self.add_column("execstate","xs/rqid");
      self.add_column("result",'',24,iconset=pixmaps.blue_round_result.iconset());
      icol = self.add_column("class");
      self._icol_disable = icol;
      icol = self.add_column("index",width=60);
      self._nlv.setColumnAlignment(icol,Qt.AlignRight);
    # clear view
    _dprint(1,"updating node list");
    self.clear();
    self.is_loaded = True;
    self._update_all_controls();
    # add forest state and bookmarks
    self._fst_item = StickyListViewItem(self._nlv,"Forest state",key=5);
    self._fst_item.setPixmap(0,pixmaps.view_tree.pm());
    self._fst_item._udi = '/forest';
    self._fst_item.setDragEnabled(True);
    self._fst_item._item_event_handler = {};
   # left-click: view
    self._fst_item._item_event_handler[('click',1)] = xcurry(self._view_forest_state);
    # middle-click: new view
    self._fst_item._item_event_handler[('click',4)] = xcurry(self._view_forest_state,newcell=True);
    
    # self._bkmark_item = StickyListViewItem(self._nlv,"Bookmarks",key=60);
    # self._bkmark_item.setPixmap(0,pixmaps.bookmark.pm());
    # add nodelist views
    nodelist = meqds.nodelist;
    self._recent_item = None;
    all_item  = StickyListViewItem(self._nlv,"All nodes (%d)"%len(nodelist),key=10);
    all_item._no_auto_open = True;
    all_item._iter_nodes = nodelist.iternodes();
    all_item.setExpandable(True);
    rootnodes = nodelist.rootnodes();
    rootitem  = self._nlv_rootitem = \
      StickyListViewItem(self._nlv,all_item,"Root nodes (%d)"%len(rootnodes),key=30);
    rootitem._iter_nodes = iter(rootnodes);
    rootitem.setExpandable(True);
    classes = nodelist.classes();
    cls_item  = item = \
      StickyListViewItem(self._nlv,rootitem,"By class (%d)"%len(classes),key=20);
    cls_item._no_auto_open = True;
    for (cls,nodes) in classes.iteritems():
      if len(nodes) == 1:
        item = self.NodeItem(self,nodes[0],nodes[0].name,cls_item,item);
      else:
        item = QListViewItem(cls_item,item,"%s (%d)"%(cls,len(nodes)));
        item.setText(self.icolumn("class"),cls);
        item.setExpandable(True);
        item._iter_nodes = iter(nodes);
      item._no_auto_open = True;
      
  def clear (self):
    _dprint(2,"clearing tree browser");
    self.is_loaded = False;
    self._nlv_rootitem = self._fst_item = self._bkmark_item = \
      self._recent_item = self._debug_node = \
      self._current_debug_stack = None;
    self.NodeItem.clear_children(self._nlv);
    self._nlv.clear();
    self._update_all_controls();
    
    
  def xcurry (self,*args,**kwargs):
    cb = xcurry(*args,**kwargs);
    self._callbacks.append(cb);
    return cb;
    
  def add_column (self,colname,caption=None,width=-1,iconset=None):
    """adds column to listview. Colname is column name, caption is displayed
    name (same as colname by default), width is >=0 for fixed width""";
    icol = self._nlv.columns();
    if caption is None:
      caption = colname;
    if iconset:
      self._nlv.addColumn(iconset,caption,width);
    else:
      self._nlv.addColumn(caption,width);
    self._column_map[colname] = (icol,width);
    return icol;
    
  def icolumn (self,colname):
    """returns column number for a given colname""";
    return self._column_map[colname][0];
    
  def show_column (self,colname,show=True):
    """shows or hides the column specified by name""";
    try: (icol,width) = self._column_map[colname];
    except KeyError,AttributeError: return;
    # make column visible or not
    if show: 
      if width >= 0:
        self._nlv.setColumnWidth(icol,width);
      else:
        self._nlv.setColumnWidthMode(icol,QListView.Maximum);
    else:
      self._nlv.setColumnWidthMode(icol,QListView.Manual);
      self._nlv.setColumnWidth(icol,0);
      
  def _update_all_controls (self):
    """updates state of toolbar and other controls based on app state""";
    _dprint(3,self.debug_level,self.is_connected,self.is_running,self.is_stopped);
    self._set_debug_control(self.debug_level>0);
    # toolbar
    for act in self._toolbar_actions:
      # call _is_visible() to setup visibility
      try:
        visible = act._is_visible();
      except AttributeError: pass;
      except:
        _dprint(0,'exception while calling _is_visible on tb action:',sys.exc_info());
        traceback.print_exc();
      else:
        _dprint(4,'action',act.text(),'visible:',enable);
        act.setVisible(visible);
      # call _is_enabled() to setup enabledness
      try:
        enable = act._is_enabled();
      except AttributeError: pass;
      except:
        _dprint(0,'exception while calling _is_enabled on tb action:',sys.exc_info());
        traceback.print_exc();
      else:
        _dprint(4,'action',act.text(),'enabled:',enable);
        act.setEnabled(enable);
    # show/hide the breakpoint column
    self.show_column("breakpoint",self.debug_level > 0);
    self.show_column("result",self.debug_level > 0);
    # show/hide the execstate column
    self.show_column("execstate",self.debug_level > 0 and self.is_running);

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
      self._qa_dbg_enable.setText("Disable tree debugger and continue");
      self._qa_dbg_enable.setMenuText("Disable tree &debugger");
      if not getattr(self,'_setting_debug_control',False):
        mqs().meq('Debug.Set.Level',record(debug_level=2,get_forest_status=True),wait=False);
    else:
      if not getattr(self,'_setting_debug_control',False):
        # confirm disable if in debugger
        if self._current_debug_stack:
          if QMessageBox.warning(None,"Disabling Tree Debugger",\
               """This will disable the debugger and release the tree. 
The tree will then ignore all breakpoints and run until it 
finishes executing the current request, or runs out of data.
You will not be able to interrupt this process.
Please press OK to confirm.""",QMessageBox.Ok,\
               QMessageBox.Cancel|QMessageBox.Default|QMessageBox.Escape) \
             != QMessageBox.Ok:
            self._set_debug_control(True);
            return;
        mqs().meq('Debug.Set.Level',record(debug_level=0,get_forest_status=True),wait=False);
      # really disable
      self.clear_debug_stack();
      self._qa_dbg_enable.setAccel(Qt.Key_F5);
      self._qa_dbg_enable.setText("Enable tree debugger");
      self._qa_dbg_enable.setMenuText("Enable tree &debugger");

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
    
  def get_drag_item (self,key):
    if key == '/forest':
      return meqgui.makeForestDataItem();
    elif key.startswith('/node'):
      (name,ni) = meqds.parse_node_udi(key);
      node = meqds.nodelist[name or ni];
      return meqgui.makeNodeDataItem(node);
      
  def get_drag_item_type (self,key):
    return Timba.Grid.DataItem;
 
  def wtop (self):
    return self._wtop;
    
  def wtoolbar (self):
    return self._toolbar;
    
  def connected (self,conn,auto_request=True):
    self.emit(PYSIGNAL("connected()"),(conn,));
    self.is_connected = conn;
    if conn is True:
      self._update_all_controls();
      if auto_request:
        self._request_nodelist();
    else:
      self.clear();

  def update_app_state (self,state):
    self.app_state = state;
    self.is_running = state in (AppState.Debug,AppState.Stream,AppState.Execute);
    self.is_stopped = state == AppState.Debug;
    self._update_all_controls();
    
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
      if meqds.nodelist and fst.debug_stack:
        for (n,frame) in enumerate(fst.debug_stack):
          try: node = meqds.nodelist[frame.nodeindex];
          except KeyError: continue;
          # top (most recently stopped) node gets special treatment
          if not n:
            self._debug_node = weakref_proxy(node);
          node._stopped = n;
          debug_stack.add(node.nodeindex);
          if hasattr(frame,'state'):
            node.update_state(frame.state);
          else:
            node.update_status(frame.control_status);
    else:
      _dprint(2,"debugging disabled");
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
    # reset all controls
    self._update_all_controls();
        
  def clear_debug_stack (self,clearset=None):
    """Clears highlighting of stopped nodes. If a set is supplied, that 
    set is cleared, otherwise the current set is used""";
    if clearset is None:
      clearset = self._current_debug_stack;
      self._current_debug_stack = None;
    if clearset:
      for ni in clearset:
        try: node = meqds.nodelist[ni];
        except keyError: continue;
        delattr(node,'_stopped');
        node.emit(PYSIGNAL("update_debug()"),(node,));
  
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
    if best_item:
      self._nlv.ensureItemVisible(best_item);
    
  def expand_active_tree (self,start=None,active_ni=None):
    """expands all items from start (the "Root nodes" menu, if start=None) that
    correspond to active (i.e. non-idle) nodes. If 'active' is specified and is a node, 
    returns the item corresponding to that node (if it finds it)."""
    if start is None:
      try: start = self._nlv_rootitem;
      except AttributeError: return;
      if not start:
        return None;
    active_item = None;
    self._nlv.setOpen(start,True);
    # recursively expand all non-idle child nodes
    item = start.firstChild();
    while item:
      if isinstance(item,self.NodeItem):
        if item.node.nodeindex == active_ni and not active_item:   
          self._nlv.ensureItemVisible(item);
          active_item = item;
        if (item.node.control_status&meqds.CS_MASK_EXECSTATE) != meqds.CS_ES_IDLE:
          i1 = self.expand_active_tree(item,active_ni);
          active_item = active_item or i1;
      item = item.nextSibling();
    return active_item;
    
  def _view_forest_state (self,viewer=None,**kws):
    _dprint(2,"adding viewer for forest state");
    item = Grid.DataItem('/forest',name='Forest state',caption='<b>Forest state</b>',
                          desc='State of forest',data=meqds.get_forest_state(),
                          refresh=meqds.request_forest_state,viewer=viewer);
    Grid.addDataItem(item,show_gw=True,**kws);
  
  # slot: called to show a context menu for a browser item
  def _item_event (self,item,event,*args,**kw):
    handlers = getattr(item,'_item_event_handler',None);
    if handlers:
      hh = handlers.get(event,None);
      if callable(hh):
        hh(*args,**kw);
  
  def _show_context_menu (self,item,point,col):
    _dprint(3,item,point,col);
    self._item_event(item,'menu',point,col);
      
  def _item_clicked (self,button,item,point,col):
    _dprint(3,button,item,point,col);
    if button == 1 or button == 4:
      self._recent_item = item;
    self._item_event(item,('click',button),point,col);
        
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
    _dprint(1,"requesting node list and forest state");
    meqds.request_forest_state();
    meqds.request_nodelist();
    
  def _debug_single_step (self):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._update_all_controls();
    mqs().meq('Debug.Single.Step',record(),wait=False);
  
  def _debug_next_node (self):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._update_all_controls();
    mqs().meq('Debug.Next.Node',record(),wait=False);
    
  def _debug_until_node (self,node):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._update_all_controls();
    mqs().meq('Debug.Until.Node',record(nodeindex=node.nodeindex),wait=False);
  
  def _debug_continue (self):
    self.clear_debug_stack();
    self.is_stopped = False;
    self._update_all_controls();
    mqs().meq('Debug.Continue',record(),wait=False);
    
  def _debug_pause (self):
    mqs().meq('Debug.Pause',record(),wait=False);

  def add_action (self,action,order=1000,where="toolbar",callback=None):
    if callback:
      QObject.connect(action,SIGNAL("activated()"),callback);
    self._actions.setdefault(where,[]).append((order,action));
    
  def add_separator (self,order=1000,where="toolbar"):
    self._actions.setdefault(where,[]).append((order,None));
    
  def add_stretch (self,order=1000,where="toolbar"):
    self._actions.setdefault(where,[]).append((order,"stretch"));
    
  def get_action_list (self,which):
    return self._actions.get(which,[]);

  def save_forest_dialog (self):
    try: dialog = self._save_forest_dialog;
    except AttributeError:
      self._save_forest_dialog = dialog = QFileDialog(self.wtop(),"save dialog",True);
      dialog.resize(800,500);
      dialog.setMode(QFileDialog.AnyFile);
      dialog.setFilters("Forests (*.forest *.meqforest);;All files (*.*)");
      dialog.setViewMode(QFileDialog.Detail);
      dialog.setCaption("Save forest");
    else:
      dialog.rereadDir();
    if dialog.exec_loop() == QDialog.Accepted:
      fname = str(dialog.selectedFile());
      rec = record(file_name=fname,get_forest_status=True);
      mqs().meq('Save.Forest',rec,wait=False);

  def load_forest_dialog (self):
    try: dialog = self._load_forest_dialog;
    except AttributeError:
      self._load_forest_dialog = dialog = QFileDialog(self.wtop(),"load dialog",True);
      dialog.resize(800,500);
      dialog.setMode(QFileDialog.ExistingFile);
      dialog.setFilters("Forests (*.forest *.meqforest);;All files (*.*)");
      dialog.setViewMode(QFileDialog.Detail);
      dialog.setCaption("Load forest");
    else:
      dialog.rereadDir();
    if dialog.exec_loop() == QDialog.Accepted:
      fname = str(dialog.selectedFile());
      rec = record(file_name=fname,get_forest_status=True);
      mqs().meq('Load.Forest',rec,wait=False);
      self._request_nodelist();
      
  def show_icon_reference (self):
    try: iconref = self._icon_reference;
    except AttributeError:
      iconref = self._icon_reference = NodeIconReference(self.wtop().topLevelWidget());
    iconref.show();
      
class NodeIconReference (QMainWindow):
  RefList = None;
  def __init__ (self,parent):
    fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
    fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title;
    QMainWindow.__init__(self,parent,"iconref",fl);
    self.setCaption("Node Icon Reference");
    self.setIcon(pixmaps.info_blue_round.pm());
    # define list
    if not self.RefList:
      self.RefList = [ \
        (None,"      Node exec state icons:"),
        (None,None) ];
      # add state icons
      self.RefList += [ (pixmap,desc) for (val,name,char,desc,pixmap) in meqds.CS_ES_statelist ];
      # add result icons
      self.RefList += [ \
        (None,None),\
        (None,"      Node result icons:"),
        (None,None),\
        (None,"no node result (no icon)"),
        (pixmaps.blue_round_reload,"new result, cached"),
        (pixmaps.blue_round_empty,"new empty result, cached"),
        (pixmaps.green_return,"new result, not cached"),
        (pixmaps.blue_round_reload_return,"reused result from cache"),
        (pixmaps.blue_round_empty_return,"reused empty result from cache"),
        (pixmaps.blue_round_clock,"'wait' result"),
        (pixmaps.grey_round_cross,"'missing' result"),
        (pixmaps.red_round_cross,"'fail' result"),
        (None,None),\
        (None,"      Miscellaneous icons:"),
        (None,None),\
        (pixmaps.breakpoint,"node has breakpoints"),
        (pixmaps.forward_to,"node has a temp ('until') breakpoint"),
        (pixmaps.publish,"node is publishing snapshots"),
        (pixmaps.publish_active,"node state is updated (brief flash)"),
        (pixmaps.cancel,"node is disabled") ];
    #
    canvas = QGrid(2,self);
    canvas.setMargin(3);
    canvas.setSpacing(3);
    self.setCentralWidget(canvas);
    for (pixmap,text) in self.RefList:
      if text is None:  # draw separator 
        icon = QWidget(canvas); 
        label = QFrame(canvas);
        label.setFrameShape(QFrame.HLine+QFrame.Sunken);
      else: # draw entry
        if pixmap is None:
          icon = QWidget(canvas);
        else:
          icon = QLabel(canvas);
          icon.setPixmap(pixmap.pm());
        label = QLabel(text,canvas);  
      # make icon non-resizable
      icon.setSizePolicy(QSizePolicy(0,0));
    canvas.setSizePolicy(QSizePolicy(0,0));
    self.setSizePolicy(QSizePolicy(0,0));
  def mouseReleaseEvent (self,ev):
    self.hide();
    
def define_treebrowser_actions (tb):
  _dprint(1,'defining standard treebrowser actions');
  parent = tb.wtop();
  # populate the toolbar
  # Refresh
  refresh = tb._qa_refresh = QAction("Refresh",pixmaps.refresh.iconset(),"Refresh node list",Qt.Key_F2,parent);
  refresh._is_enabled = lambda tb=tb: tb.is_connected;
  tb.add_action(refresh,10,callback=tb._request_nodelist);
  tb.add_separator(20);
  # Save and load
  qa_load = tb._qa_load = QAction("Load",pixmaps.file_open.iconset(),"Load forest",0,parent);
  qa_save = tb._qa_save = QAction("Save",pixmaps.file_save.iconset(),"Save forest",0,parent);
  qa_load._is_enabled = qa_save._is_enabled = lambda tb=tb: tb.is_connected and tb.app_state == AppState.Idle;
  tb.add_action(qa_load,30,callback=tb.load_forest_dialog);
  tb.add_action(qa_save,40,callback=tb.save_forest_dialog);
  tb.add_separator(50);
  # Enable debugger
  dbg_enable = tb._qa_dbg_enable = QAction("Enable tree debugger",pixmaps.debugger.iconset(),"Enable tree &debugger",Qt.Key_F5,parent,"",True);
  QObject.connect(dbg_enable,SIGNAL("toggled(bool)"),tb._debug_enable_slot);
  QObject.connect(tb,PYSIGNAL("debug_enabled()"),dbg_enable.setOn);
  dbg_enable._is_enabled = lambda tb=tb: tb.is_connected;
  tb.add_action(dbg_enable,60);
  # Pause
  pause = QAction("Pause",pixmaps.pause.iconset(),"&Pause",Qt.Key_F6,parent);
  pause._is_visible = lambda tb=tb: tb.is_connected and tb.debug_level>0;
  pause._is_enabled = lambda tb=tb: tb.is_running and not tb.is_stopped;
  tb.add_action(pause,70,callback=tb._debug_pause);
  tb.add_separator(80);
  # Debug action group
  ag_debug = tb._qa_dbg_tools = QActionGroup(parent);
  ag_debug.setText("Debugger tools");
  dbgcont  = QAction("Continue",pixmaps.right_2triangles.iconset(),"&Continue",Qt.Key_F6+Qt.SHIFT,parent);      
  QObject.connect(dbgcont,SIGNAL("activated()"),tb._debug_continue);
  dbgstep  = QAction("Step",pixmaps.down_triangle.iconset(),"&Step",Qt.Key_F7,parent);      
  QObject.connect(dbgstep,SIGNAL("activated()"),tb._debug_single_step);
  dbgnext  = QAction("Step to next node",pixmaps.down_2triangles.iconset(),"Step to &next node",Qt.Key_F8,parent);      
  QObject.connect(dbgnext,SIGNAL("activated()"),tb._debug_next_node);
  ag_debug._is_visible = lambda tb=tb: tb.is_connected and tb.debug_level>0;
  ag_debug._is_enabled = lambda tb=tb: tb.is_loaded and tb.is_stopped;
  ag_debug.add(dbgcont);
  ag_debug.add(dbgstep);
  ag_debug.add(dbgnext);
  tb.add_action(ag_debug,90);
  
  # show node icon reference
  tb.add_stretch(1000);
  show_help = QAction("Show icon reference",pixmaps.info_blue_round.iconset(),"Show icon &reference...",Qt.CTRL+Qt.Key_F1,parent);
  QObject.connect(show_help,SIGNAL("activated()"),tb.show_icon_reference);
  show_help._is_enabled = lambda tb=tb:True;
  tb.add_action(show_help,1010);
  tb.add_action(show_help,5,where="node");
  
  # populate node context menu
  tb.add_action(NA_NodeDisable,10,where="node");
  tb.add_action(NA_NodePublish,20,where="node");

  # populate debug context sub-menu
  tb.add_action(NA_ContinueUntil,10,where="debug");
  tb.add_action(ag_debug,20,where="debug");

class NodeAction (object):
  """NodeAction is a class implementing a node-associated action.""";
  # static attributes of action
  # these are meant to be redefined by subclasses
  text = 'unknown action';
  iconset = None;
  nodeclass = None;  # None means all nodes; else assign meqds.NodeClass('class');
  # static methods describing properties of this action
  def applies_to_node (self,node):
    _dprint(3,'nodeclass',self.nodeclass,'applies to',node,'?');
    if self.nodeclass is None:
      return True;
    if isinstance(self.nodeclass,str):
      self.nodeclass = meqds.NodeClass(self.nodeclass);
    _dprint(3,self.nodeclass,meqds.NodeClass(node.classname));
    try: applies = issubclass(meqds.NodeClass(node.classname),self.nodeclass);
    except: applies = False;
    _dprint(3,'applies:',applies);
    return applies;
  applies_to_node = classmethod(applies_to_node);
  
  def __init__ (self,item,menu,callback=None,separator=False):
    """instantiates action and adds it to the given menu.
    item is a TreeBrowser.NodeItem with which the menu is associated."""
    self.item = weakref_proxy(item);
    self.node = weakref_proxy(item.node);
    self.tb   = weakref_proxy(item.tb);
    if separator:
      menu.insertSeparator();
    self._callback = callback or xcurry(self.activate,_args=(self.node,));
    if self.iconset:
      self.item_id = menu.insertItem(self.iconset(),self.text,self._callback);
    else:
      self.item_id = menu.insertItem(self.text,self._callback);
      
  def is_checked (self,node):
    return None;
    
  def is_enabled (self,node):
    return True;
      
  def update (self,menu,node):
    """this is called whenever a menu is being displayed. Subclasses may
    redefine this to set up the item as appropriate
    The node argument defines which node the action is being applied to, or None 
    if the action is global. For actions residing in context menus, node is the 
    same as self.node.""";
    # enable/disable item
    print self;
    menu.setItemEnabled(self.item_id,self.is_enabled(node));
    # if is_checked returns not None, set item as checked/unchecked
    checked = self.is_checked(node);
    if checked is not None:
      menu.setItemChecked(self.item_id,checked);
      
  def activate (self,node):
    """callback: called whenever the menu item is selected. 
    The node argument defines which node the action is being applied to, or None 
    if the action is global. For actions residing in context menus, node is the 
    same as self.node.""";
    pass;
      
class NA_NodeDisable (NodeAction):
  text = "Disable";
  iconset = pixmaps.cancel.iconset;
  def activate (self,node):
    cs = node.control_status ^ meqds.CS_ACTIVE;
    meqds.set_node_state(node,control_status=cs);
  # define is_checked as a property that is computed on-the-fly
  def is_checked (self,node):
    return not node.is_active();

class NA_NodePublish (NodeAction):
  text = "Publish";
  iconset = pixmaps.publish.iconset;
  def activate (self,node):
    meqds.enable_node_publish(node,not node.is_publishing());
  def is_checked (self,node):
    return node.is_publishing();

class NA_ContinueUntil (NodeAction):
  text = "Continue until";
  iconset = pixmaps.forward_to.iconset;
  def __init__ (self,item,menu,**kw):
    NodeAction.__init__(self,item,menu,**kw);
    menu.changeItem(self.item_id,"Continue &until "+item.node.name);
  def activate (self,node):
    self.tb._debug_until_node(node);
  def is_enabled (self,node):
    return self.tb.debug_level>0 and self.tb.is_running and self.tb.is_stopped;
