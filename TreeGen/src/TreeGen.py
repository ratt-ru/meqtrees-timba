
from Timba import dmi
from Timba import utils

import weakref
import traceback
import sets

_dbg = utils.verbosity(2,name='treegen');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class TreeGenError (RuntimeError):
  """base class for tree generation errors""";
  pass;

class NodeRedefinedError (TreeGenError):
  """this error is raised when a node is being redefined with a different 
  init-record""";
  pass;

class UninitializedNode (TreeGenError):
  """this error is raised when a node has not been initialized with an init-record""";
  pass;
  
class ChildError (TreeGenError):
  """this error is raised when a child is incorrectly specified""";
  pass;
  
class _NodeSpec (object):
  """this represents a node specification, as returned by a node class call""";
  __slots__ = ("children","initrec");
  def __init__ (self,children,initrec):
    (self.children,self.initrec) = (children,initrec);

def _identifyCaller (depth=3,skip_internals=True):
  """Identifies source location from which function was called.
  Normal depth is 3, corresponding to the caller of the caller of
  _identifyCaller(), but if skip_internals=True, this will also 
  skip over calls to built-ins.""";
  stack = traceback.extract_stack();
  if skip_internals:
    for frame in stack[-depth::-1]:
      (filename,line,funcname,text) = frame;
      if not funcname.startswith('__'):
        break;
    # got to the end of the stack without finding a non-built-in? Fall back 
    # to starting frame
    if funcname.startswith('__'):
      (filename,line,funcname,text) = stack[-depth];
  else:
    (filename,line,funcname,text) = stack[-depth];
  filename = filename.split('/')[-1];
  return "%s:%d:%s" % (filename,line,funcname);

class _NodeRepr (object):
  def __init__ (self,name,rep):
    self.name = name;
    self._initrec = None;         # uninitialized node
    self.classname = None;
    self.parents = weakref.WeakValueDictionary();
    self._repository = rep;
    # figure out source location from where node was defined.
    self._debuginfo = "%s(%s)" % (name,_identifyCaller());
  def __lshift__ (self,arg):
    if not isinstance(arg,_NodeSpec):
      raise TypeError,self._debuginfo+": incorrectly initialized";
    (children,initrec) = (arg.children,arg.initrec);
    if not self.initialized():
      try: self.classname = getattr(initrec,'class');
      except AttributeError: 
        raise ValueError,self._debuginfo+": init record missing class field";
      self._initrec = initrec;
      # normalize child list
      if children is None:
        children = [];
      elif isinstance(children,(_NodeRepr,_NodeSpec)):  # single child
        children = [(0,children)];
      elif isinstance(children,dict): # dict of children
        children = list(children.iteritems());
        self._child_dict = True;
      else:
        children = list(enumerate(children));
      _dprint(4,self.name,'children are',children);
      self.children = children;
      # resolve children, check their types and mark parents
      for (i,(ich,child)) in enumerate(self.children):
        _dprint(5,'checking child',i,ich,'=',child);
        if isinstance(child,_NodeSpec):      # anon child, create it
          _dprint(4,self.name,': creating anon child',ich);
          newname = "%s:%s" % (self.name,str(ich));
          childnode = _NodeRepr(newname,self._repository);
          childnode << child; 
          child = childnode;
          self.children[i] = (ich,child);
          self._repository[newname] = child;
        elif isinstance(child,str):        # child referenced by name? 
          try: child = self._repository[child];
          except KeyError:
            raise ChildError,"%s: child %s = %s not found" % (self._debuginfo,str(ich),child);
          self.children[i] = (ich,child);
        elif not isinstance(child,_NodeRepr):  # else node expected
          raise ChildError,"%s: child %s has illegal type %s" % (self._debuginfo,str(ich),str(type(child)));
        # add ourselves to parent list
        child.parents[self.name] = self;
    else: # already initialized, check for conflicts
      if self._initrec != initrec:
        raise NodeRedefinedError,self._debuginfo+": conflicting definition at "+_indentifyCaller();
    # return weakref to self
    return weakref.proxy(self);
  def initialized (self):
    return self._initrec is not None;
  def __str__ (self):
    return "%s(%s)" % (self.name,self.classname);
    
