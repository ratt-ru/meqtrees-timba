#!/usr/bin/python
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

from Timba.Apps import app_defaults

if app_defaults.include_gui:
  import Timba.GUI.app_proxy_gui;
  if app_defaults.args.threads:
    import Timba.qt_threading;

try:
  from PyQt4.Qt import QObject,SIGNAL
  from Kittens.widgets import PYSIGNAL
except:
  print("Qt not available, substituting proxy types for QObject");
  from .QObject import QObject,PYSIGNAL
  

from Timba.dmi import *
from Timba import octopussy
# from Timba import py_app_launcher
if app_defaults.args.threads:
  import threading
import sys
import os
import os.path
import string
import time
import socket;

class Client (QObject):
  def __init__ (self,name):
    QObject.__init__(self,None);
    self.host = socket.gethostname().split('.')[0];
    self.addr = None;

class Server (QObject):
  def __init__ (self,addr,state=0,statestr=''):
    QObject.__init__(self,None);
    self.addr = addr;
    self.state = state;
    self.statestr = statestr;
    self.process_state = None;
    self.host = None;
    self.remote = None;  # or hostname...
    self.session_id = None;
    self.session_name = None;
    self.cwd = None;

class multiapp_proxy (verbosity):
  """multiapp_proxy is an interface to a multiple remote OCTOPUSSY workprocesses that 
  accepts commands. The app is assumed to use the following message IDs:
  <appclass>.In.*     for incoming messages
  <appclass>.Out.*    for outgoing messages
  <appclass>.Debug.*  for outgoing debug messages
  multiapp_proxy will attempt to discover all connected workprocesses
  """;
  
  set_debug = staticmethod(octopussy.set_debug);
  setdebug = staticmethod(octopussy.set_debug);
  
  def __init__(self,appid,client_id,
               spawn=None,       # spawn process (pass in process name and arguments)
               extra=[],         # extra arguments to spawned process
               wait_init=None,   # wait for process to connect (values in seconds, <0 for unlimited)
               verbose=0,        # verbosity level
               wp_verbose=0,     # WP verbosity level
               gui=False,        # construct a GUI?
               threads=False,    # run communications in separate thread
               checkrefs=False,  # check refs on incoming messages (for debugging)?
               debug=True):      # subscribe to debug messages?
    verbosity.__init__(self,verbose,name=str(appid));
    self._checkrefs = checkrefs;
    self.appid = hiid(appid);
    self.client_id = hiid(client_id);
    self._rcv_prefix = self.appid + "Out";          # messages from app
    self._rcv_prefix_debug = self.appid + "Debug";  # debug messages from app
    self._snd_prefix = self.appid + "In";           # messages to app
    self.dprint(1,"initializing");
    # a client QObject emits global signals
    self.client = Client("client");
    # connected server objects are collected here
    self.servers = dict();
    # this is the "current" server object that we're attached to
    self.current_server = None;
    # we may be set up to auto-attach to a server with a particular pid or host
    self._auto_attach_pid = self._auto_attach_host = None;
    self._auto_attached = False;
    # start a proxy wp. Select threaded or polled version, depending on
    # arguments
    if wp_verbose is None:
      wp_verbose = verbose;
    if threads:
      self.dprint(1,"running in threaded mode");
      # select threading API
      if gui: api = Timba.qt_threading;
      else:   api = threading;
      self._pwp = octopussy.proxy_wp_thread(str(client_id),verbose=wp_verbose,thread_api=api);
    else:
      self.dprint(1,"running in non-threaded mode");
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
    self._command_index = 1;
    # ------------------------------ this state is meant to be visible
    self.client.addr = self._pwp.address();
    self.paused = False;
    # ------------------------------ export some proxy_wp and octopussy methods
    self.pause_events = self._pwp.pause_events;
    self.resume_events = self._pwp.resume_events;
      
    # ------------------------------ run/connect to app process
    self.serv_pid = None;
    if spawn: 
      if isinstance(spawn,str):
        spawn = spawn.split(" ");
      # first argument is app binary
      path = spawn[0];
      args = list(spawn[1:]);
      # extra arguments (after "--" in command line)
      if extra:
        if isinstance(extra,str):
          extra = extra.split(' ');
        args += list(map(str,extra));
      if path[0] != '/': # not absolute path, so need to search $PATH
        for dirname in os.environ['PATH'].split(':'):
          filename = os.path.join(dirname,path);
          if os.path.isfile(filename) and os.access(filename,os.X_OK):
            path = filename;
            break;
      if not os.path.isfile(path) or not os.access(path,os.X_OK):
        raise RuntimeError("can't spawn %s: not an executable file" % (path,));
      self.dprint(1,"spawning",path,*args);
      self.serv_pid = os.spawnv(os.P_NOWAIT,path,[path]+args);
      self.auto_attach(pid=self.serv_pid);
      self.dprint(1,"spawned external app, pid",self.serv_pid);
      self.dprint(2,"waiting for Hello message from app");
      self._req_state = False;
    else: # no launch spec, simply wait for a connection, and request state when it's there
      self._req_state = True;
      pass;
    self._gui_event_handler = lambda ev,value,server:None;
    
    # start the gui, if so specified
    if gui:
      self.dprint(1,"starting a GUI");
      if not app_defaults.include_gui:
        raise ValueError('gui=True but app_defaults.include_gui=False');
      # gui argument can be a callable object (called to start the gui),
      # or simply True to use a standard GUI.
      if callable(gui):
        self._gui = gui;
      else:
        self._gui = Timba.GUI.app_proxy_gui.app_proxy_gui;
      if threads: 
        self.dprint(1,"threading enabled, posting construct event");
        # threaded model: post a GUI construction event to the main app
        mainapp = Timba.GUI.app_proxy_gui.mainapp();
        mainapp.postCallable(self._construct_gui);
        # after GUI has been constructed, start WP event thread
        mainapp.postCallable(self._pwp.start);
      else:
        # non-threaded: construct GUI here & now
        self.dprint(1,"threading disabled, constructing GUI immediately");
        self._construct_gui(poll_app=50);
    else:     
      self._gui = None;
      # start the wp event thread now
      if threads:
        self._pwp.start();
    # wait for connection?
    if wait_init:
      self.ensure_connection(wait_init);
    
  def __del__ (self):
    self.dprint(1,"destructor");
    self.disconnect();
    
  def disconnect (self):
    if hasattr(self._pwp,'stop'):
      self.dprint(1,"stopping proxy_wp thread");
      self._pwp.stop();
      self.dprint(1,"stopped");
    
  # poll: dispatches all pending events. Only useful in the unthreaded
  # mode (when an event thread is not running)
  def poll (self):
    return self._pwp.poll_pending_events();
    
  # message handler to actually construct an application's GUI
  def _construct_gui (self,poll_app=None):
    try:
      self.dprint(2,"_construct_gui: creating GUI");
      self._gui = self._gui(self,poll_app=poll_app,verbose=self.get_verbose());
      self.dprint(2,"_construct_gui: showing GUI");
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
  server_state_event = hiid("App.State");
  server_attach_event = hiid("Attach.Server");
  server_detach_event = hiid("Detach.Server");
  
  def attach_server (self,addr,auto_attached=False):
    """Attaches to a server specified by address""";
    server = self.servers.get(addr,None);
    if server and server is not self.current_server:
      self.detach_current_server();
      self.current_server = server;
      server.emit(SIGNAL("attached"));
      self.client.emit(SIGNAL("serverAttached"),server,auto_attached);
      self._gui_event_handler(self.server_attach_event,None,server);
      self._auto_attach_pid = self._auto_attach_host = None;
      
  def detach_current_server (self):
    """Detaches from current server""";
    if self.current_server:
      self.current_server.emit(SIGNAL("detached"));
      self.client.emit(SIGNAL("serverDetached"),self.current_server,);
      self._gui_event_handler(self.server_detach_event,None,self.current_server);
      self.current_server = None;
      
  def auto_attach (self,pid=None,host=None):
    self._auto_attach_pid,self._auto_attach_host = pid,host;
    
  def is_auto_attached (self):
    return self._auto_attached;
  
  def _connect_server (self,addr):
    """common procedure used by message handlers to connect a new server""";
    server = Server(addr,state=0,statestr='connected');
    self.servers[addr] = server;
    self.dprint(2, "requesting state and status update");
    self.send_command("Request.State",destination=addr);
    self.client.emit(SIGNAL("serverConnected"),server,);
    self._gui_event_handler(self.hello_event,addr,server);
    self._gui_event_handler(self.server_state_event,record(),server);
    # is an auto-attach request in place?
    if str(self._auto_attach_pid) == str(addr[2]) and str(addr[3]) == str(self.client.addr[3]):
      self.dprint(2, "auto-attaching to this server");
      self.attach_server(addr,auto_attached=True);
      self._auto_attached = True;
    else:
      self._auto_attached = False;
    return server;
    
  def _disconnect_server (self,addr,server):
    """common procedure used by Bye handler and Remote.Down handler
    to disconnect a server""";
    server.state = server.process_state = None;
    server.statestr = '';
    server.emit(SIGNAL("newState"));
    server.emit(SIGNAL("disconnected"));
    self._gui_event_handler(self.bye_event,addr,server);
    self._gui_event_handler(self.server_state_event,record(),server);
    if server is self.current_server:
      self.detach_current_server();
    self.client.emit(SIGNAL("serverDisconnected"),server,);
    del self.servers[addr];
  
  def _hello_handler (self,msg):
    self.dprint(2,"got hello message:",msg);
    addr = getattr(msg,'from');
    if addr not in self.servers:
      server = self._connect_server(addr);
    
  def _bye_handler (self,msg):
    self.dprint(2,"got bye message:",msg);
    addr = getattr(msg,'from');
    server = self.servers.get(addr,None);
    # if in server map, emit signals and throw away
    if server:
      self._disconnect_server(server.addr,server);

  def _process_stat_handler (self,msg):
    self.dprint(5,"got process status: ",msg.msgid);
    fromaddr = getattr(msg,'from');
    for addr,server in self.servers.items():
      if fromaddr[2:3] == addr[2:3]:
        server.process_status = msg.msgid[2:];
        self.dprintf(5,"server %s, process status %s",addr,server.process_status);
        server.emit(SIGNAL("processStatus"),server.process_status,);
        self._gui_event_handler(self.process_status_event,server.process_status,server);
    
  def _remote_down_handler (self,msg):
    self.dprint(2,"got gw.remote.down message:",msg);
    # check if remote gateway belongs to a server that went down, make
    # list of servers to disconnect
    disconnects = [];
    for addr,server in self.servers.items():
      if msg.msgid[3:] == addr[2:]:
        disconnects.append((addr,server));
        self.dprint(2,"matches server",addr,"removing");
    # now disconnect listed servers
    for addr,server in disconnects:
      self._disconnect_server(addr,server);

  def _event_handler (self,msg):
    """event handler for servers""";
    addr = getattr(msg,'from');
    self.dprint(5,"got message: ",msg.msgid,"from",addr);
    # verify source address
    server = self.servers.get(addr,None);
    if server is None:
      self.dprint(2,"hmmm, ",addr,": not in known connected servers, adding connection anyway");
      server = self._connect_server(addr);
    # else update state if not connected
    elif server.state is None:
      server.state = 0;
      server.statestr = 'connected';
      self._gui_event_handler(self.server_state_event,record(),server);
    # extract event name: message ID is <appid>.Out.<event>, so get a slice
    event = msg.msgid[len(self.appid)+1:];
    value = msg.payload;
    if self._checkrefs:
      refcount_report(value,name=str(event));
    self.dprint(5,"which maps to event: ",event);
    # process app updates, messages and error reports
    if isinstance(value,record):
      # process state notifications
      if hasattr(value,'app_state_string'):
        self.dprint(1,'app_state_string',value.app_state_string);
        server.statestr = value.app_state_string;
      if hasattr(value,'app_host'):
        host = str(value.app_host).lower();
        self.dprint(1,'app_host',host);
        server.host = host;
        if host == self.client.host:
          server.remote = None;
        else:
          server.remote = host;
        # check for auto-attach request
        if self._auto_attach_host == host:
          self.attach_server(server.addr);
      if hasattr(value,'session_name'):
        server.session_name = value.session_name;
      if hasattr(value,'cwd'):
        server.cwd = value.cwd;
      if hasattr(value,'app_session_id'):
        sid = str(value.app_session_id).lower();
        self.dprint(1,'app_session_id',sid);
        server.session_id = sid;
      if hasattr(value,'app_state'):
        self.dprint(1,'app_state',value.app_state);
        server.state = str(value.app_state).lower();
        # send message to GUI that server state has changed
        self._gui_event_handler(self.server_state_event,value,server);
      # process messages from current server (if any)
      if server is self.current_server:
        if value.has_field('error'):
          self.log_error(event,value.error);
        for f in ("text","message","error"):
          if value.has_field(f):
            self.dprint(1,'[',f,']',value[f]); 
    # print events if so requested
    if self._verbose_events:
      self.dprint(2,'   event:',event);
      self.dprint(3,'   value:',value);
    # emit signals
    server.emit(SIGNAL("event"),event,value);
    # forward to gui
    self._gui_event_handler(event,value,server);
    
  def ensure_connection (self,wait=True):
    """If no server is connected, waits for the specified number of seconds
    for one to connect. If wait=True, waits forever. If wait=None/False, 
    does not wait at all.""";
    if not wait:
      wait = 0;
    elif isinstance(wait,bool):
      wait = -1;
      self.dprint(0,'blocking until a server is connected');
    try:
      self._pwp.pause_events();
      if wait >= 0:
        endtime = time.time() + wait;
        timeout = min(wait,5);
      else:
        endtime = time.time() + 1e+40;
        timeout = 5;
      while not self.current_server:
        self.dprint(2,'no connection to servers, awaiting (wait=',wait,')');
        res = self._pwp.await_('*',resume=True,timeout=5);  # await anything, but keep looping until status changes
        self.dprint(3,'await_ returns',res);
        if time.time() >= endtime:
          raise RuntimeError("timeout waiting for connection");
    finally:
      self._pwp.resume_events();
    
  def send_command (self,msgid,payload=None,priority=5,destination=None):
    """Sends an app control command to the app""";
    if not destination:
      if not self.current_server:
        raise RuntimeError("no current server set up, cannot send default-destination messages");
      destination = self.current_server.addr;
    msgid = self._snd_prefix + msgid;
    msg = message(msgid,payload=payload,priority=priority);
    # self.relay->[spaste('sending_command_',message)](payload);
    self._pwp.send(msg,destination);
    if self._checkrefs:
      refcount_report(msg,name=str(msgid));
      refcount_report(payload,name=str(msgid)+" payload");
      
  def set_verbose_events (self,verb=True):
    "enables/disables printing of all incoming events";
    self.verbose_events = verb;

  def new_command_index(self):
    "generates new command index";
    ret = self._command_index;
    self._command_index = max(1,self._command_index+1);
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
    
  def await_ (self,what,timeout=None,resume=False):
    "interface to pwp's event loop, in the await_ form";
    if timeout is not None:
      await_timeout = min(1,timeout);
      timeout = time.time() + timeout;
    else:
      await_timeout = 1;
    while True:
      # throw error on disconnect
      if not self.servers:
        raise RuntimeError("lost all connections while waiting for event "+str(what));
      res = self._pwp.await_(self._rcv_prefix + what,timeout=await_timeout,resume=resume);
      # return message if something is received
      if res is not None:
        return res;
      # check for timeout and return None
      if timeout is not None and time.time() >= timeout:
        return None;
      # else go back to top of loop to wait some more
    
  def run_gui (self):
    if not app_defaults.include_gui:
      raise RuntimeError("Can't call run_gui without gui support");
    self._gui.await_gui_exit();
    
