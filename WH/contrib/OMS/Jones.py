from Timba.TDL import *
from Timba.Meq import meq
from Timba.Contrib.OMS.Utils import *

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
    J2c = jones(sta2)('conj') ** Meq.ConjTranspose(jones(sta2));
    J2ci = J2c('inv') ** Meq.MatrixInvert22(J2c);
    # create multiplication node
    vis(sta1,sta2) << Meq.MatrixMultiply(J1i,vis0(sta1,sta2),J2ci);
  return vis;
