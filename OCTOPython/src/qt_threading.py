#!/usr/bin/env python3

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

from PyQt4 import Qt
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
  return _active_threads.get(Qt.QThread.currentThread(),_main_thread);

def trace_lines (frame, event, arg):
  if event == "line":
    print(("%s %s:%d"%(id(Qt.QThread.currentThread()),frame.f_code.co_filename,frame.f_lineno)));
  return trace_lines;


class Thread (Qt.QThread):
  def __init__(self,target=None,name=None):
    Qt.QThread.__init__(self);
    self._name = name;
    if not callable(target):
      raise TypeError("Thread target argument must be a callable object");
    self._target = target;
  def run (self):
#    sys.settrace(trace_lines);
    handle = Qt.QThread.currentThread();
    _active_threads[handle] = self;
    if self._name is None:
      self._name = str(handle);
    self._target();
    del _active_threads[handle];
  def getName (self):
    return self._name;
  def setName (self,name):
    self._name = name;
  def join (self):
    return self.wait();
  currentThread = staticmethod(currentThread);

from traceback import print_stack
    
class Lock (object):
  """emulates threading.Lock, by using a QMutex""";
  def __init__(self):
    self._lock = Qt.QMutex(Qt.QMutex.NonRecursive);
    self._locker = None;
  def acquire (self):
##    print id(self),'acquiring in',Qt.QThread.currentThread(),'; locked is ',self._lock.locked();
##    print_stack();
    self._lock.lock();
##    if self._locker is not None:
##      raise RuntimeError,"acquired lock held by %s from %s" % (str(self._locker),str(Qt.QThread.currentThread()));
    self._locker = Qt.QThread.currentThread();
##    print id(self),'acquired in',Qt.QThread.currentThread(),'; locked is ',self._lock.locked();
  def release (self):
##    print id(self),'releasing in',Qt.QThread.currentThread();
##    thr = Qt.QThread.currentThread();
##    if self._locker != thr:
##      raise RuntimeError,"attempt to release lock held by %s from %s" % (str(self._locker),str(thr));
    self._locker = None;
    self._lock.unlock();

class RLock (Lock):
  """emulates threading.RLock, by using a recursive QMutex""";
  def __init__(self):
    self._lock = Qt.QMutex(Qt.QMutex.Recursive);
    self._locker = None;
  
class Condition (Lock):
  """emulates a regular thread.Condition, by using a QMutex and a QCondition""";
  def __init__(self):
    Lock.__init__(self);
    self._cond = Qt.QWaitCondition();
  def wait (self,timeout=None):
    if timeout is None:
      timeout = sys.maxsize;
    else:
      timeout = int(timeout*1000);
##    print id(self),'waiting in ',Qt.QThread.currentThread();
    self._cond.wait(self._lock,timeout);
##    print id(self),'wait over, lock is ',self._lock.locked();
  def notify (self):
##    print id(self),'notify in ',Qt.QThread.currentThread();
    self._cond.wakeOne();
  def notifyAll (self):
##    print id(self),'notifyAll in ',Qt.QThread.currentThread();
    self._cond.wakeAll();

class QThreadWrapper (Qt.QThread):
  def __init__(self,target,name=None,args=(),kwargs={}):
    if not callable(target):
      raise TypeError("target argument must be a callable object");
    Qt.QThread.__init__(self);
    self._target = target;
    self._args = args;
    self._kwargs = kwargs;
    if name is None:
      self._name = str(target);
    else:
      self._name = name;
  def run (self):
    print(("********** QThreadWrapper: running ",self._name));
    self._target(*self._args,**self._kwargs);
  def join (self):
    return self.wait();
