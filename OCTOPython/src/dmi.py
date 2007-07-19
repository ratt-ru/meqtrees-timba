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

import sys

# this ensures that C++ symbols (RTTI, DMI registries, etc.) are
# shared across dynamically-loaded modules
import DLFCN
sys.setdlopenflags(DLFCN.RTLD_NOW | DLFCN.RTLD_GLOBAL);

import string
import numarray
import types
import weakref
import re
import new
from numarray import array

import Timba
from Timba.utils import *

# 
# === class hiid ===
#
class hiid (tuple):
  "Represents the DMI HIID class";
  def __new__ (self,*args,**kw):
    sep = kw.get('sep','._');           # use '.' separator by default
    mylist = ();
    for x in args:
      if isinstance(x,str):            # a string? Use HIID mapping functions
        try:
          mylist = mylist + Timba.octopython.str_to_hiid(x,sep);
        except:
          # normally, this would never fail, but if it ever does, here's a fallback
          mylist = mylist + (x,);
      elif isinstance(x,(tuple,list)): # other sequence? use as list
        mylist = mylist + tuple(x);
      elif isinstance(x,(int,long)):   # int/long? add to list
        mylist = mylist + (x,);
      else:
        raise ValueError, "can't construct hiid from a %s"%type(x);
    return tuple.__new__(self,mylist);
  # get(n) returns element N as integer
  def get (self,n):
    return tuple.__getitem__(self,n);
  # redefine __getitem__: if key is a slice, then the subsequence should be
  # converted to hiid
  def __getitem__ (self,key):
    return hiid(tuple.__getitem__(self,key));
  def __getslice__ (self,i,j):
    # print 'getslice: ',i,j;
    return hiid(tuple.__getslice__(self,i,j));
  def __str__ (self):
    try:
      return Timba.octopython.hiid_to_str(self);
    except:
      return '.'.join(map(str,self));
  def __repr__ (self):
    return "hiid('%s')" % str(self);
  # matches() function matches hiids
  def matches (self,other):
    return Timba.octopython.hiid_matches(self,make_hiid(other));
  def startswith (self,other):
    other = make_hiid(other);
    return self[:len(other)] == other;
  # concatenation with '+' must return a hiid
  def __add__ (self,other):
    return hiid(self,other);
  def __radd__ (self,other):
    return hiid(other,self);
  # comparison with strings -- convert to hiid
  def __cmp__ (self,other):
    return cmp(str(self).lower(),str(other).lower());
  # as_str converts to string
  def as_str (self,sep='.'):
    return Timba.octopython.hiid_to_str(self,sep);
  # as_int converts to int
  def as_int (self):
    if len(self) > 1:
      raise TypeError,"can't convert multiple-element hiid to int";
    return int(tuple.__getitem__(self,0));
  __int__ = as_int;

# make_hiid()
#   ensures argument is a hiid
#    
def make_hiid (x,sep='.'):
  "converts argument to hiid, if it is not a hiid already";
  if isinstance(x,hiid):
    return x;
  return hiid(x,sep=sep);

# make_hiid_list()
#   converts argument to list of HIIDs: argument can be a single hiid, a single
#   string, or a sequence of such
def make_hiid_list (x):
  if isinstance(x,hiid):       # single hiid - to list
    return [x];
  elif isinstance(x,str):  # single string - to list
    return [hiid(x)];
  else: # treat everything else as a sequence of hiids or strings
    return map(make_hiid,x); 
  
#
# === dmize_object() ===
# Converts obj to DMI-compatible representation, or raises TypeError if this
# is impossible.
# Current valid types are:
# (*) see _dmi_supported_types tuple defined below
# (*) lists or tuples of supported object types
def dmize_object (obj):
  "coerces object into a DMI-supported type as needed. Returns the "
  "object on success, or raises a TypeError on failure";
  if obj is None:
    return obj;
  # check if sequence of supported types
  if isinstance(obj,(list,tuple)):
    seqtype = type(obj);
    if not len(obj):    # empty sequences always allowed
      return obj;   
    outlist = [ dmize_object(item) for item in obj ]; 
    # convert resulting list back into original sequence type
    return seqtype(outlist);
  # else expect object of supported type, returned as-is
  for tp in _dmi_typename_map.keys():
    if isinstance(obj,tp):
      return obj;
  raise TypeError,'dmi: type %s not supported'%type(obj);


