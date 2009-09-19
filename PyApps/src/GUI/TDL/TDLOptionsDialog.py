# -*- coding: utf-8 -*-
from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL

import Timba
from Timba.dmi import *
from Timba.utils import *
from Timba.GUI.pixmaps import pixmaps
  
class TDLOptionsDialog (QDialog,PersistentCurrier):
  """implements a floating window for TDL options""";
  def __init__ (self,parent,ok_label=None,ok_icon=None):
    QDialog.__init__(self,parent);
    self.setSizeGripEnabled(True);
    
    lo_main = QVBoxLayout(self);
    # add option treeWidget
    self._tw = QTreeWidget(self);
    self._tw.setColumnCount(3);
    self._tw.setRootIsDecorated(True);
    self._tw.setSortingEnabled(False);
    self._tw.setSelectionMode(QAbstractItemView.NoSelection);
    
    self._tw.header().setResizeMode(0,QHeaderView.ResizeToContents);
    self._tw.header().setResizeMode(1,QHeaderView.ResizeToContents);
    self._tw.header().setResizeMode(2,QHeaderView.Stretch);
    self._tw.header().hide();
    QObject.connect(self._tw.header(),SIGNAL("sectionResized(int,int,int)"),self._resize_dialog);
    self._allow_resize_dialog = True;
    # self._tw.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    # add signals
    QObject.connect(self._tw,SIGNAL("itemClicked(QTreeWidgetItem*,int)"),self._process_treewidget_click);
    QObject.connect(self._tw,SIGNAL("itemActivated(QTreeWidgetItem*,int)"),self._process_treewidget_press);
    # self._tw.setMinimumSize(QSize(200,100));
    lo_main.addWidget(self._tw);
    # set geometry
    # self.setMinimumSize(QSize(200,100));
    # self.setGeometry(0,0,200,60);
    
    # add buttons on bottom
    lo_btn  = QHBoxLayout(None);
    if ok_label:
      if ok_icon:
        self.wok = QPushButton(ok_icon.icon(),ok_label,self);
      else:
        self.wok = QPushButton(ok_label,self);
      lo_btn.addWidget(self.wok);
      QObject.connect(self.wok,SIGNAL("clicked()"),self.accept);
    else:
      self.wok = None; 
    # add cancel button
    tb = QPushButton(pixmaps.red_round_cross.icon(),"Cancel",self);
    QObject.connect(tb,SIGNAL("clicked()"),self.hide);
    spacer = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum);
    lo_btn.addItem(spacer)
    lo_btn.addWidget(tb);
    lo_main.addLayout(lo_btn);
    self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))

  def enableOkButton (self,enable):
    if self.wok:
      self.wok.setEnabled(enable);

  def _resize_dialog (self,section,*dum):
    if self._allow_resize_dialog and section<2:
      width = 128;  # initial size of help section
      # add width of other sections
      for col in [0,1]:
	width += self._tw.header().sectionSize(col);
      # print width;
      self.resize(max(width,self.width()),self.height());
      
  def accept (self):
    self.emit(PYSIGNAL("accepted()"));
    self.hide();
    
  def show (self):
    #self._tw.adjustColumn(0);
    #self._tw.adjustColumn(1);
    return QDialog.show(self);
  
  def exec_ (self):
    #self._tw.adjustColumn(0);
    #self._tw.adjustColumn(1);
    return QDialog.exec_(self);
  
  def treeWidget (self):
    return self._tw;
  
  def clear (self):
    self._tw.clear();
    
  class ActionListViewItem (QTreeWidgetItem):
    def __init__ (self,*args):
      QTreeWidgetItem.__init__(self,*args);
      font = QFont(self.font(0));
      font.setBold(True);
      self.setFont(0,font);
    
  def addAction (self,label,callback,icon=None):
    # find last item
    last = self._tw.topLevelItem(self._tw.topLevelItemCount()-1);
    item = self.ActionListViewItem(self._tw,last);
    item.setText(0,label);
    if icon:
      item.setIcon(0,icon.icon());
    item._on_click = callback;
    item._close_on_click = True;
    
  def _process_treewidget_click (self,item,*dum):
    """helper function to process a click on a treeWidget item. Meant to be connected
    to the clicked() signal of a QListView""";
    getattr(item,'_on_click',lambda:None)();
    if getattr(item,'_close_on_click',False):
      self.hide();
      
  def _process_treewidget_press (self,item,*dum):
    """helper function to process a press on a treeWidget item. Meant to be connected
    to the pressed() signal of a QListView""";
    getattr(item,'_on_press',lambda:None)();

