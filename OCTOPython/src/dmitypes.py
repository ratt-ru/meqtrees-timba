#!/usr/bin/python

import string
import octopython_c
import numarray

class hiid (tuple):
  "Represents the DMI HIID class";
  def __new__ (self,*args,**kw):
    sep = kw.get('sep','.');           # use '.' separator by default
    mylist = ();
    for x in args:
      if isinstance(x,str):            # a string? Use HIID mapping functions
        mylist = mylist + octopython_c.str_to_hiid(x,sep);
      elif isinstance(x,(tuple,list)): # other sequence? use as list
        mylist = mylist + tuple(x);
      elif isinstance(x,(int,long)):   # int/long? add to list
        mylist = mylist + (x,);
      else:
        raise TypeError, "can't construct hiid from " + str(x);
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
  
class dmicontainer (object):
  "Common base for DMI containers";
  pass;
  
class field (dmicontainer):
  pass;
  
array_class = numarray.array(0).__class__;
  
class record (dict,dmicontainer):
  "represents a DMI record";
  supported_types = (int,long,float,complex,str,array_class,dmicontainer);
  def __init__ (self,initdict={},verbose=0):
    # initialize from dictionary, checking for valid (hiid) jkeys
    if len(initdict):
      dictiter = initdict.iteritems();
      for (key,value) in dictiter:
        try:
          key = make_hiid(key,sep='._');
          if isinstance(value,self.supported_types):
            dict.__setitem__(self,key,value);
            if verbose>1: print "adding %s=%s" % (key,value);
          else:
            if verbose>0: print "skipping %s=%s (bad type %s)" % (key,value,type(value));
        except:
          if verbose>0: print "skipping %s=%s (bad key?)" % (key,value);
      if verbose>0: print "initialized",dict.__len__(self),"fields";
  # __getattr__: dict contents are exposed as extra attributes
  def __getattr__(self,name):
    try: return dict.__getattr__(self,name);
    except AttributeError: pass
    # print 'getattr(%s) failed, looking up key'%name;
    try:    key = make_hiid(name,sep='._');
    except: raise AttributeError,"field name '%s' is not a legal hiid"%name;
    try:    return dict.__getitem__(self,key);
    except KeyError: raise KeyError,"no such field: "+str(key);
  # __setattr__: sets entry in dict
  def __setattr__(self,name,value):
    if not isinstance(value,self.supported_types):
      raise TypeError,"type %s not supported by record"%type(value);
    try:    key = make_hiid(name,sep='._');
    except: raise AttributeError,"field name '%s' is not a legal hiid"%name;
    return dict.__setitem__(self,key,value);
  # __delattr__: deletes key
  def __delattr__(self,name):
    try:    key = make_hiid(name,sep='._');
    except: raise AttributeError,"field name '%s' is not a legal hiid"%name;
    return dict.__delitem__(self,key);
  # __getitem__: string names implicitly converted to HIIDs
  def __getitem__(self,name):
    if isinstance(name,str):
      try: key = make_hiid(name,sep='._');
      except: raise AttributeError,"field name '%s' is not a legal hiid"%name;
      try: return dict.__getitem__(self,key);
      except KeyError: raise KeyError,"no such field: "+str(key);
    return dict.__getitem__(self,key);
  # __setitem__: check types, string names implicitly converted to HIIDs
  def __setitem__ (self,name,value):
    if not isinstance(value,self.supported_types):
      raise TypeError,"type %s not supported by record"%type(value);
    try:    key = make_hiid(name,sep='._');
    except: raise TypeError,"key '%s' is not a legal hiid"%name;
    return dict.__setitem__(self,key,value);
    
  def field_names (self):
    "returns a list of field names, in underscore-separator format";
    return map(lambda x:x.as_str('_'),self.keys());
    
#  def __str__ (self):
#    dictiter = self.iteritems();
#    for (key,value) in dictiter:
    
    
  
#  def __repr__ (self):
    
  
    
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

def __test_messages():  
  global msg1,msg2;
  # test messages
  msg1 = message('a.b.c.d');
  msg2 = message('x.y.z',priority=10);
  msg1.extra = 1;
  msg2.extra2 = 2;
  print msg1;
  print msg2;
  
def __test_records():
  global rec1,rec2;
  rec1 = record();
  rec1.a_b = 0;
  rec1.b = "test";
  rec1.c = record();
  rec1.c.a = 0;
  print rec1;
  print "accessing unknown field";
  try: rec1.d
  except: print "got exception";
  print rec1.field_names();
  rec2 = record({'a':0,'b':1,'c_d':2,'e':[1,2,3],'notincluded':4},2);
  print rec2;
  return rec1;
    
if __name__ == "__main__":
  # print some aids
  print "Number of known AIDs: ",len(octopython_c.aid_map),len(octopython_c.aid_rmap);
  __test_hiids();
  __test_messages();
  __test_records();
  