class _UnqualifiedNode (object):
  __slots__ = [ "name","_repository" ];
  def __init__ (self,name,rep):  
    self.name = name;
    self._repository = rep;
  def __call__ (self,*quals,**kwquals):
    fqname = qualifyName(self.name,*quals,**kwquals);
    node = self._repository.get(fqname,None);
    if node is not None:
      return node;
    node = self._repository[fqname] = _NodeRepr(fqname,self._repository);
    return node;

def qualifyName (name,*args,**kws):
  """Qualifies name by appending a dict of qualifiers to it, in the form
  of name:a1:a2:k1=v1:k2=v2, etc."""
  qqs = list(kws.iteritems());
  qqs.sort();
  qqs = map(lambda x: '='.join(map(str,x)),qqs);
  return ':'.join([name]+map(str,args)+qqs);

class Namespace (object):
  class _ClassRepr (object):
    """_ClassRepr represents a node class. When called with (), it returns
    a tuple of (children,initrec) composed of its arguments."""
    def __init__ (self,name):
      self._name = name;
    def __call__ (self,*childlist,**kw):
      """Calling a node class creates a (children,initrec) tuple.
      Children are built up from either the argument list of the children
      keyword (if both are supplied, an error is thrown), or None if no
      children are specified. The initrec is built from the additional 
      arguments, with 'class' inserted.
      """;
      children = kw.pop('children',None);
      initrec = dmi.record(**kw);
      initrec['class'] = self._name;
      if childlist:
        if children:
          raise ChildError,"children specified both by arguments and keyword at "+_identifyCaller();
        children = childlist;
      return _NodeSpec(children,initrec);
  def __init__ (self,prefix=''):
    self._prefix = prefix;
  def __getattr__ (self,name):
    """Accessing as, e.g., Meq.Nodeclass automatically inserts a _ClassRepr
    attribute for 'NodeClass'.""";
    try: return object.__getattr__(self,name);
    except AttributeError: pass;
    classrepr = self._ClassRepr(self._prefix+name);
    setattr(self,name,classrepr);
    return classrepr;
    
class NodeGroup (dict):
  """This represents a group of nodes, such as, e.g., root nodes. The
  << operator is redefined to add nodes to the group.""";
  def __init__ (self,name=''):
    self.name = name;
  def __lshift__ (self,node):
    if not isinstance(node,_NodeRepr):
      raise TypeError,"you may only add nodes to a node group with <<";
    dict.__setitem__(self,node.name,node);
    return node;
  def __contains__ (self,node):
    if isinstance(node,str):
      return dict.__contains__(self,node);
    try: return dict.__contains__(self,node.name);
    except AttributeError: return False;

def _printNode (node,name='',offset=0):
  header = (' ' * offset);
  if name:
    header += name+": ";
  header += str(node);
  print "%s: %.*s" % (header,78-len(header),str(node._initrec));
  for (ich,child) in node.children:
    _printNode(child,str(ich),offset+2);
    
class _NodeRepository (dict):
  def deleteOrphan (self,name):
    """recursively deletes orphaned branches""";
    node = self.pop(name,None);
    if not node:  # already deleted
      return 0;
    count = 1;
    # get list of children names (don't wanna hold refs to them because
    # it interferes with the orphaning)
    children = map(lambda x:x[1].name,node.children);
    del node;
    if children:
      _dprint(3,"deleted orphan node",name,", checking children: ",children);
      for ch in children:
        chnode = self.get(ch,None);
        if chnode is None:
          _dprint(3,"child ",ch,"already deleted");
        elif chnode.parents:
          _dprint(3,"child ",ch,"is not an orphan (yet)");
        else:
          del chnode;
          count += self.deleteOrphan(ch);
    else:
      _dprint(3,"deleted orphan node",name);
    return count;
  def resolve (self,rootnodes=NodeGroup()):
    uninit = [];
    orphans = [];
    for (name,node) in self.iteritems():
      if not node.initialized():
        uninit.append(name);
      else:
        if not node.parents:
          if not node in rootnodes:
            orphans.append(name);
        for (i,ch) in node.children:
          if not ch.initialized():
            raise ChildError,"%s: child %s = %s is not initialized" % (node._debuginfo,str(i),ch._debuginfo);
        # finalize the init-record by adding node name and children
        node._initrec.name = node.name;
        if getattr(node,'_child_dict',False): # children as record
          childrec = dmi.record();
          for (name,ch) in node.children:
            childrec[name] = ch.name;
          node._initrec.children = childrec;
        else:  # children as list
          node._initrec.children = map(lambda x:x[1].name,node.children);
    _dprint(1,"found",len(uninit),"uninitialized nodes");
    _dprint(1,"found",len(orphans),"orphan nodes");
    if uninit:
      _dprint(3,"uninitialized:",uninit);
      for name in uninit:
        del self[name];
    ndel = 0;
    if orphans:
      for o in orphans:
        ndel += self.deleteOrphan(o);
    if _dbg.verbose > 3:
      for node in rootnodes.itervalues():
        _printNode(node);
    _dprint(2,"root nodes",rootnodes.keys());
    _dprint(1,"found",len(rootnodes),"root nodes");
    _dprint(1,"found",len(orphans),"orphans and deleted",ndel,"recursively");
    _dprint(1,"found",len(uninit),"uninitialized nodes");
    _dprint(1,len(self),"total nodes created");
      
