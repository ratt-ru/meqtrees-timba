#!/usr/bin/python

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
  import Timba.qt_threading;

from Timba.dmi import *
from Timba import octopussy
# from Timba import py_app_launcher

import threading
import sys
import os
import os.path
import string
import time

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
  
  def __init__(self,appid,client_id,
               launch=None,      # launch app in separate thread (disabled for now)
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
    self.state = None; # None means offline -- we'll get a Hello message for online
    self.statestr = 'no connection';
    self.app_addr = None;
    self.client_addr = self._pwp.address();
    self.paused = False;
    # ------------------------------ export some proxy_wp and octopussy methods
    self.pause_events = self._pwp.pause_events;
    self.resume_events = self._pwp.resume_events;
      
    # ------------------------------ run/connect to app process
    if spawn: 
      if launch:
        raise ValueError('specify either launch or spawn, not both');
      if isinstance(spawn,str):
        spawn = spawn.split(" ");
      # first argument is app binary
      path = spawn[0];
      args = list(spawn[1:]);
      # extra arguments (after "--" in command line)
      args += list(app_defaults.args.extra);
      if path[0] != '/': # not absolute path, so need to search $PATH
        for dirname in os.environ['PATH'].split(':'):
          filename = os.path.join(dirname,path);
          if os.path.isfile(filename) and os.access(filename,os.X_OK):
            path = filename;
            break;
      if not os.path.isfile(path) or not os.access(path,os.X_OK):
        raise RuntimeError("can't spawn %s: not an executable file" % (path,));
      self.dprint(1,"spawning",path,args);
      self.serv_pid = os.spawnv(os.P_NOWAIT,path,[path]+args);
      self.dprint(1,"spawned external server, pid",self.serv_pid);
      self.dprint(2,"waiting for Hello message from app");
      self._req_state = False;
    elif launch: # use py_app_launcher to run a local app thread
      raise RuntimeError("launch option temporarily disabled");
##       self.dprint(1,"launching",launch);
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
  
  def _hello_handler (self,msg):
    self.dprint(2,"got hello message:",msg);
    self.app_addr = getattr(msg,'from');
    if self.state is None:
      self.state = 0;
      self.statestr = 'connected';
    # request state & status 
    if self._req_state:
      self.dprint(2,"requesting state and status update");
      self.send_command("Request.State");
    self._gui_event_handler(self.hello_event,getattr(msg,'from'));
      
  def _bye_handler (self,msg):
    self.dprint(2,"got bye message:",msg);
    self.app_addr = None;
    self.state = None;
    self.statestr = 'no connection';
    self._gui_event_handler(self.bye_event,getattr(msg,'from'));

  def _process_stat_handler (self,msg):
    self.dprint(5,"got process status: ",msg.msgid);
    if self.app_addr is None:
      self.dprint(5,"no app address set, ignoring");
      return;
    fromaddr = getattr(msg,'from');
    if fromaddr[2:3] == self.app_addr[2:3]:
      self.app_process_status = msg.msgid[2:];
      self.dprint(5,"process status set");
      self._gui_event_handler(self.process_status_event,self.app_process_status);
    else:
      self.dprint(5,"process status source does not match app address, ignoring");
    
  def _remote_down_handler (self,msg):
    self.dprint(2,"got gw.remote.down message:",msg);
    if self.app_addr:
      if msg.msgid[3:] == self.app_addr[2:]:
        self.dprint(2,"matches ourselves, generating synthetic bye");
        self._bye_handler(msg);
      else:
        self.dprint(2,"does not match ourselves, ignoring");
    else:
      self.dprint(2,"no app address set, ignoring");

  def _event_handler (self,msg):
    "event handler for app";
    self.dprint(5,"got message: ",msg.msgid);
    # verify source address
    addr = getattr(msg,'from');
    if self.app_addr is None:
      self.dprint(2,"hmmm, no app address set, let's assume this is it",addr);
      self.app_addr = addr;
    else:
      if self.app_addr != addr:
        self.dprint(2,"ignoring message from",addr,": doesn't match app address",self.app_addr);
        return;
    # update state if not connected
    if self.state is None:
      self.state = 0;
      self.statestr = 'connected';
    # extract event name: message ID is <appid>.Out.<event>, so get a slice
    event = msg.msgid[len(self.appid)+1:];
    value = msg.payload;
    if self._checkrefs:
      refcount_report(value,name=str(event));
    self.dprint(5,"which maps to event: ",event);
    # process app updates, messages and error reports
    if isinstance(value,record):
      # process state notifications
      if hasattr(value,'app_state'):
        self.dprint(1,'app_state',value.app_state);
        self.state = str(value.app_state).lower();
      if hasattr(value,'app_state_string'):
        self.dprint(1,'app_state_string',value.app_state_string);
        self.statestr = value.app_state_string;
      # process messages
      if value.has_field('error'):
        self.log_error(event,value.error);
      for f in ("text","message","error"):
        if value.has_field(f):
          self.dprint(1,'[',f,']',value[f]); 
    # print events if so requested
    if self._verbose_events:
      self.dprint(2,'   event:',event);
      self.dprint(3,'   value:',value);
    # forward to gui
    self._gui_event_handler(event,value);
    
  def ensure_connection (self,wait=True):
    """If app is not connected, waits for the specified number of seconds
    for it to connect. If wait=True, waits forever. If wait=None/False, 
    does not wait at all.""";
    if not wait:
      wait = 0;
    elif isinstance(wait,bool):
      wait = -1;
      self.dprint(0,'blocking until server is connected');
    try:
      self._pwp.pause_events();
      if wait >= 0:
        endtime = time.time() + wait;
        timeout = min(wait,5);
      else:
        endtime = time.time() + 1e+40;
        timeout = 5;
      while self.state is None:
        self.dprint(2,'no connection to app, awaiting (wait=',wait,')');
        res = self._pwp.await_('*',resume=True,timeout=5);  # await anything, but keep looping until status changes
        self.dprint(3,'await returns',res);

        if time.time() >= endtime:
          raise RuntimeError("timeout waiting for connection");
    finally:
      self._pwp.resume_events();
    
  def send_command (self,msgid,payload=None,priority=5):
    "Sends an app control command to the app";
    msgid = self._snd_prefix + msgid;
    msg = message(msgid,payload=payload,priority=priority);
    # self.relay->[spaste('sending_command_',message)](payload);
    self._pwp.publish(msg);
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
    
  def await_(self,what,timeout=None,resume=False):
    "interface to pwp's event loop, in the await form";
    if timeout is not None:
      await_timeout = min(1,timeout);
      timeout = time.time() + timeout;
    else:
      await_timeout = 1;
    while True:
      # throw error on disconnect
      if self.app_addr is None:
        raise RuntimeError("lost connection while waiting for event "+str(what));
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
    
