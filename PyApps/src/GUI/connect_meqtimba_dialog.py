#/usr/bin/python
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

from Timba.GUI import meqgui
from Timba.GUI.pixmaps import pixmaps

from PyQt4.Qt import *
from Kittens.widgets import PYSIGNAL


class ConnectMeqKernel(QDialog):
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

        self.bg_connect = QButtonGroup(LayoutWidget,"bg_connect")
#        self.bg_connect.setInsideMargin(10);

        lo_connect = QVBoxLayout(self.bg_connect,11,6,"lo_connect")
        lo_connect_space = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Fixed)
        lo_connect.addItem(lo_connect_space)

        # self.btn_wait = QRadioButton(self.bg_connect,"btn_wait")
        # self.btn_wait.setChecked(1)
        # lo_connect.addWidget(self.btn_wait)

        self.btn_start = QRadioButton(self.bg_connect,"btn_start")
        self.btn_start.setChecked(1)
        lo_connect.addWidget(self.btn_start)

        lo_start_grp = QWidget(self.bg_connect)
        lo_start = QHBoxLayout(lo_start_grp,0,6,"lo_start")
        lo_start_space = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
        lo_start.addItem(lo_start_space)
        
        lo_start_lbl = QLabel("program:",lo_start_grp);
        lo_start.addWidget(lo_start_lbl)
        self.start_pathname = QLineEdit(lo_start_grp,"start_pathname")
        self.start_pathname.setText(self._default_path);
        self.start_pathname.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed);
        self.start_pathname.setMinimumSize(QSize(400,0))
        lo_start.addWidget(self.start_pathname)

        lo_start_grp2 = QWidget(self.bg_connect)
        lo_start2 = QHBoxLayout(lo_start_grp2,0,6,"lo_start2")
        lo_start_space2 = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
        lo_start2.addItem(lo_start_space2)
        lo_start_lbl2 = QLabel("args:",lo_start_grp2);
        lo_start2.addWidget(lo_start_lbl2)
        self.start_args = QLineEdit(lo_start_grp2,"start_args")
        lo_start2.addWidget(self.start_args)
        self.start_browse = QPushButton(lo_start_grp2,"start_browse")
        lo_start2.addWidget(self.start_browse)
        self.start_default = QPushButton(lo_start_grp2,"start_default")
        self.start_default.setEnabled(False);
        lo_start2.addWidget(self.start_default)

        lo_connect.addWidget(lo_start_grp)
        lo_connect.addWidget(lo_start_grp2)
        
        # lo_start_grp.setEnabled(False);
        # lo_start_grp2.setEnabled(False);

        self.btn_remote = QRadioButton(self.bg_connect,"btn_remote")
        self.btn_remote.setEnabled(0)
        lo_connect.addWidget(self.btn_remote)
        
        lo_remote_grp = QWidget(self.bg_connect)
        lo_remote = QHBoxLayout(lo_remote_grp,0,6,"lo_remote")
        lo_remote_space = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
        lo_remote.addItem(lo_remote_space)

        self.remote_host_lbl = QLabel(lo_remote_grp,"remote_host_lbl")
        self.remote_host_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        lo_remote.addWidget(self.remote_host_lbl)

        self.remote_host = QLineEdit(lo_remote_grp,"remote_host")
        lo_remote.addWidget(self.remote_host)

        self.remote_port_lbl = QLabel(lo_remote_grp,"remote_port_lbl")
        self.remote_port_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        lo_remote.addWidget(self.remote_port_lbl)

        self.remote_port = QLineEdit(lo_remote_grp,"remote_port")
        self.remote_port.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed);
        self.remote_port.setMinimumSize(QSize(60,0))
        lo_remote.addWidget(self.remote_port)
        lo_connect.addWidget(lo_remote_grp)
        lo_remote_grp.setEnabled(False);
        
        lo_top.addWidget(self.bg_connect)

        lo_mainbtn = QHBoxLayout(None,0,6,"lo_mainbtn")
        lo_mainbtn_space = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        lo_mainbtn.addItem(lo_mainbtn_space)

        self.btn_ok = QPushButton(LayoutWidget,"btn_ok")
        self.btn_ok.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,1,0,self.btn_ok.sizePolicy().hasHeightForWidth()))
        self.btn_ok.setMinimumSize(QSize(60,0))
        self.btn_ok.setAutoDefault(1)
        self.btn_ok.setDefault(1)
        lo_mainbtn.addWidget(self.btn_ok)

        self.btn_cancel = QPushButton(LayoutWidget,"btn_cancel")
        self.btn_cancel.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,1,0,self.btn_cancel.sizePolicy().hasHeightForWidth()))
        self.btn_cancel.setMinimumSize(QSize(60,0))
        self.btn_cancel.setAutoDefault(1)
        lo_mainbtn.addWidget(self.btn_cancel)
        lo_space = QSpacerItem(20,20,QSizePolicy.Fixed,QSizePolicy.Expanding);
        lo_top.addItem(lo_space)
        lo_top.addLayout(lo_mainbtn)

        self.languageChange()
        
        LayoutWidget.adjustSize();

        #LayoutWidget.resize(QSize(489,330).expandedTo(LayoutWidget.minimumSizeHint()))
        #self.resize(QSize(489,330).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)
        
        self.connect(self.btn_ok,SIGNAL("clicked()"),self.accept)
        self.connect(self.btn_cancel,SIGNAL("clicked()"),self.reject)
        
        ### my additions
        self.connect(self.btn_start,SIGNAL("toggled(bool)"),lo_start_grp,SLOT("setEnabled(bool)"));
        self.connect(self.btn_start,SIGNAL("toggled(bool)"),lo_start_grp2,SLOT("setEnabled(bool)"));
        self.connect(self.btn_remote,SIGNAL("toggled(bool)"),lo_remote_grp,SLOT("setEnabled(bool)"));
        self.connect(self.start_browse,SIGNAL("clicked()"),self.browse_kernel_dialog);
        self.connect(self.start_default,SIGNAL("clicked()"),self.reset_default_path);
        self.connect(self.start_pathname,SIGNAL("textChanged(const QString &)"),self.changed_path);


    def languageChange(self):
        self.setWindowTitle(self.__tr("Connect to meqserver"))
        self.title_icon.setText(QString.null)
        self.title_label.setText(self.__tr( \
          """<p>Not connected to a MeqTrees kernel.</p>
          <p><i>If you will be starting a kernel locally using external tools,
          a connection should be established automatically.</i></p>
          <p><i>Otherwise, select one of the connection methods below.</i></p>""" \
          ));

        self.bg_connect.setTitle(self.__tr("Pick a connection method"))
        # self.btn_wait.setText(self.__tr("wait for local connection"))
        self.btn_start.setText(self.__tr("start a local meqserver:"))
        self.start_browse.setText(self.__tr("Browse..."))
        self.start_default.setText(self.__tr("Reset"))
        self.btn_remote.setText(self.__tr("connect to remote meqserver:"))
        self.remote_host_lbl.setText(self.__tr("Host"))
        self.remote_port_lbl.setText(self.__tr("Port"))
        self.remote_port.setInputMask(self.__tr("#####; "))
        self.btn_ok.setText(self.__tr("&OK"))
        self.btn_ok.setAccel(QString.null)
        self.btn_cancel.setText(self.__tr("&Cancel"))
        self.btn_cancel.setAccel(QString.null)


    def __tr(self,s,c = None):
        return qApp.translate("ConnectMeqKernel",s,c)

    ### override the accept method to start kernel as appropriate
    def accept (self):
      selected = self.bg_connect.selected();
      if selected is self.btn_start:
        # start kernel
        pathname = str(self.start_pathname.text());
        args = str(self.start_args.text());
        self.emit(SIGNAL("startKernel"),pathname,args);
      elif selected is self.btn_remote:
        # not implemented yet
        pass;
      QDialog.accept(self);
      
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
        self._browse_dialog = dialog = QFileDialog(self,"Select meqserver binary");
        dialog.resize(500,dialog.height());
        dialog.setMode(QFileDialog.ExistingFile);
        dialog.setViewMode(QFileDialog.Detail);
      else:
        # trying to have the same effect as rereadDir() in the Qt3 version...
        dialog.setDirectory(dialog.directory());
      if dialog.exec_() == QDialog.Accepted:
        self.start_pathname.setText(str(dialog.selectedFiles()[0]));
        
