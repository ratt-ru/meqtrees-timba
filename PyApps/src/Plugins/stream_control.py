#!/usr/bin/python

import Timba
from Timba.dmi import *
from Timba.Meq import meqds
from Timba.Meq.meqds import mqs
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI.treebrowser import NodeAction
import Timba.GUI.app_proxy_gui 
from Timba import Grid
from numarray import *
from Timba.Meq import meq
from time import sleep
from qt import *
from string import *
from operator import isNumberType
import os

_dbg = verbosity(0,name='StreamCtrl');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

def mkInput():
  inp = record();
  inp.tile_size = 1;
  sel = record();
  sel.channel_start_index=0;
  sel.channel_end_index=-1;
  inp.selection = sel;
  inp.ms_name = '';
  inp.date_column_name = 'DATA';
  return inp;

#
# Class StreamData
# Contains:
#   Data from the input and output record for a spigot to sink tree
# Duties
#   - Contain the data mentioned above
#   - Update the fileds in its parents - method=updateGui
#
class StreamData:
  def __init__(self, parent):
    self.parent = parent;
    self.cwd = ''            # Directory for pre-loaded MS 
    self.NChan = -1;         # Number of channels in the Measurement Set (MS)
    self.Ch0 = 0;            # First channel of the data in the tree, user selected
    self.Ch1 = -1;           # Last channel of the data in the tree, user selected
    self.FullMS = '';        # Name of the MS with full Path
    self.MS = '';            # Name of the MS
    self.DataFrom = '';      # Column to read from
    self.DataTo = '';        # Column to write to
    self.Ant1 = 0;           # One of the antennas of the interferometer for
                             # which datee is selected.
    self.Ant2 = 0;           # Other antenna
    self.TileSize = 1;       # Number of tiles in a data chunk
    self.MaxTSize = -1;      # Maximum tilesize for the current MS

#
# Load the data from the input stream to the object.
#
  def loadData(self, fst):
    self.cwd = fst.cwd;
    InData = fst.stream
    if not hasattr(InData, 'input'):
       InData.input = mkInput();
       return;
    self.Ch0 = InData.input.selection.channel_start_index;
    if self.Ch0 == -1:
      print 'ERROR Ch0 == -1'
      self.Ch0 = 0;
    self.Ch1 = InData.input.selection.channel_end_index;
    if self.Ch1 == -2:
      print 'ERROR Ch1 == -2'
      self.Ch1 = -1;
    self.setMS(InData.input.ms_name);
    self.TileSize = InData.input.tile_size;

    self.DataFrom = str(InData.input.data_column_name);
    self.DataTo = str(InData.output.predict_column);

#
# Set the current MS.
# This function can be called with the full path as parameter.
#
  def setMS(self, FullMS):
    self.FullMS = FullMS;
    MSa = split(self.FullMS, '/');
    if len(MSa) == 1:
      self.MS = FullMS;
      self.FullMS = self.cwd + '/' + FullMS;
    else:
      l = len(MSa)-1;
      self.MS = MSa[l];

#
# Update the GUI in the parent with myself
#
  def updateGui(self):
    self.parent.ChInfo.setText(self.chInfo());
    self.parent.MSInfo.setText(self.MSInfo());
    self.parent.TileInfo.setText(self.TileInfo());
    self.parent.ColInfo.setText(self.ColInfo());

#
# Copy my contents to the ourput stream
#
  def copy(self, OutData):
    OutData.input.selection.channel_start_index = self.Ch0;
    OutData.input.selection.channel_end_index = self.Ch1;
    OutData.input.ms_name = self.FullMS;
#    print 'DEBUG - MS=', OutData.input.ms_name;
    OutData.input.data_column_name = self.DataFrom;
    OutData.output.predict_column = self.DataTo;

#
# Show myself on-screen
#
  def show(self):
    print '*****************************';
    print '      cwd:', self.cwd;
    print 'Channel info:';
    print '      Max:', self.NChan;
    print '    Start:', self.Ch0;
    print '      End:', self.Ch1;
    print 'Data info:';
    print '       MS:', self.MS;
    print '          ', self.FullMS;
    print ' DataFrom:', self.DataFrom;
    print '   DataTo:', self.DataTo;
    print 'Tilesize:';
    print '      Max:', self.MaxTSize;
    print '  Current:', self.TileSize;

