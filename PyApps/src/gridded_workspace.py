#!/usr/bin/python

from qt import *
from dmitypes import *
import app_pixmaps as pixmaps
import app_proxy_gui 
import weakref
import sets
import re
import gc
import types

_dbg = verbosity(0,name='gw');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


_reg_viewers = {};

# registers a viewer plug-in for the specified type
#
# a viewer plug-in must provide the following interface:
#
#

def registerViewer (tp,viewer,dmitype=None,priority=0):
  """Registers a viewer for the specified type:
    registerViewer(datatype,viewer);
  The 'viewer' argument must be a class (or callable) providing the following 
  interface:
    viewer.viewer_name 
      # (optional static attribute) returns "official name" of this 
      # viewer class, for use in menus and such. If not defined, the classname 
      # (viewer.__name__) will be used instead. 
    viewer.is_viewable(data); 
      # (optional static method) checks if a specific data item (of the 
      # registered type) is viewable in this viewer or not. If not defined, 
      # True is assumed.
    viewer.icon(); 
      # (optional static method) returns a QIconSet for this viewer
    vo = viewer(parent_widget,dataitem=None,**opts); 
      # construct a viewer object. A dataitem (GridDataItem class) object 
      # may be supplied at this time, or set via set_data() below. See
      # GridDataItem below. Note that dataitem.data may be None if the 
      # object is not yet populated. 
      # **opts may be used to pass in optionalkeyword arguments on a 
      # per-viewer basis.
    vo.wtop();
      # return top-level Qt widget of viewer object
    vo.set_data(dataitem,**opts);
      # sets/updates the content of the viewer. **opts may be used to pass 
      # in optional keyword arguments on a per-viewer basis.
    vo.add_data(dataitem,**opts); 
      # (optional method) adds another data object to the viewer. If 
      # multiple-object viewing is not supported, the viewer class should not
      # define this method. The method must return True if the object is
      # successfully added, or False if this cannot be done.
      
  The viewer object may also issue one Qt signal: PYSIGNAL("refresh()"), if
  a refresh of the data contents is requested. Note that the GridCell interface
  already provides a refresh button, so this signal is normally not needed.
  """;
  global _reg_viewers;
  _reg_viewers.setdefault((tp,dmitype),[]).append((priority,viewer));

def isViewableWith (arg,viewer):
  if type(arg) is type:
    return True;
  try: checker = viewer.is_viewable;
  except AttributeError: return True; 
  if callable(checker):
    return checker(arg);
  return True;

def isViewable (arg,dmitype=None):
  global _reg_viewers;
  # arg may specify a type or a data object
  if type(arg) is type:
    datatype = arg;
  else:
    datatype = type(arg);
    dmitype  = dmi_type(arg);
  for (tptuple,vlist) in _reg_viewers.iteritems():
    (tp,dmitp) = tptuple;
    # registered type must be a superclass of the supplied type;
    # registered dmi type must be either None or match the argument dmi type
    if issubclass(datatype,tp) and (dmitp is None or dmitp == dmitype):
      for (pri,viewer) in vlist:
        if isViewableWith(arg,viewer):
          return True;
  return False;

def getViewerList (arg,dmitype=None):
  global _reg_viewers;
  if arg is None:
    return [];
  # arg may specify a type or a data object
  if type(arg) is type:
    datatype = arg;
  else:
    datatype = type(arg);
    dmitype  = dmi_type(arg);
  viewer_list = [];
  # resolve data type (argument may be object or type)
  for (tptuple,vlist) in _reg_viewers.iteritems():
    # find viewers for this class
    (tp,dmitp) = tptuple;
    if issubclass(datatype,tp) and (dmitp is None or dmitp == dmitype):
      if type(arg) is type:  # if specified as type, add all
        viewer_list.extend(vlist);
      else: # if specified as object, check to see which are compatible
        viewer_list.extend([(pri,v) for (pri,v) in vlist if isViewableWith(arg,v)]);
  # sort by priority
  viewer_list.sort();
  return [ v for (pri,v) in viewer_list ];

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
      self._accept_drops_from_children = False;
    def setAcceptDropsFromChildren(self,value):
      self._accept_drops_from_children = value;
    # Drag objects must be text drags containing a UDI, originating from 
    # another widget (i.e., within the same app). The widget must implement a 
    # get_data_item(udi) method.
    def dragEnterEvent (self,ev):
      udi = QString();
      try: 
        wsrc = ev.source();
        try: 
          if not (callable(wsrc.get_data_item) and QTextDrag.decode(ev,udi)):
            return;
        except AttributeError: return;
        if not self._accept_drops_from_children:
          while wsrc:
            if wsrc is self:
              return;
            wsrc = wsrc.parent();
        ev.accept(True);
      except AttributeError: pass;
    # The text drag is decoded into a UDI, a data item is fetched from the 
    # source using get_data_item(udi), and a dataItemDropped() signal is 
    # emitted
    def dropEvent (self,ev):
      udi = QString();
      QTextDrag.decode(ev,udi);
      item = ev.source().get_data_item(str(udi));
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
    try: udi = self.selectedItem()._udi;
    except AttributeError:
      return None;
    return udi and QTextDrag(udi,self);

