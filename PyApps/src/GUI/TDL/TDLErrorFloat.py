# -*- coding: utf-8 -*-
from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

import Timba
from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
from Timba import TDL

import sys
import os
import os.path

_dbg = verbosity(0,name='tdlerrors');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class TDLErrorFloat (QMainWindow,PersistentCurrier):
  """implements a floating window for TDL error reports""";
  def __init__ (self,parent):
    QMainWindow.__init__(self,parent,Qt.Dialog|Qt.WindowTitleHint);
    self.hide();
    # self.setWindowIcon(pixmaps.red_round_cross.icon());
    self.setWindowTitle("TDL Errors");
    # make widgets
    self._werrlist_box = QWidget(self);
    lo = QVBoxLayout(self._werrlist_box);
    lo.setContentsMargins(0,0,0,0);
    lo.setSpacing(0);
    self.setCentralWidget(self._werrlist_box);
    # error list header is a toolbar
    errlist_hdr = QToolBar("TDL errors",self._werrlist_box);
    errlist_hdr.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed);
    errlist_hdr.setIconSize(QSize(16,16));
    lo.addWidget(errlist_hdr);
    # prev/next error buttons
    self._qa_prev_err = errlist_hdr.addAction(pixmaps.red_leftarrow.icon(),"Show &previous error")
    self._qa_prev_err.setShortcut(Qt.ALT+Qt.Key_P);
    QObject.connect(self._qa_prev_err,SIGNAL("triggered()"),self._show_prev_error);
    self._qa_next_err = errlist_hdr.addAction(pixmaps.red_rightarrow.icon(),"Show &next error");
    self._qa_next_err.setShortcut(Qt.ALT+Qt.Key_N);
    QObject.connect(self._qa_next_err,SIGNAL("triggered()"),self._show_next_error);
    # label with error count
    self._error_count_label = QLabel(errlist_hdr);
    errlist_hdr.addWidget(self._error_count_label);
    self._error_count_label.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed);
    # error list itself
    self._werrlist = QTreeWidget(self._werrlist_box);
    lo.addWidget(self._werrlist);
    self._werrlist.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred);
    QObject.connect(self._werrlist,SIGNAL("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)"),self.curry(self._process_item_click,"currentChanged"));
    QObject.connect(self._werrlist,SIGNAL("itemClicked(QTreeWidgetItem*,int)"),self.curry(self._process_item_click,"clicked"));
    QObject.connect(self._werrlist,SIGNAL("itemActivated(QTreeWidgetItem*,int)"),self.curry(self._process_item_click,"spacePressed"));
    QObject.connect(self._werrlist,SIGNAL("itemExpanded(QTreeWidgetItem*)"),self.curry(self._process_item_click,"expanded"));
    self._werrlist.setColumnCount(4);
    self._werrlist.setSortingEnabled(False);
    self._werrlist.setRootIsDecorated(True);
    try: # only in qt-4.2 and later
      self._werrlist.setAllColumnsShowFocus(True);
    except AttributeError:
      pass;
    header = self._werrlist.header();
    header.hide(); # setHeaderHidden(True);
    header.setStretchLastSection(False);
    for col in [0,2,3]:
      header.setResizeMode(col,QHeaderView.ResizeToContents);
    header.setResizeMode(1,QHeaderView.Stretch);
    self._werrlist.setSelectionMode(QAbstractItemView.SingleSelection);
    # size the widget
    # self.setMinimumSize(QSize(500,120));
    # self.setGeometry(0,0,800,120);
    # anchor and position relative to anchor
    self._anchor_widget = None;
    self._anchor_xy0 = None;
    self._anchor_xy  = 0,0;
    self._current_xy = 0,0;
    self._anchor_ref = 0,0;
    self._anchoring = False;
    # explicit geometry set via anchor, None of none set
    self._geom = None;
    # timer used for move operations
    self._move_timer = QTimer(self);
    self._move_timer.setSingleShot(True);
    # internal state
    self._item_shown = None;
    self._in_show_error_item = False;
    self._error_list = [];

  def closeEvent (self,ev):
    """Window closed: hide and set a flag""";
    self.hide();
    ev.ignore();

  def show (self):
    """Only show the window if we have errors in it""";
    if self._error_list:
      QMainWindow.show(self);

  def moveEvent (self,ev):
    QMainWindow.moveEvent(self,ev);
#    print "moveEvent spontaneous:",ev.spontaneous();
    # ignore move events for some time after a move_anchor() -- these are probably caused
    # by the anchor moving us, and not by the user
    if not self._move_timer.isActive():
      self._current_xy = self.geometry().x(),self.geometry().y();
#      print "current xy is",self._current_xy;

  def showEvent (self,ev):
#    print "showEvent spontaneous:",ev.spontaneous();
    if not ev.spontaneous():
      x,y = self._current_xy;
      self.setGeometry(x,y,self.width(),self.height());
      self._move_timer.start(200);
    QMainWindow.showEvent(self,ev);
