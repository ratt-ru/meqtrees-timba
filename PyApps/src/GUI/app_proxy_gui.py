#!/usr/bin/python

MainApp = None;
MainAppThread = None;

from Timba.dmi import *
from Timba import qt_threading
from Timba.GUI.pixmaps import pixmaps
from Timba import dmi_repr
from Timba import Grid
from Timba.GUI.browsers import *
from Timba.GUI.widgets import *

import sys
import time
from qt import *
import traceback
import weakref
import re
import imp
import sets
import signal


dmirepr = dmi_repr.dmi_repr();

_MessageCategories = {};

# Reloads GUI modules on the fly
# Does not work reliably, so:
_reloading_enabled = False;

_reloadables = sets.Set([ __name__,'app_pixmaps','dmi_repr','app_browsers','gridded_workspace','array_plotter']);
def reloadableModule (name):
  _reloadables.add(name);

def reloadAllModules ():
  imp.acquire_lock();
  try:
    for name in _reloadables:
      try:
        info = imp.find_module(name);
      except ImportError,what:
        print 'skipping module',name,':',what;
      else:
        print 'reloading module:',info[1];
        imp.load_module(*((name,)+info));
  finally:
    imp.release_lock();

def defaultFont ():
  global _def_font;
  try: return _def_font;
  except NameError:
    _def_font = QApplication.font();
  return _def_font;
  
def defaultBoldFont ():
  global _def_bold_font;
  try: return _def_bold_font;
  except NameError:
    _def_bold_font = QFont(defaultFont());
    _def_bold_font.setBold(True);
  return _def_bold_font;
  
def defaultCursor ():
  global _def_default_cursor;
  try: return _def_default_cursor;
  except NameError:
    _def_default_cursor = QCursor(Qt.ArrowCursor);
  return _def_default_cursor;

def hourglassCursor ():
  global _def_hourglass_cursor;
  try: return _def_hourglass_cursor;
  except NameError:
    _def_hourglass_cursor = QCursor(Qt.WaitCursor);
  return _def_hourglass_cursor;
  
def setBusyCursor ():
  QApplication.setOverrideCursor(hourglassCursor());
  
def restoreCursor ():
  QApplication.restoreOverrideCursor();
  
def busyCursorMethod (func):
  def callit (*args,**kw):
    try: 
      setBusyCursor();
      func(*args,**kw);
    finally: restoreCursor();
  return callit;

