#!/usr/bin/python

import re
import weakref
import sys
import string
import types
import traceback

def type_maker(objtype,**kwargs):
  def maker(x):
    if isinstance(x,objtype):
      return x;
    return objtype(x);
  return maker;
  
# 
# === class verbosity ===
# Verbosity includes methods for verbosity levels and conditional printing
#
class verbosity:
  _verbosities = {};
  def __init__(self,verbose=0,stream=sys.stderr,name=None,tb=2):
    if not __debug__:
      verbose=0;
    (self.verbose,self.stream,self._tb) = (verbose,stream,tb);
    # setup name
    if name:
      self.verbosity_name = name;
    else:
      if self.__class__ is verbosity:
        raise RuntimeError,"""When creating a verbosity object directly,
          a name must be specified.""";
      self.verbosity_name = name = self.__class__.__name__;
    # look for argv to override debug levels
    # NB: sys.argv doesn't always exist -- e.g., when embedding Python
    # it doesn't seem to be present.  Hence the check.
    argv = getattr(sys,'argv',None);
    if argv:
      patt = re.compile('-d'+name+'=(.*)$');
      for arg in argv[1:]:
        try: 
          self.verbose = int(patt.match(arg).group(1));
        except: pass;
    # add name to map
    self._verbosities[name] = self;
    print "Registered verbose context:",name,"=",self.verbose;
  def __del__ (self):
    del self._verbosities[self.verbosity_name];
  def dheader (self,tblevel=-2):
    if self._tb:
      tb = traceback.extract_stack();
      (filename,line,funcname,text) = tb[tblevel];
      filename = filename.split('/')[-1];
      if self._tb > 1:
        return "%s(%s:%d:%s): "%(self.get_verbosity_name(),filename,line,funcname);
      else:
        return "%s(%s): "%(self.get_verbosity_name(),funcname);
    else:
      return self.get_verbosity_name()+': ';
  def dprint(self,level,*args):
    if level <= self.verbose:
      self.stream.write(self.dheader(-3));
      self.stream.write(string.join(map(str,args),' ')+'\n'); 
  def dprintf(self,level,format,*args):
#    print format,args;
    if level <= self.verbose:
      try: s = format % args;
      except: 
        self.stream.write('dprintf format exception: ' + str(format) + '\n');
      else:
        self.stream.write(self.dheader(-3));
        self.stream.write(s);
  def get_verbose(self):
    return self.verbose;
  def set_verbose(self,verbose):
    self.verbose = verbose;
  def set_stream(self,stream):
    self.stream = stream;
  def set_verbosity_name(self,name):
    self.verbosity_name = name;
  def get_verbosity_name (self):
    return self.verbosity_name;
    

def _print_curry_exception ():
  (et,ev,etb) = sys.exc_info();
  print "%s: %s" % (getattr(ev,'_classname',ev.__class__.__name__),getattr(ev,'__doc__',''));
  if hasattr(ev,'args'):
    print "  ",' '.join(ev.args);
  print '======== exception traceback follows:';
  traceback.print_tb(etb);
  
# curry() composes callbacks and such
# See The Python Cookbook recipe 15.7
def curry (func,*args,**kwds):
  def callit(*args1,**kwds1):
    kw = kwds.copy();
    kw.update(kwds1);
    a = args+args1;
    try:
      return func(*a,**kw);
    except:
      print "======== curry: exception while calling a curried function";
      print "  function:",func;
      print "  args:",a;
      print "  kwargs:",kw;
      _print_curry_exception();
      raise;
  return callit;
  
# Extended curry() version
# The _argslice argument is applied to the *args of the
# curry when it is subsequently called; this allows only a subset of the
# *args to be passed to the curried function.
def xcurry (func,_args=(),_argslice=slice(0),_kwds={},**kwds):
  kwds0 = _kwds.copy();
  kwds0.update(kwds);
  if not isinstance(_args,tuple):
    _args = (_args,);
  def callit(*args1,**kwds1):
    a = _args+args1[_argslice];
    kw = kwds0.copy();
    kw.update(kwds1);
    try: return func(*a,**kw);
    except:
      print "======== xcurry: exception while calling a curried function";
      print "  function:",func;
      print "  args:",a;
      print "  kwargs:",kw;
      _print_curry_exception();
      raise;
  return callit;
  
class PersistentCurrier (object):
  """This class provides curry() and xcurry() instance methods that 
  internally store the curries in a list. This is handy for currying
  callbacks to be passed to, e.g., PyQt slots: since PyQt holds the callbacks 
  via weakrefs, using the normal curry() method to compose a callback 
  on-the-fly would cause it to disappear immediately.
  """
  def _add_curry (self,cr):
    try: self._curries.append(cr);
    except AttributeError: self._curries = [cr];
    return cr;
  def curry (self,func,*args,**kwds):
    return self._add_curry(curry(func,*args,**kwds));
  def xcurry (self,func,*args,**kwds):
    return self._add_curry(xcurry(func,*args,**kwds));
  def clear (self):
    self._curries = [];
  

class WeakInstanceMethod (object):
  # return value indicating call of a weakinstancemethod whose object
  # has gone
  DeadRef = object();
  def __init__ (self,method):
    if type(method) != types.MethodType:
      raise TypeError,"weakinstancemethod must be constructed from an instancemethod";
    (self.im_func,self.im_self) = (method.im_func,weakref.ref(method.im_self));
  def __nonzero__ (self):
    return self.im_self() is not None;
  def __call__ (self,*args,**kwargs):
    obj = self.im_self();
    if obj is None:
      return self.DeadRef;
    return self.im_func(obj,*args,**kwargs);

def weakref_proxy (obj):
  """returns either a weakref.proxy for the object, or if object is already a proxy,
  returns itself.""";
  if type(obj) in weakref.ProxyTypes:
    return obj;
  else:
    return weakref.proxy(obj);


  