# ====== GridDataItem ==========================================================
# represents a per-cell data item 
#
class GridDataItem (object):
  """Represents a DataItem that is displayed in a GridCell. This is meant to
  be constructed by data sources, and passed to the workspace for displaying.
  """;
  def __init__ (self,udi,name='',desc='',data=None,datatype=None,
                refresh=None,viewer=None,viewopts={}):
    """the constructor initializes standard attributes:
    udi:      the Uniform DataItem ID   (e.g. "nodestate/<nodename>")
    name:     the name of the data item (e.g. the node name)
    desc:     the description           (e.g. "node state")
    data:     content, None if not yet initialized
    datatype: if content=None, may be used to specify which data type it will be
    refresh:  refresh function. (If not None, then the GridCell will have a 
              'refresh' button calling this function when pressed)
    viewer:   If None, a viewer will be selected from among the registered
              viewers for the data type. Otherwise, provide a callable 
              viewer plug-in. See registerViewer() for details.
    viewopts: dict (of dicts) of viewer options. 
              viewopts[None]         applies to all viewers,
              viewopts[viewer_class] applies to a specific class (overrides [None])
    """;
    if self.refresh and not callable(self.refresh):
      raise ValueError,'refresh argument must be a callable';
    self.udi  = udi;
    self.name = name;
    self.desc = desc;
    self.data = data;
    if viewopts is None:
      viewopts = {};
    self.viewopts = viewopts;
    self.refresh_func = refresh;
    # build list of compatible viewers
    self.viewer_list = getViewerList(datatype or data);
    # is a viewer also explicitly specifed?
    self.viewer = viewer;
    if viewer is None:
      if not self.viewer_list:
        raise TypeError,"no viewers registered and none specified";
      self.default_viewer = self.viewer_list[0];
    else:
      if not callable(viewer):
        raise TypeError,'viewer argument must be a callable';
      # prepend to list
      if viewer not in self.viewer_list:
        self.viewer_list.insert(0,viewer);
      self.default_viewer = viewer;
    self.cells = sets.Set();
  def refresh (self):
    self.refresh_func and self.refresh_func();
  def is_mutable (self):
    return self.refresh_func is not None;
  def attach_cell (self,cell):
    self.cells.add(cell);
  def detach_cell (self,cell):
    self.cells.discard(cell);
  def update (self,data):
    self.data = data;
    map(lambda cell:cell.update_data(self),self.cells);
  def highlight (self,enable=True):
    map(lambda cell:cell.highlight(enable),self.cells);
  # returns True if the specified viewer is already displaying this item
  def is_viewed_by (self,viewer):
    for c in self.cells:
      if c._viewer_class == viewer:
        return True;
    return False;
  # removes all cells from item
  def remove (self):
    # shallow-copy cells set, because cell.close() calls detach_cell, 
    # which modifies it
    map(lambda cell:cell.close(),self.cells.copy());

