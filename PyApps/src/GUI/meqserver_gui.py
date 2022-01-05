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
from Timba.GUI.app_proxy_gui import *
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba.GUI.browsers import *
from Timba.GUI import treebrowser
import Timba.GUI.TDL as tdlgui
from Timba.GUI import profiler
from Timba.GUI.procstatuswidget import *
from Timba.GUI import meqgui
from Timba.GUI import bookmarks
from Timba.GUI import servers_dialog
from Timba.GUI import about_dialog
from Timba.GUI import widgets
from Timba.GUI import VisProgressMeter
from Timba.GUI import SolverProgressMeter
from Timba import Grid
from Timba import TDL
import Timba.TDL.GUI
import Purr.MainWindow
import Purr.Startup

import weakref
import math
import re
import os
import os.path
import signal
import traceback

import Timba.Apps
import Timba.Apps.config
Config = Timba.Apps.config.section("meqbrowser");

_dbg = verbosity(0,name='gui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

makeNodeDataItem = meqgui.makeNodeDataItem;

# splash screen

#_mainapp = mainapp();
#_splash_screen = QSplashScreen(pixmaps.trees48x48.pm());
#_splash_screen.show();
#_splash_screen.message("Starting MeqTrees Browser");

# global symbol: meqserver object; initialized when a meqserver_gui
# is constructed
mqs = None;

class meqserver_gui (app_proxy_gui):

  StatePixmaps = { None: pixmaps.stop, \
    'idle': pixmaps.grey_cross,
    'executing': pixmaps.gear,
    'executing.debug': pixmaps.breakpoint,
    'executing_debug': pixmaps.breakpoint };

  def __init__(self,app,*args,**kwargs):
    meqds.set_meqserver(app);
    global mqs;
    self.mqs = mqs = app;
    self.mqs.track_results(False);
    # init internal state
    self._purr = None;
    self._is_tree_in_sync = False;
    self._tdl_tabs = {};
    self._wait_cursor = None;
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    # add handlers for various application events
    QObject.connect(self,PYSIGNAL("node.result"),self.ce_NodeResult);
    QObject.connect(self,PYSIGNAL("process.status"),self.ce_ProcessStatus);
    QObject.connect(self,PYSIGNAL("result.node.get.state"),self.ce_NodeState);
    QObject.connect(self,PYSIGNAL("result.get.node.list"),self.ce_LoadNodeList);

  def populate (self,main_parent=None,*args,**kwargs):
    # register ourselves with TDL services
    Timba.TDL.GUI.meqbrowser = self;

    app_proxy_gui.populate(self,main_parent=main_parent,*args,**kwargs);
    self.setWindowTitle("MeqBrowser");
    self.setWindowIcon(pixmaps.trees48x48.icon());
    self.set_verbose(self.get_verbose());

    # the _check_connection_status method is called every time we connect/disconnect/etc.
    # This is meant to update relevant GUI elements, etc.
    QObject.connect(self,PYSIGNAL("isConnected()"),self._check_connection_status);

    _dprint(0,"meqserver-specific init");
    # size window if stored in config
    width = max(100,min(Config.getint('browser-window-width',0),4000));
    height = max(50,min(Config.getint('browser-window-height',0),2000));
    if width or height:
      self.resize(QSize(width,height));

    # add Tree browser panel
    self.tb_panel = self.PanelizedWindow(self.splitter,"Trees","Trees",pixmaps.view_tree.icon());
    self.treebrowser = treebrowser.TreeBrowser(self.tb_panel);
    self.tb_panel.addWidget(self.treebrowser.wtop());
    QObject.connect(self.tb_panel,PYSIGNAL("visible()"),
          self.treebrowser.wtoolbar().setShown);

    self.maintab_panel.show();
    self.gw_panel.hide();
    self.tb_panel.hide();


    self.splitter.insertWidget(0,self.tb_panel);
    self.splitter.setStretchFactor(0,0);

    self.splitter.setSizes([100,300,400]);

    # add Snapshots tab
    self.resultlog = Logger(self,"node snapshot log",limit=1000,scroll=False,
          udi_root='snapshot');
    self.resultlog.wtop()._newres_icon  = pixmaps.gear.icon();
    self.resultlog.wtop()._newres_label    = "Snapshots";
    self.resultlog.wtop()._newresults      = False;
    self.add_tab(self.resultlog.wtop(),"Snapshots",index=2);
    QObject.connect(self.resultlog.treeWidget(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self.maintab,SIGNAL("currentChanged(int)"),self._reset_resultlog_label);

    # add Profiler tab
    self.profiler = profiler.Profiler(self,"tree profiler");
    self.profiler.wtop()._busy_icon  = pixmaps.clock.icon();
    self.profiler.wtop()._busy_label    = "Snapshots";
    self.add_tab(self.profiler.wtop(),"Profiler");
    self.show_tab(self.profiler.wtop(),False);
    QObject.connect(self.profiler.wtop(),PYSIGNAL("collecting()"),self._show_profiler_busy);
    QObject.connect(self.profiler.wtop(),PYSIGNAL("collected()"),self._show_profiler);

    # create main toolbar
    self.maintoolbar = QToolBar(self);
    self.maintoolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    self.maintoolbar.setIconSize(QSize(16,16));
    self.qa_viewpanels = QActionGroup(self);
    self.qa_viewpanels.setExclusive(False);

    # populate it with view controls
    for panel in (self.tb_panel,self.maintab_panel,self.gw_panel):
      panel.visQAction(self.qa_viewpanels);
      self.maintoolbar.addWidget(panel.makeMinButton(self.maintoolbar));

    # add TDL jobs button
    self._qa_jobs = self.maintoolbar.addAction(pixmaps.gear.icon(),"TDL Exec",self._show_current_tdl_jobs);
#    self._qa_jobs.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    self._qa_jobs.setToolTip("Access run-time options & jobs defined by current TDL script");
    self._qa_jobs.setVisible(False);

    # add TDL run button
    self._qa_runtdl = self.maintoolbar.addAction(pixmaps.blue_round_reload.icon(),
                        "&Reload current TDL script",self._run_current_tdl_script);
    self._qa_runtdl.setIconText("Reload");
    self._qa_runtdl.setShortcut(Qt.CTRL+Qt.Key_R);
    QObject.connect(self,PYSIGNAL("isConnected()"),self._enable_run_current);
    self._enable_run_current(False);
    self._qa_runtdl.setWhatsThis("""This button reloads the current TDL script.""");
    self._qa_runtdl.setVisible(False);
    self._qa_runtdl.setEnabled(False);
    self._main_tdlfile = None; # this is used by _run_current

    # add TDL options button
    self._qa_opts = self.maintoolbar.addAction(pixmaps.wrench.icon(),"TDL Options",self._show_current_tdl_opts);
    self._qa_opts.setToolTip("Access compile-time options for current TDL script");
    self._qa_opts.setVisible(False);
    # disable TDL job controls while running
    QObject.connect(self.treebrowser.wtop(),PYSIGNAL("isRunning()"),self._qa_jobs.setDisabled);
    QObject.connect(self.treebrowser.wtop(),PYSIGNAL("isRunning()"),self._qa_runtdl.setDisabled);

    dum = QWidget(self.maintoolbar);
    dum.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self.maintoolbar.addWidget(dum);

    # add Purr button
    qa_purr = self.maintoolbar.addAction(pixmaps.purr_logo.icon(),"Show Purr window",self.show_purr_window);
    qa_purr.setIconText("Purr");
    qa_purr.setToolTip("Shows the Purr tool");

    # make a TDLErrorFloat for errors
    self._tdlgui_error_window = tdlgui.TDLErrorFloat(self);
    QObject.connect(self._tdlgui_error_window,PYSIGNAL("showError()"),self._show_tdl_error);
    self._tdlgui_error_window.setGeometry(0,0,300,60);
    # anchor it to maintab_panel
    self._tdlgui_error_window.set_anchor(self.maintab_panel,40,-40,xref=0,yref=1);
    QObject.connect(self.maintab_panel,PYSIGNAL("resized()"),
                    self._tdlgui_error_window.move_anchor);
    QObject.connect(self.maintab_panel,PYSIGNAL("hidden()"),
                    self._tdlgui_error_window.hide);
    QObject.connect(self.maintab_panel,PYSIGNAL("shown()"),
                    self._tdlgui_error_window.show);
    # hide/show error float based on what kind of tab is selected
    def _hide_or_show_error_float(index):
      widget = self.maintab.widget(index);
      if isinstance(widget,tdlgui.TDLEditor):
        self._tdlgui_error_window.show();
      else:
        self._tdlgui_error_window.hide();
    QObject.connect(self.maintab,SIGNAL("currentChanged(int)"),self.curry(_hide_or_show_error_float));

    # self.maintoolbar.setStretchableWidget(dum);
    ### skip the what's this button
    # add what's this button at far right
    self._whatsthisaction = QWhatsThis.createAction(self);
    #self.maintoolbar.addAction(self._whatsthisaction);
    ###
    self.addToolBar(Qt.TopToolBarArea,self.maintoolbar);
    self.addToolBar(Qt.LeftToolBarArea,self.treebrowser.wtoolbar());
    self.treebrowser.wtoolbar().hide();

#     # add TDL editor panel
#     self.tdledit = tdl_editor.TDLEditor(self,"tdl editor tab");
#     self.add_tab(self.tdledit,"TDL");
#     QObject.connect(self.tdledit,PYSIGNAL("loadedFile()"),self._set_tdl_pathname);

    # excluse ubiquotous events from the event logger
    self.eventlog.set_mask('!node.status.*;!process.status;'+self.eventlog.get_mask());

    meterbar = QWidget(self.statusbar);
    meterbar_lo = QVBoxLayout(meterbar);
    meterbar_lo.setContentsMargins(0,0,0,0);
    meterbar_lo.setSpacing(0);
    self.statusbar.addWidget(meterbar,1);
    # add a VisProgressMeter to status bar
    self._visprogmeter = VisProgressMeter.VisProgressMeter(meterbar);
    meterbar_lo.addWidget(self._visprogmeter);
    self._visprogmeter.hide();
    # self.statusbar.addWidget(self._visprogmeter); # ,2);
    self._visprogmeter.connect_app_signals(self);

    # add a SolverProgressMeter to status bar
    self._solprogmeter = SolverProgressMeter.SolverProgressMeter(meterbar);
    self._solprogmeter.hide();
    # self.statusbar.addWidget(self._solprogmeter); # ,2);
    self._solprogmeter.connect_app_signals(self);
    meterbar_lo.addWidget(self._solprogmeter);

    # add dummy stretch, and a memory size widget to status bar
    self._wstat = ProcStatusWidget(self.statusbar);
    self._wstat.hide();
    dum = QWidget(self.statusbar);
    dum.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    self.statusbar.addWidget(dum,10);
    self.statusbar.addWidget(self._wstat) #,0);

    # create a servers dialog
    self._connect_dialog = servers_dialog.ServersDialog(self,\
        name="&Attach to a meqserver",modal=False);
    QObject.connect(self,PYSIGNAL("isConnected()"),self._connect_dialog.setHidden);
    QObject.connect(self._connect_dialog,PYSIGNAL("startKernel()"),self._start_kernel);
    QObject.connect(self._connect_dialog,PYSIGNAL("serverSelected()"),self._select_attach_kernel);
    # --- find path to kernel binary if not configured
    self._default_meqserver_path = Config.get('meqserver-path','meqserver');
    if self._default_meqserver_path.find('/') < 0: # need to search $PATH
      for dirname in os.environ['PATH'].split(':'):
        filename = os.path.join(dirname,self._default_meqserver_path);
        if os.path.isfile(filename) and os.access(filename,os.X_OK):
          self._default_meqserver_path = filename;
          break;
    self._connect_dialog.set_default_path(self._default_meqserver_path);
    self._connect_dialog.set_default_args(Config.get('meqserver-args',''));
    ## NB: this shows the dialog BEFORE showing ourselves
    # self._connect_dialog.show();

    # build menu bar
    menubar = self.menuBar();
    self._menus = {};
    kernel_menu    = self._menus['MeqTrees']  = menubar.addMenu("&MeqTrees");
    tdl_menu       = self._tdlmenu = self._menus['TDL'] = menubar.addMenu("&TDL");
    debug_menu     = self._menus['Debug']     = menubar.addMenu("&Debug");
    view_menu      = self._menus['View']      = menubar.addMenu("&View");
    bookmarks_menu = self._menus['Bookmarks'] = menubar.addMenu("&Bookmarks");
    menubar.addSeparator();
    help_menu      = self._menus['Help']      = menubar.addMenu("&Help");

    # some menus only available when connected
    self._enable_bookmarks_menu = bookmarks_menu.menuAction().setVisible;
    QObject.connect(self,PYSIGNAL("isConnected()"),self._enable_bookmarks_menu);
    self._enable_bookmarks_menu(False);

    # --- MeqTrees menu
    connect  = self._qa_connect  = kernel_menu.addAction("Attach to a meqserver...",self._connect_dialog.show,Qt.CTRL+Qt.Key_A);
    stopkern = self._qa_stopkern = kernel_menu.addAction(pixmaps.red_round_cross.icon(),
                                            "&Stop current meqserver",self._stop_kernel,Qt.CTRL+Qt.Key_S);
    stopkern.setDisabled(True);
    QObject.connect(self,PYSIGNAL("isConnected()"),stopkern.setEnabled);

    renamekern = self._qa_renamekern = kernel_menu.addAction("&Rename current meqserver",self._rename_kernel);
    renamekern.setDisabled(True);
    QObject.connect(self,PYSIGNAL("isConnected()"),renamekern.setEnabled);

    kernel_menu.addSeparator();
    kernel_menu.addAction(self.treebrowser._qa_refresh);
    clearforest = kernel_menu.addAction("Clear current forest",meqds.clear_forest);
    clearforest.setDisabled(True);
    QObject.connect(self,PYSIGNAL("isConnected()"),clearforest.setEnabled);
    # self.treebrowser._qa_load.addTo(kernel_menu);
    # self.treebrowser._qa_save.addTo(kernel_menu);

    # --- TDL menu
    syncedit = tdl_menu.addAction("Sync scripts to external editor");
    syncedit.setCheckable(True);
    QObject.connect(syncedit,SIGNAL("toggled(bool)"),self.curry(Config.set,'tdl-sync-to-external-editor'));
    QObject.connect(syncedit,SIGNAL("toggled(bool)"),tdlgui.TDLEditor.set_external_sync);
    sync = Config.getbool('tdl-sync-to-external-editor',True);
    syncedit.setChecked(sync);

    showlnum = tdl_menu.addAction("Show line numbers in editor");
    showlnum.setVisible(tdlgui.TDLEditor.SupportsLineNumbers);
    showlnum.setCheckable(True);
    QObject.connect(showlnum,SIGNAL("toggled(bool)"),self._show_tdl_line_numbers);
    show = Config.getbool('tdl-show-line-numbers',True);
    showlnum.setChecked(show);

    self._qa_loadtdl_cwd = tdl_menu.addAction("Change to directory of TDL script when loading");
    self._qa_loadtdl_cwd.setCheckable(True);
    self._qa_loadtdl_cwd.setChecked(Config.getbool('cwd-follows-tdlscript',False));

    loadruntdl = tdl_menu.addAction("&Load TDL script...",self._load_tdl_script_dialog,Qt.CTRL+Qt.Key_T);
    QObject.connect(self,PYSIGNAL("isConnected()"),loadruntdl.setEnabled);
    loadruntdl.setEnabled(False);

    tdl_menu.addAction(self._qa_runtdl);
    # menu for tdl jobs is inserted when TDL script is run
    QObject.connect(self,PYSIGNAL("isConnected()"),self._clear_tdl_jobs);

    # add menu actions for recent scripts
    tdl_menu.addSeparator();
    self._recent_scripts = list(filter(bool,Config.get('recent-tdl-scripts','').split(';;')));
    self._qa_recent_scripts = [
      tdl_menu.addAction("recent script %d"%i,self.curry(self._load_recent_script_number,i),Qt.CTRL+key)
      for i,key in enumerate((Qt.Key_1,Qt.Key_2,Qt.Key_3,Qt.Key_4,Qt.Key_5))
    ];
    for qa in self._qa_recent_scripts:
      qa.setVisible(False);
    self._populate_recent_script_menu();

    # --- View menu
    for qa in self.qa_viewpanels.actions():
      view_menu.addAction(qa);
#     showgw = QAction(pixmaps.view_split.icon(),"&Gridded workspace",Qt.Key_F3,self);
#     showgw.addTo(view_menu);
#     showgw.setCheckable(True);
#     QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),showgw.setChecked);
#     QObject.connect(showgw,SIGNAL("toggled(bool)"),self.gw.show);
    view_menu.addSeparator();
    # optional tab views
    view_menu.addAction(self.resultlog.wtop()._show_qaction);
    view_menu.addAction(self.eventtab._show_qaction);
    view_menu.addAction(self.profiler.wtop()._show_qaction);

    self.show_tab(self.eventtab,False);
#    self.tdledit._show_qaction.addTo(view_menu);
#    self.show_tab(self.tdledit,False);
    # process status view
    showps = view_menu.addAction("&Process status");
    showps.setCheckable(True);
    showps.setChecked(False);
    QObject.connect(showps,SIGNAL("toggled(bool)"),self._wstat.setShown);
    QObject.connect(self._wstat,PYSIGNAL("shown()"),showps.setChecked);

    view_menu.addSeparator();
    view_menu.addAction(qa_purr);

    # --- Bookmarks menu
    self._qa_addbkmark   = addbkmark   = bookmarks_menu.addAction(pixmaps.bookmark_add.icon(),
                                              "Add bookmark",self._add_bookmark,Qt.CTRL+Qt.Key_B);
    self._qa_addpagemark = addpagemark = bookmarks_menu.addAction(pixmaps.bookmark_toolbar.icon(),
                                              "Add pagemark for this page",self._add_pagemark,Qt.SHIFT+Qt.CTRL+Qt.Key_B);
    # self._qa_autopublish = autopublish = QAction(pixmaps.publish.icon(),"Auto-publish loaded bookmarks",0,self);
    # self._qa_autopublish = autopublish = QAction("Auto-publish loaded bookmarks",0,self);
    # autopublish.addTo(bookmarks_menu);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),PYSIGNAL("itemSelected()"),self._gw_reset_bookmark_actions);
    QObject.connect(self.gw.wtop(),SIGNAL("currentChanged(int)"),self._gw_reset_bookmark_actions);
    addbkmark.setEnabled(False);
    addpagemark.setEnabled(False);
    # autopublish.setCheckable(True);
    # autopublish.setChecked(Config.getbool('autopublish-bookmarks',True));
    # autopublish.setChecked(True);
    # QObject.connect(autopublish,SIGNAL("toggled(bool)"),self.curry(Config.set,'autopublish-bookmarks'));
    # QObject.connect(autopublish,SIGNAL("toggled(bool)"),self._autopublish_bookmarks);
    self._autopublish_bookmarks(True);
    # bookmark manager
    bookmarks_menu.addSeparator();
    self._bookmarks = bookmarks.BookmarkFolder("main",self,menu=bookmarks_menu,gui_parent=self);
    # copy of current bookmark record
    self._bookmarks_rec = None;
    QObject.connect(self._bookmarks,PYSIGNAL("updated()"),self._save_bookmarks);
    QObject.connect(self._bookmarks,PYSIGNAL("showBookmark()"),self._show_bookmark);
    QObject.connect(self._bookmarks,PYSIGNAL("showPagemark()"),self._show_pagemark);

    # --- Debug menu
    for qa in self.treebrowser._qa_dbg_verbosity.actions():
      debug_menu.addAction(qa);
    debug_menu.addSeparator();
    for qa in self.treebrowser._qa_dbg_tools.actions():
      debug_menu.addAction(qa);
    debug_menu.addSeparator();
    self._qa_log_results = debug_menu.addAction("Log node results to console");
    self._qa_log_results.setCheckable(True);
    collect_prof = debug_menu.addAction("Collect profiling stats",self.profiler.collect_stats);
    collect_prof.setEnabled(False);
    QObject.connect(self,PYSIGNAL("isConnected()"),collect_prof.setEnabled);

    attach_gdb = self._qa_attach_gdb = debug_menu.addAction("Attach binary debugger to meqserver",self._debug_kernel);
    attach_gdb.setEnabled(False); # for now

    # --- Help menu
    self._about_dialog = about_dialog.AboutDialog(self);
    qa_about = help_menu.addAction("About MeqTrees...",self._about_dialog.exec_);
    help_menu.addAction(self._whatsthisaction);

    # populate menus from plugins
    # scan all modules for define_mainmenu_actions methods, and call them all
    self._actions = {};
    funcs = set();
    for (name,mod) in list(sys.modules.items()):
      _dprint(4,'looking for mainmenu actions in',name);
      try:
        if name.startswith("Timba") and callable(mod.define_mainmenu_actions):
          _dprint(3,'mainmenu action found in',name,'adding to set');
          funcs.add(mod.define_mainmenu_actions);
      except AttributeError: pass;
    _dprint(1,len(funcs),'unique mainmenu action-definition methods found');
    for f in funcs:
      f(self._menus,self);

    # finally, add standard stuff to bottom of menus
    kernel_menu.addSeparator();
    exit = kernel_menu.addAction(pixmaps.exit.icon(),"&Quit browser",self.close,Qt.CTRL+Qt.Key_Q);
    ## NB: uncomment the line below to have Ctrl+C handled through the GUI
    ## (confirmation dialog will be displayed if running a kernel)
    # signal.signal(signal.SIGINT,self.xcurry(self.close));

    # subscribe to nodelist requests
    QObject.connect(meqds.nodelist,PYSIGNAL("requested()"),self.curry(
      self.log_message,"fetching forest from meqserver, please wait"));
    QObject.connect(self.treebrowser,PYSIGNAL("forestLoaded()"),self._notify_forest_loaded);
    # subscribe to updates of forest state
    meqds.subscribe_forest_state(self._update_forest_state);
    # clear the splash screen
    # _splash_screen.finish(self);
    # add signal handler for SIGCHLD. This will probably override the signal handler set
    # by Apps.meqserver, but that's OK
    signal.signal(signal.SIGCHLD,self._sigchld_handler);
    self._kernel_pid = self._kernel_pathname = None;
    # other internal state
    self._have_nodelist = False;
    self._have_forest_state = False;
    self._autoreq_timer = QTimer(self);
    self._autoreq_disable_timer = QTimer(self);
    self._autoreq_sent = False;
    # timer is used to automatically request a nodelist
    QObject.connect(self._autoreq_timer,SIGNAL("timeout()"),self._auto_update_request);
    # timer is used to connect to a kernel
    self._connect_timer = QTimer(self);
    QObject.connect(self._connect_timer,SIGNAL("timeout()"),self._connection_timeout);
    # if a nodelist is requested by other means, the timer is stopped
    QObject.connect(meqds.nodelist,PYSIGNAL("requested()"),self._autoreq_timer.stop);

  def show (self):
    app_proxy_gui.show(self);
    self._connect_dialog.show();
    self._connect_dialog.move(self.mapToGlobal(QPoint(100,100)));

  def moveEvent (self,ev):
    app_proxy_gui.moveEvent(self,ev);
    self._tdlgui_error_window.move_anchor();

  def resizeEvent (self,ev):
    app_proxy_gui.resizeEvent(self,ev);
    sz = ev.size();
    Config.set('browser-window-width',sz.width());
    Config.set('browser-window-height',sz.height());
    self._tdlgui_error_window.move_anchor();

  def _notify_forest_loaded (self):
    if len(meqds.nodelist):
      self.log_message("fetched forest, %d nodes"%(len(meqds.nodelist),));
    else:
      self.log_message("forest is empty");

  def _show_profiler (self):
    self._reset_maintab_label(self.profiler.wtop());
    self.show_tab(self.profiler.wtop(),switch=True);

  def _show_profiler_busy (self):
    self.show_tab(self.profiler.wtop(),switch=False);
    self._reset_maintab_label(self.profiler.wtop(),icon=pixmaps.clock.icon());
    QApplication.flush();

  def _autopublish_bookmarks (self,enabled):
    if not enabled:
      QMessageBox.warning(self,"Auto-publishing disabled",
"""You have disabled auto-publishing. When you load a bookmark,
the displays will no longer refresh automatically. You can reactivate
auto-publishing via the Bookmarks menu.""",QMessageBox.Ok);

  def _debug_kernel (self):
    pid = self._kernel_pid;
    if not pid:
      if self.app.current_server:
        if self.app.current_server.remote:
          QMessageBox.warning(self,"Can't debug remote meqserver",
            """<p>It seems we're currently connected to a remote meqserver, so I
            can't attach a debugger.</p>""","Cancel");
          return;
        else:
          pid = self.app.current_server.addr[2];
      else:
        QMessageBox.warning(self,"Not attached to a meqserver",
          """<p>It seems we're not attached to a meqserver, and we don't know a
          PID for it, so I can't attach a debugger.</p>""","Cancel");
        return;
    pathname = self._kernel_pathname or ( "/proc/%d/exe"%(pid,) );
    cmd0 = Config.get("debugger-command","ddd %path %pid");
    prompt = "Debugger command (use '%path' to insert path to meqserver binary, '%pid' for process ID):";
    (cmd,ok) = QInputDialog.getText(self,"Attaching debugger to meqserver",
		  prompt,QLineEdit.Normal,cmd0);
    if ok:
      cmd = str(cmd);
      if cmd != cmd0:
        Config.set('debugger-command',cmd);
      cmd = cmd.replace('%pid',str(pid)).replace('%path',pathname);
      # see if command has changed, write to config if so
      args = cmd.split(' ');
      self.log_message("running \""+cmd+"\"");
      Timba.Apps.spawnvp_nowait(args[0],args);

  def _check_connection_status (self,dum=None):
    """this method is called whenever we connect/disconnect to a kernel.
    The dum argument is provided to make it easy to connect single-argument
    signals to this slot""";
    if self.app.current_server:
      addr = self.app.current_server.addr;
    else:
      addr = None;
    _dprint(1,"pid",self._kernel_pid,"addr",None);
    connected = bool(self._kernel_pid or addr);
    if addr:
      self._connect_timer.stop();
      try:
        self._timeout_dialog.hide();
      except AttributeError:
        pass;
    _dprint(1,"connected is",connected);
#    if connected and self.app.is_auto_attached():
#      self.app.meq('Set.Forest.Breakpoint',record(breakpoint=meqds.BP_FAIL),wait=False);
    self._qa_stopkern.setEnabled(connected);
    # self._qa_connect.setDisabled(connected);
    self._qa_attach_gdb.setEnabled(connected);

  def _select_attach_kernel (self,addr):
    self._connect_dialog.hide();
    self.app.attach_server(addr);

  def _start_kernel (self,pathname,args):
    _dprint(0,pathname,args);
    if pathname != self._default_meqserver_path:
      self._default_meqserver_path = pathname;
      Config.set('meqserver-path',pathname);
    Config.set('meqserver-args',args);
    if not os.path.isfile(pathname) or not os.access(pathname,os.X_OK):
      self.log_message("can't start meqserver \"%s\": not an executable file" % (pathname,), \
        category=Logger.Error);
      return;
    self.log_message("starting meqserver process \"%s %s\" and waiting for connection"%(pathname,args));
    self._kernel_pid = self._kernel_pid0 = Timba.Apps.spawnvp_nowait(pathname,[pathname]+args.split(' '));
    _dprint(0,"started meqserver process",self._kernel_pid);
    # tell the client to attach as soon as it sees this pid
    self.app.auto_attach(pid=self._kernel_pid,host=None);
    self._kernel_pathname = pathname;
    self._connect_timer.setSingleShot(True);
    self._connect_timer.start(8000);  # start an 8-second timer
    self._check_connection_status();

  def _connection_timeout (self):
    """called by connection timer when it expires""";
    if self._connected:
      return;
    # NB: since at the moment we don't really support remote kernels,
    # always offer to kill the local kernel. In the future we need to be
    # able to tell the difference.
    try:
      timeout_dialog = self._timeout_dialog;
    except AttributeError:
      timeout_dialog = self._timeout_dialog = QMessageBox("""meqserver timed out""",
        """<p>We have started a local meqserver process (pid %s), but we can't
        establish a connection to it. This may be due to any one of the following reasons:</P>
        <ul>
        <li>an out-of-date meqserver build.</li>
        <li>leftover meqbrowser, meqserver or child processes (such as glish) can sometimes interfere with the connection. Try a <tt>ps x</tt> to see what's running, and kill any old processes.</li>
        <li>a genuine bug -- please report this.</li>
        </ul>
        <P>You can also try killing and restarting the meqserver process itself.</p>""" % str(self._kernel_pid0),
        QMessageBox.Critical,
        QMessageBox.Ok,QMessageBox.NoButton,QMessageBox.NoButton,
        self);
      timeout_dialog.setModal(False);
    timeout_dialog.show();

  def _rename_kernel (self):
    if not self.app.current_server:
      return;
    sname = self.app.current_server.session_name or '';
    sname,ok = QInputDialog.getText("Renaming meqserver session",
              "Enter a name for this meqserver session",QLineEdit.Normal,sname);
    if ok:
      self.app.meq('Set.Session.Name',record(session_name=str(sname)),wait=False);

  def _stop_kernel (self):
    # check if we have a PID for the kernel
    pid = self._kernel_pid;
    addr = self.app.current_server and self.app.current_server.addr;
    # if connected to local kernel, get PID from address
    if not pid and self.app.current_server and not self.app.current_server.remote:
      pid = addr[2];
    # show different dialogs depending on what we know about the meqserver
    if pid and addr:
      buttons = ("HALT","KILL","Cancel",0,2);
      res = QMessageBox.warning(self,"Stopping meqserver",
        """<p>We are attached to a local meqserver. The normal way to stop it
        is by sending it a <tt>HALT</tt> command. If the meqserver doesn't respond to this,
        we can always brute-force it with a <tt>KILL</tt> signal. Which method do you want
        to use?</p>""",
        *buttons);
      res = buttons[res];
    elif pid:
      buttons = ("KILL","Cancel","",0,1);
      res = QMessageBox.warning(self,"Stopping meqserver",
        """<p>It seems there's a meqserver running (pid %d) but we can't
        establish a connection to it. Should we try to stop it with
        a <tt>KILL</tt> signal?</p>""" % pid,
        *buttons);
      res = buttons[res];
    elif addr:
      buttons = ("HALT","Cancel","",0,1);
      res = QMessageBox.warning(self,"Stopping meqserver",
        """<p>We are connected to a remote meqserver (%s). Should we try
        to stop it with a <tt>HALT</tt> command?</p>""" % str(addr),
        *buttons);
      res = buttons[res];
    else:
      buttons = ("Cancel",);
      QMessageBox.warning(self,"No meqserver attached",
        """<p>It seems we're not attached to a meqserver, and we don't know a
        PID for it, so there's nothing for me to stop. In this situation you
        shouldn't have been able to get to this dialog in the first place,
        so you may want to report a bug!</p>""",
        *buttons);
      res = "Cancel";
    # stop kernel in one of many possible ways
    if res == "HALT":
      self.log_message('sending HALT command to meqserver');
      self.app.halt();
    elif res == "KILL":
      self.log_message('sending KILL signal to meqserver process '+str(pid));
      os.kill(pid,signal.SIGKILL);

  def _sigchld_handler (self,sig,stackframe):
    _dprint(1,'got signal',sig);
    try:
      wstat = os.waitpid(-1,os.WNOHANG);
    except:
      return;
    if wstat:
      (pid,st) = wstat;
      if not pid:   # pid 0 means we got a STOP/CONT signal, ignore
        return;
      if pid == self._kernel_pid:
        msg = "meqserver process " + str(pid);
        self._kernel_pid = None;
        cat = Logger.Error;
        self._check_connection_status();
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

  def _verify_quit (self):
    if self._connected and self._kernel_pid:
      res = QMessageBox.warning(self,"Quit browser",
        """<p>We have started a meqserver process (pid %d) from this browser.
        Would you like to quit the browser only, or kill the meqserver process as
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

  def _clear_tdl_jobs (self,dum=False):
    """removes the TDL Jobs submenu, if it exists""";
    self._qa_opts.setVisible(False);
    self._qa_jobs.setVisible(False);

  def _enable_run_current (self,dum=False):
    """enables/disables the Run TDL QAction. If kernel is connected and a TDL script
    is loaded, enables, else disables.""";
    if self._connected and self._main_tdlfile is not None:
      filename = "("+os.path.basename(self._main_tdlfile)+")";
      self._qa_runtdl.setWhatsThis("Re-runs the current TDL script "+filename);
      self._qa_runtdl.setVisible(True);
      self._qa_runtdl.setEnabled(True);
    else:
      self._qa_runtdl.setVisible(False);
      self._qa_runtdl.setEnabled(False);

  def _run_current_tdl_script (self):
    """runs the currently loaded TDL script""";
    if self._main_tdlfile is None:
      QMessageBox.warning(self,"No TDL script","No TDL script has been loaded.",QMessageBox.Ok);
      return;
    if not self._connected:
      QMessageBox.warning(self,"No meqserver","Not connected to a meqserver.",QMessageBox.Ok);
      return;
    self._tdltab_compile_file(None,self._main_tdlfile,show=False,import_only=True);


  def _show_current_tdl_opts (self):
    if self._main_tdlfile is None:
      QMessageBox.warning(self,"No TDL script","No TDL script has been loaded.",QMessageBox.Ok);
      return;
    tab = self._tdl_tabs.get(self._main_tdlfile,None);
    if tab:
      tab.show_compile_options();

  def _show_current_tdl_jobs (self):
    if self._main_tdlfile is None:
      QMessageBox.warning(self,"No TDL script","No TDL script has been loaded.",QMessageBox.Ok);
      return;
    if not self._connected:
      QMessageBox.warning(self,"No meqserver","Not connected to a meqserver.",QMessageBox.Ok);
      return;
    tab = self._tdl_tabs.get(self._main_tdlfile,None);
    if tab:
      tab.show_runtime_options();

  class LoadTDLDialog (QFileDialog):
    def __init__ (self,*args):
      QFileDialog.__init__(self,*args);
      self.setFileMode(QFileDialog.ExistingFile);
      self.setDirectory(os.getcwd());
      try:
        self.setNameFilters(["TDL scripts (*.tdl *.py)","All files (*.*)"]);
      except AttributeError:  # earlier versions of qt call it setFilters
        self.setFilters(["TDL scripts (*.tdl *.py)","All files (*.*)"]);
      self.setViewMode(QFileDialog.Detail);

  def _load_tdl_script_dialog (self):
    try: dialog = self._run_tdl_dialog;
    except AttributeError:
      self._run_tdl_dialog = dialog = self.LoadTDLDialog(self);
      dialog.setModal(True);
      dialog.resize(800,500);
      dialog.setWindowTitle("Load TDL Script");
      # add sidebar URL for Cattery and other packages
      urls = list(dialog.sidebarUrls());
      for pkg,(path,version) in Timba.packages().items():
      	urls.append(QUrl.fromLocalFile(path));
      dialog.setSidebarUrls(urls);
    if dialog.exec_() == QDialog.Accepted:
      self._load_tdl_script(str(dialog.selectedFiles()[0]));

  def _load_tdl_script (self,filename):
    self.log_message("loading TDL script "+filename);
    QApplication.processEvents(QEventLoop.ExcludeUserInputEvents);
    # close all TDL tabs
    for (path,tab) in list(self._tdl_tabs.items()):
      index = self.maintab.indexOf(tab);
      self.maintab.setCurrentIndex(index);
      if tab.confirm_close():
        tab.disable_editor();
        del self._tdl_tabs[path];
        self.maintab.removeTab(index);
        tab.setParent(QWidget());
    # change working directory
    cwd = self._qa_loadtdl_cwd.isChecked();
    Config.set('cwd-follows-tdlscript',cwd);
    if cwd:
      dirname = os.path.dirname(filename);
      if os.access(dirname,os.W_OK):
	      self.change_working_directory(dirname,browser=True,kernel=True);
      else:
	      QMessageBox.warning(self,"Cannot change directory","""
                                  <P><NOBR>Cannot change working directory to </NOBR><tt>%s</tt>, as it is not writable.</P>
                                  <P>Will keep using the current working directory, <tt>%s</tt>.</P>"""%(dirname,os.getcwd()),
                                  "OK");
    # show this file
    self.show_tdl_file(filename,run=True);
    self._add_recent_script(filename,save=True);

  def _add_recent_script (self,filename,save=False):
    # remove from list if found
    try: self._recent_scripts.remove(filename);
    except ValueError: pass;
    # insert at start of list, and keep list to 5 items
    self._recent_scripts.insert(0,filename);
    del self._recent_scripts[5:];
    if save:
      Config.set("recent-tdl-scripts",';;'.join(self._recent_scripts));
    self._populate_recent_script_menu();

  def _populate_recent_script_menu (self):
    for i,filename in enumerate(self._recent_scripts):
      qa = self._qa_recent_scripts[i];
      qa.setText(filename);
      qa.setVisible(True);

  def _load_recent_script_number (self,num):
    filename = self._recent_scripts[num];
    self._load_tdl_script(filename);

  def _show_tdl_line_numbers (self,show):
    Config.set('tdl-show-line-numbers',show);
    for tab in self._tdl_tabs.values():
      tab.show_line_numbers(show);

  def show_tdl_file (self,pathname,run=False,mainfile=None,show=True):
    if not isinstance(pathname,str) and not isinstance(pathname,unicode):
      raise TypeError("show_tdl_file: string argument expected, but got {}".format(type(pathname)));
    if mainfile is None:
      self._main_tdlfile = pathname;
      self._enable_run_current();  # update GUI
      self._tdlgui_error_window.clear_errors();
      self._update_app_state();
    tab = self._tdl_tabs.get(pathname,None);
    if tab is None:
      self._qa_jobs.setVisible(False);
      _dprint(1,'No tab open, loading',pathname);
    # try to load file into new tab
      try:
        ff = open(pathname);
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
      # only include close button for non-main files
      tab = tdlgui.TDLEditor(self.maintab,close_button=(pathname != self._main_tdlfile),
             error_window=self._tdlgui_error_window);
      label = os.path.basename(pathname);
      if mainfile:
        label = '(' + label + ')';
      self.add_tab(tab,label);
      self._tdl_tabs[pathname] = tab;
      QObject.connect(self,PYSIGNAL("isConnected()"),tab.hide_jobs_menu);
      QObject.connect(self,PYSIGNAL("isConnected()"),tab.show_run_control);
      tab.hide_jobs_menu(self._connected);
      tab.show_run_control(self._connected);
      tab.show_line_numbers(Config.getbool('tdl-show-line-numbers'));
      if show:
        self._tdltab_show(tab);
      QObject.connect(self.treebrowser.wtop(),PYSIGNAL("isRunning()"),tab.disable_controls);
      QObject.connect(tab,PYSIGNAL("fileSaved()"),self._tdltab_change);
      QObject.connect(tab,PYSIGNAL("hasErrors()"),self._tdltab_has_errors);
      QObject.connect(tab,PYSIGNAL("textModified()"),self._tdltab_modified);
      QObject.connect(tab,PYSIGNAL("fileClosed()"),self._tdltab_close);
      QObject.connect(tab,PYSIGNAL("showEditor()"),self._tdltab_show);
      QObject.connect(tab,PYSIGNAL("importFile()"),self._tdltab_import_file);
      QObject.connect(tab,PYSIGNAL("compileFile()"),self._tdltab_compile_file);
      QObject.connect(tab,PYSIGNAL("fileChanged()"),self._tdltab_reset_label);
      QObject.connect(tab,PYSIGNAL("hasCompileOptions()"),self._tdltab_refresh_compile_options);
      tab.load_file(pathname,text,mainfile=mainfile);
    else:
      _dprint(1,'we already have a tab for',pathname);
      if show:
        self._tdltab_show(tab);
    # ok, we have a working tab now, run if requested
    if run:
      self._tdl_import_tab_contents(tab);
    self.splitter.refresh();
    return tab;

  def _tdltab_refresh_compile_options (self,tab,nopt=None):
    """called when a tab has a new TDL Options popup""";
    _dprint(2,"new compile options",nopt);
    self._qa_opts.setVisible(bool(nopt));

  def _tdl_import_tab_contents (self,tab):
    self._main_tdlfile = tab.get_filename();
    QApplication.flush();
    self._qa_opts.setVisible(False);
    if tab.import_content(show_options=True):
      # if compile options are available, actual compile will
      # proceed when user presses the recompile button, so we
      # can let the other signal handlers take care of it
      if tab.has_compile_options():
        self._qa_opts.setVisible(True);
      # no options, initiate our own compile
      else:
        if tab.compile_content():
          # since we were successful, a nodelist will have been requested
          # by compile_content(). We want to disable automatic nodelist requests
          # which may have been generated by any other messages in the queue, so
          # we disable the auto-request for the next second or so
          self.tree_is_in_sync(True);
          self._autoreq_disable_timer.start(1000);
          self.tb_panel.show();
          # show/hide the jobs button
          self._qa_jobs.setVisible(tab.has_runtime_options());
          # do not restore cursor: wait for nodelist
          # jobs window will be shown when the nodelist arrives
          if tab.has_runtime_options():
            self._show_tdljobs_on_nodelist = True;

  def _tdl_compile_tab_contents (self,tab):
    self._main_tdlfile = tab.get_filename();
    basename = os.path.basename(self._main_tdlfile);
    self.log_message("compiling TDL script "+basename);
    QApplication.flush();
    self._qa_jobs.setVisible(False);
    if tab.compile_content():
      # since we were successful, a nodelist will have been requested
      # by compile_content(). We want to disable automatic nodelist requests
      # which may have been generated by any other messages in the queue, so
      # we disable the auto-request for the next second or so
      self.tree_is_in_sync(True);
      self._autoreq_disable_timer.start(1000);
      self.tb_panel.show();
      # show/hide the jobs button
      self._qa_jobs.setVisible(tab.has_runtime_options());
      # jobs window will be shown when the nodelist arrives
      if tab.has_runtime_options():
        self._show_tdljobs_on_nodelist = True;

  def _tdltab_import_file (self,origin_tab,filename,show=True):
    return self._tdltab_compile_file(origin_tab,filename,show=show,import_only=True);

  def _tdltab_compile_file (self,origin_tab,filename,show=True,import_only=False):
    # reset all tab icons
    for tab in self._tdl_tabs.values():
      self.maintab.setTabIcon(self.maintab.indexOf(tab),QIcon());
    # load file as needed
    tab = self._tdl_tabs.get(filename,None);
    if tab is None:
      _dprint(1,'No tab open, loading',filename);
      self.show_tdl_file(filename,run=True,show=show);
    else:
      if show:
        self.show_tab(tab);
      if import_only:
        self._tdl_import_tab_contents(tab);
      else:
        self._tdl_compile_tab_contents(tab);

  def _tdltab_show (self,tab):
    self.show_tab(tab);
    self.gw_panel.hide();
    self.maintab_panel.show();

  def _tdltab_reset_label (self,tab):
    name = os.path.basename(tab.get_filename());
    if tab.get_mainfile():
      name = '(' + name + ')';
    self.maintab.setTabText(self.maintab.indexOf(tab),name);

  def _tdltab_change (self,tab,pathname):
    for (path,tab1) in list(self._tdl_tabs.items()):
      if tab is tab1:
        del self._tdl_tabs[path];
        self._tdl_tabs[pathname] = tab;
        self._tdltab_reset_label(tab);
        return;
    raise ValueError("tab not found in map");

  def _show_tdl_error (self,index,filename,line,column):
    """Shows error with the given index, in file filename, at the given location.
    Loads file if necessary. Can be connected to a showError() signal from a TDL error window""";
    if filename is None:
      return;
    try:
      if getattr(self,'_tdltab_show_error_lock',False):
        return;
      self._tdltab_show_error_lock = True;
      _dprint(1,"showing error in",filename);
      # check if tab already exists
      tab = self._tdl_tabs.get(filename,None);
      # make it visible if it exists
      if tab:
        self._tdltab_show(tab);
        tab.sync_external_file(ask=False);
      # else load new tab
      else:
        tab = self.show_tdl_file(filename,mainfile=self._main_tdlfile,show=True);
        tab._reset_errors(len(self._tdlgui_error_window.get_error_list()));
      tab.show_error(index,filename,line,column);
    finally:
      self._tdltab_show_error_lock = False;

  def _tdltab_has_errors (self,tab,nerr):
    # nerr indicates the # of errors in that actual file
    if nerr:
      self.maintab.setTabIcon(self.maintab.indexOf(tab),pixmaps.red_round_cross.icon());
    else:
      self.maintab.setTabIcon(self.maintab.indexOf(tab),QIcon());

  def _tdltab_modified (self,tab,mod):
    if mod:
      self.tree_is_in_sync(False);
      self.maintab.setTabIcon(self.maintab.indexOf(tab),pixmaps.file_save.icon());
    else:
      self.maintab.setTabIcon(self.maintab.indexOf(tab),QIcon());

  def tree_is_in_sync (self,sync):
    if sync != self._is_tree_in_sync:
      for (path,tab) in list(self._tdl_tabs.items()):
        tab.tree_is_in_sync(sync);
      if sync:
        self._qa_jobs.setIcon(pixmaps.gear.icon());
        self._qa_jobs.setToolTip("Access run-time options & jobs defined by this TDL script");
      else:
        self._qa_jobs.setIcon(pixmaps.exclaim_yellow_warning.icon());
        self._qa_jobs.setToolTip("""Access run-time options & jobs defined by this TDL script.
Warning! You have modified the script since it was last compiled, so the tree may be out of date.""");
      self._is_tree_in_sync = sync;

  def _tdltab_close (self,tab):
    for (path,tab1) in list(self._tdl_tabs.items()):
      if tab is tab1:
        if path == self._main_tdlfile:
          self._main_tdlfile = None;
          self._enable_run_current();  # update GUI
          self._clear_tdl_jobs();
        self.maintab.setCurrentWidget(tab);
        if tab.confirm_close():
          tab.disable_editor();
          del self._tdl_tabs[path];
          self.maintab.removeTab(self.maintab.indexOf(tab));
          tab.setParent(QWidget());
        return;
    raise ValueError("tab not found in map");

  def closeEvent (self,event):
    if self._verify_quit():
      event.accept();
      if self._purr:
        self._purr.detachPurrlog();
      mainapp().quit();
    else:
      event.ignore();

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
          page.set_icon(pixmaps.bookmark.icon(),True);
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
    try:
      item = meqgui.makeDataItem(udi,viewer=viewer,publish=True);
      Grid.addDataItem(item,show_gw=True);
    except:
      (exctype,excvalue,tb) = sys.exc_info();
      self.dprint(0,'exception',str(exctype),'while loading bookmark',udi);
      QMessageBox.warning(self,"Error loading bookmark",
        """<p>Cannot load bookmark:</p>
        <p><small><i>%s: %s</i><small></p>""" % (exctype.__name__,excvalue),
        QMessageBox.Ok);

  def _show_pagemark (self,pagemark):
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
      curpage = self.gw.add_page(pagemark.name,pixmaps.bookmark.icon());
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
          item = meqgui.makeDataItem(rec.udi,viewer=rec.viewer,publish=True);
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
    curpage.set_icon(pixmaps.bookmark.icon(),True);

  def _gw_reset_bookmark_actions (self,dum=None):
    # figure out if Add bookmark is enabled
    enable_bkmark = enable_pgmark = False;
    if self._connected and self.gw.isVisible():
      item = Grid.Services.getHighlightedItem();
      if item:
        enable_bkmark = meqgui.isBookmarkable(item.udi);
        if enable_bkmark:
          self._qa_addbkmark.setText("Add bookmark for "+item.name);
      enable_pgmark = self.gw.current_page().has_content();
    self._qa_addbkmark.setEnabled(enable_bkmark);
    if not enable_bkmark:
      self._qa_addbkmark.setText("Add bookmark");
    self._qa_addpagemark.setEnabled(enable_pgmark);

  def change_working_directory(self,path,browser=True,kernel=True):
    """Changes the current WD of browser and/or kernel to the specified path.""";
    if browser:
      _dprint(1,'cwd',path);
      # change TDL dialog path
      dialog = getattr(self,'_run_tdl_dialog',None);
      if dialog:
        dialog.setDirectory(path);
      # change browser path
      curpath = os.getcwd();
      os.chdir(path);
      if not os.path.samefile(path,curpath):
        self.log_message("browser working directory is now "+path);
        # notify purr, if running
        if self._purr:
          self._purr.detachPurrlog();
          if self._purr.isVisible() and not Purr.Startup.startWizard([path],self._purr):
            self._purr.hide();
    if kernel and self.app.current_server:
      _dprint(1,'kernel cwd',path);
      self.app.change_wd(path);

  def _attached_server_event (self,ev,value,server):
    self._wait_cursor = None;     # clear any wait-cursors
    app_proxy_gui._attached_server_event(self,ev,value,server);
    self._connect_dialog.attach_to_server(server.addr);
    self._wstat.show();
    self._wstat.emit(SIGNAL("shown"),True,);
    self.treebrowser.clear();
    self.treebrowser.connected(True);
    self.resultlog.connected(True);
    self._gw_reset_bookmark_actions();
    wtop = self.resultlog.wtop();
    index = self.maintab.indexOf(wtop);
    self.maintab.setTabIcon(index,wtop._default_icon);
    self.maintab.setTabText(index,wtop._default_label);
    meqds.request_forest_state();

  def _detached_server_event (self,ev,value,server):
    self._wait_cursor = None;     # clear any wait-cursors
    app_proxy_gui._detached_server_event(self,ev,value,server);
    self._connect_dialog.attach_to_server(None);
    self._autoreq_timer.stop();
    self._autoreq_sent = False;
    self._wstat.hide();
    self._wstat.emit(SIGNAL("shown"),False,);
    self.treebrowser.connected(False);
    self.resultlog.connected(False);
    self._gw_reset_bookmark_actions();
    wtop = self.resultlog.wtop();
    index = self.maintab.indexOf(wtop);
    self.maintab.setTabIcon(index,wtop._default_icon);
    self.maintab.setTabText(index,wtop._default_label);

  def ce_ProcessStatus (self,ev,value):
    _dprint(5,'status:',ev,value);
    self._wstat.setStatus(list(map(int,value)));

  def _checkStateUpdate (self,ev,value):
    try:
      state = value.node_state;
      name  = state.name;
    except AttributeError:
      return None;
    _dprint(5,'got state for node ',name);
    self.update_node_state(state,ev);
    meqds.update_node_state(state,ev);
    return True;

  _prefix_NodeStatus = hiid('node.status');
  # override handleAppEvent to catch node state updates, whichever event they
  # may be in
  def handleAppEvent (self,ev,value,server):
    # call top-level handler
    app_proxy_gui.handleAppEvent(self,ev,value,server);
    # state events are processed regardless of which server they came from
    if ev is self.app.server_state_event:
      self._connect_dialog.update_server_state(server,value);
    # all other events are processed for the currently connected server only
    if server is not self.app.current_server:
      return;
    # check for node status
    if ev.startswith(self._prefix_NodeStatus):
      (ni,status,rqid) = (ev.get(2),ev.get(3),ev[4:]);
      _dprint(5,'got status for node',ni,':',status,rqid);
      try: node = meqds.nodelist[ni];
      except KeyError: pass;
      else: node.update_status(status,rqid);
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
      if fstatus is not None:
        self.treebrowser.update_forest_status(fstatus);
      # check for change of working directory, make sure browser tracks that of kernel
      cwd = getattr(value,'cwd',None);
      if cwd and os.path.exists(cwd) and not os.path.samefile(cwd,os.getcwd()):
        self.change_working_directory(cwd,browser=True,kernel=False);
    # auto-request mechanism:
    # if we're not up-to-date with a node list or forest state, start a timer as soon as we
    # reach idle mode or stopped mode. If this timer is allowed to expire, consider the
    # application "quiet" and go request an update
    if not ev.startswith("process.status"):
      if self._connected:
        if self._have_nodelist and self._have_forest_state:
          self._autoreq_timer.stop();
        elif self.app.current_server:
          state = self.app.current_server.state;
          if state == treebrowser.AppState.Idle or state == treebrowser.AppState.Debug:
            if not self._autoreq_disable_timer.isActive():
              self._autoreq_sent = False;
              self._autoreq_timer.start(800);

  def _auto_update_request (self):
    state = self.app.current_server and self.app.current_server.state;
    if state == treebrowser.AppState.Idle or state == treebrowser.AppState.Debug:
      if self._autoreq_sent:  # refuse to send additional requests
        return;
      self._autoreq_sent = True;
      # and, don't send nodelist requests if one was sent <1 second ago.
      if not self._have_nodelist and meqds.age_nodelist_request() > 1:
        meqds.request_nodelist();
      if not self._have_forest_state:
        meqds.request_forest_state();

  def ce_NodeState (self,ev,value):
    if hasattr(value,'name'):
      _dprint(5,'got state for node ',value.name);
      meqds.update_node_state(value,ev);
      self.update_node_state(value,ev);

  def ce_NodeResult (self,ev,value):
    self.update_node_state(value,ev);
    if self._qa_log_results.isChecked():
      print("### received result for node",getattr(value,'name',''));
      print(value);
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
        udi=udi,name=name,desc=desc,caption=caption,viewopts=meqgui.defaultResultViewopts,flood_protection=0);
      wtop = self.resultlog.wtop();
      if self.maintab.currentWidget() is not wtop and not wtop._newresults:
        itab = self.maintab.indexOf(wtop);
        self.maintab.setTabText(itab,wtop._newres_label);
        self.maintab.setTabIcon(itab,wtop._newres_icon);
        wtop._newresults = True;

  def ce_LoadNodeList (self,ev,meqnl):
    if not meqds.nodelist.is_valid_meqnodelist(meqnl):
      _dprint(2,"got nodelist but it is not valid, ignoring");
      return;
    self._autoreq_timer.stop();
    # create a wait-cursor if not already waiting
    if self._wait_cursor is not None:
      self._wait_cursor = self.wait_cursor();
    self._have_nodelist = True;
    self._autoreq_timer.stop();
    meqds.nodelist.load(meqnl);
    _dprintf(2,"loaded %d nodes into nodelist\n",len(meqds.nodelist));
    # re-update forest status, if available
    try:
      fst = meqnl.forest_status;
      num_init_err = fst.num_init_errors;
    except AttributeError:
      num_init_err = 0;
      pass;
    else:
      self.treebrowser.update_forest_status(fst);
    # clear wait-cursor
    self._wait_cursor = None;
    # if we have just compiled a script, and there are no init errors, show the jobs
    if getattr(self,'_show_tdljobs_on_nodelist',False) and not num_init_err:
      self._show_tdljobs_on_nodelist = False;
      self._show_current_tdl_jobs();


  def update_node_state (self,node,event=None):
    meqds.reclassify_nodestate(node);
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

  def _reset_resultlog_label (self,index):
    tabwin = self.maintab.widget(index);
    if tabwin is self.resultlog.wtop() and tabwin._newresults:
      self._reset_maintab_label(tabwin);
      tabwin._newresults = False;

  def _update_app_state (self):
    app_proxy_gui._update_app_state(self);
    server = self.app.current_server;
    # if server is active, update window caption accordingly
    if server:
      server_name = str(server.session_name) or '%s.%s'%(str(server.addr[0]),str(server.addr[2]));
      if server.remote:
        server_name += "@"+server.host;
      caption = "MeqBrowser - %s (%s)"%(server_name,server.state);
      if self._main_tdlfile:
        caption += " - %s"%os.path.basename(self._main_tdlfile);
      self.setWindowTitle(caption);
      self.treebrowser.update_app_state(self.app.current_server.state);
    else:
      self.setWindowTitle("MeqBrowser - not connected to a meqserver");

  def show_purr_window (self):
    if not self._purr:
      self._purr = Purr.MainWindow.MainWindow(self,hide_on_close=True);
    if not self._purr.hasPurrlog():
      if not Purr.Startup.startWizard([os.getcwd()],self._purr):
        return;
    self._purr.show();
    self._purr.raise_();

  def attach_purr (self,dirname,watchdirs=[],show=True,modal=True):
    if not self._purr:
      self._purr = Purr.MainWindow.MainWindow(self,hide_on_close=True);
    if Purr.Startup.startWizard([dirname]+list(watchdirs),self._purr,modal=modal):
      self._purr.show();


# register reloadables
reloadableModule(__name__);
# reloadableModule('meqds');