class Logger(HierBrowser):
  Normal = 0;
  Event  = 1;
  Error  = 2;
  _LogPixmaps =  { Normal:pixmaps.check, Error:pixmaps.exclaim };
  _LogCatNames = { Normal:"message",Event:"event",Error:"error" };
  def __init__(self,parent,name,
               click=None,udi_root=None,
               enable=True,use_clear=True,auto_clear=True,
               limit=-100):
    """Initializes a Logger panel. Arguments are:
          parent:     parent widget
          name:       name of panel (appears at top)
          limit:      initial log size. If <0, then the log size control starts
                      out disabled. If None, size is always unlimited.
          enable:     initial state of enable control (None for no control)
          use_clear:  if True, logger has a clear button
          auto_clear: initial state of auto-clear toggle (None for no toggle)
          click:      callback, called when a log item is clicked
                      (QListView::mouseButtonClicked() signal is connected to this slot)
          udi_root:   the UDI root name corresponding to this logger.
                      if None, then panel name is used instead.
    """;
    self._vbox = QVBox(parent);
    # init the browser base class
    HierBrowser.__init__(self,self._vbox,name,udi_root=udi_root);
    # add controls
    self._controlgrid = QWidget(self._vbox);
    self._controlgrid_lo = QGridLayout(self._controlgrid,2,6);
    self._controlgrid_lo.setColStretch(0,1000);
    self._controlgrid_lo.setColSpacing(1,8);
    self._controlgrid_lo.setColSpacing(3,8);
    self._controlgrid_lo.setColSpacing(5,8);
    self._controlgrid_lo.setSpacing(0);
    self.enabled = enable != False;
    # enable control
    if enable is not None:
      self._enable = QCheckBox("log",self._controlgrid);
      self._enable.setChecked(enable);
      self._enable_dum = QVBox(self._controlgrid);
      QObject.connect(self._enable,SIGNAL('toggled(bool)'),self._toggle_enable);
      self._controlgrid_lo.addWidget(self._enable,0,2);
    else:
      self._enable = None;
    # limit control
    if limit is not None:
      self._limit_enable = QCheckBox("limit",self._controlgrid);
      self._limit_field  = QLineEdit("",self._controlgrid);
      self._limit_field.setFixedWidth(60);
      try: self._limit_field.setInputMask('00000');
      except: pass; # older Qt versions do not support this
      self.wtop().connect(self._limit_enable,SIGNAL('toggled(bool)'),
                      self._limit_field,SLOT('setEnabled(bool)'));
      self.wtop().connect(self._limit_field,SIGNAL('returnPressed()'),
                      self._enter_log_limit);
      self._controlgrid_lo.addWidget(self._limit_enable,0,4);
      self._controlgrid_lo.addWidget(self._limit_field,1,4);
    else:
      self._limit_enable = None;
    # auto-clear control
    if auto_clear is not None:
      self._auto_clear = QCheckBox("clear on connect",self._controlgrid);
      self._auto_clear.setChecked(auto_clear);
      self._controlgrid_lo.addWidget(self._auto_clear,0,6);
    else:
      self._auto_clear = None;
    # clear button
    if use_clear:
      clear = QPushButton("Clear",self._controlgrid);
      QObject.connect(clear,SIGNAL("clicked()"),self.clear);
      self._controlgrid_lo.addWidget(clear,1,6);
    # connect click callback
    if callable(click):
      self._lv.connect(self._lv,
        SIGNAL('mouseButtonClicked(int,QListViewItem*,const QPoint &,int)'),click);
    # set log limit        
    self.set_log_limit(limit);
    # compile regex to match our udi pattern
    self._patt_udi = re.compile("/"+self._udi_root+"/(.*)$");
    # define get_data_item method for the listview
    self.wlistview().get_data_item = self.get_data_item;
    
  def wtop (self):
    return self._vbox;
    
  def enable (self,val=True):
    self._enable.setChecked(val);
    
  def disable (self,val=True):
    self._enable.setChecked(not val);
    
  def connected (self,conn=True):
    if conn and self._auto_clear is not None and self._auto_clear.isOn():
      self.clear();
    
  def _enter_log_limit (self):
    try: self._limit = int(str(self._limit_field.text()));
    except: pass; # catch conversion errors
    self._limit = max(10,self._limit);
    self._limit_field.setText(str(self._limit));
    self.apply_limit(self._limit);
    
  def set_log_limit (self,limit):
    if limit is None:
      self._limit = None;
    else:
      self._limit = abs(limit);
      if self._limit_enable is not None:
        self._limit_field.setText(str(self._limit));
        self._limit_enable.setChecked(limit>0);
        self._limit_field.setEnabled(limit>0);
      self.apply_limit(self._limit);
    
  def add (self,msg,label=None,content=None,
           category=Normal,force=False,
           udi=None,udi_key=None,name=None,caption=None,desc=None,viewopts={}):
    """Adds item to logger. Arguments are:
      msg:     item message (for message column)
      label:   item label (for label column -- timestamp is used if this is None)
      content: item data content (item will be expandable if this is not None)
      category: item category: Normal, Event, Error.
      force:   if False and logging is disabled, add() call does nothing.
               if True, item is always added.
      udi_key: item UDI key, auto-generated if None
    If content is not None, then content will be available to viewers. In
    this case, the following parameters define its properties:
      name:    item name for viewers; if None, then category name is used
      desc:    item description; if None, then label is used
      viewopts: dict of optional viewer settings for this item
    Return value: a QListViewItem
    """;
    # disabled? return immediately
    if not force and not self.enabled:
      return;
    # if label not specified, use a timestamp 
    if label is None:
      label = time.strftime("%H:%M:%S");
    # if udi_key is None, set to the id type object. This will tell the
    # HierBrowser.Item constructor to use the item id for key, rather than 
    # the text in column 0
    if udi is None and udi_key is None:
      udi_key = id;
    # create listview item
    item = self.Item(self.wlistview(),label,msg,udi=udi,udi_key=udi_key, \
      name=name or self._LogCatNames.get(category,self._udi_root),\
      desc=desc or label,caption=caption or name);
    item._category = category;
    # if content is specified, cache it inside the item
    if content is not None:
      # if content is just a single message, override viewable property to False,
      # else let browser decide (=None)
      viewable = None;
      if isinstance(content,dict) and \
         (len(content)==1 and content.keys()[0] in MessageCategories):
        viewable = False;
      item.cache_content(content,viewable=viewable,viewopts=viewopts);
    # add pixmap according to category
    pm = self._LogPixmaps.get(category,None);
    if pm is not None:
      item.setPixmap(2,pm.pm());
    # apply a log limit
    if self._limit is not None:
      self.apply_limit(self._limit);
    # ensure item is visible
    self.wlistview().ensureItemVisible(item);
    return item;
    
  def _toggle_enable (self,en):
    self.enabled = en;
    if en: self.add("logging enabled",category=self.Normal);
    else:  self.add("logging disabled",category=self.Error,force=True);
    