# ====== GridCell ==============================================================
# manages one cell of a gridded workspace
#
class GridCell (object):
  # define top-level widget class. This accepts data drops, and 
  # display context menus
  DataDroppableQWidget = DataDroppableWidget(QWidget);
  class TopLevelWidget (DataDroppableQWidget):
    def __init__ (self,*args):
      GridCell.DataDroppableQWidget.__init__(self,*args);
      self._menu = None;
    def set_context_menu (self,menu):
      self._menu = menu;
    def contextMenuEvent (self,ev):
      ev.accept();
      if self._menu:
        self._menu.exec_loop(ev.globalPos());
      
  def __init__ (self,parent):
    # init state
    self._viewer = self._viewer_widget = self._dataitem = None;
    self._refresh_func = lambda:None;
    
    self._highlight_colors = \
      (QApplication.palette().active().highlight(),\
       QApplication.palette().active().highlightedText()); \
    self._highlight = False;
    
    # init widgets
    wtop = self._wtop = self.TopLevelWidget(parent,'cell '+str(id(self))+' top');
    wtop.hide();
    top_lo = self._top_lo = QVBoxLayout(self._wtop);
    control_box = self._control_box = QWidget(self._wtop);
    control_lo = QHBoxLayout(control_box);
    # icon button
    self._iconbutton = iconbutton = QToolButton(control_box);
    iconbutton.setAutoRaise(True);
    QToolTip.add(iconbutton,"menu");
    QObject.connect(iconbutton,SIGNAL("clicked()"),self.show_popup_menu);
    # pin button
    pin_is = pixmaps.pin_up.iconset();
    pin_is.setPixmap(pixmaps.pin_down.pm(),QIconSet.Automatic,QIconSet.Normal,QIconSet.On);
    self._pin = pin = QToolButton(control_box);
    pin.setAutoRaise(True);
    pin.setToggleButton(True);
    pin.setIconSet(pin_is);
    QObject.connect(pin,SIGNAL("clicked()"),self._update_pin_menu);
    QToolTip.add(pin,"pin (i.e. protect) or unpin this panel");
    # float button
    self._float_btn = flt = QToolButton(control_box);
    flt.setAutoRaise(True);
    flt.setToggleButton(True);
    flt.setIconSet(pixmaps.float_window.iconset());
    QObject.connect(flt,SIGNAL("toggled(bool)"),self.float_cell);
    QToolTip.add(flt,"float this cell in a separate window");
    # refresh button
    self._refresh = refresh = QToolButton(control_box);
    refresh.setIconSet(pixmaps.refresh.iconset());
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
    close.setIconSet(pixmaps.cancel.iconset());
    close.setAutoRaise(True);
    QToolTip.add(close,"close this panel");
    QObject.connect(close,SIGNAL("clicked()"),self.close);
    # create menu
    self._viewers_menu = QPopupMenu(wtop);
    self._menu = menu = QPopupMenu(wtop);
    
    # add buttons and labels to the control bar layout
    control_lo.addWidget(iconbutton);
    control_lo.addWidget(pin);
    control_lo.addWidget(flt);
    control_lo.addWidget(refresh);
    control_lo.addSpacing(10);
    control_lo.addWidget(self._label);
    control_lo.addSpacing(10);
    control_lo.addWidget(self._label1);
    control_lo.addStretch();
    control_lo.addWidget(close);

    # add a widget holder (for viewer) to the top-level layout
    top_lo.addWidget(control_box,0);
    top_lo.addStretch(1);
