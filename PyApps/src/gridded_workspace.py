#!/usr/bin/python

from qt import *
from dmitypes import *
import app_pixmaps as pixmaps
import app_proxy_gui 

dbg = verbosity(3,name='gw');

class GridCell (object):
  def __init__ (self,parent):
    wtop = self._wtop = QWidget(parent);
#    self._wtop = QVBox(parent,"gridcell.wtop");
    wtop.hide();
    top_lo = QVBoxLayout(self._wtop);
#    control_box = QWidget(self._wtop,"controlbox");
    control_box = self._control_box = QWidget(self._wtop);
    control_lo = QHBoxLayout(control_box);
    # control_lo.setResizeMode(QLayout.Fixed);
    # pin button
    pin_is = QIconSet(pixmaps.pin_up.pm());
    pin_is.setPixmap(pixmaps.pin_down.pm(),QIconSet.Automatic,QIconSet.Normal,QIconSet.On);
    self._pin = pin = QToolButton(control_box);
    pin.setAutoRaise(True);
    pin.setToggleButton(True);
    pin.setIconSet(pin_is);
#    pin.hide();
    QToolTip.add(pin,"pin (i.e. protect) or unpin this panel");
    # refresh button
    self._refresh = refresh = QToolButton(control_box);
    refresh.setIconSet(QIconSet(pixmaps.refresh.pm()));
    refresh.setAutoRaise(True);
#    refresh.hide();
    QObject.connect(refresh,SIGNAL("clicked()"),self._dorefresh);
    QToolTip.add(self._refresh,"refresh contents of this panel");
    # label
    self._label = QLabel("(empty)",control_box);
    self._label.setFont(app_proxy_gui.defaultBoldFont());
    self._label1 = QLabel("",control_box);
    hsp = QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed)
    # self._label.setSizePolicy(hsp);
    self._label1.setSizePolicy(hsp);
    # close button
    self._close = close = QToolButton(control_box);
    close.setIconSet(QIconSet(pixmaps.cancel.pm()));
    close.setAutoRaise(True);
#    close.setDisabled(True);
    QToolTip.add(close,"close this panel");
    QObject.connect(close,SIGNAL("clicked()"),self.close);
    
    control_lo.addWidget(pin);
    control_lo.addWidget(refresh);
    control_lo.addSpacing(10);
    control_lo.addWidget(self._label);
    control_lo.addSpacing(10);
    control_lo.addWidget(self._label1);
    control_lo.addStretch();
    control_lo.addWidget(close);

    self._wstack = QWidgetStack(self._wtop);
    top_lo.addWidget(control_box,0);
#    top_lo.setStretchFactor(control_lo,0);
    top_lo.addStretch(1);
    top_lo.addWidget(self._wstack,1000);
    top_lo.setResizeMode(QLayout.Minimum);
   
    control_box.setSizePolicy(hsp);
    control_box.hide();
#    self._wstack.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding));
    self._wtop.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding));
    self._id     = None;
    self._widget = None;

  def wtop (self):
    return self._wtop;
  def hide (self):
    self._wtop.hide();
  def show (self):
    self._wtop.show();
  def is_empty (self):
    return self._id is None;
  def get_id (self):
    return self._id;
  def is_pinned (self):
    return self._pin.isOn();
  def set_pinned (self,state=True):
    self._pin.setOn(state);

  def _dorefresh (self):
    self._widget.emit(PYSIGNAL("refresh()"),(self,));

  # wipe: deletes contents in preperation for inserting other content
  def wipe (self):
    dbg.dprint(5,'GridCell: wiping cell ',self._id);
    self.set_pinned(False);
    if self._widget:
      self._wstack.removeWidget(self._widget);
    self._widget = self._id = None;
    self._wstack.hide();

  # close(): wipe, hide everything, and emit a closed signal
  def close (self,signal=True):
    dbg.dprint(5,'GridCell: clearing cell ',self._id);
    old_id = self._id;
    self.wipe();
    self._wtop.hide();
    self._control_box.hide();
