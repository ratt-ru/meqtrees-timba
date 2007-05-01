from Timba.TDL import *
from Timba.Meq import meq
from numarray import *
import Meow

def create_polc(c00=0.0,deg_f=0,deg_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((deg_t+1, deg_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

# type of polc object  
POLC_TYPE = type(meq.polc(0));

def resolve_parameter (name,node,value,tags=[],solvable=True):
  # make sure tags is a list, and add name
  if isinstance(tags,str):
    tags = tags.split(" ");
  else:
    tags = list(tags);
  tags.append(name);
  if isinstance(value,(int,float,complex)):
    return node << Meq.Constant(value=value,tags=tags);
  elif is_node(value):
    return value;
  elif isinstance(value,Meow.Parm):
    if solvable:
      tags.append("solvable");
    return node << value.make(tags);
  else:
    raise TypeError,"Pparameter '"+name+"' can only be defined as a constant, a node, or a Meow.Parm";
  

class Parameterization (object):
  """Parameterization is a base class for objects with parameters.
  It provides services for managing parms, etc.
  It also provides a "qualified scope" object -- available
  as self.ns -- that can be used just like a proper node scope
  to create all nodes associated with this object, automatically
  assigning them the given qualifiers (including the name, if not None).
  The global node scope is available as self.ns0.
  If needed, the set of qualifiers (including name) can be accessed via 
  quals()/kwquals().
  """;
  
  def __init__(self,ns,name,quals=[],kwquals={}):
    self.ns0    = ns;
    self.name   = name;
    self._parmnodes = {};
    self._parmdefs = {};
    self._quals     = list(quals);
    self._kwquals   = kwquals;
    if name is not None:
      self._quals.append(name);
    if self._quals or self._kwquals:
      self.ns = ns.QualScope(*self._quals,**self._kwquals);
    else:
      self.ns = ns;
    
  def _add_parm (self,name,value,tags=[],solvable=True):
    """Adds an entry for parameter named 'name'. No nodes are created yet;
    they will only be created when self._parm(name) is called later. This
    is useful because a Meow component can pre-define all necessary 
    parameters at construction time with _add_parm(), but then make nodes
    only for the ones that are actually in use with _parm().
    
    'value' can be:
    * a numeric constant, in which case a Meq.Constant is created
    * an actual node, in which case that node is used as is
    * a Meow.Parm, in which case a Meq.Parm is defined, with the given tags
      added on.
    If solvable=True, a "solvable" tag will be added on. This marks 
    potentially solvable parms. This is true by default since everything
    can be solved for; if you want to make a non-solvable parm, use False.
    """;
    if not isinstance(value,(int,float,complex,Meow.Parm)) and \
       not is_node(value):
      raise TypeError,"argument must be a constant, a node, or a Meow.Parm";
    self._parmdefs[name] = (value,tags,solvable);
    
  def _parm (self,name,value=None,tags=[],nodename=None,solvable=True):
    """Returns node representing parameter 'name'.
    If 'nodename' is None, node is named after parm, else
    another name may be given.
    If value is not supplied, then the parameter should have been previously
    defined via _add_parm(). Otherwise, you can define and create a parm 
    on-the-fly by suppying a value and tags as to _add_parm.
    
    """;
    if name in self._parmnodes:
      if value is not None:
        raise TypeError,"duplicate values for Meow parm '"+name+"'";
      return self._parmnodes[name];
    # else has to be defined first (possibly)
    if value is None:
      value,tags,solvable = self._parmdefs.get(name,(None,None,None));
      if value is None:
        raise TypeError,"Meow parm '"+name+"' not previously defined";
    else:
      self._add_parm(name,value,tags,solvable=solvable);
    # now define the node
    nodename = nodename or name;
    self._parmnodes[name] = resolve_parameter(name,self.ns[nodename],
                                              value,tags,solvable);
    return self._parmnodes[name];
