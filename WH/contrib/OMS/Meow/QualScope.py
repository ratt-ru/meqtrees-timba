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
#   ns2 = ns1.derive(append=[list] or {dict})          appends quals/kwquals
#   ns2 = ns1.derive(prepend=[list])                   prepends quals
#   ns2 = ns1.derive(exclude=[list] or {dict})         excludes quals/kwquals
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
      self.quals = [quals]
    else:
      self.quals = quals
      
    # Store its keyword qualifiers:
    if not isinstance(kwquals,dict):
      self.kwquals = dict()
    else:  
      self.kwquals = kwquals
      
    return None
    

  def __getattr__ (self, name=None):
    """This is the function that is called when a node(stub) is created
    with:   node = ns1.name << 1."""
    ns = self.ns[name](*self.quals,**self.kwquals)
    # print '** __getattr__(',name,') ->',str(ns)
    return ns

  def __getitem__ (self, name=None):
    """This is the function that is called when a node(stub) is created
    with:   node = ns1[name] << 1."""
    ns = self.ns[name](*self.quals,**self.kwquals)
    # print '** __getitem__(',name,') ->',str(ns)
    return ns

  #----------------------------------------------------------------

  def merge (self, other):
    """Derive a new QualScope object by merging its qualifiers
    with the qualifiers of another QualScope (other).
    Double qualifiers are avoided."""

    # Do NOT modify its own qualifiers (use copies):
    quals = deepcopy(self.quals)
    kwquals = deepcopy(self.kwquals)

    # Modify the copied qualifiers, as specified:
    for key in other.kwquals.keys():
      if (not kwquals.has_key(key)):
        kwquals[key] = other.kwquals[key]
    for item in other.quals:
      if (not item in quals):
        quals.append(item)

    # Make the new QualScope:
    qs = QualScope(self.ns, quals=quals, kwquals=kwquals)
    # print '** merge() ->',qs.quals,qs.kwquals
    return qs

  #----------------------------------------------------------------

  def derive (self, append=None, prepend=None, exclude=None):
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
          quals.append(item)

    if prepend:
      if not isinstance(prepend, dict):
        if not isinstance(prepend, (list,tuple)):
          prepend = [prepend]
        for item in prepend:
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
# Test program:
#=======================================================================

if __name__ == '__main__':
  ns = NodeScope();
  print '** ns =',ns

  ns1 = QualScope(ns, None)
  ns1 = QualScope(ns, 5)
  ns1 = QualScope(ns, ['q1','q2'], dict(g=56))
  print '** ns1 =',ns1

  node = ns1.xxx(7)

  node = ns1.xxx << 1

  node = ns1['yyy'] << 1

  # node = ns1 << 1

  ns2 = ns1.derive()
  ns2 = ns1.derive(append=55)
  ns2 = ns1.derive(prepend=55)
  ns2 = ns1.derive(append=dict(y=55))

  ns2 = ns1.derive(exclude='q1')
  ns2 = ns1.derive(exclude=dict(g=None))

  ns3 = QualScope(ns, ['q1','q3'], dict(g=56, h=-7))
  ns4 = ns3.merge(ns1)
  node = ns4.node('extra') << 1
  print str(node)

  ns.Resolve();  
  print len(ns.AllNodes()),'nodes defined';




    
