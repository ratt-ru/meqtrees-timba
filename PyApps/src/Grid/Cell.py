#!/usr/bin/python

from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.widgets import *
import Timba.Grid 
from Timba import *
from Timba.Grid.Debug import *

import weakref
import sets
import re
import gc
import types
from qt import *

# ====== Grid.Cell ==============================================================
# manages one cell of a gridded workspace
#
class Cell (object):
  """The Cell class represents a grid cell with float/pin/close/menu
  controls and a title label.
  
  The top-level widget of a cell is available as cell.wtop(). This
  widget will emit the following PYSIGNALS:
    "float()"               : float of cell is requested
    "flash(bool)"           : cell is flash/unflashing its refresh button  
    "highlight(color|bool)" : cell is highlighted (True for default color)
                              or dehighlighted (False)
    "enable(bool)"          : cell is enabled/disabled
    "wiped()"               : cell contents are cleared
    "closed()"              : cell has been closed via the close button 
                              (wiped() will also be emitted)
    "fontChanged(QFont)"    : cell font has been changed. The same signal is
                              emitted by the content widget.
    "changeViewer(viewer_class)": different viewer selected from "Dispay with" menu
    "dataItemDropped(item)" : a dataitem has been dropped on the cell.
                                        
  In addition, a cell will connect PYSIGNAL("refresh()") from its content
  widget to the refresh function of its dataitem, if available. Thus cell
  contents may ask for a refresh of the cell by emitting this signal.
  """
  # define top-level cell widget class. This accepts data drops, 
  # displays context menus, has toolbars, etc.
  DataDroppableMainWindow = DataDroppableWidget(QMainWindow);
  class TopLevelWidget (DataDroppableMainWindow):
    def __init__ (self,parent,name=None):
      Cell.DataDroppableMainWindow.__init__(self,parent,name,0);
      self._menu = None;
    def set_context_menu (self,menu):
      self._menu = menu;
    def contextMenuEvent (self,ev):
      ev.accept();
      if self._menu:
        self._menu.exec_loop(ev.globalPos());
      
  def __init__ (self,parent,gridpos,fixed_cell=False,notitle=False):
    """constructor. 
    parent:     parent widget
    gridpos:    the grid position. A tuple of (gridpage,ix,iy).
                This is used to uniquely identify the cell within the workspace.
    fixed_cell: if True, the cell will not support change of viewers, closing,
                pinning, etc., and will not accept drops of data items.
    notitle:    if True, cell will be fixed, and will not have a 'titlebar'.
    """
    # init state
    self._content_widget = self._leader = self._udi = None;
    self._gridpos = gridpos;
    self._refresh_func = lambda:None;
    self._highlight_colors = \
      (QApplication.palette().active().highlight(),\
       QApplication.palette().active().highlightedText()); \
    self._highlight = False;
    self._enabled = False;  
    # init widgets
    wtop = self._wtop = self.TopLevelWidget(parent,'cell '+str(id(self))+' top');
    wtop.hide();
    # --- build toolbar
    self._toolbar = QToolBar("Panel tools",wtop,wtop);
    # icon button and popup menu    
    self._icon_act = QAction("Panel &menu",QKeySequence(),wtop);
    self._icon_act.setToolTip("Displays panel menu");
    self._icon_act.addTo(self._toolbar);
    QObject.connect(self._icon_act,SIGNAL("activated()"),self.show_popup_menu);
    # pin button
    pin_is = pixmaps.pin_up.iconset();
    pin_is.setPixmap(pixmaps.pin_down.pm(),QIconSet.Automatic,QIconSet.Normal,QIconSet.On);
    self._pin = pin = QAction(pin_is,"&Pin/unpin panel",QKeySequence(),wtop);
    pin.setToolTip("pin (i.e. protect) or unpin this panel");
    pin.setToggleAction(True);
    pin.addTo(self._toolbar);
    QObject.connect(pin,SIGNAL("activated()"),self._update_pin_menu);
    # float button
    self._float_act = flt = QAction(pixmaps.float_window.iconset(),"&Float panel",QKeySequence(),wtop);
    flt.setToolTip("float this cell in a separate window");
    # flt.setToggleAction(True);
    flt.addTo(self._toolbar);
    QObject.connect(flt,SIGNAL("activated()"),self.wtop(),PYSIGNAL("float()"));
    # refresh button
    self._refresh = refresh = QAction(pixmaps.refresh.iconset(),"&Refresh contents",QKeySequence(),wtop);
    refresh.setToolTip("refresh contents of this panel");
    refresh.addTo(self._toolbar);
    QObject.connect(refresh,SIGNAL("activated()"),self._dorefresh);
    self._toolbar.addSeparator();
    # stretchable label
    self._label = QLabel("(empty)",self._toolbar);
    self._label.setAlignment(Qt.AlignLeft+Qt.AlignVCenter+Qt.SingleLine);
    # close button
    self._close = close = QAction(pixmaps.cancel.iconset(),"&Close panel",QKeySequence(),wtop);
    close.setToolTip("close this panel");
    close.addTo(self._toolbar);
    QObject.connect(close,SIGNAL("activated()"),self.close);
    # complete toolbar setup
    self._toolbar.setHorizontallyStretchable(True);
    self._toolbar.setStretchableWidget(self._label);
    self._toolbar.setMovingEnabled(False);
    # set resize policy
    wtop.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding));
    
  def wtop (self):
    return self._wtop;
  def wcontent (self):
    try: return self._content_widget();
    except AttributeError: return None;
  def grid_position (self):
    return self._gridpos;
  def hide (self):
    self._wtop.hide();
  def show (self):
    self._wtop.show();
  def get_udi (self):
    return self._udi;
  def is_parent_of (self,udi):
    return udi and self._udi and len(udi) > len(self._udi) and udi.startswith(self._udi);
  def is_empty (self):
    return self._content_widget is None;
  def is_pinned (self):
    return self._pin.isOn();
  def set_pinned (self,state=True):
    self._pin.setOn(state);
    self._update_pin_menu(state);
  def show_popup_menu (self,point=None):
    self._menu.exec_loop(point or QCursor.pos());
  def _toggle_pinned_state (self):
    self.set_pinned(not self.is_pinned());
  def _update_pin_menu (self,state=None):
    try: pinid = self._m_pin;
    except: return;
    if state is None:
      state = self.is_pinned();
    self._pin.setOn(state);
    
  # highlights a cell
  # pass in a QColor, or True for default color, or False value to disable highlights
  def highlight (self,color=True):
