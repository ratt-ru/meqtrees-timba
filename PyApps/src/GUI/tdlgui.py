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

# this holds the module object which all TDL scripts are imported into
_tdlmod = None;

class TDLEditor (QFrame,PersistentCurrier):
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
    # add editor window
    self._editor = QextScintilla(self);
    lo.addWidget(self._editor);
    self._editor.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self._lexer = QextScintillaLexerPython(self);
    self._editor.setLexer(self._lexer);
    self._editor.markerDefine(QextScintilla.RightTriangle,self.Error.Marker);
    self._editor.markerDefine(QextScintilla.RightTriangle,self.Error.CurrentMarker);
    self._editor.setMarkerForegroundColor(QColor("red"),self.Error.Marker);
    self._editor.setMarkerForegroundColor(QColor("red"),self.Error.CurrentMarker);
    self._editor.setMarkerBackgroundColor(QColor("red"),self.Error.CurrentMarker);
    # add message window
    self._message_box = QFrame(self);
    lo.addWidget(self._message_box);
    self._message_box.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    self._message_box.setFrameStyle(QFrame.Panel+QFrame.Sunken);
    self._message_box.setLineWidth(2);
    mblo = QVBoxLayout(self._message_box);
    msgb1 = QHBox(self._message_box);
    mblo.addWidget(msgb1);
    self._message_icon = QLabel(msgb1);
    self._message = QLabel(msgb1);
    self._message.setTextFormat(Qt.RichText);
    self._message.setMargin(0);
    self._message.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    self._message_icon.setAlignment(Qt.AlignTop);
    self._message_icon.setMargin(4);
    self._message_icon.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed);
    self._message_widgets = [];
    self._message_transient = False;
    # set filename
    self._filename = None;
    # set error list
    self._errlist = [];
    self._cur_err = -1;
    # connect up some signals
    QObject.connect(self._editor,SIGNAL("modificationAttempted()"),
      self._clear_transients);
    QObject.connect(self._editor,SIGNAL("textChanged()"),
      self._clear_transients);
    
  def _clear_transients (self):
    """if message box contains a transient message, clears it""";
    if self._message_transient:
      self.clear_message();
    
  def clear_message (self):
    self._message_box.hide();
    self._message.setText('');
    self._message_icon.setText('');
    self._message_transient = False;
    if self._message_widgets:
      dum = QWidget();
      for w in self._message_widgets:
        w.reparent(dum);
      self._message_widgets = [];
    self._editor.markerDeleteAll(self.Error.CurrentMarker);
    
  def show_message (self,msg,error=False,pixmap=None,transient=False):
    """Shows message in box.
    If pixmap is not None, a pixmap is shown as well.
    If error=True, an error pixmap is show (pixmap overrides this).
    If transient=True, message will be cleared when text is edited.
    """;
    self._message.setText(msg);
    if not pixmap:
      if error:
        pixmap = pixmaps.red_round_cross.pm();
      else:
        pixmap = pixmaps.info_blue_round.pm();
    # show pixmap
    if pixmap:    
      self._message_icon.setPixmap(pixmap);
    self._message_box.show();
    self._message_transient = transient;
    
  def messagebox ():
    return self._message_box;
    
  def add_message_widget (self,widget):
    self._mblo.addWidget(widget);
    self._message_widgets.append(widget);
    
  class Error (object):
    Marker = 0;
    CurrentMarker = 1;
    def __init__ (self,editor,message,line=None):
      self.editor = editor;
      self.message = message;
      self.line = line;
      if line is not None:
        self.mhandle = editor.markerAdd(line,self.Marker);
      else:
        self.mhandle = None;
    def __del__ (self):
      if self.mhandle is not None:
        self.editor.markerDeleteHandle(self.mhandle);
    def highlight (self):
      self.editor.markerDeleteAll(self.CurrentMarker);
      if self.line is not None:
        self.editor.markerAdd(self.line,self.CurrentMarker);
        self.editor.ensureLineVisible(self.line);
    
  def clear_errors (self):
    self._editor.markerDeleteAll();
    self.clear_message();
    self._errlist = [];
    self._cur_err = -1;
    
  def add_error (self,errtype,errvalue,tb):
    """Adds an error to the error list.  Arguments are as returned by 
    sys.exc_info(). A source position in the current script will be looked
    for in the tb traceback""";
    # look for error line
    errline = None;
    stack = traceback.extract_tb(tb);
    for (filename,line,funcname,text) in stack[-1::-1]:
      if filename == self._filename:
        errline = line-1;  # lines (as reported by traceback) are 1-based
        break;
    # form message
    msg = "%s <i>(%s)</i>" % (errvalue,errtype.__name__)
    err = self.Error(self._editor,msg,errline);
    self._errlist.append(err);
    
  def show_next_error (self):
    self._cur_err = max(self._cur_err+1,len(self._errlist)-1);
    if self._cur_err >= 0:
      err = self._errlist[self._cur_err];
      err.highlight();
      self.show_message(err.message,error=True,transient=True);
    
  def compile_content (self):
    self.clear_errors();
    pathname = self._filename;
    # open file first
    try:
      ff = file(pathname,'r');
      tdltext = ff.read();
      ff.seek(0);
    except IOError:
      (exctype,excvalue,tb) = sys.exc_info();
      _dprint(0,'exception',sys.exc_info(),'opening TDL file',pathname);
      self.show_message("""<b>Can't open file <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (pathname,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
    # import module
    modname = '__tdlruntime';
    global _tdlmod;
    if _tdlmod is not None:
      _tdlmod.__dict__.clear();
    try:
      imp.acquire_lock();
      _tdlmod = imp.load_source(modname,pathname,ff);
    except:
      imp.release_lock();
      ff.close();
      traceback.print_exc();
      (exctype,excvalue,tb) = sys.exc_info();
      _dprint(0,'exception',sys.exc_info(),'importing TDL file',pathname);
      self.show_message("""<b>Error importing <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (pathname,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
    imp.release_lock();
    ff.close();
    mqs = meqds.mqs();
    # module here, call functions
    try:
      ns = TDL.NodeScope();
      _tdlmod.define_forest(ns);
      ns.Resolve();
    except:
      (exctype,excvalue,tb) = sys.exc_info();
      traceback.print_exc();
      _dprint(0,'exception',sys.exc_info(),'in define_forest() of TDL file',pathname);
      self.add_error(exctype,excvalue,tb);
      self.show_next_error();
      return None;
    num_nodes = len(ns.AllNodes());
    # no nodes? return
    if not num_nodes:
      self.show_message("Script executed successfully, but no nodes were defined.",
              transient=True);
      return None;
    # try to run stuff
    mqs.meq('Clear.Forest');
    mqs.meq('Create.Node.Batch',record(batch=map(lambda nr:nr.initrec(),ns.AllNodes().itervalues())));
    mqs.meq('Resolve.Batch',record(name=list(ns.RootNodes().iterkeys())));

    ### NB: presume this was successful for now

    # is a forest state defined?
    fst = getattr(_tdlmod,'forest_state',record());
    # add in source code
    fst.tdl_source = record(**{os.path.basename(pathname):tdltext});
    mqs.meq('Set.Forest.State',record(state=fst));

    # does the script define a testing function?
    testfunc = getattr(_tdlmod,'test_forest',None);
    # no, show status and return
#    if not callable(testfunc):
    self.show_message("Script executed successfully. %d node definitions (of which %d are root nodes) sent to the kernel."
            % (num_nodes,len(ns.RootNodes())),
            transient=True);
    return None;
#     # yes, offer to run the test
#     if QMessageBox.information(self,"TDL script executed",
#          """<p>Executed TDL script <tt>%s</tt>.</p>
#          <p>%d nodes (%d roots) were defined.</p>
#          <p>This script provides a built-in test, would you like to run this now?</p>
#          """ % (pathname,num_nodes,len(ns.RootNodes())),
#          "Run test","Skip test") != 0:
#       return None;
#     # run test
#     try:
#       testfunc(mqs);
#     except:
#       traceback.print_exc();
#       (exctype,excvalue,tb) = sys.exc_info();
#       _dprint(0,'exception',sys.exc_info(),'in test_forest() of TDL file',pathname);
#       QMessageBox.warning(self,"Error testing TDL script",
#         """<p>Error running tests in <tt>%s</tt>:</p>
#         <p><small><i>%s: %s</i><small></p>""" % (pathname,exctype.__name__,excvalue),
#         QMessageBox.Ok);
    
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
    









class TDLFileDataItem (Grid.DataItem):
  """represents a GridDataItem for a TDL script""";
  def __init__ (self,pathname):
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
    Grid.DataItem.__init__(self,udi,name=name,caption=caption,desc=desc,data=text,viewer=TDLBrowser,refresh=None);
    # add extra pathname attribute for tdl objects
    self.tdl_pathname = pathname;
      





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
  def editor (self):
    return self._wedit;
      
  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    pathname = getattr(dataitem,'tdl_pathname',None);
    self._wedit.load_file(pathname,text=dataitem.data,readonly=True);

Grid.Services.registerViewer(str,TDLBrowser,priority=10,check_udi=lambda x:x.endswith('.tdl'));
