#!/usr/bin/python

from dmitypes import *
from qt import *
from app_pixmaps import pixmaps
import weakref
import meqds
import copy
import app_browsers
import meq
from meqds import mqs
from treebrowser import NodeAction
from numarray import *
from time import sleep

class editRequest(QDialog):
    def __init__(self, parent):
        self.parent = parent
        QDialog.__init__(self, parent, 'TEST', 1, 0)
        self.setCaption('Test')
        self.setGeometry(30, 30, 200, 100)

        self.v = QVBoxLayout(self, 10, 5)

        self.Xh = QHBoxLayout(self.v, 5)
        lbl = QLabel('X', self)
        self.Xh.addWidget(lbl)
        self.X0 = QLineEdit(self)
        self.X0.setText(str(self.parent.f0))
        self.Xh.addWidget(self.X0)
        self.Xn = QLineEdit(self)
        self.Xn.setText(str(self.parent.fn))
        self.Xh.addWidget(self.Xn)
        self.X1 = QLineEdit(self)
        self.X1.setText(str(self.parent.f1))
        self.Xh.addWidget(self.X1)

        self.Yh = QHBoxLayout(self.v, 5)
        lbl = QLabel('Y', self)
        self.Yh.addWidget(lbl)
        self.Y0 = QLineEdit(self)
        self.Y0.setText(str(self.parent.t0))
        self.Yh.addWidget(self.Y0)
        self.Yn = QLineEdit(self)
        self.Yn.setText(str(self.parent.tn))
        self.Yh.addWidget(self.Yn)
        self.Y1 = QLineEdit(self)
        self.Y1.setText(str(self.parent.t1))
        self.Yh.addWidget(self.Y1)
        
        self.cmdOK = QPushButton('OK', self)
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)
        self.v.addWidget(self.cmdOK)

        self.show()

    def slotcmdOK(self):
        self.parent.f0 = float(str(self.X0.text()))
        self.parent.f1 = float(str(self.X1.text()))
        self.parent.fn = int(str(self.Xn.text()))
        self.parent.t0 = float(str(self.Y0.text()))
        self.parent.t1 = float(str(self.Y1.text()))
        self.parent.tn = int(str(self.Yn.text()))
	self.parent.doNewRequest()
        self.close()

class askNumber(QDialog):
    def __init__(self, parent, name='LoopCnt', modal=1):
        self.parent = parent
        QDialog.__init__(self, parent, name, modal, 0)
        self.setCaption('LoopCnt')
        self.setGeometry(30, 30, 200, 100)

        self.v = QVBoxLayout(self, 10, 5)

        self.Xh = QHBoxLayout(self.v, 5)
        lbl = QLabel('X', self)
        self.Xh.addWidget(lbl)
        self.X0 = QLineEdit(self)
        self.X0.setText(str(self.parent.DTime))
        self.Xh.addWidget(self.X0)

        self.cmdOK = QPushButton('OK', self)
        QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)
        self.v.addWidget(self.cmdOK)

        self.show()

    def slotcmdOK(self):
        x0 = int(str(self.X0.text()))
        self.parent.DTime = x0;
        self.parent.timer = self.parent.startTimer(self.parent.DTime);
        self.parent.buttonLoop.setText('Stop');
        self.close()

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
    self.doLoop = False;
    self.DTime = 1000;
    self.f0 = 0;
    self.f1 = 1;
    self.fn = 10;
    self.t0 = 0;
    self.t1 = 1;
    self.tn = 10;
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

    self.buttonDef = QPushButton(self)
    self.buttonDef.setText('NewRequest')
    Layout1.addWidget(self.buttonDef)

    self.buttonLoop = QPushButton(self);
    self.buttonLoop.setText('Loop');
    Layout1.addWidget(self.buttonLoop);

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
    self.connect(self.buttonDef,SIGNAL("clicked()"),self.newreq)
    self.connect(self.buttonLoop,SIGNAL("clicked()"),self.toggleLoop)

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
#      self.buttonOk.setEnabled(True);
    else:  # got request in state
      self.reqView.wlistview().setRootIsDecorated(True);
#      self._request = copy.deepcopy(request);
      self._request = state.request;
      self._request.request_id = hiid();
      self.buttonOk.setEnabled(True);
      self.reqView.set_content(self._request);
      self.reqView.set_open_items(self.defaultOpenItems);

    
  def reject (self):
    self._node = self._request = self._callback = None; # this will disconnect the Qt signal
    self.killTimers();
    QDialog.hide(self);
    
  def accept (self):
    if not self._request:
      return;
    cmd = srecord(nodeindex=self._node.nodeindex,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);
    self.hide();

  def toggleLoop(self):
    if not self._request:
      return;
    self.doLoop = not self.doLoop
    if self.doLoop:
      askNumber(self)
    else:
      self.killTimers();
      self.buttonLoop.setText('Loop');
    
  def timerEvent(self, event):
      if self.doLoop:
        cmd = srecord(nodeindex=self._node.nodeindex,request=self._request,get_state=True);
        mqs().meq('Node.Execute',cmd,wait=False);
    

  def newreq(self):
    editRequest(self);

  def doNewRequest(self):
    newd = meq.domain(self.f0, self.f1, self.t0, self.t1);
    newc = meq.cells(domain=newd, num_freq=self.fn, num_time=self.tn);
    self._request = meq.request(cells=newc);
    self._request.request_id = hiid();
    cmd = srecord(nodeindex=self._node.nodeindex,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);
    self.hide();

def define_treebrowser_actions (tb):
  tb.add_action(NA_NodeExecute,30,where="node");