#    top_lo.addWidget(self._viewer_holder,1000);
    top_lo.setResizeMode(QLayout.Minimum);
   
    # other init
    control_box.setSizePolicy(hsp);
    control_box.hide();
    self._wtop.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding));
    
  # destructor
  def __del__ (self):
    if self._dataitem:
      self._dataitem.detach_cell(self);

  def wtop (self):
    return self._wtop;
  def wcontent (self):
    try: return self._viewer.wtop();
    except AttributeError: return None;
  def hide (self):
    self._wtop.hide();
  def show (self):
    self._wtop.show();
  def is_empty (self):
    return self._dataitem is None;
  def is_pinned (self):
    return self._pin.isOn();
  def set_pinned (self,state=True):
    self._pin.setOn(state);
    self._update_pin_menu(state);
  def viewer (self):
    return self._viewer;
    
  def rebuild_menu (self):
    self._menu.clear();
    # self._m_viewer = menu.insertItem("Viewer");
    udi = self._dataitem and self._dataitem.udi;
    if udi:
      self._m_udi     = self._menu.insertItem(udi);
      self._menu.insertSeparator();
    self._m_viewers = self._menu.insertItem("View using",self._viewers_menu);
    self._m_pin     = self._menu.insertItem(self._pin.iconSet(),(self.is_pinned() and "Unpin") or "Pin",self._toggle_pinned_state);
    self._menu.setItemChecked(self._m_pin,self.is_pinned());
    if self._dataitem.is_mutable():
      self._menu.insertItem(self._refresh.iconSet(),"Refresh",self._dorefresh);
    self._menu.insertItem(self._close.iconSet(),"Close panel",self.close);
    self.wtop().set_context_menu(self._menu);
    
  def udi (self):
    return self._dataitem and self._dataitem.udi;
  def is_parent_of (self,udi):
    my_udi = self.udi();
    return my_udi and re.match(my_udi+'/?',udi);

  def show_popup_menu (self,point=None):
    self._menu.exec_loop(point or QCursor.pos());

  def _toggle_pinned_state (self):
    self.set_pinned(not self.is_pinned());
    
  def _update_pin_menu (self,state=None):
    try: pinid = self._m_pin;
    except: return;
    if state is None:
      state = self.is_pinned();
    self._menu.setItemChecked(pinid,state);
    self._menu.changeItem(pinid,(state and "Unpin") or "Pin");
    
  # highlights a cell
  # pass in a QColor, or True for default color, or False value to disable highlights
  def highlight (self,color=True):
#      wlist = [self._control_box] + self._control_box.children();
    wlist = (self._control_box,self._label,self._label1);
    if color:
      color = self._highlight_colors;
      for w in wlist:
        if isinstance(w,QWidget):
          w.setPaletteBackgroundColor(color[0]);
          w.setPaletteForegroundColor(color[1]);
      self._highlight = True;
    else:
      for w in wlist:
        if isinstance(w,QWidget):
          w.unsetPalette();
      self._highlight = False;

  def _dorefresh (self):
    self._refresh_func();
    
  def _remove_viewer (self):
    self._viewer = None;
    if self._viewer_widget:
      dum = QWidget();
      self._viewer_widget.reparent(dum, 0, QPoint())
      self._viewer_widget = None;

  # wipe: deletes contents in preperation for inserting other content
  def wipe (self):
    _dprint(5,'GridCell: wiping cell ',id(self));
    self.set_pinned(False);
    self._remove_viewer();
    if self._dataitem:
      self._dataitem.detach_cell(self);
    self._dataitem = None;
    self._refresh_func = lambda:None;
