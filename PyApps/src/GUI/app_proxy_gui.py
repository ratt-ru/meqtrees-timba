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

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

import traceback
import weakref
import re
import imp
import signal

dmirepr = dmi_repr.dmi_repr();

_dbg = verbosity(0,name='appgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

_MessageCategories = {};

# Reloads GUI modules on the fly
# Does not work reliably, so:
_reloading_enabled = False;

_reloadables = set([ __name__,'app_pixmaps','dmi_repr','app_browsers','gridded_workspace','array_plotter']);
def reloadableModule (name):
  _reloadables.add(name);

def reloadAllModules ():
  imp.acquire_lock();
  try:
    for name in _reloadables:
      try:
        info = imp.find_module(name);
      except ImportError as what:
        print('skipping module',name,':',what);
      else:
        print('reloading module:',info[1]);
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
#  _LogPixmaps =  { Normal:pixmaps.gear, Error:pixmaps.round_red_cross };
  _LogPixmaps =  { Error:pixmaps.red_round_cross };
  _LogCatNames = { Normal:"message",Event:"event",Error:"error" };
  def __init__(self,parent,name,
               click=None,udi_root=None,
               enable=True,scroll=False,use_clear=True,auto_clear=True,
               limit=-100):
    """Initializes a Logger panel. Arguments are:
          parent:     parent widget
          name:       name of panel (appears at top)
          limit:      initial log size. If <0, then the log size control starts
                      out disabled. If None, size is always unlimited.
          enable:     initial state of enable control (None for no control)
          scroll:     initial state of scroll control (None for no control)
          use_clear:  if True, logger has a clear button
          auto_clear: initial state of auto-clear toggle (None for no toggle)
          click:      callback, called when a log item is clicked
                      (QListView::mouseButtonClicked() signal is connected to this slot)
          udi_root:   the UDI root name corresponding to this logger.
                      if None, then panel name is used instead.
    """;
    self._vbox = QWidget(parent);
    self._vbox_lo = QVBoxLayout(self._vbox);
    self._vbox_lo.setContentsMargins(0,0,0,0);
    self._vbox_lo.setSpacing(0);
    # init the browser base class
    HierBrowser.__init__(self,self._vbox,name,udi_root=udi_root);
    self._vbox_lo.addWidget(self.treeWidget());
    # add controls
    self._controlgrid = QWidget(self._vbox);
    self._vbox_lo.addWidget(self._controlgrid);
    self._controlgrid_lo = QGridLayout(self._controlgrid); # ,3,6);
    self._controlgrid_lo.setColumnStretch(1,1000);
    for icol in 3,5:
      self._controlgrid_lo.setColumnMinimumWidth(icol,8);
    self._controlgrid_lo.setContentsMargins(0,0,0,0);
    self._controlgrid_lo.setSpacing(0);
    self.enabled = enable != False;
    # enable control
    if enable is not None:
      self._enable = QCheckBox("log",self._controlgrid);
      self._enable.setChecked(enable);
      QObject.connect(self._enable,SIGNAL('toggled(bool)'),self._toggle_enable);
      self._controlgrid_lo.addWidget(self._enable,1,2);
    else:
      self._enable = None;
    # scroll control
    if scroll is not None:
      self._scroll = QCheckBox("scroll",self._controlgrid);
      self._scroll.setChecked(scroll);
      self._controlgrid_lo.addWidget(self._scroll,2,2);
    else:
      self._scroll = None;
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
      self._controlgrid_lo.addWidget(self._limit_enable,1,4);
      self._controlgrid_lo.addWidget(self._limit_field,2,4);
    else:
      self._limit_enable = None;
    # auto-clear control
    if auto_clear is not None:
      self._auto_clear = QCheckBox("autoclear",self._controlgrid);
      self._auto_clear.setChecked(auto_clear);
      self._controlgrid_lo.addWidget(self._auto_clear,1,6);
    else:
      self._auto_clear = None;
    # clear button
    if use_clear:
      clear = QPushButton("Clear",self._controlgrid);
      QObject.connect(clear,SIGNAL("clicked()"),self.clear);
      self._controlgrid_lo.addWidget(clear,2,6);
    # connect click callback
    if callable(click):
      QObject.connect(self.treeWidget(),SIGNAL('mouseButtonClicked()'),click);
    # event counter
    self._event_count = 0;
    # set log limit
    self.set_log_limit(limit);
    self._disable_until = 0;
    self._prev_event_clock = 0;
    self._flood_clock = 0;
    self._flood_count = 0;
    # compile regex to match our udi pattern
    self._patt_udi = re.compile("/"+self._udi_root+"/(.*)$");
    # define get_drag_item methods for the listview
    self.treeWidget().get_drag_item = self.get_drag_item;
    self.treeWidget().get_drag_item = self.get_drag_item;
    self.treeWidget().header().hide();

  def event_count (self):
    return self._event_count;

  def wtop (self):
    return self._vbox;

  def enable (self,val=True):
    self._enable.setChecked(val);

  def disable (self,val=True):
    self._enable.setChecked(not val);

  def connected (self,conn=True):
    if conn and self._auto_clear is not None and self._auto_clear.isChecked():
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
           flood_protection=50,
           udi=None,udi_key=None,name=None,caption=None,desc=None,viewopts={}):
    """Adds item to logger. Arguments are:
      msg:     item message (for message column)
      label:   item label (for label column -- timestamp is used if this is None)
      content: item data content (item will be expandable if this is not None)
      category: item category: Normal, Event, Error.
      force:   if False and logging is disabled, add() call does nothing.
               if True, item is always added.
      udi_key: item UDI key, auto-generated if None
      flood_protection: if !=0, logger will check the clock, and if more than 'flood_protection'
          events have been received in the past second, will suspend logging for 10 seconds, or until
          one eventless second has elapsed.
    If content is not None, then content will be available to viewers. In
    this case, the following parameters may define its properties:
      name:    item name for viewers; if None, then generated from udi
      caption: item caption for viewers; if None, then generated from udi
      desc:    item description; if None, then label is used
      viewopts: dict of optional viewer settings for this item
    Return value: a QListViewItem
    """
    # disabled? return immediately
    if not force and not self.enabled:
      return None;
    # check for event flood
    if flood_protection:
      clock = time.time();
      # if >3 sec since last event, always reenable the logger and restart the flood counter
      if clock - self._prev_event_clock >= 3:
        self._disable_until = 0;
        self._flood_clock = clock;
        self._flood_count = 0;
      self._prev_event_clock = clock;
      # if logging is temporarily disabled, return
      if clock < self._disable_until:
        return None;
      # count events for a one-second interval
      flood = self._flood_count > flood_protection;
      if clock - self._flood_clock < 1:
        self._flood_count += 1;
      else:
        self._flood_clock = clock;
        self._flood_count = 0;
      if flood:
        msg = "Event flood detected, disabling logging for 10 seconds";
        content = udi = udi_key = None;
        category = Logger.Error;
        self._disable_until = clock+10;
        self._flood_count = 0;
    # # is scrolling enabled?
    # preserve_top_item = self._scroll is not None and not self._scroll.isOn() and \
    #                    self.treeWidget().itemAt(QPoint(0,0));
    # if label not specified, use a timestamp
    self._event_count += 1;
    if label is None:
      label = time.strftime("%H:%M:%S");
    # if udi_key is None, set to the id type object. This will tell the
    # HierBrowser.Item constructor to use the item id for key, rather than
    # the text in column 0
    if udi is None and udi_key is None:
      udi_key = str(self._event_count);
    # create listview item
    item = self.Item(None,label,msg,udi=udi,udi_key=udi_key, \
      name=name,caption=caption,desc=desc or label);
    item._category = category;
    # if content is specified, cache it inside the item
    if content is not None:
      # if content is just a single message, override viewable property to False,
      # else let browser decide (viewable=None)
      viewable = None;
      if isinstance(content,dict) and \
         (len(content)==1 and list(content.keys())[0] in MessageCategories):
        viewable = False;
      item.cache_content(content,viewable=viewable,viewopts=viewopts);
    # add pixmap according to category
    pm = self._LogPixmaps.get(category,None);
    if pm is not None:
      item.setIcon(2,pm.icon());
    # apply a log limit
    if self._limit is not None:
      self.apply_limit(self._limit);
    # if scroll is enabled, ensure item is visible
    self.treeWidget().insertTopLevelItem(self.treeWidget().topLevelItemCount(),item)
    if item._udi:
      self.treeWidget()._content_map[item._udi] = item;
    if self._scroll is None or self._scroll.isChecked():
      self.treeWidget().scrollToItem(item);
    return item;

  def _toggle_enable (self,en):
    self.enabled = en;
    if en: self.add("logging enabled",category=self.Normal);
    else:  self.add("logging disabled",category=self.Error,force=True);

