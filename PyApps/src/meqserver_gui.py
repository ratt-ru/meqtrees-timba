#!/usr/bin/python

import meqserver
from app_proxy_gui import *
import app_pixmaps as pixmaps
import weakref
import math
import sets

class GriddedPage (object):
  class Cell (object):
    def __init__ (self,parent):
      self._wtop = QWidget(parent);
      self._wtop.hide();
      self._top_lo = QVBoxLayout(self._wtop);
      self._control_lo = QHBoxLayout();
      # pin button
      pin_is = QIconSet(pixmaps.pin_up.pm());
      pin_is.setPixmap(pixmaps.pin_down.pm(),QIconSet.Automatic,QIconSet.Normal,QIconSet.On);
      self._pin = QToolButton(self._wtop);
      self._pin.setAutoRaise(True);
      self._pin.setToggleButton(True);
      self._pin.setIconSet(pin_is);
      self._pin.hide();
      self._wtop.connect(self._pin,SIGNAL("toggled(bool)"),self._set_pinned);
      # refresh button
      self._refresh = QToolButton(self._wtop);
      self._refresh.setIconSet(QIconSet(pixmaps.refresh.pm()));
      self._refresh.setAutoRaise(True);
      self._refresh.hide();
      self._wtop.connect(self._refresh,SIGNAL("clicked()"),self._dorefresh);
      # label
      self._label = QLabel("(empty)",self._wtop);
      # close button
      self._close = QToolButton(self._wtop);
      self._close.setIconSet(QIconSet(pixmaps.cancel.pm()));
      self._close.setAutoRaise(True);
      self._close.hide();
      self._wtop.connect(self._close,SIGNAL("clicked()"),self.clear);
      self._control_lo.addWidget(self._pin);
      self._control_lo.addWidget(self._refresh);
      self._control_lo.addWidget(self._label);
      self._control_lo.addStretch();
      self._control_lo.addWidget(self._close);
      
      self._top_lo.addLayout(self._control_lo);
      self._top_lo.addStretch();

      self._id     = None;
      self._pinned = False;
      self._widget = None;
      
    def wtop (self):
      return self._wtop;
    def hide (self):
      self._wtop.hide();
    def show (self):
      self._wtop.show();
      
    def _dorefresh (self):
      self.wtop().emit(PYSIGNAL("refresh()"),(self,));
      
    def _set_pinned (self,state):
      self._pinned = state;
      self.wtop().emit(PYSIGNAL("pin()"),(self,self._pinned));
      
    def clear (self):
      _id = self._id;
      self._pin.hide();
      self._close.hide();
      self._refresh.hide();
      self._label.setText("(empty)");
      self._pinned = False;
      self._widget = self._id = None;
      self.wtop().disconnect(PYSIGNAL("refresh()"));
      self.wtop().emit(PYSIGNAL("clear()"),(self,_id));
      
    def is_empty (self):
      return self._id is None;
    def is_pinned (self):
      return self._pinned;
    def get_id (self):
      return self._id;

    def disable (self,disable=True):
      for w in (self._pin,self._label,self._close,self._refresh):
        w.setDisabled(disable);
    def enable (self,enable=True):
      self.disable(not enable);
    
    def set_content (self,widget,name,_id,refresh=False,reparent=False,pin=None,disable=False):
      self._label.setText(name);
      self._pin.show();
      self._close.show();
      (refresh and self._refresh.show()) or self._refresh.hide();
      self._id = _id;
      pin is not None and self._pin.setOn(pin);
      # set widget
      self._widget = widget;
      if reparent:
        widget.reparent(self._wtop);
      self._top_lo.addWidget(widget);
      self.disable(disable);
  
  class GridRow (QSplitter):
    def __init__(self,parent):
      QSplitter.__init__(self,QSplitter.Horizontal,parent);
      self._cells = [];
    def cells (self):
      return self._cells;
      
  def __init__ (self,parent,max_nx=4,max_ny=4):
    self._topgrid = QSplitter(QSplitter.Vertical,parent);
    self.max_nx     = max_nx;
    self.max_ny     = max_ny;
    self.max_items  = max_nx*max_ny;
    self._rows      = [];
    self._cellmap   = {};
    # possible layout formats (nrow,ncol)
    self._layouts = [(0,0),(1,1)];
    for i in range(2,self.max_nx+1):
      self._layouts += [(i,i-1),(i,i)];
    # create cells matrix
    for i in range(self.max_ny):
      row = self.GridRow(self._topgrid);
      row.hide();
      self._rows.append(row);
      for i in range(self.max_nx):
        cell = self.Cell(row);
        row._cells.append(cell);
        self.wtop().connect(cell.wtop(),PYSIGNAL("clear()"),self._clear_cell);
    # prepare layout
    self.set_layout(0);
  
  # changes current layout scheme
  def set_layout (self,nlo):
    self._cur_layout_num = nlo;
    (nrow,ncol) = self._cur_layout = self._layouts[nlo];
    for row in self._rows[:nrow]:
      for cell in row.cells()[:ncol]:
        cell.show();
      for cell in row.cells()[ncol:]:
        cell.hide();
      row.show();
    for row in self._rows[nrow:]:
      row.hide();
    
  # returns top-level widget
  def wtop   (self):
    return self._topgrid;
    
  # finds cell matching id, or None for none
  def find_cell (self,cell_id):
    return self._cellmap.get(cell_id,None);
    
  # finds a free cell if one is available
  # returns Cell object, or None if everything is full
  # adds cell_id to cell map
  def reserve_cell (self):
    (nrow,ncol) = self._cur_layout;
    # find free space in layout
    for icol in range(ncol):
      for row in self._rows[:nrow]:
        cell = row.cells()[icol];
        if cell.is_empty():
          return cell;
        if not cell.is_pinned():
          cell.clear();
          return cell;
    # current layout is full: proceed to next layout 
    nlo = self._cur_layout_num+1;
    if nlo >= len(self._layouts):
      return None;
    self.set_layout(nlo);
    return self.reserve_cell();

  def reserve_or_find_cell(self,cell_id):
    cell = self.find_cell(cell_id);
    if cell is None:
      cell = self.reserve_cell();
    return cell;

  def _clear_cell (self,cell,cell_id):
    del self._cellmap[cell_id];
    self.rearrange_cells();
      
  # rearranges cells by getting rid of empty rows and columns
  def rearrange_cells (self):
    nrow = 0;
    ncol = 0;
    # find max dimensions of non-empty cells
    for (irow,row) in enumerate(self._rows):
      for (icell,cell) in enumerate(row.cells()):
        if not cell.is_empty():
          nrow = max(nrow,irow);
          ncol = max(ncol,icol);
    # find suitable layout
    for (i,(nr,nc)) in enumerate(self._layouts):
      if nr >= nrow and nc >= ncol:
        self.set_layout(i);
        break;
    else:
      raise RuntimeError,"failed to find a suitable layout";
  
