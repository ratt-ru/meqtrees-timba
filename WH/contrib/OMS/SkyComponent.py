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
    # init empty list of Jones matrices
    self._jones = [];
    # store other attributes
    self._parm_options = parm_options;
    pass
    
  def add_station_jones (self,jones,prepend=False):
    """adds a per-station image-plane effect represented by a Jones
    matrix. 'jones' should be a callable object (e.g. an unqualified node)
    such that jones(x) returns the Jones matrix node for station x, or None
    if no matrix is to be applied""";
    # prepend to list
    if prepend:
      self._jones.insert(0,jones);
    else:
      self._jones.append(jones);
    
  def add_jones (self,jones,prepend=False):
    """adds an station-independent image-plane effect represented by the 
    given Jones matrix. Argument should be an valid node.""";
    # emulate a per-station jones so that we may jones matrices uniformly 
    # in visibility()
    self.add_station_jones(lambda sta : jones,prepend);
    
  def jones_list (self):
    return self._jones;

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
    
  def apply_jones (self,vis,vis0,ifr_list):
    """Creates nodes to apply the Jones chain associated with this 
    component.
    'ifr_list' should be a list of (sta1,sta2) pairs
    'vis' is the output node which will be qualified with (sta1,sta2)
    'vis0' is an input visibility node which will be qualified with (sta1,sta2)
    """;
    # multiply input visibilities by our jones list
    for (sta1,sta2) in ifr_list:
      # collect list of per-source station-qualified Jones terms
      terms = [ jones(sta1) for jones in self.jones_list() if jones(sta1) is not None ];
      # reverse list since they are applied in reverse order
      # first (J2*J1*C*...)
      terms.reverse();
      terms.append(vis0(sta1,sta2));
      # collect list of conjugate terms. The '**' operator
      # is for init-if-not-initialized
      terms += [ jones(sta2)('conj') ** Meq.ConjTranspose(jones(sta2))
                 for jones in self.jones_list() if jones(sta2) is not None ];
      # create multiplication node
      vis(sta1,sta2) << Meq.MatrixMultiply(*terms);
    return vis;
    
  def make_clean_visibilities (self,visnode,array,observation):
    raise TypeError,type(self).__name__+".make_clean_visibilities() not defined";
    
  def visibility (self,array,observation):
    """creates nodes computing visibilities of component for all ifrs.
    Returns unqualified visibility node which must be qualified 
    with an (sta1,sta2) pair.""";
    radec0 = observation.radec0();
    # check if a vis node is initialized for first ifr, if it is
    # we don't need to do anything
    # look for visibility node relative to this direction
    visnode = self.ns.visibility(self.name).qadd(radec0);
    if not visnode(*(array.ifrs()[0])).initialized():
      # do we have extra jones terms?
      if self._jones:
        visclean = visnode('cln');
        self.make_clean_visibilities(visclean,array,observation);
        self.apply_jones(visnode,visclean,array.ifrs());
      # no jones terms, use clean visibilities directly
      else:
        self.make_clean_visibilities(visnode,array,observation);
    return visnode;
