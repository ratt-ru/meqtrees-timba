#!/usr/bin/python

import sys
import time
from qt import *
from dmitypes import *
import qt_threading

MainApp = None;

def initPixmaps ():
  global _pixmaps;
  _pixmaps = {};
  _pixmaps['exclaim'] = QPixmap([ "14 14 3 1",
          "       c None",
          ".      c red",
          "X      c yellow",
          "              ",
          "     ....     ",
          "    ......    ",
          "    ......    ",
          "    ......    ",
          "    ......    ",
          "    ......    ",
          "     ....     ",
          "     ....     ",
          "      ..      ",
          "              ",
          "      ..      ",
          "     ....     ",
          "      ..      " ]);

  _pixmaps['check'] = QPixmap([ "11 11 2 1",
          "@ c #00FF40",
          "_ s none m none c none",
          "__________@",
          "_________@@",
          "________@@@",
          "_______@@@_",
          "_@@___@@@__",
          "@@@__@@@___",
          "@@@_@@@____",
          "@@@@@@_____",
          "@@@@@______",
          "@@@@_______",
          "_@@________"
          ]);

def getPixmap (name):
  global _pixmaps;
  return _pixmaps[name];

class RecordBrowser (object):
  TypeToStr = {};
  for t in (bool,int,long,float,complex):
    TypeToStr[t] = str;
  TypeToStr[hiid] = lambda x:'hiid: '+str(x);
  TypeToStr[str] = lambda x:'"'+x+'"';
  
  # adds content to listview item: marks as expandable,
  # ensures content is a dict
  def add_item_content(self,item,content):
    item.setExpandable(True);
    if isinstance(content,dict):
      item._content = content;
    elif isinstance(content,message):
      item._content = {};
      for k in filter(lambda x:not x.startswith('_'),dir(content)):
        item._content[k] = getattr(content,k);
    else:
      item._content = {"":content};
  
  def insert_item_content(self,item):
    if hasattr(item,'_content_list'):
      return;
    item._content_list = [item];
    for (key,value) in item._content.iteritems():
      if self.TypeToStr.has_key(type(value)):
        itemstr = self.TypeToStr[type(value)](value);
        i0 = QListViewItem(item,item._content_list[-1],str(key),"",itemstr);
      elif isinstance(value,array_class):
        itemstr = 'array';
        i0 = QListViewItem(item,item._content_list[-1],str(key),"",itemstr);
      elif isinstance(value,dict):
        itemstr = "%s [%d]" % (value.__class__.__name__,len(value));
        i0 = QListViewItem(item,item._content_list[-1],str(key),"",itemstr);
        if len(value):
          self.add_item_content(i0,value);
      elif isinstance(value,message):
        itemstr = "message: "+str(value.msgid);
        i0 = QListViewItem(item,item._content_list[-1],str(key),"",itemstr);
        self.add_item_content(i0,value);
      elif isinstance(value,(list,tuple)):
        itemstr = 'seq';
        i0 = QListViewItem(item,item._content_list[-1],str(key),"",str(type(value)));
      else:
        i0 = QListViewItem(item,item._content_list[-1],str(key),"",str(value));
      item._content_list.append(i0);
    
