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
from Timba.utils import *
from Timba import Grid 
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import app_proxy_gui
from Timba.GUI.treebrowser import StickyTreeWidgetItem
from Timba.Meq import meqds

import time
import math
import copy
import Timba.array

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

_dbg = verbosity(0,name='profiler');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class Profiler (PersistentCurrier):
  
  def __init__ (self,parent,name):
    self._wtop = wtop = QWidget(parent);
    self._wtop_lo = wtop_lo = QVBoxLayout(self._wtop);
    wtop_lo.setContentsMargins(0,0,0,0);
    wtop_lo.setSpacing(0);
    self._appgui = app_proxy_gui.appgui(parent);
    
    # find main window to associate our toolbar with
    self._toolbar = QToolBar("Profiler tools",wtop);
    wtop_lo.addWidget(self._toolbar);
    self._toolbar.setIconSize(QSize(16,16));
    self._toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    
    ## COLLECT button
    self._qa_collect = self._toolbar.addAction(pixmaps.refresh.icon(),"Collect",self.collect_stats);
    self._qa_collect.setToolTip("Collect profiling stats from meqserver");

    #self._tb_collect = QToolButton(self._toolbar);
    #self._tb_collect.setIcon(pixmaps.refresh.icon());
    #self._tb_collect.setText("Collect");
    #self._tb_collect.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    #self._tb_collect.setToolTip("Collect profiling stats from meqserver");
    #QObject.connect(self._tb_collect,SIGNAL("clicked()"),self.collect_stats);
   
    ## RESET button
    qa_reset = self._toolbar.addAction(pixmaps.grey_round_cross.icon(),"Reset",self.reset_stats);
    qa_reset.setToolTip("Reset meqserver's profiling stats");

    #tb_reset = QToolButton(self._toolbar);
    #tb_reset.setIcon(pixmaps.grey_round_cross.icon());
    #tb_reset.setText("Reset");
    #tb_reset.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
    #tb_reset.setToolTip("Reset meqserver's profiling stats");
    #QObject.connect(tb_reset,SIGNAL("clicked()"),self.reset_stats);
    
    ## label     
    self._label = QLabel(self._toolbar);
    self._toolbar.addWidget(self._label);
    # self._toolbar.setStretchableWidget(self._label);
    self._label.setAlignment(Qt.AlignRight|Qt.AlignVCenter);
    self._label.setIndent(20);
    
    ## listview
    self._tw = QTreeWidget(wtop);
    wtop_lo.addWidget(self._tw);
    self._tw.setHeaderLabels(['','',
    # profiling columns
         'Exec',
         '#',
         'avg',
         'Ch/x',
         '#',
         'avg',
         'Own',
         '#',
         'avg',
    # all cache columns
         'Rq all',
         'c/hit',
         'c/m',
         'c/-',
         '+C',
         '++C',
    # new cache columns
         'Rq new',
         'c/hit',
         'c/m',
         'c/-',
         '+C',
         '++C'
      ]);
    self._tw.setRootIsDecorated(True);
    self._tw.setAllColumnsShowFocus(True);
    self._tw.setSortingEnabled(True);
    self._tw.header().setResizeMode(QHeaderView.ResizeToContents);
    self._tw.header().setMovable(False);
    self._tw.header().setDefaultAlignment(Qt.AlignRight);
    QObject.connect(self._tw,SIGNAL('itemExpanded(QTreeWidgetItem*)'),self._expand_item);
