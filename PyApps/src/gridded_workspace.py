#!/usr/bin/python

from qt import *
from dmitypes import *
import app_pixmaps as pixmaps
import app_proxy_gui 
from app_browsers import *
import weakref

dbg = verbosity(3,name='gw');

# ====== DataDroppableWidget ===================================================
# A metaclass implementing a data-droppable widget.
# Use, e.g., DataDroppableWidget(QToolButton) to create a class that
# subclasses QToolButton, handles data-drop events, and emits a
# dataItemDropped() signal.
#
def DataDroppableWidget (parent_class):
  class widgetclass (parent_class):
    def __init__ (self,*args):
      parent_class.__init__(self,*args);
      self.setAcceptDrops(True);
    # Drag objects must be text drags containing a UDI, originating from 
    # another widget (i.e., within the same app). The widget must implement a 
    # get_data_item(udi) method.
    def dragEnterEvent (self,ev):
      udi = QString();
      try: ev.accept(callable(ev.source().get_data_item) and QTextDrag.decode(ev,udi));
      except AttributeError: pass;
    # The text drag is decoded into a UDI, a data item is fetched from the 
    # source using get_data_item(udi), and a dataItemDropped() signal is 
    # emitted
    def dropEvent (self,ev):
      udi = QString();
      QTextDrag.decode(ev,udi);
      item = ev.source().get_data_item(str(udi));
      print 
      if item:
        self.emit(PYSIGNAL("dataItemDropped()"),(item,));
  return widgetclass;


# ====== DataDraggableListView =================================================
# A QListView implementing the dragObject() function as follows:
#   if the selected item has a _udi attribute, returns a text drag containing 
#   the udi.
class DataDraggableListView (QListView):
  def __init__ (self,*args):
    QListView.__init__(self,*args);
    self.setSelectionMode(QListView.Single);
  def dragObject (self):
    try:
      return QTextDrag(self.selectedItem()._udi,self);
    except AttributeError:
      return None;


# ====== GridDataItem ==========================================================
# represents a per-cell data item 
#
class GridDataItem (object):
  """Represents a DataItem that is displayed in a GridCell. This is meant to
  be constructed by data sources, and passed to the workspace for displaying.
  """;
  def __init__ (self,udi,name='',desc='',data=None,refresh=None,widgetclass=RecordBrowser):
    """the constructor initializes standard attributes:
    udi:      the Uniform DataItem ID   (e.g. "nodestate/<nodename>")
    name:     the name of the data item (e.g. the node name)
    desc:     the description           (e.g. 'node state')
    data:     content, None if not yet initialized
    refresh:  refresh function. (If not None, then the GridCell will have a 
              'refresh' button calling this function when pressed)
    widgetclass: a callable that will construct a widget for displaying this
              data item. Default is RecordBrowser. Must provide the following 
              interface:
              widgetclass(parent_widget,udi=udi): construct object
              obj.wtop():          return top-level Qt widget
              obj.set_data(data):  sets/updates the data item
    """;
    if self.refresh and not callable(self.refresh):
      raise ValueError,'refresh argument must be a callable';
    if not callable(widgetclass):
      raise ValueError,'widgetclass argument must be a callable';
    self.udi  = udi;
    self.name = name;
    self.desc = desc;
    self.data = data;
    self.refresh_func = refresh;
    self.widgetclass = widgetclass;
    self.cells = [];
  def refresh (self):
    return self.refresh_func and self.refresh_func();
  def attach_cell (self,cell):
    self.cell = cell;
    self.widget = self.widgetclass(cell.wtop(),udi=self.udi);
    if self.data is not None:
      self.widget.set_data(self.data);
    cell.set_content(self.widget.wtop(),self.name,subname=self.desc,cell_id=self.udi,
          refresh=(self.refresh_func is not None),disable=(self.data is None));
    if self.refresh_func is not None:
      QWidget.connect(cell.wtop(),PYSIGNAL("refresh()"),self.refresh);
  def update (self,data):
    self.data = data;
    self.widget.set_data(data);
    self.cell.enable();
  