class EventLogger (Logger):
  def __init__(self,parent,name,evmask="*",*args,**kwargs):
    Logger.__init__(self,parent,name,*args,**kwargs);
    self.mask = make_hiid(evmask);
    label = QLabel('Event mask:',self._controlgrid);
    self._controlgrid_lo.addWidget(label,0,0);
    self._evmask_field  = QLineEdit(str(evmask),self._controlgrid);
    self._controlgrid_lo.addMultiCellWidget(self._evmask_field,1,1,0,2);
    self.wtop().connect(self._evmask_field,SIGNAL('returnPressed()'),
                    self._enter_mask);
    self._exclusions = [];
  def _enter_mask(self):
    self.set_mask(str(self._evmask_field.text()));
  def set_mask (self,mask):
    try:
      self.mask = make_hiid(mask);
    except: pass;
    self._evmask_field.setText(str(self.mask));
    self.wtop().emit(PYSIGNAL('maskChanged()'),(self.wtop(),self.mask));
  # adds an exclusion
  def add_exclusion (self,excl_str):
    self._exclusions.append(re.compile(excl_str));
  # for event viewers, use the event name as name, and 'event' as description
  def add (self,msg,*args,**kwargs):
    # omit messages listed in exclusions
    for ex in self._exclusions:
      if ex.match(msg):
        return None;
    label = time.strftime("%H:%M:%S");
    kw = kwargs.copy();
    kw['label'] = label;
    kw['name'] = msg;
    kw['desc'] = 'event '+label;
    Logger.add(self,msg,*args,**kw);

class MessageLogger (Logger):
  def __init__(self,*args,**kwargs):
    Logger.__init__(self,*args,**kwargs);
    self._num_err = 0;
    self.wtop().connect(self._lv,SIGNAL('clicked(QListViewItem*)'),
                        self._clear_error_count);
    
  def add (self,msg,category=Logger.Normal,*args,**kwargs):
    Logger.add(self,msg,category=category,*args,**kwargs);
    # keep track of new errors
    if category is Logger.Error:
      items = self.get_items();
      if self._num_err == 0:
        self._first_err = items[-1];
      self._num_err += 1;
      self.wtop().emit(PYSIGNAL('hasErrors()'),(self.wtop(),self._num_err));
      self._last_err = items[-1];
  def _clear_error_count (self):
    self._num_err = 0;
    self._first_err = self._last_err = None;
    self.wtop().emit(PYSIGNAL('hasErrors()'),(self.wtop(),0));


