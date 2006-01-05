#!/usr/bin/python

from Timba.Apps import app_defaults
if app_defaults.include_gui:
  import Timba.GUI.app_proxy_gui;
  import Timba.qt_threading;

from Timba.dmi import *
from Timba import octopussy
from Timba import py_app_launcher

import threading
import sys
import os
import string
import time

_dbg = verbosity(0,name='app_proxy');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# class app_proxy
class app_proxy (verbosity):
  """app_proxy is an interface to a remote OCTOPUSSY workprocess that 
  accepts commands. The app is assumed to use the following message IDs:
  <appclass>.In.*     for incoming messages
  <appclass>.Out.*    for outgoing messages
  <appclass>.Debug.*  for outgoing debug messages
  """;
  
  set_debug = staticmethod(octopussy.set_debug);
  setdebug = staticmethod(octopussy.set_debug);
  
  def __init__(self,appid,client_id,launch=None,spawn=None,
               verbose=0,wp_verbose=0,
               gui=False,threads=False,debug=True):
    verbosity.__init__(self,verbose,name=str(appid));
    self.appid = hiid(appid);
    self.client_id = hiid(client_id);
    self._rcv_prefix = self.appid + "Out";          # messages from app
    self._rcv_prefix_debug = self.appid + "Debug";  # debug messages from app
    self._snd_prefix = self.appid + "In";           # messages to app
    _dprint(1,"initializing");

    # start a proxy wp. Select threaded or polled version, depending on
    # arguments
    if wp_verbose is None:
      wp_verbose = verbose;
    
    if threads:
      _dprint(1,"running in threaded mode");
      # select threading API
      if gui: api = Timba.qt_threading;
      else:   api = threading;
      self._pwp = octopussy.proxy_wp_thread(str(client_id),verbose=wp_verbose,thread_api=api);
    else:
      _dprint(1,"running in non-threaded mode");
      self._pwp = octopussy.proxy_wp(str(client_id),verbose=wp_verbose);
      
    # subscribe and register handler for app events
    self._pwp.whenever(self._rcv_prefix+"*",self._event_handler,subscribe=True);
    if debug:
      self._pwp.whenever(self._rcv_prefix_debug+"*",self._event_handler,subscribe=True);
    # subscribe to app hello message 
    self._pwp.whenever('wp.hello'+self.appid+'*',self._hello_handler,subscribe=True);
    # subscribe to app bye message 
    self._pwp.whenever('wp.bye'+self.appid+'*',self._bye_handler,subscribe=True);
    # subscribe to down message
    self._pwp.whenever('gw.remote.down.*',self._remote_down_handler,subscribe=True);
    # subscribe to process status
    self._pwp.whenever('process.status.*',self._process_stat_handler,subscribe=True);
    
    # setup state
    self._verbose_events = True;
    self._error_log = [];
    self._rqid = 1;
    # ------------------------------ this state is meant to be visible
    self.state = None; # None means offline -- we'll get a Hello message for online
    self.statestr = 'no connection';
    self.app_addr = None;
    self.client_addr = self._pwp.address();
    self.paused = False;
    # ------------------------------ export some proxy_wp and octopussy methods
    self.pause_events = self._pwp.pause_events;
    self.resume_events = self._pwp.resume_events;
    # ------------------------------ define default control record
    self.initrec_prev = record(
      throw_error=True,
      control=record(
        event_map_in  = record(default_prefix=self._snd_prefix),
        event_map_out = record(default_prefix=self._rcv_prefix,
                                debug_prefix=self._rcv_prefix_debug),
        stop_when_end = False ));
      
    # ------------------------------ run/connect to app process
    if spawn: 
      if launch:
        raise ValueError,'specify either launch or spawn, not both';
      if isinstance(spawn,str):
        spawn = spawn.split(" ");
      # subscribe to hello message from remot -- we wait for it
      _dprint(1,"spawning",spawn);
      self.serv_pid = os.spawnv(os.P_NOWAIT,spawn[0],spawn);
      _dprint(1,"spawned external server, pid",self.serv_pid);
      _dprint(2,"waiting for Hello message from app");
      self._req_state = False;
    elif launch: # use py_app_launcher to run a local app thread
      raise RuntimeError,"launch option temporarily disabled";
