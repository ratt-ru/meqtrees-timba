#!/usr/bin/python

import meqserver
from app_proxy_gui import *

class meqserver_gui (app_proxy_gui):

  def make_node_list (self,nlrec)
    

  class TreeBrowser (object):
    def __init__ (parent):
      self._splitter = QSplitter(QSplitter.Horizontal,parent);
      self._nodelist = QListView(self._splitter);
      self._nodelist.addColumn('name');
      self._nodelist.addColumn('lbl');
      self._nodelist.addColumn('class');
      self._nodelist.addColumn('index');
      self._nodelist.setRootIsDecorated(True);
      # self._nodelist.setSorting(-1);
      self._nodelist.setResizeMode(QListView.NoColumn);
      for icol in range(4):
        self._nodelist.setColumnWidthMode(icol,QListView.Maximum);
      self._nodelist.setFocus();
      self._nodelist.connect(self._nodelist,SIGNAL('expanded(QListViewItem*)'),
                       self._expand_node);
                       
    def _expand_node (self,item):
      pass;
      
    def set_node_list (self,nodelist):
      pass;
      
      
      
      
    

  def __init__(self,app,*args,**kwargs):
    # init standard proxy GUI
    app_proxy_gui.__init__(self,app,*args,**kwargs);
    self.dprint(2,"meqserver-specifc init"); 
    
    # add extra panels
    self.resultlog = Logger(self,"node result log",limit=100);
    self.maintab.insertTab(self.resultlog.wtop(),"Result Log",1);
    self.resultlog.wtop()._default_iconset = QIconSet();
    self.resultlog.wtop()._default_label   = "Result Log";
    self.resultlog.wtop()._newres_iconset  = QIconSet(pixmaps.check.pm());
    self.resultlog.wtop()._newres_label    = "New Results";
    self.connect(self.maintab,SIGNAL("currentChanged(QWidget*)"),self._reset_resultlog_label);
    # add handler
    self._add_ce_handler("node.result",self.ce_NodeResult);
    
  def ce_NodeResult (self,ev,value):
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
      
  def _reset_resultlog_label (self,tabwin):
    if tabwin is self.resultlog.wtop():
      self._reset_maintab_label(tabwin);

  customEventMap = app_proxy_gui.customEventMap.copy();
  customEventMap[hiid("node.result")] = ce_NodeResult;
  
