# file: ../Meow/QualScope.py

# History:
# - 24mar2007: creation (from Parameterization.py)
# - 24mar2007: addition of merge() and derive()

# Description:

# One of the most difficult features of the Tree Definition Language (TDL)
# is the generation of descriptive but unique nodenames. Especiall when the
# trees are large and complicated, and use other modules to generate subtrees.
# The QualScope object is a powerful help in this process. It is constructed
# from an existing nodescope (ns), together with an arbitrary number of
# nodename qualifiers:
#   ns1 = Meow.QualScope(ns, quals=[some list], kwquals={some dict})
# The object (ns1) behaves just like a regular nodescope, in the sense that
# it is used to generate nodes with it. The difference is that the nodenames
# will automatically have all its qualifiers, in addition to any qualifiers
# that are specified explicitly:
#   node = ns1.nodename(q1)(s=3) << Meq.Constant(78)
#
# Of course, the QualScope is cumulative: i.e. one may create a new QualScope
# from an existing one, with new qualifiers. The new QualScope will have both the
# old and the new qualifiers.
# There is also a function to merge two QualScope objects into a new one:
#   ns3 = ns2.merge(ns1)
#
# There is a function to derive a new QualScope object from an existing one with
# its own qualifiers, plus any new ones. The latter can be specified in various
# ways:
#   ns2 = ns1._derive(append=[list] or {dict})          appends quals/kwquals
#   ns2 = ns1._derive(prepend=[list])                   prepends quals
#   ns2 = ns1._derive(exclude=[list] or {dict})         excludes quals/kwquals
#
# It is also possible to create a new QualScope object by merging its
# qualifiers with those of another one:
#   ns2 = ns1._merge(other=ns3)
#   ns2 = ns1.copy()                                   produces a copy of ns1        
#   

#======================================================================================


from Timba.TDL import *
from Timba.Meq import meq
from copy import deepcopy
import Meow


