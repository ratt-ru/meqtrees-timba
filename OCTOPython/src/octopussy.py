#!/usr/bin/python

import octopython
from dmitypes import *
import numarray
import string
import sys
import time
import threading

# pulls in various things from the C module directly
from octopython import aid_map,aid_rmap,start_reflector,OctoPythonError

def set_debug (context,level=0):
  if isinstance(context,str):
    octopython.set_debug(context,level);
  elif isinstance(context,dict):
    for c,lev in context.iteritems():
      octopython.set_debug(c,lev);
  else:
    for c in context:
      octopython.set_debug(c,level);
      
_octopussy_init = False;
_octopussy_running = False;      
      
def is_initialized ():
  return _octopussy_init;
def is_running ():
  return _octopussy_running;

def init (gw=False):
  "Inits OCTOPUSSY subsystem. If gw=True (default False), also creates gateways."
  global _octopussy_running,_octopussy_init;
  res = octopython.init(gw);
  _octopussy_init = True;
  return res;
  
def start (wait=True):
  "Starts OCTOPUSSY event thread."
  "If wait=True (default), waits for startup to complete before returning."
  "Returns the thread id of the OCTOPUSSY thread.";
  global _octopussy_running,_octopussy_init;
  if not _octopussy_init:
    raise OctoPythonError,"octopussy not initialized, call init() first"
  res = octopython.start(wait);
  _octopussy_running = True;
  return res;

def stop ():
  "stops OCTOPUSSY thread";
  global _octopussy_running;
  res = octopython.stop();
  _octopussy_running = False;
  return res;
  
