#!/usr/bin/python

# MEQ Data Services

from dmitypes import *
import weakref
import types
import new
import sets

class _meqnode_nodeclass(record):
  pass;

_NodeClassDict = { 'meqnode':_meqnode_nodeclass };

# this function returns (creating as needed) the "Node class" class object
# for a given classname
def NodeClass(nodeclass=None):
  global _NodeClassDict;
  if nodeclass is None:
    return _meqnode_nodeclass;
  elif not isinstance(nodeclass,str):
    nodeclass = getattr(nodeclass,'classname',None) or getattr(nodeclass,'class');
  cls = _NodeClassDict.get(nodeclass,None);
  if cls is None:
    cls = _NodeClassDict[nodeclass] = new.classobj(nodeclass,(_meqnode_nodeclass,),{});
  return cls;

# this class defines and manages a node list
class NodeList (object):
  NodeAttrs = ('name','class','children');
  RequestRecord = srecord(dict.fromkeys(NodeAttrs,True),nodeindex=True);
  
  class Node (object):
    def __init__ (self,ni):
      self.nodeindex = ni;
      self.name = None;
      self.classname = None;
      self.children = [];
      self.parents  = [];

  # init node list
  def __init__ (self,meqnl=None):
    if meqnl:
      self.load_meqlist(meqnl);
  
  # initialize from a MEQ-produced nodelist
  def load (self,meqnl):
    if not self.is_valid_meqnodelist(meqnl):
      raise ValueError,"not a valid meqnodelist";
    # check that all list fields are correct
    num = len(meqnl.nodeindex);
    # form sequence of iterators
    iter_name     = iter(meqnl.name);
    iter_class    = iter(meqnl['class']);
    iter_children = iter(meqnl.children);
    self._nimap = {};
    self._namemap = {};
    self._classmap = {};
    # iterate over all nodes in list
    for ni in meqnl.nodeindex:
      # insert node into list (or use old one: may have been inserted below)
      node = self._nimap.setdefault(ni,self.Node(ni));
      node.name      = iter_name.next();
      node.classname = iter_class.next();
      children  = iter_children.next();
      if isinstance(children,dict):
        node.children = tuple(children.iteritems());
      else:
        node.children = tuple(enumerate(children));
      # for all children, init node entry in list (if necessary), and
      # add to parent list
      for (i,ch_ni) in node.children:
        self._nimap.setdefault(ch_ni,self.Node(ch_ni)).parents.append(ni);
      # add to name map
      self._namemap[node.name] = node;
      # add to class map
      self._classmap.setdefault(node.classname,[]).append(node);
    # compose list of root (i.e. parentless) nodes
    self._rootnodes = [ node for node in self._nimap.itervalues() if not node.parents ];
    
#  __init__ = busyCursorMethod(__init__);
  # return list of root nodes
  def rootnodes (self):
    return self._rootnodes;
  # return map of classes
  def classes (self):
    return self._classmap;
  def iteritems (self):
    return self._nimap.iteritems();
  def iternodes (self):
    return self._nimap.itervalues();
  # mapping methods
  def __len__ (self):
    return len(self._nimap);
  # helper method: selects name or nodeindex map depending on key type
  def _map_ (self,key):
    if isinstance(key,str):     return self._namemap;
    elif isinstance(key,int):   return self._nimap;
    else:                       raise TypeError,"invalid node key "+str(key);
  def __getitem__ (self,key):
    return self._map_(key).__getitem__(key);
  def __contains__ (self,key):
    return self._map_(key).__contains__(key);
  def __setitem__ (self,key,node):
    if __debug__:
      if isinstance(key,string):  assert value.name == key;
      elif isinstance(key,int):   assert value.nodeindex == key;
      else:                       raise TypeError,"invalid node key "+str(key);
    self._nimap[node.nodeindex] = self._namemap[node.name] = node;
  def __iter__(self):
    return iter(self._nimap);

  # return True if this is a valid meqNodeList (i.e. node list object from meq kernel)
  def is_valid_meqnodelist (nodelist):
    for f in ('nodeindex',) + NodeList.NodeAttrs:
      if f not in nodelist:
        return False;
    return True;
  is_valid_meqnodelist = staticmethod(is_valid_meqnodelist);

# creates a UDI from a node record or node index or node name
def node_udi (node):
  try: (name,index) = (node.name,node.nodeindex);
  except AttributeError,KeyError: 
    node = nodelist[node];
    (name,index) = (node.name,node.nodeindex);
  return "/nodestate/%s#%d"%(name,index);

def set_meqserver (mqs1):
  global mqs;
  mqs = weakref.proxy(mqs1);

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

def reclassify_nodestate (nodestate):
  nodestate.__class__ = NodeClass(nodestate['class']);

# Adds a subscriber to node state changes
#   If weak=True, callback will be held via weakref, otherwise
#   via WeakInstanceMethod (if object method), otherwise via direct ref
#
def subscribe_node_state (node,callback,weak=False):
  if not isinstance(node,record):
    node = nodelist[node];
  if type(callback) == types.MethodType:
    callback = WeakInstanceMethod(callback);
  elif not callable(callback):
    raise TypeError,"callback argument is not a callable";
  elif weak:
    callback = weakref.ref(callback);
  # add to subscriber list
  node_subscribers.setdefault(node.nodeindex,sets.Set()).add(callback);

def request_node_state (node):
  if not isinstance(node,record):
    node = nodelist[node];
  mqs1 = mqs or mqs();
  if mqs1 is None:
    raise RuntimeError,"meqserver not initialized or not running";
  mqs.meq('Node.Get.State',srecord(nodeindex=node.nodeindex),wait=False);
  
def update_node_state (node,event):
  callbacks = node_subscribers.get(node.nodeindex,());
  deleted = [];
  for cb in callbacks:
    if type(cb) == weakref.ReferenceType:
      cb1 = cb();
      if cb1 is None:
        deleted.append(cb);
      else:
        cb1(node,event);
    elif isinstance(cb,WeakInstanceMethod):
      if cb(node,event) is WeakInstanceMethod.DeadRef:
        deleted.append(cb);
    else:
      cb(node,event);
  # delete any dead subscribers
  for d in deleted:
    callbacks.remove(d);


# create global node list
nodelist = NodeList();

node_subscribers = {};
mqs = None;


