#!/usr/bin/env python3

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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

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
from Timba.array import *
from Timba.Meq import meq
from time import sleep
from qt import *
from string import *
from operator import isNumberType

_dbg = verbosity(0,name='node_exec');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class editRequest(QDialog):
  def __init__(self, parent):
    self.parent = parent
    QDialog.__init__(self, parent._wtop, 'TEST', 1, 0)
    self.setCaption('Test')
#    self.setGeometry(30, 30, 400, 200)

#
# All input/text/button widgets are in rows -> enclosed in a VBox
#
    self.top = QVBoxLayout(self, 10, 5)

#
# All input/text widgets are in are in columns -> envlosed in an HBox
#
    self.UserIn = QHBoxLayout(self.top)

#
# Left side lables
#
    self.LeftLables = QVBoxLayout(self.UserIn, 5)
    lbl = QLabel(' ', self)
    self.LeftLables.addWidget(lbl)
    lbl = QLabel('Freq', self)
    self.LeftLables.addWidget(lbl)
    lbl = QLabel('Time', self)
    self.LeftLables.addWidget(lbl)

#
# Start values
#
    self.StartValues = QVBoxLayout(self.UserIn, 5)
    lbl = QLabel('start', self)
    self.StartValues.addWidget(lbl);
    self.X0 = QLineEdit(self)
    self.X0.setText(str(self.parent.f0))
    self.StartValues.addWidget(self.X0)
    self.Y0 = QLineEdit(self)
    self.Y0.setText(str(self.parent.t0))
    self.StartValues.addWidget(self.Y0)
    
#
# Number of steps
#
    self.StepValues = QVBoxLayout(self.UserIn, 5)
    lbl = QLabel('n-steps', self)
    self.StepValues.addWidget(lbl);
    self.Xn = QLineEdit(self)
    self.Xn.setText(str(self.parent.fn))
    self.StepValues.addWidget(self.Xn)
    self.Yn = QLineEdit(self)
    self.Yn.setText(str(self.parent.tn))
    self.StepValues.addWidget(self.Yn)

#
# Stop values
#
    self.StopValues = QVBoxLayout(self.UserIn, 5)
    lbl = QLabel('stop', self)
    self.StopValues.addWidget(lbl);
    self.X1 = QLineEdit(self)
    self.X1.setText(str(self.parent.f1))
    self.StopValues.addWidget(self.X1)
    self.Y1 = QLineEdit(self)
    self.Y1.setText(str(self.parent.t1))
    self.StopValues.addWidget(self.Y1)

#
# Variable Time
#
#    self.TimeRange = QHBoxLayout(self.top, 5)
#    lbl = QLabel('Time', self)
#    self.TimeRange.addWidget(lbl)
#    self.TimeEdit = QLineEdit(self)
#    self.TimeRange.addWidget(self.TimeEdit)

#
# Buttons
#
    self.Buttons = QHBoxLayout(self.top, 5)
    self.cmdOK = QPushButton('OK', self)
    QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)
    self.Buttons.addWidget(self.cmdOK)
    self.cmdCancel = QPushButton('Cancel', self)
    QObject.connect(self.cmdCancel, SIGNAL('clicked()'), self.slotcmdCancel)
    self.Buttons.addWidget(self.cmdCancel)

    self.show()

  def slotcmdCancel(self):
    self.close();

  def slotcmdOK(self):
    f0 = float(str(self.X0.text()));
    f1 = float(str(self.X1.text()));
    fn = int(str(self.Xn.text()))

    if f0 == f1:
       f1 = f1 + 1;
    if fn == 0: fn = 1

    self.parent.f0 = f0;
    self.parent.f1 = f1;
    self.parent.fn = fn;

    t1 = float(str(self.Y1.text()))
    tn = int(str(self.Yn.text()))
    if tn == 0: tn = 1
    self.parent.tn = tn
#
# Allow three values for t0
#
    tvalue = str(self.Y0.text())
    s1 = split(tvalue)
    l = len(s1)
    t00 = float(s1[0])
    if l == 1:
      t01 = 0
      t02 = -1
    elif l == 2:
      t01 = 1
      t02 = float(s1[1])
    else:
      t01 = float(s1[1])
      t02 = float(s1[2])
    dt = t1 - t00
    if t02 == -1:
      self.parent.t0 = t00
      if t1 == t00:
        t1 = t1+1
      self.parent.t1 = t1
      self.parent.doNewRequest()
    else:
      t = t00
      while t <= t02:
        self.parent.t0 = t
        self.parent.t1 = self.parent.t0 + dt
        self.parent.doNewRequest()
        t = t + t01

#    self.close()