# ====== GridCell ==============================================================
# manages one cell of a gridded workspace
#
class GridCell (object):
  # define top-level widget class to accept data drops
  TopLevelWidget = DataDroppableWidget(QWidget);
      
  def __init__ (self,parent):
    wtop = self._wtop = self.TopLevelWidget(parent);
    wtop.hide();
    top_lo = QVBoxLayout(self._wtop);
    control_box = self._control_box = QWidget(self._wtop);
    control_lo = QHBoxLayout(control_box);
    pin_is = QIconSet(pixmaps.pin_up.pm());
    pin_is.setPixmap(pixmaps.pin_down.pm(),QIconSet.Automatic,QIconSet.Normal,QIconSet.On);
    self._pin = pin = QToolButton(control_box);
    pin.setAutoRaise(True);
    pin.setToggleButton(True);
    pin.setIconSet(pin_is);
    QToolTip.add(pin,"pin (i.e. protect) or unpin this panel");
    # refresh button
    self._refresh = refresh = QToolButton(control_box);
    refresh.setIconSet(QIconSet(pixmaps.refresh.pm()));
    refresh.setAutoRaise(True);
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
    top_lo.addStretch(1);
    top_lo.addWidget(self._wstack,1000);
    top_lo.setResizeMode(QLayout.Minimum);
   
    control_box.setSizePolicy(hsp);
    control_box.hide();
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
  def set_id (self,_id):
    self._id = _id;
  def is_pinned (self):
    return self._pin.isOn();
  def set_pinned (self,state=True):
    self._pin.setOn(state);
    
  # highlights a cell
  # pass in a QColor, or True for default color, or False value to disable highlights
  def highlight (self,color=True):
    if color:
      if not isinstance(color,QColor):
        color = QColor(255,255,0);
      self._control_box.setPaletteBackgroundColor(color);
      map(lambda w:isinstance(w,QWidget) and w.setPaletteBackgroundColor(color),
            self._control_box.children());
    else:
      self._control_box.unsetPalette();
      map(lambda w:isinstance(w,QWidget) and w.unsetPalette(),
            self._control_box.children());

  def _dorefresh (self):
    self._widget.emit(PYSIGNAL("refresh()"),(self,));

  # wipe: deletes contents in preperation for inserting other content
  def wipe (self):
    dbg.dprint(5,'GridCell: wiping cell ',self._id);
    self.set_pinned(False);
    if self._widget:
      self._wstack.removeWidget(self._widget);
    self._widget = None;
    self._wstack.hide();
    self.wtop().emit(PYSIGNAL("wiped()"),(self,));
    self._id = None;

  # close(): wipe, hide everything, and emit a closed signal
  def close (self):
    dbg.dprint(5,'GridCell: clearing cell ',self._id);
    self.wipe();
    self._wtop.hide();
    self._control_box.hide();
    self._label.setText("(empty)");
    self._label1.setText("");
    self.wtop().emit(PYSIGNAL("closed()"),(self,));

  def disable (self,disable=True):
    for w in (self._label,self._label1,self._refresh):
      w.setDisabled(disable);
  def enable (self,enable=True):
    self.disable(not enable);

  def set_content (self,widget,name,subname='',cell_id=None,refresh=False,pin=None,disable=False):
    self.set_id(cell_id);
    self._label.setText(name);
    self._label1.setText(subname);
    self._control_box.show();
    if refresh: self._refresh.show();
    else:       self._refresh.hide();
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

    
# ====== GriddedPage ===========================================================
# manages one page of a gridded workspace
#
class GriddedPage (object):
  class GridRow (QSplitter):
    def __init__(self,parent):
      QSplitter.__init__(self,QSplitter.Horizontal,parent);
      self._cells = [];
    def cells (self):
      return self._cells;
      
  def __init__ (self,gw,parent_widget,max_nx=4,max_ny=4):
    self._topgrid = QSplitter(QSplitter.Vertical,parent_widget);
    self.max_nx     = max_nx;
    self.max_ny     = max_ny;
    self.max_items  = max_nx*max_ny;
    self._rows      = [];
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
        QWidget.connect(cell.wtop(),PYSIGNAL("closed()"),self._clear_cell);
        cell._drop_slot = curry(gw.add_data_cell,cell=weakref.proxy(cell));
        QWidget.connect(cell.wtop(),PYSIGNAL("dataItemDropped()"),
                        cell._drop_slot);
    # prepare layout
    self.set_layout(0);
    
  def num_layouts (self):
    return len(self._layouts);
  def current_layout (self):
    return (self._cur_layout_num,) + self._cur_layout;
  
  # changes current layout scheme
  def set_layout (self,nlo):
    (nrow,ncol) = self._cur_layout = self._layouts[nlo];
    self._cur_layout_num = nlo;
    print "setting layout:",self._cur_layout;
    for row in self._rows[:nrow]:
      for cell in row.cells()[:ncol]: 
        # if not cell.is_empty(): 
        cell.show();
      for cell in row.cells()[ncol:]: cell.hide();
      row.show();
    for row in self._rows[nrow:]:
      row.hide();
    self.align_layout();
    # emit signal for change of layout
    self.wtop().emit(PYSIGNAL("layoutChanged()"),(nlo,len(self._layouts),nrow,ncol));
    return self._cur_layout;
    
  # increments current layout scheme by one (i.e. adds more windows)
  def next_layout (self):
    try: return self.set_layout(self._cur_layout_num+1);
    except IndexError: 
      return None;
      
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
      map(lambda cell:cell.close(),row.cells());
    
  # Finds a free cell if one is available, switches to the next layout
  # as needed.
  # Returns Cell object, or None if everything is full
  # If new=False, tries to reuse unpinned cells before switching layouts
  # If new=True,  does not reuse cells
  def find_cell (self,new=False):
    # loop over layouts until we find a cell (or run out of layouts)
    while True:
      (nrow,ncol) = self._cur_layout;
      # find free space in layout
      for icol in range(ncol):
        for row in self._rows[:nrow]:
          cell = row.cells()[icol];
          if cell.is_empty():
            return cell;
      # no free space, try to find an unpinned cell (starting from the back)
      if not new:
        for icol in range(ncol-1,-1,-1):
          for irow in range(nrow-1,-1,-1):
            cell = self._rows[irow].cells()[icol];
            if not cell.is_pinned():
              cell.wipe();
              return cell;
      # current layout is full: proceed to next layout
      if not self.next_layout():
        return None;

  def _clear_cell (self,cell):
    # if a cell is closed and layout is not empty, rearrange the layout
    if self._cur_layout_num:
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

