#!/usr/bin/python

import octopython
from dmitypes import *
import numarray
import string
import sys
import threading
import types
import time

# pulls in various things from the C module directly
from octopython import aid_map,aid_rmap,start_reflector

def set_debug (context,level=0):
  if isinstance(context,str):
    octopython.set_debug(context,level);
  elif isinstance(context,dict):
    for c,lev in context.iteritems():
      octopython.set_debug(c,lev);
  else:
    for c in context:
      octopython.set_debug(c,level);
      
_octopussy_running = False;      
      
def is_running ():
  return _octopussy_running;

def start (gw=False,wait=True):
  "Starts OCTOPUSSY thread. If gw=True (default False), also starts gateways"
  "If wait=True (default), waits for startup to complete before returning."
  "Returns the thread id of the OCTOPUSSY thread.";
  global _octopussy_running;
  res = octopython.start(gw,wait);
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
  
  def __init__(self,wpid=None,verbose=0,vobj_name=None):
    octopython.proxy_wp.__init__(self,wpid);
    verbosity.__init__(self,verbose);
    self.set_vobj_name(vobj_name or str(self.address()));
    self.dprint(1,"initializing");
  
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


#
# Wrapper for an object method that is protected by entry/exit locks
# See proxy_wp_thread() below for examples of use
#
class LockProtectedMethod(object):
  def __init__(self,method,lockmethod):
    self.func = method; # ThreadSafeFunctionWrapper(f,lock);
    self.lock = lockmethod;
  def __get__(self,obj,objtype=None):
#    print 'get:',self,obj,objtype;
    def wrapper(*args,**kwargs):
      self.lock(obj).acquire();
      args = (obj,)+args;
      try: return self.func(*args,**kwargs);
      finally: self.lock(obj).release();
    return wrapper;
  def __set__(self,obj,value):
    raise RuntimeError,"can't set method attribute";
  def __delete__(self,obj):
    raise RuntimeError,"can't delete method attribute";

#  class dummylock(object):
#    def acquire(self):
#      print self,'acquire';
#    def release(self):
#      print self,'release';
  
    
#
# proxy_wp_thread
#    
class proxy_wp_thread(proxy_wp,threading.Thread):
  "represents an OCTOPUSSY connection endpoint (i.e. WorkProcess)"
  class whenever_handler(object):
    def __init__(self,weid,target,args=(),kwargs={}):
      self.weid = weid;
      self.target = target;
      self.args = args;
      self.kwargs = kwargs;
      self.active = True;
    def get_id(self):
      return self.weid;
    def activate(self):
      self.active = True;
    def deactivate(self):
      self.active = False;
    def fire (self,msg):
      if self.active: 
        self.kwargs['msg'] = msg;
        self.target(*self.args,**self.kwargs);
        
  def __init__ (self,wpid='python',verbose=0):
    self._lock = threading.RLock(); # verbose=True)
    proxy_wp.__init__(self,wpid,verbose=verbose);
    self.name = 'pwpt:'+str(self.address());
    threading.Thread.__init__(self,name=self.name);
    self.set_vobj_name(self.name);
    self.we_ids   = {};  # dict of whenevers (for exact matches)
    self.we_masks = {};  # list of whenevers (for mask lookups)
    self._awaiting = None;
    self._await_cond = octopython.thread_condition(verbose=True);
    self._await_cond_locks = 0;
    
  def lock (self):
    return self._lock;
    
  # this is meant to pause() event processing -- do nothing since
  # we don't deal in threads for now
  def pause_events (self):
    pass;
    
#  dprint = LockProtectedMethod(proxy_wp.dprint,lock);
#  dprintf = LockProtectedMethod(proxy_wp.dprintf,lock);

  # adds an event handler to the thread tables    
  def whenever (self,msgid,target,args=(),kwargs={},subscribe=False):
    msgid = make_hiid(msgid);
    is_mask = '?' in str(msgid) or '*' in str(msgid);
    we = self.whenever_handler(msgid,target,args,kwargs);
    if is_mask:
      self.dprint(2,"adding masked whenever:",str(msgid),str(target));
      self.we_masks.setdefault(msgid,[]).append(we);
    else:
      self.dprint(2,"adding matched whenever:",str(msgid),str(target));
      self.we_ids.setdefault(msgid,[]).append(we);
    # add subscription if asked to
    if subscribe:
      self.subscribe(msgid);
    return we;
  
  # removes event handler
  def cancel_whenever(self,we):
    msgid = we.get_id();
    for dicts in (self.we_masks,self.we_ids):
      seq = dicts.get(msgid,[]);
      for i in range(len(seq)):
        if we is seq[i]:
          self.dprint(2,"cancelling whenever:",str(msgid));
          del seq[i];
          return;
    self.dprintf(2,"whenever for %s not found",str(msgid));
    
  whenever = LockProtectedMethod(whenever,lock);

  # event_loop()
  # Calls receive() in a continuous loop, processes events by invoking
  # their whenever handlers.
  # If await is supplied (is a hiid), returns when a message matching the
  # await mask is received (returns message).
  # If timeout is supplied, returns None after it has expired.
  # Otherwise loop indefinitely, or until the C++ ProxyWP has exited
  def event_loop (self,await=None,timeout=None):
    # make sure await is a hiid
    if await and not isinstance(await,hiid):
      await = hiid(await);
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
      pending_list = [];
      self._lock.acquire();
      try:
        self.dprint(3,"processing message",msg.msgid);
        # check for current await
        # check the matched dictionary
        welist = self.we_ids.get(msg.msgid,[]);
        self.dprintf(3,"found %d matched whenevers for %s\n",len(welist),msg.msgid);
        pending_list += welist;
        # check the masks list
        for mask,welist in self.we_masks.iteritems():
          if msg.msgid.matches(mask):
            self.dprintf(3,"found %d mask whenevers for %s\n",len(welist),mask);
            pending_list += welist;
      finally:
        self._lock.release();
      self.dprintf(3,"firing %d matched whenevers\n",len(pending_list));
      for we in pending_list:
        we.fire(msg);
      # check for await match
      if await and await.matches(msg.msgid):
        self.dprint(3,"matches await, returning");
        return msg;
    # end of while-loop, if we dropped out, it's a timeout, return None
    return None
  
  # flush_events(): dispatches all queued events
  #   this is actually an alias for event_loop with a 0 timeout
  def flush_events(self):
    return self.event_loop(timeout=0);