#
# Produce a string with column info
#
  def ColInfo(self):
    msg = 'Column info:';
    msg = msg + ' from ' + self.DataFrom;
    msg = msg + ', to ' + self.DataTo;
    msg = msg + '   ';
    return msg;

#
# Produce a string with channel info
#
  def chInfo(self):
    msg = 'Channel Info:';
    if self.NChan > 0:
      msg = msg + ' Max=' + str(self.NChan);
    else:
      msg = msg + ' Max=???';
    msg = msg + ', Start=' + str(self.Ch0);
    msg = msg + ', End=' + str(self.Ch1);
    msg = msg + '   ';
    return msg;

#
# Produce a string with MS info
#
  def MSInfo(self):
    msg = 'MS: ' + self.MS;
    return msg;

#
# Produce a string with interfermeter info
#
  def IntferInfo(self):
    msg = 'Select antennas: [Cannot be selected yet]  '
    return msg;

#
# Produce a string with tile info
#
  def TileInfo(self):
    msg = 'Tile info:';
    msg = msg + ' Size=' + str(self.TileSize);
    if self.MaxTSize > 0: 
      msg = msg + ' Max size=' + str(self.MaxTSize);
    else:
      msg = msg + ' Max size= ???';
    msg = msg + '   ';
    return msg;

#
# GUI to allow user to select columns
#
class ColumnSelect(QDialog):
  def __init__(self, parent):
    self.parent = parent
    QDialog.__init__(self, parent._wtop, 'Set Columns', 1, 0)
    self.parent = parent;
    self.StrData = parent.StrData;
    self.DataFrom = self.StrData.DataFrom;
    self.DataTo = self.StrData.DataTo;

    self.GUI = QVBoxLayout(self);

    btnIN = QVButtonGroup('Select input column', self);
    self.InData = QRadioButton('DATA', btnIN);
    if self.StrData.DataFrom == 'DATA':
       self.InData.setChecked(1);
    self.InPred = QRadioButton('PREDICT', btnIN);
    if self.StrData.DataFrom == 'PREDICT':
       self.InPred.setChecked(1);
    self.InRes = QRadioButton('RESIDUALS', btnIN);
    if self.StrData.DataFrom == 'RESIDUALS':
       self.InRes.setChecked(1);
    self.GUI.addWidget(btnIN);

    btnOUT = QVButtonGroup('Select output column', self);
    self.OutData = QRadioButton('DATA', btnOUT);
    if self.StrData.DataTo == 'DATA':
       self.OutData.setChecked(1);
    self.OutPred = QRadioButton('PREDICT', btnOUT);
    if self.StrData.DataTo == 'PREDICT':
       self.OutPred.setChecked(1);
    self.OutRes = QRadioButton('RESIDUALS', btnOUT);
    if self.StrData.DataTo == 'RESIDUALS':
       self.OutRes.setChecked(1);
    self.GUI.addWidget(btnOUT);

    self.Btns = QVBox(self);
    run = QPushButton('OK', self.Btns);
    QObject.connect(run,SIGNAL("clicked()"),self.runOK);
    cnc = QPushButton('Cancel', self.Btns);
    QObject.connect(cnc,SIGNAL("clicked()"),self.runCancel);
    self.GUI.addWidget(self.Btns);

  def runOK(self):
    if self.InData.isOn():
      self.StrData.DataFrom = 'DATA';
    elif self.InPred.isOn():
      self.StrData.DataFrom = 'PREDICT';
    elif self.InRes.isOn():
      self.StrData.DataFrom = 'RESIDUALS';
    else:
      print 'ERROR ...';

    if self.OutData.isOn():
      self.StrData.DataTo = 'DATA';
    elif self.OutPred.isOn():
      self.StrData.DataTo = 'PREDICT';
    elif self.OutRes.isOn():
      self.StrData.DataTo = 'RESIDUALS';
    else:
      print 'ERROR ...';

    self.StrData.updateGui()
    self.close()

  def runCancel(self):
    self.close();