class Logger(RecordBrowser):
  Normal = 0;
  Event  = 1;
  Error  = 2;
  _LogPixmaps = { Normal:'check', Error:'exclaim' };
  def __init__(self,parent,name,limit=-100,enable=True,use_enable=True,use_limit=True):
    self.items = [];
    self._vbox = QVBox(parent);
    self._controlgrid = QWidget(self._vbox);
    self._controlgrid_lo = QHBoxLayout(self._controlgrid);
    self._controlgrid_lo.addStretch();
    if use_enable:
      self._enable = QCheckBox("logging enabled",self._controlgrid);
      self._enable.setChecked(enable);
      self._enable_dum = QVBox(self._controlgrid);
      MainApp.connect(self._enable,SIGNAL('toggled(bool)'),self._toggle_enable);
      self._controlgrid_lo.addWidget(self._enable);
    else:
      self._enable = None;
    if use_limit:
      self._limit_enable = QCheckBox("limit:",self._controlgrid);
      self._limit_field  = QLineEdit("",self._controlgrid);
      self._limit_field.setFixedWidth(60);
      try: self._limit_field.setInputMask('00000');
      except: pass; # older Qt versions do not support this
      MainApp.connect(self._limit_enable,SIGNAL('toggled(bool)'),
                      self._limit_field,SLOT('setEnabled(bool)'));
      MainApp.connect(self._limit_field,SIGNAL('returnPressed()'),
                      self._enter_log_limit);
      self._controlgrid_lo.addWidget(self._limit_enable);
      self._controlgrid_lo.addWidget(self._limit_field);
    else:
      self._limit_enable = None;
    
    self.set_log_limit(limit);
    
    self._lv = QListView(self._vbox);
    self._lv.addColumn("");
    self._lv.addColumn("");
    self._lv.addColumn(name);
    self._lv.setRootIsDecorated(True);
    self._lv.setSorting(-1);
    self._lv.setResizeMode(QListView.LastColumn);
    self._lv.setColumnWidthMode(0,QListView.Maximum);
    self._lv.setColumnWidthMode(1,QListView.Maximum);
    self._lv.setFocus();
    MainApp.connect(self._lv,SIGNAL('expanded(QListViewItem*)'),
                    self.insert_item_content);
    
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
    self.apply_log_limit();
    
  def set_log_limit (self,limit):
    self._limit = abs(limit);
    if self._limit_enable is not None:
      self._limit_field.setText(str(self._limit));
      self._limit_enable.setChecked(limit>0);
      self._limit_field.setEnabled(limit>0);
    self.apply_log_limit();

  def apply_log_limit (self):
    if self._limit>0 and len(self.items) > self._limit:
      for i in self.items[:len(self.items)-self._limit]:
        self._lv.takeItem(i);
      del self.items[:len(self.items)-self._limit];
    
  def add (self,msg,content=None,category=Normal,force=False):
    # disabled? return immediately
    if not force and self._enable and not self._enable.isChecked():
      return;
    # create timestamp and listview item
    timestr = time.strftime("%H:%M:%S");
    if self.items:
      item = QListViewItem(self._lv,self.items[-1],timestr,"",msg);
    else:
      item = QListViewItem(self._lv,timestr,"",msg);
    if content is not None:
      self.add_item_content(item,content);
    # add pixmap according to category
    if category in self._LogPixmaps:
      item.setPixmap(1,getPixmap(self._LogPixmaps[category]));
    # add to list and show
    self.items.append(item);
    self.apply_log_limit();
    self._lv.ensureItemVisible(item);
    
  def _toggle_enable (self,en):
    if en: self.add("logging enabled",category=self.Normal);
    else:  self.add("logging disabled",category=self.Error,force=True);
    
class MessageLogger (Logger):
  def __init__(self,parent,name,evmask="*",*args,**kwargs):
    Logger.__init__(self,parent,name,*args,**kwargs);
    self.mask = make_hiid(evmask);
    self._controlgrid_lo.insertWidget(0,QLabel('Event mask: ',self._controlgrid));
    self._evmask_field  = QLineEdit(str(evmask),self._controlgrid);
    self._controlgrid_lo.insertWidget(1,self._evmask_field);
    MainApp.connect(self._evmask_field,SIGNAL('returnPressed()'),
                    self._enter_mask);

  def _enter_mask(self):
    self.set_mask(str(self._evmask_field.text()));
    
  def set_mask (self,mask):
    try:
      self.mask = make_hiid(mask);
    except: pass;
    self._evmask_field.setText(str(self.mask));
    self.wtop().emit(PYSIGNAL('maskChanged()'),(self.wtop(),self.mask));


