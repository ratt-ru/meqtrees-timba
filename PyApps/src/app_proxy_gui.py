#!/usr/bin/python

import sys
import threading
import time
from qt import *
from dmitypes import *

MainApp = QApplication(sys.argv);

pixmap_exclaim = QPixmap([ "14 14 3 1",
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
        
pixmap_check = QPixmap([ "11 11 2 1",
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


class app_thread(threading.Thread):
  def __init__(self,app,*args,**kwargs):
    self.app = app;
    threading.Thread.__init__(self,*args,**kwargs);
    app.connect(app, SIGNAL("lastWindowClosed()"),
                         app, SLOT("quit()"))
  def run (self):
    self.app.exec_loop();
    
class Logger(object):
  Normal = 0;
  Event  = 1;
  Error  = 2;
  _LogPixmaps = { Normal:pixmap_check, Error:pixmap_exclaim };
  def __init__(self,parent,name,limit=-100,enable=True,use_enable=True,use_limit=True):
    self._vbox = QVBox(parent);
    self._controlgrid = QGrid(2,Qt.Horizontal,self._vbox);
    if use_enable:
      self._enable = QCheckBox("log enabled",self._controlgrid);
      self._enable.setChecked(enable);
      self._enable_dum = QVBox(self._controlgrid);
    else:
      self._enable = None;
    if use_limit:
      self._limit_enable = QCheckBox("limit",self._controlgrid);
      self._limit_value  = QLineEdit(str(abs(limit)),self._controlgrid);
      self._limit_value.setMaxLength(4);
      self._limit_enable.setChecked(limit>0);
      self._limit_value.setEnabled(limit>0);
      MainApp.connect(self._limit_enable,SIGNAL('toggled(bool)'),
                      self._limit_value,SLOT('setEnabled(bool)'));
#      MainApp.connect(self._limit_enable,SIGNAL('toggle(int)'),
#                      lambda x:self._limit_value.setDisabled(x));
                      
    
    self._lv = QListView(self._vbox);
    self._lv.addColumn("");
    self._lv.addColumn("");
    self._lv.addColumn(name);
    self._lv.setRootIsDecorated(False);
    self._lv.setSorting(-1);
    self._lv.setResizeMode(QListView.LastColumn);
    self._lv.setColumnWidthMode(0,QListView.Maximum);
    self._lv.setColumnWidthMode(1,QListView.Maximum);
    self.items = [];
    
  def wtop (self):
    return self._vbox;
    
  def add (self,msg,rec=None,category=Normal):
    if self._enable and not self._enable.isChecked():
      return;
    timestr = time.strftime("%H:%M:%S");
    print msg;
    if self.items:
      item = QListViewItem(self._lv,self.items[-1],timestr,"",msg);
    else:
      item = QListViewItem(self._lv,timestr,"",msg);
    if category in self._LogPixmaps:
      item.setPixmap(1,self._LogPixmaps[category]);
    self.items.append(item);
    
class app_gui(verbosity,QMainWindow):
  def __init__(self,app,verbose=0,*args):
    self.app = app;
    print dir(app);
    verbosity.__init__(self,verbose,name=app.name());
    self.dprint(1,"initializing");
    QMainWindow.__init__(self,*args);
    self.setCaption(app.name());
    
    #------ create a message log
    self.msglog = Logger(self,"message log",use_enable=False);
    self.msglog.add('starting up',category=Logger.Normal);
    
    #------ create an event log
    self.eventlog = Logger(self,"event log");
    
    #------ add whenever to maintain message logs
    if hasattr(app,'whenever'):
      app.whenever('*',self.message_handler);

    #------ tab bar       
    self.toptab = QTabWidget(self);
    self.toptab.addTab(self.msglog.wtop(),"Messages");
    self.toptab.addTab(self.eventlog.wtop(),"Events");
    
    #------ main window layout
    self.setCentralWidget(self.toptab)
    self.show();

  _MessageFields = (('error',   Logger.Error),
                    ('message', Logger.Normal),
                    ('text',    Logger.Normal));
    
  def message_handler (self,msg):
    report = False;
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
    else: 
      self.eventlog.add(str(self.app.trim_msgid(msg.msgid)),msg,Logger.Event);
    
  def log_message(self,msg,rec=None,category=Logger.Normal):
    self.msglog.add(msg,rec,category);

MainAppThread = app_thread(MainApp);
thread_started = False;

def start():
  global MainApp,MainAppThread,thread_started;
  if not thread_started:
    thread_started = True;
    MainAppThread.start();

if __name__=="__main__":
  class dummyapp(object):
    def name (self):
      return "test_app"
      
  app = dummyapp();
  gui = app_gui(app,verbose=2);
  start();