class EventLogger (Logger):
  def __init__(self,parent,name,evmask="*",*args,**kwargs):
    Logger.__init__(self,parent,name,scroll=True,*args,**kwargs);
    # label = QLabel('Event mask:',self._controlgrid);
    # self._controlgrid_lo.addWidget(label,0,0);
    self._evmask_field  = QLineEdit(str(evmask),self._controlgrid);
    self._controlgrid_lo.addWidget(self._evmask_field,0,0,2,6);
    self.wtop().connect(self._evmask_field,SIGNAL('returnPressed()'),
                        self._enter_mask);
    self.set_mask('*');

  def _enter_mask(self):
    self.set_mask(str(self._evmask_field.text()));

  def set_mask (self,mask):
    self._filters = [];
    maskstrings = [];
    for m in mask.split(';'):
      m.strip(); # strips whitespace
      invert = ( m[0] == '!' );
      if invert:
        m = m[1:];
      # try to convert mask to hiid, skip if fails
      try: hm = make_hiid(m);
      except: continue;
      # add a filter
      self._filters.append((invert,hm));
      if invert:
        maskstrings.append('!'+str(hm));
      else:
        maskstrings.append(str(hm));
    self._mask = ';'.join(maskstrings);
    self._evmask_field.setText(self._mask);
    self.wtop().emit(SIGNAL("maskChanged"),self.wtop(),self._mask);

  def get_mask (self):
    return self._mask;

  # for event viewers, use the event name as name, and 'event' as description
  def add (self,msg,*args,**kwargs):
    # apply filters
    for (invert,mask) in self._filters:
      if mask.matches(msg):
        if invert:
          return None;
        else:
          break;
    else: # matched nothing
      return None;
    # add entry
    msg = msg.lower();
    label = time.strftime("%H:%M:%S");
    kw = kwargs.copy();
    kw['udi_key'] = "%s:%d:%s" % (msg,self._event_count,time.strftime("%H%M%S"));
    kw['label'] = label;
    kw['name'] = "%s @%s" % (msg,label);
    kw['caption'] = "%s <small>%s</small>" % (msg,label);
    kw['desc'] = "event %s at %s" % (msg,label);
    Logger.add(self,msg,*args,**kw);

