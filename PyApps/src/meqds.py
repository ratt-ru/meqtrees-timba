#!/usr/bin/python

# MEQ Data Services

from dmitypes import *
import weakref
import types
import new
import sets
import re
import time
from qt import *
import app_pixmaps as pixmap

_dbg = verbosity(0,name='meqds');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class _meqnode_nodeclass(record):
  pass;

_NodeClassDict = { 'meqnode':_meqnode_nodeclass };

# this function returns (creating as needed) the "Node class" class object
# for a given classname
def NodeClass (nodeclass=None):
  global _NodeClassDict;
  if nodeclass is None:
    return _meqnode_nodeclass;
  elif not isinstance(nodeclass,str):
    nodeclass = getattr(nodeclass,'classname',None) or getattr(nodeclass,'class');
  nodeclass = nodeclass.lower();
  cls = _NodeClassDict.get(nodeclass,None);
  if cls is None:
    cls = _NodeClassDict[nodeclass] = new.classobj(nodeclass,(_meqnode_nodeclass,),{});
  return cls;

# this is copied verbatim from the ControlStates definition in MEQ/Node.h
CS_ACTIVE              = 0x0001;
CS_MASK_CONTROL        = 0x000F;
CS_RES_MASK            = 0x0070;
CS_RES_NONE            = 0x0000;
CS_RES_OK              = 0x0010;
CS_RES_WAIT            = 0x0020;
CS_RES_EMPTY           = 0x0030;
CS_RES_MISSING         = 0x0040;
CS_RES_FAIL            = 0x0050;
CS_PUBLISHING          = 0x0100;
CS_CACHED              = 0x0200;
CS_RETCACHE            = 0x0400;
CS_BREAKPOINT          = 0x0800;
CS_BREAKPOINT_SS       = 0x1000;
CS_STOP_BREAKPOINT     = 0x2000;

CS_LSB_EXECSTATE       = 16;  # first bit of exec-state segment
CS_MASK_EXECSTATE      = 0xF<<CS_LSB_EXECSTATE;

CS_ES_statelist = [ (0<<CS_LSB_EXECSTATE,'IDLE' ,'-','idle',pixmap.node_idle),
                    (1<<CS_LSB_EXECSTATE,'REQ'  ,'R','received request',pixmap.node_request),
                    (2<<CS_LSB_EXECSTATE,'CMD'  ,'C','processing command rider',pixmap.node_command),
                    (3<<CS_LSB_EXECSTATE,'POLL' ,'P','polling children',pixmap.node_poll),
                    (4<<CS_LSB_EXECSTATE,'EVAL' ,'E','evaluating result',pixmap.node_eval) ];
                    
# define CS_ES_XXX constants for the listed states, and
# BP_XXX constants to represent breakpoint masks
for st in CS_ES_statelist:
  globals()['CS_ES_'+st[1]] = st[0];
  globals()['BP_'+st[1]] = int(1<<st[0]);

# mask of all breakpoints
BP_ALL = 0xFF;
                    
def CS_ES_state (statusword):
  "returns tuple describing exec-state based on the given status word";
  return CS_ES_statelist[(statusword&CS_MASK_EXECSTATE)>>CS_LSB_EXECSTATE];

def breakpoint_mask (es=-1):
  """for a given exec-state, returns corresponding breakpoint mask, or ALL if argument is <0""";
  if es<0:
    return BP_ALL;
  else:
    return 1<<(es>>CS_LSB_EXECSTATE);
                     
# map of result types                 
CS_RES_map = {  CS_RES_NONE:     ('-','valid result'),
                CS_RES_OK:       ('o','valid result'),
                CS_RES_WAIT:     ('w','WAIT code returned'),
                CS_RES_EMPTY:    ('e','empty result returned'),
                CS_RES_FAIL:     ('!','fail result returned')   };
 
