#!/usr/bin/python

import sys
import time
from qt import *
from dmitypes import *
import qt_threading
import app_pixmaps as pixmaps
import dmi_repr

MainApp = None;
MainAppThread = None;

dmirepr = dmi_repr.dmi_repr();

class HierBrowser (object):
  
  class BrowserItem (QListViewItem):
    def __init__(self,*args):
      QListViewItem.__init__(self,*args);

    def subitem (self,key,value):
      return self.__class__(self,self._content_list[-1],str(key),"",str(value));

    # caches content in an item: marks as expandable, ensures content is a dict
    def cache_content(self,content):
      self.setExpandable(True);
      if isinstance(content,(dict,list,tuple,array_class)):
        self._content = content;
      elif isinstance(content,message):
        self._content = {};
        for k in filter(lambda x:not x.startswith('_'),dir(content)):
          attr = getattr(content,k);
          if not callable(attr):
            self._content[k] = attr;
      else:
        self._content = {"":content};

    # seqs/dicts with <= items than this are treated as "short"
    ShortSeq       = 5;
    # maximum number of sequence items to show in expanded view
    MaxExpSeq      = 20;
    # max number of dictionary items to show in expanded view
    MaxExpDict     = 100;
    
    # actually expands item content into subitems
    def expand_content(self):
      if hasattr(self,'_content_list'):
        return;
      self._content_list = [self];
      # Setup content_iter as an iterator that returns (label,value)
      # pairs, depending on content type.
      # Apply limits here
      if isinstance(self._content,dict):
        n = len(self._content) - self.MaxExpDict;
        if n > 0:
          keys = self._content.keys()[:self.MaxExpDict];
          content_iter = map(lambda k:(k,self._content[k]),keys);
          content_iter.append(('...','...(%d items skipped)...'%n));
        else:
          content_iter = self._content.iteritems();
      elif isinstance(self._content,(list,tuple,array_class)):
        n = len(self._content) - self.MaxExpSeq;
        if n > 0:
          content_iter = list(enumerate(self._content[:self.MaxExpSeq-2]));
          content_iter.append(('...','...(%d items skipped)...'%(n+1)));
          content_iter.append((len(self._content)-1,self._content[-1]));
        else:
          content_iter = enumerate(self._content);
      else:
        content_iter = (("",self._content),);
      for (key,value) in content_iter:
        # simplest case: do we have an inlined to-string converter?
        # then the value is represented by a single item
        (itemstr,inlined) = dmirepr.inline_str(value);
        if itemstr is not None:
          self._content_list.append( self.subitem(key,itemstr) );
          continue;
        # else get string representation, insert item with it
        (itemstr,inlined) = dmirepr.expanded_repr_str(value);
        i0 = self.subitem(key,itemstr);
        self._content_list.append(i0);
        # cache value for expansion, if not inlined
        if isinstance(value,(list,tuple,dict,array_class)):
          if not inlined:
            i0.cache_content(value);
        elif isinstance(value,message):
          i0.cache_content(value);
        self._content_list.append(i0);
        
  # init for HierBrowser
  def __init__(self,parent,name):
    self._lv = QListView(parent);
    self._lv.addColumn("");
    self._lv.addColumn("");
    self._lv.addColumn(name);
    self._lv.setRootIsDecorated(True);
    self._lv.setSorting(-1);
    self._lv.setResizeMode(QListView.NoColumn);
    self._lv.setColumnWidthMode(0,QListView.Maximum);
    self._lv.setColumnWidthMode(1,QListView.Maximum);
    self._lv.setColumnWidthMode(2,QListView.Maximum);
    self._lv.setFocus();
    self._lv.connect(self._lv,SIGNAL('expanded(QListViewItem*)'),
                     self._expand_item_content);
    self.items = [];
  def wlistview (self):
    return self._lv;
  # inserts a new item into the browser
  def new_item (self,*args):
    if self.items:
      item = self.BrowserItem(self._lv,self.items[-1],*args);
    else:
      item = self.BrowserItem(self._lv,*args);
    self.items.append(item);
    self._lv.ensureItemVisible(item);
    return item;
  # limits browser to last 'limit' items
  def apply_limit (self,limit):
    if limit>0 and len(self.items) > limit:
      for i in self.items[:len(self.items)-limit]:
        self._lv.takeItem(i);
      del self.items[:len(self.items)-limit];
  # called when an item is expanded                    
  def _expand_item_content (self,item):
    item.expand_content();
    