class MessageLogger (Logger):
  def __init__(self,*args,**kwargs):
    Logger.__init__(self,scroll=True,*args,**kwargs);
    self._num_err = 0;
    # self.wtop().connect(self._tw,SIGNAL('clicked(QTreeWidgetItem*)'),
    #                    self._clear_error_count);
    self._wclearerr = QPushButton(pixmaps.exclaim.icon(),"Clear errors",self._controlgrid);
    self._controlgrid_lo.addWidget(self._wclearerr,1,0);
    self._wclearerr.setVisible(False);
    QObject.connect(self._wclearerr,SIGNAL("clicked()"),self._clear_error_count);

  def add (self,msg,category=Logger.Normal,*args,**kwargs):
    label = time.strftime("%H:%M:%S");
    kw = kwargs.copy();
    kw['udi_key'] = "%d:%s" % (self._event_count,label);
    kw['name'] = "message @%s" % (label,);
    kw['caption'] = "message <small>%s</small>" % (label,);
    kw['desc'] = "message at %s" % (label,);
    item = Logger.add(self,msg,category=category,*args,**kw);
    # keep track of new errors
    if item and category is Logger.Error:
      if self._num_err == 0:
        self._first_err = item;
      self._num_err += 1;
      self._wclearerr.setVisible(True);
      self.wtop().emit(SIGNAL("hasErrors"),self.wtop(),self._num_err);
      self._last_err = item;
    return item;
  def _clear_error_count (self):
    self._num_err = 0;
    self._first_err = self._last_err = None;
    self._wclearerr.setVisible(False);
    self.wtop().emit(SIGNAL("hasErrors"),self.wtop(),0);
  def clear (self):
    Logger.clear(self);
    self._clear_error_count();


#--------------------------------------------------------------
#--- some custom event types
#--------------------------------------------------------------
EvType_AppMessage = QEvent.Type(QEvent.User + 1);
EvType_Callable   = QEvent.Type(QEvent.User + 2);

class QAppMessageEvent (QEvent):
  """This custom event class is used to pass a callable object into the main app thread."""
  def __init__ (self,msg,value,server):
    QEvent.__init__(self,EvType_AppMessage);
    self.msg = msg;
    self.value = value;
    self.server = server;

class QCallableEvent (QEvent):
  """This custom event class is used to pass a callable object into the main app thread."""
  def __init__ (self,func,*args,**kwargs):
    QEvent.__init__(self,EvType_Callable);
    self.func = func;
    self.args = args;
    self.kwargs = kwargs;
  def call (self):
    return self.func(*self.args,**self.kwargs);

