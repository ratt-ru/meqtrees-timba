#!/usr/bin/python

import string
import numarray

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
          mylist = mylist + octopython_c.str_to_hiid(x,sep);
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
    return octopython_c.hiid_to_str(self);
  def __repr__ (self):
    return "hiid('%s')" % str(self);
  # concatenation with '+' must return a hiid
  def __add__ (self,other):
    return hiid(self,other);
  def __radd__ (self,other):
    return hiid(other,self);
  def as_str (self,sep='.'):
    return octopython_c.hiid_to_str(self,sep);
    
def make_hiid (x,sep='.'):
  "converts argument to hiid, if it is not a hiid already";
  if isinstance(x,hiid):
    return x;
  return hiid(x,sep=sep);
  
  
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
  raise TypeError,'dmi: type %s not supported'%type(item);


# === class conv_error ===
# This class represents a conversion error.
# When converting from DMI structures to Python, any errors are represented
# by instances of this class.
# When converting the other way, these objects are ignored.
class conv_error(TypeError):
  def __init__(self,message,exc=None):
    self.message = message;
    self.exc=exc;
  def __repr__(self):
    return '<dmitypes.conv_eror>';
  def __str__(self):
    return '<conv_error>';
  def details(self):
    s = 'conv_error' + str(self.message);
    if( self.exc ): s += ','+str(self.exc);
    return s+')';
  
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
  def __init__ (self,init=None,verbose=0):
    # initialize from init dictionary, checking for valid keys
    if isinstance(init,dict) and len(init):
      dictiter = init.iteritems();
      for (key,value) in dictiter:
        try:
          key = self.make_key(key);
        except Exception,info:
          if verbose>0: print "skipping %s=%s (%s)" % (key,value,info);
          continue;
        try:
          value = dmize_object(value);
        except Exception,info:
          if verbose>0: print "skipping %s=%s (%s)" % (key,value,info);
          continue;
        dict.__setitem__(self,key,value);
        if verbose>1: print "adding %s=%s" % (key,value);
      if verbose>0: print "initialized",dict.__len__(self),"fields";
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
    except KeyError: raise KeyError,"no such field: "+str(key);
  # __setattr__: sets entry in dict
  def __setattr__(self,name,value):
    value = dmize_object(value);
    try:   key = self.make_key(name);
    except ValueError,info: raise AttributeError,info;
    return dict.__setitem__(self,key,value);
  # __delattr__: deletes key
  def __delattr__(self,name):
    try:    key = self.make_key(name);
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
    
# 
# === class message ===
# A message represents an OCTOPUSSY message
#
class message (object):
  "Represents an OCTOPUSSY message";
  stdattrs = ("from","to","priority","state","hops");
  def __init__ (self,msgid,payload=None,priority=0):
    self.msgid = hiid(msgid);
    self.payload = payload;
    self.priority = priority;
  def __repr__ (self):
    return "message(%s)" % self.msgid;
  def __str__ (self):
    s = "message(" + str(self.msgid);
    attrs = dir(self);
    stds = [ "%s=%s" % (x,getattr(self,x)) for x in message.stdattrs 
                                              if x in attrs ];
    return string.join([s]+stds,";") + ")";
    
def make_message(msg,payload=None,priority=0):
  "creates/resolves a message object";
  if isinstance(msg,hiid):
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
  
# tuple of dmi-compatible classes.
dmi_supported_types = (int,long,float,complex,str,hiid,array_class,record,message);

# import C module
import octopython_c
    


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
  print type(x);
  print "exception expected now";
  try:
    print hiid('x_y_z');
  except: pass

def __test_records():
  global rec1,rec2;
  print '------------- building record (non-strict) -------------------------';
  rec1 = record();
  rec1.a_b = 0;
  rec1.b = "test";
  rec1.c = record();
  rec1.c.a = 0;
  print 'rec1:',rec1;
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
  print "Number of known AIDs: ",len(octopython_c.aid_map),len(octopython_c.aid_rmap);
  __test_hiids();
  __test_records();
  __test_messages();
  