class GriddedWorkspace (object):
  def __init__ (self,parent,max_nx=4,max_ny=4):
    self._maintab = QTabWidget(parent);
    self.max_nx = max_nx;
    self.max_ny = max_ny;
    self._pages = [];
    self.add_page();
  def wtop(self):
    return self._maintab;
  def add_page(self):
    page = GriddedPage(self._maintab,max_nx=self.max_nx,max_ny=self.max_ny);
    page.wtop()._page = page;
    self._pages.append(page);
    self._maintab.addTab(page.wtop(),str(len(self._pages)));
    return page;
    
  def current_page (self):
    return self._maintab.currentPage()._page;
    
  def reserve_or_find_cell(self,cell_id):
    cell = self.current_page().reserve_or_find_cell(cell_id);
    if cell is None:
      return self.add_page().reserve_or_find_cell(cell_id);
    return cell;
    

class NodeList (dict):
  NodeAttrs = ('name','class','children');
  class Node (object):
    def __init__ (self,ni):
      self.nodeindex = ni;
      self.name = None;
      self.classname = None;
      self.children = [];
      self.parents  = [];
      
  # initialize from a MEQ-produced nodelist
  def __init__ (self,meqnl):
    # check that all list fields are correct
    num = len(meqnl.nodeindex);
    for f in self.NodeAttrs:
      if f not in meqnl:
        raise ValueError,"bad nodelist record: missing "+f+" field";
      if len(meqnl[f]) != num:
        raise ValueError,"malformed nodelist record: len(%s)=%d, expected %d"%(f,len(meqnl[f]),num);
    # form sequence of iterators
    iter_name     = iter(meqnl.name);
    iter_class    = iter(meqnl['class']);
    iter_children = iter(meqnl.children);
    # iterate over all nodes in list
    for ni in meqnl.nodeindex:
      # insert node into list (or use old one: may have been inserted below)
      node = self.setdefault(ni,self.Node(ni));
      node.name      = iter_name.next();
      node.classname = iter_class.next();
      children  = iter_children.next();
      if isinstance(children,dict):
        node.children = tuple(children.iteritems());
      else:
        node.children = tuple(enumerate(children));
      # for all children, init node entry in list (if necessary), and
      # add ourselves to parent list
      for (i,ch_ni) in node.children:
        self.setdefault(ch_ni,self.Node(ch_ni)).parents.append(ni);
    # generate list of root nodes
    self._rootnodes = [];
    for (ni,node) in self.iteritems():
      if not node.parents:
        self._rootnodes.append(ni)
        
  # return list of root nodes
  def rootnodes (self):
    return self._rootnodes;

