#!/usr/bin/python

from Timba.dmi import *
from Timba.utils import *
from Timba import Grid 
from Timba.GUI import browsers
from Timba.GUI.pixmaps import pixmaps
from Timba.GUI import app_proxy_gui
from Timba.Meq import meqds
from Timba import TDL
import Timba.TDL.Settings
import Timba.TDL.Compile

from qt import *
from qtext import *

import imp
import sys
import re
import traceback
import os
import os.path
import sets
import tempfile

_dbg = verbosity(0,name='tdlgui');
_dprint = _dbg.dprint;
_dprintf = _dbg.dprintf;

def _file_mod_time (path):
  try:
    return os.stat(path).st_mtime; 
  except IOError:
    return None;
    
# flag: sync to external editor
_external_sync = True;
def set_external_sync (value):
  global _external_sync;
  _external_sync = value;

class TDLEditor (QFrame,PersistentCurrier):
  ErrorMarker = 0;
  CurrentErrorMarker = 1;
  # a single editor always has the focus
  current_editor = None;
  
  def __init__ (self,parent,close_button=False):
    QFrame.__init__(self,parent);
    toplo = QVBoxLayout(self);
    self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    splitter = QSplitter(Qt.Vertical,self);
    toplo.addWidget(splitter);
    splitter.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding);
    splitter.setChildrenCollapsible(False);
    
    # figure out our app_gui parent
    self._appgui = app_proxy_gui.appgui(parent);
    
    # create an editor box
    editor_box = QFrame(splitter);
    lo = QVBoxLayout(editor_box);
    
    # find main window to associate our toolbar with
    self._toolbar = QToolBar("TDL tools",self._appgui,editor_box);
    lo.addWidget(self._toolbar);
    
    #### populate toolbar
    self._tb_jobs = QToolButton(self._toolbar);
    self._tb_jobs.setIconSet(pixmaps.gear.iconset());
    self._tb_jobs.setTextLabel("Exec");
    self._tb_jobs.setUsesTextLabel(True);
    self._tb_jobs.setTextPosition(QToolButton.BesideIcon);
    QToolTip.add(self._tb_jobs,"Executes jobs predefined by this TDL script");
    self._jobmenu = QPopupMenu(self);
    self._tb_jobs.setPopup(self._jobmenu);
    self._tb_jobs.setPopupDelay(1);
    self._tb_jobs.hide();
    
    # save menu and button
    self._tb_save = QToolButton(self._toolbar);
    self._tb_save.setIconSet(pixmaps.file_save.iconset());
    QToolTip.add(self._tb_save,"Saves script. Click on the down-arrow for other options.");
    savemenu = QPopupMenu(self);
    self._tb_save.setPopup(savemenu);
    self._tb_save.setPopupDelay(0);
    self._tb_save._modified_color = QColor("yellow");
    qa_save = QAction(pixmaps.file_save.iconset(),"&Save script",Qt.ALT+Qt.Key_S,self);
    QObject.connect(qa_save,SIGNAL("activated()"),self._save_file);
    QObject.connect(self._tb_save,SIGNAL("clicked()"),self._save_file);
    qa_save.addTo(savemenu);
    qa_save_as = QAction(pixmaps.file_save.iconset(),"Save script &as...",0,self);
    QObject.connect(qa_save_as,SIGNAL("activated()"),self.curry(self._save_file,save_as=True));
    qa_save_as.addTo(savemenu);
    qa_revert = self._qa_revert = QAction("Revert to saved",0,self);
    QObject.connect(qa_revert,SIGNAL("activated()"),self._revert_to_saved);
    qa_revert.addTo(savemenu);
    
    # run menu and button
    self._tb_run = QToolButton(self._toolbar);
    self._tb_run.setIconSet(pixmaps.blue_round_reload.iconset());
    
    self._tb_runmenu = QPopupMenu(self);
    self._tb_run.setPopup(self._tb_runmenu);
    self._tb_run.setPopupDelay(0);
    self._qa_runmain = QAction(pixmaps.blue_round_reload.iconset(),
                              "&Save & run main script",Qt.ALT+Qt.Key_R,self);
    QObject.connect(self._qa_runmain,SIGNAL("activated()"),self._run_main_file);
    QObject.connect(self._tb_run,SIGNAL("clicked()"),self._run_main_file);
    self._qa_runmain.addTo(self._tb_runmenu);
    qa_runthis_as = QAction(pixmaps.blue_round_reload.iconset(),"Save & run this script as main script...",0,self);
    qa_runthis_as.setToolTip("Saves and reruns this script as a top-level TDL script");
    QObject.connect(qa_runthis_as,SIGNAL("activated()"),self._run_as_main_file);
    qa_runthis_as.addTo(self._tb_runmenu);
    
    # self._qa_run = QAction(pixmaps.blue_round_reload.iconset(),"&Run script",Qt.ALT+Qt.Key_R,self);
    # self._qa_run.addTo(self._toolbar);
    # QObject.connect(self._qa_run,SIGNAL("activated()"),self.compile_content);
    self._toolbar.addSeparator();
    self._poslabel = QLabel(self._toolbar);
    width = self._poslabel.fontMetrics().width("L:999 C:999");
    self._poslabel.setMinimumWidth(width);
    self._pathlabel = QLabel(self._toolbar);
    self._pathlabel.setAlignment(Qt.AlignRight);
    self._pathlabel.setIndent(10);
    if close_button:
      if not isinstance(close_button,QIconSet):
        close_button = pixmaps.remove.iconset();
      self._qa_close = QAction(close_button,"&Close file",Qt.ALT+Qt.Key_W,self);
      QObject.connect(self._qa_close,SIGNAL("activated()"),self,PYSIGNAL("fileClosed()"));
      self._qa_close.addTo(self._toolbar);
    self._toolbar.setStretchableWidget(self._pathlabel);
    
    #### add editor window
    
    self._editor = QextScintilla(editor_box);
    # base font adjustment factor
    self._editor_fontadjust = self.fontInfo().pointSize() + 1;
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
    self._message_icon = QToolButton(msgb1);
    self._message = QLabel(msgb1);
    self._message.setTextFormat(Qt.RichText);
    self._message.setMargin(0);
    self._message.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);
    # self._message_icon.setAlignment(Qt.AlignTop);
    # self._message_icon.setMargin(4);
    self._message_icon.setAutoRaise(True);
    self._message_icon.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed);
    QObject.connect(self._message_icon,SIGNAL("clicked()"),self.clear_message);
    QToolTip.add(self._message_icon,"Click here to clear the message");
    self._message_widgets = [];
    self._message_transient = False;

    # add error list widget
    self._werrlist_box = QFrame(splitter);
    eblo = QVBoxLayout(self._werrlist_box);
    # error list header is a toolbar
    errlist_hdr = QToolBar("TDL errors",self._appgui,self._werrlist_box);
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
    self._qa_runmain.addTo(errlist_hdr);
    # error list itself
    # self._werrlist = QListBox(self._werrlist_box);
    # QObject.connect(self._werrlist,SIGNAL("highlighted(int)"),self._highlight_error);
    self._werrlist = QListView(self._werrlist_box);
    QObject.connect(self._werrlist,SIGNAL("currentChanged(QListViewItem*)"),self._highlight_error_item);
    QObject.connect(self._werrlist,SIGNAL("clicked(QListViewItem*)"),self._highlight_error_item);
    QObject.connect(self._werrlist,SIGNAL("spacePressed(QListViewItem*)"),self._highlight_error_item);
    QObject.connect(self._werrlist,SIGNAL("returnPressed(QListViewItem*)"),self._highlight_error_item);
    self._werrlist.addColumn(''); 
    self._werrlist.addColumn(''); 
    self._werrlist.addColumn(''); 
    # self._werrlist.setColumnAlignment(0,Qt.AlignRight);
    self._werrlist.setRootIsDecorated(True);
    self._werrlist.setAllColumnsShowFocus(True);
    self._werrlist.header().hide();
    
    eblo.addWidget(self._werrlist);
    self._werrlist_box.hide();
    self._error_list = [];
    self._error_at_line = {};

    # set filename
    self._filename = None;       # "official" path of file (None if new script not yet saved)
    self._mainfile = None;       # if not None, then we're "slaved" to a main file (see below)
    self._file_disktime = None;  # modtime on disk when file was loaded
    self._basename = None;
    self._modified = False;
    
  def __del__ (self):
    self.has_focus(False);
    
  def hide_jobs_menu (self,dum=False):
    self._tb_jobs.hide();
    
  def get_filename (self):
    return self._filename;
  def get_mainfile (self):
    return self._mainfile;
    
  def _run_main_file (self):
    self.clear_error_list();
    if self._mainfile and self._editor.isModified():
      self._save_file();
    self.emit(PYSIGNAL("compileFile()"),(self._mainfile or self._filename,));
    
  def _run_as_main_file (self):
    self.clear_error_list();
    self._set_mainfile(None);
    self._text_modified(self._editor.isModified());   # to reset labels
    self.emit(PYSIGNAL("fileChanged()"),());
    self.emit(PYSIGNAL("compileFile()"),(self._filename,));
    
  def _clear_transients (self):
    """if message box contains a transient message, clears it""";
    if self._message_transient:
      self.clear_message();
      
  def _text_changed (self):
    self._clear_transients();