class QualScope (object):
  """Helper class used to create nodes with a given scope and set of
  qualifiers.""";

  def __init__ (self, ns, quals=[], kwquals={}):
    self.ns = ns

    # Store its list qualifiers:
    if quals==None:
      self.quals = []
    elif not isinstance(quals,(list,tuple)):
      self.quals = [deepcopy(quals)]
    else:
      self.quals = deepcopy(quals)
      
    # Store its keyword qualifiers:
    if not isinstance(kwquals,dict):
      self.kwquals = dict()
    else:  
      self.kwquals = deepcopy(kwquals)

    # Cumulative qualifiers (including those of the ns):
    self.cumuquals = []
    if isinstance(ns.cumuquals,(list,tuple)):
      self.cumuquals.extend(ns.cumuquals)
    self.cumuquals.extend(self.quals)

    self.cumukwquals = dict()
    if isinstance(ns.cumukwquals,dict):
      self.cumukwquals.update(ns.cumukwquals)
    self.cumukwquals.update(self.kwquals)
    # print '** cumu:',self.cumuquals,self.cumukwquals
      
    return None
    
  #----------------------------------------------------------------

  def __getattr__ (self, name=None):
    """This is the function that is called when a node(stub) is created
    with:   node = ns1.name << ...."""
    nodestub = self.ns[name](*self.quals, **self.kwquals)
    # print '** __getattr__(',name,') ->',str(nodestub)
    return nodestub

  def __getitem__ (self, name=None):
    """This is the function that is called when a node(stub) is created
    with:   node = ns1[name] << ...."""
    nodestub = self.ns[name](*self.quals, **self.kwquals)
    # print '** __getitem__(',name,') ->',str(nodestub)
    return nodestub




  #================================================================
  # Some useful extra functions (prepended with _)
  #================================================================


  def _qualstring(self):
    """Return a single qualifying string, make of its qualifiers."""

    # This is a temporary thing, needed to deal with some JEN legacy modules
    
    ss = ''
    first = True
    for qual in self.cumuquals:
      if not first: ss += ':'
      first = False
      ss += str(qual)
      
    for key in self.cumukwquals.keys():
      if not first: ss += ':'
      first = False
      ss += str(key)+'='+str(self.cumukwquals[key])

    if first: return ''
    return ss
  
  
  #---------------------------------------------------------------------


  def _unique (self, name, quals=None, kwquals=None, mode='quals', level=0):
    """Return a unique (i.e. a non-initialized) nodestub.
    If the resulting nodestub with the specified name and quals/kwquals
    has already been initialized, generate a unique one."""

    # NB: Perhaps not very useful, since we will usually use it as an
    #     unqualified node to make qualified nodes. Thus, the unqualified
    #     node never gets initialised, so it can be used again, after which
    #     its qualified nodes may still be non-unique.....

    # First generate a nodestub in a robust manner:
    if quals==None: quals = []
    if not isinstance(quals,(list,tuple)): quals = [quals]
    if isinstance(kwquals,dict):
      nodestub = self.__getitem__(name)(*quals)(**kwquals)
    else:
      nodestub = self.__getitem__(name)(*quals)  


    # Then test whether such a node has already been initialized:
    if nodestub.initialized():
      # Recursively try slightly different names, until unique.
      uniqual = _counter (name, increment=1)
      # There are various ways to attach this unique qualifier:
      if mode=='quals':
        # The preferred method?
        qq = deepcopy(quals)
        qq.insert(0,'('+str(uniqual)+')')
        nodestub = self._unique(name, quals=qq, kwquals=kwquals,
                                mode=mode, level=level+1)

      elif mode=='name':
        # NB: This may interfere with a name-search of the nodescope!
        nodestub = self._unique(name+'('+str(uniqual)+')',
                                mode=mode, level=level+1,
                                quals=quals, kwquals=kwquals)
      else:
        # A bit cumbersome?:
        kwq = deepcopy(kwquals)
        if not isinstance(kwq, dict): kwq = dict()
        kwq['_unique'] = uniqual
        nodestub = self._unique(name, quals=quals, kwquals=kwq,
                                mode=mode, level=level+1)
    # Finished:
    if False:
      prefix = level*'..'
      print '**',prefix,'unique(',name,quals,kwquals,'):',str(nodestub),nodestub.initialized()
      if level==0: print
    return nodestub

  #----------------------------------------------------------------

  def _copy (self):
    """Make a (fully independent) copy of itself"""
    return Meow.QualScope(self.ns, quals=self.quals, kwquals=self.kwquals)

  #----------------------------------------------------------------

  def _merge (self, other=None):
    """Make a new QualScope object by merging its qualifiers with
    the qualifiers of another QualScope (other).
    - Double qualifiers are avoided....(?).
    - If 'other' is a Subscope, .....?
    - If 'other' is a NodeScope, return a copy of itself."""

    # NB: We still need a solution for when 'other' is a Subscope....    <-----!!

    if isinstance(other, NodeScope):
      # If other is a NodeScope, just return a copy of itself
      print '\n** merge(): other is not a QualScope, but:',type(other)
      return Meow.QualScope(self.ns, quals=self.quals, kwquals=self.kwquals)

    if not isinstance(other, QualScope): 
      # If other is anything else....
      raise ValueError, 'merge(): other is not a QualScope, but: '+str(type(other))

    # Do NOT modify its own qualifiers (use copies):
    quals = deepcopy(self.quals)
    kwquals = deepcopy(self.kwquals)

    # Modify the copied qualifiers, as specified:
    for key in other.cumukwquals.keys():
      if (not self.cumukwquals.has_key(key)):
        kwquals[key] = other.cumukwquals[key]
    for item in other.cumuquals:
      if (not item in self.cumuquals):
        quals.append(item)

    # Make the new QualScope:
    qs = QualScope(self.ns, quals=quals, kwquals=kwquals)
    # print '** merge() ->',qs.quals,qs.kwquals
    return qs

  #----------------------------------------------------------------

  def _derive (self, append=None, prepend=None, exclude=None):
    """Derive another QualScope object with more/less qualifiers"""

    # Do NOT modify its own qualifiers (use copies):
    quals = deepcopy(self.quals)
    kwquals = deepcopy(self.kwquals)

    # Modify the copied qualifiers, as specified:
    if append:
      if isinstance(append, dict):
        for key in append.keys():
          kwquals[key] = append[key]
      elif not isinstance(append, (list,tuple)):
        append = [append]
      if isinstance(append, (list,tuple)):
        for item in append:
          if not item in self.cumuquals:         # avoid doubles
            quals.append(item)

    if prepend:
      if not isinstance(prepend, dict):
        if not isinstance(prepend, (list,tuple)):
          prepend = [prepend]
        for item in prepend:
          if not item in self.cumuquals:         # avoid doubles
            quals.insert(0,item)

    if exclude:
      if isinstance(exclude, dict):
        for key in exclude.keys():
          if kwquals.has_key(key):
            kwquals.__delitem__(key)
      elif not isinstance(exclude, (list,tuple)):
        exclude = [exclude]
      if isinstance(exclude, (list,tuple)):
        for item in exclude:
          if item in quals:
            quals.remove(item)

    # Make the new QualScope:
    qs = QualScope(self.ns, quals=quals, kwquals=kwquals)
    # print '** derive(',append,' prepend=',prepend,' exclude=',exclude,') ->',qs.quals,qs.kwquals
    return qs



