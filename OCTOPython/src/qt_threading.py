#!/usr/bin/python

import qt
import sys

# dummy thread object represents main thread, plus all non-qt threads
class _DummyThread (object):
  def __init__(self,name):
    self.name = name;
  def getName (self):
    return self.name;

# map of running threads
_main_thread = _DummyThread("main");
_active_threads = {};

def currentThread ():
  return _active_threads.get(qt.QThread.currentThread(),_main_thread);

class Thread (qt.QThread):
  def __init__(self,target=None,name=None):
    qt.QThread.__init__(self);
    self._name = name;
    if not callable(target):
      raise TypeError,"Thread target argument must be a callable object";
    self._target = target;
  def run (self):
    handle = qt.QThread.currentThread();
    _active_threads[handle] = self;
    if self._name is None:
      self._name = str(handle);
    self._target();
    del _active_threads[handle];
  def getName (self):
    return self._name;
  def setName (self,name):
    self._name = name;
  currentThread = staticmethod(currentThread);

from traceback import print_stack
    
class Lock (object):
  """emulates threading.Lock, by using a QMutex""";
  def __init__(self):
    self._lock = qt.QMutex(False);
    self._locker = None;
  def acquire (self):
##    print id(self),'acquiring in',qt.QThread.currentThread(),'; locked is ',self._lock.locked();
##    print_stack();
    self._lock.lock();
##    if self._locker is not None:
##      raise RuntimeError,"acquired lock held by %s from %s" % (str(self._locker),str(qt.QThread.currentThread()));
    self._locker = qt.QThread.currentThread();
##    print id(self),'acquired in',qt.QThread.currentThread(),'; locked is ',self._lock.locked();
  def release (self):
##    print id(self),'releasing in',qt.QThread.currentThread();
##    thr = qt.QThread.currentThread();
##    if self._locker != thr:
##      raise RuntimeError,"attempt to release lock held by %s from %s" % (str(self._locker),str(thr));
    self._locker = None;
    self._lock.unlock();

class RLock (Lock):
  """emulates threading.RLock, by using a recursive QMutex""";
  def __init__(self):
    self._lock = qt.QMutex(True);
    self._locker = None;
  
class Condition (Lock):
  """emulates a regular thread.Condition, by using a QMutex and a QCondition""";
  def __init__(self):
    Lock.__init__(self);
    self._cond = qt.QWaitCondition();
  def wait (self,timeout=None):
    if timeout is None:
      timeout = sys.maxint;
    else:
      timeout = int(timeout*1000);
##    print id(self),'waiting in ',qt.QThread.currentThread();
    self._cond.wait(self._lock,timeout);
##    print id(self),'wait over, lock is ',self._lock.locked();
  def notify (self):
##    print id(self),'notify in ',qt.QThread.currentThread();
    self._cond.wakeOne();
  def notifyAll (self):
##    print id(self),'notifyAll in ',qt.QThread.currentThread();
    self._cond.wakeAll();

class QThreadWrapper (qt.QThread):
  def __init__(self,target,name=None,args=(),kwargs={}):
    if not callable(target):
      raise TypeError,"target argument must be a callable object";
    qt.QThread.__init__(self);
    self._target = target;
    self._args = args;
    self._kwargs = kwargs;
    if name is None:
      self._name = str(target);
    else:
      self._name = name;
  def run (self):
    print "********** QThreadWrapper: running ",self._name;
    self._target(*self._args,**self._kwargs);
  def join (self):
    return self.wait();
