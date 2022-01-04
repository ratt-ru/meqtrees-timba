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

from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.widgets import *
from Timba import *
from Timba.Grid.Debug import *
import Timba.Grid.Services

import weakref
import re
import gc
import types

from PyQt4.Qt import *
import Kittens
from Kittens.widgets import PYSIGNAL

# ====== Grid.Cell ==============================================================
# manages one cell of a gridded workspace
#
class Cell (object):
  """The Cell class represents a grid cell with float/pin/close/menu
  controls and a title label.
  
  The top-level widget of a cell is available as cell.wtop(). This
  widget will emit the following PYSIGNALS:
    "clicked()"             : cell has been clicked anywhere
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
    "itemDropped(item)"     : a dataitem has been dropped on the cell.
                                        
  In addition, a cell will connect PYSIGNAL("refresh()") from its content
  widget to the refresh function of its dataitem, if available. Thus cell
  contents may ask to refresh themselves by emitting this signal. Also,
  when the cell's refresh button is clicked, "refresh()" is emitted on behalf
  of the content widget, thus causing a refresh.
  """
  # define top-level cell widget class. This accepts data drops, 
  # displays context menus, has toolbars, etc.
  DataDroppableQWidget = DataDroppableWidget(QWidget);
  class TopLevelWidget (DataDroppableQWidget):
    def __init__ (self,cell,parent):
      Cell.DataDroppableQWidget.__init__(self,parent);
      self._cell = cell;
      self._menu = None;
    def set_context_menu (self,menu):
      self._menu = menu;
    def mousePressEvent (self,ev):
      self.emit(SIGNAL("clicked"));
      ev.ignore();
    def contextMenuEvent (self,ev):
      # self.emit(SIGNAL("clicked"));
      ev.accept();
      if self._menu:
        self._menu.exec_(ev.globalPos());
    def accept_drop_item_type (self,itemtype):
      return issubclass(itemtype,Timba.Grid.DataItem);
    def get_cell (self):
      return self._cell;
      
  class DraggableCellLabel (QLabel):
    def __init__ (self,cell,*args):
      QLabel.__init__(self,*args);
      self._grid_cell = cell;
      self._pressed = None;
      self._dragtimer = QTimer(self);
      self._dragtimer.setSingleShot(True);
      QObject.connect(self._dragtimer,SIGNAL("timeout()"),self._timeout);
    # these are standard methods to support drags
    def get_drag_item (self,key):
      return self._grid_cell.content_dataitem();
    def get_drag_item_type (self,key):
      item = self._grid_cell.content_dataitem();
      if item is None:
        return None;
      return type(item);
    # process mouse and timer events to start a drag  
    def mousePressEvent (self,ev):
      if ev.button() == Qt.LeftButton \
         and self._grid_cell.content_dataitem() is not None:
        self._pressed = ev.pos();
        self._dragtimer.start(QApplication.startDragTime());
      return QLabel.mousePressEvent(self,ev);
    # mouse released, cancel drag  
    def mouseReleaseEvent (self,ev):
      self._pressed = None;
      self._dragtimer.stop();
      return QLabel.mouseReleaseEvent(self,ev);
    # mouse move, start drag if far enough      
    def mouseMoveEvent (self,ev):
      # start a drag if mouse has moved far enough
      if self._pressed and ev.buttons() & Qt.LeftButton: 
        dist = (self._pressed - ev.pos()).manhattanLength();
        if dist >= QApplication.startDragDistance():
          self._dragtimer.stop();
          self._start_drag();
      return QLabel.mouseMoveEvent(self,ev);
    # timer fired, start drag if mouse still pressed
    def _timeout (self):
      if self._pressed:
        self._start_drag();
    # this method starts the drag  
    def _start_drag (self):
      item = self._grid_cell.content_dataitem();
      if item is not None:
        drag = QDrag(self);
        mimedata = QMimeData();
        mimedata.setUrls([QUrl(item.udi)]);
        drag.setMimeData(mimedata);
        drag.exec_();
        
  def __init__ (self,parent,gridpos,page=None,fixed_cell=False,notitle=False,noviewer=False):
    """constructor. 
    parent:     parent widget
    gridpos:    the grid position. A tuple of (gridpage,row,col).
                This is used to uniquely identify the cell within the workspace.
    noviewer:   if True, the cell will not support change of viewers or drops
                of data items
    fixed_cell: if True, the cell will not support change of viewers, closing,
                pinning, etc., and will not accept drops of data items.
    notitle:    if True, cell will be fixed, and will not have a 'titlebar'.
    page:       this cell's Page parent. None if cell does not belong to a grid
                page (e.g. a floater window)
    """
    # init state
    self._content_widget = self._leader = self._udi = None;
    self._gridpos = gridpos;
    self._refresh_func = lambda:None;
    self._highlight = False;
    self._enabled = False;  
    self._dataitem = None;
    self._parent_page = page;
    # init widgets
    wtop = self._wtop = self.TopLevelWidget(self,parent);
    wtop.hide();
    self._wtop_lo = QVBoxLayout(wtop);
    self._wtop_lo.setSpacing(0);
    self._wtop_lo.setContentsMargins(0,0,0,0);
    self.enable_viewers(not noviewer);
    # --- build toolbar
    self._toolbar = QToolBar("Panel tools",wtop);
    self._toolbar.setIconSize(QSize(16,16));
    self._wtop_lo.addWidget(self._toolbar);
    # icon button and popup menu    
    self._icon_act = self._toolbar.addAction("Panel &menu",self.show_popup_menu);
    self._icon_act.setToolTip("Displays panel menu");
    # refresh button
    self._refresh = refresh = self._toolbar.addAction(pixmaps.refresh.icon(),
				"&Refresh contents",self._dorefresh);
    refresh.setToolTip("refresh contents of this panel");
    self._flashcolor = QColor("yellow");
    # stretchable label
    self._label = self.DraggableCellLabel(self,"(empty)",self._toolbar);
    self._label.setAlignment(Qt.AlignLeft|Qt.AlignVCenter);
    self._label.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum);
    self._toolbar.addSeparator();