##   # pause suspends the event loop by acquiring lock
##   def await_lock (self):
##     self._await_cond.lock();
##     self._await_cond_locks += 1;
##     self.dprint(2,"await_lock: thread",threading.currentThread().getName());
##     
##   def await_unlock (self):
##     self.dprint(2,"await_unlock: thread",threading.currentThread().getName());
##     self._await_cond.unlock();
##     
##   # await blocks until the specified message has been received
##   # (with optional timeout)
##   def await (self,msgid,timeout=None):
##     self.dprint(2,"await: thread",threading.currentThread().getName());
##     self.dprintf(2,"await: waiting for %s, timeout %s\n",msgid,timeout);
##     # start by setting a lock on the wait condition
##     self._await_cond.lock();
##     self._await_cond_locks += 1;
##     try:
##       self._awaiting = hiid(msgid);
##       self._await_result = None;
##       self.dprint(3,"calling wait on awaitcond");
##       endtime = timeout and time.time() + timeout;
##       while self._await_result is None:
##         if endtime and time.time() >= endtime: # timeout
##           return None;
##         self._await_cond.wait(.1);
##         self.dprint(2,"await: wait returns ",self._await_result);
##     finally:
##       self._awaiting = None;
##       n = self._await_cond_locks;
##       self._await_cond_locks = 0;  
##       for i in range(n):
##         self._await_cond.unlock();
##     return self._await_result;
##   #  await = LockProtectedMethod(await,lock);
## 
##   # the run-loop: calls receive() in a continuous loop, processes events
##   def run (self):
##     running = 1;
##     self.dprint(1,"running thread");
##     while True:
##       try:  
##         self.dprint(3,"going into receive()");
##         msg = self.receive();
##       except octopython.OctoPythonError, value:
##         self.dprint(1,"exiting on receive error:",value);
##         return;
##       # got message, process it
##       pending_list = [];
##       self._lock.acquire();
##       try:
##         self.dprint(3,"processing message",msg.msgid);
##         # check for current await
##         self._await_cond.lock();
##         try:
##           if self._awaiting and msg.msgid.matches(self._awaiting):
##             self.dprint(3,"matches current await, notifying");
##             self._await_result = msg;
##             self._await_cond.notify();
##         finally:
##           self._await_cond.unlock();
##         # check the matched dictionary
##         we = self.we_ids.get(msg.msgid,None);
##         if we != None:
##           self.dprint(3,"found matched whenever",msg.msgid);
##           pending_list.append(we);
##         # check the maks list
##         for wem in self.we_masks:
##           if msg.msgid.matches(wem[0]):
##             self.dprint(3,"found mask whenever",wem[0]);
##             pending_list.append(wem[1]);
##       finally:
##         self.dprintf(3,"firing %d matched whenevers\n",len(pending_list));
##         self._lock.release();
##       for we in pending_list:
##         we.fire(msg);
##     # end of while-loop (exit is inside) 
 
# self-test code 
if __name__ == "__main__":
  import time
  # do some basic checking
  print "set_debug()";
  set_debug("Octopussy",1);
  set_debug("OctoPython",1);
  set_debug({"Dsp":1,"loggerwp":0});
  set_debug(("reflectorwp","python"),1);
  # start/stop thread
  print "start()";
  thread = start();
  print "Thread ID is:",thread;
  addr_refl = start_reflector();
  print "Reflector address is:",addr_refl;

  print "=== (1) ===";
  
  wp1 = proxy_wp("Python",verbose=2);
  print "WP1 address is:",wp1.address();
  wp2 = proxy_wp("Python",verbose=2);
  print "WP2 address is:",wp2.address();
  wp3 = proxy_wp_thread("Python",verbose=3);
  print "WP3 address is:",wp2.address();
  wp3.subscribe("1.2.*");
  wp3.subscribe("Reflect.*");
#  wp3.start();
  we = wp3.whenever("*",lambda msg,header: sys.stderr.write(header+str(msg)+'\n'),(),{'header':'======'});
  
  print "=== (2) ===";
  
  wp1.subscribe("1.2.*","global");
  wp2.subscribe("b.c.*","local");
  wp1.unsubscribe("a");
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

  msg2.msgid = hiid('Reflect.1');
  print "=== (2b) ===";
  wp2.publish(msg2);
  print "=== (2c) ===";
  wp1.send(msg1,addr_refl);
  print "=== (2d) ===";
  time.sleep(.5);
  
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

  wp3.cancel_whenever(we);
  print "=== (5) ===";
  
  time.sleep(.5);
  print "stop()";
  stop();
#  print "wp3.join()";
#  wp3.join();
  
  
