#!/usr/bin/python

from Timba.dmi import *
from Timba.utils import *
from Timba import Grid 
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.Meq import meqds
from Timba import TDL

from qt import *
from qtext import *

import imp
import sys
import traceback
import os.path

_dbg = verbosity(0,name='tdlgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

def run_tdl_script (pathname,parent):
  # open file first
  try:
    ff = file(pathname,'r');
    tdltext = ff.read();
    ff.seek(0);
  except IOError:
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'opening TDL file',pathname);
    QMessageBox.warning(parent,"Error loading TDL script",
      """<p>Cannot open file <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);
    return;
  # import module
  modname = '__tdlruntime';
  try:
    imp.acquire_lock();
    mod = imp.load_source(modname,pathname,ff);
  except:
    imp.release_lock();
    ff.close();
    traceback.print_exc();
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'importing TDL file',pathname);
    QMessageBox.warning(parent,"Error loading TDL script",
      """<p>Error during import of <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);
    return;
  imp.release_lock();
  ff.close();
  mqs = meqds.mqs();
  # module here, call functions
  try:
    ns = TDL.NodeScope();
    mod.define_forest(ns);
    delattr(mod,'define_forest');  # delete so it doesn't confuse the next import
    ns.Resolve();
  except:
    traceback.print_exc();
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'in define_forest() of TDL file',pathname);
    QMessageBox.warning(parent,"Error running TDL script",
      """<p>Error defining forest in <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);
    return;
  num_nodes = len(ns.AllNodes());
  # no nodes? return
  if not num_nodes:
    QMessageBox.warning(parent,"TDL script executed",
      """<p>Executed TDL script <tt>%s</tt>, but no nodes were defined.</p>""",
      QMessageBox.Ok);
    return;
  # try to run stuff
  mqs.meq('Clear.Forest');
  mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),ns.AllNodes().itervalues())));
  mqs.meq('Resolve.Batch',record(name=list(ns.RootNodes().iterkeys())));
  
  ### NB: presume this was successful for now
  
  # is a forest state defined?
  fst = getattr(mod,'forest_state',record());
  # add in source code
  fst.tdl_source = record(**{os.path.basename(pathname):tdltext});
  mqs.meq('Set.Forest.State',record(state=fst));
  delattr(mod,'forest_state');  # delete so it doesn't confuse the next import
    
  # does the script define a testing function?
  testfunc = getattr(mod,'test_forest',None);
  # no, show status and return
  if not callable(testfunc):
    QMessageBox.information(parent,"TDL script executed",
      """<p>Executed TDL script <tt>%s</tt>. %d node definition (of which %d are root nodes) were sent to the kernel.
      </p>""" % (pathname,num_nodes,len(ns.RootNodes())),
      QMessageBox.Ok);
    return;
  # yes, offer to run the test
  delattr(mod,'test_forest');  # delete so it doesn't confuse the next import
  if QMessageBox.information(parent,"TDL script executed",
       """<p>Executed TDL script <tt>%s</tt>.</p>
       <p>%d nodes (%d roots) were defined.</p>
       <p>This script provides a built-in test, would you like to run this now?</p>
       """ % (pathname,num_nodes,len(ns.RootNodes())),
       "Run test","Skip test") != 0:
    return;
  # run test
  try:
    testfunc(mqs);
  except:
    traceback.print_exc();
    (exctype,excvalue,tb) = sys.exc_info();
    _dprint(0,'exception',sys.exc_info(),'in test_forest() of TDL file',pathname);
    QMessageBox.warning(parent,"Error testing TDL script",
      """<p>Error running tests in <tt>%s</tt>:</p>
      <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
      QMessageBox.Ok);

class TDLEditor (QFrame):
  def __init__ (self,*args):
    QFrame.__init__(self,*args);
    lo = QVBoxLayout(self);
    # find main window to associate our toolbar with
    mainwin = self.parent();
    while mainwin and not isinstance(mainwin,QMainWindow):
      mainwin = self.parent();
    self._toolbar = QToolBar("TDL tools",mainwin,self);
    lo.addWidget(self._toolbar);
    # populate toolbar
    self._qa_jobs = QActionGroup(self);
    self._qa_jobs.setUsesDropDown(True);
    self._pathlabel = QLabel(self._toolbar);
    self._toolbar.setStretchableWidget(self._pathlabel);
    # add splitter
    self._splitter = QSplitter(QSplitter.Vertical,self);
    lo.addWidget(self._splitter);
    # add editor window
    self._editor = QextScintilla(self._splitter);
    self._lexer = QextScintillaLexerPython(self);
    self._editor.setLexer(self._lexer);
    self._editor.show();
    # add message window
    self._message = QLabel(self._splitter);
    self._splitter.setCollapsible(self._message,True);
    self._message.hide();
    # set filename
    self._filename = None;
    
  def load_file (self,filename,text=None,readonly=False):
    # load text from file if not supplied
    if text is None:
      ff = file(filename);
      text = ff.read();
      ff.close();
    self._filename = filename;
    if filename is None:
      self._pathlabel.setText("");
    else:
      self._pathlabel.setText("<b>"+filename+"</b>");
    self._editor.setText(text);
    self._editor.setReadOnly(readonly);
    # emit signals
    self.emit(PYSIGNAL("loadedFile()"),(filename,));
    
def makeTDLFileDataItem (pathname):
  """creates a GridDataItem for a TDL script""";
  # read the file (exception propagated outwards on error)
  ff = file(pathname);
  text = ff.read();
  ff.close();
  basename = os.path.basename(pathname);
  # create the item
  udi = '/tdlfile/'+pathname;
  name = basename;
  caption = '<b>'+basename+'</b>';
  desc = 'TDL file '+pathname;
  return Grid.DataItem(udi,name=name,caption=caption,desc=desc,data=text,viewer=TDLBrowser,refresh=None);

class TDLBrowser(browsers.GriddedPlugin):
  _icon = pixmaps.text_left;
  viewer_name = "TDL Browser";
  
  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    self._wedit = TDLEditor(self.wparent());
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    if dataitem.data is not None:
      self.set_data(dataitem);
      
  def wtop (self):
    return self._wedit;
      
  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    self._wedit.load_file(None,text=dataitem.data,readonly=True);

Grid.Services.registerViewer(str,TDLBrowser,priority=10,check_udi=lambda x:x.endswith('.tdl'));