##       _dprint(1,"launching",launch);
##       (appname,inagent,outagent) = launch;
##       if not appname in py_app_launcher.application_names:
##         raise NameError,appname+' is not a recognized app name';
##       self.initrec_prev.control.delay_init = True;
##       py_app_launcher.launch_app(appname,inagent,outagent,self.initrec_prev);
##       self._req_state = False;
    else: # no launch spec, simply wait for a connection, and request state when it's there
      self._req_state = True;
      pass;
    self._gui_event_handler = lambda ev,value:None;
    
    # start the gui, if so specified
    if gui:
      _dprint(1,"starting a GUI");
      if not app_defaults.include_gui:
        raise ValueError,'gui=True but app_defaults.include_gui=False';
      # gui argument can be a callable object (called to start the gui),
      # or simply True to use a standard GUI.
      if callable(gui):
        self._gui = gui;
      else:
        self._gui = Timba.GUI.app_proxy_gui.app_proxy_gui;
      if threads: 
        _dprint(1,"threading enabled, posting construct event");
        # threaded model: post a GUI construction event to the main app
        mainapp = Timba.GUI.app_proxy_gui.mainapp();
        mainapp.postCallable(self._construct_gui);
        # after GUI has been constructed, start WP event thread
        mainapp.postCallable(self._pwp.start);
      else:
        # non-threaded: construct GUI here & now
        _dprint(1,"threading disabled, constructing GUI immediately");
        self._construct_gui(poll_app=50);
    else:     
      self._gui = None;
      # start the wp event thread now
      self._pwp.start();
    
  def __del__ (self):
    _dprint(1,"destructor");
    self.disconnect();
    
  def disconnect (self):
    if hasattr(self._pwp,'stop'):
      _dprint(1,"stopping proxy_wp thread");
      self._pwp.stop();
      _dprint(1,"stopped");
    
  # poll: dispatches all pending events. Only useful in the unthreaded
  # mode (when an event thread is not running)
  def poll (self):
    return self._pwp.poll_pending_events();
    
  # message handler to actually construct an application's GUI
  def _construct_gui (self,poll_app=None):
    try:
      _dprint(2,"_construct_gui: creating GUI");
      self._gui = self._gui(self,poll_app=poll_app,verbose=self.get_verbose());
      _dprint(2,"_construct_gui: showing GUI");
      self._gui.show();
      if poll_app:
        self._gui_event_handler = self._gui.handleAppEvent;
      else:
        self._gui_event_handler = self._gui._relay_event;
    except:
      (exctype,excvalue,tb) = sys.exc_info();
      self.dprint(0,'exception',str(exctype),'while constructing GUI');
      traceback.print_exc();
      self.dprint(0,'exiting');
      sys.exit(1);
    
  def name(self):
    return str(self.appid);
      
  hello_event = hiid("Hello");
  bye_event = hiid("Bye");
  process_status_event = hiid("Process.Status");
  
  def _hello_handler (self,msg):
    _dprint(2,"got hello message:",msg);
    self.app_addr = getattr(msg,'from');
    if self.state is None:
      self.state = 0;
      self.statestr = 'connected';
    # request state & status 
    if self._req_state:
      _dprint(2,"requesting state and status update");
      self.send_command("Request.State");
    self._gui_event_handler(self.hello_event,getattr(msg,'from'));
      
  def _bye_handler (self,msg):
    _dprint(2,"got bye message:",msg);
    self.app_addr = None;
    self.state = None;
    self.statestr = 'no connection';
    self._gui_event_handler(self.bye_event,getattr(msg,'from'));

  def _process_stat_handler (self,msg):
    _dprint(5,"got process status: ",msg.msgid);
    if self.app_addr is None:
      _dprint(5,"no app address set, ignoring");
      return;
    fromaddr = getattr(msg,'from');
    if fromaddr[2:3] == self.app_addr[2:3]:
      self.app_process_status = msg.msgid[2:];
      _dprint(5,"process status set");
      self._gui_event_handler(self.process_status_event,self.app_process_status);
    else:
      _dprint(5,"process status source does not match app address, ignoring");
    
  def _remote_down_handler (self,msg):
    _dprint(2,"got gw.remote.down message:",msg);
    if self.app_addr:
      if msg.msgid[3:] == self.app_addr[2:]:
        _dprint(2,"matches ourselves, generating synthetic bye");
        self._bye_handler(msg);
      else:
        _dprint(2,"does not match ourselves, ignoring");
    else:
      _dprint(2,"no app address set, ignoring");

  def _event_handler (self,msg):
    "event handler for app";
    _dprint(5,"got message: ",msg.msgid);
    # verify source address
    addr = getattr(msg,'from');
    if self.app_addr is None:
      _dprint(2,"hmmm, no app address set, let's assume this is it",addr);
      self.app_addr = addr;
    else:
      if self.app_addr != addr:
        _dprint(2,"ignoring message from",addr,": doesn't match app address",self.app_addr);
        return;
    # update state if not connected
    if self.state is None:
      self.state = 0;
      self.statestr = 'connected';
    # extract event name: message ID is <appid>.Out.<event>, so get a slice
    event = msg.msgid[len(self.appid)+1:];
    value = msg.payload;
    _dprint(5,"which maps to event: ",event);
    # process state notifications
    if event == 'app.notify.state':
      _dprint(1,value.state_string,' (',value.state,')');
      self.state = str(value.state).lower();
      self.statestr = value.state_string;
    # process messages and error reports
    if isinstance(value,record):
      if value.has_field('error'):
        self.log_error(event,value.error);
      for f in ("text","message","error"):
        if value.has_field(f):
          _dprint(1,'[',f,']',value[f]); 
    # print events if so requested
    if self._verbose_events:
      _dprint(2,'   event:',event);
      _dprint(3,'   value:',value);
    # forward to gui
    self._gui_event_handler(event,value);
    
  def ensure_connection (self):
    "If app is not connected, blocks until it is";
    try:
      self._pwp.pause_events();
      while self.state is None:
        _dprint(2,'no connection to app, awaiting');
        res = self._pwp.await('*',resume=True);  # await anything, but keep looping until status changes
        _dprint(3,'await returns',res);
    finally:
      self._pwp.resume_events();
    
  def send_command (self,msgid,payload=None,priority=5):
    "Sends an app control command to the app";
    msgid = self._snd_prefix + msgid;
    msg = message(msgid,payload=payload,priority=priority);
    # self.relay->[spaste('sending_command_',message)](payload);
    self._pwp.publish(msg);
      
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
    
  def halt (self):
    "sends Halt command to app"
    return self.send_command("Halt");
  def kill (self):
    "sends Halt command to app and exits OCTOPUSSY"
    self.send_command("Halt");
    octopussy.stop();
  def pause (self):
    "sends Pause command to app"
    return self.send_command("Pause");
  def resume (self,payload=None):
    "sends Resume command to app"
    return self.send_command("Resume",payload=payload,priority=10);
    
  def trim_msgid (self,msgid):
    if msgid[:len(self._rcv_prefix)] == self._rcv_prefix:
      return msgid[len(self._rcv_prefix):];
    elif msgid[:len(self._rcv_prefix_debug)] == self._rcv_prefix_debug:
      return msgid[len(self._rcv_prefix_debug):];
    return msgid;

  def event_loop (self,timeout=None):
    "interface to pwp's event loop";
    return self._pwp.event_loop(timeout=timeout);
    
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
    
  def run_gui (self):
    if not app_defaults.include_gui:
      raise RuntimeError,"Can't call run_gui without gui support";
    self._gui.await_gui_exit();
    
