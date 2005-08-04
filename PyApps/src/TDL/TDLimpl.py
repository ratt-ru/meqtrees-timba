from Timba import dmi
from Timba import utils
import Timba.TDL.Settings

import sys
import weakref
import gc
import traceback
import re
import os.path
import copy

_dbg = utils.verbosity(0,name='tdl');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class TDLError (RuntimeError):
  """Base class for TDL errors. Note that TDL errors are always raised 
  with 3 arguments:
    message,filename,location
  where location is either a line number, or a (line,column) tuple.
  Exception handlers below ensure that any other errors get their location 
  tagged onto their argument set.
  """;
  def __str__ (self):
    return ':'.join([self.__class__.__name__]+list(map(str,self.args)));

class NodeRedefinedError (TDLError):
  """this error is raised when a node is being redefined with a different 
  init-record""";
  pass;

class UninitializedNode (TDLError):
  """this error is raised when a node has not been initialized with an init-record""";
  pass;

class UnboundNode (TDLError):
  """this error is raised when a node definition has not been bound to a name""";
  pass;
  
class ChildError (TDLError):
  """this error is raised when a child is incorrectly specified""";
  pass;

class NodeDefError (TDLError):
  """this error is raised when a node is incorrectly defined""";
  pass;

class ExtraInfoError (TDLError):
  """this error is added after one of the "real" errors above to indicate
  additional information such as, e.g., "called from", "first defined here",
  etc.""";
  pass;

class CumulativeError (TDLError):
  """this exception is raised at resolve time when errors have been reported
  but deferred. Its args tuple is composed of exception objects.
  """;
  def __str__ (self):
    s = '';
    for n,err in enumerate(self.args):
      s += '\n [%3d] %s' % (n+1,str(err));
    return s;