#
# GUI to allow the user to select channels
#
class ChannelSelect(QDialog):
  def __init__(self, parent):
    self.parent = parent
    QDialog.__init__(self, parent._wtop, 'TEST', 1, 0)
    self.parent = parent;
    self.StrData = parent.StrData;

    self.GUI = QVBoxLayout(self);
    self.UserIn = QVBox(self);
    self.GUI.addWidget(self.UserIn);

    self.ChannelBox = QHBox(self.UserIn);
    self.ChLbl = QVBox(self.ChannelBox);
    lbl = QLabel('Nr of Channels ', self.ChLbl);
    lbl = QLabel('Select inner ', self.ChLbl);
    lbl = QLabel('Exclude outer ', self.ChLbl);
    lbl = QLabel('Exclude outer ', self.ChLbl);
    lbl = QLabel('Full range ', self.ChLbl);
    lbl = QLabel('Start Channel ', self.ChLbl);
    lbl = QLabel('End Channel ', self.ChLbl);

    self.ChVal = QVBox(self.ChannelBox);
    self.NChan = QLineEdit(self.ChVal);
    self.NChan.setText(str(self.StrData.NChan));
    self.ChInnPerc = QLineEdit(self.ChVal);
    self.ChOutPerc = QLineEdit(self.ChVal);
    self.ChOutChan = QLineEdit(self.ChVal);
    btn = QPushButton('Select', self.ChVal);
    QObject.connect(btn,SIGNAL("clicked()"),self.setFull);
    self.StartChannel = QLineEdit(self.ChVal);
    self.StartChannel.setText(str(self.StrData.Ch0));
    self.EndChannel = QLineEdit(self.ChVal);
    self.EndChannel.setText(str(self.StrData.Ch1));

    self.ChBtn = QVBox(self.ChannelBox);
    QLabel(' ', self.ChBtn);
    innprc = QPushButton('percent', self.ChBtn);
    outprc = QPushButton('percent', self.ChBtn);
    outchn = QPushButton('channels', self.ChBtn);
    QObject.connect(innprc,SIGNAL("clicked()"),self.setInnerPercent);
    QObject.connect(outprc,SIGNAL("clicked()"),self.setOuterPercent);
    QObject.connect(outchn,SIGNAL("clicked()"),self.setOuterChan);
    QLabel(' ', self.ChBtn);
    QLabel(' ', self.ChBtn);
    QLabel(' ', self.ChBtn);
    QLabel(' ', self.ChBtn);

    self.Buttons = QHBox(self);
    self.GUI.addWidget(self.Buttons);
    run = QPushButton('OK', self.Buttons);
    QObject.connect(run,SIGNAL("clicked()"),self.runOK);
    cnc = QPushButton('Cancel', self.Buttons);
    QObject.connect(cnc,SIGNAL("clicked()"),self.runCancel);

  def setFull(self):
    self.StartChannel.setText('0');
    self.EndChannel.setText('-1');    

  def setInnerPercent(self):
    self.StrData.NChan = int(str(self.NChan.text()));
    pc = str(self.ChInnPerc.text());
    if pc == '':
      return;
    pcval = float(pc);
    dp = (100.0-pcval)/2.0/100.0;
    self.StartChannel.setText(str(int(self.StrData.NChan*dp)));
    self.EndChannel.setText(str(int(self.StrData.NChan*(1-dp))));

  def setOuterPercent(self):
    self.StrData.NChan = int(str(self.NChan.text()));
    pc = str(self.ChOutPerc.text());
    if pc == '':
      return;
    pcval = float(pc);
    dp = pcval/2.0/100.0;
    self.StartChannel.setText(str(int(self.StrData.NChan*dp)));
    self.EndChannel.setText(str(int(self.StrData.NChan*(1-dp))));

  def setOuterChan(self):
    self.StrData.NChan = int(str(self.NChan.text()));
    pc = str(self.ChOutChan.text());
    if pc == '':
      return;
    pcval = float(pc);
    dp = pcval/2.0;
    self.StartChannel.setText(str(int(dp)));
    self.EndChannel.setText(str(int(self.StrData.NChan-dp)));