#--------------------------------------------------------------
#--- app_proxy_gui() class
#--------------------------------------------------------------
class app_proxy_gui(verbosity,QMainWindow,utils.PersistentCurrier):
  def __init__(self,app,verbose=0,size=(500,500),poll_app=None,*args,**kwargs):
    """create and populate the main application window""";
    global gui;
    gui = self;
    #------ starts the main app object and event thread, if not already started
    self._qapp = mainapp();
    #------ init base classes
    verbosity.__init__(self,verbose,name=app.name()+"/gui");
    _dprint(1,"initializing");
    QMainWindow.__init__(self,*args);
    self.app = app;
    self._connected = False;

    self.populate(size=size,*args,**kwargs);

    #------ set size
    self.setCentralWidget(self.splitter);
    sz = self.size().expandedTo(QSize(size[0],size[1]));
    self.resize(sz);

    # events from remote application are emitted as PYSIGNALS taking
    # two arguments. Connect some standard handlers here
    #QObject.connect(self,PYSIGNAL("hello"),self._attached_server_event);
    #QObject.connect(self,PYSIGNAL("hello"),self.xcurry(self._update_app_state));
    #QObject.connect(self,PYSIGNAL("bye"),self._detached_server_event);
    #QObject.connect(self,PYSIGNAL("bye"),self.xcurry(self._update_app_state));
    QObject.connect(self,PYSIGNAL("app.notify.state"),self.xcurry(self._update_app_state));

    #------ start timer when in polling mode
    if poll_app:
      self.startTimer(poll_app);

    global splash_screen;
    if splash_screen is not None:
      splash_screen.finish(self);

    _dprint(2,"init complete");\

  class PanelizedWindow (QWidget):
    def __init__ (self,parent,name,shortname,icon,*args):
      QWidget.__init__(self,parent,*args);
      self._lo = QVBoxLayout(self);
      self._lo.setSpacing(0);
      self._lo.setContentsMargins(2,0,2,0);
      self.name = name;
      self.shortname = shortname;
      self.icon = icon;
      # build title "toolbar"
      titlebar = QFrame(self);
      self._lo.addWidget(titlebar);
      titlebar.setLineWidth(0);
      titlebar.setFrameStyle(QFrame.Panel|QFrame.Raised);
      tblo = QHBoxLayout(titlebar);
      tblo.setMargin(2);
      self.populate_titlebar(titlebar,tblo);
      # separator
      sep = QFrame(self);
      sep.setFrameStyle(QFrame.HLine+QFrame.Sunken);
      self._lo.addWidget(sep);
    def populate_titlebar (self,titlebar,layout):
      icon = QLabel(titlebar);
      pm = self.icon.pixmap(128,128);
      height = pm.height() + 4;
      icon.setPixmap(pm);
      icon.setMargin(0);
      icon.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum);
      icon.setFixedSize(height,height);
      label = QLabel("<b>"+self.name+"</b>",titlebar);
      label.setMargin(0);
      label.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
      label.setFixedHeight(height);
      minbtn = QToolButton(titlebar);
      minbtn.setIcon(pixmaps.minimize_line.icon());
      minbtn.setAutoRaise(True);
      minbtn.setFixedSize(height,height);
      minbtn.setToolTip("Minimize this panel");
      QObject.connect(minbtn,SIGNAL("clicked()"),self.hide);
      layout.addSpacing(2);
      layout.addWidget(icon);
      layout.addSpacing(2);
      layout.addWidget(label);
      layout.addWidget(minbtn);
    def resizeEvent (self,ev):
      self.emit(SIGNAL("resized"));
      return QWidget.resizeEvent(self,ev);
    def setVisible (self,visible):
      _dprint(1,self.name,"visible",visible);
      self.emit(SIGNAL("visible"),visible);
      if visible:
        _dprint(1,'showing',self,self.parent());
        self.emit(SIGNAL("shown"));
      else:
        _dprint(1,'hiding',self,self.parent());
        self.emit(SIGNAL("hidden"));
      QWidget.setVisible(self,visible);
    def visQAction (self,parent=None):
      try: return self._qa_vis;
      except AttributeError: pass;
      qa = self._qa_vis = QAction(self.icon,"Show/hide "+self.name,parent);
      qa.setCheckable(True);
      qa.setChecked(self.isVisible());
      QObject.connect(qa,SIGNAL("triggered(bool)"),self.setVisible);
      QObject.connect(self,PYSIGNAL("visible()"),qa.setChecked);
      return qa;
    def makeMinButton (self,parent):
      return self.MinimizedPanelButton(self,parent);
    def addWidget (self,widget):
      self._lo.addWidget(widget);

    class MinimizedPanelButton (QToolButton):
      def __init__ (self,panel,parent):
        QToolButton.__init__(self,parent);
        self._panel = panel;
        self._label = [ "("+panel.shortname+")",panel.shortname+" " ];
        self.setIcon(panel.icon);
        self.setText(self._label[int(panel.isVisible())]);
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
        self.setToolTip("Show "+panel.name);
        QObject.connect(self,SIGNAL("clicked()"),self._toggle);
        QObject.connect(panel,PYSIGNAL("visible()"),self._show_panel);
        self._default_palette = self.palette();
        self._flash_palette   = QPalette(self.palette());
        self._flash_palette.setBrush(QPalette.Background,QBrush(QColor("yellow")));
      def _toggle (self):
        self._panel.setVisible(not self._panel.isVisible());
      def _show_panel (self,show):
        if show:
          self.setText(self._label[1]);
          self.setFixedWidth(self.width());
        else:
          self.setText(self._label[0]);
          self.setPalette(self._flash_palette);
          QTimer.singleShot(300,self._unsetPalette);
      def _unsetPalette (self):
        self.setPalette(self._default_palette);

  def populate (self,main_parent=None,*args,**kwargs):
    #------ main window contains a splitter
    splitter = self.splitter = QSplitter(Qt.Horizontal,main_parent or self);
    # splitter.setFrameStyle(QFrame.Box+QFrame.Plain);
    splitter.setChildrenCollapsible(True);

    #------ create top-level tab bar
    self.maintab_panel = self.PanelizedWindow(splitter,"Tabbed Tools","Tabs",pixmaps.tabs.icon());
    self.maintab = maintab = QTabWidget(self.maintab_panel);
    self.maintab_panel.addWidget(maintab);
    self.connect(self.maintab,SIGNAL("currentChanged(int)"),self._change_current_page);
    maintab.setTabPosition(QTabWidget.North);
    splitter.setStretchFactor(splitter.indexOf(self.maintab_panel),0);
    _dprint(1,"parent is",self.maintab_panel.parent());

    #------ create a message log
    self.msglog = MessageLogger(self,"message log",enable=None,limit=1000,
          udi_root='message');
    self.msglog.add('start of log',category=Logger.Normal);
    QObject.connect(self.msglog.wtop(),PYSIGNAL("cleared()"),
                    self.curry(self._reset_maintab_label,self.msglog.wtop()));
    QObject.connect(self.msglog.wtop(),PYSIGNAL("hasErrors()"),self._indicate_msglog_errors);
    QObject.connect(self.msglog.treeWidget(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self,PYSIGNAL("isConnected()"),self.msglog.connected);
    # set current page to message log
    self._current_page = self.msglog.wtop();
    self.add_tab(self.msglog.wtop(),"Messages");
    self.msglog.wtop()._error_label = "%d errors";
    self.msglog.wtop()._error_icon = pixmaps.exclaim.icon();
    self._last_log_message = time.clock();
    
    #------ create an event log
    self.eventlog = EventLogger(self,"event log",limit=1000,evmask="*",
          udi_root='event');
    QObject.connect(self.eventlog.treeWidget(),PYSIGNAL("displayDataItem()"),self.display_data_item);
    QObject.connect(self,PYSIGNAL("isConnected()"),self.eventlog.connected);

    self.eventtab = QTabWidget(self.maintab);
    self.eventtab.setTabPosition(QTabWidget.South);
    self.add_tab(self.eventtab,"Events");
    QObject.connect(self.eventtab._show_qaction,SIGNAL("toggled(bool)"),self.eventlog.enable);

    #------ event window tab bar
    self.eventtab.setTabShape(QTabWidget.Triangular);
    self.eventtab.addTab(self.eventlog.wtop(),"*");
    self.connect(self.eventlog.wtop(),PYSIGNAL("maskChanged()"),self._change_eventlog_mask);

    #------ status bar, pause button
    self.statusbar = self.statusBar();
    ## self.pause_button = QToolButton(self.statusbar);
    ## self.pause_button.setAutoRaise(True);
    statholder = QWidget(self.statusbar);
    statholder_lo = QHBoxLayout(statholder);
    statholder_lo.setMargin(2);
    self.status_icon  = QLabel(statholder);
    self.status_label = QLabel(statholder);
    statholder_lo.addWidget(self.status_icon);
    statholder_lo.addWidget(self.status_label);
    # self.status_icon.setFrameStyle(QFrame.NoFrame);
    self.status_icon.setMinimumWidth(20);
    self.status_icon.setMaximumWidth(20);
    self.status_icon.setAlignment(Qt.AlignCenter);


    ##    self.pause_button.setIconSet(pixmaps.pause_normal.icon());
    ##    self.pause_button.setToolTip("pause the application");
    ##    self.pause_button.setDisabled(True);
    ##    self.connect(self.pause_button,SIGNAL("clicked()"),self._press_pause);
    ##    self.pause_requested = None;

    #------ reload button
    if _reloading_enabled:
      reloadbtn = QToolButton(self.statusbar);
      reloadbtn.setIcon(pixmaps.reload_slick.icon());
      reloadbtn.setToolTip("reload Python modules");
      self.connect(reloadbtn,SIGNAL("clicked()"),reloadAllModules);

    # self.status_icon.setFrameStyle(QFrame.NoFrame);
    ## self.statusbar.addWidget(self.pause_button,0,True);
    if _reloading_enabled:
      self.statusbar.addWidget(reloadbtn,0,True);
    self.statusbar.addWidget(statholder);

    #------ gridded workspace
    self.gw_panel = self.PanelizedWindow(splitter,"Gridded Viewers","Grid",pixmaps.view_split.icon());
    self.gw = gw = Grid.Workspace(self.gw_panel,max_nx=4,max_ny=4);
    self.gw_panel.addWidget(self.gw.wtop());
    splitter.setStretchFactor(splitter.indexOf(self.gw_panel),1);
    self.gw_panel.hide();
    QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self.gw_panel.setShown);
    QObject.connect(self.gw.wtop(),PYSIGNAL("showMessage"),self.log_message);

    self.gw_visible = {};