#    self._pin.hide();
#    self._close.setDisabled(True);
#    self._refresh.hide();
    self._label.setText("(empty)");
    self._label1.setText("");
    if signal:
      self.wtop().emit(PYSIGNAL("closed()"),(self,old_id));
    self._widget = self._id = None;

  def disable (self,disable=True):
    for w in (self._pin,self._label,self._close,self._refresh):
      w.setDisabled(disable);
  def enable (self,enable=True):
    self.disable(not enable);

  def set_content (self,widget,name,_id,subname='',refresh=False,reparent=False,pin=None,disable=False):
    print self,'set_content',widget;
    self._label.setText(name);
    self._label1.setText(subname);
    self._control_box.show();
#    self._pin.show();
#    self._close.show();
    if refresh: self._refresh.show();
    else:       self._refresh.hide();
    self._id = _id;
    pin is not None and self._pin.setOn(pin);
    # set widget
    self._wstack.addWidget(widget);
    self._wstack.raiseWidget(widget);
    if self._widget:
      self._wstack.removeWidget(self._widget);
    self._widget = widget;
    self._wtop.updateGeometry();
    self._wstack.show();
    self.disable(disable);
    self._wtop.show();
    
  def wcontent (self):
    return self._widget;
    

class GriddedPage (object):
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
        cell = GridCell(row);
        row._cells.append(cell);
        self.wtop().connect(cell.wtop(),PYSIGNAL("closed()"),self._clear_cell);
    # prepare layout
    self.set_layout(0);
  
  # changes current layout scheme
  def set_layout (self,nlo):
    self._cur_layout_num = nlo;
    (nrow,ncol) = self._cur_layout = self._layouts[nlo];
    for row in self._rows[:nrow]:
      for cell in row.cells()[:ncol]: 
        # if not cell.is_empty(): 
        cell.show();
      for cell in row.cells()[ncol:]: cell.hide();
      row.show();
    for row in self._rows[nrow:]:
      row.hide();
    self.align_layout();
  
  def align_layout (self):
    xsizes = [1000]*self.max_nx;
    map(lambda row:row.setSizes(xsizes),self._rows);
    self._topgrid.setSizes([1000]*self.max_ny);
    
  # returns top-level widget
  def wtop   (self):
    return self._topgrid;
    
  def clear (self):
    dbg.dprint(2,'GriddedPage: clearing');
    self.set_layout(0);
    for row in self._rows:
      dbg.dprint(2,'GriddedPage: clearing row',row);
      map(lambda c:c.close(signal=False),row.cells());
    self._cellmap = {};
    
  # finds cell matching id, or None for none
  def find_cell (self,cell_id):
    return self._cellmap.get(cell_id,None);
    
  # finds a free cell if one is available
  # returns Cell object, or None if everything is full
  # adds cell_id to cell map
  def reserve_cell (self,cell_id):
    (nrow,ncol) = self._cur_layout;
    # find free space in layout
    for icol in range(ncol):
      for row in self._rows[:nrow]:
        cell = row.cells()[icol];
        if cell.is_empty():
          self._cellmap[cell_id] = cell;
          return cell;
    # no free space, try to find an unpinned cell (starting from the back)
    for icol in range(ncol-1,-1,-1):
      for irow in range(nrow-1,-1,-1):
        cell = self._rows[irow].cells()[icol];
        if not cell.is_pinned():
          del self._cellmap[cell.get_id()];
          cell.wipe();
          self._cellmap[cell_id] = cell;
          return cell;
    # current layout is full: proceed to next layout 
    nlo = self._cur_layout_num+1;
    if nlo >= len(self._layouts):
      return None;
    self.set_layout(nlo);
    return self.reserve_cell(cell_id);

  def reserve_or_find_cell(self,cell_id):
    cell = self.find_cell(cell_id);
    if cell is None:
      return self.reserve_cell(cell_id);
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
      for (icol,cell) in enumerate(row.cells()):
        if not cell.is_empty():
          nrow = max(nrow,irow);
          ncol = max(ncol,icol);
    nrow += 1;
    ncol += 1;
    # are they good for the current layout?
    if nrow == self._cur_layout[0] and ncol == self._cur_layout[1]:
      return;
    # find suitable layout
    for (i,(nr,nc)) in enumerate(self._layouts):
      if nr >= nrow and nc >= ncol:
        self.set_layout(i);
        break;
    else:
      raise RuntimeError,"failed to find a suitable layout";
  
