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

_dbg = verbosity(0,name='StreamCtrl');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

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
    b1  = QPushButton("Tilesize = 5",self._wtop);
    b2  = QPushButton("Tilesize = 10",self._wtop);
    run = QPushButton("Run stuff!",self._wtop);
    QObject.connect(run,SIGNAL("clicked()"),self.run_stuff);
    # note use of currier to create a callback, the same function will
    # be called in both cases, but with different arguments
    QObject.connect(b1,SIGNAL("clicked()"),self._currier.curry(self.set_tilesize,5));
    QObject.connect(b2,SIGNAL("clicked()"),self._currier.curry(self.set_tilesize,10));
    
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
    
  # GUI callbacks
  def set_tilesize (self,size):
    _dprint(3,'streamrec is',self._streamrec);
    # exception handler ensures that we don't break when a record is missing 
    # for some reason
    try: self._streamrec.input.tile_size = size;
    except AttributeError: pass;
  
  def run_stuff (self):
    _dprint(3,'streamrec is',self._streamrec);
    if self._streamrec:
      # feed the full record to the kernel
      mqs().init(self._streamrec);

    
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
  
    
def define_treebrowser_actions (tb):
  _dprint(1,'defining stream control treebrowser actions');
  parent = tb.wtop();
  # create QAction for the Stream control plugin
  stream = QAction("Stream Control",pixmaps.spigot.iconset(),"Stream Control",0,parent);
  # make sure it's enabled/disabled as appropriate
  stream._is_enabled = lambda tb=tb: tb.is_connected;
  # "200" is priority of action, determining its place in the toolbar
  tb.add_action(stream,200,callback=_start_stream_control);