#
# proxy_wp
#   This is an interface to a WorkProcess
#
class proxy_wp(octopython.proxy_wp,verbosity):
  "represents an OCTOPUSSY connection endpoint (i.e. WorkProcess)"
  
  class whenever_handler(object):
    """wrapper for a message handler to be registered vith the whenever
    function""";
    def __init__(self,weid,target,pass_msg=False,one_shot=False,args=(),kwargs={}):
      self.weid = weid;
      self.target = target;
      self.args = args;
      self.kwargs = kwargs.copy();
      self.pass_msg = pass_msg;
      self.active = True;
      self.one_shot = one_shot;
    def get_id(self):
      return self.weid;
    def activate(self):
      self.active = True;
    def deactivate(self):
      self.active = False;
    def fire (self,msg):
      if self.active: 
        if self.pass_msg:
          self.kwargs['msg'] = msg;
        self.active = not self.one_shot;
        return self.target(*self.args,**self.kwargs);
      return None;
  
  def __init__(self,wpid=None,verbose=0,vobj_name=None):
    # init base classes
    octopython.proxy_wp.__init__(self,wpid);
    verbosity.__init__(self,verbose);
    self.set_vobj_name(vobj_name or str(self.address()));
    self.dprint(1,"initializing");
    # registered whenevers
    self._we_ids   = {};  # dict of whenevers (for exact matches)
    self._we_masks = {};  # list of whenevers (for mask lookups)

  def send (self,msg,to,payload=None,priority=0):
    "sends message to recepient";
    msg = make_message(msg,payload,priority);
    self.dprintf(3,"sending %s to %s\n",msg.msgid,to);
    return octopython.proxy_wp.send(self,
      make_message(msg,payload,priority),make_hiid(to));
    
  def publish (self,msg,payload=None,priority=0,scope='global'):
    "publishes message";
    msg = make_message(msg,payload,priority);
    self.dprintf(3,"publishing %s scope %s\n",msg.msgid,scope);
    return octopython.proxy_wp.publish(self,
              make_message(msg,payload,priority),make_scope(scope));
    
  def subscribe (self,mask,scope='global'):
    "subscribes WP to message id mask";
    self.dprintf(2,"subscribing to %s scope %s\n",mask,scope);
    return octopython.proxy_wp.subscribe(self,make_hiid(mask),make_scope(scope));
    
  def unsubscribe (self,mask):
    "unsubscribes WP from mask";
    self.dprintf(2,"unsubscribing from %s\n",mask);
    return octopython.proxy_wp.unsubscribe(self,make_hiid(mask));
  
  # this is meant to pause and resume event processing -- no implementation
  # needed since this class is synchronous (i.e., events are not being dealt 
  # with outside await/event_loop calls), but thje threaded proxy class
  # may override this
  def pause_events (self):
    """pauses the event loop for this wp (if any); this will halt the
    processing of any whenevers. Note that a call to await() or event_loop()
    or flush_events() will resume the event loop automatically.
    """;
    pass;
    
  def resume_events (self):
    """resumes the event loop for this wp""";
    pass;
    
  def whenever (self,msgid,target,args=(),kwargs={},subscribe=False,pass_msg=True,one_shot=False):
    """adds an event handler. 'target' (must be a callable object) will be 
    called whenever a message matching 'msgid' (may be a mask with wildcards)
    is received. 'args' and 'kwargs' are passed to the target (the message
    itself is passed kwargs['msg'], unless 'pass_msg' is False). 
    If 'subscribe' is True, calls subscribe() to subscribe the WP to 'msgid'.
    """;
    msgid = make_hiid(msgid);
    is_mask = '?' in str(msgid) or '*' in str(msgid);
    we = self.whenever_handler(msgid,target,pass_msg,one_shot,args,kwargs);
    self.pause_events();
    try:
      if is_mask:
        self.dprint(2,"adding masked whenever:",str(msgid),str(target));
        self._we_masks.setdefault(msgid,[]).append(we);
      else:
        self.dprint(2,"adding matched whenever:",str(msgid),str(target));
        self._we_ids.setdefault(msgid,[]).append(we);
    finally:
      self.resume_events();
    # add subscription if asked to
    if subscribe:
      self.subscribe(msgid);
    return we;
  
  # removes event handler
  def cancel_whenever(self,we):
    msgid = we.get_id();
    self.pause_events();
    try:
      for dicts in (self._we_masks,self._we_ids):
        seq = dicts.get(msgid,[]);
        for i in range(len(seq)):
          if we is seq[i]:
            self.dprint(2,"cancelling whenever:",str(msgid));
            del seq[i];
            return;
    finally:
      self.resume_events();
    self.dprintf(2,"whenever for %s not found",str(msgid));
    
  def _clear_oneshots (welist):
    i = 0;
    while i<len(welist):
      if welist[i].one_shot: del welist[i];
      else:                  i+=1;
    return len(welist);
  _clear_oneshots = staticmethod(_clear_oneshots);
    
  def _dispatch_whenevers (self,msg):
    # got message, process it
    pending_list = [];
    self.pause_events();
    try:
      self.dprint(3,"processing message",msg.msgid);
      # check the matched dictionary
      welist = self._we_ids.get(msg.msgid,[]);
      self.dprintf(3,"found %d matched whenevers for %s\n",len(welist),msg.msgid);
      pending_list += welist;
      # clear one-shots, and remove list if it becomes empty
      if welist and not self._clear_oneshots(welist):
        del self._we_ids[msg.msgid];
      # check the masks list
      for mask,welist in self._we_masks.iteritems():
        if msg.msgid.matches(mask):
          self.dprintf(3,"found %d mask whenevers for %s\n",len(welist),mask);
          pending_list += welist;
          if welist and not self._clear_oneshots(welist):
            del self._we_masks[mask];
    finally:
      self.resume_events();
    self.dprintf(3,"firing %d matched whenevers\n",len(pending_list));
    for we in pending_list:
      we.fire(msg);
    
  # event_loop()
  # Calls receive() in a continuous loop, processes events by invoking
  # their whenever handlers.
  # If await is supplied (is a hiid), returns when a message matching the
  # await mask is received (returns message).
  # If timeout is supplied, returns None after it has expired.
  # Otherwise loop indefinitely, or until the C++ ProxyWP has exited
  def event_loop (self,await=[],timeout=None):
    """runs event loop for this WP -- calls receive() to fetch messages,
    dispatches whenevers, discards messages not matching a whenever. 'await'
    may be set to one or more msgids, in this case the method will  exit when a
    matching message is received. 'timeout' may be used to specify a time
    limit, use None to loop indefinitely (or until the C++ WP has  exited). If
    timeout=0, processes all pending messages and returns. 
    """;
    # convert await argument to list of hiids
    await = make_hiid_list(await);
    self.dprint(1,"running event loop, timeout",timeout,"await",await);
    if timeout is None: 
      endtime = 1e+40; # quite long enough...
    else:
      endtime = time.time() + timeout;
    while self.num_pending() or time.time() <= endtime:
      try:  
        self.dprint(3,"going into receive()");
        if timeout is None:
          to = -1;
        else:
          to = max(0,endtime - time.time());
        msg = self.receive(to);
      except octopython.OctoPythonError,value:
        self.dprint(1,"exiting on receive error:",value);
        return None;
      # msg=None probably indicates timeout, go back up to check
      if msg is None:
        continue;
      # got message, process it
      self._dispatch_whenevers(msg);
      # check for a match in the await-list
      for aw in await:
        if aw.matches(msg.msgid):
          self.dprintf(3,"matches await %s, returning\n",aw);
          return msg;
    # end of while-loop, if we dropped out, it's a timeout, return None
    return None

  def await (self,what,timeout=None,resume=False):
    """alias for event_loop() with an await argument.
    if resume is true, resumes the event loop before commencing await. This
    is meant for child classes only.
    """;
    return self.event_loop(await=what,timeout=timeout);
  
  # flush_events(): dispatches all queued events
  #   this is actually an alias for event_loop with a 0 timeout
  def flush_events (self):
    """alias for event_loop() with timeout=0""";
    return self.event_loop(timeout=0);


