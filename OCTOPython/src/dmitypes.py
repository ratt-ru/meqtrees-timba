#!/usr/bin/python

import string
import numarray
import sys

from numarray import array;

# 
# === class hiid ===
#
class hiid (tuple):
  "Represents the DMI HIID class";
  def __new__ (self,*args,**kw):
    sep = kw.get('sep','.');           # use '.' separator by default
    mylist = ();
    for x in args:
      if isinstance(x,str):            # a string? Use HIID mapping functions
        try:
          mylist = mylist + octopython.str_to_hiid(x,sep);
        except:
          raise ValueError, "'%s' is not a valid hiid"%x;
      elif isinstance(x,(tuple,list)): # other sequence? use as list
        mylist = mylist + tuple(x);
      elif isinstance(x,(int,long)):   # int/long? add to list
        mylist = mylist + (x,);
      else:
        raise ValueError, "can't construct hiid from a %s"%type(x);
    return tuple.__new__(self,mylist);
  # redefine __getitem__: if key is a slice, then the subsequence should be
  # converted to hiid
  def __getitem__ (self,key):
    return hiid(tuple.__getitem__(self,key));
  def __getslice__ (self,i,j):
    # print 'getslice: ',i,j;
    return hiid(tuple.__getslice__(self,i,j));
  def __str__ (self):
    return octopython.hiid_to_str(self);
  def __repr__ (self):
    return "hiid('%s')" % str(self);
  # matches() function matches hiids
  def matches (self,other):
    return octopython.hiid_matches(self,make_hiid(other));
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
    return octopython.hiid_to_str(self,sep);
  # as_int converts to int
  def as_int (self):
    if len(self) > 1:
      raise TypeError,"can't convert multiple-element hiid to int";
    return int(tuple.__getitem__(self,0));
  __int__ = as_int;

def type_maker(objtype,**kwargs):
  def maker(x):
    if isinstance(x,objtype):
      return x;
    return objtype(x);
  return maker;
  
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
# is impossible/
# Current valid types are:
# (*) see dmi_supported_types tuple defined below
# (*) homogenous lists or tuples of supported object types
#     (homogenous == all items in sequence have the same type)
def dmize_object (obj):
  "coerces object into a DMI-supported type as needed. Returns the "
  "object on success, or raises a TypeError on failure";
  # object of supported type is returned as-is
  if isinstance(obj,dmi_supported_types):
    return obj;
  # homogenous sequences of supported types are also supported, converted
  # to a list
  if isinstance(obj,(list,tuple)):
    seqtype = type(obj);
    if not len(obj):    # empty sequences always allowed
      return obj;   
    outlist = []; # dmize seqeuence elements one by one and collect them in this list
    eltype = type(obj[0]);  # element type must be homogenous
    for item in obj:
      if type(item) != eltype:
        raise TypeError,'dmi: mixed-type sequences not supported (have %s and %s)'%(eltype,type(item));
      outlist.append(dmize_object(item));
    # convert resulting list back into original sequence type
    return seqtype(outlist);
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
  