#    self._viewer_holder.hide();
    self.wtop().emit(PYSIGNAL("wiped()"),(self,));
    self.wtop().set_context_menu(None);

  # close(): wipe, hide everything, and emit a closed signal
  def close (self):
    _dprint(5,'GridCell: clearing cell ',id(self));
    self.wipe();
    self._wtop.hide();
    self._control_box.hide();
    self._label.setText("(empty)");
    self._label1.setText("");
    self.wtop().emit(PYSIGNAL("closed()"),(self,));

  def disable (self,disable=True):
    for w in (self._label,self._label1,self._refresh):
      w.setDisabled(disable);
    self.wtop().set_context_menu(None);
  def enable (self,enable=True):
    self.disable(not enable);
    self.wtop().set_context_menu(self._menu);
    
  MaxDescLen = 40;

  def set_data_item (self,dataitem,pin=None,viewer=None):
    _dprint(5,'GridCell.set_data_item(): content is',self._dataitem);
    if not self.is_empty():
      self.wipe();
    dataitem.attach_cell(self);
    self._dataitem = dataitem;
    self._label.setText(dataitem.name);
    desc = dataitem.desc;
    # trim desc to reasonable length
    if len(desc)>self.MaxDescLen:
      dd = desc.split('/');
      # remove second-to-last item until length is suitable
      while len(dd)>2 and sum(map(len,dd),len(dd)+3)>self.MaxDescLen:
        del dd[-2];
      if len(dd)>2:  # succeeded? replace with '...'
        dd.insert(-1,'...');
        desc = '/'.join(dd);
      else:          # fallback: terminate string
        desc = desc[:57]+'...';
    self._label1.setText(desc);
    # show the control box
    self._control_box.show();
    # set up the viewer
    self.change_viewer(viewer or dataitem.default_viewer);
    # setup refresh function and button
    if dataitem.is_mutable():
      self._refresh.show();
      self._refresh_func = dataitem.refresh_func;    
      QWidget.connect(self._viewer.wtop(),PYSIGNAL("refresh()"),self._refresh_func);
    else:
      self._refresh.hide();
      self._refresh_func = lambda:None;
    # setup pin button
    if pin is not None:
      self._pin.setOn(pin);
    # disable cell if no data yet
    self.disable(dataitem.data is None);
    
  class FloatingCell (QMainWindow):
    def __init__ (self,parent):
      fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
      fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title;
      QMainWindow.__init__(self,parent,"float",fl);
      self.setIcon(pixmaps.float_window.pm());
    def hideEvent (self,ev):
      _dprint(1,'hideEvent',ev);
      self.emit(PYSIGNAL("hidden()"),());
    
  def float_cell (self,enable=True):
    if enable:
      QToolTip.add(self._float_btn,"return view contents to cell");
      try: float_window = self._float_window;
      except AttributeError:
        self._float_window = float_window = self.FloatingCell(self.wtop());
        QObject.connect(float_window,PYSIGNAL("hidden()"),self.__unfloat_cell);
        self._float_label = QLabel("This viewer is now floating in a separate window.",self.wtop());
        self._float_label.setAlignment(Qt.AlignTop|Qt.AlignLeft|Qt.WordBreak);
        self._float_ret_btn = QPushButton(pixmaps.float_window.iconset(),"Return it here",self.wtop());
        QObject.connect(self._float_ret_btn,SIGNAL("clicked()"),self.unfloat_cell);
        self._top_lo.addWidget(self._float_label);
        self._top_lo.addWidget(self._float_ret_btn);
        self._top_lo.addStretch(1);
      caption = str(self._label.text()) + " * " + str(self._label1.text());
      float_window.setCaption(str(self._label.text()) + " * " + str(self._label1.text()));
      self._viewer_widget.reparent(float_window,0,QPoint(0,0));
      self._viewer_widget.emit(PYSIGNAL("reparent()"),(float_window,));
      float_window.setCentralWidget(self._viewer_widget);
      float_window.resize(self.wtop().size());
      float_window.show();
      self._float_label.show();
      self._float_ret_btn.show();
    else:
      try: 
        if not self._float_window.isHidden():
          self._float_window.hide();     # this causes unfloat_cell to be called
      except AttributeError: pass;
      
  def __unfloat_cell (self):
    _dprint(1,'unfloating cells');
    QToolTip.add(self._float_btn,"float this view in a separate window");
    dum = QWidget();
    self._float_label.hide();
    self._float_ret_btn.hide();
    # self._float_label.reparent(dum,0,QPoint(0,0));
    # self._float_ret_btn.reparent(dum,0,QPoint(0,0));
    # self._float_label = self._float_ret_btn = None;
    self._float_btn.setOn(False);
    self._remove_viewer();
    self.change_viewer(self._viewer_class);
    
  def unfloat_cell (self):  
    try: float_window = self._float_window;
    except AttributeError: return;
    if not float_window.isHidden(): 
      float_window.hide();              # this causes __unfloat_cell to be called
        
  def unfloat_cell (self):
    _dprint(1,'unfloating cells');
    QToolTip.add(self._float_btn,"return view contents to cell");
    self._remove_viewer();
    # self._viewer_widget.emit(PYSIGNAL("reparent()"),(self._wtop,));
    # self._top_lo.addWidget(self._viewer_widget,1000);
    # self._float_btn.setOn(False);
    try: float_window = self._float_window;
    except AttributeError: pass;
    else:
      if not float_window.isHidden():
        float_window.hide();
    
  def change_viewer (self,viewer_class,dum=None,viewopts={}):
             # note: dum argument is needed to make this function callable
             # from popupMenu(), since that passes an extra arg 
    self._wtop.hide();
    # build dict of extra viewer options
    vopts = viewopts.copy();
    vopts.update(self._dataitem.viewopts.get(None,{}));
    for (vclass,vo) in self._dataitem.viewopts.iteritems():
      _dprint(5,'GridCell.change_viewer:',vclass,viewer_class);
      if vclass and issubclass(viewer_class,vclass):
        vopts.update(vo);
    # create a viewer
    try:
      print self.wtop().name();
      viewer = viewer_class(self.wtop(),dataitem=self._dataitem,
                            context_menu=self._menu,**vopts);
    # catch failures
    except:
      ei = sys.exc_info();
      print 'Error creating a plug-in viewer of class',viewer_class,'for item',self._dataitem.udi;
      print 'Exception is:',ei;
      traceback.print_tb(ei[2]);
      if not self._viewer:
        txt = "(Error creating %s)"%str(viewer_class);
        self._viewer_widget = self._viewer = QLabel(txt,self.wtop());
        self._top_lo.addWidget(self._viewer_widget,1000);
        self._float_btn.setEnabled(False);
    else:
      self._float_btn.setEnabled(True);
      try: self._float_window.isHidden() or self._float_window.hide();
      except AttributeError: pass;
      self._remove_viewer();
      # insert new
      self._viewer_class = viewer_class;
      self._viewer = viewer;
      self._viewer_widget = widget = viewer.wtop();
      self._top_lo.addWidget(widget,1000);
      _dprint(5,'GridCell: widget',widget,'added');
      # connect displayDataItem() signal from viewer to be resent from top widget
      QWidget.connect(widget,PYSIGNAL("displayDataItem()"),
                      self.wtop(),PYSIGNAL("displayDataItem()"));