#    self._qa_run.setVisible(True);

  def _display_cursor_position (self,line,col):
    self._poslabel.setText("L:<b>%d</b> C:<b>%d</b>" % (line+1,col+1));
    self._poslabel.repaint();
  
  def _text_modified (self,mod):
    self._modified = mod;
    self.emit(PYSIGNAL("textModified()"),(bool(mod),));
    if mod:
      self._tb_save.setPaletteBackgroundColor(self._tb_save._modified_color);
    else:
      self._tb_save.unsetPalette();
    if self._filename:
      label = '<b>' + self._basename + '</b>';
      QToolTip.add(self._pathlabel,self._filename);
    else:
      label = '';
      QToolTip.remove(self._pathlabel);
    if self._mainfile:
      label += ' (from <b>' + self._mainfile_base +'</b>)';
    if self._readonly:
      label = '[r/o] ' + label;
    if mod:
      self._clear_transients();
      label = '[mod] ' + label;
    self._pathlabel.setText(label);
    
#   def _show_jobs_menu (self):
#     if self._jobmenu:
#       pos = self._toolbar.mapToGlobal(QPoint(0,self._toolbar.height()));
#       self._jobmenu.popup(pos);

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
    
  def show_message (self,msg,error=False,iconset=None,transient=False):
    """Shows message in box.
    If iconset is not None, overrides standard icon.
    If error=True, uses error icon (iconset overrides this).
    If transient=True, message will be cleared when text is edited.
    """;
    self._message.setText(msg);
    if not iconset:
      if error:
        iconset = pixmaps.red_round_cross.iconset();
      else:
        iconset = pixmaps.info_blue_round.iconset();
    self._message_icon.setIconSet(iconset);
    self._message_box.show();
    self._message_transient = transient;
    self._werrlist_box.hide();
    
  def messagebox ():
    return self._message_box;
    
  def add_message_widget (self,widget):
    self._mblo.addWidget(widget);
    self._message_widgets.append(widget);

  def clear_error_list (self,signal=True):
    if signal:
      self.emit(PYSIGNAL("hasErrors()"),(0,));
    self._error_items = None;
    self._werrlist.clear();
    self._editor.markerDeleteAll();
    self._error_count_label.setText('');
    self._error_list = [];
    self._error_at_line = {};
    self.clear_message();
    
  def get_error_list (self):
    """returns the current error list."""
    return self._error_list;
      
  def set_error_list (self,errlist,signal=True,show_item=True):
    """Shows an error list. errlist should be a sequence of Exception
    objects following the TDL error convention.
    """;
    _dprint(1,self._filename,"error list of",len(errlist),"entries",id(errlist));
    _dprint(1,self._filename,"current list has",len(self._error_list),"entries",id(self._error_list));
    # do nothing if already set
    if self._error_list is errlist:
      return;
    self.clear_error_list(signal=False);
    self._error_list = errlist;
    _dprint(1,self._filename,"processing list");
    if errlist:
      self._error_items = [];
      self._error_at_line = {};
      previtem = self._werrlist;
      nerr = 1;
      nhere = 0;
      for index,err in enumerate(errlist):
        errmsg = str(err.args[0]);
        filename = getattr(err,'filename',None);
        line = getattr(err,'lineno',0);
        column = getattr(err,'offset',0);
        # effectively, this makes CalledFrom errors child items
        # of the previous non-error item (previtem)
        if isinstance(err,TDL.CalledFrom):
          item = QListViewItem(previtem,'');
        else:
          previtem = item = QListViewItem(self._werrlist,"%d:"%(nerr,));
          nerr += 1;
          if filename == self._filename:
            nhere += 1;
        item.setOpen(True);
        self._error_items.append(item);
        # set item content
        item.setText(1,errmsg);
        if filename is None:
          item.setText(2,"[internal error; more info may be available on the text console]");
        elif filename == self._filename:
          item._err_location = index,None,line,column;
          item.setText(2,"[line %d]" % (line,));
          self._editor.markerAdd(line-1,self.ErrorMarker);
          self._error_at_line.setdefault(line-1,item);
        else:
          item._err_location = index,filename,line,column;
          item.setText(2,"[line %d of %s]" % (line,filename));
      if nhere == nerr-1:
        self._error_count_label.setText('<b>%d</b> errors total'%(nhere,));
      else:
        self._error_count_label.setText('<b>%d</b> errors here, <b>%d</b> total'%(nhere,nerr-1,));
      self._werrlist_box.show();
      if show_item:
        self._show_error_item(self._error_items[0]);
      if signal:
        self.emit(PYSIGNAL("hasErrors()"),(nhere,));
      # self._highlight_error(0);
      # disable run control until something gets modified
      # self._qa_run.setVisible(False);
    else:
      self._werrlist_box.hide();
      
  def _highlight_error_item (self,item):
    self._qa_prev_err.setEnabled(item is not self._error_items[0]);
    self._qa_next_err.setEnabled(item is not self._error_items[-1]);
    self._editor.markerDeleteAll(self.CurrentErrorMarker);
    # does item contain a location attribute?
    try: index,filename,line,column = item._err_location;
    except AttributeError: return;
    # indicate location
    if filename is None:
      self.show_position(line-1,column,mark_error=True);
    else:
      self.emit(PYSIGNAL("showError()"),(index,filename,line,column));
  
  def show_position (self,line,column=0,mark_error=False):
    """shows indicated position""";
    self._editor.ensureLineVisible(line);
    self._editor.setCursorPosition(line,column);
    # a little kludge to prevent line from being hidden by a resize
    self._editor.ensureLineVisible(line+5); 
    if mark_error:
      self._editor.markerDeleteAll(self.CurrentErrorMarker);
      self._editor.markerAdd(line,self.CurrentErrorMarker);
      
  def _show_next_error (self):
    item = self._werrlist.currentItem();
    if item:
      item = item.itemBelow();
    else:
      item = self._error_items[0];
    if item:
      self._show_error_item(item);
    
  def _show_prev_error (self):
    item = self._werrlist.currentItem();
    if item:
      item = item.itemAbove();
    else:
      item = self._error_items[-1];
    if item:
      self._show_error_item(item);
  
  def show_error_number (self,index):
    self._show_error_item(self._error_items[index]);
    
  def _show_error_item (self,item):
    _dprint(1,item);
    self._werrlist.ensureItemVisible(item);
    self._werrlist.setCurrentItem(item);
    self._highlight_error_item(item);
      
  def _process_margin_click (self,margin,line,button):
    _dprint(1,margin,line,button);
    # look through current error widget to find relevant error
    item = self._error_at_line.get(line,None);
    if item:
      self._show_error_item(item);
      
  def _sync_external_file (self,filename,ask=True):
    filetime = _file_mod_time(filename);
    if not filetime or filetime == self._file_disktime:
      return True;  # in sync
    if not ask:
      res = 1;
    else:
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
      return True;  # in sync
      
  def _save_file (self,filename=None,text=None,force=False,save_as=False):
    """Saves text. If force=False, checks modification times in case
    the file has been modified by another program. 
    If force=True, saves unconditionally. 
    If no filename is known, asks for one. 
    Returns True if file was successfully saved, else None.""";
    filename = filename or self._filename;
    if filename and not save_as:
      if not force:
        if not self._sync_external_file(filename,ask=True):
          return None;
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
      outfile = file(filename,"w").write(text);
    except IOError:
      (exctype,excvalue,tb) = sys.exc_info();
      _dprint(0,'exception',sys.exc_info(),'saving TDL file',filename);
      self.show_message("""<b>Error writing <tt>%s</tt>:
        <i>%s (%s)</i></b>""" % (filename,excvalue,exctype.__name__),
        error=True,transient=True);
      return None;
    # saved successfully, update stuff
    self._filename = filename;
    self._qa_revert.setEnabled(True);
    self._basename = os.path.basename(filename);
    self._file_disktime = _file_mod_time(filename);
    self._editor.setModified(False);
    self._text_modified(False);
    self.emit(PYSIGNAL("fileSaved()"),(filename,));
    return self._filename;
    
  def confirm_close (self):
    if not self._modified:
      return True;
    res = QMessageBox.warning(self,"TDL file modified",
      """Save modified file <p><tt>%s</tt>?</p>"""
      % (self._filename or "",),
      "Save","Don't Save","Cancel",0,2);
    if res == 2:
      return False;
    if res == 0:
      return bool(self._save_file());
    return True; 
    
  def _revert_to_saved (self,force=False):
    if not self._filename:
      return;
    if not force:
      if QMessageBox.question(self,"Revert to saved",
        """Revert to saved version of <p><tt>%s</tt>?"""
        % (self._filename,),
        "Revert","Cancel",None,0,1):
        return;
    self.load_file(self._filename);
        
  def compile_content (self):
    _dprint(1,self._filename,"compiling");
    self.clear_message();
    self.clear_error_list();
    # clear predefined functions
    self._tb_jobs.hide();
    dum = None;
    # The Python imp module expects text to reside in a disk file, which is
    # a pain in the ass for us if we're dealing with modified text or text
    # entered on-the-fly. So, either save or sync before proceeding
    global _external_sync;
    if self._editor.isModified() or not self._filename:
      if not self._save_file():
        return None;
    else:
      if not self._sync_external_file(self._filename,ask=False):
        return None;
    tdltext = str(self._editor.text());
    # make list of publishing nodes 
    pub_nodes = [ node.name for node in meqds.nodelist.iternodes() 
                  if node.is_publishing() ];
    # try the compilation
    try:
      QApplication.setOverrideCursor(QCursor(Qt.WaitCursor));
      try:
        (_tdlmod,ns,msg) = TDL.Compile.compile_file(meqds.mqs(),self._filename,tdltext,parent=self);
      finally:
        QApplication.restoreOverrideCursor();
    # catch compilation errors
    except TDL.CumulativeError,value:
      self.set_error_list(value.args);
      return None;
    except Exception,value:
      self.set_error_list([value]);
      return None;
    # refresh the nodelist
    allnodes = ns.AllNodes();
    meqds.request_nodelist();
    # restore publishing nodes
    for name in pub_nodes: 
      if name in allnodes:
        meqds.mqs().meq('Node.Publish.Results',record(name=name,enable=True),wait=False);
    ### NB: presume this all was successful for now

    # does the script define an explicit job list?
    joblist = getattr(_tdlmod,'_tdl_job_list',[]);
    if not joblist:
      joblist = []; 
      # try to build it from implicit function names
      for (name,func) in _tdlmod.__dict__.iteritems():
        if name.startswith("_tdl_job_") and callable(func):
          joblist.append(func);
    # does the script define a testing function?
    testfunc = getattr(_tdlmod,'_test_forest',None);
    if not callable(testfunc):
      testfunc = getattr(_tdlmod,'test_forest',None);
      if callable(testfunc):
        res = QMessageBox.warning(self,"Deprecated method",
          """Your script contains a test_forest() method. This is deprecated
          and will be disabled in the future. Please rename it to 
          _test_forest(). 
          """,
          QMessageBox.Ok);
    if callable(testfunc):
      joblist.append(testfunc);
    joblist.sort(lambda a,b:cmp(str(a),str(b)));

    # create list of job actions
    self._jobmenu.clear();
    if joblist:
      self._tb_jobs.show();
      for func in joblist:
        name = re.sub("^_tdl_job_","",func.__name__);
        name = name.replace('_',' ');
        qa = QAction(pixmaps.gear.iconset(),name,0,self._jobmenu);
        if func.__doc__:
          qa.setToolTip(func.__doc__);
        qa._call = curry(func,meqds.mqs(),self);
        QObject.connect(qa,SIGNAL("activated()"),qa._call);
        qa.addTo(self._jobmenu);
    else:
      self._tb_jobs.hide();

    if joblist:
      msg += " %d predefined function(s) available." % (len(joblist),);
      
    self.show_message(msg,transient=True);
    return True;
    
  def get_jobs_popup (self):
    return self._jobmenu;

  def _set_mainfile (self,mainfile):
    """adjusts GUI controls based on whether we are a mainfile or not""";
    self._mainfile = mainfile;
    self._mainfile_base = mainfile and os.path.basename(mainfile);
    # if we have a mainfile, add extra options for the Run button
    if mainfile:
      self._tb_run.setPopup(self._tb_runmenu);
      QToolTip.add(self._tb_run,"Saves this script and runs the main script "+self._mainfile_base+". Click on the down-arrow for other options.");
      self._qa_runmain.setToolTip("Saves this script and runs the main script "+self._mainfile_base+".");
      self._qa_runmain.setMenuText("Run "+self._mainfile_base);
    else:
      self._tb_run.setPopup(None);
      QToolTip.add(self._tb_run,"Saves and runs the script.");
    
  def load_file (self,filename,text=None,readonly=False,mainfile=None):
    """loads editor content.
    filename is filename. text is file contents, if none then file will be re-read.
    readonly is True for readonly mode.
    If mainfile is not None, then this editor is "slaved" to the mainfile. This is the
    case for files included from other modules.
    """
    self.clear_message();
    self.clear_error_list();
    if not os.access(filename,os.W_OK):
      readonly = True;
    # load text from file if not supplied
    if text is None:
      ff = file(filename);
      text = ff.read();
      ff.close();
    self._filename = filename;
    # sets as as the mainfile or as a submodule of a main file
    self._set_mainfile(mainfile);
    # set save icons, etc.
    self._qa_revert.setEnabled(bool(filename));
    self._basename = os.path.basename(filename);
    self._readonly = readonly;
    self._file_disktime = filename and _file_mod_time(filename);
    self._editor.setText(text);
    self._editor.setReadOnly(readonly);
    self._editor.setModified(False);
    self._text_modified(False);
    # emit signals
    self.emit(PYSIGNAL("fileLoaded()"),(filename,));
    
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

# # standard method to register actions in the main menu
# #
# def define_mainmenu_actions (menu,parent):
#   _dprint(1,'defining stream control menu actions');
#   global _qa_next,_qa_prev,_qa_run;
#   _qa_next = QAction(pixmaps.blue_round_rightarrow.iconset(),"&Next error",Qt.CTRL+Qt.Key_N,parent);
#   _qa_next.addTo(menu['TDL']);
#   _qa_next.setEnabled(False);
#   _qa_prev = QAction(pixmaps.blue_round_leftarrow.iconset(),"&Previous error",Qt.CTRL+Qt.Key_P,parent);
#   _qa_prev.addTo(menu['TDL']);
#   _qa_prev.setEnabled(False);
#   _qa_run = QAction(pixmaps.blue_round_reload.iconset(),"&Run script",Qt.CTRL+Qt.Key_R,parent);
#   _qa_run.addTo(menu['TDL']);
#   _qa_run.setEnabled(False);
# 