# === class conv_error ===
# This class represents a conversion error.
# When converting from DMI structures to Python, any errors are represented
# by instances of this class.
# When converting the other way, these objects are ignored.
class conv_error(TypeError):
  def __init__(self,message,exc=None):
    self.message = message;
    self.exc     = exc;
  def __repr__(self):
    return '<dmitypes.conv_eror>';
  def __str__(self):
    return '<conv_error>';
  def details(self):
    s = '<conv_error: ' + str(self.message);
    if( self.exc ): s += ','+str(self.exc);
    return s+'>';
  def __eq__ (self,other):
    return True;
  def __ne__ (self,other):
    return False;


class recdict (dict):
  """A recdict is basically a dict whose contents may also be
  accessed via attributes, using the rec.field notation.
  """;
  def __getattr__(self,name):
    if name.startswith('__'):
      return dict.__getattr__(self,name);
    # else try to access attribute anyway, to see if we have one
    try: return dict.__getattr__(self,name);
    except AttributeError: pass;
    return dict.__getitem__(self,name);
  # __setattr__: sets entry in dict
  def __setattr__(self,name,value):
    if name.startswith('__'):
      return dict.__setattr__(self,name,value);
    return dict.__setitem__(self,name,value);
  # __delattr__: deletes key
  def __delattr__(self,name):
    if name.startswith('__'):
      return dict.__delattr__(self,name,value);
    return dict.__delitem__(self,key);


