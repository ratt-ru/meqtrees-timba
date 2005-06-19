from Timba import dmi
from Timba import utils

import weakref
import traceback
import sets

_dbg = utils.verbosity(0,name='tdl');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class TDLError (RuntimeError):
  """base class for TDL errors""";
  pass;

class NodeRedefinedError (TDLError):
  """this error is raised when a node is being redefined with a different 
  init-record""";
  pass;

class UninitializedNode (TDLError):
  """this error is raised when a node has not been initialized with an init-record""";
  pass;
  
class ChildError (TDLError):
  """this error is raised when a child is incorrectly specified""";
  pass;

class NodeDefError (TDLError):
  """this error is raised when a node is incorrectly defined""";
  pass;
  
class _NodeSpec (object):
  """this represents a node specification, as returned by a node class call""";
  __slots__ = ("children","initrec");
  def __init__ (self,children,initrec):
    (self.children,self.initrec) = (children,initrec);
  def resolve (arg,recurse=5):
    """static method to resolve an argument to a _NodeSpec object, or return None on error.
    This method implements some implicit ways to create a node:
      * by specifying a constant value
      * by specifying a node class (such as Meq.Parm) without arguments
      * by specifying anything callable that returns one of the above
    """;
    if isinstance(arg,_NodeSpec):
      return arg;
    if isinstance(arg,(complex,float)):
      return _Meq.Constant(value=arg);
    if isinstance(arg,(bool,int,long,float)):
      return _Meq.Constant(value=float(arg));
    if callable(arg) and recurse>0:
      return _NodeSpec.resolve(arg(),recurse=recurse-1);
    return None;
  resolve = staticmethod(resolve);
  # define implicit arithmetic
  def __add__ (self,other):
    return _Meq.Add(self,other);
  def __sub__ (self,other):
    return _Meq.Subtract(self,other);
  def __mul__ (self,other):
    return _Meq.Multiply(self,other);
  def __div__ (self,other):
    return _Meq.Divide(self,other);
  def __radd__ (self,other):
    return _Meq.Add(other,self);
  def __rsub__ (self,other):
    return _Meq.Subtract(other,self);
  def __rmul__ (self,other):
    return _Meq.Multiply(other,self);
  def __rdiv__ (self,other):
    return _Meq.Divide(other,self);
  
def _identifyCaller (depth=3,skip_internals=True):
  """Identifies source location from which function was called.
  Normal depth is 3, corresponding to the caller of the caller of
  _identifyCaller(), but if skip_internals=True, this will also 
  skip over calls to built-ins.""";
  stack = traceback.extract_stack();
  if skip_internals:
    for frame in stack[-depth::-1]:
      (filename,line,funcname,text) = frame;
      if not filename.endswith('TDLimpl.py'):
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
  def __init__ (self,name,scope,basename,quals,kwquals):
    self.name = name;
    self.scope = scope;
    self.basename = basename;
    self.quals = quals;
    self.kwquals = kwquals;
    self.classname = None;
    self.parents = weakref.WeakValueDictionary();
    self._initrec = None;         # uninitialized node
    # figure out source location from where node was defined.
    self._debuginfo = "%s(%s)" % (name,_identifyCaller());
  def __lshift__ (self,arg):
    # resolve argument to a node spec. This will throw an exception on error
    arg = _NodeSpec.resolve(arg);
    if arg is None:
      raise TypeError,self._debuginfo+": cannot << something of type "+type(arg).__name__;
    (children,initrec) = (arg.children,arg.initrec);
    if not self.initialized():
      try: self.classname = getattr(initrec,'class');
      except AttributeError: 
        raise ValueError,self._debuginfo+": init record missing class field";
      self._initrec = initrec;
      # normalize child list
      if children is None:
        children = [];
      elif isinstance(children,dict): # dict of children
        children = list(children.iteritems());
        self._child_dict = True;
      elif isinstance(children,(list,tuple)): # sequence of children
        children = list(enumerate(children));
      else: # single child converted to list anyway
        children = [(0,children)];
      _dprint(4,self.name,'children are',children);
      self.children = children;
      # resolve children, check their types and mark parents
      for (i,(ich,child)) in enumerate(self.children):
        _dprint(5,'checking child',i,ich,'=',child);
        if not isinstance(child,_NodeRepr):
          if isinstance(child,str):        # child referenced by name? 
            try: child = self.scope.Repository()[child];
            except KeyError:
              raise ChildError,"%s: child %s = %s not found" % (self._debuginfo,str(ich),child);
          elif isinstance(child,(complex,float)):
            child = self.scope.MakeConstant(child);
          elif isinstance(child,(bool,int,long,float)):
            child = self.scope.MakeConstant(float(child));
          else:
            # try to resolve child to a _NodeSpec
            anonch = _NodeSpec.resolve(child);
            if anonch is None:
              raise ChildError,"%s: child %s has illegal type %s" % (self._debuginfo,str(ich),type(child).__name__);
            _dprint(4,self.name,': creating anon child',ich);
            childnode = self('-'+str(ich));    # add extra "-n" qualifier to our own name to get child node
            child = childnode << anonch;
          self.children[i] = (ich,child);
        # add ourselves to parent list
        child.parents[self.name] = self;
    else: # already initialized, check for conflicts
      if self._initrec != initrec:
        _dprint(1,'old definition',self._initrec);
        _dprint(1,'new definition',initrec);
        for (f,val) in initrec.iteritems():
          _dprint(2,f,val,self._initrec[f],val == self._initrec[f]);
        raise NodeRedefinedError,self._debuginfo+": conflicting definition at "+_identifyCaller();
    # return weakref to self
    return weakref.proxy(self);
  def __str__ (self):
    return "%s(%s)" % (self.name,self.classname);
  def initialized (self):
    return self._initrec is not None;
  def initrec (self):
    return self._initrec;
  def __call__ (self,*quals,**kwquals):
    """Creates a node based on this one, with additional qualifiers. Returns a _NodeRepr.""";
    kw = self.kwquals;
    kw.update(kwquals);
    return self.scope[self.basename](*(self.quals + quals),**kw);
  def buddy (self,name,*quals,**kwquals):
    """Derives a node with a different basename and the same qualifier, plus (optionally) additional qualifiers. 
    Returns a _NodeRepr.""";
    kw = self.kwquals;
    kw.update(kwquals);
    return self.scope[name](*(self.quals + quals),**kw);
  # define implicit arithmetic
  def __add__ (self,other):
    return _Meq.Add(self,other);
  def __sub__ (self,other):
    return _Meq.Subtract(self,other);
  def __mul__ (self,other):
    return _Meq.Multiply(self,other);
  def __div__ (self,other):
    return _Meq.Divide(self,other);
  def __radd__ (self,other):
    return _Meq.Add(other,self);
  def __rsub__ (self,other):
    return _Meq.Subtract(other,self);
  def __rmul__ (self,other):
    return _Meq.Multiply(other,self);
  def __rdiv__ (self,other):
    return _Meq.Divide(other,self);
    
