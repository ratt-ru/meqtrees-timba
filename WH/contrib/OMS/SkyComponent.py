from Timba.TDL import *
from Timba.Meq import meq
from Parameterization import *
from Direction import *

class SkyComponent (Parameterization):
  """A SkyComponent represents an abstract sky model element.
  SkyComponents have an name and an associated direction.
  """;
  def __init__(self,ns,name,direction,
               parm_options=record(node_groups='Parm')):
    Parameterization.__init__(self,ns,name,parm_options=parm_options);
    print direction;
    if isinstance(direction,Direction):
      self.direction = direction;
    else:
      if not isinstance(direction,(list,tuple)) or len(direction) != 2:
        raise TypeError,"direction: Direction object or (ra,dec) tuple expected";
      ra,dec = direction;
      self.direction = Direction(ns,name,ra,dec,parm_options=parm_options);
    
  def radec (self):
    """Returns ra-dec two-pack for this component's direction""";
    return self.direction.radec();
    
  def lmn (self,radec0):
    return self.direction.lmn(radec0);
    
  def make_visibilities (self,nodes,array,observation):
    """Abstract method.
    Creates nodes computing nominal visibilities of this component 
    Actual nodes are then created as nodes(name,sta1,sta2) for all array.ifrs().
    Returns partially qualified visibility node which must be qualified 
    with an (sta1,sta2) pair.
    """;
    raise TypeError,type(self).__name__+".make_visibilities() not defined";
    
  def visibilities  (self,array,observation,nodes=None):
    """Creates nodes computing visibilities of component.
    If nodes=None, creates nodes as ns.visibility:'name', with extra
    qualifiers from observation.radec0(), otherwise uses 'nodes' directly. 
    Actual nodes are then created as node(name,sta1,sta2) for all array.ifrs().
    Returns partially qualified visibility node which must be qualified 
    with an (sta1,sta2) pair.""";
    if nodes is None:
      nodes = self.ns.visibility.qadd(observation.radec0());
    if not nodes(*(array.ifrs()[0])).initialized():
      self.make_visibilities(nodes,array,observation);
    return nodes;
