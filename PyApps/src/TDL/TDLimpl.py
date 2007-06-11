#try:
#  import psyco
#  psyco.full();
#except:
#  pass;

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

# this regex is used to match "local" files during error processing. Stack frames
# within the local files will not be added to nested CalledFrom error lists
_re_localfiles = re.compile('.*TDL/(TDLimpl|MeqClasses).py$');

# name of file from which the node scope was created. Error tracebacks will
# be stopped once they hit this name. Initialized when a NodeRepository is
# created
_original_invocation_filename = None;

class TDLError (RuntimeError):
  """Base class for TDL errors.
  In order to be processed properly, errors may be raised with one or
  two arguments. The first argument is an error message, the second
  (optional) is a another error object (the allows multiple errors to
  be chained together and raised as one value).
  Optional attributes:
    filename,lineno: indicates error location.
    offset:          optional error column.
    tb: the exception traceback (as returned by traceback.extract_tb()). This
      will automatically be turned into a list of CalledFrom nested errors.
    next_error: chained error object, for throwing several exceptions at once
    nested_errors: list of additional nested error objects, usually describing the call
      stack where the error occurred. These will be placed in front of the
      CalledFrom nested errors.
  """;
  def __init__(self,message,next=None,nested=[],tb=None,filename=None,lineno=None,append_callstack=True):
    RuntimeError.__init__(self,message);
    self.next_error = next;
    # resolve traceback
    if tb:
      tb = list(tb);
    else:
      tb = Timba.utils.extract_stack();
    # pop "internal" frames from the traceback
    while tb and _re_localfiles.match(tb[-1][0]):
      tb.pop(-1);
    self.tb = tb;
    # put error location into object
    self.filename = filename or (tb and tb[-1][0]) or None;
    if lineno is None and tb:
      lineno = tb[-1][1];
    self.lineno = lineno;
    # init nested errors
    self.nested_errors = list(nested);
    # add CalledFrom chain
    if append_callstack:
      for (filename,lineno,funcname,text) in tb[-1::-1]:
        global _original_invocation_filename;
        # _original_invocation_filename refers to whoever is calling define_forest, so we stop the stack
        # when we reach that
        if filename == _original_invocation_filename:
          break;
        if (filename,lineno) != (self.filename,self.lineno):
          self.nested_errors.append(CalledFrom("called from "+filename,
                                        filename=filename,lineno=lineno,append_callstack=False));

  def __str__ (self):
    s = ':'.join([self.__class__.__name__]+list(map(str,self.args)));
    if self.filename is not None:
      s += "[%s:%d]" % (self.filename,self.lineno);
    if self.tb is not None:
      s += "[tb:%d]" % (len(self.tb),);
    # if self.next_error is not None:
    #   s += '\n' + str(self.next_error);
    return s;

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
  pass;

class NestedTDLError (TDLError):
  """one or more of these errors are added to error lists after one of the
  "real" errors above to indicate that it is a nested error""";
  pass;

class DefinedHere (NestedTDLError):
  """a nested error indicating where a node was first defined""";
  pass;

class NamedHere (NestedTDLError):
  """a nested error indicating where a node was first named""";
  pass;

class CalledFrom (NestedTDLError):
  """a nested error indicating where the offending code was called from""";
  pass;

class TooManyErrors(TDLError):
  """error indicating that too many errors have been reported""";
  pass;

