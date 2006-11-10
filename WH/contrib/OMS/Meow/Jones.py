from Timba.TDL import *
from Timba.Meq import meq
from Parameterization import *


class Jones (Parameterization):
  """A Jones object represents a set of Jones terms for a set of antennas.
  'name' should be a unique Jones name (e.g. 'E', 'G', etc.).
  'array' is an IfrArray object.
  """;
  def __init__(self,ns,name,array,
               parm_options=record(node_groups='Parm'),
               quals=[],kwquals={}):
               
    Parameterization.__init__(self,ns,name,parm_options=parm_options,
                              quals=quals,kwquals=kwquals);
    self._array = array;
    
  def jones (self):
    """virtual method returning an under-qualified Jones node, which
    must be qualified by station to get the actual Jones node.
    """;
    raise TypeError,"this Jones subclass does not implement a jones() method";
               
  def corrupt (self,vis,vis0):
    jones = self.jones();
    # multiply input visibilities by our jones list
    for (sta1,sta2) in self._array.ifr_list():
      j1 = jones(sta1);
      j2c = jones(sta2)('conj') ** Meq.ConjTranspose(jones(sta2));
      # create multiplication node
      vis(sta1,sta2) << Meq.MatrixMultiply(j1,vis0(sta1,sta2),j2c);
    return vis;
  
  def correct (self,vis,vis0):
    jones = self.jones();
    # multiply input visibilities by our jones list
    for (sta1,sta2) in self._array.ifr_list():
      # collect list of per-source station-qualified Jones terms
      J1i = jones(sta1)('inv') ** Meq.MatrixInvert22(jones(sta1));
      J2c = jones(sta2)('conj') ** Meq.ConjTranspose(jones(sta2));
      J2ci = J2c('inv') ** Meq.MatrixInvert22(J2c);
      # create multiplication node
      vis(sta1,sta2) << Meq.MatrixMultiply(J1i,vis0(sta1,sta2),J2ci);
    return vis;
    

  

def apply_corruption (vis,vis0,jones,ifr_list):
  """Creates nodes to corrupt with a set of Jones matrices.
  'ifr_list' should be a list of (sta1,sta2) pairs
  'vis' is the output node which will be qualified with (sta1,sta2)
  'vis0' is an input visibility node which will be qualified with (sta1,sta2)
  'jones' is a set of Jones matrices which will be qualified with (sta)
  """;
  # multiply input visibilities by our jones list
  for (sta1,sta2) in ifr_list:
    # collect list of per-source station-qualified Jones terms
    J2c = jones(sta2)('conj') ** Meq.ConjTranspose(jones(sta2));
    # create multiplication node
    vis(sta1,sta2) << Meq.MatrixMultiply(jones(sta1),vis0(sta1,sta2),J2c);
  return vis;


def apply_correction (vis,vis0,jones,ifr_list):
  """Creates nodes to apply the inverse of a set of Jones matrices.
  'ifr_list' should be a list of (sta1,sta2) pairs
  'vis' is the output node which will be qualified with (sta1,sta2)
  'vis0' is an input visibility node which will be qualified with (sta1,sta2)
  'jones' is a set of Jones matrices which will be qualified with (sta)
  """;
  # multiply input visibilities by our jones list
  for (sta1,sta2) in ifr_list:
    # collect list of per-source station-qualified Jones terms
    J1i = jones(sta1)('inv') ** Meq.MatrixInvert22(jones(sta1));
    J2i = jones(sta2)('inv') ** Meq.MatrixInvert22(jones(sta2));
    J2ci = J2i('conj') ** Meq.ConjTranspose(J2i);
    # create multiplication node
    vis(sta1,sta2) << Meq.MatrixMultiply(J1i,vis0(sta1,sta2),J2ci);
  return vis;
