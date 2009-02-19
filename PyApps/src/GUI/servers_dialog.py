#/usr/bin/python
#
#% $Id: connect_meqtimba_dialog.py 5418 2007-07-19 16:49:13Z oms $ 
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

from Timba.GUI import meqgui
from Timba.GUI.pixmaps import pixmaps
from qt import *
import os
import os.path

class ServersDialog (QDialog):
  def __init__(self,parent=None,name=None,modal=0,fl=None):
    if fl is None:
      fl = Qt.WType_TopLevel|Qt.WStyle_Customize;
      fl |= Qt.WStyle_DialogBorder|Qt.WStyle_Title;
    
    QDialog.__init__(self,parent,name,modal,fl)
    
    self._default_path = "meqserver";
    
    self.image0 = pixmaps.trees48x48.pm();
    if not name:
        self.setName("ConnectDialog")

    # self.setSizeGripEnabled(0)
    lo_dialog = QVBoxLayout(self);

    LayoutWidget = QWidget(self,"lo_top")
    lo_dialog.addWidget(LayoutWidget);
    LayoutWidget.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding);
    # LayoutWidget.setGeometry(QRect(10,10,472,400))
    lo_top = QVBoxLayout(LayoutWidget,11,6,"lo_top")

    lo_title = QHBoxLayout(None,0,6,"lo_title")

    self.title_icon = QLabel(LayoutWidget,"title_icon")
    self.title_icon.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,self.title_icon.sizePolicy().hasHeightForWidth()))
    self.title_icon.setPixmap(self.image0)
    self.title_icon.setAlignment(QLabel.AlignCenter)
    lo_title.addWidget(self.title_icon)

    self.title_label = QLabel(LayoutWidget,"title_label")
    lo_title.addWidget(self.title_label)
    lo_top.addLayout(lo_title)
            
    self.gb_servers = QGroupBox(1,Qt.Vertical,LayoutWidget,"gb_servers");
    self.server_list = QListView(self.gb_servers);
    # self.server_list.header().hide();
    self.server_list.addColumn("server");
    self.server_list.addColumn("stat");
    self.server_list.addColumn("dir");
    self.server_list.addColumn("script");
    self.server_list.setAllColumnsShowFocus(True);
    QObject.connect(self.server_list,SIGNAL("doubleClicked(QListViewItem*,const QPoint &,int)"),self._server_selected);
    QObject.connect(self.server_list,SIGNAL("returnPressed(QListViewItem*)"),
            self._server_selected);
    lo_top.addWidget(self.gb_servers)

    self.gb_local = QGroupBox(1,Qt.Horizontal,LayoutWidget,"gb_local")

    lo_start_grp = QWidget(self.gb_local)
    lo_start = QHBoxLayout(lo_start_grp,0,6,"lo_start")
    #lo_start_space = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
    #lo_start.addItem(lo_start_space)
    
    lo_start_lbl = QLabel("program:",lo_start_grp);
    lo_start.addWidget(lo_start_lbl)
    self.start_pathname = QLineEdit(lo_start_grp,"start_pathname")
    self.start_pathname.setText(self._default_path);
    self.start_pathname.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
    self.start_pathname.setMinimumSize(QSize(400,0))
    lo_start.addWidget(self.start_pathname)

    lo_start_grp2 = QWidget(self.gb_local)
    lo_start2 = QHBoxLayout(lo_start_grp2,0,6,"lo_start2")
    #lo_start_space2 = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
    #lo_start2.addItem(lo_start_space2)
    lo_start_lbl2 = QLabel("args:",lo_start_grp2);
    lo_start2.addWidget(lo_start_lbl2)
    self.start_args = QLineEdit(lo_start_grp2,"start_args")
    lo_start2.addWidget(self.start_args);
    
    lo_start_grp3 = QWidget(self.gb_local);
    lo_start3 = QHBoxLayout(lo_start_grp3,0,6,"lo_start3")
    self.start_local = QPushButton(lo_start_grp3,"start_local");
    lo_start3.addWidget(self.start_local,0);
    self.start_local.setAutoDefault(1);
    self.start_local.setDefault(1);
    lo_start3.addStretch(1);
    self.start_browse = QPushButton(lo_start_grp3,"start_browse")
    lo_start3.addWidget(self.start_browse,0)
    self.start_default = QPushButton(lo_start_grp3,"start_default")
    self.start_default.setEnabled(False);
    lo_start3.addWidget(self.start_default,0)
    QObject.connect(self.start_local,SIGNAL("clicked()"),
                    self._start_local_server_selected);

    #lo_remote_grp = QWidget(self.gb_local)
    #lo_remote = QHBoxLayout(lo_remote_grp,0,6,"lo_remote")
    #lo_remote_space = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
    #lo_remote.addItem(lo_remote_space)

    #self.remote_host_lbl = QLabel(lo_remote_grp,"remote_host_lbl")
    #self.remote_host_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
    #lo_remote.addWidget(self.remote_host_lbl)

    #self.remote_host = QLineEdit(lo_remote_grp,"remote_host")
    #lo_remote.addWidget(self.remote_host)

    #self.remote_port_lbl = QLabel(lo_remote_grp,"remote_port_lbl")
    #self.remote_port_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
    #lo_remote.addWidget(self.remote_port_lbl)

    #self.remote_port = QLineEdit(lo_remote_grp,"remote_port")
    #self.remote_port.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed);
    #self.remote_port.setMinimumSize(QSize(60,0))
    #lo_remote.addWidget(self.remote_port)
    #lo_connect.addWidget(lo_remote_grp)
    #lo_remote_grp.setEnabled(False);
    
    lo_top.addWidget(self.gb_local)

    lo_mainbtn = QHBoxLayout(None,0,6,"lo_mainbtn")
    #lo_mainbtn_space = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
    #lo_mainbtn.addItem(lo_mainbtn_space)

    #self.btn_ok = QPushButton(LayoutWidget,"btn_ok")
    #self.btn_ok.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,1,0,self.btn_ok.sizePolicy().hasHeightForWidth()))
    #self.btn_ok.setMinimumSize(QSize(60,0))
    #self.btn_ok.setAutoDefault(1)
    #self.btn_ok.setDefault(1)
    #lo_mainbtn.addWidget(self.btn_ok)

    lo_mainbtn.addStretch(1);
    self.btn_cancel = QPushButton(LayoutWidget,"btn_cancel")
    self.btn_cancel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,1,0,self.btn_cancel.sizePolicy().hasHeightForWidth()))
    self.btn_cancel.setMinimumSize(QSize(60,0))
    self.btn_cancel.setAutoDefault(1)
    self.btn_cancel.setIconSet(pixmaps.red_round_cross.iconset());
    lo_mainbtn.addWidget(self.btn_cancel,0)
    
    #lo_space = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Expanding);
    #lo_top.addItem(lo_space)
    lo_top.addLayout(lo_mainbtn);

    self.languageChange()
    
    LayoutWidget.adjustSize();

    #LayoutWidget.resize(QSize(489,330).expandedTo(LayoutWidget.minimumSizeHint()))
    #self.resize(QSize(489,330).expandedTo(self.minimumSizeHint()))
    self.clearWState(Qt.WState_Polished)
    
    self.connect(self.btn_cancel,SIGNAL("clicked()"),self.reject)
    
    ### my additions
    #self.connect(self.btn_remote,SIGNAL("toggled(bool)"),lo_remote_grp,SLOT("setEnabled(bool)"));
    self.connect(self.start_browse,SIGNAL("clicked()"),self.browse_kernel_dialog);
    self.connect(self.start_default,SIGNAL("clicked()"),self.reset_default_path);
    self.connect(self.start_pathname,SIGNAL("textChanged(const QString &)"),self.changed_path);


  def languageChange(self):
    self.setCaption(self.__tr("Attach to a meqserver"))
    self.title_icon.setText(QString.null)
    self.title_label.setText(self.__tr( \
      """<p><i>Pick a running meqserver to attach to, or else start a new one
      using one of the methods below.</i></p>
      <p><i>You can also start a meqserver process externally, e.g. from a terminal or from a debugger,
      and it should show up in the list.</i></p>""" \
      ));
    self.gb_servers.setTitle(self.__tr("Running meqservers (double-click to attach)"))
    self.gb_local.setTitle(self.__tr("Start && attach a new local meqserver"))
    # self.btn_wait.setText(self.__tr("wait for local connection"))
    self.start_browse.setText(self.__tr("Browse..."))
    self.start_default.setText(self.__tr("Reset"))
    self.start_local.setText(self.__tr("Start"))
    #self.btn_remote.setText(self.__tr("connect to remote kernel:"))
    #self.remote_host_lbl.setText(self.__tr("Host"))
    #self.remote_port_lbl.setText(self.__tr("Port"))
    #self.remote_port.setInputMask(self.__tr("#####; "))
    self.btn_cancel.setText(self.__tr("Cancel"))


  def __tr(self,s,c = None):
    return qApp.translate("ConnectMeqKernel",s,c)

  def set_default_args (self,args):
    self.start_args.setText(args);
  
  def set_default_path (self,path):
    self._default_path = path;
    self.start_pathname.setText(path);
    self.start_default.setEnabled(False);

  def reset_default_path (self):
    self.start_pathname.setText(self._default_path);
    self.start_default.setEnabled(False);
    
  def changed_path (self,path):
    self.start_default.setEnabled(bool(str(path) != self._default_path));

  def browse_kernel_dialog (self):
    try: dialog = self._browse_dialog;
    except AttributeError:
      self._browse_dialog = dialog = QFileDialog(self,"kernel dialog",True);
      dialog.resize(500,dialog.height());
      dialog.setMode(QFileDialog.ExistingFile);
      # dialog.setFilters("Forests (*.forest *.meqforest);;All files (*.*)");
      dialog.setViewMode(QFileDialog.Detail);
      dialog.setCaption("Select meqserver executable");
    else:
      dialog.rereadDir();
    if dialog.exec_loop() == QDialog.Accepted:
      self.start_pathname.setText(str(dialog.selectedFile()));
  
  def _server_selected (self,item,*dum):
    self.emit(PYSIGNAL("serverSelected()"),(item._addr,));
    
  def _start_local_server_selected (self):
    pathname = str(self.start_pathname.text());
    args = str(self.start_args.text());
    self.emit(PYSIGNAL("startKernel()"),(pathname,args));
  
  def attach_to_server (self,addr):
    item = self.server_list.firstChild();
    while item:
      if item._addr == addr:
        item.setPixmap(0,pixmaps.blue_round_rightarrow.pm());
      else:
        item.setPixmap(0,QPixmap());
      item = item.nextSibling();
    
  def update_server_state (self,server,staterec=None):
    # find matching item
    item = self.server_list.firstChild();
    while item and item._addr != server.addr:
      item = item.nextSibling();
    # disconnected server: remove from list
    if server.state is None:
      if item is not None:
        self.server_list.takeItem(item);
    else:
      # connected server: add to list and/or change state
      if item is None:
        item = QListViewItem(self.server_list);
        setattr(item,'_addr',server.addr);
      # change fields
      name = server.session_name or str(server.addr);
      if server.remote and server.host:
        name += ' @'+server.host;
      item.setText(0,name);
      item.setText(1,server.statestr.lower() or '');
      cwd = server.cwd;
      if cwd:
        home = os.path.expanduser('~');
        prefix = os.path.commonprefix((home,cwd));
        if prefix:
          cwd = os.path.join('~',cwd[len(prefix)+1:],'');
      item.setText(2,cwd or '');
      script = staterec and staterec.get('script_name');
      script = script and os.path.basename(script);
      item.setText(3,script or '');
