from numarray import *
from Timba.TDL import *
from Timba.Meq import meq

def create_polc(c00=0.0,degree_f=0,degree_t=0):
  """helper function to create a t/f polc with the given c00 coefficient,
  and with given order in t/f""";
  polc = meq.polc(zeros((degree_t+1, degree_f+1))*0.0);
  polc.coeff[0,0] = c00;
  return polc;
  
POLC_TYPE = type(meq.polc(0));

class SkyComponent(object):
  """A SkyComponent represents an abstract sky model element.
  SkyComponents have a ra/dec position, and a set of Jones matrices
  associated with that direction.
  """;
  def __init__(self,ns,name,ra=0.0,dec=0.0,
               parm_options=record(node_groups='Parm')):
    self.ns     = ns;
    self.name   = name;
    self._polcs = record();
    # create ra/dec polcs
    if not isinstance(ra,(int,float)):
      raise TypeError,"ra: numeric value expected";
    self._polcs.ra = create_polc(c00=ra);
    if not isinstance(dec,(int,float)):
      raise TypeError,"dec: numeric value expected";
    self._polcs.dec = create_polc(c00=dec);
    # store other attributes
    self._parm_options = parm_options;
    pass
    
  def _parm (self,parmname):
    """Helper function. Creates a Meq.Parm node for the given parameter, using
    the polc stored in self._polcs.""";
    polc = self._polcs[parmname];
    node = self.ns[parmname](self.name) << \
        Meq.Parm(polc,real_polc=polc,  # real polc also saved in parm state
                 **self._parm_options);
    # self._solvables[parmname] = node.name;
    return node;
    
  def radec (self):
    """Returns ra-dec two-pack for this component""";
    radec = self.ns.radec(self.name);
    if not radec.initialized():
      radec << Meq.Composer(self._parm("ra"),self._parm("dec"));
    return radec;
    
  def lmn (self,radec0):
    """Returns LMN three-pack for this component, given a phase centre.
    Qualifiers from radec0 are added in.""";
    # create coordinate nodes, add in qualifiers of radec0 since
    # we may ahve different LMN sets for different directions
    lmn = self.ns.lmn(self.name).qadd(radec0);
    if not lmn.initialized():
      lmn << Meq.LMN(radec_0=radec0,radec=self.radec());
    return lmn;
    
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
      nodes = self.ns.visibility(self.name).qadd(observation.radec0());
    if not nodes(*(array.ifrs()[0])).initialized():
      self.make_visibilities(nodes,array,observation);
    return nodes;
