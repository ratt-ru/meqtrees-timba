#!/usr/bin/python

from Timba.dmi import *
from Timba.GUI.app_proxy_gui import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba.GUI.browsers import *
from Timba.GUI import treebrowser
from Timba.GUI import tdlgui
from Timba.GUI.procstatuswidget import *
from Timba.GUI import meqgui 
from Timba.GUI import bookmarks 
from Timba.GUI import connect_meqtimba_dialog 
from Timba.GUI import widgets 
from Timba import Grid
from Timba import TDL

import weakref
import math
import sets
import re
import os
import os.path
import signal
import traceback

_dbg = verbosity(0,name='gui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

makeNodeDataItem = meqgui.makeNodeDataItem;

# splash screen

#_mainapp = mainapp();
#_splash_screen = QSplashScreen(pixmaps.trees48x48.pm());
#_splash_screen.show();
#_splash_screen.message("Starting MeqTimba Browser");

# global symbol: meqserver object; initialized when a meqserver_gui
# is constructed
mqs = None;

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
    treebrowser.AppState.Idle: pixmaps.grey_cross,
    treebrowser.AppState.Stream: pixmaps.spigot,
    treebrowser.AppState.Execute: pixmaps.gear,
    treebrowser.AppState.Debug: pixmaps.breakpoint };

  def __init__(self,app,*args,**kwargs):
    meqds.set_meqserver(app);
    global mqs;
    self.mqs = mqs = app;
    self.mqs.track_results(False);
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    # add handlers for various application events
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("process.status",self.ce_ProcessStatus);
    self._add_ce_handler("app.result.node.get.state",self.ce_NodeState);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("app.update.status.num.tiles",self.ce_UpdateAppStatus);
    
  def populate (self,main_parent=None,*args,**kwargs):
    # init icons
    pixmaps.load_icons('treebrowser');
    
    app_proxy_gui.populate(self,main_parent=main_parent,*args,**kwargs);
    self.setIcon(pixmaps.trees48x48.pm());
    self.set_verbose(self.get_verbose());
    
    _dprint(2,"meqserver-specifc init"); 
    # add Tree browser panel
    self.tb_panel = self.PanelizedWindow(self.splitter,"Trees","Trees",pixmaps.view_tree.iconset());
    self.treebrowser = treebrowser.TreeBrowser(self.tb_panel);
    QObject.connect(self.tb_panel,PYSIGNAL("visible()"),
          self.treebrowser.wtoolbar().setShown);
    
    # self.add_tab(self.treebrowser.wtop(),"Trees",index=1);
    self.splitter.moveToFirst(self.tb_panel);
    self.splitter.setResizeMode(self.tb_panel,QSplitter.KeepSize);
    
    self.splitter.setSizes([100,300,400]);
    
    self.maintab_panel.show();
    self.gw_panel.hide();
    self.tb_panel.hide();
    
    # add Snapshots tab
    self.resultlog = Logger(self,"node snapshot log",limit=1000,scroll=False,
          udi_root='snapshot');
    self.resultlog.wtop()._newres_iconset  = pixmaps.gear.iconset();
    self.resultlog.wtop()._newres_label    = "Snapshots";
    self.resultlog.wtop()._newresults      = False;
    self.add_tab(self.resultlog.wtop(),"Snapshots",index=2);
    QObject.connect(self.resultlog.wlistview(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    
    # create main toolbar
    self.maintoolbar = QToolBar(self,"Panels");
    self.qa_viewpanels = QActionGroup(self);
    self.qa_viewpanels.setExclusive(False);
    
    # populate it with view controls
    for panel in (self.tb_panel,self.maintab_panel,self.gw_panel):
      panel.visQAction(self.qa_viewpanels);
      panel.makeMinButton(self.maintoolbar);
    dum = QWidget(self.maintoolbar);
    self.maintoolbar.setStretchableWidget(dum);
    self._whatsthisbutton = QWhatsThis.whatsThisButton(self.maintoolbar);
    # self.moveDockWindow(self.maintoolbar,QMainWindow.DockTop);
    self.moveDockWindow(self.treebrowser.wtoolbar(),QMainWindow.DockLeft);
    self.treebrowser.wtoolbar().hide();
    
#     # add TDL editor panel
#     self.tdledit = tdl_editor.TDLEditor(self,"tdl editor tab");
#     self.add_tab(self.tdledit,"TDL");
#     QObject.connect(self.tdledit,PYSIGNAL("loadedFile()"),self._set_tdl_pathname);
    
    # excluse ubiquotous events from the event logger
    self.eventlog.set_mask('!node.status.*;!process.status;'+self.eventlog.get_mask());
    
    # add dummy stretch, and a memory size widget
    self._wstat = ProcStatusWidget(self.statusbar);
    self._wstat.hide();
    dum = QWidget(self.statusbar);
    self.statusbar.addWidget(dum,10);
    self.statusbar.addWidget(self._wstat,0);
    
    # build menu bar
    self._menus = {};
    kernel_menu    = self._menus['MeqTimba'] = QPopupMenu(self);
    tdl_menu       = self._menus['TDL'] = QPopupMenu(self);
    bookmarks_menu = self._menus['Bookmarks'] = QPopupMenu(self);
    debug_menu     = self._menus['Debug'] = QPopupMenu(self);
    view_menu      = self._menus['View'] = QPopupMenu(self);
    help_menu      = self._menus['Help'] = QPopupMenu(self);

    menubar = self.menuBar();    
    kernel_menu_id = menubar.insertItem("&MeqTimba",kernel_menu);
    kernel_menu_id = menubar.insertItem("&TDL",tdl_menu);
    bookmarks_menu_id = menubar.insertItem("&Bookmarks",bookmarks_menu);
    debug_menu_id = menubar.insertItem("&Debug",debug_menu);
    window_menu_id = menubar.insertItem("&View",view_menu);
    menubar.insertSeparator();
    help_menu_id = menubar.insertItem("&Help",help_menu);
    
    # some menus only available when connected
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(menubar.setItemVisible,_args=(bookmarks_menu_id,True)));
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(menubar.setItemVisible,_args=(debug_menu_id,True)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(menubar.setItemVisible,_args=(bookmarks_menu_id,False)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(menubar.setItemVisible,_args=(debug_menu_id,False)));
    menubar.setItemVisible(bookmarks_menu_id,False);
    menubar.setItemVisible(debug_menu_id,False);

    # --- MeqTimba menu
    connect = QAction("Connect to kernel...",0,self);
    connect.addTo(kernel_menu);
    QObject.connect(self,PYSIGNAL("isConnected()"),connect.setDisabled);
    stopkern = QAction(pixmaps.red_round_cross.iconset(),"&Stop kernel process",0,self);
    QObject.connect(self,PYSIGNAL("isConnected()"),stopkern.setEnabled);
    QObject.connect(stopkern,SIGNAL("activated()"),self._stop_kernel);
    stopkern.addTo(kernel_menu);
    kernel_menu.insertSeparator();
    self.treebrowser._qa_refresh.addTo(kernel_menu);
    self.treebrowser._qa_load.addTo(kernel_menu);
    self.treebrowser._qa_save.addTo(kernel_menu);
    self._connect_dialog = connect_meqtimba_dialog.ConnectMeqKernel(self,\
        name="&Connect to MeqTimba kernel",modal=False);
    QObject.connect(self,PYSIGNAL("isConnected()"),self._connect_dialog.setHidden);
    QObject.connect(connect,SIGNAL("activated()"),self._connect_dialog.show);
    QObject.connect(self._connect_dialog,PYSIGNAL("startKernel()"),self._start_kernel);
    # --- find default path to kernel binary
    binname = "meqserver";
    for dirname in os.environ['PATH'].split(':'):
      filename = os.path.join(dirname,binname);
      if os.path.isfile(filename) and os.access(filename,os.X_OK):
        self._connect_dialog.set_default_path(filename);
        break;
    self._connect_dialog.show();
    
    # --- TDL menu
    loadtdl = QAction("Load TDL script...",0,self);
    loadtdl.addTo(tdl_menu);
    QObject.connect(loadtdl,SIGNAL("activated()"),self._load_tdl_script);
    runtdl = QAction("&Load && run TDL script...",Qt.ALT+Qt.Key_T,self);
    runtdl.addTo(tdl_menu);
    QObject.connect(self,PYSIGNAL("isConnected()"),runtdl.setEnabled);
    QObject.connect(runtdl,SIGNAL("activated()"),self._run_tdl_script);
    tdl_menu.insertSeparator();
    
    # --- View menu
    self.qa_viewpanels.addTo(view_menu);
#     showgw = QAction(pixmaps.view_split.iconset(),"&Gridded workspace",Qt.Key_F3,self);
#     showgw.addTo(view_menu);
#     showgw.setToggleAction(True);
#     QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),showgw.setOn);
#     QObject.connect(showgw,SIGNAL("toggled(bool)"),self.gw.show);
    view_menu.insertSeparator();
    # optional tab views
    self.resultlog.wtop()._show_qaction.addTo(view_menu);
    self.eventtab._show_qaction.addTo(view_menu);
    self.show_tab(self.eventtab,False);
#    self.tdledit._show_qaction.addTo(view_menu);
#    self.show_tab(self.tdledit,False);
    # process status view
    showps = QAction("&Process status",0,self);
    showps.addTo(view_menu);
    showps.setToggleAction(True);
    showps.setOn(False);
    QObject.connect(showps,SIGNAL("toggled(bool)"),self._wstat.setShown);
    QObject.connect(self._wstat,PYSIGNAL("shown()"),showps.setOn);
    
    # --- Bookmarks menu
    self._qa_addbkmark = addbkmark = QAction(pixmaps.bookmark_add.iconset(),"Add bookmark",Qt.ALT+Qt.Key_B,self);
    addbkmark.addTo(bookmarks_menu);
    self._qa_addpagemark = addpagemark = QAction(pixmaps.bookmark_toolbar.iconset(),"Add pagemark for this page",Qt.ALT+Qt.CTRL+Qt.Key_B,self);
    addpagemark.addTo(bookmarks_menu);
    self._qa_autopublish = autopublish = QAction(pixmaps.publish.iconset(),"Auto-publish loaded bookmarks",0,self);
    autopublish.addTo(bookmarks_menu);
    QObject.connect(addbkmark,SIGNAL("activated()"),self._add_bookmark);
    QObject.connect(addpagemark,SIGNAL("activated()"),self._add_pagemark);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("itemSelected()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),SIGNAL("currentChanged(QWidget*)"),self._gw_reset_bookmark_actions);
    addbkmark.setEnabled(False);
    addpagemark.setEnabled(False);
    autopublish.setToggleAction(True);
    autopublish.setOn(True);
    # bookmark manager
    bookmarks_menu.insertSeparator();
    self._bookmarks = bookmarks.BookmarkFolder("main",self,menu=bookmarks_menu,gui_parent=self);
    # copy of current bookmark record
    self._bookmarks_rec = None;
    QObject.connect(self._bookmarks,PYSIGNAL("updated()"),self._save_bookmarks);
    QObject.connect(self._bookmarks,PYSIGNAL("showBookmark()"),self._show_bookmark);
    QObject.connect(self._bookmarks,PYSIGNAL("showPagemark()"),self._show_pagemark);
    
    # --- Debug menu
    self.treebrowser._qa_dbg_enable.addTo(debug_menu);
    self.treebrowser._qa_dbg_tools.addTo(debug_menu);
    debug_menu.insertSeparator();
    attach_gdb = QAction("Attach binary debugger to kernel",0,self);
    attach_gdb.addTo(debug_menu);
    attach_gdb.setEnabled(False); # for now
    QObject.connect(attach_gdb,SIGNAL("activated()"),self._debug_kernel);
    QObject.connect(self,PYSIGNAL("isConnected()"),attach_gdb.setEnabled);
    
    # --- Help menu
    help_menu.insertItem(self._whatsthisbutton.iconSet(),
                              "What's &This",self.whatsThis,Qt.SHIFT+Qt.Key_F1);
    
    # populate menus from plugins                          
    # scan all modules for define_mainmenu_actions methods, and call them all
    self._actions = {};
    funcs = sets.Set();
    for (name,mod) in sys.modules.iteritems():
      _dprint(4,'looking for mainmenu actions in',name);
      try: 
        if callable(mod.define_mainmenu_actions):
          _dprint(3,'mainmenu action found in',name,'adding to set');
          funcs.add(mod.define_mainmenu_actions);
      except AttributeError: pass;
    _dprint(1,len(funcs),'unique mainmenu action-definition methods found');
    for f in funcs:
      f(self._menus,self);
      
    # finally, add standard stuff to bottom of menus
    kernel_menu.insertSeparator();
    exit = QAction(pixmaps.exit.iconset(),"&Quit browser",Qt.ALT+Qt.Key_Q,self);
    exit.addTo(kernel_menu);
    QObject.connect(exit,SIGNAL("activated()"),self.close);
    ## NB: uncomment the line below to have Ctrl+C handled through the GUI
    ## (confirmation dialog will be displayed if running a kernel)
    # signal.signal(signal.SIGINT,self.xcurry(self.close));
 
    # subscribe to updates of forest state
    meqds.subscribe_forest_state(self._update_forest_state);
    # clear the splash screen
    # _splash_screen.finish(self);
    # add signal handler for SIGCHLD
    signal.signal(signal.SIGCHLD,self._sigchld_handler);
    self._kernel_pid = self._kernel_pathname = None;
    # other internal state
    self._have_nodelist = False;
    self._have_forest_state = False;
    self._autoreq_timer = QTimer(self);
    QObject.connect(self._autoreq_timer,SIGNAL("timeout()"),self._auto_update_request);
    # tdl tabs
    self._tdl_tabs = {};
    
  def _debug_kernel (self):
    pid = self.app.app_addr[2];    
    pathname = self._kernel_pathname or ( "/proc/%d/exe"%(pid,) );
    cmd = "ddd %s %d" % (pathname,pid);
    prompt = "Debugger command:";
    (cmd,ok) = QInputDialog.getText("Attaching debugger to kernel",prompt,QLineEdit.Normal,cmd);
    if ok:
      cmd = str(cmd);
      args = cmd.split(' ');
      self.log_message("running \""+cmd+"\"");
      os.spawnvp(os.P_NOWAIT,args[0],args);
    
  def _start_kernel (self,pathname,args):
    _dprint(0,pathname,args);
    if not os.path.isfile(pathname) or not os.access(pathname,os.X_OK):
      self.log_message("can't start kernel %s: not an executable file" % (pathname,), \
        category=Logger.Error);
      return;
    self.log_message(' '.join(('starting kernel process:',pathname,args)));
    self._kernel_pid = os.spawnv(os.P_NOWAIT,pathname,[pathname]+args.split(' '));
    self._kernel_pathname = pathname;
    
  def _stop_kernel (self):
    res = QMessageBox.warning(self,"Stopping MeqTimba kernel",
      """<p>The normal way to stop the MeqTimba kernel is by sending it
      a <tt>HALT</tt> command. If the kernel doesn't respond to this, we can always
      brute-force it with a <tt>KILL</tt> signal. Which method do you want to use?""",
      "HALT","KILL","Cancel",0,2);
    if res == 0:
      self.log_message('sending HALT command to kernel');
      self.app.halt();
    elif res == 1:
      pid = self.app.app_addr[2];    
      self.log_message('sending KILL signal to kernel process '+str(pid));
      os.kill(pid,signal.SIGKILL);
      
  def _run_tdl_script (self,run=False):
    self._load_tdl_script(True);
    
  class LoadTDLDialog (QFileDialog):
    def __init__ (self,*args):
      QFileDialog.__init__(self,*args);
      self.setMode(QFileDialog.ExistingFile);
      self.setFilters("TDL scripts (*.tdl *.py);;All files (*.*)");
      self.setViewMode(QFileDialog.Detail);
      self._replace = QCheckBox("close all currently loaded scripts first",self);
      self._replace.setChecked(True);
      self.addWidgets(None,self._replace,None);
    def set_replace_visible (self,visible):
      self._replace.setShown(visible);
    def get_replace (self):
      return self._replace.isOn();
    
  def _load_tdl_script (self,run=False):
    # tdlgui.run_tdl_script('tdl_test.tdl',self);
    # return;    
    try: dialog = self._run_tdl_dialog;
    except AttributeError:
      self._run_tdl_dialog = dialog = self.LoadTDLDialog(self,"load tdl dialog",True);
      dialog.resize(800,dialog.height());
    else:
      dialog.rereadDir();
    dialog.set_replace_visible(bool(self._tdl_tabs));
    if run:
      dialog.setCaption("Run TDL Script");
    else:
      dialog.setCaption("Load TDL Script");
    if dialog.exec_loop() == QDialog.Accepted:
      # close all TDL tabs if requested
      for (path,tab) in self._tdl_tabs.items():
        self.maintab.showPage(tab);
        if tab.confirm_close():
          del self._tdl_tabs[path];
          self.maintab.removePage(tab);
          tab.reparent(QWidget(),0,QPoint(0,0));
      # show this file
      self.show_tdl_file(str(dialog.selectedFile()),run=run);
      
  def show_tdl_file (self,pathname,run=False,mainfile=None):
    tab = self._tdl_tabs.get(pathname,None);
    if tab is None:
      _dprint(1,'No tab open, loading',pathname);
    # try to load file into new tab
      try:
        ff = file(pathname);
        text = ff.read();
        ff.close();
      except:
        (exctype,excvalue,tb) = sys.exc_info();
        _dprint(0,'exception loading TDL file',pathname,':');
        traceback.print_exc();
        QMessageBox.warning(self,"Error loading TDL script",
          """<p>Error reading <tt>%s</tt>:</p>
          <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
          QMessageBox.Ok);
        return;
      _dprint(1,'Creating editor tab for',pathname);
      # create editor tab with item
      tab = tdlgui.TDLEditor(self.maintab,close_button=True);
      tab.load_file(pathname,text,mainfile=mainfile);
      label = os.path.basename(pathname);
      if mainfile:
        label = '(' + label + ')';
      self.add_tab(tab,label);
      self._tdl_tabs[pathname] = tab;
      QObject.connect(tab,PYSIGNAL("fileSaved()"),self.curry(self._tdltab_change,tab));
      QObject.connect(tab,PYSIGNAL("hasErrors()"),self.curry(self._tdltab_errors,tab));
      QObject.connect(tab,PYSIGNAL("textModified()"),self.curry(self._tdltab_modified,tab));
      QObject.connect(tab,PYSIGNAL("fileClosed()"),self.curry(self._tdltab_close,tab));
      QObject.connect(tab,PYSIGNAL("showError()"),self.curry(self._tdltab_show_error,tab));
      QObject.connect(tab,PYSIGNAL("compileFile()"),self._tdl_compile_file);
      QObject.connect(tab,PYSIGNAL("fileChanged()"),self.curry(self._tdltab_reset_label,tab));
    else:
      _dprint(1,'we already have a tab for',pathname);
    self.show_tab(tab);
    self.gw_panel.hide();
    self.maintab_panel.show();
    # ok, we have a working tab now
    # run if requested
    if run and tab.compile_content():
      self.tb_panel.show();
    self.splitter.refresh();
    return tab;
    
  def _tdl_compile_file (self,filename):
    tab = self._tdl_tabs.get(filename,None);
    if tab is None:
      _dprint(1,'No tab open, loading',pathname);
      show_tdl_file(self,filename,run=True);
    else:
      self.show_tab(tab);
      if tab.compile_content():
        self.tb_panel.show();
    
  def _tdltab_reset_label (self,tab):
    name = os.path.basename(tab.get_filename());
    if tab.get_mainfile():
      name = '(' + name + ')';
    self.maintab.setTabLabel(tab,name);

  def _tdltab_change (self,tab,pathname):
    for (path,tab1) in self._tdl_tabs.iteritems():
      if tab is tab1:
        del self._tdl_tabs[path];
        self._tdl_tabs[pathname] = tab;
        self._tdltab_reset_label(tab);
        return;
    raise ValueError,"tab not found in map";
    
  def _tdltab_show_error (self,tab,index,filename,line,column):
    try:
      if getattr(self,'_tdltab_show_error_lock',False):
        return;
      self._tdltab_show_error_lock = True;
      if filename != tab.get_filename():
        mainfile = tab.get_mainfile() or tab.get_filename();
      else:
        mainfile = None;
      newtab = self.show_tdl_file(filename,mainfile=mainfile);
      newtab.set_error_list(tab.get_error_list(),show_item=False);
      newtab.show_error_number(index);
    finally:
      self._tdltab_show_error_lock = False;
  
  def _tdltab_errors (self,tab,nerr):
    # nerr indicates the # of errors in that actual file
    if nerr:
      self.maintab.setTabIconSet(tab,pixmaps.red_round_cross.iconset());
    else:
      self.maintab.setTabIconSet(tab,QIconSet());
    # get the full error list (which may include errors in other files) and
    # propagate it to slaved tabs
    errlist = tab.get_error_list();
    _dprint(1,len(errlist),"errors in",tab.get_filename(),tab.get_mainfile());
    if not tab.get_mainfile():
      filename = tab.get_filename();
      for tab1 in self._tdl_tabs.itervalues():
        if tab1.get_mainfile() == filename:
          tab1.set_error_list(errlist,show_item=False);
    
  def _tdltab_modified (self,tab,mod):
    if mod:
      self.maintab.setTabIconSet(tab,pixmaps.file_save.iconset());
    else:
      self.maintab.setTabIconSet(tab,QIconSet());
    
  def _tdltab_close (self,tab):
    for (path,tab1) in self._tdl_tabs.iteritems():
      if tab is tab1:
        self.maintab.showPage(tab);
        if tab.confirm_close():
          del self._tdl_tabs[path];
          self.maintab.removePage(tab);
          tab.reparent(QWidget(),0,QPoint(0,0));
        return;
    raise ValueError,"tab not found in map";

  def _verify_quit (self):
    if self._connected and self._kernel_pid:
      res = QMessageBox.warning(self,"Quit browser",
        """<p>We have started a kernel process (pid %d) from this browser. 
        Would you like to quit the browser only, or kill the kernel as 
        well?</p>""" % (self._kernel_pid,),
        "&Quit only","Quit && &kill","Cancel",1,2);
      if res == 0:
        return True;
      elif res == 1:
        os.kill(self._kernel_pid,signal.SIGKILL);
        return True;
      else:
        return False;
    else:
      return True;
      
  def closeEvent (self,event):
    if self._verify_quit():
      event.accept();
      mainapp().quit();
    else:
      event.ignore();
    
  def _sigchld_handler (self,sig,stackframe):
    _dprint(0,'signal',sig);
    wstat = os.waitpid(-1,os.WNOHANG);
    if wstat:
      (pid,st) = wstat;
      if pid == self._kernel_pid:
        msg = "kernel process " + str(pid);
        self._kernel_pid = None;
        cat = Logger.Error;
      else:
        msg = "child process " + str(pid);
        cat = Logger.Normal;
      if st&0x7F:
        msg += " killed by signal " + str(st&0x7F);
      else:
        msg += " exited with status " + str(st>>8);
      if st&0x80:
        msg += " (core dumped)";
      self.log_message(msg,category=cat);
    
  def _add_bookmark (self):
    item = Grid.Services.getHighlightedItem();
    if item is not None:
      if not meqgui.isBookmarkable(item.udi):
        caption = "Can't set bookmark";
        text = "Item <b>"+item.name+"<b> is transient and thus cannot be bookmarked";
        QMessageBox.warning(self,caption,text,QMessageBox.Cancel);
      else:
        vname = getattr(item.viewer,'viewer_name',item.viewer.__name__);
        name = "%s [%s]" % (item.name,vname);
        self._bookmarks.add(name,item.udi,item.viewer);
        
  def _add_pagemark (self):
    if self.gw.isVisible():
      page = self.gw.current_page();
      # if page has a fragile tag, get the name
      tag = page.get_fragile_tag();
      pagemarked = isinstance(tag,bookmarks.Pagemark) and tag.name;
      (nl,nrow,ncol) = page.current_layout();
      _dprint(2,'creating pagemark for layout',nrow,ncol);
      pagelist = [];
      for irow in range(nrow):
        for icol in range(ncol):
          cell = page.get_cell(irow,icol);
          item = cell.content_dataitem();
          if not cell.leader() and item and meqgui.isBookmarkable(item.udi):
            viewer = item.viewer;
            vname = getattr(viewer,'viewer_name',viewer.__name__);
            _dprint(3,irow,icol,item.udi,vname);
            pagelist.append(record(udi=item.udi,viewer=vname,pos=(irow,icol)));
      if pagelist:
        if page.is_auto_name():
          name = self._bookmarks.generatePageName();
        else:
          name = page.get_name();
        if pagemarked:
          prompt = """<p><b>Warning:</b> this pagemark is already defined as 
                   <i>"%s"</i>. Please press <i>Cancel</i> if you don't want
                   to set it again.</p> 
                   <p>Enter name for new pagemark:</p>""" % (pagemarked);
        else:
          prompt = "Enter name for new pagemark:";
        (name,ok) = QInputDialog.getText("Setting pagemark",prompt,
                    QLineEdit.Normal,name);
        if ok:
          name = str(name);
          pagemark = self._bookmarks.addPage(name,pagelist);
          page.set_fragile_tag(pagemark);
          page.set_name(name);
          page.set_icon(pixmaps.bookmark.iconset(),True);
      else:
        caption = "Can't set pagemark";
        text = "Current page does not have any bookmarkable content";
        QMessageBox.warning(self,caption,text,QMessageBox.Cancel);
      
  def _save_bookmarks (self):
    """saves current bookmarks to forest state""";
    _dprint(2,'saving bookmarks');
    self._bookmarks_rec = self._bookmarks.getList();
    meqds.set_forest_state("bookmarks",self._bookmarks_rec);
    
  def _show_bookmark (self,udi,viewer):
    pub = self._qa_autopublish.isOn();
    try:
      item = meqgui.makeDataItem(udi,viewer=viewer,publish=pub);
      Grid.addDataItem(item,show_gw=True);
    except:
      (exctype,excvalue,tb) = sys.exc_info();
      self.dprint(0,'exception',str(exctype),'while loading bookmark',udi);
      QMessageBox.warning(self,"Error loading bookmark",
        """<p>Cannot load bookmark:</p>
        <p><small><i>%s: %s</i><small></p>""" % (exctype.__name__,excvalue),
        QMessageBox.Ok);
    
  def _show_pagemark (self,pagemark):
    pub = self._qa_autopublish.isOn();
    self.gw.show();
    curpage = self.gw.current_page();
    # check if current page has content
    if curpage.has_content():
      # if page is still tagged with this pagemark, then do nothing
      # (this avoid multiple openings of the same pagemark)
      if curpage.get_fragile_tag() is pagemark and \
        QMessageBox.question(self,"Pagemark already loaded","""<p>This pagemark is already loaded. Load
          another copy in a new tab?</p>""",QMessageBox.Ok,QMessageBox.Cancel) \
           == QMessageBox.Cancel:
        return;
      curpage = self.gw.add_page(pagemark.name,pixmaps.bookmark.iconset());
    else: # no content, just use current page
      curpage.set_name(pagemark.name);
    # preset page layout
    (nrow,ncol) = (0,0);
    errs = [];
    # to avoid repetitive state updates when displaying multiple views of the
    # same item, ask meqds to hold node state requests
    meqds.hold_node_state_requests();
    try:
      for rec in pagemark.page:
        udi = getattr(rec,'udi',None);
        try:
          item = meqgui.makeDataItem(rec.udi,viewer=rec.viewer,publish=pub);
          Grid.addDataItem(item,position=(0,rec.pos[0],rec.pos[1]));
          nrow = max(nrow,rec.pos[0]);
          ncol = max(ncol,rec.pos[1]);
        except:
          (exctype,excvalue,tb) = sys.exc_info();
          self.dprint(0,'exception',str(exctype),'while loading pagemark item',rec);
          traceback.print_exc();
          errs.append((udi,exctype.__name__,excvalue));
    finally:
      # now release the node updates
      meqds.resume_node_state_requests();
    _dprint(2,'setting layout',nrow+1,ncol+1);
    curpage.set_layout(nrow+1,ncol+1);
    # display errors, if any
    if errs:
      message = """<p>Some items within this pagemark could not be loaded:</p><dl>""";
      for (udi,exctype,excvalue) in errs:
        message += "<dt><b>%s</b></dt> <dd><small><i>%s: %s</i><small></dd>" % (udi,exctype,excvalue);
      message += "</dl>";
      QMessageBox.warning(self,"Errors loading pagemark",message,QMessageBox.Ok);
    # self.gw.current_page().rearrange_cells();
    curpage.set_fragile_tag(pagemark);
    curpage.set_icon(pixmaps.bookmark.iconset(),True);
    
  def _gw_reset_bookmark_actions (self,dum=None):
    # figure out if Add bookmark is enabled
    enable_bkmark = enable_pgmark = False;
    if self._connected and self.gw.isVisible():
      item = Grid.Services.getHighlightedItem();
      if item:
        enable_bkmark = meqgui.isBookmarkable(item.udi);
        if enable_bkmark:
          self._qa_addbkmark.setMenuText("Add bookmark for "+item.name);
      enable_pgmark = self.gw.current_page().has_content();
    self._qa_addbkmark.setEnabled(enable_bkmark);
    if not enable_bkmark:
      self._qa_addbkmark.setMenuText("Add bookmark");
    self._qa_addpagemark.setEnabled(enable_pgmark);
        
  def _connected_event (self,ev,value):  
    app_proxy_gui._connected_event(self,ev,value);
    self._wstat.show();
    self._wstat.emit(PYSIGNAL("shown()"),(True,));
    self.treebrowser.clear();
    self.treebrowser.connected(True);  
    self.resultlog.connected(True);
    self._gw_reset_bookmark_actions();
    wtop = self.resultlog.wtop();
    self.maintab.changeTab(wtop,wtop._default_iconset,wtop._default_label);
    meqds.request_forest_state();
      
  def _disconnected_event (self,ev,value):  
    app_proxy_gui._disconnected_event(self,ev,value);
    self._autoreq_timer.stop();
    self._wstat.hide();
    self._wstat.emit(PYSIGNAL("shown()"),(False,));
    self.treebrowser.connected(False);  
    self.resultlog.connected(False);
    self._gw_reset_bookmark_actions();
    wtop = self.resultlog.wtop();
    self.maintab.changeTab(wtop,wtop._default_iconset,wtop._default_label);
    
  def ce_ProcessStatus (self,ev,value):
    _dprint(5,'status:',ev,value);
    self._wstat.setStatus(map(int,value));
    
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
    # call top-level handler
    app_proxy_gui.handleAppEvent(self,ev,value);
    # check for generic event contents
    if isinstance(value,record):
      # check if forest has changed
      if getattr(value,'forest_changed',False):
        if self._have_nodelist:
          self._have_nodelist = False;
          meqds.nodelist.clear();
          self.treebrowser.clear();
        self._have_forest_state = False;
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
    # auto-request mechanism:
    # if we're not up-to-date with a node list or forest state, start a timer as soon as we
    # reach idle mode or stopped mode. If this timer is allowed to expire, consider the 
    # application "quiet" and go request an update
    if not ev.startswith("process.status"):
      if self._connected:
        if self._have_nodelist and self._have_forest_state:
          self._autoreq_timer.stop();
        elif self.app.state == treebrowser.AppState.Idle or self.app.state == treebrowser.AppState.Debug:
          self._autoreq_timer.start(800);
          
  def _auto_update_request (self):
    if self._connected and \
          self.app.state == treebrowser.AppState.Idle or self.app.state == treebrowser.AppState.Debug:
      if not self._have_nodelist:
        meqds.request_nodelist();
      if not self._have_forest_state:
        meqds.request_forest_state();
    
  def ce_NodeState (self,ev,value):
    if hasattr(value,'name'):
      _dprint(5,'got state for node ',value.name);
      self.update_node_state(value,ev);
      
  def ce_NodeResult (self,ev,value):
    self.update_node_state(value,ev);
    if self.resultlog.enabled:
      txt = '';
      name = getattr(value,'name','') or "#" + str(value.nodeindex);
      cls  = getattr(value,'class','') or '?';
      rqid = str(getattr(value,'request_id',None)) or None;
      txt = ''.join((name,' <',cls.lower(),'>'));
      desc = 'snapshot for %s (%s)' % (name,cls);
      caption = '<B>%s</B> s/shot' % (name,);
      if rqid:
        txt = ''.join((txt,' rqid:',rqid));
        desc = desc + '; rqid: ' + rqid;
        caption = caption + ( ' <small>(rqid: %s)</small>' % (rqid,) );
      udi = meqds.snapshot_udi(value,rqid=rqid,count=self.resultlog.event_count());
      self.resultlog.add(txt,content=value,category=Logger.Event,
        udi=udi,name=name,desc=desc,caption=caption,viewopts=meqgui.defaultResultViewopts);
      wtop = self.resultlog.wtop();
      if self.maintab.currentPage() is not wtop and not wtop._newresults:
        self.maintab.changeTab(wtop,wtop._newres_iconset,wtop._newres_label);
        wtop._newresults = True;
        
  def ce_LoadNodeList (self,ev,meqnl):
    if not meqds.nodelist.is_valid_meqnodelist(meqnl):
      _dprint(2,"got nodelist but it is not valid, ignoring");
      return;
    self._have_nodelist = True;
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
      if self.app.state == treebrowser.AppState.Stream:
        self.status_label.setText(' streaming data (%d tiles) ' % (nt,) ); 
        
  def update_node_state (self,node,event=None):
    meqds.reclassify_nodestate(node);
    meqds.add_node_snapshot(node,event);
    udi = meqds.node_udi(node);
    Grid.updateDataItem(udi,node);
    
  def _update_forest_state (self,fst):
    self._have_forest_state = True;
    # update bookmarks if needed
    bkrec = getattr(fst,'bookmarks',[]);
    if bkrec != self._bookmarks_rec:
      _dprint(1,"bookmarks changed in forest, reloading");
      self._bookmarks_rec = bkrec;
      self._bookmarks.load(bkrec);
    else:
      _dprint(3,"bookmarks not changed in forest, ignoring");
    Grid.updateDataItem('/forest',fst);
    
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop() and tabwin._newresults:
      self._reset_maintab_label(tabwin);
    tabwin._newresults = False;

  def _update_app_state (self):
    app_proxy_gui._update_app_state(self);
    if self.app.state == treebrowser.AppState.Stream:
      self.ce_UpdateAppStatus(None,self.app.status);
    self.treebrowser.update_app_state(self.app.state);

# register NodeBrowser at low priority for now (still experimental),
# but eventually we'll make it the default viewer
# Grid.Services.registerViewer(meqds.NodeClass(),NodeBrowser,priority=30);

# register reloadables
reloadableModule(__name__);
# reloadableModule('meqds');