class ClassNamespace (object):
  class _ClassRepr (object):
    """_ClassRepr represents a node class. When called with (), it returns
    a tuple of (children,initrec) composed of its arguments."""
    def __init__ (self,name):
      self._name = name;
    def __call__ (self,*childlist,**kw):
      """Calling a node class creates a _NodeSpec object. See _make_nodespec()
      method below for details.""";
      return ClassNamespace._make_nodespec(self._name,childlist,kw);
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
  def _make_nodespec (classname,childlist,kw):
    """helper method to make a _Nodespec object, used by _ClassRepr above.
    Children are built up from either the argument list, or the 'children'
    keyword (if both are supplied, an error is thrown), or from keywords of
    type '_NodeSpec' or '_NodeRepr', or set to None if no children are specified. 
    The initrec is built from the remaining keyword arguments, with the field
    class=classname inserted as well.
    """;
    # figure out children
    children = kw.pop('children',None);
    if children:
      if childlist: raise ChildError,"children specified both by arguments and keyword at "+_identifyCaller();
    else:  # no children dict, use list if we got it
      if childlist: children = childlist;
      else: # else see if some keywords specify children
        children = {};
        for (key,val) in kw.iteritems():
          if isinstance(val,(_NodeSpec,_NodeRepr)):
            children[key] = val;
        # remove from keyword set if found any   
        if children:
          map(kw.pop,children.iterkeys());
        else:
          children = None;
    # create init-record 
    initrec = dmi.record(**kw);
    initrec['class'] = classname;
    # ensure type of node_groups argument (so that strings are implicitly converted to hiids)
    groups = getattr(initrec,'node_groups',None);
    if groups is not None:
      initrec.node_groups = dmi.make_hiid_list(groups);
    return _NodeSpec(children,initrec);
  _make_nodespec = staticmethod(_make_nodespec);
  
_Meq = ClassNamespace('Meq');
    
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
    
  def rootmap (self):
    try: return self._roots;
    except:
      raise TDLError,"Repository must be resolve()d to determine root nodes";
      
  def resolve (self,rootnodes=None):
    """resolves contents of repository. If a rootnodes NodeGroup is specified,
    then all orphan nodes not in this group will be automatically deleted,
    while orphans within the group will be collected in self._roots.
    If rootnodes is None, then all orphans will be collected in self._roots and
    NOT deleted.
    """;
    uninit = [];
    orphans = [];
    self._roots = {};
    for (name,node) in self.iteritems():
      if not node.initialized():
        uninit.append(name);
      else:
        if not node.parents:
          if rootnodes is None or node in rootnodes:
            self._roots[name] = node;
          else:
            orphans.append(name);
        for (i,ch) in node.children:
          if not ch.initialized():
            raise ChildError,"%s: child %s = %s is not initialized" % (node._debuginfo,str(i),ch._debuginfo);
        # finalize the init-record by adding node name and children
        node._initrec.name = node.name;
        if getattr(node,'_child_dict',False): # children as record
          children = dmi.record();
          for (name,ch) in node.children:
            children[name] = ch.name;
        else:  # children as list
          children = map(lambda x:x[1].name,node.children);
        if children:
          node._initrec.children = children;
    _dprint(1,"found",len(uninit),"uninitialized nodes");
    _dprint(1,"found",len(orphans),"orphan nodes");
    _dprint(1,"found",len(self._roots),"root nodes");
    if uninit:
      _dprint(3,"uninitialized:",uninit);
      for name in uninit:
        del self[name];
    ndel = 0;
    for o in orphans:
      ndel += self.deleteOrphan(o);
    # print roots in debug mode
    if _dbg.verbose > 3:
      for node in self._roots.itervalues():
        _printNode(node);
    _dprint(2,"root nodes:",self._roots.keys());
    _dprint(1,len(self),"total nodes in repository");