class CumulativeError (RuntimeError):
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
      """A ChildList may be initialized from a dict, from a sequence (of
      children, or of (id,child) tuples), or from a single object.""";
      self.is_dict = isinstance(x,dict);
      if x is None:
        list.__init__(self);
      elif self.is_dict:
        list.__init__(self,x.iteritems());
      elif isinstance(x,(list,tuple)):
        # check if it is a sequence if duplets
        # no -- assume sequence of children
        if [ True for y in x if not isinstance(y,tuple) or len(y) != 2 ]:
          list.__init__(self,enumerate(x));
        else: # yes -- use directly, assume is a dict
          self.is_dict = True;
          list.__init__(self,x);
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
        if child is not None and not isinstance(child,_NodeStub):
          if isinstance(child,str):        # child referenced by name?
            try: child = scope.Repository()[child];
            except KeyError:
              raise ChildError,"child node specified by name '%s' not found" % child;
          elif isinstance(child,(complex,float)):
            child = scope.MakeConstant(child);
          elif isinstance(child,(bool,int,long)):
            child = scope.MakeConstant(float(child));
          else:
            # try to resolve child to a _NodeDef
            anonch = _NodeDef.resolve(child);
            if anonch is None:
              raise ChildError,"child %s has illegal type '%s'" % (str(ich),type(child).__name__);
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
      # make sure tags is a list or tuple
      tags = kw.get('tags',None);
      if tags is not None:
        if isinstance(tags,str):
          kw['tags'] = tags.split(" ");
        elif isinstance(tags,(list,tuple)):
          if filter(lambda tag:not isinstance(tag,str),tags):
            raise TypeError,"'tags' must be a string or a sequence of strings";
        else:
          raise TypeError,"'tags' must be a string or a sequence of strings";
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
      (exctype,excvalue,) = sys.exc_info()[:2];
      self.error = excvalue;
      if not hasattr(self.error,'tb'):
        setattr(self.error,'tb',Timba.utils.extract_stack(None));
      _dprint(1,'creating error def',self.error);

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
    elif isinstance(arg,(bool,int,long,float)):
      return _Meq.Constant(value=float(arg));
    elif callable(arg) and recurse>0:
      return _NodeDef.resolve(arg(),recurse=recurse-1);
    return None;
  resolve = staticmethod(resolve);

  def autodefine (self,scope):
    """Auto-defines a stub from NodeDef. Name is generated
    automatically using classname, child names and child qualifiers."""
    if self.error:
      raise self.error;
    # for starters, we need to resolve all children to NodeStubs
    self.children = self.children.resolve(scope);
    classname = self._class.lower();
    # create name as Class(child1,child2,...):qualifiers
    if self.children:
      # use the scope of the first child. If scopes differ, we'll append them as subscopes
      scope = self.children[0][1].scope;
      # generate qualifier list
      quals = [];
      kwquals = {};
      for (ich,child) in self.children:
        child_quals = list(child.quals);
        # if child (1+) comes from a different scope, then prepend its name and qualifiers
        if child.scope is not scope:
          child_quals = list(child.scope._quals) + child_quals;
          if child.scope._name != scope._name:
            child_quals.insert(0,child.scope._name);
        _mergeQualifiers(quals,kwquals,
           child_quals,child.kwquals,uniq=True);
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
  def __truediv__ (self,other):
    return _Meq.Divide(self,other);
  def __mod__ (self,other):
    return _Meq.FMod(self,other);
  def __radd__ (self,other):
    return _Meq.Add(other,self);
  def __rsub__ (self,other):
    return _Meq.Subtract(other,self);
  def __rmul__ (self,other):
    return _Meq.Multiply(other,self);
  def __rdiv__ (self,other):
    return _Meq.Divide(other,self);
  def __rtruediv__ (self,other):
    return _Meq.Divide(other,self);
  def __rmod__ (self,other):
    return _Meq.FMod(other,self);
  def __neg__ (self):
    return _Meq.Negate(self);
  def __abs__ (self):
    return _Meq.Abs(self);

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

def NodeType ():
  return _NodeStub;

def is_node (x):
  return isinstance(x,_NodeStub);