# 
# === class record ===
# A record is a restricted dict that only allows specific kinds of keys
# (in this case strings, but this may be redefined in subclasses).
# Records also provide access to their elements via attributes, using the 
# conventional rec.field notation.
# Field values are limited to dmizable objects.
#
class record (dict):
  "represents a record class with string keys";
  def __init__ (self,_initdict_=None,_verbose_=0,**kwargs):
    # initialize from init dictionary and from kwargs, checking for valid keys
    for source in _initdict_,kwargs:
      if isinstance(source,dict):
        for key,value in source.iteritems():
          try:
            key = self.make_key(key);
          except Exception,info:
            if _verbose_>0: print "skipping %s=%s (%s)" % (key,value,info);
            continue;
          try:
            value = dmize_object(value);
          except Exception,info:
            if _verbose_>0: print "skipping %s=%s (%s)" % (key,value,info);
            continue;
          dict.__setitem__(self,key,value);
          if _verbose_>1: print "adding %s=%s" % (key,value);
        if _verbose_>0: print "initialized",dict.__len__(self),"fields";
  # make_key: coerces value to legal key, throws ValueError if illegal
  # this version coerces to string keys, subclasses may redefine this to
  # use different kinds of keys
  def make_key (self,key): 
    "checks key for validity, returns key, raises TypeError if key is illegal";
    return str(key);
  # __getattr__: dict contents are exposed as extra attributes
  def __getattr__(self,name):
    # try to access attribute directly first
    try: return dict.__getattr__(self,name);
    except AttributeError: pass
    # if no found, go look for a dict key
    try:   key = self.make_key(name);
    except ValueError,info: raise AttributeError,info;
    try:   return dict.__getitem__(self,key);
    except KeyError: raise AttributeError,"no such field: "+str(key);
  # __setattr__: sets entry in dict
  def __setattr__(self,name,value):
    if name.startswith('__'):
      return dict.__setattr__(self,name,value);
    value = dmize_object(value);
    try:   key = self.make_key(name);
    except ValueError,info: raise AttributeError,info;
    return dict.__setitem__(self,key,value);
  # __delattr__: deletes key
  def __delattr__(self,name):
    if name.startswith('__'):
      return dict.__delattr__(self,name,value);
    try:   key = self.make_key(name);
    except ValueError,info: raise AttributeError,info;
    return dict.__delitem__(self,key);
  # __getitem__: string names implicitly converted to HIIDs
  def __getitem__(self,name):
    if isinstance(name,str):
      try: name = self.make_key(name);
      except ValueError,info: raise TypeError,info;
      try: return dict.__getitem__(self,name);
      except KeyError: raise KeyError,"no such field: "+str(name);
    return dict.__getitem__(self,name);
  # __setitem__: check types, string names implicitly converted to HIIDs
  def __setitem__ (self,name,value):
    value = dmize_object(value);
    try: name = self.make_key(name);
    except ValueError,info: raise TypeError,info;
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
  # field_names: list of dictionary keys  
  def field_names (self):
    "returns a list of field names, in underscore-separator format";
    return self.keys();
  def has_field (self,name):
    "returns a list of field names, in underscore-separator format";
    try: name = self.make_key(name);
    except ValueError,info: raise TypeError,info;
    return self.has_key(name);

# 
# === class srecord ===
# srecord ("strict record") is a record with hiid-compatible keys. 
# The actual keys are still strings, but they all must have a valid HIID 
# representation.
#
class srecord (record):
  "represents a strict DMI-like record (all keys must be legal HIIDs)";
  # redefine make_key to check for HIIDs
  def make_key (self,key): 
    "checks key for validity (must be hiid), returns key, raises "
    "TypeError if key is illegal";
    try: make_hiid(key,sep='._');
    except Exception,info: raise TypeError,info;
    return str(key);
    
make_record = type_maker(record);
make_srecord = type_maker(srecord);

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
  
# 
# === class verbosity ===
# Verbosity includes methods for verbosity levels and conditional printing
#
class verbosity:
  def __init__(self,verbose=0,stream=sys.stderr,name=None):
    self.verbose = verbose;
    self.stream = stream;
    self.vobj_name = name or self.__class__.__name__;
  def dprint(self,level,*args):
    if level <= self.verbose:
      self.stream.write(self.object_name()+': ');
      self.stream.write(string.join(map(str,args),' ')+'\n'); 
  def dprintf(self,level,format,*args):
#    print format,args;
    if level <= self.verbose:
      try: s = format % args;
      except: 
        self.stream.write('dprintf format exception: ' + str(format) + '\n');
      else:
        self.stream.write(self.object_name()+': ');
        self.stream.write(s);
  def get_verbose(self):
    return self.verbose;
  def set_verbose(self,verbose):
    self.verbose = verbose;
  def set_stream(self,stream):
    self.stream = stream;
  def set_vobj_name(self,name):
    self.vobj_name = name;
  def object_name (self):
    return self.vobj_name;
  
  
  