#
# proxy_wp_thread
#   Threaded interface to a WorkProcess
#   This has a start() method which will start the event loop in a separate
#   thread. All whenevers are then executed in that thread.
#   The thread_api argument allows another threading layer (i.e. Qt) to
#   be used in place of the standard threading module.
# 
class proxy_wp_thread(proxy_wp):
  "represents an OCTOPUSSY connection endpoint (i.e. WorkProcess)"
  ExitMessage = hiid("e.x.i.t");
  
  def __init__ (self,wpid='python',verbose=0,thread_api=threading):
    self.name = str(wpid)+'-init';  # because parent calls self.object_name()
    proxy_wp.__init__(self,wpid,verbose=verbose);
    self.name = str(self.address());
    # lock for event queue
    self._lock = thread_api.RLock(); 
    self._paused = 0;
    # await-related stuff 
    self._awaiting = {};
    self._await_cond = thread_api.Condition();
    # event thread
    self._api = thread_api;
    self._thread = thread_api.Thread(target=self.run,name=self.name);
#    # klduge for non-Python APIs: use regular receive
#    if self._api is not threading:
#      self.receive_threaded = self.receive;

  def object_name (self):
    if hasattr(self,'_thread'):
      thr = self._api.currentThread();
      if thr is self._thread:
        return self.name + "(EvT)";
      else:
        return self.name + "(" + thr.getName() + ")";
    return self.name;

  def start (self):
    self.dprint(1,"starting WP thread");
    self._thread.start();
    self.dprint(1,"thread started");
    
  def stop (self):
    self.dprint(1,"stopping & joining WP event thread");
    self.send(self.ExitMessage,self.address());
    self._thread.join();
    self.dprint(1,"thread joined");
    
  def lock (self):
    return self._lock;
    
  # this is meant to pause and resume event processing -- no implementation
  # needed since threads don't actually work for now (i.e., events are
  # not being deal with outside await/event_loop calls)
  
  def pause_events (self):
    """pauses the event loop for this wp (if any); this will halt the"
    processing of any whenevers. Note that a call to await() or event_loop()"
    or flush_events() will resume the event loop automatically.
    """;
    self._lock.acquire();
    self._paused += 1;
    self.dprintf(3,"pausing event loop (count %d)\n",self._paused);
    
  # pauses the event loop for this wp (if any); this will halt the processing
  #   of any whenevers
  def resume_events (self):
    """resumes the event loop for this wp""";
    if self._paused > 0:
      self._lock.release();
      self._paused = max(self._paused-1,0);
    self.dprintf(3,"resuming event loop (count %d)\n",self._paused);
    
  # await blocks until the specified message has been received
  # (with optional timeout)
  def await (self,what,timeout=None,resume=False):
    cur_thread = self._api.currentThread();
    if cur_thread is self._thread:
      raise AssertionError,"can't call await() from event handler thread";
    thread_name = cur_thread.getName();
    self.dprint(2,"await: thread",thread_name);
    self.dprint(2,"await: waiting for",what,"timeout ",timeout);
    what = make_hiid_list(what);
    await_pair = [make_hiid_list(what),None];  # result will be returned as second item
    # start by setting a lock on the wait condition
    self._await_cond.acquire();
    self._awaiting[thread_name] = await_pair;
    try:
      if resume:
        self.resume_events();
      self.dprint(3,"calling wait on awaitcond");
      endtime = timeout and time.time() + timeout;
      while await_pair[1] is None:
        if endtime and time.time() >= endtime: # timeout
          return None;
        self._await_cond.wait(timeout);
        self.dprint(2,"await: wait returns ",await_pair[1]);
    finally:
      del self._awaiting[thread_name];
      self._await_cond.release();
    return await_pair[1];

  def event_loop (self,*args,**kwargs):
    raise RuntimeError,"can't call event_loop on " + self.__class__.__name__;
    
  # the run-loop: calls receive() in a continuous loop, processes events
  def run (self):
    running = 1;
    self.dprint(1,"running thread");
    while True:
      try:  
        self.dprint(3,"going into receive()");
        msg = self.receive_threaded();
      except octopython.OctoPythonError, value:
        self.dprint(1,"exiting on receive error:",value);
        break;
      # msg=None probably indicates timeout, go back up to check
      if msg is None:
        continue;
      # check for predefined exit message
      if msg.msgid == self.ExitMessage and msg.is_from(self.address()):
        self.dprint(1,"got exit message",msg);
        break;
      # process messages
      self._dispatch_whenevers(msg);
      # now, check for matching awaits
      self._lock.acquire();
      self._await_cond.acquire();
      try:
        for awp in self._awaiting.itervalues():
          for msgid in awp[0]:
            if msg.msgid.matches(msgid):
              self.dprintf(3,"matches await %s, notifying\n",msgid);
              awp[1] = msg;
              self._await_cond.notifyAll();
              break; # break out to next awaiting pair
      finally:
        self._await_cond.release();
        self._lock.release();
    # end of while-loop (exit is inside) 
    self.dprint(1,"finishing thread");
 
