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
from os import popen

_dbg = verbosity(0,name='StreamCtrl');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

class MSinfoWnd(QDialog):
  def __init__(self, parent):
    self.parent = parent
    QDialog.__init__(self, parent._wtop, 'TEST', 0, 0)
    self.setFont(QFont("courier", 8))
    self.VList = QVBoxLayout(self);
    self.lblMS = QLabel(self);
    self.VList.addWidget(self.lblMS)
    self.lblbox = []
    self.maxcnt = 55;
    for i in range(self.maxcnt):
      self.lblbox.append(QLabel(self));
      self.VList.addWidget(self.lblbox[i]);

  def setMS(self, MS):
    self.lblMS.setText('Info on: '+ MS);
    p = popen('glish -l MSinfo.g '+MS);
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
        rtnval = strip(lsp[1]);
    return rtnval

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
    
    
    # add GUI controls
    # self._currier is a helper object to create callbacks, see use below
    # parent class will probably have allocated one for us already, hence the check
    if not hasattr(self,'_currier'):
      self._currier = PersistentCurrier();

#
# GUI set-up
#
# GUI = QVBox
#  UserIn = QVBox
#    ChannelBox = QHbox
#      ChLbl = QVbox | ChVal = QVbox | ChHlp = QVbox
#    MSBox = QHbox
#      MSLbl = QVbox | MSVal = QVbox | MSHlp = QVbox
#    IntfBox = QHbox
#      IntfLbl = QVbox | IntfVal = QVbox | IntfHlp = QVbox
#  Buttons = QHBox
#
    self.GUI = self._wtop;
    self.UserIn = QVBox(self.GUI);

    self.ChannelBox = QHBox(self.UserIn);
    self.ChLbl = QVBox(self.ChannelBox);
    lbl = QLabel('Nr of Channels ', self.ChLbl);
    lbl = QLabel('Select inner ', self.ChLbl);
    lbl = QLabel('Exclude outer ', self.ChLbl);
    lbl = QLabel('Exclude outer ', self.ChLbl);
    lbl = QLabel('Start Channel ', self.ChLbl);
    lbl = QLabel('End Channel ', self.ChLbl);

    self.ChVal = QVBox(self.ChannelBox);
    self.NChanB = QLineEdit(self.ChVal);
    self.NChan = 64;
    self.NChanB.setText(str(self.NChan));
    self.ChInnPerc = QLineEdit(self.ChVal);
    self.ChOutPerc = QLineEdit(self.ChVal);
    self.ChOutChan = QLineEdit(self.ChVal);
    self.StartChannel = QLineEdit(self.ChVal);
    self.EndChannel = QLineEdit(self.ChVal);

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

    self.MSBox = QHBox(self.UserIn);
    self.MSLbl = QVBox(self.MSBox);
    lbl = QLabel('MS ', self.MSLbl);
    self.MSVal = QVBox(self.MSBox);
    self.MS = QLineEdit(self.MSVal);
    self.MSBtn = QVBox(self.MSBox);
    MSinf = QPushButton('Info', self.MSBtn);
    QObject.connect(MSinf,SIGNAL("clicked()"),self._getMSinfo);

    self.IntfBox = QHBox(self.UserIn);
    self.IntfLbl = QVBox(self.IntfBox);
    lbl = QLabel('Telesc. 1 ', self.IntfLbl);
    lbl = QLabel('Telesc. 2 ', self.IntfLbl);
    self.IntfVal = QVBox(self.IntfBox);
    self.Station1 = QLineEdit(self.IntfVal);
    self.Station2 = QLineEdit(self.IntfVal);
    
    self.TimeBox = QHBox(self.UserIn);
    self.TimeLbl = QVBox(self.TimeBox);
    lbl = QLabel('TileSize ', self.TimeLbl);
    self.TimeVal = QVBox(self.TimeBox);
    self.NTiles = QLineEdit(self.TimeVal);

#
# Put empty label to create a right-margin
#
    lbl = QLabel('  ', self.ChannelBox);
    lbl = QLabel('  ', self.MSBox);
    lbl = QLabel('  ', self.IntfBox);
    lbl = QLabel('  ', self.TimeBox);

    self.Buttons = QHBox(self.GUI);
    run = QPushButton('GO', self.Buttons);
    QObject.connect(run,SIGNAL("clicked()"),self.run_stuff);
    # note use of currier to create a callback, the same function will
    # be called in both cases, but with different arguments