# Other classes  

# array_class
#   use class object from numarray (array() itself is only a function)
array_class = type(numarray.array(0));

# shortcuts for array types 
arr_double = numarray.Float64;
arr_dcomplex = numarray.Complex64;


def is_array (x):
  return isinstance(x,array_class);
  
def is_scalar (x):
  return isinstance(x,(int,long,float,complex));

# map of python types to DMI type names
dmi_type_map = { bool:'bool', int:'int', long:'long', float:'double',
                 complex:'dcomplex', str:'string', hiid:'HIID',
                 array_class:'DataArray', 
                 record:'DataRecord',srecord:'DataRecord', 
                 message:'Message' };

# tuple of python types supported by DMI                 
dmi_supported_types = tuple(dmi_type_map.keys());
  
def dmi_type (x):
  "returns the DMI type of its argument, or None if argument is not a DMI type";
  # __dmi_type attribute overrides everything
  if hasattr(x,'__dmi_type'):
    return x.__dmi_type;
  elif isinstance(x,record):       # record may have subclasses
    return 'DataRecord';
  else:
    return dmi_type_map.get(type(x),None);
  
# curry() composes callbacks and such
# See The Python Cookbook recipe 15.7
def curry (func,*args,**kwds):
  def callit(*args1,**kwds1):
    kw = kwds.copy();
    kw.update(kwds1);
    return func(*(args+args1),**kw);
  return callit;
  
# Extended curry() version
# The _argslice argument is applied to the *args of the
# curry when it is subsequently called; this allows only a subset of the
# *args to be passed to the curried function.
def xcurry (func,_args=(),_argslice=slice(None),_kwds={},**kwds):
  kwds0 = _kwds.copy();
  kwds0.update(kwds);
  def callit(*args1,**kwds1):
    kw = kwds0.copy();
    kw.update(kwds1);
    return func(*(_args+args1[_argslice]),**kw);
  return callit;

# import C module
import octopython

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
  print 'dmi_type of x:',dmi_type(x);
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
  rec1 = record();
  rec1.a_b = 0;
  rec1.b = "test";
  rec1.c = record();
  rec1.c.a = 0;
  rec1.__dmi_type = 'Polc';
  print 'rec1:',rec1;
  print 'rec1.__dmi_type:',rec1.__dmi_type;
  print 'rec1 dmi type:',dmi_type(rec1);
  print "accessing unknown field, expecting exception";
  try: rec1.d
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print "assigning illegal type, expecting exception";
  try: rec1.d = [0,'x'];
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print 'rec1.field_names():',rec1.field_names();
  print 'rec1.repr():',`rec1`;
  print '------------- building record (strict) -----------------------------';
  srec1 = srecord();
  srec1.a_b = 0;
  srec1.b = "test";
  srec1.c = srecord();
  srec1.c.a = 0;
  print 'srec1:',srec1;
  print "accessing unknown field, expecting exception";
  try: print srec1.d;
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print "accessing illegal field, expecting exception";
  try: print srec1.nonhiid;
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print "assigning to illegal field, expecting exception";
  try: srec1.nonhiid = 0;
  except Exception,info: print "got exception:",info;
  else: raise RuntimeError,'exception should have been raised';
  print 'srec1.field_names():',srec1.field_names();
  print 'srec1.repr():',`srec1`;
  print '------------- initializing strict record from dict -----------------';
  rec2 = srecord({'a':0,'b':1,'c_d':2,'e':[1,2,3],'f':('x','y'),'g':[1,'x'],'z':(hiid('a'),hiid('b')),'nonhiid':4},verbose=2);
  print 'rec2:',rec2;
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
  print "Number of known AIDs: ",len(octopython.aid_map),len(octopython.aid_rmap);
  __test_hiids();
  __test_records();
  __test_messages();
  