#
# Copy the selected start/end channel to the data object.
# Let the data object update the gui
#
  def runOK(self):
    self.StrData.NChan = int(str(self.NChan.text()));
    self.StrData.Ch0 = int(str(self.StartChannel.text()));
    self.StrData.Ch1 = int(str(self.EndChannel.text()));
    self.StrData.updateGui();
    self.close()

  def runCancel(self):
    self.close();

#
# Get info on an MS by means of a glish call
#
class MSinfoWnd(QDialog):
  def __init__(self, parent):
    self.parent = parent
    QDialog.__init__(self, parent._wtop, 'TEST', 0, 0)
    self.setFont(QFont("courier", 8))
    self.VList = QVBoxLayout(self);
    self.lblMS = QLabel(self);
    self.VList.addWidget(self.lblMS)
    self.lblbox = []
    self.maxcnt = 50;
    for i in range(self.maxcnt):
      self.lblbox.append(QLabel(self));
      self.VList.addWidget(self.lblbox[i]);

#
# Fire the glish script and catch the output from a pipe.
# Select some values to update the GUI
#  - the number of channels
#  - the maximum tile size
#
  def setMS(self, MS):
    self.lblMS.setText('TEST - Info on: '+ MS);
    syscmd = 'glish -l MSinfo.g ' + MS + ' > /tmp/out.txt';
#    print 'DEBUG - ', syscmd;
    try: os.system(syscmd);
    except: pass;
    p = open('/tmp/out.txt');
#    print 'DEBUG - ', p;
    rtnval = 'Not Found';
    cnt = 0;
    inData = False;
    for l in p.readlines():
      lsp = split(l, '=');
      if strip(lsp[0]) == 'SeqNr':
        inData = True;
      if inData and (cnt < self.maxcnt):
        self.lblbox[cnt].setText(l);
        cnt = cnt + 1;
      if strip(lsp[0]) == 'IFNChan':
        nchan = strip(lsp[1]);
      if strip(lsp[0]) == 'NRows':
        nrows = int(strip(lsp[1]));
      if strip(lsp[0]) == 'IFBands':
        ifbands = int(strip(lsp[1]));
    self.parent.StrData.NChan = nchan;
    mts = nrows / ifbands / 105;
    self.parent.StrData.MaxTSize = mts;
    self.parent.StrData.updateGui();

#
# MAIN class
#
class StreamController (browsers.GriddedPlugin):
  viewer_name = "DataStream Controller";
  _icon = pixmaps.spigot;

## no need for this method, since we're not really a viewer as such
#  def is_viewable (data):
#    return isinstance(data,_request_type) or \
#      isinstance(getattr(data,'request',None),_request_type);
#  is_viewable = staticmethod(is_viewable);

  def __init__(self,gw,dataitem,cellspec={},**opts):
    _dprint(3,"init");
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    _dprint(3,"started with",dataitem.udi);
    self._wtop = QVBox(self.wparent());

#
# All data items are kept in an object
#
    self.StrData = StreamData(self);

# add GUI controls
# self._currier is a helper object to create callbacks, see use below
# parent class will probably have allocated one for us already, hence the check
    if not hasattr(self,'_currier'):
      self._currier = PersistentCurrier();

    self.GUI = self._wtop;
    self.UserIn = QVBox(self.GUI);

#
# Channel box
#
    self.ChannelBox = QHBox(self.UserIn);
    msg = self.StrData.chInfo()
    self.ChInfo = QLabel(msg, self.ChannelBox);
    self.ChBtn = QVBox(self.ChannelBox);
    ChSelect = QPushButton('Change', self.ChBtn);
    QObject.connect(ChSelect,SIGNAL("clicked()"),self._ChannelSelect);

#
# MS box
#
    self.MSBox = QHBox(self.UserIn);
    msg = self.StrData.MSInfo();
    self.MSInfo = QLabel(msg, self.MSBox);
    MSsel = QPushButton('Select', self.MSBox);
    QObject.connect(MSsel,SIGNAL("clicked()"),self._MSSelect);
    MSinf = QPushButton('Info', self.MSBox);
    QObject.connect(MSinf,SIGNAL("clicked()"),self._getMSInfo);

