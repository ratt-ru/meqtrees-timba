#!/usr/bin/python
from dmitypes import *

# this returns a string repr of a container
def _contToRepr (value):
  return "<%s:%d>" % (class_name(value),len(value));

# className: returns the DMI class correspodnignt to value
# (__dmi_type attribute if this is set, or simply the class name otherwise)
def class_name (value):
  if hasattr(value,'__dmi_type'):
    return getattr(value,'__dmi_type');
  else:
    return value.__class__.__name__;

# Map of inline conversion methods. Only available for those types for which
# a complete & brif string form is available.
# No methods are defined for containers
TypeToInline = dict.fromkeys((bool,int,long,float,complex),str);
TypeToInline[hiid] = lambda x:'`'+str(x)+'`';
TypeToInline[str]  = lambda x:'"'+x+'"';

def _nonefunc (*args):
    return None;

# Map of representative conversion methods. For types with an inline 
# conversion, this is just the same thing. Containers get a summary
# (see _contToRepr, above)
TypeToRepr = TypeToInline.copy();
for tp in (dict,tuple,list):
  TypeToRepr[dict] = _contToRepr;
TypeToRepr[array_class] = lambda value: "<array:%s:%s>" % (str(value.type()),",".join(map(str,value.shape)));  
TypeToRepr[conv_error] = lambda ce: ce.details();
TypeToRepr[message]    = lambda msg: class_name(msg) + ": "+str(msg.msgid);


#
# class contains methods to convert DMI objects to string representations
#
class dmi_repr (object):
  def __init__ (self,maxlen=256,inline_arr=5,inline_arr_maxlen=32,
                max_inline_arr=50,inline_seq=5):
    self.maxlen            = maxlen;
    self.inline_arr        = inline_arr;
    self.inline_arr_maxlen = inline_arr_maxlen;
    self.inline_seq        = inline_seq;
    self.max_inline_arr    = max_inline_arr;


  def _arrToInline (self,value):
    if value.nelements() <= self.inline_arr:
      s = str(value).replace('\n','').replace('] ',']').replace(' [','[');
      if len(s) <= self.inline_arr_maxlen:
        return (s,True);
    return (None,False);
  
  def _arrToRepr (self,value):
    res = self._arrToInline(value);
    if res[0] is None:
      return ("<array:%s:%s>" % (str(value.type()),",".join(map(str,value.shape))),False);
    return res;
    
  _contToRepr = staticmethod(_contToRepr);

  # returns inline string representation of value, or None if one is not available
  def inline_str (self,value):
    if isinstance(value,array_class):
      return self._arrToInline(value);
    s = TypeToInline.get(type(value),_nonefunc)(value);
    if s is not None and len(s)>self.maxlen:
      return (s[:self.maxlen-3] + '...',False);
    return (s,True);

  # returns representative string for value; use str() built-in as default
  # if a specific repr-method is not defined
  def repr_str (self,value):
    tp = type(value);
    if issubclass(tp,array_class):
      return self._arrToRepr(value);
    # container class? Use container repr
    for cont in (dict,tuple,list):
      if issubclass(tp,cont):
        s = self._contToRepr(value);
        break;
    else:
      s = TypeToRepr.get(type(value),str)(value);
    if len(s)>self.maxlen:
      return (s[:self.maxlen-3] + '...',False);
    return (s,True);


  # converts a sequence to an inline string
  # returns a tuple of (str,bool); the bool flag is True if the sequence was
  # entirely inline-able
  def expanded_repr_str (self,value,use_typename=True):
    # first, process arrays
    if isinstance(value,array_class):
      (str0,inlined) = self._arrToRepr(value);
      if inlined:  # if this is true, str0 already contains complete array
        return (str0+"   <array:%s:%s>" % (str(value.type()),",".join(map(str,value.shape))),False);
      # array size + array stats
      str1 = map(lambda attr:':'.join((attr,str(getattr(value,attr)()))),("mean","min","max"));
      str1 = ' '.join(str1);
      return (''.join((str0,'   ',str1)),False);
      
    ### now try to inline value as a whole
    (res,inlined) = self.inline_str(value);
    if res is not None:
      return (res,inlined);
    
    ### failed; get repr_str, treat as container
    (str0,inlined) = self.repr_str(value);
    # figure out how to convert container items to strings
    conv = None;
    if isinstance(value,tuple):
      braces = '()';
      iterator = value;
      conv = lambda x: ('',x);
    elif isinstance(value,list):
      braces = '[]';
      iterator = value;
      conv = lambda x: ('',x);
    elif isinstance(value,dict):
      braces = '{}';
      iterator = value.iteritems();
      conv = lambda x: (str(x[0])+':',x[1]);
    else:  # else some other type: simply return its repr
      return (str0,inlined);
    # now convert sequence
    inlined = True;
    str1 = '';
    for item in iterator:
      (s0,x) = conv(item);
      # try to get inlined string
      (s1,inl) = self.inline_str(x);
      # else use summary string
      if s1 is None:
        inlined = False;
        (s1,inl) = self.repr_str(x);
      s1 = s0+s1;
      if not str1:  # first item always added
        str1 = s1;
      else:    # else check, are we still under max length? append and go on
        if len(str1) + len(s1) < self.maxlen:
          str1 = ','.join((str1,s1));
        else:  # else terminate string with '...' and break out 
          inlined = False;
          str1 = ''.join((braces[0],str1,',...'));
          break;
    else:  # no breaks, add closing brace
      str1 = ''.join((braces[0],str1,braces[1]));
    if use_typename:
      return (''.join((str1,'   ',str0)),inlined);
    else:
      return str1;