class record (dict):
  """A record is a restricted dict that only allows specific kinds of keys
  (in this case strings, but this may be redefined in subclasses).
  Records also provide access to their elements via attributes, using the 
  conventional rec.field notation.
  Field values are limited to dmizable objects.
  """
  def __init__ (self,_initdict_=[],_verbose_=0,**kwargs):
    # initialize from init dictionary and from kwargs, checking for valid keys
    if isinstance(_initdict_,dict):
      _initdict_ = _initdict_.iteritems();
    for source in _initdict_,kwargs.iteritems():
      for key,value in source:
        try:
          key = self.make_key(key);
        except Exception,info:
          if _verbose_>0: print "skipping %s=%s (%s)" % (key,value,info);
          continue;
        try:
          value = self.make_value(value);
        except Exception,info:
          if _verbose_>0: print "skipping %s=%s (%s)" % (key,value,info);
          continue;
        dict.__setitem__(self,key,value);
        if _verbose_>1: print "adding %s=%s" % (key,value);
    if _verbose_>0: print "initialized",dict.__len__(self),"fields";
  def copy (self):
    rec = record();
    for (k,v) in self.iteritems():
      rec[k] = v;
    return rec;
  # make_key: coerces value to legal key, throws TypeError if illegal
  # this version coerces to string keys, subclasses may redefine this to
  # use different kinds of keys
  def make_key (self,key): 
    "checks key for validity, returns key, raises TypeError if key is illegal";
    return str(key);
  # make_value: coerces value to legal value, throws TypeError if illegal
  # this version does nothing, subclasses may redefine this to do value checking
  def make_value (self,value): 
    "checks value for validity, returns value, raises TypeError if illegal";
    return dmize_object(value);
    
  # helper function to resolve all lazy refs in the record.
  # various functions below that access the dict as a whole will require
  # that all lazy refs are converted to real objects. This function
  # accomplishes that task.
  def _resolve_all_lazy_refs (self):
    lazies = filter(lambda pair:isinstance(pair[1],lazy_objref),dict.iteritems(self));
    for key,ref in lazies:
      dict.__setitem__(self,key,ref.resolve());

  # helper function to resolve a lazy ref to a real value, and replace
  # this in the record
  def _resolve_lazy_ref (self,key,value):
    if isinstance(value,lazy_objref):
      value = value.resolve();
      dict.__setitem__(self,key,value);
    return value;
  
  # items(): we need to resolve all lazy refs first
  def items (self):
    self._resolve_all_lazy_refs();
    return dict.items(self);
  def values (self):  
    self._resolve_all_lazy_refs();
    return dict.items(self);
  # itervalues(): we need to resolve all lazy refs first
  def itervalues (self):
    self._resolve_all_lazy_refs();
    return dict.itervalues(self);
  # iteritems(): we need to resolve all lazy refs first
  def iteritems (self):
    self._resolve_all_lazy_refs();
    return dict.iteritems(self);
  # __getattr__: dict contents are exposed as extra attributes, lazy refs resolved
  def __getattr__(self,name):
    if name.startswith('__'):
      return dict.__getattr__(self,name);
    # else try to access attribute anyway, to see if we have one
    try: return dict.__getattr__(self,name);
    except AttributeError: pass;
    # if none found, go look for a dict key
    try:   key = self.make_key(name);
    except ValueError,info: raise AttributeError,info;
    try:   value = dict.__getitem__(self,key);
    except KeyError: raise AttributeError,"no such field: "+str(key);
    return self._resolve_lazy_ref(key,value);
  # __setattr__: sets entry in dict
  def __setattr__(self,name,value):
    if name.startswith('__'):
      return dict.__setattr__(self,name,value);
    value = self.make_value(value);
    try:   key = self.make_key(name);
    except TypeError,info: raise AttributeError,info;
    return dict.__setitem__(self,key,value);
  # __delattr__: deletes key
  def __delattr__(self,name):
    if name.startswith('__'):
      return dict.__delattr__(self,name,value);
    try:   key = self.make_key(name);
    except ValueError,info: raise AttributeError,info;
    return dict.__delitem__(self,key);
  # get: string names implicitly converted to HIIDs, lazy refs resolved
  def get (self,key,*args):
    if isinstance(key,str):
      try: key = self.make_key(key);
      except ValueError,info: raise TypeError,info;
    value = dict.get(self,key,*args);
    return self._resolve_lazy_ref(key,value);
  # __getitem__: string names implicitly converted to HIIDs, lazy refs resolved
  def __getitem__(self,name):
    return self.get(name);
  # __setitem__: check types, string names implicitly converted to HIIDs
  def __setitem__ (self,name,value):
    value = self.make_value(value);
    try: name = self.make_key(name);
    except TypeError,info: raise TypeError,info;
    return dict.__setitem__(self,name,value);
  # __contains__: string names implicitly converted to HIIDs
  def __contains__(self,name):
    try: 
      return dict.__contains__(self,self.make_key(name));
    except: 
      return False;
    # return map(lambda x:x.as_str('_'),self.keys());
  # __str__: pretty-print
  def __str__ (self):
    dictiter = self.iteritems();
    items = [];
    for (key,value) in dictiter:
      items += ["%s: %s" % (key,str(value)) ];
    return "{ " + string.join(items,', ') + " }";
  # __repr__: official form
  def __repr__ (self):
    dictiter = self.iteritems();
    items = [];
    for (key,value) in dictiter:
      items += ["'%s':%s" % (key,repr(value)) ];
    return self.__class__.__name__+"({" + string.join(items,',') + "})";
  # pop: string names implicitly converted to HIIDs, lazy refs resolved
  def pop (self,key,*args):
    if isinstance(key,str):
      try: key = self.make_key(key);
      except ValueError,info: raise TypeError,info;
    value = dict.pop(self,key,*args);
    if isinstance(value,lazy_objref):
      value = value.resolve();
    return value;
  # popitem: lazy refs resolved
  def popitem (self):
    value = dict.popitem(self);
    if isinstance(value,lazy_objref):
      value = value.resolve();
    return value;
  # field_names: list of dictionary keys  
  def field_names (self):
    "returns a list of field names, in underscore-separator format";
    return self.keys();
  def has_field (self,name):
    "returns a list of field names, in underscore-separator format";
    try: name = self.make_key(name);
    except ValueError,info: raise TypeError,info;
    return self.has_key(name);
  def __eq__ (self,other):
    # helper function compares items
    def item_eq (a,b):
      try:
        if a is b:
          return True;
        if type(a) != type(b):
##          print 'type mismatch';
          return False;
        elif isinstance(a,array_class):
          eq = (a==b);
          if isinstance(eq,int):
            return eq;
          return numarray.alltrue(eq.getflat());
        elif isinstance(a,(list,tuple)):
          if len(a) != len(b):
##            print 'length mismatch';
            return False;
          for (a1,b1) in zip(a,b):
            if not item_eq(a1,b1):
              return False;
          return True;
        else:
          return a == b;
      except: # any exception: comparison fails
##        ei = sys.exc_info();
##        print 'exception in item_eq',ei;
##        traceback.print_tb(ei[2]);
        return False;
      return True;
    # check for trivial case
    if self is other:
      return True;
    # iterate over dict
    if type(self) != type(other) or len(self) != len(other):
##      print 'type/len mismatch';
      return False;
    for (key,a) in self.iteritems():
      if key not in other:
##        print 'key',key,'not in other';
        return False;
      b = other[key];
##      print 'key',key,type(a),type(b);
      if not item_eq(a,b):
##        print 'key',key,'item_eq fails';
        return False;
    return True;
  def __ne__ (self,other):
    return not self.__eq__(other);

make_record = type_maker(record);

