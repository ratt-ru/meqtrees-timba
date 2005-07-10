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
import os
import os.path
import tempfile

_dbg = verbosity(0,name='tdlgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

# this holds the module object which all TDL scripts are imported into
_tdlmod = None;

def _file_mod_time (path):
  try:
    return os.stat(path).st_mtime; 
  except IOError:
    return None;

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
    self._qa_save = QAction(pixmaps.file_save.iconset(),"&Save script",Qt.ALT+Qt.Key_S,self);
    self._qa_save.addTo(self._toolbar);
    QObject.connect(self._qa_save,SIGNAL("activated()"),self._save_file);
    self._qa_run = QAction(pixmaps.blue_round_reload.iconset(),"&Run script",Qt.ALT+Qt.Key_R,self);
    self._qa_run.addTo(self._toolbar);
    QObject.connect(self._qa_run,SIGNAL("activated()"),self.compile_content);
    self._toolbar.addSeparator();
    self._poslabel = QLabel(self._toolbar);
    self._pathlabel = QLabel(self._toolbar);
    self._pathlabel.setAlignment(Qt.AlignRight);
    self._pathlabel.setIndent(10);
    self._toolbar.setStretchableWidget(self._pathlabel);
    # add editor window
    self._editor = QextScintilla(editor_box);
    # base font adjustment factor
    self._editor_fontadjust = self.fontInfo().pointSize() + 3;
    self.adjust_editor_font();
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
    QObject.connect(self._editor,SIGNAL("textChanged()"),self._text_changed);
    QObject.connect(self._editor,SIGNAL("modificationChanged(bool)"),self._text_modified);
    QObject.connect(self._editor,SIGNAL("cursorPositionChanged(int,int)"),self._display_cursor_position);
    # QObject.connect(self._editor,SIGNAL("textChanged()"),self._clear_transients);

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
    # prev/next error buttons
    self._qa_prev_err = QAction(pixmaps.red_leftarrow.iconset(),"Show &previous error",Qt.ALT+Qt.Key_P,self);
    self._qa_prev_err.addTo(errlist_hdr);
    QObject.connect(self._qa_prev_err,SIGNAL("activated()"),self._show_prev_error);
    self._qa_next_err = QAction(pixmaps.red_rightarrow.iconset(),"Show &next error",Qt.ALT+Qt.Key_N,self);
    self._qa_next_err.addTo(errlist_hdr);
    QObject.connect(self._qa_next_err,SIGNAL("activated()"),self._show_next_error);
    # run button
    self._qa_run.addTo(errlist_hdr);
    # error list itself
    self._errlist = QListBox(self._errlist_box);
    eblo.addWidget(self._errlist);
    QObject.connect(self._errlist,SIGNAL("highlighted(int)"),self._highlight_error);
    self._errlist_box.hide();
    self._errloc = [];

    # set filename
    self._filename = None;       # "official" path of file (None if new script not yet saved)
    self._real_filename = None;  # real name of disk file. This may be a temp file.
    self._file_disktime = None;  # modtime on disk when file was loaded
    
  def __del__ (self):
    self.has_focus(False);
    
  def _clear_transients (self):
    """if message box contains a transient message, clears it""";
    if self._message_transient:
      self.clear_message();
      
  def _text_changed (self):
    self._clear_transients();
    self._qa_run.setVisible(True);
  
  def _display_cursor_position (self,line,col):
    self._poslabel.setText("L:<b>%d</b> C:<b>%d</b>" % (line+1,col+1));
    self._poslabel.repaint();
  
  def _text_modified (self,mod):
    self._qa_save.setVisible(mod);
    if self._filename:
      label = '<b>' + self._filename + '</b>';
    else:
      label = '';
    if mod:
      self._clear_transients();
      self._qa_run.setVisible(True);
      label = '(modified) ' + label;
    self._pathlabel.setText(label);
    
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
    self._errlist_box.hide();
    
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
      for (errtype,errmsg,filename,location) in errlist:
        if isinstance(location,int):
          (line,column) = (location,0);
        else:
          (line,column) = location;
        index = self._errlist.count();
        self._errlist.insertItem('');
        if filename == self._real_filename:
          self._errlist.changeItem("%d: %s (%s) [%d]" % (index+1,errmsg,errtype,line),index);
          self._editor.markerAdd(line-1,self.ErrorMarker);
          self._errloc.append((line-1,column));
        else:
          self._errlist.changeItem("%d: %s (%s) [%s:%d]" % (index+1,errmsg,errtype,filename,line),index);
          self._errloc.append((filename,line,column));
      self._error_count_label.setText('<b>%d</b> errors'%(len(errlist)));
      self._errlist_box.show();
      self._errlist.setCurrentItem(0);
      self._highlight_error(0);
      # disable run control until something gets modified
      self._qa_run.setVisible(False);
    else:
      self._errlist_box.hide();
      self._qa_run.setVisible(True);
      
  def _show_next_error (self):
    ni = self._errlist.currentItem()+1;
    if ni >= self._errlist.count():
      ni = 0;
    self._errlist.setCurrentItem(ni);
    
  def _show_prev_error (self):
    ni = self._errlist.currentItem()-1;
    if ni < 0:
      ni = self._errlist.count()-1;
    self._errlist.setCurrentItem(ni);
      
  def _highlight_error (self,number):
    self._qa_prev_err.setEnabled(number>0);
    self._qa_next_err.setEnabled(number<self._errlist.count()-1);
    self._editor.markerDeleteAll(self.CurrentErrorMarker);
    if number < len(self._errloc):
      loc = self._errloc[number];
      if len(loc) == 2:
        (line,column) = loc;
        self._editor.ensureLineVisible(line);
        self._editor.setCursorPosition(line,column);
        # a little kludge to prevent line from being hidden by a resize
        self._editor.ensureLineVisible(line+5); 
        self._editor.markerAdd(line,self.CurrentErrorMarker);
        
  def _process_margin_click (self,margin,line,button):
    _dprint(0,margin,line,button);
    for (ierr,errline) in enumerate(self._errloc):
      if errline == line:
        self._errlist.setCurrentItem(ierr);
        break;
        
  def _save_file (self,filename=None,text=None,force=False):
    """Saves text. If force=False, checks modification times in case
    the file has been modified by another program, otherwise saves
    unconditionally. If no filename is known, asks for one.
    Returns True if file was successfully saved, else None.""";
    filename = filename or self._filename;
    if filename:
      if not force:
        filetime = _file_mod_time(filename);
        if filetime and filetime != self._file_disktime:
          res = QMessageBox.warning(self,"TDL file changed",
            """<p><tt>%s</tt> has been modified by another program. 
            Would you like to overwrite the disk version, revert to the disk
            version, or cancel the operation?"""
            % (filename,),
            "Overwrite","Revert","Cancel",-1,2);
          if res == 2:
            return None;
          elif res == 1:
            self.load_file(filename);
            return None;
          # else fall through to save
    else: # no filename, ask for one
      try: dialog = self._save_as_dialog;
      except AttributeError:
        self._save_as_dialog = dialog = QFileDialog(self,"save tdl dialog",True);
        dialog.resize(800,dialog.height());
        dialog.setMode(QFileDialog.AnyFile);
        dialog.setFilters("TDL scripts (*.tdl);;Python scripts (*.py);;All files (*.*)");
        dialog.setViewMode(QFileDialog.Detail);
        dialog.setCaption("Save TDL Script");
      else:
        dialog.rereadDir();
      if dialog.exec_loop() != QDialog.Accepted:
        return None;
      filename = str(dialog.selectedFile());
    # save the file
    if text is None:
      text = str(self._editor.text());
    try:
      outfile = file(filename,"w");
      outfile.write(text);
      outfile.close();
    except IOError:
      (exctype,excvalue,tb) = sys.exc_info();
      _dprint(0,'exception',sys.exc_info(),'saving TDL file',filename);
      self.show_message("""<b>Error writing <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (filename,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
    # saved successfully, update stuff
    self._filename = self._real_filename = filename;
    self._file_disktime = _file_mod_time(filename);
    self._editor.setModified(False);
    self._text_modified(False);
        
  def _write_to_tempfile (self,text,prefix='tmp',suffix='.py'):
    """helper func for compile below: writes text to a temporary file.""";
    try:
      infile = tempfile.NamedTemporaryFile(prefix='tmp',suffix='.py');
      infile.write(text);
      infile.seek(0);
      self._real_filename = infile.name;
      return file(infile.name);
    except IOError:
      (exctype,excvalue,tb) = sys.exc_info();
      _dprint(0,'exception',sys.exc_info(),'writing temp file',self._real_filename);
      self.show_message("""<b>Error writing temporary file <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (self._real_filename,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
      
  def compile_content (self):
    self.clear_message();
    self.clear_error_list();
    editor_text = str(self._editor.text());
    # The Python imp module expects text to reside in a disk file, which is
    # a pain in the ass for us if we're dealing with modified text or text
    # entered on-the-fly. So, several scenarios:
    # 1. We're working with a real filename
    #   1a. our text is newer: save text to temp file and compile from there
    #   1b. disk file modified since last load: display save/revert/cancel 
    #       dialog and go to 1c, or cancel.
    #   1c. nothing modified: load and compile text straight from disk file
    # 2. We have no filename (new file not yet saved, or TDL text from, e.g.,
    #   forest state):
    #   Save text to temp file, compile from there.
    # When using temp files, we'll retain the temp name in real_filename. We
    # need it to match error locations returned by python.
    if self._filename:  # real file
      pathname = self._filename;
      disktime = _file_mod_time(self._filename);
      # check 1a first:
      if disktime == self._file_disktime and self._editor.isModified():
        infile = self._write_to_tempfile(editor_text,suffix=os.path.basename(pathname));
        if infile is None:
          return None;
        tdltext = editor_text;
      else: # 1b or 1c
        # ok, read text from disk
        try:
          infile = file(pathname,'r');
          tdltext = infile.read();
          infile.seek(0);
        except IOError:
          (exctype,excvalue,tb) = sys.exc_info();
          _dprint(0,'exception',sys.exc_info(),'reading disk file',pathname);
          tdltext = None;
        # has text changed? save or revert according to user choice
        if tdltext != editor_text:
          res = QMessageBox.warning(self,"TDL file changed",
            """<p><tt>%s</tt> has been modified by another program. 
            Would you like to overwrite the disk version, revert to the disk
            version, or cancel the operation?"""
            % (pathname,),
            "Overwrite","Revert","Cancel",-1,2);
          if res == 0:
            infile.close();
            if not self._save_file(text=editor_text,force=True):
              return None;
            # reopen the file for reading, this ought to always succeed
            infile = file(pathname,'r');
            tdltext = editor_text;
          elif res == 1:
            self.load_file(pathname,text=tdltext);
          else:
            return;
    else:  # no file at all, have to save to temp file 
      pathname = 'tmp.py';
      infile = self._write_to_tempfile(editor_text);
      if infile is None:
        return None;
    # ok, the code above has presumably sorted out the file situation
    # infile is now an open input file object, pathname is some (possibly fake) 
    # name, self._real_filename is the real filename, and tdltext is the script 
    # text
    modname = '__tdlruntime';
    global _tdlmod;
    if _tdlmod is not None:
      _tdlmod.__dict__.clear();
    try:
      imp.acquire_lock();
      _tdlmod = imp.load_source(modname,self._real_filename,infile);
    except: # other import errors
      imp.release_lock();
      infile.close();
      (exctype,excvalue,tb) = sys.exc_info();
      traceback.print_exc();
      _dprint(0,'exception',sys.exc_info(),'importing TDL file',self._real_filename);
      if exctype is SyntaxError:
        msg = "syntax error at column %d" % (excvalue.offset,);
        self.show_error_list([('SyntaxError',msg,excvalue.filename,(excvalue.lineno,excvalue.offset))]);
        return None;
      self.show_message("""<b>Error importing <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (self._real_filename,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
    imp.release_lock();
    infile.close();
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
      _dprint(0,'exception',sys.exc_info(),'in define_forest() of TDL file',self._real_filename);
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
    self.clear_message();
    self.clear_error_list();
    # load text from file if not supplied
    if text is None:
      ff = file(filename);
      text = ff.read();
      ff.close();
    self._filename = self._real_filename = filename;
    self._file_disktime = filename and _file_mod_time(filename);
    self._editor.setText(text);
    self._editor.setReadOnly(readonly);
    self._editor.setModified(False);
    self._text_modified(False);
    # emit signals
    self.emit(PYSIGNAL("loadedFile()"),(filename,));
    
  def adjust_editor_font (self):
    # sets the editor font size based on our own size
    fi = self.fontInfo();
    self._editor.zoomTo(fi.pointSize() - self._editor_fontadjust);
    
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
  _icon = pixmaps.text_tdl;
  viewer_name = "TDL Browser";
  
  def __init__(self,gw,dataitem,cellspec={},default_open=None,**opts):
    browsers.GriddedPlugin.__init__(self,gw,dataitem,cellspec=cellspec);
    self._wedit = TDLEditor(self.wparent());
    self.set_widgets(self.wtop(),dataitem.caption,icon=self.icon());
    if dataitem.data is not None:
      self.set_data(dataitem);
    QObject.connect(self.wtop(),PYSIGNAL("fontChanged()"),self.wtop().adjust_editor_font);
    
  def wtop (self):
    return self._wedit;
  def editor (self):
    return self._wedit;
    
  def set_data (self,dataitem,default_open=None,**opts):
    _dprint(3,'set_data ',dataitem.udi);
    pathname = getattr(dataitem,'tdl_pathname',None);
    self._wedit.load_file(pathname,text=dataitem.data);
    
  def highlight (self,color=True):
    browsers.GriddedPlugin.highlight(self,color);
    self._wedit.has_focus(bool(color));

Grid.Services.registerViewer(str,TDLBrowser,priority=10,check_udi=lambda x:x.endswith('_tdl'));

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