class _CallStack (object):
  """CallStack represents a call stack. It is initialized with a traceback
  object, and encapsulates information about the caller, etc.""";
  def __init__ (self,tb):
    """tb is a traceback object, such as returned by Timba.utils.extract_stack()
    or Timba.utils.nonportable_extract_stack()""";
    self._tb = tb;
    # strip off all "internal" stack frames
    while tb and _re_localfiles.match(tb[-1][0]):
      tb.pop(-1);
    if tb:
      self._caller = tb[-1][:2];
    else:
      self._caller = None,None;
  def tb (self):
    return self._tb;
  def caller (self):
    return self._caller;
  def filename (self):
    return self._caller[0];
  def lineno (self):
    return self._caller[1];
  def make_error (self,error_class,message,**kwargs):
    """Makes an error object of the given class, and includes traceback information.
    Any keyword arguments are passed to the error constructor""";
    return error_class(message,
              filename=self._caller[0],lineno=self._caller[1],tb=self._tb,**kwargs);
  def __eq__ (self,other):
    return self._tb == other._tb;
  def __ne__ (self,other):
    return self._tb != other._tb;

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
            "nodeindex",
            "_initrec","_name_stack","_bind_stack","_debuginfo","_basenode",
            "_must_define_stack","_must_define_by",
            "_search_cookie" );
  class Parents (weakref.WeakValueDictionary):
    """The Parents class is used to manage a weakly-reffed dictionary of the
    node's parents. We only redefine it as a class to implement __copy__
    and __depcopy__ (which otherwise crashes and burns on weakrefs)
    """;
    def __copy__ (self):
      return self.__class__(self);
    def __deepcopy__ (self,memo):
      return self.__class__(self);

  def __init__ (self,fqname,basename,scope,basenode,*quals,**kwquals):
    """Creates a NodeStub. This is usually called as a result of
    ns.name(...). fqname is the fully-qualified node name. Basename
    is the unqualified name. Scope is the parent scope object. Basenode is
    the node stub from which this one was derived (via qualifying, presumably),
    or None if node was not derived from anything.
    Quals and kwquals are the (user-supplied) qualifiers that were applied.
    """;
    _dprint(5,'creating node stub',fqname,basename,quals,kwquals,'in scope',scope.Description());
    self.name = fqname;
    self.basename = basename;
    self.scope = scope;
    self.quals = quals;
    self.kwquals = kwquals;
    self.classname = None;
    self.parents = self.Parents();
    self._basenode = basenode;
    self._initrec = None;         # uninitialized node
    # figure out source location from where node was defined.
    ## this used to say
    # self._deftb = Timba.utils.extract_stack(None,4);
    ## but this broke the mechanism used to identify where in 'user' code a node
    ## was initialized (because implicit arithmetic can cause a stack of deeper than
    ## 4 of internal calls.) On the other hand, removing the limit:
    # self._deftb = Timba.utils.extract_stack(None);
    # self._caller = _identifyCaller(stack=self._deftb,depth=2)[:2];
    ## causes compilation to be really slow, since extract_stack() is so slow.
    ## So now we use a slightly less portable, but hopefully faster version:
    tb = Timba.utils.nonportable_extract_stack(None);
    self._name_stack = _CallStack(tb);
    self._debuginfo = "%s:%d" % \
          (os.path.basename(self._name_stack.filename()),self._name_stack.lineno());
    self._must_define_stack = self._must_define_by = None;
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
  def __pow__ (self,arg):
    """The ** operator is an optional-bind: it binds a node with a
    definition, but only if the node is not already bound.""";
    if self.initialized():
      return self;
    return self << arg;
  def __lshift__ (self,arg):
    """The << operator binds a node with a definition""";
    tb = Timba.utils.nonportable_extract_stack(None);
    this_stack = _CallStack(tb);
    # Error handling: unexpected error will be caught by the except clause below,
    # which will append the traceback "tb" to them, and optionally a "NamedHere" error,
    # if the _name_stack set in the constructor is different from this_stack.
    # More elaborate errors will be added to the repository explicitly.
    try:
      # resolve argument to a node spec. This will throw an exception on error
      nodedef = _NodeDef.resolve(arg);
      _dprint(4,self.name,self.quals,self.kwquals,'<<',nodedef);
      # can't resolve? error
      if nodedef is None:
        traceback.print_stack();
        raise NodeDefError,"can't define node '%s' using an argument of type '%s'"%(self.name,type(arg).__name__);
      # error NodeDef? reraise for processing by except clause below
      if nodedef.error:
        raise nodedef.error;
      # resolve list of children in the nodedef to a list of node stubs
      children = nodedef.children.resolve(self.scope);
      stepchildren = nodedef.stepchildren.resolve(self.scope);
      # are we already initialized? If yes, check for exact match of initrec
      # and child list
      initrec = nodedef.initrec;
      if self.initialized():
        if initrec != self._initrec or \
              children != self.children or \
              stepchildren != self.stepchildren:
          _dprint(1,'old definition',self._initrec);
          _dprint(1,'new definition',initrec);
          for (f,val) in initrec.iteritems():
            _dprint(2,f,val,self._initrec[f],val == self._initrec[f]);
          # report error
          err = self._make_redefinition_error(this_stack,self._bind_stack,
                        "conflicting definition for node '%s'"%self.name);
          self.scope.Repository().add_error(err);
          return self;
        else: # else node initialized the same way, that's ok
          return self;
      else:  # else node not initialized
        try: self.classname = getattr(initrec,'class');
        except AttributeError:
          raise NodeDefError,"init record missing class field, this is clearly impossible";
        _dprint(4,self.name,'children are',children);
        self.children = children;
        self.stepchildren = stepchildren;
        # add ourselves to parent list
        for (lbl,child) in self.children + self.stepchildren:
          if child is not None:
            child.parents[self.name] = self;
        # set init record and add ourselves to repository
        # if creating sink or spigot, mark that we need a VisDataMux
        if self.classname == 'MeqSink':
          self.scope._repository._sinks.append(self);
        elif self.classname == 'MeqSpigot':
          self.scope._repository._spigots.append(self);
        # if creating a VisDataMux explicitly, mark that we have one
        elif self.classname == 'MeqVisDataMux':
          self.scope._repository._have_vdm = self;
        self._initrec = initrec;
      # success
      self._bind_stack = this_stack;
      return self;
    # any error is reported to the scope object for accumulation, we remain
    # uninitialized and return ourselves
    except:
      exctype,excvalue = sys.exc_info()[:2];
      traceback.print_exc();
      _dprint(0,"caught",exctype,excvalue);
      # if exception already contains a traceback attribute, use that, else
      # add our own traceback ('tb') which we made at the top of the function
      tb = getattr(excvalue,'tb',None) or tb;
      self.scope.Repository().add_error(excvalue,tb=tb);
      return self;
  def __str__ (self):
    return "%s(%s)" % (self.name,self.classname);
  def initialized (self):
    """Returns True if node stub is already initialized, False otherwise""";
    return self._initrec is not None;
  def _make_redefinition_error (self,callstack,bindstack,message):
    """helper function to form up 'node redefined' errors. Called both by lshift()
    above, and must_define_here() below.
    callstack is a _CallStack for the current caller.
    binstack is a _CallStack where the node was defined
    message is error message.
    """;
    if self._name_stack == bindstack:
      where = bindstack.make_error(DefinedHere,
                      "...node '%s' first named and defined here"%self.name,
                      nested=self._get_definition_chain());
    else:
      where = bindstack.make_error(DefinedHere,"...and defined here");
      where = self._name_stack.make_error(NamedHere,
                      "...node '%s' first named here"%self.name,
                      nested=self._get_definition_chain(),next=where);
    return callstack.make_error(NodeRedefinedError,message,next=where);
    
  def must_define_here (self,*by_whom):
    """If node stub is already initialized, checks that the _defined_where and _defined_by
    attributes match the caller and the argument list. Throws an exception on
    mismatch, else returns False.
    If node stub is not initialized, sets the _must_define_stack and _must_define_by attributes 
    from the caller and arguments, and returns True.
    Used for patterns like:
      node = ns.somename
      if node.must_define_here(self):
        node << ...
    This skips initialization if node is already defined, but does check that someone else
    doesn't try to use the same node name somewhere else.
    """;
    # get stack traceback and extract caller information
    tb = Timba.utils.nonportable_extract_stack(None);
    this_stack = _CallStack(tb);
    # three options:
    # option 1: must_define_here() already called before -- check for match, return True/False
    # depending on whether the node needs to be initialized.
    if self._must_define_stack:
      if self._must_define_stack.caller() != this_stack.caller():
        message = "node '%s' must be defined here"%self.name;
      elif self._must_define_by != by_whom:
        message = "node '%s' has been defined here, but with different arguments"%self.name;
      else:
        return self._initrec is None;
      # at this point we must report an error
      err = self._make_redefinition_error(this_stack,self._must_define_stack,message);
      self.scope.Repository().add_error(err);
      return False;
    # option 2: called for the first time, node already initialized elsewhere
    elif self._initrec is not None:
      err = self._make_redefinition_error(this_stack,self._bind_stack,
        message = "node '%s' must be defined here"%self.name);
      self.scope.Repository().add_error(err);
      return False;
    # option 3: called for the first time, node not initialized
    else:
      self._must_define_stack = this_stack;
      self._must_define_by = by_whom;
      return True;
    
  def initrec (self):
    return self._initrec;
  def num_children (self):
    return len(self.children);
  def num_parents (self):
    return len(self.parents);
  def set_options (self,**kw):
    if not self.initialized():
      raise NodeDefError,"set_options() on an uninitialized node";
    for name,value in kw.iteritems():
      self._initrec[name] = value;
  def _get_definition_chain (self):
    """helper method for error reporting. Returns a list of DefinedHere
    errors for all the basenodes of the current node. If no basenodes found, returns
    None""";
    chain = [];
    basenode = self._basenode;
    _dprint(5,"_get_definition_chain: basenode is",basenode and basenode.name);
    while basenode:
      chain.append(basenode._name_stack.make_error(NamedHere,
                      "possibly derived from node '%s'"%basenode.name,append_callstack=False));
      basenode = basenode._basenode;
      _dprint(5,"_get_definition_chain: basenode is",basenode and basenode.name);
    return chain;

  def _qualify (self,quals,kwquals,merge):
    """Helper method for operator (), qadd() and qmerge() below.
    Creates a node based on this one, with additional qualifiers. If merge=True,
    merges the quals lists (i.e. skips non-unique items), otherwise appends lists.
    Returns a _NodeStub.""";
    (q,kw) = (list(self.quals),dict(self.kwquals));
    _mergeQualifiers(q,kw,quals,kwquals,uniq=merge);
    fqname = self.scope.QualifyScopedName(self.basename,*q,**kw);
    _dprint(4,"creating requalified node",self.basename,q,kw,':',fqname);
    return self.scope._repository.nodeStub(fqname,self.basename,self.scope,self,*q,**kw);
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
  def Subscope (self,*quals,**kwquals):
    """turns node into a subscope. The node's name and qualifiers will be used as
    the subscope name. See NodeScope.Subscope() for details.""";
    quals = list(self.quals) + list(quals);
    kwq = dict(self.kwquals);
    kwq.update(kwquals);
    return self.scope.Subscope(self.basename,*quals,**kwq);
  def QualScope (self):
    """turns node into a QualScope. The node's qualifiers will be used
    to create the QualScope. See NodeScope.QualScope() for details.""";
    return self.scope.QualScope(*self.quals,**self.kwquals);
  # add_children(...,label=...)    adds children to node
  def add_children (self,*args):
    """adds children to node. Node stub must have been already initialized."""
    if not self.initialized():
      raise UninitializedNode,"node %s not initialized"%(self.name,);
    children = _NodeDef.ChildList(args).resolve(self.scope);
    for num,node in children:
      self.children.append((len(self.children),node));
    # add ourselves to parent list
    for num,child in children:
      if child is not None:
        child.parents[self.name] = self;
    return self;
  # add_stepchildren(...)    adds stepchildren to node
  def add_stepchildren (self,*args):
    """adds stepchildren to node. Node stub must have been already initialized."""
    if not self.initialized():
      raise UninitializedNode,"node %s not initialized"%(self.name,);
    stepchildren = _NodeDef.ChildList(args).resolve(self.scope);
    # add to stepchildren list
    for num,node in stepchildren:
      self.stepchildren.append((len(self.stepchildren),node));
    # add ourselves to parent list
    for num,child in stepchildren:
      child.parents[self.name] = self;
    return self;
  def family (self):
    """Returns the node's "family": i.e. all (initialized) nodes which have
    been derived from this one using any set of qualifiers.""";
    return self.scope.FindFamily(self);
  def search (self,no_family=False,*args,**kw):
    """Does a search operation on the node's entire family tree (i.e. all
    subtrees in the node's family.) Arguments are the same as to
    NodeScope.Search()""";
    if no_family:
      subtree = [ self ];
    else:
      subtree = self.family();
    return self.scope.Search(subtree=subtree,*args,**kw);
  # define implicit arithmetic
  def __add__ (self,other):
    return _Meq.Add(self,other);
  def __sub__ (self,other):
    return _Meq.Subtract(self,other);
  def __mul__ (self,other):
    return _Meq.Multiply(self,other);
  def __div__ (self,other):
    return _Meq.Divide(self,other);
  def __truediv__ (self,other):
    return _Meq.Divide(self,other);
  def __mod__ (self,other):
    return _Meq.FMod(self,other);
  def __radd__ (self,other):
    return _Meq.Add(other,self);
  def __rsub__ (self,other):
    return _Meq.Subtract(other,self);
  def __rmul__ (self,other):
    return _Meq.Multiply(other,self);
  def __rdiv__ (self,other):
    return _Meq.Divide(other,self);
  def __rtruediv__ (self,other):
    return _Meq.Divide(other,self);
  def __rmod__ (self,other):
    return _Meq.FMod(other,self);
  def __neg__ (self):
    return _Meq.Negate(self);
  def __abs__ (self):
    return _Meq.Abs(self);

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