#
# self-test code
#

if __name__ == "__main__":
  import time
  import numarray
  if '-qt' in sys.argv:
    import qt_threading
    thread_api = qt_threading; 
    print "================== Using Qt thread API ===================";
  else:
    thread_api = threading; 
    print "================== Using standard thread API ===================";
    
  # do some basic checking
  print "set_debug()";
  set_debug("Octopussy",1);
  set_debug("OctoPython",1);
  set_debug({"Dsp":1,"loggerwp":0});
  set_debug(("reflectorwp","python"),1);
  print "init()"
  init();
  addr_refl = start_reflector();
  print "Reflector address is:",addr_refl;

  print "=== (1) ===";
  
  wp1 = proxy_wp("Python",verbose=2);
  print "WP1 address is:",wp1.address();
  wp2 = proxy_wp("Python",verbose=2);
  print "WP2 address is:",wp2.address();
  wp3 = proxy_wp("Python",verbose=3);
  print "WP3 address is:",wp2.address();
  wp3.subscribe("1.2.*");
  wp3.subscribe("Reflect.*");
  
  wp4 = proxy_wp_thread("Python",verbose=3,thread_api=thread_api);
  print "WP4 address is:",wp2.address();
  wp4.subscribe("1.2.*");
  wp4.subscribe("Reflect.*");
  