class Logger(HierBrowser):
  Normal = 0;
  Event  = 1;
  Error  = 2;
  _LogPixmaps = { Normal:pixmaps.check, Error:pixmaps.exclaim };
  def __init__(self,parent,name,limit=-100,enable=True,use_enable=True,use_limit=True):
    self._vbox = QVBox(parent);
    self._controlgrid = QWidget(self._vbox);
    self._controlgrid_lo = QHBoxLayout(self._controlgrid);
    self._controlgrid_lo.addStretch();
    if use_enable:
      self._enable = QCheckBox("logging enabled",self._controlgrid);
      self._enable.setChecked(enable);
      self._enable_dum = QVBox(self._controlgrid);
      self.wtop().connect(self._enable,SIGNAL('toggled(bool)'),self._toggle_enable);
      self._controlgrid_lo.addWidget(self._enable);
    else:
      self._enable = None;
    if use_limit:
      self._limit_enable = QCheckBox("limit:",self._controlgrid);
      self._limit_field  = QLineEdit("",self._controlgrid);
      self._limit_field.setFixedWidth(60);
      try: self._limit_field.setInputMask('00000');
      except: pass; # older Qt versions do not support this
      self.wtop().connect(self._limit_enable,SIGNAL('toggled(bool)'),
                      self._limit_field,SLOT('setEnabled(bool)'));
      self.wtop().connect(self._limit_field,SIGNAL('returnPressed()'),
                      self._enter_log_limit);
      self._controlgrid_lo.addWidget(self._limit_enable);
      self._controlgrid_lo.addWidget(self._limit_field);
    else:
      self._limit_enable = None;
    # init the browser base class
    HierBrowser.__init__(self,self._vbox,name);
    
    self.set_log_limit(limit);
    
  def wtop (self):
    return self._vbox;
    
  def enable (self,val=True):
    self._enable.setChecked(val);
    
  def disable (self,val=True):
    self._enable.setChecked(not val);
    
  def _enter_log_limit (self):
    try: self._limit = int(str(self._limit_field.text()));
    except: pass; # catch conversion errors
    self._limit = max(10,self._limit);
    self._limit_field.setText(str(self._limit));
    self.apply_limit(self._limit);
    
  def set_log_limit (self,limit):
    self._limit = abs(limit);
    if self._limit_enable is not None:
      self._limit_field.setText(str(self._limit));
      self._limit_enable.setChecked(limit>0);
      self._limit_field.setEnabled(limit>0);
    self.apply_limit(self._limit);

  def add (self,msg,content=None,category=Normal,force=False):
    # disabled? return immediately
    if not force and self._enable and not self._enable.isChecked():
      return;
    # create timestamp and listview item
    timestr = time.strftime("%H:%M:%S");
    item = self.new_item(timestr,"",msg);
    item._category = category;
    if content is not None:
      item.cache_content(content);
    # add pixmap according to category
    pm = self._LogPixmaps.get(category,None);
    if pm is not None:
      item.setPixmap(1,pm.pm());
    # apply a log limit
    self.apply_limit(self._limit);
    
  def _toggle_enable (self,en):
    if en: self.add("logging enabled",category=self.Normal);
    else:  self.add("logging disabled",category=self.Error,force=True);
    
class EventLogger (Logger):
  def __init__(self,parent,name,evmask="*",*args,**kwargs):
    Logger.__init__(self,parent,name,*args,**kwargs);
    self.mask = make_hiid(evmask);
    self._controlgrid_lo.insertWidget(0,QLabel('Event mask: ',self._controlgrid));
    self._evmask_field  = QLineEdit(str(evmask),self._controlgrid);
    self._controlgrid_lo.insertWidget(1,self._evmask_field);
    self.wtop().connect(self._evmask_field,SIGNAL('returnPressed()'),
                    self._enter_mask);

  def _enter_mask(self):
    self.set_mask(str(self._evmask_field.text()));
    
  def set_mask (self,mask):
    try:
      self.mask = make_hiid(mask);
    except: pass;
    self._evmask_field.setText(str(self.mask));
    self.wtop().emit(PYSIGNAL('maskChanged()'),(self.wtop(),self.mask));
    