_MODULE_FILENAME = Timba.utils.extract_stack()[-1][0];
_MODULE_DIRNAME = os.path.dirname(_MODULE_FILENAME);

class _NodeRepository (dict):
  def __init__ (self,root_scope,testing=False,caller_filename=None):
    """initializes repository.
    If testing=True, errors will be thrown immediately rather than accumulated.
    caller_filename specifies the creator of the repository. This is used
    in reporting error tracebacks -- they are only unrolled up to the caller
    filename. If not specified, it is extracted from the stack.
    """;
    self._root_scope = root_scope;
    self._errors = [];
    self._testing = testing;
    # determine original invocation filename
    global _original_invocation_filename;
    if not _original_invocation_filename:
      for (filename,lineno,funcname,text) in Timba.utils.extract_stack()[-2::-1]:
        if filename != _MODULE_FILENAME:
          _original_invocation_filename = filename;
          break;
    # other state
    self._sinks = [];
    self._spigots = [];
    self._have_vdm = None;
    # used during recursive searches
    self._search_cookie = 0;

  def nodeStub (self,name,*args,**kwargs):
    """If the named node stub exists in the repository, returns it.
    Else creates a new _NodeStub with the given arguments, adds it to the repository,
    and returns it.
    """;
    try:
      return self[name];
    except KeyError:
      nodestub = self[name] = _NodeStub(name,*args,**kwargs);
      return nodestub;

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
    _dprint(3,"deleting orphan node",name);
    # get list of children names (don't wanna hold refs to them because
    # it interferes with the orphaning)
    children = map(lambda x:x[1] and x[1].name,node.children) + map(lambda x:x[1] and x[1].name,node.stepchildren);
    del self[name];
    node = None;
    if children:
      _dprint(3,"checking potentially orphaned children: ",children);
      for ch in children:
        if ch:
          self.deleteOrphan(ch);
    return True;

  def rootmap (self):
    try: return self._roots;
    except:
      raise TDLError,"Repository must be resolve()d to determine root nodes";

  def add_error (self,err,tb=None,error_limit=100):
    """adds an error object to internal error list.
    If error_limit is not None, raises exception if the length of the error
    list exceeds error_limit.
    The object is augumented with location information (err.filename, err.lineno)
    as follows:
      * if err.filename and err.lineno exist, they are left as-is
      * otherwise, filename and lineno is extracted from tb, err.tb or
        Timba.utils.extract_stack() (in that order) and placed into err.
    Then, the traceback (tb or err.tb or Timba.utils.extract_stack()) is
    processed, and all stack frames leading up to the error are added
    to the list as CalledFrom() errors.
    Note that the stack traceback is trimmed as follows:
      * frames from bottom up to and including our caller_filename (see above).
      * consecutive frames from the top of the stack that belong to
        this module here
      (NB: the old behaviour was:
          * consecutive frames from the top of the stack that belong to files in
            the same directory as ours
       but this led to some confusing error messages so I changed it).
    Hopefully, this leaves a stack list with only 'user code' frames in it.
    Finally, if err.next_error is defined, add_error() is called on it
    recursively.
    """;
    # determine error location
    tb = tb or getattr(err,'tb',None) or Timba.utils.extract_stack();
    _dprint(1,'error',err,'tb',len(tb));
    _dprint(2,'traceback',tb);
    # trim our own frames from top of stack
    # while tb and os.path.dirname(tb[-1][0]) == _MODULE_DIRNAME:
    while tb and _re_localfiles.match(tb[-1][0]):
      tb.pop(-1);
    # put error location into object
    filename = getattr(err,'filename',None);
    lineno = getattr(err,'lineno',None);
    if not (filename and lineno is not None):
      _dprint(2,'no error information, setting from traceback');
      if tb:
        filename,lineno = tb[-1][:2]
      setattr(err,'filename',filename);
      setattr(err,'lineno',lineno);
    setattr(err,'tb',tb);
    _dprint(1,'error location resolved:',filename,lineno);
    # in test mode, raise error immediately
    if self._testing:
      raise err;
    # add to list
    self._errors.append(err);
    # add nested traceback, if not already present
    if not hasattr(err,'nested_errors'):
      setattr(err,'nested_errors',[]);
      for (filename1,lineno1,funcname,text) in tb[-1::-1]:
        _dprint(2,'next traceback frame',filename1,lineno1);
        global _original_invocation_filename;
        if filename1 == _original_invocation_filename:
          break;
        if (filename1,lineno1) != (filename,lineno):
          err.nested_errors.append(CalledFrom("called from "+filename1,
                                     filename=filename1,lineno=lineno1,append_callstack=False));
    # add a chained error if appropriate
    next = getattr(err,'next_error',None);
    if next:
      self.add_error(next);
    # raise cumulative error if we get too many
    if error_limit is not None and len(self._errors) >= error_limit:
      self._errors.append(TooManyErrors("too many errors, giving up",
                                        filename=filename,lineno=lineno,append_callstack=False));
      raise CumulativeError(*self._errors);

  def get_errors (self):
    return self._errors;

  def _make_OR_conditional (arg,argname):
    """helper function to make a OR-conditional from an argument.
    The argument can be either boolean false (corresponding to an
    always-true conditional), a string, or a sequence of strings giving
    a regex. Returns a callable conditional
    """;
    if not arg:
      return lambda x:True;
    elif isinstance(arg,str):
      return re.compile(arg+'$').match;
    else:
      raise TypeError,("%s argument must be a a string, or None"%argname);
  _make_OR_conditional = staticmethod(_make_OR_conditional);

  def search (self,return_names=False,subtree=None,name=None,tags=None,class_name=None):
    """Searches repository for nodes matching the specified criteria.
    If subtree is None, searches entire repository, else searches
    the subtree rooted at the given node or list of nodes.
    name and class_name are strings.
    tags may be a string or a list of strings.
    All strings may contain wildcards, and will be interpreted as regexes.
    If return_names is true, returns node names, else returns node objects.
    """;
    # make OR-conditionals for names and classnames
    name_conditional = self._make_OR_conditional(name,"find: 'name'");
    class_conditional = self._make_OR_conditional(class_name,"find: 'class_name'");
    # make a list of tag conditonals
    tag_conds = [];
    if tags:
      if isinstance(tags,str):
        tags = tags.split(" ");
      for tag in tags:
        if not isinstance(tag,str):
          raise TypeError,"find: 'tags' argument must be a string, or a list of strings, or None";
        tag_conds.append(re.compile(tag).match);
    # create search function
    def search_condition (node):
      # check if initialized
      if node._initrec is None:
        return False;
      # check class match
      if not class_conditional(node.classname):
        return False;
      # no tag conditionals, we have a match
      if not tag_conds:
        return True;
      # else must have a matching tag for every tag in list
      node_tags = node._initrec.get('tags',[]);
      if not node_tags:
        return False;
      for cond in tag_conds:
        for t in node_tags:
          if isinstance(t,str) and cond(t):
            break;  # found, break and go to next condition
        # no node tag found for this conditon
        else:
          return False;
      return True;
    # if no subtree specified, search whole repository
    if subtree is None:
      if return_names:
        return [ name for name,node in self.iteritems()
                 if name_conditional(name) and search_condition(node) ];
      else:
        return [ node for name,node in self.iteritems()
                 if name_conditional(name) and search_condition(node) ];
    # else search subtree rooted at 'subtree'
    else:
      if is_node(subtree):
        subtree = [ subtree ];
      elif not isinstance(subtree,(list,tuple)):
        raise TypeError,"find: 'subtree' argument must be a node or a list of nodes";
      self._search_cookie += 1;
      # Define function to recursively search node and its children.
      # A list of matching nodes is returned.
      # We use search_cookie to mark branches that have already been searched.
      def recursive_find (result,node):
        if getattr(node,'_search_cookie',None) != self._search_cookie:
          node._search_cookie = self._search_cookie;
          if node._initrec is not None:
            if name_conditional(node.name) and search_condition(node):
              result.append(node);
            if node.children:
              for label,child in node.children:
                recursive_find(result,child);
        return result;
      # now do the search
      found = [];
      for node in subtree:
        recursive_find(found,node);
      # make list of names if needed
      if return_names:
        return [ node.name for node in found ];
      else:
        return found;

  def find_node_family (self,name_prefix):
    """finds the node "family" with the given name prefix:
    i.e. all nodes that are initialized, and whose name is "name_prefix"
    or "name_prefix:*" """;
    regex = re.compile(name_prefix+"(:.*)?$").match;
    return [ node for name,node in self.iteritems() \
                  if regex(name) and node._initrec is not None ];

  def resolve (self,cleanup_orphans):
    """resolves contents of repository.
    cleanup_orphans: If True, then all orphan nodes are deleted.
                     If False, all orphans will be treated as root nodes.
    This will also create a VisDataMux as needed.
    """;
    uninit = [];
    orphans = [];
    self._roots = {};
    # create mux if needed.
    if self._sinks or self._spigots:
      if not self._have_vdm:
        self._have_vdm = self._root_scope.VisDataMux << \
          _Meq.VisDataMux(children={'pre':None,'post':None,'start':None});
      # now assign sinks and spigots to vdm, unless they already have a
      # vdm parent
      self._have_vdm.add_children(*[ node for node in self._sinks
        if 'MeqVisDataMux' not in [ p.classname for p in node.parents.itervalues() ] ]);
      self._have_vdm.add_stepchildren(*[ node for node in self._spigots
        if 'MeqVisDataMux' not in [ p.classname for p in node.parents.itervalues() ] ]);
    else: # no vdm needed. So release ref to it even if explicitly created,
      # to ensure it is orphaned or kept as needed elsewhere.
      self._have_vdm = None;
    # now go through node list, weed out uninitialized nodes, finalize
    # parents and children, etc.
    current_nodeindex = 1;
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
          if ch is not None and not ch.initialized():
            self.add_error(
              ch._name_stack.make_error(UninitializedNode,
                                "node '%s' not initialized"%ch.name,
                                 nested=ch._get_definition_chain()));
            if node._name_stack != ch._name_stack:
              self.add_error(node._name_stack.make_error(UninitializedNode,
                                "...node '%s' used in this context"%ch.name));
        # make copy of initrec if needed
        if hasattr(node._initrec,'name'):
          node._initrec = node._initrec.copy();
        # finalize the init-record by adding node name and children
        node.nodeindex = node._initrec.nodeindex = current_nodeindex;
        current_nodeindex += 1;
        node._initrec.node_description = ':'.join((name,node.classname,node._debuginfo));
        node._initrec.name = node.name;\
        _dprint(3,'checked node',node.name,'nodeindex',node.nodeindex);
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
    # now that all nodeindices have been assigned, do another loop to resolve
    # the children specifications and replace them with node indices
    for node in self.itervalues():
      if node.children.is_dict:
        children = dmi.record([(label,getattr(child,'nodeindex',-1))
                                  for label,child in node.children]);
      else:  # children as list
        children = [ getattr(child,'nodeindex',-1) for label,child in node.children ];
      _dprint(5,'node',node.name,'child nodeindices are',children);
      if children:
        node._initrec.children = children;
      if node.stepchildren:
        node._initrec.step_children = [ child.nodeindex for label,child in node.stepchildren ];
    # print roots in debug mode
    if _dbg.verbose > 3:
      for node in self._roots.itervalues():
        _printNode(node);
    _dprint(2,"root nodes:",self._roots.keys());
    _dprint(1,len(self),"total nodes in repository");
    if _dbg.verbose>4:
      _dprint(5,"nodes remaining:",self.keys());