class dmilist (list):
  """A dmilist() is a list that is explicitly converted into a DMI::List
  type when passed to C++ (note that normal lists may be converted into a 
  DMI::Vec or DMI::List depending on whether their contents are homogenous
  or not). In all other respects this is identical to a Python list.
  """;
  pass;
  


# 
# === class message ===
# A message represents an OCTOPUSSY message
#
class message (object):
  "Represents an OCTOPUSSY message";
  _stdattrs = ("from","to","priority","state","hops");
  def __init__ (self,msgid,payload=None,priority=0):
    self.msgid = hiid(msgid);
    self.payload = payload;
    self.priority = priority;
  def _is_attr_eq (self,attr,value):
    return hasattr(self,attr) and getattr(self,attr) == value;
  def is_from (self,addr):
    return self._is_attr_eq('from',addr);
  def __repr__ (self):
    return "message("+str(self.msgid)+")";
  def __str__ (self):
    s = "message(" + str(self.msgid);
    attrs = dir(self);
    stds = [ "%s=%s" % (x,getattr(self,x)) for x in message._stdattrs if hasattr(self,x) ];
    return string.join([s]+stds,";") + ")";
    
def make_message(msg,payload=None,priority=0):
  "creates/resolves a message object";
  if isinstance(msg,str):
    msg = message(hiid(msg),payload=payload,priority=priority);
  elif isinstance(msg,hiid):
    msg = message(msg,payload=payload,priority=priority);
  elif isinstance(msg,message):
    if payload != None or priority != 0:
      raise ValueError, "payload and priority specified along with full message object";
  else:
    raise TypeError, "expecting message, got " + str(msg);
  return msg;
  
def make_scope (scope):
  "converts scope string to valid lowercase specifier";
  scope = scope[0].lower();
  if not scope in "ghl":
    raise ValueError,"scope argument must be one of: (g)lobal, (h)ost, (local)";
  return scope;
  
# Other classes  

# array_class
#   use class object from numarray (array() itself is only a function)
array_class = type(numarray.array(0));

# shortcuts for array types 
arr_double = numarray.Float64;
arr_dcomplex = numarray.Complex64;
arr_int32 = numarray.Int32;

def is_array (x):
  return isinstance(x,array_class);
  
def is_scalar (x):
  return isinstance(x,(int,long,float,complex));

# this is a map of known DMI base classes and their corresponding DMI typenames
# subtypes may be derived from these base classes
_dmi_baseclasses = { dmilist:'DMIList',record:'DMIRecord',array_class:'DMINumArray' };

# map of other python DMI types to DMI type names
_dmi_typename_map = { bool:'bool', int:'int', long:'long', float:'double',
                      complex:'dcomplex', str:'string', hiid:'DMIHIID',
                      tuple:'DMIVec',message:'OctopussyMessage' };
                      
# extend this map with the base classes            
_dmi_typename_map.update(_dmi_baseclasses);

# generate reverse map: type names to python DMI types
_dmi_nametype_map = {};
for (t,n) in _dmi_typename_map.iteritems():
  _dmi_nametype_map[n.lower()] = t;
  
def dmi_typename (x,strict=False):
  """returns the DMI type name of its argument.
  If argument is not of a known DMI type, raises KeyError if strict=True, or 
  returns None."""
  nm = _dmi_typename_map.get(type(x),None);
  if strict and nm is None:
    raise KeyError,str(type(x))+" is not a known DMI type";
  return nm;
    
def dmi_type (name,baseclass=None):
  """Returns the type object associated with a DMI type name.
  If not a known DMI type, attempts to register it as a derived class of 
  baseclass. If no base class is supplied, raises an exception."""
  tp = _dmi_nametype_map.get(name.lower(),None);
  # if unknown type, we register a derived type using the baseclass as
  if tp is None:
    if not baseclass:
      raise KeyError,name+" is not a known DMI type, and no base class supplied";
    for bc in _dmi_baseclasses.iterkeys():
      if issubclass(baseclass,bc):
        globals()[name] = tp = new.classobj(name,(baseclass,),{});
        _dmi_typename_map[tp] = name;
        _dmi_nametype_map[name.lower()] = tp;
        return tp;
    # got to here, so no supported baseclass found
    raise TypeError,str(baseclass)+" is not a supported DMI base class";
  else:
    # check base class if supplied
    if baseclass is not None and not issubclass(tp,baseclass):
      raise TypeError,name + " registered with a different base class";
  return tp;