# this class defines and manages a node list
class NodeList (object):
  NodeAttrs = ('name','class','children','control_status');
  RequestRecord = srecord(**dict.fromkeys(NodeAttrs,True));
  RequestRecord.nodeindex=True;
  RequestRecord.get_forest_status=True;
  
  class Node (QObject):
    def __init__ (self,ni):
      QObject.__init__(self);
      self.nodeindex = ni;
      self.name = None;
      self.classname = None;
      self.children = [];
      self.parents  = [];
      self.request_id = None;
      self.breakpoint = 0;
      self.control_status = 0;
      self.control_status_string = '';
    def is_active (self):
      return bool(self.control_status&CS_ACTIVE);
    def is_publishing (self):
      return bool(self.control_status&CS_PUBLISHING);
    def has_breakpoints (self):
      return bool(self.control_status&CS_BREAKPOINT);
    def exec_state (self):
      return self.control_status&CS_MASK_EXECSTATE;
    def exec_state_str (self):
      return CS_ES_state(self.control_status)[1];
    def is_idle (self):
      return self.exec_state() == CS_ES_IDLE;
    def update_status (self,status,rqid=False):
      old_status = self.control_status;
      self.control_status = status;
      s = ['-'] * 8;
      s[0] = CS_ES_state(status)[2];
      if status&CS_STOP_BREAKPOINT:   s[0] = ">"+s[0];
      if status&CS_BREAKPOINT_SS:     s[1] = "b";
      if status&CS_BREAKPOINT:        s[1] = "B";
      if status&CS_ACTIVE:            s[2] = "A";
      if status&CS_PUBLISHING:        s[3] = "P";
      if status&CS_CACHED:            s[4] = "C";
      if status&CS_RETCACHE:          s[5] = "c";
      s[6] = CS_RES_map[status&CS_RES_MASK][0];
      s = ''.join(s);
      if not isinstance(rqid,bool):
        self.request_id = rqid;
      self.control_status_string = s;
      _dprint(6,"node",self.name,"update status %X"%(status,));
      self.emit(PYSIGNAL("status()"),(self,old_status));
    def update_state (self,state,event=None):
      try: self.breakpoint = state.breakpoint;
      except AttributeError: pass;
      self.update_status(state.control_status,state.get('request_id',None));
      _dprint(5,"node",self.name,"update state (event ",event,")");
      self.emit(PYSIGNAL("state()"),(self,state,event));
    # Adds a subscriber to node status changes
    def subscribe_status (self,callback):
      _dprint(4,"connecting status of node ",self.name," to ",callback);
      QObject.connect(self,PYSIGNAL("status()"),callback);
    # Adds a subscriber to node state changes
    def subscribe_state (self,callback):
      _dprint(4,"connecting state of node ",self.name," to ",callback);
      QObject.connect(self,PYSIGNAL("state()"),callback);
    def unsubscribe_status (self,callback):
      _dprint(4,"disconnecting status of node ",self.name," from ",callback);
      QObject.disconnect(self,PYSIGNAL("status()"),callback);
    # Adds a subscriber to node state changes
    def unsubscribe_state (self,callback):
      _dprint(4,"disconnecting state of node ",self.name," from ",callback);
      QObject.disconnect(self,PYSIGNAL("state()"),callback);

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
    iter_cstate   = iter(meqnl.control_status);
    self._nimap = {};
    self._namemap = {};
    self._classmap = {};
    # iterate over all nodes in list
    # (0,) is a special case of an empty list (see bug in DMI/DataField.cc)
    if meqnl.nodeindex != (0,):
      for ni in meqnl.nodeindex:
        # insert node into list (or use old one: may have been inserted below)
        node = self._nimap.setdefault(ni,self.Node(ni));
        node.name      = iter_name.next();
        node.classname = iter_class.next();
        node.update_status(iter_cstate.next());
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
    try: return len(self._nimap);
    except AttributeError: return 0;
  # helper method: selects name or nodeindex map depending on key type
  def _map_ (self,key):
    if not hasattr(self,'_namemap'):
      raise KeyError,"nodelist is empty";
    if isinstance(key,str):      return self._namemap;
    elif isinstance(key,int):    return self._nimap;
    else:                        raise TypeError,"invalid node key "+str(key);
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
def node_udi (node,suffix=None):
  try: (name,index) = (node.name,node.nodeindex);
  except AttributeError,KeyError: 
    node = nodelist[node];
    (name,index) = (node.name,node.nodeindex);
  udi = "/node/%s#%d"%(name,index);
  if suffix:
    udi += "/" + suffix;
  return udi;