class MessageLogger (Logger):
  def __init__(self,*args,**kwargs):
    Logger.__init__(self,*args,**kwargs);
    self._num_err = 0;
    self.wtop().connect(self._lv,SIGNAL('clicked(QListViewItem*)'),
                        self._clear_error_count);
    
  def add (self,msg,content=None,category=Logger.Normal,force=False):
    Logger.add(self,msg,content,category,force);
    # keep track of new errors
    if category is Logger.Error:
      if self._num_err == 0:
        self._first_err = self.items[-1];
      self._num_err += 1;
      self.wtop().emit(PYSIGNAL('hasErrors()'),(self.wtop(),self._num_err));
      self._last_err = self.items[-1];
  def _clear_error_count (self):
    self._num_err = 0;
    self._first_err = self._last_err = None;
    self.wtop().emit(PYSIGNAL('hasErrors()'),(self.wtop(),0));


#--------------------------------------------------------------
#--- app_proxy_gui() class
#--------------------------------------------------------------
class app_proxy_gui(verbosity,QMainWindow):
  def __init__(self,app,verbose=0,size=(500,500),start=True,*args):
    """create and populate the main application window""";
    #------ starts the main app object and event thread, if not already started
    self._qapp = mainapp();
    #------ init base classes
    verbosity.__init__(self,verbose,name=app.name()+"/gui");
    self.dprint(1,"initializing");
    QMainWindow.__init__(self,*args);
    self.app = app;
    
    #------ create a message log
    self.msglog = MessageLogger(self,"message log",use_enable=False,limit=1000);
    self.msglog.add('start of log',category=Logger.Normal);
    self.msglog.wtop()._default_label = "Message Log";
    self.msglog.wtop()._default_iconset = QIconSet();
    self.msglog.wtop()._error_label = "%d errors";
    self.msglog.wtop()._error_iconset = QIconSet(pixmaps.exclaim.pm());
    self.connect(self.msglog.wtop(),PYSIGNAL("hasErrors()"),self._indicate_msglog_errors);
    
    #------ create an event log
    self.eventlog = EventLogger(self,"event log",limit=1000,evmask="*");
    
    #------ toplevel tab bar       
    self.maintab = QTabWidget(self);
    self.maintab.addTab(self.msglog.wtop(),self.msglog.wtop()._default_label);
    
    self.eventtab = QTabWidget(self);
    self.maintab.addTab(self.eventtab,"Event Tracker");
    
    #------ event window tab bar
    self.eventtab.setTabShape(QTabWidget.Triangular);
    self.eventtab.addTab(self.eventlog.wtop(),"*");
    self.connect(self.eventlog.wtop(),PYSIGNAL("maskChanged()"),self._change_eventlog_mask);
    
    #------ status bar
    self.statusbar = QStatusBar(self);
    self.status_label = QLabel(self.statusbar);
    self.status_icon  = QLabel(self.statusbar);
    self.status_icon.setFrameStyle(QFrame.NoFrame);
    self.status_icon.setMinimumWidth(20);
    self.status_icon.setMaximumWidth(20);
    self.status_icon.setAlignment(QLabel.AlignVCenter|QLabel.AlignHCenter);
    # self.status_icon.setFrameStyle(QFrame.NoFrame);
    self.statusbar.addWidget(self.status_icon);
    self.statusbar.addWidget(self.status_label);
    # clears message from status bar whenever a tab changes
    self.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),
                 self.statusbar,SLOT("clear()"));
                 
    #------ pause button
    self.pause_button = QPushButton(self.maintab);
    self.pause_button.setPixmap(pixmaps.pause_normal.pm());
    self.pause_button.setMinimumWidth(35);
    self.pause_button.setMaximumWidth(35);
    self.pause_button.setDisabled(True);
    # self.pause_button.setToggleButton(True);
    self.connect(self.pause_button,SIGNAL("clicked()"),self._press_pause);
    self.pause_requested = None;
    
    self.maintab.setCornerWidget(self.pause_button,Qt.TopRight);
    
    #------ main window layout
    sz = self.size().expandedTo(QSize(size[0],size[1]));
    self.resize(sz);
    self.setCentralWidget(self.maintab)
    self.setCaption(app.name());
    
    #------ show the main window
    self._update_app_state();
    self.show();
    
  #  # starts main app thread     
  #  def start (self):
  #    start_mainapp();          # start main event thread, if not yet running
  #    self.app_thread.start();  # start application thread
    