class startLoop(QDialog):
  def __init__(self, parent, name='LoopCnt', modal=0):
    self.parent = parent
    QDialog.__init__(self, parent._wtop, name, modal, 0)
    self.setCaption('LoopCnt')
    self.DTime = 1000;
    self.setGeometry(30, 30, 200, 100)

    self.v = QVBoxLayout(self, 10, 5)

    self.Xh = QHBoxLayout(self.v, 5)
    lbl = QLabel('X', self)
    self.Xh.addWidget(lbl)
    self.X0 = QLineEdit(self)
    self.X0.setText(str(self.DTime))
    self.Xh.addWidget(self.X0)

    self.buttons = QHBoxLayout(self.v, 5)
    self.cmdOK = QPushButton('OK', self)
    QObject.connect(self.cmdOK, SIGNAL('clicked()'), self.slotcmdOK)
    self.buttons.addWidget(self.cmdOK)

    self.cmdExit = QPushButton('Exit', self)
    QObject.connect(self.cmdExit, SIGNAL('clicked()'), self.slotExit)
    self.buttons.addWidget(self.cmdExit)

    self.doLoop = False;

    self.show()

  def slotcmdOK(self):
    if self.doLoop:
      self.killTimers();
      self.doLoop = False;
      self.cmdOK.setText('OK');
    else:
      x0 = int(str(self.X0.text()))
      self.DTime = x0;
      self.startTimer(self.DTime);
      self.cmdOK.setText('Stop');
      self.doLoop = True;

  def slotExit(self):
    self.killTimers();
    self.close();

  def timerEvent(self, event):
    self.parent._reexecute();

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
    self.rid1 = 0
    self.rid2 = 0
    self.rid3 = 0
    self.rid4 = 0
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

    self.buttonDef = QPushButton(buttonbox, "buttonDef")
    self.buttonDef.setText('&NewRequest')

    self.buttonLoop = QPushButton(buttonbox, "buttonLoop");
    self.buttonLoop.setText('&Loop');
    self.doLoop = False;

    self.buttonOk = QPushButton(buttonbox,"buttonOk");
    self.buttonOk.setText("&Execute");
    self.buttonOk.setIconSet(pixmaps.reexecute.iconset());
    self.buttonOk.setAccel(Qt.ALT+Qt.Key_E);
    
    buttonRefresh = QPushButton(buttonbox,"buttonRefresh");
    buttonRefresh.setText("&Refresh");
    buttonRefresh.setIconSet(pixmaps.refresh.iconset());
    buttonRefresh.setAccel(Qt.ALT+Qt.Key_R);
    
    QObject.connect(self.buttonDef,SIGNAL("clicked()"),self._newreq);
    QObject.connect(self.buttonLoop,SIGNAL("clicked()"),self._startLoop)
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
    self._name = name;
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
      if not self._request.has_field('request_id'):
        self._request.request_id = hiid(0,0,0,0);
      self.rid1 = int(self._request.request_id[0]);
      self.rid2 = int(self._request.request_id[1]);
      self.rid3 = int(self._request.request_id[2]);
      self.rid4 = int(self._request.request_id[3]);
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
    self.rid1 = self.rid1 + 1
    self._request.request_id = hiid(self.rid1, self.rid2, self.rid3, self.rid4);
    
    if self._node:
      cmd = record(nodeindex=self._node,request=self._request,get_state=True);
    elif self._name:
      cmd = record(name=self._name,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);
    self._refresh();

  def _startLoop(self):
    startLoop(self)

  def _newreq(self):
    if self._request == None:
      self.f0 = 0
      self.f1 = 1
      self.fn = 10
      self.t0 = 0
      self.t1 = 1
      self.tn = 10
    else:
      self.f0 = self._request.cells.domain.freq[0];
      self.f1 = self._request.cells.domain.freq[1];
      if self._request.cells.segments.freq.start_index == self._request.cells.segments.freq.end_index:
        self.fn = 1
      else:
        self.fn = len(self._request.cells.cell_size.freq);
      self.t0 = self._request.cells.domain.time[0];
      self.t1 = self._request.cells.domain.time[1];
      if self._request.cells.segments.time.start_index == self._request.cells.segments.time.end_index:
        self.tn = 1
      else:
        self.tn = len(self._request.cells.cell_size.time);
    editRequest(self);
    self._refresh();

  def doNewRequest(self):
    newd = meq.domain(self.f0, self.f1, self.t0, self.t1);
    newc = meq.cells(domain=newd, num_freq=self.fn, num_time=self.tn);
    self._request = meq.request(cells=newc);
    self.rid1 = self.rid1 + 1
    self.rid2 = self.rid2 + 1
    self.rid3 = self.rid3 + 1
    self.rid4 = self.rid4 + 1
    self._request.request_id = hiid(self.rid1, self.rid2, self.rid3, self.rid4);
    if self._node:
      cmd = record(nodeindex=self._node,request=self._request,get_state=True);
    elif self._name:
      cmd = record(name=self._name,request=self._request,get_state=True);
    mqs().meq('Node.Execute',cmd,wait=False);
    self._refresh();


def define_treebrowser_actions (tb):
  _dprint(1,'defining node-execute treebrowser actions');
  tb.add_action(NA_NodeExecute,30,where="node");

Grid.Services.registerViewer(_request_type,Executor,priority=25);
Grid.Services.registerViewer(meqds.NodeClass(),Executor,priority=25);