def dmi_coerce (obj,dmitype):
  """Changes type of object to the given dmitype. dmitype must be a subclass
  of the object's type. Use with care. Note that this won't work for 
  internal types (i.e. lists, tuples and such), only for record and arrays."""
  if not issubclass(dmitype,type(obj)):
    raise TypeError,str(dmitype)+' is not a subclass of '+str(type(obj));
  obj.__class__ = dmitype;
  return obj;




def refcount_report (obj,indent=0,name="?",bias=3):
  """Debugging method.
  Prints a report on the refcount of object obj""";
  rc = sys.getrefcount(obj)-bias;
  if rc < 1:
    alert = "*******************";
  else:
    alert = "";
  print " "*indent,"%s (%s): rc %d %s"%(name,type(obj).__name__,rc,alert);
  # print contents
  if isinstance(obj,hiid):
    pass;    # hiid sequencing returns new items, so no point counting refs
  elif isinstance(obj,(list,tuple)):
    for i,x in enumerate(obj):
      refcount_report(x,indent=indent+2,name="[%i]"%i,bias=5);
  elif isinstance(obj,dict):
    for key,val in obj.iteritems():
      refcount_report(val,indent=indent+2,name=str(key),bias=5);
 

  
# import C module
try:
  # when running from inside the kernel, we may already have Timba.octopython
  # as a symbol, but for some reason it's not always in the modules dict
  if not hasattr(Timba,'octopython'):
    import Timba.octopython 
  lazy_objref = Timba.octopython.lazy_objref;
except ImportError:
  print '=========================================================================';
  print '======= Error importing octopython module:';
  traceback.print_exc();
  print '======= Running Timba.dmi module stand-alone with limited functionality';
  print '======= (some things may fail)';
  print '=========================================================================';
  # provide dummy lazy_objref class
  class lazy_objref (object):
    def resolve (self):
      return None;
  
#
# self-test code follows
#
#
def __test_hiids():
  global abc,abc1,a1b1,abca1b1,x;
  print "Checking HIID class";
  abc1 = hiid('a_b_c_1',sep='_');
  abc = hiid('a.b.c');
  a1b1 = hiid('a',1,'b',1);
  abca1b1 = hiid(abc,a1b1);
  print abc1,abc,a1b1,abca1b1;
  print abc+a1b1;
  x = abc;
  print x;
  x += a1b1;
  print x;
  print abca1b1[2];
  print abca1b1[2:6];
  print 'type of x:',type(x);
  print 'dmi_type of x:',dmi_typename(x);
  print "exception expected now";
  try:
    print hiid('x_y_z');
  except: pass
  print "Checking matches() method"
  if not ( abc.matches('a.b.?') and abc.matches('a.*') and not abc.matches('b.*') ):
    raise RuntimeError,'hiid.matches() failed';
  print "Checking comparison"
  if hiid('a') == hiid('b'):
    raise RuntimeError,'comparison error';
  if hiid('a') == 'b':
    raise RuntimeError,'comparison error';
  if hiid('a') != 'a':
    raise RuntimeError,'comparison error';
  if hiid('a') != hiid('a'):
    raise RuntimeError,'comparison error';

def __test_records():
  global rec1,rec2;
  print '------------- building record (non-strict) -------------------------';
  rec1 = dmi_type('MeqPolc',record)();
  rec1.a_b = 0;
  rec1.b = "test";
  rec1.c = record();
  rec1.c.a = 0;
  print 'rec1:',rec1;
  print 'rec1 dmi type:',dmi_typename(rec1);
  print "accessing unknown field, expecting exception";
  try: rec1.d
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print "assigning illegal type, expecting exception";
  try: rec1.d = {}; # plain dicts not supported
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print 'rec1.field_names():',rec1.field_names();
  print 'rec1.repr():',`rec1`;
  print '------------- initializing non-strict record from dict -------------';
  rec3 = record({'a':0,'b':1,'c_d':2,'e':[1,2,3],'f':('x','y'),'g':[1,'x'],'z':(hiid('a'),hiid('b')),'nonhiid':4},verbose=2);
  print 'rec3:',rec3;
  return rec1;
  
def __test_messages():  
  global msg1,msg2;
  # test messages
  msg1 = message('a.b.c.d');
  msg2 = message('x.y.z',priority=10);
  msg1.extra = 1;
  msg2.extra2 = 2;
  print msg1;
  print msg2;

if __name__ == "__main__":
  # print some aids
  print "Number of known AIDs: ",len(Timba.octopython.aid_map),len(Timba.octopython.aid_rmap);
  __test_hiids();
  __test_records();
  __test_messages();
  
