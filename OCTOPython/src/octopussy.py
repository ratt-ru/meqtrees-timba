#!/usr/bin/python

import octopython_c
import string
from dmitypes import *
import numarray

# pulls in various things from the C module directly
from octopython_c import set_debug,aid_map,aid_rmap,start_reflector

def start (gw=False,wait=True):
  "Starts OCTOPUSSY thread. If gw=True (default False), also starts gateways"
  "If wait=True (default), waits for startup to complete before returning."
  "Returns the thread id of the OCTOPUSSY thread.";
  return octopython_c.start(gw,wait);

def stop ():
  "stops OCTOPUSSY thread";
  return octopython_c.stop();

class proxy_wp(octopython_c.proxy_wp):
  "represents an OCTOPUSSY connection endpoint (i.e. WorkProcess)"
  
  def send (self,msg,to,payload=None,priority=0):
    "sends message to recepient";
    return octopython_c.proxy_wp.send(self,
      make_message(msg,payload,priority),make_hiid(to));
    
  def publish (self,msg,payload=None,priority=0,scope='global'):
    "publishes message";
    return octopython_c.proxy_wp.publish(self,
              make_message(msg,payload,priority),make_scope(scope));
    
  def subscribe (self,mask,scope='global'):
    "subscribes WP to message id mask";
    return octopython_c.proxy_wp.subscribe(self,make_hiid(mask),make_scope(scope));
    
  def unsubscribe (self,mask):
    "unsubscribes WP from mask";
    return octopython_c.proxy_wp.unsubscribe(self,make_hiid(mask));
  
# print 'testattr:',octopython_c.proxy_wp.testattr;
 
# self-test code 
if __name__ == "__main__":
  import time
  # do some basic checking
  print "set_debug()";
  set_debug("Octopussy",1);
  set_debug("OctoPython",2);
  set_debug("Dsp",1);
  set_debug("loggerwp",0);
  set_debug("reflectorwp",2);
  set_debug("python",2);
  # start/stop thread
  print "start()";
  thread = start();
  print "Thread ID is:",thread;
  addr_refl = start_reflector();
  print "Reflector address is:",addr_refl;
  
  wp1 = proxy_wp("Python");
  print "WP address is:",wp1.address();
  wp2 = proxy_wp("Python");
  print "WP address is:",wp2.address();
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
  wp2.publish(msg2);
#  set_debug("OctoPython",2);

  msg2.msgid = hiid('Reflect.1');
  wp2.publish(msg2);
  wp1.send(msg1,addr_refl);
  time.sleep(1);
  
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
    
  print 'wp1 queue: ',wp1.num_pending();
  print 'wp2 queue: ',wp2.num_pending();
  time.sleep(1);
  print "stop()";
  stop();
  
  