class GriddedWorkspace (object):
  def __init__ (self,parent,max_nx=4,max_ny=4,use_hide=None):
    self._maintab = QTabWidget(parent);
    self._maintab.setTabPosition(QTabWidget.Top);
    
    self.max_nx = max_nx;
    self.max_ny = max_ny;
    self.add_page();
    # set of parents for corners of the maintab (added on demand)
    self._tb_corners = {};
    #------ align button
    self.add_tool_button(Qt.TopRight,pixmaps.view_split.pm(),
        tooltip="align child panels",
        click=self._align_grid);
    #------ add/remove tab        
    self.add_tool_button(Qt.TopLeft,pixmaps.tab_new.pm(),
        tooltip="open new browser page",
        click=self.add_page);
    self.add_tool_button(Qt.TopLeft,pixmaps.tab_remove.pm(),
        tooltip="remove this browser page",
        click=self.remove_current_page);
      
  def add_tool_button (self,corner,pixmap,tooltip=None,click=None,leftside=False):
    # create corner box on demand
    layout = self._tb_corners.get(corner,None);
    if not layout:
      parent = QWidget(self._maintab);
      self._maintab.setCornerWidget(parent,corner);
      if corner == Qt.TopLeft: # add extra space
        lo1 = QHBoxLayout(parent);
        parent = QWidget(parent);
        lo1.addWidget(parent);
        lo1.addSpacing(5);
      self._tb_corners[corner] = layout = QHBoxLayout(parent);
    # add button
    button = QToolButton(layout.mainWidget());
    if leftside:
      layout.insertWidget(0,button);
    else:
      layout.addWidget(button);
    button.setPixmap(pixmap);
    button.setAutoRaise(True);
    if tooltip:
      QToolTip.add(button,tooltip);
    if callable(click):
      QWidget.connect(button,SIGNAL("clicked()"),click);
    return button;
    
  def wtop (self):
    return self._maintab;
    
  def add_page (self,name=None):
    page = GriddedPage(self._maintab,max_nx=self.max_nx,max_ny=self.max_ny);
    page.wtop()._page = page;
    if name is None:
      name = 'Page '+str(self._maintab.count()+1);
    self._maintab.addTab(page.wtop(),name);
    self._maintab.setCurrentPage(self._maintab.count()-1);
    return page;
    
  def remove_current_page (self):
    page = self._maintab.currentPage()
    page._page.clear();
    # first page is cleared, never removed
    if self._maintab.currentPageIndex():
      self._maintab.removePage(page);
    
  def current_page (self):
    return self._maintab.currentPage()._page;
    
  def _align_grid (self):
    self.current_page().align_layout();
    
  def clear (self):
    dbg.dprint(5,'GriddedWorkspace: clearing');
    self._maintab.page(0)._page.clear();
    for p in range(1,self._maintab.count()):
      page = self._maintab.page(p);
      page._page.clear();
      if p:
        self._maintab.removePage(page);
    
  def reserve_or_find_cell(self,cell_id):
    cell = self.current_page().reserve_or_find_cell(cell_id);
    if cell is None:
      return self.add_page().reserve_or_find_cell(cell_id);
    return cell;