##### event relay: reposts message as a Qt custom event for ourselves
  MessageEventType = QEvent.User+1;
  def _relay_event (self,event,value):
    # print 'eventRelay: ',msg;
    MainApp.postEvent(self,QCustomEvent(self.MessageEventType,(event,value)));
    # print 'eventRelay returning';

##### event handlers for octopussy messages
  def customEvent (self,event):
    (ev,value) = event.data();
    # print 'customEvent: ',ev;
    report = False;
    print value;
    msgtext = None; 
    if isinstance(value,record):
      for (field,cat) in self._MessageFields:
        if value.has_field(field):
          (msgtext,category) = (value[field],cat);
          break;
    # messages added to message log, everything else to event log
    if msgtext is not None:
      self.msglog.add(msgtext,value,category);
      self.statusbar.message(msgtext,2000);  # display for 2 secs
    self.eventlog.add(str(ev),value,Logger.Event);
    # execute procedures from the custom map
    for proc in self.customEventMap.get(ev,()):
      proc(self,ev,value);
    # print 'customEvent returning';
    
  def ce_Hello (self,ev,value):
    self.msglog.add("connected to "+str(value),None,Logger.Normal);
  def ce_Bye (self,ev,value):
    self.msglog.add("lost connection to "+str(value),None,Logger.Error);
  def ce_UpdateState (self,ev,value):
    self._update_app_state();
    
  customEventMap = { 
    hiid("hello"):            (ce_Hello,ce_UpdateState),
    hiid("bye"):              (ce_Bye,ce_UpdateState),
    hiid("app.notify.state"): (ce_UpdateState,)                };
  
##### updates status bar based on app state 
  StatePixmaps = { None: pixmaps.cancel };
  StatePixmap_Default = pixmaps.check;
  def _update_app_state (self):
    self.status_label.setText(' '+self.app.statestr.lower()+' '); 
    pm = self.StatePixmaps.get(self.app.state,self.StatePixmap_Default);
    self.status_icon.setPixmap(pm.pm());
    self.pause_button.setDisabled(not self.app.state>0);
    if self.app.state>0:
      if self.app.paused:   self.pause_button.setPixmap(pixmaps.pause_green.pm());
      else:                 self.pause_button.setPixmap(pixmaps.pause_normal.pm());
      print self.app.paused,self.pause_requested;
      # if requested pause/resume state is reached, get button up and clear
      if self.pause_requested == self.app.paused:
        print 'Pause state reached!'
        self.pause_button.setDown(False);
        self.pause_requested = None;
##### slot: pause button pressed
  def _press_pause (self):
    if self.pause_requested is None:
      if self.app.paused:
        self.pause_requested = False;
        self.app.resume();
      else:
        self.pause_requested = True;
        self.app.pause();
    self.pause_button.setDown(True);
##### slot for the Event tab bar -- changes the label of a particular event logger
  def _change_eventlog_mask (self,logger,mask):
    self.eventtab.setTabLabel(logger,str(mask));
  # adds error count to label of message logger
  def _indicate_msglog_errors (self,logger,numerr):
    if numerr:
      self.maintab.changeTab(logger,logger._error_iconset,logger._error_label % numerr);
    else:
      self.maintab.changeTab(logger,logger._default_iconset,logger._default_label);

  _MessageFields = (('error',   Logger.Error),
                    ('message', Logger.Normal),
                    ('text',    Logger.Normal));
    
  def log_message(self,msg,rec=None,category=Logger.Normal):
    self.msglog.add(msg,rec,category);

  def await_gui_exit ():
    global MainApp,MainAppThread;
    if MainAppThread:
      MainAppThread.join();
    else:
      MainApp.exec_loop(); 
  await_gui_exit = staticmethod(await_gui_exit);  

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
    self.connect(self,SIGNAL("lastWindowClosed()"),self,SLOT("quit()"));
    # notify all waiters
    self._waitcond.acquire();
    self._started = True;
    self._waitcond.notifyAll();
    self._waitcond.release();
  
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
  class dummyapp(object):
    def name (self):
      return "test_app"
      
  app = dummyapp();
  gui = app_gui(app,verbose=2);
  start();