#
# Interferometer box
#
    self.IntferBox = QHBox(self.UserIn);
    msg = self.StrData.IntferInfo();
    self.IntferInfo = QLabel(msg, self.IntferBox);
    IntferSel = QPushButton('Select', self.IntferBox);
    QObject.connect(MSinf,SIGNAL("clicked()"),self._IntferSelect);
    
#
# Tilesize box
#
    self.TileBox = QHBox(self.UserIn);
    msg = self.StrData.TileInfo();
    self.TileInfo = QLabel(msg, self.TileBox);
    self.NTiles = QLineEdit(self.TileBox);
    self.NTiles.setText(str(self.StrData.TileSize));
    TileSize = QPushButton('Set', self.TileBox);
    QObject.connect(TileSize,SIGNAL("clicked()"),self._TileSet);

#
# Data column box
#
    self.ColBox = QHBox(self.UserIn);
    msg = self.StrData.ColInfo();
    self.ColInfo = QLabel(msg, self.ColBox);
    ColSel = QPushButton('Select', self.ColBox);
    QObject.connect(ColSel, SIGNAL("clicked()"), self._ColSet);

#
# Put empty label to create a right-margin
#
    lbl = QLabel('  ', self.ChannelBox);
    lbl = QLabel('  ', self.MSBox);
    lbl = QLabel('  ', self.IntferBox);
    lbl = QLabel('  ', self.TileBox);
    lbl = QLabel('  ', self.ColBox);

    self.Buttons = QHBox(self.GUI);
    run = QPushButton('GO', self.Buttons);
    QObject.connect(run,SIGNAL("clicked()"),self.run_stuff);

#    test = QPushButton('TEST', self.Buttons);
#    QObject.connect(test, SIGNAL("clicked()"), self.test_stuff);

#
# note use of currier to create a callback, the same function will
# be called in both cases, but with different arguments
#
#    QObject.connect(b4,SIGNAL("clicked()"),self._currier.curry(self.set_endindex, 2));

#    
# tell parent class what our contents are
# enable_viewers=False disables some GUI functions which we don't need
# (i.e. item drops, "View using" menu, etc.)
#
    self.set_widgets(self.wtop(),'<b>Data Stream</b>',
                     icon=pixmaps.spigot.iconset(),
                     enable_viewers=False);

#
# enable GUI of parent class, then disable our buttons until data is loaded
#
    self.enable();
    self.wtop().setEnabled(False);
    
    # # this may be needed later if you add widgets that need special handling of font change
    # # commands (i.e. the HierBrowser). Basic widgets are fine without it.
    # QObject.connect(self.wtop(),PYSIGNAL("fontChanged()"),
    #                      self._childwidget.wtop(),PYSIGNAL("fontChanged()"));
    
    # internal copy of control record: this will be assigned to by update_forest_state()
    self._streamrec = None;
    # try to load data from forest state
    self.update_forest_state(meqds.get_forest_state());
    # it may happen that we haven't received a forest state yet, in which
    # case no data will have been loaded because get_forest_state() returned
    # an empty record. If this happens, we subscribe to the state and request 
    # an update.

    if not self._streamrec:
      meqds.subscribe_forest_state(self.update_forest_state);
      meqds.request_forest_state();
    
  def wtop(self):
    return self._wtop;

#
# Update the stream info - this will be called from outside
#
  def update_forest_state (self,fst):
    # once we've received data, we ignore all further updates
    if self._streamrec: 
      return;

    # try to extract record from the forest state
    try: self._streamrec = fst.stream;
    except AttributeError: pass;

    # if we haven't found anything, return and wait for another update
    if not self._streamrec:
      return;

    # ok, we've got data. Fill in and enable GUI accordingly
    self.wtop().setEnabled(True);
    print '***************************** Got stream record:';
    print self._streamrec;
    print '*****************************';

#
# Load values in Data object, update gui
#
    self.StrData.loadData(fst);
#    self.StrData.show();
    self.StrData.updateGui();

#
# update values in GUI
#
#    self.NTiles.setText(str(self._streamrec.input.tile_size));