# return True if this is a valid NodeList
def is_valid_nodelist (nodelist):
  for f in ('nodeindex',) + NodeList.NodeAttrs:
    if f not in nodelist:
      return False;
  return True;
    

class TreeBrowser (object):
  def __init__ (self,parent,mqs):
    self._mqs = mqs;
    self._splitter = QSplitter(QSplitter.Horizontal,parent);
    self._nl_vbox = QVBox(self._splitter);
    self._nl_control = QWidget(self._nl_vbox);
    self._nl_control_lo = QHBoxLayout(self._nl_control);
    # add refresh button
    self._nl_update = QToolButton(self._nl_control);
    self._nl_update.setIconSet(QIconSet(pixmaps.refresh.pm()));
    self._nl_update.setAutoRaise(True);
    #    self._nl_update.setMinimumWidth(30);
    #    self._nl_update.setMaximumWidth(30);
    self._nl_control_lo.addWidget(self._nl_update);
    self._nl_label = QLabel("Tree Browser",self._nl_control);
    self._nl_control_lo.addWidget(self._nl_label);
    self._nl_control_lo.addStretch();
    QObject.connect(self._nl_update,SIGNAL("clicked()"),self._request_nodelist);
    # node list
    self._nlv = QListView(self._nl_vbox);
    self._nlv.addColumn('node');
    self._nlv.addColumn('class');
    self._nlv.addColumn('index');
    self._nlv.setRootIsDecorated(True);
    self._nlv.setTreeStepSize(12);
    # self._nlv.setSorting(-1);
    self._nlv.setResizeMode(QListView.NoColumn);
    for icol in range(4):
      self._nlv.setColumnWidthMode(icol,QListView.Maximum);
    self._nlv.setFocus();
    self._nlv.connect(self._nlv,SIGNAL('expanded(QListViewItem*)'),
                      self._expand_node);
    self._nlv.connect(self._nlv,SIGNAL('clicked(QListViewItem*)'),
                      self._node_clicked);
    # workspace
    self._gw = GriddedWorkspace(self._splitter);
    
    self._splitter.setSizes([100,200]);
    
    self.nodelist = None;
    self._wait_nodestate = {};
 
  def wtop (self):
    return self._splitter;
    
  def clear (self):
    self._nlv.clear();
  def connected (self,conn):
    self._nl_update.setDisabled(not conn);

  def _request_nodelist (self):
#    self._nl_update.setDisabled(True);
    self.nodelist = None;
    rec = srecord(dict.fromkeys(NodeList.NodeAttrs,True));
    rec.nodeindex = True;
    self._mqs.meq('Get.Node.List',rec,wait=False);
    
  def make_node_item (self,node,name,parent,after):
    item = QListViewItem(parent,after,name,' '+node.classname,' '+str(node.nodeindex));
    item._node = node;
    if node.children:
      item.setExpandable(True);
    return item;

  def update_nodelist (self,nodelist):