class _NodeDef (object):
  """this represents a node definition, as returned by a node class call""";
  __slots__ = ("children","stepchildren","initrec","error","_class");
  
  class ChildList (list):
    """A ChildList is a list of (id,child) pairs. 
    'id' may be a child label, or an ordinal number.
    'child' may be a NodeStub, a string node name, a numeric constant, or
        something that resolves to a NodeDef.
    """;
    def __init__ (self,x=None):
      """A ChildList may be initialized from a dict, from a sequence,
      or from a single object.""";
      self.is_dict = isinstance(x,dict);
      if x is None:
        list.__init__(self);
      elif self.is_dict:
        list.__init__(self,x.iteritems());
      elif isinstance(x,(list,tuple)):
        list.__init__(self,enumerate(x));
      else:
        list.__init__(self,[(0,x)]);
      self._resolved = False;
    def resolve (self,scope):
      """Returns a 'resolved' list based on this list. A resolved list
      contains only valid NodeStubs. The scope argument is used to look
      up and create nodes.""";
      if self._resolved:
        return self;
      reslist = _NodeDef.ChildList();
      for (i,(ich,child)) in enumerate(self):
        _dprint(5,'checking child',i,ich,'=',child);
        if not isinstance(child,_NodeStub):
          if isinstance(child,str):        # child referenced by name? 
            try: child = scope.Repository()[child];
            except KeyError:
              raise ChildError,"child %s = %s not found" % (str(ich),child);
          elif isinstance(child,(complex,float)):
            child = scope.MakeConstant(child);
          elif isinstance(child,(bool,int,long)):
            child = scope.MakeConstant(float(child));
          else:
            # try to resolve child to a _NodeDef
            anonch = _NodeDef.resolve(child);
            if anonch is None:
              raise ChildError,"child %s has illegal type %s" % (str(ich),type(child).__name__);
            _dprint(4,'creating anon child',ich);
            child = anonch.autodefine(scope);
        reslist.append((ich,child));
      reslist.is_dict = self.is_dict;
      reslist._resolved = True;
      return reslist;
        
  def __init__ (self,pkgname,classname='',*childlist,**kw):
    """Creates a _NodeDef object for a node of the given package/classname.
    Children are built up from either the argument list, or the 'children'
    keyword (if both are supplied, an error is thrown), or from keywords of
    type '_NodeDef' or '_NodeStub', or set to None if no children are specified. 
    The initrec is built from the remaining keyword arguments, with the field
    class=pkgname+classname inserted as well.
    """;
    try:
      # an error def may be constructed with an exception opject
      if isinstance(pkgname,Exception):
        raise pkgname;
      # figure out children. May be specified as
      # (a) a 'children' keyword 
      # (b) an argument list (but not both a and b)
      # (c) keywords with values of type NodeDef or NodeStub
      try:
        children = kw.pop('children');
        if childlist: 
          raise ChildError,"children specified both by arguments and 'children' keyword";
      except KeyError:  # no 'children' keyword, case (b) or (c)
        if childlist: 
          children = childlist;
        else: # else see if some keyword arguments specify children-like objects
          children = dict([(key,val) for (key,val) in kw.iteritems()
                            if isinstance(val,(_NodeDef,_NodeStub)) ]);
          map(kw.pop,children.iterkeys());
      _dprint(3,"NodeDef",classname,"children are",children);
      self.children = self.ChildList(children);
      # now check for step_children:
      stepchildren = kw.pop('stepchildren',None);
      if isinstance(stepchildren,dict):
        raise ChildError,"'stepchildren' must be a list or a single node";
      self.stepchildren = self.ChildList(stepchildren);
      # create init-record 
      initrec = dmi.record(**kw);
      initrec['class'] = ''.join((pkgname,classname));
      self._class = classname;
      # ensure type of node_groups argument (so that strings are implicitly converted to hiids)
      groups = getattr(initrec,'node_groups',None);
      if groups is not None:
        initrec.node_groups = dmi.make_hiid_list(groups);
      self.initrec = initrec;
      self.error = None;
    except:
      # catch exceptions and produce an "error" def, to be reported later on
      self.children = self.initrec = None;
      (exctype,excvalue) = sys.exc_info()[:2];
      if len(excvalue.args) == 1:
        excvalue = exctype(excvalue.args[0],*_identifyCaller()[:2]);
      self.error = excvalue;
  
  def resolve (arg,recurse=5):
    """static method to resolve an argument to a _NodeDef object, or return None on error.
    This method implements some implicit ways to create a node:
      * by specifying a constant value
      * by specifying a node class (such as Meq.Parm) without arguments
      * by specifying anything callable that returns one of the above
    """;
    if isinstance(arg,_NodeDef):
      return arg;
    elif isinstance(arg,complex):
      return _Meq.Constant(value=arg);
    if isinstance(arg,(bool,int,long,float)):
      return _Meq.Constant(value=float(arg));
    if callable(arg) and recurse>0:
      return _NodeDef.resolve(arg(),recurse=recurse-1);
    return None;
  resolve = staticmethod(resolve);
  
  def autodefine (self,scope):
    """Auto-defines a stub from NodeDef. Name is generated
    automatically using classname, child names and child qualifiers."""
    # for starters, we need to resolve all children to NodeStubs
    self.children = self.children.resolve(scope);
    classname = self._class.lower();
    # create name as Class(child1,child2,...):qualifiers
    if self.children:
      # generate qualifier list
      quals = [];
      kwquals = {};
      for (ich,child) in self.children:
        _mergeQualifiers(quals,kwquals,child.quals,child.kwquals,uniq=True);
      basename = ','.join(map(lambda x:x[1].basename,self.children));
      basename = "%s(%s)" % (classname,basename);
      _dprint(4,"creating auto-name",basename,quals,kwquals);
      return scope[basename](*quals,**kwquals) << self;
    else:
      basename = scope.MakeUniqueName(classname);
      return scope[basename] << self;
    
  # define implicit arithmetic operators
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
    
def _mergeQualifiers (qual0,kwqual0,qual,kwqual,uniq=False):
  """Merges qualifiers qual,kwqual into qual0,kwqual0.
  If uniq=False, then the unnamed qualifier lists (qual0 and qual) are simply
  concatenated.
  If uniq=True, then the lists are merged (i.e. duplicates from qual are removed).
  Note that keyword qualifiers are always merged.
  """
  # add/merge unnamed qualifiers
  if uniq:
    qual0.extend([ q for q in qual if q not in qual0 ]);
  else:
    qual0.extend(qual);
  # always merge keyword qualifiers
  for kw,val in kwqual.iteritems():
    val0 = kwqual0.get(kw,[]);
    if not isinstance(val0,list):
      kwqual0[kw] = val0 = [val0];
    if not isinstance(val,list):
      val = [val];
    val0.extend([q for q in val if q not in val0]);
    kwqual0[kw] = val0;
  