class NodeScope (object):
  def __init__ (self,name=None,parent=None,test=False,quals=[],kwquals={}):
    """Creates a NodeScope.
    If 'name' is not None, this is a subscope. The name will then be added as a prefix to
    all nodes created within this scope.
    'parent' is the parent node scope. If None, then this is the global node scope. Normally,
    only one global node scope may exist; this is created before running the TDL script.
    'test' should normally be False. If True, the script is being run in test mode.
    'quals' and 'kwquals' are optional 'scope qualifiers'. These will be applied before
    node qualifiers within QualifyScopedName.
    """;
    self._name = name;
    self._quals = list(quals) + NodeScope._flatten_keyword_quals(kwquals);
    # repository: only one parent repository is created
    if parent is None:
      self._globalscope = self;
      self._repository = _NodeRepository(self,test);
      self._constants = weakref.WeakValueDictionary();
      # predefined root group to be used by TDL scripts
      object.__setattr__(self,'ROOT',NodeGroup());
    else:
      self._globalscope = parent._globalscope;
      self._repository = parent._repository;
      self._constants = parent._constants;
      object.__setattr__(self,'ROOT',parent.ROOT);
    # unique names
    self._uniqname_counters = {};

  def Description (self):
    """returns description of scope""";
    desc = self._name or 'GLOBAL';
    if self._quals:
      desc = "%s(%s)" % (desc,NodeScope._apply_qualifiers('',self._quals));
    return desc;

  def QualifyScopedName (self,name,*quals,**kwquals):
    """Returns a fully-qualified name for the given basename and set of
    qualifiers. The default behaviour is to add our name prefix, then apply the
    scope's qualifiers, then the supplied qualifiers. Subclasses may override this."""
    name = str(name);
    if self._name:
      name = '::'.join((self._name,name));
    name = NodeScope._apply_qualifiers(name,self._quals);
    return NodeScope._apply_qualifiers(name,quals,kwquals);

  def _resolve_to_string (value):
    """helper method, resolves a value to a string for qualification purposes.
    If value has a 'name' attribute, uses that.
    If value is a list or tuple, recursively resolves the elements and concatenates them
    with ','. All else failing, uses plain str.
    """;
    name = getattr(value,'name',None);
    if isinstance(name,str):
      return name;
    if isinstance(value,(list,tuple)):
      return ','.join(map(NodeScope._resolve_to_string,value));
    return str(value);
  _resolve_to_string = staticmethod(_resolve_to_string);

  def _flatten_keyword_quals (kwquals):
    """converts a dict (presumably, of keyword qualifiers) into a list of
    "key=value" strings."""
    return [ "=".join((str(key),NodeScope._resolve_to_string(value)))
             for key,value in kwquals.iteritems() ];
  _flatten_keyword_quals = staticmethod(_flatten_keyword_quals);

  def _apply_qualifiers (name,quals=[],kwquals={}):
    """Qualifies a name by appending qualifiers to it, in the form
    of name:a1:a2:k1=v1:k2=v2, etc."""
    return ':'.join([str(name)]+
                     map(NodeScope._resolve_to_string,quals)+
                     NodeScope._flatten_keyword_quals(kwquals));
  _apply_qualifiers = staticmethod(_apply_qualifiers);

  def Subscope (self,name,*quals,**kwquals):
    """Creates a subscope based on this scope, with name and qualifiers.
    A subscope adds a prefix to each node name created within it, separated
    from the node name with '::'. The prefix may include qualifiers. For example,
      ns1 = ns.Subscope("foo",1,x=2)
      ns1.a(3) << 1
      ns2 = ns1.Subscope("bar",y=4)
      ns2.b(5) << 1
    will create nodes named "foo:1:x=2::a:3" and "foo:1:x=2::bar:y=4::b:5"
    """;
    return NodeScope(self.QualifyScopedName(name,*quals,**kwquals),parent=self,test=False);

  def QualScope (self,*quals,**kwquals):
    """Creates a qualscope of this scope, with name and qualifiers.
    A qualscope prepends extra qualifiers to each node name created within it. For example,
      ns1 = ns.QualScope("foo",1,x=2)
      ns1.a(3,y=4) << 1
    will create a node named "a:1:x=2:3:y=4"
    """;
    qq = self._quals + list(quals) + NodeScope._flatten_keyword_quals(kwquals);
    return NodeScope(self._name,parent=self,test=False,quals=qq);

  def __call__ (self,*quals,**kwquals):
    """Using () on a NodeScope is equivalent to calling ns.QualScope() with the same
    arguments.""";
    return self.QualScope(*quals,**kwquals);

  def __getattr__ (self,name):
    try: node = self.__dict__[name];
    except KeyError:
      _dprint(5,'node',name,'not found, creating stub for it');
      fqname = self.QualifyScopedName(name);
      node = self._repository.nodeStub(fqname,name,self,None);
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

  def AddError (self,*args,**kwargs):
    return self._repository.add_error(*args,**kwargs);

  def MakeUniqueName (self,name):
    num = self._uniqname_counters.get(name,0);
    self._uniqname_counters[name] = num+1;
    if num:
      return "(%s)%d" % (name,num);
    else:
      return "(%s)" % (name,);

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
    node = self._repository.nodeStub(name,name,self._globalscope,None);
    # bind node, this also adds it to the repository
    node << _Meq.Constant(value=value);
    # add to map of constants
    self._constants[value] = node;
    return node;

  def Search (self,*args,**kw):
    return self._repository.search(*args,**kw);

  def FindFamily (self,node):
    if isinstance(node,str):
      name = node;
    elif is_node(node):
      name = node.name;
    else:
      raise TypeError,"FindFamily: 'node' argument must be a node or a node name";
    return self._repository.find_node_family(name);

  def Repository (self):
    """Returns the repository""";
    return self._repository;

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