_patt_Udi_NodeState = re.compile("^/node/([^#/]*)(#[0-9]+)?$");
def parse_node_udi (udi):
  match = _patt_Udi_NodeState.match(udi);
  if match is None:
    return (None,None);
  (name,ni) = match.groups();
  if ni is not None:
    ni = int(ni[1:]);
  return (name,ni);
  
def set_meqserver (mqs1):
  global _mqs;
  _mqs = weakref.proxy(mqs1);

def reclassify_nodestate (nodestate):
  nodestate.__class__ = NodeClass(nodestate['class']);
  
def nodeindex (node):
  if isinstance(node,int):
    return node;
  elif isinstance(node,str):
    return nodelist[node].nodeindex;
  else:
    return node.nodeindex;

def nodeobject (node):
  if isinstance(node,NodeList.Node):
    return node;
  else:
    return nodelist[nodeindex(node)];

def mqs ():
  mqs1 = _mqs or (callable(_mqs) and _mqs());
  if mqs1 is None:
    raise RuntimeError,"meqserver not initialized or not running";
  return mqs1;

# Adds a subscriber to node state changes
def subscribe_node_state (node,callback):
  nodelist[nodeindex(node)].subscribe_state(callback);

def request_node_state (node):
  ni = nodeindex(node);
  mqs().meq('Node.Get.State',srecord(nodeindex=ni),wait=False);
  
def set_node_breakpoint (node,bp=BP_ALL,oneshot=False):
  mqs().meq('Node.Set.Breakpoint',\
    srecord(nodeindex=nodeindex(node),breakpoint=bp,single_shot=oneshot,get_state=True),wait=False);

def clear_node_breakpoint (node,bp=BP_ALL,oneshot=False):
  mqs().meq('Node.Clear.Breakpoint',\
    srecord(nodeindex=nodeindex(node),breakpoint=bp,single_shot=oneshot,get_state=True),wait=False);

def set_node_state (node,**kwargs):
  ni = nodeindex(node);
  newstate = srecord(kwargs);
  mqs().meq('Node.Set.State',srecord(nodeindex=ni,get_state=True,state=newstate),wait=False);
  
def update_node_state (state,event):
  ni = state.nodeindex;
  _dprint(5,"updating state of node ",state.name);
  if nodelist:
    nodelist[ni].update_state(state,event);

def add_node_snapshot (state,event):
  ni = state.nodeindex;
  _dprint(5,"adding snapshot for node ",state.name);
  # update state
  try: node = nodelist[ni];
  except KeyError: pass;
  else: node.update_state(state,event);
  # get list of snapshots and filter it to eliminate dead refs
  sslist = filter(lambda s:s[0]() is not None,snapshots.get(ni,[]));
  if len(sslist) and sslist[-1][0]() == state:
    state.__nochange = True;
    return;
  sslist.append((weakref.ref(state),event,time.time()));
  snapshots[ni] = sslist;
  
def get_node_snapshots (node):
  ni = nodeindex(node);
  sslist0 = snapshots.get(ni,[]);
  # filter out dead refs, reset list if it changes
  sslist = filter(lambda s:s[0]() is not None,sslist0);
  if len(sslist) != len(sslist0):
    snapshots[ni] = sslist;
  return sslist;

# create global node list
snapshots = {};
nodelist = NodeList();

_mqs = None;