#  wp3.start();
  we3 = wp3.whenever("*",lambda msg,header: sys.stderr.write(header+str(msg)+'\n'),(),{'header':'[3]======'});
  we4 = wp4.whenever("*",lambda msg,header: sys.stderr.write(header+str(msg)+'\n'),(),{'header':'[4]======'});
  
  print "=== (2) ===";
  
  wp1.subscribe("1.2.*","global");
  wp2.subscribe("b.c.*","local");
  wp1.unsubscribe("a");
  
  # start
  print "start()";
  thread = start(wait=True);
  print "OCTOPUSSY thread ID is:",thread;
  
  # start threaded WP
  wp4.start();
  
  print "wp1.receive(), no wait: ",wp1.receive(False);
  print "wp2.receive(), no wait: ",wp2.receive(False);
  msg1 = message('a.b.c');
  print "message1",msg1;
  wp1.send(msg1,wp2.address());
  
  arr = numarray.array([1,2,3,4,5,6],shape=[3,2]);
  subseq = ([1,2,3],['x','y','z'],[hiid('a'),hiid('b')]);
  subrec = srecord({'x':0,'y':arr});
  payload = srecord({'a':0,'b':arr,'c_d':2,'e':subseq,'f':subrec,'z':(hiid('a'),hiid('b')),'nonhiid':4},verbose=2);
  
  msg2 = message('1.2.3',priority=10,payload=payload);
  
  print "message2",msg2;
#  set_debug("OctoPython",5);
  print "=== (2a) ===";
  wp2.publish(msg2);
#  set_debug("OctoPython",2);

  wp4.pause_events();

  msg2.msgid = hiid('Reflect.1');
  print "=== (2b) ===";
  wp2.publish(msg2);
  print "=== (2c) ===";
  wp1.send(msg1,addr_refl);
  print "=== (2d) ===";
#  time.sleep(.5);
  
  print "awaiting on wp4...";
  res = wp4.await("reflect.*",resume=True);
  print "await result: ",res;
  
  print "=== (3) ===";
  
  print 'wp1 queue: ',wp1.num_pending();
  print 'wp2 queue: ',wp2.num_pending();
  
  while wp1.num_pending():
#    set_debug("OctoPython",5);
    msg1a = wp1.receive();
#    set_debug("OctoPython",2);
    print "wp1.receive(): ",msg1a;
    print "payload: ",msg1a.payload;
    
  while wp2.num_pending():
#    set_debug("OctoPython",5);
    msg2a = wp2.receive();
#    set_debug("OctoPython",2);
    print "wp2.receive(): ",msg2a;
    print "payload: ",msg2a.payload;
  
  print "=== (4) ===";
  wp1.send('x.y.z',wp3.address());
    
  print 'wp1 queue: ',wp1.num_pending();
  print 'wp2 queue: ',wp2.num_pending();
  print 'wp3 queue: ',wp3.num_pending();
  print 'going into wp3.event_loop()';
  wp3.event_loop(await='x.*');

  wp3.cancel_whenever(we3);
  wp4.cancel_whenever(we4);
  
  print "=== (5) ===";
  
  time.sleep(.5);
  print "stop()";
  stop();
#  print "wp3.join()";
#  wp3.join();
  
  