class _NodeStub (object):
  """A NodeStub represents a node. Initially a stub is created with only
  a name. To make a fully-fledged node, a stub must be bound with a NodeDef 
  object via the bind() method, or the << operator. One bound, the 
  node stub is added to its repository.
  A stub may also be qualified via the () operator, this creates new node stubs
  with qualified names.
  """;
  slots = ( "name","scope","basename","quals","kwquals",
            "classname","parents","children","stepchildren",
            "_initrec","_caller","_debuginfo" );
  # The Parents class is used to manage a weakly-reffed dictionary of the node's parents
  # We redefine it as a class to implement __copy__ and __depcopy__ (which otherwise
  # crashes and burns on weakrefs)
  class Parents (weakref.WeakValueDictionary):
    def __copy__ (self):
      return self.__class__(self);
    def __deepcopy__ (self,memo):
      return self.__class__(self);
  
  def __init__ (self,fqname,basename,scope,*quals,**kwquals):
    _dprint(5,'creating node stub',fqname,basename,scope._name,quals,kwquals);
    self.name = fqname;
    self.scope = scope;
    self.basename = basename;
    self.quals = quals;
    self.kwquals = kwquals;
    self.classname = None;
    self.parents = self.Parents();
    self._initrec = None;         # uninitialized node
    # figure out source location from where node was defined.
    self._caller = _identifyCaller()[:2];
    self._debuginfo = "%s:%d" % (os.path.basename(self._caller[0]),self._caller[1]);
  def __copy__ (self):
    return self;
  def __deepcopy__ (self,memo):
    return self;
  def bind (self,arg,*args,**kwargs):
    """The bind() method is an alternative form of <<. If called with
    a str as the first argument, it is assumed to be a classname, and a 
    NodeDef is constructed using all the arguments. This NodeDef is bound 
    with the normal << call.
    Otherwise, a straight call to << with the first argument is done.
    """
    if isinstance(arg,str):
      arg = _NodeDef(arg,*args,**kwargs);
    return self << arg;
  def __lshift__ (self,arg):
    try:
      # resolve argument to a node spec. This will throw an exception on error
      nodedef = _NodeDef.resolve(arg);
      _dprint(4,self.name,self.quals,self.kwquals,'<<',nodedef);
      # can't resolve? error
      if nodedef is None:
        raise TypeError,"can't bind node name (operator <<) with argument of type "+type(arg).__name__;
      # error NodeDef? raise it as a proper exception
      if nodedef.error:
        raise nodedef.error;
      # resolve list of children in the nodedef to a list of node stubs
      children = nodedef.children.resolve(self.scope);
      stepchildren = nodedef.stepchildren.resolve(self.scope);
      # are we already initialized? If yes, check for exact match of initrec
      # and child list
      initrec = nodedef.initrec;
      if self.initialized():
        if self._initrec != initrec:
          _dprint(1,'old definition',self._initrec);
          _dprint(1,'new definition',initrec);
          for (f,val) in initrec.iteritems():
            _dprint(2,f,val,self._initrec[f],val == self._initrec[f]);
          raise NodeRedefinedError,"node %s already defined with different settings at %s"%(self.name,self._debuginfo);
        if children != self.children:
          raise NodeRedefinedError,"node %s already defined with different children at %s"%(self.name,self._debuginfo);
        if stepchildren != self.stepchildren:
          raise NodeRedefinedError,"node %s already defined with different children at %s"%(self.name,self._debuginfo);
      else:
        try: self.classname = getattr(initrec,'class');
        except AttributeError: 
          raise NodeDefError,"init record missing class field";
        _dprint(4,self.name,'children are',children);
        self.children = children;
        self.stepchildren = stepchildren;
        # add ourselves to parent list
        for child in self.children + self.stepchildren:
          child[1].parents[self.name] = self;
        # set init record and add ourselves to repository
        _dprint(5,'adding',self.name,'to repository with initrec',self._initrec);
        self.scope._repository[self.name] = self;
        self._initrec = initrec;
      return self;
    # any error is reported to the scope object for accumulation, we remain
    # uninitialized and return ourselves
    except:
      (exctype,excvalue) = sys.exc_info()[:2];
      args = excvalue.args;
      _dprint(0,"caught",exctype,args);
      if _dbg.verbose > 0:
        traceback.print_exc();
      if len(args) == 3:
        self.scope.Repository().add_error(exctype(*args));
      else:
        self.scope.Repository().add_error(exctype(args[0],*self._caller));
      return self;
  def __str__ (self):
    return "%s(%s)" % (self.name,self.classname);
  def initialized (self):
    return self._initrec is not None;
  def initrec (self):
    return self._initrec;
  def _qualify (self,quals,kwquals,merge):
    """Helper method for operator (), qadd() and qxfer() below.
    Creates a node based on this one, with additional qualifiers. If merge=True,
    merges the quals lists (i.e. skips non-unique items), otherwise appends lists.
    Returns a _NodeStub.""";
    (q,kw) = (list(self.quals),copy.deepcopy(self.kwquals));
    _mergeQualifiers(q,kw,quals,kwquals,uniq=merge);
    _dprint(4,"creating requalified node",self.basename,q,kw);
    fqname = qualifyName(self.basename,*q,**kw);
    try: 
      return self.scope._repository[fqname];
    except KeyError:
      return _NodeStub(fqname,self.basename,self.scope,*q,**kw);
  def __call__ (self,*quals,**kwquals):
    """Creates a node based on this one, with additional qualifiers. Extend, not merge
    is implied. Returns a _NodeStub.""";
    return self._qualify(quals,kwquals,False);
  def qadd (self,*nodes):
    """Adds qualifiers of listed nodes to qualifiers of this one.""";
    res = self;
    for n in nodes:
      res = res._qualify(n.quals,n.kwquals,False);
    return res;
  def qmerge (self,*nodes):
    """Merges qualifiers of listed nodes into qualifiers of this one.""";
    res = self;
    for n in nodes:
      res = res._qualify(n.quals,n.kwquals,True);
    return res;
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