#    qaw = QWidgetAction(wtop);
#    qaw.setDefaultWidget(self._label);
#    self._toolbar.addAction(qaw);
    self._toolbar.addWidget(self._label);
    self._toolbar.addSeparator();
    # pin button
    pin_icon = pixmaps.pin_up.icon();
    pin_icon.addPixmap(pixmaps.pin_down.pm(),QIcon.Normal,QIcon.On);
    self._pin = pin = self._toolbar.addAction(pin_icon,"&Pin/unpin panel");
    pin.setToolTip("pin (i.e. protect) or unpin this panel");
    pin.setCheckable(True);
    # float button
    self._float_act = flt = self._toolbar.addAction(pixmaps.float_window.icon(),"&Float panel",self._float);
    flt.setToolTip("float this cell in a separate window");
    # flt.setToggleAction(True);
    # close button
    self._toolbar.addSeparator();
    self._close = close = self._toolbar.addAction(pixmaps.cancel.icon(),"&Close panel",self.close);
    close.setToolTip("close this panel");
    # finalize toolbar setup
    #self._toolbar.setHorizontallyStretchable(True);
    #self._toolbar.setStretchableWidget(self._label);
    self._toolbar.setMovable(False);
    try: # early Qt4 versions do not have this function
      self._toolbar.setFloatable(False);
    except AttributeError:
      pass;
    self._label.setEnabled(False);
    self._refresh.setVisible(False);
    self._pin.setVisible(False);
    self._close.setVisible(False);
    self._float_act.setVisible(False);
    # set resize policy
    wtop.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding));
    # add currier for self.connect() below
    self._currier = PersistentCurrier();
    # clear menus
    self._menu = self._font_menu = self._viewers_menu = None;
    
  def wtop (self):
    return self._wtop;
  def wcontent (self):
    try: return self._content_widget();
    except AttributeError: return None;
  def connect (self,signal,receiver,*args,**kws):
    """connects a signal from the cell's top-level widget to the receiver.
    This is really a kludge to get around the fact that PyQt does not support
    QObject.disconnect() properly, so there's no easy way to disconnect
    all of an object's signals -- which we need to do when clearing a cell.
    Hence, we provide our own connect/disconnect.
    The syntax is similar to the standard utils.curry() call, except with 
    an extra signal argument.
    """;
    # wrap the signal receiver in a curry -- since connect() holds weakrefs,
    # all we need to do for a full disconnect is clear the currier.
    cc = self._currier.curry(receiver,*args,**kws);
    QObject.connect(self._wtop,signal,cc);
    
  def _float (self):
    self.wtop().emit(PYSIGNAL("float()"));
    
  def disconnect_all (self):
    self._currier.clear();
    
  def parent_page (self):
    return self._parent_page;
  def grid_position (self):
    return self._gridpos;
  def hide (self):
    self._wtop.hide();
  def show (self):
    self._wtop.show();
  def enable_viewers (self,enable):
    self._enable_viewers = enable;
    self._wtop.setAcceptDrops(enable);
  def get_udi (self):
    return self._udi;
  def is_parent_of (self,udi):
    return udi and self._udi and len(udi) > len(self._udi) and udi.startswith(self._udi);
  def is_empty (self):
    return self._content_widget is None;
  def is_pinned (self):
    return self._pin.isChecked();
  def set_pinned (self,state=True):
    self._pin.setChecked(state);
  def show_popup_menu (self,point=None):
    self._menu.exec_(point or QCursor.pos());
  def _toggle_pinned_state (self):
    self.set_pinned(not self.is_pinned());
    
  # highlights a cell
  # pass in a QColor, or True for default color, or False value to disable highlights
  def highlight (self,enable=True):
