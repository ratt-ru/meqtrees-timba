#!/usr/bin/python

import Timba
from Timba.dmi import *
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.treebrowser import NodeAction
import Timba.GUI.app_proxy_gui 
from Timba.GUI.meqserver_gui import makeNodeDataItem
from Timba import Grid

from qt import *

_dbg = verbosity(0,name='node_exec');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class NA_NodeExecute (NodeAction):
  text = "Reexecute";
  iconset = pixmaps.reexecute.iconset;
  def activate (self,node):
    Grid.Services.addDataItem(makeNodeDataItem(node,viewer=Executor));
    
  def is_enabled (self,node):
    # available in idle mode, or when stopped at a debugger. 
    # If debug_level is set, node must be idle (otherwise, we can't trust the
    # node control status to be up-to-date)
    return ( self.tb.is_stopped or not self.tb.is_running ) and \
           ( not self.tb.debug_level or node.is_idle() );

_request_type = dmi_type('MeqRequest',record);

class Executor (browsers.GriddedPlugin):
  viewer_name = "Executor";
  _icon = pixmaps.reexecute;
  
  def is_viewable (data):
    return isinstance(data,_request_type) or \
      isinstance(getattr(data,'request',None),_request_type);
  is_viewable = staticmethod(is_viewable);
  
  defaultOpenItems = ({'cells':({'grid':None,'domain':None},None)},None);
  
  def __init__(self,gw,dataitem,cellspec={},**opts):
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    _dprint(1,"started with",dataitem.udi,dataitem.data);
    self._has_data = False;
    self._request = None;
    self._wtop = QVBox(self.wparent());
  
    udi_root = dataitem.udi;
    if not udi_root.endswith('/request'): # not a direct request object
      udi_root += '/request';
    self.reqView = browsers.HierBrowser(self.wtop(),"","",udi_root=udi_root);
    QObject.connect(self.reqView.wtop(),PYSIGNAL("displayDataItem()"),
                    self.wtop(),PYSIGNAL("displayDataItem()"));
    self.reqView.set_refresh_func(dataitem.refresh_func);
    
    buttonbox = QHBox(self.wtop());
    self.buttonOk = QPushButton(buttonbox,"buttonOk");
    self.buttonOk.setText("&Execute");
    self.buttonOk.setIconSet(pixmaps.reexecute.iconset());
    self.buttonOk.setAccel(Qt.ALT+Qt.Key_E);
    
    buttonRefresh = QPushButton(buttonbox,"buttonRefresh");
    buttonRefresh.setText("&Refresh");
    buttonRefresh.setIconSet(pixmaps.refresh.iconset());
    buttonRefresh.setAccel(Qt.ALT+Qt.Key_R);
    
    QObject.connect(self.buttonOk,SIGNAL("clicked()"),self._reexecute);
    QObject.connect(buttonRefresh,SIGNAL("clicked()"),
                    self.wtop(),PYSIGNAL("refresh()"));
    QObject.connect(self.wtop(),PYSIGNAL("refresh()"),self._refresh);
    
    ### refresh initially disabled, until we get data in
    self.buttonOk.setEnabled(0);
    
    # form a caption and set contents
    (name,ni) = meqds.parse_node_udi(dataitem.udi);
    caption = "Reexecute <b>%s</b>" % (name or '#'+str(ni),);
    self._node = ni;
    # setup widgets
    self.set_widgets(self.wtop(),caption,icon=self.icon());
    
    # connect font signal 
    QObject.connect(self.wtop(),PYSIGNAL("fontChanged()"),
                      self.reqView.wtop(),PYSIGNAL("fontChanged()"));
    # add menu entry
    context_menu = self.cell_menu();
    if context_menu is not None:
      context_menu.insertSeparator();
      menu = browsers.PrecisionPopupMenu(context_menu,prec=self.reqView.get_precision());
      context_menu.insertItem(pixmaps.precplus.iconset(),'Number format',menu);
      QWidget.connect(menu,PYSIGNAL("setPrecision()"),\
                      self.reqView.set_precision);
    
    # set data
    if dataitem.data is not None:
      self.set_data(dataitem);
    
  def wtop(self):
    return self._wtop;

  def set_data (self,dataitem,**opts):
    _dprint(2,'set_data called, has_data is',self._has_data);
    if not self._has_data: 
      self._has_data = True;
      req = dataitem.data;
      # data is not a request, must be node state then
      if not isinstance(req,_request_type):
        req = getattr(req,'request',None);
        # if no request in node state, report this
        if not isinstance(req,_request_type): 
          if self._request is not None:
            QMessageBox.warning(self.wtop(),'Missing request',
                "No request field found in node state, keeping old request",
                QMessageBox.Ok,QMessageBox.NoButton);
          else:
            self.reqView.wlistview().setRootIsDecorated(False);
            self.reqView.clear();
            QListViewItem(self.reqView.wlistview(),'','','(no request found in node)');
          return;
      # ok, at this point req is a valid request object, load it
      self._request = req;
      self.reqView.wlistview().setRootIsDecorated(True);
      self._request.request_id = hiid();
      self.buttonOk.setEnabled(True);
      self.reqView.set_content(self._request);
      self.reqView.set_open_items(self.defaultOpenItems);
      # enable cell and flash
      self.enable();
      self.flash_refresh();
      
  def _refresh (self):
    # clear the has_data flag, so that set_data above will accept new data
    _dprint(2,'refresh expected now');
    self._has_data = False;
    
  def _reexecute (self):
    if not self._request:
      return;
    _dprint(1,'accepted: ',self._request);
    cmd = record(nodeindex=self._node,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);
    
    

def define_treebrowser_actions (tb):
  _dprint(1,'defining node-execute treebrowser actions');
  tb.add_action(NA_NodeExecute,30,where="node");

Grid.Services.registerViewer(_request_type,Executor,priority=25);
Grid.Services.registerViewer(meqds.NodeClass(),Executor,priority=25);