#    gw.add_tool_button(Qt.TopRight,pixmaps.remove.pm(),
#      tooltip="hide the value browser panel",click=self.hide_gridded_workspace);
    Grid.Services.setDefaultWorkspace(self.gw);
    # QObject.connect(self.gw.wtop(),PYSIGNAL("shown()"),self._gridded_workspace_shown);

#     self.show_workspace_button = DataDroppableWidget(QToolButton)(maintab);
#     self.show_workspace_button.setPixmap(pixmaps.view_split.pm());
#     self.show_workspace_button.setAutoRaise(True);
#     maintab.setCornerWidget(self.show_workspace_button,Qt.BottomRight);
#     QObject.connect(self.show_workspace_button,SIGNAL("clicked()"),self.gw.show);
#     QObject.connect(self.show_workspace_button,PYSIGNAL("itemDropped()"),
#                     self.xcurry(self.display_data_item,_argslice=slice(0,1)));
#     self.show_workspace_button.setToolTip("show the viewer panel. You can also drop data items here.");

    splitter.setSizes([200,600]);
##    self.maintab.setCornerWidget(self.pause_button,Qt.TopRight);

  def show(self):
    #------ show the main window
    _dprint(2,"showing GUI");
    self._update_app_state();
    QMainWindow.show(self);

  def add_tab (self,widget,label,icon=None,index=-1):
    widget._default_label = label;
    widget._default_icon  = icon = icon or QIcon();
    widget._default_index = index;
    widget._show_qaction = QAction(icon,label+" tab",self);
    widget._show_qaction.setCheckable(True);
    widget._show_qaction.setChecked(True);
    self.maintab.insertTab(index,widget,icon,label);
    QObject.connect(widget._show_qaction,SIGNAL("toggled(bool)"),
      self.curry(self.show_tab,widget));

  def rename_tab (self,widget,label,icon=None):
    widget._default_label = label;
    index = self.maintab.indexOf(widget);
    self.maintab.setTabText(index,label);
    if icon:
      widget._default_icon = icon;
      self.maintab.setTabIcon(index,icon);
    widget._show_qaction.setText(label);

  def show_tab (self,widget,show=True,switch=True):
    curindex = self.maintab.indexOf(widget);
    if show:
      if curindex<0:
        widget.show();
        self.maintab.insertTab(widget._default_index,widget,widget._default_icon,widget._default_label);
        widget._show_qaction.setChecked(True);
      if switch:
        self.maintab.setCurrentWidget(widget);
    elif not show and curindex >= 0:
      widget._default_index = curindex;
      widget.hide();
      self.maintab.removeTab(curindex);
      widget._show_qaction.setChecked(False);

  def show_gridded_workspace (self,shown=True):
    _dprint(1,"showing",shown);
    self.gw_panel.setShown(shown);
    self.gw.show(shown);

  def hide_gridded_workspace (self):
    return self.show_gridded_workspace(False);