#      wlist = [self._control_box] + self._control_box.children();
#    wlist = (self._toolbar,self._label,self._label1);
    wlist = (self._label,);
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
    # if we're a leader, grab the focus
    if not self._leader:
      self.wtop().setFocus();
    self.wtop().emit(PYSIGNAL("highlight()"),(color,));
      
  def _dorefresh (self):
    self._refresh_func();
    
  def _clear_content (self):
    if self._content_widget:
      dum = QWidget();
      self._content_widget.reparent(dum, 0, QPoint())
      self._content_widget = None;
      
  # wipe: deletes contents in preparation for inserting other content
  def wipe (self):
    _dprint(5,id(self),': wiping cell');
    self.set_pinned(False);
    self._clear_content();
    self._refresh_func = lambda:None;
    self.wtop().emit(PYSIGNAL("wiped()"),());
    self.wtop().set_context_menu(None);

  # close(): wipe, hide everything, and emit a closed signal
  def close (self):
    _dprint(5,id(self),': clearing cell');
    self.wipe();
    self._wtop.hide();
    self._toolbar.hide();
    self._label.setText("(empty)");
    self.wtop().emit(PYSIGNAL("closed()"),());
    
  def release (self):
    self._content_widget = None;
    self._refresh_func = lambda:None;
    self.wtop().set_context_menu(None);
    self._wtop.hide();
    self._toolbar.hide();
    self._label.setText("(empty)");

  def disable (self,disable=True):
    self.enable(not disable);
    
  def enable (self,enable=True):
    self._enabled = enable;
    for w in (self._label,self._close,self._toolbar):
      w.setEnabled(enable);
    if enable:
      self.wtop().set_context_menu(self._menu);
    else:
      self.wtop().set_context_menu(None);
    self.wtop().emit(PYSIGNAL("enable()"),(enable,));
    
  def is_enabled (self):
    return self._enabled;
    
  def cell_menu (self):
    return self._menu;
    
  def clear_menu (self):
    self._menu = self._font_menu = self._viewers_menu = None;
    
  # rebuild or clears menu
  def rebuild_menu (self,title,font=None,use_refresh=False):
    # create menu
    self._menu = menu = QPopupMenu(self.wtop());
    if title:
      tlab = QLabel(title,menu);
      tlab.setAlignment(Qt.AlignCenter);
      tlab.setFrameShape(QFrame.ToolBarPanel);
      tlab.setFrameShadow(QFrame.Sunken);
      self._m_title = self._menu.insertItem(tlab);
      # self._menu.insertSeparator();
    if font:
      self._font_menu = QPopupMenu(self.wtop());
      self._m_fonts = {};
      menu.insertItem("Change font size",self._font_menu);
      # populate font menu
      ps = font.pointSize();
      if ps<0:
        ps = font.pixelSize();
      rng = range(min(4,ps),15) + range(16,max(26,ps),2);
      for sz in rng:
        self._m_fonts[sz] = self._font_menu.insertItem(str(sz),
                  self._menu_currier.curry(self.set_font_size,sz));
      self._reset_font_menu(ps);
      # i1 = self._menu.insertItem("Larger font",self.increase_font);
      # self._menu.setAccel(Qt.CTRL+Qt.Key_Plus,i1);
      # i1 = self._menu.insertItem("Smaller font",self.decrease_font);
      # self._menu.setAccel(Qt.CTRL+Qt.Key_Minus,i1);
    self._m_viewers = menu.insertItem("View using",self._viewers_menu);
    self._pin.addTo(menu);
    self._pin.setOn(self.is_pinned());
    self._float_act.addTo(menu);
    if use_refresh:
      self._refresh.addTo(menu);
    self._close.addTo(menu);
    
  def adjust_font (self,incr):
    """adjusts content font size by 'incr' points""";
    font = self._content_widget.font();
    ps = font.pointSize();
    if ps >= 0:
      self.set_font_size(ps+incr);
    else:
      self.set_font_size(font.pixelSize()+incr);
    
  def set_font_size (self,size,dum=None):
    """sets content font size. dum argument ignored, used for compatibility
    with menu callbacks""";
    font = QFont(self._content_widget.font());
    if font.pointSize() > 0:
      font.setPointSize(size);
    else:
      font.setPixelSize(size);
    self._content_widget.setFont(font);
    self._content_widget.emit(PYSIGNAL("fontChanged()"),(font,));
    self.wtop().emit(PYSIGNAL("fontChanged()"),(font,));
    self._reset_font_menu(size);
    
  def _reset_font_menu (self,size):
    for (sz,menu_id) in self._m_fonts.iteritems():
      self._font_menu.setItemChecked(menu_id,sz==size);
      
  def _change_viewer (self,dataitem,viewer):
    self.wtop().emit(PYSIGNAL("changeViewer()"),(dataitem,viewer));
    
  def set_content (self,widget,dataitem=None,leader=None,icon=None):
    """inits cell as a leader cell for a dataitem. Leader cells have
    an active toolbar and menu. When a viewer is using a single cell,
    that cell is always a leader cell."""
    # check that widget is our child
    if widget.parent() is not self.wtop():
      raise ValueError,'content widget must be child of this Grid.Cell';
    # init cell content
    self._wtop.hide();
    # insert new content
    self._clear_content();
    self._content_widget = widget;
    self.wtop().setCentralWidget(widget);
    _dprint(5,id(self),': widget',widget,'added');
    # recreate currier for callbacks (discards old curries)
    self._menu_currier = PersistentCurrier();
    # setup cell controls based on data item
    if dataitem is not None:
      self._udi = dataitem.udi;
      if leader is not None:
        raise ValueError,"both dataitem and leader specified";
      self._leader = None;
      _dprint(5,id(self),': dataitem is',dataitem);
      self.clear_menu();
      # set icon for the menu button
      self._icon_act.setIconSet(icon or pixmaps.magnify.iconset());
      # build a "Display with" submenu 
      if len(dataitem.viewer_list) > 1:
        vmenu = self._viewers_menu = QPopupMenu(self.wtop());
        for v in dataitem.viewer_list:
          # create entry for viewer
          name = getattr(v,'viewer_name',v.__name__);
          try: icon = v.icon();
          except AttributeError: icon = QIconSet();
          func = self._menu_currier.xcurry(self._change_viewer,_args=(dataitem,v));
          mid = vmenu.insertItem(icon,name,func);
          vmenu.setItemChecked(mid,v is dataitem.viewer_obj.__class__);
      # build main/context menu
      self.rebuild_menu(dataitem.caption,font=widget.font(),
                        use_refresh=dataitem.is_mutable());
      # setup refresh control
      if dataitem.is_mutable():
        self._refresh_func = dataitem.refresh_func;    
        QWidget.connect(self._content_widget,PYSIGNAL("refresh()"),self._refresh_func);
        self._refresh.setVisible(True);
      else:
        self._refresh_func = lambda:None;
        self._refresh.setVisible(False);
      # setup pin and close button
      self._pin.setVisible(True);
      self._close.setVisible(True);
      self._float_act.setEnabled(True);
      # enable cell if data is available
      self.enable(dataitem.data is not None);
    else: # no dataitem, assume follower cell
      if leader is None:
        raise ValueError,"leader must be specified if dataitem isn't";
      _dprint(5,id(self),': leader is',leader);
      self._leader = leader;
      self._udi = leader.get_udi();
      # disable controls
      self.clear_menu();
      self._refresh.setVisible(False);
      self._pin.setVisible(False);
      self._close.setVisible(False);
      self._float_act.setVisible(False);
      # enable cell as per leader
      self.enable(leader.is_enabled());
      # attach leader's signals
      QObject.connect(leader.wtop(),PYSIGNAL("enable()"),self.enable);
      QObject.connect(leader.wtop(),PYSIGNAL("highlight()"),self.highlight);
      QObject.connect(leader.wtop(),PYSIGNAL("closed()"),self.close);
    # show the control box
    self._toolbar.show();
    # disable cell if no data yet
    # show and resize everything
    self._toolbar.show();
    self._content_widget.show();
    self._wtop.show();
    self._refit_size();
    
  def set_caption (self,caption):
    """sets the caption of a cell."""
    self._label.setText(caption);
    # set negative margin, to keep rich text from bloating the label's height
    self._label.setMargin(-20);
    # set menu title if menu is present
    try: self._menu.changeItem(self._m_title,caption);
    except AttributeError: pass;
    
  def leader (self):
    return self._leader;
    
  def flash (self,flash=True):
    _dprint(5,id(self),': flash()');
    self.wtop().emit(PYSIGNAL("flash()"),(flash,));
    self.enable();
    if flash:
      self._refresh.setIconSet(pixmaps.refresh_highlight.iconset());
      QTimer.singleShot(500,self._unflash);
    else:
      self._unflash();
      
  def _unflash (self):
    self._refresh.setIconSet(pixmaps.refresh.iconset());
      
  def _refit_size (self):
    """ugly kludge to get the layout system to do its stuff properly after
    viewer widget has been inserted.""";
    topwidget = self.wtop().topLevelWidget();
    sz = topwidget.size();
    topwidget.resize(sz.width(),sz.height()+1);
    topwidget.resize(sz);