#=======================================================================
# Counter service (use to automatically generate unique node names)
#=======================================================================

_counters = {}

def _counter (key, increment=0, reset=False, trace=False):
  global _counters
  _counters.setdefault(key, 0)
  if reset: _counters[key] = 0
  _counters[key] += increment
  if trace:
    print '** QualScope: _counters(',key,') =',_counters[key]
  return _counters[key]


#=======================================================================
# Test program:
#=======================================================================

if __name__ == '__main__':
  ns = NodeScope();
  print '** ns =',ns

  ns1 = QualScope(ns, None)
  ns1 = QualScope(ns, 5)
  ns1 = QualScope(ns, ['q1','q2'], dict(g=56))
  print '\n** ns1 =',ns1,ns1._qualstring()

  if 0:
    ns2 = QualScope(ns1,range(2),dict(c=8))
    print ns2._qualstring()
    ns3 = QualScope(ns2,'xx',dict(y=6))
    print ns3._qualstring()

  node = ns1.xxx(7)

  node = ns1.xxx << 1

  node = ns1['yyy'] << 1

  # node = ns1 << 1

  if 0:
    node = ns1.xxx << 1
    node = ns1._unique('xxx') << 3
    node = ns1._unique('xxx')
    node = ns1._unique('xxx', 79)
    node = ns1._unique('xxx', None)
    node = ns1._unique('xxx', [79])
    node = ns1._unique('xxx', [79], dict(op='op'))


  if 1:
    ns2 = ns1._derive()
    ns2 = ns1._derive(append=55)
    ns2 = ns1._derive(prepend=55)
    ns2 = ns1._derive(append=dict(y=55))
    
    ns2 = ns1._derive(exclude='q1')
    ns2 = ns1._derive(exclude=dict(g=None))

    if 1:
      ns3 = QualScope(ns2, ['q1','q3'], dict(g=56, h=-7))
      ns4 = ns3._merge(ns1)
      node = ns4.node('extra') << 1
      print str(node)

  if 0:
    ns3 = QualScope(ns, ['q1','q3'], dict(g=56, h=-7))
    ns4 = ns3._merge(ns1)
    node = ns4.node('extra') << 1
    print str(node)

    if 0:
      nsub = ns.Subscope('sub')
      print '\n** Subscope:',type(nsub)
      ns7 = QualScope(nsub, ['q1','q3'], dict(g=56, h=-7))
      node = ns7.node('subsub') << 1
      print str(node)

      ns5 = ns3._merge(nsub)           # This does not yet work...
      node = ns5.node('uuu') << 1
      print str(node)

      ns5 = ns3._merge(ns)
      node = ns5.node('ggg') << 1
      print str(node)

  if 0:
    ns6 = ns3._merge()
    node = ns6.node('hhh') << 1
    print str(node)

  if 0:
    isn = is_node(node)             # function defined in Timba.TDL           
    print 'is_node() ->',isn,type(node)

  ns.Resolve();  
  print len(ns.AllNodes()),'nodes defined';




    