def qualifyName (name,*args,**kws):
  """Qualifies name by appending a dict of qualifiers to it, in the form
  of name:a1:a2:k1=v1:k2=v2, etc."""
  qqs = list(kws.iteritems());
  qqs.sort();
  qqs = map(lambda x: '='.join(map(str,x)),qqs);
  return ':'.join([name]+map(str,args)+qqs);

class NodeScope (object):
  class UnqualNode (object):
    """An UnqualNode is a placeholder object returned by 'ns.name'. Once qualified with the () operator
    (or initialized via <<), it becomes a fully-fledged _NodeRepr registered in the repository.""";
    __slots__ = [ "name","scope","_debuginfo" ];
    def __init__ (self,name,scope):  
      (self.name,self.scope) = (name,scope);
      self._debuginfo = "%s(%s)" % (name,_identifyCaller());
    def __call__ (self,*quals,**kwquals):
      return self.scope.QualifyNode(self.name,*quals,**kwquals);
    def __lshift__ (self,arg):
      arg = _NodeSpec.resolve(arg);
      if arg is None:
        raise TypeError,self._debuginfo+": cannot << something of type "+type(arg).__name__;
      # doing a << on an unqualified node implictly applies empty qualifiers to it. Which we do here, but
      # we must also replace the UnqualNode entry in out NodeScope with the qualified one in case
      # it is accessed later.
      node = self.scope.QualifyNode(self.name);
      self.scope.__dict__[self.name] = node << arg;
      return node;
      
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
      self._constants = weakref.WeakValueDictionary();
    else:
      self._repository = parent._repository;
      self._constants = parent._constants;
    # root nodes
    self._roots = None;
    # predefined root group to be used by TDL scripts
    self.ROOT = NodeGroup();
      
  def __getattr__ (self,name):
    try: return self.__dict__[name];
    except KeyError: pass;
    _dprint(5,'creating unqual node',name);
    if self._name is None:
      nodename = name;
    else:
      nodename = '/'.join((self._name,name));
    node = self.UnqualNode(nodename,self);
    _dprint(5,'inserting node',name,'into our attributes');
    self.__dict__[name] = node;
    return node;
  __getitem__ = __getattr__;
  
  def MakeConstant (self,value):
    """make or reuse a Meq.Constant node with the given value""";
    node = self._constants.get(value,None);
    if node:
      return node;
    name = name0 = qualifyName('c',value);
    # oops, name already defined for some reason, requalify with a counter
    count = 1;
    while name in self._repository:
      name = qualifyName(name0,count);
      count += 1;
    # create the node
    node = _NodeRepr(name,self,name,(),{});
    self._repository[name] = node;
    self._constants[value] = node;
    return node << _Meq.Constant(value=value);
    
  def QualifyNode (self,name,*quals,**kwquals):
    """Returns a _NodeRepr object corresponding to a qualified node.""";
    fqname = qualifyName(name,*quals,**kwquals);
    node = self._repository.get(fqname,None);
    if node is None:
      node = self._repository[fqname] = _NodeRepr(fqname,self,name,quals,kwquals);
    return node;
    
  def Repository (self):
    """Returns the repository""";
    return self._repository;
    
  def Subscope (self,name,*quals,**kwquals):
    """Creates a subscope of this scope, with optional qualifiers""";
    return NodeScope(name,self,*quals,**kwquals);
    
  def Resolve (self,rootnodes=None):
    """Resolves the node repository: checks tree, trims orphans, etc. Should be done as the final
    step of tree definition. If rootnodes is supplied (or if self.ROOT is populated), then root 
    nodes outside the specified group will be considered orphans and trimmed away.
    """;
    self._repository.resolve(rootnodes or self.ROOT or None);
    
  def AllNodes (self):
    """returns the complete node repository. A node repository is essentially
    a dict, with node names as keys and node init-records as values.""";
    return self._repository;
    
  def RootNodes (self):
    """returns the root nodes of the node repository, as a dict with name keys
    and init-record values. Only available after a resolve() has been performed.
    """;
    return self._repository.rootmap();