#    print "showEvent ends";

  def set_anchor (self,widget,x,y,xref=0,yref=0):
    """Tells the window to anchor itself to point x,y of the given widget.
    If xref is 0, x is relative to the left side, otherwise to the right side.
    If yref is 0, y is relative to the top edge, otherwise to the bottom edge.
    """;
    self._anchor_widget = widget;
    self._anchor_xy = x,y;
    self._anchor_ref = xref,yref;
#    print "anchoring to",x,y,xref,yref;
    self.move_anchor();

  def move_anchor (self):
    """Notifies the window that its anchor widget has moved around.
    Changes position following the anchor.""";
    # get dx,dy coordinates relative to old anchor point
    if self._anchor_xy0 is not None:
      x0,y0 = self._anchor_xy0;
      x,y = self._current_xy;
#      print "move_anchor: old location is",x,y;
      dx = x - x0;
      dy = y - y0;
    else:
      dx = dy = 0;
#    print "move_anchor: dxy relative to old anchor is",dx,dy;
    # compute new anchoring point
    top = self._anchor_widget.mapToGlobal(QPoint(0,0));
    btm = self._anchor_widget.mapToGlobal(QPoint(self._anchor_widget.width(),
                          self._anchor_widget.height()));
    #print "move_anchor: widget top is",top.x(),top.y();
    #print "move_anchor: widget btm is",btm.x(),btm.y();
    x,y = self._anchor_xy;
    # add to coordinates of reference point on anchor
    if self._anchor_ref[0]:
      x0 = btm.x() + x;
    else:
      x0 = top.x() + x;
    if self._anchor_ref[1]:
      y0 = btm.y() + y;
    else:
      y0 = top.y() + y;
    # move to new location
    #print "move_anchor: new location is",x0,y0;
    self._anchor_xy0 = x0,y0;
    self._current_xy = x0+dx,y0+dy;
    self.setGeometry(x0+dx,y0+dy,self.width(),self.height());
    # Start a timer to ignore move events for a bit. The reason for this is that sometimes
    # very rapid moving of the main window causes the float to "lag" because the setGeometry()
    # call is not processed before another call to move_anchor(). A small delay should eliminate this.
    self._move_timer.setSingleShot(True);
    self._move_timer.start(200);

  def _populate_error_list (self,parent,errlist,toplevel=False):
    """helper function to recursively populate the error ListView""";
    previtem = None;
    for index,err in enumerate(errlist):
      if isinstance(err,TDL.TDLError):
        errmsg = str(err.args[0]);
      else:
        errmsg = str(err);
      filename = getattr(err,'filename',None);
      line = getattr(err,'lineno',0);
      column = getattr(err,'offset',0) or 0;  # offset is sometimes None, make sure this is 0
      suberror = isinstance(err,TDL.NestedTDLError);
      _dprint(1,errmsg,"at",filename,line,column);
      # index of corresponding top-level item
      toplevel_index = len(self._toplevel_error_items)-1;
      if toplevel:
        toplevel_index += 1;
      # create item
      if previtem is not None:
        previtem = item = QTreeWidgetItem(parent,previtem);
      else:
        previtem = item = QTreeWidgetItem(parent);
      item.setText(0,"%d:"%(toplevel_index+1,));
      item.setTextAlignment(0,Qt.AlignLeft);
      # add housekeeping info
      item._toplevel_index = toplevel_index;
      if toplevel:
	      self._toplevel_error_items.append(item);
      toplevel_index = len(self._toplevel_error_items)-1;
      self._error_items.append(item);
      item.setExpanded(False);
      # set item content
      if filename is None:
        item.setText(1,errmsg);
        item.setText(2,"<unknown>");
        item.setText(3,"(%s)"%err.__class__.__name__);
      else:
        # normalize filenames: eliminate CWD, leave just one path element
        fname = filename;
        try: is_cwd = os.path.samefile(os.path.dirname(fname),'.');
        except: is_cwd = False;
        if is_cwd:
          fname = os.path.basename(filename);
        else:
          dirname,fname = os.path.split(filename);
          dir1,dir2 = os.path.split(dirname);
          if dir1 == '/' or not dir1:
            fname = filename;
          else:
            fname = os.path.join("...",dir2,fname);
        item.setText(1,errmsg);
        item.setText(3,"(%s)"%err.__class__.__name__);
        item._err_location = len(self._error_items)-1,filename,line,column,suberror;
        self._error_locations.append(item._err_location);
        item.setText(2,"[%s:%d]" % (fname,line));
      # recursively populate with nested errors if needed
      nested = getattr(err,'nested_errors',None);
      if nested:
        self._populate_error_list(item,nested);
    # resize ourselves according to number of errors and width of treeview
    height = (len(errlist)+1)*self._werrlist.fontMetrics().lineSpacing();
    height = min(200,height);
    # work out recommended width
    width = 400;  # initial width for message section
    # add width of other sections
    for col in [0,2,3]:
      width += self._werrlist.header().sectionSize(col);
    _dprint(2,"hinted width is",width);
    self.setGeometry(self.x(),self.y(),max(width,self.width()),height);
    self.updateGeometry();

  def set_errors (self,error_list,emit_signal=True,show_item=True,
                      message="TDL compile failed"):
    """Shows an error list. errlist should be a sequence of Exception
    objects following the TDL error convention.
    message is a status message
    If show_item=True, highlights the first error
    If emit_signal=True, emits a hasErrors(nerr) pysignal
    """;
    _dprint(1,"set_errors: list of",len(error_list),"entries");
    _dprint(1,"current list has",len(self._error_list),"entries");
    # do nothing if already set
    if self._error_list is error_list:
      return;
    self.clear_errors(emit_signal=False);
    self._error_list = error_list;
    self._error_locations = [];         # list of error locations
    self._error_items = [];
    self._toplevel_error_items = [];
    if error_list:
      self._populate_error_list(self._werrlist,error_list,toplevel=True);
      nerr = len(self._toplevel_error_items);
      self._error_count_label.setText('%s: <b>%d</b> errors'%(message,nerr));
      self.setWindowTitle("TDL Errors: %d"%nerr);
      if emit_signal:
        self.emit(PYSIGNAL("hasErrors"),nerr);
      if show_item:
        self._show_error_item(self._toplevel_error_items[0]);
      self.show();
      # self._highlight_error(0);
      # disable run control until something gets modified
      # self._qa_run.setVisible(False);
    else:
      if emit_signal:
        self.emit(PYSIGNAL("hasErrors"),0);
      self.setWindowTitle("TDL Errors");
      self.hide();

  def get_error_list (self):
    return self._error_list;

  def get_error_locations (self):
    return self._error_locations;

  def clear_errors (self,emit_signal=True):
    """clears the error list. If emit_signal=True, emits a hasErrors(0) pysignal""";
    if emit_signal:
      self.emit(PYSIGNAL("hasErrors"),0);
    self._error_items = self._toplevel_error_items = None;
    self.setWindowTitle("TDL Errors");
    self._werrlist.clear();
    self._error_count_label.setText('');
    self._error_list = [];
    self._error_locations = [];
    self._item_shown = None;
    self.hide();

  def _highlight_error_item (self,item,emit_signal=True):
    """highlights the given error item. If emit_signal=True, emits a
    showError(index,filename,line,column) or showError(None) pysignal.
    """;
    if item:
      self.show();
      toplevel_index = item._toplevel_index;
      self._qa_prev_err.setEnabled(toplevel_index > 0);
      self._qa_next_err.setEnabled(toplevel_index < len(self._toplevel_error_items)-1);
      # does item contain a location attribute?
      errloc = getattr(item,'_err_location',None);
      if errloc:
        # indicate location
        _dprint(1,"highlighting error in",errloc);
        if emit_signal:
          self.emit(PYSIGNAL("showError"),*errloc);
        return
    # if we fell through to here, then no error has been shown -- emit appropriate signal
    if emit_signal:
      self.emit(PYSIGNAL("showError"),None,None,None,None);

  def _show_next_error (self):
    item = self._werrlist.currentItem();
    if item:
      toplevel_index = item._toplevel_index + 1;
      if toplevel_index >= len(self._toplevel_error_items):
        toplevel_index = 0;
      item = self._toplevel_error_items[toplevel_index];
    else:
      item = self._error_items[0];
    if item:
      self._show_error_item(item);

  def _show_prev_error (self):
    item = self._werrlist.currentItem();
    if item:
      toplevel_index = item._toplevel_index - 1;
      if toplevel_index < 0:
        toplevel_index = len(self._toplevel_error_items)-1;
      item = self._toplevel_error_items[toplevel_index];
    else:
      item = self._toplevel_error_items[-1];
    if item:
      self._show_error_item(item);

  def show_error_number (self,index,emit_signal=True):
    self._show_error_item(self._error_items[index],emit_signal=emit_signal);

  def _show_error_item (self,item,emit_signal=True):
    # do nothing if item is None, or already shown, or if already within this function
    if item is None or self._in_show_error_item or item is self._item_shown:
      return;
    self._in_show_error_item = True;
    try:
      self._item_shown = item;
      self._werrlist.setCurrentItem(item);
      for other in self._toplevel_error_items:
        if other is item:
          other.setExpanded(True);
        else:
          other.setExpanded(False);
      self._werrlist.scrollToItem(item);
      self._highlight_error_item(item,emit_signal=emit_signal);
    finally:
      self._in_show_error_item = False;

  def _process_item_click (self,why,item,dum=None):
    self._show_error_item(item,emit_signal=True);


