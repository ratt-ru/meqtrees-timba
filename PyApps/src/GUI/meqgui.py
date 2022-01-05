#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from Timba.dmi import *
from Timba.Meq import meqds
from Timba import Grid
from Timba.GUI import browsers
from Timba.GUI import app_proxy_gui

import os
import Timba.Apps

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

def makeDataItem (udi,data=None,viewer=None,publish=False,viewopts={}):
  """Creates a data item given a UDI""";
  # parse udi
  (cat,name,trailer) = meqds.parse_udi(udi);
  if cat == 'node':
    if not name:
      raise ValueError("invalid UDI: "+udi);
    # check name or node index
    nn = name.split('#',1);
    if not nn[0]:
      name = int(nn[1]);     # use node index if no name given
    node = meqds.nodelist[name];
    # enable publishing but do not ask for a state update -- this will
    # be done by the item later
    if publish:
      meqds.enable_node_publish(node,True,get_state=False);
    if not trailer:
      return makeNodeDataItem(node,viewer,viewopts);
    else:
      (name,caption) = meqds.make_udi_node_caption(node,trailer);
      desc = "node %s#%d, state field %s" % (node.name,node.nodeindex,trailer);
      return Grid.DataItem(udi,
                name=name,caption=caption,desc=desc,
                data=data,
                refresh=curry(meqds.request_node_state,node.nodeindex),
                              viewer=viewer,viewopts=viewopts);
  elif cat == 'forest':
    if not trailer:
      return makeForestDataItem(data,viewer,viewopts);
    else:
      (name,caption) = meqds.make_parsed_udi_caption(cat,name,trailer);
      return Grid.DataItem(udi,
         name=name,caption=caption,desc="Forest state field "+trailer,
         data=data,
         refresh=meqds.request_forest_state,
         viewer=viewer,viewopts=viewopts);
  else:
    raise ValueError("can't display "+udi);

def makeNodeDataItem (node,viewer=None,viewopts={}):
  """creates a GridDataItem for a node""";
  udi = meqds.node_udi(node);
  nodeclass = meqds.NodeClass(node);
  vo = viewopts.copy();
  vo.update(defaultNodeViewopts);
  (name,caption) = meqds.make_udi_node_caption(node,None);
  # curry is used to create a call for refreshing its state
  return Grid.DataItem(udi,name=name,caption=caption,desc=name,
            datatype=nodeclass,
            refresh=curry(meqds.request_node_state,node.nodeindex),
            viewer=viewer,viewopts=vo);

def makeForestDataItem (data=None,viewer=None,viewopts={}):
  """creates a GridDataItem for forest state""";
  data = data or meqds.get_forest_state();
  udi = '/forest';
  (name,caption) = meqds.make_parsed_udi_caption('forest',None,None);
  return Grid.DataItem('/forest',
     name=name,caption=caption,desc='State of forest',
     data=meqds.get_forest_state(),
     refresh=meqds.request_forest_state,viewer=viewer,viewopts=viewopts);

def start_kernel (pathname,args=''):
  _dprint(0,pathname,args);
  app_proxy_gui.gui.log_message(' '.join(('starting kernel process:',pathname,args)));
  pid = Timba.Apps.spawnvp_nowait(pathname,[pathname]+args.split(' '));