##### slot: called when change-of-page occurs
  def _change_current_page (self,index):
    page = self.maintab.widget(index);
    if page is not self._current_page:
      # clears message from status bar whenever a tab changes
      self.statusbar.clearMessage();
      # emit signals
      self._current_page.emit(SIGNAL("leaving"));
      page.emit(SIGNAL("entering"));
      self._current_page = page;
#       # show or hide the workspace
#       if self.gw_visible.get(page,False):
#         self.gw.wtop().show();
#         self.show_workspace_button.hide();
#       else:
#         self.gw.wtop().hide();
#         self.show_workspace_button.show();

##### displays data item in gridded workspace
  def display_data_item (self,item,kwargs={}):
    Grid.Services.addDataItem(item,gw=self.gw,**kwargs);

##### event relay: reposts message as a Qt custom event for ourselves
  MessageEventType = QEvent.User+1;
  def _relay_event (self,event,value,server):
    _dprint(5,'_relay_event:',event,value);
    ev = QAppMessageEvent(event,value,server);
    QApplication.postEvent(self,ev);
    _dprint(5,'_relay_event: event posted');

##### event handler for timer messages
  def timerEvent (self,event):
    # check WP for messages
    self.app.poll();

##### Qt customEvent handler maps to handleAppEvent(). This is used to relay events
  def customEvent (self,event):
    self.handleAppEvent(event.msg,event.value,event.server);

