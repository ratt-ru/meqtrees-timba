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
from Timba.GUI.treebrowser import StickyListViewItem
from Timba.Meq import meqds

import time
import math
import copy
import numarray
from qt import *
from qtext import *

_dbg = verbosity(0,name='profiler');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class Profiler (PersistentCurrier):
  
  def __init__ (self,parent,name):
    self._wtop = wtop = QVBox(parent,name);
    self._appgui = app_proxy_gui.appgui(parent);
    
    # find main window to associate our toolbar with
    self._toolbar = QToolBar("Profiler tools",self._appgui,wtop);
    
    ## COLLECT button
    self._tb_collect = QToolButton(self._toolbar);
    self._tb_collect.setIconSet(pixmaps.refresh.iconset());
    self._tb_collect.setTextLabel("Collect");
    self._tb_collect.setUsesTextLabel(True);
    self._tb_collect.setTextPosition(QToolButton.BesideIcon);
    QToolTip.add(self._tb_collect,"Collect profiling stats from kernel");
    QObject.connect(self._tb_collect,SIGNAL("clicked()"),self.collect_stats);
   
    ## RESET button
    tb_reset = QToolButton(self._toolbar);
    tb_reset.setIconSet(pixmaps.grey_round_cross.iconset());
    tb_reset.setTextLabel("Reset");
    tb_reset.setUsesTextLabel(True);
    tb_reset.setTextPosition(QToolButton.BesideIcon);
    QToolTip.add(tb_reset,"Reset kernel profiling stats");
    QObject.connect(tb_reset,SIGNAL("clicked()"),self.reset_stats);
    
    ## label     
    self._label = QLabel(self._toolbar);
    self._toolbar.setStretchableWidget(self._label);
    self._label.setAlignment(Qt.AlignRight);
    self._label.setIndent(10);
    
    ## listview
    self._listview = QListView(wtop);
    self._listview.addColumn('');
    self._listview.addColumn('');
    # profiling columns
    self._listview.addColumn('Exec');
    self._listview.addColumn('#');
    self._listview.addColumn('avg');
    self._listview.addColumn('Ch/x');
    self._listview.addColumn('#');
    self._listview.addColumn('avg');
    self._listview.addColumn('Own');
    self._listview.addColumn('#');
    self._listview.addColumn('avg');
    # all cache columns
    self._listview.addColumn('Rq all');
    self._listview.addColumn('c/hit');
    self._listview.addColumn('c/m');
    self._listview.addColumn('c/-');
    self._listview.addColumn('+C');
    self._listview.addColumn('++C');
    # new cache columns
    self._listview.addColumn('Rq new');
    self._listview.addColumn('c/hit');
    self._listview.addColumn('c/m');
    self._listview.addColumn('c/-');
    self._listview.addColumn('+C');
    self._listview.addColumn('++C');
    self._listview.setRootIsDecorated(True);
    self._listview.setAllColumnsShowFocus(True);
    self._listview.header().setMovingEnabled(False);
    QObject.connect(self._listview,SIGNAL('expanded(QListViewItem*)'),self._expand_item);
    for col in range(1,self._listview.columns()):
      self._listview.setColumnAlignment(col,Qt.AlignRight);
    
    ## subscribe to nodelist changes
    meqds.subscribe_nodelist(self._process_nodelist);
  
  def wtop (self):
    return self._wtop;
    
  class StatEntry (object):
    __slots__ = ( "name","ps","cs","count" );
    def __init__ (self,name,ps=None,cs=None,count=1):
      self.name = name;
      if ps is None:
        ps = numarray.zeros((3,2));
      if cs is None:
        cs = numarray.zeros((2,6));
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
    self._tb_collect.setEnabled(True);
    if not meqds.nodelist.has_profiling():
      return;
    tmp = self._appgui.wait_cursor();
    self.clear();
    # build internal list of by-class stats
    self._stats = {};
    for ni,node in meqds.nodelist.iteritems():
      self._stats[ni] = self.NodeStatEntry(node);
    # populate profiler view
    if self._stats:
      self._label.setText("profiling stats collected at "+time.strftime("%H:%M:%S"));
      self._appgui.log_message("profiling stats collected");
      # create base items
      treeview = StickyListViewItem(self._listview,"Tree View",key=10);
      roots = [ (node.name,node.nodeindex) for node in meqds.nodelist.rootnodes() ];
      treeview._generate_items = self.curry(self._generate_node_items,roots);
      treeview.setExpandable(True);

      # by-class views
      self._classes = meqds.nodelist.classes();
      classview = StickyListViewItem(self._listview,"By Class",key=20);
      classview._generate_items = self.curry(self._generate_summary_stats,lambda x:x.classname);
      classview.setExpandable(True);
    else:
      self._label.setText("forest is empty");
      self._appgui.log_message("forest is empty, no profiling available");
    
    # generate signal
    self.wtop().emit(PYSIGNAL("collected()"),());
    
  class StatItem (QListViewItem):
    def __init__(self,parent,name,name2,se):
      QListViewItem.__init__(self,parent,name,name2);
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
      cs = list(se.cs.getflat());
      for val in cs:
        self.setText(col,str(val)); 
        col += 1;
      self._content += cs;
      
    def compare (self,other,icol,ascending):
      return cmp(self._content[icol],other._content[icol]);
    
  def _summarize_stats (self,keyfunc,stats):
    sums = {};
    for se in stats.itervalues():
      key = keyfunc(se);
      try: sums[key] += se;
      except KeyError:
        sums[key] = newentry = self.StatEntry(str(key),count=0);
        newentry += se;
    return sums;
    
  def _generate_summary_stats (self,keyfunc,parent_item):
    # generate summary stats using the supplied key-function
    sums = self._summarize_stats(keyfunc,self._stats);
    for key,se in sums.iteritems():
      self.StatItem(parent_item,str(key),str(se.count),se);
        
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
          item.setExpandable(True);
          item._generate_items = self.curry(self._generate_node_items,childlist);
      else: # missing child
        item = self.StatItem(parent_item,label,'',self.StatEntry(''));
      
  def _expand_item (self,item):
    # populate item when first
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
    self._listview.clear();

  def collect_stats (self):
    self.wtop().emit(PYSIGNAL("collecting()"),());
    self._appgui.log_message("collecting profiling stats, please wait");
    self.clear();
    self._tb_collect.setEnabled(False);
    self._label.setText("<i>(waiting for profiling stats from kernel)</i>");
    meqds.request_nodelist(profiling_stats=True);
  
  def reset_stats (self):
    self._tb_collect.setEnabled(True);
    self._appgui.log_message("resetting profiling stats");
    meqds.mqs().meq('Reset.Profiling.Stats',record(),wait=False);