class ClassGen (object):
  class _ClassStub (object):
    """_ClassStub represents a node class. When called with (), it returns
    a _NodeDef composed of its arguments."""
    __slots__ = ("_names");
    def __init__ (self,*names):
      self._names = names;
    def __call__ (self,*arg,**kw):
      """Calling a node class stub creates a _NodeDef object, with the
      _names passed in as the initial arguments.""";
      return _NodeDef(*(self._names+arg),**kw);
  def __init__ (self,prefix=''):
    self._prefix = prefix;
  def __getattr__ (self,name):
    """Accessing as, e.g., Meq.Nodeclass automatically inserts a _ClassStub
    attribute for 'NodeClass'.""";
    try: return object.__getattr__(self,name);
    except AttributeError: pass;
    _dprint(5,'creating class stub',self._prefix,name);
    stub = self._ClassStub(self._prefix,name);
    setattr(self,name,stub);
    return stub;
  def __getitem__ (self,name):
    return getattr(self,name);
  
class NodeGroup (dict):
  """This represents a group of nodes, such as, e.g., root nodes. The
  << operator is redefined to add nodes to the group.""";
  def __init__ (self,name=''):
    self.name = name;
  def __lshift__ (self,node):
    if not isinstance(node,_NodeStub):
      raise TypeError,"can't use NodeGroup operator << with argument of type "+type(node).__name__;
#       nodedef = _NodeDef.resolve(node);
#       _dprint(4,self.name,'<<',nodedef);
#       # can't resolve? error
#       if nodedef is None:
#         raise TypeError,"can't use NodeGroup operator << with argument of type "+type(node).__name__;
#       # error NodeDef? raise it as a proper exception
#       if nodedef.error:
#         raise nodedef.error;
#       node = nodedef.autodefine(self);
    dict.__setitem__(self,node.name,node);
    return node;
  def __contains__ (self,node):
    if isinstance(node,str):
      return dict.__contains__(self,node);
    try: return dict.__contains__(self,node.name);
    except AttributeError: return False;