class NodeScope (object):
  def __init__ (self,name=None,parent=None,*quals,**kwquals):
    if name is None:
      if quals:
        raise ValueError,"scope name must be set if qualifiers are used";
      self._name = None;
    else:
      self._name = qualifyName(name,*quals,**kwquals);
    # repository: only one parent repositorey is created
    if parent is None:
      self._repository = _NodeRepository();
    else:
      self._repository = parent._repository;
      
  def __getattr__ (self,name):
    try: return object.__getattr__(self,name);
    except AttributeError: pass;
    if self._name is None:
      nodename = name;
    else:
      nodename = '/'.join((self._name,name));
    node = _UnqualifiedNode(nodename,self._repository);
    setattr(self,name,node);
    return node;
    
  def subscope (self,name,*quals,**kwquals):
    return NodeScope(name,self,*quals,**kwquals);
    
  def resolve (self,rootnodes=NodeGroup()):
    self._repository.resolve(rootnodes);

# test code follows
#
if __name__ == '__main__':
  # stations list
  STATIONS = range(1,15);
  # 3 sources
  SOURCES = ('a','b','c');
  
  #--- these are generated automatically from the station list
  # list of ifrs as station pairs: each entry is two indices, (s1,s2)
  IFRS   = [ (s1,s2) for s1 in STATIONS for s2 in STATIONS if s1<s2 ];
  # list of ifr strings of the form "s1-s2"
  QIFRS  = [ '-'.join(map(str,ifr)) for ifr in IFRS ];
  # combined list: each entry is ("s1-s2",s1,s2)
  QQIFRS = [ ('-'.join(map(str,ifr)),) + ifr for ifr in IFRS ];
  
  # namespace of all node classes
  Meq = Namespace('Meq');   
  # global node scope & repository
  nsglob = NodeScope();     
  # init some node groups
  ROOT = NodeGroup('root');
  SOLVERS = NodeGroup('solvers');
  
  #------- create nodes for instrumental model
  # some handy aliases
  ZERO = nsglob.zero() << Meq.Constant(value=0);
  UNITY = nsglob.unity() << Meq.Constant(value=1);
  
  PHASE_CENTER_RA  = nsglob.ra0() << Meq.Parm();
  PHASE_CENTER_DEC = nsglob.dec0() << Meq.Parm();
  
  STATION_UWV = {};
  STATION_POS = {};
  
  ARRAY_POS = nsglob.xyz0() << Meq.Composer(
    nsglob.x0() << Meq.Parm(),
    nsglob.y0() << Meq.Parm(),
    nsglob.z0() << Meq.Parm() );
    
  # create station-related nodes and branches
  for s in STATIONS:
    STATION_POS[s] = nsglob.xyz(s) << Meq.Composer(
      nsglob.x(s) << Meq.Parm(),
      nsglob.y(s) << Meq.Parm(),
      nsglob.z(s) << Meq.Parm() );
    STATION_UWV[s] = nsglob.stuwv(s) << Meq.UWV(children={
      'xyz': STATION_POS[s],
      'xyz0': ARRAY_POS,
      'ra': PHASE_CENTER_RA,
      'dec': PHASE_CENTER_DEC
    });
    # create per-source station gains
    for (q,src) in enumerate(SOURCES):
      nsglob.G(s,q=q) << Meq.Composer(
        nsglob.Gxx(s,q=q) << Meq.Polar(Meq.Parm(),Meq.Parm()), ZERO,
        ZERO, nsglob.Gyy(s,q=q) << Meq.Polar(Meq.Parm(),Meq.Parm()),
      dims=[2,2]);
    # alternative: single gain with no direction dependence
    # nsglob.G(s) << Meq.Composer(
    #    nsglob.Gxx(s) << Meq.Polar(Meq.Parm(),Meq.Parm()), ZERO,
    #    ZERO, nsglob.Gyy(s) << Meq.Polar(Meq.Parm(),Meq.Parm()),
    #  dims=[2,2]);
  
  # this function returns a per-station gain node, given a set of qualifiers
  def STATION_GAIN (s=s,q=q,**qual):  
    # **qual swallows any remaining qualifiers
    return nsglob.G(s,q=q);
    # note alternative for no direction dependence:
    # def STATION_GAIN (s=s,**qual):  
    #   return nsglob.G(s);
    
  #------- end of instrumental model
      
  #------- create model for unpolarized point source
  # References instrumental model: STATION_GAIN(s,**qual), STATION_UWV[s].
  # Returns unqualified predict node, should be qualified with ifr string.
  def makeUnpolarizedPointSource (ns,**qual):
    ns.lmn() << Meq.LMN(children={
        'ra':   ns.ra() << Meq.Parm(),
        'dec':  ns.dec() << Meq.Parm(),
        'ra0':  PHASE_CENTER_RA,
        'dec0': PHASE_CENTER_DEC
    });
    ns.stokes_i() << Meq.Parm();
    # create per-station term subtrees
    for s in STATIONS:
      ns.sdft(s) << Meq.MatrixMultiply(
        STATION_GAIN(s,**qual),
        Meq.StatPSDFT(ns.lmn(),STATION_UWV[s])
      );
    # create per-baseline predicters
    for (q,s1,s2) in QQIFRS:
      ns.predict(q) << Meq.Multiply(
          ns.stokes_i(),
          ns.dft(q) << Meq.DFT(ns.sdft(s1),ns.sdft(s2)),
      );
    return ns.predict;
    
  #------- create peeling unit
  # inputs: an unqualified input node, will be qualified with ifr string.
  # predicters: list of unqualified predict nodes, will be qualified with ifr string.
  # Returns unqualified output node, should be qualified with ifr string.
  def peelUnit (inputs,predicters,ns):
    for q in QIFRS:
      # create condeq branch
      ns.condeq(q) << Meq.Condeq(
        ns.measured(q) << Meq.PhaseShift(children=inputs(q)),
        ns.predicted(q) << Meq.Add(*[prd(q) for prd in predicters])
      );
      # create subtract branch
      ns.subtract(q) << Meq.Subtract(ns.measured(q),ns.predicted(q));
    # creates solver and sequencers
    ns.solver() << Meq.Solver(*[ns.condeq(q) for q in QIFRS]);
    for q in QIFRS:
      ns.reqseq(q) << Meq.ReqSeq(ns.solver(),ns.subtract(q));
    # returns root nodes of unit
    return ns.reqseq;
  
  # create source predictors, each in its own subscope
  predicter = {};
  for (q,src) in enumerate(SOURCES):
    predicter[q] = makeUnpolarizedPointSource(nsglob.subscope('predict',src),q=q);
  
  # create spigots
  for q in QIFRS:
    nsglob.spigot(q) << Meq.Spigot();
    
  # chain peel units, by connecting outputs to inputs. First input
  # is spigot.
  inputs = nsglob.spigot;
  for (q,src) in enumerate(SOURCES):
    ns_pu = nsglob.subscope('peelunit',q);
    inputs = peelUnit(inputs,predicter.values(),ns=ns_pu);
    SOLVERS << ns_pu.solver();
    
  # create sinks, connect them to output of last peel unit
  for q in QIFRS:
    ROOT << nsglob.sink(q) << Meq.Sink(inputs(q));
    
  # create data collectors (this simply shows off the use of arbitrary node
  # groupings)
  ROOT << nsglob.solver_collect() << Meq.DataCollect(*SOLVERS.values());
    
  # deliberately create an orphan branch. This checkes orphan collection.
  # this whole branch should go away, and so should the UNITY node, which
  # is not used anywhere
  nsglob.orphan() << Meq.Add(Meq.Const(value=0),UNITY,Meq.Add(UNITY,ZERO));

  # resolve all nodes
  nsglob.resolve(ROOT);