#    for col in range(1,self._tw.columns()):
#      self._tw.setColumnAlignment(col,Qt.AlignRight);
    
    ## subscribe to nodelist changes
    meqds.subscribe_nodelist(self._process_nodelist);
  
  def wtop (self):
    return self._wtop;
    
  class StatEntry (object):
    __slots__ = ( "name","ps","cs","count" );
    def __init__ (self,name,ps=None,cs=None,count=1):
      self.name = name;
      if ps is None:
        ps = Timba.array.zeros((3,2));
      if cs is None:
        cs = Timba.array.zeros((2,6));
      self.ps,self.cs,self.count = ps,cs,count;
    def __iadd__ (self,other):
      self.ps = self.ps + other.ps;
      self.cs = self.cs + other.cs;
      self.count += other.count;
      return self;
    def __add__ (self,other):
      res = copy.deepcopy(self);
      return res.__iadd__(other);
    
  class NodeStatEntry (StatEntry):
    __slots__ = ( "classname" );
    def __init__ (self,node):
      Profiler.StatEntry.__init__(self,node.name,node.profiling_stats,node.cache_stats);
      self.classname = node.classname;
      
  def _process_nodelist (self,dum):
    self._qa_collect.setEnabled(True);
    if not meqds.nodelist.has_profiling():
      return;
    tmp = self._appgui.wait_cursor();
    self.clear();
    # build internal list of by-class stats
    self._stats = {};
    for ni,node in meqds.nodelist.items():
      self._stats[ni] = self.NodeStatEntry(node);
    # populate profiler view
    if self._stats:
      self._label.setText("profiling stats collected at "+time.strftime("%H:%M:%S"));
      self._appgui.log_message("profiling stats collected");
      # create base items
      self.tw_item = treeview = StickyTreeWidgetItem(self._tw,"Tree View",key=10);
      roots = [ (node.name,node.nodeindex) for node in meqds.nodelist.rootnodes() ];
      treeview._generate_items = self.curry(self._generate_node_items,roots);
      treeview.setFlags(Qt.ItemIsEnabled);
      treeview.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator);

      # by-class views
      self._classes = meqds.nodelist.classes();
      self.cw_item = classview = StickyTreeWidgetItem(self._tw,"By Class",key=20);
      classview._generate_items = self.curry(self._generate_summary_stats,lambda x:x.classname);
      classview.setFlags(Qt.ItemIsEnabled);
      classview.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator);
    else:
      self._label.setText("forest is empty");
      self._appgui.log_message("forest is empty, no profiling available");
    
    # generate signal
    self.wtop().emit(SIGNAL("collected"));
    
  class StatItem (QTreeWidgetItem):
    def __init__(self,parent,name,name2,se):
      QTreeWidgetItem.__init__(self,parent,[str(name),str(name2)]);
      # populate item content
      self._content = [name,name2];
      col = 2;
      for (tot,count) in se.ps:
        self.setText(col,"%.0f"%(tot));     col += 1;
        self.setText(col,str(int(count)));  col += 1;
        if count:
          avg = tot/count;
          self.setText(col,"%.2f"%avg);
        else:
          avg = 0;
        col += 1;
        self._content += [tot,int(count),avg ];
      cs = list(se.cs.ravel());
      for val in cs:
        self.setText(col,str(val)); 
        col += 1;
      self._content += cs;
      # set alignment	
      self.setTextAlignment(0,Qt.AlignLeft);
      if isinstance(name2,str):
        self.setTextAlignment(1,Qt.AlignLeft);
      else:
        self.setTextAlignment(1,Qt.AlignRight);
      for col in range(2,self.columnCount()):
        self.setTextAlignment(col,Qt.AlignRight);

    def __lt__ (self,other):
      icol = self.treeWidget().sortColumn();
      try: return self._content[icol] < other._content[icol];
      except:  # other item not keyed
        return self._content[icol] < 0;

    def __ge__ (self,other):
      return other < self;
      
  def _summarize_stats (self,keyfunc,stats):
    sums = {};
    for se in stats.values():
      key = keyfunc(se);
      try: sums[key] += se;
      except KeyError:
        sums[key] = newentry = self.StatEntry(str(key),count=0);
        newentry += se;
    return sums;
    
  def _generate_summary_stats (self,keyfunc,parent_item):
    # generate summary stats using the supplied key-function
    sums = self._summarize_stats(keyfunc,self._stats);
    for key,se in sums.items():
      self.StatItem(parent_item,str(key),se.count,se);
        
  def _generate_node_items (self,nodelist,parent_item):
    for label,ni in nodelist:
      # get node object and stats
      if ni > 0:
        try: node = meqds.nodelist[ni];
        except KeyError: 
          _dprint(1,"lost node",label,ni);
          continue;
        try: se = self._stats[ni];
        except KeyError: 
          _dprint(1,"lost node stats",label,ni);
          continue;
        # create item
        item = self.StatItem(parent_item,label,node.classname,se);
        # add children to item as needed
        childlist = [];
        if node.children:
          # format string for enumerating children -- need to use sufficient digits
          chform = '%%0%dd: %%s' % (math.floor(math.log10(len(node.children)))+1,);
          for (key,ni) in node.children:
            if ni > 0:
              childname = meqds.nodelist[ni].name;
            else:
              childname = '<none>';
            childlabel = node.child_label_format() % (key,childname);
            childlist.append((childlabel,ni));
        for ni in node.step_children:
          childnode = meqds.nodelist[ni];
          childlist.append(("(" + childnode.name +")",ni));
        # do we have a childlist now?
        if childlist:
          item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator);
          item._generate_items = self.curry(self._generate_node_items,childlist);
      else: # missing child
        item = self.StatItem(parent_item,label,'',self.StatEntry(''));
      
  def _expand_item (self,item):
    # treeview and classview mutually exclusive; also adjust column names
    if item is self.tw_item:
      self.cw_item.setExpanded(False);
      self._tw.headerItem().setText(0,"node");
      self._tw.headerItem().setText(1,"class");
    elif item is self.cw_item:
      self.tw_item.setExpanded(False);
      self._tw.headerItem().setText(0,"class");
      self._tw.headerItem().setText(1,"# nodes");
    # populate item when first opened
    try: genfunc = item._generate_items;
    except: pass;
    else:
      tmp = self._appgui.wait_cursor();
      delattr(item,'_generate_items');
      try:
        genfunc(item);
      except:
        tmp = None;
        raise;
      
  def clear (self):      
    self._stats = self._classes = None;
    self._tw.clear();

  def collect_stats (self):
    self.wtop().emit(SIGNAL("collecting"));
    self._appgui.log_message("collecting profiling stats, please wait");
    self.clear();
    self._qa_collect.setEnabled(False);
    self._label.setText("<i>(waiting for profiling stats from meqserver)</i>");
    meqds.request_nodelist(profiling_stats=True);
  
  def reset_stats (self):
    self._qa_collect.setEnabled(True);
    self._appgui.log_message("resetting profiling stats");
    meqds.mqs().meq('Reset.Profiling.Stats',record(),wait=False);