##### event handler for app events from octopussy
  def handleAppEvent (self,ev,value,server):
    _dprint(5,'appEvent:',ev,value);
    # process server attach/detach events
    if ev == self.app.server_detach_event:
      self._detached_server_event(ev,value,server);
      return;
    elif ev == self.app.server_attach_event:
      self._attached_server_event(ev,value,server);
      return;
    # ignore events not from current server
    if server is not self.app.current_server:
      return;
    # ignore server_state events: they are doubled up
    if ev is self.app.server_state_event:
      return;
    try:
      report = False;
      msgtext = None;
      # see if event contains state updates, or a message to be logged
      if isinstance(value,record):
        # update app state if appropriate fields are found
        if hasattr(value,'app_state') or hasattr(value,'app_state_str'):
          self._update_app_state();
        # the value of 'content' will later determine whether a data object
        # is logged along with the message. This will be the case if the
        # content is anything more complicated than a single string. In
        # all these cases we will reassign to content
        content = None;
        # if there's something else besides the message, add it as hierarchical
        # content to the entry
        if len(value) > 1:
          content = value;
        # look for fields of specific form ('message', 'error', etc.)
        for (field,cat) in list(MessageCategories.items()):
          msg = value.get(field,None);
          if msg is None:
            continue;
          # if msg is a sequence, reverse the order to form up message text
          # if not, make sure it is treated as one anyway
          if isinstance(msg,(list,tuple)):
            content = content or msg;
            msg = msg[-1::-1];
          else:
            msg = [msg];
          text = [];
          # now iterate to collect complete text
          for m in msg:
            # first form: message field is a string
            if isinstance(m,str):
              text.append(m);
            # second form: message field is a record containing 'message' field
            elif isinstance(m,record):
              content = content or m;
              try: text.append(m.message);
              except: pass;
          # have we collected any messages?
          if text:
            if len(text) > 3:
              text = text[:3];
            self.log_message(' / '.join(text),content=content,category=cat);
      # add to event log (if enabled)
      self.eventlog.add(str(ev),content=value,category=Logger.Event);
      # strip off index from end of event
      ev0 = ev;
      if int(ev0[-1]) >= 0:
        ev0 = ev0[:-1];
      # emit event as a PYSIGNAL so that registered handlers can get it
      self.emit(SIGNAL(str(ev).lower()),ev,value);
      ## NB: 31/01/2008: removed this, since we always send an attach event
      ## finally, just in case we've somehow missed a Hello message,
      ## force a connected call signal
      # if not self._connected and ev0 != hiid('bye'):
      #   self._attached_server_event(ev,value,server);
    except:
      (exctype,excvalue) = sys.exc_info()[:2];
      _dprint(0,'exception',str(exctype),'while handling event ',ev);
      traceback.print_exc();

  def _attached_server_event (self,ev,value,server):
    if not self._connected:
      self._connected = True;
      self.emit(SIGNAL("connected"),value,);
      self.emit(SIGNAL("isConnected"),True,);
      self.log_message("attached to server ("+str(server.addr)+")",category=Logger.Normal);
      self.gw.clear();

  def _detached_server_event (self,ev,value,server):
    if self._connected:
      self._connected = False;
      self.emit(SIGNAL("disconnected"),value,);
      self.emit(SIGNAL("isConnected"),False,);
      self.log_message("server detached",category=Logger.Normal);
    self._update_app_state();

##### updates status bar based on app state
  StatePixmaps = { None: pixmaps.red_round_cross };
  StatePixmap_Default = pixmaps.grey_cross;
  def _update_app_state (self):
    if self.app.current_server:
      state = self.app.current_server.statestr.lower();
      self.status_label.setText(' '+state+' ');
      _dprint(2,'app.state is',self.app.current_server.state,', setting pixmap');
      pm = self.StatePixmaps.get(self.app.current_server.state,self.StatePixmap_Default);
      self.status_icon.setPixmap(pm.pm());
      # update window title
      if self.app.current_server.addr is None:
        self.setWindowTitle(self.app.name()+" - "+state);
      else:
        self.setWindowTitle(str(self.app.current_server.addr)+" - "+state);
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
    self.eventtab.setTabText(self.eventtab.indexOf(logger),str(mask));