# ====== GriddedWorkspace ======================================================
# implements a multi-page, multi-panel viewing grid
#
class GriddedWorkspace (object):
  # define a toolbutton that accepts data drops
  DataDropButton = DataDroppableWidget(QToolButton);
        
  def __init__ (self,parent,max_nx=4,max_ny=4,use_hide=None):
    # dictionary of active dataitems
    self._dataitems = {};
    # list of highlighted cells
    self._highlights = [];
    # highlight color
    self._highlight_color = QApplication.palette().active().highlight();
  
    self._maintab = QTabWidget(parent);
    self._maintab.setTabPosition(QTabWidget.Top);
    QWidget.connect(self._maintab,SIGNAL("currentChanged(QWidget*)"),self._set_layout_button);
    self.max_nx = max_nx;
    self.max_ny = max_ny;
    # set of parents for corners of the maintab (added on demand when GUI is built)
    self._tb_corners = {};
    #------ add page
    newpage = self.add_tool_button(Qt.TopLeft,pixmaps.tab_new.pm(),
        tooltip="open new page. You can also drop data items here.",
        class_=self.DataDropButton,
        click=self.add_page);
    newpage._dropitem = curry(self.add_data_cell,newpage=True);
    QWidget.connect(newpage,PYSIGNAL("dataItemDropped()"),
        newpage._dropitem);
    #------ new panels button
    self._new_panel = self.add_tool_button(Qt.TopLeft,pixmaps.view_right.pm(),
        tooltip="add more panels to this page. You can also drop data items here.",
        class_=self.DataDropButton,
        click=self._add_more_panels);
    self._new_panel._dropitem = curry(self.add_data_cell,newcell=True);
    QWidget.connect(self._new_panel,PYSIGNAL("dataItemDropped()"),
        self._new_panel._dropitem);
    #------ align button
    self.add_tool_button(Qt.TopLeft,pixmaps.view_split.pm(),
        tooltip="align panels on this page",
        click=self._align_grid);
    #------ remove page
    self.add_tool_button(Qt.TopRight,pixmaps.tab_remove.pm(),
        tooltip="remove this page",
        click=self.remove_current_page);
    # init first page
    self.add_page();
  
      
  def add_tool_button (self,corner,pixmap,tooltip=None,click=None,
                        leftside=False,class_=QToolButton):
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
    button = class_(layout.mainWidget());
    button._gw = weakref.proxy(self);
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
    page = GriddedPage(self,self._maintab,max_nx=self.max_nx,max_ny=self.max_ny);
    page.wtop()._page = page;
    if name is None:
      name = 'Page '+str(self._maintab.count()+1);
    self._maintab.addTab(page.wtop(),name);
    self._maintab.setCurrentPage(self._maintab.count()-1);
    QWidget.connect(page.wtop(),PYSIGNAL("layoutChanged()"),self._set_layout_button);
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
    self.current_page().rearrange_cells();
    self.current_page().align_layout();
  def _add_more_panels (self):
    print "adding more panels";
    self.current_page().next_layout();
  def _set_layout_button (self):
    page = self.current_page();
    (nlo,nx,ny) = page.current_layout();
    self._new_panel.setDisabled(nlo >= page.num_layouts());
  def clear (self):
    dbg.dprint(5,'GriddedWorkspace: clearing');
    self._maintab.page(0)._page.clear();
    for p in range(1,self._maintab.count()):
      page = self._maintab.page(p);
      page._page.clear();
      if p:
        self._maintab.removePage(page);
  # highlights specfic cell, removes highlights from other cells
  def highlight_cell (self,cell):
    # remove highlights from current list
    for c in self._highlights:
      if c() and c() is not cell:
        c().highlight(False);
    # add highlight
    cell.highlight(self._highlight_color);
    self._highlights = [ weakref.ref(cell) ];
  # Adds a data cell with the given item
  #   cell:    if not None, must be a cell to which item will be added
  #   newpage: if True, creates a new page wtih the data cell
  #   newcell: if True, creates a new display panel rather than reusing
  #            an existing unpinned panel
  def add_data_cell (self,item,cell=None,newcell=False,newpage=False):
    print 'adding',item,'to cell',cell;
    if newpage:
      self.add_page();
    # If we're already displaying this item, then either update its contents
    # (if supplied), or initiate a refresh call
    item0 = self._dataitems.setdefault(item.udi,item);
    if item0 is not item:
      if item.data is None:  
        item0.refresh();
      else: 
        item0.update(di.data);
      self._maintab.setCurrentPage(item0._pageindex);
      # highlight the cell
      self.highlight_cell(item0.cell);
    # else we've just inserted a new item, create a cell for it
    else:
      # create new cell (and, possibly, a new page)
      cell = cell or self.current_page().find_cell(new=newcell) \
                  or self.add_page().find_cell();
      item.attach_cell(cell);
      # ask for a refresh
      item.refresh();
      # when cell is wiped, _cell_wiped will be called to delete the data item
      QWidget.connect(cell.wtop(),PYSIGNAL("wiped()"),self._cell_wiped);
      item._pageindex = self._maintab.currentPageIndex();
      self.wtop().updateGeometry();
      self.highlight_cell(cell);
    self.wtop().emit(PYSIGNAL("addedCell()"),(item.udi,item));
  # updates a data cell, if it is known
  def update_data_cell (self,udi,data):
    if udi in self._dataitems:
      self._dataitems[udi].update(data);
  # removes a data cell
  def remove_data_cell (self,udi):
    if udi in self._dataitems:
      # this emits a wiped() signal, thus calling _cell_wiped();
      self._dataitems[udi].cell.close();  
    self.wtop().emit(PYSIGNAL("removedCell()"),(udi,));
  # slot, called when a cell widget is removed, to remove the data item
  def _cell_wiped (self,cell):
    if cell.get_id() in self._dataitems:
      del self._dataitems[cell.get_id()];
