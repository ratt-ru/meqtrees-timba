#!/usr/bin/python

from dmitypes import *
from qt import *
from app_pixmaps import pixmaps
import weakref
import meqds
import copy
import app_browsers
from meqds import mqs
from treebrowser import NodeAction

_dbg = verbosity(0,name='node_exec');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;


class NA_NodeExecute (NodeAction):
  text = "Reexecute";
  iconset = pixmaps.reexecute.iconset;
  def activate (self):
    try: dialog = self.item.tb._node_reexecute_dialog;
    except AttributeError:
      self.item.tb._node_reexecute_dialog = dialog = NodeExecuteDialog(self.item.tb.wtop());
    dialog.show(self.node);
  def is_enabled (self):
    # available in idle mode, or when stopped at a debugger. 
    # If debug_level is set, node must be idle (otherwise, we can't trust the
    # node control status to be up-to-date)
    return ( self.tb.is_stopped or not self.tb.is_running ) and \
           ( not self.tb.debug_level or self.node.is_idle() );


class NodeExecuteDialog (QDialog):
  defaultOpenItems = ({'cells':({'grid':None,'domain':None},None)},None);
  def __init__(self,parent = None,name = None,modal = 0,fl = 0):
    QDialog.__init__(self,parent,name,modal,fl)
    if not name:
        self.setName("NodeExecuteDialog")
    self.setSizeGripEnabled(1)

    NodeExecuteDialogLayout = QVBoxLayout(self,11,6,"NodeExecuteDialogLayout")

    ### custom settings 
    self.setIcon(pixmaps.reexecute.pm());
    reqFrame = QVBox(self);
    reqFrame.setFrameShape(QFrame.Panel+QFrame.Sunken);
    reqFrame.setMargin(10);
    reqCtrlFrame = QHBox(reqFrame);
    self.reqRefresh = QToolButton(reqCtrlFrame);
    self.reqRefresh.setIconSet(pixmaps.refresh.iconset());
    self.reqRefresh.setAutoRaise(True);
    self.reqRefresh.setSizePolicy(QSizePolicy(0,0));  # fixed size
    QObject.connect(self.reqRefresh,SIGNAL("clicked()"),self._dorefresh);
    QToolTip.add(self.reqRefresh,"refresh request from node state");
    self.reqViewLabel = QLabel(" Request:",reqCtrlFrame);
    self.reqView = app_browsers.HierBrowser(reqFrame,"","");
    NodeExecuteDialogLayout.addWidget(reqFrame);
    ###
    
    Layout1 = QHBoxLayout(None,0,6,"Layout1")
    Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
    Layout1.addItem(Horizontal_Spacing2)

    self.buttonOk = QPushButton(self,"buttonOk")
    self.buttonOk.setAutoDefault(1)
    self.buttonOk.setDefault(1)
    Layout1.addWidget(self.buttonOk)

    self.buttonCancel = QPushButton(self,"buttonCancel")
    self.buttonCancel.setAutoDefault(1)
    Layout1.addWidget(self.buttonCancel)
    NodeExecuteDialogLayout.addLayout(Layout1)

    self.languageChange()

    self.resize(QSize(511,482).expandedTo(self.minimumSizeHint()))
    self.clearWState(Qt.WState_Polished)

    self.connect(self.buttonOk,SIGNAL("clicked()"),self.accept)
    self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)
    
    ### custom settings 
    self.buttonOk.setIconSet(pixmaps.reexecute.iconset());
    self.buttonOk.setEnabled(0);
    self.buttonCancel.setIconSet(pixmaps.cancel.iconset());

  def languageChange(self):
    self.setCaption(self.__tr("Execute node"))
    self.buttonOk.setText(self.__tr("&Execute"))
    self.buttonOk.setAccel(self.__tr("Alt+E"))
    self.buttonCancel.setText(self.__tr("&Cancel"))
    self.buttonCancel.setAccel(QString.null)

  def __tr(self,s,c = None):
      return qApp.translate("NodeExecuteDialog",s,c)

  def show (self,node):
    self.setCaption("Execute node: "+node.name);
    self.reqView.clear();
    self._node = weakref_proxy(node);
    self._request = None;
    self._dorefresh();
    QDialog.show(self);
    
  def _dorefresh (self):
    # request node state, and subscribe to it via the curried callback
    # the curry() is handy because it will automatically disconnect the
    # subscription when deleted
    self._callback = curry(self._update_state);
    self._node.subscribe_state(self._callback);
    meqds.request_node_state(self._node);
    
  def _update_state(self,node,state,event=None):
    if self._request:
      return;
    try: request = state.request;
    except AttributeError: 
      self.reqView.wlistview().setRootIsDecorated(False);
      QListViewItem(self.reqView.wlistview(),'','','(no request found in node)');
    else:  # got request in state
      self.reqView.wlistview().setRootIsDecorated(True);
      self._request = copy.deepcopy(request);
      self._request.request_id = hiid();
      self.buttonOk.setEnabled(True);
      self.reqView.set_content(self._request);
      self.reqView.set_open_items(self.defaultOpenItems);

    
  def reject (self):
    self._node = self._request = self._callback = None; # this will disconnect the Qt signal
    QDialog.hide(self);
    
  def accept (self):
    if not self._request:
      return;
    cmd = srecord(nodeindex=self._node.nodeindex,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);
    self.hide();


def define_treebrowser_actions (tb):
  _dprint(1,'defining node-execute treebrowser actions');
  tb.add_action(NA_NodeExecute,30,where="node");