class _NodeRepository (dict):
  def __init__ (self,testing=False):
    self._errors = [];
    self._testing = testing;

  def deleteOrphan (self,name):
    """recursively deletes orphaned branches""";
    node = self.get(name,None);
    if not node:  # already deleted
      return True;
    # unqualified name: delete from scope dictionary too
    if not ( node.quals or node.kwquals ):
      try: delattr(node.scope,node.name.split('::')[-1]);
      except AttributeError: pass;
    # get refcount of this node. True orphans will only have 2:
    # ourselves, and the local 'node' symbol. 
    refcount = len(gc.get_referrers(node));
    if refcount > 2:
      _dprint(3,"node",name,"has",refcount,"refs to it, skipping");
      if _dbg.verbose > 4:
        for r in gc.get_referrers(node):
          _dprint(5,'referrer:',type(r),getattr(r,'__name__',''),getattr(r,'f_lineno',''));
      if not node.parents:
        _dprint(3,"node",name,"is now a true root");
        self._roots[name] = node;
      return False;
    # get list of children names (don't wanna hold refs to them because
    # it interferes with the orphaning)
    children = map(lambda x:x[1].name,node.children) + map(lambda x:x[1].name,node.stepchildren);
    _dprint(3,"deleting orphan node",name);
    del self[name];
    node = None;
    if children:
      _dprint(3,"checking potentially orphaned children: ",children);
      for ch in children:
        self.deleteOrphan(ch);
    return True;
    
  def rootmap (self):
    try: return self._roots;
    except:
      raise TDLError,"Repository must be resolve()d to determine root nodes";
      
  def add_error (self,err):
    if self._testing:
      raise err;
    self._errors.append(err);
    if len(self._errors) > 100:
      raise CumulativeError(*self._errors);
      
  def get_errors (self):
    return self._errors;
      
  def resolve (self,cleanup_orphans):
    """resolves contents of repository. 
    If cleanup_orphans is True
    If a rootnodes NodeGroup is specified,
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
        # no parents? add to roots or to suspected orphans
        if not node.parents:
          if cleanup_orphans:
            orphans.append(name);
          else:
            self._roots[name] = node;
        for (i,ch) in node.children:
          if not ch.initialized():
            self.add_error(ChildError("child %s = %s is not initialized" % (str(i),ch.name),*node._caller));
            if node._caller != ch._caller:
              self.add_error(ExtraInfoError("     child referenced here",*ch._caller));
        # make copy of initrec if needed
        if hasattr(node._initrec,'name'):
          node._initrec = node._initrec.copy();
        # finalize the init-record by adding node name and children
        node._initrec.defined_at = node._debuginfo;
        node._initrec.name = node.name;
        if node.children.is_dict:
          children = dmi.record([(lbl,ch.name) for (lbl,ch) in node.children]);
        else:  # children as list
          children = [ ch.name for (lbl,ch) in node.children ];
        _dprint(5,'node',node.name,'children are',children);
        if children:
          node._initrec.children = children;
        if node.stepchildren:
          node._initrec.step_children = [ ch.name for (lbl,ch) in node.stepchildren ];
        ch = None; # relinquish ref to node, otherwise orphan collection is confused
    node = None;  # relinquish ref to node, otherwise orphan collection is confused
    # now check for accumulated errors
    if len(self._errors):
      _dprint(1,len(self._errors),"errors reported");
      raise CumulativeError(*self._errors);
    _dprint(1,"found",len(uninit),"uninitialized nodes");
    _dprint(1,"found",len(orphans) or len(self._roots),"roots");
    if uninit:
      _dprint(3,"uninitialized:",uninit);
      for name in uninit:
        del self[name];
    # clean up potential orphans: if deleteOrphan() returns False, then node is
    # not really an orphan, so we move it to the roots group instead
    len0 = len(self);
    if cleanup_orphans:
      map(self.deleteOrphan,orphans);
    _dprint(1,len0 - len(self),"orphans were deleted,",len(self._roots),"roots remain");
    # print roots in debug mode
    if _dbg.verbose > 3:
      for node in self._roots.itervalues():
        _printNode(node);
    _dprint(2,"root nodes:",self._roots.keys());
    _dprint(1,len(self),"total nodes in repository");
    if _dbg.verbose>4:
      _dprint(5,"nodes remaining:",self.keys());

class NodeScope (object):
  def __init__ (self,name=None,parent=None,test=False,*quals,**kwquals):
    if name is None:
      if quals:
        raise ValueError,"scope name must be set if qualifiers are used";
      self._name = None;
    else:
      self._name = qualifyName(name,*quals,**kwquals);
    # repository: only one parent repositorey is created
    if parent is None:
      self._repository = _NodeRepository(test);
      self._constants = weakref.WeakValueDictionary();
    else:
      self._repository = parent._repository;
      self._constants = parent._constants;
    # root nodes
    self._roots = None;
    # unique names
    self._uniqname_counters = {};
    # predefined root group to be used by TDL scripts
    object.__setattr__(self,'ROOT',NodeGroup());
    
  def __getattr__ (self,name):
    try: node = self.__dict__[name];
    except KeyError: 
      _dprint(5,'node',name,'not found, creating stub for it');
      if self._name is None:
        nodename = name;
      else:
        nodename = '::'.join((self._name,name));
      node = _NodeStub(nodename,nodename,self);
      _dprint(5,'inserting node stub',name,'into our attributes');
      self.__dict__[name] = node;
    return node;
  
  def __setattr__ (self,name,value):
    """you can directly assign a node definition to a scope. Names
    starting with "_" are treated as true attributes though.
    """;
    if name.startswith("_"):
      return object.__setattr__(self,name,value);
    self.__getattr__(name) << value;
    
  __getitem__ = __getattr__;
  __setitem__ = __setattr__;
  __contains__ = hasattr;
    
  def __lshift__ (self,arg):
    """<<ing a NodeDef into a scope creates a node with an auto-generated name""";
    nodedef = _NodeDef.resolve(arg);
    _dprint(4,self.name,'<<',nodedef);
    # can't resolve? error
    if nodedef is None:
      raise TypeError,"can't use NodeScope operator << with argument of type "+type(arg).__name__;
    # error NodeDef? raise it as a proper exception
    if nodedef.error:
      raise nodedef.error;
    return nodedef.autodefine(self);
  
  def GetErrors (self):
    return self._repository.get_errors();
    
  def MakeUniqueName (self,name):
    num = self._uniqname_counters.get(name,0);
    self._uniqname_counters[name] = num+1;
    return "%s%d" % (name,num);
  
  def MakeConstant (self,value):
    """make or reuse a Meq.Constant node with the given value""";
    node = self._constants.get(value,None);
    if node:
      return node;
    name = name0 = 'c%s' % (str(value),);
    # oops, name already defined for some reason, requalify with a counter
    count = 1;
    while name in self._repository:
      name = "%s%d" % (name0,count);
      count += 1;
    # create the node
    node = _NodeStub(name,name,self);
    # bind node, this also adds it to the repository
    node << _Meq.Constant(value=value);
    # add to map of constants 
    self._constants[value] = node;
    return node;
    
  def Repository (self):
    """Returns the repository""";
    return self._repository;
    
  def Subscope (self,name,*quals,**kwquals):
    """Creates a subscope of this scope, with optional qualifiers""";
    return NodeScope(name,self,*quals,**kwquals);
    
  def Resolve (self):
    """Resolves the node repository: checks tree, trims orphans, etc. Should be done as the final
    step of tree definition. If rootnodes is supplied (or if self.ROOT is populated), then root 
    nodes outside the specified group will be considered orphans and trimmed away.
    """;
    self._repository.resolve(not Timba.TDL.Settings.orphans_are_roots);
    
  def AllNodes (self):
    """returns the complete node repository. A node repository is essentially
    a dict, with node names as keys and node init-records as values.""";
    return self._repository;
    
  def RootNodes (self):
    """returns the root nodes of the node repository, as a dict with name keys
    and init-record values. Only available after a resolve() has been performed.
    """;
    return self._repository.rootmap();


# helper func to qualify a name
def qualifyName (name,*args,**kws):
  """Qualifies name by appending a dict of qualifiers to it, in the form
  of name:a1:a2:k1=v1:k2=v2, etc."""
  qqs0 = list(kws.iteritems());
  qqs0.sort();
  qqs = [];
  for (kw,val) in qqs0:
    if isinstance(val,list):
      val = ','.join(map(str,val));
    else:
      val = str(val);
    qqs.append('='.join((kw,val)));
  return ':'.join([name]+map(str,args)+qqs);

# used to generate Meq.Constants and such
_Meq = ClassGen('Meq');

_re_localfiles = re.compile('.*TDL/(TDLimpl|MeqClasses).py$');

# helper func to identify original caller of a function
def _identifyCaller (depth=3,skip_internals=True):
  """Identifies source location from which function was called.
  Normal depth is 3, corresponding to the caller of the caller of
  _identifyCaller(), but if skip_internals=True, this will additionally 
  skip over stack frames in TDLimpl.py itself.
  Returns triplet of (filename,line,funcname).
  """;
  stack = traceback.extract_stack();
  if skip_internals:
    for frame in stack[-depth::-1]:
      (filename,line,funcname,text) = frame;
      if not _re_localfiles.match(filename):
        break;
    # got to the end of the stack without finding a non-built-in? Fall back 
    # to starting frame
    if funcname.startswith('__'):
      (filename,line,funcname,text) = stack[-depth];
  else:
    (filename,line,funcname,text) = stack[-depth];
  return (filename,line,funcname);
  # return "%s:%d:%s" % (filename,line,funcname);
  
# helper func to pretty-print a node
def _printNode (node,name='',offset=0):
  header = (' ' * offset);
  if name:
    header += name+": ";
  header += str(node);
  print "%s: %.*s" % (header,78-len(header),str(node._initrec));
  for (ich,child) in node.children:
    _printNode(child,str(ich),offset+2);
    