#
# Select an MS, update GUI
#  
  def _MSSelect(self):
    fdialog = QFileDialog(self.wtop(),"MS dialog",True);
    fdialog.setMode(QFileDialog.DirectoryOnly);
    if fdialog.exec_loop() == QDialog.Accepted:
      self.StrData.setMS(str(fdialog.selectedFile()));
      self.StrData.NChan = -1;
      self.StrData.MaxTSize = -1;
      self.StrData.updateGui();

#
# Select channels, GUI is updated from the class
#
  def _ChannelSelect(self):
    cs = ChannelSelect(self);
    cs.show();

#
# Set interferometer
#
  def _IntferSelect(self):
    pass;

#
# Set tilesize
#
  def _TileSet(self):
    x = int(str(self.NTiles.text()));
    self.StrData.TileSize = x;
    self.StrData.updateGui();

  def _ColSet(self):
    cs = ColumnSelect(self);
    cs.show();

#  def test_stuff(self):
#    cs = ChannelSelect(self);
#    cs.show();

#
# Get info on MS, reset selected channels, GUI is updated from .setMS
#
  def _getMSInfo(self):
    MS = self.StrData.FullMS;
    self.StrData.Ch0 = 0;
    self.StrData.Ch1 = -1;
    MSinfo = MSinfoWnd(self);
    MSinfo.show()
    MSinfo.setMS(MS);

#
# Get the info from the StrData object and run the tree
#
  def run_stuff (self):
    if self._streamrec:
      self.StrData.copy(self._streamrec);

      self._streamrec.input.tile_size = int(str(self.NTiles.text()));
#      s1 = str(self.Station1.text());
#      s2 = str(self.Station2.text());
#      if (s1 != '') and (s2 != ''):
#        selStr = 'ANTENNA1 in ' + s1 + ' && ANTENNA2 in ' + s2;
#        self._streamrec.input.selection.selection_string = selStr;
#      else:
      self._streamrec.input.selection.selection_string = '';

#      DataFrom = str(self.DataFrom.text());
#      if DataFrom != self.currDataFrom:
#	self._streamrec.input.data_column_name = DataFrom;
#      DataTo = str(self.DataTo.text());
#      if DataTo != self.currDataTo:
#	self._streamrec.output_col = DataFrom;

      mqs().init(self._streamrec);
#
# Force an update of the stream data
#
    self._streamrec = None;
    self.update_forest_state(meqds.get_forest_state());

def _start_stream_control ():
  _dprint(2,'adding a stream control viewer');
  # Create a 'data item', which represents our box in the grid.
  # The first argument is a UDI, we only need to ensure it is unique
  # so that it doesn't get confused with other data items in the system
  item = Grid.DataItem('/StreamControl',                    # UDI
                        name='Data Stream Control',         # name
                        caption='<b>Data Stream</b>',       # caption for GUI -- note use of Rich Text markup
                        desc='Datastream control plug-in',
                        data=None,refresh=None,             # no data and no refresh function
                        viewer=StreamController);           # viewer class
  # this registers us with the grid and creates a viewer
  Grid.addDataItem(item);
  
# this is called automatically by the browser to populate the tree browser
# context menus and toolbar
def define_treebrowser_actions (tb):
  _dprint(1,'defining stream control treebrowser actions');
  parent = tb.wtop();
  # create QAction for the Stream control plugin
  global _qa_stream;
  _qa_stream = QAction("Stream Control",pixmaps.spigot.iconset(),"Stream Control",0,parent);
  _qa_stream.setMenuText("I/O stream control");
  # make sure it's enabled/disabled as appropriate
  _qa_stream._is_enabled = lambda tb=tb: tb.is_connected;
  # "45" is priority of action, determining its place in the toolbar
  tb.add_action(_qa_stream,45,callback=_start_stream_control);

# this is called automatically by the main app to populate its menus.
# Called *after* define_treebrowser_actions, so it's ok to use stuff initialized
# there.
def define_mainmenu_actions (menu):
  _dprint(1,'defining stream control menu actions');
  global _qa_stream;
  # add ourselves to the MeqTimba menu
  _qa_stream.addTo(menu['MeqTimba']);

