#!/usr/bin/python
from dmitypes import *

# this returns a string repr of a container
def _contToRepr (value,prec=None):
  return "<%s:%d>" % (class_name(value),len(value));

# className: returns the DMI class correspodnignt to value
# (__dmi_type attribute if this is set, or simply the class name otherwise)
def class_name (value):
  if hasattr(value,'__dmi_type'):
    return getattr(value,'__dmi_type');
  else:
    return value.__class__.__name__;

def str_no_prec(x,prec=None):
  return str(x);

def str_float (x,prec=None):
  if prec is None:
    return str(x);
  else:
    return "%.*g" % (prec,x);
    
def str_complex (x,prec=None):
  if prec is None:
    return "%f%+fi"%(x.real,x.imag);
  else:
    return "%.*g%+.*gi" % (prec,x.real,prec,x.imag);

# Map of inline conversion methods. Only available for those types for which
# a complete & brief string form is available.
# No methods are defined for containers
TypeToInline = dict.fromkeys((bool,int,long),str_no_prec);
TypeToInline[float] = str_float;
TypeToInline[complex] = str_complex;
TypeToInline[hiid] = lambda x,prec=None:'`'+str(x)+'`';
TypeToInline[str]  = lambda x,prec=None:'"'+x+'"';

def _nonefunc (*args,**kwargs):
  return None;

# Map of representative conversion methods. For types with an inline 
# conversion, this is just the same thing. Containers get a summary
# (see _contToRepr, above)
TypeToRepr = TypeToInline.copy();
for tp in (dict,tuple,list):
  TypeToRepr[tp] = _contToRepr;
TypeToRepr[array_class] = lambda value,prec=None: "<array:%s:%s>" % (str(value.type()),",".join(map(str,value.shape)));  
TypeToRepr[conv_error] = lambda ce,prec=None: ce.details();
TypeToRepr[message]    = lambda msg,prec=None: class_name(msg) + ": "+str(msg.msgid);


#
# class contains methods to convert DMI objects to string representations
#
class dmi_repr (object):
  def __init__ (self,maxlen=256,inline_arr=5,
                max_inline_arr=50,inline_seq=5):
    self.maxlen            = maxlen;
    self.inline_arr        = inline_arr;
    self.inline_seq        = inline_seq;
    self.max_inline_arr    = max_inline_arr;


  def _arrToInline (self,value,prec=None):
    def list_to_str (arg,prec=None):
      if not arg:
        return '[]';
      if isinstance(arg[0],list):
        res = map(lambda x:list_to_str(x,prec=prec),arg);
        if res and res[0] is None:
         return None;
      else:
        func = TypeToInline.get(type(arg[0]),None);
        res = func and map(lambda x:func(x,prec=prec),arg);
      if res is None:
        return None;
      else:
        return ''.join(('[',','.join(res),']'));
    if value.nelements() <= self.inline_arr:
      s = list_to_str(value.tolist(),prec=prec);
      if s:
        if len(value.shape) > 1:
          s = ' '.join(('x'.join(map(str,value.shape)),s));
        return (s,True);
    return (None,False);
  
  def _arrReprString (self,value):
    return ("[array %s: %s]" % (str(value.type()),"x".join(map(str,value.shape))),False);
  
  def _arrToRepr (self,value,prec=None):
    res = self._arrToInline(value,prec=prec);
    if res[0] is None:
      return self._arrReprString(value);
    return res;
    
  _contToRepr = staticmethod(_contToRepr);

  # returns inline string representation of value, or None if one is not available
  def inline_str (self,value,prec=None):
    if isinstance(value,array_class):
      return self._arrToInline(value,prec=prec);
    s = TypeToInline.get(type(value),_nonefunc)(value,prec=prec);
    if s is not None and len(s)>self.maxlen:
      return (s[:self.maxlen-3] + '...',False);
    return (s,True);

  # returns representative string for value; use str() built-in as default
  # if a specific repr-method is not defined
  def repr_str (self,value,prec=None):
    tp = type(value);
    if issubclass(tp,array_class):
      return self._arrToRepr(value,prec=prec);
    # container class? Use container repr
    for cont in (dict,tuple,list):
      if issubclass(tp,cont):
        s = self._contToRepr(value,prec=prec);
        break;
    else:
      s = TypeToRepr.get(type(value),str_no_prec)(value,prec=prec);
    if len(s)>self.maxlen:
      return (s[:self.maxlen-3] + '...',False);
    return (s,True);


  # converts a sequence to an inline string
  # returns a tuple of (str,bool); the bool flag is True if the sequence was
  # entirely inline-able
  def expanded_repr_str (self,value,use_typename=True,prec=None):
    # first, process arrays
    if isinstance(value,array_class):
      (str0,inlined) = self._arrToRepr(value,prec=prec);
      if inlined:  # if this is true, str0 already contains complete array
        return (str0+self._arrReprString(value),True);
      # array size + array stats
      str1 = [ ': '.join((attr,self.inline_str(getattr(value,attr)(),prec=prec)[0])) \
                  for attr in ("mean","min","max") ];
      str1 = ', '.join(str1);
      return (''.join((str0,' ',str1)),False);
      
    ### now try to inline value as a whole
    (res,inlined) = self.inline_str(value,prec=prec);
    if res is not None:
      return (res,inlined);
    
    ### failed; get repr_str, treat as container
    (str0,inlined) = self.repr_str(value,prec=prec);
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
      conv = lambda x: (str(x[0])+': ',x[1]);
    elif isinstance(value,conv_error):
      return (value.details(),True);
    else:  # else some other type: simply return its repr
      return (str0,inlined);
    # now convert sequence
    inlined = True;
    str1 = '';
    for item in iterator:
      (s0,x) = conv(item);
      # try to get inlined string
      (s1,inl) = self.inline_str(x,prec=prec);
      # else use summary string
      if s1 is None:
        inlined = False;
        (s1,inl) = self.expanded_repr_str(x,use_typename=use_typename,prec=prec);
      s1 = s0+s1;
      if not str1:  # first item always added
        str1 = s1;
      else:    # else check, are we still under max length? append and go on
        if len(str1) + len(s1) < self.maxlen:
          str1 = ', '.join((str1,s1));
        else:  # else terminate string with '...' and break out 
          inlined = False;
          str1 = ''.join((braces[0],str1,',...'));
          break;
    else:  # no breaks, add closing brace
      str1 = ''.join((braces[0],str1,braces[1]));
    if use_typename:
      return (''.join((str1,'   ',str0)),inlined);
    else:
      return (str1,inlined);