#    QObject.connect(b4,SIGNAL("clicked()"),self._currier.curry(self.set_endindex, 2));
    
    # tell parent class what our contents are
    # enable_viewers=False disables some GUI functions which we don't need
    # (i.e. item drops, "View using" menu, etc.)
    self.set_widgets(self.wtop(),'<b>Data Stream</b>',
                     icon=pixmaps.spigot.iconset(),
                     enable_viewers=False);
    # enable GUI of parent class, then disable our buttons until data is loaded
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

  def update_forest_state (self,fst):
    _dprint(3,'streamrec is',self._streamrec);
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
    self.NTiles.setText(str(self._streamrec.input.tile_size));
    if self._streamrec.input.selection.channel_start_index == -1:
      self.StartChannel.setText('0');
    else:
      self.StartChannel.setText(str(self._streamrec.input.selection.channel_start_index));
    if self._streamrec.input.selection.channel_end_index == -2:
      self.EndChannel.setText('-1');
    else:
      self.EndChannel.setText(str(self._streamrec.input.selection.channel_end_index));
    self.currMS = str(self._streamrec.input.ms_name);
    self.MS.setText(self.currMS);

# GUI callbacks
#  def set_tilesize (self,size):
#    _dprint(3,'streamrec is',self._streamrec);
#    # exception handler ensures that we don't break when a record is missing 
#    # for some reason
#    try: self._streamrec.input.tile_size = size;
#    except AttributeError: pass;
  
  def setInnerPercent(self):
    self.NChan = int(str(self.NChanB.text()));
    pc = str(self.ChInnPerc.text());
    if pc == '':
      return;
    pcval = float(pc);
    dp = (100.0-pcval)/2.0/100.0;
    self.StartChannel.setText(str(int(self.NChan*dp)));
    self.EndChannel.setText(str(int(self.NChan*(1-dp))));

  def setOuterPercent(self):
    self.NChan = int(str(self.NChanB.text()));
    pc = str(self.ChOutPerc.text());
    if pc == '':
      return;
    pcval = float(pc);
    dp = pcval/2.0/100.0;
    self.StartChannel.setText(str(int(self.NChan*dp)));
    self.EndChannel.setText(str(int(self.NChan*(1-dp))));

  def setOuterChan(self):
    self.NChan = int(str(self.NChanB.text()));
    pc = str(self.ChOutChan.text());
    if pc == '':
      return;
    pcval = float(pc);
    dp = pcval/2.0;
    self.StartChannel.setText(str(int(dp)));
    self.EndChannel.setText(str(int(self.NChan-dp)));

  def _getMSinfo(self):
    MS = str(self.MS.text());
    MSinfo = MSinfoWnd(self);
    nch = MSinfo.setMS(MS);
    MSinfo.show()
    self.NChanB.setText(nch);

  def set_startindex (self, value):
    _dprint(3,'streamrec is',self._streamrec);
    # exception handler ensures that we don't break when a record is missing 
    # for some reason
    try: self._streamrec.input.selection.channel_start_index = value;
    except AttributeError: pass;

  def set_endindex (self, value):
    _dprint(3,'streamrec is',self._streamrec);
    # exception handler ensures that we don't break when a record is missing 
    # for some reason
    try: self._streamrec.input.selection.channel_end_index = value;
    except AttributeError: pass;

  def run_stuff (self):
    _dprint(3,'streamrec is',self._streamrec);
    if self._streamrec:

      self._streamrec.input.tile_size = int(str(self.NTiles.text()));
      self._streamrec.input.selection.channel_start_index = \
                     int(str(self.StartChannel.text()));
      self._streamrec.input.selection.channel_end_index = \
                     int(str(self.EndChannel.text()));
      s1 = str(self.Station1.text());
      s2 = str(self.Station2.text());
      if (s1 != '') and (s2 != ''):
        selStr = 'ANTENNA1 in ' + s1 + ' && ANTENNA2 in ' + s2;
        self._streamrec.input.selection.selection_string = selStr;
      else:
        self._streamrec.input.selection.selection_string = '';
      MS = str(self.MS.text())
      if MS != self.currMS:
        self.currMS = MS;
        self._streamrec.input.ms_name = MS;
      # feed the full record to the kernel
      mqs().init(self._streamrec);
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

