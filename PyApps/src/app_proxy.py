#!/usr/bin/python

import app_defaults
if app_defaults.include_gui:
  print '========================== Using gui';
  import app_proxy_gui
  from app_proxy_gui import app_gui
  import qt

from dmitypes import *
import octopussy
import py_app_launcher
import sys
import os
import string
import time

# class app_proxy
class app_proxy (verbosity):
  "app_proxy is an interface to a C++ ApplicationBase (see AppAgents)"
  
  set_debug = staticmethod(octopussy.set_debug);
  setdebug = staticmethod(octopussy.set_debug);
  
  def __init__(self,appid,launch=None,spawn=None,
               verbose=0,wp_verbose=0,
               gui=False):
    verbosity.__init__(self,verbose,name=str(appid));
    self.appid = hiid(appid);
    self._rcv_prefix = self.appid + "Out";   # messages from app
    self._snd_prefix = self.appid + "In";       # messages to app
    self.dprint(1,"initializing");

    # start a proxy wp
    if wp_verbose is None:
      wp_verbose = verbose;
    self._pwp = octopussy.proxy_wp_thread(verbose=wp_verbose);
    # subscribe and register handler for app events
    self._pwp.whenever(self._rcv_prefix+"*",self._event_handler,subscribe=True);
    # subscribe to app hello message 
    self._pwp.whenever('wp.hello'+self.appid+'*',self._hello_handler,subscribe=True);
    # setup state
    self._verbose_events = True;
    self._error_log = [];
    self._rqid = 1;
    # ------------------------------ this state is meant to be visible
    self.state = None; # None means offline -- we'll get a Hello message for online
    self.statestr = 'unknown';
    self.status = record();
    self.paused = False;
    # ------------------------------ export some proxy_wp and octopussy methods
    self.pause_events = self._pwp.pause_events;
    self.resume_events = self._pwp.resume_events;
    # ------------------------------ define default control record
    self.initrec_prev = srecord(
      throw_error=True,
      control=srecord(
        event_map_in  = srecord(default_prefix=self._snd_prefix),
        event_map_out = srecord(default_prefix=self._rcv_prefix),
        stop_when_end = False ));
    # ------------------------------ create a gui if requested
    if gui:
      self.dprint(1,'initializing gui');
      if not app_defaults.include_gui:
        raise ValueError,'gui=True but app_defaults.include_gui=False';
      self._gui = app_gui(self,verbose);
      # halt & exit when window is closed
      qapp = app_proxy_gui.MainApp;
      qapp.connect(qapp, qt.SIGNAL("lastWindowClosed()"),self.halt);
      qapp.connect(qapp, qt.SIGNAL("lastWindowClosed()"),octopussy.stop);
      app_proxy_gui.start();
      
    # ------------------------------ run/connect to app process
    if spawn: 
      if launch:
        raise ValueError,'specify either launch or spawn, not both';
      if isinstance(spawn,str):
        spawn = spawn.split(" ");
      # subscribe to hello message from remot -- we wait for it
      self.dprint(1,"spawning",spawn);
      self.serv_pid = os.spawnv(os.P_NOWAIT,spawn[0],spawn);
      self.dprint(1,"spawned external server, pid",self.serv_pid);
      self.dprint(2,"waiting for Hello message from app");
    elif launch: # use py_app_launcher to run a local app thread
      self.dprint(1,"launching",launch);
      (appname,inagent,outagent) = launch;
      if not appname in py_app_launcher.application_names:
        raise NameError,appname+' is not a recognized app name';
      self.initrec_prev.control.delay_init = True;
      py_app_launcher.launch_app(appname,inagent,outagent,self.initrec_prev);
    else: # no launch spec, simply wait for a connection
      pass;
    # start the WP thread
    self._pwp.start();
    
  def name(self):
    return str(self.appid);
      
  def _hello_handler (self,msg):
    self.dprint(2,"got hello message:",msg);
    if self.state is None:
      self.state = -1;

  def _event_handler (self,msg):
    "event handler for app";
    self.dprint(5,"got message: ",msg.msgid);
    if self.state is None:
      self.state = -1;
    # extract event name: message ID is <appid>.Out.<event>, so get a slice
    event = msg.msgid[len(self.appid)+1:];
    value = msg.payload;
    self.dprint(5,"which maps to event: ",event);
    # process some special events
    if event == 'app.notify.state':
      self.dprint(1,value.state_string,' (',value.state,')');
      self.state = value.state;
      self.paused = value.paused;
      self.statestr = value.state_string;
    # update_status: update our status record
    elif event[:3] == 'app.update.status':
      for f in value.field_names():
        self.status[f] = value[f];
      self.dprint(5,'new status record',self.status);
    # process messages and error reports
    if isinstance(value,record):
      if value.has_field('error'):
        self.log_error(event,value.error);
      for f in ("text","message","error"):
        if value.has_field(f):
          self.dprint(1,'[',f,']',value[f]); 
    # print events if so requested
    if self._verbose_events:
      self.dprint(2,'   event:',event);
      self.dprint(3,'   value:',value);
    # old glish code:
    # # forward event to local relay agent
    # $value::event_name := shortname;
    # self.relay->[shortname]($value);
    
  def ensure_connection (self):
    "If app is not connected, blocks until it is";
    try:
      self._pwp.pause_events();
      while self.state is None:
        self.dprint(2,'no connection to app, awaiting');
        res = self._pwp.await('*',resume=True);  # await anything, but keep looping until status changes
        self.dprint(3,'await returns',res);
    finally:
      self._pwp.resume_events();
    
  def send_command (self,msgid,payload=None,priority=5):
    "Sends an app control command to the app";
    msgid = self._snd_prefix + "App.Control" + msgid;
    msg = message(msgid,payload=payload,priority=priority);
    # self.relay->[spaste('sending_command_',message)](payload);
    self._pwp.publish(msg);
      
  def init (self,initrec=None,inputinit=None,outputinit=None,controlinit=None,wait=False):
    "Initializes the app. All four of the records may be supplied,"
    "or any may be omitted to reuse the old record"
    "If wait=T, waits for the app to complete init";
    self.dprint(1,'initializing');
    self.ensure_connection();
    self.dprint(2,'initrec:',initrec);
    self.dprint(2,'input init:',inputinit);
    self.dprint(2,'output init:',outputinit);
    self.dprint(2,'control_init:',controlinit);
    # get init record from previous value or from arguments
    if initrec is not None:
      initrec = make_record(initrec);
    else:
      initrec = self.initrec_prev;
      self.dprint(2,'init: reusing previous initrec:',initrec);
    # get subrecord from previous values or from arguments
    for (f,subrec) in ( ('input',inputinit),('output',outputinit),('control',controlinit) ):
      if subrec is not None:
        initrec[f] = make_record(subrec);
        self.dprintf(2,'init: using %s subrec from parameters\n',f);
      else:
        if initrec.has_field(f):
          self.dprintf(2,'init: initrec contains a %s subrec\n',f);
        else:
          if self.initrec_prev.has_field(f):
            initrec[f] = self.initrec_prev[f];
            self.dprintf(2,'init: using previous %s subrec\n',f);
          else:
            self.dprintf(2,'init: no %s subrec at all\n',f);
    # initialize
    self.initrec_prev = initrec;
    self.dprint(3,'init: initrec is ',initrec);
    # send init command
    if wait: 
      self.pause_events();
    self.send_command("Init",initrec);
    if wait:
      self.dprint(2,'init: awaiting app.notify.init event');
      res = self.await('app.notify.init',resume=True);
      self.dprint(2,'init: got event ',res);

  def set_verbose_events (self,verb=True):
    "enables/disables printing of all incoming events";
    self.verbose_events = verb;

  def new_rqid(self):
    "generates new request ID";
    ret = self._rqid;
    self._rqid = max(0,self._rqid+1);
    return ret;

  def log_error (self,event,error):
    "adds an entry to the error log";
    self._error_log.append((event,error));
    return len(self._error_log);
  def num_errors (self):
    "returns size of error log";
    return len(self._error_log);
  def get_error_log (self,flush=True):
    "returns and flushes (unless flush=False) error log";
    log = self._error_log;
    if flush:
      self._error_log = [];
    return log;
    
  def stop (self):
    "sends Stop command to app"
    return self.send_command("Stop");
  def halt (self):
    "sends Halt command to app"
    return self.send_command("Halt");
  def pause (self):
    "sends Pause command to app"
    return self.send_command("Pause");
  def resume (self,payload=None):
    "sends Resume command to app"
    return self.send_command("Resume",payload=payload,priority=10);
  def reqstatus (self):
    "sends Request.Status command to app"
    return self.send_command("Request.Status");
    
  def trim_msgid (self,msgid):
    if msgid[:len(self._rcv_prefix)] == self._rcv_prefix:
      return msgid[len(self._rcv_prefix):];
    return msgid;

  def whenever (self,*args,**kwargs):
    "interface to pwp's whenever function, with message id translation";
    evid = kwargs.get('msgid',None);
    if evid:
      kwargs['msgid'] = self._rcv_prefix + evid;
    elif len(args):
      args = (self._rcv_prefix + args[0],) + args[1:];
    return self._pwp.whenever(*args,**kwargs);
    
  def await (self,what,timeout=None,resume=False):
    "interface to pwp's event loop, in the await form";
    return self._pwp.await(self._rcv_prefix + what,timeout=timeout,resume=resume);
    
if __name__ == "__main__":
  app_defaults.parse_argv(sys.argv);
  octopussy.init();
  octopussy.start();
  args = app_defaults.args;
  args['verbose'] = 2;
  args['wp_verbose'] = 2;
  args['launch'] = ('repeater','o','o');
  print '================= launching app';
  print 'Args are:',args;
  app = app_proxy('repeater',**args);
  print '================= going into init()';
  app.init(wait=True);
  
  if not args['gui']:
    print '================= sleeping for 2 sec';
    time.sleep(2);
    print '================= stopping octopussy';
    octopussy.stop();
  
  
