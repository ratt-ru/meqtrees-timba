#!/usr/bin/python

from Timba.dmi import *
from Timba.Meq import meqds
from Timba import Grid
from Timba.GUI import browsers

_dbg = verbosity(0,name='meqgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

default_state_open =  ({'cache':({'result':({'vellsets':({'0':None},None)},None)},None), \
                         'request':None },None);

defaultResultViewopts = { \
  browsers.RecordBrowser: { 'default_open': default_state_open }, \
};

defaultNodeViewopts = { \
  browsers.RecordBrowser: { 'default_open': default_state_open },
#  NodeBrowser:   { 'default_open': ({'state':_default_state_open},None) } 
};

def makeNodeDataItem (node,viewer=None,viewopts={}):
  """creates a GridDataItem for a node""";
  udi = meqds.node_udi(node);
  nodeclass = meqds.NodeClass(node);
  vo = viewopts.copy();
  vo.update(defaultNodeViewopts);
  namestr = node.name or '#'+str(node.nodeindex);
  name = "%s (%s)" % (namestr,node.classname);
  caption = "<b>%s</b> <small><i>(%s)</i></small>" % (namestr,node.classname);
  desc = "State record of node %s#%d (class %s)" % (node.name,node.nodeindex,node.classname);
  # curry is used to create a call for refreshing its state
  return Grid.DataItem(udi,name=name,caption=caption,desc=desc,
            datatype=nodeclass,
            refresh=curry(meqds.request_node_state,node.nodeindex),
            viewer=viewer,viewopts=vo);