##### slot: adds error count to label of message logger
  def _indicate_msglog_errors (self,logger,numerr):
#    try: has_err = logger._numerr > 0;
#    except AttributeError: has_err = False;
#    # only add when going from or to 0 errors
#     if numerr and not has_err:
#       self.maintab.changeTab(logger,logger._error_icon,logger._error_label % numerr);
#     elif not numerr and has_err:
#       self._reset_maintab_label(logger);
#     logger._numerr = numerr;
    index = self.maintab.indexOf(logger);
    had_errors = getattr(self,'_had_errors',0);
    if numerr:
      if not had_errors:
        self.maintab.setTabIcon(index,logger._error_icon);
      self.maintab.setTabText(index,logger._error_label%numerr);
      self.maintab.show();
    else:
      self._reset_maintab_label(logger);
    self._had_errors = numerr;

  # resets tab label to default values
  def _reset_maintab_label (self,tabwin,icon=None,label=None):
    index = self.maintab.indexOf(tabwin);
    self.maintab.setTabIcon(index,icon or tabwin._default_icon);
    self.maintab.setTabText(index,label or tabwin._default_label);
    
  def log_message(self,msg,content=None,category=Logger.Normal):
    if category is not None and \
          self.msglog.add(msg,content=content,category=category,flood_protection=20,udi="message") and \
          self.maintab.currentWidget() is not self.msglog.wtop(): 
      self.statusbar.showMessage(msg,2000);

  def await_gui_exit ():
    global MainApp,MainAppThread;
    if MainAppThread:
      MainAppThread.join();
    else:
      try:
        MainApp.exec_();
      except KeyboardInterrupt: pass;
  await_gui_exit = staticmethod(await_gui_exit);

  class OverrideCursor (object):
    """When created, calls QApplication.setOverrideCursor() to change the app
    cursor. When destroyed, calls QApplication.restoreOverrideCursor() to
    restore the cursor. Handy to use as follows:
      tmp = OverrideCursor(Qt.WaitCursor);
      # do lenghty job
      # when 'tmp' goes out of scope, normal cursor automatically restored
    """
    def __init__ (self,cursor):
      QApplication.setOverrideCursor(QCursor(cursor));
    def __del__ (self):
      QApplication.restoreOverrideCursor();

  def override_cursor (cursor):
    """shortcut to create an override-cursor object""";
    return app_proxy_gui.OverrideCursor(cursor);
  override_cursor = staticmethod(override_cursor);

  def wait_cursor ():
    """shortcut to create an hourglass override-cursor""";
    return app_proxy_gui.OverrideCursor(Qt.WaitCursor);
  wait_cursor = staticmethod(wait_cursor);


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
    ## NB: uncomment the line below to have Ctrl+C quit the app
    ## unconditionally (for alternative, see meqserver_gui.py)
    signal.signal(signal.SIGINT,self.__sigint_handler);
    # notify all waiters
    self._waitcond.acquire();
    self._started = True;
    self._waitcond.notifyAll();
    self._waitcond.release();

  def __sigint_handler (self,sig,stackframe):
    print('signal',sig);
    self.quit();

  def customEvent(self,ev):
    if isinstance(ev,QCallableEvent):
      ev.call();

  def postCallable(self,func,*args,**kwargs):
    self.postEvent(self,QCallableEvent(func,*args,**kwargs));


def appgui (widget):
  """finds app_proxy_gui parent of given widget, or None if none""";
  appgui = widget;
  while appgui and not isinstance(appgui,app_proxy_gui):
    appgui = appgui.parent();
  return appgui;

def mainapp ():
  """Creates if needed, and returns the MainApp object."""
  global MainApp;
  if not MainApp:
    MainApp = MainAppClass(sys.argv);
  return MainApp;

splash_screen = None;

def set_splash_screen (pm,message=None):
  mainapp();
  global splash_screen;
  splash_screen = QSplashScreen(pm());
  if message is not None:
    splash_screen.showMessage(message);
  splash_screen.show();

def mainapp_run ():
  MainApp.exec_();

def mainapp_threaded():
  """Creates the MainApp object and runs its event loop in its own thread.
  Not recommended."""
  global MainApp,MainAppThread;
  def _run_mainapp_thread ():
    global MainApp;
    # start the app
    MainApp = MainAppClass(sys.argv);
    # start the event loop thread
    MainApp.exec_();

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