#      # add viewer widget to cell
#      self._wstack.addWidget(widget);
#      self._wstack.raiseWidget(widget);
      # create an icon set for the menu button
      try: icon = viewer_class.icon();
      except AttributeError: icon = pixmaps.magnify.iconset();
      self._iconbutton.setIconSet(icon);
      # rebuild the menu
      self.rebuild_menu();
      self._viewers_menu.clear();
      self._viewers_proc = [];
      if len(self._dataitem.viewer_list) > 1:
        for v in self._dataitem.viewer_list:
          # create entry for viewer
          name = getattr(v,'viewer_name',v.__name__);
          try: icon = v.icon();
          except AttributeError: icon = QIconSet();
          func = curry(self.change_viewer,v);
          self._viewers_proc.append(func);
          mid = self._viewers_menu.insertItem(icon,name,func);
          self._viewers_menu.setItemChecked(mid,v is viewer_class);
        self._menu.setItemEnabled(self._m_viewers,True);
      else:
        self._menu.setItemEnabled(self._m_viewers,False);
    self._wtop.show();
    self._refit_size();
    
  def update_data (self,dataitem,flash=True):
    _dprint(5,'GridCell: update data',dataitem);
    if self._viewer:
      self._dataitem = dataitem;
      self._viewer.set_data(dataitem);
      self._refit_size();
    self.enable();
    if flash:
      self._iconbutton.setPaletteBackgroundColor(self._highlight_colors[0]);
      self._iconbutton.setPaletteForegroundColor(self._highlight_colors[1]);
      QTimer.singleShot(500,self._unflash);
      
  def _unflash (self):
      self._iconbutton.unsetPalette();
      
  def _refit_size (self):
    """ugly kludge to get the layout system to do its stuff properly after
    viewer widget has been inserted.""";
    topwidget = self.wtop().topLevelWidget();
    sz = topwidget.size();
    topwidget.resize(sz.width(),sz.height()+1);
    topwidget.resize(sz);
  
    
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
    self._gw = gw;
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
        cell._drop_slot = curry(gw.add_data_item,cell=weakref.ref(cell));
        QWidget.connect(cell.wtop(),PYSIGNAL("dataItemDropped()"),
                        cell._drop_slot);
        cell._display_slot = curry(self._display_data_item,parent=weakref.ref(cell));
        QWidget.connect(cell.wtop(),PYSIGNAL("displayDataItem()"),
                        cell._display_slot);
    # prepare layout
    self.set_layout(0);
    
  def _display_data_item (self,item,args,kwargs,parent=None):
    self._gw.add_data_item(item,parent=parent,*args,**kwargs);
    
  def num_layouts (self):
    return len(self._layouts);
  def current_layout (self):
    return (self._cur_layout_num,) + self._cur_layout;
  
  # changes current layout scheme
  def set_layout (self,nlo):
    (nrow,ncol) = self._cur_layout = self._layouts[nlo];
    self._cur_layout_num = nlo;
    _dprint(5,"setting layout:",self._cur_layout);
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
    _dprint(2,'GriddedPage: clearing');
    self.set_layout(0);
    for row in self._rows:
      _dprint(2,'GriddedPage: clearing row',row);
      map(lambda cell:cell.close(),row.cells());
    
  # Finds a free cell if one is available, switches to the next layout
  # as needed. Returns Cell object, or None if everything is full.
  # If new=False, tries to reuse unpinned cells before switching layouts.
  #   If parent_udi is specified, then also avoids reusing cells with the 
  #   parent udi, or parents of those cells (cells whose udi is a prefix of 
  #   parent_udi).
  # If new=True, never reuses cells.
  def find_cell (self,udi,new=False,parent_udi=None):
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
            if not cell.is_pinned() and not (parent_udi and cell.is_parent_of(parent_udi)):
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
    self._dataitems = weakref.WeakValueDictionary();
    # highlighted item
    self._highlight = None;
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
    newpage = self.add_tool_button(Qt.TopLeft,pixmaps.tab_new_raised.pm(),
        tooltip="open new page. You can also drop data items here.",
        class_=self.DataDropButton,
        click=self.add_page);
    newpage._dropitem = curry(self.add_data_item,newpage=True);
    QWidget.connect(newpage,PYSIGNAL("dataItemDropped()"),
        newpage._dropitem);
    #------ new panels button
    self._new_panel = self.add_tool_button(Qt.TopLeft,pixmaps.view_right.pm(),
        tooltip="add more panels to this page. You can also drop data items here.",
        class_=self.DataDropButton,
        click=self._add_more_panels);
    self._new_panel._dropitem = curry(self.add_data_item,newcell=True);
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
  
  # adds a tool button to one of the corners of the workspace viewer
  def add_tool_button (self,corner,pixmap,tooltip=None,click=None,
                        leftside=False,class_=QToolButton):
    # create corner box on demand
    layout = self._tb_corners.get(corner,None);
    if not layout:
      parent = QWidget(self._maintab);
      self._tb_corners[corner] = layout = QHBoxLayout(parent);
      layout.setMargin(2);
      self._maintab.setCornerWidget(parent,corner);
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
    wpage = page.wtop();
    wpage._page = page;
    # generate page name, if none is supplied
    if name is None:
      name = 'Page '+str(self._maintab.count()+1);
      wpage._auto_name = True;
    else:
      wpage._auto_name = False;
    # add page to tab
    self._maintab.addTab(wpage,name);
    self._maintab.setCurrentPage(self._maintab.count()-1);
    QWidget.connect(page.wtop(),PYSIGNAL("layoutChanged()"),self._set_layout_button);
    return page;
    
  def remove_current_page (self):
    ipage = self._maintab.currentPageIndex();
    page = self._maintab.currentPage();
    page._page.clear();
    # if more than one page, then remove (else clear only)
    if self._maintab.count()>1:
      self._maintab.removePage(page);
    # renumber remaining pages
    for i in range(ipage,self._maintab.count()):
      wpage = self._maintab.page(i);
      if wpage._auto_name:
        self._maintab.setTabLabel(wpage,'Page '+str(i+1));
      
  def current_page (self):
    return self._maintab.currentPage()._page;
    
  def _align_grid (self):
    self.current_page().rearrange_cells();
    self.current_page().align_layout();
  def _add_more_panels (self):
    _dprint(5,"adding more panels");
    self.current_page().next_layout();
  def _set_layout_button (self):
    page = self.current_page();
    (nlo,nx,ny) = page.current_layout();
    self._new_panel.setDisabled(nlo >= page.num_layouts());
  def clear (self):
    _dprint(5,'GriddedWorkspace: clearing');
    self._maintab.page(0)._page.clear();
    for p in range(1,self._maintab.count()):
      page = self._maintab.page(p);
      page._page.clear();
      self._maintab.removePage(page);
  
  # highlights specfic cells, removes highlights from previous cells (if any)
  def highlight_cells (self,cells):
    # ensure arg is sequence
    if isinstance(cells,GridCell):
      cells = (cells,);
    # remove highlights from previous cells, if any
    if self._highlight:
      map(lambda c:c.highlight(False),self._highlight);
    map(lambda c:c.highlight(self._highlight_color),cells);
    self._highlight = cells;
    
  # Adds a data cell with the given item
  #   cell:    if not None, must be a cell (or a callable returning a cell) to 
  #            which item will be added. If None, a cell will be allocated.
  #   newpage: if True, creates a new page with the data cell
  #   newcell: if True, uses an empty cell (changing layouts as needed)
  #            rather than reusing an existing unpinned panel. If False,
  #            reuses a panel if possible; in this case, avoid_cells may be 
  #            a collection of cell ids reuse of which is to be avoided.
  def add_data_item (self,item,cell=None,parent=None,
                     newcell=False,newpage=False):
    # Helper function to resolve arguments specified as object or ref to object.
    # If specified via a callable (i.e. via weakref), try to resolve to 
    # an object
    def resolve_arg (arg,tp):
      if arg is not None: 
        if not isinstance(arg,tp):
          if callable(arg):
            arg = arg();
          if arg and not isinstance(arg,tp):
            raise TypeError,'argument not of type '+str(tp);
      return arg;
    _dprint(5,'add_data_item:',item,item.viewer,item.default_viewer);
    # add page if requested
    if newpage:
      self.add_page();
    # resolve cell and parent arguments 
    cell = resolve_arg(cell,GridCell);
    parent = resolve_arg(parent,GridCell);
    parent_udi = parent and parent.udi();
    # Are we already displaying this UDI? If so, then item0 will be it,
    # otherwise, item will be inserted into map (and thus item0 is item)
    item0 = self._dataitems.setdefault(item.udi,item);
    # compile list of cells which display this item (and use the same viewer
    # if one is explicitly specified)
    viewer = item.viewer;
    if item0 is not item:
      if item.viewer is None:
        disp_cells = list(item0.cells);
      else:
        disp_cells = filter(lambda c:type(c.viewer()) is viewer,item0.cells);
    else:
      disp_cells = [];
    # If the item is already displayed somewhere, we may still choose to
    # assign a new cell to it in one of two cases:
    # * cell/newcell/newpage is specified
    # * all cells displaying the item are not visible (i.e. are on different
    #   pages)
    if cell or newcell or newpage \
       or not filter(lambda c:c.wtop().isVisible(),disp_cells):
      # set item=item0, so that further operations below are done
      # on the original dataitem object
      item = item0;
    # finally, decide whether to highlight old cells, or display a new one
    if item0 is not item:
      if item.data is None:  
        item0.refresh();
      else: 
        item0.update(item.data);
    # else item is inserted into the specified cell
    else:
      # no cell specified (or callable returned None), allocate new cell/page
      if not cell: 
        cell = self.current_page().find_cell(item.udi,new=newcell,parent_udi=parent_udi) \
               or self.add_page().find_cell(item.udi,parent_udi=parent_udi);
      cell.set_data_item(item,viewer=viewer);
      # ask for a refresh
      item.refresh();
      disp_cells.append(cell); # will highlight below
      # ugly kludge to make cell size itself properly
#      topwidget = self.wtop().topLevelWidget();
#      sz = topwidget.size();
#      topwidget.resize(sz.width(),sz.height()+10);
    # highlight all cells displaying this item
    self.highlight_cells(disp_cells);
    self.wtop().emit(PYSIGNAL("addedDataItem()"),(item,));
    
  # updates a data item, if it is known
  def update_data_item (self,udi,data):
    # scan current data items to see which need updating
    for (u,item) in self._dataitems.iteritems():
      if u.startswith(udi):
        subudi = u[len(udi):];
        if subudi:   # a sub-udi, so we must process it by indexing into the data
          # split into keys and process one by one (first one is empty string)
          data1 = data;
          for key in subudi.split("/")[1:]:
            try: data1 = data1[key];
            except TypeError: # try to convert data to integer instead
              try: data1 = data1[int(key)];
              except TypeError,KeyError: 
                break;
          else: # loop successful
            item.update(data1);
        else:               # not a sub-udi, directly update the value
          item.update(data);
      
  # removes a data item
  def remove_data_item (self,udi):
    if udi in self._dataitems:
      self._dataitems[udi].remove();
      del self._dataitems[udi];
