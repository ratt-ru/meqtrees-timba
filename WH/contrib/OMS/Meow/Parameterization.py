from Timba.TDL import *
from Timba.Meq import meq
from numarray import *


def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;

# type of polc object  
POLC_TYPE = type(meq.polc(0));

class QualScope (object):
  """Helper class used to create nodes with a given scope and set of
  qualifiers.""";
  def __init__ (self,ns,quals,kwquals):
    self.ns = ns;
    self.quals = quals;
    self.kwquals = kwquals;
  def __getattr__ (self,name):
    return self.ns[name](*self.quals,**self.kwquals);
  def __getitem__ (self,name):
    return self.ns[name](*self.quals,**self.kwquals);

class Parameterization (object):
  """Parameterization is a base class for objects with parameters.
  It provides services for managing polcs, etc.
  Mainly, it also provides a "qualified scope" object -- available
  as self.ns -- that can be used just like a proper node scope
  to create all nodes associated with this object, automatically
  assigning them the given qualifiers (including the name, if not None).
  The global node scope is available as self.ns0.
  If needed, the set of qualifiers (including name) can be accessed via 
  quals()/kwquals().
  """;
  
  def __init__(self,ns,name,parm_options=record(node_groups='Parm'),quals=[],kwquals={}):
    self.ns0    = ns;
    self.name   = name;
    self._polcs = record();
    self._parm_options = parm_options;
    self._quals     = list(quals);
    self._kwquals   = kwquals;
    if name is not None:
      self._quals.append(name);
    if self._quals or self._kwquals:
      self.ns = QualScope(ns,self._quals,self._kwquals);
    else:
      self.ns = ns;
    
  def quals (self):
    """Returns qualifiers for this object""";
    return self._quals;
    
  def kwquals (self):
    """Returns keyword qualifiers for this object""";
    return self._kwquals;
    
  def _const_node (self,name,value):
    """Creates a node called 'name' in the object's NodeScope, and applies
    the object's qualifiers. Returns node stub.
    """;
    return self.ns[name] << Meq.Constant(value=value);
    
  def _create_polc (self,polcname,value,degree_f=0,degree_t=0):
    """Creates a polc called 'polcname' with the given c00 coefficient and
    f/t degrees""";
    if not isinstance(value,POLC_TYPE):
      if not isinstance(value,(int,float)):
        raise TypeError,polcname+": numeric value expected";
      value = create_polc(value,degree_f,degree_t);
    self._polcs[polcname] = value;
    
  def _rename_polc (self,old,new):
    """Renames a polc""";
    self._polcs[new] = self._polcs.pop(old);
    
  def _parm (self,parmname,value=0):
    """Creates a Meq.Parm node called 'parmname' in the object's NodeScope, 
    and applies the object's qualifiers. Inits the parm with the polc of
    the same name.
    """;
    node = self.ns[parmname];
    if not node.initialized():
      polc = self._polcs.get(parmname,None);
      if polc is None:
        polc = self._polcs[parmname] = create_polc(value);
      node << Meq.Parm(polc,real_polc=polc,  # real polc also saved in parm state
                   shape=polc.coeff.shape,
                   **self._parm_options);
    return node;

