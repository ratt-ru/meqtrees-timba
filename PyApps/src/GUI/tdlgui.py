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
  ErrorMarker = 0;
  CurrentErrorMarker = 1;
  # a single editor always has the focus
  current_editor = None;
  
  def __init__ (self,*args):
    QFrame.__init__(self,*args);
    toplo = QVBoxLayout(self);
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    splitter = QSplitter(Qt.Vertical,self);
    toplo.addWidget(splitter);
    splitter.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    splitter.setChildrenCollapsible(False);
    
    # create an editor box
    editor_box = QFrame(splitter);
    lo = QVBoxLayout(editor_box);
    # find main window to associate our toolbar with
    mainwin = self.parent();
    while mainwin and not isinstance(mainwin,QMainWindow):
      mainwin = self.parent();
    self._toolbar = QToolBar("TDL tools",mainwin,editor_box);
    lo.addWidget(self._toolbar);
    # populate toolbar
    self._qa_jobs = QActionGroup(self);
    self._qa_jobs.setUsesDropDown(True);
    self._pathlabel = QLabel(self._toolbar);
    self._toolbar.setStretchableWidget(self._pathlabel);
    # add editor window
    self._editor = QextScintilla(editor_box);
    lo.addWidget(self._editor);
    self._editor.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    self._lexer = QextScintillaLexerPython(self);
    self._editor.setLexer(self._lexer);
    self._editor.markerDefine(QextScintilla.RightTriangle,self.ErrorMarker);
    self._editor.markerDefine(QextScintilla.RightTriangle,self.CurrentErrorMarker);
    self._editor.setMarkerForegroundColor(QColor("red"),self.ErrorMarker);
    self._editor.setMarkerForegroundColor(QColor("red"),self.CurrentErrorMarker);
    self._editor.setMarkerBackgroundColor(QColor("red"),self.CurrentErrorMarker);
    self._editor.setMarginSensitivity(1,True);
    QObject.connect(self._editor,SIGNAL("marginClicked(int,int,Qt::ButtonState)"),self._process_margin_click);
    QObject.connect(self._editor,SIGNAL("modificationAttempted()"),self._clear_transients);
    QObject.connect(self._editor,SIGNAL("textChanged()"),self._clear_transients);

    # add message window
    self._message_box = QFrame(editor_box);
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

    # add error list widget
    self._errlist_box = QFrame(splitter);
    eblo = QVBoxLayout(self._errlist_box);
    # error list header is a toolbar
    errlist_hdr = QToolBar("TDL errors",mainwin,self._errlist_box);
    eblo.addWidget(errlist_hdr);
    errsym = QLabel(errlist_hdr);
    errsym.setPixmap(pixmaps.red_round_cross.pm());
    errlist_hdr.addSeparator();
    self._error_count_label = QLabel(errlist_hdr);
    errlist_hdr.setStretchableWidget(self._error_count_label);
    # error list itself
    self._errlist = QListBox(self._errlist_box);
    eblo.addWidget(self._errlist);
    QObject.connect(self._errlist,SIGNAL("highlighted(int)"),self._highlight_error);
    self._errlist_box.hide();
    self._errloc = [];

    # set filename
    self._filename = None;
    
  def __del__ (self):
    self.has_focus(False);
    
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
    
  def clear_error_list (self):
    self._errlist.clear();
    self._editor.markerDeleteAll();
    self._error_count_label.setText('');
    self._errloc = []
    self.clear_message();
      
  def show_error_list (self,errlist):
    self.clear_error_list();
    if errlist:
      for (errtype,errmsg,filename,line) in errlist:
        index = self._errlist.count();
        self._errlist.insertItem('');
        if filename == self._filename:
          self._errlist.changeItem("%d: %s (%s) [%d]" % (index+1,errmsg,errtype,line),index);
          self._editor.markerAdd(line-1,self.ErrorMarker);
          self._errloc.append(line-1);
        else:
          self._errlist.changeItem("%d: %s (%s) [%s:%d]" % (index+1,errmsg,errtype,filename,line),index);
          self._errloc.append((filename,line));
      self._error_count_label.setText('<b>%d</b> errors'%(len(errlist)));
      self._errlist_box.show();
      self._errlist.setCurrentItem(0);
    else:
      self._errlist_box.hide();
      
  def _highlight_error (self,number):
    self._editor.markerDeleteAll(self.CurrentErrorMarker);
    if number < len(self._errloc):
      loc = self._errloc[number];
      if isinstance(loc,int):
        self._editor.ensureLineVisible(loc);
        # a little kludge to prevent line from being hidden by a resize
        self._editor.ensureLineVisible(loc+5); 
        self._editor.markerAdd(loc,self.CurrentErrorMarker);
        
  def _process_margin_click (self,margin,line,button):
    _dprint(0,margin,line,button);
    for (ierr,errline) in enumerate(self._errloc):
      if errline == line:
        self._errlist.setCurrentItem(ierr);
        break;
      
  def compile_content (self):
    self.clear_message();
    self.clear_error_list();
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
    errlist = [];
    try:
      ns = TDL.NodeScope();
      _tdlmod.define_forest(ns);
      ns.Resolve();
    except TDL.CumulativeError,value:
    # this exception gives us an error list directly
      errlist = value[0];
    except:
    # other exception; check if we also have an error list
      errlist = ns.GetErrors();
      # look through traceback to figure out caller
      (exctype,excvalue,tb) = sys.exc_info();
      traceback.print_exc();
      _dprint(0,'exception',sys.exc_info(),'in define_forest() of TDL file',pathname);
      errline = None;
      stack = traceback.extract_tb(tb);
      for (filename,line,funcname,text) in stack[-1::-1]:
        if filename == self._filename:
          errlist.append((exctype.__name__,str(excvalue),filename,line));
          break;
      else:
        errlist.append((exctype.__name__,str(excvalue),stack[-1][0],stack[-1][1]));
    # do we have an error list? show it
    if errlist:
      self.show_error_list(errlist);
      return;
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
    self.clear_message();
    self.clear_error_list();
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
    
  def has_focus (self,focus):
    if focus:
      TDLEditor.current_editor = self;
    else:
      if TDLEditor.current_editor == self:
        TDLEditor.current_editor = None;

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
    
  def highlight (self,color=True):
    browsers.GriddedPlugin.highlight(self,color);
    self._wedit.has_focus(bool(color));

Grid.Services.registerViewer(str,TDLBrowser,priority=10,check_udi=lambda x:x.endswith('.tdl'));

# standard method to register actions in the main menu
#
def define_mainmenu_actions (menu,parent):
  _dprint(1,'defining stream control menu actions');
  global _qa_next,_qa_prev,_qa_run;
  _qa_next = QAction(pixmaps.blue_round_rightarrow.iconset(),"&Next error",Qt.CTRL+Qt.Key_N,parent);
  _qa_next.addTo(menu['TDL']);
  _qa_next.setEnabled(False);
  _qa_prev = QAction(pixmaps.blue_round_leftarrow.iconset(),"&Previous error",Qt.CTRL+Qt.Key_P,parent);
  _qa_prev.addTo(menu['TDL']);
  _qa_prev.setEnabled(False);
  _qa_run = QAction(pixmaps.blue_round_reload.iconset(),"&Run script",Qt.CTRL+Qt.Key_R,parent);
  _qa_run.addTo(menu['TDL']);
  _qa_run.setEnabled(False);