#      wlist = [self._control_box] + self._control_box.children();
#    wlist = (self._toolbar,self._label,self._label1);
    wlist = (self._label,);
    if enable:
      for w in wlist:
        if isinstance(w,QWidget):
          if not self._highlight:
            w._default_background = w.backgroundRole();
            w._default_foreground = w.foregroundRole();
#          w.setBackgroundRole(QPalette.Dark);
          w.setForegroundRole(QPalette.ButtonText);
      self._highlight = True;
    else:
      for w in wlist:
        if isinstance(w,QWidget):
          if hasattr(w,'_default_background'):
            w.setBackgroundRole(w._default_background);
          if hasattr(w,'_default_foreground'):
            w.setForegroundRole(w._default_foreground);
      self._highlight = False;
    # if we're a leader, grab the focus
    if not self._leader:
      self.wtop().setFocus();
    self.wtop().emit(SIGNAL("highlight"),enable,);
      
  def _dorefresh (self):
    if self._content_widget:
      self._content_widget.emit(SIGNAL("refresh"));
    
  def _clear_content (self):
    if self._content_widget:
      self._content_widget.setParent(QWidget());
      self._content_widget = None;
      
  # wipe: deletes contents of cell, possibly in preparation for inserting 
  # other content
  def wipe (self,delete_content=True,close=False):
    """if delete_content==True, content widget is reparented and destroyed,
    and a wiped() signal is emitted. Otherwise, reference to content widget
    is removed but the widget is left alone (this is used for reparenting the
    widget into, e.g., a float window).
    If close==True, a closed() signal is also emitted.
    """;
    _dprint(5,id(self),': wiping cell');
    self._dataitem = self._udi = None;
    self.set_pinned(False);
    self._refresh_func = lambda:None;
    self.wtop().set_context_menu(None);
    self._label.setToolTip('');
    self.highlight(False);
    self._label.setText("(empty)");
    self._label.setEnabled(False);
    self._icon_act.setVisible(False);
    self._refresh.setVisible(False);
    self._pin.setVisible(False);
    self._close.setVisible(False);
    self._float_act.setVisible(False);
    if delete_content:
      self._clear_content();
      _dprint(5,id(self),': emitting wiped() signal');
      self.wtop().emit(SIGNAL("wiped"));
    else:
      self._content_widget = None;
    if close:
      _dprint(5,id(self),': emitting closed() signal');
      self.wtop().emit(SIGNAL("closed"));
    # this is the last step
    self.disconnect_all();

  # close(): wipe, hide everything, and emit a closed signal
  def close (self):
    _dprint(5,id(self),': clearing cell');
    self.wipe(close=True);
    
  def release (self):
    """same as wipe, except content widget is not deleted, and wiped()
    signal is not sent. Used when content has been reparented."""
    self.wipe(delete_content=False);

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
    self.wtop().emit(SIGNAL("enable"),enable,);
    
  def is_enabled (self):
    return self._enabled;
    
  def cell_menu (self):
    return self._menu;
    
  def clear_menu (self):
    self._menu = self._font_menu = self._viewers_menu = None;
    
  # rebuild or clears menu
  def rebuild_menu (self,title,font=None,use_refresh=False):
    # create menu
    self._menu = menu = QMenu(self.wtop());
    if title:
      self._menu_label = Kittens.widgets.addMenuLabel(menu,title);
    if font:
      fontmenu = menu.addMenu(pixmaps.fontsizedown.icon(),"Change font size");
      self._font_qas = {};
      ag = QActionGroup(menu);
      ag.setExclusive(True);
      # populate font menu
      ps = font.pointSize();
      if ps<0:
        ps = font.pixelSize();
      rng = list(range(min(4,ps),15)) + list(range(16,max(26,ps),2));
      for sz in rng:
        self._font_qas[sz] = qa = ag.addAction(str(sz));
        qa.setCheckable(True);
        fontmenu.addAction(qa);
        QObject.connect(qa,SIGNAL("toggled(bool)"),self._menu_currier.curry(self.set_font_size,sz));
      self._reset_font_menu(ps);
    if self._enable_viewers and self._viewers_menu:
      menu.addMenu(self._viewers_menu);
    menu.addAction(self._pin);
    menu.addAction(self._float_act);
    if use_refresh:
      menu.addAction(self._refresh);
    menu.addAction(self._close);
    
  def adjust_font (self,incr):
    """adjusts content font size by 'incr' points""";
    font = self._content_widget.font();
    ps = font.pointSize();
    if ps >= 0:
      self.set_font_size(ps+incr);
    else:
      self.set_font_size(font.pixelSize()+incr);
    
  def set_font_size (self,size,really_set=True):
    """sets content font size. Really_set should be True to actually set the font, this 
    is to make the method compatible with the toggled(bool) signal.""";
    if not really_set:
      return;
    font = QFont(self._content_widget.font());
    if font.pointSize() > 0:
      font.setPointSize(size);
    else:
      font.setPixelSize(size);
    self._content_widget.setFont(font);
    self._content_widget.emit(SIGNAL("fontChanged"),font,);
    self.wtop().emit(SIGNAL("fontChanged"),font,);
    self._reset_font_menu(size);
    
  def _reset_font_menu (self,size):
    qa = self._font_qas.get(size);
    if qa:
      qa.setChecked(True);
      
  def _change_viewer (self,dataitem,viewer):
    self.wtop().emit(SIGNAL("changeViewer"),dataitem,viewer);
    
  def exclusive_highlight (self):
    if self._dataitem:
      Timba.Grid.Services.highlightDataItem(self._dataitem);
    
  def set_content (self,widget,dataitem=None,leader=None,icon=None,enable_viewers=True):
    """inits cell as a leader cell for a dataitem. Leader cells have
    an active toolbar and menu. When a viewer is using a single cell,
    that cell is always a leader cell."""
    # check that widget is our child
    if widget.parent() is not self.wtop():
      raise ValueError('content widget must be child of this Grid.Cell');
    _dprint(3,id(self),': setting content');
    # connect a click on the titlebar to highlight ourselves 
    self.connect(PYSIGNAL("clicked()"),self.exclusive_highlight);
    # init cell content
    self.enable_viewers(enable_viewers);
    self._wtop.hide();
    # insert new content
    self._clear_content();
    self._content_widget = widget;
    widget.setParent(self.wtop());
    self._wtop_lo.addWidget(widget);
    _dprint(5,id(self),': widget',widget,'added');
    # recreate currier for callbacks (discards old curries)
    self._menu_currier = PersistentCurrier();
    self._dataitem = dataitem;
    # setup cell controls based on data item
    if dataitem is not None:
      self._udi = dataitem.udi;
      if leader is not None:
        raise ValueError("both dataitem and leader specified");
      self._leader = None;
      _dprint(5,id(self),': dataitem is',dataitem);
      self.clear_menu();
      # set icon for the menu button
      self._icon_act.setIcon(icon or pixmaps.viewmag.icon());
      # build a "Display with" submenu 
      if len(dataitem.viewer_list) > 1:
        vmenu = self._viewers_menu = QMenu(self.wtop());
        vmenu.setTitle("Display using");
        vmenu.setIcon(pixmaps.viewmag.icon());
        for v in dataitem.viewer_list:
          # create entry for viewer
          name = getattr(v,'viewer_name',v.__name__);
          try: icon = v.icon();
          except AttributeError: icon = QIcon();
          func = self._menu_currier.xcurry(self._change_viewer,_args=(dataitem,v));
          qa = vmenu.addAction(icon,name,func);
          qa.setCheckable(True);
          qa.setChecked(v is dataitem.viewer_obj.__class__);
      else:
        self._viewers_menu = None;
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
      self._float_act.setVisible(True);
      # enable cell if data is available
      self.enable(dataitem.data is not None);
    else: # no dataitem, assume follower cell
      if leader is None:
        raise ValueError("leader must be specified if dataitem isn't");
      _dprint(5,id(self),': leader is',leader);
      self._leader = leader;
      self._dataitem = leader._dataitem;
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
      leader.connect(PYSIGNAL("enable()"),self.enable);
      leader.connect(PYSIGNAL("highlight()"),self.highlight);
      leader.connect(PYSIGNAL("closed()"),self.close);
    self._icon_act.setVisible(True);
    self._label.setEnabled(True);
    # disable cell if no data yet
    # show and resize everything
    self._toolbar.show();
    self._content_widget.show();
    self._wtop.show();
    self._refit_size();
    
  def set_caption (self,caption):
    """sets the caption of a cell."""
    self._label.setToolTip(caption);
    self._label.setText(caption);
    # set menu title if menu is present
    try: self._menu_label.setText(caption);
    except AttributeError: pass;
    
  def leader (self):
    return self._leader;
  def content_udi (self):
    return self._udi;
  def content_dataitem (self):
    return self._dataitem;
    
  def flash (self,flash=True):
    _dprint(5,id(self),': flash()');
    self.wtop().emit(SIGNAL("flash"),flash,);
    self.enable();
    if flash:
      # self._refresh_btn.setPaletteBackgroundColor(self._flashcolor);
      self._refresh.setIcon(pixmaps.refresh_highlight.icon());
      QTimer.singleShot(300,self._unflash);
    else:
      self._unflash();
      
  def _unflash (self):
    # self._refresh_btn.unsetPalette();
    self._refresh.setIcon(pixmaps.refresh.icon());
 
  def _refit_size (self):
    """ugly kludge to get the layout system to do its stuff properly after
    viewer widget has been inserted.""";
    #topwidget = self.wtop().topLevelWidget();
    #sz = topwidget.size();
    #topwidget.resize(sz.width(),sz.height()+1);
    #topwidget.resize(sz);
    pass;