# used to generate Meq.Constants and such
_Meq = ClassGen('Meq');


# helper func to identify original caller of a function
def _identifyCaller (depth=3,skip_internals=True,stack=None):
  """Identifies source location from which function was called.
  Normal depth is 3, corresponding to the caller of the caller of
  _identifyCaller(), but if skip_internals=True, this will additionally
  skip over internal methods (which are supposed to start with __).
  Returns triplet of (filename,line,funcname).
  """;
  stack = stack or Timba.utils.extract_stack();
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

def _fastIdentifyCaller (depth=2,skip_internals=True):
  """Identifies source location from which function was called.
  Normal depth is 2, corresponding to the caller of the caller of
  _fastIdentifyCaller(), but if skip_internals=True, this will additionally
  skip over internal methods.
  This is an alternative to _identifyCaller() which does not use traceback/stack objects,
  and so should be significantly faster. It may be less portable though.
  Returns triplet of (filename,line,None).
  """;
  fr = sys._getframe(depth);  # caller's frame
  while fr:
    filename = fr.f_code.co_filename;
    lineno = fr.f_lineno;
    if not _re_localfiles.match(filename):
      break;
    fr = fr.f_back;
  return (filename,lineno,None);


# helper func to pretty-print a node
def _printNode (node,name='',offset=0):
  header = (' ' * offset);
  if name:
    header += name+": ";
  header += str(node);
  if node is None:
    print header;
  else:
    print "%s: %.*s" % (header,78-len(header),str(node._initrec));
    for (ich,child) in node.children:
      _printNode(child,str(ich),offset+2);
    for (ich,child) in node.stepchildren:
      _printNode(child,"(%d)"%ich,offset+2);

