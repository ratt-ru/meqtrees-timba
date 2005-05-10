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


_patt_Udi_NodeState = re.compile("^/[^/]+/(([^#/]+)|(#[0-9]+))(/.*)?$");

def isBookmarkable (udi):
  "Returns True if udi refers to a valid bookmark-able data item";
  ff = udi.split('/',3);
  if ff[0] != '':
    return False;
  cat = ff[1];
  if cat == 'forest':
    return True;
  elif cat == 'node' and len(ff) > 2 and ff[2]:  # node must have name
    return True;
  return False;

def makeDataItem (udi,data=None,viewer=None,viewopts={}):
  """Creates a data item given a UDI""";
  # parse udi
  ff = udi.split('/',3);
  if ff[0] != '' or len(ff)<2:
    raise ValueError,"invalid UDI: "+udi;
  cat = ff[1];
  if len(ff)>2:
    name = ff[2];
  else:
    name = None;
  if not cat:
    raise ValueError,"invalid UDI: "+udi;
  if len(ff) > 3:
    trailer = ff[3];
  else:
    trailer = None;
  # see what data category it belongs to
  if cat == 'node':
    if not name:
      raise ValueError,"invalid UDI: "+udi;
    # check name or node index
    nn = name.split('#',1);
    if not nn[0]:
      name = int(nn[1]);     # use node index if no name given
    node = meqds.nodelist[name];
    if trailer is None:
      return makeNodeDataItem(node,viewer,viewopts);
    else:
      namestr = node.name or '#'+str(node.nodeindex);
      name = "%s %s" % (namestr,trailer);
      caption = "<b>%s</b> <small>%s</small>" % (namestr,trailer);
      desc = "node %s#%d field %s" % (node.name,node.nodeindex,trailer);
      return Grid.DataItem(udi,name=name,caption=caption,desc=desc,
                data=data,
                refresh=curry(meqds.request_node_state,node.nodeindex),
                              viewer=viewer,viewopts=viewopts);
  elif cat == 'forest':
    if trailer is None:
      return makeForestDataItem(data,viewer,viewopts);
    else:
      name = "forest %s" % (namestr,trailer);
      caption = "<b>Forest</b> <small>%s</small>" % (trailer,);
      desc = "forest state field "+trailer;
      return Grid.DataItem('/forest',name=name,
         caption=caption,desc=desc,data=data,
         refresh=meqds.request_forest_state,
         viewer=viewer,viewopts=viewopts);
  else:
    raise ValueError,"can't display "+udi;

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

def makeForestDataItem (data=None,viewer=None,viewopts={}):
  """creates a GridDataItem for forest state""";
  data = data or meqds.get_forest_state();
  return Grid.DataItem('/forest',name='Forest state',
     caption='<b>Forest state</b>',
     desc='State of forest',data=meqds.get_forest_state(),
     refresh=meqds.request_forest_state,viewer=viewer,viewopts=viewopts);