#--------------------------------------------------------------
#--- app_proxy_gui() class
#--------------------------------------------------------------
class app_proxy_gui(verbosity,QMainWindow,utils.PersistentCurrier):
  def __init__(self,app,verbose=0,size=(500,500),poll_app=None,*args,**kwargs):
    """create and populate the main application window""";
    #------ starts the main app object and event thread, if not already started
    self._qapp = mainapp();
    #------ init base classes
    verbosity.__init__(self,verbose,name=app.name()+"/gui");
    self.dprint(1,"initializing");
    QMainWindow.__init__(self,*args);
    self.app = app;
    self._connected = False;
    
    #------ populate the GUI
    self.populate(size=size,*args,**kwargs);
    
    #------ set size 
    self.setCentralWidget(self.splitter);
    sz = self.size().expandedTo(QSize(size[0],size[1]));
    self.resize(sz);
    
    #------ populate the custom event map
    self._ce_handler_map = { 
      hiid("hello"):            [self.ce_Hello,self.ce_UpdateState],
      hiid("bye"):              [self.ce_Bye,self.ce_UpdateState],
      hiid("app.notify.state"): [self.ce_UpdateState]                };
      
    #------ start timer when in polling mode
    if poll_app:
      self.startTimer(poll_app);
      
    self.dprint(2,"init complete");

  def populate (self,main_parent=None,*args,**kwargs):
    #------ split main window in two
    splitter = self.splitter = QSplitter(QSplitter.Horizontal,main_parent or self);
    splitter.setFrameStyle(QFrame.Box+QFrame.Plain);
    splitter.setChildrenCollapsible(False);
  
    #------ create top-level tab bar
    self.maintab = maintab = QTabWidget(splitter);
    self.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._change_current_page);
    maintab.setTabPosition(QTabWidget.Bottom);
    splitter.setResizeMode(maintab,QSplitter.KeepSize);
    
    #------ create a message log
    self.msglog = MessageLogger(self,"message log",enable=None,limit=1000,
          udi_root='message');
    self.msglog.add('start of log',category=Logger.Normal);
    self.msglog.wtop()._default_label = "Messages";
    self.msglog.wtop()._default_iconset = QIconSet();
    self.msglog.wtop()._error_label = "%d errors";
    self.msglog.wtop()._error_iconset = pixmaps.exclaim.iconset();
    QObject.connect(self.msglog.wtop(),PYSIGNAL("hasErrors()"),self._indicate_msglog_errors);
    QObject.connect(self.msglog.wlistview(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(self.msglog.connected,_args=(True,)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(self.msglog.connected,_args=(False,)));
    # set current page to message log
    self._current_page = self.msglog.wtop();
    
    #------ create an event log
    self.eventlog = EventLogger(self,"event log",limit=1000,evmask="*",
          udi_root='event');
    QObject.connect(self.eventlog.wlistview(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self,PYSIGNAL("connected()"),self.xcurry(self.eventlog.connected,_args=(True,)));
    QObject.connect(self,PYSIGNAL("disconnected()"),self.xcurry(self.eventlog.connected,_args=(False,)));
    
    self.maintab.addTab(self.msglog.wtop(),self.msglog.wtop()._default_label);
    
    self.eventtab = QTabWidget(self.maintab);
    self.maintab.addTab(self.eventtab,"Events");
    
    #------ event window tab bar
    self.eventtab.setTabShape(QTabWidget.Triangular);
    self.eventtab.addTab(self.eventlog.wtop(),"*");
    self.connect(self.eventlog.wtop(),PYSIGNAL("maskChanged()"),self._change_eventlog_mask);
    
    #------ status bar, pause button
    self.statusbar = self.statusBar();
    ## self.pause_button = QToolButton(self.statusbar);
    ## self.pause_button.setAutoRaise(True);
    self.status_label = QLabel(self.statusbar);
    self.status_icon  = QLabel(self.statusbar);
    self.status_icon.setFrameStyle(QFrame.NoFrame);
    self.status_icon.setMinimumWidth(20);
    self.status_icon.setMaximumWidth(20);
    self.status_icon.setAlignment(QLabel.AlignVCenter|QLabel.AlignHCenter);
                 
    ##    self.pause_button.setIconSet(pixmaps.pause_normal.iconset());
    ##    QToolTip.add(self.pause_button,"pause the application");
    ##    self.pause_button.setDisabled(True);
    ##    self.connect(self.pause_button,SIGNAL("clicked()"),self._press_pause);
    ##    self.pause_requested = None;
    
    #------ reload button
    if _reloading_enabled:
      reloadbtn = QToolButton(self.statusbar);
      reloadbtn.setIconSet(pixmaps.reload_slick.iconset());
      QToolTip.add(reloadbtn,"reload Python modules");
      self.connect(reloadbtn,SIGNAL("clicked()"),reloadAllModules);
    
    # self.status_icon.setFrameStyle(QFrame.NoFrame);
    ## self.statusbar.addWidget(self.pause_button,0,True);
    if _reloading_enabled:
      self.statusbar.addWidget(reloadbtn,0,True);
    self.statusbar.addWidget(self.status_icon);
    self.statusbar.addWidget(self.status_label);
    
    #------ gridded workspace
    self.gw = gw = Grid.Workspace(splitter,max_nx=4,max_ny=4);
    splitter.setResizeMode(gw.wtop(),QSplitter.Stretch);
    self.gw_visible = {};
    gw.wtop().hide();
    gw.add_tool_button(Qt.TopRight,pixmaps.remove.pm(),
      tooltip="hide the value browser panel",click=self.hide_gridded_workspace);
    Grid.Services.setDefaultWorkspace(self.gw);
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gridded_workspace_shown);
    
    self.show_workspace_button = DataDroppableWidget(QToolButton)(maintab);
    self.show_workspace_button.setPixmap(pixmaps.view_split.pm());
    self.show_workspace_button.setAutoRaise(True);
    maintab.setCornerWidget(self.show_workspace_button,Qt.BottomRight);
    QObject.connect(self.show_workspace_button,SIGNAL("clicked()"),self.gw.show);
    QObject.connect(self.show_workspace_button,PYSIGNAL("dataItemDropped()"),self.display_data_item);
    QToolTip.add(self.show_workspace_button,"show the viewer panel. You can also drop data items here.");
    
    splitter.setSizes([200,600]);
##    self.maintab.setCornerWidget(self.pause_button,Qt.TopRight);
    
  def _add_ce_handler (self,event,handler):
    self._ce_handler_map.setdefault(make_hiid(event),[]).append(handler);

  def show(self):
    #------ show the main window
    self.dprint(2,"showing GUI"); 
    self._update_app_state();
    QMainWindow.show(self);
    
  def _gridded_workspace_shown (self,shown):
    page = self.maintab.currentPage();
    self.gw_visible[page] = shown;
    # "hide workspace" button only visible when workspace is hidden
    self.show_workspace_button.setHidden(shown)
    
  def show_gridded_workspace (self,shown=True):
    self.gw.show(shown);
    
  def hide_gridded_workspace (self):
    return self.show_gridded_workspace(False);
    
##### slot: called when change-of-page occurs
  def _change_current_page (self,page):
    if page is not self._current_page:
      # clears message from status bar whenever a tab changes
      self.statusbar.clear();
      # emit signals
      self._current_page.emit(PYSIGNAL("leaving()"),());
      page.emit(PYSIGNAL("entering()"),());
      self._current_page = page;
      # show or hide the workspace
      if self.gw_visible.get(page,False):
        self.gw.wtop().show();
        self.show_workspace_button.hide();
      else:
        self.gw.wtop().hide();
        self.show_workspace_button.show();
      
##### displays data item in gridded workspace
  def display_data_item (self,item,kwargs={}):
    Grid.Services.addDataItem(item,gw=self.gw,**kwargs);
    
##### event relay: reposts message as a Qt custom event for ourselves
  MessageEventType = QEvent.User+1;
  def _relay_event (self,event,value):
    self.dprint(5,'_relay_event:',event,value);
    QApplication.postEvent(self,QCustomEvent(self.MessageEventType,(event,value)));
    self.dprint(5,'_relay_event: event posted');
    
##### event handler for timer messages
  def timerEvent (self,event):
    # check WP for messages
    self.app.poll();

##### Qt customEvent handler maps to handleAppEvent(). This is used to relay events
  def customEvent (self,event):
    self.handleAppEvent(*event.data());

##### event handler for app events from octopussy
  def handleAppEvent (self,ev,value):
    self.dprint(5,'appEvent:',ev,value);
    try:
      report = False;
      msgtext = None; 
      if isinstance(value,record):
        for (field,cat) in MessageCategories.items():
          if field in value:
            self.log_message(value[field],content=value,category=cat);
            break;
      # add to event log (if enabled)
      self.eventlog.add(str(ev),content=value,category=Logger.Event);
      # strip off index from end of event
      ev0 = ev;
      if int(ev0[-1]) >= 0:
        ev0 = ev0[:-1];
      # execute procedures from the custom map
      for handler in self._ce_handler_map.get(ev0,()):
        handler(ev,value);
      # finally, just in case we've somehow missed a Hello message,
      # force a connected() signal
      if not self._connected and ev0 != hiid('bye'):
        self.emit(PYSIGNAL("connected()"),("?",));
        self.log_message("found kernel (missed Hello message)",category=Logger.Normal);
        self._connected = True;
    except:
      (exctype,excvalue,tb) = sys.exc_info();
      self.dprint(0,'exception',str(exctype),'while handling event ',ev);
      traceback.print_exc();
      
##### custom event handlers for various messages
  def ce_Hello (self,ev,value):
    self.emit(PYSIGNAL("connected()"),(value,));
    self.log_message("found kernel ("+str(value)+")",category=Logger.Normal);
    self.gw.clear();
    self._connected = True;
    
  def ce_Bye (self,ev,value):
    self.emit(PYSIGNAL("disconnected()"),(value,));
    self.log_message("kernel disconnected",category=Logger.Normal);
    self._update_app_state();
    self._connected = False;
    
  def ce_UpdateState (self,ev,value):
    self._update_app_state();
    
##### updates status bar based on app state 
  StatePixmaps = { None: pixmaps.stop };
  StatePixmap_Default = pixmaps.check;
  def _update_app_state (self):
    state = self.app.statestr.lower();
    self.status_label.setText(' '+state+' '); 
    pm = self.StatePixmaps.get(self.app.state,self.StatePixmap_Default);
    self.status_icon.setPixmap(pm.pm());
    # update window title        
    if self.app.app_addr is None:
      self.setCaption(self.app.name()+" - "+state);
    else:
      self.setCaption(str(self.app.app_addr)+" - "+state);
####### slot: pause button pressed
##  def _press_pause (self):
##    if self.pause_requested is None:
##      if self.app.paused:
##        self.pause_requested = False;
##        self.app.resume();
##      else:
##        self.pause_requested = True;
##        self.app.pause();
##    ## self.pause_button.setDown(True);
##### slot for the Event tab bar -- changes the label of a particular event logger
  def _change_eventlog_mask (self,logger,mask):
    self.eventtab.setTabLabel(logger,str(mask));
##### slot: adds error count to label of message logger
  def _indicate_msglog_errors (self,logger,numerr):
#    try: has_err = logger._numerr > 0;
#    except AttributeError: has_err = False;
#    # only add when going from or to 0 errors
#     if numerr and not has_err:
#       self.maintab.changeTab(logger,logger._error_iconset,logger._error_label % numerr);
#     elif not numerr and has_err:
#       self._reset_maintab_label(logger);
#     logger._numerr = numerr;
    if numerr:
      self.maintab.changeTab(logger,logger._error_iconset,logger._error_label % numerr);
    else:
      self._reset_maintab_label(logger);
      
  # resets tab label to default values
  def _reset_maintab_label (self,tabwin):
    self.maintab.changeTab(tabwin,tabwin._default_iconset,tabwin._default_label);
    
  def log_message(self,msg,content=None,category=Logger.Normal):
    self.msglog.add(msg,content=content,category=category);
    if self.maintab.currentPage() is not self.msglog.wtop():
      self.statusbar.message(msg,2000);

  def await_gui_exit ():
    global MainApp,MainAppThread;
    if MainAppThread:
      MainAppThread.join();
    else:
      try:
        MainApp.exec_loop(); 
      except KeyboardInterrupt: pass;
        
  await_gui_exit = staticmethod(await_gui_exit);  

MessageCategories = record( error   = Logger.Error,
                            message = Logger.Normal,
                            text    = Logger.Normal );
    
#--------------------------------------------------------------
#--- MainAppClass
#--------------------------------------------------------------
class MainAppClass (QApplication):
  _started = False;
  _waitcond = qt_threading.Condition();
  def __init__ (self,args):
    if self._started:
      raise "Only one MainApp may be started";
    QApplication.__init__(self,args);
    self.setDesktopSettingsAware(True);
#    # set 10pt font as default
#    font = self.font();
#    font.setPointSize(12);
#    self.setFont(font);
#    font = QFont("Georgia",10);
#    font.setStyleHint(QFont.System);
#    self.setFont(font);
    self.connect(self,SIGNAL("lastWindowClosed()"),self,SLOT("quit()"));
    # connect Ctrl+C handler
    signal.signal(signal.SIGINT,self.__sigint_handler);
    # notify all waiters
    self._waitcond.acquire();
    self._started = True;
    self._waitcond.notifyAll();
    self._waitcond.release();
    
  def __sigint_handler (self,sig,stackframe):
    print 'signal',sig;
    self.quit();
  
  # This event is used to pass a callable object into the main app thread.
  # see customEvent() implementation, below
  EvType_Callable = QEvent.User+2;
  
  def customEvent(self,ev):
    if ev.type() == self.EvType_Callable:
      (func,args,kwargs) = ev.data();
      func(*args,**kwargs);
      
  def postCallable(self,func,*args,**kwargs):
    self.postEvent(self,QCustomEvent(self.EvType_Callable,(func,args,kwargs)));

def mainapp ():
  """Creates if needed, and returns the MainApp object."""
  global MainApp;
  if not MainApp:
    MainApp = MainAppClass(sys.argv);
  return MainApp;

def mainapp_run ():
  MainApp.exec_loop();
  
def mainapp_threaded():
  """Creates the MainApp object and runs its event loop in its own thread. 
  Not recommended."""
  global MainApp,MainAppThread;
  def _run_mainapp_thread ():
    global MainApp;
    # start the app 
    MainApp = MainAppClass(sys.argv);
    # start the event loop thread
    MainApp.exec_loop();

  if MainAppClass._started:
    return MainApp;
  # start the main app in a separate thread
  MainAppThread = qt_threading.QThreadWrapper(_run_mainapp_thread);
  MainAppThread.start();
  # wait for start to complete
  MainAppClass._waitcond.acquire();
  while not MainAppClass._started:
    MainAppClass._waitcond.wait();
  MainAppClass._waitcond.release();
  return MainApp;
  
if __name__=="__main__":
  pass;