#--------------------------------------------------------------
#--- app_proxy_gui() class
#--------------------------------------------------------------
class app_proxy_gui(verbosity,QMainWindow):
  def __init__(self,app,verbose=0,size=(500,500),start=True,*args):
    """create and populate the main application window""";
    #------ starts the main app object and event thread, if not already started
    self._qapp = _start_mainapp();
    #------ init base classes
    verbosity.__init__(self,verbose,name=app.name()+"/gui");
    self.dprint(1,"initializing");
    QMainWindow.__init__(self,*args);
    self.app = app;
    
    #------ create a message log
    self.msglog = Logger(self,"message log",use_enable=False,limit=1000);
    self.msglog.add('starting up',category=Logger.Normal);
    
    #------ create an event log
    self.eventlog = MessageLogger(self,"event log",limit=1000,evmask="*");
    
    #------ add whenevers to maintain app state
    if hasattr(app,'_pwp'):
      app._pwp.whenever(app._rcv_prefix+"*",self._event_relay,subscribe=True);
      app._pwp.whenever('wp.hello'+app.appid+'*',self._event_relay,subscribe=True);

    #------ toplevel tab bar       
    self.toptab = QTabWidget(self);
    self.toptab.addTab(self.msglog.wtop(),"Message Log");
    
    self.eventtab = QTabWidget(self);
    self.toptab.addTab(self.eventtab,"Event Tracker");
    
    #------ event window tab bar
    self.eventtab.setTabShape(QTabWidget.Triangular);
    self.eventtab.addTab(self.eventlog.wtop(),"*");
    MainApp.connect(self.eventlog.wtop(),PYSIGNAL("maskChanged()"),self._change_eventlog_mask);
    
    #------ status bar
    self.statusbar = QStatusBar(self);
    
    #------ main window layout
    sz = self.size().expandedTo(QSize(size[0],size[1]));
    self.resize(sz);
    self.setCentralWidget(self.toptab)
    self.setCaption(app.name());
    
    #------ show the main window
    self.show();
    
  # starts main app thread     
  def start (self):
    start_mainapp();          # start main event thread, if not yet running
    self.app_thread.start();  # start application thread
    
  # whenever handler -- reposts everything as a Qt custom event for ourselves
  CustomEventType = QEvent.User+1;
  def _event_relay (self,msg):
#    print 'eventRelay: ',msg;
    MainApp.postEvent(self,QCustomEvent(self.CustomEventType,msg));
#    print 'eventRelay returning';
    
  # event handlers for octopussy messages
  def customEvent (self,ev):
#    print 'customEvent: ',ev;
    report = False;
    msg = ev.data();
    print msg;
    msgtext = None; 
    if isinstance(msg.payload,record):
      for (field,cat) in self._MessageFields:
        if msg.payload.has_field(field):
          (msgtext,category) = (msg.payload[field],cat);
          break;
    # messages added to message log, everything else to event log
    if msgtext is not None:
      self.msglog.add(msgtext,msg.payload,category);
    self.eventlog.add(str(self.app.trim_msgid(msg.msgid)),msg,Logger.Event);
#    print 'customEvent returning';
    
  # signal handler for the Event tab bar
  def _change_eventlog_mask (self,logger,mask):
    self.eventtab.setTabLabel(logger,str(mask));
    
  _MessageFields = (('error',   Logger.Error),
                    ('message', Logger.Normal),
                    ('text',    Logger.Normal));
    
  def log_message(self,msg,rec=None,category=Logger.Normal):
    self.msglog.add(msg,rec,category);

  def await_exit ():
    global MainAppThread;
    MainAppThread.join();
  await_exit = staticmethod(await_exit);  

_mainapp_started = False;
_mainapp_waitcond = qt_threading.Condition();

def _run_mainapp_thread ():
  global MainApp,_mainapp_started,_mainapp_waitcond;
  # start the app 
  MainApp = QApplication(sys.argv);
  MainApp.connect(MainApp,SIGNAL("lastWindowClosed()"),MainApp,SLOT("quit()"));
  initPixmaps();
  # notify all waiters
  _mainapp_waitcond.acquire();
  _mainapp_started = True;
  _mainapp_waitcond.notifyAll();
  _mainapp_waitcond.release();
  # start the event loop thread
  MainApp.exec_loop();

def _start_mainapp():
  global MainApp,_mainapp_started,_mainapp_waitcond,MainAppThread;
  if _mainapp_started:
    return MainApp;
  # start the main app in a separate thread
  MainAppThread = qt_threading.QThreadWrapper(_run_mainapp_thread);
  MainAppThread.start();
  # wait for start to complete
  _mainapp_waitcond.acquire();
  while not _mainapp_started:
    _mainapp_waitcond.wait();
  _mainapp_waitcond.release();
  return MainApp;
  
if __name__=="__main__":
  class dummyapp(object):
    def name (self):
      return "test_app"
      
  app = dummyapp();
  gui = app_gui(app,verbose=2);
  start();