#    self._nl_update.setDisabled(False);
    if self.nodelist is None:
      # reset the nodelist view
      self._nlv.clear();
      all_item  = QListViewItem(self._nlv,"All Nodes");
      all_item._all_nodes = True;
      all_item.setExpandable(True);
      rootitem  = item = QListViewItem(self._nlv,all_item,"Root Nodes");
      rootitem._expanded = True;
      for ni in nodelist.rootnodes():
        node = nodelist[ni];
        item = self.make_node_item(node,node.name,rootitem,item);
      self._nlv.setOpen(rootitem,True);
      self.nodelist = nodelist;
      
  def update_node_state(self,value):
    ni = value.nodeindex;
    cell = self._wait_nodestate.get(value.nodeindex,None);
    if cell is not None:
      del self._wait_nodestate[value.nodeindex];
      cell._widget._rb.set_record(value);
      cell.enable();

  def _node_clicked (self,item):
    if hasattr(item,'_node'):
      ni = item._node.nodeindex;
      cell_id = (hiid('node.state'),ni);
      cell = self._gw.reserve_or_find_cell(cell_id);
      if cell.is_empty():
        rb = RecordBrowser(cell.wtop());
        rb.wtop()._rb = rb;
        cell.set_content(rb.wtop(),item._node.name,cell_id,refresh=True,disable=True);
        cell.wtop().connect(cell.wtop(),PYSIGNAL("refresh()"),self._refresh_state_cell);
      cell._node = item._node;
      self._refresh_state_cell(cell);
  
  def _refresh_state_cell (self,cell):
    ni = cell._node.nodeindex;
    self._wait_nodestate[ni] = cell;
    self._mqs.meq('Node.Get.State',srecord(nodeindex=ni),wait=False);
  
  def _expand_node (self,item):
    # populate when first opened
    if not hasattr(item,'_expanded'):
      i1 = item;
      if hasattr(item,'_all_nodes'):
        for (ni,node) in self.nodelist.iteritems():
          i1 = self.make_node_item(node,node.name,item,i1);
      elif hasattr(item,'_node'):
        for (key,ni) in item._node.children:
          node = self.nodelist[ni];
          name = str(key) + ": " + node.name;
          i1 = self.make_node_item(node,name,item,i1);
        item._expanded = True;

class meqserver_gui (app_proxy_gui):

  def __init__(self,app,*args,**kwargs):
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    self.dprint(2,"meqserver-specifc init"); 
    
    # add Tree browser panel
    self.treebrowser = TreeBrowser(self,app);
    self.maintab.insertTab(self.treebrowser.wtop(),"MeqTrees",1);
    
    # add Result Log panel
    self.resultlog = Logger(self,"node result log",limit=100);
    self.maintab.insertTab(self.resultlog.wtop(),"Result Log",2);
    self.resultlog.wtop()._default_iconset = QIconSet();
    self.resultlog.wtop()._default_label   = "Result Log";
    self.resultlog.wtop()._newres_iconset  = QIconSet(pixmaps.check.pm());
    self.resultlog.wtop()._newres_label    = "New Results";
    self.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    # add handler for result log
    self._add_ce_handler("node.result",self.ce_NodeResult);
    self._add_ce_handler("app.result.node.get.state",self.ce_NodeState);
    self._add_ce_handler("app.result.get.node.list",self.ce_LoadNodeList);
    self._add_ce_handler("hello",self.ce_Hello);
    self._add_ce_handler("bye",self.ce_Bye);
    
  def ce_Hello (self,ev,value):
    self.treebrowser.clear();
    self.treebrowser.connected(True);  
  def ce_Bye (self,ev,value):
    self.treebrowser.connected(False);  
  def ce_NodeState (self,ev,value):
    self.treebrowser.update_node_state(value);
  
  def ce_NodeResult (self,ev,value):
    self.treebrowser.update_node_state(value);
    if self.resultlog.enabled:
      txt = '';
      name = ('name' in value and value.name) or '<unnamed>';
      cls  = ('class' in value and value['class']) or '?';
      rqid = 'request_id' in value and value.request_id;
      txt = ''.join((name,' <',cls,'>'));
      if rqid:
        txt = ''.join((txt,' rqid:',str(rqid)));
      self.resultlog.add(txt,value,Logger.Event);
      wtop = self.resultlog.wtop();
      if self.maintab.currentPage() is not wtop:
        self.maintab.changeTab(wtop,wtop._newres_iconset,wtop._newres_label);
        
  def ce_LoadNodeList (self,ev,nodelist):
    if is_valid_nodelist(nodelist):
      self.nodelist = NodeList(nodelist);
      self.dprintf(2,"loaded %d nodes into nodelist\n",len(self.nodelist));
      self.treebrowser.update_nodelist(self.nodelist);
    else:
      self.dprint(2,"got nodelist but it is not valid, ignoring");
  
      
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop():
      self._reset_maintab_label(tabwin);
  
